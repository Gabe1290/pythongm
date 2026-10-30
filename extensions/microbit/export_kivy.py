"""The micro:bit on the Kivy (Android/iOS) export -- Stage P, unit K1.

The Python simulator is pure (no Qt, no pygame), so it is shipped into the game
byte for byte as the ``microbit_sim`` package (``SUPPORT_FILES``) and the
generated objects drive it through the ``_mb_*`` helper methods this file adds
to the base object (``BASE_OBJECT_CODE``). The action/condition codegen only
emits calls to those helpers (the M34 "two halves" pattern: the generator emits
a call, the helper holds the logic), so the behaviour is the desktop handler's
(``handlers.py``) rather than a second reading of it.

The extension loader ``exec``s this file without ``__file__``, so everything
here is plain data.
"""

# {path under the game folder: source path relative to this extension's folder}
SUPPORT_FILES = {
    "microbit_sim/__init__.py": "export/kivy_sim_init.py",
    "microbit_sim/simulator.py": "simulator.py",
    "microbit_sim/font.py": "font.py",
    "microbit_sim/images.py": "images.py",
    "microbit_sim/sound.py": "sound.py",
    "microbit_sim/melodies.py": "melodies.py",
    "microbit_sim/radio.py": "radio.py",
    "microbit_sim/layout.py": "layout.py",              # verbatim (K3)
    "microbit_sim/state.py": "export/kivy_state.py",    # layout.py's option_of
    "microbit_sim/draw.py": "kivy_draw.py",
    "microbit_sim/touch.py": "kivy_touch.py",
    "microbit_sim/speaker.py": "kivy_audio.py",
}


# ---------------------------------------------------------------------------
# Action / condition codegen. Each fn(gen, params, event_type) returns code
# (an expression, for a condition). Value params go through the generator's own
# expression helpers so `coins + 1` / `"text"` mean what they mean elsewhere.
# ---------------------------------------------------------------------------

def _helpers():
    from export.Kivy.code_generator import _num_code, _value_code
    return _num_code, _value_code


def _unquote(raw):
    text = str(raw if raw is not None else "").strip()
    if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    return text


def _cg_show_image(gen, params, event_type):
    num, _ = _helpers()
    spec = str(params.get("image", "HEART")).strip()
    return f"self._mb_show_image({spec!r}, {num(params.get('hold'), 0)})"


def _cg_scroll_text(gen, params, event_type):
    num, value = _helpers()
    return (f"self._mb_scroll_text({value(params.get('text', ''))}, "
            f"{num(params.get('delay'), 0)})")


def _cg_show_number(gen, params, event_type):
    _, value = _helpers()
    return f"self._mb_show_number({value(params.get('value', 0))})"


def _cg_set_pixel(gen, params, event_type):
    num, _ = _helpers()
    return (f"self._mb_set_pixel({num(params.get('x'), 0)}, {num(params.get('y'), 0)}, "
            f"{num(params.get('brightness'), 9)})")


def _cg_clear_display(gen, params, event_type):
    return "self._mb_clear_display()"


def _cg_set_brightness(gen, params, event_type):
    num, _ = _helpers()
    return f"self._mb_set_brightness({num(params.get('brightness'), 255)})"


def _cg_play_tone(gen, params, event_type):
    num, _ = _helpers()
    return (f"self._mb_play_tone({num(params.get('frequency'), 440)}, "
            f"{num(params.get('duration'), 500)})")


def _cg_play_melody(gen, params, event_type):
    num, _ = _helpers()
    spec = _unquote(params.get("melody", ""))
    return f"self._mb_play_melody({spec!r}, {num(params.get('tempo'), 120)})"


def _cg_stop_sound(gen, params, event_type):
    return "self._mb_stop_sound()"


def _cg_radio_set_group(gen, params, event_type):
    num, _ = _helpers()
    return f"self._mb_radio_set_group({num(params.get('group'), 0)})"


