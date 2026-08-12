#!/usr/bin/env python3
"""Block World renderer -- Phase 2a of docs/VOXEL_WORLD_PLAN.md: a flat,
single-layer first-person view.

Reuses the SHAPE of extensions/raycast_2_5d/renderer.py (DDA ray marching,
per-column screen strips, camera-plane projection, fisheye correction) but
the hit test is genuinely simpler: raycast derives thin WALL EDGES from
sprite instances and a ray stops at a specific edge; a voxel world's blocks
each fill a whole grid cell, so this is the more standard "cell occupancy"
DDA (Amanatides & Woo) -- a ray steps cell by cell and stops at the first
occupied one, checked via state.get_block.

Phase 2a scope, deliberately: ONE z-layer (the camera's own layer -- no
looking up/down, no stacking multiple visible layers), flat-colour floor and
ceiling, textured wall columns using each block type's "side" face texture.
No floor/ceiling texturing, no sky, no billboards -- later-phase work,
mirroring how raycast staged its own texturing in over several phases.

What ``room`` must provide is ordinary GameRoom API, none of it owned by
this extension: ``parse_color()``, ``_find_first_instance()``,
``_sprite_top_left()`` -- plus ``extension_state`` (the per-room namespace,
reached through ``state.py``).
"""

import math

import pygame

from .state import block_world_state, get_block, block_face_textures

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


