"""LAN multiplayer extension (docs/MULTIPLAYER_LAN_PLAN.md, Phases 1-2).

The plan's own "Suggested sequencing" pulls the Phase 3 loopback test
forward to land with Phase 1 rather than waiting: "a loopback test
spinning up a real NetworkHost and NetworkClient against 127.0.0.1 in
the same test process ... confirming a broadcast snapshot round-trips
and poll() returns it" -- that's TestNetworkLoopback below, plus a
stronger end-to-end test that goes through the real action handler and
frame-update hooks, not just the raw transport.

Four tiers: pure state.py unit tests, real-socket network.py loopback
tests (127.0.0.1, port 0 so the OS picks a free ephemeral port -- no
fixed-port collisions between parallel test runs), the set_network_mode
action dispatched via the established MockGameRunner/MockRoom
action_executor pattern (tests/test_raycast_view.py's
_raycast_executor/_dispatch), and an end-to-end test that drives a
"host" and a "client" side purely through _frame_update_broadcast/
_frame_update_apply_inbound -- the exact functions the real game loop
calls every frame via runtime/extension_hooks.py.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import socket
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
from runtime.action_executor import ActionExecutor  # noqa: E402

from extensions.multiplayer_lan.network import (  # noqa: E402
    NetworkHost, NetworkClient, CONN_OPENED, CONN_CLOSED, _HostConn,
)
from extensions.multiplayer_lan.state import (  # noqa: E402
    SNAPSHOT_MSG_TYPE, MAX_FRAME_BYTES, multiplayer_state, peek_multiplayer,
)
from extensions.multiplayer_lan.handlers import (  # noqa: E402
    ENV_MODE, ENV_PORT,
    _frame_update_apply_inbound, _frame_update_broadcast,
)
import extensions.multiplayer_lan.handlers as mp_handlers  # noqa: E402


# ---------------------------------------------------------------------------
# Shared fixtures/helpers
# ---------------------------------------------------------------------------

class MockInstance:
    def __init__(self, object_name="obj_player"):
        self.object_name = object_name
        self.action_executor = None
        self.x = 0.0
        self.y = 0.0
        self.rotation = 0.0
        self.image_index = 0.0
        self.visible = True


class MockRoom:
    def __init__(self):
        self.instances = []
        self.extension_state = {}


class MockGameRunner:
    def __init__(self, room=None):
        self.current_room = room if room is not None else MockRoom()
        self.global_variables = {}


def _executor(game_runner=None):
    ex = ActionExecutor(game_runner=game_runner)
    load_all_plugins(ex)
    return ex


def _dispatch(executor, action_name, instance, params):
    instance.action_executor = executor
    return executor.action_handlers[action_name](instance, params)


# ---------------------------------------------------------------------------
# state.py: pure unit tests
# ---------------------------------------------------------------------------

class TestState:
    def test_peek_before_create_returns_none(self):
        room = MockRoom()
        assert peek_multiplayer(room) is None

    def test_fresh_state_shape(self):
        room = MockRoom()
        st = multiplayer_state(room)
        assert st == {
            "enabled": False, "mode": None, "host": None, "client": None,
            "session": None, "sync_ids_assigned": False,
        }

    def test_state_is_cached_per_room(self):
        room = MockRoom()
        st1 = multiplayer_state(room)
        st1["mode"] = "host"
        st2 = multiplayer_state(room)
        assert st2 is st1
        assert peek_multiplayer(room) is st1

    def test_two_rooms_get_independent_state(self):
        room_a, room_b = MockRoom(), MockRoom()
        multiplayer_state(room_a)["mode"] = "host"
        assert peek_multiplayer(room_b) is None


# ---------------------------------------------------------------------------
# network.py: real sockets over 127.0.0.1
# ---------------------------------------------------------------------------

def _bound_port(host: NetworkHost) -> int:
    return host._listen_sock.getsockname()[1]


class TestNetworkLoopback:
    def test_broadcast_snapshot_round_trips_to_client(self):
        host = NetworkHost(port=0)
        host.start()
        client = NetworkClient("127.0.0.1", port=_bound_port(host))
        client.connect()
        try:
            rows = [(0, 10.0, 20.0, 0.0, 1.0, True), (1, -5.0, 3.5, 90.0, 0.0, False)]
            msg = None
            deadline = time.time() + 2.0
            while time.time() < deadline and msg is None:
                host.broadcast_snapshot(rows)
                time.sleep(0.02)
                msg = client.poll()

            assert msg is not None
            assert msg["t"] == SNAPSHOT_MSG_TYPE
            assert msg["i"] == [list(r) for r in rows]
        finally:
            client.close()
            host.close()

    def test_multiple_clients_all_receive_the_broadcast(self):
        host = NetworkHost(port=0)
        host.start()
        port = _bound_port(host)
        client_a = NetworkClient("127.0.0.1", port=port)
        client_b = NetworkClient("127.0.0.1", port=port)
        client_a.connect()
        client_b.connect()
        try:
            rows = [(0, 1.0, 2.0, 0.0, 0.0, True)]
            msg_a = msg_b = None
            deadline = time.time() + 2.0
            while time.time() < deadline and (msg_a is None or msg_b is None):
                host.broadcast_snapshot(rows)
                time.sleep(0.02)
                msg_a = msg_a or client_a.poll()
                msg_b = msg_b or client_b.poll()

            assert msg_a is not None and msg_a["i"] == [list(rows[0])]
            assert msg_b is not None and msg_b["i"] == [list(rows[0])]
        finally:
            client_a.close()
            client_b.close()
            host.close()

    def test_client_poll_returns_none_when_nothing_was_sent(self):
        host = NetworkHost(port=0)
        host.start()
        client = NetworkClient("127.0.0.1", port=_bound_port(host))
        client.connect()
        try:
            time.sleep(0.05)
            assert client.poll() is None
        finally:
            client.close()
            host.close()

    def test_a_disconnected_host_does_not_crash_client_poll(self):
        host = NetworkHost(port=0)
        host.start()
        client = NetworkClient("127.0.0.1", port=_bound_port(host))
        client.connect()
        try:
            host.broadcast_snapshot([])  # forces the pending accept
            time.sleep(0.05)
            host.close()
            time.sleep(0.05)
            client.poll()  # must not raise
        finally:
            client.close()


class _FailingSocket:
    """A duck-typed socket standing in for a real one whose peer vanished
    mid-write (cable pulled, Wi-Fi client isolation, the peer process
    killed) -- send() raises exactly like a real dead socket's would."""

    def send(self, data):
        raise OSError("simulated send failure")

    def close(self):
        pass


