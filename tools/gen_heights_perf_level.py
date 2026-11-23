"""Build tools/perf_levels/base_heights/ -- an original 2.5D test level with many height levels.

A hand-test level for the stairs renderer, larger and taller than stairs_speed: an
original layout (not a copy of any existing game's map) on a 32 x 24 grid with 17
floor heights, 0 to 128 px in steps of 8:

  - an entrance hall (ground level) with pedestals at 24 / 48 / 72 / 96 px;
  - a grand staircase (10 steps of 8 px) up to a balcony at 80 px, open towards the hall;
  - a stepped tower on the balcony climbing to a lookout at 128 px;
  - a zig-zag corridor descending from the balcony (72 -> 32 px) to a pillared courtyard;
  - a pit room: a walkway at 32 px around a pool of green sludge at 8 px, with steps out;
  - static monsters and pickups standing at different heights (billboards).

The camera can climb 12 px at a time (max_step), so every 8 px step is walkable and
every drop is allowed. Walls are 5 cells tall, so the highest floor allowed is 132 px.

Yellow readout (top left): average WORK time per frame over the last 30 frames
(Clock.get_rawtime: update + draw, without the 60 fps wait), frames per second, and the
floor height under the camera. A small map sits at the top right.

Art comes from samples/raycast_5 plus one generated texture (spr_nukage). Re-run after
changing that sample:  python3 tools/gen_heights_perf_level.py
"""

import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "samples" / "raycast_5"
OUT = REPO / "tools" / "perf_levels" / "base_heights"

CELL = 32
W, H = 32, 24
ROOM = "base"
WALL_HEIGHT = 5          # cells; max floor = (5 - 0.75) * 32 - 4 = 132 px
MAX_STEP = 12

# Map legend: '#' wall, '.' ground (0 px), '1'..'9' = 8..72 px, 'a'..'g' = 80..128 px,
# 'n' = green sludge at 8 px (the pit floor).
LEVELS = "123456789abcdefg"
HEIGHT_OF = {ch: 8 * (i + 1) for i, ch in enumerate(LEVELS)}
HEIGHT_OF["."] = 0
HEIGHT_OF["n"] = 8

START = (2, 6)            # camera cell, facing east (towards the staircase)
GUARDS = [(5, 6), (24, 6), (28, 9), (29, 2), (6, 20), (27, 21), (20, 15)]
PICKUPS = [(7, 3), (3, 9), (7, 19), (20, 16), (21, 21), (25, 2)]


