"""Regression test for room_speed -> fps (audit M48).

The GMK importer (and templates) persist settings['room_speed'] (GM8 default
30), but the runtime ignored it and hardcoded fps=60, so imported games ran at
double speed. _load_project_settings now reads room_speed (clamped 1..240).
"""

import pytest

pytest.importorskip("pygame")

from runtime.game_runner import GameRunner


def _runner_with_settings(settings):
    runner = GameRunner.__new__(GameRunner)
    runner.fps = 60
    runner.project_data = {"settings": settings}
    runner._load_project_settings()
    return runner


def test_room_speed_sets_fps():
    assert _runner_with_settings({"room_speed": 30}).fps == 30


def test_no_room_speed_keeps_default():
    assert _runner_with_settings({}).fps == 60


def test_room_speed_clamped_high():
    assert _runner_with_settings({"room_speed": 10000}).fps == 240


def test_room_speed_clamped_low():
    assert _runner_with_settings({"room_speed": 0}).fps == 1


def test_room_speed_invalid_keeps_default():
    assert _runner_with_settings({"room_speed": "fast"}).fps == 60
