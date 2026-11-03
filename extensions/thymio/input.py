#!/usr/bin/env python3
"""Keyboard and mouse control of a simulated robot's buttons (Stage B2).

This is the Thymio-specific input handling ``runtime/input_handler.py``
used to carry, verbatim in behaviour, now declared through the input hook
(runtime/extension_hooks ``PLUGIN_INPUT_HANDLERS``):

* arrow keys / space map to the robot's five capacitive buttons -- press
  sets the button and fires that robot's ``thymio_button_*`` event (and
  ``thymio_any_button``); release clears it and fires them again, as the real
  robot's ``onevent button.*`` handlers run on every change of state, press AND
  release (per instance, right after that instance's own keyboard events);
* a left click that lands on a button drawn on the robot body presses it and
  fires the events, and is swallowed (no ``mouse`` event fires for it); the
  matching release clears the button, fires them again and is swallowed too.
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


def fire_button_events(executor, instance, button) -> bool:
    """Run ``thymio_button_<button>`` and ``thymio_any_button`` on ``instance``
    when it defines them. Called on press AND on release -- the real Thymio runs
    a button's handler on every change, so a program that guards with "if the
    button is pressed" / "is released" behaves the same here. True if any ran.
    Shared with the playground runner, which has its own input path."""
    events = (instance.object_data or {}).get('events', {})
    fired = False
    for name in (f"thymio_button_{button}", "thymio_any_button"):
        if name in events:
            logger.debug(f"  🤖 Executing {name} for {instance.object_name}")
            try:
                executor.execute_event(instance, name, events)
            except Exception as e:
                logger.error(f"{name} failed: {e}")
            fired = True
    return fired


def _toggle_mute_once(instance):
    """key_down reaches every robot of the room: only the first one toggles, or two robots would cancel out."""
    try:
        robots = [i for i in instance.action_executor.game_runner.current_room.instances if _simulator(i) is not None]
        if robots and robots[0] is not instance:
            return
    except Exception:
        pass
    from . import audio
    audio.toggle_muted()


def key_down(instance, key):
    """Per-instance key press. True if a robot button event was fired."""
    sim = _simulator(instance)
    if sim is not None and key == 'm':
        _toggle_mute_once(instance)       # M mutes every robot; it is also free for the game's own use
        return False
    if sim is None or key not in _KEY_TO_BUTTON:
        return False
    button_name, _event_name = _KEY_TO_BUTTON[key]
    sim.set_button(button_name, True)
    return fire_button_events(instance.action_executor, instance, button_name)


def key_up(instance, key):
    """Per-instance key release: clear the mapped robot button."""
    sim = _simulator(instance)
    if sim is None or key not in _KEY_TO_BUTTON:
        return
    button_name = _KEY_TO_BUTTON[key][0]
    sim.set_button(button_name, False)
    fire_button_events(instance.action_executor, instance, button_name)


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
        fire_button_events(instance.action_executor, instance, hit)
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
        fire_button_events(instance.action_executor, instance, btn_name)
    return True


INPUT_HANDLERS = {
    "key_down": key_down,
    "key_up": key_up,
    "mouse_down": mouse_down,
    "mouse_up": mouse_up,
}
