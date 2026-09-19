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


# ---------------------------------------------------------------------------
# Tutorial 03 - Classic Pong   (phases 1..3)
# ---------------------------------------------------------------------------

T03_PHASES = ["paddles_and_ball", "goals_and_scoring", "score_display"]


def build_t03(root, phase=3):
    p = Project(root, "Pong")
    p.sprite("spr_ball", "circle", 16, 16, (255, 255, 255, 255))
    p.sprite("spr_paddle", "rect", 16, 64, (255, 255, 255, 255))
    p.sprite("spr_wall", "rect", 32, 32, (128, 128, 128, 255))
    p.obj("obj_wall", "spr_wall", solid=True)

    def paddle(up, down):
        return {"keyboard": {
            up: {"actions": [act("set_vspeed", speed=-8)]},
            down: {"actions": [act("set_vspeed", speed=8)]},
            "nokey": {"actions": [act("stop_movement")]}},
            "collision_with_obj_wall": {"target_object": "obj_wall", "actions": [act("stop_movement")]}}

    p.obj("obj_paddle_left", "spr_paddle", paddle("w", "s"), solid=True)
    p.obj("obj_paddle_right", "spr_paddle", paddle("up", "down"), solid=True)
    bounce = {"actions": [act("bounce")]}
    ball_ev = {
        "create": {"actions": [act("start_moving_direction", directions=[], direction_expr="45", speed=6)]},
        "collision_with_obj_wall": {"target_object": "obj_wall", **bounce},
        "collision_with_obj_paddle_left": {"target_object": "obj_paddle_left", **bounce},
        "collision_with_obj_paddle_right": {"target_object": "obj_paddle_right", **bounce}}
    placements = [("obj_paddle_left", 48, 208), ("obj_paddle_right", 576, 208), ("obj_ball", 312, 232)]
    for x in range(0, 640, 32):
        placements += [("obj_wall", x, 0), ("obj_wall", x, 448)]
    if phase >= 2:
        p.sprite("spr_goal", "rect", 32, 32, (200, 0, 0, 255))
        p.obj("obj_goal_left", "spr_goal", solid=True, visible=False)
        p.obj("obj_goal_right", "spr_goal", solid=True, visible=False)
        ball_ev["collision_with_obj_goal_left"] = {"target_object": "obj_goal_left", "actions": [
            act("set_variable", variable="p2score", value=1, scope="global", relative=True), act("jump_to_start")]}
        ball_ev["collision_with_obj_goal_right"] = {"target_object": "obj_goal_right", "actions": [
            act("set_variable", variable="p1score", value=1, scope="global", relative=True), act("jump_to_start")]}
        for y in range(32, 448, 32):
            placements += [("obj_goal_left", 0, y), ("obj_goal_right", 608, y)]
    if phase >= 3:
        p.obj("obj_score", "", {
            "create": {"actions": [act("set_variable", variable="p1score", value=0, scope="global"),
                                   act("set_variable", variable="p2score", value=0, scope="global")]},
            "draw": {"actions": [act("set_draw_color", color="#ffffff"),
                                 act("draw_text", text='"Player 1:"', x=10, y=40),
                                 act("draw_variable", x=100, y=40, variable="global.p1score"),
                                 act("draw_text", text='"Player 2:"', x=10, y=60),
                                 act("draw_variable", x=100, y=60, variable="global.p2score")]}})
        placements.append(("obj_score", 300, 100))
    p.obj("obj_ball", "spr_ball", ball_ev)
    p.room("room_pong", 640, 480, placements)
    return p.save()


# ---------------------------------------------------------------------------
# Tutorial 04 - Breakout   (phases 1..4)
# ---------------------------------------------------------------------------

T04_PHASES = ["bouncing_ball", "first_bricks", "more_bricks", "game_controller"]
T04_BRICKS = [("red", (220, 40, 40, 255)), ("orange", (240, 140, 30, 255)),
              ("yellow", (240, 220, 40, 255)), ("green", (50, 190, 70, 255))]


