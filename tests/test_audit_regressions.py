"""
Regression tests for the multi-agent latent-bug audit (2026-06-03).

Each test pins a specific confirmed defect so it cannot silently return.
References point at the fixed call sites.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_qt_widgets

from editors.object_editor.python_code_parser import events_to_python, python_to_events


# ============================================================================
# #4 — Alarm events were silently dropped by events_to_python
#      (python_code_parser.py: generate_full_class only special-cased keyboard*)
# ============================================================================

class TestAlarmEventRoundTrip:
    """Alarm sub-events must survive the events <-> Python code round-trip."""

    def test_alarm_actions_are_emitted_not_dropped(self):
        events = {"alarm": {"alarm_0": {"actions": [
            {"action": "stop_movement", "parameters": {}}
        ]}}}
        code = events_to_python("obj_t", events)
        # The regression produced a bare `def on_alarm(self): pass`.
        assert "def on_alarm_0(self):" in code
        assert "def on_alarm(self):" not in code
        assert "self.hspeed = 0" in code  # the action body, not `pass`

    def test_alarm_round_trips_back_into_nested_container(self):
        events = {"alarm": {"alarm_3": {"actions": [
            {"action": "stop_movement", "parameters": {}}
        ]}}}
        code = events_to_python("obj_t", events)
        parsed, errors = python_to_events(code)
        assert errors == []
        assert "alarm" in parsed
        assert "alarm_3" in parsed["alarm"]
        assert parsed["alarm"]["alarm_3"]["actions"], "alarm actions were lost"

    def test_multiple_alarms_all_preserved(self):
        events = {"alarm": {
            "alarm_0": {"actions": [{"action": "stop_movement", "parameters": {}}]},
            "alarm_5": {"actions": [{"action": "stop_movement", "parameters": {}}]},
        }}
        parsed, errors = python_to_events(events_to_python("obj_t", events))
        assert errors == []
        assert set(parsed.get("alarm", {})) == {"alarm_0", "alarm_5"}


# ============================================================================
# #5 — keyboard_press / keyboard_release round-tripped into wrong container
#      (python_code_parser.py: split('_', 1) mis-parsed the base event)
# ============================================================================

class TestKeyboardEventRoundTrip:
    """keyboard_press/keyboard_release/keyboard must keep their base + key."""

    def test_keyboard_press_keeps_base_and_key(self):
        events = {"keyboard_press": {"space": {"actions": [
            {"action": "stop_movement", "parameters": {}}
        ]}}}
        parsed, errors = python_to_events(events_to_python("obj_t", events))
        assert errors == []
        # The regression stored this under keyboard.press_space.
        assert "press_space" not in parsed.get("keyboard", {})
        assert "space" in parsed.get("keyboard_press", {})
        assert parsed["keyboard_press"]["space"]["actions"]

    def test_keyboard_release_is_not_lost(self):
        events = {"keyboard_release": {"left": {"actions": [
            {"action": "stop_movement", "parameters": {}}
        ]}}}
        parsed, errors = python_to_events(events_to_python("obj_t", events))
        assert errors == []
        # The regression dropped keyboard_release entirely.
        assert "left" in parsed.get("keyboard_release", {})
        assert parsed["keyboard_release"]["left"]["actions"]

    def test_held_keyboard_still_works(self):
        events = {"keyboard": {"right": {"actions": [
            {"action": "stop_movement", "parameters": {}}
        ]}}}
        parsed, errors = python_to_events(events_to_python("obj_t", events))
        assert errors == []
        assert "right" in parsed.get("keyboard", {})

    def test_all_three_keyboard_kinds_coexist(self):
        events = {
            "keyboard_press": {"space": {"actions": [{"action": "stop_movement", "parameters": {}}]}},
            "keyboard_release": {"left": {"actions": [{"action": "stop_movement", "parameters": {}}]}},
            "keyboard": {"right": {"actions": [{"action": "stop_movement", "parameters": {}}]}},
        }
        parsed, errors = python_to_events(events_to_python("obj_t", events))
        assert errors == []
        assert "space" in parsed.get("keyboard_press", {})
        assert "left" in parsed.get("keyboard_release", {})
        assert "right" in parsed.get("keyboard", {})


# ============================================================================
# #3 — Roberta export turned "decrease variable" into "increase"
#      (roberta_exporter.py: decrease reused the increase builder, no negation)
# ============================================================================

class TestRobertaDecreaseVariableSign:
    """Decrease must emit a negated DELTA; increase stays positive."""

    @staticmethod
    def _delta(block):
        field = block.find('.//value[@name="DELTA"]//field[@name="NUM"]')
        return field.text

    def test_decrease_negates_amount(self):
        from export.Roberta.roberta_exporter import _build_decrease_variable
        block = _build_decrease_variable({"variable": "counter", "amount": "3"})
        assert self._delta(block) == "-3"

    def test_increase_stays_positive(self):
        from export.Roberta.roberta_exporter import _build_increase_variable
        block = _build_increase_variable({"variable": "counter", "amount": "3"})
        assert self._delta(block) == "3"

    def test_decrease_registered_to_dedicated_builder(self):
        from export.Roberta import roberta_exporter as r
        assert r._ACTION_BUILDERS["thymio_decrease_variable"] is r._build_decrease_variable
        assert r._ACTION_BUILDERS["thymio_decrease_variable"] is not r._build_increase_variable

    def test_decrease_handles_non_numeric_amount(self):
        from export.Roberta.roberta_exporter import _build_decrease_variable
        # Must not raise; falls back to a "-<amount>" expression.
        block = _build_decrease_variable({"variable": "counter", "amount": "speed"})
        assert self._delta(block) == "-speed"


# ============================================================================
# #7 — Room package export collected zero dependencies
#      (resource_packager.py: read 'object_type', instances use 'object_name')
# ============================================================================

class TestRoomPackageDependencyCollection:
    """_collect_room_dependencies must find objects via object_name/object."""

    def _project(self):
        return {
            "assets": {
                "objects": {"obj_player": {"sprite": "spr_player"}},
                "sprites": {"spr_player": {"frames": []}},
            }
        }

    def test_collects_via_object_name_key(self):
        from utils.resource_packager import ResourcePackager
        room = {"instances": [{"object_name": "obj_player", "x": 0, "y": 0}]}
        deps = ResourcePackager._collect_room_dependencies(room, self._project(), Path("."))
        assert "obj_player" in deps["objects"]
        assert "spr_player" in deps["sprites"]

    def test_collects_via_legacy_object_key(self):
        from utils.resource_packager import ResourcePackager
        room = {"instances": [{"object": "obj_player", "x": 0, "y": 0}]}
        deps = ResourcePackager._collect_room_dependencies(room, self._project(), Path("."))
        assert "obj_player" in deps["objects"]
        assert "spr_player" in deps["sprites"]


# ============================================================================
# #2 — Conditional editor saved translated condition_type (locale-dependent)
#      (conditional_editor.py: stored currentText() instead of canonical id)
# ============================================================================

@skip_without_qt_widgets
class TestConditionalEditorCanonicalValues:
    """condition_type and sub-fields must save canonical English identifiers."""

    def test_default_condition_type_is_canonical(self, qtbot):
        from events.conditional_editor import ConditionalActionEditor
        dialog = ConditionalActionEditor({})
        qtbot.addWidget(dialog)
        params = dialog.get_parameter_values()
        assert params["condition_type"] == "instance_count"

    def test_condition_type_round_trips(self, qtbot):
        from events.conditional_editor import ConditionalActionEditor
        src = {"condition_type": "expression", "expression": "x > 5",
               "then_actions": [], "else_actions": []}
        dialog = ConditionalActionEditor(src)
        qtbot.addWidget(dialog)
        out = dialog.get_parameter_values()
        assert out["condition_type"] == "expression"
        assert out["expression"] == "x > 5"

    def test_key_pressed_subfields_are_canonical(self, qtbot):
        from events.conditional_editor import ConditionalActionEditor
        src = {"condition_type": "key_pressed", "key": "Space", "state": "Held",
               "then_actions": [], "else_actions": []}
        dialog = ConditionalActionEditor(src)
        qtbot.addWidget(dialog)
        out = dialog.get_parameter_values()
        assert out["condition_type"] == "key_pressed"
        # The canonical key value is the lowercase pygame key name the runtime
        # matches against (str(key).lower() in keys_pressed) — audit M30 fixed
        # the editor to store "space"/"left"/… instead of the display labels
        # "Space"/"Left Arrow" that never matched. Lowercase is the canonical id.
        assert out["key"] == "space"
        assert out["state"] == "Held"

    def test_combo_stores_english_as_userdata(self, qtbot):
        from events.conditional_editor import ConditionalActionEditor
        dialog = ConditionalActionEditor({})
        qtbot.addWidget(dialog)
        # Every item's userData is the canonical English id, independent of
        # the displayed (translatable) label.
        combo = dialog.condition_type
        datas = [combo.itemData(i) for i in range(combo.count())]
        assert "instance_count" in datas
        assert "variable_compare" in datas
        assert "expression" in datas


# ============================================================================
# Runtime action-executor fixes (#8, #9, #11, #22)
# ============================================================================

from runtime.action_executor import ActionExecutor
sys.path.insert(0, str(Path(__file__).parent))  # ensure tests/ dir importable
from test_action_executor import MockInstance, MockRoom, MockGameRunner


class TestKeyPressedConditionReadsInstance:
    """#8 — if_condition 'key_pressed' read game_runner.pressed_keys (which does
    not exist), so it was always false. It must read instance.keys_pressed."""

    def test_true_when_instance_holds_key(self):
        executor = ActionExecutor(game_runner=MockGameRunner())
        inst = MockInstance()
        inst.keys_pressed = {"space"}
        assert executor._evaluate_if_condition(
            inst, "key_pressed", {"key": "space"}) is True

    def test_case_insensitive(self):
        executor = ActionExecutor(game_runner=MockGameRunner())
        inst = MockInstance()
        inst.keys_pressed = {"space"}
        assert executor._evaluate_if_condition(
            inst, "key_pressed", {"key": "Space"}) is True

    def test_false_when_not_held(self):
        executor = ActionExecutor(game_runner=MockGameRunner())
        inst = MockInstance()
        inst.keys_pressed = set()
        assert executor._evaluate_if_condition(
            inst, "key_pressed", {"key": "space"}) is False


class TestCollisionDestroyTargetObject:
    """#9 — destroy_instance target='object' inside a collision event was a
    silent no-op (handle_collision_action only inlined self/other)."""

    def test_target_object_destroys_all_matching(self):
        runner = MockGameRunner()
        e1, e2 = MockInstance("enemy"), MockInstance("enemy")
        bystander = MockInstance("hero")
        runner.current_room.instances = [e1, e2, bystander]
        executor = ActionExecutor(game_runner=runner)
        actor, other = MockInstance("bullet"), MockInstance("enemy")
        executor.handle_collision_action(
            actor,
            {"action": "destroy_instance",
             "parameters": {"target": "object", "target_object": "enemy"}},
            other)
        assert e1.to_destroy is True and e2.to_destroy is True
        assert bystander.to_destroy is False

    def test_target_self_other_still_inlined(self):
        executor = ActionExecutor(game_runner=MockGameRunner())
        actor, other = MockInstance("a"), MockInstance("b")
        executor.handle_collision_action(
            actor, {"action": "destroy_instance", "parameters": {"target": "self"}}, other)
        assert actor.to_destroy is True and other.to_destroy is False
        actor2, other2 = MockInstance("a"), MockInstance("b")
        executor.handle_collision_action(
            actor2, {"action": "destroy_instance", "parameters": {"target": "other"}}, other2)
        assert other2.to_destroy is True and actor2.to_destroy is False


class TestRepeatInsideCollisionEvent:
    """#11 — 'repeat' was unknown inside collision events, so the repeated
    action ran exactly once instead of N times."""

    def test_repeat_runs_action_n_times(self):
        executor = ActionExecutor(game_runner=MockGameRunner())
        calls = []
        executor.action_handlers["_count_marker"] = lambda inst, params: calls.append(1)
        actions = [
            {"action": "repeat", "parameters": {"times": 3}},
            {"action": "_count_marker", "parameters": {}},
        ]
        executor.execute_collision_action_list(MockInstance(), actions, MockInstance("other"))
        assert len(calls) == 3


class TestIfObjectExistsSkipsToDestroy:
    """#22 — if_object_exists counted instances already flagged to_destroy,
    lagging 'level cleared' gating by a frame."""

    def test_only_to_destroy_instance_means_not_exists(self):
        runner = MockGameRunner()
        doomed = MockInstance("enemy")
        doomed.to_destroy = True
        runner.current_room.instances = [doomed]
        executor = ActionExecutor(game_runner=runner)
        assert executor.execute_if_object_exists_action(
            MockInstance(), {"object": "enemy"}) is False

    def test_live_instance_means_exists(self):
        runner = MockGameRunner()
        runner.current_room.instances = [MockInstance("enemy")]
        executor = ActionExecutor(game_runner=runner)
        assert executor.execute_if_object_exists_action(
            MockInstance(), {"object": "enemy"}) is True


# ============================================================================
# Simple independent fixes (#21, #26)  [#20/#27/#28 are Qt-widget paths]
# ============================================================================

class TestThymioPresetEnablesElseAction:
    """#21 — the thymio preset called enable_block("else") instead of the
    canonical "else_action", so the Else block never appeared in its toolbox."""

    def test_thymio_preset_has_else_action_block(self):
        from config.blockly_config import BlocklyConfig
        cfg = BlocklyConfig.get_thymio()
        assert "else_action" in cfg.enabled_blocks
        assert "else" not in cfg.enabled_blocks


class TestMissingFileFlagSurvivesImportMigration:
    """#26 — load_assets_from_project_data flipped imported back to True right
    after _validate_asset_paths flagged a missing file, hiding the breakage."""

    def test_missing_file_stays_flagged(self, tmp_path):
        from core.asset_manager import AssetManager
        mgr = AssetManager(project_directory=tmp_path)
        project_data = {"assets": {"sprites": {
            "spr_missing": {"file_path": "does_not_exist.png", "imported": True},
        }}}
        mgr.load_assets_from_project_data(project_data)
        asset = mgr.assets_cache["sprites"]["spr_missing"]
        assert asset.get("file_missing") is True
        assert asset.get("imported") is False


# ============================================================================
# Thymio playground fixes (#13 button state)  [#14/#24 are Qt-runtime paths]
# ============================================================================

class TestThymioKeyButtonStateMapping:
    """#13 — keyboard button presses fired events but never set the simulator
    button state, so state-polling (get_button / thymio_if_button_pressed)
    always read 0. Every key→event in the map must derive a settable button."""

    def test_key_event_map_buttons_are_settable(self):
        from runtime.playground_runner import PlaygroundRunnerWindow
        from runtime.thymio_simulator import ThymioSimulator
        sim = ThymioSimulator(x=0, y=0, angle=0)
        assert PlaygroundRunnerWindow._KEY_EVENT_MAP, "key->event map is empty"
        for event_name in PlaygroundRunnerWindow._KEY_EVENT_MAP.values():
            assert event_name.startswith("thymio_button_")
            button = event_name[len("thymio_button_"):]
            assert button in sim.sensors.buttons
            sim.set_button(button, True)
            assert sim.get_button(button) == 1
            sim.set_button(button, False)
            assert sim.get_button(button) == 0


# ============================================================================
# GMK import fixes (#16 repeat count)  [#17 verified by loader-compat inspection]
# ============================================================================

class TestGmkRepeatKeepsCount:
    """#16 — the action_kind dispatch returned empty params for repeat (kind 5)
    before the ID path that knows the 'times' arg, so imported repeats ran once."""

    def test_repeat_captures_times_from_first_arg(self):
        from importers.gmk_converter import GmkConverter
        from importers.gmk_parser import GmkAction
        conv = GmkConverter.__new__(GmkConverter)  # no I/O; _convert_single_action is self-contained
        act = GmkAction(action_kind=5, argument_values=["7"])
        out = conv._convert_single_action(act)
        assert out["action"] == "repeat"
        assert out["parameters"].get("times") == "7"

    def test_other_control_flow_markers_still_empty(self):
        from importers.gmk_converter import GmkConverter
        from importers.gmk_parser import GmkAction
        conv = GmkConverter.__new__(GmkConverter)
        for kind, name in ((1, "start_block"), (2, "end_block"), (4, "exit_event")):
            out = conv._convert_single_action(GmkAction(action_kind=kind))
            assert out == {"action": name, "parameters": {}}


# ============================================================================
# Kivy export (#18 if_object_exists must gate nested actions)
# ============================================================================

class TestKivyIfObjectExistsGates:
    """#18 — if_object_exists returned a bare expression, so its then_actions
    ran unconditionally. It must open an `if` block like if_condition."""

    def test_then_actions_are_indented_under_an_if(self):
        from export.Kivy.code_generator import ActionCodeGenerator
        gen = ActionCodeGenerator(base_indent=0)
        gen.process_action({
            "action": "if_object_exists",
            "parameters": {
                "object": "enemy",
                "then_actions": [{"action": "restart_room", "parameters": {}}],
            },
        })
        code = gen.get_code()
        lines = [ln for ln in code.splitlines() if ln.strip()]
        # First line opens the if; the gated body follows, indented deeper.
        assert lines[0].startswith("if ") and "object_exists('enemy')" in lines[0]
        assert len(lines) >= 2, "then_action was not emitted under the if"
        if_indent = len(lines[0]) - len(lines[0].lstrip())
        body_indent = len(lines[1]) - len(lines[1].lstrip())
        assert body_indent > if_indent

    def test_not_flag_negates(self):
        from export.Kivy.code_generator import ActionCodeGenerator
        gen = ActionCodeGenerator(base_indent=0)
        gen.process_action({
            "action": "if_object_exists",
            "parameters": {"object": "enemy", "not_flag": True,
                           "then_actions": [{"action": "restart_room", "parameters": {}}]},
        })
        code = gen.get_code()
        assert "if not self.scene.object_exists('enemy'):" in code


# ============================================================================
# Room save data-loss (#15 emptying a room must not resurrect instances)
# ============================================================================

class TestRoomSaveRespectsEmptied:
    """#15 — _save_rooms_to_files preserved the file's instances whenever the
    in-memory list was empty, so emptying a room then saving resurrected the
    old instances. Preservation must only apply to rooms NOT loaded this
    session (empty == 'not loaded', not 'user emptied it')."""

    def _setup(self, tmp_path):
        import json
        from core.project_manager import ProjectManager
        pm = ProjectManager()
        rooms_dir = tmp_path / "rooms"
        rooms_dir.mkdir()
        # File on disk has one instance.
        (rooms_dir / "room1.json").write_text(json.dumps(
            {"name": "room1", "instances": [{"object_name": "obj_a", "x": 0, "y": 0}]}))
        # In-memory room is now empty (user deleted everything).
        pm.current_project_data = {"assets": {"rooms": {
            "room1": {"name": "room1", "instances": []}}}}
        return pm, tmp_path

    def _saved_instances(self, tmp_path):
        import json
        return json.loads((tmp_path / "rooms" / "room1.json").read_text())["instances"]

    def test_emptied_loaded_room_saves_empty(self, tmp_path):
        pm, path = self._setup(tmp_path)
        pm._rooms_loaded_this_session = {"room1"}  # was loaded -> empty is authoritative
        pm._save_rooms_to_files(path)
        assert self._saved_instances(path) == []

    def test_unloaded_room_preserves_file_instances(self, tmp_path):
        pm, path = self._setup(tmp_path)
        pm._rooms_loaded_this_session = set()  # never loaded -> protect against data loss
        pm._save_rooms_to_files(path)
        assert len(self._saved_instances(path)) == 1


# ============================================================================
# Pixel-perfect collision (#12 mask offset must use the FRAME origin)
# ============================================================================

class TestPreciseCollisionMaskOffset:
    """#12 — _precise_refine aligned full-frame masks at the bbox top-left, so
    the overlap offset was wrong by the two sprites' bbox-offset difference.
    Two precise sprites with DIFFERENT bbox offsets are the failing case."""

    def _make(self):
        import pygame
        from runtime.game_runner import GameRunner

        def sprite(px, py):
            surf = pygame.Surface((16, 16), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 0))
            surf.set_at((px, py), (255, 255, 255, 255))
            s = type("S", (), {})()
            s.precise = True
            s.origin_x = s.origin_y = 0
            s.bbox_left, s.bbox_top = px, py
            s.bbox_right, s.bbox_bottom = px + 1, py + 1
            s._mask = pygame.mask.from_surface(surf)
            s.get_mask = lambda idx, _m=s._mask: _m
            return s

        def inst(s, x, y):
            i = type("I", (), {})()
            i.sprite = s; i.x = x; i.y = y
            i.image_index = 0; i.rotation = 0; i.image_angle = 0
            i.scale_x = i.scale_y = 1
            return i

        gr = GameRunner.__new__(GameRunner)  # _precise_refine uses no self state
        return gr, sprite, inst

    def test_overlap_detected_across_different_bbox_offsets(self):
        gr, sprite, inst = self._make()
        s1, s2 = sprite(2, 2), sprite(10, 10)
        # inst1 frame TL (0,0) -> opaque world pixel (2,2);
        # inst2 frame TL (-8,-8) -> opaque world pixel (2,2). They coincide.
        i1, i2 = inst(s1, 0, 0), inst(s2, -8, -8)
        bx1 = i1.x - s1.origin_x + s1.bbox_left   # = 2
        by1 = i1.y - s1.origin_y + s1.bbox_top
        bx2 = i2.x - s2.origin_x + s2.bbox_left   # = 2
        by2 = i2.y - s2.origin_y + s2.bbox_top
        assert gr._precise_refine(i1, bx1, by1, i2, bx2, by2) is True

    def test_non_overlapping_pixels_rejected(self):
        gr, sprite, inst = self._make()
        s1, s2 = sprite(2, 2), sprite(10, 10)
        # Both frames at (0,0): opaque pixels land at world (2,2) and (10,10).
        i1, i2 = inst(s1, 0, 0), inst(s2, 0, 0)
        bx1, by1 = s1.bbox_left, s1.bbox_top
        bx2, by2 = s2.bbox_left, s2.bbox_top
        assert gr._precise_refine(i1, bx1, by1, i2, bx2, by2) is False


# ============================================================================
# load_game instance restore (#10 distinct instances must not collapse)
# ============================================================================

class TestRestoreInstancesDistinctMatch:
    """#10 — _restore_instances matched by object_name with break but never
    consumed the matched instance, so N saved instances of one object all
    restored onto the first one in the room."""

    def test_two_same_object_instances_get_distinct_state(self):
        runner = MockGameRunner()
        e1, e2 = MockInstance("enemy"), MockInstance("enemy")
        e1.x = e1.y = e2.x = e2.y = 0
        runner.current_room.instances = [e1, e2]
        executor = ActionExecutor(game_runner=runner)
        executor._restore_instances([
            {"object_name": "enemy", "x": 100, "y": 100},
            {"object_name": "enemy", "x": 200, "y": 200},
        ])
        got = sorted([(e1.x, e1.y), (e2.x, e2.y)])
        assert got == [(100, 100), (200, 200)]
