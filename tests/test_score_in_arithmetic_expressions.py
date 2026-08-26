"""score/lives/health were only resolvable as a BARE token equal to the
WHOLE parameter value (e.g. value="score", already fixed for
set_variable/draw_text) — inside a larger arithmetic expression (e.g. a
difficulty ramp like "40 - score/50"), the string contains an operator
and routes through the arithmetic evaluator instead, which had no
concept of these names at all: on desktop, _evaluate_expression's bare-
token substitution only checked hasattr(instance, name), and score lives
on game_runner, not the instance; the token would reach eval() unbound,
raise NameError, and the WHOLE expression would silently default to 0.

Needed for the promo game's Sky Strike level: a set_alarm re-arm interval
that decreases as score rises ("max(15, 40 - score/100)"), so the level
gets harder the longer you survive.

Also needed: max()/min() in the same evaluator (HTML5's gmExpressionValue
already had them; desktop's _evaluate_expression didn't), to clamp the
ramp at a floor without a separate nested if_condition.

Verification tier: desktop via direct ActionExecutor calls; HTML5 via
source-level assertions on engine.js's set_alarm case (gmExpressionValue
itself already supported score/max/min before this session — only the
set_alarm case's own bare `params.steps || 30` needed fixing to actually
route through it).
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


class _FakeGameRunner:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.health = 100
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


def test_desktop_score_resolves_inside_an_arithmetic_expression():
    ex, gr, inst = _executor()
    gr.score = 500
    assert ex._parse_value("40 - score/100", inst) == 35.0


def test_desktop_max_and_min_are_available_in_expressions():
    ex, gr, inst = _executor()
    gr.score = 5000
    # Without a floor this would go deeply negative.
    assert ex._parse_value("max(15, 40 - score/100)", inst) == 15


def test_desktop_difficulty_ramp_decreases_then_floors():
    ex, gr, inst = _executor()
    results = []
    for score in (0, 500, 1000, 2000, 5000):
        gr.score = score
        results.append(ex._parse_value("max(15, 40 - score/100)", inst))
    assert results == [40.0, 35.0, 30.0, 20.0, 15]
    assert results == sorted(results, reverse=True)  # monotonically harder


def test_desktop_lives_and_health_also_resolve_in_expressions():
    ex, gr, inst = _executor()
    gr.lives = 2
    gr.health = 60
    assert ex._parse_value("lives * 10", inst) == 20
    assert ex._parse_value("health / 2", inst) == 30.0


def test_html5_set_alarm_routes_steps_through_gm_expression_value():
    m = re.search(r"case 'set_alarm': \{(.*?)\n            \}", ENGINE, re.S)
    assert m, "set_alarm case not found"
    body = m.group(1)
    assert "gmExpressionValue(String(params.steps" in body
    assert "this.alarms[alarmNum] = Math.trunc(steps);" in body


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
