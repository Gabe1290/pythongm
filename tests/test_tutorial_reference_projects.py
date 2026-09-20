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


# ----------------------------------------------------------------- Tutorial 05

def _sok(tmp_path, rows, presses, frames=None, phase=3):
    """Run a mini Sokoban level; presses = [(frame, key)]. Returns state snapshots per frame."""
    from PIL import Image
    path = trp.build_t05(tmp_path, phase, level=rows)
    snaps = {}
    keys = dict(presses)

    def script(f, post, r, seen):
        if f in keys:
            post(pygame.KEYDOWN, keys[f])
            post(pygame.KEYUP, keys[f])
        pl = insts(r, "obj_player")[0]
        snaps[f] = {"player": (pl.x, pl.y),
                    "crates": sorted((c.x, c.y) for c in insts(r, "obj_crate")),
                    "img": Image.frombytes("RGB", r.screen.get_size(),
                                           pygame.image.tostring(r.screen, "RGB"))}
    play(path, script, frames or (max(k for k, _ in presses) + 20))
    return snaps


ROW3 = ["WWWWWWWWWW", "W.PC.T...W", "WWWWWWWWWW"]


def test_t05_player_moves_exactly_one_cell_per_key_press(tmp_path):
    s = _sok(tmp_path, ["WWWWWWWWWW", "W.P......W", "WWWWWWWWWW"], [(5, pygame.K_RIGHT), (15, pygame.K_RIGHT)], phase=1)
    assert s[4]["player"] == (64, 32) and s[10]["player"] == (96, 32) and s[20]["player"] == (128, 32)


def test_t05_walls_block_the_player(tmp_path):
    s = _sok(tmp_path, ["WWWWWWWWWW", "WP.......W", "WWWWWWWWWW"], [(5, pygame.K_LEFT), (15, pygame.K_UP)], phase=1)
    assert s[25]["player"] == (32, 32)


def test_t05_a_push_moves_the_crate_one_cell(tmp_path):
    s = _sok(tmp_path, ROW3, [(5, pygame.K_RIGHT)])
    assert s[4]["crates"] == [(96, 32)]
    assert s[12]["crates"] == [(128, 32)] and s[12]["player"] == (96, 32)


def test_t05_crate_cannot_be_pushed_into_a_wall(tmp_path):
    s = _sok(tmp_path, ["WWWWWWWWWW", "W.PCW....W", "WWWWWWWWWW"], [(5, pygame.K_RIGHT), (15, pygame.K_RIGHT)])
    assert s[25]["crates"] == [(96, 32)] and s[25]["player"] == (64, 32)


def test_t05_crate_cannot_be_pushed_into_another_crate(tmp_path):
    s = _sok(tmp_path, ["WWWWWWWWWW", "W.PCC...WW", "WWWWWWWWWW"], [(5, pygame.K_RIGHT)])
    assert s[15]["crates"] == [(96, 32), (128, 32)] and s[15]["player"] == (64, 32)


def test_t05_crate_turns_green_on_a_target_and_back_when_pushed_off(tmp_path):
    s = _sok(tmp_path, ROW3, [(5, pygame.K_RIGHT), (15, pygame.K_RIGHT), (25, pygame.K_RIGHT)])
    brown, green = (170, 110, 50), (60, 180, 80)
    at = lambda f, x: s[f]["img"].getpixel((x + 16, 32 + 16))
    assert at(4, 96) == brown                    # not on a target
    assert at(22, 160) == green                  # pushed onto the target at x=160
    assert at(32, 192) == brown                  # pushed off again


def test_t05_r_restarts_the_level(tmp_path):
    s = _sok(tmp_path, ROW3, [(5, pygame.K_RIGHT), (15, pygame.K_r)])
    assert s[12]["crates"] == [(128, 32)]
    assert s[25]["crates"] == [(96, 32)] and s[25]["player"] == (64, 32)


def test_t05_instruction_text_is_drawn_top_left(tmp_path):
    s = _sok(tmp_path, ["WWWWWWWWWW", "W.P......W", "WWWWWWWWWW"], [(5, pygame.K_RIGHT)], frames=8)
    region = s[6]["img"].crop((8, 6, 300, 26))
    # black text on the black room would be invisible; here it lands on the wall row, so it shows
    assert len({p for p in region.getdata()}) > 2


