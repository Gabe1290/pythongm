"""Touch and keyboard control of the drawn micro:bit on Kivy (Stage P, unit K4).

Shipped into a Kivy export as ``microbit_sim/touch.py``; pure (no Kivy, no
pygame). It mirrors ``input.py`` -- which stays the source of truth for the
rules -- but takes the board geometry explicitly instead of reading a pygame
game instance. tests/test_kivy_microbit_touch.py drives both with the same
gestures and compares the simulator state they leave behind.

A ``Board`` pairs a simulator with its layout. Coordinates are room pixels,
y down -- the space ``kivy_draw`` draws in.
"""
from .layout import (hit_test, strip_hit_test, tilt_from_pos, slider_value,
                     strip_layout)
from .simulator import REST_ACCELERATION

LEFT, RIGHT = "left", "right"          # Kivy's touch.button names
TILT = 1000                            # milli-g held while a tilt key is down
TILT_KEYS = ("left", "right", "up", "down")

# Kivy 1.x keycodes -> the key names input.py uses (a, b, s and the arrows).
KEY_NAMES = {97: "a", 98: "b", 115: "s", 273: "up", 274: "down", 275: "right", 276: "left"}

_SETTERS = {
    "light": "set_light_level", "temperature": "set_temperature",
    "compass": "set_compass_heading", "sound": "set_sound_level",
}


class Board:
    """One drawn board: its simulator, layout and whether the strip shows."""

    def __init__(self, owner, sim, layout, show_strip=True):
        self.owner = owner
        self.sim = sim
        self.layout = layout
        self.strip = strip_layout(layout)
        self.show_strip = show_strip


def apply(board, target, down, x=0, y=0):
    """Press (``down``) or release one control; the tilt pad and sliders also
    follow the pointer position."""
    sim = board.sim
    if target in ("a", "b"):
        sim.set_button(target, down)
    elif target == "logo":
        sim.set_logo_touched(down)
    elif target.startswith("pin"):
        sim.set_pin_touched(int(target[3:]), down)
    elif target == "shake":
        if down:
            sim.shake()
    elif target == "tilt":
        if down:
            sim.set_acceleration(*tilt_from_pos(board.strip.tilt, x, y))
        else:
            sim.set_acceleration(*REST_ACCELERATION)       # springs back
    elif target.startswith("slider:"):
        if down:
            name = target[7:]
            getattr(sim, _SETTERS[name])(slider_value(name, board.strip.sliders[name], x))


def press(boards, presses, button, x, y):
    """A pointer goes down. ``boards`` is topmost first; ``presses`` maps the
    pointer button to ``(board, [targets])`` so the release finds it again.
    True if the press landed on a board (the caller swallows it)."""
    if button not in (LEFT, RIGHT):
        return False
    for board in boards:
        target = hit_test(board.layout, x, y)
        if target is None and button == LEFT and board.show_strip:
            target = strip_hit_test(board.strip, x, y)
        if target is None:
            continue
        targets = [target]
        if button == RIGHT and target in ("a", "b"):
            targets = ["a", "b"]                 # the A+B chord
        elif button == RIGHT:
            return True                          # a right click elsewhere does nothing
        release(presses, button, x, y)           # a release we never saw
        for each in targets:
            apply(board, each, True, x, y)
        presses[button] = (board, targets)
        return True
    return False


def release(presses, button, x, y):
    """The pointer goes up. True if it was holding something."""
    held = presses.pop(button, None)
    if held is None:
        return False
    board, targets = held
    for each in targets:
        apply(board, each, False, x, y)
    return True


def follow(presses, x, y):
    """Move every held tilt pad / slider to the pointer."""
    for board, targets in list(presses.values()):
        for target in targets:
            if target == "tilt" or target.startswith("slider:"):
                apply(board, target, True, x, y)


def dragging(presses):
    return any(t == "tilt" or t.startswith("slider:")
               for _, targets in presses.values() for t in targets)


def key_down(sim, tilt_keys, key):
    """A key goes down on a board whose keyboard is on. True if it drove it."""
    if key in ("a", "b"):
        sim.set_button(key, True)
    elif key == "s":
        sim.shake()
    elif key in TILT_KEYS:
        tilt_keys.add(key)
        _retilt(sim, tilt_keys)
    else:
        return False
    return True


def key_up(sim, tilt_keys, key):
    if key in ("a", "b"):
        sim.set_button(key, False)
    elif key in TILT_KEYS:
        tilt_keys.discard(key)
        _retilt(sim, tilt_keys)


def _retilt(sim, held):
    x = (TILT if "right" in held else 0) - (TILT if "left" in held else 0)
    y = (TILT if "up" in held else 0) - (TILT if "down" in held else 0)
    if x or y:
        sim.set_acceleration(x, y, 0)
    else:
        sim.set_acceleration(*REST_ACCELERATION)


def keyboard_on(value):
    """The ``microbit_keyboard`` option as input.py reads it."""
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)
