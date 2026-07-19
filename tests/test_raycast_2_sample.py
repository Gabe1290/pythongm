"""End-to-end smoke test for the raycast_2 sample (Level 2), Unit 1 baseline.

raycast_2 is a bigger Doom-style maze built on the (complete) raycast 2.5D
engine — a recursive-backtracker maze converted to raycast_1's thin edge-wall
model (obj_wall_h/obj_wall_v), reusing obj_person / obj_goal and the textured
wall/sky/floor. This pins that the sample loads, enables the first-person
camera, turns in response to input, and (crucially — see the raycast_1 lesson
about registered collision handlers gating the movement-block) that the player
is stopped by walls rather than walking out of the room.

Runs through the REAL GameRunner.run() loop: the raycast render path needs
set_sprites_for_instances to have run in run()'s startup, so a hand-built room
would smoke-pass for the wrong reason.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

PROJECT = str(REPO_ROOT / "samples" / "raycast_2" / "project.json")


def _runner():
    from runtime.game_runner import GameRunner
    runner = GameRunner(PROJECT)
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.show_highscore_dialog = lambda *a, **k: None
    runner._show_name_entry_dialog = lambda *a, **k: ""
    runner.process_pending_messages = lambda *a, **k: None
    return runner


def _run(runner, key_script, max_frames):
    state = {"frames": 0}

    class _FakeClock:
        def tick(self, fps=0):
            f = state["frames"] = state["frames"] + 1
            for at, ev in key_script.get(f, []):
                pygame.event.post(pygame.event.Event(ev[0], key=ev[1]))
            if f >= max_frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        result = runner.run()
    finally:
        pygame.time.Clock = real
    return result, state["frames"]


def test_raycast_2_runs_and_enables_first_person_camera():
    runner = _runner()
    # Hold LEFT (turn) frames 5..35 -> 30 * 3 deg = 90 degrees.
    script = {
        5: [("kd", (pygame.KEYDOWN, pygame.K_LEFT))],
        35: [("ku", (pygame.KEYUP, pygame.K_LEFT))],
    }
    result, frames = _run(runner, script, 60)

    assert result is not False, "game loop reported a fatal crash"
    assert frames == 60
    assert runner.current_room.name == "room0"
    assert runner.current_room.raycast_camera["enabled"] is True
    # Textured raycast config carried over from raycast_1's create event.
    cfg = runner.current_room.raycast_camera
    assert cfg["wall_texture"] == "spr_wall_texture"
    assert cfg["sky_texture"] == "spr_sky"
    assert cfg["floor_texture"] == "spr_floor"

    player = next(i for i in runner.current_room.instances
                  if i.object_name == "obj_person")
    assert player.facing_angle == pytest.approx(90.0, abs=0.01)


def test_raycast_2_player_is_blocked_by_walls():
    runner = _runner()
    # Hold UP (move forward) far longer than the room is wide; the player must
    # stay inside the 480x480 room (registered collision_with_obj_wall_* gates
    # the movement-block — copied from raycast_1's obj_person).
    script = {3: [("kd", (pygame.KEYDOWN, pygame.K_UP))]}
    result, frames = _run(runner, script, 120)

    assert result is not False
    player = next(i for i in runner.current_room.instances
                  if i.object_name == "obj_person")
    assert -8 <= player.x <= 480, f"player x escaped the room: {player.x}"
    assert -8 <= player.y <= 480, f"player y escaped the room: {player.y}"


def test_gems_placed_and_registered():
    """Unit 2: obj_gem billboards are scattered and wired to score + destroy."""
    import json
    root = REPO_ROOT / "samples" / "raycast_2"
    room = json.loads((root / "rooms" / "room0.json").read_text(encoding="utf-8"))
    gems = [i for i in room["instances"] if i.get("object_name") == "obj_gem"]
    assert len(gems) >= 4, "expected several collectible gems"

    obj = json.loads((root / "objects" / "obj_gem.json").read_text(encoding="utf-8"))
    assert obj["solid"] is False and obj["sprite"] == "spr_gem"   # billboard, not a wall
    ev = obj["events"]
    # collision destroys self; the destroy event awards score (maze_2 pattern)
    assert ev["collision_with_obj_person"]["actions"][0]["action"] == "destroy_instance"
    assert ev["destroy"]["actions"][0]["action"] == "set_score"
    assert ev["destroy"]["actions"][0]["parameters"].get("relative") is True

    proj = json.loads((root / "project.json").read_text(encoding="utf-8"))
    assert "obj_gem" in proj["assets"]["objects"]
    assert "spr_gem" in proj["assets"]["sprites"]


def test_gem_collision_awards_score_and_destroys():
    """Colliding with a gem (via the real event dispatch) destroys it and adds
    10 to the score through its destroy event — run through the loop so the
    destroy/cleanup phase actually fires."""
    runner = _runner()
    hit = {"done": False}

    def _fire(runner):
        gems = [i for i in runner.current_room.instances
                if i.object_name == "obj_gem"]
        if gems and not hit["done"]:
            hit["done"] = True
            g = gems[0]
            runner.action_executor.execute_event(
                g, "collision_with_obj_person", g.object_data["events"])

    state = {"frames": 0}

    class _FakeClock:
        def tick(self, fps=0):
            f = state["frames"] = state["frames"] + 1
            if f == 5:
                _fire(runner)                 # collide with a gem
            if f >= 20:                        # let cleanup fire the destroy event
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    n_before = None
    real = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        # snapshot gem count after startup by hooking the first tick
        runner.run()
    finally:
        pygame.time.Clock = real

    gems_after = [i for i in runner.current_room.instances
                  if i.object_name == "obj_gem" and not getattr(i, "_destroyed", False)]
    assert hit["done"], "never found a gem to collide with"
    assert runner.score == 10, f"score should be 10 after one gem, got {runner.score}"
    assert len(gems_after) == 7, f"one gem should be gone, {len(gems_after)} remain"


def test_score_hud_enabled_from_start():
    """Unit 2 polish: set_score 0 in obj_person's create enables the window
    caption score HUD from frame 1 (in-view HUD is a tracked engine follow-up)."""
    import json
    create = json.loads((REPO_ROOT / "samples" / "raycast_2" / "objects"
                         / "obj_person.json").read_text(encoding="utf-8")
                        )["events"]["create"]["actions"]
    assert create[0]["action"] == "set_score"      # runs before enable_raycast_view

    runner = _runner()
    _run(runner, {}, 5)
    assert runner.show_score_in_caption is True
    assert runner.score == 0


def test_gem_sprite_sized_for_billboard():
    """The placeholder gem was resized to 32px so it reads in the raycast view."""
    import json
    s = json.loads((REPO_ROOT / "samples" / "raycast_2" / "sprites"
                    / "spr_gem.json").read_text(encoding="utf-8"))
    assert s["width"] == 32 and s["height"] == 32
    assert s["origin_x"] == 16 and s["origin_y"] == 16


def test_raycast_2_room0_is_a_thin_wall_maze():
    """The generated room uses raycast_1's thin edge-wall objects, not
    full-cell blocks — a sanity check on the geometry conversion."""
    import json
    room = json.loads((REPO_ROOT / "samples" / "raycast_2" / "rooms"
                       / "room0.json").read_text(encoding="utf-8"))
    names = [i.get("object_name") for i in room["instances"]]
    assert names.count("obj_wall_h") > 40
    assert names.count("obj_wall_v") > 40
    assert names.count("obj_person") == 1
    assert names.count("obj_goal") == 1
    assert room["width"] == 480 and room["height"] == 480
