"""LAN multiplayer v2 -- Tier B ghost replication (Phase 5.4b).

docs/MULTIPLAYER_LAN_V2_PLAN.md: network_spawn on the host creates a real
instance that shows up on every client as an interpolated "ghost". Two
REAL GameRunner instances over the shipped multiplayer_lan_1 project,
talking over a real 127.0.0.1 socket, driven a frame at a time through the
extension_hooks -- the pattern from
tests/test_multiplayer_lan_1_sample.py's networked smoke.
"""
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from events.plugin_loader import load_all_plugins  # noqa: E402
from runtime.action_executor import ActionExecutor  # noqa: E402
from runtime import extension_hooks  # noqa: E402
from extensions.multiplayer_lan.state import peek_multiplayer  # noqa: E402
import extensions.multiplayer_lan.handlers as mp_handlers  # noqa: E402


def _loaded_handlers():
    """The handlers module actually behind the registered frame-update
    hooks -- the loader imports the extension under a synthetic package
    name, so that's a different module object from the one imported the
    normal way above (see CLAUDE.md's raycast note)."""
    import sys
    for func, _phase in extension_hooks.get_frame_updates():
        if getattr(func, "__name__", "") == "_frame_update_broadcast":
            return sys.modules[func.__module__]
    return mp_handlers

PROJECT_JSON = str(REPO_ROOT / "samples" / "multiplayer_lan_1" / "project.json")


def _init(runner):
    assert runner.load_project_data_only(PROJECT_JSON)
    start = runner.find_starting_room()
    runner.current_room = runner.rooms[start]
    runner._visited_rooms.add(start)


def _controller(runner):
    inst = runner.current_room.instances[0]
    inst.action_executor = runner.action_executor
    return inst


def _do(runner, name, params):
    inst = _controller(runner)
    return runner.action_executor.action_handlers[name](inst, params)


def _tick(*runners):
    for r in runners:
        extension_hooks.run_frame_updates(r, "before_step")
    for r in runners:
        extension_hooks.run_frame_updates(r, "after_update")


def _make_pair():
    from runtime.game_runner import GameRunner

    host = GameRunner(PROJECT_JSON)
    host.language = "en"
    _init(host)
    _do(host, "host_game", {"port": 0, "max_players": 8})
    port = peek_multiplayer(host.current_room)["session"].bound_port

    client = GameRunner(PROJECT_JSON)
    client.language = "en"
    _init(client)
    _do(client, "join_game", {"host": "127.0.0.1", "port": port})

    for _ in range(60):
        _tick(host, client)
        time.sleep(0.01)
        if client.global_variables.get("player_id", -1) == 1:
            break
    return host, client


def _teardown(*runners):
    for r in runners:
        try:
            _do(r, "leave_game", {})       # stops session + discovery beacon/listener
        except Exception:
            st = peek_multiplayer(r.current_room)
            if st and st.get("session"):
                st["session"].close()
    extension_hooks.clear_frame_updates()
    load_all_plugins(ActionExecutor())     # restore real hooks for later tests


def _ghosts(runner):
    return [i for i in runner.current_room.instances
            if getattr(i, "_net_ghost", None) is not None]


