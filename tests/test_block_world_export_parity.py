"""Block World DDA/shading parity across the desktop and Kivy renderer
copies (Phase 6 Unit 10 of docs/VOXEL_WORLD_PLAN.md).

Mirrors tests/test_raycast_export_parity.py's own two-tier approach:

- **Desktop <-> Kivy: exact numeric equality.** Both are runnable Python, so
  the same world is fed to each and march_ray/pick_voxel are asserted to
  return identical results across a dense ray matrix -- the ports were
  transcribed line-for-line and must stay so.
- **HTML5: structural equivalence + shared shading constants.** No JS
  engine/Playwright in this environment (same standing limitation as the
  raycast HTML5 port), so bwMarchRay can't be executed here; instead its
  body is checked for the same load-bearing DDA statements, and the shading
  constants are compared as literal numbers extracted from the source.
"""
import math
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import

from extensions.block_world.renderer import (  # noqa: E402
    march_ray, pick_voxel, wall_shade, face_shade,
    SIDE_SHADE, FOG_STRENGTH, MIN_SHADE, TOP_SHADE, BOTTOM_SHADE,
    DEFAULT_EYE_HEIGHT, MAX_PITCH_DEGREES,
)

from test_kivy_block_world import (  # noqa: E402
    _stub_kivy_env, _scene_class, _blank_scene, _export_block_world_1,
)

EXPORT_HTML5 = (REPO_ROOT / "extensions" / "block_world" / "export_html5.js").read_text(
    encoding="utf-8")


class _DesktopRoom:
    """A bare state bag matching what march_ray/pick_voxel read off `room`
    via extension_state -- mirrors GameRoom.__new__'s role in the raycast
    parity test, without needing a real GameRoom."""
    def __init__(self, blocks):
        self.extension_state = {"block_world": {"blocks": blocks, "camera": {}, "_columns": None}}


def _shared_world():
    """A representative sparse world: a 4x4 floor at z=0, a single-block
    step at (2,2,1), and a taller 2-block obstacle at (5,5,{0,1}) -- enough
    structure to exercise stacking, gaps, and multi-layer hits."""
    blocks = {}
    for x in range(4):
        for y in range(4):
            blocks[f"{x},{y},0"] = "stone"
    blocks["2,2,1"] = "cobble"
    blocks["5,5,0"] = "stone"
    blocks["5,5,1"] = "stone"
    return blocks


def test_desktop_and_kivy_march_ray_are_numerically_identical():
    game = _export_block_world_1()
    blocks = _shared_world()
    cell_size = 32
    max_cells = 20
    origins = [(1.5, 1.5), (0.5, 3.5), (2.2, 2.7), (5.9, 5.1), (3.0, 0.5)]
    angles = [math.radians(a) for a in range(0, 360, 9)]

    desktop_room = _DesktopRoom(blocks)

    with _stub_kivy_env(game):
        cls = _scene_class(game)
        scene = _blank_scene(cls)
        scene._bw_blocks = {tuple(int(p) for p in k.split(",")): v
                            for k, v in blocks.items()}

        checked = 0
        for (ox, oy) in origins:
            px, py = ox * cell_size, oy * cell_size
            for ang in angles:
                d_hits = list(march_ray(desktop_room, px, py, ang, cell_size, max_cells))
                k_hits = list(scene._bw_march_ray(px, py, ang, cell_size, max_cells))
                assert len(d_hits) == len(k_hits), (ox, oy, ang)
                for d, k in zip(d_hits, k_hits):
                    # desktop: (map_x, map_y, entry, exit, side, tex_u);
                    # kivy: (map_x, map_y, entry, exit, side) -- no tex_u
                    # (this port never texture-maps).
                    assert d[0] == k[0] and d[1] == k[1], (ox, oy, ang, "cell")
                    assert abs(d[2] - k[2]) < 1e-9, (ox, oy, ang, "entry")
                    assert abs(d[3] - k[3]) < 1e-9, (ox, oy, ang, "exit")
                    assert d[4] == k[4], (ox, oy, ang, "side")
                checked += 1
        assert checked == len(origins) * len(angles)


