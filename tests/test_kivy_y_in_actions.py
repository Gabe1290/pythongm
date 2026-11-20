"""Kivy export: every action that takes or reads a ``y`` means the AUTHOR's y.

The author's y (the editor, the desktop runtime) is down from the sprite's top; a Kivy instance's is up
from its bottom. Only conditions and set_variable converted (2026-11-20), so elsewhere an absolute y
landed from the wrong edge, a relative +y went UP, and a ``y`` read inside any expression was Kivy's:
create_instance, create_random_instance, jump_to_position, destroy_at_position, move_towards_point,
move_towards, check_empty, test_variable on ``y``, and every numeric expression (``set_hspeed y / 10``,
``draw_text`` at ``y + 8`` ...). Differential where the desktop handler can run on a stand-in (the
generated code is EXECUTED, with the real GameObject helpers from a real export), analytic where it
cannot (create_instance needs a whole room).
"""
import math
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from conftest import skip_without_pyside6  # noqa: E402
from test_if_condition_parity import kivy_base_methods  # noqa: E402,F401

ROOM_W, ROOM_H, IMG_H = 640, 480, 32
START = dict(x=10, y=20, hp=5)


class _Inst:
    pass


def _desktop_runner(instances=()):
    room = types.SimpleNamespace(width=ROOM_W, height=ROOM_H, instances=list(instances))
    return types.SimpleNamespace(global_variables={}, score=0, lives=3, health=100, current_room=room,
                                 project_data={})


def _desktop_inst(**kw):
    inst = _Inst()
    inst.x, inst.y, inst.hp = START["x"], START["y"], START["hp"]
    inst.hspeed = inst.vspeed = 0
    inst.object_name = "obj_probe"
    inst.solid = False
    inst.to_destroy = False
    inst.__dict__.update(kw)
    return inst


def _kivy_class(base_methods):
    ns = {}
    exec(compile(base_methods + "    def m(self):\n        pass\n", "<helpers>", "exec"), ns)
    return ns["_C"]


def _kivy_inst(cls, scene, gm_x, gm_y, **kw):
    inst = cls()
    inst.scene = scene
    inst.image_height, inst.grid_size = IMG_H, 32
    inst.x, inst.y = gm_x, ROOM_H - gm_y - IMG_H           # Kivy: y up from the sprite's bottom
    inst.hp, inst.hspeed, inst.vspeed, inst.solid = START["hp"], 0, 0, False
    inst.__dict__.update(kw)
    return inst


def _run_kivy(action, params, base_methods, event_type="step", extra_scene=None, **inst_kw):
    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator(base_indent=2)
    gen.process_action({"action_type": action, "parameters": params}, event_type)
    src = base_methods + "    def m(self):\n" + gen.get_code() + "\n"
    ns = {}
    exec(compile(src, "<generated>", "exec"), ns)
    cls = ns["_C"]
    created = []

    class Scene:
        room_width, room_height = ROOM_W, ROOM_H
        keys_pressed = {}
        instances = []

        def create_instance(self, name, x, y):
            inst = _kivy_inst(cls, self, x, 0)
            inst.y = y
            inst.object_name = name
            created.append(inst)
            return inst

        def destroy_instance(self, inst):
            self.destroyed.append(inst)

    scene = Scene()
    scene.destroyed = []
    scene.instances = []
    for k, v in (extra_scene or {}).items():
        setattr(scene, k, v)
    me = _kivy_inst(cls, scene, START["x"], START["y"], **inst_kw)
    scene.instances.append(me)
    me.m()
    return me, scene, created


def _author_y(inst):
    return ROOM_H - inst.y - IMG_H


# ---------------------------------------------------------------- jump_to_position

JUMPS = [
    {"x": "100", "y": "200"}, {"x": "0", "y": "0"}, {"x": "x + 5", "y": "y - 4"},
    {"x": "hp", "y": "y + 32"}, {"x": "50", "y": "8", "relative": True},
    {"x": "-3", "y": "-9", "relative": True}, {"x": "0", "y": "y", "relative": True},
]