class TestGhostReplication:
    def test_network_spawn_creates_a_ghost_on_the_client(self):
        host, client = _make_pair()
        try:
            assert client.global_variables["player_id"] == 1
            _do(host, "network_spawn", {"object": "obj_player", "x": "140", "y": "150"})

            deadline = time.time() + 3.0
            while time.time() < deadline and not _ghosts(client):
                _tick(host, client)
                time.sleep(0.02)

            ghosts = _ghosts(client)
            assert len(ghosts) == 1
            g = ghosts[0]
            assert g.object_name == "obj_player"
            # position converges toward the host's spawn point (interpolated)
            for _ in range(30):
                _tick(host, client)
                time.sleep(0.02)
            assert abs(g.x - 140) < 5
            assert abs(g.y - 150) < 5
        finally:
            _teardown(host, client)

    def test_ghost_follows_the_host_instance_moving(self):
        host, client = _make_pair()
        try:
            _do(host, "network_spawn", {"object": "obj_player", "x": "50", "y": "50"})
            for _ in range(20):
                _tick(host, client)
                time.sleep(0.02)
            ghost = _ghosts(client)[0]

            st = peek_multiplayer(host.current_room)
            host_inst = next(iter(st["synced"].values()))
            host_inst.x = 400.0
            host_inst.y = 220.0

            deadline = time.time() + 3.0
            while time.time() < deadline and abs(ghost.x - 400) > 5:
                _tick(host, client)
                time.sleep(0.02)
            assert abs(ghost.x - 400) < 5
            assert abs(ghost.y - 220) < 5
        finally:
            _teardown(host, client)

    def test_destroying_the_host_instance_removes_the_ghost(self):
        host, client = _make_pair()
        try:
            _do(host, "network_spawn", {"object": "obj_player", "x": "60", "y": "60"})
            for _ in range(25):
                _tick(host, client)
                time.sleep(0.02)
            assert len(_ghosts(client)) == 1

            st = peek_multiplayer(host.current_room)
            host_inst = next(iter(st["synced"].values()))
            host_inst.to_destroy = True
            host.current_room.instances = [
                i for i in host.current_room.instances if not getattr(i, "to_destroy", False)]

            deadline = time.time() + 3.0
            while time.time() < deadline and _ghosts(client):
                _tick(host, client)
                time.sleep(0.02)
            assert _ghosts(client) == [] or all(
                getattr(g, "to_destroy", False) for g in _ghosts(client))
        finally:
            _teardown(host, client)

    def test_network_spawn_is_a_no_op_on_a_client(self):
        host, client = _make_pair()
        try:
            before = len(client.current_room.instances)
            _do(client, "network_spawn", {"object": "obj_player", "x": "10", "y": "10"})
            _tick(host, client)
            assert len(client.current_room.instances) == before
            st = peek_multiplayer(client.current_room)
            assert not st.get("synced")
        finally:
            _teardown(host, client)

    def test_ghost_create_event_is_suppressed(self):
        host, client = _make_pair()
        try:
            _do(host, "network_spawn", {"object": "obj_player", "x": "70", "y": "70"})
            for _ in range(25):
                _tick(host, client)
                time.sleep(0.02)
            g = _ghosts(client)[0]
            assert getattr(g, "_create_fired", False) is True
        finally:
            _teardown(host, client)

    def test_set_sync_rate_action_tunes_the_session(self):
        host, client = _make_pair()
        try:
            _do(host, "set_sync_rate", {"hz": "30", "interp_ms": "50"})
            _do(client, "set_sync_rate", {"hz": "30", "interp_ms": "50"})
            hs = peek_multiplayer(host.current_room)["session"]
            cs = peek_multiplayer(client.current_room)["session"]
            assert hs._snap_every == 2
            assert cs.interp_delay == 0.05
        finally:
            _teardown(host, client)


def _player(runner):
    return next(i for i in runner.current_room.instances
               if i.object_name == "obj_player")


