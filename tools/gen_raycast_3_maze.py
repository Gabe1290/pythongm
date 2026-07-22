#!/usr/bin/env python3
"""Generate raycast_3's maze rooms.

raycast_2's maze was built by a throwaway script that was never committed, so
its rooms can't be regenerated. This one lives in the repo: re-running it with
the same seeds reproduces the shipped rooms byte-for-byte (bar the timestamps),
which makes the level design reviewable and tweakable instead of opaque.

Geometry follows raycast_1/raycast_2's thin edge-wall model exactly:
  - a horizontal wall on the TOP edge of cell (c, r) -> obj_wall_h at
    (c*CELL, r*CELL - 4)
  - a vertical wall on the LEFT edge of cell (c, r) -> obj_wall_v at
    (c*CELL - 4, r*CELL)
Walls are 32x8 and 8x32, so the -4 centres the 8px thickness on the cell
boundary. The raycast renderer derives its wall edges from these solid
instances' sprite aspect ratios
(extensions/raycast_2_5d/renderer.build_raycast_walls).

Usage:  py -3.12 tools/gen_raycast_3_maze.py
"""
import json
import random
from pathlib import Path

CELL = 32
GRID = 15                      # 15x15 cells -> 480x480 room
ROOM = CELL * GRID
EXTRA_OPENINGS = 12            # knocked-through walls, for loops rather than a
                               # pure tree (a perfect maze is tedious in FPS)

SAMPLE = Path(__file__).resolve().parent.parent / "samples" / "raycast_3"


def carve(seed):
    """Recursive-backtracker maze. Returns (h_walls, v_walls) sets of cells.

    h_walls holds (c, r) meaning "wall along the TOP edge of cell (c, r)";
    v_walls holds (c, r) meaning "wall along the LEFT edge of cell (c, r)".
    Both start full and get carved away.
    """
    rng = random.Random(seed)
    h = {(c, r) for c in range(GRID) for r in range(GRID + 1)}
    v = {(c, r) for c in range(GRID + 1) for r in range(GRID)}

    seen = [[False] * GRID for _ in range(GRID)]
    stack = [(0, 0)]
    seen[0][0] = True
    while stack:
        c, r = stack[-1]
        nbrs = []
        if r > 0 and not seen[r - 1][c]:
            nbrs.append((c, r - 1, "N"))
        if r < GRID - 1 and not seen[r + 1][c]:
            nbrs.append((c, r + 1, "S"))
        if c > 0 and not seen[r][c - 1]:
            nbrs.append((c - 1, r, "W"))
        if c < GRID - 1 and not seen[r][c + 1]:
            nbrs.append((c + 1, r, "E"))
        if not nbrs:
            stack.pop()
            continue
        nc, nr, d = rng.choice(nbrs)
        if d == "N":
            h.discard((c, r))
        elif d == "S":
            h.discard((c, r + 1))
        elif d == "W":
            v.discard((c, r))
        else:
            v.discard((c + 1, r))
        seen[nr][nc] = True
        stack.append((nc, nr))

    # Knock through some interior walls so the maze has loops.
    for _ in range(EXTRA_OPENINGS):
        if rng.random() < 0.5:
            c, r = rng.randrange(GRID), rng.randrange(1, GRID)
            h.discard((c, r))
        else:
            c, r = rng.randrange(1, GRID), rng.randrange(GRID)
            v.discard((c, r))
    return h, v


def open_cells(h, v, seed):
    """Cells with at least two open sides — good spots for pickups/enemies.

    Deterministic given the seed, so re-running reproduces the same layout.
    """
    rng = random.Random(seed + 1000)
    out = []
    for r in range(GRID):
        for c in range(GRID):
            sides = sum([
                (c, r) not in h,            # top open
                (c, r + 1) not in h,        # bottom open
                (c, r) not in v,            # left open
                (c + 1, r) not in v,        # right open
            ])
            if sides >= 2:
                out.append((c, r))
    rng.shuffle(out)
    return out


def inst(name, x, y):
    return {"object_name": name, "rotation": 0, "scale_x": 1.0,
            "scale_y": 1.0, "visible": True, "x": x, "y": y}


