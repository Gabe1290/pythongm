"""Thymio is becoming an EXTENSION (docs/THYMIO_EXTENSION_PLAN.md).

These pin each move: what now lives in extensions/thymio, that core no
longer carries a copy, and that the extension is discovered and wired
through the loader. Behavioural Thymio coverage stays in the test_thymio_*
files -- this file is only about WHERE the code lives.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# A1 — action schemas
# ---------------------------------------------------------------------------

def test_action_schemas_live_in_the_extension():
    from extensions.thymio.actions import THYMIO_ACTIONS, THYMIO_TAB
    from actions.core import ActionDefinition
    assert len(THYMIO_ACTIONS) == 28
    assert all(isinstance(a, ActionDefinition) for a in THYMIO_ACTIONS.values())
    assert all(a.tab == "thymio" for a in THYMIO_ACTIONS.values())
    assert THYMIO_TAB["thymio"]["name"] == "Thymio"


def test_core_no_longer_carries_the_schemas():
    assert not (REPO_ROOT / "actions" / "thymio_actions.py").exists()
    import actions
    assert not hasattr(actions, "THYMIO_ACTIONS")
    src = (REPO_ROOT / "actions" / "core.py").read_text(encoding="utf-8")
    assert '"thymio":' not in src, "the Thymio tab is the extension's now"


def test_manifest_declares_every_action():
    from extensions.thymio.actions import THYMIO_ACTIONS
    manifest = json.loads((REPO_ROOT / "extensions" / "thymio" / "extension.json")
                          .read_text(encoding="utf-8"))
    assert set(manifest["provides_actions"]) == set(THYMIO_ACTIONS)
    assert manifest["enabled"] is True


# ---------------------------------------------------------------------------
# A2 — runtime handlers
# ---------------------------------------------------------------------------

def test_handlers_live_in_the_extension_as_a_plugin_executor():
    from extensions.thymio.actions import THYMIO_ACTIONS
    from extensions.thymio.handlers import PluginExecutor, register_thymio_actions
    ex = PluginExecutor()
    for name in THYMIO_ACTIONS:
        assert callable(getattr(ex, f"execute_{name}_action", None)), name
    captured = {}

    class _Sink:
        def register_custom_action(self, n, h):
            captured[n] = h

    register_thymio_actions(_Sink())
    assert set(captured) == set(THYMIO_ACTIONS)


def test_core_no_longer_carries_the_handlers():
    assert not (REPO_ROOT / "runtime" / "thymio_action_handlers.py").exists()
    src = (REPO_ROOT / "runtime" / "game_runner.py").read_text(encoding="utf-8")
    assert "register_thymio_actions" not in src
    assert "thymio_action_handlers" not in src


def test_game_executor_gets_the_handlers_through_the_loader():
    """GameRunner no longer registers Thymio handlers itself; load_all_plugins
    (which it calls) does, via the extension's PluginExecutor."""
    from runtime.action_executor import ActionExecutor
    from events.plugin_loader import load_all_plugins
    ex = ActionExecutor(game_runner=None)
    assert "thymio_set_motor_speed" not in ex.action_handlers
    load_all_plugins(ex)
    assert "thymio_set_motor_speed" in ex.action_handlers
    assert "thymio_if_variable" in ex.action_handlers

    class _Inst:
        thymio_simulator = None

    assert ex.action_handlers["thymio_if_proximity"](_Inst(), {}) is False


# ---------------------------------------------------------------------------
# A3 — event types
# ---------------------------------------------------------------------------

def test_events_live_in_the_extension_and_use_the_real_event_type():
    from extensions.thymio import PLUGIN_EVENTS, PLUGIN_EVENT_BLOCKLY_MAP
    from extensions.thymio.events import THYMIO_EVENT_TYPES, is_thymio_event
    from events.event_types import EventType
    assert PLUGIN_EVENTS is THYMIO_EVENT_TYPES and len(THYMIO_EVENT_TYPES) == 14
    assert all(type(e) is EventType for e in THYMIO_EVENT_TYPES.values())
    assert PLUGIN_EVENT_BLOCKLY_MAP == {n: n for n in THYMIO_EVENT_TYPES}
    assert is_thymio_event("thymio_button_forward") and not is_thymio_event("create")


