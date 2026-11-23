#!/usr/bin/env python3
"""Climbing stairs in the raycast view (docs/RAYCAST_STAIRS_PLAN.md, S8).

Movement stays 2-D and stays core's: the player walks with Set Direction
Speed, solid walls block it as always. This module adds the one rule stairs
need, through the extension frame hooks (no core change):

* ``before_step`` remembers where every mover stands (every non-solid,
  non-step instance: the camera, monsters, projectiles -- decision D4);
* ``after_collision`` (core has moved things and resolved the walls) looks
  at each mover that moved: if the floor under its centre rose by more than
  the camera's ``max_step`` (room px, default 12), the move is undone ONE
  AXIS AT A TIME -- keep x, else keep y, else neither -- so a player slides
  along the edge of a too-high block exactly as along a wall. Going down is
  always allowed (you can walk off a ledge). A move longer than one cell in
  a single frame is a teleport (Jump to Position, ...), not a step, and is
  never undone.

Each mover gets three readable variables (D5): ``raycast_floor_z`` -- the
floor height under it --, ``raycast_ceiling_z`` -- the ceiling height over it
(the room's, or a lowered one from Set Ceiling Height; ceilings plan, C6) --
and ``raycast_step_blocked`` -- 1 on a frame its move was refused, else 0 --
so an End Step event can, say, turn a monster round. The camera's VIEW height
eases toward the floor under it instead of snapping: up at CLIMB_SPEED px per
frame, down with FALL_GRAVITY (stored as ``eye_floor`` in the room's raycast
state, read by the renderer) -- and never rises above the ceiling over it:
walking off a ledge into a low tunnel drops the view to CEILING_MARGIN under
the tunnel roof at once, then it eases down as usual.

There is no separate "headroom" refusal for movement: build_ceiling_heights
already clamps every cell's ceiling to at least its floor plus the eye plus
CEILING_MARGIN, so every cell can be stood in and only the VIEW needs the
limit above.

Pure Python, no pygame (the IDE imports the extension without one).
"""

from .heights import (build_ceiling_heights, build_floor_heights, CEILING_MARGIN,
                      clamp_wall_height, is_geometry, max_floor_height,
                      RAYCAST_EYE_HEIGHT, RAYCAST_WALL_HEIGHT)
from .state import peek_camera, raycast_state

DEFAULT_MAX_STEP = 12.0     # room px: 8-px stairs climb, a 16-px block does not
CLIMB_SPEED = 2.0           # px per frame the view rises onto a step
FALL_GRAVITY = 0.6          # px per frame^2 the view falls off a ledge


def _camera_cfg(game_runner):
    room = getattr(game_runner, "current_room", None)
    cfg = peek_camera(room) if room is not None else None
    if not cfg or not cfg.get("enabled"):
        return None, None
    return room, cfg


def _is_mover(inst):
    if is_geometry(inst):          # steps and ceiling markers never move
        return False
    return not (getattr(inst, "_cached_object_data", None) or {}).get("solid", False)


def _centre_offset(room, inst):
    """From (x, y) to the sprite centre: constant while the instance moves."""
    tlx, tly = room._sprite_top_left(inst)
    return (tlx - inst.x + (getattr(inst, "_cached_width", 0) or 0) / 2,
            tly - inst.y + (getattr(inst, "_cached_height", 0) or 0) / 2)


def _floor(heights, cell_size, cx, cy):
    return heights.get((int(cx // cell_size), int(cy // cell_size)), 0.0)


def _ceiling(ceilings, room_top, cell_size, cx, cy):
    return ceilings.get((int(cx // cell_size), int(cy // cell_size)), room_top)


def before_step(game_runner):
    """Remember where every mover stands before this frame moves it."""
    room, cfg = _camera_cfg(game_runner)
    if room is None:
        return
    raycast_state(room)["step_prev"] = [
        (inst, inst.x, inst.y) for inst in room.instances if _is_mover(inst)]


def after_collision(game_runner):
    """Refuse climbs higher than max_step, publish the floor variables and
    ease the camera's view height."""
    room, cfg = _camera_cfg(game_runner)
    if room is None:
        return
    st = raycast_state(room)
    prev = st.pop("step_prev", None) or []
    cell_size = int(cfg.get("cell_size", 32))
    wall_h = clamp_wall_height(cfg.get("wall_height", RAYCAST_WALL_HEIGHT))
    heights, _ = build_floor_heights(
        room, cell_size, max_floor_height(cell_size, wall_h, RAYCAST_EYE_HEIGHT))
    room_top = wall_h * cell_size
    eye_px = RAYCAST_EYE_HEIGHT * cell_size
    ceilings, _ = build_ceiling_heights(room, cell_size, room_top, heights, eye_px)
    try:
        max_step = max(0.0, float(cfg.get("max_step", DEFAULT_MAX_STEP)))
    except (TypeError, ValueError):
        max_step = DEFAULT_MAX_STEP

    alive = {id(i) for i in room.instances}
    for inst, ox, oy in prev:
        if id(inst) not in alive or getattr(inst, "to_destroy", False):
            continue
        offx, offy = _centre_offset(room, inst)
        nx, ny = inst.x, inst.y
        blocked = 0
        if (nx, ny) != (ox, oy) and abs(nx - ox) <= cell_size and abs(ny - oy) <= cell_size:
            f_old = _floor(heights, cell_size, ox + offx, oy + offy)
            if _floor(heights, cell_size, nx + offx, ny + offy) - f_old > max_step:
                blocked = 1
                for tx, ty in ((nx, oy), (ox, ny), (ox, oy)):
                    if (tx, ty) == (ox, oy) or \
                            _floor(heights, cell_size, tx + offx, ty + offy) - f_old <= max_step:
                        inst.x, inst.y = tx, ty
                        break
        inst.raycast_step_blocked = blocked
        inst.raycast_floor_z = _floor(heights, cell_size, inst.x + offx, inst.y + offy)
        inst.raycast_ceiling_z = _ceiling(ceilings, room_top, cell_size,
                                          inst.x + offx, inst.y + offy)

    camera = room._find_first_instance(cfg.get("camera_object", ""))
    if camera is None:
        return
    offx, offy = _centre_offset(room, camera)
    target = _floor(heights, cell_size, camera.x + offx, camera.y + offy)
    camera.raycast_floor_z = target
    camera.raycast_ceiling_z = _ceiling(ceilings, room_top, cell_size,
                                        camera.x + offx, camera.y + offy)
    cur = st.get("eye_floor")
    vz = st.get("eye_vz", 0.0)
    if cur is None:
        cur, vz = target, 0.0                  # first frame in this room: no easing
    elif cur < target:
        cur, vz = min(target, cur + CLIMB_SPEED), 0.0
    elif cur > target:
        vz += FALL_GRAVITY
        cur = max(target, cur - vz)
        if cur == target:
            vz = 0.0
    else:
        vz = 0.0
    # The view never rises above the ceiling over the camera (CEILING_MARGIN
    # below it): off a ledge into a low tunnel the eye drops to it at once.
    limit = camera.raycast_ceiling_z - CEILING_MARGIN - eye_px
    if cur > limit:
        cur, vz = max(target, limit), 0.0
    st["eye_floor"] = cur
    st["eye_vz"] = vz