class TestSyncInstanceAndOwnership:
    def test_deterministic_netid_matches_across_machines(self):
        host, client = _make_pair()
        try:
            _do(host, "sync_instance", {"vars": ""})
            _do(client, "sync_instance", {"vars": ""})
            _tick(host, client)
            assert _player(host)._net_id == "obj_player#0"
            assert _player(client)._net_id == "obj_player#0"
        finally:
            _teardown(host, client)

    def test_host_owned_synced_room_instance_drives_the_client_copy(self):
        host, client = _make_pair()
        try:
            _do(host, "sync_instance", {"vars": ""})       # owner defaults to host (0)
            _do(client, "sync_instance", {"vars": ""})
            for _ in range(15):
                _tick(host, client); time.sleep(0.02)

            _player(host).x = 480.0
            _player(host).y = 90.0
            deadline = time.time() + 3.0
            while time.time() < deadline and abs(_player(client).x - 480) > 5:
                _tick(host, client); time.sleep(0.02)
            assert abs(_player(client).x - 480) < 5
            assert abs(_player(client).y - 90) < 5
        finally:
            _teardown(host, client)

    def test_client_owned_instance_drives_the_host_copy(self):
        host, client = _make_pair()
        try:
            _do(host, "sync_instance", {"vars": ""})
            _do(host, "set_instance_owner", {"player": "1"})   # host hands slot 1 the avatar
            _do(client, "sync_instance", {"vars": ""})

            deadline = time.time() + 3.0
            while time.time() < deadline and getattr(_player(client), "_net_owner", 0) != 1:
                _tick(host, client); time.sleep(0.02)
            assert _player(client)._net_owner == 1

            _player(client).x = 250.0
            _player(client).y = 175.0
            deadline = time.time() + 3.0
            while time.time() < deadline and abs(_player(host).x - 250) > 5:
                _tick(host, client); time.sleep(0.02)
            assert abs(_player(host).x - 250) < 5
            assert abs(_player(host).y - 175) < 5
        finally:
            _teardown(host, client)

    def test_is_instance_owner_condition(self):
        host, client = _make_pair()
        try:
            _do(host, "sync_instance", {"vars": ""})
            _do(host, "set_instance_owner", {"player": "1"})
            _do(client, "sync_instance", {"vars": ""})
            deadline = time.time() + 3.0
            while time.time() < deadline and getattr(_player(client), "_net_owner", 0) != 1:
                _tick(host, client); time.sleep(0.02)

            h = host.action_executor.action_handlers["is_instance_owner"]
            c = client.action_executor.action_handlers["is_instance_owner"]
            assert c(_player(client), {}) is True
            assert h(_player(host), {}) is False
        finally:
            _teardown(host, client)

    def test_client_cannot_grab_an_instance_the_host_owns(self):
        host, client = _make_pair()
        try:
            _do(host, "sync_instance", {"vars": ""})          # host keeps ownership (0)
            _do(client, "sync_instance", {"vars": ""})
            _do(client, "set_instance_owner", {"player": "1"})  # client *claims* it -- must be refused
            for _ in range(15):
                _tick(host, client); time.sleep(0.02)

            host_x = _player(host).x
            _player(client).x = 999.0
            for _ in range(20):
                _tick(host, client); time.sleep(0.02)
            # the host's copy did not jump to the client's forged position
            assert abs(_player(host).x - host_x) < 20
            assert _player(host).x != 999.0
        finally:
            _teardown(host, client)

    def test_synced_vars_replicate(self):
        host, client = _make_pair()
        try:
            hp = _player(host)
            hp.hp = 7
            _do(host, "sync_instance", {"vars": "hp"})
            _do(client, "sync_instance", {"vars": "hp"})
            deadline = time.time() + 3.0
            while time.time() < deadline and getattr(_player(client), "hp", None) != 7:
                _tick(host, client); time.sleep(0.02)
            assert _player(client).hp == 7
        finally:
            _teardown(host, client)


