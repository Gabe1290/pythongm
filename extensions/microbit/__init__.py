#!/usr/bin/env python3
"""BBC micro:bit simulator, packaged as a folder extension.

Built one unit at a time -- docs/MICROBIT_EXTENSION_PLAN.md is the map.
What lives here so far:

* ``state.py`` -- the board's per-instance state under
  ``instance.extension_state["microbit"]``; ``on_instance_created`` below
  attaches a simulator to ``microbit*`` instances as a room builds (S1).
* ``simulator.py`` -- ``MicrobitSimulator``, the pure (no pygame, no Qt)
  board state. Only the 5x5 display buffer so far (S1); S2 fills it in.
"""

PLUGIN_NAME = "micro:bit"

from core.logger import get_logger
from .state import attach_simulator

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
