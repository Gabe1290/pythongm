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

from .heights import build_floor_heights, is_step, max_floor_height
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
    format. Rebuilt every frame from the live instance list (cheap --
    a few hundred instances at most, dwarfed by the DDA ray casting
    that follows), so a wall instance created or destroyed at runtime
    (a door opening, a maze that grows) is reflected immediately. An
    earlier version cached this and only rebuilt on a cell_size change,
    which left the first-person view showing walls that had already
    been destroyed (user report, 2026-10-06) -- fixed by just not
    caching it; see render_raycast_view.
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
# The vertical model behind it (docs/RAYCAST_STAIRS_PLAN.md, S4), in grid
# cells. The eye sits RAYCAST_EYE_HEIGHT above the floor -- half the default
# wall, so the horizon is the middle of a default wall. Walls (and the
# ceiling plane) rise to the camera's `wall_height`, default
# RAYCAST_WALL_HEIGHT; a wall texture covers RAYCAST_TEXTURE_HEIGHT of it and
# REPEATS above that (anchored at the floor), so raising the walls for stairs
# keeps the bricks their usual size instead of stretching them. With the
# default height a wall is exactly one tile: today's picture, bit for bit.
RAYCAST_EYE_HEIGHT = 0.75
RAYCAST_TEXTURE_HEIGHT = 1.5
# Where the eye sits inside one texture tile, from its top (0.5: mid-tile).
# Kept as a ratio so the default wall's top is computed as
# `half_h - tile_h * 0.5`, numerically identical to the old `full_h / 2.0`.
_EYE_FROM_TILE_TOP = (RAYCAST_TEXTURE_HEIGHT - RAYCAST_EYE_HEIGHT) / RAYCAST_TEXTURE_HEIGHT
# Allowed wall_height range (cells): the ceiling must clear the eye.
RAYCAST_MIN_WALL_HEIGHT = 1.0
RAYCAST_MAX_WALL_HEIGHT = 10.0


