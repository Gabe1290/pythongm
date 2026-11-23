"""Build tools/perf_levels/large_junction/ -- a large hand-test level in the style of raycast_6.

Two 48 x 48 rooms (32 px cells) joined by three SEAMLESS junctions (Go to Room Seamlessly), with
stairs (Set Floor Height) and low ceilings (Set Ceiling Height) throughout -- about ten times
raycast_6's area, for trying the 2.5D view at a realistic large size. An original layout.

room0 "upper level":
  * west hall: a 32 px gallery along the north wall, reached by a 3-step staircase;
  * centre: a stepped pyramid, six rings from 8 to 48 px;
  * east: a raised plaza at 32 px (ramp up from the south) under a low arcade (ceiling 64 px);
  * south: a corridor quarter with three low TUNNELS (ceiling 40 px). Each tunnel holds a junction
    marker and, two cells further in, a line of gates that drops you into room1 at the same spot.
room1 "the crypt": the same three tunnels (same markers), low-ceilinged halls (48 px) with a grid
  of pillars, flags to find, and in each tunnel's far end a line of gates back up.

The camera, the gates and the flags work as in raycast_6 (whose objects and art are reused). The
yellow line: average WORK ms per frame over 30 frames (Clock.get_rawtime: update + draw, without
the 60 fps wait), frames per second, the room and the floor height under you.

    python3 tools/gen_large_junction_level.py      # (re)write the level
"""
import importlib.util
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "tools" / "perf_levels" / "large_junction"
SRC = REPO / "samples" / "raycast_6"
CELL = 32
SIZE = 48
STAMP = "2026-11-24T00:00:00.000000"

TUNNEL = 40          # tunnel ceiling (px)
CRYPT = 48           # crypt ceiling (px)
ARCADE = 64          # arcade over the 32 px plaza (lowest legal: 32 + 24 + 4 = 60)

# Junction tunnels, identical in both rooms: (x range, rows, marker cell, gate-A x, gate-B x)
JUNCTIONS = [
    (range(4, 14), (30, 31), (5, 30), 7, 12),
    (range(19, 29), (38, 39), (20, 38), 22, 27),
    (range(34, 44), (30, 31), (35, 30), 37, 42),
]
START = (24, 44)     # room0, facing north
ROOMS = ("room0", "room1")


