#!/usr/bin/env python3
"""Block World renderer -- Phases 2a-2c of docs/VOXEL_WORLD_PLAN.md: a
first-person view of a world whose blocks STACK, which you can look up and
down in.

Reuses the SHAPE of extensions/raycast_2_5d/renderer.py (DDA ray marching,
per-column screen strips, camera-plane projection, fisheye correction) but
the hit test is genuinely different: raycast derives thin WALL EDGES from
sprite instances and a ray stops at a specific edge; a voxel world's blocks
each fill a whole grid cell, so this is the more standard "cell occupancy"
DDA (Amanatides & Woo), stepping cell by cell.

Where 2a stopped a ray at the first occupied cell on ONE layer and drew a
single cube centred on the horizon, 2b marches on and draws the whole
vertical STACK at each cell -- so a wall can be two blocks high, a step can
be climbed, and standing on a ledge lets you see over things. The vertical
projection is one line of maths, spelled out in render_block_world_view's
own docstring.

Looking up and down (2c) is a Y-shear -- see horizon_for -- so it costs the
horizontal DDA nothing. No sky, no billboards: later-phase work, mirroring
how raycast staged its own texturing in over several phases.

What ``room`` must provide is ordinary GameRoom API, none of it owned by
this extension: ``parse_color()``, ``_find_first_instance()``,
``_sprite_top_left()`` -- plus ``extension_state`` (the per-room namespace,
reached through ``state.py``).
"""

import math

import pygame

from .state import (block_world_state, get_block, block_face_textures,
                    column_index, is_transparent)

_TEXTURE_CACHE = {}


def _load_texture(path):
    """Lazily load + cache a block face texture. Matches the convert_alpha
    convention runtime/game_runner.py's GameSprite already uses for sprite
    loading -- proven safe under this repo's headless
    (SDL_VIDEODRIVER=dummy) test setup, so no separate fallback is needed."""
    surface = _TEXTURE_CACHE.get(path)
    if surface is None:
        surface = pygame.image.load(path).convert_alpha()
        _TEXTURE_CACHE[path] = surface
    return surface


def march_ray(room, px: float, py: float, angle_rad: float,
              cell_size: int, max_cells: int):
    """Walk the DDA cell by cell, yielding one tuple per cell ENTERED:

        (map_x, map_y, entry_dist, exit_dist, side, tex_u)

    both distances in pixels from the ray origin. Phase 2b needs the exit
    distance as well as the entry one: a block's TOP face is a horizontal
    surface running from the near vertical face (entry) back to the far one
    (exit), so projecting it needs both edges.

    This is the single DDA in the extension -- cast_ray below is a thin
    first-hit wrapper over it, and Phase 3's block picking should reuse it
    too rather than growing a third copy of the same stepping code.

    The ray does NOT yield the cell the origin is already inside; a camera
    standing inside a block is a caller bug, not a thing to render.
    """
    px_cell, py_cell = px / cell_size, py / cell_size
    dx, dy = math.cos(angle_rad), math.sin(angle_rad)
    map_x, map_y = int(math.floor(px_cell)), int(math.floor(py_cell))

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

    for _ in range(max_cells):
        # The entry distance is deliberately recovered as (side - delta)
        # AFTER the step rather than captured before it. Those differ by an
        # ULP in floating point, and the pre-step value -- though marginally
        # the more accurate one -- shifts a strip edge by a pixel in the
        # occasional column where the rounding lands either side of an
        # integer. Phase 2a's renderer computed it this way, so matching it
        # keeps a single-layer world provably pixel-identical and leaves any
        # future difference meaning a real regression.
        if side_x < side_y:
            side_x += delta_x
            map_x += step_x
            side = 0
            entry = side_x - delta_x
        else:
            side_y += delta_y
            map_y += step_y
            side = 1
            entry = side_y - delta_y
        # Texture-U: fractional position along the hit face, same derivation
        # as raycast_2_5d.renderer.cast_ray.
        if side == 0:
            wall_coord = py_cell + entry * dy
            if dx > 0:
                wall_coord = -wall_coord
        else:
            wall_coord = px_cell + entry * dx
            if dy < 0:
                wall_coord = -wall_coord
        tex_u = wall_coord - math.floor(wall_coord)
        exit_cells = side_x if side_x < side_y else side_y
        yield (map_x, map_y, max(entry, 1e-4) * cell_size,
               exit_cells * cell_size, side, tex_u)