class TestNamedInput:
    def test_default_inputs_are_bound(self):
        host, client = _make_pair()
        try:
            _tick(host, client)
            binds = peek_multiplayer(client.current_room)["input_binds"]
            for name in ("left", "right", "up", "down", "space"):
                assert name in binds and binds[name] is not None
        finally:
            _teardown(host, client)

    def test_bind_network_input_writes_a_binding(self):
        host, client = _make_pair()
        try:
            _do(client, "bind_network_input", {"name": "jump", "key": "space"})
            assert peek_multiplayer(client.current_room)["input_binds"]["jump"] == pygame.K_SPACE
        finally:
            _teardown(host, client)

    def test_client_input_reaches_host_via_remote_input(self, monkeypatch):
        host, client = _make_pair()
        try:
            hs = peek_multiplayer(host.current_room)["session"]
            # simulate the client holding jump + left (the real
            # _poll_held_inputs reads pygame's keyboard, unavailable headless)
            monkeypatch.setattr(_loaded_handlers(), "_poll_held_inputs",
                                lambda st: {"jump", "left"})
            for _ in range(15):
                _tick(host, client); time.sleep(0.02)
            assert hs.remote_input(1, "jump") is True
            assert hs.remote_input(1, "left") is True
            assert hs.remote_input(1, "fire") is False
            assert hs.remote_input(2, "jump") is False

            monkeypatch.setattr(_loaded_handlers(), "_poll_held_inputs", lambda st: set())
            for _ in range(15):
                _tick(host, client); time.sleep(0.02)
            assert hs.remote_input(1, "jump") is False
        finally:
            _teardown(host, client)

    def test_remote_input_action_reads_host_state(self, monkeypatch):
        host, client = _make_pair()
        try:
            monkeypatch.setattr(_loaded_handlers(), "_poll_held_inputs", lambda st: {"jump"})
            for _ in range(15):
                _tick(host, client); time.sleep(0.02)
            act = host.action_executor.action_handlers["remote_input"]
            assert act(_player(host), {"player": "1", "name": "jump"}) is True
            assert act(_player(host), {"player": "1", "name": "nope"}) is False
        finally:
            _teardown(host, client)

    def test_host_own_input_is_player_zero(self):
        host, client = _make_pair()
        try:
            hs = peek_multiplayer(host.current_room)["session"]
            hs.set_local_input(["up", "space"])
            assert hs.remote_input(0, "up") is True
            assert hs.remote_input(0, "down") is False
        finally:
            _teardown(host, client)

    def test_input_send_is_deduped(self):
        host, client = _make_pair()
        try:
            cs = peek_multiplayer(client.current_room)["session"]
            cs.send_input(["a"])
            assert cs._last_input_sent == frozenset(["a"])
            cs.send_input(["a"])                   # unchanged -> no-op, must not raise
            assert cs._last_input_sent == frozenset(["a"])
        finally:
            _teardown(host, client)


class TestConnectFlow:
    def test_host_game_starts_and_stops_a_discovery_beacon(self):
        from runtime.game_runner import GameRunner
        host = GameRunner(PROJECT_JSON)
        host.language = "en"
        _init(host)
        try:
            _do(host, "host_game", {"port": 0})
            beacon = peek_multiplayer(host.current_room)["beacon"]
            assert beacon is not None and beacon._thread is not None
            _do(host, "leave_game", {})
            assert peek_multiplayer(host.current_room)["beacon"] is None
            assert beacon._thread is None
        finally:
            _teardown(host)

    def test_join_auto_headless_connects_to_loopback(self):
        from runtime.game_runner import GameRunner
        host = GameRunner(PROJECT_JSON); host.language = "en"; _init(host)
        _do(host, "host_game", {"port": 0})
        port = peek_multiplayer(host.current_room)["session"].bound_port

        client = GameRunner(PROJECT_JSON); client.language = "en"; _init(client)
        try:
            _do(client, "join_game", {"host": "auto", "port": port})
            deadline = time.time() + 3.0
            while time.time() < deadline and client.global_variables.get("player_id", -1) != 1:
                _tick(host, client); time.sleep(0.02)
            assert client.global_variables["player_id"] == 1
        finally:
            _teardown(host, client)

    def test_join_auto_cancel_leaves_no_session(self, monkeypatch):
        from runtime.game_runner import GameRunner
        client = GameRunner(PROJECT_JSON); client.language = "en"; _init(client)
        try:
            monkeypatch.setattr(_loaded_handlers(), "_run_connect_flow",
                                lambda *a, **k: "cancel")
            _do(client, "join_game", {"host": "auto", "port": 45999})
            st = peek_multiplayer(client.current_room)
            assert st is None or st.get("session") is None
        finally:
            _teardown(client)

    def test_host_show_lobby_start(self, monkeypatch):
        from runtime.game_runner import GameRunner
        host = GameRunner(PROJECT_JSON); host.language = "en"; _init(host)
        try:
            monkeypatch.setattr(_loaded_handlers(), "_run_connect_flow",
                                lambda *a, **k: "start")
            _do(host, "host_game", {"port": 0, "show_lobby": True})
            session = peek_multiplayer(host.current_room)["session"]
            assert session is not None and session.started is True
        finally:
            _teardown(host)

    def test_host_show_lobby_cancel_tears_down(self, monkeypatch):
        from runtime.game_runner import GameRunner
        host = GameRunner(PROJECT_JSON); host.language = "en"; _init(host)
        try:
            monkeypatch.setattr(_loaded_handlers(), "_run_connect_flow",
                                lambda *a, **k: "cancel")
            _do(host, "host_game", {"port": 0, "show_lobby": True})
            st = peek_multiplayer(host.current_room)
            assert st.get("session") is None
            assert st.get("beacon") is None
        finally:
            _teardown(host)


