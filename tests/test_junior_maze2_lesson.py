"""Truth tests for the Junior lesson "Treasure Maze" (tools/junior_maze2_lesson.py).

The student handout and teacher guide (docs/junior/lessons/maze2/) promise: only
Junior blocks are needed; a closed door stops the hero; the key opens every door;
gems score, a heart adds a life, a bomb costs a life and sends the hero home; the
goal only wins once every gem is collected; no lives left ends the game; and the
HTML5 export is one file with on-screen arrows. Each promise is pinned here by
running the real engine / exporter.
"""
import importlib.util
import json
import os
import sys
from collections import deque
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
_spec = importlib.util.spec_from_file_location(
    "junior_maze2_lesson", REPO / "tools" / "junior_maze2_lesson.py")
jm = importlib.util.module_from_spec(_spec)
sys.modules["junior_maze2_lesson"] = jm
_spec.loader.exec_module(jm)

from test_junior_maze_lesson import play, insts  # noqa: E402  (same real-loop harness)

CELL = jm.CELL
SOLID = "WD"


def cell_xy(c, r):
    return c * CELL, r * CELL


def where(ch):
    return [(c, r) for r, row in enumerate(jm.LEVEL) for c, x in enumerate(row) if x == ch]


# ------------------------------------------------------------------ the maze

def test_level_has_the_promised_pieces():
    assert len(jm.LEVEL) == jm.ROWS and all(len(r) == jm.COLS for r in jm.LEVEL)
    assert {ch: len(where(ch)) for ch in "PEKHGBD"} == \
        {"P": 1, "E": 1, "K": 1, "H": 1, "G": 4, "B": 4, "D": 6}


def test_every_corridor_is_two_cells_wide():
    open_cells = {(c, r) for r, row in enumerate(jm.LEVEL)
                  for c, ch in enumerate(row) if ch not in SOLID}
    for (c, r) in open_cells:
        squares = [{(c0 + dc, r0 + dr) for dc in (0, 1) for dr in (0, 1)}
                   for c0 in (c - 1, c) for r0 in (r - 1, r)]
        assert any(sq <= open_cells for sq in squares), (c, r)


def _bfs(start, goal, blocked):
    prev, todo = {start: None}, deque([start])
    while todo:
        cur = todo.popleft()
        if cur == goal:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (cur[0] + dx, cur[1] + dy)
            if n not in blocked and n not in prev and jm.LEVEL[n[1]][n[0]] != "W":
                prev[n] = cur
                todo.append(n)
    assert goal in prev, f"no way from {start} to {goal}"
    path, cur = [], goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    return path[::-1]


def _tour():
    """Cell path: first gem, key, the door, the other gems, goal -- keeping one
    cell away from every bomb, with the door closed until the key is taken."""
    bombs = set(where("B"))
    danger = {(c + dc, r + dr) for c, r in bombs for dc in (-1, 0, 1) for dr in (-1, 0, 1)}
    doors = set(where("D"))
    stops = [(15, 3), where("K")[0], (8, 9), (8, 16), (20, 16), where("E")[0]]
    path, here, door_open = [], where("P")[0], False
    for stop in stops:
        blocked = danger - {stop} | (set() if door_open else doors)
        leg = _bfs(here, stop, blocked)
        path += leg if not path else leg[1:]
        here = stop
        if stop == where("K")[0]:
            door_open = True
    return path


def test_the_maze_can_be_finished_avoiding_every_bomb_and_the_door_needs_the_key():
    path = _tour()
    assert path[0] == where("P")[0] and path[-1] == where("E")[0]
    assert not (set(path) & set(where("B")))
    # before the key the middle band is split by the door: the left half is unreachable
    with pytest.raises(AssertionError):
        _bfs(where("P")[0], (8, 9), set(where("D")))


# ---------------------------------------------------- only Junior blocks used

def _collect(actions, blocks, block_for):
    """Add the block for each action, looking inside If blocks' then/else slots."""
    for a in actions:
        blocks.add(block_for(a))
        params = a.get("parameters", {})
        for slot in ("then_actions", "else_actions"):
            _collect(params.get(slot, []), blocks, block_for)