def _cg_radio_send(gen, params, event_type):
    _, value = _helpers()
    return f"self._mb_radio_send({value(params.get('value', 1))})"


def _cg_read_sensor(gen, params, event_type):
    sensor = str(params.get("sensor", "accelerometer x")).strip().lower()
    name = str(params.get("variable") or "sensor_value").strip()
    # A scope prefix is split here, so the generated helper call carries a plain
    # name and a flag (no "global." text in a generated line).
    is_global = name.startswith("global.")
    if is_global:
        name = name[len("global."):]
    return f"self._mb_read_sensor({sensor!r}, {name!r}, {is_global!r})"


# ---------------------------------------------------------------------------
# Events (K2). The simulator reports (kind, detail); events.py maps that onto a
# flat event name. The same two tables are repeated here as plain data because
# the exported game cannot import events.py -- tests/test_kivy_microbit_events.py
# pins them to it. Every event type gets an `on_<name>` handler method.
# ---------------------------------------------------------------------------
_FIXED_EVENTS = {
    "button:a": "microbit_button_a",
    "button:b": "microbit_button_b",
    "button:ab": "microbit_button_ab",
    "logo:touched": "microbit_logo_touched",
    "pin:0": "microbit_pin_0",
    "pin:1": "microbit_pin_1",
    "pin:2": "microbit_pin_2",
    "sound:loud": "microbit_loud_sound",
    "sound:quiet": "microbit_quiet_sound",
    "display_done:None": "microbit_display_done",
    "sound_done:None": "microbit_sound_done",
    "radio": "microbit_radio_received",
}
_GESTURE_EVENTS = {
    "shake": "shake", "up": "logo_up", "down": "logo_down",
    "left": "tilt_left", "right": "tilt_right",
    "face up": "screen_up", "face down": "screen_down",
    "freefall": "free_fall", "2g": "2g", "3g": "3g", "6g": "6g", "8g": "8g",
}

# Room-entry keys copied onto the instance an entry creates (desktop: __init__'s
# on_instance_created reads instance_data.get('is_microbit')).
INSTANCE_ATTRS = ("is_microbit",)

# Object-level properties baked into every instance of the object: on the desktop `option_of`
# falls back to instance.object_data.get(name); an exported object has no such dict.
OBJECT_ATTRS = ("microbit_scale", "microbit_show_sensors", "microbit_keyboard")

EVENT_METHODS = {name: "on_" + name for name in _FIXED_EVENTS.values()}
EVENT_METHODS.update({"microbit_gesture_" + g: "on_microbit_gesture_" + g
                      for g in _GESTURE_EVENTS.values()})


ACTION_CODEGEN = {
    "microbit_show_image": _cg_show_image,
    "microbit_scroll_text": _cg_scroll_text,
    "microbit_show_number": _cg_show_number,
    "microbit_set_pixel": _cg_set_pixel,
    "microbit_clear_display": _cg_clear_display,
    "microbit_set_brightness": _cg_set_brightness,
    "microbit_play_tone": _cg_play_tone,
    "microbit_play_melody": _cg_play_melody,
    "microbit_stop_sound": _cg_stop_sound,
    "microbit_radio_set_group": _cg_radio_set_group,
    "microbit_radio_send": _cg_radio_send,
    "microbit_read_sensor": _cg_read_sensor,
}


def _cc_if_button(gen, params, event_type):
    return f"self._mb_if_button({str(params.get('button', 'a')).strip().lower()!r})"


def _cc_if_gesture(gen, params, event_type):
    return f"self._mb_if_gesture({str(params.get('gesture', 'shake')).strip().lower()!r})"


def _cc_if_tilt(gen, params, event_type):
    num, _ = _helpers()
    return (f"self._mb_if_tilt({str(params.get('axis', 'x')).strip().lower()!r}, "
            f"{str(params.get('comparison', '>')).strip()!r}, {num(params.get('value'), 0)})")


