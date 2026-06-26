"""Regression tests for exporting `execute_code` (inline Python) actions to
Kivy (2026-06-26).

The Kivy code generator had NO handler for the execute_code action, so inline
Python authored in the IDE was silently dropped from the export. It now emits
the code verbatim — preserving the block's own indentation (the
_convert_simple_action path strips lines and would flatten nested if/for) —
and makes math/random importable so they resolve like the IDE's exec
namespace. Like the runtime, the code is expected to use self.<attr>.
"""

import ast
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


def _gen(code, event_type="step", base_indent=2):
    from export.Kivy.code_generator import ActionCodeGenerator
    g = ActionCodeGenerator(base_indent=base_indent)
    g.process_action(
        {"action_type": "execute_code", "parameters": {"code": code}},
        event_type,
    )
    return g.get_code()


def _is_valid_python(src):
    # Wrap in a method so the (indented) body is a legal compilation unit.
    wrapper = "class _C:\n    def m(self, other=None):\n" + src + "\n"
    try:
        compile(wrapper, "<gen>", "exec")
        return True
    except SyntaxError:
        return False


def test_simple_code_emitted_verbatim():
    out = _gen("self.x += 5")
    assert "self.x += 5" in out
    assert _is_valid_python(out)


def test_multiline_code_preserves_nested_indentation():
    code = "if self.x > 100:\n    self.x = 0\n    self.hspeed = -self.hspeed"
    out = _gen(code)
    # The nested assignments must stay indented under the if (not flattened).
    lines = [ln for ln in out.split("\n") if ln.strip()]
    if_line = next(ln for ln in lines if "if self.x > 100:" in ln)
    body_line = next(ln for ln in lines if "self.x = 0" in ln)
    if_indent = len(if_line) - len(if_line.lstrip())
    body_indent = len(body_line) - len(body_line.lstrip())
    assert body_indent > if_indent, "nested block lost its indentation"
    assert _is_valid_python(out)


def test_math_is_imported_when_referenced():
    out = _gen("self.dist = math.sqrt(self.x * self.x + self.y * self.y)")
    assert "import math" in out
    assert _is_valid_python(out)


def test_random_is_imported_when_referenced():
    out = _gen("self.x = random.randint(0, 100)")
    assert "import random" in out
    assert _is_valid_python(out)


def test_no_spurious_import_without_reference():
    out = _gen("self.x = self.x + 1")
    assert "import math" not in out
    assert "import random" not in out


def test_empty_code_emits_pass():
    out = _gen("   ")
    assert out.strip() == "pass"
    assert _is_valid_python(out)


def test_execute_code_nests_under_a_preceding_guard():
    """A test_expression guards the next action; execute_code must land
    inside that `if` block, not after it."""
    from export.Kivy.code_generator import ActionCodeGenerator

    g = ActionCodeGenerator(base_indent=2)
    g.process_action(
        {"action_type": "test_expression",
         "parameters": {"expression": "vspeed > 0"}},
        "collision_obj_monstre",
    )
    g.process_action(
        {"action_type": "execute_code", "parameters": {"code": "self.destroy()"}},
        "collision_obj_monstre",
    )
    out = g.get_code()
    lines = [ln for ln in out.split("\n") if ln.strip()]
    if_line = next(ln for ln in lines if ln.lstrip().startswith("if "))
    body_line = next(ln for ln in lines if "self.destroy()" in ln)
    assert (len(body_line) - len(body_line.lstrip())) > \
           (len(if_line) - len(if_line.lstrip())), "execute_code not nested under the guard"
    assert _is_valid_python(out)
