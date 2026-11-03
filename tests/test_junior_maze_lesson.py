"""Truth tests for the Junior lesson "My First Maze" (tools/junior_maze_lesson.py).

The student handout and teacher guide (docs/junior/lessons/maze/) promise: only
Junior blocks are needed, a hero stops at walls, reaching the goal shows "You
win!" and restarts, and the HTML5 export is one file with on-screen arrows for
a phone. Each promise is pinned here by running the real engine / exporter.
"""
import importlib.util
import os
import sys
from collections import deque
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

REPO = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "junior_maze_lesson", REPO / "tools" / "junior_maze_lesson.py")
jm = importlib.util.module_from_spec(_spec)
sys.modules["junior_maze_lesson"] = jm
_spec.loader.exec_module(jm)


def play(project_path, script, frames):
    """Real game loop with a fake clock. script(frame, post, runner)."""
    from runtime.game_runner import GameRunner
    runner = GameRunner(str(project_path))
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    seen = {"frame": 0}

    def post(kind, key):
        pygame.event.post(pygame.event.Event(kind, key=key))

    class Clock:
        def tick(self, fps=0):
            seen["frame"] += 1
            script(seen["frame"], post, runner)
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
    return runner


def insts(runner, name):
    return [i for i in runner.current_room.instances if i.object_name == name]


def _route(level=jm.LEVEL):
    start, goal = jm._find(level, "P"), jm._find(level, "E")
    prev, todo = {start: None}, deque([start])
    while todo:
        cur = todo.popleft()
        if cur == goal:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (cur[0] + dx, cur[1] + dy)
            if level[n[1]][n[0]] != "W" and n not in prev:
                prev[n] = cur
                todo.append(n)
    assert goal in prev, "maze is not solvable"
    path, cur = [], goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    return path[::-1]


def _key_script(path):
    """(frame -> [(KEYDOWN/KEYUP, key)]) driving the hero along a cell path:
    32 px at 4 px/frame = 8 frames per cell."""
    keys = {(1, 0): pygame.K_RIGHT, (-1, 0): pygame.K_LEFT,
            (0, 1): pygame.K_DOWN, (0, -1): pygame.K_UP}
    runs = []
    for a, b in zip(path, path[1:]):
        k = keys[(b[0] - a[0], b[1] - a[1])]
        if runs and runs[-1][0] == k:
            runs[-1][1] += 1
        else:
            runs.append([k, 1])
    by_frame, t = {}, 3
    for k, n in runs:
        by_frame.setdefault(t, []).append((pygame.KEYDOWN, k))
        t += 8 * n
        by_frame.setdefault(t, []).append((pygame.KEYUP, k))
        t += 1
    return by_frame, t


# ------------------------------------------------------------------ the maze

def test_level_is_solvable_and_every_corridor_is_two_cells_wide():
    assert len(jm.LEVEL) == jm.ROWS and all(len(r) == jm.COLS for r in jm.LEVEL)
    _route()
    open_cells = {(c, r) for r, row in enumerate(jm.LEVEL)
                  for c, ch in enumerate(row) if ch != "W"}
    for (c, r) in open_cells:
        # every open cell is a corner of some fully open 2x2 square
        squares = [{(c0 + dc, r0 + dr) for dc in (0, 1) for dr in (0, 1)}
                   for c0 in (c - 1, c) for r0 in (r - 1, r)]
        assert any(sq <= open_cells for sq in squares), (c, r)


# ---------------------------------------------------- only Junior blocks used

def test_the_finished_project_uses_only_junior_toolbox_blocks(tmp_path):
    import json
    from config.blockly_config import PRESETS
    from events.action_types import ACTION_TO_BLOCKLY_MAP
    junior = PRESETS["junior"].enabled_blocks

    data = json.loads(jm.build_finished(tmp_path).read_text(encoding="utf-8"))
    blocks = set()
    for obj in data["assets"]["objects"].values():
        for event, body in obj["events"].items():
            blocks.add("event_collision" if event.startswith("collision_with")
                       else {"keyboard": "event_keyboard_held"}.get(event, event))
            subs = body.values() if event == "keyboard" else [body]
            for sub in subs:
                if event == "keyboard" and "nokey" in body:
                    blocks.add("event_keyboard_nokey")
                for a in sub.get("actions", []):
                    blocks.add(ACTION_TO_BLOCKLY_MAP.get(a["action"], a["action"]))
    assert {"move_set_hspeed", "move_set_vspeed", "move_stop", "output_message",
            "room_restart", "event_keyboard_held", "event_collision"} <= blocks
    assert blocks <= junior, blocks - junior


