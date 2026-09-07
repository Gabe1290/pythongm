"""Regression tests for room restart/game-restart/re-entry (M51, M52, M53,
M5 docs/FULL_AUDIT_2026-09-07.md).

M51: restart_current_room rebuilt the room from the layout and discarded
persistent instances carried in from other rooms (a persistent player not in
the room's own layout ceased to exist after restart_room).

M52: restart_game rebuilt only the first room; rooms 2..N kept the previous
playthrough's mutated state (destroyed/moved instances).

M53: change_room re-fired the create event on already-initialised instances on
every re-entry, accumulating side effects.

M5: an orphan instance (its object was deleted from the project, but it's
still sitting in a room's authored layout) has object_data=None -- nothing
ever calls set_object_data for an instance whose object name isn't in the
project's objects dict (see runtime/room.py's set_sprites_for_instances).
_readd_persistent_instances' and change_room's "drop the room's own
non-persistent instance of this type" filter did
`inst.object_data.get('persistent', False)` with no None guard, so simply
restarting or changing to a room containing such an orphan raised
AttributeError and crashed the whole game loop.
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
    runner._visited_rooms = set()
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
# M5 — an orphan instance (object deleted, still in the room layout) must
# not crash restart_current_room / change_room's persistent-instance filter
# --------------------------------------------------------------------------

def test_restart_room_with_orphan_instance_does_not_crash(tmp_path):
    """The crash needs the orphan's object_name to match a CARRIED-IN
    persistent instance's object_name -- the filter only reaches
    `.get(...)` on the room's own instance when
    `inst.object_name == persistent_inst.object_name` is already True (an
    `and` short-circuit), so a mismatched name never exercised the bug.
    This models an object ("obj_ghost") that was deleted from the project
    after the room was authored: the room's own layout still has an
    "obj_ghost" instance (which set_sprites_for_instances leaves with
    object_data=None, since the name is no longer in the live objects
    dict), while a DIFFERENT, still-persistent "obj_ghost" instance was
    carried in from another room (its object_data is a stale snapshot
    from before the deletion -- exactly how a real persistent instance
    can retain valid, non-None object_data for a since-deleted object).
    """
    project = {
        "assets": {
            "objects": {
                # NOTE: no "obj_ghost" entry -- it was deleted from the
                # project after this room's layout was authored, but the
                # room JSON still references it, and a persistent instance
                # created before the deletion can still be carrying it.
            },
            "rooms": {
                "r1": {"width": 320, "height": 240,
                       "instances": [{"object_name": "obj_ghost", "x": 0, "y": 0}]},
            },
        },
        "settings": {},
    }
    runner = _runner(project, tmp_path)
    room = _room(runner, "r1")
    runner.current_room = room

    # A persistent "obj_ghost" carried in, with a stale-but-valid object_data
    # snapshot from before the object was deleted.
    ghost_persistent = GameInstance("obj_ghost", 10, 10, {}, action_executor=runner.action_executor)
    ghost_persistent.set_object_data({"name": "obj_ghost", "persistent": True})
    room.instances.append(ghost_persistent)

    runner.restart_current_room()  # must not raise AttributeError

    names = [i.object_name for i in runner.current_room.instances]
    assert names.count("obj_ghost") >= 1, "the persistent instance must survive"


def test_change_room_with_orphan_instance_does_not_crash(tmp_path):
    """Same fault, change_room's own inline copy of the filter (it doesn't
    call the shared _readd_persistent_instances): the TARGET room's
    authored layout has an orphan "obj_ghost" instance (object deleted),
    while the room being LEFT carries a persistent "obj_ghost" with a
    stale-but-valid object_data snapshot."""
    project = {
        "assets": {
            "objects": {},  # "obj_ghost" deleted from the project
            "rooms": {
                "r1": {"width": 320, "height": 240, "instances": []},
                "r2": {"width": 320, "height": 240,
                       "instances": [{"object_name": "obj_ghost", "x": 0, "y": 0}]},
            },
        },
        "settings": {},
    }
    runner = _runner(project, tmp_path)
    r1 = _room(runner, "r1")
    r2 = _room(runner, "r2")
    runner.current_room = r1

    ghost_persistent = GameInstance("obj_ghost", 5, 5, {}, action_executor=runner.action_executor)
    ghost_persistent.set_object_data({"name": "obj_ghost", "persistent": True})
    r1.instances.append(ghost_persistent)

    runner.change_room("r2")  # must not raise AttributeError

    names = [i.object_name for i in runner.current_room.instances]
    assert names.count("obj_ghost") >= 1, "the persistent instance must survive the room change"


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
