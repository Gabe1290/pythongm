"""Raycast stairs in the HTML5 export (docs/RAYCAST_STAIRS_PLAN.md, S10).

Run in headless Chromium where Playwright is installed (the dev box; skipped
in CI, like the micro:bit browser tests). The port's pure geometry
(raycastLayoutColumn, castRaySteps) is compared with the Python originals on
random inputs; an exported project's rendered rows, its climbing with real
key presses, and its minimap are checked against the desktop's numbers.
Structural checks (no browser) run everywhere.
"""
import functools
import http.server
import math
import random
import shutil
import sys
import threading
from contextlib import contextmanager
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling test import

JS = (ROOT / "extensions" / "raycast_2_5d" / "export_html5.js").read_text(encoding="utf-8")
ENGINE = (ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


# ------------------------------------------------------------ structural

def test_the_engine_has_an_after_collision_phase():
    assert "function registerFrameUpdate(fn, phase)" in ENGINE
    step = ENGINE[ENGINE.index("        // 6. Collision events"):ENGINE.index("        // 7. End Step events")]
    assert "runExtensionAfterCollisionUpdates(game);" in step


def test_the_port_registers_its_pieces():
    assert "registerExtensionAction('set_floor_height'" in JS
    assert "registerFrameUpdate(raycastClimbBefore);" in JS
    assert "registerFrameUpdate(raycastClimbAfter, 'after_collision');" in JS
    assert "max_step: rNum('max_step', 12)," in JS
    assert "if (raycastIsStep(inst)) continue;" in JS          # steps are not billboards


def test_the_port_s_constants_match_python():
    from extensions.raycast_2_5d import climbing, heights
    for name, value in (("RAYCAST_CEILING_MARGIN", heights.CEILING_MARGIN),
                        ("RAYCAST_DEFAULT_MAX_STEP", climbing.DEFAULT_MAX_STEP),
                        ("RAYCAST_CLIMB_SPEED", climbing.CLIMB_SPEED),
                        ("RAYCAST_FALL_GRAVITY", climbing.FALL_GRAVITY)):
        line = next(l for l in JS.splitlines() if l.startswith("const %s = " % name))
        assert float(line.split("=")[1].split(";")[0]) == value, name


# --------------------------------------------------------------- browser

def _browser_ok():
    try:
        import microbit_js_parity
        return microbit_js_parity.available()
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="needs Playwright + Chromium")


@contextmanager
def _page(project_dir, tmp_path):
    from playwright.sync_api import sync_playwright
    from export.HTML5.html5_exporter import HTML5Exporter

    out = tmp_path / "out"
    out.mkdir()
    assert HTML5Exporter().export(project_dir, out, {})
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out))
    handler.log_message = lambda *a, **k: None
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    name = next(out.glob("*.html")).name
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            pg = browser.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(f"http://127.0.0.1:{server.server_address[1]}/{name}")
            pg.wait_for_function("window.game && window.game.currentRoom "
                                 "&& window.game.currentRoom.raycastCamera", timeout=20000)
            pg.wait_for_timeout(300)
            yield pg
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()


def _stairs_project(tmp_path):
    from test_raycast_stairs_render import _write_project
    proj = tmp_path / "proj"
    proj.mkdir()
    _write_project(proj)
    return proj


