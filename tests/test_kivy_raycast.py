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
    # scenes/ also holds a package __init__.py; glob("*.py") order is
    # filesystem-dependent (CI/Linux returned __init__.py first, failing this),
    # so pick a real scene module explicitly.
    scene_file = next(p for p in sorted((exported / "scenes").glob("*.py"))
                      if p.name != "__init__.py")
    scene = scene_file.read_text(encoding="utf-8")
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


class _FakeGLTexture:
    """Stub for kivy.graphics.texture.Texture — records blit_buffer calls."""
    def __init__(self, size):
        self.width, self.height = size
        self.blits = []

    @staticmethod
    def create(size=(1, 1), colorfmt='rgba'):
        return _FakeGLTexture(size)

    def blit_buffer(self, buf, colorfmt='rgba', bufferfmt='ubyte'):
        self.blits.append(len(buf))


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
        mod("kivy.graphics.texture", Texture=_FakeGLTexture)
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


class _FakeTex:
    """A stand-in Kivy texture; get_region records the requested slice."""
    def __init__(self, w=16, h=16):
        self.width, self.height = w, h
        self.regions = []

    def get_region(self, x, y, w, h):
        self.regions.append((x, y, w, h))
        return self


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


def _textured_rects(scene):
    return [c for c in scene._raycast_group.children
            if getattr(c, "kw", None) and "texture" in c.kw]


