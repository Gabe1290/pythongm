"""Kivy export: the if_condition mouse_check condition.

It used to become ``if True:`` (the scene tracked no pointer state), so "if the left button is
pressed" and "if the mouse is over me" were always true on Android/iOS. Now the scene remembers
which buttons are held and the last pointer position (room coordinates, y down) and each instance
answers ``_mouse_check`` as the desktop runtime does. A touchscreen is the left button; the pointer
stays where the finger last was. "In region" has no region parameters in the editor, so it is false.

Checked three ways: the generated code, the generated methods executed against stand-ins, and (dev
box, skips without Kivy) a real scene sent real touch calls.
"""
import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402


# ---------------------------------------------------------------- codegen

def _gen(params):
    g = ActionCodeGenerator(base_indent=2)
    g.process_action({"action_type": "if_condition", "parameters": params}, "step")
    return g.get_code()


def test_mouse_check_generates_a_call_to_the_instance_helper():
    code = _gen({"condition_type": "mouse_check", "check": "Left button pressed"})
    assert "self._mouse_check('Left button pressed')" in code and "if True" not in code
    assert "self._mouse_check('Over object')" in _gen({"condition_type": "mouse_check", "check": "Over object"})
    assert "self._mouse_check('')" in _gen({"condition_type": "mouse_check"})


# ---------------------------------------------------------------- the generated methods

@pytest.fixture(scope="module")
def game_dir():
    from export.Kivy.kivy_exporter import KivyExporter
    from test_kivy_parity_batch import _load_project
    out = Path(tempfile.mkdtemp(prefix="kivy_mouse_")) / "export"
    assert KivyExporter(_load_project("maze_1"), ROOT / "samples" / "maze_1", out).export()
    return out / "game"


def _method(path, class_name, method):
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method)
    return ast.get_source_segment(src, fn)


def _scene_class(game_dir):
    for f in sorted((game_dir / "scenes").glob("*.py")):
        for node in ast.parse(f.read_text(encoding="utf-8")).body:
            if isinstance(node, ast.ClassDef) and any(
                    isinstance(n, ast.FunctionDef) and n.name == "_track_mouse" for n in node.body):
                return f, node.name
    raise AssertionError("no scene has _track_mouse")


@pytest.fixture()
def classes(game_dir):
    """A stand-in scene and instance that carry the REAL generated methods."""
    scene_file, scene_name = _scene_class(game_dir)
    track = _method(scene_file, scene_name, "_track_mouse")
    check = _method(game_dir / "objects" / "base_object.py", "GameObject", "_mouse_check")
    ns = {}
    exec("class Scene:\n" + _indent(track) + "\n\nclass Inst:\n" + _indent(check) + "\n", ns)
    return ns["Scene"], ns["Inst"]


def _indent(src):
    first = src.splitlines()[0]
    pad = len(first) - len(first.lstrip())
    return "\n".join(("    " + line[pad:]) if line.strip() else line for line in src.splitlines())


def _world(classes, x=100, y=300, w=32, h=32, has_sprite=True):
    Scene, Inst = classes
    scene = Scene()
    scene.room_height = 480
    inst = Inst()
    inst.scene, inst.x, inst.y = scene, x, y
    inst.image_width, inst.image_height, inst.grid_size, inst.has_sprite = w, h, 32, has_sprite
    return scene, inst


def test_no_pointer_yet_means_nothing_is_pressed_or_over(classes):
    scene, inst = _world(classes)
    assert not any(inst._mouse_check(c) for c in
                   ("Left button pressed", "Middle button pressed", "Right button pressed", "Over object"))


def test_buttons_are_held_between_down_and_up_and_a_touch_is_the_left_button(classes):
    scene, inst = _world(classes)
    scene._track_mouse(0, 0, "left", True)
    assert inst._mouse_check("Left button pressed") and not inst._mouse_check("Right button pressed")
    scene._track_mouse(0, 0, "right", True)
    scene._track_mouse(0, 0, "middle", True)
    assert [inst._mouse_check(c) for c in
            ("Left button pressed", "Middle button pressed", "Right button pressed")] == [True, True, True]
    scene._track_mouse(0, 0, "left", False)
    assert not inst._mouse_check("Left button pressed") and inst._mouse_check("Right button pressed")


def test_a_scroll_tick_or_a_move_does_not_press_anything(classes):
    scene, inst = _world(classes)
    scene._track_mouse(5, 5, "scrollup", True)
    scene._track_mouse(5, 5, None, None)                 # a move: position only
    assert not inst._mouse_check("Left button pressed")
    assert scene._mouse_pos == (5, 5)


def test_over_object_uses_the_authors_y_down_box(classes):
    """Kivy y 300, 32 px tall, in a 480 px room: the author's box is y 148..180, x 100..132."""
    scene, inst = _world(classes)
    for (mx, my), over in {(100, 148): True, (131, 179): True, (116, 164): True,
                           (132, 164): False, (116, 180): False, (99, 164): False, (116, 147): False}.items():
        scene._track_mouse(mx, my, None, None)
        assert inst._mouse_check("Over object") is over, (mx, my)


def test_over_object_is_false_for_a_spriteless_instance_and_in_region_is_never_true(classes):
    scene, inst = _world(classes, has_sprite=False)
    scene._track_mouse(116, 164, None, None)
    assert inst._mouse_check("Over object") is False
    assert inst._mouse_check("In region") is False and inst._mouse_check("") is False
    scene2, inst2 = _world(classes, w=0, h=0)               # unmeasured sprite: the grid size
    scene2._track_mouse(110, 160, None, None)
    assert inst2._mouse_check("Over object") is True


# ---------------------------------------------------------------- real Kivy

def test_a_real_scene_tracks_real_touch_calls(game_dir):
    pytest.importorskip("kivy")
    project = json.loads((ROOT / "samples" / "maze_1" / "project.json").read_text(encoding="utf-8"))
    room = next(iter(project["assets"]["rooms"]))
    text = (game_dir / "scenes" / f"{room}.py").read_text(encoding="utf-8")
    cls = next(line.split("class ")[1].split("(")[0] for line in text.splitlines()
               if line.startswith("class ") and "(Widget)" in line)
    work = Path(tempfile.mkdtemp(prefix="kivy_mouse_run_"))
    result = work / "result.json"
    try:
        proc = subprocess.run([sys.executable, str(ROOT / "tests" / "_real_kivy_mouse.py"), str(game_dir),
                               f"scenes.{room}", cls, str(result)],
                              capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        pytest.skip("real Kivy worker timed out")
    if not result.exists():
        pytest.skip(f"real Kivy cannot run here: {proc.stderr[-300:]}")
    data = json.loads(result.read_text(encoding="utf-8"))
    if data["error"] and any(s in data["error"] for s in ("No module named 'kivy'", "GL", "Window")):
        pytest.skip("real Kivy cannot open a window here: " + data["error"][-200:])
    assert data["error"] is None, data["error"]
    assert data["idle"] == [False, False]
    # a touchscreen touch on the first instance: left held, pointer over it and NOT over the other
    assert data["down_left"] == [True, False, True, False]
    assert data["up_left"] == [False, True]                      # released; the pointer stays put
    # a right click on the other instance: the first is no longer under the pointer
    assert data["down_right_elsewhere"] == [True, False, True, True]
    assert data["scroll"] == [False, False, False]
    assert data["region"] is False
