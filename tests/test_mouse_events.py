#!/usr/bin/env python3
"""Regression tests for mouse-event dispatch (audit H11).

The IDE events panel writes flat top-level keys (f"mouse_{button}_{event_type}",
e.g. 'mouse_left_press') and the GMK importer writes 'mouse_left_button' etc.,
but the runtime dispatchers historically read only the nested
events['mouse'][button_name] form — so every authored/imported mouse event was
silently inert. The dispatchers now accept both forms.
"""

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
            r._thymio_mouse_presses = {}
            return r


def _instance(events):
    inst = MagicMock()
    inst.object_data = {'events': events}
    inst.is_thymio = False
    inst.action_executor = MagicMock()
    return inst


class TestMouseSubEventLookup:
    def test_flat_press_key_resolves_to_left_button(self):
        from runtime.game_runner import _mouse_sub_event
        events = {'mouse_left_press': {'actions': [{'action': 'x'}]}}
        sub = _mouse_sub_event(events, 'left_button')
        assert sub == {'actions': [{'action': 'x'}]}

    def test_gmk_button_key_resolves(self):
        from runtime.game_runner import _mouse_sub_event
        events = {'mouse_left_button': {'actions': []}}
        assert _mouse_sub_event(events, 'left_button') is not None

    def test_release_key_maps_to_released_button_name(self):
        from runtime.game_runner import _mouse_sub_event
        events = {'mouse_left_release': {'actions': []}}
        assert _mouse_sub_event(events, 'left_button_released') is not None
        assert _mouse_sub_event(events, 'left_button') is None

    def test_nested_form_still_works(self):
        from runtime.game_runner import _mouse_sub_event
        events = {'mouse': {'left_button': {'actions': []}}}
        assert _mouse_sub_event(events, 'left_button') is not None

    def test_move_and_enter_map_to_mouse_move(self):
        from runtime.game_runner import _mouse_sub_event
        assert _mouse_sub_event({'mouse_move': {'actions': []}}, 'mouse_move')
        assert _mouse_sub_event({'mouse_enter': {'actions': []}}, 'mouse_move')

    def test_no_match_returns_none(self):
        from runtime.game_runner import _mouse_sub_event
        assert _mouse_sub_event({'create': {}}, 'left_button') is None


class TestDispatchFiresFlatEvents:
    def test_handle_mouse_press_fires_flat_left_event(self):
        runner = _runner()
        actions = [{'action': 'show_message', 'parameters': {}}]
        inst = _instance({'mouse_left_press': {'actions': actions}})
        runner.current_room = MagicMock(instances=[inst])

        runner.handle_mouse_press(1, (10, 20))

        inst.action_executor.execute_action_list.assert_called_once_with(inst, actions)
        assert (inst.mouse_x, inst.mouse_y) == (10, 20)

    def test_handle_mouse_release_fires_flat_release_event(self):
        runner = _runner()
        actions = [{'action': 'a'}]
        inst = _instance({'mouse_left_release': {'actions': actions}})
        runner.current_room = MagicMock(instances=[inst])

        runner.handle_mouse_release(1, (1, 2))

        inst.action_executor.execute_action_list.assert_called_once_with(inst, actions)

    def test_press_event_does_not_fire_on_release(self):
        runner = _runner()
        inst = _instance({'mouse_left_press': {'actions': [{'action': 'a'}]}})
        runner.current_room = MagicMock(instances=[inst])

        runner.handle_mouse_release(1, (1, 2))

        inst.action_executor.execute_action_list.assert_not_called()
