"""The promo game's per-level hub score badges are synced every step via
`set_variable(global.score_<level>, value: "score", relative: false)`
(a plain overwrite). Sky Strike and the side-scroller both have a
mid-level restart that resets game.score to 0 (no_more_lives ->
restart_game for Sky Strike; the obstacle-collision handler's
restart_room for the side-scroller) — the OTHER four levels have no
restart mechanic, so their score only ever climbs monotonically.

A plain overwrite sync happily propagates that momentary 0 into the
global the instant the level resets, so if the player leaves for the
hub anywhere near a restart (Sky Strike's no_more_lives, in particular,
resets score then very shortly returns to the hub), the badge shows 0
instead of the run's actual achieved score.

Fix: the sync expression became a high-water mark,
"max(global.score_<level>, score)", so a momentary reset can never
lower what the hub displays — only a genuinely higher score updates it.
This needed two small engine capabilities that didn't exist yet:
max()/min() weren't routed to at all in desktop's expression evaluator
(added to the safe namespace in an earlier session turn, but the ROUTING
check that decides whether to even invoke the evaluator only recognized
random/irandom/choose as function calls — "max(a, b)" has no arithmetic
operator, so it fell through unevaluated as a literal string); and
HTML5's set_variable only ever special-cased a bare "score"/"lives"/
"health" token or a literal number — a general expression like
"max(global.X, score)" was stored as-is, never evaluated, and needed
`global` exposed in gmExpressionValue's scope (it had self/other/score/
max/min already, but no way to read a global by name).

Verification: desktop via direct ActionExecutor calls; HTML5 via source-
level assertions plus a real headless-Chromium run against the actual
exported promo game reproducing the exact reported scenario (score
climbs, an in-level restart resets it to 0, the hub-facing global must
not drop).
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Desktop
# ---------------------------------------------------------------------------

class _FakeGameRunner:
    def __init__(self):
        self.score = 0
        self.global_variables = {}


class _FakeInstance:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.object_name = "test"


def _executor():
    from runtime.action_executor import ActionExecutor
    gr = _FakeGameRunner()
    return ActionExecutor(game_runner=gr), gr, _FakeInstance()


def test_desktop_max_call_with_no_arithmetic_operator_still_routes_to_the_evaluator():
    """"max(a, b)" alone has no + - * / % character — the routing check
    that decides whether _parse_value even calls _evaluate_expression
    must also recognize a bare function call, or this returns the raw
    string unevaluated."""
    ex, gr, inst = _executor()
    gr.global_variables["score_x"] = 300
    gr.score = 0
    assert ex._parse_value("max(global.score_x, score)", inst) == 300


def test_desktop_high_water_mark_survives_a_score_reset():
    ex, gr, inst = _executor()
    gr.score = 400
    gr.global_variables["score_skystrike"] = ex._parse_value(
        "max(global.score_skystrike, score)", inst)
    assert gr.global_variables["score_skystrike"] == 400

    gr.score = 0  # simulated no_more_lives -> restart_game
    gr.global_variables["score_skystrike"] = ex._parse_value(
        "max(global.score_skystrike, score)", inst)
    assert gr.global_variables["score_skystrike"] == 400  # NOT wiped to 0


def test_desktop_a_genuinely_higher_score_still_updates():
    ex, gr, inst = _executor()
    gr.global_variables["score_skystrike"] = 400
    gr.score = 550
    result = ex._parse_value("max(global.score_skystrike, score)", inst)
    assert result == 550


# ---------------------------------------------------------------------------
# HTML5
# ---------------------------------------------------------------------------

def test_html5_gm_expression_value_exposes_global():
    # global is a defaulting Proxy over game.globalVariables (see
    # test_html5_undefined_global_in_expressions.py for why: a bare
    # `|| {}` read left a never-set global as `undefined`, and JS
    # arithmetic on `undefined` produces NaN rather than Python's
    # graceful default-to-0).
    m = re.search(r"function gmExpressionValue\(expr, inst, game\) \{(.*?)\n\}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "global: new Proxy(" in body
    assert "game.globalVariables" in body


def test_html5_set_variable_routes_expressions_through_gm_expression_value():
    m = re.search(r"case 'set_variable': \{(.*?)\n            \}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "gmExpressionValue(trimmed, this, game)" in body


def test_html5_parse_num_param_routing_unaffected():
    """Regression guard: the set_variable change must not have touched
    parseNumParam's own, separate expression path."""
    m = re.search(r"function parseNumParam\(value, inst, fallback\) \{(.*?)\n\}", ENGINE, re.S)
    assert m
    assert "Function(" in m.group(1)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
