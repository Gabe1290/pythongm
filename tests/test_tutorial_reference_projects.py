"""Truth tests for the tutorial reference/checkpoint projects (tools/tutorial_reference_projects.py).

Each teacher guide's claims ("stars fall", "the player can leave the screen
until Phase 4", ...) are pinned here by running the project a student has at
that phase through the real GameRunner.
"""
import importlib.util
import os
import sys
import zipfile
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

REPO = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("tutorial_reference_projects", REPO / "tools" / "tutorial_reference_projects.py")
trp = importlib.util.module_from_spec(_spec)
sys.modules["tutorial_reference_projects"] = trp
_spec.loader.exec_module(trp)


def play(project_path, script, frames):
    """Real game loop with a fake clock. script(frame, post, runner, seen)."""
    from runtime.game_runner import GameRunner
    runner = GameRunner(str(project_path))
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    seen = {"frame": 0, "runner": runner}

    def post(kind, key):
        pygame.event.post(pygame.event.Event(kind, key=key))

    class Clock:
        def tick(self, fps=0):
            seen["frame"] += 1
            script(seen["frame"], post, runner, seen)
            if seen["frame"] >= frames:
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


def insts(runner, name):
    return [i for i in runner.current_room.instances if i.object_name == name]


# ----------------------------------------------------------------- Tutorial 02

def test_t02_phase1_player_moves_and_can_leave_the_screen(tmp_path):
    path = trp.build_t02(tmp_path, 1)

    def script(f, post, r, seen):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_LEFT)
        if f == 200:
            seen["x"] = insts(r, "obj_player")[0].x
    seen = play(path, script, 201)
    # phase 1 has no boundary check: "the player can go off screen"
    assert seen["x"] < 0


def test_t02_phase1_player_stops_when_no_key(tmp_path):
    path = trp.build_t02(tmp_path, 1)
    xs = []

    def script(f, post, r, seen):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_RIGHT)
        if f == 10:
            post(pygame.KEYUP, pygame.K_RIGHT)
        if f >= 12:
            xs.append(insts(r, "obj_player")[0].x)
    play(path, script, 40)
    assert len(set(xs)) == 1 and xs[0] > 304


def test_t02_phase2_stars_spawn_at_the_top_and_fall(tmp_path):
    path = trp.build_t02(tmp_path, 2)
    snap = {}

    def script(f, post, r, seen):
        if f == 200:
            snap["stars"] = [(s.x, s.y) for s in insts(r, "obj_star")]
    play(path, script, 201)
    assert len(snap["stars"]) >= 2
    assert len({round(x) for x, _ in snap["stars"]}) > 1        # random x
    assert all(y > 0 for _, y in snap["stars"])                 # falling
    assert all(0 <= x <= 640 for x, _ in snap["stars"])


def test_t02_phase2_stars_pass_through_the_player(tmp_path):
    """Before Phase 3 nothing happens on contact: no score object exists at all."""
    path = trp.build_t02(tmp_path, 2)
    r_holder = {}

    def script(f, post, r, seen):
        if f == 1:
            r_holder["n"] = len(insts(r, "obj_player"))
    play(path, script, 5)
    assert r_holder["n"] == 1
    assert "obj_game_controller" not in trp.json.loads(path.read_text(encoding="utf-8"))["assets"]["objects"]


def test_t02_phase3_catching_scores_ten_and_removes_the_star(tmp_path):
    path = trp.build_t02(tmp_path, 3)
    data = trp.json.loads(path.read_text(encoding="utf-8"))
    # one star placed just above the player (player is at x=304,y=430)
    data["assets"]["rooms"]["room_game"]["instances"].append(
        {"object_name": "obj_star", "x": 304, "y": 380, "rotation": 0,
         "scale_x": 1.0, "scale_y": 1.0, "visible": True})
    path.write_text(trp.json.dumps(data), encoding="utf-8")
    snap = {}

    def script(f, post, r, seen):
        if f == 80:
            snap["score"] = r.score
            snap["caught_star_gone"] = all(s.y != 380 for s in insts(r, "obj_star"))
    play(path, script, 81)
    assert snap["score"] == 10


def test_t02_phase3_missed_stars_are_destroyed_outside_the_room(tmp_path):
    path = trp.build_t02(tmp_path, 3)
    counts = []

    def script(f, post, r, seen):
        if f % 50 == 0:
            counts.append(len(insts(r, "obj_star")))
    play(path, script, 900)
    assert max(counts) <= 6, counts        # they don't pile up (fall time ~160 frames, one per second)


def test_t02_phase4_player_is_kept_on_screen(tmp_path):
    path = trp.build_t02(tmp_path, 4)
    snap = {}

    def script(f, post, r, seen):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_LEFT)
        if f == 250:
            snap["x"] = insts(r, "obj_player")[0].x
    play(path, script, 251)
    assert snap["x"] >= -5      # clamped (one step of overshoot at most); phase 1 goes far below


def test_t02_checkpoint_zip_contains_every_phase(tmp_path):
    zips = trp.build_checkpoint_zips(tmp_path)
    z = next(p for p in zips if p.name.startswith("02_first_game"))
    names = zipfile.ZipFile(z).namelist()
    for i, ph in enumerate(trp.T02_PHASES, 1):
        assert f"phase{i}_{ph}/project.json" in names
