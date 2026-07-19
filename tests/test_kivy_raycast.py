"""Kivy export — raycast (Doom-style) movement/action parity (parity unit 4a).

The shared movement + camera-config layer the Kivy raycast renderer (unit 4b)
builds on: facing_angle on the base object, and codegen for set_facing_angle,
set_direction_speed (raycast_1's FPS controls, previously unhandled by the Kivy
generator), and enable_raycast_view (building the scene's raycast_camera config).
The renderer itself lands next.
"""
import importlib
import json
import sys
import tempfile
import types
from contextlib import contextmanager
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


# ---------------------------------------------------------------------------
# Headless run of the generated renderer against stub kivy modules (unit 4b).
# Drives the real _build_raycast_walls / _cast_ray / _render_raycast on a
# controlled 3x3-cell geometry so the DDA + wall-strip pass is exercised, not
# just present in the source.
# ---------------------------------------------------------------------------

class _Group:
    def __init__(self):
        self.children = []

    def add(self, instr):
        self.children.append(instr)

    def clear(self):
        self.children.clear()


class _Canvas(_Group):
    def __init__(self):
        super().__init__()
        self.before = _Group()
        self.after = _Group()


class _Widget:
    def __init__(self, **kwargs):
        self.canvas = _Canvas()


class _Instr:
    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw


class _WindowCls:
    width, height = 320, 200

    def bind(self, **kw):
        pass


@contextmanager
def _stub_kivy_env(game_dir: Path):
    saved_path = list(sys.path)
    saved_modules = dict(sys.modules)

    def mod(name, **attrs):
        m = types.ModuleType(name)
        for k, v in attrs.items():
            setattr(m, k, v)
        sys.modules[name] = m

    try:
        mod("kivy")
        mod("kivy.uix")
        mod("kivy.uix.widget", Widget=_Widget)
        mod("kivy.graphics", Rectangle=_Instr, Color=_Instr, Line=_Instr,
            Ellipse=_Instr, InstructionGroup=_Group,
            PushMatrix=_Instr, PopMatrix=_Instr, Translate=_Instr,
            Fbo=_Instr, ClearColor=_Instr, ClearBuffers=_Instr)
        mod("kivy.core")
        mod("kivy.core.window", Window=_WindowCls())
        mod("kivy.core.image", Image=object)
        mod("kivy.core.text", Label=object)
        mod("main", get_game_app=lambda: None)
        for name in [n for n in sys.modules
                     if n == "utils" or n.startswith(("utils.", "scenes",
                                                       "objects", "asset_paths"))]:
            del sys.modules[name]
        sys.path = [str(game_dir)] + [p for p in sys.path if p != str(REPO_ROOT)]
        yield
    finally:
        sys.path[:] = saved_path
        for name in [n for n in sys.modules if n not in saved_modules]:
            del sys.modules[name]
        sys.modules.update(saved_modules)


class _FakeInst:
    def __init__(self, x, y, w, h, solid, facing=0.0, sprite=None):
        self.x, self.y = float(x), float(y)
        self.image_width, self.image_height = w, h
        self.solid = solid
        self.facing_angle = facing
        self.sprite_name = sprite
        self.visible = True


def _scene_class(game_dir):
    scene_file = next(f for f in (game_dir / "scenes").glob("*.py")
                      if "_render_raycast" in f.read_text(encoding="utf-8"))
    scene_mod = importlib.import_module("scenes." + scene_file.stem)
    return next(v for v in vars(scene_mod).values()
                if isinstance(v, type) and issubclass(v, _Widget)
                and v.__module__ == scene_mod.__name__)


def _blank_scene(cls):
    """A scene with the raycast state initialised but __init__ (and its
    create_instances) bypassed, so the geometry under test is fully ours."""
    scene = cls.__new__(cls)
    scene.canvas = _Canvas()
    scene.instances = []
    scene.instances_to_destroy = []
    scene.raycast_camera = None
    scene._raycast_group = None
    scene._raycast_v_walls = None
    scene._raycast_cell_size = None
    scene._raycast_tex_cache = {}
    scene.room_width = 96
    scene.room_height = 96
    scene.display_width = 320
    scene.display_height = 200
    return scene


