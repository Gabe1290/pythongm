#!/usr/bin/env python3
"""Regression tests for two runtime lifecycle fixes:

1. The once-per-game `game_start` event is actually triggered (it previously
   had no trigger anywhere in the engine, so startup setup authored there —
   score/lives/caption — never ran until something else happened to flip it on).
2. Collision processing stops as soon as a handler queues a room
   change/restart, so a single death can't deduct one life per overlapping
   instance when several cluster on the player.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pygame

pytestmark = skip_without_pygame


def _runner():
    with patch('runtime.game_runner.pygame'):
        with patch('runtime.game_runner.load_all_plugins'):
            from runtime.game_runner import GameRunner
            r = GameRunner.__new__(GameRunner)
            r.current_room = None
            r.running = True
            return r


def _instance(name, events=None):
    with patch('runtime.game_runner.pygame'):
        with patch('runtime.game_runner.load_all_plugins'):
            from runtime.game_runner import GameInstance
            inst = GameInstance(name, 0, 0, {}, MagicMock())
            inst.object_data = {'events': events or {}}
            return inst


class TestGameStartFires:
    def test_game_start_event_is_triggered(self):
        runner = _runner()
        inst = _instance('player', {'game_start': {'actions': []}})
        runner.current_room = SimpleNamespace(instances=[inst])

        runner.trigger_game_start_event()

        # Mirrors trigger_room_start_event: the engine dispatches the event name
        # for every instance that has an events dict, and execute_event itself
        # no-ops when 'game_start' isn't authored on that object.
        inst.action_executor.execute_event.assert_called_once()
        called_event = inst.action_executor.execute_event.call_args[0][1]
        assert called_event == 'game_start'

    def test_instance_without_events_is_skipped(self):
        runner = _runner()
        inst = _instance('wall')
        inst.object_data = {}  # no 'events' key at all
        runner.current_room = SimpleNamespace(instances=[inst])

        runner.trigger_game_start_event()

        inst.action_executor.execute_event.assert_not_called()

    def test_no_current_room_is_safe(self):
        runner = _runner()
        runner.current_room = None
        runner.trigger_game_start_event()  # must not raise


class TestRoomTransitionPending:
    @pytest.mark.parametrize('flag', [
        'restart_room_flag', 'next_room_flag',
        'previous_room_flag', 'restart_game_flag',
    ])
    def test_each_transition_flag_is_detected(self, flag):
        runner = _runner()
        inst = _instance('player')
        runner.current_room = SimpleNamespace(instances=[inst])

        assert runner._room_transition_pending() is False
        setattr(inst, flag, True)
        assert runner._room_transition_pending() is True

    def test_goto_room_target_is_detected(self):
        runner = _runner()
        inst = _instance('player')
        runner.current_room = SimpleNamespace(instances=[inst])

        assert runner._room_transition_pending() is False
        inst.goto_room_target = 'room1'
        assert runner._room_transition_pending() is True

    def test_no_room_returns_false(self):
        runner = _runner()
        runner.current_room = None
        assert runner._room_transition_pending() is False