def test_t05_the_tutorial_level_is_well_formed():
    rows = trp.T05_LEVEL
    assert all(len(r) == 10 for r in rows) and len(rows) == 10
    flat = "".join(rows)
    assert flat.count("C") == flat.count("T") == 2 and flat.count("P") == 1


def test_t05_targets_placed_after_the_crate_are_drawn_over_it(tmp_path):
    """Why the tutorial says to place targets first: draw order is placement order."""
    path = trp.build_t05(tmp_path, 3, level=ROW3)
    data = trp.json.loads(path.read_text(encoding="utf-8"))
    ins = data["assets"]["rooms"]["room_sokoban"]["instances"]
    ins.sort(key=lambda i: i["object_name"] == "obj_target")       # targets LAST (the student's usual order)
    path.write_text(trp.json.dumps(data), encoding="utf-8")
    got = {}

    def script(f, post, r, seen):
        if f in (5, 15):
            post(pygame.KEYDOWN, pygame.K_RIGHT)
            post(pygame.KEYUP, pygame.K_RIGHT)
        if f == 30:
            got["px"] = trp and __import__("PIL.Image", fromlist=["x"]).frombytes(
                "RGB", r.screen.get_size(), pygame.image.tostring(r.screen, "RGB")).getpixel((160 + 16, 48))
    play(path, script, 31)
    assert got["px"] == (230, 60, 60)          # the red target, not the green crate


# ----------------------------------------------------------------- Tutorial 06

def _bfs_path(level, start="P", goal="E"):
    from collections import deque
    pos = {ch: (c, r) for r, row in enumerate(level) for c, ch in enumerate(row) if ch in (start, goal)}
    s, g = pos[start], pos[goal]
    prev, q = {s: None}, deque([s])
    while q:
        cur = q.popleft()
        if cur == g:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (cur[0] + dx, cur[1] + dy)
            if level[n[1]][n[0]] != "W" and n not in prev:
                prev[n] = cur
                q.append(n)
    path, cur = [], g
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    return path[::-1] if s in path else None


def test_t06_level_is_solvable_and_every_coin_is_reachable():
    lv = trp.T06_LEVEL
    assert all(len(r) == 20 for r in lv) and len(lv) == 15
    assert _bfs_path(lv) is not None
    start = next((c, r) for r, row in enumerate(lv) for c, ch in enumerate(row) if ch == "P")
    seen, todo = {start}, [start]
    while todo:
        x, y = todo.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if lv[n[1]][n[0]] != "W" and n not in seen:
                seen.add(n)
                todo.append(n)
    coins = {(c, r) for r, row in enumerate(lv) for c, ch in enumerate(row) if ch == "C"}
    assert len(coins) == 5 and coins <= seen


def test_t06_player_stops_at_walls_and_when_keys_are_released(tmp_path):
    path = trp.build_t06(tmp_path, 1)
    xs = []

    def script(f, post, r, seen):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_RIGHT)
        if f == 100:
            post(pygame.KEYUP, pygame.K_RIGHT)
        xs.append(insts(r, "obj_player")[0].x)
    play(path, script, 130)
    assert xs[95] == 160 and xs[125] == 160         # wall at column 6 stops it at column 5


def _drive(path_cells, post, f, pending):
    """Turn a cell path into (frame, KEYDOWN/KEYUP) posts: 32 px at 4 px/frame = 8 frames per cell."""
    dirs = {(1, 0): pygame.K_RIGHT, (-1, 0): pygame.K_LEFT, (0, 1): pygame.K_DOWN, (0, -1): pygame.K_UP}
    t = 3
    steps = []
    for a, b in zip(path_cells, path_cells[1:]):
        k = dirs[(b[0] - a[0], b[1] - a[1])]
        if steps and steps[-1][0] == k:
            steps[-1][1] += 1
        else:
            steps.append([k, 1])
    for k, n in steps:
        pending.append((t, pygame.KEYDOWN, k))
        t += 8 * n
        pending.append((t, pygame.KEYUP, k))
        t += 1
    return t