def _cc_if_pixel(gen, params, event_type):
    num, _ = _helpers()
    return (f"self._mb_if_pixel({num(params.get('x'), 0)}, {num(params.get('y'), 0)}, "
            f"{str(params.get('comparison', '>')).strip()!r}, {num(params.get('value'), 0)})")


CONDITION_CODEGEN = {
    "microbit_if_button": _cc_if_button,
    "microbit_if_gesture": _cc_if_gesture,
    "microbit_if_tilt": _cc_if_tilt,
    "microbit_if_pixel": _cc_if_pixel,
}


# ---------------------------------------------------------------------------
# Scene class-body code (K2), injected at the scene's extension marker: steps
# every board once per frame, after collision (the desktop's after_collision
# hook), and fires what they report as `on_<event>` on the board's instance.
# The scene's dispatchers (kivy_exporter.py) call every `_ext_<hook>__<extension>` method, so this
# extension shares the per-frame, touch and key hooks with any other.
# ---------------------------------------------------------------------------
SCENE_CODE = '''\n    # -- micro:bit (extension: microbit) ---------------------------------
    _MB_FIXED_EVENTS = %(fixed)r
    _MB_GESTURE_EVENTS = %(gestures)r

    def _mb_event_name(self, kind, detail):
        if kind == 'radio':
            return self._MB_FIXED_EVENTS['radio']
        if kind == 'gesture':
            gesture = self._MB_GESTURE_EVENTS.get(detail)
            return 'microbit_gesture_' + gesture if gesture else None
        return self._MB_FIXED_EVENTS.get('%%s:%%s' %% (kind, detail))

    def _ext_update__microbit(self, dt):
        boards = [i for i in list(self.instances)
                  if getattr(i, '_mb_sim', None) is not None and i._mb_sim() is not None]
        if not boards:
            return
        from microbit_sim import radio
        from microbit_sim.speaker import get_speaker
        radio.deliver([i._mb_sim() for i in boards])
        step = min(max(float(dt), 0.0), 0.1)
        for board in boards:
            for kind, detail in board._mb_sim().update(step):
                if kind == 'radio':
                    board.radio_string = str(detail)
                    board.radio_number = radio.as_number(detail)
                get_speaker().handle(kind, detail)
                name = self._mb_event_name(kind, detail)
                handler = getattr(board, 'on_' + name, None) if name else None
                if handler is not None:
                    handler()
        for board in boards:
            board._mb_draw(self.room_height)

    # -- touch and keyboard (K4) ---------------------------------------
    def _mb_entries(self):
        """The visible boards as touch.Board entries, topmost first."""
        from microbit_sim.touch import Board
        from microbit_sim.layout import strip_visible
        entries = []
        for inst in reversed(list(self.instances)):
            if getattr(inst, '_mb_sim', None) is None or not inst.visible:
                continue
            sim = inst._mb_sim()
            if sim is not None:
                entries.append(Board(inst, sim, inst._mb_layout(self.room_height),
                                     strip_visible(inst)))
        return entries

    def _mb_presses(self):
        presses = getattr(self, '_mb_press_state', None)
        if presses is None:
            presses = self._mb_press_state = {}
        return presses

    def _ext_touch_down__microbit(self, touch, mx, my, button):
        from microbit_sim import touch as mb_touch
        return mb_touch.press(self._mb_entries(), self._mb_presses(), button, mx, my)

    def _ext_touch_up__microbit(self, touch, mx, my, button):
        from microbit_sim import touch as mb_touch
        return mb_touch.release(self._mb_presses(), button, mx, my)

    def _ext_touch_move__microbit(self, touch, mx, my):
        from microbit_sim import touch as mb_touch
        presses = self._mb_presses()
        if not mb_touch.dragging(presses):
            return False
        mb_touch.follow(presses, mx, my)
        return True

    def _mb_key(self, key, down):
        from microbit_sim import touch as mb_touch
        name = mb_touch.KEY_NAMES.get(key)
        if name is None:
            return
        for inst in list(self.instances):
            if getattr(inst, '_mb_sim', None) is None:
                continue
            sim = inst._mb_sim()
            if sim is None or not mb_touch.keyboard_on(getattr(inst, 'microbit_keyboard', False)):
                continue
            held = getattr(inst, '_mb_tilt_keys', None)
            if held is None:
                held = inst._mb_tilt_keys = set()
            (mb_touch.key_down if down else mb_touch.key_up)(sim, held, name)

    def _ext_key_down__microbit(self, key):
        self._mb_key(key, True)

    def _ext_key_up__microbit(self, key):
        self._mb_key(key, False)
''' %{"fixed": _FIXED_EVENTS, "gestures": _GESTURE_EVENTS}