def test_the_finished_project_uses_only_junior_toolbox_blocks(tmp_path):
    from config.blockly_config import PRESETS
    from events.action_types import ACTION_TO_BLOCKLY_MAP
    junior = PRESETS["junior"].enabled_blocks
    data = json.loads(jm.build_finished(tmp_path).read_text(encoding="utf-8"))

    def block_for(a):
        name, p = a["action"], a.get("parameters", {})
        if name in ("set_score", "set_lives") and p.get("relative") is True:
            return "score_add" if name == "set_score" else "lives_add"
        if name == "destroy_instance":
            return {"self": "instance_destroy", "other": "instance_destroy_other",
                    "object": "instance_destroy_object"}[p.get("target", "self")]
        return ACTION_TO_BLOCKLY_MAP.get(name, name)

    blocks = set()
    for obj in data["assets"]["objects"].values():
        for event, body in obj["events"].items():
            if event == "keyboard":
                blocks.add("event_keyboard_held")
                subs = [b.get("actions", []) for b in body.values()]
                if "nokey" in body:
                    blocks.add("event_keyboard_nokey")
            elif event == "no_more_lives":
                blocks.add("event_other")
                subs = [body.get("actions", [])]
            else:
                blocks.add("event_collision" if event.startswith("collision_with") else event)
                subs = [body.get("actions", [])]
            for actions in subs:
                _collect(actions, blocks, block_for)
    assert {"lives_add", "score_add", "instance_destroy_object", "instance_destroy_other",
            "if_condition", "jump_to_start", "restart_game", "event_other"} <= blocks
    # the nested If block replaces the flat Test Instance Count + Start/End Block + Else
    assert not ({"test_instance_count", "start_block", "end_block", "else_action"} & blocks)
    assert blocks <= junior, blocks - junior


def test_the_goal_uses_the_nested_if_block_with_the_fields_blockly_writes(tmp_path):
    """Parameter names/values must be exactly what blockly_generators.js emits for
    the If block's "count of object" type, or the Blockly editor would not show it."""
    data = json.loads(jm.build_finished(tmp_path).read_text(encoding="utf-8"))
    actions = data["assets"]["objects"]["obj_goal"]["events"]["collision_with_obj_hero"]["actions"]
    assert [a["action"] for a in actions] == ["if_condition"]
    prm = actions[0]["parameters"]
    assert (prm["condition_type"], prm["object_name"], prm["operator"], str(prm["value"])) == \
        ("instance_count", "obj_gem", "==", "0")
    assert [a["action"] for a in prm["then_actions"]] == ["show_message", "restart_game"]
    assert [a["action"] for a in prm["else_actions"]] == ["show_message"]
    gen = (REPO / "editors" / "object_editor" / "blockly" / "blockly_generators.js").read_text(encoding="utf-8")
    for field in ("object_name", "then_actions", "else_actions", "condition_type"):
        assert field in gen[gen.index("case 'if_condition':"):][:3500], field


# --------------------------------------------------------------- the starter

def test_starter_has_all_sprites_a_not_yet_solid_wall_and_a_bordered_room(tmp_path):
    data = json.loads(jm.build_starter(tmp_path).read_text(encoding="utf-8"))
    assert set(data["assets"]["sprites"]) == set(jm.ART)
    assert set(data["assets"]["objects"]) == {"obj_wall"}
    assert data["assets"]["objects"]["obj_wall"]["solid"] is False
    room = data["assets"]["rooms"]["room0"]
    assert (room["width"], room["height"]) == (960, 640)
    assert {i["object_name"] for i in room["instances"]} == {"obj_wall"}
    assert len(room["instances"]) == 2 * jm.COLS + 2 * (jm.ROWS - 2)
    for name in jm.ART:                                   # every sprite file really exists
        assert (tmp_path / "sprites" / f"{name}.png").exists()
    runner = play(tmp_path / "project.json", lambda f, p, r: None, 5)
    assert len(insts(runner, "obj_wall")) == len(room["instances"])


# ------------------------------------------------------------ the real game

def _teleport(script_steps, tmp_path, frames=40, **kw):
    """Run the finished game; script_steps(f, post, r, log) may move instances."""
    path = jm.build_finished(tmp_path, **kw)
    log = {"msgs": []}

    def script(f, post, r):
        if f == 1:
            r.show_message_dialog = lambda m, *a, **k: log["msgs"].append(m)
        script_steps(f, post, r, log)
    log["runner"] = play(path, script, frames)
    return log


def _hero(r):
    return insts(r, "obj_hero")[0]


def _put_on(r, ch, index=0):
    """Move the hero onto the index-th instance of an item type."""
    name = jm.OBJECT_FOR[ch]
    target = sorted(insts(r, name), key=lambda i: (i.x, i.y))[index]
    _hero(r).x, _hero(r).y = target.x, target.y
    return target


