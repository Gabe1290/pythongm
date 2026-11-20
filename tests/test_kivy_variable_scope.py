"""Kivy export: set_variable / test_variable honour the ``scope`` parameter and "Applies to".

The action offers scope self / other / global, and the GMK importer emits GameMaker's "Applies to"
(``target``: self / other / object + ``target_object``). The Kivy generator read neither, so a variable set
with scope "global" -- or "other" -- was written to THIS instance's attribute: a global score never changed
and the collision partner's variable never did either. set_variable on ``vspeed`` also wrote the author's
value (positive DOWN) into Kivy's (positive UP) field, so ``vspeed = -8`` jumped DOWN. Differential: the
desktop handlers are the reference; the generated code is executed with the real GameObject helpers.
"""
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from conftest import skip_without_pyside6  # noqa: E402
from test_if_condition_parity import kivy_base_methods  # noqa: E402,F401

ROOM_H, IMG_H = 480, 32
SPECS = {"me": dict(x=10, y=20, hp=5, vspeed=1), "other": dict(x=70, y=90, hp=1, vspeed=2),
         "gem1": dict(x=0, y=0, hp=10, vspeed=0), "gem2": dict(x=30, y=40, hp=20, vspeed=3)}
GLOBALS = {"score_total": 7}
ORDER = ("me", "other", "gem1", "gem2")


class _Inst:
    pass


# ---------------------------------------------------------------- desktop (the reference)

def _desktop_world():
    insts = {}
    for key, spec in SPECS.items():
        i = _Inst()
        i.x, i.y, i.hp, i.vspeed, i.hspeed = spec["x"], spec["y"], spec["hp"], spec["vspeed"], 0
        i.object_name = "obj_gem" if key.startswith("gem") else f"obj_{key}"
        insts[key] = i
    runner = types.SimpleNamespace(global_variables=dict(GLOBALS), score=0, lives=3, health=100, project_data={},
                                   current_room=types.SimpleNamespace(width=640, height=ROOM_H,
                                                                      instances=list(insts.values())))
    return runner, insts


def desktop_set(params, collision):
    from runtime.action_executor import ActionExecutor
    runner, insts = _desktop_world()
    ex = ActionExecutor(game_runner=runner)
    if collision:
        ex._collision_other = insts["other"]
    ex.execute_set_variable_action(insts["me"], dict(params))
    out = []
    for key in ORDER:
        i = insts[key]
        out += [i.x, i.y, i.hp, i.vspeed]
    out += [runner.global_variables.get("score_total", -1), runner.global_variables.get("fresh", -1)]
    return out


def desktop_test(params, collision):
    from runtime.action_executor import ActionExecutor
    runner, insts = _desktop_world()
    ex = ActionExecutor(game_runner=runner)
    if collision:
        ex._collision_other = insts["other"]
    return bool(ex.execute_test_variable_action(insts["me"], dict(params)))


# ---------------------------------------------------------------- the generated Kivy code

def _kivy_world(source, code, collision):
    ns = {}
    sig = "self, other" if collision else "self"
    exec(compile(source + f"    def m({sig}):\n" + code + "\n", "<generated>", "exec"), ns)
    cls = ns["_C"]
    scene = types.SimpleNamespace(room_height=ROOM_H, instances=[])
    insts = {}
    for key, spec in SPECS.items():
        i = cls()
        i.scene = scene
        i.image_height, i.grid_size = IMG_H, 32
        i.x, i.y = spec["x"], ROOM_H - spec["y"] - IMG_H
        i.hp, i.vspeed, i.hspeed = spec["hp"], -spec["vspeed"], 0
        i.object_name = "obj_gem" if key.startswith("gem") else f"obj_{key}"
        insts[key] = i
        scene.instances.append(i)
    return insts


def _with_main(globals_dict):
    main = types.ModuleType("main")
    main.get_global = lambda n, d=0: globals_dict.get(n, d)
    main.set_global = lambda n, v: globals_dict.__setitem__(n, v)
    main.get_game_app = lambda: types.SimpleNamespace(globals=globals_dict)
    saved = sys.modules.get("main")
    sys.modules["main"] = main
    return saved


def _restore(saved):
    if saved is None:
        sys.modules.pop("main", None)
    else:
        sys.modules["main"] = saved


def _event(collision):
    return "collision_with_obj_other" if collision else "step"


def kivy_set(params, collision, source):
    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator(base_indent=2)
    gen.process_action({"action_type": "set_variable", "parameters": params}, _event(collision))
    globals_dict = dict(GLOBALS)
    saved = _with_main(globals_dict)
    try:
        insts = _kivy_world(source, gen.get_code(), collision)
        insts["me"].m(insts["other"]) if collision else insts["me"].m()
    finally:
        _restore(saved)
    out = []
    for key in ORDER:
        i = insts[key]
        out += [i.x, ROOM_H - i.y - IMG_H, i.hp, -i.vspeed]            # back to the author's space
    out += [globals_dict.get("score_total", -1), globals_dict.get("fresh", -1)]
    return out


