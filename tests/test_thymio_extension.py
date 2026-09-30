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
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


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
    from config.blockly_config import BlocklyConfig, PRESETS
    load_all_plugins()
    assert "thymio_button_forward" in EVENT_TYPES
    assert EVENT_TO_BLOCKLY_MAP["thymio_button_forward"] == "thymio_button_forward"
    # Gated by the Blockly config exactly as before the move.
    names = {e.name for e in get_available_events(BlocklyConfig.get_beginner())}
    assert "thymio_button_forward" not in names
    names = {e.name for e in get_available_events(PRESETS["thymio"])}
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
        ("extensions/thymio/dialogs/thymio_action_selector.py", "widgets.thymio_diagram_widget"),
        ("extensions/thymio/dialogs/thymio_event_selector.py", "widgets.thymio_diagram_widget"),
        ("extensions/thymio/object_editor_panel.py", "widgets.thymio_diagram_widget"),
    ):
        assert needle not in (REPO_ROOT / fname).read_text(encoding="utf-8"), fname
    widgets_init = (REPO_ROOT / "widgets" / "__init__.py").read_text(encoding="utf-8")
    assert "thymio_diagram_widget" not in widgets_init
    assert "'ThymioDiagramWidget'" not in widgets_init


# ---------------------------------------------------------------------------
# C5 — "Playgrounds" wired through the Stage-0.4/0.5 registries, no
# hardcoded core entry left
# ---------------------------------------------------------------------------

def test_playground_asset_type_registers_through_the_extension():
    from events.plugin_loader import load_all_plugins
    from core.asset_types import get_registered_asset_types, side_file_type_names
    load_all_plugins()
    assert "playgrounds" in side_file_type_names()
    spec = {s.plural: s for s in get_registered_asset_types()}["playgrounds"]
    assert spec.singular == "playground"
    assert spec.file_keys == ("arena", "colors", "walls", "robots")
    assert spec.strip_keys == ("walls", "robots", "colors")


def test_playground_asset_tree_category_registers_through_the_extension():
    from events.plugin_loader import load_all_plugins
    from widgets.asset_tree.asset_utils import ASSET_TYPE_REGISTRY
    load_all_plugins()
    entry = ASSET_TYPE_REGISTRY["playgrounds"]
    assert entry["singular"] == "playground"
    assert callable(entry["open_editor"])
    assert "editor_method" not in entry

    from core.ide_extension_points import get_asset_tree_category
    cat = get_asset_tree_category("playgrounds")
    assert cat.label == "Playgrounds" and cat.icon == "🏟️"
    template = cat.new_asset_template("arena_1")
    assert template["name"] == "arena_1" and template["arena"]["width"] == 400
    assert template["walls"] == [] and template["robots"] == []


def test_core_carries_no_hardcoded_playground_entries():
    needle_by_file = {
        "core/asset_types.py": 'plural="playgrounds"',
        "widgets/asset_tree/asset_utils.py": '"playgrounds": {"singular"',
        "widgets/asset_tree/asset_tree_item.py": '"playgrounds": "',
        "core/ide/_editor_lifecycle.py": "def open_playground_editor",
        "core/ide/_assets.py": "asset_type == 'playgrounds'",
    }
    for rel_path, needle in needle_by_file.items():
        src = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        assert needle not in src, rel_path


def test_open_playground_editor_lives_in_the_extension_and_opens_a_tab():
    """The IDE method moved to a free function taking `ide` explicitly, so
    it can be registered as the category's open_editor without living in
    core. Drives it against a real IDE, matching the generic dispatch
    test_ide_extension_points.py already proved for a dummy category."""
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    from extensions.thymio.editor import open_playground_editor
    from core.ide._editor_lifecycle import EditorLifecycleMixin
    assert not hasattr(EditorLifecycleMixin, "open_playground_editor")

    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from core.ide_window import PyGameMakerIDE
    import tempfile
    ide = PyGameMakerIDE()
    try:
        ide.current_project_path = tempfile.mkdtemp()
        # A lingering window (deleteLater only schedules destruction) can
        # receive a deferred changeEvent from pytest-qt's next-test event
        # pump, which reads current_project_data['name'] -- leaving it None
        # crashes that unrelated later test (found the hard way; same
        # landmine class as the plan doc's pre-existing-crash note).
        ide.current_project_data = {"name": "test_project", "assets": {}}
        data = {"name": "arena_1", "asset_type": "playground",
               "arena": {"width": 400, "height": 400}, "walls": [], "robots": []}
        before = ide.editor_tabs.count()
        ide.on_asset_double_clicked({"asset_type": "playgrounds", "name": "arena_1", "data": data})
        assert ide.editor_tabs.count() == before + 1
        key = ide._editor_key("playgrounds", "arena_1")
        assert key in ide.open_editors

        # Reopening the same live tab must not duplicate it.
        ide.on_asset_double_clicked({"asset_type": "playgrounds", "name": "arena_1", "data": data})
        assert ide.editor_tabs.count() == before + 1
    finally:
        ide.deleteLater()