class TestSendPathConnectionLoss:
    """H3, docs/FULL_AUDIT_2026-09-07.md: NetworkHost.send()/broadcast()
    used to pass _flush_conn a throwaway `[]` for its events list, so a
    connection killed by a failed WRITE (as opposed to a failed read, which
    poll() itself surfaces) never produced a CONN_CLOSED event at all --
    session.py's _drop_conn (player_left, player_count, roster cleanup)
    was never told, leaving a permanent phantom player.

    Uses a real NetworkHost with one real accepted connection swapped for
    a fake failing socket, rather than real network fault injection --
    deterministic, no timing/flakiness, and exercises the exact code path
    (_flush_conn's OSError branch) the finding is about.
    """

    def _host_with_dead_conn(self):
        host = NetworkHost(port=0)
        host.start()
        conn = _HostConn(_FailingSocket(), ("127.0.0.1", 0))
        host._conns[1] = conn
        return host

    def test_broadcast_send_failure_surfaces_conn_closed_on_next_poll(self):
        host = NetworkHost(port=0)
        host.start()
        try:
            conn = _HostConn(_FailingSocket(), ("127.0.0.1", 0))
            host._conns[1] = conn

            host.broadcast({"t": "x"})  # send fails -> _kill -> used to be lost
            assert conn.alive is False, "the connection must be marked dead immediately"

            events = host.poll()
            closed = [e for e in events if e[1].get("t") == CONN_CLOSED]
            assert closed, (
                "poll() must return the CONN_CLOSED event from a "
                "broadcast()-path failure, or session.py never sees the "
                "player leave")
            assert closed[0][0] == 1
        finally:
            host.close()

    def test_send_failure_surfaces_conn_closed_on_next_poll(self):
        host = NetworkHost(port=0)
        host.start()
        try:
            conn = _HostConn(_FailingSocket(), ("127.0.0.1", 0))
            host._conns[7] = conn

            host.send(7, {"t": "x"})
            assert conn.alive is False

            events = host.poll()
            closed = [e for e in events if e[1].get("t") == CONN_CLOSED]
            assert closed, (
                "poll() must return the CONN_CLOSED event from a "
                "send()-path failure")
            assert closed[0][0] == 7
        finally:
            host.close()

    def test_pending_events_do_not_duplicate_or_leak_across_polls(self):
        """A pending CONN_CLOSED must be returned exactly once, and a poll
        with nothing pending must not keep re-returning stale events."""
        host = NetworkHost(port=0)
        host.start()
        try:
            conn = _HostConn(_FailingSocket(), ("127.0.0.1", 0))
            host._conns[3] = conn
            host.broadcast({"t": "x"})

            first = host.poll()
            assert sum(1 for e in first if e[1].get("t") == CONN_CLOSED) == 1

            second = host.poll()
            assert not any(e[1].get("t") == CONN_CLOSED for e in second), (
                "a already-delivered CONN_CLOSED must not repeat on the "
                "next poll()")
        finally:
            host.close()


