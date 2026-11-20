"""Raycast stairs in the Kivy (Android/iOS) export (docs/RAYCAST_STAIRS_PLAN.md, S11).

Three layers, like the rest of the Kivy raycast tests:

* codegen and constants (run everywhere);
* the stub-kivy harness drives the REAL generated scene code: the copied
  geometry (_cast_ray_steps, _layout_column) equals the desktop functions on
  random inputs, the riser rectangles land where the projection puts them
  (Kivy y = h - row), and the climbing hook refuses / allows / eases;
* real Kivy (skipped without it or without GL): an exported staircase is drawn
  on the predicted rows, and a monster turns back at a block too high.
"""
import json
import math
import random
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling test import

from test_kivy_raycast import (  # noqa: E402
    _stub_kivy_env, _scene_class, _blank_scene, _FakeInst, _export_raycast_1,
)

KIVY_SRC = (ROOT / "extensions" / "raycast_2_5d" / "export_kivy.py").read_text(encoding="utf-8")


# ------------------------------------------------------------- everywhere

def test_codegen_for_the_action_and_max_step():
    from extensions.raycast_2_5d.export_kivy import (
        _cg_set_floor_height, _cg_enable_raycast_view, ACTION_CODEGEN)
    assert ACTION_CODEGEN["set_floor_height"] is _cg_set_floor_height
    code = _cg_set_floor_height(None, {"height": "16", "top_texture": "spr_top"}, "create")
    assert code == ("self.raycast_floor_height = float(16); "
                    "self.raycast_step_top_texture = 'spr_top'; "
                    "self.raycast_step_side_texture = ''")
    assert "self.raycast_floor_height = float(8)" in _cg_set_floor_height(None, {}, "create")
    assert "'max_step': 20.0" in _cg_enable_raycast_view(None, {"max_step": "20"}, "create")
    assert "'max_step': 12" in _cg_enable_raycast_view(None, {}, "create")


def test_constants_match_desktop():
    from extensions.raycast_2_5d import climbing, heights
    for name, value in (("RAYCAST_CEILING_MARGIN", heights.CEILING_MARGIN),
                        ("RAYCAST_DEFAULT_MAX_STEP", climbing.DEFAULT_MAX_STEP),
                        ("RAYCAST_CLIMB_SPEED", climbing.CLIMB_SPEED),
                        ("RAYCAST_FALL_GRAVITY", climbing.FALL_GRAVITY)):
        line = next(l for l in KIVY_SRC.splitlines() if l.strip().startswith(name + " = "))
        assert float(line.split("=")[1]) == value, name


def test_steps_are_not_billboards_in_kivy():
    body = KIVY_SRC[KIVY_SRC.index("        billboards = []"):]
    assert "if getattr(inst, 'raycast_floor_height', None) is not None:" in body[:1200]


# ------------------------------------------------------------ stub harness

@pytest.fixture(scope="module")
def exported():
    return _export_raycast_1()


def test_cast_ray_steps_and_layout_equal_desktop(exported):
    from runtime.game_runner import GameRoom
    from extensions.raycast_2_5d.renderer import cast_ray_steps, layout_column
    from extensions.raycast_2_5d.state import raycast_state
    rnd = random.Random(3)
    v = {(rnd.randrange(1, 14), rnd.randrange(0, 15)) for _ in range(40)}
    h = {(rnd.randrange(0, 15), rnd.randrange(1, 14)) for _ in range(40)}
    heights = {(rnd.randrange(15), rnd.randrange(15)): rnd.choice([8.0, 16.0, 40.0])
               for _ in range(60)}
    room = GameRoom.__new__(GameRoom)
    raycast_state(room).update(v_walls=v, h_walls=h, v_sprites={}, h_sprites={})
    with _stub_kivy_env(exported):
        scene = _blank_scene(_scene_class(exported))
        scene._raycast_v_walls, scene._raycast_h_walls = v, h
        scene._raycast_v_wall_sprites, scene._raycast_h_wall_sprites = {}, {}
        for _ in range(300):
            px, py = rnd.uniform(33, 447), rnd.uniform(33, 447)
            ang = rnd.uniform(-math.pi, math.pi)
            want = cast_ray_steps(room, px, py, ang, 32, 20, heights)
            got = scene._cast_ray_steps(px, py, ang, 32, 20, heights)
            assert got == want
            cos_off, h0 = rnd.uniform(0.85, 1.0), rnd.choice([0.0, 8.0, 16.0])
            args = (want[0], want[1], h0, h0 + 24, 96.0, 32, cos_off, 240.0, 480, 20)
            assert scene._layout_column(*args) == layout_column(*args)