def test_hero_stops_at_a_wall_and_a_closed_door(tmp_path):
    xs = []

    def steps(f, post, r, log):
        if f == 2:
            _hero(r).x, _hero(r).y = 13 * CELL, 9 * CELL       # left of the door, row 9
            post(pygame.KEYDOWN, pygame.K_RIGHT)
        xs.append(_hero(r).x)
    _teleport(steps, tmp_path, frames=60)
    assert xs[50] == 14 * CELL                     # flush against the door at column 15


def test_gem_adds_ten_points_and_disappears(tmp_path):
    seen = {}

    def steps(f, post, r, log):
        if f == 3:
            seen["gems_before"] = len(insts(r, "obj_gem"))
            _put_on(r, "G")
        if f == 8:
            seen["score"], seen["gems_after"] = r.score, len(insts(r, "obj_gem"))
    _teleport(steps, tmp_path, frames=12)
    assert (seen["gems_before"], seen["gems_after"], seen["score"]) == (4, 3, 10)


def test_key_opens_every_door_and_is_used_up(tmp_path):
    seen = {}

    def steps(f, post, r, log):
        if f == 3:
            seen["before"] = (len(insts(r, "obj_door")), len(insts(r, "obj_key")))
            _put_on(r, "K")
        if f == 8:
            seen["after"] = (len(insts(r, "obj_door")), len(insts(r, "obj_key")))
    _teleport(steps, tmp_path, frames=12)
    assert seen["before"] == (6, 1) and seen["after"] == (0, 0)


def test_heart_adds_a_life(tmp_path):
    seen = {}

    def steps(f, post, r, log):
        if f == 3:
            seen["lives_before"] = r.lives
            _put_on(r, "H")
        if f == 8:
            seen["lives_after"], seen["hearts"] = r.lives, len(insts(r, "obj_heart"))
    _teleport(steps, tmp_path, frames=12)
    assert seen["lives_after"] == seen["lives_before"] + 1 and seen["hearts"] == 0


@pytest.mark.parametrize("offset", [(0, 0), (16, 16)])
def test_bomb_costs_a_life_goes_off_and_sends_the_hero_home(tmp_path, offset):
    seen = {}

    def steps(f, post, r, log):
        if f == 3:
            seen["lives_before"] = r.lives
            _put_on(r, "B")
        if f == 8:
            h = _hero(r)
            seen["after"] = (r.lives, len(insts(r, "obj_bomb")), (h.x, h.y))
    _teleport(steps, tmp_path, frames=12, hero_offset=offset)
    start = (32 + offset[0], 32 + offset[1])
    assert seen["after"] == (seen["lives_before"] - 1, 3, start)


def test_three_bombs_end_the_game_and_restart_it(tmp_path):
    seen = {}

    def steps(f, post, r, log):
        if f in (3, 8, 13):
            _put_on(r, "B", 0)
        if f == 30:
            seen["after"] = (r.lives, r.score, len(insts(r, "obj_bomb")), len(insts(r, "obj_gem")))
    log = _teleport(steps, tmp_path, frames=34)
    assert log["msgs"] == ["Game over!"]
    assert seen["after"] == (3, 0, 4, 4)           # the whole game started again


def test_goal_needs_every_gem_then_wins_and_restarts(tmp_path):
    seen = {}

    def steps(f, post, r, log):
        if f == 3:
            _put_on(r, "E")                         # too early
        if f == 9:
            seen["early"] = (list(log["msgs"]), len(insts(r, "obj_gem")))
            h = _hero(r)
            h.x, h.y = 2 * CELL, 2 * CELL            # step away so the next touch is a new collision
            for g in list(insts(r, "obj_gem")):
                r.current_room.instances.remove(g)    # the player collected them all
        if f == 14:
            _put_on(r, "E")
        if f == 24:
            seen["late"] = (len(insts(r, "obj_gem")), r.score)
    log = _teleport(steps, tmp_path, frames=28)
    assert seen["early"] == (["Collect every gem first!"], 4)
    assert log["msgs"] == ["Collect every gem first!", "You win!"]
    assert seen["late"][0] == 4                      # restarted: the gems are back


def _steer(r, route, state, post):
    hero = insts(r, "obj_hero")
    if not hero or state["done"]:
        return
    h = hero[0]
    cx, cy = h.x + 16, h.y + 16
    while state["i"] < len(route) - 1:
        tx, ty = route[state["i"]][0] * CELL + 16, route[state["i"]][1] * CELL + 16
        if abs(cx - tx) <= 6 and abs(cy - ty) <= 6:
            state["i"] += 1
        else:
            break
    tx, ty = route[state["i"]][0] * CELL + 16, route[state["i"]][1] * CELL + 16
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