# ---------------------------------------------------------------------------
# C6 — the config/event/action selector dialogs
# ---------------------------------------------------------------------------

def test_config_dialogs_live_in_the_extension():
    for old in ("thymio_config_dialog.py", "thymio_action_selector.py",
               "thymio_event_selector.py"):
        assert not (REPO_ROOT / "dialogs" / old).exists(), old

    from extensions.thymio.dialogs.thymio_config_dialog import ThymioConfigDialog
    from extensions.thymio.dialogs.thymio_action_selector import ThymioActionSelector
    from extensions.thymio.dialogs.thymio_event_selector import ThymioEventSelector
    assert callable(ThymioConfigDialog) and callable(ThymioActionSelector) \
        and callable(ThymioEventSelector)

    dialogs_init = (REPO_ROOT / "dialogs" / "__init__.py").read_text(encoding="utf-8")
    assert "from .thymio" not in dialogs_init
    assert "'ThymioConfigDialog'" not in dialogs_init
    assert "'ThymioActionSelector'" not in dialogs_init
    assert "'ThymioEventSelector'" not in dialogs_init

    # The shared base (genuinely shared with BlocklyConfigDialog) stays in
    # core; only the Thymio subclasses moved.
    assert (REPO_ROOT / "dialogs" / "_block_config_dialog_base.py").exists()
    from dialogs._block_config_dialog_base import THYMIO_CATEGORIES, BaseBlockConfigDialog
    from extensions.thymio.dialogs.thymio_config_dialog import THYMIO_CATEGORIES as reexported
    assert THYMIO_CATEGORIES is reexported
    assert ThymioConfigDialog.__bases__[0] is BaseBlockConfigDialog

    # blockly_config_dialog.py (core, unrelated extension surface) must not
    # depend on the moved Thymio dialogs -- it already imports
    # THYMIO_CATEGORIES from the shared base directly. Mentioning the CLASS
    # NAME in a comment ("...their own ThymioConfigDialog") is fine; an
    # import of the module it now lives in is not.
    blockly_src = (REPO_ROOT / "dialogs" / "blockly_config_dialog.py").read_text(encoding="utf-8")
    assert "thymio_config_dialog" not in blockly_src
    assert "extensions.thymio" not in blockly_src


# ---------------------------------------------------------------------------
# D1/D2 — the Aseba/Open Roberta export+import interop
# ---------------------------------------------------------------------------

def test_aseba_and_roberta_interop_live_in_the_extension():
    for old in ("export/Aseba", "export/Roberta", "importers/roberta_importer.py"):
        assert not (REPO_ROOT / old).exists(), old

    ext_export = REPO_ROOT / "extensions" / "thymio" / "export"
    for fname in ("aseba_exporter.py", "playground_exporter.py",
                  "roberta_exporter.py", "roberta_importer.py"):
        assert (ext_export / fname).exists(), fname

    from extensions.thymio.export.aseba_exporter import AsebaExporter
    from extensions.thymio.export.playground_exporter import PlaygroundExporter
    from extensions.thymio.export.roberta_exporter import RobertaExporter
    from extensions.thymio.export.roberta_importer import import_roberta, RobertaImportError
    assert all(callable(c) for c in
              (AsebaExporter, PlaygroundExporter, RobertaExporter, import_roberta))
    assert issubclass(RobertaImportError, Exception)

    importers_init = (REPO_ROOT / "importers" / "__init__.py").read_text(encoding="utf-8")
    assert "from importers.roberta" not in importers_init
    assert "'import_roberta'" not in importers_init
    assert "'RobertaImportError'" not in importers_init


# ---------------------------------------------------------------------------
# D3 — the Aseba export / Open Roberta import File-menu entries
# ---------------------------------------------------------------------------