def _step(gx, gy, height, room_h=480):
    inst = _FakeInst(gx * 32, room_h - gy * 32 - 32, 32, 32, solid=False)
    inst.raycast_floor_height = float(height)
    inst.raycast_step_top_texture = ""
    inst.raycast_step_side_texture = ""
    return inst


def _stairs_scene(cls, steps, cam_cell=(2, 7), room=480):
    scene = _blank_scene(cls)
    scene.room_width = scene.room_height = room
    scene.display_width = scene.display_height = room
    scene._raycast_floor_heights = {}
    scene._raycast_step_prev = None
    scene._raycast_eye_floor = None
    scene._raycast_eye_vz = 0.0
    insts = [_FakeInst(14 * 32, room - gy * 32 - 32, 32, 32, solid=True) for gy in range(15)]
    insts += [_step(gx, gy, hgt, room) for (gx, gy), hgt in steps.items()]
    cam = _FakeInst(cam_cell[0] * 32, room - cam_cell[1] * 32 - 32, 32, 32, solid=False)
    insts.append(cam)
    scene.instances = insts
    scene.raycast_camera = {
        "enabled": True, "cell_size": 32, "fov": 66, "render_distance": 20,
        "columns": 480, "camera_instance": cam, "wall_textured": False,
        "wall_color": "#ff0000", "floor_color": "#00ff00", "ceiling_color": "#0000ff",
        "wall_height": 3}
    return scene, cam


def test_risers_are_drawn_where_the_projection_puts_them(exported):
    """Facing a 5-wide staircase: the first riser (0 -> 8, 80 px away)
    covers y-down rows y(8)=336 .. y(0)=384, i.e. a Kivy rectangle from
    y = 480 - 384 to 480 - 336 in the centre column."""
    from extensions.raycast_2_5d.renderer import stairs_y
    steps = {(x, r): 8.0 * (x - 4) for x in range(5, 9) for r in range(5, 10)}
    with _stub_kivy_env(exported):
        scene, _ = _stairs_scene(_scene_class(exported), steps)
        scene._render_raycast()
        rects = [c.kw for c in scene._raycast_group.children
                 if getattr(c, "kw", None) and "pos" in c.kw and "texture" not in c.kw]
    row = lambda y: int(math.floor(y + 0.5))  # noqa: E731
    r0, r1 = row(stairs_y(8, 24, 80, 240, 480)), row(stairs_y(0, 24, 80, 240, 480))
    centre = [r for r in rects if r["pos"][0] == 240 and r["size"][0] == 1]
    assert any(r["pos"][1] == 480 - r1 and r["size"][1] == r1 - r0 for r in centre), centre


def _tick(scene, cam, dx=0.0, dy=0.0):
    cam.x += dx
    cam.y += dy
    scene._ext_update__raycast_2_5d(1 / 60)