def cast_ray(room, px: float, py: float, z_layer: int, angle_rad: float,
             cell_size: int, max_cells: int):
    """First-hit raycast through the block grid at a SINGLE z_layer: march
    until the ray enters an occupied cell -- not "crosses an edge" (see this
    module's docstring for why that differs from raycast_2_5d's own
    cast_ray).

    Returns (distance_in_pixels, side, hit, tex_u, block_type):
      - side is 0 for a vertical face (x-step hit) or 1 for a horizontal one
        (y-step hit), the same convention raycast_2_5d uses -- a free depth
        cue for shading.
      - hit is False when the ray reached max range without entering an
        occupied cell; the caller must draw no strip for that column.
      - tex_u in [0, 1) is the horizontal texture coordinate along the hit
        face; block_type is the block id at the hit cell (or None on a miss).

    Since 2b the renderer draws every layer and uses march_ray directly, so
    this is no longer on the render path -- it stays as the single-layer
    query (Phase 3 picking, tests, anything wanting one answer not a stack).
    """
    side = 0
    for map_x, map_y, dist, _exit, side, tex_u in march_ray(
            room, px, py, angle_rad, cell_size, max_cells):
        block_type = get_block(room, map_x, map_y, z_layer)
        if block_type is not None:
            return dist, side, True, tex_u, block_type
    return max(float(max_cells), 1e-4) * cell_size, side, False, 0.0, None


def pick_block(room, cam_x, cam_y, layer, angle_rad, cell_size, reach):
    """What the camera's centre ray is pointing at (Phase 3).

    Returns ``(target, placement)``, each an ``(x, y, z)`` cell or None:

    - ``target`` is the first cell along the ray that holds a block -- what
      breaking removes.
    - ``placement`` is the empty cell a new block should occupy. In order of
      preference: the first GAP the ray passes through, else the cell
      immediately before the target, else — when the ray reaches nothing
      within ``reach`` — the cell directly ahead. None when there is nowhere
      valid (the camera is already up against a block, so the only cell
      "before" the target is the one the camera is standing in).

    A **gap** is an empty cell at the camera's layer with a block resting on
    top of it: the hole left by knocking a block out of a wall. It gets
    priority because otherwise such a hole can never be refilled — a
    one-cell-thick wall has no cell "before the hit" that IS the hole, from
    either side, so the block always lands somewhere past it. That was a real
    dead end found by playtesting, not a theoretical one. An open doorway is
    not a gap (nothing above it) and so is never blocked up by accident.

    Note the target still reaches PAST a gap, so the crosshair lights up on
    whatever is really behind the hole and can still be broken. Only where
    the new block goes changes.

    **A returned placement is always air**, and callers may rely on it: the
    march only advances past cells it has read as empty, and a first cell
    that is occupied returns immediately with no placement at all. Nothing
    downstream needs to re-check before building there.

    Deliberately the same march the renderer uses, at the same angle the
    centre column is drawn from, so you break exactly what is under the
    middle of the screen. A second raycast for picking would be a second
    thing to keep in step.

    Phase 2b's level camera constrains this: the ray runs horizontally at eye
    height, so it can only ever reach blocks on the camera's OWN layer. You
    build outwards at your feet and climb what you have built -- digging down
    and placing onto ground below you need the free look Phase 2c is for.

    Transparency is not consulted: glass is pickable like anything else, or
    it could not be broken.
    """
    first = None
    prev = None
    gap = None
    for map_x, map_y, _entry, _exit, _side, _tex_u in march_ray(
            room, cam_x, cam_y, angle_rad, cell_size, reach):
        if first is None:
            first = (map_x, map_y)
        if get_block(room, map_x, map_y, layer) is not None:
            if gap is not None:
                return (map_x, map_y, layer), gap
            return (map_x, map_y, layer), (prev[0], prev[1], layer) if prev else None
        if gap is None and get_block(room, map_x, map_y, layer + 1) is not None:
            gap = (map_x, map_y, layer)   # a hole with a block resting on it
        prev = (map_x, map_y)
    if gap is not None:
        return None, gap
    return None, (first[0], first[1], layer) if first else None


def project_point(wx, wy, wz, cam_x, cam_y, eye_z, facing_screen_rad,
                  fov_rad, screen_w, screen_h, cell_size, horizon=None):
    """Screen (x, y) for a world point, or None if it is at or behind the
    camera plane.

    The inverse of what the render loop does per column, and deliberately
    built from the same two facts, so an overlay lands exactly on the
    geometry underneath it:

    - depth is the CAMERA-PLANE distance (the component along the facing
      direction), the same already-fisheye-corrected quantity the wall pass
      shades and scales by;
    - the vertical mapping is render_block_world_view's one line,
      ``y = horizon + (eye_z - wz) * (screen_h * cell_size / depth)``.

    Horizontally, a column's ray offset satisfies
    ``lateral / depth == tan(fov/2) * camera_x`` with camera_x running -1 to
    +1 across the screen, so inverting that gives the column a point falls
    in. Screen-right is the facing direction turned +90 degrees in this
    y-down frame, i.e. ``(-dir_y, dir_x)``.
    """
    dir_x, dir_y = math.cos(facing_screen_rad), math.sin(facing_screen_rad)
    rel_x, rel_y = wx - cam_x, wy - cam_y
    depth = rel_x * dir_x + rel_y * dir_y
    if depth <= 1e-6:
        return None
    lateral = rel_x * -dir_y + rel_y * dir_x
    plane_tan = math.tan(fov_rad / 2)
    sx = screen_w * 0.5 * (1.0 + lateral / (depth * plane_tan))
    if horizon is None:
        horizon = screen_h * 0.5
    sy = horizon + (eye_z - wz) * (screen_h * cell_size / depth)
    return sx, sy


