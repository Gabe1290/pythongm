#!/usr/bin/env python3
"""Generate the block_world_1 sample's room data.

Same discipline as tools/gen_block_world_demo.py / tools/gen_raycast_3_maze.py:
committed and regeneratable, not a throwaway script. Emits the
to_block_list-shaped JSON the sample's obj_person loads via
load_block_world in its game_start event.

Layout (top-down, GRID x GRID cells):
  - a grass floor at z=0 across the whole interior
  - a WALL_HEIGHT-tall (3, not 1 -- see gen_block_world_demo.py's own note
    on why) cobble perimeter wall
  - a wood-plank staircase, one block of rise per step (matching
    DEFAULT_MAX_STEP_UP), climbing from the floor to...
  - ...a brick terrace, with a gold_block marking the goal at its centre

The sample's whole "win" condition is reaching that gold_block's (x, y) --
climbable by walking, no precision block-placement puzzle required (see
docs/VOXEL_WORLD_PLAN.md's Unit 7 notes on why: the picking model targets
one layer above a level camera's own footing, which makes an "always
achievable via simple walking" goal a much safer bet for a first sample
than a build-your-own-bridge puzzle that depends on tricky pitch/distance
combinations to even be reachable).

Usage:  python3 tools/gen_block_world_1_room.py
"""
import json
from pathlib import Path

GRID = 14
WALL_HEIGHT = 3
STEP_COUNT = 4
STAIR_X0 = 6
STAIR_Y = 2

# The terrace sits at the top of the stairs, spanning a small square
# centred one cell past the last step.
TERRACE_Z = STEP_COUNT
TERRACE_CX, TERRACE_CY = STAIR_X0 + STEP_COUNT, STAIR_Y

# Where the player starts -- well inside the floor, facing the stairs.
START_X, START_Y = 2, 2
START_FACING = 0.0   # GM convention: 0 = +x (east), toward the stairs

SAMPLE = Path(__file__).resolve().parent.parent / "samples" / "block_world_1"
OUT = SAMPLE / "blocks" / "room0.json"


def build_room():
    """Return the room as a {(x, y, z): block_type} dict."""
    blocks = {}

    def place(x, y, z, block_type):
        blocks[(x, y, z)] = block_type

    for x in range(GRID):
        for y in range(GRID):
            place(x, y, 0, "grass")

    for x in range(GRID):
        for y in (0, GRID - 1):
            for z in range(1, WALL_HEIGHT + 1):
                place(x, y, z, "cobble")
    for y in range(GRID):
        for x in (0, GRID - 1):
            for z in range(1, WALL_HEIGHT + 1):
                place(x, y, z, "cobble")

    for i in range(STEP_COUNT):
        x = STAIR_X0 + i
        for z in range(1, i + 2):
            place(x, STAIR_Y, z, "wood_plank")

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            place(TERRACE_CX + dx, TERRACE_CY + dy, TERRACE_Z, "brick")
    place(TERRACE_CX, TERRACE_CY, TERRACE_Z, "gold_block")   # the goal marker

    return blocks


def to_block_list(blocks):
    return [{"x": x, "y": y, "z": z, "type": t}
            for (x, y, z), t in sorted(blocks.items())]


def main():
    block_list = to_block_list(build_room())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(block_list, indent=2) + "\n", encoding="utf-8")
    print(f"{len(block_list)} blocks written to {OUT}")


if __name__ == "__main__":
    main()
