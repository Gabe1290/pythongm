"""Regression tests for docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md that drive the
REAL editors/object_editor/blockly/blockly_workspace.html headlessly, rather
than reimplementing its save/load logic in Python.

**All such tests live in this ONE file, sharing ONE QWebEngineView fixture.**
Creating more than one QWebEngineView per pytest process has been observed to
segfault here -- confirmed the hard way: splitting B1's and B2's real-page
tests into two separate module-scoped-fixture files worked fine individually,
then segfaulted every time pytest selected both in one run (`-k blockly`
alone was enough, no other files needed). If a future finding (B3, B4, ...)
needs its own real-page round trip, add its CASES entries and test class
HERE -- don't start a new file with its own fixture.

## B1 -- Typing 0 gives the default instead

Two independent halves of the same `value || default` anti-pattern:
- blockly_generators.js's getInputValue (SAVE: blocks -> events) -- typing 0
  into a number block saved the block's DEFAULT: "set gravity 0" saved 0.5
  (gravity turned ON when the student meant to turn it off).
- blockly_workspace.html's setBlockParameters, via connectNumberBlock /
  connectTextBlock (LOAD: events -> blocks) -- a project.json storing gravity
  as the JSON NUMBER 0 (not the string "0") loaded the STRENGTH field as 0.5
  before getInputValue's own fix ever got a chance to see a real 0 (the 98
  bundled samples all store parameters as strings, where "0" is truthy, so
  this half never showed up in the audit tool's own sample-based round trip).

(The audit's other named B1 example, "set sprite subimage 0 / speed 0",
turned out to have a second, separate bug layered on top -- the loader never
connects a number block to SUBIMAGE/SPEED for set_sprite at all, so it's
wrong for every value, not just 0; logged as B10 in the audit doc.)

## B2 -- Conditions lose their condition and nested actions

if_condition and test_variable had no entry in the loader's
actionToBlockType, so an authored object loaded them as the generic
custom_if_condition / custom_test_variable block -- which has no DO/ELSE
statement input at all (registerCustomBlocks only knows number/choice/
boolean/string fields). The condition AND every nested then/else action
vanished the moment the object synced into Blockly: round-tripping either
action through the real page produced zero actions, not even a lossy
placeholder. if_next_room_exists / if_previous_room_exists were already
loadable but had no ELSE statement input, so an authored else_actions
(which the runtime genuinely executes -- runtime/action_room.py's
_dispatch_room_test) was silently dropped.

Known, documented remaining gap, NOT fixed: if_condition's hand-written
block only has fields for condition_type='instance_count' -- loading any
other condition_type (expression, key, ...) now preserves the nested
actions, but the condition itself reverts to instance_count. test_expression
and if_collision_at have no hand-written block at all and are untouched by
this fix (see the audit doc).
"""
import json

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

pytest.importorskip("PySide6.QtWebEngineWidgets")

REPO_ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent
PAGE = REPO_ROOT / "editors" / "object_editor" / "blockly" / "blockly_workspace.html"