@needs_browser
def test_layout_column_matches_python(tmp_path):
    from extensions.raycast_2_5d.renderer import layout_column
    rnd = random.Random(11)
    cases = []
    for _ in range(300):
        d, crossings = 0.3, []
        h0 = rnd.choice([0.0, 8.0, 16.0, 32.0])
        for _ in range(rnd.randrange(0, 7)):
            d += rnd.uniform(0.2, 2.5)
            crossings.append([d, rnd.choice([0.0, 8.0, 16.0, 24.0, 40.0, 68.0]),
                              rnd.randrange(2), rnd.random(), "%d,%d" % (rnd.randrange(9), 1)])
        is_hit = rnd.random() < 0.8
        hit = {"dist": (d + rnd.uniform(0.1, 3)) * 32, "side": rnd.randrange(2),
               "hit": is_hit, "texU": rnd.random(), "sprite": None}
        cases.append([crossings, hit, h0, h0 + 24, 96.0, 32, rnd.uniform(0.85, 1.0),
                      240, 480, 20])
    with _page(_stairs_project(tmp_path), tmp_path) as pg:
        js = pg.evaluate("""cases => cases.map(c => {
            const r = raycastLayoutColumn(...c);
            return {treads: r.treads, risers: r.risers, wall: r.wall,
                    occluders: r.occluders, wallDist: r.wallDist === Infinity ? null : r.wallDist};
        })""", cases)
    for case, got in zip(cases, js):
        crossings, hit = case[0], case[1]
        py = layout_column([tuple(c) for c in crossings],
                           (hit["dist"], hit["side"], hit["hit"], hit["texU"], None),
                           *case[2:])
        for key in ("treads", "risers", "occluders"):
            assert len(py[key]) == len(got[key]), (key, case)
            for a, b in zip(py[key], got[key]):
                for x, y in zip(a, b):
                    if isinstance(x, str) or x is None:
                        assert x == y, (key, case)
                    else:
                        assert x == pytest.approx(y, rel=1e-12, abs=1e-9), (key, case)
        assert (py["wall"] is None) == (got["wall"] is None)
        if py["wall"] is not None:
            assert list(py["wall"][:5]) == pytest.approx(got["wall"][:5], rel=1e-12, abs=1e-9)
        want = None if py["wall_dist"] == float("inf") else py["wall_dist"]
        assert (want is None and got["wallDist"] is None) or want == pytest.approx(got["wallDist"])


@needs_browser
def test_cast_ray_steps_matches_python(tmp_path):
    from runtime.game_runner import GameRoom
    from extensions.raycast_2_5d.renderer import cast_ray_steps
    from extensions.raycast_2_5d.state import raycast_state
    rnd = random.Random(5)
    v = {(rnd.randrange(1, 14), rnd.randrange(0, 15)) for _ in range(40)}
    h = {(rnd.randrange(0, 15), rnd.randrange(1, 14)) for _ in range(40)}
    heights = {(rnd.randrange(15), rnd.randrange(15)): rnd.choice([8.0, 16.0, 32.0])
               for _ in range(60)}
    rays = [(rnd.uniform(33, 447), rnd.uniform(33, 447), rnd.uniform(-math.pi, math.pi))
            for _ in range(300)]
    room = GameRoom.__new__(GameRoom)
    st = raycast_state(room)
    st.update(v_walls=v, h_walls=h, v_sprites={}, h_sprites={})
    with _page(_stairs_project(tmp_path), tmp_path) as pg:
        js = pg.evaluate("""([v, h, hs, rays]) => {
            const room = window.game.currentRoom;
            room._vWalls = new Set(v); room._hWalls = new Set(h);
            room._vWallSprites = new Map(); room._hWallSprites = new Map();
            const heights = new Map(hs);
            return rays.map(r => room.castRaySteps(r[0], r[1], r[2], 32, 20, heights));
        }""", [["%d,%d" % k for k in v], ["%d,%d" % k for k in h],
               [["%d,%d" % k, val] for k, val in heights.items()], rays])
    for (px, py, ang), got in zip(rays, js):
        crossings, hit = cast_ray_steps(room, px, py, ang, 32, 20, heights)
        assert len(crossings) == len(got["crossings"])
        for a, b in zip(crossings, got["crossings"]):
            assert list(a[:4]) == pytest.approx(b[:4], rel=1e-12, abs=1e-9)
            assert "%d,%d" % a[4] == b[4]
        assert hit[2] == got["hit"]["hit"] and hit[1] == got["hit"]["side"]
        assert hit[0] == pytest.approx(got["hit"]["dist"], rel=1e-12)
        assert hit[3] == pytest.approx(got["hit"]["texU"], abs=1e-9)


