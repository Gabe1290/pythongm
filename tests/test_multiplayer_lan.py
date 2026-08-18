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

from extensions.multiplayer_lan.network import NetworkHost, NetworkClient  # noqa: E402
from extensions.multiplayer_lan.state import (  # noqa: E402
    SNAPSHOT_MSG_TYPE, multiplayer_state, peek_multiplayer,
)
from extensions.multiplayer_lan.handlers import (  # noqa: E402
    ENV_MODE, ENV_PORT,
    _frame_update_apply_inbound, _frame_update_broadcast,
)


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
            "sync_ids_assigned": False,
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