# ---------------------------------------------------------------------------
# H4, docs/FULL_AUDIT_2026-09-07.md: replicated state/vars hardening
# ---------------------------------------------------------------------------

class TestReplicatedVarKeyHardening:
    """The two helper functions the fix introduces: an engine-attribute
    denylist built from a real GameInstance (not hand-maintained), and a
    finite-float coercion for numeric wire fields."""

    def test_engine_attrs_include_known_internals(self):
        attrs = mp_handlers._engine_instance_attrs()
        for name in ("object_data", "action_executor", "sprite",
                     "keys_pressed", "x", "y"):
            assert name in attrs, name

    def test_is_safe_replicated_var_key(self):
        assert mp_handlers._is_safe_replicated_var_key("hp") is True
        assert mp_handlers._is_safe_replicated_var_key("score_bonus") is True
        for bad in ("object_data", "action_executor", "sprite", "x", "y",
                    "_private", "123bad", "", None, 42):
            assert mp_handlers._is_safe_replicated_var_key(bad) is False, bad

    def test_coerce_finite_float(self):
        assert mp_handlers._coerce_finite_float("5.5", 0) == 5.5
        assert mp_handlers._coerce_finite_float(3, 0) == 3.0
        for bad in ("pwned", [1, 2], {"a": 1}, None,
                    float("nan"), float("inf"), float("-inf")):
            assert mp_handlers._coerce_finite_float(bad, 99) == 99, bad


class _FakeOwnStateSession:
    """Minimal stand-in for NetworkSession, exposing only what
    _apply_host_own_state calls."""

    def __init__(self, rows):
        self._rows = rows

    def take_own_state(self):
        rows, self._rows = self._rows, {}
        return rows


