"""
Regression tests for the Kivy ActionCodeGenerator (audit L21).

L21 — show_message embedded the message into a single-quoted literal with only
a quote-replace, so a trailing backslash escaped the closing quote and an
embedded newline split the generated source — both SyntaxError. repr() emits a
valid Python literal in every case.

The collision tests below pin the call-site CONTRACT for if_collision: x/y are
absolute coordinate expressions defaulting to the instance position (matching
the check_empty sibling and the existing tests in test_exporters.py). M34's
actual defect — check_collision_at being undefined in the generated runtime —
is fixed by defining the method in kivy_exporter.py, not by changing these
coordinate semantics here.

Pure-logic tests: the generator is a plain class, no Qt needed.
"""

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from export.Kivy.code_generator import ActionCodeGenerator


def _gen(actions, event_type="step"):
    g = ActionCodeGenerator(base_indent=0)
    for a in actions:
        g.process_action(a, event_type)
    return g.get_code()


# ---- if_collision call-site contract (absolute coords) --------------------

def test_if_collision_uses_explicit_coords():
    code = _gen([
        {"action": "if_collision",
         "parameters": {"x": "50", "y": "50", "object": "solid"}},
        {"action": "set_vspeed", "parameters": {"speed": "-10"}},
    ])
    assert "self.check_collision_at(50, 50, 'solid')" in code


def test_if_collision_defaults_to_self_position():
    # No x/y given -> probe the instance's own position (self.x/self.y).
    code = _gen([
        {"action": "check_collision", "parameters": {"object": "wall"}},
    ])
    assert "self.check_collision_at(self.x, self.y, 'wall')" in code


def test_if_collision_not_flag_inverts():
    code = _gen([
        {"action": "if_collision",
         "parameters": {"x": "50", "y": "50", "object": "solid",
                        "not_flag": True}},
    ])
    assert "if not self.check_collision_at(50, 50, 'solid'):" in code


def test_generated_collision_block_is_valid_python():
    # The whole emitted suite must parse (guards close, body non-empty).
    code = _gen([
        {"action": "if_collision",
         "parameters": {"x": "50", "y": "50", "object": "solid"}},
        {"action": "set_vspeed", "parameters": {"speed": "-10"}},
    ])
    ast.parse(code)


# ---- L21: show_message escaping -------------------------------------------

def _show_message_line(message):
    code = _gen([{"action": "show_message", "parameters": {"message": message}}])
    return code


def test_show_message_trailing_backslash_is_valid():
    code = _show_message_line("done\\")
    ast.parse(code)  # would be SyntaxError under the old quote-only escape


def test_show_message_embedded_newline_is_valid():
    code = _show_message_line("line one\nline two")
    ast.parse(code)
    # No real newline must leak into the source between the import and the call.
    assert code.count("show_message(") == 1


def test_show_message_single_quote_is_valid():
    code = _show_message_line("it's a trap")
    ast.parse(code)


def test_show_message_double_quote_is_valid():
    code = _show_message_line('say "hi"')
    ast.parse(code)


def test_show_message_roundtrips_text():
    # The generated literal must reconstruct the original message exactly.
    msg = "Bravo!\nNiveau terminé\\"
    code = _show_message_line(msg)
    tree = ast.parse(code)
    # Find the show_message(...) call's single string argument.
    found = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "show_message"):
            arg = node.args[0]
            assert isinstance(arg, ast.Constant)
            found = arg.value
    assert found == msg
