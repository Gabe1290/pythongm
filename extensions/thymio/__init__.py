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
  ground sensors, LEDs, tones, timers (A4).
* ``state.py`` — the robot's per-instance state under
  ``instance.extension_state["thymio"]``; ``on_instance_created`` below
  attaches a simulator to ``thymio*`` instances as a room builds (B3).
* ``runtime.py`` — the per-frame simulator step + sensor events, run
  through the ``after_collision`` frame-update hook (A5).
* ``renderer.py`` — ``ThymioRenderer`` (robot body, LEDs, sensor rays,
  button hit-testing); ``draw_robot`` below is the instance overlay that
  draws every robot over the room (B1).
* ``input.py`` — keyboard/mouse control of the robot's buttons, through
  the input hook (B2).
* ``editor/`` — the arena-authoring editor (C1).
* ``playground_runner.py`` — ``PlaygroundRunnerWindow``: a standalone
  simulation window that embeds pygame in Qt and runs linked objects'
  code against a playground arena, independent of a full game project (C2).
* ``playground_window.py`` — ``ThymioPlaygroundWindow``: the live test/
  config window for a single robot (C3b). ``PygameWidget``, the generic
  pygame-in-Qt widget it and ``playground_runner.py`` both use, stayed in
  core (``widgets/pygame_widget.py``, C3a) since Block World reuses it too.

The rest — the Aseba/Open Roberta interop — still lives in core and moves
in Stages D–F.
"""

PLUGIN_NAME = "Thymio Robot"

from core.logger import get_logger
from actions.core import register_action_tabs
from .state import attach_simulator, simulator_of, is_robot

logger = get_logger(__name__)
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


def draw_robot(instance, screen):
    """Instance-overlay hook: draw a robot body over its instance (B1)."""
    sim = simulator_of(instance)
    if sim is None:
        return
    from .renderer import shared_renderer
    shared_renderer().render(screen, sim.get_render_data())


PLUGIN_INSTANCE_OVERLAYS = [draw_robot]


def on_instance_created(instance, instance_data, room):
    """Instance-created hook: a ``thymio*``-named object, or one whose room
    entry sets ``is_thymio``, gets a simulator at its start position (B3)."""
    name = instance.object_name or ''
    if name.lower().startswith('thymio') or instance_data.get('is_thymio', False):
        from .simulator import ThymioSimulator
        attach_simulator(instance, ThymioSimulator(x=instance.x, y=instance.y, angle=0))
        logger.debug(f"🤖 Created Thymio robot: {instance.object_name}")


PLUGIN_INSTANCE_CREATED = [on_instance_created]

# Arrow keys / space drive the robot's buttons; a click on a drawn button
# presses it (B2). See input.py.
from .input import INPUT_HANDLERS
PLUGIN_INPUT_HANDLERS = [INPUT_HANDLERS]