def _wall_rects(scene):
    """Rectangles the render added beyond the two flat ceiling/floor fills."""
    kids = scene._raycast_group.children
    rects = [c for c in kids if getattr(c, "kw", None) and "pos" in c.kw]
    # first two rects are the ceiling + floor fills
    return rects[2:]


def test_cast_ray_hits_wall_ahead(exported):
    import math
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        # 32px cells. Camera cell (1,1); a square wall fills cell (2,1) to the
        # east. GM y-down top-lefts -> Kivy y-up (y = room_h - gm_y - h).
        cam = _FakeInst(32, 96 - 32 - 32, 32, 32, solid=False)   # gm (32,32)
        wall = _FakeInst(64, 96 - 32 - 32, 32, 32, solid=True)   # gm (64,32)
        scene.instances = [cam, wall]
        scene._build_raycast_walls(32)
        # A square block registers all 4 edges of its cell.
        assert (2, 1) in scene._raycast_v_walls
        # Ray due east (angle 0) from the cell centre (48,48) hits x=64 at 16px.
        dist, side, hit, tex_u, spr = scene._cast_ray(48, 48, 0.0, 32, 20)
        assert hit is True
        assert side == 0                       # vertical (x-step) face
        assert abs(dist - 16) < 1e-6
        assert 0.0 <= tex_u < 1.0


def test_render_raycast_draws_fills_and_walls(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        cam = _FakeInst(32, 32, 32, 32, solid=False, facing=0.0)   # facing east
        wall = _FakeInst(64, 32, 32, 32, solid=True)
        scene.instances = [cam, wall]
        scene.raycast_camera = {
            "enabled": True, "cell_size": 32, "fov": 66, "render_distance": 20,
            "columns": 80, "camera_instance": cam, "wall_textured": False,
            "wall_color": "#993333", "floor_color": "#464632",
            "ceiling_color": "#87CEEB",
        }
        scene._render_raycast()
        kids = scene._raycast_group.children
        # Ceiling fill sits in the TOP half (Kivy y-up): pos y == half height.
        fills = [c for c in kids if getattr(c, "kw", None) and "pos" in c.kw]
        assert fills[0].kw["pos"] == (0, 100.0)          # ceiling, top half
        assert fills[0].kw["size"] == (320.0, 100.0)
        assert fills[1].kw["pos"] == (0, 0)              # floor, bottom half
        # Facing the wall to the east -> some columns drew wall strips.
        assert len(_wall_rects(scene)) > 0
        # Every wall strip is vertically centred on the horizon (y0 <= 100).
        for r in _wall_rects(scene):
            assert r.kw["pos"][1] <= 100.0


def test_render_raycast_no_walls_when_facing_away(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        # Wall only to the east; face WEST (180) into open cells -> no hits.
        cam = _FakeInst(32, 32, 32, 32, solid=False, facing=180.0)
        wall = _FakeInst(64, 32, 32, 32, solid=True)
        scene.instances = [cam, wall]
        scene.raycast_camera = {
            "enabled": True, "cell_size": 32, "fov": 66, "render_distance": 20,
            "columns": 80, "camera_instance": cam, "wall_textured": False,
        }
        scene._render_raycast()
        assert len(_wall_rects(scene)) == 0              # only the two fills


def test_render_raycast_noop_and_clears_when_disabled(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        cam = _FakeInst(32, 32, 32, 32, solid=False)
        scene.instances = [cam]
        scene.raycast_camera = {"enabled": True, "cell_size": 32,
                                "camera_instance": cam, "wall_textured": False}
        scene._render_raycast()
        assert scene._raycast_group is not None
        # Disabling clears the overlay rather than leaving a stale 3D frame.
        scene.raycast_camera["enabled"] = False
        scene._render_raycast()
        assert scene._raycast_group.children == []