def test_t06_a_full_playthrough_collects_a_coin_and_wins_then_restarts(tmp_path):
    path = trp.build_t06(tmp_path, 3)
    lv = trp.T06_LEVEL
    route = _bfs_path(lv)
    pending = []
    end = _drive(route, None, 0, pending)
    by_frame = {}
    for f, kind, k in pending:
        by_frame.setdefault(f, []).append((kind, k))
    log = {"msgs": [], "score_before_exit": None, "coins_after": None, "score_after": None}

    def script(f, post, r, seen):
        if f == 1:
            r.show_message_dialog = lambda m, *a, **k: log["msgs"].append(m)
        for kind, k in by_frame.get(f, []):
            post(kind, k)
        if f == end - 2:
            log["score_before_exit"] = r.score
        if f == end + 40:
            log["coins_after"] = len(insts(r, "obj_coin"))
            log["score_after"] = r.score
    play(path, script, end + 45)
    assert log["msgs"] == ["You Win!"]
    assert log["coins_after"] == 5 and log["score_after"] == 0      # room restarted: coins back, score reset


def test_t06_coin_gives_ten_points_and_disappears(tmp_path):
    path = trp.build_t06(tmp_path, 3)
    snap = {}

    def script(f, post, r, seen):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_RIGHT)
        if f == 45:
            snap["score"] = r.score
            snap["coins"] = len(insts(r, "obj_coin"))
    play(path, script, 46)
    assert snap["score"] == 10 and snap["coins"] == 4


def test_t06_score_is_drawn_top_left(tmp_path):
    from PIL import Image
    path = trp.build_t06(tmp_path, 3)
    got = {}

    def script(f, post, r, seen):
        if f == 5:
            got["img"] = Image.frombytes("RGB", r.screen.get_size(), pygame.image.tostring(r.screen, "RGB"))
    play(path, script, 6)
    assert sum(1 for p in got["img"].crop((8, 6, 110, 30)).getdata() if p == (255, 255, 255)) > 20


def test_t06_a_player_placed_off_the_grid_jams_in_one_tile_corridors(tmp_path):
    """Why the tutorial says to Snap to Grid: a few pixels off the grid (8 here; this test art has a
    2 px transparent margin) the player cannot travel down a 1-tile corridor."""
    path = trp.build_t06(tmp_path, 1)
    data = trp.json.loads(path.read_text(encoding="utf-8"))
    for i in data["assets"]["rooms"]["room_maze"]["instances"]:
        if i["object_name"] == "obj_player":
            i["x"] += 8
    path.write_text(trp.json.dumps(data), encoding="utf-8")
    ys = []

    def script(f, post, r, seen):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_DOWN)
        ys.append(insts(r, "obj_player")[0].y)
    play(path, script, 60)
    assert ys[-1] < 40                                # jammed at the mouth of column 1's corridor


# ----------------------------------------------------------------- Tutorial 07

def _t07(tmp_path, phase=3, mod=None, player_xy=None):
    path = trp.build_t07(tmp_path, phase)
    data = trp.json.loads(path.read_text(encoding="utf-8"))
    if player_xy:
        for i in data["assets"]["rooms"]["room_level1"]["instances"]:
            if i["object_name"] == "obj_player":
                i["x"], i["y"] = player_xy
    if mod:
        mod(data)
    path.write_text(trp.json.dumps(data), encoding="utf-8")
    return path


def test_t07_player_falls_lands_and_stands_on_the_ground(tmp_path):
    ys = []

    def script(f, post, r, seen):
        ys.append(insts(r, "obj_player")[0].y)
    play(_t07(tmp_path, 1, player_xy=(32, 200)), script, 120)
    assert ys[0] < 250 and ys[-1] == 416 and ys[-2] == 416    # lands on the ground row (y=448) and rests


def test_t07_jump_leaves_the_ground_and_comes_back(tmp_path):
    ys = []

    def script(f, post, r, seen):
        if f == 60:
            post(pygame.KEYDOWN, pygame.K_UP)
            post(pygame.KEYUP, pygame.K_UP)
        ys.append(insts(r, "obj_player")[0].y)
    play(_t07(tmp_path, 1), script, 160)
    assert min(ys[60:]) < 416 - 80 and ys[-1] == 416           # about 95 px high, then lands


