"""Lowered ceilings in the HTML5 export (docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md, C7).

Run in headless Chromium where Playwright is installed (the dev box; skipped in CI). The port's pure
geometry (raycastLayoutColumnCeilings, castRaySteps with a ceilings map) is compared with the Python
originals on random inputs to 1e-12; an exported tunnel project's rendered rows (flat and textured),
its lintel hiding a billboard, and the view under a low roof while walking are checked against the
desktop's numbers. Structural checks (no browser) run everywhere.
"""
import json
import math
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_html5_raycast_stairs import _page, needs_browser, JS, PERSON  # noqa: E402

CELL = 32
TUNNEL = 40.0


# ------------------------------------------------------------ structural

def test_the_port_registers_the_ceiling_pieces():
    assert "registerExtensionAction('set_ceiling_height'" in JS
    for name in ("function raycastLayoutColumnCeilings(", "function raycastClipTopBefore(",
                 "buildCeilingHeights(cellSize, roomCeiling, floorHeights, eyeHeight) {",
                 "castCeilingSpans(ctx, layouts, sf, cellTex, ceilTex, facingScreenRad, fovRad, res) {",
                 "raycast_ceiling_z"):
        assert name in JS, name


# --------------------------------------------------------------- geometry

@needs_browser
def test_layout_column_ceilings_matches_python(tmp_path):
    from extensions.raycast_2_5d.renderer import layout_column_ceilings
    from test_html5_raycast_stairs import _stairs_project
    rnd = random.Random(23)
    cases = []
    for _ in range(300):
        d, crossings = 0.3, []
        h0 = rnd.choice([0.0, 8.0, 16.0, 32.0])
        c0 = rnd.choice([None, 40.0, 60.0, 80.0])
        for _ in range(rnd.randrange(0, 7)):
            d += rnd.uniform(0.2, 2.5)
            crossings.append([d, rnd.choice([0.0, 8.0, 16.0, 24.0, 40.0]), rnd.randrange(2), rnd.random(),
                              "%d,%d" % (rnd.randrange(9), 1), rnd.choice([None, 40.0, 56.0, 72.0])])
        is_hit = rnd.random() < 0.8
        hit = {"dist": (d + rnd.uniform(0.1, 3)) * 32, "side": rnd.randrange(2),
               "hit": is_hit, "texU": rnd.random(), "sprite": None}
        cases.append([crossings, hit, h0, c0, h0 + 24, 96.0, 32, rnd.uniform(0.85, 1.0), 240, 480, 20])
    with _page(_stairs_project(tmp_path), tmp_path) as pg:
        js = pg.evaluate("""cases => cases.map(c => {
            const r = raycastLayoutColumnCeilings(...c);
            return {treads: r.treads, risers: r.risers, wall: r.wall, ceilings: r.ceilings,
                    lintels: r.lintels, occluders: r.occluders, occludersTop: r.occludersTop,
                    wallDist: r.wallDist === Infinity ? null : r.wallDist};
        })""", cases)

    def same(a, b, ctx):
        assert len(a) == len(b), ctx
        for x, y in zip(a, b):
            for u, v in zip(x, y):
                if isinstance(u, str) or u is None or isinstance(u, bool):
                    assert u == v, ctx
                else:
                    assert u == pytest.approx(v, rel=1e-12, abs=1e-9), ctx

    for case, got in zip(cases, js):
        crossings, hit = case[0], case[1]
        py = layout_column_ceilings(
            [tuple(c) for c in crossings], (hit["dist"], hit["side"], hit["hit"], hit["texU"], None),
            *case[2:])
        for key, jkey in (("treads", "treads"), ("risers", "risers"), ("ceilings", "ceilings"),
                          ("lintels", "lintels"), ("occluders", "occluders"),
                          ("occluders_top", "occludersTop")):
            same(py[key], got[jkey], (key, case))
        assert (py["wall"] is None) == (got["wall"] is None)
        if py["wall"] is not None:
            assert list(py["wall"][:5]) == pytest.approx(got["wall"][:5], rel=1e-12, abs=1e-9)
        want = None if py["wall_dist"] == float("inf") else py["wall_dist"]
        assert (want is None and got["wallDist"] is None) or want == pytest.approx(got["wallDist"])


