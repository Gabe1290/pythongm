"""Kivy export: execute_code / execute_script see y (and vspeed) in the author's space.

The author's Python runs against ``self`` / ``other``. On desktop (and HTML5/Pyodide) ``self.y`` is down
from the sprite's TOP and ``self.vspeed`` is positive DOWN; a Kivy instance keeps y up from its bottom and
vspeed positive UP, and the code was handed the raw instance -- so ``self.y = self.y - 4`` moved down,
``self.y = 100`` landed 100 px from the bottom, and a jump written ``self.vspeed = -8`` went DOWN. The code
now gets ``GameObject._gm_view()`` (a ``_GmView``), which converts y and vspeed both ways and passes
everything else through; a bare local copied back onto the instance goes through it too.

Differential: the desktop's ``execute_execute_code_action`` is the reference; the generated Kivy code is
executed with the real GameObject helpers from a real export.
"""
import ast
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from conftest import skip_without_pyside6  # noqa: E402

ROOM_H, IMG_H = 480, 32
START = dict(x=10, y=20, hp=5, vspeed=0)
OTHER = dict(x=70, y=90, hp=1, vspeed=2)

HELPERS = ("_cond", "_gm_y", "_set_gm_y", "_gm_view", "_script_game", "_check_key")


@pytest.fixture(scope="module")
def kivy_source(tmp_path_factory):
    pytest.importorskip("PySide6")
    from export.Kivy.kivy_exporter import KivyExporter
    from test_kivy_parity_batch import _load_project
    out = tmp_path_factory.mktemp("execy") / "export"
    assert KivyExporter(_load_project("maze_1"), ROOT / "samples" / "maze_1", out).export()
    src = (out / "game" / "objects" / "base_object.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    view = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "_GmView")
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "GameObject")
    parts = [ast.get_source_segment(src, view), "", "class _C:"]
    for fn in cls.body:
        if isinstance(fn, ast.FunctionDef) and fn.name in HELPERS:
            seg = ast.get_source_segment(src, fn).splitlines()
            parts += ["    " + seg[0]] + seg[1:]
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------- the references

class _Inst:
    pass


def _desktop_inst(spec):
    inst = _Inst()
    inst.x, inst.y, inst.hp, inst.vspeed = spec["x"], spec["y"], spec["hp"], spec["vspeed"]
    inst.hspeed = 0
    inst.object_name = "obj_probe"
    inst.keys_pressed = set()
    return inst


def desktop(code, collision=False, action="execute_code"):
    from runtime.action_executor import ActionExecutor
    runner = types.SimpleNamespace(global_variables={}, score=0, lives=3, health=100, project_data={"assets": {}},
                                   current_room=types.SimpleNamespace(width=640, height=ROOM_H, instances=[]))
    ex = ActionExecutor(game_runner=runner)
    me, other = _desktop_inst(START), _desktop_inst(OTHER)
    if collision:
        ex._collision_other = other
    ex.execute_execute_code_action(me, {"code": code})
    return (me.x, me.y, me.hp, me.vspeed), (other.x, other.y, other.hp, other.vspeed)


def kivy(code, source, collision=False, action="execute_code"):
    from export.Kivy.code_generator import ActionCodeGenerator
    event = "collision_with_obj_other" if collision else "step"
    gen = ActionCodeGenerator(base_indent=2)
    gen.process_action({"action_type": action, "parameters": {"code": code}}, event)
    sig = "self, other" if collision else "self"
    src = source + f"    def m({sig}):\n" + gen.get_code() + "\n"
    main = types.ModuleType("main")
    main._ScriptGameProxy = type("_ScriptGameProxy", (), {})
    saved = sys.modules.get("main")
    sys.modules["main"] = main
    try:
        ns = {}
        exec(compile(src, "<generated>", "exec"), ns)
        cls = ns["_C"]

        def make(spec):
            inst = cls()
            inst.scene = types.SimpleNamespace(room_height=ROOM_H, keys_pressed={})
            inst.image_height, inst.grid_size = IMG_H, 32
            inst.x, inst.y = spec["x"], ROOM_H - spec["y"] - IMG_H
            inst.hp, inst.vspeed, inst.hspeed = spec["hp"], -spec["vspeed"], 0
            return inst
        me, other = make(START), make(OTHER)
        me.m(other) if collision else me.m()
    finally:
        if saved is None:
            sys.modules.pop("main", None)
        else:
            sys.modules["main"] = saved

    def back(inst):
        return (inst.x, ROOM_H - inst.y - IMG_H, inst.hp, -inst.vspeed)      # to the author's space
    return back(me), back(other)


def _flat(pair):
    return [v for state in pair for v in state]      # (me, other) -> eight numbers