@pytest.mark.parametrize("offset", [(0, 0), (8, 8), (16, 12)])
def test_a_whole_game_can_be_played_and_won(tmp_path, offset):
    """Steering like a person (arrow keys only), also with the hero off the grid."""
    path = jm.build_finished(tmp_path, hero_offset=offset)
    route = _tour()
    state = {"i": 0, "key": None, "done": False}
    log = {"msgs": [], "score": None, "lives": None}

    def script(f, post, r):
        if f == 1:
            def message(m, *a, **k):
                log["msgs"].append(m)
                if m == "You win!":
                    log["score"], log["lives"] = r.score, r.lives
                    state["done"] = True
            r.show_message_dialog = message
        _steer(r, route, state, post)
    play(path, script, 6000)
    assert log["msgs"] == ["You win!"], log
    assert (log["score"], log["lives"]) == (4 * jm.GEM_POINTS, 3)


# ------------------------------------------------------------- the HTML5 file

def _game_data(html):
    import base64
    import gzip
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
    assert 'id="touchControls"' in html and 'name="viewport"' in html
    for key in ("up", "down", "left", "right"):
        assert f'data-key="{key}"' in html
    data = _game_data(html)
    objects = data["assets"]["objects"]
    assert {"obj_hero", "obj_wall", "obj_door", "obj_gem", "obj_key", "obj_heart",
            "obj_bomb", "obj_goal"} <= set(objects)
    assert len(data["assets"]["sprites"]) == 8
    key_actions = objects["obj_key"]["events"]["collision_with_obj_hero"]["actions"]
    assert key_actions[0]["parameters"]["target_object"] == "obj_door"
    assert "no_more_lives" in objects["obj_hero"]["events"]


