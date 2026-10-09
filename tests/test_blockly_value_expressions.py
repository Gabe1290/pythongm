"""Engine side of Blockly audit B6a / B15 / B6b / B6c
(docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md).

Blockly's value and arithmetic blocks save expression TEXT (self.hspeed,
score, "(score * (self.x + 2))", ...) -- see the page-side tests in
test_blockly_block_audit_roundtrip.py. That text is only useful if every
engine evaluates it. Before B6a the score/lives/health blocks saved
"game.score", which the desktop engine left as a literal string (and turned
into 0 inside arithmetic), and HTML5's numeric-parameter evaluator rejected
any bare name it didn't substitute itself.
"""

import ast
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parent.parent

# Every spelling getInputValue can save for a value / arithmetic block.
SPELLINGS = {
    "self.x": 10, "self.hspeed": 2, "self.vspeed": -1,
    "self.mouse_x": 120, "self.mouse_y": 80,
    "score": 7, "lives": 3, "health": 50,
    "(score * (self.x + 2))": 84, "(self.x ** 2)": 100, "(3 + 4)": 7,
}


@pytest.fixture
def executor():
    from runtime.action_executor import ActionExecutor
    return ActionExecutor(game_runner=SimpleNamespace(
        score=7, lives=3, health=50, global_variables={}))


def _instance(**extra):
    # Plain objects, not MagicMock: a mock "has" every attribute, which is
    # exactly how game.score's failure stayed hidden.
    return SimpleNamespace(x=10, y=20, hspeed=2, vspeed=-1, object_name="o", **extra)


@pytest.mark.parametrize("expr,expected", SPELLINGS.items())
def test_desktop_evaluates_every_saved_spelling(executor, expr, expected):
    inst = _instance(mouse_x=120, mouse_y=80)
    assert executor._parse_value(expr, inst) == expected


def test_desktop_game_score_was_the_broken_spelling(executor):
    """Pins why B15 changed the spelling (not the engine)."""
    assert executor._parse_value("game.score", _instance()) == "game.score"


def test_new_desktop_instance_has_mouse_position_zero():
    """HTML5 and Kivy start mouse_x/mouse_y at 0; desktop only set them on
    the first click, so "self.mouse_x" stayed a literal string before it."""
    from runtime.instance import GameInstance
    inst = GameInstance("obj", 0, 0, {})
    assert inst.mouse_x == 0 and inst.mouse_y == 0


@pytest.mark.parametrize("expr", list(SPELLINGS))
def test_kivy_emits_compilable_code_for_every_saved_spelling(expr):
    from export.Kivy.code_generator import _num_code
    code = _num_code(expr)
    ast.parse(code, mode="eval")
    assert "game." not in code
    if "score" in expr:
        assert "get_score()" in code


def test_html5_numeric_params_fall_back_to_the_full_expression_evaluator():
    """No JS engine in CI: pin that parseNumParam tries gmExpressionValue
    (whose scope has score/lives/health/self/mouse) before the fallback.
    Verified in a real browser engine when this landed: score -> 7,
    self.mouse_x -> 120, "(score * (self.x + 2))" -> 84."""
    js = (REPO / "export/HTML5/templates/engine.js").read_text(encoding="utf-8")
    body = js[js.index("function parseNumParam("):]
    body = body[:body.index("\n}\n")]
    tail = body[body.rindex("} catch (e)"):]
    assert re.search(r"gmExpressionValue\(s, inst,", tail), "fallback missing"
    assert tail.index("gmExpressionValue") < tail.rindex("return fallback")


# --- B6b: math functions, with "domain error -> 0 for that call" everywhere.
MATH = {
    "sqrt(self.x)": 4, "sqrt(16) + 1": 5, "5 + sqrt(-1)": 5, "ln(0)": 0,
    "log10(100)": 2, "exp(0)": 1, "(10 ** (2))": 100, "(-(self.x))": -16,
    "abs(-3)": 3,
}


@pytest.mark.parametrize("expr,expected", MATH.items())
def test_desktop_math_functions(executor, expr, expected):
    inst = SimpleNamespace(x=16, y=0, hspeed=0, vspeed=0, object_name="o", mouse_x=0, mouse_y=0)
    assert executor._parse_value(expr, inst) == pytest.approx(expected)


def test_desktop_conditions_can_use_math_functions():
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor(game_runner=SimpleNamespace(
        score=0, lives=0, health=0, global_variables={}, current_room=None))
    inst = SimpleNamespace(x=16, y=0, hspeed=0, vspeed=0, object_name="o")
    assert ex._eval_bool_expression(inst, "sqrt(x) > 3") is True
    assert ex._eval_bool_expression(inst, "sqrt(x) > 5") is False