def clamp_wall_height(value) -> float:
    """A camera's wall_height in cells, defaulted and clamped to the range."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return RAYCAST_WALL_HEIGHT
    if v != v:                                   # NaN
        return RAYCAST_WALL_HEIGHT
    return min(RAYCAST_MAX_WALL_HEIGHT, max(RAYCAST_MIN_WALL_HEIGHT, v))


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


def billboard_rotation_frame(bx: float, by: float, facing_angle_deg: float,
                              cam_x: float, cam_y: float, frames: int) -> int:
    """Pick which of a billboard instance's `frames` equally-spaced
    view-angle sprite frames the camera should see right now — the
    Doom/Build-engine "actor rotation" trick: instead of a single flat
    always-the-same-image cutout, the sprite strip holds `frames` views of
    the object shot from equally-spaced angles, and walking a full circle
    around it cycles through all of them exactly once, so it finally reads
    as something with real sides instead of a cardboard cutout.

    Frame 0 is the object's FRONT view: the camera sees frame 0 when it is
    positioned in the direction the object's own facing_angle points (set
    via set_facing_angle, independently of the camera's facing_angle —
    these are two different instances' two different angles). Frames then
    advance clockwise in screen space (GM angle convention, same as every
    other facing_angle use in this file) as the camera moves around the
    object.

    frames <= 1 always returns 0 (the degenerate/disabled case — the caller
    falls back to the normal animated image_index instead of calling this
    at all). HTML5 (export_html5.js) and Kivy (export_kivy.py
    _billboard_rotation_frame) mirror this formula exactly; pinned by
    tests/test_raycast_export_parity.py.
    """
    if frames <= 1:
        return 0
    facing_rad = math.radians(-facing_angle_deg)
    view_rad = math.atan2(cam_y - by, cam_x - bx)
    rel = (view_rad - facing_rad) % (2 * math.pi)
    step = (2 * math.pi) / frames
    return int(round(rel / step)) % frames


# --- stairs (docs/RAYCAST_STAIRS_PLAN.md, S5) ------------------------------
# A room with at least one step (heights.build_floor_heights) is drawn by a
# front-to-back COLUMN WALK instead of "one wall strip per column": the ray
# keeps going past steps, every change of floor height on the way is drawn
# (a step's front, called a riser, where the floor rises; nothing where it
# drops -- the lower floor is hidden behind the nearer edge), and the wall
# that finally stops the ray is drawn only down to whatever is in front of
# it. One clip value per column (the lowest screen row still free) does all
# the hiding. A room with no step never takes this path, so it renders
# exactly as before.


def stairs_y(z, eye_z, d, half_h, view_h):
    """Screen row of world height z (room px) at corrected distance d (px):
    the one projection walls, risers, treads and floor share."""
    return half_h + (eye_z - z) * view_h / d


def cast_ray_steps(room, px, py, angle_rad, cell_size, max_cells, heights):
    """cast_ray, also recording where the floor height changes on the way.

    Returns (crossings, hit). ``crossings`` lists, nearest first, every grid
    line crossed where the entered cell's floor height differs from the
    previous one: (dist_cells, new_height, side, tex_u, cell). ``hit`` is
    cast_ray's wall result (dist_px, side, hit, tex_u, sprite) -- identical
    to cast_ray for the same ray: steps never stop a ray, walls do.
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

    crossings = []
    h_prev = heights.get((map_x, map_y), 0.0)
    side = 0
    dist_cells = float(max_cells)
    for _ in range(max_cells):
        if side_x < side_y:
            side_x += delta_x
            map_x += step_x
            side = 0
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
        d_cells = (side_x - delta_x) if side == 0 else (side_y - delta_y)
        # Texture-U exactly as cast_ray computes it (a riser is textured like
        # a wall standing on that grid line).
        if side == 0:
            wall_coord = py_cell + d_cells * dy
            if dx > 0:
                wall_coord = -wall_coord
        else:
            wall_coord = px_cell + d_cells * dx
            if dy < 0:
                wall_coord = -wall_coord
        tex_u = wall_coord - math.floor(wall_coord)
        if hit:
            sprite = v_sprites.get(wall_key) if side == 0 else h_sprites.get(wall_key)
            return crossings, (max(d_cells, 1e-4) * cell_size, side, True, tex_u, sprite)
        h_next = heights.get((map_x, map_y), 0.0)
        if h_next != h_prev:
            crossings.append((d_cells, h_next, side, tex_u, (map_x, map_y)))
            h_prev = h_next
    return crossings, (max(dist_cells, 1e-4) * cell_size, side, False, 0.0, None)


def layout_column(crossings, hit, h0, eye_z, wall_top_z, cell_size, cos_off,
                  half_h, view_h, max_cells):
    """Turn one column's crossings into what to draw, front to back.

    Pure geometry, the parity target for the export ports. Rows are floats
    (unclamped); the caller rounds and clips. Returns a dict:

    * ``treads``: [(y_top, y_bot, height, d_near)] floor spans, at every
      height including 0 (the floor cast needs them all from S6 on);
    * ``risers``: [(y_top, y_bot, d, side, tex_u, cell, h_lo, h_hi)];
    * ``wall``: (y_top, y_bot, d, side, tex_u, sprite) or None;
    * ``occluders``: [(d, clip)] -- the free-rows limit after each crossing,
      for billboards (S7);
    * ``wall_dist``: the wall's corrected distance (inf on a miss).
    """
    clip = float(view_h)
    treads, risers, occluders = [], [], []
    h_cur = h0
    d_prev = 0.0
    for dist_cells, h_next, side, tex_u, cell in crossings:
        d = max(dist_cells * cell_size * cos_off, 1e-4)
        y_cur = stairs_y(h_cur, eye_z, d, half_h, view_h)
        if y_cur < clip:
            treads.append((y_cur, clip, h_cur, d_prev))
            clip = y_cur
        if h_next > h_cur:
            y_top = stairs_y(h_next, eye_z, d, half_h, view_h)
            if y_top < clip:
                risers.append((y_top, clip, d, side, tex_u, cell, h_cur, h_next))
                clip = y_top
        occluders.append((d, clip))
        h_cur = h_next
        d_prev = d
        if clip <= 0:
            return {"treads": treads, "risers": risers, "wall": None,
                    "occluders": occluders, "wall_dist": float("inf")}
    dist_px, side, is_hit, tex_u, sprite = hit
    d = max(dist_px * cos_off, 1e-4)
    if not is_hit:
        d = max(max_cells * cell_size * cos_off, 1e-4)
    y_cur = stairs_y(h_cur, eye_z, d, half_h, view_h)
    if y_cur < clip:
        treads.append((y_cur, clip, h_cur, d_prev))
        clip = y_cur
    wall = None
    if is_hit:
        y_top = stairs_y(wall_top_z, eye_z, d, half_h, view_h)
        if y_top < clip:
            wall = (y_top, clip, d, side, tex_u, sprite)
        occluders.append((d, min(clip, y_top)))
    return {"treads": treads, "risers": risers, "wall": wall,
            "occluders": occluders, "wall_dist": d if is_hit else float("inf")}


