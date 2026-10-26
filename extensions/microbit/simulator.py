#!/usr/bin/env python3
"""``MicrobitSimulator`` -- the pure state of one simulated micro:bit.

No pygame, no Qt: the frame update, the overlay, the input hook and (later)
the serial link all read and write this object (Stage S2,
docs/MICROBIT_EXTENSION_PLAN.md).

Inputs are set from outside (``set_button``, ``set_acceleration``, ...);
``update(dt)`` advances time and returns the events that happened since the
last call, as ``(kind, detail)`` tuples:

* ``("button", "a" | "b" | "ab")`` -- on press-down, like MicroPython's
  ``was_pressed``. "ab" fires when the second button goes down while the
  other is held, in addition to that button's own event.
* ``("logo", "touched")``, ``("pin", 0 | 1 | 2)`` -- on touch-down.
* ``("gesture", name)`` -- MicroPython's gesture names: "up", "down",
  "left", "right", "face up", "face down", "freefall", "2g", "3g", "6g",
  "8g", "shake".
* ``("sound", "loud" | "quiet")`` -- crossing the microphone thresholds.
* ``("display_done", None)`` -- the display queue has just emptied.
* ``("sound_note", (hz, seconds))`` / ``("sound_stop", None)`` -- for the
  audio output: a note (0 Hz = rest) just began / sound was cut off.
* ``("sound_done", None)`` -- the sound queue has just emptied.
* ``("radio", value)`` -- a radio message arrived (a number or a string).

Gesture recognition is the micro:bit runtime's own algorithm (codal-core
``Accelerometer::updateGesture``/``instantaneousPosture``), run on a fixed
20 ms sample clock so its damping counts mean the same time as on the
device. Display commands queue and play one after another, because on the
device ``display.scroll``/``show`` wait for the display to be free.
"""

from .font import GLYPHS
from .images import IMAGES
from .sound import melody_notes, tone_notes, DEFAULT_BPM
from .radio import clamp_group, clean_message

WIDTH = 5
HEIGHT = 5
MAX_BRIGHTNESS = 9

# MicroPython's defaults (microbit_display.c).
SCROLL_DELAY = 0.150

# A Step event that shows something every frame would otherwise grow the
# queue without bound (on the device the loop blocks instead).
MAX_QUEUE = 16
MAX_SOUND_QUEUE = 16     # tones/melodies waiting, as with the display
MAX_RADIO_OUTBOX = 32    # messages a board can have in flight at once

# --- accelerometer (codal-core Accelerometer.h), milli-g -------------------
SAMPLE_PERIOD = 0.020
TILT_TOLERANCE = 200
FREEFALL_TOLERANCE = 400
SHAKE_TOLERANCE = 400
SHAKE_COUNT_THRESHOLD = 4
SHAKE_DAMPING = 10
SHAKE_RTX = 30
GESTURE_DAMPING = 5
IMPULSES = (("2g", 2048), ("3g", 3072), ("6g", 6144), ("8g", 8192))
# Never run more than this many samples in one update, so a long stall
# (a breakpoint, a dragged window) doesn't freeze the game catching up.
MAX_SAMPLES_PER_UPDATE = 50

# Resting flat on a table, face up.
REST_ACCELERATION = (0, 0, -1024)

# --- microphone (codal-microbit-v2 MicroBitAudio: 85 dB / 65 dB on the
# 35-100 dB -> 0-255 scale MicroPython's sound_level() uses) ------------------
LOUD_THRESHOLD = 196
QUIET_THRESHOLD = 118

BUTTONS = ("a", "b")
PINS = (0, 1, 2)


def _blank():
    return [[0] * WIDTH for _ in range(HEIGHT)]


def parse_image(spec):
    """A 5x5 brightness grid (``[y][x]``, 0-9) from a built-in image name
    ("HEART", any case) or MicroPython's ``"09090:99999:..."`` row string.
    Raises ``ValueError`` for anything else."""
    if not isinstance(spec, str):
        raise ValueError(f"not an image: {spec!r}")
    text = spec.strip()
    rows = IMAGES.get(text.upper())
    if rows is None:
        rows = text.rstrip(":").split(":")
        if len(rows) != HEIGHT or any(
                len(r) != WIDTH or not r.isdigit() for r in rows):
            raise ValueError(f"not an image: {spec!r}")
    return [[int(ch) for ch in row] for row in rows]


def _glyph(ch):
    # The device shows '?' for anything outside printable ASCII (accents
    # included), so the simulator does too.
    return GLYPHS.get(ch, GLYPHS["?"])


def glyph_image(ch):
    """The 5x5 grid for one character, lit at full brightness."""
    rows = _glyph(ch)
    return [[MAX_BRIGHTNESS if row & (0x10 >> x) else 0 for x in range(WIDTH)]
            for row in rows]


