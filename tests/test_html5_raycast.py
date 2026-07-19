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
    # depth cue is now the shared shading model (subtle side hint + distance
    # falloff), not the old binary `r.side === 1` half-brightness overlay
    assert "this.wallShade(r.side, corrected, renderDist * cellSize)" in body


def test_sky_panorama_pans_over_ceiling():
    m = re.search(r"renderRaycastView\(ctx\)\s*\{(.*?)\n    \}", ENGINE, re.S)
    body = m.group(1)
    assert "cfg.sky_texture ? sprites[cfg.sky_texture]" in body
    # pano width = w*360/fov, panned by facing_angle, wrap copy
    assert "w * 360 / Math.max(1, cfg.fov" in body
    assert "camera.facing_angle % 360" in body
    assert "panoW - pan < w" in body


def test_billboards_with_per_column_occlusion():
    m = re.search(r"renderRaycastView\(ctx\)\s*\{(.*?)\n    \}", ENGINE, re.S)
    body = m.group(1)
    # only non-solid visible sprited instances, farthest-first
    assert "!inst.visible || !inst.sprite || inst.solid" in body
    assert "billboards.sort((a, b) => b.corr - a.corr)" in body
    # per-column occlusion against the wall distances the wall pass recorded
    assert "const colWallDist = new Array(numCols).fill(Infinity)" in body
    assert "colWallDist[col] = corrected" in body
    assert "b.corr < colWallDist[colIdx]" in body


def test_build_walls_derives_edges_with_sprites():
    m = re.search(r"buildRaycastWalls\(cellSize\)\s*\{(.*?)\n    \}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "width >= height * 1.5" in body        # wide -> horizontal segment
    assert "height >= width * 1.5" in body        # tall -> vertical segment
    assert "_vWallSprites" in body and "_hWallSprites" in body


def test_floor_casting_pass_invoked_before_walls():
    """renderRaycastView casts the textured floor (and, sans sky, ceiling)
    between the sky pass and the wall loop — matching the desktop order."""
    m = re.search(r"renderRaycastView\(ctx\)\s*\{(.*?)\n    \}", ENGINE, re.S)
    body = m.group(1)
    # res from cfg.floor_cast_res, texture resolved to ImageData, camera in cells
    assert "cfg.floor_cast_res || 4" in body
    assert "this._textureData(sprites[cfg.floor_texture])" in body
    assert "const camCx = camX / cellSize, camCy = camY / cellSize" in body
    assert "this.castFloorPlane(ctx, floorTex" in body
    # ceiling only when no sky claimed it
    assert "cfg.ceiling_texture && !skyTex" in body
    # the floor pass must precede the wall loop (so walls occlude it)
    assert body.index("castFloorPlane(ctx, floorTex") < body.index("colWallDist[col] = corrected")


def test_cast_floor_plane_mirrors_desktop():
    """castFloorPlane ports _cast_floor_plane's camera-plane cast faithfully."""
    m = re.search(r"castFloorPlane\(ctx, texData, camCx, camCy, facingScreenRad, fovRad, res, ceiling\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "castFloorPlane not found"
    body = m.group(1)
    # row distance from the same projection the walls use
    assert "const posZ = 0.5 * h" in body
    assert "const rowd = posZ / p" in body
    # the two FOV-edge rays interpolated across columns (camera-plane method)
    assert "const rdx0 = dirX - planeX" in body and "const rdx1 = dirX + planeX" in body
    # low-res ImageData fill + upscale
    assert "sctx.createImageData(sw, sh)" in body
    assert "ctx.drawImage(small, 0, 0, sw, sh, 0, halfH, w, regionH)" in body
    # ceiling variant flips vertically
    assert "ctx.scale(1, -1)" in body


def test_texture_data_helper_caches_and_guards_taint():
    m = re.search(r"_textureData\(sprite\)\s*\{(.*?)\n    \}", ENGINE, re.S)
    assert m, "_textureData not found"
    body = m.group(1)
    assert "getImageData(0, 0, sprite.width, sprite.height)" in body
    assert "this._texDataCache" in body            # cached per sprite
    assert "catch" in body                          # tainted-canvas fallback -> null


def test_raycast_1_export_includes_floor_texture():
    """The floor sprite referenced by enable_raycast_view ships in the export."""
    from export.HTML5.html5_exporter import HTML5Exporter
    src = REPO_ROOT / "samples" / "raycast_1"
    out = Path(tempfile.mkdtemp(prefix="raycast_html5_floor_")) / "out"
    out.mkdir(parents=True)
    assert HTML5Exporter().export(src, out)
    html = next(out.glob("*.html")).read_text(encoding="utf-8")
    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    data = json.loads(gzip.decompress(base64.b64decode(m.group(1))))
    person = json.dumps(data["assets"]["objects"].get("obj_person", {}))
    assert "spr_floor" in person                    # floor_texture param
    assert "spr_floor" in data["assets"]["sprites"]  # the sprite itself


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