class TestEnvAutoStart:
    def test_autohost_env_starts_a_v2_host_session(self, monkeypatch):
        from runtime.game_runner import GameRunner
        monkeypatch.setenv("PYGM_NET_AUTOHOST", "1")
        monkeypatch.setenv("PYGM_NET_PORT", "0")
        monkeypatch.delenv("PYGM_NET_AUTOJOIN", raising=False)
        monkeypatch.delenv("PYGM_NET_MODE", raising=False)
        host = GameRunner(PROJECT_JSON); host.language = "en"; _init(host)
        try:
            _tick(host)
            st = peek_multiplayer(host.current_room)
            assert st is not None and st["session"] is not None
            assert st["session"].mode == "host"
        finally:
            _teardown(host)

    def test_autojoin_env_connects_as_v2_client(self, monkeypatch):
        from runtime.game_runner import GameRunner
        monkeypatch.setenv("PYGM_NET_AUTOHOST", "1")
        monkeypatch.setenv("PYGM_NET_PORT", "0")
        monkeypatch.delenv("PYGM_NET_AUTOJOIN", raising=False)
        monkeypatch.delenv("PYGM_NET_MODE", raising=False)
        host = GameRunner(PROJECT_JSON); host.language = "en"; _init(host)
        _tick(host)
        port = peek_multiplayer(host.current_room)["session"].bound_port

        monkeypatch.delenv("PYGM_NET_AUTOHOST", raising=False)
        monkeypatch.setenv("PYGM_NET_AUTOJOIN", "127.0.0.1")
        monkeypatch.setenv("PYGM_NET_PORT", str(port))
        client = GameRunner(PROJECT_JSON); client.language = "en"; _init(client)
        try:
            deadline = time.time() + 3.0
            while time.time() < deadline and client.global_variables.get("player_id", -1) != 1:
                _tick(host, client); time.sleep(0.02)
            assert client.global_variables["player_id"] == 1
        finally:
            _teardown(host, client)


class TestCaption:
    def test_host_and_client_captions_reflect_the_session(self):
        host, client = _make_pair()
        try:
            for _ in range(20):
                _tick(host, client); time.sleep(0.02)
            assert "Hôte" in host.window_caption
            assert "2 joueurs" in host.window_caption
            assert "Client" in client.window_caption
            assert "connecté" in client.window_caption
        finally:
            _teardown(host, client)

    def test_caption_is_restored_on_leave(self):
        from runtime.game_runner import GameRunner
        host = GameRunner(PROJECT_JSON); host.language = "en"; _init(host)
        host.window_caption = "Mon jeu"
        try:
            _do(host, "host_game", {"port": 0})
            _tick(host)
            assert "Hôte" in host.window_caption
            assert host.window_caption.startswith("Mon jeu")
            _do(host, "leave_game", {})
            assert host.window_caption == "Mon jeu"
        finally:
            _teardown(host)


