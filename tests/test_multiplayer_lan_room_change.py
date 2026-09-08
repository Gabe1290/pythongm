"""M1, docs/FULL_AUDIT_2026-09-07.md: a live multiplayer session must
survive a room change, not be silently orphaned.

Before this fix, extensions/multiplayer_lan state lived only in
room.extension_state, which is fresh and empty on the room GameRunner
switches to -- so change_room (or restart_current_room) left the session's
sockets and discovery-beacon thread running, unreachable, while the new
room reported "not connected". With PYGM_NET_AUTOHOST set, the next frame
would go on to auto-start a SECOND session for the new room, fighting the
first over the same port.

Uses a real GameRunner (loaded from a real, minimal two-room project
written to tmp_path -- host_game needs the real plugin-loaded action
dispatch _do()/_controller() drive) and the extension's own room-change
hook (_on_room_change), resolved via the same "loader imports under a
synthetic package name" pattern tests/test_multiplayer_lan_ghosts.py
already established.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from runtime import extension_hooks  # noqa: E402
from extensions.multiplayer_lan.state import peek_multiplayer  # noqa: E402
import extensions.multiplayer_lan.handlers as mp_handlers  # noqa: E402


def _loaded_handlers():
    """The handlers module actually behind the registered hooks -- the
    loader imports the extension under a synthetic package name, so a spy
    must patch the LOADED copy (see CLAUDE.md's raycast note; the same
    pattern test_multiplayer_lan_ghosts.py uses)."""
    for func, _phase in extension_hooks.get_frame_updates():
        if getattr(func, "__name__", "") == "_frame_update_broadcast":
            return sys.modules[func.__module__]
    return mp_handlers


def _write_two_room_project(tmp_path):
    project = {
        "name": "RoomChangeTest",
        "assets": {
            "objects": {"obj_ctrl": {"name": "obj_ctrl", "events": {}}},
            "rooms": {
                "r1": {"width": 320, "height": 240,
                       "instances": [{"object_name": "obj_ctrl", "x": 0, "y": 0}]},
                "r2": {"width": 320, "height": 240,
                       "instances": [{"object_name": "obj_ctrl", "x": 0, "y": 0}]},
            },
        },
        "settings": {},
    }
    path = tmp_path / "project.json"
    path.write_text(json.dumps(project), encoding="utf-8")
    return str(path)


def _controller(runner):
    inst = runner.current_room.instances[0]
    inst.action_executor = runner.action_executor
    return inst


def _do(runner, name, params):
    inst = _controller(runner)
    return runner.action_executor.action_handlers[name](inst, params)


def _make_hosting_runner(tmp_path):
    from runtime.game_runner import GameRunner

    runner = GameRunner(_write_two_room_project(tmp_path))
    runner.language = "en"
    start = runner.find_starting_room()
    runner.current_room = runner.rooms[start]
    runner._visited_rooms.add(start)
    _do(runner, "host_game", {"port": 0, "max_players": 8})
    return runner


class TestSessionSurvivesChangeRoom:
    def test_session_migrates_to_the_new_room(self, tmp_path):
        runner = _make_hosting_runner(tmp_path)
        old_room = runner.current_room
        old_state = peek_multiplayer(old_room)
        assert old_state is not None
        session = old_state.get("session")
        assert session is not None, "host_game must have created a live session"

        runner.change_room("r2")

        new_state = peek_multiplayer(runner.current_room)
        assert new_state is not None, "the new room must have multiplayer state"
        assert new_state.get("session") is session, (
            "the SAME session object must carry over -- not a fresh/lost one")

        try:
            assert session.bound_port, "the migrated session's socket must still be bound"
        finally:
            session.close()

    def test_old_room_no_longer_claims_the_session(self, tmp_path):
        runner = _make_hosting_runner(tmp_path)
        old_room = runner.current_room
        session = peek_multiplayer(old_room)["session"]

        runner.change_room("r2")

        try:
            assert peek_multiplayer(old_room) is None, (
                "the old room must not keep a stale reference to a session "
                "that now lives on the new room")
        finally:
            session.close()

    def test_beacon_migrates_alongside_the_session(self, tmp_path):
        """host_game(show_lobby=False) still starts a discovery beacon (see
        handlers.py's execute_host_game_action) -- it must migrate too, or
        it would keep advertising a game whose room reports not connected."""
        runner = _make_hosting_runner(tmp_path)
        old_state = peek_multiplayer(runner.current_room)
        beacon = old_state.get("beacon")
        assert beacon is not None, "host_game must have started a discovery beacon"

        runner.change_room("r2")

        new_state = peek_multiplayer(runner.current_room)
        try:
            assert new_state.get("beacon") is beacon
        finally:
            new_state["session"].close()
            beacon.stop()

    def test_autohost_does_not_start_a_second_session_after_migration(self, tmp_path, monkeypatch):
        """The other half of M1: PYGM_NET_AUTOHOST auto-starting a fresh
        session for every room that has none. Once the session correctly
        migrates, _resolve_state's "peek returns None" branch is never
        reached for r2, so no second session is ever created."""
        runner = _make_hosting_runner(tmp_path)
        session = peek_multiplayer(runner.current_room)["session"]
        monkeypatch.setenv("PYGM_NET_AUTOHOST", "1")
        try:
            runner.change_room("r2")

            handlers = _loaded_handlers()
            room, st = handlers._resolve_state(runner)

            assert st.get("session") is session, (
                "AUTOHOST must not replace the migrated session with a new one")
        finally:
            monkeypatch.delenv("PYGM_NET_AUTOHOST", raising=False)
            session.close()

    def test_room_with_no_networking_is_unaffected(self, tmp_path):
        """Behaviour-preservation: an ordinary, non-networked room change
        must not gain any multiplayer state out of nowhere."""
        from runtime.game_runner import GameRunner

        runner = GameRunner(_write_two_room_project(tmp_path))
        runner.language = "en"
        start = runner.find_starting_room()
        runner.current_room = runner.rooms[start]
        runner._visited_rooms.add(start)

        assert peek_multiplayer(runner.current_room) is None

        runner.change_room("r2")

        assert peek_multiplayer(runner.current_room) is None