def _row(y):
    """The screen row a float boundary falls on: rows [_row(a), _row(b))
    partition the screen without gaps or overlaps between neighbours."""
    return int(math.floor(y + 0.5))


def _blit_tile_cached(screen, cache, frame, th, tex_x, x0, strip_w, y_top,
                      full_h, y0, vis_h, shade_v):
    """blit_wall_tile's exact maths, reusing the scaled+shaded strip when an
    identical one was already made this frame. A step front facing the
    camera is at the same distance in every column, so neighbouring columns
    that sample the same texture column produce the very same strip: the
    expensive part (crop, scale, shade) is done once and only the blit is
    repeated. Keyed by the integers that fully determine the strip.
    ``th`` is the frame's height; ``shade_v`` the 0-255 multiplier, or 256
    for "no shading" (shade >= 1). Written for speed: it runs ~1,500 times a
    frame on a staircase, so no builtin min/max calls."""
    texels_per_px = th / full_h
    src_y_f = (y0 - y_top) * texels_per_px
    src_y = int(math.floor(src_y_f))
    if src_y < 0:
        src_y = 0
    elif src_y > th - 1:
        src_y = th - 1
    src_h = int(math.ceil(vis_h * texels_per_px)) + 2
    if src_h > th - src_y:
        src_h = th - src_y
    if src_h < 1:
        src_h = 1
    dest_h = int(round(src_h / texels_per_px))
    if dest_h < 1:
        dest_h = 1
    key = (id(frame), tex_x, src_y, src_h, dest_h, strip_w, shade_v)
    strip = cache.get(key)
    if strip is None:
        strip = pygame.transform.scale(frame.subsurface((tex_x, src_y, 1, src_h)),
                                       (strip_w, dest_h))
        if shade_v < 256:
            strip.fill((shade_v, shade_v, shade_v), special_flags=pygame.BLEND_RGB_MULT)
        cache[key] = strip
    off = int(round((src_y_f - src_y) / texels_per_px))
    if off > dest_h - 1:
        off = dest_h - 1
    if off < 0:
        off = 0
    blit_h = dest_h - off
    if blit_h > vis_h:
        blit_h = vis_h
    screen.blit(strip, (x0, y0), (0, off, strip_w, blit_h))