class TestConnectionLostTeardown:
    """Phase 8.6: connection_lost already fired the event and zeroed
    network_connected (Phase 5.2); this closes the other half -- a lost
    host will never send another snapshot, so a client's ghost puppets
    must not just freeze forever."""

    def test_losing_the_host_destroys_client_ghosts(self):
        host, client = _make_pair()
        try:
            _do(host, "network_spawn", {"object": "obj_player", "x": "140", "y": "150"})
            deadline = time.time() + 3.0
            while time.time() < deadline and not _ghosts(client):
                _tick(host, client)
                time.sleep(0.02)
            assert len(_ghosts(client)) == 1

            # Simulate the host vanishing: kill the client's own transport
            # socket directly, rather than tearing down the host GameRunner
            # (which would also stop responding to the host's own ticks and
            # complicate cleanup) -- the client-side effect is identical
            # either way, since NetworkClient._fail() (a dead/closed peer)
            # is exactly what this reproduces.
            client_session = peek_multiplayer(client.current_room)["session"]
            client_session._client.close()

            def _live_ghosts():
                return [g for g in _ghosts(client) if not getattr(g, "to_destroy", False)]

            deadline = time.time() + 3.0
            while time.time() < deadline and _live_ghosts():
                _tick(client)
                time.sleep(0.02)

            assert client.global_variables.get("network_connected") == 0
            # _tick() only runs the frame-update hooks, not a full engine
            # step, so a destroyed instance isn't necessarily pruned from
            # room.instances yet -- to_destroy=True is what actually
            # matters (matches test_destroying_the_host_instance_removes_
            # the_ghost's own assertion shape above).
            assert _live_ghosts() == []
            st = peek_multiplayer(client.current_room)
            assert st["ghosts"] == {}
        finally:
            _teardown(host, client)

    def test_connection_lost_does_not_destroy_the_clients_own_avatar(self):
        """The client's locally-owned avatar (synced_local) keeps running
        after the host disappears -- matching this repo's "the game
        continues single-player" precedent elsewhere in this extension."""
        host, client = _make_pair()
        try:
            for _ in range(5):
                _tick(host, client)
                time.sleep(0.01)
            st = peek_multiplayer(client.current_room)
            synced_local_before = dict(st.get("synced_local") or {})

            client_session = peek_multiplayer(client.current_room)["session"]
            client_session._client.close()

            deadline = time.time() + 3.0
            while (time.time() < deadline
                   and client.global_variables.get("network_connected") != 0):
                _tick(client)
                time.sleep(0.02)

            assert client.global_variables.get("network_connected") == 0
            st_after = peek_multiplayer(client.current_room)
            for nid, inst in synced_local_before.items():
                assert not getattr(inst, "to_destroy", False)
                assert st_after["synced_local"].get(nid) is inst
        finally:
            _teardown(host, client)

    def test_connection_lost_fires_the_event_exactly_once(self):
        host, client = _make_pair()
        mod = _loaded_handlers()
        orig_fire = mod._fire_network_event
        fired = []
        def spy(room, event_name):
            if event_name == "connection_lost":
                fired.append(1)
            return orig_fire(room, event_name)
        mod._fire_network_event = spy
        try:
            client_session = peek_multiplayer(client.current_room)["session"]
            client_session._client.close()

            deadline = time.time() + 3.0
            while time.time() < deadline and not fired:
                _tick(client)
                time.sleep(0.02)
            assert len(fired) == 1

            for _ in range(20):
                _tick(client)
                time.sleep(0.01)
            assert len(fired) == 1  # not re-fired every subsequent frame
        finally:
            mod._fire_network_event = orig_fire
            _teardown(host, client)
