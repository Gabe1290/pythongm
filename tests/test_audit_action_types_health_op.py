"""Regression test for audit finding M29.

test_health declared operation choices 'less_or_equal'/'greater_or_equal'
that no runtime branch in execute_test_health_action matches, so selecting
either silently left the conditional always False. Every sibling conditional
(test_score/test_lives/test_instance_count/test_variable) and the runtime use
the canonical 'less_equal'/'greater_equal' spelling.
"""

from events.action_types import ACTION_TYPES


def _operation_choices(action_name):
    action = ACTION_TYPES[action_name]
    for param in action.parameters:
        if param.name == "operation":
            return list(param.choices)
    raise AssertionError(f"{action_name} has no 'operation' parameter")


def test_test_health_uses_canonical_comparison_spellings():
    choices = _operation_choices("test_health")
    assert choices == ["equal", "less", "greater", "less_equal", "greater_equal", "not_equal"]


def test_no_or_equal_misspelling_remains():
    choices = _operation_choices("test_health")
    assert "less_or_equal" not in choices
    assert "greater_or_equal" not in choices


def test_test_health_matches_sibling_conditionals():
    health = _operation_choices("test_health")
    for sibling in ("test_score", "test_lives", "test_instance_count"):
        assert _operation_choices(sibling) == health, sibling
