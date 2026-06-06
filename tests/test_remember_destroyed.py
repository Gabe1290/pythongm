#!/usr/bin/env python3
"""Tests for the per-object `remember_destroyed` ("Stay destroyed") feature.

When an object opts in, destroying one of its instances is remembered so the
instance does NOT respawn when the room is rebuilt from its layout (a room
restart). Leaving and re-entering a room already preserves the deletion because
change_room reuses the same room object, so that path needs no memory. A full
game restart clears the memory, bringing every instance back.
"""

from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pygame

pytestmark = skip_without_pygame


def _make_runner():
    """A bare GameRunner with just the attributes the restart paths touch."""
    with patch('runtime.game_runner.pygame'):
        with patch('runtime.game_runner.load_all_plugins'):
            from runtime.game_runner import GameRunner
            runner = GameRunner.__new__(GameRunner)
            runner.action_executor = MagicMock()
            runner.project_path = None
            runner.sprites = {}
            runner.backgrounds = {}
            runner.screen = None
            runner.rooms = {}
            runner.current_room = None
            runner.score = 0
            runner.lives = 3
            runner.health = 100
            runner._room_transition_grace_frames = 0
            runner._destroyed_memory = {}
            return runner


def _make_room(name, instances):
    """A real GameRoom so identity (xstart/ystart) and grid behave for real."""
    with patch('runtime.game_runner.pygame'):
        with patch('runtime.game_runner.load_all_plugins'):
            from runtime.game_runner import GameRoom
            return GameRoom(
                name,
                {'width': 640, 'height': 480, 'instances': instances},
                action_executor=MagicMock(),
            )


# Two bonuses at distinct positions plus a player. Positions are the identity,
# so the two bonuses must not share coordinates.
_LAYOUT = [
    {'object_name': 'obj_bonus', 'x': 100, 'y': 100},
    {'object_name': 'obj_bonus', 'x': 200, 'y': 150},
    {'object_name': 'player', 'x': 50, 'y': 50},
]

# Project data used by the restart paths: obj_bonus opts in, player does not.
_PROJECT = {
    'assets': {
        'rooms': {'lvl': {'width': 640, 'height': 480, 'instances': _LAYOUT}},
        'objects': {
            'obj_bonus': {'name': 'obj_bonus', 'remember_destroyed': True},
            'player': {'name': 'player'},
        },
    },
    'settings': {},
}


def _names_at(room):
    return sorted((i.object_name, i.xstart, i.ystart) for i in room.instances)


class TestRememberDestroyedHelpers:
    def test_record_only_flagged_objects(self):
        runner = _make_runner()
        room = _make_room('lvl', _LAYOUT)
        room.set_sprites_for_instances({}, _PROJECT['assets']['objects'])

        bonus = next(i for i in room.instances if i.object_name == 'obj_bonus')
        player = next(i for i in room.instances if i.object_name == 'player')

        runner._remember_destroyed_instance(room, bonus)
        runner._remember_destroyed_instance(room, player)  # not flagged -> ignored

        assert runner._destroyed_memory == {
            'lvl': {('obj_bonus', 100.0, 100.0)}
        }

    def test_record_and_consume_use_the_same_identity(self):
        """The recorded key must be exactly what the filter looks for."""
        runner = _make_runner()
        room = _make_room('lvl', _LAYOUT)
        room.set_sprites_for_instances({}, _PROJECT['assets']['objects'])
        bonus = next(i for i in room.instances if i.x == 100)

        runner._remember_destroyed_instance(room, bonus)
        # Rebuild a fresh copy of the room and filter it.
        fresh = _make_room('lvl', _LAYOUT)
        runner._apply_destroyed_memory(fresh)

        remaining = [(i.object_name, i.xstart, i.ystart) for i in fresh.instances]
        assert ('obj_bonus', 100.0, 100.0) not in remaining
        assert ('obj_bonus', 200.0, 150.0) in remaining  # the uncollected one
        assert ('player', 50.0, 50.0) in remaining

    def test_apply_is_noop_without_memory(self):
        runner = _make_runner()
        room = _make_room('lvl', _LAYOUT)
        before = _names_at(room)
        runner._apply_destroyed_memory(room)
        assert _names_at(room) == before


class TestRestartHonorsMemory:
    def test_restart_does_not_respawn_remembered_bonus(self):
        runner = _make_runner()
        runner.project_data = _PROJECT
        runner.current_room = _make_room('lvl', _LAYOUT)
        runner.rooms = {'lvl': runner.current_room}
        # Simulate that the (100,100) bonus was collected during play.
        runner._destroyed_memory = {'lvl': {('obj_bonus', 100.0, 100.0)}}

        runner.restart_current_room()

        ids = _names_at(runner.current_room)
        assert ('obj_bonus', 100.0, 100.0) not in ids   # stays gone
        assert ('obj_bonus', 200.0, 150.0) in ids       # uncollected respawns
        assert ('player', 50.0, 50.0) in ids            # player respawns

    def test_restart_respawns_everything_when_nothing_remembered(self):
        runner = _make_runner()
        runner.project_data = _PROJECT
        runner.current_room = _make_room('lvl', _LAYOUT)
        runner.rooms = {'lvl': runner.current_room}

        runner.restart_current_room()

        assert len(runner.current_room.instances) == 3


class TestGameRestartResets:
    def test_game_restart_clears_memory(self):
        runner = _make_runner()
        runner.project_data = _PROJECT
        runner.current_room = _make_room('lvl', _LAYOUT)
        runner.rooms = {'lvl': runner.current_room}
        runner._destroyed_memory = {'lvl': {('obj_bonus', 100.0, 100.0)}}

        # get_room_list drives which room restart_game rebuilds.
        runner.get_room_list = lambda: ['lvl']

        runner.restart_game()

        assert runner._destroyed_memory == {}
        # First room fully repopulated (bonus is back).
        ids = _names_at(runner.current_room)
        assert ('obj_bonus', 100.0, 100.0) in ids


class TestInheritanceIsChildOnly:
    def test_remember_destroyed_not_inherited_from_parent(self):
        from runtime.game_runner import resolve_parent_inheritance
        objects = {
            'parent_obj': {'name': 'parent_obj', 'remember_destroyed': True},
            'child_obj': {'name': 'child_obj', 'parent': 'parent_obj'},
        }
        merged = resolve_parent_inheritance(objects['child_obj'], objects)
        # Child did not set it, so it must NOT pick up the parent's True.
        assert merged.get('remember_destroyed') in (None, False)
