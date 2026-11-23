#!/usr/bin/env python3
"""Floor heights for the raycast view: the height map stairs are drawn and
climbed from (docs/RAYCAST_STAIRS_PLAN.md, unit S3).

A STEP is an ordinary non-solid instance whose Create event ran
``set_floor_height``; the handler records ``raycast_floor_height`` (plus two
texture names) on the instance, exactly as ``set_billboard_rotation`` records
its frame count. This module turns those instances into a per-cell map:

* an instance raises EVERY grid cell its sprite box covers (a 64x32 sprite
  raises two cells), using the origin-aware sprite top-left like every other
  raycast geometry;
* where steps overlap, the HIGHEST wins, together with its textures;
* heights are clamped to ``[0, max_height]`` -- no pits, and never so high the
  eye would reach the ceiling -- with one warning per instance, not per frame;
* solid instances are walls, never steps (a wall's edges already block rays
  and movement), so a solid object that also ran the action is ignored.

Rebuilt from the live instance list every frame, for the same reason the wall
edges are (renderer.build_raycast_walls): a step created or destroyed at
runtime is reflected immediately. The renderer (S5) and the climbing rule (S8)
read the SAME map, so what you see is what you can climb.

Pure Python, no pygame: the IDE imports the extension's handlers without one.
"""

import logging
import math

from .state import raycast_state

logger = logging.getLogger(__name__)

# --- The vertical model (moved from renderer.py in stairs S8, unchanged) ---
# Wall strips project this many times taller than a cube would (1.0 =
# cube): the default wall height, in cells. HTML5 and Kivy mirror it --
# pinned by tests/test_raycast_export_parity.py.
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


# Never let the eye get closer than this to the ceiling (room pixels).
CEILING_MARGIN = 4.0


def is_step(inst) -> bool:
    """True if this instance ran set_floor_height (it is floor, not a sprite)."""
    return getattr(inst, "raycast_floor_height", None) is not None


def is_ceiling(inst) -> bool:
    """True if this instance ran set_ceiling_height (it is ceiling, not a sprite)."""
    return getattr(inst, "raycast_ceiling_height", None) is not None


def is_geometry(inst) -> bool:
    """A step or a ceiling marker: part of the level, never a billboard or a mover."""
    return is_step(inst) or is_ceiling(inst)


def max_floor_height(cell_size, wall_height_cells, eye_height_cells) -> float:
    """Highest floor allowed: the eye (floor + eye height) must stay at least
    CEILING_MARGIN below the ceiling (wall_height_cells * cell_size)."""
    return max(0.0, (wall_height_cells - eye_height_cells) * cell_size - CEILING_MARGIN)


def _covered_cells(room, inst, cell_size):
    """Grid cells the instance's sprite box covers (at least its own cell)."""
    ix, iy = room._sprite_top_left(inst)
    w = getattr(inst, "_cached_width", 0) or 0
    h = getattr(inst, "_cached_height", 0) or 0
    gx0 = int(math.floor(ix / cell_size))
    gy0 = int(math.floor(iy / cell_size))
    # A box ending exactly on a grid line does not reach into the next cell.
    gx1 = int(math.floor((ix + w) / cell_size - 1e-9)) if w > 0 else gx0
    gy1 = int(math.floor((iy + h) / cell_size - 1e-9)) if h > 0 else gy0
    return [(gx, gy) for gx in range(gx0, max(gx0, gx1) + 1)
            for gy in range(gy0, max(gy0, gy1) + 1)]


def _clamped(inst, height, max_height, warned):
    if 0.0 <= height <= max_height:
        return height
    clamped = min(max(height, 0.0), max_height)
    key = id(inst)
    if key not in warned:
        warned.add(key)
        logger.warning(
            "set_floor_height: %s's height %s is outside 0..%s for this view "
            "(it would sink below the ground or bring the eye to the ceiling); "
            "using %s. Raise the wall height or lower the step.",
            getattr(inst, "object_name", "?"), height, max_height, clamped)
    return clamped


def build_floor_heights(room, cell_size, max_height):
    """Derive the floor-height map from the room's step instances.

    Stores, and returns, ``(heights, textures)`` in the room's raycast state:
    ``heights`` maps ``(gx, gy) -> height`` for raised cells only (an absent
    cell is at 0); ``textures`` maps the same cells to the winning step's
    ``(top_texture, side_texture)`` names ('' = fall back).
    """
    st = raycast_state(room)
    warned = st.setdefault("floor_height_warned", set())
    heights = {}
    textures = {}
    for inst in room.instances:
        if not is_step(inst):
            continue
        if (getattr(inst, "_cached_object_data", None) or {}).get("solid", False):
            continue
        height = _clamped(inst, float(inst.raycast_floor_height), max_height, warned)
        if height <= 0.0:
            continue
        tex = (getattr(inst, "raycast_step_top_texture", "") or "",
               getattr(inst, "raycast_step_side_texture", "") or "")
        for cell in _covered_cells(room, inst, cell_size):
            if height > heights.get(cell, 0.0):
                heights[cell] = height
                textures[cell] = tex
    st["floor_heights"] = heights
    st["floor_textures"] = textures
    return heights, textures


def build_ceiling_heights(room, cell_size, room_ceiling, floor_heights, eye_height):
    """Derive the per-cell ceiling map from the room's ceiling markers
    (docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md, C1).

    ``room_ceiling`` is the room-wide ceiling in room px (wall_height x cell),
    ``floor_heights`` the map build_floor_heights returned, ``eye_height`` the
    eye above the floor in room px. Stores, and returns, ``(ceilings,
    textures)`` in the room's raycast state: ``ceilings`` maps ``(gx, gy) ->
    height`` for LOWERED cells only (an absent cell has the room ceiling);
    ``textures`` maps the same cells to the winning marker's texture name.

    Same rules as the floor map, mirrored: a marker covers every cell its
    sprite box covers; where markers overlap the LOWEST wins; solid instances
    are walls and are ignored. Each cell's ceiling is clamped to
    ``[floor(cell) + eye_height + CEILING_MARGIN, room_ceiling]`` -- never so
    low the eye would reach it, never above the walls -- with one warning per
    instance. A marker at or above the room ceiling changes nothing.
    """
    st = raycast_state(room)
    warned = st.setdefault("ceiling_height_warned", set())
    ceilings = {}
    textures = {}
    for inst in room.instances:
        if not is_ceiling(inst):
            continue
        if (getattr(inst, "_cached_object_data", None) or {}).get("solid", False):
            continue
        raw = float(inst.raycast_ceiling_height)
        tex = getattr(inst, "raycast_ceiling_texture", "") or ""
        clamped_to = None
        for cell in _covered_cells(room, inst, cell_size):
            lowest = floor_heights.get(cell, 0.0) + eye_height + CEILING_MARGIN
            height = min(max(raw, lowest), room_ceiling)
            if height != raw:
                clamped_to = height
            if height >= room_ceiling:
                continue
            if height < ceilings.get(cell, room_ceiling):
                ceilings[cell] = height
                textures[cell] = tex
        if clamped_to is not None and id(inst) not in warned:
            warned.add(id(inst))
            logger.warning(
                "set_ceiling_height: %s's height %s is outside the range this view "
                "allows (at least the floor plus the eye height plus %s, at most the "
                "room ceiling %s); using %s. Lower the floor or raise the ceiling.",
                getattr(inst, "object_name", "?"), raw, CEILING_MARGIN,
                room_ceiling, clamped_to)
    st["ceiling_heights"] = ceilings
    st["ceiling_textures"] = textures
    return ceilings, textures