def build_t04(root, phase=4):
    p = Project(root, "Breakout")
    p.sprite("spr_ball", "circle", 16, 16, (255, 230, 60, 255))
    p.sprite("spr_paddle", "rect", 64, 16, (60, 110, 230, 255))
    p.sprite("spr_wall", "rect", 32, 32, (128, 128, 128, 255))
    p.sprite("spr_death_zone", "rect", 32, 32, (120, 0, 0, 255))
    p.obj("obj_wall_side", "spr_wall", solid=True)
    p.obj("obj_wall_top", "spr_wall", solid=True)
    p.obj("obj_death_zone", "spr_death_zone", visible=False)
    p.obj("obj_paddle", "spr_paddle", {"keyboard": {
        "left": {"actions": [act("set_hspeed", speed=-8)]},
        "right": {"actions": [act("set_hspeed", speed=8)]},
        "nokey": {"actions": [act("stop_movement")]}},
        "collision_with_obj_wall_side": {"target_object": "obj_wall_side", "actions": [act("stop_movement")]}},
        solid=True)
    death = [act("jump_to_position", x=320, y=100)]
    if phase >= 4:
        death.insert(0, act("set_lives", value=-1, relative=True))
    ball_ev = {
        "create": {"actions": [act("set_hspeed", speed=3), act("set_vspeed", speed=-3)]},
        "collision_with_obj_wall_side": {"target_object": "obj_wall_side", "actions": [act("reverse_horizontal")]},
        "collision_with_obj_wall_top": {"target_object": "obj_wall_top", "actions": [act("reverse_vertical")]},
        "collision_with_obj_paddle": {"target_object": "obj_paddle", "actions": [act("reverse_vertical")]},
        "collision_with_obj_death_zone": {"target_object": "obj_death_zone", "actions": death}}
    placements = [("obj_paddle", 288, 416), ("obj_ball", 312, 300)]
    for y in range(0, 448, 32):
        placements += [("obj_wall_side", 0, y), ("obj_wall_side", 608, y)]
    for x in range(32, 608, 32):
        placements.append(("obj_wall_top", x, 0))
    for x in range(0, 640, 32):
        placements.append(("obj_death_zone", x, 448))
    if phase >= 2:
        p.obj("obj_brick_parent", "", solid=True)
        ball_ev["collision_with_obj_brick_parent"] = {"target_object": "obj_brick_parent", "actions": [
            act("reverse_vertical"), act("destroy_instance", target="other"), act("set_score", value=10, relative=True)]}
        colours = T04_BRICKS if phase >= 3 else T04_BRICKS[:1]
        for row, (name, rgba) in enumerate(colours):
            p.sprite(f"spr_brick_{name}", "rect", 32, 16, rgba)
            p.obj(f"obj_brick_{name}", f"spr_brick_{name}", solid=True)
            p.data["assets"]["objects"][f"obj_brick_{name}"]["parent"] = "obj_brick_parent"
            for x in range(64, 576, 32):
                placements.append((f"obj_brick_{name}", x, 64 + 16 * row))
    if phase >= 4:
        p.obj("obj_game_controller", "", {
            "create": {"actions": [act("set_lives", value=3), act("set_score", value=0)]},
            "draw": {"actions": [act("draw_score", x=10, y=10, caption="Score: "),
                                 act("draw_lives", x=200, y=10)]},
            "no_more_lives": {"actions": [act("show_message", message="Game Over!"),
                                          act("show_highscore"), act("end_game")]}})
        placements.append(("obj_game_controller", 300, 200))
    p.obj("obj_ball", "spr_ball", ball_ev)
    p.room("room_breakout", 640, 480, placements)
    return p.save()


BUILDERS = {  # folder -> (builder, phase names)
    "02_first_game": (build_t02, T02_PHASES),
    "03_pong": (build_t03, T03_PHASES),
    "04_breakout": (build_t04, T04_PHASES),
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