def test_core_no_longer_carries_the_menu_action_bodies():
    for fname, needle in (
        ("core/ide/_export.py", "def export_aseba_code"),
        ("core/ide/_assets.py", "def import_roberta_xml"),
    ):
        src = (REPO_ROOT / fname).read_text(encoding="utf-8")
        assert needle not in src, fname
    # The File-menu section no longer builds these actions itself (the
    # still-dormant, out-of-scope Tools->Thymio Programming submenu further
    # down the same file also mentions self.import_roberta_xml -- that's
    # fine, it now correctly resolves to the lambda the extension attaches).
    menu_src = (REPO_ROOT / "core" / "ide" / "_menu_builder.py").read_text(encoding="utf-8")
    file_menu_section = menu_src.split("edit_menu = menubar.addMenu")[0]
    assert "self.export_aseba_code" not in file_menu_section
    assert "self.import_roberta_xml" not in file_menu_section
    assert "[1.0] Aseba" not in menu_src
    assert "[1.0] Open Roberta import hidden from the menu" not in menu_src


def test_file_menu_gets_the_aseba_and_roberta_entries():
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from core.ide_window import PyGameMakerIDE
    ide = PyGameMakerIDE()
    try:
        texts = [a.text() for a in ide._extension_menus["file"].actions()]
        assert "Export &Aseba (Thymio) code..." in texts
        assert "Import Open &Roberta XML..." in texts

        # Reuses core's own generic enable/disable + always-enabled seams,
        # with no core change needed beyond what Stage 0.5/C5 already built.
        assert callable(ide.export_aseba_code) and callable(ide.import_roberta_xml)
        assert ide.export_aseba_action.isEnabled() is False   # no project yet
        ide.current_project_path = "/tmp/whatever"
        # A lingering window can receive a deferred changeEvent from a
        # later test's pytest-qt event pump, which reads this -- same
        # landmine as Stage C5's note (docs/THYMIO_EXTENSION_PLAN.md).
        ide.current_project_data = {"name": "test_project", "assets": {}}
        ide.update_ui_state()
        assert ide.export_aseba_action.isEnabled() is True

        import_action = next(a for a in ide._extension_menus["file"].actions()
                             if a.text() == "Import Open &Roberta XML...")
        assert import_action.property("pygm_always_enabled") is True
    finally:
        ide.deleteLater()


def test_welcome_tab_roberta_entry_is_no_longer_hidden_and_calls_through():
    src = (REPO_ROOT / "widgets" / "welcome_tab.py").read_text(encoding="utf-8")
    assert "# (self.tr(\"📥  Import Open Roberta XML...\")" not in src
    assert '(self.tr("📥  Import Open Roberta XML..."),  self._on_import_roberta)' in src

    from types import SimpleNamespace
    called = []
    stub = SimpleNamespace(main_window=SimpleNamespace(
        import_roberta_xml=lambda: called.append(True)))
    from widgets.welcome_tab import WelcomeTab
    WelcomeTab._on_import_roberta(stub)   # ordinary method, called unbound
    assert called == [True]


# ---------------------------------------------------------------------------
# E1/E2 — the object-editor's Thymio tab
# ---------------------------------------------------------------------------

def test_object_editor_panel_lives_in_the_extension():
    assert not (REPO_ROOT / "editors" / "object_editor" / "thymio_events_panel.py").exists()
    from extensions.thymio.object_editor_panel import ThymioEventsPanel
    assert callable(ThymioEventsPanel)

    main_src = (REPO_ROOT / "editors" / "object_editor" / "object_editor_main.py").read_text(encoding="utf-8")
    for needle in ("from .thymio_events_panel import", "self.thymio_events_panel",
                  "self.thymio_tab", "def _on_thymio_events_modified",
                  "def _on_thymio_event_selected", "def switch_to_thymio_mode"):
        assert needle not in main_src, needle
    # The one still-needed, thin, generically-implemented wrapper.
    assert "def set_thymio_tab_visible" in main_src
    assert "self.set_extension_panel_visible('thymio'" in main_src

    init_src = (REPO_ROOT / "editors" / "object_editor" / "__init__.py").read_text(encoding="utf-8")
    assert "from .thymio_events_panel" not in init_src
    assert "'ThymioEventsPanel'" not in init_src


