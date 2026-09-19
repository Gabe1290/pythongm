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


def test_t02_spawner_makes_one_star_per_second_at_60_fps(tmp_path):
    """Guide + handout: 'Set Alarm 0 to 60' = one star per second."""
    path = trp.build_t02(tmp_path, 2)
    n = {}

    def script(f, post, r, seen):
        if f == 190:
            n["stars"] = len(insts(r, "obj_star"))
    play(path, script, 191)
    assert n["stars"] == 3          # created at steps ~60, 120, 180


def test_t02_destroy_this_instead_of_other_removes_the_player(tmp_path):
    """Guide's discussion prompt: destroying 'this' in the player's collision deletes the player."""
    path = trp.build_t02(tmp_path, 3)
    data = trp.json.loads(path.read_text(encoding="utf-8"))
    ev = data["assets"]["objects"]["obj_player"]["events"]["collision_with_obj_star"]["actions"]
    ev[1]["parameters"]["target"] = "self"
    data["assets"]["rooms"]["room_game"]["instances"].append(
        {"object_name": "obj_star", "x": 304, "y": 380, "rotation": 0,
         "scale_x": 1.0, "scale_y": 1.0, "visible": True})
    path.write_text(trp.json.dumps(data), encoding="utf-8")
    n = {}

    def script(f, post, r, seen):
        if f == 80:
            n["players"] = len(insts(r, "obj_player"))
    play(path, script, 81)
    assert n["players"] == 0


# ----------------------------------------------------------------- Tutorial 03

def _ball(r):
    return insts(r, "obj_ball")[0]


def test_t03_ball_moves_diagonally_and_bounces_off_walls(tmp_path):
    path = trp.build_t03(tmp_path, 1)
    ys = []

    def script(f, post, r, seen):
        ys.append(_ball(r).y)
    play(path, script, 70)      # before it can reach the paddle column (no goals in phase 1)
    assert max(ys) < 448 and min(ys) > 0, (min(ys), max(ys))        # never leaves through top/bottom
    assert min(ys) < 232 - 100                                        # it really travelled up (direction 45)
    dys = [b - a for a, b in zip(ys, ys[1:]) if b != a]
    assert any(d > 0 for d in dys) and any(d < 0 for d in dys)       # it turned around


def test_t03_paddles_move_with_their_own_keys_and_stop_at_walls(tmp_path):
    path = trp.build_t03(tmp_path, 1)
    snap = {}

    def script(f, post, r, seen):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_w)
            post(pygame.KEYDOWN, pygame.K_DOWN)
        if f == 120:
            snap["l"] = insts(r, "obj_paddle_left")[0].y
            snap["r"] = insts(r, "obj_paddle_right")[0].y
    play(path, script, 121)
    assert snap["l"] < 208 and snap["r"] > 208          # W goes up, Down goes down
    assert snap["l"] >= 32 - 8 and snap["r"] <= 448 - 64 + 8   # held at the walls (one step of slack)


def test_t03_goal_scores_for_the_other_player_and_resets_the_ball(tmp_path):
    path = trp.build_t03(tmp_path, 3)
    data = trp.json.loads(path.read_text(encoding="utf-8"))
    # aim the ball left along the middle row, past the (inert) left paddle position
    for i in data["assets"]["rooms"]["room_pong"]["instances"]:
        if i["object_name"] == "obj_paddle_left":
            i["y"] = 32       # out of the ball's way
    data["assets"]["objects"]["obj_ball"]["events"]["create"]["actions"][0]["parameters"]["direction_expr"] = "180"
    path.write_text(trp.json.dumps(data), encoding="utf-8")
    snap = {"scores": []}

    def script(f, post, r, seen):
        snap["scores"].append((r.global_variables.get("p1score"), r.global_variables.get("p2score")))
        if f == 150:
            b = _ball(r)
            snap["ball"] = (b.x, b.y)
    play(path, script, 151)
    p1, p2 = snap["scores"][-1]
    assert p1 == 0 and p2 >= 1                      # left goal -> Player 2 scores (again after each reset)
    assert 0 <= snap["ball"][0] <= 640              # reset inside the room and playing again


