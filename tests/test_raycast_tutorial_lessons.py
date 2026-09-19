"""Pins for the 2.5D (raycast) tutorial series (docs/RAYCAST_TUTORIALS_PLAN.md).

Two kinds of protection:

1. Structure -- every lesson has matching English + French index entries, the
   shared thumbnail, and the same page files in both language folders.
2. Truth -- each lesson's build-along is rebuilt here in code, exactly as the
   pages describe it, and run through the real GameRunner, so a lesson can
   never teach something the engine doesn't do. (Lesson 11's "don't skip the
   empty collision event" warning is pinned in BOTH directions: with the event
   the player is stopped by the walls; without it the player walks out.)
"""
import json
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from pathlib import Path

import pygame
import pytest
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
TUTORIALS = REPO / "Tutorials"

LESSONS = {
    "11_raycast_first_steps": [
        "01_introduction.html",
        "02_room_and_walls.html",
        "03_camera_and_controls.html",
        "04_test_and_tune.html",
    ],
    "12_raycast_textures": [
        "01_introduction.html",
        "02_textured_walls.html",
        "03_sky_and_floor.html",
        "04_tune_the_look.html",
    ],
    "13_raycast_goals_monsters": [
        "01_introduction.html",
        "02_gems_and_score.html",
        "03_monster_and_lives.html",
        "04_the_exit.html",
    ],
    "14_raycast_hud_minimap": [
        "01_introduction.html",
        "02_score_and_lives.html",
        "03_minimap.html",
        "04_status_bar.html",
    ],
}


@pytest.mark.parametrize("folder", sorted(LESSONS))
@pytest.mark.parametrize("lang_dir", ["", "fr"])
def test_lesson_is_indexed_and_complete(folder, lang_dir):
    base = TUTORIALS / lang_dir if lang_dir else TUTORIALS
    data = json.loads((base / "index.json").read_text(encoding="utf-8"))
    entries = [t for t in data["tutorials"] if t["folder"] == folder]
    assert len(entries) == 1, f"{base}: expected exactly one entry for {folder}"
    entry = entries[0]
    assert entry["pages"] == LESSONS[folder]
    assert entry["thumbnail"] == f"thumbnails/{folder}.png"
    for page in entry["pages"]:
        assert (base / folder / page).is_file(), f"{base / folder / page} missing"


@pytest.mark.parametrize("folder", sorted(LESSONS))
def test_thumbnail_matches_series_size(folder):
    with Image.open(TUTORIALS / "thumbnails" / f"{folder}.png") as im:
        assert im.size == (280, 210)


def test_lessons_hidden_from_beginner_edition():
    from config.editions import EDITIONS
    allowed = EDITIONS["beginner"]["tutorial_folders"]
    for folder in LESSONS:
        assert folder not in allowed


# ---------------------------------------------------------------------------
# Lesson 11 build-along, rebuilt in code
# ---------------------------------------------------------------------------