def _kivy_game_object():
    """The math helpers exactly as the exporter writes them into the
    generated GameObject (extracted from its source, then executed)."""
    src = (REPO / "export/Kivy/kivy_exporter.py").read_text(encoding="utf-8")
    start = src.index("    def _gm_math(self, fn, x):")
    end = src.index("    def choose(self, *options):")
    ns = {}
    exec("class GO:\n    x = 16\n" + src[start:end], ns)
    return ns["GO"]()


@pytest.mark.parametrize("expr,expected", MATH.items())
def test_kivy_math_functions(expr, expected):
    from export.Kivy.code_generator import _num_code
    code = _num_code(expr)
    assert eval(code, {}, {"self": _kivy_game_object()}) == pytest.approx(expected)


def test_html5_expression_scope_has_the_math_functions():
    """Verified in a real browser engine when this landed (all nine MATH
    cases matched); CI has no JS engine, so pin the scope entries."""
    js = (REPO / "export/HTML5/templates/engine.js").read_text(encoding="utf-8")
    assert "function gmSafeMath(fn, x)" in js
    for name, fn in (("sqrt", "Math.sqrt"), ("ln", "Math.log"),
                     ("log10", "Math.log10"), ("exp", "Math.exp")):
        assert re.search(rf"\b{name}: \(x\) => gmSafeMath\({re.escape(fn)}, x\)", js), name


# --- B6c: conditions the test_expression block saves
CONDITIONS = {
    "((score > 10) and (not (lives == 0)))": True,
    "((score > 20) or (self.x >= 16))": True,
    "((score > 20) and (lives == 2))": False,
    "True": True, "False": False, "(not True)": False,
}


@pytest.mark.parametrize("expr,expected", CONDITIONS.items())
def test_desktop_evaluates_logic_block_conditions(expr, expected):
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor(game_runner=SimpleNamespace(
        score=12, lives=2, health=50, global_variables={}, current_room=None))
    inst = SimpleNamespace(x=16, y=20, hspeed=2, vspeed=-1, object_name="o")
    assert ex._eval_bool_expression(inst, expr) is expected


@pytest.mark.parametrize("expr,expected", CONDITIONS.items())
def test_kivy_logic_block_conditions_mean_the_same(expr, expected):
    from export.Kivy.code_generator import _resolve_instance_names
    code = _resolve_instance_names(expr)
    main = SimpleNamespace(get_score=lambda: 12, get_lives=lambda: 2, get_health=lambda: 50)
    env = {"__import__": lambda name: main, "self": SimpleNamespace(x=16, y=20)}
    assert bool(eval(code, {"__builtins__": {}}, env)) is expected


def _kivy_lines(*actions):
    from export.Kivy.code_generator import ActionCodeGenerator
    g = ActionCodeGenerator(base_indent=0)
    for action in actions:
        g.process_action(action, "step")
    return g.get_code()


def test_kivy_test_expression_runs_nested_branches():
    """Before B6c, Kivy only opened a guard over the NEXT action and dropped
    then/else -- which is all Blockly's block ever saves."""
    code = _kivy_lines({"action_type": "test_expression", "parameters": {
        "expression": "score > 3",
        "then_actions": [{"action_type": "set_hspeed", "parameters": {"value": "4"}}],
        "else_actions": [{"action_type": "set_hspeed", "parameters": {"value": "-4"}}]}})
    tree = ast.parse(code)
    ifs = [n for n in ast.walk(tree) if isinstance(n, ast.If)]
    assert len(ifs) == 1
    body_src = ast.unparse(ast.Module(body=ifs[0].body, type_ignores=[]))
    else_src = ast.unparse(ast.Module(body=ifs[0].orelse, type_ignores=[]))
    assert "self.hspeed = 4" in body_src
    assert "self.hspeed = -4" in else_src


def test_kivy_flat_test_expression_still_guards_the_next_action():
    code = _kivy_lines(
        {"action_type": "test_expression", "parameters": {"expression": "score > 3"}},
        {"action_type": "set_hspeed", "parameters": {"value": "4"}})
    tree = ast.parse(code)
    ifs = [n for n in ast.walk(tree) if isinstance(n, ast.If)]
    assert len(ifs) == 1
    assert "self.hspeed = 4" in ast.unparse(ast.Module(body=ifs[0].body, type_ignores=[]))


def test_html5_treats_test_expression_as_a_nested_conditional():
    js = (REPO / "export/HTML5/templates/engine.js").read_text(encoding="utf-8")
    block = js[js.index("static isConditionalAction(actionType)"):]
    block = block[:block.index("}")]
    assert "actionType === 'test_expression'" in block
