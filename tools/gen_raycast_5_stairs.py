#!/usr/bin/env python3
"""Generate the raycast_5 sample ("Stairs" / « Les escaliers »).

docs/RAYCAST_STAIRS_PLAN.md, S12: a small level built to show climbable
stairs in the 2.5D view. Committed (like gen_raycast_3_maze.py) so the room
can be regenerated, and tests/test_raycast_5_sample.py pins the committed
files against it.

    python tools/gen_raycast_5_stairs.py            # (re)write samples/raycast_5
    python tools/gen_raycast_5_stairs.py --check    # exit 1 if the files differ

The level (cells, x right, y down; 15 x 15 cells of 32 px):

* a solid border;
* a GALLERY 32 px up across the north (rows 1-4);
* a 3-wide STAIRCASE climbing to it (x 6-8): 8, 16, 24 px (rows 7, 6, 5);
* a PILLAR 48 px high at (5, 10) -- too high to climb, it blocks like a wall;
* a MONSTER patrolling row 10 west of the pillar, turning back at the wall
  and at the pillar (raycast_step_blocked in its End Step);
* the GOAL on the gallery at (12, 1); the player starts at (7, 12) facing
  north, so walking straight ahead climbs the stairs.

The gallery's south edge is a ledge you can walk off anywhere. Walls and
ceiling are 3 cells high (wall_height 3) so there is headroom above it.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "samples" / "raycast_5"
CELL = 32
SIZE = 15
STAMP = "2026-11-20T00:00:00.000000"     # fixed, so regenerating changes nothing

GALLERY = 32
STEPS = {7: 8, 6: 16, 5: 24}             # row -> height, at x 6..8
STAIR_X = (6, 7, 8)
PILLAR = (5, 10, 48)
MONSTER = (2, 10)
GOAL = (12, 1)
START = (7, 12)

COPIED_SPRITES = {                        # name -> source sample
    "spr_wall_texture": "raycast_4", "spr_floor": "raycast_4",
    "spr_ceiling": "raycast_4", "spr_person": "raycast_4",
    "spr_monster": "raycast_4", "spr_goal": "raycast_1",
}
STEP_HEIGHTS = (8, 16, 24, 32, 48)


def _sprite_meta(name, w=32, h=32):
    return {"name": name, "asset_type": "sprite", "file_path": f"sprites/{name}.png",
            "width": w, "height": h, "origin_x": 0, "origin_y": 0, "precise": False,
            "frames": 1, "frame_width": w, "frame_height": h,
            "animation_type": "single", "speed": 10.0, "imported": False,
            "created": STAMP, "modified": STAMP}


def _write_png(path, rgb):
    """A 32x32 flat square with a darker 1-px border (room-editor look only:
    steps and walls are never drawn as sprites in the first-person view).
    Written with zlib, no pygame needed."""
    import struct
    import zlib
    rows = []
    edge = tuple(max(0, c - 40) for c in rgb)
    for y in range(32):
        row = bytearray([0])
        for x in range(32):
            row += bytes(edge if x in (0, 31) or y in (0, 31) else rgb)
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", 32, 32, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    path.write_bytes(png)


def _obj(name, sprite, events, solid=False, visible=True):
    return {"name": name, "asset_type": "object", "sprite": sprite, "visible": visible,
            "solid": solid, "persistent": False, "depth": 0, "parent": "",
            "events": events}


def _act(action, **params):
    return {"action": action, "parameters": params}


def _message(en, fr):
    return _act("show_message", message=en, message_translations={"fr": fr})


def objects():
    move = lambda d: {"actions": [_act("set_direction_speed", direction=d, speed="3")]}  # noqa: E731
    person = _obj("obj_person", "spr_person", {
        "create": {"actions": [
            _act("enable_raycast_view", camera_object="", fov="66", cell_size="32",
                 render_distance="20", wall_texture="spr_wall_texture", sky_texture="",
                 floor_texture="spr_floor", ceiling_texture="spr_ceiling",
                 wall_color="#993333", floor_color="#464632", ceiling_color="#87CEEB",
                 wall_height="3", max_step="12"),
            _act("set_facing_angle", angle="90", relative=False)]},
        "keyboard": {
            "up": move("facing_angle"),
            "down": move("facing_angle+180"),
            "left": {"actions": [_act("set_facing_angle", angle="3", relative=True)]},
            "right": {"actions": [_act("set_facing_angle", angle="-3", relative=True)]},
            "nokey": {"actions": [_act("set_direction_speed", direction="0", speed="0")]}},
        # Empty, but registering it is what makes solid walls block the
        # player (see the raycast_1 sample notes).
        "collision_with_obj_wall": {"actions": [], "target_object": "obj_wall"},
        "collision_with_obj_monster": {"actions": [
            _message("The monster caught you! Back to the start.",
                     "Le monstre t'a attrapé ! Retour au départ."),
            _act("restart_room")], "target_object": "obj_monster"},
        "collision_with_obj_goal": {"actions": [
            _message("You climbed the stairs and reached the goal!",
                     "Tu as monté l'escalier et atteint le but !"),
            _act("restart_game")], "target_object": "obj_goal"},
        "draw": {"actions": [_act("draw_minimap", x="8", y="8", size="96",
                                  mark_object="obj_goal", mark_color="#40e0ff")]},
    })
    monster = _obj("obj_monster", "spr_monster", {
        "create": {"actions": [_act("set_hspeed", speed="2")]},
        "collision_with_obj_wall": {"actions": [_act("reverse_horizontal")],
                                    "target_object": "obj_wall"},
        # A refused step fires no event: raycast_step_blocked is how a
        # monster learns it walked into something too high to climb.
        "end_step": {"actions": [
            _act("test_variable", variable="raycast_step_blocked", value="1",
                 scope="instance", operation="equal"),
            _act("reverse_horizontal")]},
    })
    objs = {
        "obj_wall": _obj("obj_wall", "spr_wall", {}, solid=True),
        "obj_person": person,
        "obj_monster": monster,
        "obj_goal": _obj("obj_goal", "spr_goal", {}),
    }
    for h in STEP_HEIGHTS:
        objs[f"obj_step_{h}"] = _obj(f"obj_step_{h}", f"spr_step_{h}", {
            "create": {"actions": [_act("set_floor_height", height=str(h),
                                        top_texture="", side_texture="")]}})
    return objs


def instances():
    inst = []

    def add(obj, gx, gy):
        inst.append({"object_name": obj, "x": gx * CELL, "y": gy * CELL,
                     "rotation": 0, "scale_x": 1.0, "scale_y": 1.0, "visible": True})
    for g in range(SIZE):
        for gx, gy in ((g, 0), (g, SIZE - 1)):
            add("obj_wall", gx, gy)
    for g in range(1, SIZE - 1):
        for gx, gy in ((0, g), (SIZE - 1, g)):
            add("obj_wall", gx, gy)
    for gy in range(1, 5):
        for gx in range(1, SIZE - 1):
            add(f"obj_step_{GALLERY}", gx, gy)
    for gy, h in sorted(STEPS.items()):
        for gx in STAIR_X:
            add(f"obj_step_{h}", gx, gy)
    add(f"obj_step_{PILLAR[2]}", PILLAR[0], PILLAR[1])
    add("obj_goal", *GOAL)
    add("obj_monster", *MONSTER)
    add("obj_person", *START)
    return inst


def room():
    inst = instances()
    return {"name": "room0", "asset_type": "room", "width": SIZE * CELL,
            "height": SIZE * CELL, "background_color": "#202020",
            "background_image": "", "tile_horizontal": False, "tile_vertical": False,
            "instance_count": len(inst), "instances": inst, "tiles": [],
            "created": STAMP, "modified": STAMP, "imported": False}


def sprites():
    meta = {}
    for name, src in COPIED_SPRITES.items():
        m = json.loads((ROOT / "samples" / src / "sprites" / f"{name}.json").read_text(encoding="utf-8"))
        m.update(created=STAMP, modified=STAMP)
        meta[name] = m
    meta["spr_wall"] = _sprite_meta("spr_wall")
    for h in STEP_HEIGHTS:
        meta[f"spr_step_{h}"] = _sprite_meta(f"spr_step_{h}")
    return meta


def project():
    return {
        "name": "raycast_5", "version": "1.0", "created": STAMP, "modified": STAMP,
        "settings": {"window_title": "", "window_width": 640, "window_height": 480,
                     "room_speed": 30, "fullscreen": False, "starting_lives": 3,
                     "show_lives_in_caption": False, "starting_score": 0,
                     "show_score_in_caption": False, "starting_health": 100,
                     "show_health_in_caption": False, "blockly_preset": "full",
                     "starting_room": "room0"},
        "assets": {"sprites": sprites(), "sounds": {}, "backgrounds": {},
                   "objects": objects(), "rooms": {"room0": room()},
                   "scripts": {}, "fonts": {}, "data": {}},
    }


def _dump(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def files():
    """{relative path: text} for every generated JSON file."""
    proj = project()
    out = {"project.json": _dump(proj), "rooms/room0.json": _dump(proj["assets"]["rooms"]["room0"])}
    for name, obj in proj["assets"]["objects"].items():
        out[f"objects/{name}.json"] = _dump(obj)
    for name, spr in proj["assets"]["sprites"].items():
        out[f"sprites/{name}.json"] = _dump(spr)
    return out


def write(out=OUT):
    for rel, text in files().items():
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for name, src in COPIED_SPRITES.items():
        shutil.copyfile(ROOT / "samples" / src / "sprites" / f"{name}.png",
                        out / "sprites" / f"{name}.png")
    _write_png(out / "sprites" / "spr_wall.png", (60, 60, 60))
    for i, h in enumerate(STEP_HEIGHTS):
        shade = 90 + i * 30
        _write_png(out / "sprites" / f"spr_step_{h}.png", (shade, shade, int(shade * 0.8)))


def check(out=OUT):
    bad = [rel for rel, text in files().items()
           if not (out / rel).exists() or (out / rel).read_text(encoding="utf-8") != text]
    return bad


if __name__ == "__main__":
    if "--check" in sys.argv:
        diff = check()
        print("raycast_5 differs from the generator:" if diff else "raycast_5 is up to date", *diff)
        sys.exit(1 if diff else 0)
    write()
    print("wrote", OUT)
