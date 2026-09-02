"""LAN multiplayer v2 -- Tier A end to end (actions + events + GameRunner glue).

docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 5.2/5.3: the student-facing actions
(host_game / join_game / set_shared_var / get_shared_var /
send_network_message / start_networked_game / leave_game), the Réseau
PLUGIN_EVENTS, and handlers.py's frame-update glue that mirrors the session
into globals and fires the events.

Real 127.0.0.1 sockets; a light mock GameRunner/room/instance stack plus a
real ActionExecutor (so the action dispatch and execute_event paths are
the real ones).
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
import time
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

import extensions.multiplayer_lan.handlers as H  # noqa: E402
from extensions.multiplayer_lan.state import peek_multiplayer  # noqa: E402


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


def _make_side(listener_events=("network_message", "player_joined", "player_left",
                                "network_started", "network_game_started",
                                "connection_lost")):
    room = _Room()
    gr = _GR(room)
    ex = _RecordingExecutor(gr)
    load_all_plugins(ex)
    ctrl = _Inst()
    listener = _Inst(events={name: {"actions": []} for name in listener_events})
    ctrl.action_executor = ex
    listener.action_executor = ex
    room.instances = [ctrl, listener]
    return room, gr, ex, ctrl


def _do(ex, name, inst, params):
    inst.action_executor = ex
    return ex.action_handlers[name](inst, params)


def _pump(*grs, rounds=40, sleep=0.005):
    for _ in range(rounds):
        for gr in grs:
            H._frame_update_apply_inbound(gr)
            H._frame_update_broadcast(gr)
        time.sleep(sleep)


def _connect():
    hroom, hgr, hex_, hctrl = _make_side()
    _do(hex_, "host_game", hctrl, {"port": 0, "max_players": 8})
    session = peek_multiplayer(hroom)["session"]
    port = session.bound_port

    croom, cgr, cex, cctrl = _make_side()
    _do(cex, "join_game", cctrl, {"host": "127.0.0.1", "port": port})

    for _ in range(60):
        _pump(hgr, cgr, rounds=1)
        if cgr.global_variables.get("player_id", -1) == 1:
            break
    return (hroom, hgr, hex_, hctrl), (croom, cgr, cex, cctrl)


def _close(*sides):
    for room, gr, ex, ctrl in sides:
        try:
            _do(ex, "leave_game", ctrl, {})   # stops session + discovery beacon
        except Exception:
            st = peek_multiplayer(room)
            if st and st.get("session"):
                st["session"].close()


class TestRegistration:
    def test_actions_and_events_registered_after_plugin_load(self):
        load_all_plugins(ActionExecutor())
        for a in ("host_game", "join_game", "leave_game", "set_shared_var",
                  "get_shared_var", "send_network_message", "start_networked_game"):
            assert a in ACTION_TYPES, a
        for e in ("network_started", "player_joined", "player_left",
                  "network_message", "network_game_started", "connection_lost"):
            assert e in EVENT_TYPES, e

    def test_reseau_category(self):
        load_all_plugins(ActionExecutor())
        assert ACTION_TYPES["host_game"].category == "Réseau"
        assert EVENT_TYPES["player_joined"].category == "Réseau"


class TestIdentity:
    def test_host_and_client_identity_globals(self):
        host, client = _connect()
        try:
            hgr, cgr = host[1], client[1]
            assert hgr.global_variables["is_host"] == 1
            assert hgr.global_variables["is_client"] == 0
            assert hgr.global_variables["player_id"] == 0
            assert hgr.global_variables["network_role"] == "host"
            assert cgr.global_variables["is_host"] == 0
            assert cgr.global_variables["player_id"] == 1
            assert cgr.global_variables["player_count"] == 2
            assert hgr.global_variables["player_count"] == 2
            assert cgr.global_variables["network_connected"] == 1
        finally:
            _close(host, client)

    def test_host_game_twice_is_a_no_op(self):
        room, gr, ex, ctrl = _make_side()
        _do(ex, "host_game", ctrl, {"port": 0})
        first = peek_multiplayer(room)["session"]
        _do(ex, "host_game", ctrl, {"port": 0})
        assert peek_multiplayer(room)["session"] is first
        first.close()

    def test_set_network_mode_refuses_when_session_present(self):
        room, gr, ex, ctrl = _make_side()
        _do(ex, "host_game", ctrl, {"port": 0})
        _do(ex, "set_network_mode", ctrl, {"mode": "client", "host": "127.0.0.1"})
        st = peek_multiplayer(room)
        assert st["session"] is not None
        assert st["client"] is None
        st["session"].close()


class TestEvents:
    def test_join_fires_player_joined_on_host_and_network_started_on_client(self):
        host, client = _connect()
        try:
            _pump(host[1], client[1], rounds=20)
            assert "player_joined" in host[2].fired
            assert "network_started" in client[2].fired
            assert host[1].global_variables.get("network_sender") == 1
        finally:
            _close(host, client)

    def test_client_leaving_fires_player_left_on_host(self):
        host, client = _connect()
        try:
            peek_multiplayer(client[0])["session"].close()
            _pump(host[1], rounds=50)
            assert "player_left" in host[2].fired
            assert host[1].global_variables["player_count"] == 1
        finally:
            _close(host)

    def test_host_closing_fires_connection_lost_on_client(self):
        host, client = _connect()
        try:
            peek_multiplayer(host[0])["session"].close()
            _pump(client[1], rounds=50)
            assert "connection_lost" in client[2].fired
            assert client[1].global_variables["network_connected"] == 0
        finally:
            _close(client)

    def test_start_networked_game_fires_everywhere(self):
        host, client = _connect()
        try:
            _do(host[2], "start_networked_game", host[3], {})
            _pump(host[1], client[1], rounds=20)
            assert "network_game_started" in host[2].fired
            assert "network_game_started" in client[2].fired
        finally:
            _close(host, client)


class TestSharedVars:
    def test_host_set_shared_var_reaches_client_global(self):
        host, client = _connect()
        try:
            _do(host[2], "set_shared_var", host[3], {"name": "score", "value": "7"})
            # host mirrors its own write immediately
            assert host[1].global_variables["score"] == 7
            _pump(host[1], client[1], rounds=25)
            assert client[1].global_variables["score"] == 7
        finally:
            _close(host, client)

    def test_client_set_shared_var_reaches_host_global(self):
        host, client = _connect()
        try:
            _do(client[2], "set_shared_var", client[3], {"name": "choix", "value": "\"B\""})
            _pump(host[1], client[1], rounds=30)
            assert host[1].global_variables.get("choix") == "B"
            assert client[1].global_variables.get("choix") == "B"
        finally:
            _close(host, client)

    def test_get_shared_var_copies_into_named_global(self):
        host, client = _connect()
        try:
            _do(host[2], "set_shared_var", host[3], {"name": "lvl", "value": "3"})
            _pump(host[1], client[1], rounds=25)
            _do(client[2], "get_shared_var", client[3], {"name": "lvl", "into": "ma_copie"})
            assert client[1].global_variables["ma_copie"] == 3
        finally:
            _close(host, client)

    def test_invalid_shared_name_is_ignored(self):
        host, client = _connect()
        try:
            _do(host[2], "set_shared_var", host[3], {"name": "a b", "value": "1"})
            _pump(host[1], client[1], rounds=15)
            assert "a b" not in host[1].global_variables
        finally:
            _close(host, client)


class TestMessages:
    def test_client_message_fires_network_message_event_on_host(self):
        host, client = _connect()
        try:
            _do(client[2], "send_network_message", client[3],
                {"event": "buzz", "data": "42", "target": "all"})
            _pump(host[1], client[1], rounds=30)
            assert "network_message" in host[2].fired
            gv = host[1].global_variables
            assert gv["network_event"] == "buzz"
            assert gv["network_sender"] == 1
            assert str(gv["network_data"]) == "42"
        finally:
            _close(host, client)

    def test_host_message_fires_event_on_client(self):
        host, client = _connect()
        try:
            _do(host[2], "send_network_message", host[3],
                {"event": "go", "data": "", "target": "all"})
            _pump(host[1], client[1], rounds=30)
            assert "network_message" in client[2].fired
            assert client[1].global_variables["network_event"] == "go"
            assert client[1].global_variables["network_sender"] == 0
        finally:
            _close(host, client)


class TestLeave:
    def test_leave_game_clears_session_and_network_globals(self):
        host, client = _connect()
        try:
            _pump(host[1], client[1], rounds=15)
            assert "player_id" in client[1].global_variables
            _do(client[2], "leave_game", client[3], {})
            st = peek_multiplayer(client[0])
            assert st["session"] is None
            assert st["mode"] is None
            for key in ("player_id", "is_host", "network_role", "network_connected"):
                assert key not in client[1].global_variables
        finally:
            _close(host)


class TestV1PathUnaffected:
    def test_env_var_host_path_still_works_without_a_session(self, monkeypatch):
        monkeypatch.setenv(H.ENV_MODE, "host")
        monkeypatch.setenv(H.ENV_PORT, "0")
        room, gr, ex, ctrl = _make_side()
        H._frame_update_broadcast(gr)
        st = peek_multiplayer(room)
        assert st is not None
        assert st["session"] is None
        assert st["mode"] == "host"
        assert st["host"] is not None
        st["host"].close()