# ---------------------------------------------------------------------------
# Base-object class-body code, injected at base_object.py's extension marker
# (post-.format(), so { } are single). Mirrors handlers.py.
# ---------------------------------------------------------------------------
BASE_OBJECT_CODE = '''\n    # -- micro:bit (extension: microbit) ---------------------------------
    def _mb_sim(self):
        """This object's simulated micro:bit, created on first use; None for
        any object that is not a board (as simulator_of() on desktop)."""
        sim = getattr(self, '_mb_simulator', None)
        if sim is None:
            name = str(getattr(self, 'object_name', '') or '')
            if not (name.lower().startswith('microbit') or getattr(self, 'is_microbit', False)):
                return None
            from microbit_sim.simulator import MicrobitSimulator
            sim = self._mb_simulator = MicrobitSimulator()
        return sim

    @staticmethod
    def _mb_int(value, default=0):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default

    @classmethod
    def _mb_seconds(cls, value):
        return max(0.0, cls._mb_int(value, 0) / 1000.0)

    @staticmethod
    def _mb_compare(left, comparison, right):
        import operator as _op
        return {'<': _op.lt, '<=': _op.le, '==': _op.eq, '>=': _op.ge,
                '>': _op.gt, '!=': _op.ne}.get(comparison, _op.gt)(left, right)

    def _mb_show_image(self, spec, hold=0):
        sim = self._mb_sim()
        if sim is not None:
            try:
                sim.show_image(spec, hold=self._mb_seconds(hold) if hold else 0.0)
            except ValueError:
                pass

    def _mb_scroll_text(self, text, delay_ms=0):
        sim = self._mb_sim()
        if sim is not None:
            from microbit_sim.simulator import SCROLL_DELAY
            sim.scroll_text(str(text), self._mb_seconds(delay_ms) or SCROLL_DELAY)

    def _mb_show_number(self, value):
        sim = self._mb_sim()
        if sim is not None:
            try:
                number = float(value)
            except (TypeError, ValueError):
                number = 0.0
            sim.show_number(int(number) if number.is_integer() else number)

    def _mb_set_pixel(self, x, y, brightness=9):
        sim = self._mb_sim()
        if sim is not None:
            sim.set_pixel(self._mb_int(x), self._mb_int(y), self._mb_int(brightness, 9))

    def _mb_clear_display(self):
        sim = self._mb_sim()
        if sim is not None:
            sim.clear()

    def _mb_set_brightness(self, brightness):
        sim = self._mb_sim()
        if sim is not None:
            sim.set_brightness(self._mb_int(brightness, 255))

    def _mb_play_tone(self, frequency, duration):
        sim = self._mb_sim()
        if sim is not None:
            sim.play_tone(self._mb_int(frequency, 440), self._mb_int(duration, 500))

    def _mb_play_melody(self, spec, tempo=120):
        sim = self._mb_sim()
        if sim is not None:
            try:
                sim.play_melody(str(spec).strip(), self._mb_int(tempo, 120))
            except ValueError:
                pass

    def _mb_stop_sound(self):
        sim = self._mb_sim()
        if sim is not None:
            sim.stop_sound()

    def _mb_radio_set_group(self, group):
        sim = self._mb_sim()
        if sim is not None:
            sim.set_radio_group(self._mb_int(group, 0))

    def _mb_radio_send(self, value):
        sim = self._mb_sim()
        if sim is not None:
            sim.radio_send(value)

    def _mb_reading(self, sim, sensor):
        x, y, z = sim.acceleration
        if sensor == 'accelerometer x':
            return x
        if sensor == 'accelerometer y':
            return y
        if sensor == 'accelerometer z':
            return z
        if sensor == 'acceleration strength':
            return int(round((x * x + y * y + z * z) ** 0.5))
        if sensor == 'compass heading':
            return sim.compass_heading
        if sensor == 'light level':
            return sim.light_level
        if sensor == 'temperature':
            return sim.temperature
        if sensor == 'sound level':
            return sim.sound_level
        if sensor.startswith('pin ') and sensor.endswith(' analog'):
            try:
                return sim.pins_analog[int(sensor.split()[1])]
            except (ValueError, KeyError):
                return None
        return None

    def _mb_read_sensor(self, sensor, variable, is_global=False):
        sim = self._mb_sim()
        if sim is None or not variable:
            return
        value = self._mb_reading(sim, sensor)
        if value is None:
            return
        if is_global:
            __import__('main').set_global(variable, value)
        else:
            setattr(self, variable, value)

    def _mb_if_button(self, button):
        sim = self._mb_sim()
        if sim is None:
            return False
        if button == 'logo':
            return sim.logo_touched
        try:
            return sim.is_pressed(button)
        except KeyError:
            return False

    def _mb_if_gesture(self, gesture):
        sim = self._mb_sim()
        return sim is not None and sim.current_gesture == gesture

    def _mb_if_tilt(self, axis, comparison, value):
        sim = self._mb_sim()
        if sim is None or axis not in ('x', 'y', 'z'):
            return False
        return self._mb_compare(sim.acceleration['xyz'.index(axis)], comparison, value)

    def _mb_layout(self, room_h):
        """Where this board is, in room pixels (y down): centred on its sprite,
        or on its GameMaker point when it has none."""
        from microbit_sim.layout import board_layout, scale_of
        if self.has_sprite:
            cx, cy = self.x + self.width / 2.0, room_h - self.y - self.height / 2.0
        else:
            cx, cy = self.x, room_h - self.y - self.height
        return board_layout(cx, cy, scale_of(self))

    def _mb_draw(self, room_h):
        """Draw this board (and its sensor strip) as draw-queue commands in an
        instance-owned group on canvas.after, so it sits over the object's own
        sprite as on the desktop. Room coordinates are y-down; the draw-queue
        renderer does the flip. Scale and the strip toggle are read from the
        object properties (baked in by OBJECT_ATTRS) or instance variables microbit_scale /
        microbit_show_sensors; an instance variable wins, as option_of() does on the desktop."""
        sim = self._mb_sim()
        group = getattr(self, '_mb_group', None)
        if sim is None or not self.visible:
            if group is not None:
                group.clear()
            return
        if group is None:
            group = self._mb_group = InstructionGroup()
            self.canvas.after.add(group)
        group.clear()
        from microbit_sim.layout import strip_visible
        from microbit_sim.draw import board_commands, strip_commands
        layout = self._mb_layout(room_h)
        commands = board_commands(layout, sim, draw_body=not self.has_sprite)
        if strip_visible(self):
            commands += strip_commands(layout, sim)
        for cmd in commands:
            try:
                self._dq_render_cmd(group, cmd, room_h)
            except Exception as exc:
                print('[ERROR] micro:bit draw %s: %s' % (cmd.get('type'), exc))

    def _mb_if_pixel(self, x, y, comparison, value):
        sim = self._mb_sim()
        x, y = self._mb_int(x), self._mb_int(y)
        if sim is None or not (0 <= x < 5 and 0 <= y < 5):
            return False
        return self._mb_compare(sim.get_pixel(x, y), comparison, value)
'''