def text_columns(text):
    """The columns a scroll of ``text`` passes across the display: each
    character 5 columns wide with a 1-column gap (monospaced, as MakeCode
    scrolls). Each column is a list of 5 brightness values, top first."""
    columns = []
    for i, ch in enumerate(text):
        if i:
            columns.append([0] * HEIGHT)
        grid = glyph_image(ch)
        for x in range(WIDTH):
            columns.append([grid[y][x] for y in range(HEIGHT)])
    return columns


def scroll_frames(text):
    """Every frame of a scroll, in order: the text enters from the right
    edge and the last frame is blank once it has fully left."""
    blank = [0] * HEIGHT
    strip = [blank] * WIDTH + text_columns(text) + [blank] * WIDTH
    frames = []
    for start in range(1, len(strip) - WIDTH + 1):
        window = strip[start:start + WIDTH]
        frames.append([[window[x][y] for x in range(WIDTH)] for y in range(HEIGHT)])
    return frames


def format_number(value):
    """How ``show_number`` writes a number: whole numbers without a
    trailing ".0"."""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)


class _Frame:
    """A still image held for ``hold`` seconds (0 = just show it)."""

    def __init__(self, grid, hold):
        self.frames = [grid]
        self.step = max(0.0, float(hold))

    @property
    def duration(self):
        return self.step


class _Scroll:
    """A sequence of frames, each shown for ``step`` seconds."""

    def __init__(self, frames, step):
        self.frames = frames
        self.step = max(0.001, float(step))

    @property
    def duration(self):
        return self.step * len(self.frames)


