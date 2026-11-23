"""Lowered ceilings in the Kivy (Android/iOS) export (docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md, C8).

Three layers, like the stairs port:

* codegen (runs everywhere);
* the stub-kivy harness drives the REAL generated scene code: the copied geometry
  (_cast_ray_steps with ceilings, _layout_column_ceilings, _clip_top_before) equals the desktop
  functions on random inputs, the ceiling map clamps like heights.build_ceiling_heights, the
  textured ceiling buffer is cast only inside lowered spans, lintels and flat spans land on the
  projected rows (Kivy y = h - row), a lintel hides a billboard's top, and the climbing hook
  publishes raycast_ceiling_z and limits the view;
* real Kivy (skipped without it or without GL): an exported tunnel is drawn on the predicted rows.
"""
import math
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling test import

from test_kivy_raycast import (  # noqa: E402
    _stub_kivy_env, _scene_class, _FakeInst, _FakeTex, _export_raycast_1,
)
from test_kivy_raycast_stairs import (  # noqa: E402
    _stairs_scene, _step, _tick, _real_export, _run,
)

KIVY_SRC = (ROOT / "extensions" / "raycast_2_5d" / "export_kivy.py").read_text(encoding="utf-8")
TUNNEL = 40.0
TUNNEL_CELLS = [(x, y) for x in range(5, 9) for y in range(6, 9)]


def _marker(gx, gy, height=TUNNEL, room_h=480, texture=""):
    inst = _FakeInst(gx * 32, room_h - gy * 32 - 32, 32, 32, solid=False)
    inst.raycast_ceiling_height = float(height)
    inst.raycast_ceiling_texture = texture
    return inst


def _row(z, d):
    return 240 + (24 - z) * 480 / d


# ------------------------------------------------------------- everywhere

def test_codegen_for_the_action():
    from extensions.raycast_2_5d.export_kivy import _cg_set_ceiling_height, ACTION_CODEGEN
    assert ACTION_CODEGEN["set_ceiling_height"] is _cg_set_ceiling_height
    assert _cg_set_ceiling_height(None, {"height": "56", "texture": "spr_c"}, "create") == (
        "self.raycast_ceiling_height = float(56); self.raycast_ceiling_texture = 'spr_c'")
    assert "self.raycast_ceiling_height = float(40)" in _cg_set_ceiling_height(None, {}, "create")


def test_ceiling_markers_are_not_billboards_or_movers_in_kivy():
    body = KIVY_SRC[KIVY_SRC.index("        billboards = []"):]
    assert "if getattr(inst, 'raycast_ceiling_height', None) is not None:" in body[:1500]
    assert "and getattr(i, 'raycast_ceiling_height', None) is None]" in KIVY_SRC


# ------------------------------------------------------------ stub harness

@pytest.fixture(scope="module")
def exported():
    return _export_raycast_1()


def test_ray_walk_layout_and_clip_equal_desktop(exported):
    from runtime.game_runner import GameRoom
    from extensions.raycast_2_5d.renderer import (
        cast_ray_steps, layout_column_ceilings, _clip_top_before)
    from extensions.raycast_2_5d.state import raycast_state
    rnd = random.Random(31)
    v = {(rnd.randrange(1, 14), rnd.randrange(0, 15)) for _ in range(40)}
    h = {(rnd.randrange(0, 15), rnd.randrange(1, 14)) for _ in range(40)}
    heights = {(rnd.randrange(15), rnd.randrange(15)): rnd.choice([8.0, 16.0]) for _ in range(40)}
    ceilings = {(rnd.randrange(15), rnd.randrange(15)): rnd.choice([40.0, 56.0]) for _ in range(60)}
    room = GameRoom.__new__(GameRoom)
    raycast_state(room).update(v_walls=v, h_walls=h, v_sprites={}, h_sprites={})
    with _stub_kivy_env(exported):
        scene, _ = _stairs_scene(_scene_class(exported), {})
        scene._raycast_v_walls, scene._raycast_h_walls = v, h
        scene._raycast_v_wall_sprites, scene._raycast_h_wall_sprites = {}, {}
        for _ in range(300):
            px, py = rnd.uniform(33, 447), rnd.uniform(33, 447)
            ang = rnd.uniform(-math.pi, math.pi)
            want = cast_ray_steps(room, px, py, ang, 32, 20, heights, ceilings)
            assert scene._cast_ray_steps(px, py, ang, 32, 20, heights, ceilings) == want
            cos_off, h0 = rnd.uniform(0.85, 1.0), rnd.choice([0.0, 8.0, 16.0])
            c0 = rnd.choice([None, 40.0, 60.0])
            args = (want[0], want[1], h0, c0, h0 + 24, 96.0, 32, cos_off, 240.0, 480, 20)
            assert scene._layout_column_ceilings(*args) == layout_column_ceilings(*args)
            occ = [(rnd.uniform(1, 400), rnd.uniform(0, 480)) for _ in range(5)]
            occ.sort()
            dist = rnd.uniform(1, 400)
            assert scene._clip_top_before(occ, dist) == _clip_top_before(occ, dist)