def test_sky_panorama_drawn_over_ceiling(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        sky = _FakeTex(64, 32)
        scene._raycast_tex_cache = {"spr_sky": sky}   # pre-seed the resolver
        cam = _FakeInst(32, 32, 32, 32, solid=False, facing=0.0)
        scene.instances = [cam]
        scene.raycast_camera = {
            "enabled": True, "cell_size": 32, "fov": 66, "render_distance": 20,
            "columns": 80, "camera_instance": cam, "wall_textured": False,
            "sky_texture": "spr_sky",
        }
        scene._render_raycast()
        sky_rects = [c for c in _textured_rects(scene) if c.kw["texture"] is sky]
        assert sky_rects, "sky panorama not drawn"
        # panorama width = w*360/fov, and it lives in the ceiling (top) half.
        expected_pano = int(320 * 360.0 / 66)
        assert sky_rects[0].kw["size"] == (expected_pano, 100.0)
        assert sky_rects[0].kw["pos"][1] == 100.0     # top half (Kivy y-up)


def test_billboard_drawn_and_occluded_by_wall(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        # --- visible billboard: a goal one cell east, no wall between ---
        scene = _blank_scene(cls)
        goal_tex = _FakeTex(16, 16)
        scene._raycast_tex_cache = {"spr_goal": goal_tex}
        cam = _FakeInst(32, 32, 32, 32, solid=False, facing=0.0)   # facing east
        goal = _FakeInst(96, 32, 16, 16, solid=False, sprite="spr_goal")  # gm x=96
        scene.instances = [cam, goal]
        scene.raycast_camera = {
            "enabled": True, "cell_size": 32, "fov": 66, "render_distance": 20,
            "columns": 80, "camera_instance": cam, "wall_textured": False,
        }
        scene._render_raycast()
        billboard_rects = [c for c in _textured_rects(scene)
                           if c.kw["texture"] is goal_tex]
        assert billboard_rects, "billboard sprite not drawn when visible"

        # --- same goal, now behind a solid wall one cell east -> occluded ---
        scene2 = _blank_scene(cls)
        goal_tex2 = _FakeTex(16, 16)
        scene2._raycast_tex_cache = {"spr_goal": goal_tex2}
        cam2 = _FakeInst(32, 32, 32, 32, solid=False, facing=0.0)
        wall = _FakeInst(64, 32, 32, 32, solid=True)               # blocks the view
        goal2 = _FakeInst(96, 32, 16, 16, solid=False, sprite="spr_goal")
        scene2.instances = [cam2, wall, goal2]
        scene2.raycast_camera = dict(scene.raycast_camera, camera_instance=cam2)
        scene2._render_raycast()
        occluded = [c for c in _textured_rects(scene2)
                    if c.kw["texture"] is goal_tex2]
        assert not occluded, "billboard should be fully occluded by the wall"


def test_floor_buffer_size_and_sampling(exported):
    import math
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        scene.display_width, scene.display_height = 480, 480
        tw = th = 32
        # A recognisable RGBA texture: red gradient so the cast output varies.
        pixels = bytearray(tw * th * 4)
        for k in range(tw * th):
            pixels[k * 4] = k % 256
            pixels[k * 4 + 3] = 255
        buf, sw, sh = scene._floor_buffer(bytes(pixels), tw, th, 4,
                                          facing_screen_rad=0.0, fov_rad=math.radians(66),
                                          cam_cx=3.5, cam_cy=3.5)
        # res=4 over a 480-wide, 240-tall floor region -> 120x60 low-res grid.
        assert (sw, sh) == (120, 60)
        assert len(buf) == sw * sh * 4
        assert all(buf[i + 3] == 255 for i in range(0, len(buf), 4))   # opaque
        assert any(buf[i] for i in range(0, len(buf), 4))              # sampled non-zero


def test_render_raycast_casts_floor_texture(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        # Pre-seed the floor sprite's pixels so the caster runs headlessly.
        floor_px = (bytes([90, 90, 90, 255] * (32 * 32)), 32, 32)
        scene._raycast_px_cache = {"spr_floor": floor_px}
        cam = _FakeInst(32, 32, 32, 32, solid=False, facing=0.0)
        scene.instances = [cam]
        scene.raycast_camera = {
            "enabled": True, "cell_size": 32, "fov": 66, "render_distance": 20,
            "columns": 80, "camera_instance": cam, "wall_textured": False,
            "floor_texture": "spr_floor", "floor_cast_res": 4,
        }
        scene._render_raycast()
        # A textured floor Rectangle (the low-res cast) was added, sized to the
        # full display width, with the v-flip tex_coords for the bottom region.
        floor_rects = [c for c in scene._raycast_group.children
                       if getattr(c, "kw", None) and c.kw.get("texture") is not None
                       and c.kw.get("size", (0,))[0] == scene.display_width
                       and c.kw.get("tex_coords") == (0, 1, 1, 1, 1, 0, 0, 0)]
        assert floor_rects, "floor cast rectangle not drawn"
        assert floor_rects[0].kw["pos"] == (0, 0)     # bottom half (Kivy y-up)


# --- viewport_height letterbox (DOOM HUD Unit 3) ---------------------------
# The hard target: Kivy is y-UP, so the reserved DOOM-bar band is at the
# BOTTOM (low y), the inverse of desktop/HTML5. This drives the real
# _render_raycast on controlled geometry and asserts that inversion.

def _all_rects(scene):
    return [c for c in scene._raycast_group.children
            if getattr(c, "kw", None) and "pos" in c.kw]


def test_letterbox_reserves_the_band_at_the_bottom_in_y_up(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)                 # display 320x200
        cam = _FakeInst(32, 32, 32, 32, solid=False, facing=0.0)
        wall = _FakeInst(64, 32, 32, 32, solid=True)
        scene.instances = [cam, wall]
        scene.raycast_camera = {
            "enabled": True, "cell_size": 32, "fov": 66, "render_distance": 20,
            "columns": 80, "camera_instance": cam, "wall_textured": False,
            "wall_color": "#993333", "floor_color": "#464632",
            "ceiling_color": "#87CEEB", "viewport_height": 140,
        }
        scene._render_raycast()
        rects = _all_rects(scene)
        # view_h=140 => view_bottom=60, mid=130.
        # Ceiling fill = top of the view: pos y == mid.
        assert rects[0].kw["pos"] == (0, 130.0), rects[0].kw["pos"]
        assert rects[0].kw["size"] == (320.0, 70.0)
        # Floor fill = bottom of the VIEW (not the window): pos y == view_bottom.
        assert rects[1].kw["pos"] == (0, 60.0), rects[1].kw["pos"]
        assert rects[1].kw["size"] == (320.0, 70.0)
        # Reserved band = the BOTTOM of the window (y-up low y): pos (0,0).
        band = rects[2]
        assert band.kw["pos"] == (0, 0), band.kw["pos"]
        assert band.kw["size"] == (320.0, 60.0), band.kw["size"]
        # ...and it's painted black — the Color instruction just before it.
        kids = scene._raycast_group.children
        band_idx = kids.index(band)
        black = kids[band_idx - 1]
        assert getattr(black, "args", None) == (0, 0, 0, 1), \
            "reserved band is not filled black"


def test_letterbox_walls_never_paint_into_the_reserved_band(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        cam = _FakeInst(32, 32, 32, 32, solid=False, facing=0.0)
        wall = _FakeInst(64, 32, 32, 32, solid=True)
        scene.instances = [cam, wall]
        scene.raycast_camera = {
            "enabled": True, "cell_size": 32, "fov": 66, "render_distance": 20,
            "columns": 80, "camera_instance": cam, "wall_textured": False,
            "viewport_height": 140,
        }
        scene._render_raycast()
        # Wall strips come after the 3 fills (ceiling, floor, band).
        strips = _all_rects(scene)[3:]
        assert strips, "expected wall strips facing the east wall"
        for r in strips:
            y = r.kw["pos"][1]
            assert y >= 60.0 - 1e-6, f"wall strip at y={y} intrudes on the band (<60)"


def test_full_height_is_unchanged_no_band(exported):
    """viewport_height 0 keeps the fills at the window midpoint and adds no
    reserved band — the backward-compat guarantee, Kivy side."""
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        cam = _FakeInst(32, 32, 32, 32, solid=False, facing=0.0)
        wall = _FakeInst(64, 32, 32, 32, solid=True)
        scene.instances = [cam, wall]
        base = {
            "enabled": True, "cell_size": 32, "fov": 66, "render_distance": 20,
            "columns": 80, "camera_instance": cam, "wall_textured": False,
            "floor_color": "#464632", "ceiling_color": "#87CEEB",
        }
        scene.raycast_camera = dict(base, viewport_height=0)
        scene._render_raycast()
        rects = _all_rects(scene)
        assert rects[0].kw["pos"] == (0, 100.0)      # ceiling, true half
        assert rects[1].kw["pos"] == (0, 0)          # floor to window bottom
        # No third fill spanning a reserved band (walls may follow, but the
        # first wall strip is centred on the horizon, not a full-width band at 0).
        assert rects[1].kw["size"] == (320.0, 100.0)
