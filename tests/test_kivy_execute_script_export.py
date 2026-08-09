"""Regression tests for exporting `execute_script` (project script calls)
to Kivy.

execute_script had the identical gap execute_code just had (see
tests/test_kivy_execute_code_export.py's module docstring for the full
story): the script body was inlined as literal Python in the generated
method, so a bare local the script assigns (no self.) was just a real
Python local, discarded when the method returned instead of persisting as
an instance attribute. execute_script was ALSO missing `other` and
`keyboard` bindings entirely — unlike execute_code, which at least had
`game`/`instance` bound before this pass.

Fixed the same way: the script body now runs through a real exec() call at
runtime (self/instance/other/game/keyboard/math/random/argument0-4/
argument_count in globals), with leftover locals setattr'd back onto the
instance — mirroring runtime/action_executor.py's
execute_execute_script_action exactly. argument0-4 are still resolved to
real Python expressions at EXPORT time (so a bare instance-var reference in
an argument value keeps working, e.g. arg0="hp" -> `argument0 = self.hp`)
and passed into exec()'s globals as already-computed values.

Tests mostly execute the generated Python for real (compile + exec against
a stub class), matching test_kivy_execute_code_export.py's established
pattern — the only way to actually prove the locals-copied-back mechanism
and the argument-passing both work.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402


def _gen(script_name, code, params=None, event_type="step", base_indent=2):
    g = ActionCodeGenerator(base_indent=base_indent, scripts={script_name: {"code": code}})
    action_params = {"script": script_name}
    action_params.update(params or {})
    g.process_action({"action_type": "execute_script", "parameters": action_params}, event_type)
    return g.get_code()


def _is_valid_python(src):
    wrapper = "class _C:\n    def m(self, other=None):\n" + src + "\n"
    try:
        compile(wrapper, "<gen>", "exec")
        return True
    except SyntaxError:
        return False


_STUB_HEADER = (
    "class _C:\n"
    "    def _script_game(self):\n"
    "        return None\n"
    "    def _check_key(self, key):\n"
    "        return False\n"
)


def _run(**methods_and_bodies):
    src = _STUB_HEADER
    for name, body in methods_and_bodies.items():
        src += f"    def {name}(self, other=None):\n{body}\n"
    ns = {}
    exec(compile(src, "<gen>", "exec"), ns)
    return ns["_C"]()


def test_simple_script_runs_and_mutates_the_instance():
    out = _gen("my_script", "self.x += 5")
    inst = _run(m=out)
    inst.x = 10
    inst.m()
    assert inst.x == 15


def test_bare_local_persists_as_a_real_instance_attribute():
    """The core deliverable, same as execute_code's fix: a bare local (no
    self.) becomes a persistent instance attribute after the call returns."""
    out = _gen("set_hp", "hp = 100")
    inst = _run(m=out)
    inst.m()
    assert inst.hp == 100


def test_arguments_are_bound_and_readable():
    out = _gen("deal_damage", "self.hp -= argument0",
                params={"arg0": "25"})
    inst = _run(m=out)
    inst.hp = 100
    inst.m()
    assert inst.hp == 75


def test_argument_referencing_instance_var_resolves_at_export_time():
    """arg0="hp" must resolve to self.hp (the bare-name rewrite
    _resolve_instance_names already did before this fix and still does),
    not the literal string "hp"."""
    out = _gen("double_hp", "self.doubled = argument0 * 2",
                params={"arg0": "hp"})
    inst = _run(m=out)
    inst.hp = 21
    inst.m()
    assert inst.doubled == 42


def test_missing_arguments_are_none_and_argument_count_reflects_supplied():
    out = _gen("report_args", "self.count = argument_count\nself.a1 = argument1",
                params={"arg0": "5"})
    inst = _run(m=out)
    inst.m()
    assert inst.count == 1
    assert inst.a1 is None


def test_other_bound_only_in_collision_events():
    """execute_script never bound `other` at all before this fix — a
    collision-driven script referencing it raised NameError."""
    out = _gen("apply_damage", "self.hp -= other.damage",
                event_type="collision_with_obj_enemy")
    inst = _run(m=out)
    inst.hp = 100
    other_stub = type("O", (), {"damage": 10})()
    inst.m(other_stub)
    assert inst.hp == 90


def test_other_is_none_outside_a_collision_event():
    out = _gen("check_other", "self.other_was_none = other is None")
    inst = _run(m=out)
    inst.m()
    assert inst.other_was_none is True


def test_keyboard_check_is_wired_to_the_check_key_method():
    """execute_script never bound `keyboard` at all before this fix."""
    out = _gen("jump_check", 'self.jumped = keyboard.check("space")')
    src = (
        "class _C:\n"
        "    def _script_game(self):\n"
        "        return None\n"
        "    def _check_key(self, key):\n"
        "        return str(key).lower() == 'space'\n"
        f"    def m(self, other=None):\n{out}\n"
    )
    ns = {}
    exec(compile(src, "<gen>", "exec"), ns)
    inst = ns["_C"]()
    inst.m()
    assert inst.jumped is True


def test_math_and_random_resolve_and_work():
    out = _gen("compute", "self.dist = math.sqrt(9)\nself.roll = random.randint(5, 5)")
    inst = _run(m=out)
    inst.m()
    assert inst.dist == 3.0
    assert inst.roll == 5


def test_syntax_error_in_script_is_caught_not_a_crash():
    out = _gen("broken", "this is not valid python (((")
    inst = _run(m=out)
    inst.m()  # must not raise


def test_missing_script_prints_and_emits_pass():
    g = ActionCodeGenerator(base_indent=2, scripts={})
    g.process_action(
        {"action_type": "execute_script", "parameters": {"script": "does_not_exist"}},
        "step",
    )
    out = g.get_code()
    assert "not found or empty" in out
    assert "pass" in out
    assert _is_valid_python(out)


def test_execute_script_nests_under_a_preceding_guard():
    g = ActionCodeGenerator(base_indent=2, scripts={"s": {"code": "self.destroyed = True"}})
    g.process_action(
        {"action_type": "test_expression", "parameters": {"expression": "vspeed > 0"}},
        "collision_obj_monstre",
    )
    g.process_action(
        {"action_type": "execute_script", "parameters": {"script": "s"}},
        "collision_obj_monstre",
    )
    out = g.get_code()
    lines = [ln for ln in out.split("\n") if ln.strip()]
    if_line = next(ln for ln in lines if ln.lstrip().startswith("if "))
    body_line = next(ln for ln in lines if "try:" in ln)
    assert (len(body_line) - len(body_line.lstrip())) > \
           (len(if_line) - len(if_line.lstrip())), "execute_script not nested under the guard"
    assert _is_valid_python(out)
