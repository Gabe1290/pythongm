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

# The raycast renderer moved into the raycast_2_5d extension (Stage C); the
# exporter concatenates its export_html5.js at engine.js's marker, so the shipped
# engine JS is the two together. ENGINE_CORE / RAYCAST_JS keep them separable for
# the structural tests that assert WHERE a hook lives.
ENGINE_CORE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
RAYCAST_JS = (REPO_ROOT / "extensions" / "raycast_2_5d" / "export_html5.js").read_text(encoding="utf-8")
ENGINE = ENGINE_CORE + "\n" + RAYCAST_JS


def test_facing_angle_property_and_action():
    # facing_angle stays a core instance property (init in engine.js); the
    # set_facing_angle ACTION is a registered extension action now (Stage C1c).
    assert "this.facing_angle = 0;" in ENGINE_CORE
    assert "registerExtensionAction('set_facing_angle'" in RAYCAST_JS
    # set_direction_speed(direction="facing_angle") must resolve — parseNumParam
    # exposes facing_angle as a bare variable (stays in engine.js)
    assert "replace(/facing_angle/g" in ENGINE_CORE


def test_enable_raycast_view_action_builds_camera():
    assert "registerExtensionAction('enable_raycast_view'" in ENGINE   # Stage C1c
    assert "game.currentRoom.raycastCamera = {" in ENGINE
    # the camera carries the same fields the desktop handler sets
    for field in ("camera_object", "fov", "render_distance", "cell_size",
                  "columns", "wall_color", "wall_texture", "sky_texture",
                  "floor_texture", "wall_textured", "floor_cast_res"):
        assert field in ENGINE, field


