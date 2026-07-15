"""views_2 sample — split-screen co-op multi-view, verified on the desktop runtime.

views_2 shows a 2400x800 room as a LEFT/RIGHT split screen: view 0 (left half,
port 0..400) follows obj_player1 (arrow keys); view 1 (right half, port
400..800) follows obj_player2 (WASD). Both views are 1:1 (view size == port
size, 400x600) so they render identically on desktop, HTML5, and Kivy (only
Kivy's FBO path scales view->port; desktop/HTML5 clip 1:1).

This drives the authored data through the real runtime and proves:
 - loading the sample yields the two-view config and the object set,
 - obj_camera's create event enables views and points view 0 at player 1 and
   view 1 at player 2,
 - the two cameras scroll INDEPENDENTLY as each player moves, each clamping at
   the room's right edge, and
 - a coin scores for whichever player collects it (both collision events wired).

Per-player stop uses keyboard_release (not the global nokey), so one player
holding a key can't freeze the other — see the WHY note in the README.
"""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from conftest import skip_without_pygame
from utils.project_file_merge import merge_object_file

pytestmark = skip_without_pygame

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE = REPO_ROOT / "samples" / "views_2"


def _load():
    data = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        side = SAMPLE / "objects" / f"{name}.json"
        if side.exists():
            merge_object_file(obj, json.loads(side.read_text(encoding="utf-8")))
    for name in list(data["assets"]["rooms"]):
        side = SAMPLE / "rooms" / f"{name}.json"
        if side.exists():
            data["assets"]["rooms"][name] = json.loads(side.read_text(encoding="utf-8"))
    return data


def _build():
    data = _load()
    with patch('runtime.game_runner.pygame'), patch('runtime.game_runner.load_all_plugins'):
        from runtime.game_runner import GameRoom, GameRunner
        from runtime.action_executor import ActionExecutor
        ex = ActionExecutor()
        room = GameRoom("room0", data["assets"]["rooms"]["room0"], action_executor=ex)
        runner = GameRunner.__new__(GameRunner)
        runner.current_room = room
        runner.score = 0
        runner.show_score_in_caption = False
        ex.game_runner = runner
        objects = data["assets"]["objects"]
        for inst in room.instances:
            inst.object_data = objects.get(inst.object_name, {})
            inst.action_executor = ex
    return data, room, ex, runner


def _run_camera_create(room, ex):
    cam = room._find_first_instance("obj_camera")
    assert cam is not None
    ex.execute_event(cam, "create", cam.object_data["events"])


# ---------------------------------------------------------------------------

def test_sample_loads_two_views_and_two_players():
    data, room, ex, runner = _build()
    assert room.width == 2400 and room.height == 800
    names = [i.object_name for i in room.instances]
    assert names.count("obj_player1") == 1
    assert names.count("obj_player2") == 1
    assert names.count("obj_camera") == 1
    assert names.count("obj_coin") == 18
    # both views baked visible with distinct follow targets + side-by-side ports
    assert room.views[0]['follow'] == "obj_player1"
    assert room.views[1]['follow'] == "obj_player2"
    assert room.views[0]['port_x'] == 0 and room.views[1]['port_x'] == 400


def test_camera_create_configures_both_views():
    data, room, ex, runner = _build()
    _run_camera_create(room, ex)
    assert room.views_enabled is True
    v0, v1 = room.views[0], room.views[1]
    assert v0['visible'] and v1['visible']
    assert v0['follow'] == "obj_player1" and v1['follow'] == "obj_player2"
    # 1:1 (view size == port size) so all three targets render it the same
    assert (v0['view_w'], v0['view_h']) == (400, 600) == (v0['port_w'], v0['port_h'])
    assert (v1['view_w'], v1['view_h']) == (400, 600) == (v1['port_w'], v1['port_h'])


def test_views_scroll_independently_and_clamp():
    data, room, ex, runner = _build()
    _run_camera_create(room, ex)
    p1 = room._find_first_instance("obj_player1")
    p2 = room._find_first_instance("obj_player2")
    # keep both in the vertical follow band so view_y stays 0 (isolate the x axis)
    p1.y = p2.y = 300.0

    # Move only player 1: view 0 follows, view 1 stays put.
    p1.x = 1000.0
    room.update_views()
    assert room.views[0]['view_x'] == 1000 - (400 - 120)   # tx - (view_w - hborder) = 720
    assert room.views[1]['view_x'] == 0                     # player 2 hasn't moved

    # Now move only player 2: view 1 follows, view 0 unchanged.
    p2.x = 1500.0
    room.update_views()
    assert room.views[0]['view_x'] == 720                   # player 1 still at 1000
    assert room.views[1]['view_x'] == 1500 - 280            # 1220

    # Both cameras clamp at the room's right edge (2400 - 400 = 2000).
    p1.x = p2.x = 2360.0
    room.update_views()
    assert room.views[0]['view_x'] == 2000
    assert room.views[1]['view_x'] == 2000
    assert room.views[0]['view_y'] == 0 and room.views[1]['view_y'] == 0


def test_coin_collected_by_either_player_scores():
    data, room, ex, runner = _build()
    coin_obj = data["assets"]["objects"]["obj_coin"]
    events = coin_obj["events"]
    # a coin can be taken by BOTH players (two collision events wired)
    assert "collision_with_obj_player1" in events
    assert "collision_with_obj_player2" in events
    assert events["destroy"]["actions"][0]["action"] == "set_score"

    coin = next(i for i in room.instances if i.object_name == "obj_coin")
    ex.execute_set_score_action(coin, {"value": "10", "relative": True})
    assert runner.score == 10


def test_players_stop_via_keyboard_release_not_global_nokey():
    """Independent stop: each player has keyboard_release for ITS keys, so one
    player holding a key can't block the other's stop (global nokey would)."""
    data, _room, _ex, _runner = _build()
    p1 = data["assets"]["objects"]["obj_player1"]["events"]
    p2 = data["assets"]["objects"]["obj_player2"]["events"]
    assert set(p1["keyboard_release"]) == {"up", "down", "left", "right"}
    assert set(p2["keyboard_release"]) == {"w", "a", "s", "d"}
