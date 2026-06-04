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
        assert out["key"] == "Space"
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