@needs_browser
def test_cast_ray_steps_with_ceilings_matches_python(tmp_path):
    from runtime.game_runner import GameRoom
    from extensions.raycast_2_5d.renderer import cast_ray_steps
    from extensions.raycast_2_5d.state import raycast_state
    from test_html5_raycast_stairs import _stairs_project
    rnd = random.Random(9)
    v = {(rnd.randrange(1, 14), rnd.randrange(0, 15)) for _ in range(40)}
    h = {(rnd.randrange(0, 15), rnd.randrange(1, 14)) for _ in range(40)}
    heights = {(rnd.randrange(15), rnd.randrange(15)): rnd.choice([8.0, 16.0]) for _ in range(40)}
    ceilings = {(rnd.randrange(15), rnd.randrange(15)): rnd.choice([40.0, 56.0]) for _ in range(60)}
    rays = [(rnd.uniform(33, 447), rnd.uniform(33, 447), rnd.uniform(-math.pi, math.pi))
            for _ in range(300)]
    room = GameRoom.__new__(GameRoom)
    st = raycast_state(room)
    st.update(v_walls=v, h_walls=h, v_sprites={}, h_sprites={})
    with _page(_stairs_project(tmp_path), tmp_path) as pg:
        js = pg.evaluate("""([v, h, hs, cs, rays]) => {
            const room = window.game.currentRoom;
            room._vWalls = new Set(v); room._hWalls = new Set(h);
            room._vWallSprites = new Map(); room._hWallSprites = new Map();
            const heights = new Map(hs), ceilings = new Map(cs);
            return rays.map(r => room.castRaySteps(r[0], r[1], r[2], 32, 20, heights, ceilings));
        }""", [["%d,%d" % k for k in v], ["%d,%d" % k for k in h],
               [["%d,%d" % k, val] for k, val in heights.items()],
               [["%d,%d" % k, val] for k, val in ceilings.items()], rays])
    for (px, py, ang), got in zip(rays, js):
        crossings, hit = cast_ray_steps(room, px, py, ang, 32, 20, heights, ceilings)
        assert len(crossings) == len(got["crossings"])
        for a, b in zip(crossings, got["crossings"]):
            assert list(a[:4]) == pytest.approx(b[:4], rel=1e-12, abs=1e-9)
            assert "%d,%d" % a[4] == b[4]
            assert a[5] == b[5]
        assert hit[2] == got["hit"]["hit"] and hit[0] == pytest.approx(got["hit"]["dist"], rel=1e-12)


# ------------------------------------------------------ an exported tunnel

def _tunnel_project(tmp_path, ceiling_texture="", billboard=False):
    import pygame
    proj = tmp_path / "proj"
    (proj / "sprites").mkdir(parents=True)
    surf = pygame.Surface((32, 32))
    surf.fill((128, 128, 128))
    pygame.image.save(surf, str(proj / "sprites" / "spr_block.png"))
    big = pygame.Surface((16, 96))
    big.fill((255, 0, 255))
    pygame.image.save(big, str(proj / "sprites" / "spr_tall.png"))
    sprites = {
        "spr_block": {"name": "spr_block", "asset_type": "sprite", "file_path": "sprites/spr_block.png",
                      "width": 32, "height": 32, "origin_x": 0, "origin_y": 0, "frames": 1,
                      "frame_width": 32, "frame_height": 32, "animation_type": "single", "speed": 10.0},
        "spr_tall": {"name": "spr_tall", "asset_type": "sprite", "file_path": "sprites/spr_tall.png",
                     "width": 16, "height": 96, "origin_x": 0, "origin_y": 0, "frames": 1,
                     "frame_width": 16, "frame_height": 96, "animation_type": "single", "speed": 10.0}}

    def obj(name, solid, events, sprite="spr_block"):
        return {"name": name, "asset_type": "object", "sprite": sprite, "visible": True,
                "solid": solid, "persistent": False, "depth": 0, "events": events}

    cam_params = {"camera_object": "", "fov": "66", "cell_size": "32", "render_distance": "20",
                  "wall_color": "#ff0000", "floor_color": "#00ff00", "ceiling_color": "#0000ff",
                  "wall_textured": "false", "wall_height": "3"}
    if ceiling_texture:
        cam_params["ceiling_texture"] = ceiling_texture
    objects = {
        "obj_wall": obj("obj_wall", True, {}),
        "obj_low": obj("obj_low", False, {"create": {"actions": [
            {"action": "set_ceiling_height", "parameters": {"height": "40"}}]}}),
        "obj_person": obj("obj_person", False, {"create": {"actions": [
            {"action": "enable_raycast_view", "parameters": cam_params}]}}),
        "obj_goal": obj("obj_goal", False, {}, "spr_tall"),
    }
    instances = []
    for g in range(15):
        for (x, y) in ((g, 0), (g, 14), (0, g), (14, g)):
            instances.append({"object_name": "obj_wall", "x": x * 32, "y": y * 32})
    for x in range(5, 9):
        for y in range(6, 9):
            instances.append({"object_name": "obj_low", "x": x * 32, "y": y * 32})
    if billboard:
        instances.append({"object_name": "obj_goal", "x": 232, "y": 192})
    instances.append({"object_name": "obj_person", "x": 64, "y": 224})
    project = {
        "name": "ceilings_e2e", "version": "1.0",
        "settings": {"window_width": 480, "window_height": 480, "room_speed": 30},
        "assets": {"sprites": sprites, "sounds": {}, "backgrounds": {}, "objects": objects,
                   "scripts": {}, "fonts": {}, "data": {},
                   "rooms": {"room0": {"name": "room0", "asset_type": "room", "width": 480, "height": 480,
                                       "background_color": "#000000", "instances": instances,
                                       "tiles": []}}},
    }
    (proj / "project.json").write_text(json.dumps(project), encoding="utf-8")
    return proj


