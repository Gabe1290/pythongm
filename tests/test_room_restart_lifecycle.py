"""Regression tests for room restart/game-restart/re-entry (M51, M52, M53).

M51: restart_current_room rebuilt the room from the layout and discarded
persistent instances carried in from other rooms (a persistent player not in
the room's own layout ceased to exist after restart_room).

M52: restart_game rebuilt only the first room; rooms 2..N kept the previous
playthrough's mutated state (destroyed/moved instances).

M53: change_room re-fired the create event on already-initialised instances on
every re-entry, accumulating side effects.
"""

import pytest

pytest.importorskip("pygame")

from runtime.game_runner import GameRunner, GameRoom, GameInstance
from runtime.action_executor import ActionExecutor


def _runner(project_data, tmp_path):
    runner = GameRunner.__new__(GameRunner)
    runner.project_data = project_data
    runner.action_executor = ActionExecutor(game_runner=runner)
    runner.project_path = tmp_path
    runner.sprites = {}
    runner.backgrounds = {}
    runner.rooms = {}
    runner._objects_data = project_data.get("assets", {}).get("objects", {})
    runner._destroyed_memory = {}
    runner.screen = None
    runner.current_room = None
    runner.score = runner.lives = runner.health = 0
    runner._room_transition_grace_frames = 0
    return runner


def _room(runner, name):
    data = runner.project_data["assets"]["rooms"][name]
    room = runner._build_room_from_data(name, data)
    runner.rooms[name] = room
    return room


# --------------------------------------------------------------------------
# M53 — create fires at most once per instance
# --------------------------------------------------------------------------

def test_create_event_fires_once_per_instance():
    ex = ActionExecutor(game_runner=None)
    count = {"n": 0}
    ex.action_handlers["bump"] = lambda inst, p: count.__setitem__("n", count["n"] + 1)

    class _Inst:
        pass

    inst = _Inst()
    events = {"create": {"actions": [{"action": "bump", "parameters": {}}]}}
    ex.execute_event(inst, "create", events)
    ex.execute_event(inst, "create", events)  # re-entry
    assert count["n"] == 1


# --------------------------------------------------------------------------
# M51 — restart_current_room keeps persistent instances
# --------------------------------------------------------------------------

def test_restart_room_keeps_persistent_instance(tmp_path):
    project = {
        "assets": {
            "objects": {
                "obj_player": {"name": "obj_player", "persistent": True},
                "obj_wall": {"name": "obj_wall"},
            },
            "rooms": {
                # Room 2 layout has NO player (it was carried in from room 1).
                "r2": {"width": 320, "height": 240,
                       "instances": [{"object_name": "obj_wall", "x": 0, "y": 0}]},
            },
        },
        "settings": {},
    }
    runner = _runner(project, tmp_path)
    room = _room(runner, "r2")
    runner.current_room = room

    # Simulate a persistent player carried into r2 by change_room.
    player = GameInstance("obj_player", 50, 50, {}, action_executor=runner.action_executor)
    player.set_object_data({"name": "obj_player", "persistent": True})
    room.instances.append(player)

    runner.restart_current_room()

    names = [i.object_name for i in runner.current_room.instances]
    assert "obj_player" in names, "persistent player must survive room restart"
    assert "obj_wall" in names  # authored instance rebuilt


# --------------------------------------------------------------------------
# M52 — restart_game rebuilds every visited room
# --------------------------------------------------------------------------

def test_restart_game_rebuilds_other_rooms(tmp_path):
    project = {
        "assets": {
            "objects": {"obj_box": {"name": "obj_box"}},
            "rooms": {
                "r1": {"width": 320, "height": 240,
                       "instances": [{"object_name": "obj_box", "x": 0, "y": 0}]},
                "r2": {"width": 320, "height": 240,
                       "instances": [{"object_name": "obj_box", "x": 0, "y": 0},
                                     {"object_name": "obj_box", "x": 32, "y": 0}]},
            },
        },
        "settings": {},
    }
    runner = _runner(project, tmp_path)
    _room(runner, "r1")
    r2 = _room(runner, "r2")
    runner.current_room = runner.rooms["r1"]

    # Simulate destroying both r2 instances during the prior playthrough.
    r2.instances.clear()
    assert len(runner.rooms["r2"].instances) == 0

    runner.restart_game()

    # r2 must be rebuilt fresh from its 2-instance layout.
    assert len(runner.rooms["r2"].instances) == 2
