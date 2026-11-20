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

# Never let the eye get closer than this to the ceiling (room pixels).
CEILING_MARGIN = 4.0


def is_step(inst) -> bool:
    """True if this instance ran set_floor_height (it is floor, not a sprite)."""
    return getattr(inst, "raycast_floor_height", None) is not None


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