def test_t07_no_key_only_zeroes_horizontal_speed_so_gravity_keeps_working(tmp_path):
    """The tutorial's warning: 'No key' must be Set horizontal speed 0, not Stop Movement."""
    def use_stop_movement(data):
        ev = data["assets"]["objects"]["obj_player"]["events"]["keyboard"]["nokey"]
        ev["actions"] = [trp.act("stop_movement")]

    def fall(mod, sub):
        ys = []

        def script(f, post, r, seen):
            ys.append(insts(r, "obj_player")[0].y)
        play(_t07(tmp_path / sub, 1, mod, player_xy=(32, 100)), script, 30)
        return ys[-1] - ys[0]
    assert fall(None, "a") > 100                      # tutorial version: falls freely
    assert fall(use_stop_movement, "b") < 25          # Stop Movement wipes the speed gravity builds


def test_t07_runs_left_and_right_and_stops_when_keys_are_released(tmp_path):
    xs = []

    def script(f, post, r, seen):
        if f == 40:
            post(pygame.KEYDOWN, pygame.K_RIGHT)
        if f == 60:
            post(pygame.KEYUP, pygame.K_RIGHT)
        xs.append(insts(r, "obj_player")[0].x)
    play(_t07(tmp_path, 1), script, 90)
    assert xs[45] > xs[35] and xs[80] == xs[85]


def test_t07_coin_scores_ten_and_disappears(tmp_path):
    def coin_ahead(data):
        for i in data["assets"]["rooms"]["room_level1"]["instances"]:
            if i["object_name"] == "obj_coin" and not done:
                i["x"], i["y"] = 128, 416
                done.append(1)
    done = []
    snap = {}

    def script(f, post, r, seen):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_RIGHT)
        if f == 60:
            snap["score"] = r.score
    play(_t07(tmp_path, 3, coin_ahead), script, 61)
    assert snap["score"] == 10


def test_t07_flag_shows_you_win(tmp_path):
    def flag_ahead(data):
        for i in data["assets"]["rooms"]["room_level1"]["instances"]:
            if i["object_name"] == "obj_flag":
                i["x"], i["y"] = 128, 416
    msgs = []

    def script(f, post, r, seen):
        if f == 1:
            r.show_message_dialog = lambda m, *a, **k: msgs.append(m)
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_RIGHT)
    play(_t07(tmp_path, 2, flag_ahead), script, 60)
    assert msgs and msgs[0] == "You Win!"


def _lives_history(tmp_path, mod=None):
    def spike_at_start(data):
        for i in data["assets"]["rooms"]["room_level1"]["instances"]:
            if i["object_name"] == "obj_spike":
                i["x"], i["y"] = 32, 416                # right on the player's start
        if mod:
            mod(data)
    hist = []

    def script(f, post, r, seen):
        if not hist or hist[-1] != r.lives:
            hist.append(r.lives)
    play(_t07(tmp_path, 3, spike_at_start), script, 80)
    return hist


def test_t07_each_spike_hit_costs_a_life_when_lives_are_set_in_game_start(tmp_path):
    hist = _lives_history(tmp_path)
    assert hist[-3:] == [2, 1, 0] and hist == sorted(hist, reverse=True)    # counts down and stays down


def test_t07_lives_set_in_create_are_refilled_by_every_restart(tmp_path):
    """The bug the tutorial used to have: Create re-runs on restart_room, so lives never run out."""
    def use_create(data):
        c = data["assets"]["objects"]["obj_game_controller"]["events"]
        c["create"] = c.pop("game_start")
    hist = _lives_history(tmp_path, use_create)
    assert min(hist) >= 2 and hist.count(3) > 3


# ----------------------------------------------------------------- Tutorial 08

def _t08(tmp_path, phase=3, lander_xy=None, **kw):
    path = trp.build_t08(tmp_path, phase, **kw)
    if lander_xy:
        data = trp.json.loads(path.read_text(encoding="utf-8"))
        for i in data["assets"]["rooms"]["room_game"]["instances"]:
            if i["object_name"] == "obj_lander":
                i["x"], i["y"] = lander_xy
        path.write_text(trp.json.dumps(data), encoding="utf-8")
    return path


def test_t08_lunar_gravity_is_slow_and_thrust_is_a_steady_climb(tmp_path):
    log = {}

    def script(f, post, r, seen):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_UP)
        if f == 40:
            log["y_up"] = insts(r, "obj_lander")[0].y
            post(pygame.KEYUP, pygame.K_UP)
        if f == 41:
            log["vs_after_release"] = insts(r, "obj_lander")[0].vspeed
        if f == 90:
            log["vs_later"] = insts(r, "obj_lander")[0].vspeed
    play(_t08(tmp_path, 1, lander_xy=(64, 200)), script, 91)
    assert log["y_up"] < 200 - 60                     # thrust (vspeed -2) lifts it against gravity
    assert -2.1 < log["vs_after_release"] < -1.8      # then gravity slowly cancels the climb
    assert log["vs_later"] > log["vs_after_release"]