# (label, events) -- each round-tripped through loadEventsData -> generatePythonCode.
# Keep labels unique across B1/B2/future sections; they share one namespace.
CASES = {
    # --- B1 ---
    "gravity_zero_numeric": {"create": {"actions": [
        {"action": "set_gravity", "parameters": {"direction": 270, "gravity": 0}}]}},
    "gravity_zero_string": {"create": {"actions": [
        {"action": "set_gravity", "parameters": {"direction": "270", "gravity": "0"}}]}},
    "gravity_nonzero_control": {"create": {"actions": [
        {"action": "set_gravity", "parameters": {"direction": 270, "gravity": 0.8}}]}},
    "grid_size_zero": {"create": {"actions": [
        {"action": "snap_to_grid", "parameters": {"grid_size": 0}}]}},
    "move_direction_speed_zero": {"create": {"actions": [
        {"action": "start_moving_direction", "parameters": {"directions": 0, "speed": 0}}]}},
    "alpha_zero": {"create": {"actions": [
        {"action": "set_alpha", "parameters": {"alpha": 0}}]}},
    # --- B2 ---
    "if_condition": {"create": {"actions": [
        {"action": "if_condition", "parameters": {
            "condition_type": "instance_count", "object_name": "obj_coin",
            "operator": "==", "value": "0",
            "then_actions": [{"action": "set_score", "parameters": {"value": "10", "relative": False}}],
            "else_actions": [{"action": "set_lives", "parameters": {"value": "1", "relative": True}}]}}]}},
    "if_condition_no_else": {"create": {"actions": [
        {"action": "if_condition", "parameters": {
            "condition_type": "instance_count", "object_name": "obj_coin",
            "operator": "==", "value": "0",
            "then_actions": [{"action": "set_score", "parameters": {"value": "10", "relative": False}}],
            "else_actions": []}}]}},
    "test_variable": {"create": {"actions": [
        {"action": "test_variable", "parameters": {
            "variable": "score", "scope": "sel", "operation": "greater", "value": "5",
            "then_actions": [{"action": "set_score", "parameters": {"value": "1", "relative": True}}],
            "else_actions": [{"action": "set_lives", "parameters": {"value": "1", "relative": True}}]}}]}},
    "test_variable_global_scope": {"create": {"actions": [
        {"action": "test_variable", "parameters": {
            "variable": "wave", "scope": "global", "operation": "equal", "value": "3",
            "then_actions": [{"action": "restart_room", "parameters": {}}],
            "else_actions": []}}]}},
    "if_next_room_exists_with_else": {"create": {"actions": [
        {"action": "if_next_room_exists", "parameters": {
            "then_actions": [{"action": "next_room", "parameters": {}}],
            "else_actions": [{"action": "restart_room", "parameters": {}}]}}]}},
    "if_previous_room_exists_with_else": {"create": {"actions": [
        {"action": "if_previous_room_exists", "parameters": {
            "then_actions": [{"action": "previous_room", "parameters": {}}],
            "else_actions": [{"action": "restart_room", "parameters": {}}]}}]}},
}


@pytest.fixture(scope="module")
def round_tripped():
    """One QWebEngineView, one JS call, every CASES entry loaded and
    regenerated -- see the module docstring for why this isn't one
    QWebEngineView per test (or per test file)."""
    from PySide6.QtCore import QUrl, QTimer
    from PySide6.QtWidgets import QApplication
    from PySide6.QtWebEngineWidgets import QWebEngineView

    app = QApplication.instance() or QApplication([])
    view = QWebEngineView()
    result = {}

    js = """(function(cases){
        var out = {};
        for (var k in cases) {
            loadEventsData(cases[k]);
            out[k] = JSON.parse(generatePythonCode());
        }
        return JSON.stringify(out);
    })(%s)""" % json.dumps(CASES)

    def loaded(_ok):
        view.page().runJavaScript(js, done)

    def done(r):
        result["after"] = json.loads(r) if r else None
        app.quit()

    view.loadFinished.connect(loaded)
    view.load(QUrl.fromLocalFile(str(PAGE)))
    QTimer.singleShot(20000, app.quit)
    app.exec()
    if result.get("after") is None:
        pytest.fail("Blockly page did not finish (timeout or unparseable result)")
    return result["after"]


def _action(round_tripped, label):
    actions = round_tripped[label]["create"]["actions"]
    assert len(actions) == 1, f"{label}: expected 1 action, got {actions!r}"
    return actions[0]


def _params(round_tripped, label):
    return _action(round_tripped, label)["parameters"]