def screen_ray(sx, sy, facing_screen_rad, fov_rad, screen_w, screen_h,
               cell_size, horizon=None):
    """The 3D ray through a screen pixel, as ``(angle_rad, z_per_px)``.

    A level camera constrains the forward AXIS to horizontal; it does not
    make every ray horizontal. Each pixel still corresponds to a real ray
    sloping up or down, which is exactly what unproject_to_plane relies on.
    Reading that slope out explicitly is what lets picking work in three
    dimensions without the renderer gaining pitch.

    ``z_per_px`` is the change in height, in cells, per pixel travelled along
    the ray: negative below the horizon (descending), zero on it. Its
    magnitude is bounded by the screen: at the very bottom of a 600px view
    the ray drops about half a cell per cell travelled, roughly 26 degrees.
    That IS the vertical field of view, and it is why you cannot look
    straight down -- the limit Phase 2c exists to lift.
    """
    camera_x = 2.0 * sx / screen_w - 1.0
    offset = math.atan(math.tan(fov_rad / 2) * camera_x)
    if horizon is None:
        horizon = screen_h * 0.5
    z_per_px = -(sy - horizon) * math.cos(offset) / (screen_h * cell_size)
    return facing_screen_rad + offset, z_per_px


def pick_voxel(room, cam_x, cam_y, eye_z, angle_rad, z_per_px, cell_size,
               reach, z_min=-64, z_max=256):
    """March a 3D ray and return ``(target, placement)``.

    ``target`` is the first solid voxel it enters. ``placement`` prefers the
    same GAP pick_block prefers -- an empty voxel with a solid one directly
    above it (x, y, z+1) -- generalised from "cell" to "voxel": whichever
    empty voxel the ray reaches first that has something resting on it is
    remembered and preferred over whatever voxel merely happens to be next
    to the eventual hit. Without that, a hole punched through a wall stops
    being refillable the moment open space follows it before the ray hits
    something else -- see pick_block's docstring for the playtest that found
    this. Absent a gap, placement is the voxel on the near side of whichever
    FACE the ray came through, so pointing at a top face places on top and a
    side face places beside it -- no case analysis, it falls out of tracking
    the previous voxel. On a total miss (nothing within reach and no gap
    seen), placement is the FIRST voxel entered: build directly ahead, not
    wherever the march gave up.

    This is the general form of pick_block, and now literally: at
    z_per_px == 0 every voxel visited sits on the one layer eye_z floors to,
    one per cell, in the same order gap-then-hit-then-fallback -- the same
    walk, with the same result. The two coexist because the ACTIONS have a
    crosshair and no mouse: their ray is the centre column at the horizon,
    where z_per_px is 0 and this reduces to that walk exactly.

    Reuses the one DDA for the horizontal steps and tracks height across each
    cell's entry and exit distance, so a column the ray passes through
    diagonally has every layer it clips checked in ray order.
    """
    first = None
    prev = None
    gap = None
    for map_x, map_y, entry, exit_d, _side, _tex_u in march_ray(
            room, cam_x, cam_y, angle_rad, cell_size, reach):
        z_entry = eye_z + z_per_px * entry
        z_exit = eye_z + z_per_px * exit_d
        low, high = (z_entry, z_exit) if z_entry <= z_exit else (z_exit, z_entry)
        low = max(int(math.floor(low)), z_min)
        high = min(int(math.floor(high)), z_max)
        if high < low:
            continue                      # the ray left the world vertically
        layers = range(low, high + 1) if z_per_px >= 0 else range(high, low - 1, -1)
        for layer in layers:
            if first is None:
                first = (map_x, map_y, layer)
            if get_block(room, map_x, map_y, layer) is not None:
                if gap is not None:
                    return (map_x, map_y, layer), gap
                return (map_x, map_y, layer), prev
            if gap is None and get_block(room, map_x, map_y, layer + 1) is not None:
                gap = (map_x, map_y, layer)   # a hole with a block resting on it
            prev = (map_x, map_y, layer)
    if gap is not None:
        return None, gap
    return None, first