def test_the_ceiling_map_clamps_like_desktop(exported):
    with _stub_kivy_env(exported):
        scene, _ = _stairs_scene(_scene_class(exported), {(3, 3): 16.0})
        scene.instances += [_marker(3, 3, 0.0),        # clamped up to 16 + 24 + 4 = 44
                            _marker(4, 3, 30.0),       # lowest wins over...
                            _marker(4, 3, 60.0),       # ...this one
                            _marker(5, 3, 200.0)]      # at/above the room ceiling: nothing
        ceilings, textures = scene._raycast_build_ceiling_heights(32, 96.0, {(3, 3): 16.0}, 24.0)
    assert ceilings[(3, 3)] == 44.0
    assert ceilings[(4, 3)] == 30.0
    assert (5, 3) not in ceilings


def test_the_ceiling_clamp_keeps_a_cell_standable(exported):
    with _stub_kivy_env(exported):
        scene, _ = _stairs_scene(_scene_class(exported), {})
        scene.instances.append(_marker(4, 3, 10.0))
        ceilings, _ = scene._raycast_build_ceiling_heights(32, 96.0, {}, 24.0)
    assert ceilings[(4, 3)] == 24.0 + 4.0                      # floor + eye + margin


def _tunnel_scene(cls, **cfg):
    scene, cam = _stairs_scene(cls, {})
    scene.instances += [_marker(x, y) for x, y in TUNNEL_CELLS]
    scene.raycast_camera.update(cfg)
    return scene, cam


def _rects(scene):
    return [c.kw for c in scene._raycast_group.children
            if getattr(c, "kw", None) and "pos" in c.kw and "texture" not in c.kw]


def test_the_lintel_and_the_flat_ceiling_land_on_the_projected_rows(exported):
    with _stub_kivy_env(exported):
        scene, _ = _tunnel_scene(_scene_class(exported))
        scene._render_raycast()
        centre = [r for r in _rects(scene) if r["pos"][0] == 240 and r["size"][0] == 1]
    row = lambda y: int(math.floor(y + 0.5))  # noqa: E731
    lintel_bottom, tunnel_end = row(_row(TUNNEL, 80)), row(_row(TUNNEL, 208))
    assert any(r["pos"][1] == 480 - lintel_bottom and r["size"][1] == lintel_bottom for r in centre), centre
    assert any(r["pos"][1] == 480 - tunnel_end and r["size"][1] == tunnel_end - lintel_bottom
               for r in centre), centre


def test_the_textured_ceiling_buffer_is_cast_only_inside_the_lowered_spans(exported):
    import math as _m
    with _stub_kivy_env(exported):
        scene, _ = _tunnel_scene(_scene_class(exported))
        scene._raycast_px_cache = {"spr_c": (bytes([200, 100, 50, 255]) * 4, 2, 2)}
        scene.raycast_camera.update(ceiling_texture="spr_c")
        px = scene._raycast_px_cache["spr_c"]
        # Build the layouts the renderer would, then the buffer.
        scene._render_raycast()
        # Re-run the pieces directly for the assertion.
        heights, _ = scene._raycast_build_floor_heights(32, 1e9)
        ceilings, _ = scene._raycast_build_ceiling_heights(32, 96.0, heights, 24.0)
        layouts = []
        cam_x, cam_y = 80.0, 240.0
        for col in range(480):
            camera_x = 2.0 * (col + 0.5) / 480 - 1.0
            ro = _m.atan(_m.tan(_m.radians(66) / 2) * camera_x)
            cr, hit = scene._cast_ray_steps(cam_x, cam_y, ro, 32, 20, heights, ceilings)
            layouts.append(scene._layout_column_ceilings(
                cr, hit, 0.0, None, 24.0, 96.0, 32, _m.cos(ro), 240.0, 480.0, 20))
        sf = {"w": 480.0, "view_h": 480.0, "cell_size": 32, "eye_z": 24.0, "cam_x": cam_x,
              "cam_y": cam_y, "wall_top_z": 96.0, "ceiling_color": (0.0, 0.0, 1.0),
              "col_width": 1.0}
        buf, sw, sh, painted = scene._stairs_ceiling_buffer(layouts, sf, {}, px, 0.0, _m.radians(66), 4)
    assert painted and (sw, sh) == (120, 60)
    # Centre column i = 60: transparent above the lintel's bottom, painted inside the tunnel.
    col = [buf[(j * sw + 60) * 4: (j * sw + 60) * 4 + 4] for j in range(sh)]
    first = _row(TUNNEL, 80) / 4
    assert all(c[3] == 0 for c in col[:int(first) - 2])
    inside = col[int(first) + 3: int(_row(TUNNEL, 208) / 4) - 2]
    assert inside and all(tuple(c) == (200, 100, 50, 255) for c in inside)