class TestB1ZeroValuesSurviveTheRoundTrip:
    def test_gravity_zero_as_a_json_number_is_not_replaced_by_the_default(self, round_tripped):
        gravity = _params(round_tripped, "gravity_zero_numeric")["gravity"]
        assert float(gravity) == 0.0, f"gravity 0 (number) became {gravity!r} (default is 0.5)"

    def test_gravity_zero_as_a_json_string_is_not_replaced_by_the_default(self, round_tripped):
        gravity = _params(round_tripped, "gravity_zero_string")["gravity"]
        assert float(gravity) == 0.0, f"gravity '0' (string) became {gravity!r} (default is 0.5)"

    def test_a_genuinely_nonzero_value_still_round_trips(self, round_tripped):
        """Guard against a fix that breaks the common case while fixing 0."""
        gravity = _params(round_tripped, "gravity_nonzero_control")["gravity"]
        assert float(gravity) == 0.8

    def test_grid_size_zero_is_not_replaced_by_the_default(self, round_tripped):
        grid_size = _params(round_tripped, "grid_size_zero")["grid_size"]
        assert float(grid_size) == 0.0, f"grid_size 0 became {grid_size!r} (default is 32)"

    def test_move_direction_speed_zero_is_not_replaced_by_the_default(self, round_tripped):
        speed = _params(round_tripped, "move_direction_speed_zero")["speed"]
        assert float(speed) == 0.0, f"speed 0 became {speed!r} (default is 4)"

    def test_alpha_zero_fully_transparent_is_not_replaced_by_the_default(self, round_tripped):
        """alpha=0 (fully transparent) is a real, meaningful value, not a
        placeholder -- the default is opaque (1.0)."""
        alpha = _params(round_tripped, "alpha_zero")["alpha"]
        assert float(alpha) == 0.0, f"alpha 0 became {alpha!r} (default is 1.0)"


class TestB2ConditionsPreserveNestedActions:
    def test_if_condition_preserves_condition_then_and_else(self, round_tripped):
        params = _params(round_tripped, "if_condition")
        assert params["object_name"] == "obj_coin"
        assert params["operator"] == "=="
        assert float(params["value"]) == 0.0
        assert params["then_actions"] == [{"action": "set_score", "parameters": {"value": 10, "relative": False}}]
        assert params["else_actions"] == [{"action": "set_lives", "parameters": {"value": 1, "relative": True}}]

    def test_if_condition_with_no_else_leaves_it_empty_not_lost(self, round_tripped):
        params = _params(round_tripped, "if_condition_no_else")
        assert params["else_actions"] == []
        assert len(params["then_actions"]) == 1

    def test_test_variable_preserves_variable_operation_then_and_else(self, round_tripped):
        params = _params(round_tripped, "test_variable")
        assert params["variable"] == "score"
        assert params["scope"] == "sel"
        assert params["operation"] == "greater"
        assert float(params["value"]) == 5.0
        assert params["then_actions"] == [{"action": "set_score", "parameters": {"value": 1, "relative": True}}]
        assert params["else_actions"] == [{"action": "set_lives", "parameters": {"value": 1, "relative": True}}]

    def test_test_variable_global_scope_prefix_round_trips(self, round_tripped):
        """The VARIABLE field reconstructs the 'global.' prefix
        parseScopedVariable strips on save -- a scope mismatch here would
        silently redirect the comparison to the wrong variable."""
        params = _params(round_tripped, "test_variable_global_scope")
        assert params["variable"] == "wave"
        assert params["scope"] == "global"

    def test_if_next_room_exists_preserves_else_actions(self, round_tripped):
        """The runtime genuinely executes else_actions here
        (action_room.py's _dispatch_room_test) -- this isn't cosmetic."""
        params = _params(round_tripped, "if_next_room_exists_with_else")
        assert params["then_actions"] == [{"action": "next_room", "parameters": {}}]
        assert params["else_actions"] == [{"action": "restart_room", "parameters": {}}]

    def test_if_previous_room_exists_preserves_else_actions(self, round_tripped):
        params = _params(round_tripped, "if_previous_room_exists_with_else")
        assert params["then_actions"] == [{"action": "previous_room", "parameters": {}}]
        assert params["else_actions"] == [{"action": "restart_room", "parameters": {}}]