def _build_lesson11(root, with_collision_event):
    """The project Lesson 11 describes: a solid 32x32 obj_wall, a 16x16
    non-solid obj_player that is the camera, a 320x320 room with a border of
    walls plus three inner blocks, the player at (48, 48)."""
    (root / "sprites").mkdir(parents=True)
    Image.new("RGBA", (32, 32), (150, 150, 160, 255)).save(root / "sprites" / "spr_wall.png")
    Image.new("RGBA", (16, 16), (60, 200, 90, 255)).save(root / "sprites" / "spr_player.png")

    def spr(n, w, h):
        return {"name": n, "asset_type": "sprite", "file_path": f"sprites/{n}.png",
                "width": w, "height": h, "origin_x": 0, "origin_y": 0, "frames": 1,
                "frame_width": w, "frame_height": h, "animation_type": "single",
                "speed": 10.0, "imported": True}

    def inst(obj, x, y):
        return {"object_name": obj, "x": x, "y": y, "rotation": 0,
                "scale_x": 1.0, "scale_y": 1.0, "visible": True}

    n = 10
    instances = []
    for i in range(n):
        for x, y in ((i * 32, 0), (i * 32, (n - 1) * 32), (0, i * 32), ((n - 1) * 32, i * 32)):
            instances.append(inst("obj_wall", x, y))
    for x, y in ((128, 128), (160, 128), (128, 160)):
        instances.append(inst("obj_wall", x, y))
    instances.append(inst("obj_player", 48, 48))

    events = {
        "create": {"actions": [{"action": "enable_raycast_view", "parameters": {
            "fov": "66", "cell_size": "32", "render_distance": "20"}}]},
        "keyboard": {
            "up": {"actions": [{"action": "set_direction_speed",
                                "parameters": {"direction": "facing_angle", "speed": "3"}}]},
            "down": {"actions": [{"action": "set_direction_speed",
                                  "parameters": {"direction": "facing_angle+180", "speed": "3"}}]},
            "left": {"actions": [{"action": "set_facing_angle",
                                  "parameters": {"angle": "3", "relative": True}}]},
            "right": {"actions": [{"action": "set_facing_angle",
                                   "parameters": {"angle": "-3", "relative": True}}]},
            "nokey": {"actions": [{"action": "set_direction_speed",
                                   "parameters": {"direction": "0", "speed": "0"}}]},
        },
    }
    if with_collision_event:
        events["collision_with_obj_wall"] = {"actions": [], "target_object": "obj_wall"}

    project = {
        "name": "lesson11", "version": "1.0.0",
        "settings": {"window_width": 640, "window_height": 480, "room_speed": 30},
        "assets": {
            "sprites": {"spr_wall": spr("spr_wall", 32, 32), "spr_player": spr("spr_player", 16, 16)},
            "sounds": {}, "backgrounds": {},
            "objects": {
                "obj_wall": {"name": "obj_wall", "asset_type": "object", "sprite": "spr_wall",
                             "solid": True, "visible": True, "events": {}},
                "obj_player": {"name": "obj_player", "asset_type": "object", "sprite": "spr_player",
                               "solid": False, "visible": True, "events": events},
            },
            "rooms": {"room_main": {"name": "room_main", "asset_type": "room", "width": 320,
                                    "height": 320, "background_color": "#000000",
                                    "instances": instances}},
            "scripts": {}, "fonts": {},
        },
        "room_order": ["room_main"],
    }
    path = root / "project.json"
    path.write_text(json.dumps(project), encoding="utf-8")
    return path


def _play(project_path, script, frames):
    """Run the real game loop; `script(frame, post_key)` is called each tick.
    Returns (runner, camera_config, samples dict filled by the script)."""
    from runtime.game_runner import GameRunner
    from extensions.raycast_2_5d.state import peek_camera

    runner = GameRunner(str(project_path))
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    seen = {"frame": 0, "runner": runner}

    def post(kind, key):
        pygame.event.post(pygame.event.Event(kind, key=key))

    def player():
        return next(i for i in runner.current_room.instances if i.object_name == "obj_player")

    class Clock:
        def tick(self, fps=0):
            seen["frame"] += 1
            script(seen["frame"], post, player, seen)
            if seen["frame"] >= frames:
                seen["camera"] = peek_camera(runner.current_room)
                seen["final_xy"] = (player().x, player().y)
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real = pygame.time.Clock
    pygame.time.Clock = Clock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real
    return seen


def test_lesson11_camera_turning_and_walls_block(tmp_path):
    path = _build_lesson11(tmp_path, with_collision_event=True)

    def script(frame, post, player, seen):
        if frame == 4:
            post(pygame.KEYDOWN, pygame.K_LEFT)
        if frame == 14:
            post(pygame.KEYUP, pygame.K_LEFT)
            seen["angle_after_turn"] = getattr(player(), "facing_angle", None)
        if frame == 15:
            post(pygame.KEYDOWN, pygame.K_UP)

    seen = _play(path, script, frames=260)
    cam = seen["camera"]
    assert cam and cam["enabled"] is True
    assert cam["cell_size"] == 32 and cam["fov"] == 66.0 and cam["render_distance"] == 20
    assert seen["angle_after_turn"] and seen["angle_after_turn"] > 0     # Left turns positive
    x, y = seen["final_xy"]
    assert 0 <= x <= 320 and 0 <= y <= 320, f"player escaped the room: {(x, y)}"


def test_lesson11_without_the_empty_collision_event_walls_do_not_block(tmp_path):
    """The page's 'Don't skip this!' box: solid walls only stop an object that
    has a collision event for them."""
    path = _build_lesson11(tmp_path, with_collision_event=False)

    def script(frame, post, player, seen):
        if frame == 4:
            post(pygame.KEYDOWN, pygame.K_LEFT)
        if frame == 14:
            post(pygame.KEYUP, pygame.K_LEFT)
        if frame == 15:
            post(pygame.KEYDOWN, pygame.K_UP)

    seen = _play(path, script, frames=260)
    x, y = seen["final_xy"]
    assert not (0 <= x <= 320 and 0 <= y <= 320), f"expected escape, stayed at {(x, y)}"


