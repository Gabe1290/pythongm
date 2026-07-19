"""Raycast DDA parity across the three renderer copies (parity unit 6).

The raycast view is implemented THREE times with no shared code — desktop
Python (runtime/game_runner._cast_ray), the HTML5 engine (engine.js castRay),
and the Kivy generated scene (_cast_ray). This guards the load-bearing core,
the DDA, against drift between them.

- **Desktop <-> Kivy: exact numeric equality.** Both are runnable Python, so we
  feed IDENTICAL derived wall edges to each and assert _cast_ray returns the
  same (distance, side, hit, tex_u) across a dense ray matrix. This is the
  strong guarantee — the ports were transcribed line-for-line and must stay so.
- **HTML5: structural equivalence.** There's no JS engine / Playwright in this
  environment (same constraint as tests/test_html5_views.py), so the JS castRay
  can't be executed here. Instead we assert its body carries the exact same
  load-bearing DDA statements as the desktop source — the arithmetic that would
  make it diverge if edited. A browser run during development is the behavioural
  proof (see docs/RAYCAST_2_5D_PLAN.md).
"""
import math
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import

from runtime.game_runner import GameRoom  # noqa: E402

# Reuse the stub-kivy harness + raycast_1 export from the Kivy raycast tests.
from test_kivy_raycast import (  # noqa: E402
    _stub_kivy_env, _scene_class, _blank_scene, _export_raycast_1,
)

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(
    encoding="utf-8")


def _shared_walls():
    """A representative 6x6 map: a solid border ring plus two interior
    edges, expressed directly as (line_x, row) / (col, line_y) edge sets —
    the exact shape _build_raycast_walls produces on either target."""
    v_walls, h_walls = set(), set()
    n = 6
    for r in range(n):
        v_walls.add((0, r))          # west border (vertical line x=0)
        v_walls.add((n, r))          # east border (vertical line x=n)
    for c in range(n):
        h_walls.add((c, 0))          # south border
        h_walls.add((c, n))          # north border
    # Interior: a vertical wall segment at x=3 spanning rows 1..2, and a
    # horizontal one at y=4 spanning cols 2..4.
    v_walls.add((3, 1))
    v_walls.add((3, 2))
    h_walls.add((2, 4))
    h_walls.add((3, 4))
    h_walls.add((4, 4))
    return v_walls, h_walls


def _desktop_engine():
    room = GameRoom.__new__(GameRoom)
    v, h = _shared_walls()
    room._raycast_v_walls = v
    room._raycast_h_walls = h
    room._raycast_v_wall_sprites = {}
    room._raycast_h_wall_sprites = {}
    return room


def _kivy_engine(game_dir):
    cls = _scene_class(game_dir)
    scene = _blank_scene(cls)
    v, h = _shared_walls()
    scene._raycast_v_walls = v
    scene._raycast_h_walls = h
    scene._raycast_v_wall_sprites = {}
    scene._raycast_h_wall_sprites = {}
    return scene


def test_desktop_and_kivy_cast_ray_are_numerically_identical():
    game = _export_raycast_1()
    cell_size = 32
    max_cells = 20
    # Ray matrix: several interior origins x a full 360deg angle sweep.
    origins = [(3.5, 3.5), (1.5, 1.5), (4.2, 2.7), (2.0, 4.9), (5.5, 0.5)]
    angles = [math.radians(a) for a in range(0, 360, 7)]

    desktop = _desktop_engine()
    with _stub_kivy_env(game):
        kivy = _kivy_engine(game)
        checked = 0
        for (ox, oy) in origins:
            px, py = ox * cell_size, oy * cell_size
            for ang in angles:
                d = desktop._cast_ray(px, py, ang, cell_size, max_cells)
                k = kivy._cast_ray(px, py, ang, cell_size, max_cells)
                # Compare (distance, side, hit, tex_u) — the 5th return
                # (sprite) is an engine-specific object vs a name, by design.
                assert d[1] == k[1], (ox, oy, ang, "side")
                assert d[2] == k[2], (ox, oy, ang, "hit")
                assert abs(d[0] - k[0]) < 1e-9, (ox, oy, ang, "dist", d[0], k[0])
                assert abs(d[3] - k[3]) < 1e-9, (ox, oy, ang, "tex_u")
                checked += 1
        # A wall must actually be hit somewhere, else we'd be comparing all
        # misses and proving nothing.
        assert checked == len(origins) * len(angles)
        hits = sum(1 for ang in angles
                   for (ox, oy) in origins
                   if desktop._cast_ray(ox * cell_size, oy * cell_size, ang,
                                        cell_size, max_cells)[2])
        assert hits > 0


