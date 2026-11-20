"""if_condition answers the same on desktop, the Kivy export and the HTML5 export.

A differential test: the desktop runtime (``ActionExecutor._evaluate_if_condition``) is the reference;
every case is run through the Kivy generator (the generated code is EXECUTED, with the real
``GameObject`` helpers taken from a real export) and, on the dev box, through the real HTML5 engine in
Chromium. The matrix covers all eight condition types.

It found, and this file pins the fixes for: Kivy read ``y`` in Kivy's y-up space while the author's (and
desktop's) is y-down; a malformed or empty expression became a SyntaxError that stopped the WHOLE Kivy
object module importing; a failing expression raised instead of being false; an empty object name in
instance_count was TRUE on Kivy; variable_compare compared against the TEXT of a name or sum (``hp``,
``2 + 3``) on both exports; the HTML5 chance of 0 happened half the time and its legacy "Left Arrow"
key spelling never matched; the HTML5 evaluator quietly accepted ``&&`` / ``||`` / ``!``.
"""
import ast
import json
import sys
import tempfile
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from conftest import skip_without_pyside6  # noqa: E402

ROOM_W, ROOM_H, IMG_H = 640, 480, 32
STATE = dict(x=10, y=20, hspeed=3, vspeed=2, hp=5, score=7, lives=3, health=80, globals={"g": 2}, gems=2)


def C(condition_type, **params):
    return {"condition_type": condition_type, **params}


CASES = [
    # expression
    C("expression", expression="x > 5"), C("expression", expression="x > 50"),
    C("expression", expression="x > 5 and hp < 10"), C("expression", expression="x > 5 and hp > 10"),
    C("expression", expression="not (hp == 5)"), C("expression", expression="hp == 5 or x > 100"),
    C("expression", expression="score >= 7"), C("expression", expression="lives == 3 and health > 50"),
    C("expression", expression="global.g == 2"), C("expression", expression="global.missing == 0"),
    C("expression", expression="abs(x - 30) == 20"), C("expression", expression="max(hp, 9) == 9"),
    C("expression", expression="hspeed + 1 == 4"), C("expression", expression="room_width == 640"),
    C("expression", expression="room_height == 480"), C("expression", expression="self.hp == 5"),
    C("expression", expression="image_index == 0"),
    C("expression", expression="y == 20"), C("expression", expression="y < 100"),
    C("expression", expression="self.y == 20"), C("expression", expression="vspeed == 2"),
    C("expression", expression="vspeed > 0"),
    C("expression", expression="x > 5 && hp < 10"),            # C-style: false on desktop
    C("expression", expression="!(hp == 5)"), C("expression", expression="x != 10"),
    C("expression", expression=""), C("expression", expression="   "),
    C("expression", expression="x >"),                          # malformed
    C("expression", expression="nonsense_name > 1"),            # unknown name
    C("expression", expression="other.x > 1"),                  # no collision partner
    C("expression", expression="other.y > 1"),
    # variable_compare
    C("variable_compare", variable="hp", operator=">", value="3"),
    C("variable_compare", variable="hp", operator=">", value="9"),
    C("variable_compare", variable="hp", operator="==", value="5"),
    C("variable_compare", variable="hp", operator="!=", value="5"),
    C("variable_compare", variable="hp", operator="<=", value="5"),
    C("variable_compare", variable="hp", operator=">=", value="6"),
    C("variable_compare", variable="missing", operator="==", value="0"),
    C("variable_compare", variable="hp", operator="==", value="hp"),
    C("variable_compare", variable="hp", operator="==", value="2 + 3"),
    C("variable_compare", variable="x", operator="==", value="10"),
    C("variable_compare", variable="hspeed", operator="==", value="3"),
    C("variable_compare", variable="", operator="==", value="0"),
    # position_check
    C("position_check", check_type="x position", operator="==", value=10),
    C("position_check", check_type="y position", operator="==", value=20),
    C("position_check", check_type="y position", operator=">", value=100),
    C("position_check", check_type="x position", operator="<", value=11),
    # random_chance (0 and 100 are deterministic)
    C("random_chance", chance=0), C("random_chance", chance=100), C("random_chance", chance="0"),
    # key_pressed (the left key is held)
    C("key_pressed", key="left"), C("key_pressed", key="right"), C("key_pressed", key="Left Arrow"),
    C("key_pressed", key="a"), C("key_pressed", key="space"), C("key_pressed", key=""),
    # instance_count (two obj_gem exist)
    C("instance_count", object_name="obj_gem", operator="==", value=2),
    C("instance_count", object_name="obj_gem", operator=">", value=2),
    C("instance_count", object_name="obj_gem", operator=">=", value="2"),
    C("instance_count", object_name="obj_none", operator="==", value=0),
    C("instance_count", object_name="", operator="==", value=0),
]


