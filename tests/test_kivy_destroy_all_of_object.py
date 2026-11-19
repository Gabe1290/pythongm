"""Kivy export: destroy_instance with target "object" destroys EVERY instance of
that object (the Junior "Treasure Maze" key opens every door).

It used to fall through to ``self.destroy()``, so on Android/iOS only the key
vanished and the doors stayed (TODO.md, found 2026-11-06). Desktop and HTML5
already did this. The generated one-liner is executed here against a stand-in
scene, and a real export of the lesson project is compiled.
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402


class _Obj:
    def __init__(self, name):
        self.object_name = name
        self.destroyed = False

    def destroy(self):
        self.destroyed = True


class _Scene:
    def __init__(self, instances):
        self.instances = instances


def _run(code, me, scene):
    ns = {"self": me, "other": None}
    me.scene = scene
    exec(code, ns)


def test_target_object_destroys_every_instance_of_that_object_only():
    code = ActionCodeGenerator()._convert_simple_action(
        "destroy_instance", {"target": "object", "target_object": "obj_door"}, "collision_with_obj_hero")
    doors = [_Obj("obj_door") for _ in range(3)]
    key, wall = _Obj("obj_key"), _Obj("obj_wall")
    scene = _Scene([key, wall, *doors])
    _run(code, key, scene)
    assert all(d.destroyed for d in doors)
    assert not key.destroyed and not wall.destroyed        # the caller is not touched


def test_the_list_is_snapshotted_so_destroy_may_change_the_scene():
    code = ActionCodeGenerator()._convert_simple_action(
        "destroy_instance", {"target": "object", "target_object": "obj_door"}, "create")
    doors = [_Obj("obj_door") for _ in range(4)]
    scene = _Scene(list(doors))
    for d in doors:
        d.destroy = (lambda d=d: (scene.instances.remove(d), setattr(d, "destroyed", True)))
    _run(code, _Obj("x"), scene)
    assert all(d.destroyed for d in doors)


def test_target_object_without_a_name_does_nothing_and_self_other_are_unchanged():
    gen = ActionCodeGenerator()
    assert gen._convert_simple_action("destroy_instance", {"target": "object"}, "create") == "pass"
    assert gen._convert_simple_action("destroy_instance", {"target": "self"}, "create") == "self.destroy()"
    assert gen._convert_simple_action(
        "destroy_instance", {"target": "other"}, "collision_with_x") == "other.destroy()"


def test_the_treasure_maze_key_exports_to_compilable_kivy_code():
    import junior_maze2_lesson as jm
    from export.Kivy.kivy_exporter import KivyExporter
    from test_kivy_parity_batch import _load_project
    proj = Path(tempfile.mkdtemp())
    jm.build_finished(proj)
    out = Path(tempfile.mkdtemp()) / "export"
    assert KivyExporter(_load_project(proj), proj, out).export()
    code = "\n".join(f.read_text(encoding="utf-8") for f in (out / "game").rglob("*.py"))
    assert "if getattr(_o, 'object_name', _o.__class__.__name__) == 'obj_door'" in code
    for f in (out / "game").rglob("*.py"):
        compile(f.read_text(encoding="utf-8"), str(f), "exec")
