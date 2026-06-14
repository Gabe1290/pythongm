"""Regression test for python_code_parser string escaping (audit L10).

String parameters (message/sound/sprite/room/object names) were interpolated
into double-quoted code templates without escaping, so a quote, backslash or
newline produced syntactically invalid generated Python — breaking View
Generated Code and Edit Custom Code mode.
"""

import ast

import pytest

from editors.object_editor.python_code_parser import (
    ActionsToPythonGenerator, _escape_double_quoted,
)


def _gen(action):
    return ActionsToPythonGenerator()._generate_action_code(action)


@pytest.mark.parametrize("message", [
    'plain',
    'He said "hi"',
    'trailing backslash\\',
    'line one\nline two',
    'tab\there',
])
def test_show_message_generates_valid_python(message):
    code = _gen({"action": "display_message", "parameters": {"message": message}})
    ast.parse(code)  # must not raise SyntaxError


def test_quoted_room_and_object_names():
    for action, key in [("goto_room", "room"), ("create_instance", "object")]:
        params = {key: 'weird"name'}
        if action == "create_instance":
            params.update({"x": 0, "y": 0})
        ast.parse(_gen({"action": action, "parameters": params}))


def test_escape_helper():
    assert _escape_double_quoted('a"b') == 'a\\"b'
    assert _escape_double_quoted('a\\b') == 'a\\\\b'
    assert _escape_double_quoted('a\nb') == 'a\\nb'


def test_plain_value_unchanged():
    # A normal numeric/expression value must round-trip unescaped.
    assert _escape_double_quoted('other.x + 16') == 'other.x + 16'