def test_climbing_in_kivy(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene, cam = _stairs_scene(cls, {(3, 7): 8.0, (4, 7): 24.0})
        _tick(scene, cam)                                # first frame: snapshot
        assert scene._raycast_eye_floor == 0.0
        _tick(scene, cam, dx=16)                         # onto the 8-px step
        assert cam.x == 80 and cam.raycast_floor_z == 8.0 and cam.raycast_step_blocked == 0
        assert scene._raycast_eye_floor == 2.0           # eased, not snapped
        _tick(scene, cam, dx=32)                         # 8 -> 24: too high
        assert cam.x == 80 and cam.raycast_step_blocked == 1
        _tick(scene, cam, dx=10 * 32)                    # a teleport is kept
        assert cam.x == 80 + 320


def test_climbing_slides_along_a_ledge_in_kivy(exported):
    """Kivy is y-UP: moving 'down' the GM map is a NEGATIVE Kivy dy."""
    with _stub_kivy_env(exported):
        scene, cam = _stairs_scene(_scene_class(exported), {(3, 7): 16.0, (3, 8): 16.0})
        _tick(scene, cam)
        y0 = cam.y
        _tick(scene, cam, dx=16, dy=-6)
        assert cam.x == 64 and cam.y == y0 - 6 and cam.raycast_step_blocked == 1


# --------------------------------------------------------------- real Kivy

WORKER = ROOT / "tests" / "_real_kivy_game.py"


def _real_export(project_writer, tmp_path, *args):
    pytest.importorskip("kivy")
    from export.Kivy.kivy_exporter import KivyExporter
    proj = tmp_path / "proj"
    proj.mkdir()
    project_writer(proj, *args)
    data = json.loads((proj / "project.json").read_text(encoding="utf-8"))
    out = tmp_path / "export"
    assert KivyExporter(data, proj, out).export()
    game = out / "game"
    text = (game / "scenes" / "room0.py").read_text(encoding="utf-8")
    cls = next(l.split("class ")[1].split("(")[0] for l in text.splitlines()
               if l.startswith("class ") and "(Widget)" in l)
    return game, cls


def _run(game, request):
    work = Path(tempfile.mkdtemp(prefix="stairs_kivy_"))
    req, res = work / "request.json", work / "result.json"
    req.write_text(json.dumps(request), encoding="utf-8")
    try:
        proc = subprocess.run([sys.executable, str(WORKER), str(game), str(req), str(res)],
                              capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        pytest.skip("real Kivy worker timed out")
    if not res.exists():
        pytest.skip(f"real Kivy cannot run here (exit {proc.returncode}): {proc.stderr[-300:]}")
    data = json.loads(res.read_text(encoding="utf-8"))
    if data.get("fatal"):
        pytest.skip(f"real Kivy cannot render here: {data['fatal']}")
    assert data.get("error") is None, data["error"]
    return data


def test_real_kivy_draws_the_staircase_on_the_predicted_rows(tmp_path):
    from test_raycast_stairs_render import _write_project
    from extensions.raycast_2_5d.renderer import stairs_y
    game, cls = _real_export(_write_project, tmp_path)
    top, bot = stairs_y(8, 24, 80, 240, 480), stairs_y(0, 24, 80, 240, 480)
    points = {"riser": [240, int((top + bot) / 2)], "tread": [240, int(top) - 4],
              "ground": [240, 470], "ceiling": [240, 20]}
    data = _run(game, {"module": "scenes.room0", "class": cls, "frames": 3,
                       "width": 480, "height": 480, "points": points})
    got = {k: v[:3] for k, v in data["points"].items()}
    assert got["ground"] == [0, 255, 0] and got["tread"] == [0, 255, 0]
    assert got["ceiling"] == [0, 0, 255]
    r, g, b = got["riser"]
    assert r > 100 and g == 0 and b == 0, got


def test_real_kivy_monster_turns_back_at_a_high_block(tmp_path):
    from test_raycast_climbing import _write_project
    monster = {"name": "obj_monster", "asset_type": "object", "sprite": "spr_block",
               "visible": True, "solid": False, "persistent": False, "depth": 0,
               "events": {
                   "create": {"actions": [{"action": "set_hspeed",
                                           "parameters": {"speed": "2"}}]},
                   "end_step": {"actions": [
                       {"action": "test_variable", "parameters": {
                           "variable": "raycast_step_blocked", "value": "1",
                           "scope": "instance", "operation": "equal"}},
                       {"action": "reverse_horizontal", "parameters": {}}]}}}
    game, cls = _real_export(_write_project, tmp_path, {(8, 3): 16.0},
                             {"obj_monster": monster},
                             [{"object_name": "obj_monster", "x": 128, "y": 96}])
    data = _run(game, {"module": "scenes.room0", "class": cls, "frames": 90,
                       "width": 480, "height": 480, "track": ["obj_monster"]})
    (start,), (end,) = data["tracked"]["obj_monster"]
    # Unblocked it would be at ~128 + 180 = 308, past the block at x = 256.
    # Blocked at x ~ 240 (its centre at the block's edge) and reversed, it has
    # walked back well before the end.
    assert end[0] < 225, (start, end)


def test_kivy_minimap_raised_cells_equal_python():
    """Execute the generated base object's _draw_minimap (BASE_OBJECT_CODE)
    against a stand-in scene and compare its raised squares with
    hud.build_minimap_commands -- five heights, so five shades."""
    import types
    from extensions.raycast_2_5d.export_kivy import BASE_OBJECT_CODE
    from extensions.raycast_2_5d.hud import build_minimap_commands
    ns = {"math": math}
    exec("class _Base:\n" + BASE_OBJECT_CODE, ns)
    raised = {(5, r): 8.0 * (r - 4) for r in range(5, 10)}
    obj = ns["_Base"]()
    obj._draw_queue = []
    obj.scene = types.SimpleNamespace(
        room_width=480, room_height=480, _raycast_cell_size=32,
        _raycast_v_walls=set(), _raycast_h_walls=set(), raycast_camera={},
        _find_raycast_camera=lambda cfg: None, _raycast_floor_heights=raised)
    obj._draw_minimap(0, 0, 100, "#000000", "#c8c8c8", "#ffd040")
    py = build_minimap_commands(set(), set(), 32, 480, 480, None, None, 0.0, 0, 0, 100,
                                "#000000", "#c8c8c8", "#ffd040", raised=raised)
    got, want = obj._draw_queue[1:6], py[1:6]
    assert len({c["color"] for c in want}) == 5
    for a, b in zip(want, got):
        assert a["color"] == b["color"] and b["filled"] is True
        for k in ("x1", "y1", "x2", "y2"):
            assert a[k] == pytest.approx(b[k])


def test_kivy_textured_riser_samples_the_bottom_of_the_tile(exported):
    """A 0 -> 8 px riser is the bottom 8/48 of a wall-texture tile (tiles are
    RAYCAST_TEXTURE_HEIGHT = 1.5 cells = 48 px tall, anchored at height 0):
    its rectangle's tex_coords run from v ~ 0 (the tile's bottom; Kivy
    textures are bottom-origin) up to v ~ 1/6."""
    from test_kivy_raycast import _FakeTex
    with _stub_kivy_env(exported):
        scene, _ = _stairs_scene(_scene_class(exported), {(5, r): 8.0 for r in range(5, 10)})
        scene.raycast_camera.update(wall_textured=True, wall_texture="spr_wall")
        scene._raycast_tex_cache = {"spr_wall": _FakeTex(32, 48)}
        scene._render_raycast()
        rects = [c.kw for c in scene._raycast_group.children
                 if getattr(c, "kw", None) and "tex_coords" in c.kw and c.kw["pos"][0] == 240]
    # the riser is the nearest textured slice: the lowest on screen (smallest Kivy y)
    riser = min(rects, key=lambda r: r["pos"][1])
    v_low, v_high = riser["tex_coords"][1], riser["tex_coords"][5]
    assert v_low == pytest.approx(0.0, abs=0.02)
    assert v_high == pytest.approx(8 / 48, abs=0.02)


def test_kivy_billboard_behind_a_step_loses_its_lower_rows(exported):
    """A billboard behind an eye-height (24 px) block keeps only the rows
    above the block's far edge -- in Kivy terms its rectangles start at
    y = h - limit, not at the sprite's own bottom."""
    from test_kivy_raycast import _FakeTex
    from extensions.raycast_2_5d.renderer import stairs_y

    def bottoms(steps):
        with _stub_kivy_env(exported):
            scene, _ = _stairs_scene(_scene_class(exported), steps)
            bb = _FakeInst(7 * 32 + 8, 480 - 7 * 32 - 8 - 16, 16, 16, solid=False)
            bb.sprite_name = "spr_goal"
            scene.instances.insert(0, bb)
            scene._raycast_tex_cache = {"spr_goal": _FakeTex(16, 16)}
            scene._render_raycast()
            rects = [c.kw for c in scene._raycast_group.children
                     if getattr(c, "kw", None) and "tex_coords" in c.kw
                     and c.kw.get("texture") is not None and c.kw["size"][0] < 30]
        return min(r["pos"][1] for r in rects)

    free = bottoms({(0, 13): 8.0})                       # stairs mode, nothing in front
    behind = bottoms({(0, 13): 8.0, (4, 7): 24.0})
    limit = math.floor(stairs_y(24, 24, (5 - 2.5) * 32, 240, 480) + 0.5)
    assert free < 480 - limit - 5                        # it really reached below
    assert behind == pytest.approx(480 - limit)