def test_core_no_longer_carries_the_events():
    assert not (REPO_ROOT / "events" / "thymio_events.py").exists()
    src = (REPO_ROOT / "events" / "event_types.py").read_text(encoding="utf-8")
    assert "THYMIO_EVENT_TYPES" not in src and "thymio_events" not in src


def test_events_register_through_the_loader_with_blockly_gating():
    from events.plugin_loader import load_all_plugins
    from events.event_types import (
        EVENT_TYPES, EVENT_TO_BLOCKLY_MAP, get_available_events,
    )
    from config.blockly_config import BlocklyConfig
    load_all_plugins()
    assert "thymio_button_forward" in EVENT_TYPES
    assert EVENT_TO_BLOCKLY_MAP["thymio_button_forward"] == "thymio_button_forward"
    # Gated by the Blockly config exactly as before the move.
    names = {e.name for e in get_available_events(BlocklyConfig.get_beginner())}
    assert "thymio_button_forward" not in names
    names = {e.name for e in get_available_events(BlocklyConfig.get_thymio())}
    assert "thymio_button_forward" in names


# ---------------------------------------------------------------------------
# A4 — simulator
# ---------------------------------------------------------------------------

def test_simulator_lives_in_the_extension():
    from extensions.thymio.simulator import ThymioSimulator
    sim = ThymioSimulator(x=10, y=20, angle=0)
    assert (sim.x, sim.y) == (10, 20)
    assert not (REPO_ROOT / "runtime" / "thymio_simulator.py").exists()


# ---------------------------------------------------------------------------
# A5 — per-frame simulation through the after_collision hook
# ---------------------------------------------------------------------------

def test_robot_frame_update_is_registered_and_core_method_is_gone():
    from events.plugin_loader import load_all_plugins
    from runtime import extension_hooks
    from runtime.game_runner import GameRunner
    load_all_plugins()
    phases = {getattr(f, "__name__", ""): p for f, p in extension_hooks.get_frame_updates()}
    assert phases.get("_frame_update_robots") == "after_collision"
    assert not hasattr(GameRunner, "update_thymio_robots")
    src = (REPO_ROOT / "runtime" / "game_runner.py").read_text(encoding="utf-8")
    assert 'run_frame_updates(self, "after_collision")' in src


def test_frame_update_advances_robots_and_fires_sensor_events():
    """Drive the extension's update with a minimal stand-in runner: the
    robot's position follows its simulator and a reported sensor event
    reaches the instance's event dispatch."""
    from types import SimpleNamespace
    from extensions.thymio.runtime import update_thymio_robots

    fired = []

    class _Exec:
        def execute_event(self, inst, name, events):
            fired.append(name)

    class _Sim:
        x, y = 40.0, 50.0

        def update(self, dt, obstacles, screen):
            self.x += 1
            return {"proximity_update": True, "timer_0": False}

    robot = SimpleNamespace(
        extension_state={"thymio": {"simulator": _Sim()}}, x=0, y=0,
        object_data={"events": {"thymio_proximity_update": {}, "thymio_timer_0": {}}},
        action_executor=_Exec(), _cached_object_data={}, sprite=None)
    wall = SimpleNamespace(extension_state={}, x=10, y=10,
                           _cached_object_data={"solid": True},
                           sprite=SimpleNamespace(width=8, height=8))
    runner = SimpleNamespace(current_room=SimpleNamespace(instances=[robot, wall]),
                             screen=None)
    update_thymio_robots(runner)
    assert (robot.x, robot.y) == (41.0, 50.0)
    assert fired == ["thymio_proximity_update"]