def _castray_body():
    m = re.search(r"castRay\(px, py, angleRad, cellSize, maxCells\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "engine.js castRay not found"
    return m.group(1)


def test_html5_cast_ray_mirrors_desktop_dda():
    """The JS castRay carries the same load-bearing DDA arithmetic as the
    desktop _cast_ray (can't execute JS here — structural parity only)."""
    body = _castray_body()
    # DDA delta setup
    assert "Math.abs(1 / dx)" in body and "Math.abs(1 / dy)" in body
    # side-distance step + the vertical/horizontal branch selection
    assert "sideX < sideY" in body
    # wall-edge membership on the SAME keyed sets both other targets use
    assert "this._vWalls.has(key)" in body
    assert "this._hWalls.has(key)" in body
    # line-index naming identical to the desktop (map_x if step>0 else map_x+1)
    assert re.search(r"step[XY]\s*>\s*0", body)
    # fractional tex-U via floor, and the hit/miss returns
    assert "Math.floor(wallCoord)" in body
    assert "hit: true" in body and "hit: false" in body


def test_wall_shade_model_matches_desktop_and_kivy():
    """The wall-shading model (subtle side hint + distance falloff) must be
    numerically identical on desktop and Kivy. It replaced a binary
    half-brightness y-face that made h/v junctions at equal distance read as
    false corners (user report 2026-07-19)."""
    game = _export_raycast_1()
    with _stub_kivy_env(game):
        cls = _scene_class(game)
        for side in (0, 1):
            for corrected in (0.0, 8.0, 64.0, 320.0, 640.0, 5000.0):
                d = GameRoom._wall_shade(side, corrected, 640.0)
                k = cls._wall_shade(side, corrected, 640.0)
                assert abs(d - k) < 1e-12, (side, corrected, d, k)
        # constants agree too
        assert GameRoom.RAYCAST_SIDE_SHADE == cls.RAYCAST_SIDE_SHADE
        assert GameRoom.RAYCAST_FOG_STRENGTH == cls.RAYCAST_FOG_STRENGTH
        assert GameRoom.RAYCAST_MIN_SHADE == cls.RAYCAST_MIN_SHADE


def test_wall_shade_behaviour():
    """Sanity on the model itself: a y-face is only slightly darker than an
    x-face (no 2:1 break), and distance darkens both, floored at MIN_SHADE."""
    M = 640.0
    near0 = GameRoom._wall_shade(0, 0.0, M)
    near1 = GameRoom._wall_shade(1, 0.0, M)
    far0 = GameRoom._wall_shade(0, M, M)
    assert near0 == 1.0
    assert 0.8 < near1 < 1.0, "side hint must be subtle, not the old 0.5"
    assert far0 < near0, "distance must darken"
    assert GameRoom._wall_shade(1, 10 * M, M) >= GameRoom.RAYCAST_MIN_SHADE


def test_html5_wall_shade_mirrors_the_same_constants():
    """No JS engine in CI — pin engine.js's constants + formula structurally."""
    assert "const RAYCAST_SIDE_SHADE = 0.85" in ENGINE
    assert "const RAYCAST_FOG_STRENGTH = 0.55" in ENGINE
    assert "const RAYCAST_MIN_SHADE = 0.35" in ENGINE
    m = re.search(r"wallShade\(side, corrected, maxDist\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "engine.js wallShade not found"
    body = m.group(1)
    assert "RAYCAST_SIDE_SHADE : 1.0" in body
    assert "1.0 - RAYCAST_FOG_STRENGTH * t" in body
    assert "Math.max(RAYCAST_MIN_SHADE" in body
    # the old binary half-shade overlay must be gone
    assert "rgba(0,0,0,0.5)" not in ENGINE


def test_all_three_share_the_facing_angle_convention():
    """Turning maps to screen-space radians the same way on every target:
    -facing_angle (GM 0=right/90=up -> y-down screen)."""
    # Desktop + Kivy: radians(-camera.facing_angle)
    gr = (REPO_ROOT / "runtime" / "game_runner.py").read_text(encoding="utf-8")
    assert "math.radians(-camera.facing_angle)" in gr
    kx = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
    assert "math.radians(-float(getattr(camera, 'facing_angle', 0)))" in kx
    # HTML5: (-facing_angle) in radians
    assert re.search(r"-\s*camera\.facing_angle\s*\*\s*Math\.PI\s*/\s*180", ENGINE) \
        or "-camera.facing_angle * Math.PI / 180" in ENGINE