def draw_wall_rows(screen, frame, color, tex_u, x0, strip_w, d, eye_z,
                   cell_size, half_h, view_h, r0, r1, shade, cache=None):
    """Draw rows [r0, r1) of a wall standing at corrected distance d -- a
    whole wall, or the slice of one between two floor heights (a riser).
    The texture repeats every RAYCAST_TEXTURE_HEIGHT cells, anchored at
    world height 0, exactly like the default wall pass (one tile per default
    wall). frame None -> flat colour. With a ``cache`` dict, identical
    scaled strips are reused within the frame (see _blit_tile_cached)."""
    if r0 < 0:
        r0 = 0
    if r1 > view_h:
        r1 = view_h
    if r1 <= r0:
        return
    if frame is None:
        screen.fill(tuple(int(c * shade) for c in color), (x0, r0, strip_w, r1 - r0))
        return
    tw, th = frame.get_size()
    tile_z = RAYCAST_TEXTURE_HEIGHT * cell_size
    tile_h = view_h * tile_z / d
    tex_x = int(tex_u * tw)
    if tex_x > tw - 1:
        tex_x = tw - 1
    elif tex_x < 0:
        tex_x = 0
    # World heights at the slice's bottom and top rows -> which tiles it spans.
    z_bot = eye_z - (r1 - half_h) * d / view_h
    z_top = eye_z - (r0 - half_h) * d / view_h
    k0 = int(math.floor(z_bot / tile_z))
    if k0 < 0:
        k0 = 0
    k1 = int(math.floor(z_top / tile_z))
    if k1 < k0:
        k1 = k0
    shade_v = int(shade * 255) if shade < 1.0 else 256
    for k in range(k0, k1 + 1):
        seg_top = half_h + (eye_z - (k + 1) * tile_z) * view_h / d   # stairs_y, inlined
        sy0 = int(math.floor(seg_top))
        if sy0 < r0:
            sy0 = r0
        sy1 = int(math.ceil(seg_top + tile_h))
        if sy1 > r1:
            sy1 = r1
        if sy1 > sy0:
            if cache is None:
                blit_wall_tile(screen, frame, tex_x, x0, strip_w, seg_top, tile_h,
                               sy0, sy1 - sy0, shade)
            else:
                _blit_tile_cached(screen, cache, frame, th, tex_x, x0, strip_w,
                                  seg_top, tile_h, sy0, sy1 - sy0, shade_v)