def test_the_html5_engine_knows_every_action_the_game_uses():
    """engine.js must implement each action (a missing one is silently ignored in
    the browser). No JS engine in CI, so this pins the source."""
    engine = (REPO / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
    for case in ("'destroy_instance'", "'jump_to_start'", "'test_instance_count'",
                 "'show_message'", "'restart_game'", "'set_lives'", "'set_score'",
                 "'stop_movement'"):
        assert f"case {case}" in engine, case
    # the block scoping actions are handled by the generic conditional machinery
    for word in ("start_block", "end_block", "else_action", "no_more_lives",
                 "target_object"):
        assert word in engine, word


def test_html5_destroy_instance_can_destroy_every_instance_of_an_object():
    """The key opens every door: "Destroy all instances of obj_door" must not
    fall through to destroying the caller (it did, in the browser, until fixed;
    verified once in headless Chromium: doors 3 -> 0 after the key)."""
    engine = (REPO / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
    start = engine.index("case 'destroy_instance':")
    block = engine[start:start + 1500]
    assert "target === 'object' && params.target_object" in block
    assert "inst.name === params.target_object" in block and "toDestroy = true" in block


# ------------------------------------------------------- the lesson documents

LESSON = REPO / "docs" / "junior" / "lessons" / "maze2"


def _doc(name):
    return (LESSON / name).read_text(encoding="utf-8")


def test_en_and_fr_sheets_have_the_same_shape():
    import re
    for kind in ("student", "teacher"):
        en, fr = _doc(f"{kind}.en.md"), _doc(f"{kind}.fr.md")
        for pattern in (r"^- \[ \]", r"^> (TIP|INFO|DONE)", r"^\|", r"^#{2,3} ", r"^\d+\. "):
            assert len(re.findall(pattern, en, re.M)) == len(re.findall(pattern, fr, re.M)), (kind, pattern)


def test_french_sheets_keep_their_accents():
    for kind in ("student", "teacher"):
        fr = _doc(f"{kind}.fr.md")
        for word in ("é", "è", "à", "ê", "ç"):
            assert word in fr, (kind, word)
        for wrong in ("Equipe", "Etape", " ete ", "ecran", "deja", "tresor", "cle "):
            assert wrong not in fr, (kind, wrong)


def test_block_labels_in_the_student_sheets_are_the_real_ones():
    """Every block label the sheets name exists in the Blockly source or in the
    generated-block tables, in English and in French."""
    from config import blockly_generated_block_i18n as gen
    from events.action_types import ACTION_TYPES
    blockly = REPO / "editors" / "object_editor" / "blockly"
    en_src = (blockly / "blockly_workspace.html").read_text(encoding="utf-8") + \
        (blockly / "blockly_blocks.js").read_text(encoding="utf-8")
    i18n = (blockly / "blockly_i18n.js").read_text(encoding="utf-8")
    en_student, fr_student = _doc("student.en.md"), _doc("student.fr.md")

    for label in ("Set horizontal speed to", "Set vertical speed to", "Stop movement",
                  "Keyboard: No key", "When colliding with", "Add to score",
                  "Destroy this instance", "Destroy other instance",
                  "Destroy all instances of", "Add to lives", "Show message",
                  "Other event:", "No More Lives", "Right Arrow", "Left Arrow",
                  "Up Arrow", "Down Arrow"):
        assert label in en_src or label in i18n, label
        assert label in en_student, label
    # The nested If block (hand-written, English labels in every language).
    blocks_js = (blockly / "blockly_blocks.js").read_text(encoding="utf-8")
    if_block = blocks_js[blocks_js.index("Blockly.Blocks['if_condition']"):][:2500]
    for word in ('"If"', '"count of"', '"then"', '"else"', '"obj_coin"'):
        assert word in if_block, word
    for student in (en_student, fr_student):
        for word in ("**If**", "**then**", "**else**", "`obj_gem`", "`obj_coin`", "`==`"):
            assert word in student, word
        for gone in ("Test Instance Count", "Start Block", "End Block", "Début de Bloc"):
            assert gone not in student, gone
    for action in ("jump_to_start", "restart_game"):                  # generated blocks
        name = ACTION_TYPES[action].display_name
        assert name in en_student, (action, name)
        fr_name = gen.get_translated_action_display_name(action, "fr", name)
        assert fr_name != name and fr_name in fr_student, (action, fr_name)

    for label in ("définir vitesse horizontale à", "définir vitesse verticale à",
                  "arrêter le mouvement", "Clavier: Aucune touche", "Quand collision avec",
                  "Ajouter au score", "Détruire cette instance", "Détruire autre instance",
                  "Détruire toutes les instances de", "Ajouter aux vies", "Afficher message",
                  "Autre événement :", "Plus de vies", "Flèche droite", "Flèche gauche",
                  "Flèche haut", "Flèche bas"):
        assert label in i18n, label
        assert label in fr_student, label


def test_names_in_the_sheets_match_the_project(tmp_path):
    data = json.loads(jm.build_finished(tmp_path).read_text(encoding="utf-8"))
    names = set(data["assets"]["sprites"]) | set(data["assets"]["objects"]) | set(data["assets"]["rooms"])
    for lang in ("en", "fr"):
        text = _doc(f"student.{lang}.md")
        for name in ("spr_hero", "spr_wall", "spr_door", "spr_gem", "spr_key", "spr_heart",
                     "spr_bomb", "spr_goal", "obj_hero", "obj_wall", "obj_door", "obj_gem",
                     "obj_key", "obj_heart", "obj_bomb", "obj_goal", "room0"):
            assert name in names and name in text, (lang, name)
    assert data["name"] == "Treasure Maze"


def test_the_object_table_matches_the_finished_projects_solid_flags(tmp_path):
    import re
    data = json.loads(jm.build_finished(tmp_path).read_text(encoding="utf-8"))
    for lang, yes in (("en", "**Yes**"), ("fr", "**Oui**")):
        text = _doc(f"student.{lang}.md")
        for name, obj in data["assets"]["objects"].items():
            row = re.search(rf"^\| {name}[^|]*\| (spr_\w+) \| ([^|]+) \|", text, re.M)
            assert row, (lang, name)
            assert row.group(1) == obj["sprite"], (lang, name)
            assert (row.group(2).strip() == yes) == bool(obj["solid"]), (lang, name)


def test_zips_unpack_to_the_folder_the_sheets_name(tmp_path):
    import zipfile
    jm.write_zips(tmp_path)
    for zname, folder in (("Junior-Treasure-Starter.zip", "Treasure Maze"),
                          ("Junior-Treasure-Finished.zip", "Treasure Maze (finished)")):
        with zipfile.ZipFile(tmp_path / zname) as z:
            names = z.namelist()
        assert f"{folder}/project.json" in names, names
    assert sum(n.endswith(".png") for n in zipfile.ZipFile(tmp_path / "Junior-Treasure-Starter.zip").namelist()) == 7
    first = (tmp_path / "Junior-Treasure-Starter.zip").read_bytes()
    jm.write_zips(tmp_path)
    assert (tmp_path / "Junior-Treasure-Starter.zip").read_bytes() == first    # rebuild is byte-identical
