"""File-exchange multiplayer -- end to end (actions + events + GameRunner
glue). docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md Phase 1.

Mirrors tests/test_multiplayer_lan_tier_a.py's harness exactly (a light
mock GameRunner/room/instance stack plus a real ActionExecutor, so the
action dispatch and execute_event paths are the real ones) with a real
tempfile.TemporaryDirectory() shared folder standing in for the socket
pair.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from events.plugin_loader import load_all_plugins  # noqa: E402
from events.action_types import ACTION_TYPES  # noqa: E402
from events.event_types import EVENT_TYPES  # noqa: E402
from runtime.action_executor import ActionExecutor  # noqa: E402

import extensions.multiplayer_files.handlers as H  # noqa: E402
from extensions.multiplayer_files.state import peek_multiplayer_files  # noqa: E402


class _Inst:
    def __init__(self, events=None):
        self.object_name = "obj_ctrl"
        self.action_executor = None
        self.x = self.y = 0.0
        self.rotation = 0.0
        self.image_index = 0.0
        self.visible = True
        self.object_data = {"events": events or {}}


class _Room:
    def __init__(self):
        self.instances = []
        self.extension_state = {}


class _GR:
    def __init__(self, room):
        self.current_room = room
        self.global_variables = {}


class _RecordingExecutor(ActionExecutor):
    def __init__(self, game_runner):
        super().__init__(game_runner=game_runner)
        self.fired = []

    def execute_event(self, instance, event_name, events_data):
        self.fired.append(event_name)
        return super().execute_event(instance, event_name, events_data)


_LISTENER_EVENTS = ("file_session_started", "player_joined_files",
                    "round_resolved", "player_skipped_round",
                    "network_message_files", "file_session_lost")


def _make_side():
    room = _Room()
    gr = _GR(room)
    ex = _RecordingExecutor(gr)
    load_all_plugins(ex)
    ctrl = _Inst()
    listener = _Inst(events={name: {"actions": []} for name in _LISTENER_EVENTS})
    ctrl.action_executor = ex
    listener.action_executor = ex
    room.instances = [ctrl, listener]
    return room, gr, ex, ctrl


def _do(ex, name, inst, params):
    inst.action_executor = ex
    return ex.action_handlers[name](inst, params)


def _pump(*grs, rounds=10):
    """Force each side's session poll gate open every round -- fast,
    deterministic, no reliance on real elapsed wall time between pumps
    (the gate itself is covered at the session level, see
    test_multiplayer_files_session.py::TestPollGating)."""
    for _ in range(rounds):
        for gr in grs:
            st = peek_multiplayer_files(gr.current_room)
            if st and st.get("session") is not None:
                st["session"]._last_poll = 0.0
            H._frame_update_before_step(gr)
            H._frame_update_after_update(gr)


def _connect(tmp):
    hroom, hgr, hex_, hctrl = _make_side()
    _do(hex_, "host_game_files", hctrl, {"folder": tmp, "max_players": 8,
                                          "round_deadline": 100})

    croom, cgr, cex, cctrl = _make_side()
    _do(cex, "join_game_files", cctrl, {"folder": tmp})

    for _ in range(10):
        _pump(hgr, cgr, rounds=1)
        if cgr.global_variables.get("player_id", -1) == 1:
            break
    return (hroom, hgr, hex_, hctrl), (croom, cgr, cex, cctrl)


def _close(*sides):
    for room, gr, ex, ctrl in sides:
        try:
            _do(ex, "leave_game_files", ctrl, {})
        except Exception:
            pass


class TestRegistration:
    def test_actions_and_events_registered_after_plugin_load(self):
        load_all_plugins(ActionExecutor())
        for a in ("host_game_files", "join_game_files", "leave_game_files",
                  "set_shared_var_files", "get_shared_var_files", "end_turn",
                  "send_network_message_files"):
            assert a in ACTION_TYPES, a
        for e in _LISTENER_EVENTS:
            assert e in EVENT_TYPES, e

    def test_no_collision_with_multiplayer_lan_actions(self):
        """The whole reason set_shared_var_files/get_shared_var_files/
        send_network_message_files aren't named set_shared_var/
        get_shared_var/send_network_message -- plugin_loader skips a
        same-named action from a second extension (the landmine
        actions.py's own module docstring documents), so both must be
        present with their OWN, distinct descriptions."""
        load_all_plugins(ActionExecutor())
        for name, files_name in (
            ("set_shared_var", "set_shared_var_files"),
            ("get_shared_var", "get_shared_var_files"),
            ("send_network_message", "send_network_message_files"),
        ):
            assert name in ACTION_TYPES
            assert files_name in ACTION_TYPES
            assert ACTION_TYPES[name].description != \
                ACTION_TYPES[files_name].description

    def test_no_collision_with_multiplayer_lan_events(self):
        """Same landmine, one level up: events/plugin_loader.py's
        _load_events has the identical skip-if-already-registered
        behaviour for EVENT_TYPES -- network_message_files, not
        network_message."""
        load_all_plugins(ActionExecutor())
        assert "network_message" in EVENT_TYPES
        assert "network_message_files" in EVENT_TYPES
        assert EVENT_TYPES["network_message"].description != \
            EVENT_TYPES["network_message_files"].description

    def test_category(self):
        load_all_plugins(ActionExecutor())
        assert ACTION_TYPES["host_game_files"].category == "Network"
        assert EVENT_TYPES["round_resolved"].category == "Network"


class TestConnectFlow:
    """Phase 4: host_game_files(show_lobby=True) / join_game_files
    (folder="auto") route through FileConnectScreen.run(), which on a
    headless GameRunner (no .screen, as here) short-circuits per its own
    documented fallback -- host always "start"s immediately, client
    "cancel"s with no path given. Real screen-interaction coverage lives
    in test_multiplayer_files_connect_screen.py; this just confirms the
    action handlers wire into that fallback correctly."""

    def test_show_lobby_still_hosts_on_a_headless_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            room, gr, ex, ctrl = _make_side()
            _do(ex, "host_game_files", ctrl, {"folder": tmp, "show_lobby": True})
            st = peek_multiplayer_files(room)
            assert st is not None and st.get("session") is not None
            assert st["session"].mode == "host"

    def test_folder_auto_with_no_screen_cancels_and_leaves_single_player(self):
        room, gr, ex, ctrl = _make_side()
        _do(ex, "join_game_files", ctrl, {"folder": "auto"})
        st = peek_multiplayer_files(room)
        assert st is None or st.get("session") is None

    def test_cancelling_the_lobby_tears_down_hosting(self):
        """A real modal run this time (gr.screen set to a real Surface),
        driven to "cancel" by pre-posting a QUIT event -- proves
        execute_host_game_files_action's "cancel" branch actually calls
        _teardown, not just that the wiring compiles."""
        with tempfile.TemporaryDirectory() as tmp:
            pygame.display.set_mode((640, 480))
            room, gr, ex, ctrl = _make_side()
            gr.screen = pygame.display.get_surface()
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            _do(ex, "host_game_files", ctrl, {"folder": tmp, "show_lobby": True})
            st = peek_multiplayer_files(room)
            assert st is not None
            assert st.get("session") is None
            assert st.get("enabled") is False


class TestIdentity:
    def test_host_and_client_identity_globals(self):
        with tempfile.TemporaryDirectory() as tmp:
            host, client = _connect(tmp)
            try:
                hgr, cgr = host[1], client[1]
                assert hgr.global_variables["is_host"] == 1
                assert hgr.global_variables["player_id"] == 0
                assert cgr.global_variables["is_host"] == 0
                assert cgr.global_variables["player_id"] == 1
                assert cgr.global_variables["player_count"] == 0 or \
                    cgr.global_variables["player_count"] == 2
                assert hgr.global_variables["player_count"] == 2
                assert hgr.global_variables["round_number"] == 1
            finally:
                _close(host, client)

    def test_host_game_files_twice_is_a_no_op(self):
        with tempfile.TemporaryDirectory() as tmp:
            room, gr, ex, ctrl = _make_side()
            _do(ex, "host_game_files", ctrl, {"folder": tmp})
            first = peek_multiplayer_files(room)["session"]
            _do(ex, "host_game_files", ctrl, {"folder": tmp})
            assert peek_multiplayer_files(room)["session"] is first

    def test_host_game_files_without_a_folder_notifies_and_does_not_crash(self):
        room, gr, ex, ctrl = _make_side()
        _do(ex, "host_game_files", ctrl, {})     # no folder param at all
        assert peek_multiplayer_files(room) is None or \
            peek_multiplayer_files(room).get("session") is None


class TestSharedVars:
    def test_set_and_get_shared_var_round_trips_through_a_round(self):
        with tempfile.TemporaryDirectory() as tmp:
            host, client = _connect(tmp)
            try:
                hroom, hgr, hex_, hctrl = host
                croom, cgr, cex, cctrl = client
                _do(hex_, "set_shared_var_files", hctrl, {"name": "score", "value": "7"})
                _do(hex_, "end_turn", hctrl, {})
                _do(cex, "end_turn", cctrl, {})
                for _ in range(10):
                    _pump(hgr, cgr, rounds=1)
                    if cgr.global_variables.get("round_number") == 2:
                        break
                assert cgr.global_variables.get("score") == 7
                _do(cex, "get_shared_var_files", cctrl, {"name": "score", "into": "my_score"})
                assert cgr.global_variables.get("my_score") == 7
            finally:
                _close(host, client)


class TestEvents:
    def test_join_fires_player_joined_files_on_host_and_file_session_started_on_client(self):
        with tempfile.TemporaryDirectory() as tmp:
            host, client = _connect(tmp)
            try:
                _pump(host[1], client[1], rounds=5)
                assert "player_joined_files" in host[2].fired
                assert "file_session_started" in client[2].fired
                assert host[1].global_variables.get("network_sender") == 1
            finally:
                _close(host, client)

    def test_round_resolved_fires_on_both_machines(self):
        with tempfile.TemporaryDirectory() as tmp:
            host, client = _connect(tmp)
            try:
                hroom, hgr, hex_, hctrl = host
                croom, cgr, cex, cctrl = client
                _do(hex_, "end_turn", hctrl, {})
                _do(cex, "end_turn", cctrl, {})
                for _ in range(10):
                    _pump(hgr, cgr, rounds=1)
                    if cgr.global_variables.get("round_number") == 2:
                        break
                assert "round_resolved" in hex_.fired
                assert "round_resolved" in cex.fired
            finally:
                _close(host, client)

    def test_leave_game_files_clears_status_globals(self):
        with tempfile.TemporaryDirectory() as tmp:
            host, client = _connect(tmp)
            hroom, hgr, hex_, hctrl = host
            _do(hex_, "leave_game_files", hctrl, {})
            assert "player_id" not in hgr.global_variables
            assert "is_host" not in hgr.global_variables
            _close(client)


class TestNetworkMessage:
    def test_send_network_message_files_fires_on_both_machines_with_globals_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            host, client = _connect(tmp)
            try:
                hroom, hgr, hex_, hctrl = host
                croom, cgr, cex, cctrl = client
                _do(hex_, "send_network_message_files", hctrl,
                    {"event": "buzz", "data": "42", "target": "all"})
                _do(hex_, "end_turn", hctrl, {})
                _do(cex, "end_turn", cctrl, {})
                for _ in range(10):
                    _pump(hgr, cgr, rounds=1)
                    if cgr.global_variables.get("round_number") == 2:
                        break
                assert "network_message_files" in hex_.fired
                assert "network_message_files" in cex.fired
                assert cgr.global_variables.get("network_event") == "buzz"
                assert cgr.global_variables.get("network_data") == 42
                assert cgr.global_variables.get("network_sender") == 0
            finally:
                _close(host, client)

    def test_target_host_message_does_not_fire_on_the_client(self):
        with tempfile.TemporaryDirectory() as tmp:
            host, client = _connect(tmp)
            try:
                hroom, hgr, hex_, hctrl = host
                croom, cgr, cex, cctrl = client
                cex.fired.clear()
                _do(cex, "send_network_message_files", cctrl,
                    {"event": "whisper", "target": "host"})
                _do(hex_, "end_turn", hctrl, {})
                _do(cex, "end_turn", cctrl, {})
                for _ in range(10):
                    _pump(hgr, cgr, rounds=1)
                    if cgr.global_variables.get("round_number") == 2:
                        break
                assert "network_message_files" in hex_.fired
                assert "network_message_files" not in cex.fired
            finally:
                _close(host, client)


class TestRoomChangeMigration:
    def test_session_migrates_to_the_new_room_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            room, gr, ex, ctrl = _make_side()
            _do(ex, "host_game_files", ctrl, {"folder": tmp})
            session = peek_multiplayer_files(room)["session"]

            new_room = _Room()
            H._on_room_change(room, new_room)

            assert peek_multiplayer_files(new_room)["session"] is session
            assert peek_multiplayer_files(room) is None
            session.close()

    def test_a_room_with_no_session_is_a_no_op(self):
        room = _Room()
        new_room = _Room()
        H._on_room_change(room, new_room)   # must not raise
        assert peek_multiplayer_files(new_room) is None