def test_a_lintel_hides_the_top_of_a_billboard(exported):
    def tops(markers):
        with _stub_kivy_env(exported):
            scene, _ = _stairs_scene(_scene_class(exported), {})
            scene.instances += markers
            bb = _FakeInst(232, 480 - 192 - 96, 16, 96, solid=False)
            bb.sprite_name = "spr_goal"
            scene.instances.insert(0, bb)
            scene._raycast_tex_cache = {"spr_goal": _FakeTex(16, 96)}
            scene._render_raycast()
            rects = [c.kw for c in scene._raycast_group.children
                     if getattr(c, "kw", None) and c.kw.get("texture") is not None
                     and "tex_coords" in c.kw and c.kw["size"][0] < 30]
        return max(r["pos"][1] + r["size"][1] for r in rects)

    free = tops([])
    behind = tops([_marker(x, y) for x, y in TUNNEL_CELLS])
    lintel_bottom = int(math.floor(_row(TUNNEL, 80) + 0.5))
    assert free > 480 - 100                                   # it reaches high up
    assert behind == pytest.approx(480 - lintel_bottom)       # cut at the lintel's lower edge


def test_climbing_reads_the_ceiling_and_limits_the_view(exported):
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene, cam = _stairs_scene(cls, {(2, 7): 32.0})
        scene.instances += [_marker(3, 7)]
        _tick(scene, cam)
        assert scene._raycast_eye_floor == 32.0 and cam.raycast_ceiling_z == 96.0
        _tick(scene, cam, dx=16)                             # off the ledge, under the roof
        assert cam.raycast_ceiling_z == TUNNEL
        assert scene._raycast_eye_floor + 24.0 <= TUNNEL - 4.0
        for _ in range(20):
            _tick(scene, cam)
            assert scene._raycast_eye_floor + 24.0 <= TUNNEL - 4.0 + 1e-9
        assert scene._raycast_eye_floor == 0.0


def test_a_ceiling_marker_is_not_a_mover(exported):
    with _stub_kivy_env(exported):
        scene, cam = _stairs_scene(_scene_class(exported), {})
        m = _marker(4, 3)
        scene.instances.append(m)
        _tick(scene, cam)
        assert not hasattr(m, "raycast_ceiling_z")


# --------------------------------------------------------------- real Kivy

def _write_tunnel_project(proj, ceiling_texture=""):
    from test_html5_raycast_ceilings import _tunnel_project
    import shutil
    made = _tunnel_project(proj.parent / "built", ceiling_texture=ceiling_texture)
    for item in made.iterdir():
        dest = proj / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)


def test_real_kivy_draws_the_tunnel_on_the_predicted_rows(tmp_path):
    game, cls = _real_export(_write_tunnel_project, tmp_path)
    lintel_bottom, tunnel_end = _row(TUNNEL, 80), _row(TUNNEL, 208)
    points = {"lintel": [240, 50], "tunnel": [240, int((lintel_bottom + tunnel_end) / 2)],
              "ground": [240, 470]}
    data = _run(game, {"module": "scenes.room0", "class": cls, "frames": 3,
                       "width": 480, "height": 480, "points": points})
    got = {k: v[:3] for k, v in data["points"].items()}
    r, g, b = got["lintel"]
    assert r > 100 and g == 0 and b == 0, got                 # the lintel: shaded wall red
    assert got["tunnel"] == [0, 0, 255] and got["ground"] == [0, 255, 0], got


def test_real_kivy_casts_a_textured_tunnel_ceiling(tmp_path):
    game, cls = _real_export(lambda proj: _write_tunnel_project(proj, "spr_block"), tmp_path)
    lintel_bottom, tunnel_end = _row(TUNNEL, 80), _row(TUNNEL, 208)
    points = {"tunnel": [240, int((lintel_bottom + tunnel_end) / 2)]}
    data = _run(game, {"module": "scenes.room0", "class": cls, "frames": 3,
                       "width": 480, "height": 480, "points": points})
    r, g, b = data["points"]["tunnel"][:3]
    assert abs(r - 128) <= 2 and abs(g - 128) <= 2 and abs(b - 128) <= 2, data["points"]