def unproject_to_plane(sx, sy, plane_z, cam_x, cam_y, eye_z,
                       facing_screen_rad, fov_rad, screen_w, screen_h,
                       cell_size, horizon=None):
    """Where a screen point lands on the horizontal plane at height
    ``plane_z``: returns world ``(x, y)`` in pixels, or None if that ray
    never meets the plane.

    The exact inverse of project_point, which is what makes a mouse cursor
    land on the cell it appears to be over. Rearranging that function's two
    mappings:

        depth   = (eye_z - plane_z) * screen_h * cell_size / (sy - horizon)
        lateral = depth * tan(fov/2) * (2 * sx / screen_w - 1)

    and the world point is the camera plus ``depth`` along the facing
    direction plus ``lateral`` along screen-right.

    Returns None when the screen point is on the wrong side of the horizon
    for the plane -- looking at or above it never meets a floor below you,
    and the divide would run away to infinity as it is approached.
    """
    if horizon is None:
        horizon = screen_h * 0.5
    drop = sy - horizon
    height = eye_z - plane_z
    if height == 0 or (drop > 0) != (height > 0) or abs(drop) < 1e-6:
        return None
    depth = height * screen_h * cell_size / drop
    lateral = depth * math.tan(fov_rad / 2) * (2.0 * sx / screen_w - 1.0)
    dir_x, dir_y = math.cos(facing_screen_rad), math.sin(facing_screen_rad)
    return (cam_x + dir_x * depth + -dir_y * lateral,
            cam_y + dir_y * depth + dir_x * lateral)


def draw_cell_outline(screen, cell, cam_x, cam_y, eye_z, facing_screen_rad,
                      fov_rad, cell_size, color=(255, 255, 255), alpha=95,
                      width=1, horizon=None):
    """Outline the FLOOR square of a world cell -- the footprint a block
    would occupy if it were placed there.

    Returns True if anything was drawn. Skips silently when a corner falls at
    or behind the camera plane: a partly-behind quad projects to nonsense,
    and half an outline is worse than none.

    Drawn through a small translucent surface sized to the outline's own
    bounding box rather than a full-screen overlay, so a faint line costs a
    few hundred pixels a frame instead of a screen-sized allocation.
    """
    x, y, z = cell
    w, h = screen.get_size()
    corners = [(x * cell_size, y * cell_size),
               ((x + 1) * cell_size, y * cell_size),
               ((x + 1) * cell_size, (y + 1) * cell_size),
               (x * cell_size, (y + 1) * cell_size)]

    points = []
    for wx, wy in corners:
        projected = project_point(wx, wy, z, cam_x, cam_y, eye_z,
                                  facing_screen_rad, fov_rad, w, h, cell_size,
                                  horizon)
        if projected is None:
            return False
        points.append(projected)

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    left, top = int(math.floor(min(xs))) - width, int(math.floor(min(ys))) - width
    right, bottom = int(math.ceil(max(xs))) + width, int(math.ceil(max(ys))) + width
    left, top = max(0, left), max(0, top)
    right, bottom = min(w, right), min(h, bottom)
    if right <= left or bottom <= top:
        return False  # entirely off-screen

    overlay = pygame.Surface((right - left, bottom - top), pygame.SRCALPHA)
    pygame.draw.lines(overlay, tuple(color) + (alpha,), True,
                      [(px - left, py - top) for px, py in points], width)
    screen.blit(overlay, (left, top))
    return True


# --- wall shading -----------------------------------------------------
# A smaller, self-contained copy of raycast_2_5d.renderer's shading formula
# -- deliberately duplicated rather than imported, so each extension stays
# independently removable (see extensions/README.md).
SIDE_SHADE = 0.85
FOG_STRENGTH = 0.55
MIN_SHADE = 0.35

# Horizontal faces (Phase 2b). A top face catches the light and a bottom face
# is in shadow; without that split a stepped stack reads as one flat mass,
# since every face would otherwise share the vertical faces' shading.
TOP_SHADE = 1.15
BOTTOM_SHADE = 0.55

# How high the eye sits above the layer the feet are on.
#
# 1.5 makes the camera a TWO-BLOCK-TALL body, the way every block game does,
# and that is load-bearing rather than cosmetic: a block beside you has its
# top face at z = 1, so an eye at 0.5 is BELOW that surface and sees its
# underside. You cannot stack onto a block at your own level, at any pitch,
# because the face is pointing away from you. Playtesting found exactly that.
#
# Phases 2a and 2b drew 0.5 (2a centred a 1-cell cube on the horizon), which
# is why the pixel-identity proof recorded in the plan doc used that value.
# Changing the default is free only because no sample ships on this engine
# yet -- after Phase 5 it would not be.
DEFAULT_EYE_HEIGHT = 1.5

# Horizontal faces are cast every Nth screen row and the column upscaled.
# 4 matches raycast_2_5d's floor_cast_res default, chosen there by the same
# reasoning: full-res per-pixel casting is roughly an order of magnitude too
# slow in pure Python, and on a horizontal plane the rows between samples
# differ too little for the interpolation to show.
DEFAULT_TOP_CAST_RES = 4