@skip_without_pyside6
@pytest.mark.parametrize("params", JUMPS, ids=lambda p: f"{p['x']},{p['y']}{'+' if p.get('relative') else ''}")
def test_jump_to_position_lands_where_the_desktop_does(params, kivy_base_methods):
    from runtime.action_executor import ActionExecutor
    ref = _desktop_inst()
    ActionExecutor(game_runner=_desktop_runner([ref])).execute_jump_to_position_action(ref, dict(params))
    me, _, _ = _run_kivy("jump_to_position", params, kivy_base_methods)
    assert (me.x, _author_y(me)) == pytest.approx((ref.x, ref.y))


# ---------------------------------------------------------------- move_towards_point / move_towards

@skip_without_pyside6
@pytest.mark.parametrize("target", [(100, 200), (10, 20), (0, 0), (300, 5), ("x + 100", "y + 50")])
def test_move_towards_point_heads_to_the_same_place(target, kivy_base_methods):
    from runtime.action_executor import ActionExecutor
    params = {"x": str(target[0]), "y": str(target[1]), "speed": "4"}
    ref = _desktop_inst()
    ActionExecutor(game_runner=_desktop_runner([ref])).execute_move_towards_point_action(ref, dict(params))
    for action in ("move_towards_point", "move_towards"):
        me, _, _ = _run_kivy(action, params, kivy_base_methods)
        # Kivy's vspeed is positive UP; the desktop's is positive DOWN
        assert (me.hspeed, -me.vspeed) == pytest.approx((ref.hspeed, ref.vspeed), abs=1e-6), action


# ---------------------------------------------------------------- create_instance and friends

@skip_without_pyside6
@pytest.mark.parametrize("params,expected", [
    ({"object": "obj_gem", "x": "100", "y": "200"}, (100, 200)),
    ({"object": "obj_gem", "x": "x + 5", "y": "y + 7"}, (15, 27)),
    ({"object": "obj_gem", "x": "32", "y": "16", "relative": True}, (42, 36)),
    ({"object": "obj_gem", "x": "0", "y": "-20", "relative": True}, (10, 0)),
])
def test_create_instance_appears_at_the_authors_position(params, expected, kivy_base_methods):
    _, _, created = _run_kivy("create_instance", params, kivy_base_methods)
    assert len(created) == 1 and created[0].object_name == "obj_gem"
    assert (created[0].x, _author_y(created[0])) == pytest.approx(expected)
    # ... and that is where jump_to_start returns it
    assert (created[0].xstart, created[0].ystart) == (created[0].x, created[0].y)


@skip_without_pyside6
def test_create_random_instance_uses_the_same_placement(kivy_base_methods):
    _, _, created = _run_kivy("create_random_instance", {"object1": "obj_a", "object2": "obj_b", "x": "64", "y": "96"},
                              kivy_base_methods)
    assert created[0].object_name in ("obj_a", "obj_b")
    assert (created[0].x, _author_y(created[0])) == pytest.approx((64, 96))


@skip_without_pyside6
def test_a_missing_scene_creates_nothing_and_does_not_raise(kivy_base_methods):
    cls = _kivy_class(kivy_base_methods)
    inst = _kivy_inst(cls, None, 0, 0)
    assert inst._create_gm("obj_gem", 1, 2) is None


# ---------------------------------------------------------------- destroy_at_position