class TestApplyHostOwnStateHardening:
    """Client -> host direction: a malicious/buggy client's "own" report
    for an instance it legitimately owns must not crash the host or
    clobber engine-internal attributes."""

    @staticmethod
    def _inst(owner=1):
        inst = MockInstance()
        inst._net_owner = owner
        inst.object_data = {"events": {}}
        return inst

    def test_non_numeric_position_does_not_crash_and_falls_back(self):
        inst = self._inst()
        st = {"synced": {1: inst}}
        session = _FakeOwnStateSession({
            1: {"_from": 1, "x": "pwned", "y": ["also", "bad"],
                "r": {"nested": True}, "f": None, "v": 1},
        })
        mp_handlers._apply_host_own_state(st, session)  # must not raise
        assert inst.x == 0.0 and isinstance(inst.x, float)
        assert inst.y == 0.0 and isinstance(inst.y, float)
        assert inst.rotation == 0.0
        assert inst.image_index == 0.0

    def test_legit_numeric_row_still_applies(self):
        inst = self._inst()
        st = {"synced": {1: inst}}
        session = _FakeOwnStateSession({
            1: {"_from": 1, "x": 12.5, "y": -3, "r": 90, "f": 2, "v": 0},
        })
        mp_handlers._apply_host_own_state(st, session)
        assert inst.x == 12.5
        assert inst.y == -3.0
        assert inst.rotation == 90.0
        assert inst.image_index == 2.0
        assert inst.visible is False

    def test_engine_attribute_key_in_vars_is_refused(self):
        inst = self._inst()
        st = {"synced": {1: inst}}
        session = _FakeOwnStateSession({
            1: {"_from": 1, "x": 0, "y": 0,
                "vars": {"object_data": "pwned", "action_executor": "pwned"}},
        })
        mp_handlers._apply_host_own_state(st, session)  # must not raise
        assert inst.object_data == {"events": {}}
        assert inst.action_executor is None

    def test_ordinary_game_variable_key_is_applied(self):
        inst = self._inst()
        st = {"synced": {1: inst}}
        session = _FakeOwnStateSession({
            1: {"_from": 1, "x": 0, "y": 0, "vars": {"hp": 42, "flag": True}},
        })
        mp_handlers._apply_host_own_state(st, session)
        assert inst.hp == 42
        assert inst.flag is True

    def test_wrong_owner_is_ignored_entirely(self):
        inst = self._inst(owner=1)
        st = {"synced": {1: inst}}
        session = _FakeOwnStateSession({
            1: {"_from": 2, "x": 999, "y": 999},  # claimed by the wrong client
        })
        mp_handlers._apply_host_own_state(st, session)
        assert inst.x == 0.0 and inst.y == 0.0  # untouched


class _FakeGhostSession:
    """Minimal stand-in for NetworkSession, exposing only what
    _apply_ghosts/_apply_synced_local call."""

    def __init__(self, owner_map, pos_map, vars_map, player_id=0,
                 ghost_changes=((), ())):
        self.player_id = player_id
        self._owner_map = owner_map
        self._pos_map = pos_map
        self._vars_map = vars_map
        self._ghost_changes = ghost_changes

    def take_ghost_changes(self):
        return self._ghost_changes

    def ghost_owner(self, nid):
        return self._owner_map.get(nid)

    def sample_ghost(self, nid):
        return self._pos_map.get(nid)

    def ghost_vars(self, nid):
        return self._vars_map.get(nid, {})


class TestApplyGhostsHardening:
    """Host -> client direction (_apply_ghosts): same class of hardening,
    defence in depth against a compromised/buggy host."""

    def test_malicious_ghost_vars_key_is_refused(self):
        inst = MockInstance()
        inst.object_data = {"events": {}}
        inst.to_destroy = False
        room = MockRoom()
        runner = MockGameRunner(room)
        st = {"ghosts": {1: inst}}
        session = _FakeGhostSession(
            owner_map={1: None},          # not this player's -> stays a ghost
            pos_map={1: (5.0, 6.0, 0.0, 0.0, True)},
            vars_map={1: {"action_executor": "pwned", "score": 3}},
        )
        mp_handlers._apply_ghosts(runner, st, session)
        assert inst.action_executor is None
        assert inst.score == 3
        assert inst.x == 5.0 and inst.y == 6.0


