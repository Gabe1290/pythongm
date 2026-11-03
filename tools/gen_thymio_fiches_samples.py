"""Generate the three starter projects used by the Thymio activity sheets (docs/thymio_fiches/).

    py -3.12 tools/gen_thymio_fiches_samples.py

Each project holds ONE robot (`thymio_1`, no events: the student writes them) in a room made for one family of
sheets. Wall and tape sprites have their ORIGIN AT THE CENTRE, because the simulator treats a solid instance as a
rectangle centred on (x, y): with a top-left origin the drawn wall and the wall the sensors feel would not match.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent / "samples"
STAMP = "2026-11-03T00:00:00.000000"
W, H = 900, 560


def sprite(folder, name, w, h, draw):
    img = Image.new("RGBA", (w, h))
    draw(ImageDraw.Draw(img), w, h)
    (folder / "sprites").mkdir(parents=True, exist_ok=True)
    img.save(folder / "sprites" / f"{name}.png")
    return {"name": name, "asset_type": "sprite", "file_path": f"sprites/{name}.png", "width": w, "height": h,
            "frames": 1, "frame_width": w, "frame_height": h, "origin_x": w // 2, "origin_y": h // 2,
            "animation_type": "single", "speed": 10.0, "imported": True, "created": STAMP, "modified": STAMP}


def wall(d, w, h):
    d.rectangle([0, 0, w - 1, h - 1], fill=(70, 80, 100, 255), outline=(30, 35, 50, 255), width=3)


def tape(d, w, h):
    d.rectangle([0, 0, w - 1, h - 1], fill=(0, 0, 0, 255))


def obj(name, spr="", solid=False, thymio=False):
    o = {"name": name, "asset_type": "object", "sprite": spr, "visible": True, "solid": solid, "persistent": False,
         "depth": 0, "events": {}, "created": STAMP, "modified": STAMP}
    if thymio:
        o["is_thymio"] = True
    return o


def inst(name, x, y):
    return {"object_name": name, "x": x, "y": y, "rotation": 0, "scale_x": 1.0, "scale_y": 1.0, "visible": True}


def build(folder_name, title, background, instances, sprites, objects):
    folder = ROOT / folder_name
    (folder / "objects").mkdir(parents=True, exist_ok=True)
    (folder / "rooms").mkdir(exist_ok=True)
    spr_assets = {n: sprite(folder, n, w, h, fn) for n, (w, h, fn) in sprites.items()}
    objs = {o["name"]: o for o in objects}
    for n, o in objs.items():
        (folder / "objects" / f"{n}.json").write_text(json.dumps(o, indent=2, ensure_ascii=False), encoding="utf-8")
    room = {"name": "room0", "asset_type": "room", "width": W, "height": H, "background_color": background,
            "background_image": "", "tile_horizontal": False, "tile_vertical": False, "tiles": [],
            "instances": instances, "instance_count": len(instances), "created": STAMP, "modified": STAMP,
            "imported": False}
    (folder / "rooms" / "room0.json").write_text(json.dumps(room, indent=2), encoding="utf-8")
    project = {"name": folder_name, "version": "1.0.0", "created": STAMP, "modified": STAMP,
               "settings": {"window_title": title, "window_width": W, "window_height": H, "room_speed": 60,
                            "fullscreen": False, "starting_lives": 3, "show_lives_in_caption": False,
                            "starting_score": 0, "show_score_in_caption": False, "starting_health": 100,
                            "show_health_in_caption": False, "blockly_preset": "full",
                            "active_extensions": ["thymio"]},
               "assets": {"sprites": spr_assets, "sounds": {}, "backgrounds": {}, "objects": objs,
                          "rooms": {"room0": {**{k: room[k] for k in ("name", "asset_type", "width", "height")},
                                              "_external_file": "rooms/room0.json"}},
                          "scripts": {}, "fonts": {}, "data": {}}}
    (folder / "project.json").write_text(json.dumps(project, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    robot = obj("thymio_1", thymio=True)
    # 1 - free arena: a clean floor, nothing else (sheets 1-3 and 6-7: buttons, colours, motors, variables, timer)
    build("thymio_fiches_1", "Thymio : arène libre", "#e8eef2", [inst("thymio_1", 450, 280)], {}, [robot])
    # 2 - an arena closed by four walls and two boxes in the way (sheet 4: proximity sensors)
    items = [inst("thymio_1", 120, 280), inst("obj_mur_v", 15, 280), inst("obj_mur_v", 885, 280),
             inst("obj_mur_h", 450, 15), inst("obj_mur_h", 450, 545),
             inst("obj_boite", 480, 260), inst("obj_boite", 680, 330)]
    build("thymio_fiches_2", "Thymio : les murs", "#e8eef2", items,
          {"spr_mur_v": (30, 560, wall), "spr_mur_h": (900, 30, wall), "spr_boite": (80, 80, wall)},
          [robot, obj("obj_mur_v", "spr_mur_v", solid=True), obj("obj_mur_h", "spr_mur_h", solid=True),
           obj("obj_boite", "spr_boite", solid=True)])
    # 3 - floor: a black band across the room and a black "table edge" on the right (sheet 5: ground sensors)
    floor = [inst("thymio_1", 120, 280), inst("obj_ruban", 470, 280), inst("obj_bord", 868, 280)]
    build("thymio_fiches_3", "Thymio : le sol", "#f4f4f4", floor,
          {"spr_ruban": (40, 540, tape), "spr_bord": (64, 560, tape)},
          [robot, obj("obj_ruban", "spr_ruban"), obj("obj_bord", "spr_bord")])


if __name__ == "__main__":
    main()
    print("written: thymio_fiches_1, _2, _3")
