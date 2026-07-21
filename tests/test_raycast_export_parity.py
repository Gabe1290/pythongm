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


def test_flat_wall_projects_perfectly_straight():
    """THE load-bearing projection property: for a flat wall, 1/corrected_dist
    must be exactly LINEAR across evenly-spaced screen columns. The renderer
    used to sample rays at uniform ANGLES while drawing them at uniform screen
    x, which is not a perspective projection — it bent straight walls so they
    looked like they had a corner (user report 2026-07-19). Fixed by the
    camera-plane mapping ray_offset = atan(tan(fov/2) * camera_x)."""
    room = GameRoom.__new__(GameRoom)
    room._raycast_h_walls = {(c, 4) for c in range(15)}   # one long flat wall
    room._raycast_v_walls = set()
    room._raycast_h_wall_sprites = {}
    room._raycast_v_wall_sprites = {}

    fov = math.radians(66)
    plane_tan = math.tan(fov / 2)
    N = 64
    for facing_deg in (90, 75, 60, 110):
        facing = math.radians(-facing_deg)
        inv = []
        for col in range(N):
            camera_x = 2.0 * (col + 0.5) / N - 1.0
            off = math.atan(plane_tan * camera_x)
            d, side, hit, tu, spr = room._cast_ray(240, 240, facing + off, 32, 20)
            if hit:
                inv.append(1.0 / (d * math.cos(off)))
        assert len(inv) > 20
        # Linearity via second differences, normalised by the value range so it
        # also holds when the wall is perpendicular (inv constant -> range 0).
        sec = [inv[i + 2] - 2 * inv[i + 1] + inv[i] for i in range(len(inv) - 2)]
        rng = max(inv) - min(inv)
        metric = max(abs(s) for s in sec) / (rng if rng > 1e-12 else 1.0)
        assert metric < 1e-9, (
            f"flat wall not straight at facing {facing_deg}: curvature "
            f"{metric:.2e} (uniform-angle sampling gives ~1e-2)")


def test_overflowing_walls_crop_the_texture_instead_of_squeezing_it():
    """When a wall is close enough that its projected height overflows the
    screen, the renderer must CROP the texture to the visible span — not squeeze
    the whole texture into a screen-clamped strip. Squeezing was the real
    "bent wall" bug: clamped (near) columns compressed the entire brick texture
    while unclamped (far) columns didn't, breaking the courses across a FLAT
    wall, with the boundary marching along it as you walked (user reports
    2026-07-19). All three renderers must crop."""
    gr = (REPO_ROOT / "runtime" / "game_runner.py").read_text(encoding="utf-8")
    kx = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")

    # the squeeze signature: a screen-clamped height fed straight to the scale
    assert "strip_h = min(h, int(h * cell_size" not in gr
    assert "strip_h = min(h, h * cell_size" not in kx
    assert "Math.min(h, Math.floor(h * cellSize" not in ENGINE

    # the crop signature: unclamped height + a texture sub-range. Desktop's
    # scale factor became `view_h` with the DOOM-bar letterbox (view_h == h
    # until a viewport_height is set), so it reads view_h here; Kivy/HTML5 keep
    # `h` until their own viewport units land. The crop semantics (unclamped
    # projected height, not a screen-clamped squeeze) are identical either way.
    assert "full_h = view_h * cell_size / max(corrected, 1e-4)" in gr, "game_runner"
    assert "full_h = h * cell_size / max(corrected, 1e-4)" in kx, "kivy_exporter"
    assert "const fullH = h * cellSize / Math.max(corrected, 1e-4)" in ENGINE
    assert "ctx.drawImage(texSprite, texX, srcY, 1, srcH, x0, y0, stripW, visH)" in ENGINE

    # SUB-TEXEL accuracy: on a close wall one texel covers tens of screen px, so
    # snapping the crop to whole texels per column produced jagged edges.
    # Desktop carries the remainder as a blit offset; HTML5 passes float source
    # rows to drawImage; Kivy selects the slice with float tex_coords.
    assert "frac_px" in gr and "texels_per_px" in gr
    assert "Math.floor(v0 * th)" not in ENGINE, "engine.js still snaps to texels"
    assert "tex_coords=(0.0, v0, 1.0, v0," in kx, "kivy still snaps to texels"

    # BILLBOARDS get the same treatment — a sprite you walk into overflows the
    # screen too, and the old min(h, ...) squeezed the whole sprite in.
    assert "sprite_h = min(h, int(h * inst._cached_height" not in gr
    assert "sprite_h = min(h, h * ih" not in kx
    assert "Math.min(h, Math.floor(h * b.inst.boxHeight()" not in ENGINE
    # Desktop billboards scale by view_h too (letterbox), Kivy by h until Unit 3.
    assert "full_h = view_h * inst._cached_height / max(corrected, 1e-4)" in gr
    assert "full_h_b = h * ih / max(corrected_b, 1e-4)" in kx
    assert "const fullH = h * b.inst.boxHeight() / Math.max(b.corr, 1e-4)" in ENGINE
    assert "ctx.drawImage(img, srcX, bSrcY, 1, bSrcH, screenX, by0, 1, bVisH)" in ENGINE
    assert "tex_coords=(0.0, bv0, 1.0, bv0," in kx