# Looking up and down (Phase 2c) is a Y-SHEAR: the horizon slides along the
# screen and every other formula is left alone. That works because the whole
# renderer expresses height as
#     y = horizon + (eye_z - zval) * (screen_h * cell_size / distance)
# and because pitch does not change AZIMUTH -- a screen column still
# corresponds to the same ray, so the horizontal DDA is untouched.
#
# It is a shear, not a rotated camera: vertical edges stay vertical instead
# of converging. Doom did the same, and for a world made of cubes the
# parallel edges arguably read better than true perspective would. Past
# roughly this clamp the stretch stops being convincing, and tan() runs away.
MAX_PITCH_DEGREES = 70.0


def horizon_for(screen_h, pitch_degrees):
    """Screen row the horizon sits on for a given look angle.

    Positive pitch looks UP, which pushes the horizon DOWN the screen. The
    vertical focal length works out to exactly screen_h pixels -- a point one
    cell above the eye at one cell away lands screen_h * (cell/cell) from the
    horizon -- so the shift is simply ``screen_h * tan(pitch)``.
    """
    pitch = max(-MAX_PITCH_DEGREES, min(MAX_PITCH_DEGREES, float(pitch_degrees)))
    return screen_h * 0.5 + screen_h * math.tan(math.radians(pitch))


def wall_shade(side: int, corrected: float, max_dist: float) -> float:
    """Brightness multiplier in [MIN_SHADE, 1] for a wall strip."""
    side_factor = SIDE_SHADE if side == 1 else 1.0
    t = corrected / max_dist if max_dist > 0 else 0.0
    t = max(0.0, min(1.0, t))
    dist_factor = 1.0 - FOG_STRENGTH * t
    return max(MIN_SHADE, side_factor * dist_factor)


def face_shade(corrected: float, max_dist: float, facing: float) -> float:
    """Brightness for a HORIZONTAL face (top/bottom) at a given distance.

    Same fog curve as wall_shade so a stack's vertical and horizontal faces
    recede together, but with the top/bottom light constant in place of the
    x/y side hint. Clamped to 1.0 at the top so TOP_SHADE brightens a near
    face without blowing it out."""
    t = corrected / max_dist if max_dist > 0 else 0.0
    t = max(0.0, min(1.0, t))
    return max(MIN_SHADE, min(1.0, facing * (1.0 - FOG_STRENGTH * t)))


_AVG_COLOR_CACHE = {}


def face_average_color(path):
    """The average colour of a face texture, cached.

    Phase 2b draws horizontal faces as flat colour rather than mapping the
    texture per pixel. Per-pixel floor casting is the expensive step the
    raycast arc deliberately deferred on two of its three targets, and a
    step or a pit reads correctly without it -- what matters is that the top
    of a block is a distinct surface at the right screen position, not that
    its grain is visible. Textured tops belong with 2c's real 3D marching.
    """
    color = _AVG_COLOR_CACHE.get(path)
    if color is None:
        surface = _load_texture(path)
        try:
            color = pygame.transform.average_color(surface, consider_alpha=True)
        except TypeError:  # pygame < 2.1.3 has no consider_alpha
            color = pygame.transform.average_color(surface)
        color = tuple(int(c) for c in color[:3])
        _AVG_COLOR_CACHE[path] = color
    return color


def _occupied(stack, z):
    """Is layer z present in this cell's stack? Stacks are a handful of
    entries, so a scan beats building a set per cell per column."""
    for entry_z, _block_type in stack:
        if entry_z == z:
            return True
    return False


def _fully_covers(stack, eye_z, horizon, screen_h, px_per_cell):
    """Does this cell's stack hide everything behind it in this column?

    Only true for a GAPLESS stack of OPAQUE blocks. Two ways to be seen
    through, and both have to be excluded:

    - a hole in the stack, so the ray passes between blocks;
    - a transparent block (glass, water, ice), so the ray passes THROUGH one.

    Missing the second cost a real bug, reported from a playtest: a glass
    block looked right from the side and from a distance, then showed raw sky
    and floor through itself when you walked up to it face-on. Nothing was
    wrong with the compositing -- getting close simply made the glass big
    enough to satisfy the covers-the-screen test, which stopped the march, so
    the blocks it should have been compositing against were never drawn.
    Distance-dependent, which is why it read as a rendering glitch rather
    than an occlusion one."""
    lowest, highest = stack[0][0], stack[-1][0]
    if len(stack) != highest - lowest + 1:
        return False
    for _z, block_type in stack:
        if is_transparent(block_type):
            return False
    return (horizon + (eye_z - (highest + 1)) * px_per_cell <= 0
            and horizon + (eye_z - lowest) * px_per_cell >= screen_h)


