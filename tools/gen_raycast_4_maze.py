#!/usr/bin/env python3
"""Generate raycast_4's maze room.

raycast_4 is the DOOM-status-bar sample: a shrunk (letterboxed) 3D view with a
permanent bottom bar (viewport_height + draw_doom_hud). Its single room reuses
raycast_3's committed maze generator wholesale — same recursive-backtracker,
same thin edge-wall placement, same chosen-seed discipline — differing only in
what gets scattered (keys instead of gems/medkits) and that obj_person is the
camera itself (no separate obj_cam).

Re-running reproduces the shipped room byte-for-byte; a test pins it.

Usage:  py -3.12 tools/gen_raycast_4_maze.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_raycast_3_maze as g3           # reuse carve/open_cells/check_start/inst

CELL, GRID = g3.CELL, g3.GRID
SAMPLE = Path(__file__).resolve().parent.parent / "samples" / "raycast_4"

# Seed chosen (via gen_raycast_3's check_start rules): start cell opens east
# and every cell is reachable. Verified in build_room.
ROOM = {
    "name": "room0", "seed": 11,
    "counts": {"obj_key": 3, "obj_monster": 4},
}


def build_room():
    h, v = g3.carve(ROOM["seed"])
    g3.check_start(h, v)                  # spawn opens east + fully connected
    instances = []
    for (c, r) in sorted(h):
        instances.append(g3.inst("obj_wall_h", c * CELL, r * CELL - 4))
    for (c, r) in sorted(v):
        instances.append(g3.inst("obj_wall_v", c * CELL - 4, r * CELL))

    spots = [s for s in g3.open_cells(h, v, ROOM["seed"]) if s != (0, 0)]

    # obj_person is the camera AND draws the HUD (16x16 sprite, centred in its
    # cell like raycast_3's player). No separate obj_cam / obj_hud.
    instances.append(g3.inst("obj_person", 8, 8))

    used = 0
    for obj_name, n in ROOM["counts"].items():
        for (c, r) in spots[used:used + n]:
            instances.append(g3.inst(obj_name, c * CELL, r * CELL))
        used += n

    # Key-gated exit in the far corner.
    instances.append(g3.inst("obj_goal", (GRID - 1) * CELL, (GRID - 1) * CELL))

    return {
        "name": "room0", "asset_type": "room",
        "width": CELL * GRID, "height": CELL * GRID,
        "background_color": "#e3e3e3", "background_image": "",
        "tile_horizontal": False, "tile_vertical": False,
        "instance_count": len(instances), "tiles": [], "instances": instances,
    }


def main():
    room = build_room()
    (SAMPLE / "rooms").mkdir(parents=True, exist_ok=True)
    import json
    (SAMPLE / "rooms" / "room0.json").write_text(
        json.dumps(room, indent=2) + "\n", encoding="utf-8")
    kinds = {}
    for i in room["instances"]:
        kinds[i["object_name"]] = kinds.get(i["object_name"], 0) + 1
    print("room0:", len(room["instances"]), "instances", kinds)


if __name__ == "__main__":
    main()