CASES = [
    "self.y = 100",
    "self.y = 0",
    "self.y = self.y - 4",
    "self.y += 8",
    "self.y -= 3",
    "y = 50",                              # a bare local copied back onto the instance
    "y = self.y + 1",
    "self.x = self.y",
    "self.hp = self.y * 2",
    "self.vspeed = -8",                    # the jump a platformer writes
    "self.vspeed = self.vspeed + 1",
    "self.vspeed = -self.vspeed",
    "self.hp = self.vspeed + 10",
    "self.x = self.x + 4",                 # x and everything else are untouched by the conversion
    "self.hp = self.hp - 1",
    "if self.y > 10:\n    self.y = 200\nelse:\n    self.y = 5",
]
COLLISION_CASES = [
    "other.y = self.y + 10",
    "self.y = other.y",
    "other.vspeed = -3",
    "self.vspeed = other.vspeed",
    "other.y += 5",
    "self.x = other.y",
    "self.hp = 1 if self.y < other.y else 2",
]


@skip_without_pyside6
@pytest.mark.parametrize("code", CASES, ids=lambda c: c.replace("\n", ";")[:40])
@pytest.mark.parametrize("action", ["execute_code"])
def test_execute_code_ends_where_the_desktop_does(code, action, kivy_source):
    assert _flat(kivy(code, kivy_source)) == pytest.approx(_flat(desktop(code)))


@skip_without_pyside6
@pytest.mark.parametrize("code", COLLISION_CASES, ids=lambda c: c[:40])
def test_execute_code_in_a_collision_converts_other_too(code, kivy_source):
    assert _flat(kivy(code, kivy_source, collision=True)) == pytest.approx(_flat(desktop(code, collision=True)))


@skip_without_pyside6
def test_the_view_passes_everything_else_through_and_compares_by_the_wrapped_object(kivy_source):
    ns = {}
    exec(compile(kivy_source, "<helpers>", "exec"), ns)
    View, cls = ns["_GmView"], ns["_C"]
    inst = cls()
    inst.scene = types.SimpleNamespace(room_height=ROOM_H)
    inst.image_height, inst.grid_size, inst.y, inst.vspeed = IMG_H, 32, 400, 3
    inst.custom = "kept"
    view = View(inst)
    assert (view.custom, view.y, view.vspeed) == ("kept", ROOM_H - 400 - IMG_H, -3)
    view.custom, view.new_attr = "changed", 7
    assert (inst.custom, inst.new_attr) == ("changed", 7)
    assert view == View(inst) and view == inst and hash(view) == hash(View(inst))
    assert inst._gm_view() == view and inst._gm_view(None) is None
    with pytest.raises(AttributeError):
        view.no_such_attribute


@skip_without_pyside6
def test_a_method_called_through_the_view_gets_real_instances_not_views(kivy_source):
    """`self.touching(other)` runs the REAL method, which reads `other.y` in Kivy's space -- so the views
    in its arguments are unwrapped first."""
    ns = {}
    exec(compile(kivy_source + "    def touching(self, other, extra=None):\n"
                 "        return (other.y, extra.y if extra is not None else None)\n", "<helpers>", "exec"), ns)
    View, cls = ns["_GmView"], ns["_C"]

    def make(y):
        inst = cls()
        inst.scene = types.SimpleNamespace(room_height=ROOM_H)
        inst.image_height, inst.grid_size, inst.y = IMG_H, 32, y
        return inst
    me, other, third = make(400), make(300), make(100)
    assert View(me).touching(View(other), extra=View(third)) == (300, 100)        # raw Kivy y inside
    assert View(me).touching(other) == (300, None)                                # a real instance still works


@skip_without_pyside6
def test_execute_script_is_converted_too(kivy_source):
    """execute_script shares the namespace construction: a script named in the project sees the author's y."""
    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator(base_indent=2, scripts={"scr_hop": {"code": "self.y = self.y - 4"}})
    gen.process_action({"action_type": "execute_script", "parameters": {"script": "scr_hop"}}, "step")
    main = types.ModuleType("main")
    main._ScriptGameProxy = type("_ScriptGameProxy", (), {})
    saved = sys.modules.get("main")
    sys.modules["main"] = main
    try:
        ns = {}
        exec(compile(kivy_source + "    def m(self):\n" + gen.get_code() + "\n", "<generated>", "exec"), ns)
        inst = ns["_C"]()
        inst.scene = types.SimpleNamespace(room_height=ROOM_H, keys_pressed={})
        inst.image_height, inst.grid_size, inst.y = IMG_H, 32, ROOM_H - START["y"] - IMG_H
        inst.m()
        assert ROOM_H - inst.y - IMG_H == START["y"] - 4
    finally:
        if saved is None:
            sys.modules.pop("main", None)
        else:
            sys.modules["main"] = saved
