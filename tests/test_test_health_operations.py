"""Regression test for test_health comparison operators (audit M29).

ACTION_TYPES['test_health'] offered 'less_or_equal'/'greater_or_equal' but the
runtime only matched 'less_equal'/'greater_equal', so selecting either left
result=False forever (e.g. a natural 'health <= 0' death check never fired).
The choices now match the runtime and the runtime also heals the legacy
*_or_equal spellings.
"""

import pytest

from conftest import import_module_directly

_mod = import_module_directly("runtime/action_executor.py")
ActionExecutor = _mod.ActionExecutor


class _Runner:
    def __init__(self, health):
        self.health = health


def _exec(health):
    return ActionExecutor(game_runner=_Runner(health))


class TestHealthComparisons:
    def test_less_equal_true_at_zero(self):
        ex = _exec(0)
        assert ex.execute_test_health_action(None, {"operation": "less_equal", "value": 0}) is True

    def test_greater_equal(self):
        ex = _exec(100)
        assert ex.execute_test_health_action(None, {"operation": "greater_equal", "value": 100}) is True

    def test_legacy_less_or_equal_still_works(self):
        ex = _exec(0)
        assert ex.execute_test_health_action(None, {"operation": "less_or_equal", "value": 0}) is True

    def test_legacy_greater_or_equal_still_works(self):
        ex = _exec(50)
        assert ex.execute_test_health_action(None, {"operation": "greater_or_equal", "value": 10}) is True

    def test_less_equal_false_when_above(self):
        ex = _exec(5)
        assert ex.execute_test_health_action(None, {"operation": "less_equal", "value": 0}) is False


def test_choices_match_runtime_spellings():
    from events.action_types import ACTION_TYPES
    op = next(p for p in ACTION_TYPES["test_health"].parameters if p.name == "operation")
    assert "less_equal" in op.choices
    assert "greater_equal" in op.choices
    assert "less_or_equal" not in op.choices
    assert "greater_or_equal" not in op.choices