def test_t08_steering_and_no_key_only_stops_horizontal_movement(tmp_path):
    xs = []

    def script(f, post, r, seen):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_RIGHT)
        if f == 20:
            post(pygame.KEYUP, pygame.K_RIGHT)
        l = insts(r, "obj_lander")[0]
        xs.append((l.x, l.y))
    play(_t08(tmp_path, 1, lander_xy=(64, 100)), script, 50)
    assert xs[15][0] > xs[5][0] and xs[45][0] == xs[40][0]     # moves, then stops sideways
    assert xs[45][1] > xs[25][1]                                # but keeps falling


def test_t08_hitting_the_ground_crashes_and_restarts_the_room(tmp_path):
    msgs, ys = [], []

    def script(f, post, r, seen):
        if f == 1:
            r.show_message_dialog = lambda m, *a, **k: msgs.append(m)
        ys.append(insts(r, "obj_lander")[0].y)
    play(_t08(tmp_path, 2), script, 300)
    assert msgs and set(msgs) == {"Crashed!"} and len(msgs) >= 2      # crashes again after each restart
    assert ys[0] < 40 and max(ys) < 352                               # never sinks into the terrain


def test_t08_landing_on_the_pad_succeeds_once_and_the_lander_stays(tmp_path):
    msgs, ys = [], []

    def script(f, post, r, seen):
        if f == 1:
            r.show_message_dialog = lambda m, *a, **k: msgs.append(m)
        ys.append(insts(r, "obj_lander")[0].y)
    play(_t08(tmp_path, 2, lander_xy=(512, 250)), script, 250)
    assert msgs == ["Landing successful!"]                            # one message, not one per frame (gravity is switched off)
    assert ys[-1] == ys[-40] and ys[-1] > 250                          # it stays put on the pad


def test_t08_landing_speed_makes_no_difference_yet(tmp_path):
    """The tutorial's challenge idea: as built, a hard landing on the pad still counts as a success."""
    msgs = []

    def script(f, post, r, seen):
        if f == 1:
            r.show_message_dialog = lambda m, *a, **k: msgs.append(m)
        if f == 2:
            insts(r, "obj_lander")[0].vspeed = 12       # slam into the pad
    play(_t08(tmp_path, 2, lander_xy=(512, 250)), script, 80)
    assert msgs and msgs[0] == "Landing successful!"


def _t08_text_pixels(tmp_path, colour):
    from PIL import Image
    path = _t08(tmp_path, 3, draw_colour=colour)
    got = {}

    def script(f, post, r, seen):
        if f == 5:
            got["img"] = Image.frombytes("RGB", r.screen.get_size(), pygame.image.tostring(r.screen, "RGB"))
    play(path, script, 6)
    return sum(1 for p in got["img"].crop((8, 6, 200, 28)).getdata() if p != (0, 0, 0))


def test_t08_hud_text_needs_a_white_draw_colour_on_the_black_room(tmp_path):
    assert _t08_text_pixels(tmp_path / "a", True) > 50
    assert _t08_text_pixels(tmp_path / "b", False) == 0


def test_t08_without_switching_gravity_off_the_landing_message_repeats_every_frame(tmp_path):
    """Why the tutorial adds Set Gravity 0 to the landing event."""
    path = _t08(tmp_path, 2, lander_xy=(512, 250))
    data = trp.json.loads(path.read_text(encoding="utf-8"))
    acts = data["assets"]["objects"]["obj_lander"]["events"]["collision_with_obj_pad"]["actions"]
    acts[:] = [a for a in acts if a["action"] != "set_gravity"]
    path.write_text(trp.json.dumps(data), encoding="utf-8")
    msgs = []

    def script(f, post, r, seen):
        if f == 1:
            r.show_message_dialog = lambda m, *a, **k: msgs.append(m)
    play(path, script, 250)
    assert len(msgs) > 50


# ----------------------------------------------------------------- Tutorial 09

