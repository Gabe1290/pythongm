"""Numeric GameMaker comparison codes (Blockly audit B18,
docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md).

GameMaker stores test_variable/test_score/... operators as integer codes. The
GMK importer translates them now (importers/gmk_mappings.GM_COMPARISON_OPS),
but a project imported before that kept the raw code, and every engine
compares by NAME -- so plateforme_3's dead flying monster capped its fall
speed with operation "2" (greater) and the test was always false. Each
engine now normalises the code at its single action entry point.
"""
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parent.parent

# (code, vspeed, expected) against value 24
CASES = [
    ("0", 24, True), ("0", 23, False),
    ("1", 23, True), ("1", 24, False),
    ("2", 30, True), ("2", 24, False),
    ("3", 24, True), ("3", 25, False),
    ("4", 24, True), ("4", 23, False),
    ("5", 23, True), ("5", 24, False),
]


@pytest.mark.parametrize("code,vspeed,expected", CASES)
def test_desktop_test_variable_understands_numeric_codes(code, vspeed, expected):
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor(game_runner=SimpleNamespace(
        score=0, lives=3, health=100, global_variables={}, current_room=None))
    inst = SimpleNamespace(x=0, y=0, hspeed=0, vspeed=vspeed, object_name="o")
    result = ex.execute_action(inst, {"action": "test_variable", "parameters": {
        "variable": "vspeed", "value": "24", "operation": code}})
    assert result is expected


def test_desktop_test_score_understands_numeric_codes():
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor(game_runner=SimpleNamespace(
        score=50, lives=3, health=100, global_variables={}, current_room=None))
    inst = SimpleNamespace(x=0, y=0, object_name="o")
    assert ex.execute_action(inst, {"action": "test_score", "parameters": {
        "value": "10", "operation": "2"}}) is True


def test_unrelated_actions_keep_their_operation_untouched():
    from runtime.gm_math import normalize_gm_operation
    params = {"operation": "2"}
    assert normalize_gm_operation("set_variable", params) is params


@pytest.mark.parametrize("code,symbol", [("0", "=="), ("1", "<"), ("2", ">"),
                                         ("3", "<="), ("4", ">="), ("5", "!=")])
def test_kivy_emits_the_operator_for_a_numeric_code(code, symbol):
    from export.Kivy.code_generator import ActionCodeGenerator
    g = ActionCodeGenerator(base_indent=0)
    g.process_action({"action": "test_variable", "parameters": {
        "variable": "hspeed", "value": "24", "operation": code}}, "step")
    g.process_action({"action": "set_hspeed", "parameters": {"value": "1"}}, "step")
    if_lines = [ln.strip() for ln in g.get_code().splitlines() if ln.strip().startswith("if ")]
    assert if_lines and f" {symbol} 24" in if_lines[0], if_lines


def test_html5_table_matches_the_importers_and_both_entry_points_use_it():
    """No JS engine in CI: pin the JS copy of the table against the Python
    one, and that executeAction and evaluateCondition both normalise."""
    from importers.gmk_mappings import GM_COMPARISON_OPS, GM_OPERATION_ACTIONS
    js = (REPO / "export/HTML5/templates/engine.js").read_text(encoding="utf-8")
    table = dict(re.findall(r"'(\d)': '(\w+)'", js[js.index("const GM_COMPARISON_OPS"):
                                                    js.index("const GM_OPERATION_ACTIONS")]))
    assert table == GM_COMPARISON_OPS
    actions_src = js[js.index("const GM_OPERATION_ACTIONS"):js.index("function gmNormalizeOperation")]
    assert set(re.findall(r"'(\w+)'", actions_src)) == GM_OPERATION_ACTIONS
    for entry in ("executeAction(action, game) {", "evaluateCondition(action, game) {"):
        body = js[js.index(entry):js.index(entry) + 200]
        assert "gmNormalizeOperation(actionType" in body, entry