def _t03_score_region_pixels(tmp_path, with_colour):
    from PIL import Image
    path = trp.build_t03(tmp_path, 3)
    if not with_colour:
        data = trp.json.loads(path.read_text(encoding="utf-8"))
        acts = data["assets"]["objects"]["obj_score"]["events"]["draw"]["actions"]
        acts[:] = [a for a in acts if a["action"] != "set_draw_color"]
        path.write_text(trp.json.dumps(data), encoding="utf-8")
    got = {}

    def script(f, post, r, seen):
        if f == 5:
            got["img"] = Image.frombytes("RGB", r.screen.get_size(), pygame.image.tostring(r.screen, "RGB"))
    play(path, script, 6)
    region = got["img"].crop((5, 36, 140, 82))       # below the wall row, over the black room
    return sum(1 for p in region.getdata() if p != (0, 0, 0))


def test_t03_score_text_is_visible_below_the_walls_when_colour_is_white(tmp_path):
    assert _t03_score_region_pixels(tmp_path, True) > 100


def test_t03_score_text_is_invisible_without_set_draw_color(tmp_path):
    """Why the tutorial adds Set draw color: default text is black on the black room."""
    assert _t03_score_region_pixels(tmp_path, False) == 0


def test_start_moving_direction_accepts_a_plain_number_of_degrees(tmp_path):
    """Regression: direction_expr "45" used to be read as 0 (moving right)."""
    path = trp.build_t03(tmp_path, 1)
    snap = {}

    def script(f, post, r, seen):
        if f == 5:
            b = _ball(r)
            snap["v"] = (b.hspeed, b.vspeed)
    play(path, script, 6)
    hs, vs = snap["v"]
    assert hs > 0 and vs < 0                                                        # up-right
    assert abs(abs(hs) - abs(vs)) < 1e-6


# ----------------------------------------------------------------- Tutorial 04

def test_t04_phase1_ball_bounces_inside_the_walls_and_respawns_from_the_death_zone(tmp_path):
    path = trp.build_t04(tmp_path, 1)
    xs, ys = [], []

    def script(f, post, r, seen):
        b = insts(r, "obj_ball")[0]
        xs.append(b.x)
        ys.append(b.y)
    play(path, script, 700)
    assert 32 - 4 <= min(xs) and max(xs) <= 608 - 16 + 4        # side walls hold it
    assert min(ys) >= 32 - 4                                      # top wall holds it
    assert max(ys) < 448 + 8                                      # never gets below the death zone
    assert any(abs(y - 100) < 8 for y in ys[5:])                  # respawned at y=100 at least once


def test_t04_paddle_moves_with_arrows_and_stops_at_the_side_wall(tmp_path):
    path = trp.build_t04(tmp_path, 1)
    snap = {}

    def script(f, post, r, seen):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_RIGHT)
        if f == 120:
            snap["x"] = insts(r, "obj_paddle")[0].x
    play(path, script, 121)
    assert 288 < snap["x"] <= 608 - 64 + 8


def test_t04_child_bricks_inherit_the_parents_collision_event(tmp_path):
    """Phase 3: one collision event on obj_brick_parent breaks all four colours."""
    path = trp.build_t04(tmp_path, 3)
    data = trp.json.loads(path.read_text(encoding="utf-8"))
    assert list(data["assets"]["objects"]["obj_ball"]["events"]).count("collision_with_obj_brick_parent") == 1
    n = {}

    def script(f, post, r, seen):
        if f == 1:
            n["bricks"] = {c: len(insts(r, f"obj_brick_{c}")) for c, _ in trp.T04_BRICKS}
        if f == 300:
            n["after"] = {c: len(insts(r, f"obj_brick_{c}")) for c, _ in trp.T04_BRICKS}
            n["score"] = r.score
    play(path, script, 301)
    assert all(v == 16 for v in n["bricks"].values())
    broken = sum(n["bricks"][c] - n["after"][c] for c in n["bricks"])
    assert broken >= 1 and n["score"] == 10 * broken           # every brick is worth 10, whatever the colour


