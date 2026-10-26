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

register_action_tabs(MICROBIT_TAB)

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
