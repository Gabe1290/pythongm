"""Generic room-change extension hook (M1, docs/FULL_AUDIT_2026-09-07.md).

Before this, runtime/extension_hooks.py had room renderers and frame
updates, but no way for an extension to know a room switch happened at
all. LAN multiplayer needs it: its live NetworkSession (sockets, a
discovery-beacon thread) lived in room.extension_state, which is fresh
and empty on the new room after change_room/restart_current_room --
silently orphaning the session and, with PYGM_NET_AUTOHOST set, causing a
second session to be auto-started for every new room.

Same two-tier structure as tests/test_extension_frame_update_hook.py
(its own precedent for this hook family): pure registry unit tests, then
a real GameRunner driven through a real change_room()/restart_current_room()
call. Multiplayer's own migration behaviour has its own dedicated test in
tests/test_multiplayer_lan_room_change.py.
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
def _clear_room_change_hooks():
    extension_hooks.clear_room_change_hooks()
    yield
    extension_hooks.clear_room_change_hooks()


# ---------------------------------------------------------------------------
# Registry unit tests
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_register_and_get(self):
        def f(old_room, new_room):
            pass
        extension_hooks.register_room_change_hook(f)
        assert extension_hooks.get_room_change_hooks() == [f]

    def test_non_callable_is_rejected(self):
        extension_hooks.register_room_change_hook("not a function")
        assert extension_hooks.get_room_change_hooks() == []

    def test_registration_is_idempotent(self):
        def f(old_room, new_room):
            pass
        extension_hooks.register_room_change_hook(f)
        extension_hooks.register_room_change_hook(f)
        assert extension_hooks.get_room_change_hooks() == [f]

    def test_clear(self):
        def f(old_room, new_room):
            pass
        extension_hooks.register_room_change_hook(f)
        extension_hooks.clear_room_change_hooks()
        assert extension_hooks.get_room_change_hooks() == []

    def test_run_room_change_hooks_calls_every_registered_hook(self):
        calls = []
        extension_hooks.register_room_change_hook(
            lambda old, new: calls.append(("a", old, new)))
        extension_hooks.register_room_change_hook(
            lambda old, new: calls.append(("b", old, new)))

        extension_hooks.run_room_change_hooks("OLD", "NEW")

        assert calls == [("a", "OLD", "NEW"), ("b", "OLD", "NEW")]

    def test_a_raising_hook_does_not_stop_the_others_or_propagate(self):
        calls = []

        def bad(old_room, new_room):
            raise RuntimeError("boom")

        def good(old_room, new_room):
            calls.append("good")

        extension_hooks.register_room_change_hook(bad)
        extension_hooks.register_room_change_hook(good)

        extension_hooks.run_room_change_hooks(None, None)  # must not raise
        assert calls == ["good"]


# ---------------------------------------------------------------------------
# Loader wiring: PluginLoader._load_room_change_hooks
# ---------------------------------------------------------------------------

class TestLoaderWiring:
    def test_load_room_change_hooks_registers_each(self):
        from events.plugin_loader import PluginLoader

        def f(old_room, new_room):
            pass
        def g(old_room, new_room):
            pass

        loader = PluginLoader()
        count = loader._load_room_change_hooks([f, g])

        assert count == 2
        assert extension_hooks.get_room_change_hooks() == [f, g]

    def test_load_room_change_hooks_handles_none_and_empty(self):
        from events.plugin_loader import PluginLoader
        loader = PluginLoader()
        assert loader._load_room_change_hooks(None) == 0
        assert loader._load_room_change_hooks([]) == 0
        assert extension_hooks.get_room_change_hooks() == []


# ---------------------------------------------------------------------------
# Real GameRunner: change_room and restart_current_room both fire it
# ---------------------------------------------------------------------------

class TestRealGameRunnerIntegration:
    PROJECT_JSON = str(REPO_ROOT / "samples" / "maze_1" / "project.json")

    @classmethod
    def _runner_with_current_room(cls):
        """GameRunner.__init__ loads project data and builds every room,
        but doesn't set current_room until run() calls
        find_starting_room() -- done here explicitly, matching
        tests/test_multiplayer_lan_ghosts.py's own _init() helper."""
        from runtime.game_runner import GameRunner

        runner = GameRunner(cls.PROJECT_JSON)
        runner.language = "en"
        start = runner.find_starting_room()
        runner.current_room = runner.rooms[start]
        runner._visited_rooms.add(start)
        return runner

    def test_change_room_fires_the_hook_with_old_and_new_room(self):
        runner = self._runner_with_current_room()
        old_room = runner.current_room
        assert old_room is not None

        other_room_name = next(
            name for name in runner.rooms if runner.rooms[name] is not old_room)

        calls = []
        extension_hooks.register_room_change_hook(
            lambda old, new: calls.append((old, new)))

        runner.change_room(other_room_name)

        assert len(calls) == 1
        got_old, got_new = calls[0]
        assert got_old is old_room
        assert got_new is runner.current_room
        assert got_new is not old_room

    def test_restart_current_room_fires_the_hook(self):
        runner = self._runner_with_current_room()
        old_room = runner.current_room

        calls = []
        extension_hooks.register_room_change_hook(
            lambda old, new: calls.append((old, new)))

        runner.restart_current_room()

        assert len(calls) == 1
        got_old, got_new = calls[0]
        assert got_old is old_room
        assert got_new is runner.current_room
        # restart_current_room always rebuilds a fresh GameRoom object,
        # even though it's logically "the same" room by name.
        assert got_new is not old_room

    def test_a_broken_room_change_hook_does_not_stop_the_room_change(self):
        runner = self._runner_with_current_room()
        old_room = runner.current_room
        other_room_name = next(
            name for name in runner.rooms if runner.rooms[name] is not old_room)

        def bad(old_room, new_room):
            raise RuntimeError("a broken extension")

        extension_hooks.register_room_change_hook(bad)

        runner.change_room(other_room_name)  # must not raise

        assert runner.current_room.name == other_room_name