def cast_ray(room, px: float, py: float, z_layer: int, angle_rad: float,
             cell_size: int, max_cells: int):
    """DDA raycast from (px, py) (room pixel coords) at angle_rad (standard
    math convention: 0=+x, increasing counter-clockwise) through the block
    grid at z_layer, until it enters an occupied cell -- not "crosses an
    edge" (see this module's docstring for why that differs from
    raycast_2_5d's own cast_ray).

    Returns (distance_in_pixels, side, hit, tex_u, block_type):
      - side is 0 for a vertical face (x-step hit) or 1 for a horizontal one
        (y-step hit), the same convention raycast_2_5d uses -- a free depth
        cue for shading.
      - hit is False when the ray reached max range without entering an
        occupied cell; the caller must draw no strip for that column.
      - tex_u in [0, 1) is the horizontal texture coordinate along the hit
        face; block_type is the block id at the hit cell (or None on a miss).
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

    side = 0
    dist_cells = float(max_cells)
    for _ in range(max_cells):
        if side_x < side_y:
            side_x += delta_x
            map_x += step_x
            side = 0
        else:
            side_y += delta_y
            map_y += step_y
            side = 1
        block_type = get_block(room, map_x, map_y, z_layer)
        if block_type is not None:
            dist_cells = (side_x - delta_x) if side == 0 else (side_y - delta_y)
            # Texture-U: fractional position along the hit face, same
            # derivation as raycast_2_5d.renderer.cast_ray.
            if side == 0:
                wall_coord = py_cell + dist_cells * dy
                if dx > 0:
                    wall_coord = -wall_coord
            else:
                wall_coord = px_cell + dist_cells * dx
                if dy < 0:
                    wall_coord = -wall_coord
            tex_u = wall_coord - math.floor(wall_coord)
            return max(dist_cells, 1e-4) * cell_size, side, True, tex_u, block_type
    return max(dist_cells, 1e-4) * cell_size, side, False, 0.0, None


# --- wall shading -----------------------------------------------------
# A smaller, self-contained copy of raycast_2_5d.renderer's shading formula
# -- deliberately duplicated rather than imported, so each extension stays
# independently removable (see extensions/README.md).
SIDE_SHADE = 0.85
FOG_STRENGTH = 0.55
MIN_SHADE = 0.35


def wall_shade(side: int, corrected: float, max_dist: float) -> float:
    """Brightness multiplier in [MIN_SHADE, 1] for a wall strip."""
    side_factor = SIDE_SHADE if side == 1 else 1.0
    t = corrected / max_dist if max_dist > 0 else 0.0
    t = max(0.0, min(1.0, t))
    dist_factor = 1.0 - FOG_STRENGTH * t
    return max(MIN_SHADE, side_factor * dist_factor)


def render_block_world_view(room, screen: pygame.Surface):
    """Render the room as a flat, single-layer first-person voxel view.
    See this module's docstring for Phase 2a's scope."""
    st = block_world_state(room)
    cfg = st["camera"]
    cell_size = int(cfg.get("cell_size", 32))

    camera = room._find_first_instance(cfg.get("camera_object", ""))
    w, h = screen.get_size()
    half_h = h / 2

    floor_color = room.parse_color(cfg.get("floor_color", "#3a2f1c"))
    ceiling_color = room.parse_color(cfg.get("ceiling_color", "#87CEEB"))
    screen.fill(ceiling_color, (0, 0, w, int(half_h)))
    screen.fill(floor_color, (0, int(half_h), w, h - int(half_h)))

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
    z_layer = int(cfg.get("z_layer", 0))

    wall_color = room.parse_color(cfg.get("wall_color", "#8a8a8a"))
    fov_deg = cfg.get("fov", 66)
    fov_rad = math.radians(fov_deg)
    render_distance_cells = int(cfg.get("render_distance", 20))
    num_columns = int(cfg.get("columns", min(w, 320)))
    col_width = w / num_columns

    # GM angle convention (0=right, 90=up, ...) -> screen-space radians,
    # matching raycast_2_5d's facing_angle-to-ray-space conversion.
    facing_screen_rad = math.radians(-camera.facing_angle)
    # CAMERA-PLANE projection (not uniform-angle) -- see raycast_2_5d's own
    # comment on why: uniform-angle sampling bends straight walls.
    plane_tan = math.tan(fov_rad / 2)
    textured = bool(cfg.get("wall_textured", True))

    for col in range(num_columns):
        camera_x = 2.0 * (col + 0.5) / num_columns - 1.0
        ray_offset = math.atan(plane_tan * camera_x)
        ray_angle = facing_screen_rad + ray_offset
        dist, side, hit, tex_u, block_type = cast_ray(
            room, cam_x, cam_y, z_layer, ray_angle, cell_size, render_distance_cells)
        if not hit:
            # No block within render distance -- leave the floor/ceiling
            # fill showing for this column rather than a bogus sliver.
            continue
        corrected = dist * math.cos(ray_offset)  # fisheye correction
        # A block projects as a genuine cube (1 cell tall == 1 cell wide at
        # the same distance) -- unlike raycast_2_5d's deliberately-taller
        # corridor look, there is no height multiplier here.
        full_h = h * cell_size / max(corrected, 1e-4)
        y_top = half_h - full_h / 2.0
        x0 = int(col * col_width)
        x1 = int((col + 1) * col_width)
        strip_w = max(1, x1 - x0)
        y0 = max(0, int(math.floor(y_top)))
        y1 = min(h, int(math.ceil(y_top + full_h)))
        vis_h = y1 - y0
        if vis_h <= 0:
            continue

        shade = wall_shade(side, corrected, render_distance_cells * cell_size)
        if textured:
            faces = block_face_textures(block_type)
            frame = _load_texture(faces["side"])
            tw, th = frame.get_width(), frame.get_height()
            tex_x = min(tw - 1, max(0, int(tex_u * tw)))
            # Sub-texel crop (see raycast_2_5d.renderer's identical comment):
            # rounding src_y per column would snap adjacent columns to
            # different texels on a close wall, so crop to the floor texel
            # and carry the remainder as a blit offset instead.
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
            screen.blit(strip, (x0, y0), (0, off, strip_w, min(vis_h, dest_h - off)))
        else:
            color = tuple(int(c * shade) for c in wall_color)
            screen.fill(color, (x0, y0, strip_w, vis_h))