def test_desktop_and_kivy_pick_voxel_are_numerically_identical():
    game = _export_block_world_1()
    blocks = _shared_world()
    cell_size = 32
    desktop_room = _DesktopRoom(blocks)

    with _stub_kivy_env(game):
        cls = _scene_class(game)
        scene = _blank_scene(cls)
        scene._bw_blocks = {tuple(int(p) for p in k.split(",")): v
                            for k, v in blocks.items()}

        cases = [
            (48.0, 48.0, 1.5, 0.0, 0.0, 10),      # level ray, east
            (48.0, 48.0, 1.5, math.radians(45), 0.0, 10),
            (176.0, 176.0, 1.5, math.pi, -0.2, 10),  # looking down near the tall obstacle
            (16.0, 16.0, 0.5, math.radians(90), 0.3, 8),
        ]
        for cam_x, cam_y, eye_z, angle_rad, z_per_px, reach in cases:
            d_target, d_placement = pick_voxel(
                desktop_room, cam_x, cam_y, eye_z, angle_rad, z_per_px, cell_size, reach)
            k_target, k_placement = scene._bw_pick_voxel(
                cam_x, cam_y, eye_z, angle_rad, z_per_px, cell_size, reach)
            assert d_target == k_target, (cam_x, cam_y, angle_rad, z_per_px)
            assert d_placement == k_placement, (cam_x, cam_y, angle_rad, z_per_px)


def test_wall_and_face_shade_match_across_desktop_and_kivy():
    game = _export_block_world_1()
    with _stub_kivy_env(game):
        cls = _scene_class(game)
        scene = _blank_scene(cls)
        cases = [(0, 10.0, 320.0), (1, 10.0, 320.0), (0, 300.0, 320.0), (1, 0.0, 320.0)]
        for side, corrected, max_dist in cases:
            assert abs(wall_shade(side, corrected, max_dist)
                      - scene._bw_wall_shade(side, corrected, max_dist)) < 1e-12
        face_cases = [(10.0, 320.0, TOP_SHADE), (300.0, 320.0, BOTTOM_SHADE)]
        for corrected, max_dist, facing in face_cases:
            assert abs(face_shade(corrected, max_dist, facing)
                      - scene._bw_face_shade(corrected, max_dist, facing)) < 1e-12


def test_kivy_shading_constants_match_desktop():
    game = _export_block_world_1()
    with _stub_kivy_env(game):
        cls = _scene_class(game)
        assert cls.BW_SIDE_SHADE == SIDE_SHADE
        assert cls.BW_FOG_STRENGTH == FOG_STRENGTH
        assert cls.BW_MIN_SHADE == MIN_SHADE
        assert cls.BW_TOP_SHADE == TOP_SHADE
        assert cls.BW_BOTTOM_SHADE == BOTTOM_SHADE
        assert cls.BW_DEFAULT_EYE_HEIGHT == DEFAULT_EYE_HEIGHT
        assert cls.BW_MAX_PITCH_DEGREES == MAX_PITCH_DEGREES


# --- HTML5: structural + constant parity (no JS engine here) -----------------

def _js_march_ray_body():
    m = re.search(r"function\* bwMarchRay\([^)]*\)\s*\{(.*?)\n\}", EXPORT_HTML5, re.S)
    assert m, "bwMarchRay not found"
    return m.group(1)


def test_html5_march_ray_mirrors_desktop_dda():
    body = _js_march_ray_body()
    assert "Math.abs(1 / dx)" in body and "Math.abs(1 / dy)" in body
    assert "sideX < sideY" in body
    assert "mapX += stepX" in body and "mapY += stepY" in body


def test_html5_shading_constants_match_desktop():
    checks = {
        "BW_SIDE_SHADE": SIDE_SHADE, "BW_FOG_STRENGTH": FOG_STRENGTH,
        "BW_MIN_SHADE": MIN_SHADE, "BW_TOP_SHADE": TOP_SHADE,
        "BW_BOTTOM_SHADE": BOTTOM_SHADE, "BW_DEFAULT_EYE_HEIGHT": DEFAULT_EYE_HEIGHT,
        "BW_MAX_PITCH_DEGREES": MAX_PITCH_DEGREES,
    }
    for name, value in checks.items():
        m = re.search(rf"const {name} = ([0-9.]+);", EXPORT_HTML5)
        assert m, name
        assert float(m.group(1)) == value, name