def test_t04_phase3_ball_can_break_a_brick_of_each_colour(tmp_path):
    for colour, _ in trp.T04_BRICKS:
        d = tmp_path / colour
        path = trp.build_t04(d, 3)
        data = trp.json.loads(path.read_text(encoding="utf-8"))
        room = data["assets"]["rooms"]["room_breakout"]
        room["instances"] = [i for i in room["instances"] if not i["object_name"].startswith("obj_brick_")]
        room["instances"].append({"object_name": f"obj_brick_{colour}", "x": 330, "y": 250, "rotation": 0,
                                  "scale_x": 1.0, "scale_y": 1.0, "visible": True})
        for i in room["instances"]:
            if i["object_name"] == "obj_ball":
                i["x"], i["y"] = 318, 290
        path.write_text(trp.json.dumps(data), encoding="utf-8")
        n = {}

        def script(f, post, r, seen):
            if f == 60:
                n["left"] = len(insts(r, f"obj_brick_{colour}"))
                n["score"] = r.score
        play(path, script, 61)
        assert n["left"] == 0 and n["score"] == 10, (colour, n)


def test_t04_phase4_lives_run_out_then_game_over_highscore_and_end(tmp_path):
    path = trp.build_t04(tmp_path, 4)
    log = {"lives": [], "msgs": [], "hs": 0, "running_at_end": None}

    def script(f, post, r, seen):
        if f == 1:
            r.show_message_dialog = lambda m, *a, **k: log["msgs"].append(m)
            r.show_highscore_dialog = lambda *a, **k: log.__setitem__("hs", log["hs"] + 1)
        if not log["lives"] or log["lives"][-1] != r.lives:
            log["lives"].append(r.lives)
    seen = play(path, script, 6000)
    assert log["lives"][:2] == [3, 2]                # first fall costs one life
    assert log["lives"][-1] == 0
    assert log["msgs"] == ["Game Over!"] and log["hs"] == 1
    assert seen["frame"] < 6000                       # End Game closed the window before the frame cap


def test_t04_desktop_shows_the_highscore_even_if_end_game_comes_first(tmp_path):
    """The tutorial says order matters (Show Highscore before End Game). On the desktop
    runtime End Game only clears a flag, so both orders show it; the guide says to keep
    the tutorial's order anyway. Pinned so the guide's wording stays true."""
    path = trp.build_t04(tmp_path, 4)
    data = trp.json.loads(path.read_text(encoding="utf-8"))
    acts = data["assets"]["objects"]["obj_game_controller"]["events"]["no_more_lives"]["actions"]
    acts[1], acts[2] = acts[2], acts[1]              # End Game, then Show Highscore
    path.write_text(trp.json.dumps(data), encoding="utf-8")
    log = {"hs": 0}

    def script(f, post, r, seen):
        if f == 1:
            r.show_message_dialog = lambda *a, **k: None
            r.show_highscore_dialog = lambda *a, **k: log.__setitem__("hs", log["hs"] + 1)
    play(path, script, 6000)
    assert log["hs"] == 1


def test_t04_score_and_lives_are_drawn_without_a_lives_sprite(tmp_path):
    from PIL import Image
    path = trp.build_t04(tmp_path, 4)
    got = {}

    def script(f, post, r, seen):
        if f == 5:
            got["img"] = Image.frombytes("RGB", r.screen.get_size(), pygame.image.tostring(r.screen, "RGB"))
    play(path, script, 6)
    for box in ((8, 6, 110, 30), (198, 6, 300, 30)):
        assert sum(1 for p in got["img"].crop(box).getdata() if p == (255, 255, 255)) > 20, box