def _id(case):
    return json.dumps(case, sort_keys=True)


# ---------------------------------------------------------------- desktop (the reference)

class _Inst:
    pass


def desktop(case):
    from runtime.action_executor import ActionExecutor
    room = types.SimpleNamespace(width=ROOM_W, height=ROOM_H, instances=[])
    runner = types.SimpleNamespace(score=STATE["score"], lives=STATE["lives"], health=STATE["health"],
                                   global_variables=dict(STATE["globals"]), current_room=room, project_data={})
    inst = _Inst()
    inst.x, inst.y, inst.hspeed, inst.vspeed = STATE["x"], STATE["y"], STATE["hspeed"], STATE["vspeed"]
    inst.speed, inst.direction, inst.image_index = 0, 0, 0
    inst.hp = STATE["hp"]
    inst.keys_pressed = {"left"}
    inst.object_name = "obj_probe"
    for _ in range(STATE["gems"]):
        gem = _Inst()
        gem.object_name = "obj_gem"
        room.instances.append(gem)
    params = dict(case)
    ctype = params.pop("condition_type")
    return bool(ActionExecutor(game_runner=runner)._evaluate_if_condition(inst, ctype, params))


@pytest.fixture(scope="module")
def reference():
    return {_id(c): desktop(c) for c in CASES}


# ---------------------------------------------------------------- the Kivy export

@pytest.fixture(scope="module")
def kivy_base_methods():
    from export.Kivy.kivy_exporter import KivyExporter
    from test_kivy_parity_batch import _load_project
    out = Path(tempfile.mkdtemp(prefix="cond_parity_")) / "export"
    assert KivyExporter(_load_project("maze_1"), ROOT / "samples" / "maze_1", out).export()
    src = (out / "game" / "objects" / "base_object.py").read_text(encoding="utf-8")
    cls = next(n for n in ast.parse(src).body if isinstance(n, ast.ClassDef) and n.name == "GameObject")
    lines = ["class _C:"]
    for fn in cls.body:
        if isinstance(fn, ast.FunctionDef) and fn.name in ("_cond", "_gm_y"):
            seg = ast.get_source_segment(src, fn).splitlines()
            lines += ["    " + seg[0]] + seg[1:]
    return "\n".join(lines) + "\n"


def kivy(case, base_methods):
    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator(base_indent=2)
    then = [{"action": "set_variable", "parameters": {"variable": "hit", "value": "1", "scope": "self"}}]
    other = [{"action": "set_variable", "parameters": {"variable": "hit", "value": "2", "scope": "self"}}]
    gen.process_action({"action_type": "if_condition",
                        "parameters": {**case, "then_actions": then, "else_actions": other}}, "step")
    src = base_methods + "    def m(self):\n        self.out = []\n" + gen.get_code() + "\n"
    app = types.SimpleNamespace(globals=dict(STATE["globals"]))
    main = types.ModuleType("main")
    main.get_score, main.get_lives, main.get_health = (lambda: STATE["score"]), (lambda: STATE["lives"]), (lambda: STATE["health"])
    main.get_global = lambda n, d=0: app.globals.get(n, d)
    main.get_game_app = lambda: app
    saved = sys.modules.get("main")
    sys.modules["main"] = main
    try:
        ns = {}
        exec(compile(src, "<generated>", "exec"), ns)          # a SyntaxError here fails the test
        inst = ns["_C"]()

        class Scene:
            width, height, room_height = ROOM_W, ROOM_H, ROOM_H
            keys_pressed = {276: True}

            def count_instances(self, name):
                return STATE["gems"] if name == "obj_gem" else 0
        inst.scene = Scene()
        inst.x = STATE["x"]
        inst.y = ROOM_H - STATE["y"] - IMG_H                   # Kivy: y up from the sprite's bottom
        inst.image_height, inst.grid_size = IMG_H, 32
        inst.hspeed, inst.vspeed = STATE["hspeed"], -STATE["vspeed"]
        inst.hp, inst.image_index, inst.speed, inst.direction = STATE["hp"], 0, 0, 0
        inst.m()
        return {1: True, 2: False}[inst.hit]
    finally:
        if saved is None:
            sys.modules.pop("main", None)
        else:
            sys.modules["main"] = saved


