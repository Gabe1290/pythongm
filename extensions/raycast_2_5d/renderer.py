#!/usr/bin/env python3
"""The 2.5D raycast renderer -- the drawing half of the raycast extension.

Moved verbatim (Stage B2, docs/RAYCAST_EXTENSION_PLAN.md) out of
runtime/game_runner.py, where these lived as GameRoom methods: ``self`` became
the explicit ``room`` parameter, the shared constants became module constants,
and the leading underscores dropped (they are this module's public API).
Behaviour is identical -- the raycast tests kept their assertions and followed
the code here.

What ``room`` must provide is all ordinary GameRoom API, none of it owned by
this extension: ``instances``, ``parse_color()``, ``_find_first_instance()``,
``_sprite_top_left()``, ``_all_sprites`` (generic engine helpers/state) and
``extension_state`` (the per-room namespace). All raycast-specific state — the
camera config the ``enable_raycast_view`` action sets and the derived wall-edge
caches — lives under ``room.extension_state["raycast"]`` (Stage B3b), reached
through ``state.raycast_state(room)``; core's ``GameRoom`` carries no raycast
attributes.

The HTML5 (export/HTML5/templates/engine.js) and Kivy
(export/Kivy/kivy_exporter.py) exporters carry their own hand-written ports of
this renderer; the numeric contracts are pinned by
tests/test_raycast_export_parity.py. Stage C may move those ports here as well.
"""

import math
from typing import Any, Dict, Set, Tuple

import pygame

from .state import raycast_state


