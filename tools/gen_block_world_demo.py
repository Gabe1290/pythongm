#!/usr/bin/env python3
"""Generate a small demo Block World room.

Not a throwaway script: re-running it reproduces the output byte-for-byte,
the same discipline tools/gen_raycast_3_maze.py established for raycast.
Exists to give Unit 1's load_block_world action (and Phase 4's collision/
footing) a real, non-trivial world to load and walk around in, ahead of
Phase 5 building an actual sample around one. If/when a real sample needs a
bigger or different layout, treat this as the starting point to extend, not
something to throw away -- the JSON shape (a flat list of
{"x","y","z","type"} dicts) is exactly extensions/block_world/state.py's
to_block_list shape, so it loads with zero translation.

Layout (top-down, GRID x GRID cells):
  - a grass floor at z=0 across the whole room
  - a WALL_HEIGHT-tall cobble perimeter wall. Deliberately not 1 block: a
    one-block wall reads as a climbable STEP, not a wall -- the exact
    lesson raycast_2's own playtest already learned (see this doc's Phase
    2b notes) and the same reasoning applies here.
  - a straight staircase of single-block-high wood-plank steps (one block
    of rise per step, matching MAX_STEP_UP) climbing from the floor to a
    small flat brick terrace, so stepping up and dropping back down both
    have something real to exercise

Usage:  python3 tools/gen_block_world_demo.py
"""
import json
from pathlib import Path

GRID = 16
WALL_HEIGHT = 3
STEP_COUNT = 4
STAIR_START_Y = 3

OUT = Path(__file__).resolve().parent / "generated" / "block_world_demo.json"


def build_room():
    """Return the room as a flat {(x, y, z): block_type} dict -- the
    generator's own working representation, converted to the committed
    to_block_list shape only at the very end (build_room itself is what
    the pinning test calls, so it can compare structure directly rather
    than re-parsing JSON)."""
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

    # Staircase: one step per cell along +y, rising one block each.
    stair_x = GRID // 2
    for i in range(STEP_COUNT):
        y = STAIR_START_Y + i
        for z in range(1, i + 2):
            place(stair_x, y, z, "wood_plank")

    # Flat terrace continuing past the top step, at the last step's height.
    terrace_y0 = STAIR_START_Y + STEP_COUNT
    terrace_z = STEP_COUNT
    for dx in (-1, 0, 1):
        for dy in range(3):
            place(stair_x + dx, terrace_y0 + dy, terrace_z, "brick")

    return blocks


def to_block_list(blocks):
    """The committed shape: a flat list, sorted for a stable diff."""
    return [{"x": x, "y": y, "z": z, "type": t}
            for (x, y, z), t in sorted(blocks.items())]


def main():
    block_list = to_block_list(build_room())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(block_list, indent=2) + "\n", encoding="utf-8")
    print(f"{len(block_list)} blocks written to {OUT}")


if __name__ == "__main__":
    main()