@skip_without_pyside6
@pytest.mark.parametrize("case", CASES, ids=_id)
def test_kivy_answers_like_desktop(case, reference, kivy_base_methods):
    assert kivy(case, kivy_base_methods) is reference[_id(case)]


@skip_without_pyside6
def test_a_malformed_or_empty_expression_never_breaks_the_generated_module(kivy_base_methods):
    from export.Kivy.code_generator import ActionCodeGenerator
    for expression in ("x >", "", "   ", "x > 5 && hp < 10", "(", "import os"):
        for action in ("if_condition", "test_expression"):
            gen = ActionCodeGenerator(base_indent=2)
            params = {"condition_type": "expression", "expression": expression,
                      "then_actions": [{"action": "set_hspeed", "parameters": {"value": 1}}]}
            gen.process_action({"action_type": action, "parameters": params}, "step")
            compile("class _C:\n    def m(self):\n" + gen.get_code() + "\n", "<generated>", "exec")


@skip_without_pyside6
def test_kivy_reads_y_in_the_authors_space_not_kivys():
    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator(base_indent=2)
    gen.process_action({"action_type": "if_condition", "parameters": {
        "condition_type": "expression", "expression": "vspeed > 0 and y - vspeed < other.y + 8",
        "then_actions": [{"action": "destroy_instance", "parameters": {}}]}}, "collision_with_obj_monster")
    code = gen.get_code()
    assert "self._gm_y()" in code and "other._gm_y()" in code
    assert "self.y" not in code.replace("_gm_y", "")


# ---------------------------------------------------------------- the HTML5 export (dev box)

@pytest.fixture(scope="module")
def html5_answers():
    sync_api = pytest.importorskip("playwright.sync_api")
    from export.HTML5.html5_exporter import HTML5Exporter
    out = Path(tempfile.mkdtemp(prefix="cond_parity_h5_")) / "o"
    out.mkdir(parents=True)
    assert HTML5Exporter().export(ROOT / "samples" / "maze_1", out)
    with sync_api.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as exc:
            pytest.skip(f"no Chromium: {exc}")
        page = browser.new_page()
        page.goto(next(out.glob("*.html")).as_uri())
        page.wait_for_function("window.game && window.game.currentRoom && window.game.currentRoom.instances.length > 3",
                               timeout=20000)
        answers = page.evaluate("""([cases, st, roomW, roomH]) => {
            const game = window.game, room = game.currentRoom;
            game.score = st.score; game.lives = st.lives; game.health = st.health;
            game.globalVariables = Object.assign({}, st.globals);
            room.width = roomW; room.height = roomH;
            room.instances = room.instances.filter(i => i.name !== 'obj_gem');
            const probe = new GameObject('obj_probe', st.x, st.y, {}, {});
            probe.hp = st.hp; probe.hspeed = st.hspeed; probe.vspeed = st.vspeed;
            probe._hspeed = st.hspeed; probe._vspeed = st.vspeed;
            room.instances.push(probe);
            for (let i = 0; i < st.gems; i++) room.instances.push(new GameObject('obj_gem', 0, 0, {}, {}));
            game.keys = {ArrowLeft: true};
            return cases.map(c => { try { return !!probe.evaluateCondition({action: 'if_condition', parameters: c}, game); }
                                    catch (e) { return 'ERR ' + e.message.slice(0, 60); } });
        }""", [CASES, STATE, ROOM_W, ROOM_H])
        browser.close()
    return {_id(c): a for c, a in zip(CASES, answers)}


@pytest.mark.parametrize("case", CASES, ids=_id)
def test_html5_answers_like_desktop(case, reference, html5_answers):
    assert html5_answers[_id(case)] is reference[_id(case)]


def test_html5_has_the_c_style_operator_guard_and_the_chance_fix():
    engine = (ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
    assert "function gmBoolExpression(" in engine and engine.count("gmBoolExpression(params.expression") == 2
    assert "const chance = isNaN(parsedChance) ? 50 : parsedChance;" in engine
    assert "parseInt(params.chance) || 50" not in engine
