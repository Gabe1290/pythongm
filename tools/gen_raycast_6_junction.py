#!/usr/bin/env python3
"""Generate the raycast_6 sample ("The Junction" / « La jonction »).

docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md, D5: a small two-room game built to show the two ideas the
2.5D view borrows from Doom-era games to hide "one floor per cell" -- a LOWERED CEILING (Set Ceiling
Height) and a SEAMLESS TELEPORT (Go to Room Seamlessly). Committed (like gen_raycast_5_stairs.py) so
the rooms can be regenerated; tests/test_raycast_6_sample.py pins the committed files against it.

    python tools/gen_raycast_6_junction.py            # (re)write samples/raycast_6
    python tools/gen_raycast_6_junction.py --check    # exit 1 if the files differ

Both rooms are 15 x 15 cells of 32 px (x right, y down). They share one geometry -- a low CORRIDOR
along rows 7-8 from x = 6 to x = 13 (two cells wide, so the 32 px player fits without hugging a
wall; a ceiling 40 px high, walls on both sides), with the same JUNCTION marker object at (9, 7)
-- and differ everywhere else:

* room0 "Upper level": the START HALL (x 1-5) with a 32 px GALLERY on the north (rows 1-3) reached by
  a 3-step staircase (rows 4-6), and the player at (3, 11) facing north;
* room1 "Under the gallery": the same hall, but with a LOW CEILING over all of it (the space under the
  platform), and a line of gates at x = 2 that leads back to room0.

A line of GATES at x = 11 in room0 sends the player on, seamlessly, into room1: the camera lands at the same
offset from the junction, with the same facing, speed and view height, so walking down the corridor
never stops or jumps. Both corridors end in the same flags at x = 13; touching one wins.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "samples" / "raycast_6"
CELL = 32
SIZE = 15
STAMP = "2026-11-23T00:00:00.000000"     # fixed, so regenerating changes nothing

GALLERY = 32
STEPS = {6: 8, 5: 16, 4: 24}             # row -> height, at x 2..4
STAIR_X = (2, 3, 4)
GALLERY_ROWS = (1, 2, 3)
HALL_X = range(1, 6)                     # x 1..5
CORRIDOR_X = range(6, 14)                # x 6..13
CORRIDOR_ROWS = (7, 8)                   # two cells wide
TUNNEL = 40                              # the corridor's ceiling, px
JUNCTION = (9, 7)
GATE_A_X = 11                            # room0: on to room1 (both corridor rows)
GATE_B_X = 2                             # room1: back to room0 (a line across the hall)
GOAL_X = 13
START = (3, 11)

COPIED_SPRITES = {                        # name -> source sample
    "spr_wall_texture": "raycast_4", "spr_floor": "raycast_4",
    "spr_ceiling": "raycast_4", "spr_person": "raycast_4",
    "spr_goal": "raycast_1",
}
STEP_HEIGHTS = (8, 16, 24, 32)
PLACEHOLDERS = {                          # name -> rgb (room-editor look only)
    "spr_wall": (60, 60, 60), "spr_low": (70, 110, 150),
    "spr_junction": (200, 160, 40), "spr_gate": (160, 60, 160),
}


def _sprite_meta(name, w=32, h=32):
    return {"name": name, "asset_type": "sprite", "file_path": f"sprites/{name}.png",
            "width": w, "height": h, "origin_x": 0, "origin_y": 0, "precise": False,
            "frames": 1, "frame_width": w, "frame_height": h,
            "animation_type": "single", "speed": 10.0, "imported": False,
            "created": STAMP, "modified": STAMP}


def _write_png(path, rgb):
    """A 32x32 flat square with a darker 1-px border (room-editor look only). Written with zlib,
    no pygame needed."""
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
        # Empty, but registering it is what makes solid walls block the player.
        "collision_with_obj_wall": {"actions": [], "target_object": "obj_wall"},
        # The two gates. Each goes to the OTHER room and lines the camera up on the junction
        # marker, which both rooms carry at the same spot.
        "collision_with_obj_gate_a": {"actions": [
            _act("go_to_room_seamlessly", room="room1", marker="obj_junction")],
            "target_object": "obj_gate_a"},
        "collision_with_obj_gate_b": {"actions": [
            _act("go_to_room_seamlessly", room="room0", marker="obj_junction")],
            "target_object": "obj_gate_b"},
        "collision_with_obj_goal": {"actions": [
            _message("You walked through the junction without noticing!",
                     "Tu as traversé la jonction sans t'en apercevoir !"),
            _act("restart_game")], "target_object": "obj_goal"},
    })
    objs = {
        "obj_wall": _obj("obj_wall", "spr_wall", {}, solid=True),
        "obj_person": person,
        "obj_goal": _obj("obj_goal", "spr_goal", {}),
        # Level geometry and triggers: invisible, so the first-person view draws none of them.
        "obj_low": _obj("obj_low", "spr_low", {
            "create": {"actions": [_act("set_ceiling_height", height=str(TUNNEL), texture="")]}},
            visible=False),
        "obj_junction": _obj("obj_junction", "spr_junction", {}, visible=False),
        "obj_gate_a": _obj("obj_gate_a", "spr_gate", {}, visible=False),
        "obj_gate_b": _obj("obj_gate_b", "spr_gate", {}, visible=False),
    }
    for h in STEP_HEIGHTS:
        objs[f"obj_step_{h}"] = _obj(f"obj_step_{h}", f"spr_step_{h}", {
            "create": {"actions": [_act("set_floor_height", height=str(h),
                                        top_texture="", side_texture="")]}})
    return objs


def _shared(add):
    """Border, the hall/corridor partition, the corridor, its marker and its flag: identical in both
    rooms."""
    for g in range(SIZE):
        for gx, gy in ((g, 0), (g, SIZE - 1)):
            add("obj_wall", gx, gy)
    for g in range(1, SIZE - 1):
        for gx, gy in ((0, g), (SIZE - 1, g)):
            add("obj_wall", gx, gy)
    for gy in range(1, SIZE - 1):                      # the wall between the hall and the corridor
        if gy not in CORRIDOR_ROWS:
            add("obj_wall", 6, gy)
    for gx in range(7, 14):                            # the corridor's two sides
        add("obj_wall", gx, CORRIDOR_ROWS[0] - 1)
        add("obj_wall", gx, CORRIDOR_ROWS[-1] + 1)
    for gx in CORRIDOR_X:
        for gy in CORRIDOR_ROWS:
            add("obj_low", gx, gy)                     # the low ceiling
    add("obj_junction", *JUNCTION)
    for gy in CORRIDOR_ROWS:
        add("obj_goal", GOAL_X, gy)


def instances(room_index):
    inst = []

    def add(obj, gx, gy):
        inst.append({"object_name": obj, "x": gx * CELL, "y": gy * CELL,
                     "rotation": 0, "scale_x": 1.0, "scale_y": 1.0, "visible": True})
    _shared(add)
    if room_index == 0:
        for gy in GALLERY_ROWS:
            for gx in HALL_X:
                add(f"obj_step_{GALLERY}", gx, gy)
        for gy, h in sorted(STEPS.items()):
            for gx in STAIR_X:
                add(f"obj_step_{h}", gx, gy)
        for gy in CORRIDOR_ROWS:
            add("obj_gate_a", GATE_A_X, gy)
    else:
        for gy in range(1, SIZE - 1):                  # the space under the gallery: a low ceiling
            for gx in HALL_X:
                add("obj_low", gx, gy)
        for gy in range(1, SIZE - 1):
            add("obj_gate_b", GATE_B_X, gy)
    add("obj_person", *START)
    return inst


def room(room_index):
    inst = instances(room_index)
    return {"name": f"room{room_index}", "asset_type": "room", "width": SIZE * CELL,
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
    for name in PLACEHOLDERS:
        meta[name] = _sprite_meta(name)
    for h in STEP_HEIGHTS:
        meta[f"spr_step_{h}"] = _sprite_meta(f"spr_step_{h}")
    return meta


def project():
    return {
        "name": "raycast_6", "version": "1.0", "created": STAMP, "modified": STAMP,
        "settings": {"window_title": "", "window_width": 640, "window_height": 480,
                     "room_speed": 30, "fullscreen": False, "starting_lives": 3,
                     "show_lives_in_caption": False, "starting_score": 0,
                     "show_score_in_caption": False, "starting_health": 100,
                     "show_health_in_caption": False, "blockly_preset": "full",
                     "starting_room": "room0"},
        "assets": {"sprites": sprites(), "sounds": {}, "backgrounds": {},
                   "objects": objects(), "rooms": {"room0": room(0), "room1": room(1)},
                   "scripts": {}, "fonts": {}, "data": {}},
    }


def _dump(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def files():
    """{relative path: text} for every generated JSON file."""
    proj = project()
    out = {"project.json": _dump(proj)}
    for name, r in proj["assets"]["rooms"].items():
        out[f"rooms/{name}.json"] = _dump(r)
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
    for name, rgb in PLACEHOLDERS.items():
        _write_png(out / "sprites" / f"{name}.png", rgb)
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
        print("raycast_6 differs from the generator:" if diff else "raycast_6 is up to date", *diff)
        sys.exit(1 if diff else 0)
    write()
    print("wrote", OUT)
