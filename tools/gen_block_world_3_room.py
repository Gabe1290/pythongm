#!/usr/bin/env python3
"""Generate the block_world_3 sample's room data.

Same discipline as tools/gen_block_world_1_room.py / tools/gen_block_world_demo.py:
committed and regeneratable, not a throwaway script. Emits the
to_block_list-shaped JSON the sample's obj_person loads via
load_block_world in its game_start event.

Layout (top-down, GRID x GRID cells):
  - a grass floor at z=0 across the whole interior
  - a WALL_HEIGHT-tall (3) cobble perimeter wall
  - a CLAY VEIN: a VEIN_W-wide section of the east wall's own bottom
    layer (z=1 only) swapped from cobble to clay -- the wall stays
    WALL_HEIGHT tall overall (z=2/3 there are still cobble), so it is
    never climbable or walkable-over, only mineable from the floor in
    front of it
  - a BEACON: a single gold_block sitting on the floor, the delivery
    point, well short of the wall

The sample's whole "win" condition is Break Block-mining clay from the
vein, Craft Item-ing it into bricks, then WALKING to the beacon while
carrying enough of them -- reachable by simple flat-ground walking, no
elevation or block-placement precision required at all.

Why a wall vein, not a freestanding mound (this generator's own history,
worth keeping so nobody re-derives it the hard way): the first version
put a free-standing clay patch on the open floor, directly in the
player's walking path. A real playtest against a running GameRunner (not
just reading the code) found the patch was never actually mined during
normal play -- being exactly ONE layer tall, it read as a climbable STEP
(state.DEFAULT_MAX_STEP_UP == 1: "any obstruction taller than this reads
as a wall, anything at or under it reads as a step"), so simply walking
forward auto-stepped the player UP ONTO it rather than blocking movement
the way an actual obstacle would. Once standing on top, the eye height
(z_layer + eye_height) rose along with it, and the level-pitch aim ray
sailed clean over the vein to hit whatever was next in line instead of
the clay underfoot. A SECOND version stacked the patch two layers high
to force real blocking -- correctly unclimbable, but then the TOP layer
sat above where a level-pitch ray reaches, so only the bottom layer was
ever minable without tilting the camera up first, the same half-the-
patch problem in a different shape. Embedding the vein in the wall's own
z=1 layer, with z=2/3 there still cobble, sidesteps the whole class of
bug at once: the wall column stays 3 tall (ground_layer 4, never
climbable, matching every OTHER wall cell), so the player is never
routed onto or over it and must mine it from the floor -- exactly the
already-proven "approach a wall section, aim level, Space" interaction
block_world_1's own perimeter wall already exercises.

Usage:  python3 tools/gen_block_world_3_room.py
"""
import json
from pathlib import Path

GRID = 12
WALL_HEIGHT = 3

# Where the player starts -- facing east, toward the vein and beacon.
START_X, START_Y = 2, 6
START_FACING = 0.0   # GM convention: 0 = +x (east)

# The clay vein: a VEIN_W-wide section of the EAST wall's (x = GRID - 1)
# own MIDDLE layer, centred roughly on the player's row. z=2, not z=1:
# standing on a plain floor (itself a real block at z=0), a body's own
# footing is state.ground_layer == 1 (one layer ABOVE the floor block it
# rests on, confirmed empirically, not assumed) -- so a level-pitch aim
# from ground level (eye = z_layer(1) + eye_height(1.5) = 2.5) naturally
# lands in z=2's height range, not z=1's. A first version of this vein
# sat at z=1 and was never once hit by a level-pitch ray fired from the
# floor in a real playtest -- this off-by-one in which layer "ground
# level, looking straight ahead" actually targets is the SAME class of
# lesson as the freestanding-mound mistake this generator's own history
# above already records, just one layer removed from it.
VEIN_Y0 = 4
VEIN_W = 4
VEIN_Z = 2

# The delivery point: a single gold_block landmark sitting on the floor,
# well short of the wall.
BEACON_X, BEACON_Y = 9, 6
BEACON_Z = 1

SAMPLE = Path(__file__).resolve().parent.parent / "samples" / "block_world_3"
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

    # Swap the vein section's z=1 cobble for clay -- z=2/3 there stay
    # cobble (placed by the wall loop above), so the column's overall
    # height, and thus climbability, is unchanged.
    east_x = GRID - 1
    for dy in range(VEIN_W):
        place(east_x, VEIN_Y0 + dy, VEIN_Z, "clay")

    place(BEACON_X, BEACON_Y, BEACON_Z, "gold_block")

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