class TestApplySyncedLocalHardening:
    """Host -> client direction (_apply_synced_local): same hardening for
    an author-registered sync_instance the local player doesn't own."""

    def test_malicious_ghost_vars_key_is_refused(self):
        inst = MockInstance()
        inst.object_data = {"events": {}}
        inst.to_destroy = False
        room = MockRoom()
        room.instances = [inst]
        runner = MockGameRunner(room)
        st = {"synced_local": {1: inst}}
        session = _FakeGhostSession(
            owner_map={1: 5},             # owned by a different player
            pos_map={1: (10.0, 20.0, 0.0, 0.0, True)},
            vars_map={1: {"object_data": "pwned", "hp": 7}},
            player_id=0,
        )
        mp_handlers._apply_synced_local(runner, st, session)
        assert inst.object_data == {"events": {}}
        assert inst.hp == 7
        assert inst.x == 10.0 and inst.y == 20.0

    def test_non_numeric_ghost_position_does_not_crash(self):
        inst = MockInstance()
        inst.object_data = {"events": {}}
        inst.to_destroy = False
        room = MockRoom()
        room.instances = [inst]
        runner = MockGameRunner(room)
        st = {"synced_local": {1: inst}}
        session = _FakeGhostSession(
            owner_map={1: 5},
            pos_map={1: ("bad", None, [1], {}, 1)},
            vars_map={1: {}},
            player_id=0,
        )
        mp_handlers._apply_synced_local(runner, st, session)  # must not raise
        assert inst.x == 0.0 and inst.y == 0.0


# ---------------------------------------------------------------------------
# set_network_mode action
# ---------------------------------------------------------------------------

class TestSetNetworkModeAction:
    def test_action_is_registered(self):
        load_all_plugins(ActionExecutor())
        assert "set_network_mode" in ACTION_TYPES

    def test_host_mode_starts_a_listening_socket(self):
        room = MockRoom()
        executor = _executor(MockGameRunner(room))
        caller = MockInstance()

        _dispatch(executor, "set_network_mode", caller, {"mode": "host", "port": 0})

        st = peek_multiplayer(room)
        assert st is not None
        assert st["mode"] == "host"
        assert st["enabled"] is True
        assert st["host"] is not None
        st["host"].close()

    def test_invalid_mode_is_a_no_op(self):
        room = MockRoom()
        executor = _executor(MockGameRunner(room))
        caller = MockInstance()

        _dispatch(executor, "set_network_mode", caller, {"mode": "bogus"})

        assert peek_multiplayer(room) is None

    def test_calling_twice_does_not_reconnect(self):
        room = MockRoom()
        executor = _executor(MockGameRunner(room))
        caller = MockInstance()

        _dispatch(executor, "set_network_mode", caller, {"mode": "host", "port": 0})
        first_host = peek_multiplayer(room)["host"]
        _dispatch(executor, "set_network_mode", caller, {"mode": "host", "port": 0})
        second_host = peek_multiplayer(room)["host"]

        assert first_host is second_host
        first_host.close()

    def test_assigns_deterministic_sync_ids_to_room_instances(self):
        room = MockRoom()
        inst_a, inst_b = MockInstance(), MockInstance()
        room.instances = [inst_a, inst_b]
        executor = _executor(MockGameRunner(room))
        caller = MockInstance()

        _dispatch(executor, "set_network_mode", caller, {"mode": "host", "port": 0})

        assert inst_a._sync_id == 0
        assert inst_b._sync_id == 1
        peek_multiplayer(room)["host"].close()


# ---------------------------------------------------------------------------
# Env-var fallback (run_game.py's --net-host/--net-client CLI flags)
# ---------------------------------------------------------------------------

class TestEnvVarFallback:
    def test_frame_updates_auto_init_host_from_env_vars(self, monkeypatch):
        monkeypatch.setenv(ENV_MODE, "host")
        monkeypatch.setenv(ENV_PORT, "0")
        room = MockRoom()
        gr = MockGameRunner(room)

        _frame_update_broadcast(gr)

        st = peek_multiplayer(room)
        assert st is not None
        assert st["mode"] == "host"
        st["host"].close()

    def test_no_env_var_is_a_silent_no_op(self, monkeypatch):
        monkeypatch.delenv(ENV_MODE, raising=False)
        room = MockRoom()
        gr = MockGameRunner(room)

        _frame_update_apply_inbound(gr)  # must not raise or create state
        _frame_update_broadcast(gr)

        assert peek_multiplayer(room) is None

    def test_unrecognized_mode_value_is_ignored(self, monkeypatch):
        monkeypatch.setenv(ENV_MODE, "sideways")
        room = MockRoom()
        gr = MockGameRunner(room)

        _frame_update_broadcast(gr)

        assert peek_multiplayer(room) is None