def _draw_wall_strip(screen, x0, strip_w, y_top, full_h, shade,
                     texture_path, tex_u, flat_color):
    """One block's vertical face in one column."""
    screen_h = screen.get_height()
    y0 = max(0, int(math.floor(y_top)))
    y1 = min(screen_h, int(math.ceil(y_top + full_h)))
    vis_h = y1 - y0
    if vis_h <= 0:
        return

    if texture_path is None:
        screen.fill(tuple(int(c * shade) for c in flat_color),
                    (x0, y0, strip_w, vis_h))
        return

    frame = _load_texture(texture_path)
    tw, th = frame.get_width(), frame.get_height()
    tex_x = min(tw - 1, max(0, int(tex_u * tw)))
    # Sub-texel crop (see raycast_2_5d.renderer's identical comment):
    # rounding src_y per column would snap adjacent columns to different
    # texels on a close wall, so crop to the floor texel and carry the
    # remainder as a blit offset instead.
    texels_per_px = th / full_h
    src_y_f = (y0 - y_top) * texels_per_px
    src_y = max(0, min(th - 1, int(math.floor(src_y_f))))
    frac_px = (src_y_f - src_y) / texels_per_px
    need = int(math.ceil(vis_h * texels_per_px)) + 2
    src_h = max(1, min(th - src_y, need))
    dest_h = max(1, int(round(src_h / texels_per_px)))
    col_surf = frame.subsurface((tex_x, src_y, 1, src_h))
    strip = pygame.transform.scale(col_surf, (strip_w, dest_h))
    if shade < 1.0:
        v = int(shade * 255)
        strip.fill((v, v, v), special_flags=pygame.BLEND_RGB_MULT)
    off = max(0, min(dest_h - 1, int(round(frac_px))))
    covered = min(vis_h, dest_h - off)
    screen.blit(strip, (x0, y0), (0, off, strip_w, covered))
    if covered < vis_h:
        # dest_h ROUNDS the scaled column height while vis_h CEILS the span
        # it has to fill, so the two disagree by a pixel often enough to
        # leave a seam along the bottom of a wall -- 2a showed the flat floor
        # colour there, and 2b would show whatever block stands behind. Repeat
        # the strip's last row into the shortfall rather than rescaling the
        # whole strip to fit: rescaling shifts every texel above the seam too,
        # which recolours the entire wall to patch one row.
        last_row = strip.subsurface((0, dest_h - 1, strip_w, 1))
        screen.blit(pygame.transform.scale(last_row, (strip_w, vis_h - covered)),
                    (x0, y0 + covered))


def _draw_horizontal_face(screen, x0, strip_w, y_a, y_b, color):
    """A block's top or bottom face in one column, flat-shaded: the span
    between its near edge (the cell's entry distance) and its far edge (the
    exit). The fallback when texturing is off."""
    screen_h = screen.get_height()
    y0 = max(0, int(math.floor(min(y_a, y_b))))
    y1 = min(screen_h, int(math.ceil(max(y_a, y_b))))
    if y1 > y0:
        screen.fill(color, (x0, y0, strip_w, y1 - y0))


