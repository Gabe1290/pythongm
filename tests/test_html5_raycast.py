"""HTML5 export — raycast (Doom-style first-person) view, parity unit 2 (walls).

engine.js gained a port of the desktop raycast renderer's WALL pass: facing_angle
+ set_facing_angle, the enable_raycast_view action, wall-edge derivation
(buildRaycastWalls), the DDA (castRay), and a textured/flat wall-strip render
(renderRaycastView), hooked into GameRoom.render as an early return. Sky, floor
casting and billboards are the next unit.

Source-level assertions (there's no JS engine / Playwright in CI — same as
tests/test_html5_views.py; the behavioural proof is a browser run during
development). The DDA is ported faithfully from runtime/game_runner._cast_ray so
tests/test_raycast_export_parity.py can cross-check it against the desktop copy.
"""
import base64
import gzip
import json
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def test_facing_angle_property_and_action():
    assert "this.facing_angle = 0;" in ENGINE
    assert "case 'set_facing_angle'" in ENGINE
    # set_direction_speed(direction="facing_angle") must resolve — parseNumParam
    # exposes facing_angle as a bare variable
    assert "replace(/facing_angle/g" in ENGINE


def test_enable_raycast_view_action_builds_camera():
    assert "case 'enable_raycast_view'" in ENGINE
    assert "game.currentRoom.raycastCamera = {" in ENGINE
    # the camera carries the same fields the desktop handler sets
    for field in ("camera_object", "fov", "render_distance", "cell_size",
                  "columns", "wall_color", "wall_texture", "sky_texture",
                  "floor_texture", "wall_textured", "floor_cast_res"):
        assert field in ENGINE, field


def test_render_has_raycast_early_return():
    m = re.search(r"    render\(ctx\)\s*\{(.*?)\n        // Fill the whole canvas",
                  ENGINE, re.S)
    assert m, "GameRoom.render not found in expected shape"
    body = m.group(1)
    assert "this.raycastCamera && this.raycastCamera.enabled" in body
    assert "this.renderRaycastView(ctx)" in body


def test_dda_ported_faithfully():
    """castRay mirrors the desktop _cast_ray — the load-bearing math."""
    m = re.search(r"castRay\(px, py, angleRad, cellSize, maxCells\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "castRay not found"
    body = m.group(1)
    # DDA setup + step + the hit/tex_u return
    assert "Math.abs(1 / dx)" in body and "Math.abs(1 / dy)" in body
    assert "sideX < sideY" in body
    assert "this._vWalls.has(key)" in body and "this._hWalls.has(key)" in body
    assert "hit: true" in body and "texU" in body
    # miss path returns hit:false (no phantom wall strip)
    assert "hit: false" in body


def test_wall_render_samples_texture_strip():
    m = re.search(r"renderRaycastView\(ctx\)\s*\{(.*?)\n    \}", ENGINE, re.S)
    assert m, "renderRaycastView not found"
    body = m.group(1)
    assert "buildRaycastWalls(cellSize)" in body
    assert "Math.cos(rayOffset)" in body          # fisheye correction
    assert "h * cellSize / Math.max(corrected" in body
    # 1px source-column drawImage scaled to the strip (Canvas equiv of pygame
    # subsurface+scale)
    assert "ctx.drawImage(texSprite, texX, 0, 1, th, x0, y0, stripW, stripH)" in body
    assert "if (!r.hit) continue" in body         # miss columns draw no wall
    assert "r.side === 1" in body                 # y-face depth cue


def test_build_walls_derives_edges_with_sprites():
    m = re.search(r"buildRaycastWalls\(cellSize\)\s*\{(.*?)\n    \}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "width >= height * 1.5" in body        # wide -> horizontal segment
    assert "height >= width * 1.5" in body        # tall -> vertical segment
    assert "_vWallSprites" in body and "_hWallSprites" in body


def test_raycast_1_exports_with_camera_and_textures():
    """The real sample exports to a valid HTML whose embedded data carries the
    enable_raycast_view action and its texture sprites."""
    from export.HTML5.html5_exporter import HTML5Exporter
    src = REPO_ROOT / "samples" / "raycast_1"
    out = Path(tempfile.mkdtemp(prefix="raycast_html5_")) / "out"
    out.mkdir(parents=True)
    assert HTML5Exporter().export(src, out)
    html = next(out.glob("*.html")).read_text(encoding="utf-8")
    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    assert m
    data = json.loads(gzip.decompress(base64.b64decode(m.group(1))))
    # the create event carries enable_raycast_view with the texture params
    objs = data["assets"]["objects"]
    person = objs.get("obj_person", {})
    blob = json.dumps(person)
    assert "enable_raycast_view" in blob
    assert "spr_wall_texture" in blob
    # the wall texture sprite made it into the export
    assert "spr_wall_texture" in data["assets"]["sprites"]