def test_thymio_panel_registers_through_the_extension():
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from extensions.thymio import PLUGIN_OBJECT_EDITOR_PANELS
    spec = PLUGIN_OBJECT_EDITOR_PANELS[0]
    assert spec.key == "thymio" and spec.label == "🤖 Thymio"
    panel = spec.factory()
    from extensions.thymio.object_editor_panel import ThymioEventsPanel
    assert isinstance(panel, ThymioEventsPanel)

    from extensions.thymio.events import THYMIO_EVENT_TYPES
    assert set(spec.owned_events()) == set(THYMIO_EVENT_TYPES)
    text = spec.event_label("thymio_button_forward")
    assert text and THYMIO_EVENT_TYPES["thymio_button_forward"].display_name in text
    assert spec.event_label("not_a_real_event") is None

    from utils.config import Config
    saved = Config.get('show_thymio_tab', False)
    try:
        Config.set('show_thymio_tab', True)
        assert spec.is_visible() is True
        Config.set('show_thymio_tab', False)
        assert spec.is_visible() is False
    finally:
        Config.set('show_thymio_tab', saved)


def test_object_editor_hosts_the_registered_thymio_tab_and_translates_its_label():
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from utils.config import Config
    saved = Config.get('show_thymio_tab', False)
    try:
        Config.set('show_thymio_tab', True)
        from editors.object_editor.object_editor_main import ObjectEditor
        editor = ObjectEditor()
        try:
            texts = [editor.events_tab_widget.tabText(i)
                    for i in range(editor.events_tab_widget.count())]
            # Untranslated in this test's default locale, but routed through
            # self.tr(spec.label) -- the exact "🤖 Thymio" source text a real
            # translation catalog resolves under the ObjectEditorMain context,
            # same as the original hardcoded self.tr("🤖 Thymio") call did.
            assert "🤖 Thymio" in texts
            assert "thymio" in editor._extension_panels
        finally:
            editor.deleteLater()
    finally:
        Config.set('show_thymio_tab', saved)


def test_extension_is_discovered_and_registers_its_tab():
    from events.plugin_loader import list_available_extensions, load_all_plugins
    found = {e["folder"]: e for e in list_available_extensions()}
    assert "thymio" in found and found["thymio"]["enabled"] is True
    load_all_plugins()
    from actions.core import GM80_ACTION_TABS, get_action_tabs_ordered
    assert GM80_ACTION_TABS["thymio"]["order"] == 100
    assert get_action_tabs_ordered()[-1][0] == "thymio"


# ---------------------------------------------------------------------------
# F — Blockly toolbox: categories, preset, translations
# ---------------------------------------------------------------------------

def test_core_no_longer_carries_the_thymio_categories_or_preset():
    # Source-only: BLOCK_REGISTRY/PRESETS are process-global and another test
    # in this same session may have already called load_all_plugins(), which
    # merges the extension's categories/preset in (that merge is exactly what
    # the next test below checks) -- so this test can't assert on runtime
    # dict state, only that core's own source no longer defines them.
    src = (REPO_ROOT / "config" / "blockly_config.py").read_text(encoding="utf-8")
    assert "Thymio Events" not in src and "def get_thymio" not in src
    tr_src = (REPO_ROOT / "config" / "blockly_translations.py").read_text(encoding="utf-8")
    assert "Thymio Events" not in tr_src


def test_thymio_categories_and_preset_register_through_the_extension():
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from config.blockly_config import BLOCK_REGISTRY, PRESETS
    from extensions.thymio.blockly_categories import PLUGIN_BLOCK_CATEGORIES

    for name, blocks in PLUGIN_BLOCK_CATEGORIES.items():
        assert BLOCK_REGISTRY[name] == blocks

    cfg = PRESETS["thymio"]
    assert cfg.preset_name == "thymio"
    assert cfg.enabled_categories == set(PLUGIN_BLOCK_CATEGORIES)
    # The exact get_thymio() shape: event_create + every category's blocks +
    # the three control-flow blocks -- not just "categories enabled" (the
    # ordering bug this module's docstring documents would leave
    # enabled_blocks basically empty while enabled_categories looked fine).
    expected = {"event_create", "start_block", "end_block", "else_action"}
    for blocks in PLUGIN_BLOCK_CATEGORIES.values():
        expected.update(b["type"] for b in blocks)
    assert cfg.enabled_blocks == expected