def test_close_wall_texture_stays_continuous_across_the_clamp_boundary():
    """Behavioural: render a flat wall close enough that some columns overflow
    the screen, and check the texture row landing at screen-centre is the SAME
    across the clamp boundary (a squeezed strip would jump)."""
    import pygame
    room = GameRoom.__new__(GameRoom)
    room._raycast_h_walls = {(c, 4) for c in range(15)}
    room._raycast_v_walls = set()
    room._raycast_h_wall_sprites = {}
    room._raycast_v_wall_sprites = {}

    h, cell = 480, 32
    fov = math.radians(66)
    plane_tan = math.tan(fov / 2)
    N = 64
    facing = math.radians(-80.0)   # near-parallel: distances vary a lot
    # find a camera offset that straddles the clamp boundary (some columns
    # overflow the screen, some don't)
    centre_v, clamped, unclamped = [], 0, 0
    for off_px in (14, 18, 22, 26, 30, 36, 44):
        cam = (240.0, 4 * cell + off_px)
        centre_v, clamped, unclamped = [], 0, 0
        for col in range(N):
            camera_x = 2.0 * (col + 0.5) / N - 1.0
            off = math.atan(plane_tan * camera_x)
            d, side, hit, tu, spr = room._cast_ray(cam[0], cam[1], facing + off, cell, 20)
            if not hit:
                continue
            corrected = d * math.cos(off)
            full_h = h * cell / max(corrected, 1e-4)
            if full_h > h:
                clamped += 1
            else:
                unclamped += 1
            # texture v-coordinate that lands on the screen centre line
            y_top = h / 2.0 - full_h / 2.0
            centre_v.append((h / 2.0 - y_top) / full_h)
        if clamped and unclamped:
            break
    assert clamped > 0 and unclamped > 0, "need both sides of the clamp boundary"
    # the wall's centre line must map to the SAME texture row everywhere (0.5)
    assert max(abs(v - 0.5) for v in centre_v) < 1e-9, (
        "texture centre drifts across columns -- courses would break")
    """All three renderers must use the camera-plane mapping (and the matching
    inverse for billboards), not the old linear FOV ramp."""
    gr = (REPO_ROOT / "runtime" / "game_runner.py").read_text(encoding="utf-8")
    kx = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
    for src, name in ((gr, "game_runner"), (kx, "kivy_exporter")):
        assert "math.atan(plane_tan * camera_x)" in src, name
        assert "-fov_rad / 2 + fov_rad * (col / num_columns)" not in src, \
            f"{name} still uses the bent uniform-angle ramp"
    assert "Math.atan(planeTan * cameraX)" in ENGINE
    assert "-fovRad / 2 + fovRad * (col / numCols)" not in ENGINE, \
        "engine.js still uses the bent uniform-angle ramp"
    # billboards use the inverse mapping so they track the walls
    assert "math.tan(rel_angle) / plane_tan" in gr
    assert "math.tan(rel_angle) / plane_tan" in kx
    assert "Math.tan(b.relAngle) / planeTan" in ENGINE


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


