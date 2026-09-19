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
    seen = {"frame": 0}

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
