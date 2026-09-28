#!/usr/bin/env python3
"""Keyboard and mouse control of a simulated robot's buttons (Stage B2).

This is the Thymio-specific input handling ``runtime/input_handler.py``
used to carry, verbatim in behaviour, now declared through the input hook
(runtime/extension_hooks ``PLUGIN_INPUT_HANDLERS``):

* arrow keys / space map to the robot's five capacitive buttons -- press
  sets the button and fires that robot's ``thymio_button_*`` event, release
  clears it (per instance, right after that instance's own keyboard events);
* a left click that lands on a button drawn on the robot body presses it and
  fires the event, and is swallowed (no ``mouse`` event fires for it); the
  matching release clears the button and is swallowed too.
"""
from core.logger import get_logger

from .state import simulator_of

logger = get_logger(__name__)

# key name -> (simulator button, event name)
_KEY_TO_BUTTON = {
    'up': ('forward', 'thymio_button_forward'),
    'down': ('backward', 'thymio_button_backward'),
    'left': ('left', 'thymio_button_left'),
    'right': ('right', 'thymio_button_right'),
    'space': ('center', 'thymio_button_center'),
}

# Mouse presses that landed on a robot button, so the release maps back to
# the same instance/button: {pygame_button: (instance, button_name)}
_mouse_presses = {}


_simulator = simulator_of


def key_down(instance, key):
    """Per-instance key press. True if a robot button event was fired."""
    sim = _simulator(instance)
    if sim is None or key not in _KEY_TO_BUTTON:
        return False
    button_name, event_name = _KEY_TO_BUTTON[key]
    sim.set_button(button_name, True)
    events = (instance.object_data or {}).get('events', {})
    if event_name in events:
        logger.debug(f"  🤖 Executing {event_name} for {instance.object_name}")
        instance.action_executor.execute_event(instance, event_name, events)
        return True
    return False


def key_up(instance, key):
    """Per-instance key release: clear the mapped robot button."""
    sim = _simulator(instance)
    if sim is None or key not in _KEY_TO_BUTTON:
        return
    sim.set_button(_KEY_TO_BUTTON[key][0], False)


def mouse_down(game_runner, button, mouse_x, mouse_y):
    """Hit-test robot buttons under a left click; True swallows the click.
    Screen space on purpose: the renderer draws in screen space too."""
    if button != 1 or not game_runner.current_room:
        return False
    from .renderer import shared_renderer
    renderer = shared_renderer()
    for instance in game_runner.current_room.instances:
        sim = _simulator(instance)
        if sim is None:
            continue
        hit = renderer.hit_test_button(sim.x, sim.y, sim.angle, mouse_x, mouse_y)
        if not hit:
            continue
        sim.set_button(hit, True)
        _mouse_presses[button] = (instance, hit)
        event_name = f"thymio_button_{hit}"
        events = (instance.object_data or {}).get('events', {})
        if event_name in events:
            logger.debug(f"  🤖 Mouse-clicked {event_name} on {instance.object_name}")
            instance.action_executor.execute_event(instance, event_name, events)
        return True
    return False


def mouse_up(game_runner, button, mouse_x, mouse_y):
    """Release a robot button this mouse button had pressed; True swallows."""
    press = _mouse_presses.pop(button, None)
    if press is None:
        return False
    instance, btn_name = press
    sim = simulator_of(instance)
    if sim is not None:
        sim.set_button(btn_name, False)
    return True


INPUT_HANDLERS = {
    "key_down": key_down,
    "key_up": key_up,
    "mouse_down": mouse_down,
    "mouse_up": mouse_up,
}
