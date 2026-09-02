"""`global.NAME` inside an if_condition "expression" (or the Test
Expression action -- both route through ActionExecutor._eval_bool_expression)
was a silent no-op: `global` is a reserved Python keyword, so
`eval("global.is_host == 1", ...)` is a SyntaxError regardless of what the
namespace contains. The exception was caught, logged, and the condition
just returned False -- no crash, no visible error, the author's branch
simply never took.

Found while authoring samples/reseau_2 (LAN multiplayer v2, Phase 8.2):
docs/MULTIPLAYER_LAN_V2_PLAN.md's own "Core changes" section explicitly
claims "a condition global.player_id == 1 just works" with zero core
change -- true for _parse_value/_evaluate_expression (action PARAMETER
values, e.g. set_variable's value), which already special-case dotted
global references via a completely different, non-eval mini-language.
It was never true for _eval_bool_expression (if_condition's "expression"
condition type), a real Python eval() with no `global` namespace entry
at all -- and no existing sample before this fix ever exercised the
combination (reseau_1's own if_condition expressions are all bare
instance-scope names like "x < 16", never global.*).

Fix: a regex substitution rewrites `global.NAME` to `_global.get('NAME',
0)` before eval() ever sees the expression (`_global` is a namespace key
bound to game_runner.global_variables), matching _parse_value's own
missing-global default of 0. _parse_value/_evaluate_expression are
untouched -- their dotted-global handling already worked correctly; only
this evaluator needed the fix.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.action_executor import ActionExecutor  # noqa: E402


class _FakeGameRunner:
    def __init__(self, **globals_):
        self.score = 0
        self.lives = 3
        self.health = 100
        self.global_variables = dict(globals_)
        self.current_room = None


class _FakeInstance:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.object_name = "test"


def _ex(**globals_):
    return ActionExecutor(game_runner=_FakeGameRunner(**globals_))


def test_bare_global_equality_true():
    ex = _ex(is_host=1)
    assert ex._eval_bool_expression(_FakeInstance(), "global.is_host == 1") is True


def test_bare_global_equality_false():
    ex = _ex(is_host=0)
    assert ex._eval_bool_expression(_FakeInstance(), "global.is_host == 1") is False


def test_global_string_comparison():
    ex = _ex(etat="question")
    assert ex._eval_bool_expression(_FakeInstance(), 'global.etat == "question"') is True
    assert ex._eval_bool_expression(_FakeInstance(), 'global.etat == "fin"') is False


def test_global_not_equal():
    ex = _ex(network_connected=1)
    assert ex._eval_bool_expression(_FakeInstance(), "global.network_connected != 1") is False
    ex2 = _ex(network_connected=0)
    assert ex2._eval_bool_expression(_FakeInstance(), "global.network_connected != 1") is True


def test_missing_global_defaults_to_zero_not_an_error():
    ex = _ex()
    assert ex._eval_bool_expression(_FakeInstance(), "global.never_set == 0") is True
    assert ex._eval_bool_expression(_FakeInstance(), "global.never_set == 1") is False


def test_and_or_combining_multiple_globals():
    ex = _ex(is_host=1, etat="question")
    assert ex._eval_bool_expression(
        _FakeInstance(), 'global.is_host == 1 and global.etat == "question"') is True
    ex2 = _ex(is_host=0, etat="question")
    assert ex2._eval_bool_expression(
        _FakeInstance(), 'global.is_host == 1 and global.etat == "question"') is False


def test_global_mixed_with_self_and_instance_scope():
    ex = _ex(round_no=3)
    inst = _FakeInstance()
    inst.last_round = 2
    assert ex._eval_bool_expression(_FakeInstance(), "global.round_no != self.x") is True


def test_no_syntax_error_logged_for_valid_global_expression(caplog):
    """The original bug: eval() raised SyntaxError, caught silently by the
    broad except Exception -- only an ERROR-level log line hinted at it.
    After the fix, a well-formed global.* expression must not hit that
    except branch at all."""
    import logging
    ex = _ex(is_host=1)
    with caplog.at_level(logging.ERROR):
        result = ex._eval_bool_expression(_FakeInstance(), "global.is_host == 1")
    assert result is True
    assert not any("Error evaluating expression" in r.message for r in caplog.records)


def test_variable_named_similarly_to_global_is_not_mangled():
    """`\\bglobal\\.` must not misfire on an identifier that merely
    CONTAINS "global" without being the literal global.* dotted form."""
    ex = _ex()
    inst = _FakeInstance()
    inst.global_score = 5
    assert ex._eval_bool_expression(inst, "self.global_score == 5") is True


def test_regular_instance_expressions_still_work_unaffected():
    """Non-global expressions (the pre-existing, already-working path) —
    make sure the new substitution doesn't touch them."""
    ex = _ex()
    inst = _FakeInstance()
    inst.x = 10
    assert ex._eval_bool_expression(inst, "x < 16") is True
    assert ex._eval_bool_expression(inst, "x > 16") is False


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