def kivy_test(params, collision, source):
    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator(base_indent=2)
    gen.process_action({"action_type": "test_variable", "parameters": params}, _event(collision))
    gen.process_action({"action_type": "set_variable", "parameters": {"variable": "hit", "value": "1"}},
                       _event(collision))
    globals_dict = dict(GLOBALS)
    saved = _with_main(globals_dict)
    try:
        insts = _kivy_world(source, "        self.hit = 0\n" + gen.get_code(), collision)
        insts["me"].m(insts["other"]) if collision else insts["me"].m()
    finally:
        _restore(saved)
    return bool(insts["me"].hit)


SET_CASES = [
    ({"variable": "fresh", "value": "5", "scope": "global"}, False),
    ({"variable": "score_total", "value": "10", "scope": "global", "relative": True}, False),
    ({"variable": "hp", "value": "9", "scope": "other"}, True),
    ({"variable": "hp", "value": "2", "scope": "other", "relative": True}, True),
    ({"variable": "y", "value": "50", "scope": "other"}, True),
    ({"variable": "y", "value": "-6", "scope": "other", "relative": True}, True),
    ({"variable": "vspeed", "value": "-8", "scope": "other"}, True),
    ({"variable": "hp", "value": "9", "scope": "other"}, False),                  # no collision: dropped
    ({"variable": "hp", "value": "9", "scope": "self"}, False),
    ({"variable": "vspeed", "value": "-8"}, False),                                # the jump
    ({"variable": "vspeed", "value": "2", "relative": True}, False),
    ({"variable": "hp", "value": "3", "target": "other"}, True),
    ({"variable": "hp", "value": "1", "target": "object", "target_object": "obj_gem", "relative": True}, False),
    ({"variable": "y", "value": "100", "target": "object", "target_object": "obj_gem"}, False),
    ({"variable": "vspeed", "value": "-4", "target": "object", "target_object": "obj_gem"}, False),
    ({"variable": "hp", "value": "7", "target": "object", "target_object": "obj_missing"}, False),
    ({"variable": "hp", "value": "4", "target": "self"}, False),
    ({"variable": "hp", "value": "4", "scope": "global", "target": "other"}, True),   # global wins
]


def _id(case):
    params, collision = case
    return ",".join(f"{k}={v}" for k, v in params.items()) + ("|collision" if collision else "")


@skip_without_pyside6
@pytest.mark.parametrize("case", SET_CASES, ids=_id)
def test_set_variable_applies_to_the_same_instances_as_the_desktop(case, kivy_base_methods):
    params, collision = case
    assert kivy_set(params, collision, kivy_base_methods) == pytest.approx(desktop_set(params, collision))


TEST_CASES = [
    ({"variable": "score_total", "value": "7", "scope": "global", "operation": "equal"}, False),
    ({"variable": "score_total", "value": "8", "scope": "global", "operation": "equal"}, False),
    ({"variable": "score_total", "value": "5", "scope": "global", "operation": "greater"}, False),
    ({"variable": "nope", "value": "0", "scope": "global", "operation": "equal"}, False),   # unset global is 0
    ({"variable": "hp", "value": "1", "scope": "other", "operation": "equal"}, True),
    ({"variable": "hp", "value": "5", "scope": "other", "operation": "equal"}, True),
    ({"variable": "hp", "value": "1", "scope": "other", "operation": "equal"}, False),      # no collision: false
    ({"variable": "y", "value": "90", "scope": "other", "operation": "equal"}, True),
    ({"variable": "vspeed", "value": "2", "scope": "other", "operation": "equal"}, True),
    ({"variable": "hp", "value": "1", "target": "other", "operation": "equal"}, True),
    ({"variable": "hp", "value": "10", "target": "object", "target_object": "obj_gem", "operation": "equal"}, False),
    ({"variable": "hp", "value": "20", "target": "object", "target_object": "obj_gem", "operation": "equal"}, False),
    ({"variable": "hp", "value": "0", "target": "object", "target_object": "obj_missing", "operation": "equal"}, False),
    ({"variable": "hp", "value": "5", "scope": "self", "operation": "equal"}, False),
]


@skip_without_pyside6
@pytest.mark.parametrize("case", TEST_CASES, ids=_id)
def test_test_variable_reads_the_same_instance_as_the_desktop(case, kivy_base_methods):
    params, collision = case
    assert kivy_test(params, collision, kivy_base_methods) is desktop_test(params, collision)


@skip_without_pyside6
def test_a_name_prefix_still_names_its_own_scope(kivy_base_methods):
    """`global.x` / `other.x` / `self.x` in the NAME (the action description's own syntax) are explicit."""
    assert kivy_set({"variable": "global.fresh", "value": "3"}, False, kivy_base_methods)[-1] == 3
    other_hp = kivy_set({"variable": "other.hp", "value": "6"}, True, kivy_base_methods)[ORDER.index("other") * 4 + 2]
    assert other_hp == 6
    assert kivy_set({"variable": "self.hp", "value": "8"}, False, kivy_base_methods)[2] == 8