# ---------------------------------------------------------------------------
# B1 — renderer as an instance overlay
# ---------------------------------------------------------------------------

def test_renderer_lives_in_the_extension_and_draws_through_the_overlay():
    from types import SimpleNamespace
    from events.plugin_loader import load_all_plugins
    from runtime import extension_hooks
    from extensions.thymio import renderer as renderer_mod
    assert not (REPO_ROOT / "runtime" / "thymio_renderer.py").exists()
    src = (REPO_ROOT / "runtime" / "game_runner.py").read_text(encoding="utf-8")
    assert "thymio_simulator.get_render_data" not in src

    load_all_plugins()
    names = [getattr(f, "__name__", "") for f in extension_hooks.get_instance_overlays()]
    assert "draw_robot" in names

    drawn = []
    real = renderer_mod.ThymioRenderer.render
    renderer_mod.ThymioRenderer.render = lambda self, screen, data: drawn.append(data)
    try:
        import extensions.thymio as ext
        robot = SimpleNamespace(extension_state={"thymio": {"simulator": SimpleNamespace(
            get_render_data=lambda: {"x": 1})}})
        ext.draw_robot(robot, object())
        ext.draw_robot(SimpleNamespace(extension_state={}), object())
        ext.draw_robot(SimpleNamespace(), object())
    finally:
        renderer_mod.ThymioRenderer.render = real
    assert drawn == [{"x": 1}]


# ---------------------------------------------------------------------------
# B2 — button input through the input hook
# ---------------------------------------------------------------------------

def _robot(events):
    from types import SimpleNamespace
    fired = []
    presses = []

    class _Sim:
        x, y, angle = 100.0, 100.0, 0.0

        def set_button(self, name, state):
            presses.append((name, state))

    class _Exec:
        def execute_event(self, inst, name, evs):
            fired.append(name)

    robot = SimpleNamespace(extension_state={"thymio": {"simulator": _Sim()}},
                            object_name="thymio_1", object_data={"events": events},
                            action_executor=_Exec())
    return robot, presses, fired


def test_input_handlers_are_registered_and_core_has_no_thymio_input():
    from events.plugin_loader import load_all_plugins
    from runtime import extension_hooks
    from extensions.thymio.input import INPUT_HANDLERS
    load_all_plugins()
    # The loader imports the extension under a synthetic package name, so
    # its function objects differ from a direct import -- compare by name.
    registered = [
        {k: (f.__module__.rsplit(".", 1)[-1], f.__name__) for k, f in h.items()}
        for h in extension_hooks.get_input_handlers()
    ]
    assert {k: ("input", k) for k in INPUT_HANDLERS} in registered
    assert set(INPUT_HANDLERS) == {"key_down", "key_up", "mouse_down", "mouse_up"}
    src = (REPO_ROOT / "runtime" / "input_handler.py").read_text(encoding="utf-8")
    for ident in ("is_thymio", "thymio_simulator", "thymio_button",
                  "_handle_thymio", "thymio_renderer"):
        assert ident not in src, ident
    src = (REPO_ROOT / "runtime" / "game_runner.py").read_text(encoding="utf-8")
    assert "thymio_renderer" not in src and "_thymio_mouse_presses" not in src


def test_keys_press_and_release_robot_buttons():
    from types import SimpleNamespace
    from extensions.thymio import input as inp
    robot, presses, fired = _robot({"thymio_button_forward": {}})
    assert inp.key_down(robot, "up") is True           # event fired
    assert inp.key_down(robot, "space") is False       # button set, no event
    assert inp.key_down(robot, "a") is False           # unmapped key
    inp.key_up(robot, "up")
    assert presses == [("forward", True), ("center", True), ("forward", False)]
    assert fired == ["thymio_button_forward"]
    assert inp.key_down(SimpleNamespace(extension_state={}), "up") is False