def _gen6():
    spec = importlib.util.spec_from_file_location("gen6", REPO / "tools" / "gen_raycast_6_junction.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Grid:
    """One room: walls, floor heights, ceiling heights and placed objects, by cell."""

    def __init__(self):
        self.walls = set()
        self.floor = {}
        self.ceil = {}
        self.things = []                       # (object, gx, gy)

    def rect(self, store, x0, y0, x1, y1, value=True):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if store is self.walls:
                    self.walls.add((x, y))
                else:
                    store[(x, y)] = value

    def clear_walls(self, x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.walls.discard((x, y))


def _border(g):
    for i in range(SIZE):
        g.walls.update({(i, 0), (i, SIZE - 1), (0, i), (SIZE - 1, i)})


def _tunnels(g, room_index):
    """The three junction tunnels: walls along both sides, a low ceiling, the marker, the gates."""
    for k, (xs, rows, marker, gate_a, gate_b) in enumerate(JUNCTIONS, start=1):
        x0, x1 = xs[0], xs[-1]
        y0, y1 = rows[0], rows[-1]
        g.clear_walls(x0, y0, x1, y1)
        g.rect(g.walls, x0, y0 - 1, x1, y0 - 1)
        g.rect(g.walls, x0, y1 + 1, x1, y1 + 1)
        g.rect(g.ceil, x0, y0, x1, y1, TUNNEL)
        for y in rows:
            g.floor.pop((x0, y), None)
        g.things.append((f"obj_junction_{k}", *marker))
        gate_x = gate_a if room_index == 0 else gate_b
        for y in rows:
            g.things.append((f"obj_gate_{'a' if room_index == 0 else 'b'}{k}", gate_x, y))


def upper():
    g = Grid()
    _border(g)
    # Zone walls: x = 16 and x = 32 north of y = 24, y = 24 across, each with doorways.
    for y in range(1, 24):
        if y not in (10, 11, 12):
            g.walls.update({(16, y), (32, y)})
    for x in range(1, SIZE - 1):
        if x not in (8, 9, 24, 25, 40, 41):
            g.walls.add((x, 24))
    # West hall: gallery (rows 1-4) at 32 px, staircase 8/16/24 (rows 7, 6, 5) at x 6..9.
    g.rect(g.floor, 1, 1, 15, 4, 32)
    for row, h in ((7, 8), (6, 16), (5, 24)):
        g.rect(g.floor, 6, row, 9, row, h)
    for x, y in ((4, 14), (11, 14), (4, 19), (11, 19)):      # pillars
        g.walls.add((x, y))
    # Centre: a stepped pyramid, rings 8..48 px, centred on (24, 12).
    for ring, h in enumerate((8, 16, 24, 32, 40, 48)):
        r = 6 - ring
        g.rect(g.floor, 24 - r, 12 - r, 24 + r, 12 + r, h)
    # East: plaza at 32 px (x 35..45, y 2..16) under the arcade, ramp up from the south.
    g.rect(g.floor, 35, 2, 45, 16, 32)
    g.rect(g.ceil, 35, 2, 45, 16, ARCADE)
    for row, h in ((19, 8), (18, 16), (17, 24)):
        g.rect(g.floor, 38, row, 42, row, h)
    # South quarter: corridor walls between the tunnels (rows 26-46).
    for x in range(1, SIZE - 1):
        if x % 6 == 3:
            for y in range(26, 47):
                if y % 8 not in (2, 3):
                    g.walls.add((x, y))
    g.clear_walls(22, 40, 27, 46)                              # the start area
    _tunnels(g, 0)
    g.things.append(("obj_person", *START))
    return g


def crypt():
    g = Grid()
    _border(g)
    g.rect(g.ceil, 1, 1, SIZE - 2, SIZE - 2, CRYPT)           # everything under the upper level
    for y in range(3, SIZE - 2, 4):                           # pillar grid
        for x in range(3, SIZE - 2, 4):
            g.walls.add((x, y))
    # A dais in the north crypt; 16 px is the highest floor its 48 px ceiling allows
    # (48 - 24 eye - 4 margin = 20).
    g.rect(g.floor, 19, 3, 29, 11, 8)                         # its step: 0 -> 8 -> 16
    g.rect(g.floor, 20, 4, 28, 10, 16)
    _tunnels(g, 1)
    for x, y in ((24, 7), (6, 6), (42, 6), (6, 44), (42, 44)):
        g.things.append(("obj_goal", x, y))
    g.things.append(("obj_person", *START))                   # replaced on a seamless arrival
    return g


def instances(g):
    out = []

    def add(obj, gx, gy):
        out.append({"object_name": obj, "x": gx * CELL, "y": gy * CELL, "rotation": 0,
                    "scale_x": 1.0, "scale_y": 1.0, "visible": True})

    for gx, gy in sorted(g.walls):
        add("obj_wall", gx, gy)
    for (gx, gy), h in sorted(g.floor.items()):
        if (gx, gy) not in g.walls:
            add(f"obj_h{h}", gx, gy)
    for (gx, gy), c in sorted(g.ceil.items()):
        if (gx, gy) not in g.walls:
            add(f"obj_c{c}", gx, gy)
    for obj, gx, gy in g.things:
        add(obj, gx, gy)
    return out


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
label = 'HAUT' if game.current_room.name == 'room0' else 'CRYPTE'
self.perf_text = '%s   %.1f ms/image   %d i/s   hauteur %d px' % (label, ms, clock.get_fps(), z)
"""


def objects():
    g6 = _gen6()
    objs = g6.objects()
    act = g6._act
    obj = g6._obj
    for name in [n for n in objs if n.startswith(("obj_step_", "obj_gate_", "obj_junction", "obj_low"))]:
        del objs[name]
    floors = sorted({h for g in (upper(), crypt()) for h in g.floor.values()})
    ceils = sorted({c for g in (upper(), crypt()) for c in g.ceil.values()})
    for h in floors:
        objs[f"obj_h{h}"] = obj(f"obj_h{h}", "spr_step_%d" % min(h, 32) if h in (8, 16, 24, 32)
                                else "spr_step_32",
                                {"create": {"actions": [act("set_floor_height", height=str(h),
                                                            top_texture="", side_texture="")]}})
    for c in ceils:
        objs[f"obj_c{c}"] = obj(f"obj_c{c}", "spr_low", {
            "create": {"actions": [act("set_ceiling_height", height=str(c), texture="")]}},
            visible=False)
    person = objs["obj_person"]
    ev = {k: v for k, v in person["events"].items() if not k.startswith("collision_with_obj_gate")}
    for k in range(1, len(JUNCTIONS) + 1):
        objs[f"obj_junction_{k}"] = obj(f"obj_junction_{k}", "spr_junction", {}, visible=False)
        for side, target in (("a", "room1"), ("b", "room0")):
            name = f"obj_gate_{side}{k}"
            objs[name] = obj(name, "spr_gate", {}, visible=False)
            ev[f"collision_with_{name}"] = {"actions": [
                act("go_to_room_seamlessly", room=target, marker=f"obj_junction_{k}")],
                "target_object": name}
    ev["create"]["actions"] = [
        a if a["action"] != "enable_raycast_view" else dict(a, parameters=dict(a["parameters"], wall_height="3"))
        for a in ev["create"]["actions"]]
    ev["draw"] = {"actions": [
        act("execute_code", code=READOUT_CODE),
        act("draw_text", x="8", y="8", text="perf_text", color="#ffff00"),
        act("draw_minimap", x="536", y="8", size="96", mark_object="obj_goal", mark_color="#40e0ff"),
    ]}
    person["events"] = ev
    return objs


def room_dict(name, g):
    inst = instances(g)
    return {"name": name, "asset_type": "room", "width": SIZE * CELL, "height": SIZE * CELL,
            "background_color": "#202020", "background_image": "", "tile_horizontal": False,
            "tile_vertical": False, "instance_count": len(inst), "instances": inst, "tiles": [],
            "created": STAMP, "modified": STAMP, "imported": False}


def main():
    for part in ("objects", "rooms", "sprites"):
        if (OUT / part).exists():
            shutil.rmtree(OUT / part)
    (OUT / "objects").mkdir(parents=True)
    (OUT / "rooms").mkdir()
    shutil.copytree(SRC / "sprites", OUT / "sprites")
    shutil.copy2(SRC / "CREDITS.txt", OUT / "CREDITS.txt")
    objs = objects()
    rooms = {"room0": room_dict("room0", upper()), "room1": room_dict("room1", crypt())}
    for name, data in objs.items():
        (OUT / "objects" / f"{name}.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, data in rooms.items():
        (OUT / "rooms" / f"{name}.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    project = json.loads((SRC / "project.json").read_text(encoding="utf-8"))
    project["name"] = project["settings"]["name"] = "large_junction"
    project["settings"]["window_title"] = "Grande jonction : niveau de test"
    project["settings"]["room_speed"] = 60
    project["settings"]["starting_room"] = "room0"
    project["assets"]["objects"] = objs
    project["assets"]["rooms"] = rooms
    (OUT / "project.json").write_text(
        json.dumps(project, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, data in rooms.items():
        print(f"{name}: {data['instance_count']} instances")


if __name__ == "__main__":
    main()
