"""Generic per-frame extension hook (docs/MULTIPLAYER_LAN_PLAN.md Phase 0).

Before this, runtime/extension_hooks.py had exactly one hook kind (room
renderers, draw-pass only). LAN multiplayer (and Block World's gravity
feature before it worked around the gap by requiring an authored
apply_gravity action) needs code that runs every frame unconditionally,
at specific points in the frame -- this is the generic mechanism that
makes that possible for any extension, not just multiplayer.

Two tiers, matching this repo's established discipline for engine-loop
changes: pure unit tests of the registry itself, then a real GameRunner
(maze_1, the smallest bundled sample) driven through several real frames
via the FakeClock pattern this repo's other GameRunner-loop tests use
(tests/test_block_world_1_sample.py, tests/test_room_background_scroll_actions.py),
not a hand-rolled harness.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame
pygame.init()

from runtime import extension_hooks  # noqa: E402


import pytest


@pytest.fixture(autouse=True)
def _clear_frame_updates():
    # autouse + yield, not module-level setup_function/teardown_function --
    # those xunit-style hooks apply only to bare test functions, not to
    # methods inside test classes (this file uses classes throughout).
    extension_hooks.clear_frame_updates()
    yield
    extension_hooks.clear_frame_updates()


# ---------------------------------------------------------------------------
# Registry unit tests
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_register_and_get(self):
        def f(game_runner):
            pass
        extension_hooks.register_frame_update(f, "before_step")
        assert extension_hooks.get_frame_updates() == [(f, "before_step")]

    def test_invalid_phase_is_rejected(self):
        def f(game_runner):
            pass
        extension_hooks.register_frame_update(f, "mid_frame")
        assert extension_hooks.get_frame_updates() == []

    def test_non_callable_is_rejected(self):
        extension_hooks.register_frame_update("not a function", "before_step")
        assert extension_hooks.get_frame_updates() == []

    def test_registration_is_idempotent(self):
        def f(game_runner):
            pass
        extension_hooks.register_frame_update(f, "before_step")
        extension_hooks.register_frame_update(f, "before_step")
        assert extension_hooks.get_frame_updates() == [(f, "before_step")]

    def test_same_function_different_phases_both_register(self):
        def f(game_runner):
            pass
        extension_hooks.register_frame_update(f, "before_step")
        extension_hooks.register_frame_update(f, "after_update")
        assert extension_hooks.get_frame_updates() == [
            (f, "before_step"), (f, "after_update")]

    def test_clear(self):
        def f(game_runner):
            pass
        extension_hooks.register_frame_update(f, "before_step")
        extension_hooks.clear_frame_updates()
        assert extension_hooks.get_frame_updates() == []

    def test_run_frame_updates_only_calls_matching_phase(self):
        calls = []
        extension_hooks.register_frame_update(
            lambda gr: calls.append(("before", gr)), "before_step")
        extension_hooks.register_frame_update(
            lambda gr: calls.append(("after", gr)), "after_update")

        extension_hooks.run_frame_updates("RUNNER", "before_step")
        assert calls == [("before", "RUNNER")]

        extension_hooks.run_frame_updates("RUNNER", "after_update")
        assert calls == [("before", "RUNNER"), ("after", "RUNNER")]

    def test_a_raising_hook_does_not_stop_the_others_or_propagate(self):
        calls = []

        def bad(game_runner):
            raise RuntimeError("boom")

        def good(game_runner):
            calls.append("good")

        extension_hooks.register_frame_update(bad, "before_step")
        extension_hooks.register_frame_update(good, "before_step")

        extension_hooks.run_frame_updates(None, "before_step")  # must not raise
        assert calls == ["good"]


# ---------------------------------------------------------------------------
# Loader wiring: PluginLoader._load_frame_updates
# ---------------------------------------------------------------------------

class TestLoaderWiring:
    def test_load_frame_updates_registers_each_pair(self):
        from events.plugin_loader import PluginLoader

        def f(game_runner):
            pass
        def g(game_runner):
            pass

        loader = PluginLoader()
        count = loader._load_frame_updates([(f, "before_step"), (g, "after_update")])

        assert count == 2
        assert extension_hooks.get_frame_updates() == [
            (f, "before_step"), (g, "after_update")]

    def test_load_frame_updates_handles_none_and_empty(self):
        from events.plugin_loader import PluginLoader
        loader = PluginLoader()
        assert loader._load_frame_updates(None) == 0
        assert loader._load_frame_updates([]) == 0
        assert extension_hooks.get_frame_updates() == []


# ---------------------------------------------------------------------------
# Real GameRunner, real frames
# ---------------------------------------------------------------------------

class TestRealGameRunnerIntegration:
    def test_before_step_and_after_update_fire_once_per_frame_in_order(self):
        from runtime.game_runner import GameRunner

        project_json = str(REPO_ROOT / "samples" / "maze_1" / "project.json")
        runner = GameRunner(project_json)
        runner.language = "en"
        runner.show_message_dialog = lambda *a, **k: None
        runner.show_highscore_dialog = lambda *a, **k: None
        runner._show_name_entry_dialog = lambda *a, **k: ""
        runner.process_pending_messages = lambda *a, **k: None

        events = []
        extension_hooks.register_frame_update(
            lambda gr: events.append("before_step"), "before_step")
        extension_hooks.register_frame_update(
            lambda gr: events.append("after_update"), "after_update")

        state = {"frames": 0}
        MAX_FRAMES = 5

        class _FakeClock:
            def tick(self, fps=0):
                state["frames"] += 1
                if state["frames"] >= MAX_FRAMES:
                    runner.running = False
                return 0

            def get_fps(self):
                return 60.0

        real_clock = pygame.time.Clock
        pygame.time.Clock = _FakeClock
        try:
            result = runner.run()
        finally:
            pygame.time.Clock = real_clock
            pygame.init()
            pygame.display.set_mode((1, 1))

        assert result is not False, "game loop reported a fatal crash"
        assert state["frames"] == MAX_FRAMES

        # Exactly one before_step and one after_update per frame, and
        # before_step always precedes after_update within a frame (pairs
        # alternate: before, after, before, after, ...).
        assert events == ["before_step", "after_update"] * MAX_FRAMES

    def test_a_broken_extension_frame_update_does_not_stop_the_game(self):
        from runtime.game_runner import GameRunner

        project_json = str(REPO_ROOT / "samples" / "maze_1" / "project.json")
        runner = GameRunner(project_json)
        runner.language = "en"
        runner.show_message_dialog = lambda *a, **k: None
        runner.show_highscore_dialog = lambda *a, **k: None
        runner._show_name_entry_dialog = lambda *a, **k: ""
        runner.process_pending_messages = lambda *a, **k: None

        def bad(game_runner):
            raise RuntimeError("a broken extension")

        extension_hooks.register_frame_update(bad, "before_step")

        state = {"frames": 0}
        MAX_FRAMES = 3

        class _FakeClock:
            def tick(self, fps=0):
                state["frames"] += 1
                if state["frames"] >= MAX_FRAMES:
                    runner.running = False
                return 0

            def get_fps(self):
                return 60.0

        real_clock = pygame.time.Clock
        pygame.time.Clock = _FakeClock
        try:
            result = runner.run()
        finally:
            pygame.time.Clock = real_clock
            pygame.init()
            pygame.display.set_mode((1, 1))

        assert result is not False, "a broken extension frame update crashed the game loop"
        assert state["frames"] == MAX_FRAMES