# ------------------------------------------------------------- the real game

def test_starter_has_a_solid_wall_object_and_a_bordered_empty_room(tmp_path):
    import json
    data = json.loads(jm.build_starter(tmp_path).read_text(encoding="utf-8"))
    assert data["assets"]["objects"]["obj_wall"]["solid"] is True
    room = data["assets"]["rooms"]["room0"]
    assert (room["width"], room["height"]) == (640, 416)
    assert {i["object_name"] for i in room["instances"]} == {"obj_wall"}
    assert len(room["instances"]) == 2 * jm.COLS + 2 * (jm.ROWS - 2)
    runner = play(tmp_path / "project.json", lambda f, p, r: None, 5)
    assert not insts(runner, "obj_hero")


def test_hero_stops_at_a_wall_and_when_the_key_is_released(tmp_path):
    path = jm.build_finished(tmp_path)
    xs = []

    def script(f, post, r):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_RIGHT)
        if f == 170:
            post(pygame.KEYUP, pygame.K_RIGHT)
        xs.append(insts(r, "obj_hero")[0].x)
    play(path, script, 180)
    assert xs[150] == 18 * 32          # flush against the right-hand wall
    assert xs[179] == 18 * 32

    xs.clear()
    play(path, lambda f, post, r: (post(pygame.KEYDOWN, pygame.K_RIGHT) if f == 3 else
                                   post(pygame.KEYUP, pygame.K_RIGHT) if f == 20 else None,
                                   xs.append(insts(r, "obj_hero")[0].x)), 40)
    assert xs[35] == xs[25] and xs[25] < 18 * 32      # let go -> stops by itself


def _steer(r, route, state, post):
    """A forgiving human: aim at the centre of the next cell on the route,
    holding one arrow at a time (so the hero is rarely on the grid)."""
    hero = insts(r, "obj_hero")
    if not hero or state["done"]:
        return
    h = hero[0]
    cx, cy = h.x + 16, h.y + 16
    while state["i"] < len(route) - 1:
        tx, ty = route[state["i"]][0] * 32 + 16, route[state["i"]][1] * 32 + 16
        if abs(cx - tx) <= 6 and abs(cy - ty) <= 6:
            state["i"] += 1
        else:
            break
    tx, ty = route[state["i"]][0] * 32 + 16, route[state["i"]][1] * 32 + 16
    dx, dy = tx - cx, ty - cy
    if abs(dx) >= abs(dy) and abs(dx) > 2:
        want = pygame.K_RIGHT if dx > 0 else pygame.K_LEFT
    elif abs(dy) > 2:
        want = pygame.K_DOWN if dy > 0 else pygame.K_UP
    else:
        want = None
    if want != state["key"]:
        if state["key"] is not None:
            post(pygame.KEYUP, state["key"])
        if want is not None:
            post(pygame.KEYDOWN, want)
        state["key"] = want


@pytest.mark.parametrize("offset", [(0, 0), (8, 8), (16, 12), (24, 24)])
def test_a_full_playthrough_wins_and_the_room_restarts(tmp_path, offset):
    """Also with the hero placed OFF the grid: two-cell corridors forgive it."""
    path = jm.build_finished(tmp_path, hero_offset=offset)
    route = _route()
    state = {"i": 0, "key": None, "done": False}
    log = {"msgs": [], "won_at": None}

    def script(f, post, r):
        if f == 1:
            r.show_message_dialog = lambda m, *a, **k: (
                log["msgs"].append(m), log.update(won_at=f), state.update(done=True))
        _steer(r, route, state, post)
    runner = play(path, script, 1200)
    assert log["msgs"] == ["You win!"], log
    h = insts(runner, "obj_hero")[0]
    assert (h.x, h.y) == (32 + offset[0], 32 + offset[1])      # restarted at the start


# ------------------------------------------------------------- the HTML5 file

def _game_data(html):
    import base64
    import gzip
    import json
    import re
    blob = re.search(r'decompressData\("([^"]+)"\)', html).group(1)
    return json.loads(gzip.decompress(base64.b64decode(blob)))


