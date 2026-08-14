"""Kivy export -- Block World voxel view port (Phase 6 Unit 9 of
docs/VOXEL_WORLD_PLAN.md).

Mirrors tests/test_kivy_raycast.py's structure: codegen unit tests, a real
export of the sample (compiled, not just string-matched), and a stub-kivy
execution harness that drives the real _bw_march_ray / _render_block_world /
_bw_move_and_collide / _bw_place_block / _bw_break_block methods on
controlled geometry -- no Kivy installation or GL context needed.
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

SAMPLE = REPO_ROOT / "samples" / "block_world_1"


# ---------------------------------------------------------------------------
# Code-generator unit tests
# ---------------------------------------------------------------------------

def test_enable_block_world_view_builds_scene_camera():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "enable_block_world_view",
        {"camera_object": "obj_person", "z_layer": "1", "fov": "66",
         "cell_size": "32", "render_distance": "16"},
        "create")
    assert "self.scene.block_world_camera = {" in code
    assert "'enabled': True" in code
    assert "'camera_object': 'obj_person'" in code
    assert "'z_layer': 1" in code
    assert "'cell_size': 32" in code


def test_enable_block_world_view_disable():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "enable_block_world_view", {"enable": "false"}, "create")
    assert code == "self.scene.block_world_camera = {'enabled': False}"


def test_move_and_collide_codegen():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "move_and_collide", {"dx": "4", "dy": "0"}, "keyboard")
    assert code == "self.scene._bw_move_and_collide(self, 4, 0, True)"


def test_place_block_codegen_falls_back_to_getattr():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "place_block", {"block": "hotbar_block", "reach": "5"}, "keyboard_press")
    assert code == ("self.scene._bw_place_block(self, "
                    "getattr(self, 'hotbar_block', 'hotbar_block'), 5)")


def test_select_hotbar_slot_codegen():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "select_hotbar_slot", {"index": "1", "relative": True}, "keyboard_press")
    assert code == "self.scene._bw_select_hotbar_slot(self, 1, True)"


def test_load_block_world_codegen_without_extension_data_is_a_noop_comment():
    gen = ActionCodeGenerator()   # no extension_data supplied
    code = gen._convert_simple_action(
        "load_block_world", {"data_file": "blocks/room0.json"}, "game_start")
    assert code.startswith("pass  #")


def test_load_block_world_codegen_bakes_in_the_data():
    gen = ActionCodeGenerator(extension_data={
        "block_world_files": {"blocks/x.json": [{"x": 1, "y": 2, "z": 3, "type": "stone"}]},
    })
    code = gen._convert_simple_action(
        "load_block_world", {"data_file": "blocks/x.json"}, "game_start")
    assert code == "self.scene._bw_load_block_world([{'x': 1, 'y': 2, 'z': 3, 'type': 'stone'}])"


# ---------------------------------------------------------------------------
# End-to-end export of the real sample
# ---------------------------------------------------------------------------

def _export_block_world_1():
    data = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        side = SAMPLE / "objects" / f"{name}.json"
        if side.exists():
            merge_object_file(obj, json.loads(side.read_text(encoding="utf-8")))
    for name in list(data["assets"]["rooms"]):
        side = SAMPLE / "rooms" / f"{name}.json"
        if side.exists():
            data["assets"]["rooms"][name] = json.loads(side.read_text(encoding="utf-8"))
    out = Path(tempfile.mkdtemp(prefix="kivy_block_world_")) / "export"
    assert KivyExporter(data, SAMPLE, out).export()
    return out / "game"


@pytest.fixture(scope="module")
def exported():
    return _export_block_world_1()


def test_obj_person_generated_and_compiles(exported):
    obj = (exported / "objects" / "obj_person.py").read_text(encoding="utf-8")
    assert "self.scene.block_world_camera = {" in obj
    assert "self.scene._bw_load_block_world([" in obj
    assert "self.scene._bw_move_and_collide(self, 0, -4, True)" in obj
    assert "self.scene._bw_break_block(self, 5)" in obj
    assert "self.scene._bw_place_block(self, getattr(self, 'hotbar_block'" in obj
    compile(obj, "obj_person.py", "exec")


def test_scene_has_render_block_world(exported):
    scene_file = next(f for f in (exported / "scenes").glob("*.py")
                      if "_render_block_world" in f.read_text(encoding="utf-8"))
    scene = scene_file.read_text(encoding="utf-8")
    assert "def _render_extension_overlay(self):" in scene
    assert "block_world_camera" in scene
    compile(scene, "scene.py", "exec")


def test_loaded_world_data_matches_the_generator_output(exported):
    """The 370-block room0.json content the generator produces must reach
    the generated code byte-for-byte (as Python literals)."""
    obj = (exported / "objects" / "obj_person.py").read_text(encoding="utf-8")
    with open(SAMPLE / "blocks" / "room0.json", encoding="utf-8") as f:
        expected = json.load(f)
    assert repr(expected) in obj or str(expected) in obj
    # gold_block goal marker specifically.
    assert "'x': 10, 'y': 2, 'z': 4, 'type': 'gold_block'" in obj


# ---------------------------------------------------------------------------
# Stub-kivy execution harness -- drives the real scene methods on controlled
# geometry, mirroring test_kivy_raycast.py's own _stub_kivy_env pattern.
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
    width, height = 640, 480

    def bind(self, **kw):
        pass


class _StubScriptGameProxy:
    score = 0
    lives = 3
    health = 100


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
        mod("kivy.graphics.texture", Texture=object)
        mod("kivy.core")
        mod("kivy.core.window", Window=_WindowCls())
        mod("kivy.core.image", Image=object)
        mod("kivy.core.text", Label=object)
        mod("main", get_game_app=lambda: None, _ScriptGameProxy=_StubScriptGameProxy)
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
    def __init__(self, x, y, w, h, solid=False, facing=0.0, sprite=None):
        self.x, self.y = float(x), float(y)
        self.image_width, self.image_height = w, h
        self.solid = solid
        self.facing_angle = facing
        self.sprite_name = sprite
        self.visible = True


class _FakeTex:
    """A stand-in Kivy texture (Tier 4a) -- get_region records the
    requested slice and returns self, mirroring test_kivy_raycast.py's own
    _FakeTex."""
    def __init__(self, w=128, h=128):
        self.width, self.height = w, h
        self.regions = []

    def get_region(self, x, y, w, h):
        self.regions.append((x, y, w, h))
        return self


def _scene_class(game_dir):
    scene_file = next(f for f in (game_dir / "scenes").glob("*.py")
                      if "_render_block_world" in f.read_text(encoding="utf-8"))
    scene_mod = importlib.import_module("scenes." + scene_file.stem)
    return next(v for v in vars(scene_mod).values()
                if isinstance(v, type) and issubclass(v, _Widget)
                and v.__module__ == scene_mod.__name__)


def _blank_scene(cls, room_w=448, room_h=448, disp_w=640, disp_h=480):
    """A scene with block-world state initialised but __init__ (and its
    create_instances) bypassed, so the geometry under test is fully ours."""
    scene = cls.__new__(cls)
    scene.canvas = _Canvas()
    scene.instances = []
    scene.instances_to_destroy = []
    scene.block_world_camera = None
    scene._bw_group = None
    scene._bw_blocks = {}
    scene._bw_columns = None
    scene._bw_tex_cache = {}
    scene.room_width = room_w
    scene.room_height = room_h
    scene.display_width = disp_w
    scene.display_height = disp_h
    return scene


def _default_cfg(**overrides):
    cfg = {
        "enabled": True, "camera_object": "", "z_layer": 0, "fov": 66.0,
        "render_distance": 16, "cell_size": 32, "columns": 64,
        "wall_color": "#8a8a8a", "floor_color": "#3a2f1c",
        "ceiling_color": "#87CEEB", "wall_textured": True,
        "pitch": 0.0, "eye_height": 1.5,
    }
    cfg.update(overrides)
    return cfg


def test_march_ray_hits_a_placed_block(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        scene._bw_blocks = {(2, 1, 0): "stone"}
        # From cell (1,1) centre (48,48), ray due east hits the block at
        # x=64 after 16px (cell (2,1) starts at x=64).
        hits = list(scene._bw_march_ray(48, 48, 0.0, 32, 10))
        hit = next(h for h in hits if (h[0], h[1]) == (2, 1))
        assert abs(hit[2] - 16) < 1e-6   # entry distance
        assert hit[4] == 0               # side 0 = vertical (x-step) face


def test_render_block_world_draws_wall_strips(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        scene._bw_blocks = {(2, 1, 0): "stone"}
        cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
        scene.instances = [cam]
        scene.block_world_camera = _default_cfg(camera_object="", eye_height=0.5)
        scene.block_world_camera["camera_instance"] = cam
        scene._render_block_world()
        assert scene._bw_group is not None
        rects = [c for c in scene._bw_group.children if getattr(c, "kw", None)
                and "pos" in c.kw]
        # 2 flat fills (ceiling/floor) + at least one wall strip.
        assert len(rects) > 2


def test_render_block_world_noop_and_clears_when_disabled(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        scene.block_world_camera = _default_cfg()
        scene.instances = [_FakeInst(32, 32, 32, 32)]
        scene.block_world_camera["camera_instance"] = scene.instances[0]
        scene._render_block_world()
        assert len(scene._bw_group.children) > 0
        scene.block_world_camera["enabled"] = False
        scene._render_block_world()
        assert len(scene._bw_group.children) == 0


def test_move_and_collide_y_axis_is_flipped_correctly(exported):
    """The empirical proof this whole port's y-convention rests on: dy is a
    GM y-DOWN pixel delta (matching desktop's instance.y += dy exactly), so
    moving with dy > 0 (down in GM) must DECREASE Kivy's y (down in Kivy's
    y-up frame too), while dx behaves identically in both frames."""
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        scene.block_world_camera = _default_cfg(camera_object="obj_person")
        mover = _FakeInst(100, 100, 32, 32)
        scene.instances = [mover]

        before_gm = scene._bw_gm_xy(mover)
        scene._bw_move_and_collide(mover, dx=10, dy=20, collide=False)
        assert mover.x == 110                       # dx applied directly
        assert mover.y == 80                         # dy=20 (GM down) -> Kivy y -= 20
        after_gm = scene._bw_gm_xy(mover)
        # In GM y-down space, moving dy=20 (down) must INCREASE gm_y.
        assert abs((after_gm[1] - before_gm[1]) - 20) < 1e-6
        assert abs((after_gm[0] - before_gm[0]) - 10) < 1e-6


def test_move_and_collide_blocks_on_a_wall_two_blocks_high(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        # Mover's GM top-left at (64, 64) -- a grid-aligned multiple of
        # cell_size, so cell_of resolves it to cell (2, 2) exactly (an
        # unaligned position like 48 lands on a cell BOUNDARY under cell_of's
        # nearest-centre rounding, not the cell a naive floor-division would
        # give -- see state.cell_of's own docstring / the CLAUDE.md landmine
        # this class of bug already cost a test-authoring mistake once).
        # A 2-block-high wall one cell east (3, 2) -- taller than
        # DEFAULT_MAX_STEP_UP (1), so a mover standing at layer 0 cannot
        # enter it.
        scene._bw_blocks = {(3, 2, 0): "stone", (3, 2, 1): "stone"}
        scene.block_world_camera = _default_cfg()
        mover = _FakeInst(64, scene.room_height - 64 - 32, 32, 32)
        scene.instances = [mover]
        scene._bw_move_and_collide(mover, dx=32, dy=0, collide=True)
        assert mover.x == 64   # blocked -- unchanged


def test_move_and_collide_steps_up_one_block(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        # A single-block step one cell east (3, 2) -- within
        # DEFAULT_MAX_STEP_UP. Same grid-aligned-top-left reasoning as above.
        scene._bw_blocks = {(3, 2, 0): "stone"}
        scene.block_world_camera = _default_cfg()
        mover = _FakeInst(64, scene.room_height - 64 - 32, 32, 32)
        # camera_instance set directly (mirrors what enable_block_world_view's
        # own codegen does when no named camera_object is given) so the
        # mover IS recognised as the camera and its footing updates z_layer.
        scene.block_world_camera["camera_instance"] = mover
        scene.instances = [mover]
        scene._bw_move_and_collide(mover, dx=32, dy=0, collide=True)
        assert mover.x == 96   # allowed -- stepped up
        assert scene.block_world_camera["z_layer"] == 1   # camera's own footing rose


def test_place_and_break_block(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
        scene.instances = [cam]
        scene.block_world_camera = _default_cfg(eye_height=0.5)
        scene.block_world_camera["camera_instance"] = cam

        # Nothing ahead within reach -> placement is the first cell entered.
        scene._bw_place_block(cam, "stone", 5)
        assert scene._bw_get_block(2, 1, 0) == "stone"

        scene._bw_break_block(cam, 5)
        assert scene._bw_get_block(2, 1, 0) is None

        # obsidian is unbreakable.
        scene._bw_set_block(2, 1, 0, "obsidian")
        scene._bw_break_block(cam, 5)
        assert scene._bw_get_block(2, 1, 0) == "obsidian"


def test_select_hotbar_slot_wraps(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        obj = _FakeInst(0, 0, 32, 32)
        scene._bw_select_hotbar_slot(obj, 0, False)
        assert obj.hotbar_index == 0
        scene._bw_select_hotbar_slot(obj, -1, True)
        assert obj.hotbar_index == len(scene.BW_DEFAULT_HOTBAR) - 1
        assert obj.hotbar_block == scene.BW_DEFAULT_HOTBAR[-1]


def test_load_block_world_atomic_reject(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        scene._bw_blocks = {(9, 9, 9): "stone"}   # pre-existing world
        scene._bw_load_block_world([
            {"x": 0, "y": 0, "z": 0, "type": "stone"},
            {"x": 1, "y": 1, "z": 1, "type": "not_a_real_block"},
        ])
        # The whole load rejected -- old world untouched.
        assert scene._bw_get_block(9, 9, 9) == "stone"
        assert scene._bw_get_block(0, 0, 0) is None

        scene._bw_load_block_world([{"x": 5, "y": 5, "z": 5, "type": "gold_block"}])
        assert scene._bw_get_block(5, 5, 5) == "gold_block"
        assert scene._bw_get_block(9, 9, 9) is None   # replaced, not merged


def test_build_hud_commands_crosshair_and_hotbar(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls, disp_w=640, disp_h=480)
        cmds = scene._bw_build_hud_commands(
            0, 40, 6, 16, "#202020", "#ffffff", "#ffd040", "#ffffff", 12, "#ffffff")
        lines = [c for c in cmds if c["type"] == "line"]
        assert len(lines) == 2   # crosshair
        rects = [c for c in cmds if c["type"] == "rectangle"]
        n = len(scene.BW_DEFAULT_HOTBAR)
        assert len(rects) == n * 2   # fill + border per slot
        texts = [c for c in cmds if c["type"] == "text"]
        assert len(texts) == n
        assert texts[0]["text"] == scene.BW_DEFAULT_HOTBAR[0][:4]


# --- Real per-pixel wall textures (Phase 6 Tier 4a) --------------------------

def test_fill_span_textured_full_height_maps_v_zero_to_one(exported):
    """Boundary sanity for the GM-down-to-Kivy-up v-coordinate flip
    (_bw_fill_span_textured's own docstring derivation): an UNCLIPPED
    full-height strip must map exactly v=[0,1], texel row 0 (top of the PNG)
    at the Kivy-TOP of the rect (v=1) -- the same orientation desktop and
    HTML5 use."""
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls, disp_h=200)
        group = _Group()
        tex = _FakeTex()
        scene._bw_fill_span_textured(
            group, x0=10, strip_w=5, y0_gm=40.0, y1_gm=100.0,
            full_top_gm=40.0, full_h=60.0, tex=tex, tex_x=3, shade=1.0, H=200.0)
        rects = [c for c in group.children if getattr(c, "kw", None)
                and "tex_coords" in c.kw]
        assert len(rects) == 1
        tc = rects[0].kw["tex_coords"]
        # (u0,v_bottom, u1,v_bottom, u1,v_top, u0,v_top)
        assert abs(tc[1] - 0.0) < 1e-9   # v_bottom
        assert abs(tc[5] - 1.0) < 1e-9   # v_top
        assert rects[0].kw["pos"] == (10, 100.0)   # H - y1
        assert rects[0].kw["size"] == (5, 60.0)
        assert tex.regions == [(3, 0, 1, tex.height)]


def test_fill_span_textured_clipped_from_below_maps_partial_v(exported):
    """A strip clipped to its upper half (y1_gm cut short of the block's
    true bottom) must show only the texture's TOP half -- v_bottom lands at
    0.5, not 0, confirming the clip/flip interacts correctly."""
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls, disp_h=200)
        group = _Group()
        tex = _FakeTex()
        # Full block spans GM [40,100]; only [40,70] is visible (clipped at
        # 70, i.e. the screen cuts off the bottom half).
        scene._bw_fill_span_textured(
            group, x0=0, strip_w=1, y0_gm=40.0, y1_gm=70.0,
            full_top_gm=40.0, full_h=60.0, tex=tex, tex_x=0, shade=1.0, H=200.0)
        tc = group.children[-1].kw["tex_coords"]
        assert abs(tc[1] - 0.5) < 1e-9   # v_bottom: half the texture's height was clipped away
        assert abs(tc[5] - 1.0) < 1e-9   # v_top: the true top edge is still fully visible


def test_render_block_world_draws_a_real_texture_when_loaded(exported):
    """With a texture pre-populated in the cache (bypassing load_image/
    CoreImage, which the stub env can't provide -- mirrors
    test_kivy_raycast.py's own texture-cache-injection pattern),
    _render_block_world draws a TEXTURED rectangle for the wall face
    instead of the flat-color fallback."""
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        scene._bw_blocks = {(2, 1, 0): "stone"}
        scene._bw_tex_cache = {"default_stone.png": _FakeTex()}
        cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
        scene.instances = [cam]
        scene.block_world_camera = _default_cfg(eye_height=0.5)
        scene.block_world_camera["camera_instance"] = cam
        scene._render_block_world()
        textured = [c for c in scene._bw_group.children if getattr(c, "kw", None)
                   and "tex_coords" in c.kw]
        assert len(textured) >= 1


def test_render_block_world_draws_a_textured_top_face_when_loaded(exported):
    """Tier 4b: with textures cached for both the side and top faces, a
    block whose top is exposed (nothing stacked above it, eye above it)
    must draw a textured top face -- not the flat-color fallback.

    The block sits several cells away from the camera (not point-blank):
    empirically verified first (a point-blank distance pushed the whole
    projected wall/face span off-screen entirely at this eye_height, a
    real test-authoring trap the same class as the grid-alignment one
    documented elsewhere in this file -- caught by checking actual
    _render_block_world output, not assumed)."""
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        scene._bw_blocks = {(5, 1, 0): "stone"}
        scene._bw_tex_cache = {"default_stone.png": _FakeTex()}
        cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
        scene.instances = [cam]
        scene.block_world_camera = _default_cfg(eye_height=1.5)
        scene.block_world_camera["camera_instance"] = cam
        scene._render_block_world()
        # Horizontal-face textured rects use a plain `texture=` Rectangle
        # (no tex_coords, unlike the wall pass) -- distinguish them that way.
        horiz_textured = [c for c in scene._bw_group.children if getattr(c, "kw", None)
                         and "texture" in c.kw and "tex_coords" not in c.kw]
        assert len(horiz_textured) >= 1


def test_top_cast_res_zero_falls_back_to_flat_color(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        scene._bw_blocks = {(5, 1, 0): "stone"}
        scene._bw_tex_cache = {"default_stone.png": _FakeTex()}
        cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
        scene.instances = [cam]
        scene.block_world_camera = _default_cfg(eye_height=1.5, top_cast_res=0)
        scene.block_world_camera["camera_instance"] = cam
        scene._render_block_world()
        horiz_textured = [c for c in scene._bw_group.children if getattr(c, "kw", None)
                         and "texture" in c.kw and "tex_coords" not in c.kw]
        assert horiz_textured == []


def test_kivy_owns_the_texture_loader_and_materialization():
    export_kivy_src = (REPO_ROOT / "extensions" / "block_world" / "export_kivy.py").read_text(encoding="utf-8")
    assert "def _bw_texture(self, filename):" in export_kivy_src
    assert "BLOCK_FACE_FILES = {" in export_kivy_src
    kivy_exporter_src = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
    assert "_materialize_extension_textures" in kivy_exporter_src
    assert "block_textures" in kivy_exporter_src