def build_map():
    g = [["#"] * W for _ in range(H)]

    def fill(x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                g[y][x] = ch

    # North half: hall, staircase, balcony, tower.
    fill(1, 1, 10, 11, ".")                       # entrance hall
    fill(11, 1, 20, 3, ".")                       # hall continues beside the stairs
    fill(11, 8, 20, 11, ".")
    for i, x in enumerate(range(11, 21)):         # grand staircase 8 -> 80 px
        fill(x, 4, x, 7, LEVELS[i])
    fill(21, 1, 30, 11, "a")                      # balcony at 80 px
    for i, x in enumerate(range(22, 28)):         # tower path 88 -> 128 px
        fill(x, 1, x, 1, LEVELS[10 + i])
    fill(28, 1, 30, 2, "g")                       # lookout at 128 px
    fill(3, 3, 4, 4, "3")                         # hall pedestals: 24, 48, 72, 96 px
    fill(7, 3, 8, 4, "6")
    fill(3, 8, 4, 9, "9")
    fill(7, 8, 8, 9, "c")

    # Passages through the middle wall.
    fill(4, 12, 5, 12, "1")                       # hall -> pit room ramp
    fill(4, 13, 5, 13, "2")
    fill(4, 14, 5, 14, "3")
    fill(26, 12, 27, 12, "9")                     # balcony -> zig-zag, going down

    # South-west: pit room.
    fill(1, 15, 10, 22, "4")                      # walkway at 32 px
    fill(3, 17, 8, 21, "n")                       # sludge pool at 8 px
    g[17][5] = "3"                                # steps out of the pool
    g[18][5] = "2"
    fill(11, 20, 11, 21, "4")                     # pit room -> zig-zag

    # South-east: zig-zag corridor and courtyard.
    fill(26, 13, 27, 13, "8")
    fill(26, 14, 27, 14, "7")
    fill(26, 15, 27, 16, "6")
    fill(14, 15, 25, 16, "5")
    fill(14, 17, 15, 19, "5")
    fill(12, 20, 13, 21, "4")
    fill(14, 20, 15, 21, "5")
    fill(16, 18, 30, 22, "5")                     # courtyard at 40 px
    for (x, y) in ((18, 19), (21, 19), (18, 21)):   # pillars
        g[y][x] = "#"
    fill(25, 20, 29, 22, "7")                     # raised platform at 56 px
    g[21][24] = "6"                               # its step
    return ["".join(row) for row in g]


MAP = build_map()


def _instance(obj, gx, gy):
    return {"object_name": obj, "x": gx * CELL, "y": gy * CELL, "rotation": 0,
            "scale_x": 1.0, "scale_y": 1.0, "visible": True}


def step_object_name(ch):
    return "obj_sludge" if ch == "n" else f"obj_h{HEIGHT_OF[ch]}"


def build_room():
    inst = []
    for gy, row in enumerate(MAP):
        for gx, ch in enumerate(row):
            if ch == "#":
                inst.append(_instance("obj_wall", gx, gy))
            elif ch != ".":
                inst.append(_instance(step_object_name(ch), gx, gy))
    inst += [_instance("obj_guard", x, y) for (x, y) in GUARDS]
    inst += [_instance("obj_goal", x, y) for (x, y) in PICKUPS]
    inst.append(_instance("obj_person", *START))
    return {"name": ROOM, "asset_type": "room", "width": W * CELL, "height": H * CELL,
            "background_color": "#000000", "background_image": "",
            "tile_horizontal": False, "tile_vertical": False,
            "instance_count": len(inst), "instances": inst, "tiles": [],
            "created": "2026-11-23T00:00:00.000000", "modified": "2026-11-23T00:00:00.000000",
            "imported": False}


def _editor_sprite(height):
    # Only what the room editor shows; the 3D view uses the camera's textures.
    for limit in (8, 16, 24, 32):
        if height <= limit:
            return f"spr_step_{limit}"
    return "spr_step_48"


def _plain_object(name, sprite, solid=False, events=None):
    return {"name": name, "asset_type": "object", "sprite": sprite, "visible": True,
            "solid": solid, "persistent": False, "depth": 0, "parent": "",
            "events": events or {}}


def build_objects():
    objects = {"obj_wall": json.loads((SRC / "objects" / "obj_wall.json").read_text(encoding="utf-8")),
               "obj_goal": _plain_object("obj_goal", "spr_goal"),
               # Static monster: the same art as raycast_5's, no movement, no harm.
               "obj_guard": _plain_object("obj_guard", "spr_monster")}
    for ch in LEVELS:
        h = HEIGHT_OF[ch]
        objects[f"obj_h{h}"] = _plain_object(f"obj_h{h}", _editor_sprite(h), events={
            "create": {"actions": [{"action": "set_floor_height", "parameters": {
                "height": str(h), "top_texture": "", "side_texture": ""}}]}})
    objects["obj_sludge"] = _plain_object("obj_sludge", "spr_nukage", events={
        "create": {"actions": [{"action": "set_floor_height", "parameters": {
            "height": "8", "top_texture": "spr_nukage", "side_texture": ""}}]}})
    objects["obj_person"] = build_person()
    return objects


READOUT_CODE = """\
clock = game.clock
hist = getattr(self, 'perf_hist', None)
if hist is None:
    hist = []
    self.perf_hist = hist
hist.append(clock.get_rawtime())
del hist[:-30]
ms = sum(hist) / len(hist)
z = getattr(self, 'raycast_floor_z', 0) or 0
self.perf_text = '%.1f ms/image   %d i/s   hauteur %d px' % (ms, clock.get_fps(), z)
"""


def build_person():
    src = json.loads((SRC / "objects" / "obj_person.json").read_text(encoding="utf-8"))
    ev = src["events"]
    cam = next(a for a in ev["create"]["actions"] if a["action"] == "enable_raycast_view")
    cam = json.loads(json.dumps(cam))
    cam["parameters"]["wall_height"] = str(WALL_HEIGHT)
    cam["parameters"]["max_step"] = str(MAX_STEP)
    src["events"] = {
        "create": {"actions": [cam, {"action": "set_facing_angle",
                                     "parameters": {"angle": "0", "relative": False}}]},
        "keyboard": ev["keyboard"],
        "collision_with_obj_wall": {"actions": [], "target_object": "obj_wall"},
        "draw": {"actions": [
            {"action": "execute_code", "parameters": {"code": READOUT_CODE}},
            {"action": "draw_text", "parameters": {"x": "8", "y": "8", "text": "perf_text",
                                                   "color": "#ffff00"}},
            {"action": "draw_minimap", "parameters": {"x": "536", "y": "8", "size": "96",
                                                      "mark_object": "obj_guard",
                                                      "mark_color": "#ff4040"}},
        ]},
    }
    return src


def write_nukage_png(path):
    """32x32 green sludge: bright blobs on a darker green, tiles seamlessly."""
    from PIL import Image
    img = Image.new("RGBA", (32, 32))
    px = img.load()
    for y in range(32):
        for x in range(32):
            # Two interleaved ripples; periods divide 32 so the tile wraps.
            v = ((x * 3 + y * 5) % 16) + ((x * 7 - y * 2) % 8)
            bright = v in (0, 1, 12, 13)
            px[x, y] = (40, 200, 60, 255) if bright else (20, 110 + (v % 4) * 10, 30, 255)
    img.save(path)


def main():
    for part in ("objects", "rooms", "sprites"):
        if (OUT / part).exists():
            shutil.rmtree(OUT / part)
    (OUT / "objects").mkdir(parents=True)
    (OUT / "rooms").mkdir()
    shutil.copytree(SRC / "sprites", OUT / "sprites")
    shutil.copy2(SRC / "CREDITS.txt", OUT / "CREDITS.txt")

    write_nukage_png(OUT / "sprites" / "spr_nukage.png")
    nukage = json.loads((SRC / "sprites" / "spr_floor.json").read_text(encoding="utf-8"))
    nukage.update({"name": "spr_nukage", "file_path": "sprites/spr_nukage.png",
                   "created": "2026-11-23T00:00:00.000000",
                   "modified": "2026-11-23T00:00:00.000000"})
    (OUT / "sprites" / "spr_nukage.json").write_text(
        json.dumps(nukage, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    objects = build_objects()
    for name, data in objects.items():
        (OUT / "objects" / f"{name}.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    room = build_room()
    (OUT / "rooms" / f"{ROOM}.json").write_text(
        json.dumps(room, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    project = json.loads((SRC / "project.json").read_text(encoding="utf-8"))
    project["name"] = "base_heights"
    project["settings"]["name"] = "base_heights"
    project["settings"]["window_title"] = "Base : niveaux de hauteur"
    project["settings"]["room_speed"] = 60
    project["settings"]["starting_room"] = ROOM
    project["assets"]["sprites"]["spr_nukage"] = nukage
    project["assets"]["objects"] = objects
    project["assets"]["rooms"] = {ROOM: room}
    (OUT / "project.json").write_text(
        json.dumps(project, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}: {room['instance_count']} instances, "
          f"{len(set(HEIGHT_OF[c] for row in MAP for c in row if c in HEIGHT_OF))} floor heights")
    print("\n".join(MAP))


if __name__ == "__main__":
    main()