def render_raycast_view(room, screen: pygame.Surface):
    """Render the room as a first-person raycast projection instead of
    the normal top-down view. See docs/RAYCAST_2_5D_PLAN.md."""
    st = raycast_state(room)
    cfg = st["camera"]
    cell_size = int(cfg.get('cell_size', 32))
    wall_h = clamp_wall_height(cfg.get('wall_height', RAYCAST_WALL_HEIGHT))
    # Rebuilt every frame -- see build_raycast_walls's docstring. Billboards
    # (below) already read room.instances fresh each frame with no cache;
    # walls now do too, so a create_instance/destroy_instance of a solid
    # object is visible in the very next frame, not just on room re-entry.
    build_raycast_walls(room, cell_size)
    # Stairs (S5): the floor-height map from step instances, also rebuilt
    # every frame. Empty -> no step in the room -> the unchanged single-hit
    # path below; non-empty -> the column walk.
    heights, step_textures = build_floor_heights(
        room, cell_size, max_floor_height(cell_size, wall_h, RAYCAST_EYE_HEIGHT))
    stairs = bool(heights)

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
    # Eye height in room px: the floor under the camera's centre plus the
    # eye height. (S8 eases it between steps instead of snapping.)
    floor_z = heights.get((int(cam_x // cell_size), int(cam_y // cell_size)), 0.0) \
        if stairs else 0.0
    eye_z = floor_z + RAYCAST_EYE_HEIGHT * cell_size
    eye_cells = eye_z / cell_size

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
    if floor_sprite is not None and not stairs:   # stairs rooms: cast_stairs_floor
        cast_floor_plane(screen, floor_sprite.get_frame(0),
                               cam_cx, cam_cy, facing_screen_rad, fov_rad,
                               cast_res, ceiling=False, view_h=view_h,
                               plane_height=eye_cells if stairs else None)
    if ceil_sprite is not None and sky_sprite is None:
        # The ceiling plane is the top of the walls: wall_height above the
        # floor, so (wall_height - eye) above the eye.
        cast_floor_plane(screen, ceil_sprite.get_frame(0),
                               cam_cx, cam_cy, facing_screen_rad, fov_rad,
                               cast_res, ceiling=True, view_h=view_h,
                               plane_height=(wall_h - eye_cells) if stairs
                               else wall_h - RAYCAST_EYE_HEIGHT)

    # Phase 5: sample a vertical texture strip per wall column (per the
    # plan). Off -> flat colour (the pre-Phase-5 look), also the automatic
    # fallback when no texture is available. A `wall_texture` sprite name
    # in the camera config textures EVERY wall with one image (the usual
    # choice — the derived thin edge-wall collision sprites are not real
    # wall art); without it, each wall samples its own instance sprite.
    textured = bool(cfg.get('wall_textured', True))
    wall_tiles = wall_h / RAYCAST_TEXTURE_HEIGHT     # 1.0 for the default walls
    n_tiles = max(1, int(math.ceil(wall_tiles - 1e-9)))
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
    sf = None
    stairs_layouts = []
    if stairs:
        sprites = getattr(room, '_all_sprites', {}) or {}
        sf = {
            "heights": heights, "step_textures": step_textures, "sprites": sprites,
            "cam_x": cam_x, "cam_y": cam_y, "eye_z": eye_z, "floor_z": floor_z,
            "wall_top_z": wall_h * cell_size, "cell_size": cell_size,
            "max_cells": render_distance_cells, "half_h": half_h, "view_h": view_h,
            "col_width": col_width, "textured": textured,
            "wall_texture": wall_texture, "wall_color": wall_color,
            "floor_color": floor_color,
            "max_dist": render_distance_cells * cell_size,
            "strip_cache": {},          # scaled wall/riser strips, this frame only
        }
    for col in range(num_columns):
        camera_x = 2.0 * (col + 0.5) / num_columns - 1.0
        ray_offset = math.atan(plane_tan * camera_x)
        ray_angle = facing_screen_rad + ray_offset
        if stairs:
            lay = _layout_stairs_column(room, sf, ray_angle, math.cos(ray_offset))
            stairs_layouts.append(lay)
            col_wall_dist[col] = lay["wall_dist"]
            continue
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
        # tile_h: the projected height of ONE texture tile (the whole wall
        # when wall_height is the default). y_tile0: the top of the bottom
        # tile, the wall's top for a default wall. Tiles stack upward from
        # the floor; the wall's real top is (wall_tiles - 1) tiles higher.
        tile_h = view_h * cell_size * RAYCAST_TEXTURE_HEIGHT / max(corrected, 1e-4)
        y_tile0 = half_h - tile_h * _EYE_FROM_TILE_TOP
        y_wall_top = y_tile0 - (wall_tiles - 1.0) * tile_h
        x0 = int(col * col_width)
        x1 = int((col + 1) * col_width)
        strip_w = max(1, x1 - x0)
        y0 = max(0, int(math.floor(y_wall_top)))
        y1 = min(view_h, int(math.ceil(y_tile0 + tile_h)))
        vis_h = y1 - y0
        if vis_h <= 0:
            continue

        # Subtle side hint + distance falloff (see wall_shade).
        shade = wall_shade(side, corrected,
                       render_distance_cells * cell_size)
        tex_sprite = wall_texture if wall_texture is not None else wall_sprite
        if textured and tex_sprite is not None:
            frame = tex_sprite.get_frame(0)
            tex_x = min(frame.get_width() - 1, max(0, int(tex_u * frame.get_width())))
            # One cropped blit per texture tile, bottom tile first; the top
            # tile is cut at the wall's real top (its lower part shows).
            for k in range(n_tiles):
                seg_top = y_tile0 - k * tile_h
                sy0 = max(0, int(math.floor(max(seg_top, y_wall_top))))
                sy1 = min(view_h, int(math.ceil(seg_top + tile_h)))
                if sy1 - sy0 > 0:
                    blit_wall_tile(screen, frame, tex_x, x0, strip_w,
                                   seg_top, tile_h, sy0, sy1 - sy0, shade)
        else:
            color = tuple(int(c * shade) for c in wall_color)
            screen.fill(color, (x0, y0, strip_w, vis_h))

    if stairs:
        # Treads need a cast when the floor or any raised cell is textured.
        top_frames = {}
        for cell, (top_name, _side) in step_textures.items():
            spr = sf["sprites"].get(top_name) if top_name else None
            if spr is not None:
                top_frames[cell] = spr.get_frame(0)
        floor_frame = floor_sprite.get_frame(0) if floor_sprite is not None else None
        floor_cast = floor_frame is not None or bool(top_frames)
        if floor_cast:
            cast_stairs_floor(screen, stairs_layouts, sf, floor_frame, top_frames,
                              facing_screen_rad, fov_rad, cast_res)
        for col, lay in enumerate(stairs_layouts):
            _draw_stairs_column(screen, sf, col, lay, floor_cast)

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
        if is_step(inst):
            continue        # a step is floor, drawn by the stairs pass, not a cutout
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
        billboards.append((corrected, rel_angle, inst, bx, by))

    # Farthest first (painter's algorithm) so nearer billboards draw
    # over farther ones where sprites overlap.
    billboards.sort(key=lambda b: -b[0])
    for corrected, rel_angle, inst, bx, by in billboards:
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
        if stairs:
            # Stairs (S7): a billboard stands on the floor of its own cell,
            # placed relative to it exactly as on flat ground (centred one eye
            # height above the floor) -- so it moves by the difference between
            # the camera's eye and that cell's "eye". Zero on flat ground.
            b_floor = heights.get((int(bx // cell_size), int(by // cell_size)), 0.0)
            y_top_f += (eye_z - (b_floor + RAYCAST_EYE_HEIGHT * cell_size)) \
                * view_h / max(corrected, 1e-4)
        y0 = max(0, int(math.floor(y_top_f)))
        y1 = min(view_h, int(math.ceil(y_top_f + full_h)))
        vis_h = y1 - y0
        if vis_h <= 0:
            continue
        rot_frames = int(getattr(inst, 'billboard_rotation_frames', 0) or 0)
        if rot_frames > 1:
            frame_idx = billboard_rotation_frame(
                bx, by, inst.facing_angle, cam_x, cam_y, rot_frames)
        else:
            frame_idx = inst.image_index
        frame = inst.sprite.get_frame(frame_idx)
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
                    col_h = blit_h
                    if stairs:
                        # Steps nearer than the billboard hide its lower rows:
                        # draw only above the free-rows limit the column walk
                        # had reached before this distance (S7).
                        limit = _clip_before(stairs_layouts[col_idx]["occluders"],
                                             corrected, view_h)
                        if y0 + col_h > limit:
                            col_h = max(0, limit - y0)
                    if col_h > 0:
                        screen.blit(scaled, (screen_x, y0),
                                    (slice_x, off, 1, col_h))
            slice_x += 1

    # DOOM-bar letterbox: fill the reserved band below the 3D view opaque
    # black, unconditionally (like the ceiling/floor fills) and BEFORE the
    # draw-event pass, so draw_doom_hud paints over a clean backdrop. No-op
    # when view_h == h (the default full-height case).
    if view_h < h:
        screen.fill((0, 0, 0), (0, view_h, w, h - view_h))


def _clip_before(occluders, dist, view_h):
    """The first screen row hidden, in one column, for something at corrected
    distance ``dist``: the column walk's free-rows limit after the last
    crossing nearer than it (occluders run near -> far). view_h = nothing
    nearer hides anything."""
    limit = float(view_h)
    for d, clip in occluders:
        if d >= dist:
            break
        limit = clip
    return _row(limit)


def _layout_stairs_column(room, sf, ray_angle, cos_off):
    """One column of a room with steps: the ray walk and its layout."""
    cell_size = sf["cell_size"]
    crossings, hit = cast_ray_steps(room, sf["cam_x"], sf["cam_y"], ray_angle,
                                    cell_size, sf["max_cells"], sf["heights"])
    return layout_column(crossings, hit, sf["floor_z"], sf["eye_z"], sf["wall_top_z"],
                         cell_size, cos_off, sf["half_h"], sf["view_h"], sf["max_cells"])


def _draw_stairs_column(screen, sf, col, lay, floor_cast):
    """Draw one laid-out column: raised treads (flat, only when the floor is
    not cast), then risers and the wall at full resolution -- over the
    low-res floor, so their edges stay crisp."""
    cell_size = sf["cell_size"]
    x0 = int(col * sf["col_width"])
    strip_w = max(1, int((col + 1) * sf["col_width"]) - x0)
    view_h = sf["view_h"]
    if not floor_cast:
        # Flat floor: raised treads in the floor colour (the ground is the
        # floor fill already).
        for y_top, y_bot, height, _d in lay["treads"]:
            if height > 0:
                r0, r1 = max(0, _row(y_top)), min(view_h, _row(y_bot))
                if r1 > r0:
                    screen.fill(sf["floor_color"], (x0, r0, strip_w, r1 - r0))
    # Risers: the step's side texture, else the wall texture, else flat.
    for y_top, y_bot, d, side, tex_u, cell, _lo, _hi in lay["risers"]:
        frame = None
        if sf["textured"]:
            name = sf["step_textures"].get(cell, ("", ""))[1]
            spr = sf["sprites"].get(name) if name else None
            spr = spr if spr is not None else sf["wall_texture"]
            frame = spr.get_frame(0) if spr is not None else None
        draw_wall_rows(screen, frame, sf["wall_color"], tex_u, x0, strip_w, d,
                       sf["eye_z"], cell_size, sf["half_h"], view_h,
                       _row(y_top), _row(y_bot),
                       wall_shade(side, d, sf["max_dist"]), sf["strip_cache"])
    wall = lay["wall"]
    if wall is not None:
        y_top, y_bot, d, side, tex_u, wall_sprite = wall
        frame = None
        if sf["textured"]:
            spr = sf["wall_texture"] if sf["wall_texture"] is not None else wall_sprite
            frame = spr.get_frame(0) if spr is not None else None
        draw_wall_rows(screen, frame, sf["wall_color"], tex_u, x0, strip_w, d,
                       sf["eye_z"], cell_size, sf["half_h"], view_h,
                       _row(y_top), _row(y_bot),
                       wall_shade(side, d, sf["max_dist"]), sf["strip_cache"])


def cast_stairs_floor(screen, layouts, sf, floor_frame, top_frames,
                      facing_screen_rad, fov_rad, res):
    """The floor of a room with steps, cast COLUMN-major (stairs plan S6).

    Every low-res floor pixel belongs to one tread span of its column (from
    layout_column) and is cast at THAT tread's height:
        distance_cells = ((eye_z - h) / cell) * view_h / (y - horizon)
    then textured like cast_floor_plane (one texture tile per grid cell).
    The texture is the cell's step top texture (``top_frames``: cell ->
    frame, only cells that have one), else ``floor_frame``, else the flat
    floor colour. Each pixel is cast exactly once -- measured in the S2
    spike as cheaper than casting the ground row-major and re-casting the
    treads.

    A low-res block can straddle a tread's edge: it takes the nearest
    tread at or below its sample row (the farthest one above the last
    span), and the risers and walls drawn afterwards at full resolution
    cover whatever it overhangs -- so no block is ever left unpainted.
    """
    w = screen.get_width()
    view_h = sf["view_h"]
    half_h = view_h // 2                     # as cast_floor_plane
    region_h = view_h - half_h
    if region_h <= 0:
        return
    cell_size = sf["cell_size"]
    eye_cells = sf["eye_z"] / cell_size
    cam_cx = sf["cam_x"] / cell_size
    cam_cy = sf["cam_y"] / cell_size
    dir_x, dir_y = math.cos(facing_screen_rad), math.sin(facing_screen_rad)
    plane = math.tan(fov_rad / 2)
    plane_x, plane_y = -dir_y * plane, dir_x * plane
    rdx0, rdy0 = dir_x - plane_x, dir_y - plane_y
    rdx1, rdy1 = dir_x + plane_x, dir_y + plane_y

    sw = max(1, w // res)
    sh = max(1, region_h // res)
    small = pygame.Surface((sw, sh))
    small.fill(sf["floor_color"])
    put = small.set_at
    floor = math.floor
    flat = sf["floor_color"]
    if floor_frame is not None:
        f_get = floor_frame.get_at
        f_tw, f_th = floor_frame.get_size()
    ncol = len(layouts)
    col_width = sf["col_width"]
    for i in range(sw):
        sx = i * res
        c = int(sx / col_width)
        if c >= ncol:
            c = ncol - 1
        spans = layouts[c]["treads"]
        if not spans:
            continue
        t = sx / w
        rdx = rdx0 + (rdx1 - rdx0) * t
        rdy = rdy0 + (rdy1 - rdy0) * t
        # spans run near -> far, i.e. bottom -> top of the screen.
        k = 0
        n = len(spans)
        for j in range(sh - 1, -1, -1):
            y = half_h + j * res
            while k < n - 1 and y < spans[k][0]:
                k += 1
            height = spans[k][2]
            dz = eye_cells - height / cell_size
            if dz <= 0:
                continue
            p = j * res
            if p <= 0:
                p = 1
            rowd = dz * view_h / p
            fx = cam_cx + rowd * rdx
            fy = cam_cy + rowd * rdy
            frame = None
            if top_frames and height > 0:
                frame = top_frames.get((int(floor(fx)), int(floor(fy))))
            if frame is not None:
                tw, th = frame.get_size()
                tx = int(tw * (fx - floor(fx)))
                ty = int(th * (fy - floor(fy)))
                if tx >= tw:
                    tx = tw - 1
                if ty >= th:
                    ty = th - 1
                put((i, j), frame.get_at((tx, ty)))
            elif floor_frame is not None:
                tx = int(f_tw * (fx - floor(fx)))
                ty = int(f_th * (fy - floor(fy)))
                if tx >= f_tw:
                    tx = f_tw - 1
                if ty >= f_th:
                    ty = f_th - 1
                put((i, j), f_get((tx, ty)))
            else:
                put((i, j), flat)
    screen.blit(pygame.transform.scale(small, (w, region_h)), (0, half_h))


def blit_wall_tile(screen, frame, tex_x, x0, strip_w, y_top, full_h, y0, vis_h,
                   shade):
    """Draw the visible rows [y0, y0+vis_h) of one wall texture tile whose
    full (unclamped) projection spans [y_top, y_top+full_h), sampling texture
    column tex_x, darkened by shade."""
    th = frame.get_height()
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


def cast_floor_plane(screen, frame, cam_cx, cam_cy,
                     facing_screen_rad, fov_rad, res, ceiling=False,
                     view_h=None, plane_height=None):
    """Low-res floor/ceiling texture casting (Phase 5). Renders the ground
    (or ceiling) plane into a downsampled surface, then upscales — full-res
    per-pixel casting is ~13x too slow in pure Python (timing spike).

    The plane is sampled in CELL units so the texture tiles once per grid
    cell and lines up with the wall bases. Row distance is derived from the
    same projection the wall pass uses, so floor and walls meet seamlessly:
    rowDistance_cells = (plane_height*h) / (y - horizon), where plane_height
    is the plane's distance from the eye in cells -- RAYCAST_EYE_HEIGHT for
    the floor (the default), wall_height - RAYCAST_EYE_HEIGHT for the
    ceiling. The two FOV-edge ray
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
    # Distance between the eye and the plane, in cells: the floor is
    # RAYCAST_EYE_HEIGHT below the eye, like the wall pass's floor line. (It
    # used 0.5 here until S1 -- the pre-1.5-walls value -- which sampled the
    # floor under a wall's base at 2/3 of the wall's distance; see
    # docs/RAYCAST_STAIRS_PLAN.md, F1.)
    if plane_height is None:
        plane_height = RAYCAST_EYE_HEIGHT
    pos_z = plane_height * view_h

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
