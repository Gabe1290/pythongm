#!/usr/bin/env python3
"""Thymio educational robot, packaged as a folder extension.

Being moved out of core one stage at a time — docs/THYMIO_EXTENSION_PLAN.md
is the map. What lives here so far:

* ``actions.py`` — ``THYMIO_ACTIONS`` (the GM80-dialog ``ActionDefinition``
  schemas the Thymio panels and the Aseba exporter read) and ``THYMIO_TAB``,
  the "Thymio" tab of the GM80 action dialog, registered below (Stage A1).
* ``handlers.py`` — the 28 runtime handlers. ``PluginExecutor`` is what the
  loader registers in the game process; ``register_thymio_actions`` is the
  same set for the playground runner, which has no plugin loader (A2).
* ``events.py`` — the 14 robot events, ``PLUGIN_EVENTS`` (A3).
* ``simulator.py`` — ``ThymioSimulator``: differential drive, proximity/
  ground sensors, LEDs, tones, timers (A4). Pure logic; the engine still
  constructs it for ``thymio*`` instances until Stage B.
* ``runtime.py`` — the per-frame simulator step + sensor events, run
  through the ``after_collision`` frame-update hook (A5).

The rest — renderer, input, playground editor, the Aseba/Open Roberta
interop — still lives in core and moves in Stages B–F.
"""

PLUGIN_NAME = "Thymio Robot"

from actions.core import register_action_tabs
from .actions import THYMIO_ACTIONS, THYMIO_TAB
from .handlers import PluginExecutor, register_thymio_actions
from .events import THYMIO_EVENT_TYPES

register_action_tabs(THYMIO_TAB)

# The 14 robot events (buttons, sensors, timers, sound, IR). Each has a
# Blockly block of the same name, so it is gated by the Blockly config like
# a core event (A3).
PLUGIN_EVENTS = THYMIO_EVENT_TYPES
PLUGIN_EVENT_BLOCKLY_MAP = {name: name for name in THYMIO_EVENT_TYPES}


def _frame_update_robots(game_runner):
    # Imported lazily: pygame stays out of the IDE's schema-only load.
    from .runtime import update_thymio_robots
    update_thymio_robots(game_runner)


PLUGIN_FRAME_UPDATES = [(_frame_update_robots, "after_collision")]
