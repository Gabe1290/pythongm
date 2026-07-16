"""Regression tests for the 'fade' room transition (TODO.md's "Room
transition effects" item — the goto_room action's `transition` parameter
was accepted but ignored; every switch was instant).

GameRunner.change_room(room_name, transition='fade') now fades the old
room to black, switches rooms (identical logic to before — untouched),
then fades the new room back in. transition='none' (the default) is
byte-for-byte the pre-existing instant-switch code path — these tests
also pin that nothing changed for the common case.

Uses a real GameRunner against the bundled maze_1 sample (2 rooms) under
the SDL dummy driver, with pygame.time.Clock.tick monkeypatched to a
no-op so the fade's blocking sub-loop doesn't add real wall-clock delay
to the test suite.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pygame
from runtime.game_runner import GameRunner


class _InstantClock:
    """Drop-in for pygame.time.Clock with tick() returning immediately —
    keeps the fade's blocking sub-loop from adding real sleep time."""

    def tick(self, fps=0):
        return 0


@pytest.fixture
def runner():
    r = GameRunner(str(REPO_ROOT / "samples" / "maze_1" / "project.json"))
    r.language = "en"
    starting = r.find_starting_room()
    r.current_room = r.rooms[starting]
    r.window_width = r.current_room.width
    r.window_height = r.current_room.height
    pygame.display.set_mode((1, 1))  # any real display mode
    r.screen = pygame.display.set_mode((r.window_width, r.window_height))
    r.load_sprites()
    r.load_backgrounds()
    r.load_room_backgrounds()
    r.assign_sprites_to_rooms()
    for inst in list(r.current_room.instances):
        if inst.object_data and "events" in inst.object_data:
            r.action_executor.execute_event(inst, "create", inst.object_data["events"])
    return r


ROOM_NAMES = ["room0", "room1"]


def _other_room(runner):
    return next(n for n in ROOM_NAMES if n != runner.current_room.name)


class TestFadeTransition:
    def test_fade_switches_rooms_without_crashing(self, runner):
        target = _other_room(runner)
        with patch("pygame.time.Clock", _InstantClock):
            runner.change_room(target, transition="fade")
        assert runner.current_room.name == target

    def test_fade_actually_renders_the_new_room(self, runner):
        """The screen must not be left fully black after the fade-in —
        that would mean the snapshot/overlay math left alpha stuck at 255.
        Sampled via get_at() (no numpy dependency in this environment)."""
        target = _other_room(runner)
        with patch("pygame.time.Clock", _InstantClock):
            runner.change_room(target, transition="fade")
        w, h = runner.screen.get_size()
        non_black = any(
            runner.screen.get_at((x, y))[:3] != (0, 0, 0)
            for x in range(0, w, 8) for y in range(0, h, 8)
        )
        assert non_black, "screen is fully black after a fade-in — overlay alpha didn't reach 0"

    def test_fade_calls_the_overlay_helper_twice(self, runner):
        """Once for fade-out (old room), once for fade-in (new room)."""
        target = _other_room(runner)
        calls = []
        original = runner._fade_overlay

        def spy(base_frame, fade_in):
            calls.append(fade_in)
            return original(base_frame, fade_in)

        with patch("pygame.time.Clock", _InstantClock):
            with patch.object(runner, "_fade_overlay", side_effect=spy):
                runner.change_room(target, transition="fade")
        assert calls == [False, True]

    def test_quit_during_fade_stops_the_runner_and_does_not_hang(self, runner):
        target = _other_room(runner)
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        with patch("pygame.time.Clock", _InstantClock):
            runner.change_room(target, transition="fade")
        assert runner.running is False


class TestInstantTransitionUnchanged:
    def test_default_transition_is_instant_no_overlay_calls(self, runner):
        target = _other_room(runner)
        with patch.object(runner, "_fade_overlay") as mock_overlay:
            runner.change_room(target)  # no transition kwarg -> 'none'
            mock_overlay.assert_not_called()
        assert runner.current_room.name == target

    def test_explicit_none_and_unknown_values_are_also_instant(self, runner):
        for value in ("none", "wipe", "", None):
            target = _other_room(runner)
            with patch.object(runner, "_fade_overlay") as mock_overlay:
                runner.change_room(target, transition=value)
                mock_overlay.assert_not_called()
            assert runner.current_room.name == target

    def test_headless_no_screen_is_safe_even_with_fade_requested(self, runner):
        """A runner with no display surface (screen=None) — e.g. certain
        headless/test harnesses — must not crash when 'fade' is requested;
        it just skips the overlay like every other rendering path does."""
        runner.screen = None
        target = _other_room(runner)
        runner.change_room(target, transition="fade")  # must not raise
        assert runner.current_room.name == target


class TestGotoRoomActionTransitionPlumbing:
    def test_goto_room_action_sets_transition_attribute(self):
        from conftest import import_module_directly
        ae_module = import_module_directly("runtime/action_executor.py")
        ActionExecutor = ae_module.ActionExecutor

        class MockInstance:
            pass

        class MockGameRunner:
            def get_room_list(self):
                return ["room0", "room1"]

        ae = ActionExecutor(game_runner=MockGameRunner())
        inst = MockInstance()
        ae.execute_goto_room_action(inst, {"room": "room1", "transition": "fade"})
        assert inst.goto_room_target == "room1"
        assert inst.goto_room_transition == "fade"

    def test_update_loop_passes_transition_through_to_change_room(self, runner):
        target = _other_room(runner)
        inst = runner.current_room.instances[0]
        inst.goto_room_target = target
        inst.goto_room_transition = "fade"

        with patch.object(runner, "change_room") as mock_change:
            runner.update()
            mock_change.assert_called_once_with(target, transition="fade")

    def test_update_loop_defaults_to_none_when_transition_unset(self, runner):
        """execute_code samples that set self.goto_room_target directly
        (match3_3's pattern) never set goto_room_transition at all."""
        target = _other_room(runner)
        inst = runner.current_room.instances[0]
        inst.goto_room_target = target
        assert not hasattr(inst, "goto_room_transition")

        with patch.object(runner, "change_room") as mock_change:
            runner.update()
            mock_change.assert_called_once_with(target, transition="none")