# ---------------------------------------------------------------------------
# Lesson 12 build-along: textures, sky and floor
# ---------------------------------------------------------------------------

def _texture_pngs(root):
    """The three sprites Lesson 12 has students draw: a 64x64 brick wall, a
    256x64 sky panorama, a 32x32 checkered floor tile."""
    from PIL import ImageDraw
    sprites = root / "sprites"
    brick = Image.new("RGBA", (64, 64), (170, 60, 50, 255))
    d = ImageDraw.Draw(brick)
    for y in range(0, 64, 16):
        d.line([(0, y), (63, y)], fill=(230, 220, 200, 255))
        off = 0 if (y // 16) % 2 == 0 else 16
        for x in range(off, 64, 32):
            d.line([(x, y), (x, y + 15)], fill=(230, 220, 200, 255))
    brick.save(sprites / "spr_wall_texture.png")
    sky = Image.new("RGBA", (256, 64), (40, 90, 200, 255))
    ImageDraw.Draw(sky).ellipse([90, 10, 150, 34], fill=(255, 255, 255, 255))
    sky.save(sprites / "spr_sky.png")
    floor = Image.new("RGBA", (32, 32), (90, 90, 90, 255))
    ImageDraw.Draw(floor).rectangle([0, 0, 15, 15], fill=(140, 140, 140, 255))
    ImageDraw.Draw(floor).rectangle([16, 16, 31, 31], fill=(140, 140, 140, 255))
    floor.save(sprites / "spr_floor.png")


def _build_lesson12(root, **create_overrides):
    path = _build_lesson11(root, with_collision_event=True)
    _texture_pngs(root)
    project = json.loads(path.read_text(encoding="utf-8"))
    for name, w, h in (("spr_wall_texture", 64, 64), ("spr_sky", 256, 64), ("spr_floor", 32, 32)):
        project["assets"]["sprites"][name] = {
            "name": name, "asset_type": "sprite", "file_path": f"sprites/{name}.png",
            "width": w, "height": h, "origin_x": 0, "origin_y": 0, "frames": 1,
            "frame_width": w, "frame_height": h, "animation_type": "single",
            "speed": 10.0, "imported": True}
    params = project["assets"]["objects"]["obj_player"]["events"]["create"]["actions"][0]["parameters"]
    params.update({"wall_texture": "spr_wall_texture", "sky_texture": "spr_sky",
                   "floor_texture": "spr_floor"})
    params.update(create_overrides)
    path.write_text(json.dumps(project), encoding="utf-8")
    return path


def _frame(project_path, turn_frames=10):
    """Render a few frames (turning right a bit so a wall corner is in view)
    and return the final screen as an RGB PIL image plus the camera config."""
    holder = {}

    def script(frame, post, player, seen):
        if frame == 3:
            post(pygame.KEYDOWN, pygame.K_RIGHT)
        if frame == 3 + turn_frames:
            post(pygame.KEYUP, pygame.K_RIGHT)

    from runtime.game_runner import GameRunner
    from extensions.raycast_2_5d.state import peek_camera
    runner = GameRunner(str(project_path))
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    n = {"f": 0}

    class Clock:
        def tick(self, fps=0):
            n["f"] += 1
            script(n["f"], lambda k, key: pygame.event.post(pygame.event.Event(k, key=key)), None, None)
            if n["f"] >= 30:
                holder["img"] = Image.frombytes(
                    "RGB", runner.screen.get_size(),
                    pygame.image.tostring(runner.screen, "RGB"))
                holder["cam"] = peek_camera(runner.current_room)
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real = pygame.time.Clock
    pygame.time.Clock = Clock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real
    return holder["img"], holder["cam"]


def test_lesson12_textures_change_the_picture(tmp_path):
    flat_img, flat_cam = _frame(_build_lesson11(tmp_path / "flat", with_collision_event=True))
    tex_img, tex_cam = _frame(_build_lesson12(tmp_path / "tex"))
    assert tex_cam["wall_texture"] == "spr_wall_texture"
    assert tex_cam["sky_texture"] == "spr_sky"
    assert tex_cam["floor_texture"] == "spr_floor"
    assert flat_cam["sky_texture"] == "" and flat_cam["floor_texture"] == ""
    w, h = tex_img.size
    # Flat ceiling is one solid colour; a textured sky (sky-blue base + cloud)
    # differs from the flat ceiling colour along the top row.
    top_flat = {flat_img.getpixel((x, 2)) for x in range(0, w, 8)}
    top_tex = {tex_img.getpixel((x, 2)) for x in range(0, w, 8)}
    assert len(top_flat) == 1 and top_flat != top_tex
    # The checkered floor produces at least two distinct floor shades near the
    # bottom; the flat floor is a single colour.
    floor_flat = {flat_img.getpixel((x, h - 3)) for x in range(0, w, 4)}
    floor_tex = {tex_img.getpixel((x, h - 3)) for x in range(0, w, 4)}
    assert len(floor_flat) == 1 and len(floor_tex) >= 2
    assert tex_img.tobytes() != flat_img.tobytes()


def test_lesson12_textured_walls_off_restores_flat_wall_colour(tmp_path):
    img, cam = _frame(_build_lesson12(tmp_path, wall_textured=False, wall_color="#993333"))
    assert cam["wall_textured"] is False
    w, h = img.size
    centre_column = [img.getpixel((x, h // 2)) for x in range(0, w, 4)]
    assert any(abs(p[0] - 0x99) < 40 and p[1] < 90 for p in centre_column), \
        "expected the flat wall colour (#993333, shaded) in the middle rows"


def test_lesson12_blank_texture_names_fall_back_to_flat_colours(tmp_path):
    img, cam = _frame(_build_lesson12(tmp_path, sky_texture="", floor_texture="",
                                      wall_texture=""))
    w, h = img.size
    assert len({img.getpixel((x, 2)) for x in range(0, w, 8)}) == 1   # flat ceiling
    assert len({img.getpixel((x, h - 3)) for x in range(0, w, 4)}) == 1  # flat floor


# ---------------------------------------------------------------------------
# Lesson 13: gems, a monster, a gem-gated exit (built on the Lesson 11 project)
# ---------------------------------------------------------------------------

def _build_lesson13(root, gems=((96, 48),), monster=(48, 240), goal=(256, 48)):
    path = _build_lesson11(root, with_collision_event=True)
    project = json.loads(path.read_text(encoding="utf-8"))
    for name, colour in (("spr_gem", (240, 210, 40, 255)), ("spr_monster", (200, 40, 40, 255)),
                         ("spr_goal", (60, 120, 230, 255))):
        Image.new("RGBA", (16, 16), colour).save(root / "sprites" / f"{name}.png")
        project["assets"]["sprites"][name] = {
            "name": name, "asset_type": "sprite", "file_path": f"sprites/{name}.png",
            "width": 16, "height": 16, "origin_x": 0, "origin_y": 0, "frames": 1,
            "frame_width": 16, "frame_height": 16, "animation_type": "single",
            "speed": 10.0, "imported": True}

    def obj(name, sprite, events):
        project["assets"]["objects"][name] = {
            "name": name, "asset_type": "object", "sprite": sprite,
            "solid": False, "visible": True, "events": events}

    obj("obj_gem", "spr_gem", {
        "collision_with_obj_player": {"target_object": "obj_player", "actions": [
            {"action": "destroy_instance", "parameters": {"target": "self"}}]},
        "destroy": {"actions": [
            {"action": "set_score", "parameters": {"value": "10", "relative": True}}]}})
    obj("obj_monster", "spr_monster", {
        "create": {"actions": [{"action": "start_moving_direction",
                                "parameters": {"directions": ["left", "right"], "speed": "2"}}]},
        "collision_with_obj_wall": {"target_object": "obj_wall", "actions": [
            {"action": "reverse_horizontal", "parameters": {}}]}})
    obj("obj_goal", "spr_goal", {
        "collision_with_obj_player": {"target_object": "obj_player", "actions": [
            {"action": "test_instance_count",
             "parameters": {"object": "obj_gem", "number": "0", "operation": "equal"}},
            {"action": "start_block", "parameters": {}},
            {"action": "show_message", "parameters": {"message": "You win!"}},
            {"action": "restart_game", "parameters": {}},
            {"action": "end_block", "parameters": {}},
            {"action": "test_instance_count",
             "parameters": {"object": "obj_gem", "number": "0", "operation": "greater"}},
            {"action": "start_block", "parameters": {}},
            {"action": "show_message", "parameters": {"message": "Collect all the gems first!"}},
            {"action": "end_block", "parameters": {}}]}})

    pev = project["assets"]["objects"]["obj_player"]["events"]
    pev["game_start"] = {"actions": [
        {"action": "set_score", "parameters": {"value": "0", "relative": False}},
        {"action": "set_lives", "parameters": {"value": "3"}}]}
    pev["collision_with_obj_monster"] = {"target_object": "obj_monster", "actions": [
        {"action": "set_lives", "parameters": {"value": "-1", "relative": True}},
        {"action": "restart_room", "parameters": {"transition": "0"}}]}
    pev["no_more_lives"] = {"actions": [{"action": "restart_game", "parameters": {}}]}

    room = project["assets"]["rooms"]["room_main"]
    def inst(o, x, y):
        return {"object_name": o, "x": x, "y": y, "rotation": 0,
                "scale_x": 1.0, "scale_y": 1.0, "visible": True}
    for x, y in gems:
        room["instances"].append(inst("obj_gem", x, y))
    if monster:
        room["instances"].append(inst("obj_monster", *monster))
    room["instances"].append(inst("obj_goal", *goal))
    path.write_text(json.dumps(project), encoding="utf-8")
    return path


def _walk_east(frame, post, player, seen, until=120):
    if frame == 3:
        post(pygame.KEYDOWN, pygame.K_UP)


def _instances(seen, name):
    return [i for i in seen["runner"].current_room.instances if i.object_name == name]


def test_lesson13_gem_is_collected_and_scores_ten(tmp_path):
    path = _build_lesson13(tmp_path, monster=None)
    def script(frame, post, player, seen):
        _walk_east(frame, post, player, seen)
        if frame == 40:
            seen["gems"] = len(_instances(seen, "obj_gem"))
            seen["score"] = seen["runner"].score
    seen = _play(path, script, frames=41)
    assert seen["gems"] == 0 and seen["score"] == 10


def test_lesson13_monster_patrols_between_walls_and_stays_in_its_corridor(tmp_path):
    path = _build_lesson13(tmp_path)
    xs = []
    def script(frame, post, player, seen):
        m = _instances(seen, "obj_monster")
        if m:
            xs.append(m[0].x)
    _play(path, script, frames=200)
    assert max(xs) - min(xs) > 100, "monster never patrolled"
    assert min(xs) >= 32 - 4 and max(xs) <= 288 - 16 + 4, (min(xs), max(xs))


def test_lesson13_monster_touch_costs_a_life_and_restarts_the_room(tmp_path):
    path = _build_lesson13(tmp_path, monster=(80, 48), gems=())
    def script(frame, post, player, seen):
        _walk_east(frame, post, player, seen)
        history = seen.setdefault("history", [])
        lives = seen["runner"].lives
        if not history or history[-1] != lives:
            history.append(lives)
    seen = _play(path, script, frames=91)
    # the first touch costs exactly one life (later touches depend on timing)
    assert seen["history"][:2] == [3, 2]


def test_lesson13_exit_is_gated_on_the_gems(tmp_path):
    """With a gem still on the map the exit only complains; with none left it
    finishes the game (restart_game resets the score)."""
    shown = []
    for gems, expect in (((), "You win!"), (((200, 200),), "Collect all the gems first!")):
        root = tmp_path / str(len(gems)); root.mkdir()
        path = _build_lesson13(root, gems=gems, monster=None, goal=(96, 48))
        from runtime.game_runner import GameRunner
        msgs = []
        def script(frame, post, player, seen, msgs=msgs):
            _walk_east(frame, post, player, seen)
            r = seen["runner"]
            if not getattr(r, "_patched13", False):
                r._patched13 = True
                r.show_message_dialog = lambda m, *a, **k: msgs.append(m)
        _play(path, script, frames=60)
        assert expect in msgs, (gems, msgs)


# ---------------------------------------------------------------------------
# Lesson 14: HUD text, minimap, DOOM status bar (built on the Lesson 13 project)
# ---------------------------------------------------------------------------

def _build_lesson14(root, draw_actions, viewport_height=None):
    path = _build_lesson13(root, monster=None, gems=())
    project = json.loads(path.read_text(encoding="utf-8"))
    pev = project["assets"]["objects"]["obj_player"]["events"]
    if viewport_height is not None:
        pev["create"]["actions"][0]["parameters"]["viewport_height"] = str(viewport_height)
    pev["game_start"]["actions"].append(
        {"action": "set_health", "parameters": {"value": "100", "relative": False}})
    pev["draw"] = {"actions": draw_actions}
    path.write_text(json.dumps(project), encoding="utf-8")
    return path


def _screen(path, frame=6):
    holder = {}

    def script(f, post, player, seen):
        if f == frame:
            r = seen["runner"]
            holder["img"] = Image.frombytes("RGB", r.screen.get_size(),
                                            pygame.image.tostring(r.screen, "RGB"))
    _play(path, script, frames=frame + 1)
    return holder["img"]


def _count(img, box, rgb):
    region = img.crop(box)
    return sum(1 for p in region.getdata() if p == rgb)


def test_lesson14_score_and_lives_text_appears_where_you_put_it(tmp_path):
    hud = [
        {"action": "set_draw_color", "parameters": {"color": "#ffffff"}},
        {"action": "draw_score", "parameters": {"x": "8", "y": "8", "caption": "Score: "}},
        {"action": "draw_lives", "parameters": {"x": "230", "y": "6", "sprite": "spr_player"}},
    ]
    with_hud = _screen(_build_lesson14(tmp_path / "a", hud))
    without = _screen(_build_lesson14(tmp_path / "b", []))
    box = (4, 4, 110, 26)
    assert _count(with_hud, box, (255, 255, 255)) > 20
    assert _count(without, box, (255, 255, 255)) == 0
    lives_box = (226, 2, 320, 30)   # one spr_player icon per life, top right
    assert _count(with_hud, lives_box, (60, 200, 90)) > 200
    assert _count(without, lives_box, (60, 200, 90)) == 0


def test_lesson14_minimap_lands_at_its_corner_with_walls_and_player(tmp_path):
    hud = [{"action": "draw_minimap", "parameters": {
        "x": "230", "y": "10", "size": "80", "back_color": "#101018",
        "wall_color": "#8080a0", "player_color": "#ffd040"}}]
    img = _screen(_build_lesson14(tmp_path, hud))
    box = (230, 10, 310, 90)
    assert _count(img, box, (16, 16, 24)) > 500          # the panel
    assert _count(img, box, (128, 128, 160)) > 20        # the wall lines
    assert _count(img, box, (255, 208, 64)) > 3          # the player marker
    assert _count(img, (0, 100, 220, 320), (255, 208, 64)) == 0   # nothing leaks elsewhere


def test_lesson14_doom_bar_needs_viewport_height_to_leave_room(tmp_path):
    bar = [{"action": "draw_doom_hud", "parameters": {
        "x": "0", "y": "-1", "width": "0", "height": "64",
        "health_label": "HEALTH", "score_label": "SCORE "}}]
    letterboxed = _screen(_build_lesson14(tmp_path / "a", bar, viewport_height=256))
    # bottom band is the bar's dark panel, with the green health bar in it
    assert _count(letterboxed, (0, 262, 320, 320), (16, 16, 16)) > 5000
    assert _count(letterboxed, (0, 256, 320, 320), (32, 192, 32)) > 100
    # the 3D view still fills the top band (sky/wall/floor colours, not the panel)
    assert _count(letterboxed, (0, 0, 320, 250), (16, 16, 16)) == 0

    full = _screen(_build_lesson14(tmp_path / "b", bar))
    # without viewport_height the 3D view is not squeezed into the top band
    top = (0, 0, 320, 250)
    differing = sum(1 for a, b in zip(full.crop(top).getdata(), letterboxed.crop(top).getdata()) if a != b)
    assert differing > 1000


def test_lesson14_default_draw_colours_are_what_the_page_says(tmp_path):
    """Page: Draw text is black by default, Draw score is white."""
    box = (4, 4, 110, 26)
    txt = _screen(_build_lesson14(tmp_path / "t", [
        {"action": "draw_text", "parameters": {"text": "Hello", "x": "8", "y": "8"}}]))
    score = _screen(_build_lesson14(tmp_path / "s", [
        {"action": "draw_score", "parameters": {"x": "8", "y": "8", "caption": "Score: "}}]))
    assert _count(txt, box, (0, 0, 0)) > 20 and _count(txt, box, (255, 255, 255)) == 0
    assert _count(score, box, (255, 255, 255)) > 20 and _count(score, box, (0, 0, 0)) == 0
