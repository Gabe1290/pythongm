"""Regression test for B1 of docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md.

Two independent halves of the same anti-pattern, both in
editors/object_editor/blockly/, both `value || default`:

- blockly_generators.js's getInputValue (SAVE direction: blocks -> events) --
  typing 0 into a number block saved the block's DEFAULT: "set gravity 0"
  saved 0.5 (gravity turned ON when the student meant to turn it off).
  (The audit's other named example, "set sprite subimage 0 / speed 0",
  turned out to have a second, separate bug layered on top -- the loader
  never connects a number block to SUBIMAGE/SPEED for set_sprite at all,
  so it's wrong for every value, not just 0; logged as a new finding in
  the audit doc rather than folded into this fix.)
- blockly_workspace.html's setBlockParameters, via connectNumberBlock /
  connectTextBlock (LOAD direction: events -> blocks) -- a project.json
  storing gravity as the JSON NUMBER 0 (not the string "0") loaded the
  STRENGTH field as 0.5 before getInputValue's own fix ever got a chance to
  see a real 0. Found by testing with a native-number payload after the
  save-direction fix alone still left this failing.

A single QWebEngineView drives the REAL
editors/object_editor/blockly/blockly_workspace.html for both directions in
one page load -- creating more than one QWebEngineView per test process has
been observed to segfault here, so every case below shares one page via one
JS round trip rather than one test (and one view) per case.
"""
import json

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

pytest.importorskip("PySide6.QtWebEngineWidgets")

REPO_ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent
PAGE = REPO_ROOT / "editors" / "object_editor" / "blockly" / "blockly_workspace.html"

# (label, events) -- each round-tripped through loadEventsData -> generatePythonCode.
CASES = {
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
}


@pytest.fixture(scope="module")
def round_tripped():
    """One QWebEngineView, one JS call, every CASES entry loaded and
    regenerated -- see the module docstring for why this isn't one
    QWebEngineView per test."""
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


def _params(round_tripped, label):
    return round_tripped[label]["create"]["actions"][0]["parameters"]


class TestZeroValuesSurviveTheRoundTrip:
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
