"""Reference/checkpoint projects for the in-app tutorials.

Each ``build_tNN(root, phase)`` writes the project a student has at the END of
the given tutorial phase (1..N; the last phase is the finished game) into
``root`` -- exactly the assets, events and placements the tutorial pages tell
the student to create. They serve two purposes:

* tests/test_tutorial_reference_projects.py runs them through the real
  GameRunner, so a teacher guide can never describe behaviour the engine
  doesn't have;
* ``python tools/tutorial_reference_projects.py`` zips them for the wiki
  (teacher resources): wiki/downloads/solutions/<NN_slug>_checkpoints.zip.

Sprite art is generated (simple flat shapes) -- teachers can replace it.
"""
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent


def _art(kind, w, h, color):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if kind == "rect":
        d.rectangle((0, 0, w - 1, h - 1), fill=color)
    elif kind == "ship":
        d.polygon([(w // 2, 2), (w - 3, h - 3), (w // 2, h - 9), (3, h - 3)], fill=color)
    elif kind == "star":
        import math
        pts = []
        for i in range(10):
            r = w / 2 - 2 if i % 2 == 0 else w / 5
            a = math.pi / 5 * i - math.pi / 2
            pts.append((w / 2 + r * math.cos(a), h / 2 + r * math.sin(a)))
        d.polygon(pts, fill=color)
    elif kind == "circle":
        d.ellipse((2, 2, w - 3, h - 3), fill=color)
    return im


class Project:
    """Tiny writer for the embedded-assets project.json the engine and the IDE load."""

    def __init__(self, root, name, room_w=640, room_h=480):
        self.root = Path(root)
        (self.root / "sprites").mkdir(parents=True, exist_ok=True)
        self.data = {
            "name": name, "version": "1.0.0",
            "settings": {"window_width": room_w, "window_height": room_h, "room_speed": 60},
            "assets": {"sprites": {}, "sounds": {}, "backgrounds": {}, "objects": {},
                       "rooms": {}, "scripts": {}, "fonts": {}},
            "room_order": [],
        }

    def sprite(self, name, kind, w, h, color):
        _art(kind, w, h, color).save(self.root / "sprites" / f"{name}.png")
        self.data["assets"]["sprites"][name] = {
            "name": name, "asset_type": "sprite", "file_path": f"sprites/{name}.png",
            "width": w, "height": h, "origin_x": 0, "origin_y": 0, "frames": 1,
            "frame_width": w, "frame_height": h, "animation_type": "single",
            "speed": 10.0, "imported": True}

    def obj(self, name, sprite="", events=None, solid=False, visible=True):
        self.data["assets"]["objects"][name] = {
            "name": name, "asset_type": "object", "sprite": sprite, "solid": solid,
            "visible": visible, "events": events or {}}

    def room(self, name, width, height, placements, color="#000000"):
        self.data["assets"]["rooms"][name] = {
            "name": name, "asset_type": "room", "width": width, "height": height,
            "background_color": color,
            "instances": [{"object_name": o, "x": x, "y": y, "rotation": 0,
                           "scale_x": 1.0, "scale_y": 1.0, "visible": True} for o, x, y in placements]}
        self.data["room_order"].append(name)

    def save(self):
        (self.root / "project.json").write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        return self.root / "project.json"


def act(action, **params):
    return {"action": action, "parameters": {k: str(v) if not isinstance(v, (bool, list)) else v
                                             for k, v in params.items()}}


# ---------------------------------------------------------------------------
# Tutorial 02 - Your First Game: Catch the Star   (phases 1..4)
# ---------------------------------------------------------------------------

T02_PHASES = ["moving_player", "falling_stars", "catching_and_scoring", "finishing_touches"]


def build_t02(root, phase=4):
    p = Project(root, "CatchTheStar")
    p.sprite("spr_player", "ship", 32, 32, (70, 200, 240, 255))
    player_ev = {"keyboard": {
        "left": {"actions": [act("set_hspeed", speed=-5)]},
        "right": {"actions": [act("set_hspeed", speed=5)]},
        "nokey": {"actions": [act("stop_movement")]}}}
    placements = [("obj_player", 304, 430)]
    if phase >= 2:
        p.sprite("spr_star", "star", 32, 32, (250, 220, 40, 255))
        p.obj("obj_star", "spr_star", {"create": {"actions": [act("set_vspeed", speed=3)]}})
        p.obj("obj_spawner", "", {
            "create": {"actions": [act("set_alarm", alarm_number=0, steps=60)]},
            "alarm_0": {"actions": [act("create_instance", object="obj_star", x="irandom(600)", y=0),
                                    act("set_alarm", alarm_number=0, steps=60)]}})
        placements.append(("obj_spawner", 10, 10))
    if phase >= 3:
        player_ev["collision_with_obj_star"] = {"target_object": "obj_star", "actions": [
            act("set_score", value=10, relative=True), act("destroy_instance", target="other")]}
        p.data["assets"]["objects"]["obj_star"]["events"]["outside_room"] = {
            "actions": [act("destroy_instance", target="self")]}
        p.obj("obj_game_controller", "", {
            "create": {"actions": [act("set_score", value=0)]},
            "draw": {"actions": [act("draw_score", x=10, y=10, caption="Score: ")]}})
        placements.append(("obj_game_controller", 30, 10))
    if phase >= 4:
        player_ev["step"] = {"actions": [
            act("test_expression", expression="x < 0", then_actions=[act("set_variable", variable="x", value=0)]),
            act("test_expression", expression="x > room_width - 32",
                then_actions=[act("set_variable", variable="x", value="room_width - 32")])]}
    p.obj("obj_player", "spr_player", player_ev)
    p.room("room_game", 640, 480, placements, "#101030" if phase >= 4 else "#000000")
    return p.save()


BUILDERS = {  # folder -> (builder, phase names)
    "02_first_game": (build_t02, T02_PHASES),
}


def build_checkpoint_zips(out_dir):
    """One zip per tutorial: phaseN_<name>/ project folders, each opens in the IDE."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    made = []
    tmp = out_dir / "_tmp"
    for folder, (builder, names) in BUILDERS.items():
        shutil.rmtree(tmp, ignore_errors=True)
        for i, name in enumerate(names, 1):
            builder(tmp / f"phase{i}_{name}", i)
        zpath = out_dir / f"{folder}_checkpoints.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(tmp.rglob("*")):
                if f.is_file():
                    z.write(f, f.relative_to(tmp).as_posix())
        made.append(zpath)
    shutil.rmtree(tmp, ignore_errors=True)
    return made


if __name__ == "__main__":
    target = ROOT / "wiki" / "downloads" / "solutions"
    for z in build_checkpoint_zips(target):
        print("wrote", os.path.relpath(z, ROOT))
