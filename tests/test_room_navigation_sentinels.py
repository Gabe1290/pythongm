"""Regression test for room navigation sentinels (audit M28).

The action editor saves '__next__'/'__prev__'/'__current__' for the
"Next/Previous/Restart" dropdown entries, but the runtime consumed none of
them: execute_goto_room_action rejected them as unknown room names and
execute_check_room_action compared them literally (always false). goto_room now
maps them onto the existing navigation flags and check_room resolves them
against the room list.
"""

import pytest

from conftest import import_module_directly

_mod = import_module_directly("runtime/action_executor.py")
ActionExecutor = _mod.ActionExecutor


class _Room:
    def __init__(self, name):
        self.name = name


class _Runner:
    def __init__(self, current="room2"):
        self.current_room = _Room(current)
        self._room_list = ["room1", "room2", "room3"]

    def get_room_list(self):
        return self._room_list


class _Instance:
    def __init__(self):
        self.next_room_flag = False
        self.previous_room_flag = False
        self.restart_room_flag = False
        self.goto_room_target = None
        self.goto_room_transition = None


@pytest.fixture
def executor():
    return ActionExecutor(game_runner=_Runner())


class TestGotoRoomSentinels:
    def test_next_sets_flag(self, executor):
        inst = _Instance()
        executor.execute_goto_room_action(inst, {"room": "__next__"})
        assert inst.next_room_flag is True
        assert inst.goto_room_target is None

    def test_prev_sets_flag(self, executor):
        inst = _Instance()
        executor.execute_goto_room_action(inst, {"room": "__prev__"})
        assert inst.previous_room_flag is True

    def test_current_sets_restart_flag(self, executor):
        inst = _Instance()
        executor.execute_goto_room_action(inst, {"room": "__current__"})
        assert inst.restart_room_flag is True

    def test_concrete_room_still_sets_target(self, executor):
        inst = _Instance()
        executor.execute_goto_room_action(inst, {"room": "room3"})
        assert inst.goto_room_target == "room3"
        assert inst.next_room_flag is False


class TestCheckRoomSentinels:
    def test_current_matches(self, executor):
        inst = _Instance()
        assert executor.execute_check_room_action(inst, {"room": "__current__"}) is True

    def test_next_resolves_to_room3(self, executor):
        inst = _Instance()
        # current is room2, so __next__ -> room3, which is not the current room
        assert executor.execute_check_room_action(inst, {"room": "__next__"}) is False

    def test_prev_resolves_to_room1(self, executor):
        inst = _Instance()
        assert executor.execute_check_room_action(inst, {"room": "__prev__"}) is False

    def test_current_with_not_flag(self, executor):
        inst = _Instance()
        assert executor.execute_check_room_action(
            inst, {"room": "__current__", "not_flag": True}) is False
