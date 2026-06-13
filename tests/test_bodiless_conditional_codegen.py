"""Regression tests for conditional code generation (audit M19).

docs/FULL_AUDIT_2026-06-11.md: _generate_action_code only routed
conditionals through _generate_conditional (which appends 'pass' for empty
bodies) when sub_actions/then_actions/else_actions/actions_list was
non-empty. Otherwise it fell through to the bare template, emitting just
the header line ('if self.x > 5:' or 'for _i in range(3):') with no
indented body — invalid Python. This is exactly the shape a GMK import
produces (test_* gating the next sibling via start_block/end_block, which
render as ''), so View Generated Code showed broken Python and Edit Custom
Code was permanently blocked (every keystroke -> parse error) for that
object. Conditionals now always render a body.
"""

import ast

import pytest

from editors.object_editor.python_code_parser import events_to_python


def _assert_valid_python(code):
    ast.parse(code)  # raises SyntaxError if the generated class is broken


class TestConditionalAlwaysHasBody:
    def test_lone_test_expression_is_valid(self):
        events = {"step": {"actions": [
            {"action": "test_expression", "parameters": {"expression": "self.x > 5"}},
        ]}}
        code = events_to_python("obj", events)
        _assert_valid_python(code)
        assert "pass" in code  # empty body padded

    def test_lone_repeat_is_valid(self):
        events = {"step": {"actions": [
            {"action": "repeat", "parameters": {"times": 3}},
        ]}}
        code = events_to_python("obj", events)
        _assert_valid_python(code)
        assert "for _i in range(3):" in code

    def test_conditional_with_missing_param_is_still_valid(self):
        # A malformed conditional (template param absent) must not produce a
        # comment-only method body, which is a SyntaxError.
        events = {"step": {"actions": [
            {"action": "repeat", "parameters": {}},  # no 'times'
        ]}}
        code = events_to_python("obj", events)
        _assert_valid_python(code)

    def test_gmk_block_marker_shape_is_valid(self):
        # The audit's exact repro: a conditional gating the next sibling via
        # GM start_block/end_block markers (which render as '').
        events = {"step": {"actions": [
            {"action": "test_expression", "parameters": {"expression": "self.x > 5"}},
            {"action": "start_block", "parameters": {}},
            {"action": "set_hspeed", "parameters": {"value": 4}},
            {"action": "end_block", "parameters": {}},
        ]}}
        code = events_to_python("obj", events)
        _assert_valid_python(code)  # pre-fix: 'expected an indented block'

    def test_if_condition_without_then_actions_is_valid(self):
        events = {"step": {"actions": [
            {"action": "if_condition", "parameters": {"condition": "self.lives > 0"}},
        ]}}
        code = events_to_python("obj", events)
        _assert_valid_python(code)

    def test_conditional_with_nested_actions_still_works(self):
        events = {"step": {"actions": [
            {"action": "if_condition",
             "parameters": {"condition": "self.lives > 0",
                            "then_actions": [
                                {"action": "set_hspeed", "parameters": {"value": 2}}]}},
        ]}}
        code = events_to_python("obj", events)
        _assert_valid_python(code)
        assert "self.hspeed = 2" in code