@skip_without_pyside6
@pytest.mark.parametrize("params", [
    {"x": "100", "y": "200", "radius": "40"},
    {"x": "100", "y": "200", "radius": "0"},
    {"x": "0", "y": "40", "radius": "20", "relative": True},
    {"x": "x", "y": "y", "radius": "100"},
])
def test_destroy_at_position_hits_the_same_instances(params, kivy_base_methods):
    from runtime.action_executor import ActionExecutor
    spots = [(100, 200), (110, 215), (100, 240), (50, 60), (10, 60), (10, 20), (400, 400), (100, 190)]
    caller = _desktop_inst()
    others = []
    for i, (gx, gy) in enumerate(spots):
        o = _desktop_inst(x=gx, y=gy, object_name=f"obj_{i}")
        others.append(o)
    ActionExecutor(game_runner=_desktop_runner([caller] + others)).execute_destroy_at_position_action(
        caller, {"object": "all", **params})
    expected = {i for i, o in enumerate(others) if o.to_destroy}

    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator(base_indent=2)
    gen.process_action({"action_type": "destroy_at_position", "parameters": {"object": "all", **params}}, "step")
    ns = {}
    exec(compile(kivy_base_methods + "    def m(self):\n" + gen.get_code() + "\n", "<generated>", "exec"), ns)
    cls = ns["_C"]

    class Scene:
        room_height = ROOM_H
        instances = []
        destroyed = []

        def destroy_instance(self, inst):
            self.destroyed.append(inst)
    scene = Scene()
    scene.instances, scene.destroyed = [], []
    me = _kivy_inst(cls, scene, START["x"], START["y"])
    scene.instances.append(me)
    kivy_others = []
    for i, (gx, gy) in enumerate(spots):
        o = _kivy_inst(cls, scene, gx, gy, object_name=f"obj_{i}")
        kivy_others.append(o)
        scene.instances.append(o)
    me.m()
    assert {i for i, o in enumerate(kivy_others) if o in scene.destroyed} == expected


# ---------------------------------------------------------------- check_empty and reads of y

@skip_without_pyside6
def test_check_empty_converts_an_absolute_y_but_not_a_relative_offset(kivy_base_methods):
    seen = []

    def probe(x, y, obj=None):
        seen.append((x, y))
        return False
    me, _, _ = _run_kivy("check_empty", {"x": "100", "y": "200"}, kivy_base_methods,
                         check_collision_at=probe)
    assert seen == [(100, ROOM_H - 200 - IMG_H)]
    seen.clear()
    _run_kivy("check_empty", {"x": "5", "y": "8", "relative": True}, kivy_base_methods, check_collision_at=probe)
    assert seen == [(START["x"] + 5, ROOM_H - START["y"] - IMG_H - 8)]
    seen.clear()
    _run_kivy("check_empty", {"x": "5"}, kivy_base_methods, check_collision_at=probe)     # no y: where I am
    assert seen == [(5, ROOM_H - START["y"] - IMG_H)]


@skip_without_pyside6
def test_a_y_read_in_a_numeric_expression_is_the_authors(kivy_base_methods):
    me, _, _ = _run_kivy("set_hspeed", {"value": "y / 10"}, kivy_base_methods)
    assert me.hspeed == pytest.approx(START["y"] / 10)                    # not the Kivy y of 428
    me, _, _ = _run_kivy("set_variable", {"variable": "hp", "value": "y + 1"}, kivy_base_methods)
    assert me.hp == START["y"] + 1


@skip_without_pyside6
def test_test_variable_on_y_reads_the_authors_y(kivy_base_methods):
    from export.Kivy.code_generator import ActionCodeGenerator
    for op, expect in (("equal", True), ("greater", False), ("less_equal", True)):
        gen = ActionCodeGenerator(base_indent=2)
        gen.process_action({"action_type": "test_variable",
                            "parameters": {"variable": "y", "value": START["y"], "operation": op}}, "step")
        gen.process_action({"action_type": "set_variable",
                            "parameters": {"variable": "hit", "value": "1"}}, "step")
        ns = {}
        exec(compile(kivy_base_methods + "    def m(self):\n        self.hit = 0\n" + gen.get_code() + "\n",
                     "<generated>", "exec"), ns)
        me = _kivy_inst(ns["_C"], types.SimpleNamespace(room_height=ROOM_H), START["x"], START["y"])
        me.m()
        assert bool(me.hit) is expect, op


@skip_without_pyside6
def test_draw_text_at_a_y_expression_is_in_the_authors_space(kivy_base_methods):
    """The draw queue is in room coordinates (y down, the author's), so a y read inside its position
    expression must be the author's too."""
    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator(base_indent=2)
    gen.process_action({"action_type": "draw_text", "parameters": {"x": "x", "y": "y + 8", "text": "hi"}}, "draw")
    code = gen.get_code()
    assert "self._gm_y() + 8" in code and "self.y + 8" not in code