def test_render_gives_extensions_first_refusal():
    """GameRoom.render hands each room to the generic extension hook first (Stage
    C); a claim composites the HUD and returns. The raycast dispatch used to be
    inline here — it's now the raycast_2_5d extension's registered renderer."""
    m = re.search(r"    render\(ctx\)\s*\{(.*?)\n        // Fill the whole canvas",
                  ENGINE_CORE, re.S)
    assert m, "GameRoom.render not found in expected shape"
    body = m.group(1)
    assert "renderExtensionRoom(this, ctx)" in body
    assert "raycastCamera" not in body, "raycast dispatch should have moved out of core"
    # the raycast renderer is registered by the extension and calls renderRaycastView
    assert "registerRoomRenderer(function(room, ctx)" in RAYCAST_JS
    assert "room.renderRaycastView(ctx)" in RAYCAST_JS


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
    # viewH (letterbox height, == h until a viewport_height is set), DOOM HUD Unit 2
    assert "viewH * cellSize * RAYCAST_WALL_HEIGHT / Math.max(corrected" in body
    # 1px source-column drawImage scaled to the strip (Canvas equiv of pygame
    # subsurface+scale)
    # the texture is CROPPED to the visible span (srcY/srcH), not the whole
    # column squeezed into a screen-clamped strip
    assert "ctx.drawImage(texSprite, texX, srcY, 1, srcH, x0, y0, stripW, visH)" in body
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
    m = re.search(r"castFloorPlane\(ctx, texData, camCx, camCy, facingScreenRad, fovRad, res, ceiling, viewH\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "castFloorPlane not found"
    body = m.group(1)
    # row distance from the same projection the walls use (viewH: DOOM HUD Unit 2)
    assert "const posZ = 0.5 * viewH" in body
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


# --- In-view HUD compositing (RAYCAST_HUD_PLAN Unit 2) ----------------------
# Before this, GameRoom.render did `renderRaycastView(ctx); return;`, so the
# per-instance draw pass never ran under raycast and a raycast game's HUD
# (draw_score / draw_lives / draw_text / draw_health_bar) was invisible in the
# browser. Source-level assertions only — no JS engine in CI.

def _extension_render_hook() -> str:
    """The body of GameRoom.render's generic extension hook (Stage C) — a claim
    composites the HUD/draw-event pass and returns. Raycast rendering itself is
    now the raycast_2_5d extension's registered renderer (export_html5.js)."""
    start = ENGINE_CORE.index("if (renderExtensionRoom(this, ctx)) {")
    end = ENGINE_CORE.index("return;", start) + len("return;")
    return ENGINE_CORE[start:end]


def test_run_draw_event_is_split_out_of_on_draw():
    """The draw-queue pass is reusable without also drawing the sprite."""
    assert "runDrawEvent(ctx) {" in ENGINE
    # onDraw keeps its sprite-then-queue order by delegating.
    on_draw = ENGINE[ENGINE.index("onDraw(ctx) {"):]
    on_draw = on_draw[:on_draw.index("runDrawEvent(ctx) {")]
    assert "this.render(ctx);" in on_draw
    assert "this.runDrawEvent(ctx);" in on_draw
    # The queue machinery moved wholesale, not duplicated.
    assert on_draw.count("this._draw_queue = []") == 0
    assert ENGINE.count("runDrawEvent(ctx) {") == 1


def test_hud_pass_runs_after_an_extension_render_and_before_the_return():
    hook = _extension_render_hook()
    assert "runDrawEvent(ctx)" in hook, \
        "extension render hook returns without compositing the HUD"
    assert hook.index("runDrawEvent(ctx)") < hook.index("return;"), \
        "HUD must composite over the finished frame"
    # the raycast renderer paints the frame the HUD composites over
    assert "room.renderRaycastView(ctx)" in RAYCAST_JS


def test_hud_pass_uses_gamemaker_depth_order():
    """Descending — higher depth drawn first, so lower depth ends in front.
    The extension render hook must agree with the normal path AND the desktop
    runtime's `reverse=True` sort."""
    hook = _extension_render_hook()
    assert "sort((a, b) => b.depth - a.depth)" in hook
    normal = ENGINE_CORE[ENGINE_CORE.index("const sortedInstances = "):]
    assert "sort((a, b) => b.depth - a.depth)" in normal[:200]
    assert "a.depth - b.depth" not in ENGINE, \
        "an ascending depth sort is back — it inverts sprite z-order"


def test_invisible_instances_do_not_run_their_draw_event():
    """GameMaker semantics, matching the desktop runtime's early return on
    `not self.visible`. Regression guard: engine.js used to run the draw event
    for invisible instances, skipping only the sprite."""
    run_draw = ENGINE[ENGINE.index("runDrawEvent(ctx) {"):]
    run_draw = run_draw[:run_draw.index("\n    }")]
    assert "if (!this.visible) return;" in run_draw
    # ...and it must come before the draw event is executed.
    assert run_draw.index("if (!this.visible) return;") < run_draw.index("executeActions")


# --- viewport_height letterbox (DOOM HUD Unit 2) ---------------------------
# Mirrors the desktop change: the 3D view shrinks into the top viewH px so a
# DOOM-style status bar can occupy the band below. No JS engine in CI, so these
# are source-level (the behavioural proof is desktop's real-loop test plus a
# dev browser run); the DDA parity is locked separately.

def test_html5_render_derives_viewH_and_clamps_it():
    rv = ENGINE[ENGINE.index("renderRaycastView(ctx) {"):]
    rv = rv[:rv.index("\n    castFloorPlane")]
    assert "let viewH = cfg.viewport_height || h;" in rv
    assert "viewH = Math.max(1, Math.min(viewH, h));" in rv


def test_html5_vertical_math_uses_viewH_not_h():
    rv = ENGINE[ENGINE.index("renderRaycastView(ctx) {"):]
    rv = rv[:rv.index("\n    castFloorPlane")]
    # Horizon, fills, wall + billboard scale all key off viewH now.
    assert "const halfH = Math.floor(viewH / 2);" in rv
    assert "ctx.fillRect(0, halfH, w, viewH - halfH);" in rv
    assert "const fullH = viewH * cellSize * RAYCAST_WALL_HEIGHT / Math.max(corrected, 1e-4);" in rv
    assert "const fullH = viewH * b.inst.boxHeight() / Math.max(b.corr, 1e-4);" in rv
    assert "Math.floor(viewH * b.inst.boxWidth()" in rv
    # width is NEVER shrunk — strictly a vertical letterbox.
    assert "const colWidth = w / numCols;" in rv


def test_html5_reserved_band_is_filled_black():
    rv = ENGINE[ENGINE.index("renderRaycastView(ctx) {"):]
    rv = rv[:rv.index("\n    castFloorPlane")]
    # Once in the no-camera early return, once after the passes.
    assert rv.count("ctx.fillRect(0, viewH, w, h - viewH);") == 2
    assert "if (viewH < h)" in rv


def test_html5_floor_cast_receives_viewH():
    rv = ENGINE[ENGINE.index("renderRaycastView(ctx) {"):]
    rv = rv[:rv.index("\n    castFloorPlane")]
    assert "castFloorPlane(ctx, floorTex, camCx, camCy, facingScreenRad, fovRad, castRes, false, viewH)" in rv
    cf = ENGINE[ENGINE.index("castFloorPlane(ctx, texData"):]
    cf = cf[:cf.index("\n    render(ctx)")] if "\n    render(ctx)" in cf else cf[:4000]
    assert "res, ceiling, viewH) {" in cf
    assert "const posZ = 0.5 * viewH;" in cf
    assert "const regionH = viewH - halfH;" in cf