def build_room(name, seed, camera_obj, counts, goal_obj="obj_goal"):
    """counts: dict of object_name -> how many to scatter at open cells.

    goal_obj: obj_goal (advances to the next room) or obj_goal_final (wins the
    game). Both are gem-gated — they only fire when no obj_gem remains.
    """
    h, v = carve(seed)
    check_start(h, v)
    instances = []
    for (c, r) in sorted(h):
        instances.append(inst("obj_wall_h", c * CELL, r * CELL - 4))
    for (c, r) in sorted(v):
        instances.append(inst("obj_wall_v", c * CELL - 4, r * CELL))

    spots = open_cells(h, v, seed)
    # Player starts at cell (0,0); keep pickups away from it.
    spots = [s for s in spots if s != (0, 0)]

    # Player sprite is 16x16, centred in its cell (matches raycast_1's fix for
    # exact-grid-line ray origins — see CLAUDE.md 2026-07-17).
    instances.append(inst("obj_person", 8, 8))
    instances.append(inst(camera_obj, 0, 0))
    # The HUD controller. Its position is irrelevant (draw commands are
    # screen-space), but it MUST be a visible object: GameMaker doesn't run an
    # invisible instance's draw event, which is why this can't live on the
    # invisible camera controller.
    instances.append(inst("obj_hud", 0, 0))

    used = 0
    for obj_name, n in counts.items():
        for (c, r) in spots[used:used + n]:
            # obj_gem/obj_monster/obj_medkit sprites are 32x32 -- the same
            # size as a cell -- so their top-left IS the cell's top-left; no
            # offset needed (unlike obj_person's 16x16 sprite below, which
            # needs +8 to centre in a 32px cell). raycast_2's rooms got this
            # right (offset 0); this generator introduced the regression by
            # reusing the player's +8 centering offset for 32x32 sprites too,
            # shifting them 8px off their cell in both axes.
            instances.append(inst(obj_name, c * CELL, r * CELL))
        used += n

    # Goal goes in the far corner, so the maze has to be crossed. spr_goal is
    # also 32x32 -- no centering offset needed, same reasoning as above.
    instances.append(inst(goal_obj, (GRID - 1) * CELL, (GRID - 1) * CELL))

    return {
        "name": name,
        "asset_type": "room",
        "width": ROOM,
        "height": ROOM,
        "background_color": "#e3e3e3",
        "background_image": "",
        "tile_horizontal": False,
        "tile_vertical": False,
        "instance_count": len(instances),
        "tiles": [],
        "instances": instances,
    }


# Seeds are chosen, not arbitrary: cell (0,0) must open EAST so the player —
# who starts there facing angle 0 (east) — isn't staring at a wall on spawn,
# and the maze must be fully connected so the goal is reachable. Verified for
# every seed listed here; see check_start() below.
ROOMS = {
    # name     seed  camera       scattered contents                         goal
    # room1 is the harder half: more monsters, fewer medkits, so the health
    # bar the sample exists to show actually comes under pressure.
    "room0": (5, "obj_cam0",
              {"obj_gem": 8, "obj_monster": 3, "obj_medkit": 3}, "obj_goal"),
    "room1": (7, "obj_cam1",
              {"obj_gem": 10, "obj_monster": 5, "obj_medkit": 2}, "obj_goal_final"),
}


def check_start(h, v):
    """Assert the two properties the seeds were picked for."""
    assert (1, 0) not in v, "cell (0,0) must open EAST — player spawns facing a wall"
    seen, stack = {(0, 0)}, [(0, 0)]
    while stack:
        c, r = stack.pop()
        for nc, nr, blocked in (
            (c, r - 1, (c, r) in h), (c, r + 1, (c, r + 1) in h),
            (c - 1, r, (c, r) in v), (c + 1, r, (c + 1, r) in v),
        ):
            if blocked or not (0 <= nc < GRID and 0 <= nr < GRID):
                continue
            if (nc, nr) not in seen:
                seen.add((nc, nr))
                stack.append((nc, nr))
    assert len(seen) == GRID * GRID, f"maze not fully connected: {len(seen)}/{GRID*GRID}"


def main():
    for name, (seed, cam, counts, goal) in ROOMS.items():
        room = build_room(name, seed, cam, counts, goal)
        path = SAMPLE / "rooms" / f"{name}.json"
        path.write_text(json.dumps(room, indent=2) + "\n", encoding="utf-8")
        kinds = {}
        for i in room["instances"]:
            kinds[i["object_name"]] = kinds.get(i["object_name"], 0) + 1
        print(f"{name}: {len(room['instances'])} instances {kinds}")


if __name__ == "__main__":
    main()
