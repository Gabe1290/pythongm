"""Build tools/perf_levels/stairs_speed/ -- a hand-test level for the stairs speed test.

The level reproduces the room that
tests/test_raycast_stairs_render.py::test_a_staircase_costs_at_most_a_bit_more_than_a_flat_room
measures (15x15 cells, textured walls/floor/ceiling, wall height 3, 320 columns,
floor_cast_res 4, a 5-wide staircase 8/16/24/32 px up to a 32 px platform, the
camera at cell (2, 7) facing the stairs), twice:

  salle_escalier -- with the steps   (key S)
  salle_plate    -- the same room without them (key F)

A readout in the top-left corner shows the average WORK time per frame over the
last 30 frames (pygame Clock.get_rawtime: update + render, without the wait that
caps the game at 60 fps) and the frame rate. The work time is what the test
compares; it stays meaningful while the frame rate is pinned at 60.

Art and objects are copied from samples/raycast_5, so re-run this after changing
that sample:  python3 tools/gen_stairs_perf_level.py
"""

import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "samples" / "raycast_5"
OUT = REPO / "tools" / "perf_levels" / "stairs_speed"

CELL = 32
SIZE = 15                      # cells per side, as in the test
STEP_OBJECTS = {8: "obj_step_8", 16: "obj_step_16", 24: "obj_step_24", 32: "obj_step_32"}
START = (2 * CELL, 7 * CELL)   # the test's camera cell (2, 7)

ROOMS = {"salle_escalier": True, "salle_plate": False}

# Average work ms over the last 30 frames + fps, into self.perf_text for draw_text.
READOUT_CODE = """\
clock = game.clock
hist = getattr(self, 'perf_hist', None)
if hist is None:
    hist = []
    self.perf_hist = hist
hist.append(clock.get_rawtime())
del hist[:-30]
ms = sum(hist) / len(hist)
label = 'ESCALIER' if game.current_room.name == 'salle_escalier' else 'SOL PLAT'
self.perf_text = '%s   %.1f ms/image   %d i/s      [S] escalier   [F] plat' % (label, ms, clock.get_fps())
"""


def _instance(obj, x, y):
    return {"object_name": obj, "x": x, "y": y, "rotation": 0,
            "scale_x": 1.0, "scale_y": 1.0, "visible": True}


def build_room(name, with_steps):
    inst = []
    for g in range(SIZE):
        for (x, y) in ((g, 0), (g, SIZE - 1), (0, g), (SIZE - 1, g)):
            inst.append(_instance("obj_wall", x * CELL, y * CELL))
    # The border loops above list each corner twice; keep one.
    seen, walls = set(), []
    for i in inst:
        key = (i["x"], i["y"])
        if key not in seen:
            seen.add(key)
            walls.append(i)
    inst = walls
    if with_steps:
        for row in range(5, 10):
            for i, x in enumerate(range(5, 9)):
                inst.append(_instance(STEP_OBJECTS[8 * (i + 1)], x * CELL, row * CELL))
            for x in range(9, 12):
                inst.append(_instance(STEP_OBJECTS[32], x * CELL, row * CELL))
    inst.append(_instance("obj_person", *START))
    return {"name": name, "asset_type": "room", "width": SIZE * CELL, "height": SIZE * CELL,
            "background_color": "#000000", "background_image": "",
            "tile_horizontal": False, "tile_vertical": False,
            "instance_count": len(inst), "instances": inst, "tiles": [],
            "created": "2026-11-23T00:00:00.000000", "modified": "2026-11-23T00:00:00.000000",
            "imported": False}


def build_person():
    src = json.loads((SRC / "objects" / "obj_person.json").read_text(encoding="utf-8"))
    ev = src["events"]
    # Same camera as raycast_5, but facing east (0) at the stairs, as in the test.
    create = [a for a in ev["create"]["actions"] if a["action"] == "enable_raycast_view"]
    create.append({"action": "set_facing_angle", "parameters": {"angle": "0", "relative": False}})
    goto = lambda room: {"actions": [{"action": "goto_room",
                                      "parameters": {"room": room, "transition": "none"}}]}
    events = {
        "create": {"actions": create},
        "keyboard": ev["keyboard"],
        "keyboard_press": {"s": goto("salle_escalier"), "f": goto("salle_plate")},
        "collision_with_obj_wall": {"actions": [], "target_object": "obj_wall"},
        # No minimap: the speed test draws none, so the readout is the only overlay.
        "draw": {"actions": [
            {"action": "execute_code", "parameters": {"code": READOUT_CODE}},
            {"action": "draw_text", "parameters": {"x": "8", "y": "8", "text": "perf_text",
                                                   "color": "#ffff00"}},
        ]},
    }
    src["events"] = events
    return src


def main():
    # Rebuild only what this script generates; the hand-written README files stay.
    for part in ("objects", "rooms", "sprites"):
        if (OUT / part).exists():
            shutil.rmtree(OUT / part)
    (OUT / "objects").mkdir(parents=True)
    (OUT / "rooms").mkdir()
    shutil.copytree(SRC / "sprites", OUT / "sprites")
    shutil.copy2(SRC / "CREDITS.txt", OUT / "CREDITS.txt")

    objects = {"obj_wall": json.loads((SRC / "objects" / "obj_wall.json").read_text(encoding="utf-8")),
               "obj_person": build_person()}
    for name in STEP_OBJECTS.values():
        objects[name] = json.loads((SRC / "objects" / f"{name}.json").read_text(encoding="utf-8"))
    for name, data in objects.items():
        (OUT / "objects" / f"{name}.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rooms = {name: build_room(name, steps) for name, steps in ROOMS.items()}
    for name, data in rooms.items():
        (OUT / "rooms" / f"{name}.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    project = json.loads((SRC / "project.json").read_text(encoding="utf-8"))
    project["name"] = "stairs_speed"
    project["settings"]["name"] = "stairs_speed"
    project["settings"]["window_title"] = "Escalier : test de vitesse"
    project["settings"]["room_speed"] = 60
    project["settings"]["starting_room"] = "salle_escalier"
    sprites = project["assets"]["sprites"]
    project["assets"] = {k: v for k, v in project["assets"].items()
                         if k not in ("objects", "rooms")}
    project["assets"]["sprites"] = sprites
    project["assets"]["objects"] = objects
    project["assets"]["rooms"] = rooms
    (OUT / "project.json").write_text(
        json.dumps(project, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}: rooms {list(rooms)}, "
          f"{rooms['salle_escalier']['instance_count']} / "
          f"{rooms['salle_plate']['instance_count']} instances")


if __name__ == "__main__":
    main()
