"""raycast_3 sample — Unit 5 baseline (maze geometry + objects).

raycast_3 is the third Doom-style raycast sample. Its headline feature is the
in-view HUD (RAYCAST_HUD_PLAN Sessions A-B), which lands as gameplay in Unit 6;
this file pins the geometry and that the sample runs at all.

Unlike raycast_2 — whose maze came from a throwaway script that was never
committed, so its rooms can't be regenerated — raycast_3's rooms are produced by
tools/gen_raycast_3_maze.py. These tests assert the shipped rooms still match
what the generator produces, so the level design stays reviewable.

Runs through the REAL GameRunner.run() loop: the raycast render path needs
set_sprites_for_instances to have run in run()'s startup (2026-07-17 lesson).
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

SAMPLE = REPO_ROOT / "samples" / "raycast_3"
PROJECT = str(SAMPLE / "project.json")


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
            for ev in key_script.get(f, []):
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


# --- Generator / geometry --------------------------------------------------

def test_shipped_room_matches_the_generator():
    """The committed room0.json is exactly what the generator produces, so the
    maze can be regenerated and tweaked rather than being opaque data."""
    import gen_raycast_3_maze as gen
    seed, cam, counts = gen.ROOMS["room0"]
    built = gen.build_room("room0", seed, cam, counts)
    shipped = json.loads((SAMPLE / "rooms" / "room0.json").read_text(encoding="utf-8"))
    assert built["instances"] == shipped["instances"], \
        "room0.json has drifted from tools/gen_raycast_3_maze.py"
    assert built["width"] == shipped["width"] == 480
    assert built["height"] == shipped["height"] == 480


def test_maze_is_solvable_and_the_spawn_faces_an_opening():
    """Both properties the seed was CHOSEN for. The player starts at cell (0,0)
    facing angle 0 (east); a seed whose start cell is walled to the east spawns
    you nose-to-wall, which reads as a broken game."""
    import gen_raycast_3_maze as gen
    seed = gen.ROOMS["room0"][0]
    h, v = gen.carve(seed)
    gen.check_start(h, v)          # raises if walled-east or not fully connected


def test_walls_use_the_thin_edge_model():
    """Same geometry as raycast_1/raycast_2: 8px partitions centred on cell
    boundaries, not 32px blocks filling a cell."""
    room = json.loads((SAMPLE / "rooms" / "room0.json").read_text(encoding="utf-8"))
    hs = [i for i in room["instances"] if i["object_name"] == "obj_wall_h"]
    vs = [i for i in room["instances"] if i["object_name"] == "obj_wall_v"]
    assert hs and vs
    for i in hs:
        assert i["x"] % 32 == 0 and (i["y"] + 4) % 32 == 0, i
    for i in vs:
        assert (i["x"] + 4) % 32 == 0 and i["y"] % 32 == 0, i


def test_room_contents():
    room = json.loads((SAMPLE / "rooms" / "room0.json").read_text(encoding="utf-8"))
    kinds = {}
    for i in room["instances"]:
        kinds[i["object_name"]] = kinds.get(i["object_name"], 0) + 1
    assert kinds["obj_person"] == 1
    assert kinds["obj_cam0"] == 1
    assert kinds["obj_goal"] == 1
    assert kinds["obj_gem"] == 8
    assert kinds["obj_monster"] == 3


# --- Behaviour through the real loop ---------------------------------------

def test_sample_runs_with_the_textured_first_person_camera():
    runner = _runner()
    result, frames = _run(runner, {}, 40)
    assert result is not False, "game loop reported a fatal crash"
    assert frames == 40
    assert runner.current_room.name == "room0"
    cfg = runner.current_room.raycast_camera
    assert cfg["enabled"] is True
    assert cfg["wall_texture"] == "spr_wall_texture"
    assert cfg["sky_texture"] == "spr_sky"
    assert cfg["floor_texture"] == "spr_floor"


def test_player_can_walk_forward_from_the_spawn():
    """Guards the seed choice behaviourally, not just in the generator: holding
    Up from spawn must actually travel, rather than stalling against a wall."""
    runner = _runner()
    script = {3: [(pygame.KEYDOWN, pygame.K_UP)],
              50: [(pygame.KEYUP, pygame.K_UP)]}
    _run(runner, script, 60)
    player = next(i for i in runner.current_room.instances
                  if i.object_name == "obj_person")
    assert player.x > 8 + 32, \
        f"player barely moved from spawn (x={player.x}) — start cell walled in?"


def test_player_is_blocked_by_walls():
    runner = _runner()
    script = {3: [(pygame.KEYDOWN, pygame.K_UP)]}
    _run(runner, script, 150)
    room = runner.current_room
    player = next(i for i in room.instances if i.object_name == "obj_person")
    assert 0 <= player.x <= room.width, f"player left the room: x={player.x}"
    assert 0 <= player.y <= room.height, f"player left the room: y={player.y}"