def test_thymio_category_translations_register_through_the_extension():
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from config.blockly_translations import CATEGORY_TRANSLATIONS, get_translated_category
    for lang in ("de", "es", "fr", "it", "ru", "sl", "uk"):
        assert CATEGORY_TRANSLATIONS[lang]["Thymio Motors"]
    assert get_translated_category("Thymio Motors", "fr") == "Moteurs Thymio"


def test_thymio_categories_dialog_base_stays_in_core():
    # THYMIO_CATEGORIES is just the 8 names, needed by core's own
    # BlocklyConfigDialog for exclusion filtering -- deliberately not moved.
    from dialogs._block_config_dialog_base import THYMIO_CATEGORIES
    from extensions.thymio.blockly_categories import PLUGIN_BLOCK_CATEGORIES
    assert THYMIO_CATEGORIES == set(PLUGIN_BLOCK_CATEGORIES)
    assert (REPO_ROOT / "dialogs" / "_block_config_dialog_base.py").exists()


def test_full_preset_regains_thymio_blocks_after_extension_loads():
    # register_block_categories() rebuilds "full"/"implemented_only" once new
    # categories are merged in (config/blockly_config.py) -- confirms that
    # existing mechanism still picks up the extension's categories.
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from config.blockly_config import PRESETS
    assert "thymio_set_motor_speed" in PRESETS["full"].enabled_blocks
    assert "thymio_set_motor_speed" in PRESETS["implemented_only"].enabled_blocks


# ---------------------------------------------------------------------------
# G — Tools menu / toolbar (configure_thymio, toggle_thymio_tab,
# show_thymio_playground, show_thymio_event_selector,
# show_thymio_action_selector); the generic pygm_requires_project sweep.
# ---------------------------------------------------------------------------

def test_tools_menu_methods_live_in_the_extension_not_core():
    from extensions.thymio import tools_menu
    for name in ("configure_thymio", "toggle_thymio_tab", "show_thymio_playground",
                 "show_thymio_event_selector", "show_thymio_action_selector"):
        assert callable(getattr(tools_menu, name))

    from core.ide._dialogs import DialogsMixin
    for name in ("configure_thymio", "toggle_thymio_tab", "show_thymio_playground",
                 "show_thymio_event_selector", "show_thymio_action_selector"):
        assert not hasattr(DialogsMixin, name)

    src = (REPO_ROOT / "core" / "ide" / "_dialogs.py").read_text(encoding="utf-8")
    assert "ThymioConfigDialog" not in src
    assert "Config.set('show_thymio_tab'" not in src


