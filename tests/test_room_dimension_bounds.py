"""Regression tests for room-dimension sanitization (audit Batch A, finding #6).

A room surface is allocated at width x height, so a malformed or hostile
project.json that sets a room size to 0, a negative, a non-numeric value, or an
absurdly large number must not crash pygame or exhaust memory at room-build
time. GameRoom routes width/height through ``_sane_room_dimension`` which
coerces to int, falls back to the default on garbage, and clamps to
[ROOM_MIN_DIMENSION, ROOM_MAX_DIMENSION].

Only the parse path is exercised here, so the tests run headless without a real
display (pygame is patched out, matching the rest of test_game_runner.py).
"""

from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture
def mock_action_executor():
    return MagicMock()


def _make_room(room_data, mock_action_executor):
    with patch('runtime.game_runner.pygame'):
        with patch('runtime.game_runner.load_all_plugins'):
            from runtime.game_runner import GameRoom
            return GameRoom("test", room_data, mock_action_executor)


class TestSaneRoomDimensionHelper:
    """Direct coverage of the clamp helper."""

    def test_within_bounds_passthrough(self):
        from runtime.game_runner import _sane_room_dimension
        assert _sane_room_dimension(800, 1024) == 800
        assert _sane_room_dimension(640, 768) == 640

    def test_zero_and_negative_clamp_to_min(self):
        from runtime.game_runner import (
            _sane_room_dimension, ROOM_MIN_DIMENSION)
        assert _sane_room_dimension(0, 1024) == ROOM_MIN_DIMENSION
        assert _sane_room_dimension(-500, 1024) == ROOM_MIN_DIMENSION

    def test_absurdly_large_clamps_to_max(self):
        from runtime.game_runner import (
            _sane_room_dimension, ROOM_MAX_DIMENSION)
        assert _sane_room_dimension(10 ** 9, 1024) == ROOM_MAX_DIMENSION

    def test_non_numeric_falls_back_to_default(self):
        from runtime.game_runner import _sane_room_dimension
        assert _sane_room_dimension(None, 1024) == 1024
        assert _sane_room_dimension("wide", 768) == 768
        assert _sane_room_dimension([], 1024) == 1024

    def test_float_inf_nan_fall_back_to_default(self):
        from runtime.game_runner import _sane_room_dimension
        # int(inf)/int(nan) raise -> default; guard is belt-and-suspenders.
        assert _sane_room_dimension(float('inf'), 1024) == 1024
        assert _sane_room_dimension(float('nan'), 1024) == 1024

    def test_float_within_bounds_coerced_to_int(self):
        from runtime.game_runner import _sane_room_dimension
        assert _sane_room_dimension(800.9, 1024) == 800


class TestGameRoomDimensions:
    """End-to-end through GameRoom.__init__."""

    def test_normal_dimensions_preserved(self, mock_action_executor):
        room = _make_room({'width': 800, 'height': 600}, mock_action_executor)
        assert room.width == 800
        assert room.height == 600

    def test_missing_dimensions_use_defaults(self, mock_action_executor):
        room = _make_room({}, mock_action_executor)
        assert room.width == 1024
        assert room.height == 768

    def test_zero_dimensions_clamped(self, mock_action_executor):
        from runtime.game_runner import ROOM_MIN_DIMENSION
        room = _make_room({'width': 0, 'height': 0}, mock_action_executor)
        assert room.width == ROOM_MIN_DIMENSION
        assert room.height == ROOM_MIN_DIMENSION

    def test_negative_dimensions_clamped(self, mock_action_executor):
        from runtime.game_runner import ROOM_MIN_DIMENSION
        room = _make_room({'width': -100, 'height': -1}, mock_action_executor)
        assert room.width == ROOM_MIN_DIMENSION
        assert room.height == ROOM_MIN_DIMENSION

    def test_huge_dimensions_clamped(self, mock_action_executor):
        from runtime.game_runner import ROOM_MAX_DIMENSION
        room = _make_room(
            {'width': 10 ** 9, 'height': 10 ** 9}, mock_action_executor)
        assert room.width == ROOM_MAX_DIMENSION
        assert room.height == ROOM_MAX_DIMENSION

    def test_non_numeric_dimensions_use_defaults(self, mock_action_executor):
        room = _make_room(
            {'width': 'big', 'height': None}, mock_action_executor)
        assert room.width == 1024
        assert room.height == 768
