"""Kivy export — raycast (Doom-style) movement/action parity (parity unit 4a).

The shared movement + camera-config layer the Kivy raycast renderer (unit 4b)
builds on: facing_angle on the base object, and codegen for set_facing_angle,
set_direction_speed (raycast_1's FPS controls, previously unhandled by the Kivy
generator), and enable_raycast_view (building the scene's raycast_camera config).
The renderer itself lands next.
"""
import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402
from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402
from utils.project_file_merge import merge_object_file  # noqa: E402

SAMPLE = REPO_ROOT / "samples" / "raycast_1"


# ---------------------------------------------------------------------------
# Code-generator unit tests
# ---------------------------------------------------------------------------

def test_set_direction_speed_resolves_facing_angle():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "set_direction_speed", {"direction": "facing_angle", "speed": "3"}, "keyboard")
    # bare facing_angle -> self.facing_angle (AST-resolved by _num_code)
    assert "self.direction = (self.facing_angle)" in code
    assert "self.speed = 3" in code


def test_set_direction_speed_facing_angle_expression():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "set_direction_speed", {"direction": "facing_angle+180", "speed": "3"}, "keyboard")
    assert "self.facing_angle + 180" in code


def test_set_facing_angle_absolute_and_relative():
    gen = ActionCodeGenerator()
    abs_code = gen._convert_simple_action("set_facing_angle", {"angle": "90"}, "keyboard")
    assert abs_code == "self.facing_angle = (90) % 360"
    rel_code = gen._convert_simple_action(
        "set_facing_angle", {"angle": "3", "relative": True}, "keyboard")
    assert rel_code == "self.facing_angle = (self.facing_angle + 3) % 360"


def test_enable_raycast_view_builds_scene_camera():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "enable_raycast_view",
        {"fov": "66", "cell_size": "32", "render_distance": "20",
         "wall_texture": "spr_wall_texture", "sky_texture": "spr_sky",
         "floor_texture": "spr_floor"},
        "create")
    assert "self.scene.raycast_camera = {" in code
    assert "'enabled': True" in code
    assert "'fov': 66" in code
    assert "'cell_size': 32" in code
    assert "'wall_texture': 'spr_wall_texture'" in code
    assert "'sky_texture': 'spr_sky'" in code
    # no named camera -> the acting instance is the camera
    assert "camera_instance'] = self" in code


def test_enable_raycast_view_disable():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "enable_raycast_view", {"enable": "false"}, "create")
    assert code == "self.scene.raycast_camera = {'enabled': False}"


# ---------------------------------------------------------------------------
# End-to-end export of the real sample
# ---------------------------------------------------------------------------

def _export_raycast_1():
    data = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        side = SAMPLE / "objects" / f"{name}.json"
        if side.exists():
            merge_object_file(obj, json.loads(side.read_text(encoding="utf-8")))
    for name in list(data["assets"]["rooms"]):
        side = SAMPLE / "rooms" / f"{name}.json"
        if side.exists():
            data["assets"]["rooms"][name] = json.loads(side.read_text(encoding="utf-8"))
    out = Path(tempfile.mkdtemp(prefix="kivy_raycast_")) / "export"
    assert KivyExporter(data, SAMPLE, out).export()
    return out / "game"


@pytest.fixture(scope="module")
def exported():
    return _export_raycast_1()


def test_base_object_has_facing_angle(exported):
    base = (exported / "objects" / "base_object.py").read_text(encoding="utf-8")
    assert "self.facing_angle = 0.0" in base
    compile(base, "base_object.py", "exec")


def test_person_movement_and_camera_generated(exported):
    obj = (exported / "objects" / "obj_person.py").read_text(encoding="utf-8")
    assert "self.direction = (self.facing_angle)" in obj      # forward
    assert "self.facing_angle = (self.facing_angle + " in obj  # turn
    assert "self.scene.raycast_camera = {" in obj             # camera config
    assert "'wall_texture': 'spr_wall_texture'" in obj
    compile(obj, "obj_person.py", "exec")


def test_scene_has_raycast_camera_slot(exported):
    scene = next((exported / "scenes").glob("*.py")).read_text(encoding="utf-8")
    assert "self.raycast_camera = None" in scene
    compile(scene, "scene.py", "exec")