def _draw_horizontal_face_textured(screen, x0, strip_w, y_a, y_b, texture,
                                   cam_x, cam_y, dir_x, dir_y, cos_off,
                                   plane_z, eye_z, horizon, cell_size,
                                   shade, res):
    """The same face, texture-mapped.

    Inverting the projection gives the distance to the plane for a screen
    row directly -- ``y = horizon + (eye_z - zval) * (h * cell / dist)``
    rearranges to::

        dist_perp = (eye_z - plane_z) * h * cell_size / (y - horizon)

    so each row of the span is a known distance out along this column's ray,
    and the world point there gives the texel. Sampled every ``res`` rows
    into a one-pixel-wide column and upscaled, the trick
    raycast_2_5d.cast_floor_plane uses -- full-res per-pixel casting is an
    order of magnitude too slow in pure Python, and vertical neighbours on a
    horizontal plane differ little enough that the interpolation is close to
    free visually.

    Shading is applied once to the finished column with a hardware multiply,
    never per texel.
    """
    screen_h = screen.get_height()
    y0 = max(0, int(math.floor(min(y_a, y_b))))
    y1 = min(screen_h, int(math.ceil(max(y_a, y_b))))
    span = y1 - y0
    if span <= 0:
        return
    tw, th = texture.get_width(), texture.get_height()
    if tw <= 0 or th <= 0:
        return

    # Same sign top or bottom: looking down, eye_z > plane_z and the rows sit
    # below the horizon; looking up, both flip. The ratio stays positive.
    k = (eye_z - plane_z) * screen_h * cell_size
    samples = max(1, (span + res - 1) // res)
    tex_at = texture.get_at
    floor = math.floor
    inv_cell = 1.0 / cell_size

    def _texel(y):
        denom = y + 0.5 - horizon
        if -1e-6 < denom < 1e-6:
            denom = 1e-6 if denom >= 0 else -1e-6
        ray_dist = (k / denom) / cos_off
        gx = (cam_x + dir_x * ray_dist) * inv_cell
        gy = (cam_y + dir_y * ray_dist) * inv_cell
        tx = int(tw * (gx - floor(gx)))
        ty = int(th * (gy - floor(gy)))
        return tex_at((min(tx, tw - 1), min(ty, th - 1)))

    if samples == 1:
        # Most faces are a handful of rows -- a distant deck is hundreds of
        # one-sample slivers. Allocating a Surface and scaling it to fill a
        # span this short costs far more than the fill it replaces, and per
        # face per column that overhead was the dominant cost.
        color = _texel(y0)
        if shade < 1.0:
            color = tuple(int(c * shade) for c in color[:3])
        screen.fill(color, (x0, y0, strip_w, span))
        return

    column = pygame.Surface((1, samples))
    put = column.set_at

    for i in range(samples):
        put((0, i), _texel(y0 + i * res))

    strip = pygame.transform.scale(column, (strip_w, span))
    if shade < 1.0:
        v = int(shade * 255)
        strip.fill((v, v, v), special_flags=pygame.BLEND_RGB_MULT)
    screen.blit(strip, (x0, y0))


def render_block_world_view(room, screen: pygame.Surface):
    """Render the room as a first-person voxel view with stacked, pitchable
    layers (Phases 2b and 2c).

    Projection. A world height of ``zval`` cells projects to a single screen
    row:

        y = horizon + (eye_z - zval) * (screen_h * cell_size / distance)

    where ``eye_z`` is the camera's own height in cells and ``horizon`` is
    ``horizon_for(screen_h, pitch)`` -- looking up or down (2c) is a Y-shear
    on that one term, so this formula does not otherwise change with pitch.
    That is the whole of the vertical maths -- a block at layer z spans
    z..z+1, its top face sits at z+1, and everything else follows.

    Phase 2a is the special case pitch = 0, eye_z = 0.5, one layer at z = 0:
    the block's top lands at ``horizon - P/2`` and its bottom at
    ``horizon + P/2``, a cube centred on the horizon, exactly what 2a drew.
    That makes a single-layer, level, eye_z = 0.5 world pixel-identical
    through this code -- the compatibility proof this renderer was checked
    against. It is not a claim about what any real game looks like: the
    shipped default is DEFAULT_EYE_HEIGHT = 1.5 (a two-block-tall camera,
    needed for stacking -- see docs/VOXEL_WORLD_PLAN.md), under which even a
    single-layer world draws a top face 2a never had reason to draw. Nothing
    exposes eye_height as low as 0.5 through the action system; the geometry
    tests pin it there deliberately, to keep their closed-form numbers simple.

    Horizontal faces are flat shaded rather than texture-mapped per pixel by
    default (see face_average_color); top_cast_res turns per-pixel top/bottom
    texturing on.
    """
    st = block_world_state(room)
    cfg = st["camera"]
    cell_size = int(cfg.get("cell_size", 32))

    camera = room._find_first_instance(cfg.get("camera_object", ""))
    w, h = screen.get_size()
    horizon = horizon_for(h, cfg.get("pitch", 0.0))

    floor_color = room.parse_color(cfg.get("floor_color", "#3a2f1c"))
    ceiling_color = room.parse_color(cfg.get("ceiling_color", "#87CEEB"))
    screen.fill(ceiling_color, (0, 0, w, int(horizon)))
    screen.fill(floor_color, (0, int(horizon), w, h - int(horizon)))

    if camera is None:
        return  # nothing to render from -- flat floor/ceiling only

    # Ray origin is the camera instance's sprite CENTER, not its raw x/y
    # (top-left corner) -- a grid-aligned camera at rest has a raw x/y that
    # can land exactly on a cell boundary, which is the same exact-grid-line
    # DDA hazard raycast_2_5d hit (see its 2026-07-17 fix); centering in the
    # occupied cell avoids it here from the start rather than rediscovering
    # it later.
    _cx, _cy = room._sprite_top_left(camera)
    cam_x = _cx + camera._cached_width / 2
    cam_y = _cy + camera._cached_height / 2
    # z_layer is the layer the camera's body OCCUPIES; the eye sits partway
    # up it. Walking up a step is that number going up by one.
    eye_z = (int(cfg.get("z_layer", 0))
             + float(cfg.get("eye_height", DEFAULT_EYE_HEIGHT)))

    wall_color = room.parse_color(cfg.get("wall_color", "#8a8a8a"))
    fov_deg = cfg.get("fov", 66)
    fov_rad = math.radians(fov_deg)
    render_distance_cells = int(cfg.get("render_distance", 20))
    max_dist = render_distance_cells * cell_size
    num_columns = int(cfg.get("columns", min(w, 320)))
    col_width = w / num_columns

    # GM angle convention (0=right, 90=up, ...) -> screen-space radians,
    # matching raycast_2_5d's facing_angle-to-ray-space conversion.
    facing_screen_rad = math.radians(-camera.facing_angle)
    # CAMERA-PLANE projection (not uniform-angle) -- see raycast_2_5d's own
    # comment on why: uniform-angle sampling bends straight walls.
    plane_tan = math.tan(fov_rad / 2)
    textured = bool(cfg.get("wall_textured", True))
    # Horizontal faces cast every Nth row and upscale. 0 turns texturing of
    # tops off and falls back to the flat average colour, which is markedly
    # cheaper on a scene with a lot of visible deck.
    top_res = int(cfg.get("top_cast_res", DEFAULT_TOP_CAST_RES))
    top_textured = textured and top_res >= 1
    columns = column_index(room)

    for col in range(num_columns):
        camera_x = 2.0 * (col + 0.5) / num_columns - 1.0
        ray_offset = math.atan(plane_tan * camera_x)
        ray_angle = facing_screen_rad + ray_offset
        cos_off = math.cos(ray_offset)  # fisheye correction
        dir_x, dir_y = math.cos(ray_angle), math.sin(ray_angle)
        x0 = int(col * col_width)
        x1 = int((col + 1) * col_width)
        strip_w = max(1, x1 - x0)

        # Collect near->far so the occlusion early-out can stop the march,
        # then paint far->near.
        hits = []
        for map_x, map_y, d_entry, d_exit, side, tex_u in march_ray(
                room, cam_x, cam_y, ray_angle, cell_size, render_distance_cells):
            stack = columns.get((map_x, map_y))
            if not stack:
                continue  # air column -- floor/ceiling fill shows through
            near = max(d_entry * cos_off, 1e-4)
            far = max(d_exit * cos_off, near)
            hits.append((near, far, side, tex_u, stack))
            if _fully_covers(stack, eye_z, horizon, h, h * cell_size / near):
                break

        # Painter's algorithm. Every face is opaque, and within one cell the
        # faces of a stack tile the column without overlapping (a block's top
        # face sits directly above its own vertical face, and the next block
        # up starts exactly where this one ends), so the ordering only has to
        # be right BETWEEN cells.
        for near, far, side, tex_u, stack in reversed(hits):
            px_per_cell = h * cell_size / near
            px_per_cell_far = h * cell_size / far
            shade = wall_shade(side, near, max_dist)
            mid = (near + far) / 2.0
            for z, block_type in stack:
                faces = block_face_textures(block_type) if textured else None
                _draw_wall_strip(
                    screen, x0, strip_w,
                    horizon + (eye_z - (z + 1)) * px_per_cell, px_per_cell,
                    shade, faces["side"] if faces else None, tex_u, wall_color)

                # Top face: visible only from above it, and only when nothing
                # is stacked on top.
                if eye_z > z + 1 and not _occupied(stack, z + 1):
                    lit = face_shade(mid, max_dist, TOP_SHADE)
                    y_far = horizon + (eye_z - (z + 1)) * px_per_cell_far
                    y_near = horizon + (eye_z - (z + 1)) * px_per_cell
                    if top_textured:
                        _draw_horizontal_face_textured(
                            screen, x0, strip_w, y_far, y_near,
                            _load_texture(faces["top"]), cam_x, cam_y,
                            dir_x, dir_y, cos_off, z + 1, eye_z, horizon,
                            cell_size, lit, top_res)
                    else:
                        base = face_average_color(faces["top"]) if faces else wall_color
                        _draw_horizontal_face(
                            screen, x0, strip_w, y_far, y_near,
                            tuple(int(c * lit) for c in base))
                # Underside: only reachable by standing below an overhang,
                # which a pure heightmap never has -- but a hand-built world
                # can, and a missing face there is a hole straight to the sky.
                elif eye_z < z and not _occupied(stack, z - 1):
                    lit = face_shade(mid, max_dist, BOTTOM_SHADE)
                    y_near = horizon + (eye_z - z) * px_per_cell
                    y_far = horizon + (eye_z - z) * px_per_cell_far
                    if top_textured:
                        _draw_horizontal_face_textured(
                            screen, x0, strip_w, y_near, y_far,
                            _load_texture(faces["bottom"]), cam_x, cam_y,
                            dir_x, dir_y, cos_off, z, eye_z, horizon,
                            cell_size, lit, top_res)
                    else:
                        base = face_average_color(faces["bottom"]) if faces else wall_color
                        _draw_horizontal_face(
                            screen, x0, strip_w, y_near, y_far,
                            tuple(int(c * lit) for c in base))
