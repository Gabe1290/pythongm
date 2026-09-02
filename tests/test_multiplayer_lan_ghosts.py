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