def test_html5_export_is_one_file_with_on_screen_arrows(tmp_path):
    from export.HTML5.html5_exporter import HTML5Exporter
    proj, out = tmp_path / "proj", tmp_path / "out"
    proj.mkdir()
    out.mkdir()
    jm.build_finished(proj)
    assert HTML5Exporter().export(proj, out)
    files = list(out.iterdir())
    assert [p.suffix for p in files] == [".html"], files
    html = files[0].read_text(encoding="utf-8")
    assert 'id="touchControls"' in html
    for key in ("up", "down", "left", "right"):
        assert f'data-key="{key}"' in html
    assert 'name="viewport"' in html
    data = _game_data(html)
    objects = data["assets"]["objects"]
    assert {"obj_hero", "obj_goal", "obj_wall"} <= set(objects)
    msgs = [a["parameters"]["message"]
            for a in objects["obj_goal"]["events"]["collision_with_obj_hero"]["actions"]
            if a["action"] == "show_message"]
    assert msgs == ["You win!"]
    assert len(data["assets"]["sprites"]) == 3


# ------------------------------------------------------- the lesson documents

LESSON = REPO / "docs" / "junior" / "lessons" / "maze"


def _doc(name):
    return (LESSON / name).read_text(encoding="utf-8")


def test_en_and_fr_sheets_have_the_same_shape():
    import re
    for kind in ("student", "teacher"):
        en, fr = _doc(f"{kind}.en.md"), _doc(f"{kind}.fr.md")
        for pattern in (r"^- \[ \]", r"^> (TIP|INFO|DONE)", r"^\|", r"^## ", r"^\d+\. "):
            assert len(re.findall(pattern, en, re.M)) == len(re.findall(pattern, fr, re.M)), (kind, pattern)


def test_french_sheets_keep_their_accents():
    for kind in ("student", "teacher"):
        fr = _doc(f"{kind}.fr.md")
        for word in ("é", "è", "à", "ê"):
            assert word in fr, (kind, word)
        for wrong in ("Equipe", "Etape", " ete ", "ecran", "deja"):
            assert wrong not in fr, (kind, wrong)


def test_block_labels_in_the_student_sheets_are_the_real_ones():
    """Every bold block label the sheets name must exist in the Blockly source."""
    blockly = REPO / "editors" / "object_editor" / "blockly"
    en_src = (blockly / "blockly_workspace.html").read_text(encoding="utf-8") + \
        (blockly / "blockly_blocks.js").read_text(encoding="utf-8")
    i18n = (blockly / "blockly_i18n.js").read_text(encoding="utf-8")
    for label in ("Set horizontal speed to", "Set vertical speed to", "Stop movement",
                  "Keyboard: No key", "When colliding with", "Show message",
                  "Restart room", "Right Arrow", "Left Arrow", "Up Arrow", "Down Arrow"):
        assert label in en_src or label in i18n, label
        assert label in _doc("student.en.md"), label
    for label in ("définir vitesse horizontale à", "définir vitesse verticale à",
                  "arrêter le mouvement", "Clavier: Aucune touche", "Quand collision avec",
                  "Afficher message", "Redémarrer le niveau", "Flèche droite",
                  "Flèche gauche", "Flèche haut", "Flèche bas"):
        assert label in i18n, label
        assert label in _doc("student.fr.md"), label


def test_names_in_the_sheets_match_the_project(tmp_path):
    import json
    data = json.loads(jm.build_finished(tmp_path).read_text(encoding="utf-8"))
    names = set(data["assets"]["sprites"]) | set(data["assets"]["objects"]) | set(data["assets"]["rooms"])
    for kind in ("en", "fr"):
        text = _doc(f"student.{kind}.md")
        for name in ("spr_hero", "spr_goal", "obj_hero", "obj_goal", "obj_wall", "room0"):
            assert name in names and name in text, (kind, name)
    assert data["name"] == "My Maze"


def test_zips_unpack_to_the_folder_the_sheets_name(tmp_path):
    import zipfile
    jm.write_zips(tmp_path)
    for zname, folder in (("Junior-Maze-Starter.zip", "My Maze"),
                          ("Junior-Maze-Finished.zip", "My Maze (finished)")):
        with zipfile.ZipFile(tmp_path / zname) as z:
            names = z.namelist()
        assert f"{folder}/project.json" in names, names
    # rebuilding does not change the bytes (fixed timestamps)
    first = (tmp_path / "Junior-Maze-Starter.zip").read_bytes()
    jm.write_zips(tmp_path)
    assert (tmp_path / "Junior-Maze-Starter.zip").read_bytes() == first
