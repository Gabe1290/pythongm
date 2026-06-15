"""Regression tests for audit L10 — string params interpolated into quoted
code templates without escaping produced syntactically invalid generated code.

A message/sound/sprite/room/object name containing a double quote, backslash,
or newline must still generate valid Python (and round-trip back to the same
value). Pure logic — no Qt needed.
"""

import ast

import pytest

from editors.object_editor.python_code_parser import (
    ActionsToPythonGenerator,
    events_to_python,
    python_to_events,
)


# (action_name, parameters) pairs whose templates embed a string param inside
# a double-quoted literal. Each tricky value should still parse.
TRICKY = '''He said "hi" \\ and a
newline'''


@pytest.mark.parametrize("action,params", [
    ("display_message", {"message": TRICKY}),
    ("show_message", {"message": TRICKY}),
    ("play_sound", {"sound": TRICKY}),
    ("set_sprite", {"sprite": TRICKY}),
    ("goto_room", {"room": TRICKY}),
    ("room_goto", {"room": TRICKY}),
    ("create_instance", {"object": TRICKY, "x": 1, "y": 2}),
    ("move_grid", {"direction": 'a"b', "grid_size": 32}),
    ("draw_score", {"x": 1, "y": 2, "caption": 'Score "x"'}),
    ("if_collision_at", {"x": 0, "y": 0, "object_type": 'wall"x'}),
])
def test_generated_action_is_valid_python(action, params):
    gen = ActionsToPythonGenerator()
    code = gen._generate_action_code({"action": action, "parameters": params})
    # The template path for conditionals emits an indented body — that's
    # still valid; for the simple actions it's a single line. Parse it.
    ast.parse(code)


def test_if_can_push_escapes_object_and_direction():
    gen = ActionsToPythonGenerator()
    code = gen._generate_action_code({
        "action": "if_can_push",
        "parameters": {"object_type": 'wall"x', "direction": 'left"y'},
    })
    ast.parse(code)


def test_thymio_button_check_escapes_button_name():
    gen = ActionsToPythonGenerator()
    for action in ("thymio_if_button_pressed", "thymio_if_button_released"):
        code = gen._generate_action_code({
            "action": action,
            "parameters": {"button": 'forward"x'},
        })
        ast.parse(code)


def test_if_condition_instance_count_and_key_pressed_escaped():
    gen = ActionsToPythonGenerator()
    # instance_count with a quote in the object name
    code = gen._generate_action_code({
        "action": "if_condition",
        "parameters": {"condition_type": "instance_count",
                       "object_name": 'enemy"x', "operator": ">", "value": 0},
    })
    ast.parse(code)
    # key_pressed with a quote in the key
    code = gen._generate_action_code({
        "action": "if_condition",
        "parameters": {"condition_type": "key_pressed", "key": 'a"b'},
    })
    ast.parse(code)


def test_message_round_trips_through_full_class():
    msg = 'Press "SPACE" to jump'
    events = {"create": {"actions": [
        {"action": "display_message", "parameters": {"message": msg}}]}}
    code = events_to_python("Player", events)
    # The whole class must be parseable (the bug made it a SyntaxError).
    ast.parse(code)
    parsed, errors = python_to_events(code)
    assert errors == []
    got = parsed["create"]["actions"][0]["parameters"]["message"]
    assert got == msg


def test_plain_names_are_unchanged():
    """No regression for ordinary identifier-like names: output is byte-for-byte
    what it was before the escaping change."""
    gen = ActionsToPythonGenerator()
    assert gen._generate_action_code(
        {"action": "play_sound", "parameters": {"sound": "jump"}}
    ) == 'game.play_sound("jump")'
    assert gen._generate_action_code(
        {"action": "goto_room", "parameters": {"room": "level1"}}
    ) == 'game.goto_room("level1")'
    assert gen._generate_action_code(
        {"action": "set_sprite", "parameters": {"sprite": "spr_player"}}
    ) == 'self.sprite_index = "spr_player"'