@needs_browser
def test_an_exported_staircase_renders_on_the_predicted_rows(tmp_path):
    """The same project as the desktop end-to-end test (S5): a riser 2.5
    cells ahead, flat red/green/blue. Its rows match the projection."""
    import base64
    import io
    from PIL import Image
    from extensions.raycast_2_5d.renderer import stairs_y
    with _page(_stairs_project(tmp_path), tmp_path) as pg:
        pg.wait_for_timeout(500)
        data = pg.evaluate("document.querySelector('canvas').toDataURL('image/png')")
    img = Image.open(io.BytesIO(base64.b64decode(data.split(",")[1]))).convert("RGB")
    col = [img.getpixel((240, y)) for y in range(480)]
    top, bot = stairs_y(8, 24, 80, 240, 480), stairs_y(0, 24, 80, 240, 480)

    def wallish(c):
        return c[0] > 0 and c[1] == 0 and c[2] == 0
    assert all(wallish(c) for c in col[math.ceil(top) + 1:math.floor(bot) - 1]), col[330:390]
    assert all(c == (0, 255, 0) for c in col[math.ceil(bot) + 2:])
    assert col[math.ceil(top) - 4] == (0, 255, 0)      # the step's top


def _climb_project(tmp_path, steps):
    from test_raycast_climbing import _write_project
    proj = tmp_path / "proj"
    proj.mkdir()
    _write_project(proj, steps)
    return proj


PERSON = ("window.game.currentRoom.instances.find("
          "i => (i.object_name || i.name) === 'obj_person')")


@needs_browser
def test_climbing_a_staircase_onto_a_platform_with_the_keyboard(tmp_path):
    steps = {(x, 7): 8.0 * (x - 2) for x in range(3, 7)}
    steps.update({(x, 7): 32.0 for x in range(7, 10)})
    with _page(_climb_project(tmp_path, steps), tmp_path) as pg:
        pg.evaluate("() => { window.__eyes = []; registerFrameUpdate("
                    "g => window.__eyes.push(g.currentRoom._raycastEyeFloor)); }")
        pg.keyboard.down("ArrowUp")
        pg.wait_for_timeout(2500)
        pg.keyboard.up("ArrowUp")
        res = pg.evaluate("() => { const p = " + PERSON + "; return {x: p.x, "
                          "z: p.raycast_floor_z, eyes: window.__eyes}; }")
    assert res["z"] == 32 and res["x"] > 7 * 32
    eyes = [e for e in res["eyes"] if isinstance(e, (int, float))]
    assert eyes[-1] == 32
    assert all(0 <= b - a <= 2.0 + 1e-9 for a, b in zip(eyes, eyes[1:]))


@needs_browser
def test_a_block_too_high_stops_the_player_in_the_browser(tmp_path):
    with _page(_climb_project(tmp_path, {(5, 7): 16.0}), tmp_path) as pg:
        pg.keyboard.down("ArrowUp")
        pg.wait_for_timeout(2000)
        res = pg.evaluate("() => { const p = " + PERSON + "; return {x: p.x, "
                          "z: p.raycast_floor_z, blocked: p.raycast_step_blocked}; }")
        pg.keyboard.up("ArrowUp")
    assert res["x"] + 16 < 5 * 32 and res["z"] == 0 and res["blocked"] == 1


@needs_browser
def test_the_minimap_s_raised_cells_match_python(tmp_path):
    from extensions.raycast_2_5d.hud import build_minimap_commands
    with _page(_stairs_project(tmp_path), tmp_path) as pg:
        js = pg.evaluate("""raised => {
            const room = window.game.currentRoom;
            const hud = room.instances[0];
            hud._draw_queue = [];
            room._vWalls = new Set(); room._hWalls = new Set();
            room._raycastFloorHeights = new Map(raised);
            _extActions['draw_minimap'](hud, {x: 0, y: 0, size: 100,
                back_color: '#000000', wall_color: '#c8c8c8'}, window.game);
            return hud._draw_queue;
        }""", [["5,%d" % r, 8.0 * (r - 4)] for r in range(5, 10)])
    raised = {(5, r): 8.0 * (r - 4) for r in range(5, 10)}    # 8 .. 40: five shades
    py = build_minimap_commands(set(), set(), 32, 480, 480, None, None, 0.0, 0, 0, 100,
                                "#000000", "#c8c8c8", "#ffd040", raised=raised)
    py_rects, js_rects = py[1:6], js[1:6]
    assert len({r["color"] for r in py_rects}) == 5
    for a, b in zip(py_rects, js_rects):
        assert a["color"] == b["color"]
        for k in ("x1", "y1", "x2", "y2"):
            assert a[k] == pytest.approx(b[k])