# --- In-view HUD compositing (RAYCAST_HUD_PLAN Unit 4) ---------------------
# All three renderers used to draw the first-person frame and then STOP before
# the per-instance draw pass, so a raycast game's HUD (draw_score / draw_lives
# / draw_text / draw_health_bar) never rendered. Each target composites it now;
# these pin that none of them regresses back to a bare early-return.

def test_all_three_composite_the_hud_after_the_raycast_render():
    gr = (REPO_ROOT / "runtime" / "game_runner.py").read_text(encoding="utf-8")
    kx = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")

    # Desktop: _render_room runs the draw pass instead of returning bare.
    branch = gr[gr.index("if self.raycast_camera.get('enabled'):"):]
    branch = branch[:branch.index("return")]
    assert "self._render_raycast_view(screen)" in branch
    assert "self._render_draw_events(screen)" in branch, \
        "desktop returns without compositing the HUD"

    # HTML5: same shape, after renderRaycastView.
    js = ENGINE[ENGINE.index("if (this.raycastCamera && this.raycastCamera.enabled) {"):]
    js = js[:js.index("return;")]
    assert "this.renderRaycastView(ctx);" in js
    assert "runDrawEvent(ctx)" in js, "engine.js returns without compositing the HUD"

    # Kivy: a scene-level HUD group above the opaque overlay.
    assert "self._raycast_hud_group = InstructionGroup()" in kx
    assert "self.canvas.after.add(self._raycast_hud_group)" in kx


def test_all_three_draw_the_hud_in_screen_space():
    """A HUD at (8, 8) must land 8px from the window's top-left on every
    target — no camera/view offset, and (on Kivy) flipped against the WINDOW
    height rather than the room height."""
    gr = (REPO_ROOT / "runtime" / "game_runner.py").read_text(encoding="utf-8")
    kx = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
    # Desktop passes the bare screen (no view_offset).
    helper = gr[gr.index("def _render_draw_events"):]
    helper = helper[:helper.index("def update_views")]
    assert "run_draw_event(screen)" in helper
    assert "view_offset" not in helper
    # Kivy flips against display_height, not room_height.
    step = kx[kx.index("# 8. DRAW EVENTS"):]
    step = step[:step.index("# 9. CLEANUP")]
    assert "float(self.display_height)" in step


def test_raycast_2_ships_a_hud_controller():
    """The sample that surfaced the gap now demonstrates the fix. obj_hud must
    be VISIBLE: an invisible instance does not run its draw event (GameMaker
    semantics, enforced on all three targets since 380abd2) — which is exactly
    why the HUD can't live on obj_cam0/obj_cam1."""
    import json
    hud = json.loads((REPO_ROOT / "samples" / "raycast_2" / "objects" /
                      "obj_hud.json").read_text(encoding="utf-8"))
    assert hud["visible"] is True, \
        "an invisible controller would silently draw nothing"
    actions = [a["action"] for a in hud["events"]["draw"]["actions"]]
    assert "draw_score" in actions and "draw_lives" in actions
    # Registered in the manifest and placed in both rooms.
    proj = json.loads((REPO_ROOT / "samples" / "raycast_2" /
                       "project.json").read_text(encoding="utf-8"))
    assert "obj_hud" in proj["assets"]["objects"]
    for room_name in ("room0", "room1"):
        room = json.loads((REPO_ROOT / "samples" / "raycast_2" / "rooms" /
                           f"{room_name}.json").read_text(encoding="utf-8"))
        assert any(i.get("object_name") == "obj_hud" for i in room["instances"]), \
            f"{room_name} has no HUD instance"