def build_raycast_walls(room, cell_size: int):
    """Derive thin wall EDGES from every solid instance in the room —
    not "which whole grid cells are occupied". This is what makes a
    wall genuinely thinner than a cell (e.g. an 8px strip on a cell
    boundary) actually read as thin: a ray only stops at the specific
    edge a wall segment occupies, not at every cell the segment
    happens to touch.

    A solid instance's sprite aspect ratio decides its role: wider
    than tall -> a horizontal segment, sitting astride a horizontal
    grid line (blocks north/south passage); taller than wide -> a
    vertical segment astride a vertical line (blocks east/west).
    Roughly square (e.g. an old-style full-cell block) falls back to
    blocking all 4 edges of its cell, matching the coarse-grid
    behaviour this replaces — so non-thin-wall content still works.

    v_walls holds (line_x, row): a vertical wall on the grid line at
    column index line_x (world x = line_x * cell_size), spanning
    cell row. h_walls holds (col, line_y) symmetrically.

    Reuses existing room content instead of a separate authoring
    format. Built once and cached (room geometry is static at
    runtime for this v1 — walls created/destroyed after room load
    won't update the derived edges).
    """
    v_walls: Set[Tuple[int, int]] = set()
    h_walls: Set[Tuple[int, int]] = set()
    # Edge -> the sprite of the instance that created it (for Phase 5
    # texturing). Parallel to the sets; last writer wins if two instances
    # map to the same edge (grid walls all share one sprite anyway).
    v_sprites: Dict[Tuple[int, int], Any] = {}
    h_sprites: Dict[Tuple[int, int], Any] = {}
    for inst in room.instances:
        obj_data = inst._cached_object_data
        if not (obj_data and obj_data.get('solid', False)):
            continue
        width = inst._cached_width
        height = inst._cached_height
        spr = inst.sprite
        ix, iy = room._sprite_top_left(inst)   # origin-aware
        if width >= height * 1.5:
            line_y = round((iy + height / 2) / cell_size)
            col = int(ix // cell_size)
            h_walls.add((col, line_y))
            h_sprites[(col, line_y)] = spr
        elif height >= width * 1.5:
            line_x = round((ix + width / 2) / cell_size)
            row = int(iy // cell_size)
            v_walls.add((line_x, row))
            v_sprites[(line_x, row)] = spr
        else:
            gx = int(ix // cell_size)
            gy = int(iy // cell_size)
            v_walls.add((gx, gy))
            v_walls.add((gx + 1, gy))
            h_walls.add((gx, gy))
            h_walls.add((gx, gy + 1))
            for key in ((gx, gy), (gx + 1, gy)):
                v_sprites[key] = spr
            for key in ((gx, gy), (gx, gy + 1)):
                h_sprites[key] = spr
    st = raycast_state(room)
    st["v_walls"] = v_walls
    st["h_walls"] = h_walls
    st["v_sprites"] = v_sprites
    st["h_sprites"] = h_sprites
    st["cell_size"] = cell_size


def cast_ray(room, px: float, py: float, angle_rad: float, cell_size: int, max_cells: int):
    """DDA raycast from (px, py) (room pixel coords) at angle_rad
    (standard math convention: 0=+x, increasing counter-clockwise in
    *grid* space — see render_raycast_view for the GM-angle-to-this
    conversion) until it crosses a grid line carrying a registered
    wall edge (see build_raycast_walls) — not "until it enters a
    solid cell". The ray marches freely through open cells (however
    many) and only stops at an actual wall's real position.

    Returns (distance_in_pixels, side, hit, tex_u, sprite):
      - side is 0 for a vertical wall face (x-step hit) or 1 for a
        horizontal one (y-step hit) — used to cheaply shade one set of
        faces darker, a free depth cue with no lighting model needed.
      - hit is False when the ray reached max range without crossing a
        registered wall edge (the caller must draw no strip).
      - tex_u in [0, 1) is the horizontal texture coordinate where the ray
        met the wall (the fractional position along that wall's face) and
        sprite is the wall's sprite (or None) — both for Phase 5 texturing;
        a flat-colour caller just ignores them.
    """
    st = raycast_state(room)
    v_walls, h_walls = st["v_walls"], st["h_walls"]
    v_sprites, h_sprites = st["v_sprites"], st["h_sprites"]
    px_cell, py_cell = px / cell_size, py / cell_size
    dx, dy = math.cos(angle_rad), math.sin(angle_rad)
    map_x, map_y = int(px_cell), int(py_cell)

    delta_x = abs(1 / dx) if dx != 0 else 1e30
    delta_y = abs(1 / dy) if dy != 0 else 1e30

    if dx < 0:
        step_x = -1
        side_x = (px_cell - map_x) * delta_x
    else:
        step_x = 1
        side_x = (map_x + 1 - px_cell) * delta_x
    if dy < 0:
        step_y = -1
        side_y = (py_cell - map_y) * delta_y
    else:
        step_y = 1
        side_y = (map_y + 1 - py_cell) * delta_y

    side = 0
    dist_cells = float(max_cells)
    for _ in range(max_cells):
        if side_x < side_y:
            side_x += delta_x
            map_x += step_x
            side = 0
            # The vertical line just crossed is at the leading edge of
            # the cell just entered (moving +x) or the trailing edge
            # of the cell just left (moving -x) -- both name the same
            # absolute line index.
            line_x = map_x if step_x > 0 else map_x + 1
            wall_key = (line_x, map_y)
            hit = wall_key in v_walls
        else:
            side_y += delta_y
            map_y += step_y
            side = 1
            line_y = map_y if step_y > 0 else map_y + 1
            wall_key = (map_x, line_y)
            hit = wall_key in h_walls
        if hit:
            dist_cells = (side_x - delta_x) if side == 0 else (side_y - delta_y)
            # Texture-U: the fractional position along the wall's face
            # where the ray met it. wall_coord = the world coordinate
            # (in cell units) parallel to the wall at the hit; its
            # fractional part is U. Flip on the two faces a wall can be
            # seen from so the texture isn't mirrored between them.
            if side == 0:
                wall_coord = py_cell + dist_cells * dy
                if dx > 0:
                    wall_coord = -wall_coord
                sprite = v_sprites.get(wall_key)
            else:
                wall_coord = px_cell + dist_cells * dx
                if dy < 0:
                    wall_coord = -wall_coord
                sprite = h_sprites.get(wall_key)
            tex_u = wall_coord - math.floor(wall_coord)
            return max(dist_cells, 1e-4) * cell_size, side, True, tex_u, sprite
    # Marched the full render distance without crossing a registered
    # wall edge -- a real miss (open corridor/junction), not a wall at
    # max range. The caller must not draw a wall strip for this column:
    # earlier code drew one anyway using dist_cells==max_cells and
    # whatever `side` the last (non-hit) DDA step happened to leave
    # behind, producing a thin mis-colored sliver right at the horizon
    # for every miss column -- misread by a user as "walked outside the
    # map" when they were really just facing an opening wider than the
    # wall's own render distance.
    return max(dist_cells, 1e-4) * cell_size, side, False, 0.0, None


# --- wall shading model (shared by all three renderers; keep in sync) ----
# A y-face (side==1) used to be drawn at HALF brightness. That binary 2:1
# break produced a hard vertical seam wherever an h-wall met a v-wall at
# roughly the same distance -- no depth change behind it, so the eye read it
# as a corner that slid along the wall as you moved (user report,
# 2026-07-19; measured 60k+ such same-distance side flips in raycast_2).
# Replaced with: a SUBTLE side hint plus real distance falloff, which is
# what actually sells depth in a raycaster and stops flat runs from faking
# corners. HTML5 (engine.js wallShade) and Kivy (_wall_shade) implement the
# identical formula -- pinned by tests/test_raycast_export_parity.py.
RAYCAST_SIDE_SHADE = 0.85    # y-face brightness (was 0.5 -- too harsh)
RAYCAST_FOG_STRENGTH = 0.55  # darkening at max render distance
RAYCAST_MIN_SHADE = 0.35     # never fully black
# Wall strips project this many times taller than a cube would (1.0 =
# cube). 1.5 gives taller, more enclosed corridors -- a "maze in a
# building" look, especially with a ceiling instead of a sky. Applies to
# WALLS only, not billboards (which stay sprite-sized). HTML5 (engine.js)
# and Kivy mirror it -- pinned by tests/test_raycast_export_parity.py.
RAYCAST_WALL_HEIGHT = 1.5


def wall_shade(side: int, corrected: float, max_dist: float) -> float:
    """Brightness multiplier in [MIN_SHADE, 1] for a wall strip."""
    side_factor = RAYCAST_SIDE_SHADE if side == 1 else 1.0
    t = corrected / max_dist if max_dist > 0 else 0.0
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    dist_factor = 1.0 - RAYCAST_FOG_STRENGTH * t
    return max(RAYCAST_MIN_SHADE, side_factor * dist_factor)


def render_raycast_view(room, screen: pygame.Surface):
    """Render the room as a first-person raycast projection instead of
    the normal top-down view. See docs/RAYCAST_2_5D_PLAN.md."""
    st = raycast_state(room)
    cfg = st["camera"]
    cell_size = int(cfg.get('cell_size', 32))
    if st["v_walls"] is None or st["cell_size"] != cell_size:
        build_raycast_walls(room, cell_size)

    camera = room._find_first_instance(cfg.get('camera_object', ''))
    w, h = screen.get_size()
    # DOOM-bar letterbox: the 3D view occupies only the top `view_h` px, so
    # the horizon (view_h/2) and every vertical projection scale shrink with
    # it while the width `w` is untouched. viewport_height 0 => full height,
    # so every existing raycast game renders pixel-identical. The band
    # [view_h, h) below is filled opaque black after the passes, reserved
    # for a status bar the draw-event pass then paints over.
    view_h = int(cfg.get('viewport_height', 0)) or h
    view_h = max(1, min(view_h, h))
    half_h = view_h / 2

    floor_color = room.parse_color(cfg.get('floor_color', '#464632'))
    ceiling_color = room.parse_color(cfg.get('ceiling_color', '#87CEEB'))
    screen.fill(ceiling_color, (0, 0, w, int(half_h)))
    screen.fill(floor_color, (0, int(half_h), w, view_h - int(half_h)))

    if camera is None:
        if view_h < h:
            screen.fill((0, 0, 0), (0, view_h, w, h - view_h))
        return  # nothing to render from -- flat floor/ceiling only

    # Ray origin is the camera instance's sprite CENTER, not its raw
    # x/y (top-left corner). Every instance in a grid maze -- walls
    # and the player alike -- sits at exact multiples of cell_size, so
    # a player at rest against a wall has a raw (x, y) that lands
    # exactly on a wall-bearing grid line. DDA rays cast from exactly
    # on that line hit it (or graze past it) almost immediately and
    # inconsistently depending on ray angle, which read as "there's a
    # wall right in front of me in every direction" -- a player
    # correctly stopped against the west wall, still facing east,
    # would see a wall filling the whole screen instead of the open
    # corridor actually ahead. Centering the origin in the occupied
    # cell removes the coincidence.
    _cx, _cy = room._sprite_top_left(camera)   # origin-aware
    cam_x = _cx + camera._cached_width / 2
    cam_y = _cy + camera._cached_height / 2

    wall_color = room.parse_color(cfg.get('wall_color', '#993333'))
    fov_deg = cfg.get('fov', 66)
    fov_rad = math.radians(fov_deg)
    render_distance_cells = int(cfg.get('render_distance', 20))
    num_columns = int(cfg.get('columns', min(w, 320)))
    col_width = w / num_columns

    # GM angle convention (0=right, 90=up, ...) -> screen-space radians
    # (y grows downward), matching GameInstance.direction's own
    # atan2(-vspeed, hspeed) convention so turning via set_facing_angle
    # feels consistent with every other direction-based action.
    facing_screen_rad = math.radians(-camera.facing_angle)

    # Phase 5b: DOOM-style sky over the ceiling region. The sky is treated
    # as infinitely far away -- it does NOT recede with distance, it just
    # pans horizontally with facing_angle (turning 360deg pans the full
    # panorama exactly once, so a landmark returns to the same screen spot
    # after a full turn), giving a sense of a 360deg horizon from a
    # FOV-wide slice. Cheapest texture in the pipeline: one scale + up to
    # two blits, no per-column distance math. Drawn OVER the flat ceiling
    # fill and UNDER the walls, so wall strips occlude it for free. Absent
    # sky_texture -> the flat ceiling_color fill above stands (unchanged).
    sky_name = cfg.get('sky_texture', '')
    sky_sprite = (getattr(room, '_all_sprites', {}) or {}).get(sky_name) if sky_name else None
    if sky_sprite is not None and h > 0:
        sky_frame = sky_sprite.get_frame(0)
        # Panorama width = the sky stretched so the FOV-wide screen shows
        # exactly fov/360 of it.
        pano_w = max(1, int(w * 360.0 / max(1.0, fov_deg)))
        ceil_h = int(half_h)
        pano = pygame.transform.scale(sky_frame, (pano_w, max(1, ceil_h)))
        pan = int((camera.facing_angle % 360) / 360.0 * pano_w)
        # Two blits cover the visible window regardless of where the pan
        # lands (the second is the horizontal wrap).
        screen.blit(pano, (-pan, 0))
        if pano_w - pan < w:
            screen.blit(pano, (pano_w - pan, 0))

    # Phase 5: textured floor (and, indoors, ceiling) via low-res floor
    # casting. Full-resolution per-pixel casting measured ~64ms/frame in
    # pure Python (the plan's timing gate) -- unusable; a low-res cast +
    # transform.scale upscale is ~5ms at 4x and keeps the authentic
    # chunky Wolfenstein look. floor_texture casts the floor region; a
    # ceiling_texture casts the ceiling ONLY when no sky_texture claimed
    # it. Absent both -> the flat floor/ceiling fills stand.
    cast_res = max(1, int(cfg.get('floor_cast_res', 4)))
    floor_sprite = (getattr(room, '_all_sprites', {}) or {}).get(cfg.get('floor_texture', ''))
    ceil_tex_name = cfg.get('ceiling_texture', '')
    ceil_sprite = (getattr(room, '_all_sprites', {}) or {}).get(ceil_tex_name) if ceil_tex_name else None
    cam_cx, cam_cy = cam_x / cell_size, cam_y / cell_size
    if floor_sprite is not None:
        cast_floor_plane(screen, floor_sprite.get_frame(0),
                               cam_cx, cam_cy, facing_screen_rad, fov_rad,
                               cast_res, ceiling=False, view_h=view_h)
    if ceil_sprite is not None and sky_sprite is None:
        cast_floor_plane(screen, ceil_sprite.get_frame(0),
                               cam_cx, cam_cy, facing_screen_rad, fov_rad,
                               cast_res, ceiling=True, view_h=view_h)

    # Phase 5: sample a vertical texture strip per wall column (per the
    # plan). Off -> flat colour (the pre-Phase-5 look), also the automatic
    # fallback when no texture is available. A `wall_texture` sprite name
    # in the camera config textures EVERY wall with one image (the usual
    # choice — the derived thin edge-wall collision sprites are not real
    # wall art); without it, each wall samples its own instance sprite.
    textured = bool(cfg.get('wall_textured', True))
    wall_texture_name = cfg.get('wall_texture', '')
    wall_texture = (getattr(room, '_all_sprites', {}) or {}).get(wall_texture_name) \
        if wall_texture_name else None
    # CAMERA-PLANE projection (not uniform-angle). Screen columns are evenly
    # spaced, so the rays must be evenly spaced on the CAMERA PLANE, i.e.
    # ray_dir = dir + plane * camera_x with camera_x in [-1, 1]. The angle
    # off-centre is therefore atan(tan(fov/2) * camera_x), NOT a linear ramp
    # over the FOV. Sampling uniformly in ANGLE while drawing at uniform
    # screen x is not a perspective projection: it BENDS straight walls, so
    # a flat wall rendered as you moved past it looked like it had a corner
    # in it (user report 2026-07-19). The floor cast already used the
    # camera-plane method -- the wall pass now matches it, so walls, floor
    # and billboards finally share one projection.
    plane_tan = math.tan(fov_rad / 2)
    col_wall_dist = [float('inf')] * num_columns  # for billboard occlusion, below
    for col in range(num_columns):
        camera_x = 2.0 * (col + 0.5) / num_columns - 1.0
        ray_offset = math.atan(plane_tan * camera_x)
        ray_angle = facing_screen_rad + ray_offset
        dist, side, hit, tex_u, wall_sprite = cast_ray(
            room, cam_x, cam_y, ray_angle, cell_size, render_distance_cells)
        if not hit:
            # No wall within render distance -- leave the ceiling/floor
            # fill showing for this column instead of drawing a bogus
            # horizon-line sliver (see cast_ray's miss-path comment).
            continue
        corrected = dist * math.cos(ray_offset)  # fisheye correction
        col_wall_dist[col] = corrected
        # TRUE (unclamped) projected height. The visible slice of the
        # TEXTURE must be CROPPED to what's on screen -- NOT the whole
        # texture squeezed into a screen-clamped strip. Squeezing was the
        # real "bent wall" bug: once a wall got close enough to overflow the
        # screen, its columns clamped and showed the entire brick texture
        # compressed, while neighbouring (farther) columns still showed it
        # correctly scaled. That discontinuity is a hard break in the brick
        # courses across a FLAT wall, and the clamp boundary marches along
        # the wall as you walk toward/away from it -- exactly the "corner
        # that moves" users reported (2026-07-19).
        full_h = view_h * cell_size * RAYCAST_WALL_HEIGHT / max(corrected, 1e-4)
        y_top = half_h - full_h / 2.0
        x0 = int(col * col_width)
        x1 = int((col + 1) * col_width)
        strip_w = max(1, x1 - x0)
        y0 = max(0, int(math.floor(y_top)))
        y1 = min(view_h, int(math.ceil(y_top + full_h)))
        vis_h = y1 - y0
        if vis_h <= 0:
            continue

        # Subtle side hint + distance falloff (see wall_shade).
        shade = wall_shade(side, corrected,
                       render_distance_cells * cell_size)
        tex_sprite = wall_texture if wall_texture is not None else wall_sprite
        if textured and tex_sprite is not None:
            frame = tex_sprite.get_frame(0)
            tw, th = frame.get_width(), frame.get_height()
            tex_x = min(tw - 1, max(0, int(tex_u * tw)))
            # Texture rows that map onto the visible screen span. subsurface
            # needs INTEGER rows, but on a close wall one texel covers tens
            # of screen pixels, so rounding src_y per column made adjacent
            # columns snap to different texels -- a jump of a whole texel
            # (~30-60px), i.e. the jagged close-up edges. Crop to the floor
            # texel (+ margin) and carry the SUB-TEXEL remainder as a
            # blit offset instead, so the residual error is <=1px.
            texels_per_px = th / full_h
            src_y_f = (y0 - y_top) * texels_per_px
            src_y = max(0, min(th - 1, int(math.floor(src_y_f))))
            frac_px = (src_y_f - src_y) / texels_per_px   # in screen px
            need = int(math.ceil(vis_h * texels_per_px)) + 2
            src_h = max(1, min(th - src_y, need))
            dest_h = max(1, int(round(src_h / texels_per_px)))
            col_surf = frame.subsurface((tex_x, src_y, 1, src_h))
            strip = pygame.transform.scale(col_surf, (strip_w, dest_h))
            if shade < 1.0:
                v = int(shade * 255)
                strip.fill((v, v, v), special_flags=pygame.BLEND_RGB_MULT)
            off = max(0, min(dest_h - 1, int(round(frac_px))))
            screen.blit(strip, (x0, y0),
                        (0, off, strip_w, min(vis_h, dest_h - off)))
        else:
            color = tuple(int(c * shade) for c in wall_color)
            screen.fill(color, (x0, y0, strip_w, vis_h))

    # Billboard sprites (Phase 6 of the plan doc, scoped down to a
    # single first cut): any visible, sprited, non-solid instance
    # (goals, pickups, monsters -- walls are solid and already drawn
    # above) renders as a camera-facing sprite, scaled by distance and
    # centered on the horizon like a wall strip. Occlusion is real
    # per-column clipping against col_wall_dist (the same corrected
    # distances the wall loop above just computed), not just a single
    # bounding check, so a goal behind a wall is properly hidden while
    # one only partially behind a corner is properly clipped.
    billboards = []
    for inst in room.instances:
        if inst is camera or not inst.visible or inst.sprite is None:
            continue
        if (inst._cached_object_data or {}).get('solid', False):
            continue
        _bx0, _by0 = room._sprite_top_left(inst)   # origin-aware
        bx = _bx0 + inst._cached_width / 2
        by = _by0 + inst._cached_height / 2
        dx, dy = bx - cam_x, by - cam_y
        dist = math.hypot(dx, dy)
        if dist < 1e-4:
            continue
        rel_angle = math.atan2(dy, dx) - facing_screen_rad
        rel_angle = (rel_angle + math.pi) % (2 * math.pi) - math.pi
        if abs(rel_angle) > fov_rad / 2 + 0.5:  # margin for the sprite's own width
            continue
        corrected = dist * math.cos(rel_angle)
        if corrected <= 1e-4:
            continue
        billboards.append((corrected, rel_angle, inst))

    # Farthest first (painter's algorithm) so nearer billboards draw
    # over farther ones where sprites overlap.
    billboards.sort(key=lambda b: -b[0])
    for corrected, rel_angle, inst in billboards:
        # Same unclamped-height + sub-texel crop the wall pass uses: a
        # sprite you walk right up to overflows the screen, and squeezing
        # the whole sprite into a screen-clamped height (the old
        # min(h, ...)) both distorted it and jumped a whole texel between
        # adjacent columns.
        full_h = view_h * inst._cached_height / max(corrected, 1e-4)
        sprite_w = int(view_h * inst._cached_width / max(corrected, 1e-4))
        if sprite_w < 1 or full_h < 1:
            continue
        # Same camera-plane mapping the wall pass uses (inverse of
        # ray_offset = atan(plane_tan * camera_x)), so billboards line up
        # with the walls instead of drifting toward the screen edges.
        camera_x = math.tan(rel_angle) / plane_tan if plane_tan else 0.0
        col_center = (camera_x + 1.0) * 0.5 * num_columns
        x_center = col_center * col_width
        x_left = int(x_center - sprite_w / 2)
        y_top_f = half_h - full_h / 2.0
        y0 = max(0, int(math.floor(y_top_f)))
        y1 = min(view_h, int(math.ceil(y_top_f + full_h)))
        vis_h = y1 - y0
        if vis_h <= 0:
            continue
        frame = inst.sprite.get_frame(inst.image_index)
        fh = frame.get_height()
        rows_per_px = fh / full_h
        src_y_f = (y0 - y_top_f) * rows_per_px
        src_y = max(0, min(fh - 1, int(math.floor(src_y_f))))
        frac_px = (src_y_f - src_y) / rows_per_px
        need = int(math.ceil(vis_h * rows_per_px)) + 2
        src_h = max(1, min(fh - src_y, need))
        dest_h = max(1, int(round(src_h / rows_per_px)))
        scaled = pygame.transform.scale(
            frame.subsurface((0, src_y, frame.get_width(), src_h)),
            (sprite_w, dest_h))
        off = max(0, min(dest_h - 1, int(round(frac_px))))
        blit_h = min(vis_h, dest_h - off)
        # Clip column-by-column against the wall distance already
        # cast for that screen column -- a sprite behind a wall (or
        # half-behind a corner) only shows the unoccluded slice.
        slice_x = 0
        while slice_x < sprite_w:
            screen_x = x_left + slice_x
            if 0 <= screen_x < w:
                col_idx = min(num_columns - 1, max(0, int(screen_x / col_width)))
                if corrected < col_wall_dist[col_idx]:
                    screen.blit(scaled, (screen_x, y0),
                                (slice_x, off, 1, blit_h))
            slice_x += 1

    # DOOM-bar letterbox: fill the reserved band below the 3D view opaque
    # black, unconditionally (like the ceiling/floor fills) and BEFORE the
    # draw-event pass, so draw_doom_hud paints over a clean backdrop. No-op
    # when view_h == h (the default full-height case).
    if view_h < h:
        screen.fill((0, 0, 0), (0, view_h, w, h - view_h))


def cast_floor_plane(screen, frame, cam_cx, cam_cy,
                     facing_screen_rad, fov_rad, res, ceiling=False,
                     view_h=None):
    """Low-res floor/ceiling texture casting (Phase 5). Renders the ground
    (or ceiling) plane into a downsampled surface, then upscales — full-res
    per-pixel casting is ~13x too slow in pure Python (timing spike).

    The plane is sampled in CELL units so the texture tiles once per grid
    cell and lines up with the wall bases. Row distance is derived from the
    same projection the wall pass uses (a wall 1 cell away has its base at
    the screen bottom), so floor and walls meet seamlessly:
    rowDistance_cells = (0.5*h) / (y - horizon). The two FOV-edge ray
    directions (camera-plane method) are interpolated across columns, which
    keeps floor lines straight (the fisheye-correct equivalent of the wall
    pass). `ceiling` mirrors the same cast into the top half.
    """
    w, h = screen.get_size()
    # Letterbox: the cast fills the floor/ceiling of the shrunk 3D view, so
    # the horizon and projection reference are view_h, not the true height.
    # view_h=None keeps the legacy full-height behaviour.
    if view_h is None:
        view_h = h
    view_h = max(1, min(int(view_h), h))
    half_h = view_h // 2
    region_h = view_h - half_h
    if region_h <= 0:
        return
    tw, th = frame.get_width(), frame.get_height()
    if tw <= 0 or th <= 0:
        return
    dir_x, dir_y = math.cos(facing_screen_rad), math.sin(facing_screen_rad)
    plane = math.tan(fov_rad / 2)
    plane_x, plane_y = -dir_y * plane, dir_x * plane
    rdx0, rdy0 = dir_x - plane_x, dir_y - plane_y   # leftmost column ray
    rdx1, rdy1 = dir_x + plane_x, dir_y + plane_y   # rightmost column ray
    pos_z = 0.5 * view_h

    sw = max(1, w // res)
    sh = max(1, region_h // res)
    small = pygame.Surface((sw, sh))
    put = small.set_at
    tex_at = frame.get_at
    floor = math.floor
    step_scale = res / w  # (rdx1-rdx0)/w scaled by the horizontal stride
    for j in range(sh):
        y = half_h + j * res
        p = y - half_h
        if p <= 0:
            p = 1
        rowd = pos_z / p
        stepx = rowd * (rdx1 - rdx0) * step_scale
        stepy = rowd * (rdy1 - rdy0) * step_scale
        fx = cam_cx + rowd * rdx0
        fy = cam_cy + rowd * rdy0
        for i in range(sw):
            tx = int(tw * (fx - floor(fx)))
            ty = int(th * (fy - floor(fy)))
            if tx >= tw:
                tx = tw - 1
            if ty >= th:
                ty = th - 1
            put((i, j), tex_at((tx, ty)))
            fx += stepx
            fy += stepy
    scaled = pygame.transform.scale(small, (w, region_h))
    if ceiling:
        scaled = pygame.transform.flip(scaled, False, True)
        screen.blit(scaled, (0, 0))
    else:
        screen.blit(scaled, (0, half_h))
