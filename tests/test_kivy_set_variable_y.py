"""Kivy export: set_variable on ``y`` is in the AUTHOR's space, like the desktop's.

The author's y is down from the sprite's top (the editor, the desktop runtime); a Kivy instance's is
up from its bottom. set_variable wrote the author's arithmetic straight into the Kivy value, so
``y = y - 4`` -- the ``reseau`` avatar's "up" key -- moved the avatar DOWN on Android/iOS, and an
absolute ``y = 100`` landed 100 px from the bottom. A read of ``y`` inside any set_variable value is
converted too, and a write converts back. Differential: the desktop's execute_set_variable_action is
the reference; the Kivy generator's code is executed with the real helpers from a real export.
"""
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from conftest import skip_without_pyside6  # noqa: E402
from test_if_condition_parity import kivy_base_methods  # noqa: E402,F401  (the real helpers, via a real export)

ROOM_H, IMG_H = 480, 32
START = dict(x=10, y=20, hp=5)

CASES = [
    {"variable": "y", "value": "100"},
    {"variable": "y", "value": "0"},
    {"variable": "y", "value": "y - 4"},
    {"variable": "y", "value": "y + 32"},
    {"variable": "y", "value": "hp * 2"},
    {"variable": "y", "value": "x"},
    {"variable": "y", "value": "8", "relative": True},
    {"variable": "y", "value": "-3", "relative": True},
    {"variable": "y", "value": "y", "relative": True},
    {"variable": "x", "value": "y"},            # x = y reads the author's y
    {"variable": "hp", "value": "y + 1"},        # so does any other variable
    {"variable": "x", "value": "x + 4"},         # x itself is unchanged
    {"variable": "x", "value": "6", "relative": True},
    {"variable": "hp", "value": "hp - 1"},
]


class _Inst:
    pass


def desktop(case):
    from runtime.action_executor import ActionExecutor
    runner = types.SimpleNamespace(global_variables={}, score=0, lives=3, health=100,
                                   current_room=types.SimpleNamespace(width=640, height=ROOM_H, instances=[]),
                                   project_data={})
    inst = _Inst()
    inst.x, inst.y, inst.hp = START["x"], START["y"], START["hp"]
    inst.hspeed = inst.vspeed = 0
    inst.object_name = "obj_probe"
    ex = ActionExecutor(game_runner=runner)
    ex.execute_set_variable_action(inst, {"scope": "self", **case})
    return inst.x, inst.y, inst.hp


def kivy(case, base_methods):
    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator(base_indent=2)
    gen.process_action({"action_type": "set_variable", "parameters": {"scope": "self", **case}}, "step")
    src = base_methods + "    def m(self):\n" + gen.get_code() + "\n"
    ns = {}
    exec(compile(src, "<generated>", "exec"), ns)
    inst = ns["_C"]()
    inst.scene = types.SimpleNamespace(room_height=ROOM_H)
    inst.image_height, inst.grid_size = IMG_H, 32
    inst.x, inst.y, inst.hp = START["x"], ROOM_H - START["y"] - IMG_H, START["hp"]
    inst.hspeed = inst.vspeed = 0
    inst.m()
    return inst.x, ROOM_H - inst.y - IMG_H, inst.hp          # back to the author's y for comparison


@skip_without_pyside6
def test_a_self_prefixed_name_writes_the_same_y_on_kivy(kivy_base_methods):
    """(Not in the differential: desktop's set_variable does NOT strip a `self.` prefix -- it would set an
    attribute literally named "self.y" -- while the action's own description offers it. Kivy strips it,
    which is what the description promises, so `self.y = 50` lands at the author's y 50 here.)"""
    assert kivy({"variable": "self.y", "value": "50"}, kivy_base_methods)[1] == 50


@skip_without_pyside6
@pytest.mark.parametrize("case", CASES, ids=lambda c: f"{c['variable']}{'+' if c.get('relative') else '='}{c['value']}")
def test_set_variable_ends_where_the_desktop_does(case, kivy_base_methods):
    assert kivy(case, kivy_base_methods) == pytest.approx(desktop(case))


@skip_without_pyside6
def test_set_variable_on_other_y_in_a_collision_converts_too(kivy_base_methods):
    from export.Kivy.code_generator import ActionCodeGenerator
    for case, expect in (({"variable": "other.y", "value": "100"}, 100),
                         ({"variable": "other.y", "value": "10", "relative": True}, 30)):
        gen = ActionCodeGenerator(base_indent=2)
        gen.process_action({"action_type": "set_variable", "parameters": case}, "collision_with_obj_wall")
        src = kivy_base_methods + "    def m(self, other):\n" + gen.get_code() + "\n"
        ns = {}
        exec(compile(src, "<generated>", "exec"), ns)
        me, other = ns["_C"](), ns["_C"]()
        for inst in (me, other):
            inst.scene = types.SimpleNamespace(room_height=ROOM_H)
            inst.image_height, inst.grid_size = IMG_H, 32
        other.y = ROOM_H - 20 - IMG_H                        # the author's y = 20
        me.m(other)
        assert ROOM_H - other.y - IMG_H == expect


@skip_without_pyside6
def test_a_spriteless_instance_uses_the_grid_size_and_no_scene_is_safe(kivy_base_methods):
    ns = {}
    exec(compile(kivy_base_methods, "<helpers>", "exec"), ns)
    inst = ns["_C"]()
    inst.image_height, inst.grid_size = 0, 32
    inst.scene = types.SimpleNamespace(room_height=ROOM_H)
    inst._set_gm_y(48)
    assert inst.y == ROOM_H - 48 - 32 and inst._gm_y() == 48
    inst.scene = None
    inst._set_gm_y(7)
    assert inst.y == 7 and inst._gm_y() == 7


@skip_without_pyside6
def test_the_reseau_avatar_moves_the_right_way_on_screen(tmp_path):
    """The generated step event, executed: UP is a smaller author's y (a LARGER Kivy y)."""
    import json
    from export.Kivy.kivy_exporter import KivyExporter
    import events.plugin_loader as loader
    from export.Kivy import code_generator
    original = loader.list_available_extensions
    loader.list_available_extensions = lambda *a, **k: [dict(i, enabled=True) for i in original(*a, **k)]
    code_generator._EXTENSION_CODEGEN = None
    try:
        src = ROOT / "samples" / "reseau_1"
        out = tmp_path / "export"
        assert KivyExporter(json.loads((src / "project.json").read_text(encoding="utf-8")), src, out).export()
    finally:
        loader.list_available_extensions = original
        code_generator._EXTENSION_CODEGEN = None
    text = (out / "game" / "objects" / "obj_person.py").read_text(encoding="utf-8")
    assert "self._set_gm_y((self._gm_y() - 4))" in text          # up
    assert "self._set_gm_y((self._gm_y() + 4))" in text          # down
    assert "self.y = (self.y - 4)" not in text