def _column(pg):
    import base64
    import io
    from PIL import Image
    pg.wait_for_timeout(500)
    data = pg.evaluate("document.querySelector('canvas').toDataURL('image/png')")
    img = Image.open(io.BytesIO(base64.b64decode(data.split(",")[1]))).convert("RGB")
    return [img.getpixel((240, y)) for y in range(480)]


def _row(z, d):
    return 240 + (24 - z) * 480 / d


@needs_browser
def test_a_tunnel_renders_its_lintel_and_ceiling_on_the_predicted_rows(tmp_path):
    with _page(_tunnel_project(tmp_path), tmp_path) as pg:
        col = _column(pg)
    lintel_bottom, tunnel_end = _row(TUNNEL, 80), _row(TUNNEL, 208)
    assert col[50][0] > 0 and col[50][1:] == (0, 0)                       # the lintel: wall red
    for y in range(int(lintel_bottom) + 2, int(tunnel_end) - 1):
        assert col[y] == (0, 0, 255), y                                   # the tunnel ceiling, flat
    assert col[int(tunnel_end) + 3][0] > 0                                # far wall below the lip
    assert col[470] == (0, 255, 0)


@needs_browser
def test_a_textured_tunnel_ceiling_is_cast(tmp_path):
    with _page(_tunnel_project(tmp_path, ceiling_texture="spr_block"), tmp_path) as pg:
        col = _column(pg)
    lintel_bottom, tunnel_end = _row(TUNNEL, 80), _row(TUNNEL, 208)
    for y in range(int(lintel_bottom) + 6, int(tunnel_end) - 6):
        assert col[y] == (128, 128, 128), y


@needs_browser
def test_a_lintel_hides_the_top_of_a_billboard(tmp_path):
    with _page(_tunnel_project(tmp_path, billboard=True), tmp_path) as pg:
        col = _column(pg)
    rows = [y for y, c in enumerate(col) if c == (255, 0, 255)]
    assert rows and min(rows) >= int(_row(TUNNEL, 80)) - 1 and max(rows) > 300
    assert col[120][0] > 0 and col[120][1:] == (0, 0)


@needs_browser
def test_the_view_drops_into_a_tunnel_in_the_browser(tmp_path):
    from test_raycast_climbing import _write_project
    marker = {"name": "obj_low", "asset_type": "object", "sprite": "spr_block", "visible": True,
              "solid": False, "persistent": False, "depth": 0,
              "events": {"create": {"actions": [
                  {"action": "set_ceiling_height", "parameters": {"height": "40"}}]}}}
    platform = {(x, 7): 32.0 for x in range(2, 5)}
    tunnel = [{"object_name": "obj_low", "x": x * CELL, "y": 7 * CELL} for x in range(5, 14)]   # to the east wall
    proj = tmp_path / "proj"
    proj.mkdir()
    _write_project(proj, platform, {"obj_low": marker}, tunnel, person_x=2 * CELL)
    with _page(proj, tmp_path) as pg:
        pg.evaluate("() => { window.__eyes = []; registerFrameUpdate("
                    "g => window.__eyes.push([g.currentRoom._raycastEyeFloor, "
                    "g.currentRoom.instances.find(i => (i.object_name || i.name) === 'obj_person').x])); }")
        pg.keyboard.down("ArrowUp")
        pg.wait_for_timeout(3000)
        pg.keyboard.up("ArrowUp")
        res = pg.evaluate("() => { const p = " + PERSON + "; return {x: p.x, c: p.raycast_ceiling_z, "
                          "eyes: window.__eyes}; }")
    assert res["x"] > 6 * CELL and res["c"] == 40
    inside = [e for e, x in res["eyes"] if isinstance(e, (int, float)) and x + 16 >= 5 * CELL]
    assert inside and all(e + 24 <= 40 - 4 + 1e-9 for e in inside)
