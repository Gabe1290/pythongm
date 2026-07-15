"""views_1 sample — the camera-scrolling demo, verified on the desktop runtime.

views_1 is a 2400x800 room behind an 800x600 window; the camera (view 0) is
enabled and told to follow obj_player from the player's *create* event, using
the registered enable_views / set_view actions (not raw execute_code). This
drives that authored data through the real runtime and proves:

 - loading the sample (project.json + external object/room files) yields a room
   with the perimeter walls, 18 coins, and the baked views config,
 - the player's create event actually enables views and configures view 0 to
   follow the player with the authored borders,
 - as the player walks right across the wide room, GameRoom.update_views scrolls
   the camera and clamps it at the room's right edge (never past it), while the
   vertical stays put, and
 - a collected coin's set_score(relative) increments the run score.

The export side (HTML5 + Kivy carry the same camera) is covered by
test_html5_views / test_kivy_views / test_views_export_parity; this file is the
desktop-runtime proof for the sample content itself.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pygame
from utils.project_file_merge import merge_object_file

pytestmark = skip_without_pygame

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE = REPO_ROOT / "samples" / "views_1"


def _load_views1():
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
    """Real GameRoom + real ActionExecutor wired to a minimal GameRunner."""
    data = _load_views1()
    with patch('runtime.game_runner.pygame'), patch('runtime.game_runner.load_all_plugins'):
        from runtime.game_runner import GameRoom, GameRunner
        from runtime.action_executor import ActionExecutor
        room_data = data["assets"]["rooms"]["room0"]
        ex = ActionExecutor()
        room = GameRoom("room0", room_data, action_executor=ex)
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


# ---------------------------------------------------------------------------
# Sample content
# ---------------------------------------------------------------------------

def test_sample_loads_with_room_and_coins():
    data, room, ex, runner = _build()
    assert room.width == 2400 and room.height == 800
    names = [i.object_name for i in room.instances]
    assert names.count("obj_coin") == 18
    assert names.count("obj_player") == 1
    assert names.count("obj_wall") >= 196          # perimeter + pillars
    # baked views config survived the load
    assert room.views_enabled is True
    assert room.views[0]['follow'] == "obj_player"


def test_player_create_event_configures_camera():
    data, room, ex, runner = _build()
    player = room._find_first_instance("obj_player")
    assert player is not None

    # Run the authored create event through the real dispatch.
    ex.execute_event(player, "create", player.object_data["events"])

    assert room.views_enabled is True
    v = room.views[0]
    assert v['visible'] is True
    assert v['follow'] == "obj_player"
    assert v['view_w'] == 800 and v['view_h'] == 600
    assert v['hborder'] == 240 and v['vborder'] == 180


# ---------------------------------------------------------------------------
# Camera scroll (the whole point of the sample)
# ---------------------------------------------------------------------------

def test_camera_scrolls_right_and_clamps():
    data, room, ex, runner = _build()
    player = room._find_first_instance("obj_player")
    ex.execute_event(player, "create", player.object_data["events"])

    start_y = player.y
    seen = []
    x = player.x
    while x < room.width - 32:
        x = min(x + 60, room.width - 32)
        player.x = x
        room.update_views()
        seen.append(room.views[0]['view_x'])

    # Monotonic non-decreasing as the player walks right.
    assert seen == sorted(seen)
    # Started at the left edge, ended clamped at the room's right edge.
    assert seen[0] == 0
    assert max(seen) == room.width - room.views[0]['view_w']   # 2400-800 = 1600
    assert room.views[0]['view_x'] == 1600
    # Player never left its row, so the vertical view never scrolled.
    assert player.y == start_y
    assert room.views[0]['view_y'] == 0


def test_camera_returns_left_when_player_backtracks():
    data, room, ex, runner = _build()
    player = room._find_first_instance("obj_player")
    ex.execute_event(player, "create", player.object_data["events"])

    player.x = room.width - 32           # far right
    room.update_views()
    assert room.views[0]['view_x'] == 1600

    player.x = 32                        # back to far left
    for _ in range(4):                   # unlimited scroll speed -> one step is enough
        room.update_views()
    assert room.views[0]['view_x'] == 0


# ---------------------------------------------------------------------------
# Coin scoring
# ---------------------------------------------------------------------------

def test_coin_wires_collision_and_score():
    data, room, ex, runner = _build()
    coin_obj = data["assets"]["objects"]["obj_coin"]
    events = coin_obj["events"]
    assert "collision_with_obj_player" in events
    assert events["collision_with_obj_player"]["actions"][0]["action"] == "destroy_instance"
    assert events["destroy"]["actions"][0]["action"] == "set_score"

    # The relative set_score the coin uses actually increments the run score.
    coin = next(i for i in room.instances if i.object_name == "obj_coin")
    ex.execute_set_score_action(coin, {"value": "10", "relative": True})
    ex.execute_set_score_action(coin, {"value": "10", "relative": True})
    assert runner.score == 20