# ---------------------------------------------------------------------------
# End-to-end: real sockets, driven purely through the frame-update hooks
# (the exact functions runtime/extension_hooks.py calls every frame)
# ---------------------------------------------------------------------------

class TestEndToEndSync:
    def test_client_instance_picks_up_the_hosts_moved_position(self):
        host_room = MockRoom()
        host_inst = MockInstance()
        host_room.instances = [host_inst]
        host_gr = MockGameRunner(host_room)
        host_executor = _executor(host_gr)
        _dispatch(host_executor, "set_network_mode", MockInstance(),
                  {"mode": "host", "port": 0})
        host_state = peek_multiplayer(host_room)
        port = _bound_port(host_state["host"])

        client_room = MockRoom()
        client_inst = MockInstance()
        client_room.instances = [client_inst]
        client_gr = MockGameRunner(client_room)
        client_executor = _executor(client_gr)
        _dispatch(client_executor, "set_network_mode", MockInstance(),
                  {"mode": "client", "host": "127.0.0.1", "port": port})

        try:
            host_inst.x, host_inst.y, host_inst.rotation = 42.0, 17.0, 90.0
            host_inst.visible = False

            deadline = time.time() + 2.0
            while time.time() < deadline and client_inst.x != 42.0:
                _frame_update_broadcast(host_gr)
                time.sleep(0.02)
                _frame_update_apply_inbound(client_gr)

            assert client_inst.x == 42.0
            assert client_inst.y == 17.0
            assert client_inst.rotation == 90.0
            assert client_inst.visible is False
        finally:
            peek_multiplayer(host_room)["host"].close()
            peek_multiplayer(client_room)["client"].close()

    def test_host_side_never_applies_inbound(self):
        # A host has no NetworkClient, so calling the client-side hook on a
        # host room must be a harmless no-op, not an AttributeError.
        room = MockRoom()
        executor = _executor(MockGameRunner(room))
        _dispatch(executor, "set_network_mode", MockInstance(),
                  {"mode": "host", "port": 0})

        _frame_update_apply_inbound(MockGameRunner(room))  # must not raise

        peek_multiplayer(room)["host"].close()


# ---------------------------------------------------------------------------
# v2 bidirectional transport (docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 4.2b)
# ---------------------------------------------------------------------------

def _pump_until(fn, predicate, timeout=2.0):
    """Call fn() repeatedly (with a short sleep) until predicate(result) is
    truthy or the timeout expires. Returns the last result."""
    deadline = time.time() + timeout
    result = fn()
    while time.time() < deadline and not predicate(result):
        time.sleep(0.02)
        result = fn()
    return result