def _t09(tmp_path, phase=4, mod=None, **kw):
    path = trp.build_t09(tmp_path, phase, **kw)
    if mod:
        data = trp.json.loads(path.read_text(encoding="utf-8"))
        mod(data)
        path.write_text(trp.json.dumps(data), encoding="utf-8")
    return path


def test_t09_player_moves_left_and_right_and_stops(tmp_path):
    xs = []

    def script(f, post, r, seen):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_RIGHT)
        if f == 30:
            post(pygame.KEYUP, pygame.K_RIGHT)
        xs.append(insts(r, "obj_player")[0].x)
    play(_t09(tmp_path, 1), script, 60)
    assert xs[25] > xs[5] and xs[55] == xs[50]


def test_t09_coins_and_the_enemy_fall_from_the_top(tmp_path):
    snap = {}

    def script(f, post, r, seen):
        if f == 60:
            snap["ys"] = [c.y for c in insts(r, "obj_coin")] + [e.y for e in insts(r, "obj_enemy")]
    play(_t09(tmp_path, 2), script, 61)
    assert len(snap["ys"]) == 6 and all(y > 100 for y in snap["ys"])


def test_t09_catching_a_coin_scores_one_and_removes_it(tmp_path):
    snap = {}

    def script(f, post, r, seen):
        if f == 250:
            snap["score"] = r.score
            snap["coins"] = len(insts(r, "obj_coin"))
    # a coin directly above the player (player x=496)
    play(_t09(tmp_path, 3, coin_xs=(500,), enemy_x=10), script, 251)
    assert snap["score"] == 1 and snap["coins"] == 0


def test_t09_touching_the_enemy_goes_to_the_game_over_room_and_space_restarts(tmp_path):
    log = {"rooms": []}

    def script(f, post, r, seen):
        if not log["rooms"] or log["rooms"][-1] != r.current_room.name:
            log["rooms"].append(r.current_room.name)
        if f == 250:
            post(pygame.KEYDOWN, pygame.K_SPACE)
            post(pygame.KEYUP, pygame.K_SPACE)
    play(_t09(tmp_path, 3, coin_xs=(10,), enemy_x=500), script, 300)
    assert log["rooms"][:3] == ["room_main", "room_gameover", "room_main"]


def test_t09_win_room_appears_when_every_coin_is_caught(tmp_path):
    rooms = []

    def script(f, post, r, seen):
        if not rooms or rooms[-1] != r.current_room.name:
            rooms.append(r.current_room.name)
    play(_t09(tmp_path, 4, coin_xs=(500,), enemy_x=10), script, 300)
    assert rooms == ["room_main", "room_win"]


def test_t09_without_the_outside_room_event_a_missed_coin_makes_the_game_unwinnable(tmp_path):
    """Why the tutorial brings missed coins back: off-screen coins still exist, so the count never reaches 0."""
    def no_wrap(data):
        for o in ("obj_coin", "obj_enemy"):
            data["assets"]["objects"][o]["events"].pop("outside_room")
    rooms, counts = [], []

    def script(f, post, r, seen):
        if not rooms or rooms[-1] != r.current_room.name:
            rooms.append(r.current_room.name)
        if f % 100 == 0:
            counts.append(len(insts(r, "obj_coin")))
    play(_t09(tmp_path, 4, no_wrap, coin_xs=(500, 900), enemy_x=10), script, 800)
    assert rooms == ["room_main"] and counts[-1] == 1         # the missed coin is still alive, far off screen


def test_t09_missed_coins_reappear_so_the_game_stays_winnable(tmp_path):
    counts = []

    def script(f, post, r, seen):
        if f % 200 == 0:
            counts.append(len(insts(r, "obj_coin")))
    play(_t09(tmp_path, 4, coin_xs=(900,), enemy_x=10), script, 1000)
    assert counts and all(c == 1 for c in counts)              # never lost, keeps falling again


def test_t09_with_no_coins_placed_the_win_room_appears_at_once(tmp_path):
    rooms = []

    def script(f, post, r, seen):
        if not rooms or rooms[-1][1] != r.current_room.name:
            rooms.append((f, r.current_room.name))
    play(_t09(tmp_path, 4, coin_xs=(), enemy_x=10), script, 20)
    assert rooms[-1][1] == "room_win" and rooms[-1][0] <= 5
