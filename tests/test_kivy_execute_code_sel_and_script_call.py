"""Kivy execute_code parity with desktop for imported GameMaker code.

Two small gaps (runtime/action_misc.py binds both):
* ``sel`` -- GameMaker's name for the instance -- was not bound, so imported
  ``sel.x += 4`` raised NameError (swallowed, printed) on Android/iOS;
* ``execute_code`` whose whole body is a project script's NAME (GameMaker
  calls scripts without parentheses) now runs that script, as on desktop,
  instead of evaluating a bare name and doing nothing.
The generated Python is executed for real against a stub class.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402

_HEADER = (
    "class _C:\n"
    "    def _gm_view(self, *target):\n"
    "        return target[0] if target else self\n"
    "    def _script_game(self):\n"
    "        return None\n"
    "    def _check_key(self, key):\n"
    "        return False\n"
)


def _gen(action, scripts=None, event_type="step"):
    g = ActionCodeGenerator(base_indent=2, scripts=scripts or {})
    g.process_action(action, event_type)
    return g.get_code()


def _instance(code):
    ns = {}
    exec(compile(_HEADER + "    def m(self, other=None):\n" + code + "\n", "<gen>", "exec"), ns)
    return ns["_C"]()


def _code_action(code):
    return {"action_type": "execute_code", "parameters": {"code": code}}


def test_sel_is_the_instance_in_execute_code():
    inst = _instance(_gen(_code_action("sel.x = sel.x + 4")))
    inst.x = 1
    inst.m()
    assert inst.x == 5


def test_sel_is_the_instance_in_execute_script():
    scripts = {"nudge": {"code": "sel.y = 7"}}
    inst = _instance(_gen({"action_type": "execute_script", "parameters": {"script": "nudge"}}, scripts))
    inst.m()
    assert inst.y == 7


def test_a_bare_script_name_runs_that_script():
    scripts = {"scr_boost": {"code": "self.speed = 9\nbonus = 3"}}
    inst = _instance(_gen(_code_action("  scr_boost  "), scripts))
    inst.m()
    assert inst.speed == 9 and inst.bonus == 3        # self.x and bare locals both land


def test_a_script_call_gets_the_script_environment():
    scripts = {"scr_k": {"code": "self.n = argument_count"}}
    inst = _instance(_gen(_code_action("scr_k"), scripts))
    inst.m()
    assert inst.n == 0


def test_an_identifier_that_is_not_a_script_stays_plain_code():
    inst = _instance(_gen(_code_action("score_total"), {"scr_other": {"code": "pass"}}))
    inst.m()                                           # a bare unknown name: NameError caught, no crash
    assert not hasattr(inst, "speed")


def test_ordinary_code_that_merely_starts_with_a_script_name_is_not_delegated():
    scripts = {"scr_boost": {"code": "self.speed = 99"}}
    inst = _instance(_gen(_code_action("scr_boost = 5"), scripts))
    inst.m()
    assert inst.scr_boost == 5 and not hasattr(inst, "speed")
