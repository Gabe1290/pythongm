#!/usr/bin/env python3
"""Mouse and keyboard control of a simulated micro:bit (Stage S6).

Declared through the input hook (``PLUGIN_INPUT_HANDLERS``):

* **Mouse, always on.** A left click on button A/B, the touch logo or pad 0/1/2
  presses it, and it stays down until the mouse button is released. A right
  click on A or B presses both (the A+B chord a single mouse can't otherwise
  make). Clicks that land on the board are swallowed, so no authored
  ``mouse`` event also fires for them. Pressing only sets the simulator's
  state; the frame update fires the events (S4).
* **Keyboard, opt-in** (``microbit_keyboard: true`` on the object or instance;
  off by default so a game's own A/B/arrow keys are left alone): ``A``/``B``
  are the buttons, the arrow keys tilt the board, ``S`` shakes it.
"""
from .layout import (hit_test, layout_for, strip_layout, strip_hit_test,
                     strip_visible, tilt_from_pos, slider_value)
from .simulator import REST_ACCELERATION
from .state import option_of, scratch, simulator_of

TILT = 1000                      # milli-g held while a tilt key is down
TILT_KEYS = ("left", "right", "up", "down")

# pygame mouse buttons
LEFT, RIGHT = 1, 3

# {pygame_button: (instance, [targets])} so a release maps back to the same
# board and controls even if the board moved in between.
_mouse_presses = {}


_SETTERS = {
    "light": "set_light_level", "temperature": "set_temperature",
    "compass": "set_compass_heading", "sound": "set_sound_level",
}


def _apply(instance, sim, target, down, x=0, y=0):
    """Press (``down``) or release one control. Strip controls also take the
    pointer position: the tilt pad and the sliders follow it while held."""
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
            rect = strip_layout(layout_for(instance)).tilt
            sim.set_acceleration(*tilt_from_pos(rect, x, y))
        else:
            sim.set_acceleration(*REST_ACCELERATION)       # springs back
    elif target.startswith("slider:"):
        if down:
            name = target[7:]
            track = strip_layout(layout_for(instance)).sliders[name]
            getattr(sim, _SETTERS[name])(slider_value(name, track, x))


def drags():
    """``[(instance, target)]`` for the strip controls a mouse button is
    holding (the tilt pad and sliders), for the frame update to keep
    following the pointer (the input hook has no mouse-motion kind)."""
    return [(inst, t) for inst, targets in _mouse_presses.values()
            for t in targets if t == "tilt" or t.startswith("slider:")]


def follow(x, y):
    """Move every held tilt pad / slider to the pointer at ``(x, y)``."""
    for instance, target in drags():
        sim = simulator_of(instance)
        if sim is not None:
            _apply(instance, sim, target, True, x, y)


def mouse_down(game_runner, button, mouse_x, mouse_y):
    """Hit-test the boards under a click; True swallows it. Screen space on
    purpose: the overlay draws in screen space too."""
    if button not in (LEFT, RIGHT) or not game_runner.current_room:
        return False
    for instance in reversed(game_runner.current_room.instances):   # topmost first
        sim = simulator_of(instance)
        if sim is None or not getattr(instance, "visible", True):
            continue
        layout = layout_for(instance)
        target = hit_test(layout, mouse_x, mouse_y)
        if target is None and button == LEFT and strip_visible(instance):
            target = strip_hit_test(strip_layout(layout), mouse_x, mouse_y)
        if target is None:
            continue
        targets = [target]
        if button == RIGHT and target in ("a", "b"):
            targets = ["a", "b"]
        elif button == RIGHT:
            return True              # a right click elsewhere on the board does nothing
        mouse_up(game_runner, button, mouse_x, mouse_y)   # a release we never saw
        for each in targets:
            _apply(instance, sim, each, True, mouse_x, mouse_y)
        _mouse_presses[button] = (instance, targets)
        return True
    return False


def mouse_up(game_runner, button, mouse_x, mouse_y):
    """Release what this mouse button pressed; True swallows the release."""
    press = _mouse_presses.pop(button, None)
    if press is None:
        return False
    instance, targets = press
    sim = simulator_of(instance)
    if sim is not None:
        for each in targets:
            _apply(instance, sim, each, False, mouse_x, mouse_y)
    return True


def _keyboard_on(instance):
    value = option_of(instance, "microbit_keyboard", False)
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)


def _retilt(instance, sim):
    held = scratch(instance).setdefault("tilt_keys", set())
    x = (TILT if "right" in held else 0) - (TILT if "left" in held else 0)
    y = (TILT if "up" in held else 0) - (TILT if "down" in held else 0)
    if x or y:
        sim.set_acceleration(x, y, 0)
    else:
        sim.set_acceleration(*REST_ACCELERATION)


def key_down(instance, key):
    """Per-instance key press (opt-in). True if the key drove the board."""
    sim = simulator_of(instance)
    if sim is None or not _keyboard_on(instance):
        return False
    if key in ("a", "b"):
        sim.set_button(key, True)
    elif key == "s":
        sim.shake()
    elif key in TILT_KEYS:
        scratch(instance).setdefault("tilt_keys", set()).add(key)
        _retilt(instance, sim)
    else:
        return False
    return True


def key_up(instance, key):
    sim = simulator_of(instance)
    if sim is None or not _keyboard_on(instance):
        return
    if key in ("a", "b"):
        sim.set_button(key, False)
    elif key in TILT_KEYS:
        scratch(instance).setdefault("tilt_keys", set()).discard(key)
        _retilt(instance, sim)


INPUT_HANDLERS = {
    "key_down": key_down,
    "key_up": key_up,
    "mouse_down": mouse_down,
    "mouse_up": mouse_up,
}