class TestBidirectionalTransport:
    def test_host_poll_reports_connection_open_with_addr(self):
        host = NetworkHost(port=0)
        host.start()
        port = host._listen_sock.getsockname()[1]
        client = NetworkClient("127.0.0.1", port=port)
        client.connect()
        try:
            events = _pump_until(
                host.poll,
                lambda evs: any(f.get("t") == CONN_OPENED for _, f in evs))
            opened = [(cid, f) for cid, f in events if f.get("t") == CONN_OPENED]
            assert len(opened) == 1
            assert opened[0][1]["addr"] == "127.0.0.1"
            assert host.connection_ids == [opened[0][0]]
        finally:
            client.close()
            host.close()

    def test_client_send_reaches_host_tagged_with_conn_id(self):
        host = NetworkHost(port=0)
        host.start()
        client = NetworkClient("127.0.0.1", port=host._listen_sock.getsockname()[1])
        client.connect()
        try:
            client.send({"t": "hello", "name": "Amélie"})
            hellos = []
            deadline = time.time() + 2.0
            while time.time() < deadline and not hellos:
                for cid, f in host.poll():
                    if f.get("t") == "hello":
                        hellos.append((cid, f))
                time.sleep(0.02)
            assert len(hellos) == 1
            assert hellos[0][1]["name"] == "Amélie"
            assert hellos[0][0] in host.connection_ids
        finally:
            client.close()
            host.close()

    def test_host_send_reaches_one_client_via_take_frames(self):
        host = NetworkHost(port=0)
        host.start()
        client = NetworkClient("127.0.0.1", port=host._listen_sock.getsockname()[1])
        client.connect()
        try:
            evs = _pump_until(host.poll,
                              lambda e: any(f.get("t") == CONN_OPENED for _, f in e))
            cid = next(c for c, f in evs if f.get("t") == CONN_OPENED)

            host.send(cid, {"t": "welcome", "player_id": 3})
            frames = _pump_until(client.take_frames,
                                 lambda fr: any(f.get("t") == "welcome" for f in fr))
            welcomes = [f for f in frames if f.get("t") == "welcome"]
            assert welcomes and welcomes[0]["player_id"] == 3
        finally:
            client.close()
            host.close()

    def test_broadcast_can_exclude_one_client(self):
        host = NetworkHost(port=0)
        host.start()
        port = host._listen_sock.getsockname()[1]
        a = NetworkClient("127.0.0.1", port=port)
        b = NetworkClient("127.0.0.1", port=port)
        a.connect()
        b.connect()
        try:
            evs = _pump_until(host.poll,
                              lambda e: len([1 for _, f in e if f.get("t") == CONN_OPENED]) >= 2)
            opened = [c for c, f in evs if f.get("t") == CONN_OPENED]
            assert len(opened) == 2
            cid_a = opened[0]

            host.broadcast({"t": "msg", "event": "ping"}, exclude=cid_a)
            host.poll()
            b_frames = _pump_until(b.take_frames,
                                   lambda fr: any(f.get("t") == "msg" for f in fr))
            assert any(f.get("t") == "msg" for f in b_frames)

            time.sleep(0.1)
            a_frames = a.take_frames()
            assert not any(f.get("t") == "msg" for f in a_frames)
        finally:
            a.close()
            b.close()
            host.close()

    def test_oversize_inbound_with_no_terminator_drops_the_client(self):
        host = NetworkHost(port=0)
        host.start()
        port = host._listen_sock.getsockname()[1]
        raw = socket.create_connection(("127.0.0.1", port))
        try:
            evs = _pump_until(host.poll,
                              lambda e: any(f.get("t") == CONN_OPENED for _, f in e))
            cid = next(c for c, f in evs if f.get("t") == CONN_OPENED)
            assert cid in host.connection_ids

            raw.sendall(b"x" * (MAX_FRAME_BYTES + 64))  # no newline -> FrameOverflow

            closed = _pump_until(
                host.poll,
                lambda e: any(f.get("t") == CONN_CLOSED for _, f in e))
            reasons = [f.get("reason") for _, f in closed if f.get("t") == CONN_CLOSED]
            assert "frame overflow" in reasons
            assert cid not in host.connection_ids
        finally:
            raw.close()
            host.close()

    def test_inbound_frame_rate_is_bounded(self):
        host = NetworkHost(port=0)
        host.start()
        port = host._listen_sock.getsockname()[1]
        raw = socket.create_connection(("127.0.0.1", port))
        try:
            _pump_until(host.poll,
                        lambda e: any(f.get("t") == CONN_OPENED for _, f in e))
            # 400 valid frames in one shot -- the token bucket must let only
            # a bounded burst through, not all 400.
            blob = b"".join(b'{"t":"input","n":%d}\n' % i for i in range(400))
            raw.sendall(blob)

            received = []
            deadline = time.time() + 1.0
            while time.time() < deadline:
                for _, f in host.poll():
                    if f.get("t") == "input":
                        received.append(f)
                time.sleep(0.02)

            assert 0 < len(received) < 400
        finally:
            raw.close()
            host.close()