def test_click_on_a_drawn_button_presses_it_and_is_swallowed():
    from types import SimpleNamespace
    from extensions.thymio import input as inp, renderer as renderer_mod
    robot, presses, fired = _robot({"thymio_button_center": {}})
    runner = SimpleNamespace(current_room=SimpleNamespace(instances=[robot]))
    real = renderer_mod.ThymioRenderer.hit_test_button
    renderer_mod.ThymioRenderer.hit_test_button = \
        lambda self, rx, ry, ang, mx, my: "center" if (mx, my) == (100, 100) else None
    try:
        assert inp.mouse_down(runner, 1, 5, 5) is False        # miss
        assert inp.mouse_down(runner, 3, 100, 100) is False    # not left button
        assert inp.mouse_down(runner, 1, 100, 100) is True     # hit
        assert inp.mouse_up(runner, 1, 100, 100) is True       # release maps back
        assert inp.mouse_up(runner, 1, 100, 100) is False      # nothing pending
    finally:
        renderer_mod.ThymioRenderer.hit_test_button = real
    assert presses == [("center", True), ("center", False)]
    assert fired == ["thymio_button_center"]


# ---------------------------------------------------------------------------
# B3 — robot state in extension_state, attached by the instance-created hook
# ---------------------------------------------------------------------------

def test_core_instance_and_room_carry_no_robot_state():
    from runtime.instance import GameInstance
    inst = GameInstance("obj", 0, 0, {}, action_executor=None)
    assert not hasattr(inst, "is_thymio") and not hasattr(inst, "thymio_simulator")
    assert inst.custom_rendered is False and inst.extension_state == {}
    for fname in ("runtime/room.py", "runtime/instance.py"):
        src = (REPO_ROOT / fname).read_text(encoding="utf-8")
        assert "thymio" not in src.lower(), fname


def test_room_build_attaches_a_simulator_through_the_hook():
    from events.plugin_loader import load_all_plugins
    from runtime.game_runner import GameRoom
    from extensions.thymio.state import simulator_of
    load_all_plugins()
    room = GameRoom("r", {"width": 200, "height": 200, "instances": [
        {"object": "thymio_bot", "x": 40, "y": 50},
        {"object": "obj_wall", "x": 10, "y": 10},
        {"object": "obj_flagged", "x": 1, "y": 2, "is_thymio": True},
    ]}, action_executor=None)
    bot, wall, flagged = room.instances
    sim = simulator_of(bot)
    assert sim is not None and (sim.x, sim.y) == (40, 50)
    assert bot.custom_rendered is True
    assert simulator_of(wall) is None and wall.custom_rendered is False
    assert simulator_of(flagged) is not None


# ---------------------------------------------------------------------------
# C1 — the playground (arena) editor package
# ---------------------------------------------------------------------------

def test_playground_editor_package_lives_in_the_extension():
    assert not (REPO_ROOT / "editors" / "playground_editor").exists()
    pkg = REPO_ROOT / "extensions" / "thymio" / "editor"
    assert {p.name for p in pkg.glob("*.py")} >= {
        "__init__.py", "playground_canvas.py", "playground_elements.py",
        "playground_properties.py", "playground_tool_palette.py",
        "playground_undo_commands.py", "color_manager.py"}
    # Self-imports are relative, so the package works under the loader's
    # synthetic package name too.
    for p in pkg.glob("*.py"):
        assert "editors.playground_editor" not in p.read_text(encoding="utf-8"), p.name
    from extensions.thymio.editor.playground_elements import PlaygroundWall, PlaygroundRobot
    assert PlaygroundWall and PlaygroundRobot


# ---------------------------------------------------------------------------
# C2 — the standalone playground (arena) simulation runner
# ---------------------------------------------------------------------------

