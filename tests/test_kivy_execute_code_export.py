"""Regression tests for exporting `execute_code` (inline Python) actions to
Kivy.

The Kivy code generator had NO handler for the execute_code action at all
originally (2026-06-26); it then inlined the user's code as literal Python
source directly into the generated method body. That inlining approach lost
one piece of parity with the desktop/HTML5 runtimes: a bare local the code
assigns without `self.` (e.g. `hp = hp - 10`) is just a real Python local in
an inlined method, discarded when the method returns, instead of persisting
as an instance attribute — GameMaker's implicit-instance-var convenience,
which desktop's `exec()`-based runtime/action_executor.py and HTML5's
Pyodide-based engine.js both already have.

Fixed (DEFERRED_ITEMS_PLAN.md item 9, "locals copied back onto the
instance") by switching Kivy's own codegen to run the user's code through a
REAL `exec()` call at runtime too — Kivy runs on real CPython, so this is
available here, unlike the browser/JS HTML5 target having to route through
Pyodide. The generated method now embeds the user's code as a `repr()`'d
string literal, execs it against a small globals/locals dict (self/instance/
other/game/math/random), and setattrs every leftover local back onto the
instance — byte-for-byte the same mechanism desktop's
execute_execute_code_action and HTML5's PY_BOOTSTRAP run_code use.

Most tests here actually EXECUTE the generated Python (compile + exec against
a stub class), not just pattern-match the generated source text — the
stronger, established pattern for this exporter (see
tests/test_kivy_raycast.py, tests/test_html5_execute_code_game_binding.py)
and the only way to genuinely prove the locals-copied-back mechanism works,
since a substring check can't tell you whether `exec()` actually ran.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402


def _gen(code, event_type="step", base_indent=2):
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


def _run(method_bodies, **methods_and_bodies):
    """Compile+exec a stub class with one generated method per kwarg
    (method_name=generated_body) and return an instance. A no-op
    `_script_game` stands in for the real Kivy proxy — fine for any test
    whose generated code doesn't reference `game`."""
    src = (
        "class _C:\n"
        "    def _script_game(self):\n"
        "        return None\n"
    )
    for name, body in methods_and_bodies.items():
        src += f"    def {name}(self, other=None):\n{body}\n"
    ns = {}
    exec(compile(src, "<gen>", "exec"), ns)
    return ns["_C"]()


def test_simple_code_runs_and_mutates_the_instance():
    out = _gen("self.x += 5")
    inst = _run({}, m=out)
    inst.x = 10
    inst.m()
    assert inst.x == 15


def test_bare_local_persists_as_a_real_instance_attribute():
    """The core deliverable: a bare local (no self.) becomes a persistent
    instance attribute after the call returns, matching desktop/HTML5."""
    out = _gen("hp = 100")
    inst = _run({}, m=out)
    inst.m()
    assert inst.hp == 100


def test_bare_local_is_readable_via_self_in_a_later_separate_call():
    """Persistence across two DIFFERENT generated action units (two
    separate execute_code calls, as a real game would author them across
    frames/events) — not just within one exec() call."""
    set_out = _gen("hp = 100")
    dec_out = _gen("self.hp -= 25")
    inst = _run({}, set_hp=set_out, dec_hp=dec_out)
    inst.set_hp()
    assert inst.hp == 100
    inst.dec_hp()
    assert inst.hp == 75


def test_multiline_nested_code_executes_correctly():
    code = "if self.x > 100:\n    self.x = 0\n    self.hspeed = -self.hspeed"
    out = _gen(code)
    inst = _run({}, m=out)
    inst.x = 150
    inst.hspeed = 4
    inst.m()
    assert inst.x == 0
    assert inst.hspeed == -4
    # Below the threshold: the if-body must NOT run.
    inst2 = _run({}, m=out)
    inst2.x = 10
    inst2.hspeed = 4
    inst2.m()
    assert inst2.x == 10
    assert inst2.hspeed == 4


def test_math_and_random_resolve_and_work():
    out = _gen("self.dist = math.sqrt(9)\nself.roll = random.randint(5, 5)")
    inst = _run({}, m=out)
    inst.m()
    assert inst.dist == 3.0
    assert inst.roll == 5


def test_other_bound_only_in_collision_events():
    out = _gen("self.hp -= other.damage", event_type="collision_with_obj_enemy")
    src = (
        "class _C:\n"
        "    def _script_game(self):\n"
        "        return None\n"
        f"    def m(self, other=None):\n{out}\n"
    )
    ns = {}
    exec(compile(src, "<gen>", "exec"), ns)
    inst = ns["_C"]()
    inst.hp = 100
    other_stub = type("O", (), {"damage": 15})()
    inst.m(other_stub)
    assert inst.hp == 85


def test_other_is_none_outside_a_collision_event():
    out = _gen("self.other_was_none = other is None", event_type="step")
    inst = _run({}, m=out)
    inst.m()
    assert inst.other_was_none is True


def test_math_and_random_are_always_available_regardless_of_use():
    """Design change from the old conditional-import heuristic: math and
    random are now ALWAYS bound in exec_globals, matching desktop's
    execute_execute_code_action (which unconditionally includes both) —
    not gated on a substring guess at the user's code text."""
    out = _gen("self.x = self.x + 1")
    assert '"math": math' in out
    assert '"random": random' in out
    assert _is_valid_python(out)


def test_syntax_error_in_user_code_is_caught_not_a_crash():
    """A syntax error surfaces at runtime via the printed message (matching
    desktop/HTML5's own runtime-exec behavior), not a crashed event."""
    out = _gen("this is not valid python (((")
    inst = _run({}, m=out)
    inst.m()  # must not raise


def test_empty_code_emits_pass():
    out = _gen("   ")
    assert out.strip() == "pass"
    assert _is_valid_python(out)


def test_execute_code_nests_under_a_preceding_guard():
    """A test_expression guards the next action; execute_code must land
    inside that `if` block, not after it."""
    g = ActionCodeGenerator(base_indent=2)
    g.process_action(
        {"action_type": "test_expression",
         "parameters": {"expression": "vspeed > 0"}},
        "collision_obj_monstre",
    )
    g.process_action(
        {"action_type": "execute_code", "parameters": {"code": "self.destroyed = True"}},
        "collision_obj_monstre",
    )
    out = g.get_code()
    lines = [ln for ln in out.split("\n") if ln.strip()]
    if_line = next(ln for ln in lines if ln.lstrip().startswith("if "))
    body_line = next(ln for ln in lines if "try:" in ln)
    assert (len(body_line) - len(body_line.lstrip())) > \
           (len(if_line) - len(if_line.lstrip())), "execute_code not nested under the guard"
    assert _is_valid_python(out)