class MicrobitSimulator:
    def __init__(self):
        # display[y][x], brightness 0-9 like MicroPython's display.get_pixel
        self.display = _blank()
        # MakeCode's led.setBrightness scale, applied by the renderer.
        self.brightness = 255

        self._queue = []
        self._elapsed = 0.0      # time spent on self._queue[0]

        self.buttons = {name: False for name in BUTTONS}
        self.logo_touched = False
        self.pins_touched = {pin: False for pin in PINS}
        self.pins_analog = {pin: 0 for pin in PINS}

        self.acceleration = REST_ACCELERATION
        self.compass_heading = 0
        self.light_level = 0
        self.temperature = 21
        self.sound_level = 0

        # Sound: queued tones/melodies (each a list of (hz, seconds) steps)
        # play one after another, like the display queue. ``tone`` is the
        # frequency sounding now (0 = silent).
        self.tone = 0.0
        self._sound = []
        self._step = 0
        self._step_elapsed = 0.0

        # Radio: ``radio.deliver`` moves the outbox to the other boards
        # in the same group; a message that arrives is reported as an event.
        self.radio_group = 0
        self._radio_outbox = []

        self._pending = []
        self._sample_clock = 0.0
        # codal-core gesture state
        self.current_gesture = ""
        self._candidate = None
        self._sigma = 0
        self._shake_sign = {"x": False, "y": False, "z": False}
        self._shake_count = 0
        self._shake_timer = 0
        self._shaken = False
        self._impulses = set()
        self._impulse_sigma = 0
        # Start "quiet" so a silent room doesn't fire a quiet event at once.
        self._sound_state = "quiet"

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def get_pixel(self, x, y):
        return self.display[y][x]

    def set_pixel(self, x, y, value):
        """Set one LED now (0-9); out-of-range coordinates are ignored."""
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            self.display[y][x] = max(0, min(MAX_BRIGHTNESS, int(value)))

    def set_brightness(self, value):
        self.brightness = max(0, min(255, int(value)))

    def clear(self):
        """Blank the display and drop anything still queued."""
        self._queue.clear()
        self._elapsed = 0.0
        self.display = _blank()

    @property
    def busy(self):
        """True while something is queued or still playing."""
        return bool(self._queue)

    def show_image(self, spec, hold=0.0):
        """Queue a still image (see ``parse_image``). Returns False if the
        queue is full."""
        return self._enqueue(_Frame(parse_image(spec), hold))

    def scroll_text(self, text, delay=SCROLL_DELAY):
        return self._enqueue(_Scroll(scroll_frames(str(text)), delay))

    def show_number(self, value, delay=SCROLL_DELAY):
        """One character shows still; anything longer scrolls (MakeCode)."""
        text = format_number(value)
        if len(text) == 1:
            return self._enqueue(_Frame(glyph_image(text), 0.0))
        return self.scroll_text(text, delay)

    def _enqueue(self, item):
        if not self._queue and isinstance(item, _Frame) and item.step == 0 \
                and item.frames[0] == self.display:
            return True   # already showing it: not a new animation
        if self._queue and self._same(self._queue[-1], item):
            return True   # a repeat of what's already waiting
        if len(self._queue) >= MAX_QUEUE:
            return False
        self._queue.append(item)
        if len(self._queue) == 1:
            self._elapsed = 0.0
            self.display = [row[:] for row in item.frames[0]]
        return True

    @staticmethod
    def _same(a, b):
        return type(a) is type(b) and a.step == b.step and a.frames == b.frames

    def _advance_display(self, dt):
        if not self._queue:
            return
        remaining = dt
        while self._queue:
            item = self._queue[0]
            left = item.duration - self._elapsed
            if remaining < left:
                self._elapsed += remaining
                index = min(int(self._elapsed / item.step), len(item.frames) - 1) \
                    if item.step else 0
                self.display = [row[:] for row in item.frames[index]]
                return
            # This item is finished; its last frame stays on the display.
            remaining -= max(0.0, left)
            self.display = [row[:] for row in item.frames[-1]]
            self._queue.pop(0)
            self._elapsed = 0.0
            if self._queue:
                self.display = [row[:] for row in self._queue[0].frames[0]]
        self._pending.append(("display_done", None))

    # ------------------------------------------------------------------
    # Sound
    # ------------------------------------------------------------------

    @property
    def sound_busy(self):
        """True while a tone or melody is queued or sounding."""
        return bool(self._sound)

    def play_tone(self, frequency, milliseconds=500):
        """Queue a tone. Returns False if the queue is full."""
        return self._enqueue_sound(tone_notes(frequency, milliseconds))

    def play_melody(self, spec, bpm=DEFAULT_BPM):
        """Queue a melody (see ``sound.melody_notes``). Raises ``ValueError``
        for a melody that can't be read. Returns False if the queue is full."""
        return self._enqueue_sound(melody_notes(spec, bpm))

    def stop_sound(self):
        """Silence everything and drop what's queued."""
        was_busy = bool(self._sound) or self.tone
        self._sound.clear()
        self._step = 0
        self._step_elapsed = 0.0
        self.tone = 0.0
        if was_busy:
            self._pending.append(("sound_stop", None))

    def _enqueue_sound(self, steps):
        if self._sound and self._sound[-1] == steps:
            return True       # a repeat of what's already waiting
        if len(self._sound) >= MAX_SOUND_QUEUE:
            return False
        self._sound.append(steps)
        if len(self._sound) == 1:
            self._step = 0
            self._step_elapsed = 0.0
            self._begin_step()
        return True

    def _begin_step(self):
        hz, seconds = self._sound[0][self._step]
        self.tone = hz
        self._pending.append(("sound_note", (hz, seconds)))

    def _advance_sound(self, dt):
        if not self._sound:
            return
        remaining = dt
        while self._sound:
            hz, seconds = self._sound[0][self._step]
            left = seconds - self._step_elapsed
            if remaining < left:
                self._step_elapsed += remaining
                return
            remaining -= left
            self._step += 1
            self._step_elapsed = 0.0
            if self._step >= len(self._sound[0]):
                self._sound.pop(0)
                self._step = 0
            if self._sound:
                self._begin_step()
        if self.tone:
            self.tone = 0.0
            self._pending.append(("sound_stop", None))
        self._pending.append(("sound_done", None))

    # ------------------------------------------------------------------
    # Radio
    # ------------------------------------------------------------------

    def set_radio_group(self, group):
        self.radio_group = clamp_group(group)

    def radio_send(self, value):
        """Queue a number or string for the other boards in this group.
        Returns False if too many are already in flight."""
        if len(self._radio_outbox) >= MAX_RADIO_OUTBOX:
            return False
        self._radio_outbox.append(clean_message(value))
        return True

    def take_radio_outbox(self):
        messages, self._radio_outbox = self._radio_outbox, []
        return messages

    def radio_receive(self, value):
        """A message arrived (called by ``radio.deliver``)."""
        self._pending.append(("radio", value))

    # ------------------------------------------------------------------
    # Buttons, logo, pins
    # ------------------------------------------------------------------

    def set_button(self, name, pressed):
        name = name.lower()
        if name not in self.buttons:
            raise ValueError(f"no button {name!r}")
        was = self.buttons[name]
        self.buttons[name] = bool(pressed)
        if pressed and not was:
            self._pending.append(("button", name))
            other = "b" if name == "a" else "a"
            if self.buttons[other]:
                self._pending.append(("button", "ab"))

    def is_pressed(self, name):
        if name.lower() == "ab":
            return all(self.buttons.values())
        return self.buttons[name.lower()]

    def set_logo_touched(self, touched):
        if touched and not self.logo_touched:
            self._pending.append(("logo", "touched"))
        self.logo_touched = bool(touched)

    def set_pin_touched(self, pin, touched):
        if pin not in self.pins_touched:
            raise ValueError(f"no touch pin {pin!r}")
        if touched and not self.pins_touched[pin]:
            self._pending.append(("pin", pin))
        self.pins_touched[pin] = bool(touched)

    def set_pin_analog(self, pin, value):
        if pin not in self.pins_analog:
            raise ValueError(f"no pin {pin!r}")
        self.pins_analog[pin] = max(0, min(1023, int(value)))

    # ------------------------------------------------------------------
    # Sensors
    # ------------------------------------------------------------------

    def set_acceleration(self, x, y, z):
        self.acceleration = (int(x), int(y), int(z))

    def shake(self):
        """A shake from the sensor strip's button: the same event and
        re-arm time as a detected shake."""
        if not self._shaken:
            self._shaken = True
            self._shake_count = SHAKE_COUNT_THRESHOLD
            self._shake_timer = 0
            self.current_gesture = "shake"
            self._pending.append(("gesture", "shake"))

    def set_compass_heading(self, degrees):
        self.compass_heading = int(degrees) % 360

    def set_light_level(self, value):
        self.light_level = max(0, min(255, int(value)))

    def set_temperature(self, celsius):
        self.temperature = int(celsius)

    def set_sound_level(self, value):
        self.sound_level = max(0, min(255, int(value)))
        if self._sound_state != "loud" and self.sound_level > LOUD_THRESHOLD:
            self._sound_state = "loud"
            self._pending.append(("sound", "loud"))
        elif self._sound_state != "quiet" and self.sound_level < QUIET_THRESHOLD:
            self._sound_state = "quiet"
            self._pending.append(("sound", "quiet"))

    # ------------------------------------------------------------------
    # Gestures (codal-core Accelerometer, one call per 20 ms sample)
    # ------------------------------------------------------------------

    def _posture(self):
        x, y, z = self.acceleration
        detected = False
        for axis, value in (("x", x), ("y", y), ("z", z)):
            sign = self._shake_sign[axis]
            if (value < -SHAKE_TOLERANCE and sign) or (value > SHAKE_TOLERANCE and not sign):
                detected = True
                self._shake_sign[axis] = not sign

        if detected and self._shake_count < SHAKE_COUNT_THRESHOLD:
            self._shake_count += 1
            if self._shake_count == 1:
                self._shake_timer = 0
            if self._shake_count == SHAKE_COUNT_THRESHOLD:
                self._shaken = True
                self._shake_timer = 0
                return "shake"

        if self._shake_count > 0:
            self._shake_timer += 1
            if self._shaken and self._shake_timer >= SHAKE_RTX:
                self._shaken = False
                self._shake_timer = 0
                self._shake_count = 0
            elif not self._shaken and self._shake_timer >= SHAKE_DAMPING:
                self._shake_timer = 0
                self._shake_count -= 1

        if x * x + y * y + z * z < FREEFALL_TOLERANCE ** 2:
            return "freefall"
        if x < -1000 + TILT_TOLERANCE:
            return "left"
        if x > 1000 - TILT_TOLERANCE:
            return "right"
        if y < -1000 + TILT_TOLERANCE:
            return "down"
        if y > 1000 - TILT_TOLERANCE:
            return "up"
        if z < -1000 + TILT_TOLERANCE:
            return "face up"
        if z > 1000 - TILT_TOLERANCE:
            return "face down"
        return ""

    def _sample(self):
        x, y, z = self.acceleration
        force = x * x + y * y + z * z
        if force > IMPULSES[0][1] ** 2:
            for name, tolerance in IMPULSES:
                if force > tolerance ** 2 and name not in self._impulses:
                    self._impulses.add(name)
                    self._pending.append(("gesture", name))
            self._impulse_sigma = 0
        if self._impulse_sigma < GESTURE_DAMPING:
            self._impulse_sigma += 1
        else:
            self._impulses.clear()

        posture = self._posture()
        if posture == "shake":
            self.current_gesture = "shake"
            self._pending.append(("gesture", "shake"))
            return

        if posture == self._candidate:
            if self._sigma < GESTURE_DAMPING:
                self._sigma += 1
        else:
            self._candidate = posture
            self._sigma = 0

        if self._candidate != self.current_gesture and self._sigma >= GESTURE_DAMPING:
            self.current_gesture = self._candidate
            if self.current_gesture:
                self._pending.append(("gesture", self.current_gesture))

    # ------------------------------------------------------------------

    def update(self, dt):
        """Advance ``dt`` seconds; return the events since the last call."""
        dt = max(0.0, float(dt))
        self._sample_clock += dt
        samples = 0
        while self._sample_clock >= SAMPLE_PERIOD and samples < MAX_SAMPLES_PER_UPDATE:
            self._sample_clock -= SAMPLE_PERIOD
            self._sample()
            samples += 1
        if samples == MAX_SAMPLES_PER_UPDATE:
            self._sample_clock = 0.0
        self._advance_display(dt)
        self._advance_sound(dt)
        events, self._pending = self._pending, []
        return events
