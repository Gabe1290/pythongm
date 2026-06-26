"""Regression test: exported Kivy conditions must resolve bare instance
variable names (vspeed, y, x, custom vars) to self.<name>.

User-reported (2026-06-26): an exported platformer crashed every frame with

    File ".../objects/obj_pingus.py", line 107, in on_collision_obj_monstre
      if vspeed > 0 and y < other.y+8:
    NameError: name 'vspeed' is not defined

The IDE runtime evaluates such conditions via _eval_bool_expression, whose
namespace is seeded with the instance's attributes (x, y, hspeed, vspeed,
custom vars) — so bare names resolve there. The Kivy code generator emitted
the author expression verbatim into an `if`, where those names are unbound.

The generator now rewrites bare instance/custom names to self.<name>
(vspeed in GameMaker sign, matching the test_variable conditional), while
leaving already-qualified names (self.x, other.y), the runtime callables
(abs/min/max/round), and the game-global names the export can't map
(score/lives/health/room_*) untouched.
"""

import ast
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


def _R(expr):
    from export.Kivy.code_generator import _resolve_instance_names
    return _resolve_instance_names(expr)


def _equiv(a, b):
    """Compare two expressions by AST so spacing/paren differences don't matter."""
    return ast.dump(ast.parse(a, mode="eval")) == ast.dump(ast.parse(b, mode="eval"))


def test_reported_crash_expression_resolves():
    # vspeed is compared in GameMaker space (sign-flipped), y/other unchanged.
    assert _equiv(_R("vspeed > 0 and y < other.y+8"),
                  "-(self.vspeed) > 0 and self.y < other.y + 8")


def test_bare_instance_vars_get_self_prefix():
    assert _equiv(_R("x > 100"), "self.x > 100")
    assert _equiv(_R("hspeed != 0 or speed > 2"),
                  "self.hspeed != 0 or self.speed > 2")


def test_custom_instance_variable_resolves():
    assert _equiv(_R("my_counter >= 3"), "self.my_counter >= 3")


def test_already_qualified_names_untouched():
    assert _equiv(_R("self.vspeed > 0 and self.y < other.y"),
                  "self.vspeed > 0 and self.y < other.y")


def test_other_partner_attributes_untouched():
    assert _equiv(_R("other.vspeed < 0"), "other.vspeed < 0")


def test_runtime_callables_preserved():
    assert _equiv(_R("abs(hspeed) > 4"), "abs(self.hspeed) > 4")


def test_game_globals_left_bare():
    # Export has no instance-level score/lives/health — don't emit self.score.
    assert _equiv(_R("lives <= 0"), "lives <= 0")
    assert _equiv(_R("score > 100"), "score > 100")


def test_malformed_expression_returned_unchanged():
    assert _R("this is not python )(") == "this is not python )("


def test_codegen_emits_resolved_condition():
    """End-to-end: a test_expression action emits a self-qualified `if`."""
    from export.Kivy.code_generator import ActionCodeGenerator

    gen = ActionCodeGenerator(base_indent=2)
    gen.process_action(
        {"action_type": "test_expression",
         "parameters": {"expression": "vspeed > 0 and y < other.y+8"}},
        "collision_obj_monstre",
    )
    out = gen.get_code()
    assert "vspeed > 0 and y <" not in out, "bare names leaked into export"
    assert "self.vspeed" in out
    assert "self.y" in out
    assert "other.y" in out