def test_no_1_0_markers_remain_anywhere():
    # G1: the marker convention had exactly one user (Thymio) -- confirm
    # zero real `# [1.0]` comments survive repo-wide (a literal mention
    # inside this module's own docstring, describing what USED to be
    # there, doesn't count -- it's prose, not a marker).
    import subprocess
    result = subprocess.run(
        ["git", "grep", "-n", r"^\s*# \[1\.0\]"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    # git grep exits 1 when nothing matches -- that's the expected outcome.
    assert result.returncode == 1, f"real [1.0] markers still present:\n{result.stdout}"


def test_show_thymio_playground_reuses_window_and_deletes_on_close(monkeypatch):
    """Moved from tests/test_audit_ide_window_leaks.py (L4) once
    show_thymio_playground moved into the extension (Stage G): second open
    reuses the first live window; WA_DeleteOnClose is set."""
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    from PySide6.QtCore import Qt
    from extensions.thymio.tools_menu import show_thymio_playground
    import extensions.thymio.playground_window as tp

    created = []

    class FakePlayground:
        def __init__(self, parent):
            self.parent = parent
            self._attrs = set()
            self.shown = 0
            self.raised = 0
            created.append(self)

        def setAttribute(self, attr):
            self._attrs.add(attr)

        def show(self):
            self.shown += 1

        def showNormal(self):
            self.shown += 1

        def raise_(self):
            self.raised += 1

        def activateWindow(self):
            pass

    monkeypatch.setattr(tp, "ThymioPlaygroundWindow", FakePlayground)

    import shiboken6
    monkeypatch.setattr(shiboken6, "isValid", lambda obj: obj in created)

    class Stub:
        def tr(self, s, *a, **k):
            return s

    stub = Stub()

    show_thymio_playground(stub)
    assert len(created) == 1, "first open should construct one window"
    first = created[0]
    assert Qt.WA_DeleteOnClose in first._attrs, "WA_DeleteOnClose not set"

    show_thymio_playground(stub)
    assert len(created) == 1, "second open leaked a new window instead of reusing"
    assert first.raised >= 1, "existing window not raised on reopen"

    monkeypatch.setattr(shiboken6, "isValid", lambda obj: False)
    show_thymio_playground(stub)
    assert len(created) == 2, "a fresh window should be created once the old one is gone"


def _stub_ide():
    from PySide6.QtWidgets import QMainWindow, QApplication
    from core.ide._menu_builder import MenuBuilderMixin
    QApplication.instance() or QApplication([])

    class _StubIDE(MenuBuilderMixin, QMainWindow):
        pass

    ide = _StubIDE()
    ide.current_project_data = None

    class _Label:
        def setText(self, *a, **k):
            pass

    ide.project_label = _Label()
    return ide


def test_tools_menu_and_toolbar_build_nothing_when_hidden():
    # Default: show_thymio_tab is False, so a default install's Tools menu
    # and toolbar get nothing from the extension -- unchanged from before
    # this move (when the equivalent UI was hardcoded and commented out).
    from utils.config import Config
    from PySide6.QtWidgets import QMenu, QToolBar
    from extensions.thymio import _build_tools_menu, _build_toolbar

    saved = Config.get('show_thymio_tab', False)
    try:
        Config.set('show_thymio_tab', False)
        ide = _stub_ide()
        menu = QMenu(ide)
        toolbar = QToolBar(ide)
        _build_tools_menu(ide, menu)
        _build_toolbar(ide, toolbar)
        assert menu.actions() == []
        assert toolbar.actions() == []
        assert not hasattr(ide, 'show_thymio_tab_action')
        assert not hasattr(ide, 'thymio_toolbar_action')
    finally:
        Config.set('show_thymio_tab', saved)


def test_tools_menu_and_toolbar_build_the_full_ui_when_visible():
    from utils.config import Config
    from PySide6.QtWidgets import QMenu, QToolBar
    from extensions.thymio import _build_tools_menu, _build_toolbar

    saved = Config.get('show_thymio_tab', False)
    try:
        Config.set('show_thymio_tab', True)
        ide = _stub_ide()
        menu = QMenu(ide)
        toolbar = QToolBar(ide)
        _build_tools_menu(ide, menu)
        _build_toolbar(ide, toolbar)

        # Configure action + the Thymio Programming submenu.
        top_texts = [a.text() for a in menu.actions() if not a.isSeparator()]
        assert any("Configure" in t and "Thymio" in t for t in top_texts)
        # Look up each action's .menu() exactly once into a local -- calling
        # it twice (e.g. inside a list-comprehension filter+value) triggers
        # a PySide6/shiboken wrapper-ownership quirk on a QMenu parented to
        # a Python QMainWindow subclass that deletes the real C++ submenu
        # out from under a second lookup. Pure test-harness landmine, not a
        # production bug -- _build_tools_menu itself only ever looks up its
        # own addMenu() return value once and keeps that single reference.
        thymio_menu = None
        for a in menu.actions():
            m = a.menu()
            if m is not None:
                thymio_menu = m
        assert thymio_menu is not None
        sub_texts = [a.text() for a in thymio_menu.actions() if not a.isSeparator()]
        assert ide.show_thymio_tab_action in thymio_menu.actions()
        assert ide.show_thymio_tab_action.isChecked() is True
        assert any("Playground" in t for t in sub_texts)
        assert ide.thymio_add_event_action in thymio_menu.actions()
        assert ide.thymio_add_action_action in thymio_menu.actions()
        assert ide.thymio_import_roberta_action in thymio_menu.actions()

        # Requires-project gating: added, not requires-always-enabled.
        assert ide.thymio_add_event_action.property("pygm_requires_project") is True
        assert ide.thymio_add_action_action.property("pygm_requires_project") is True
        # Imports a new project -- must stay enabled with none open.
        assert ide.thymio_import_roberta_action.property("pygm_always_enabled") is True

        # Toolbar quick-add button.
        assert ide.thymio_toolbar_action in toolbar.actions()
        assert ide.thymio_toolbar_action.property("pygm_requires_project") is True
    finally:
        Config.set('show_thymio_tab', saved)


def test_update_ui_state_gates_thymio_actions_generically_not_by_name():
    # core/ide_window.py no longer names any Thymio action; it enables/
    # disables via the generic pygm_requires_project/pygm_always_enabled
    # QAction properties an extension sets on its own actions instead.
    # (Pointer comments referencing "extensions/thymio" by path, like every
    # other moved-code comment in this codebase, are fine -- only a literal
    # Thymio *action attribute name* would mean core still hardcodes one.)
    src = (REPO_ROOT / "core" / "ide_window.py").read_text(encoding="utf-8")
    for name in ("thymio_add_event_action", "thymio_add_action_action",
                 "thymio_toolbar_action", "thymio_import_roberta_action",
                 "export_aseba_action", "show_thymio_tab_action"):
        assert name not in src, f"{name} still hardcoded in core/ide_window.py"

    from utils.config import Config
    saved = Config.get('show_thymio_tab', False)
    try:
        Config.set('show_thymio_tab', True)
        ide = _stub_ide()
        from PySide6.QtWidgets import QMenu, QToolBar
        from extensions.thymio import _build_tools_menu, _build_toolbar
        _build_tools_menu(ide, QMenu())
        _build_toolbar(ide, QToolBar())

        ide.current_project_path = None
        # update_ui_state is a real PyGameMakerIDE method; run it unbound
        # against the stub the same way other tests in this repo drive
        # real IDE methods against lightweight stand-ins.
        from core.ide_window import PyGameMakerIDE
        PyGameMakerIDE.update_ui_state(ide)

        assert ide.thymio_add_event_action.isEnabled() is False
        assert ide.thymio_add_action_action.isEnabled() is False
        assert ide.thymio_toolbar_action.isEnabled() is False
        assert ide.thymio_import_roberta_action.isEnabled() is True  # always-enabled import

        ide.current_project_path = REPO_ROOT  # any truthy path
        ide.current_project_data = {'name': 'stub'}
        PyGameMakerIDE.update_ui_state(ide)
        assert ide.thymio_add_event_action.isEnabled() is True
        assert ide.thymio_add_action_action.isEnabled() is True
        assert ide.thymio_toolbar_action.isEnabled() is True
    finally:
        Config.set('show_thymio_tab', saved)


# ---------------------------------------------------------------------------
# G4 — README.md. Every sibling extension has one; pin its factual claims
# (counts drawn out of the simulator/schemas) so a future edit can't drift
# from reality the way the README's own first draft did (7 proximity
# sensors, not the 5 first written -- caught only by writing this test).
# ---------------------------------------------------------------------------

def test_readme_exists_and_matches_reality():
    readme = (REPO_ROOT / "extensions" / "thymio" / "README.md")
    assert readme.exists()
    text = readme.read_text(encoding="utf-8")

    from extensions.thymio.actions import THYMIO_ACTIONS
    from extensions.thymio.events import THYMIO_EVENT_TYPES
    assert f"{len(THYMIO_ACTIONS)} actions" in text
    assert len(THYMIO_ACTIONS) == 28
    assert f"{len(THYMIO_EVENT_TYPES)} events" in text
    assert len(THYMIO_EVENT_TYPES) == 14

    from extensions.thymio.simulator import ThymioSensorState, ThymioLEDState
    prox = ThymioSensorState().proximity
    ground = ThymioSensorState().ground_delta
    leds = ThymioLEDState()
    circle = leds.circle
    assert f"{len(prox)} proximity" in text
    assert f"{len(ground)} ground" in text
    assert f"{len(circle)}-LED circle" in text
    # top/bottom_left/bottom_right — the 3 named RGB LEDs the README counts
    # separately from the circle.
    named_rgb_leds = sum(1 for f in ("top", "bottom_left", "bottom_right")
                          if hasattr(leds, f))
    assert f"{named_rgb_leds} RGB LEDs" in text

    assert "tools_menu.py" in text
    assert "show_thymio_tab" in text  # the UI-visibility flag is documented


# ---------------------------------------------------------------------------
# G2 — every Thymio/Roberta/Aseba/playground test already imports from
# extensions.thymio.* (each prior stage updated its own tests as it moved
# code, so this turned out to already be done; pinned here rather than
# re-migrated).
# ---------------------------------------------------------------------------

def test_thymio_behavioural_tests_import_from_the_extension_not_old_paths():
    import re
    old_path_import = re.compile(
        r"^from (runtime\.thymio_|actions\.thymio_|events\.thymio_|"
        r"widgets\.thymio_|dialogs\.thymio_|editors\.playground_editor|"
        r"export\.Aseba|export\.Roberta|importers\.roberta_importer)",
        re.MULTILINE,
    )
    names = (
        "test_aseba_export.py", "test_aseba_resource_packager_object_file_merge.py",
        "test_audit_aseba_export_format.py", "test_audit_playground_undo_panel.py",
        "test_audit_playground_undo_redo.py", "test_audit_roberta_led.py",
        "test_audit_thymio_simulator.py", "test_audit_thymio_simulator_guard.py",
        "test_object_events_panel_thymio_lossless_rewrite.py",
        "test_playground_editor_undo.py", "test_playground_editor_undo_refresh.py",
        "test_playground_linkable_objects_merge.py", "test_playground_robot_ports.py",
        "test_roberta_led_keys.py", "test_roberta_xxe.py",
        "test_thymio_choice_labels.py", "test_thymio_config_preset_name.py",
        "test_thymio_else_preserved.py", "test_thymio_playground_fstring_tr_fix.py",
        "test_thymio_playground_zoom.py", "test_thymio_set_variable.py",
        "test_thymio_sim_geometry.py", "test_thymio_sound_honesty.py",
    )
    offenders = []
    for name in names:
        path = REPO_ROOT / "tests" / name
        assert path.exists(), f"expected test file missing: {name}"
        if old_path_import.search(path.read_text(encoding="utf-8")):
            offenders.append(name)
    assert offenders == []


# ---------------------------------------------------------------------------
# G5b.1 — the Blockly toolbox visibility filter. blockly_widget.py no
# longer names Thymio at all; it asks the generic ToolboxVisibilityFilter
# registry, which Thymio (among any future extension) registers into.
# ---------------------------------------------------------------------------

def test_blockly_widget_no_longer_names_thymio():
    # The file may still mention "Thymio" in an illustrative comment (the
    # ToolboxVisibilityFilter seam's own generic example, same as every
    # other seam's docstring) -- what must be gone is actual code:
    # startswith("thymio_") / "Thymio " prefix checks and the deleted method.
    src = (REPO_ROOT / "editors" / "object_editor" / "blockly_widget.py").read_text(encoding="utf-8")
    assert 'startswith("thymio_")' not in src
    assert 'startswith("Thymio ")' not in src
    assert "def project_has_playgrounds" not in src  # method deleted, a pointer comment mentioning it is fine
    assert "extensions.thymio" not in src  # no direct import of the extension


def test_thymio_toolbox_filter_registers_and_hides_only_without_playgrounds():
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from core.ide_extension_points import apply_toolbox_visibility_filters

    blocks = {"thymio_set_motor_speed", "move_free"}
    cats = {"Thymio Motors", "Movement"}

    class _NoPlaygrounds:
        def parent(self):
            return None

    filtered_blocks, filtered_cats = apply_toolbox_visibility_filters(
        blocks, cats, _NoPlaygrounds())
    assert filtered_blocks == {"move_free"}
    assert filtered_cats == {"Movement"}

    class _Parent:
        current_project_data = {"assets": {"playgrounds": {"arena_1": {}}}}

    class _WithPlaygrounds:
        def parent(self):
            return _Parent()

    filtered_blocks, filtered_cats = apply_toolbox_visibility_filters(
        blocks, cats, _WithPlaygrounds())
    assert filtered_blocks == blocks
    assert filtered_cats == cats


def test_blockly_widget_apply_configuration_filters_thymio_end_to_end():
    import json
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from editors.object_editor.blockly_widget import BlocklyWidget
    from config.blockly_config import BlocklyConfig

    widget = BlocklyWidget()  # no parent -> no project data -> no playgrounds
    try:
        sent = {}

        def _capture(js):
            payload = js[len("window.blocklyApi.reconfigureToolbox("):-1]
            sent["config"] = json.loads(payload)

        widget.web_view.page().runJavaScript = _capture

        cfg = BlocklyConfig(preset_name="test")
        cfg.enabled_blocks = {"thymio_set_motor_speed", "move_free"}
        cfg.enabled_categories = {"Thymio Motors", "Movement"}
        widget.apply_configuration(cfg)

        assert set(sent["config"]["enabled_blocks"]) == {"move_free"}
        assert set(sent["config"]["enabled_categories"]) == {"Movement"}
    finally:
        widget.deleteLater()