def test_playground_runner_lives_in_the_extension():
    assert not (REPO_ROOT / "runtime" / "playground_runner.py").exists()
    from extensions.thymio.playground_runner import PlaygroundRunnerWindow
    assert callable(PlaygroundRunnerWindow)
    src = (REPO_ROOT / "extensions" / "thymio" / "playground_runner.py").read_text(encoding="utf-8")
    assert "runtime.playground_runner" not in src


# ---------------------------------------------------------------------------
# C3a — PygameWidget extracted to a shared core home (block_world reuses it)
# ---------------------------------------------------------------------------

def test_pygame_widget_is_shared_not_extension_owned():
    """PygameWidget has zero Thymio-specific code and block_world_editor
    reuses it verbatim -- it must live somewhere BOTH extensions can import
    without one depending on the other. (widgets/thymio_playground.py, which
    re-exported it in C3a, is itself gone as of C3b -- see the next test.)"""
    from widgets.pygame_widget import PygameWidget
    from extensions.thymio.playground_window import PygameWidget as ReExported
    assert PygameWidget is ReExported
    src = (REPO_ROOT / "editors" / "block_world_editor" / "window.py").read_text(encoding="utf-8")
    assert "widgets.pygame_widget import PygameWidget" in src
    assert "widgets.thymio_playground" not in src
    tp_src = (REPO_ROOT / "extensions" / "thymio" / "playground_window.py").read_text(encoding="utf-8")
    assert "class PygameWidget" not in tp_src


# ---------------------------------------------------------------------------
# C3b — the live test/config window
# ---------------------------------------------------------------------------

def test_playground_window_lives_in_the_extension():
    assert not (REPO_ROOT / "widgets" / "thymio_playground.py").exists()
    from extensions.thymio.playground_window import ThymioPlaygroundWindow
    assert callable(ThymioPlaygroundWindow)
    src = (REPO_ROOT / "extensions" / "thymio" / "playground_window.py").read_text(encoding="utf-8")
    assert "widgets.thymio_playground" not in src
    assert "class PygameWidget" not in src, "PygameWidget stayed in core (C3a)"
    widgets_init = (REPO_ROOT / "widgets" / "__init__.py").read_text(encoding="utf-8")
    assert "__getattr__" not in widgets_init, "the lazy accessor should be gone"
    assert "'ThymioPlaygroundWindow'" not in widgets_init, "no longer in __all__"


# ---------------------------------------------------------------------------
# C4 — the interactive robot diagram
# ---------------------------------------------------------------------------

def test_diagram_widget_lives_in_the_extension():
    assert not (REPO_ROOT / "widgets" / "thymio_diagram_widget.py").exists()
    from extensions.thymio.diagram_widget import ThymioDiagramWidget, get_events_for_region
    assert callable(ThymioDiagramWidget) and callable(get_events_for_region)
    for fname, needle in (
        ("dialogs/thymio_action_selector.py", "widgets.thymio_diagram_widget"),
        ("dialogs/thymio_event_selector.py", "widgets.thymio_diagram_widget"),
        ("editors/object_editor/thymio_events_panel.py", "widgets.thymio_diagram_widget"),
    ):
        assert needle not in (REPO_ROOT / fname).read_text(encoding="utf-8"), fname
    widgets_init = (REPO_ROOT / "widgets" / "__init__.py").read_text(encoding="utf-8")
    assert "thymio_diagram_widget" not in widgets_init
    assert "'ThymioDiagramWidget'" not in widgets_init


def test_extension_is_discovered_and_registers_its_tab():
    from events.plugin_loader import list_available_extensions, load_all_plugins
    found = {e["folder"]: e for e in list_available_extensions()}
    assert "thymio" in found and found["thymio"]["enabled"] is True
    load_all_plugins()
    from actions.core import GM80_ACTION_TABS, get_action_tabs_ordered
    assert GM80_ACTION_TABS["thymio"]["order"] == 100
    assert get_action_tabs_ordered()[-1][0] == "thymio"
