#!/usr/bin/env python3
"""BBC micro:bit simulator, packaged as a folder extension.

Built one unit at a time -- docs/MICROBIT_EXTENSION_PLAN.md is the map.
What lives here so far:

* ``state.py`` -- the board's per-instance state under
  ``instance.extension_state["microbit"]``; ``on_instance_created`` below
  attaches a simulator to ``microbit*`` instances as a room builds (S1).
* ``simulator.py`` -- ``MicrobitSimulator``, the pure (no pygame, no Qt)
  board state: the display and its queue (images, scrolling text,
  numbers), buttons, logo, pins, accelerometer gestures, compass, light,
  temperature and sound level; ``update(dt)`` returns what happened (S2).
* ``actions.py`` / ``handlers.py`` -- the display, sensor-read and condition
  actions: English schemas merged into ``ACTION_TYPES`` and the
  ``PluginExecutor`` that runs them on the acting board (S3).
* ``events.py`` / ``runtime.py`` -- the flat ``microbit_*`` event types and
  the frame update that steps every board and fires them (S4).
* ``input.py`` -- mouse clicks on the board's controls and the opt-in
  keyboard shortcuts, through the input hook (S6); the sensor strip's tilt
  pad, shake button and sliders (S7) are driven the same way.
* ``layout.py`` / ``renderer.py`` -- the board's geometry (pure) and the
  pygame overlay that draws it over its instance (S5), plus the sensor
  strip underneath it (S7).
* ``sound.py`` / ``melodies.py`` / ``audio.py`` -- notes and melodies (pure),
  the 21 built-in tunes, and the square-wave speaker on a reserved mixer
  channel (S8).
* ``radio.py`` -- delivery of radio messages between the boards in a room,
  by group (S9).
* ``translations.py`` -- French text for the auto-generated Blockly blocks (S10).
* ``font.py`` / ``images.py`` -- the device's 5x5 font and its 64 built-in
  images, generated from MIT-licensed micro:bit sources
  (``THIRD_PARTY_LICENSES.md``).
"""

PLUGIN_NAME = "micro:bit"

from core.logger import get_logger
from actions.core import register_action_tabs
from .state import attach_simulator
from .actions import PLUGIN_ACTIONS, MICROBIT_TAB
from .handlers import PluginExecutor
from .events import MICROBIT_EVENT_TYPES
from .translations import PLUGIN_GENERATED_BLOCK_TRANSLATIONS

register_action_tabs(MICROBIT_TAB)

PLUGIN_EVENTS = MICROBIT_EVENT_TYPES


def _frame_update_boards(game_runner):
    # Imported lazily: keeps pygame out of the IDE's schema-only load.
    from .runtime import update_microbits
    update_microbits(game_runner)


PLUGIN_FRAME_UPDATES = [(_frame_update_boards, "after_collision")]


def _draw_board(instance, screen):
    # Imported lazily: keeps pygame out of the IDE's schema-only load.
    from .renderer import draw_overlay
    draw_overlay(instance, screen)


PLUGIN_INSTANCE_OVERLAYS = [_draw_board]

# Clicks on the drawn board press its controls; keyboard shortcuts are opt-in
# per object (S6). See input.py.
from .input import INPUT_HANDLERS
PLUGIN_INPUT_HANDLERS = [INPUT_HANDLERS]

logger = get_logger(__name__)


def on_instance_created(instance, instance_data, room):
    """Instance-created hook: a ``microbit*``-named object, or one whose room
    entry sets ``is_microbit``, gets a simulator (S1)."""
    name = instance.object_name or ''
    if name.lower().startswith('microbit') or instance_data.get('is_microbit', False):
        from .simulator import MicrobitSimulator
        attach_simulator(instance, MicrobitSimulator())
        logger.debug(f"Created micro:bit: {instance.object_name}")


PLUGIN_INSTANCE_CREATED = [on_instance_created]