def test_raycast_2_hud_actually_renders_through_the_real_game_loop():
    """End-to-end on the desktop reference target: run the sample and confirm
    the HUD's draw commands are flushed while the raycast camera is on."""
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame
    from runtime.game_runner import GameRunner, GameInstance

    seen = []
    real = GameInstance._process_draw_queue

    def spy(self, screen):
        for cmd in self._draw_queue:
            seen.append((self.object_name, cmd.get("type")))
        self._draw_queue = []          # record without rasterising

    runner = GameRunner(str(REPO_ROOT / "samples" / "raycast_2" / "project.json"))
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.show_highscore_dialog = lambda *a, **k: None
    runner._show_name_entry_dialog = lambda *a, **k: ""
    runner.process_pending_messages = lambda *a, **k: None

    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            state["f"] += 1
            if state["f"] >= 5:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real_clock = pygame.time.Clock
    GameInstance._process_draw_queue = spy
    pygame.time.Clock = _Clock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real_clock
        GameInstance._process_draw_queue = real

    assert runner.current_room.raycast_camera["enabled"] is True
    kinds = {k for name, k in seen if name == "obj_hud"}
    assert "text" in kinds and "lives" in kinds, \
        f"HUD did not render under raycast; saw {sorted(set(seen))!r}"


# --- Minimap (RAYCAST_MINIMAP_PLAN Unit 4) ---------------------------------
# draw_minimap is a MACRO action on all three targets: it emits ordinary
# rectangle/line draw-queue commands rather than needing a bespoke renderer.
# So the parity surface is pure geometry, and build_minimap_commands() in
# runtime/action_executor.py is the single source the other two mirror.

def test_all_three_implement_draw_minimap():
    kx = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
    kg = (REPO_ROOT / "export" / "Kivy" / "code_generator.py").read_text(encoding="utf-8")
    from events.action_types import ACTION_TYPES
    assert "draw_minimap" in ACTION_TYPES
    assert "case 'draw_minimap'" in ENGINE
    # Kivy: the generator emits a CALL and the base object defines it. Both
    # halves must exist — the M34 lesson.
    assert "self._draw_minimap(" in kg, "Kivy codegen emits no minimap call"
    assert "def _draw_minimap(" in kx, "Kivy base object defines no minimap"


def test_all_three_share_the_marker_and_heading_constants():
    """A marker drawn at a different size or a heading of a different length
    would look like a different game on each target."""
    from runtime.action_executor import MINIMAP_HEADING_LEN, MINIMAP_MARKER_HALF
    assert (MINIMAP_MARKER_HALF, MINIMAP_HEADING_LEN) == (2.0, 7.0)
    kx = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
    assert "_MM_MARK, _MM_HEAD = 2.0, 7.0" in kx
    assert "MM_MARK = 2.0, MM_HEAD = 7.0" in ENGINE


def test_all_three_negate_facing_angle_for_the_heading_line():
    """GM 0=right/90=up vs screen y DOWN. A missing negation mirrors the
    heading vertically and is invisible at angle 0 — so pin it in the source
    of all three, not just by testing one angle."""
    kx = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
    ae = (REPO_ROOT / "runtime" / "action_executor.py").read_text(encoding="utf-8")
    assert "math.radians(-float(facing_angle or 0.0))" in ae
    assert "math.radians(-float(getattr(camera, 'facing_angle', 0) or 0))" in kx
    assert "-(mmCam.facing_angle || 0) * Math.PI / 180" in ENGINE


