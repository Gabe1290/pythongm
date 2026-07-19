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
