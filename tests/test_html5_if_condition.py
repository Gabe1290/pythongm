"""HTML5 export — if_condition/if_variable's condition_type dispatch was a
no-op stub, so every if_condition action (a first-class registered action;
runtime/action_executor.py's execute_if_condition_action fully implements
all seven condition_types) silently always took the else branch on this
export target only.

Found while adding score to the promo game's block-world level: its
pre-existing "reach the beacon" win condition
(condition_type: "expression") never actually fired on the HTML5 export --
walking to the beacon's exact trigger coordinates left won/score
unchanged, confirmed via a real headless-Chromium run before this fix and
won=1/score=100 after it. Same root cause, same fix, as the H1 finding
already covered by test_html5_conditionals.py for test_expression/
check_empty/etc. -- a DIFFERENT switch statement (if_condition dispatches
through condition_type as a *sub*-parameter, not the action name itself),
so it needed its own case rather than falling under that fix.

Landmine this file's own first draft hit: the stub lived in TWO switch
statements that both mention 'if_condition' -- executeAction's own switch
(reached only if the earlier nested-format then_actions/else_actions
intercept in executeAction somehow misses it -- effectively dead code) and
evaluateCondition's switch (the one actually invoked for a nested-format
conditional). Fixing the executeAction copy first looked plausible (it
compiled, structurally matched, cost real debugging time) but never fired,
since nothing routes execution there for a normal if_condition with
then_actions. The real fix belongs in evaluateCondition; the executeAction
copy is now a documented-unreachable no-op, matching its pre-fix shape.

Verification tier, per this repo's "no Node in CI" convention (matching
test_html5_conditionals.py): source-level assertions on the generated
engine.js. The behavioural proof is a real headless-Chromium run during
development (Playwright, not a CI dependency): a fresh export's
bw_obj_person, teleported to the beacon's exact (416, 128) trigger
coordinates and given one evaluateCondition/onStep call, went from
won=0/score=0 (pre-fix, matching every play session before this fix) to
won=1/score=100 (post-fix).
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def _method_body(name):
    m = re.search(r"    " + re.escape(name) + r"\([^)]*\)\s*\{(.*?)\n    \}\n\n    [a-zA-Z]",
                  ENGINE, re.S)
    assert m, f"{name} not found"
    return m.group(1)


def test_evaluate_condition_dispatches_condition_type():
    """The real fix: evaluateCondition's OWN 'if_condition'/'if_variable'
    case, not executeAction's (a different, unreachable-in-practice
    switch)."""
    body = _method_body("evaluateCondition")
    assert "case 'if_condition':" in body
    assert "case 'if_variable':" in body
    assert "const conditionType = params.condition_type" in body


def test_evaluate_condition_implements_the_condition_types():
    body = _method_body("evaluateCondition")
    for case in ("case 'expression'", "case 'variable_compare'",
                 "case 'instance_count'", "case 'position_check'",
                 "case 'random_chance'", "case 'collision_check'"):
        assert case in body, f"{case} not implemented in evaluateCondition's if_condition dispatch"


def test_expression_condition_type_delegates_to_gm_expression_value():
    body = _method_body("evaluateCondition")
    assert "gmExpressionValue(params.expression, this, game)" in body


def test_execute_action_copy_is_a_documented_noop_not_a_second_impl():
    """Guards against re-introducing a second, dead implementation in
    executeAction's switch -- the landmine this file's docstring
    describes. Only evaluateCondition's copy may implement condition_type
    dispatch."""
    body = _method_body("executeAction")
    exec_if_block = re.search(
        r"case 'if_condition':\s*\n\s*case 'if_variable':(.*?)case 'destroy_instance'",
        body, re.S)
    assert exec_if_block, "if_condition case not found in executeAction"
    assert "params.condition_type" not in exec_if_block.group(1)
    assert "switch (conditionType)" not in exec_if_block.group(1)
    assert "Unreachable in practice" in exec_if_block.group(1)


def test_gm_compare_op_helper_supports_symbol_and_word_operators():
    m = re.search(r"function gmCompareOp\(left, operator, right\)\s*\{(.*?)\n\}", ENGINE, re.S)
    assert m, "gmCompareOp not found"
    body = m.group(1)
    for op in ("'=='", "'!='", "'<'", "'>'", "'<='", "'>='",
               "'equal'", "'not_equal'", "'less'", "'greater'"):
        assert op in body, f"{op} not handled in gmCompareOp"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