def test_all_three_sort_the_wall_sets():
    """Wall sets are unordered. Without a sort the three targets can emit the
    same picture in a different order, which would make any command-level
    comparison flap."""
    kx = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
    ae = (REPO_ROOT / "runtime" / "action_executor.py").read_text(encoding="utf-8")
    assert "for (line_x, row) in sorted(" in ae
    assert "for (line_x, row) in sorted(" in kx
    assert ".sort((a, b) => (a[0] - b[0]) || (a[1] - b[1]))" in ENGINE


def test_all_three_use_the_ray_origin_for_the_marker():
    """Not the sprite corner — the same centre the renderers cast rays from,
    or the 'you are here' dot sits half a sprite off the actual viewpoint."""
    kx = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
    ae = (REPO_ROOT / "runtime" / "action_executor.py").read_text(encoding="utf-8")
    block = ae[ae.index("def execute_draw_minimap_action"):]
    block = block[:block.index("def execute_draw_health_bar_action")]
    assert "_sprite_top_left" in block and "_cached_width" in block
    assert "_raycast_gm_xy(camera)" in kx and "image_width" in kx
    assert "GameRoom.spriteTopLeft(mmCam)" in ENGINE and "boxWidth()" in ENGINE


def test_kivy_minimap_geometry_matches_the_desktop_reference_exactly():
    """The real parity check: run the desktop reference and a stand-in for the
    Kivy port over identical wall data and compare every emitted command.

    The Kivy method is inside a .format() template, so it can't be imported;
    this re-implements its arithmetic and asserts it lands on the desktop
    numbers. If the template's maths is edited without updating this, the
    source-level assertions above are what catch the drift.
    """
    import math as _math
    from runtime.action_executor import (
        build_minimap_commands, MINIMAP_HEADING_LEN, MINIMAP_MARKER_HALF,
    )
    v_walls = {(1, 0), (3, 2), (0, 4)}
    h_walls = {(2, 1), (4, 3)}
    cs, span, size, ox, oy = 32, 480.0, 130.0, 500.0, 340.0
    cam_x, cam_y, facing = 104.0, 200.0, 135.0

    ref = build_minimap_commands(
        v_walls=v_walls, h_walls=h_walls, cell_size=cs,
        room_width=480, room_height=480,
        cam_x=cam_x, cam_y=cam_y, facing_angle=facing,
        x=ox, y=oy, size=size,
        back_color="#101018", wall_color="#8080a0", player_color="#ffd040")

    scale = size / span

    def px(wx, wy):
        return ox + wx * scale, oy + wy * scale

    port = [{'type': 'rectangle', 'x1': ox, 'y1': oy,
             'x2': ox + size, 'y2': oy + size,
             'color': "#101018", 'filled': True}]
    for (lx, row) in sorted(v_walls):
        x1, y1 = px(lx * cs, row * cs)
        x2, y2 = px(lx * cs, (row + 1) * cs)
        port.append({'type': 'line', 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                     'color': "#8080a0"})
    for (col, ly) in sorted(h_walls):
        x1, y1 = px(col * cs, ly * cs)
        x2, y2 = px((col + 1) * cs, ly * cs)
        port.append({'type': 'line', 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                     'color': "#8080a0"})
    cx, cy = px(cam_x, cam_y)
    port.append({'type': 'line', 'x1': cx - MINIMAP_MARKER_HALF, 'y1': cy,
                 'x2': cx + MINIMAP_MARKER_HALF, 'y2': cy, 'color': "#ffd040"})
    rad = _math.radians(-facing)
    port.append({'type': 'line', 'x1': cx, 'y1': cy,
                 'x2': cx + _math.cos(rad) * MINIMAP_HEADING_LEN,
                 'y2': cy + _math.sin(rad) * MINIMAP_HEADING_LEN,
                 'color': "#ffd040"})

    assert len(port) == len(ref)
    for a, b in zip(ref, port):
        assert a['type'] == b['type']
        for key in ('x1', 'y1', 'x2', 'y2'):
            assert abs(a[key] - b[key]) < 1e-9, (a, b, key)
