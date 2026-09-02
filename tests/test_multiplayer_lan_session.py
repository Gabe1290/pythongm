"""LAN multiplayer v2 -- NetworkSession loopback tests (Tier A).

docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 5.1: extensions/multiplayer_lan/
session.py. Real sockets over 127.0.0.1, no GameRunner -- the session is
GameRunner-agnostic, so it can be driven directly here (the engine glue
is Phase 5.2's handlers.py).
"""
import socket
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.multiplayer_lan.session import NetworkSession  # noqa: E402
from extensions.multiplayer_lan.state import MSG_HELLO, MSG_BYE  # noqa: E402


def _pump(*sessions, rounds=30, sleep=0.005):
    for _ in range(rounds):
        for s in sessions:
            s.pump_before_step()
            s.pump_after_update()
        time.sleep(sleep)


class _EventLog:
    """Accumulates a session's take_events() across pumps."""

    def __init__(self, session):
        self.session = session
        self.events = []

    def collect(self):
        self.events.extend(self.session.take_events())
        return self.events

    def names(self):
        return [e[0] for e in self.events]

    def find(self, name):
        return [e for e in self.events if e[0] == name]


def _connected_pair(**client_kw):
    host = NetworkSession(mode="host", port=0, player_name="Prof")
    host.start()
    client = NetworkSession(mode="client", host="127.0.0.1",
                            port=host.bound_port, player_name="Ada", **client_kw)
    client.start()
    hlog, clog = _EventLog(host), _EventLog(client)
    for _ in range(40):
        host.pump_before_step(); host.pump_after_update()
        client.pump_before_step(); client.pump_after_update()
        hlog.collect(); clog.collect()
        if host.player_count == 2 and client.player_id == 1:
            break
        time.sleep(0.005)
    return host, client, hlog, clog


class TestJoin:
    def test_client_gets_slot_1_and_host_sees_join(self):
        host, client, hlog, clog = _connected_pair()
        try:
            assert client.player_id == 1
            assert client.player_count == 2
            assert host.player_count == 2
            assert ("player_joined", 1, "Ada") in hlog.events
            assert "network_started" in clog.names()
            assert host.roster == [(0, "Prof"), (1, "Ada")]
        finally:
            client.close(); host.close()

    def test_second_client_gets_slot_2(self):
        host, c1, hlog, clog = _connected_pair()
        c2 = NetworkSession(mode="client", host="127.0.0.1",
                            port=host.bound_port, player_name="Bo")
        c2.start()
        c2log = _EventLog(c2)
        try:
            _pump(host, c1, c2, rounds=40)
            c2log.collect(); hlog.collect(); clog.collect()
            assert c2.player_id == 2
            assert host.player_count == 3
            # c1 was told about c2 joining
            assert ("player_joined", 2, "Bo") in clog.collect()
        finally:
            c1.close(); c2.close(); host.close()

    def test_game_full_is_refused(self):
        host = NetworkSession(mode="host", port=0, max_players=2)
        host.start()
        ok = NetworkSession(mode="client", host="127.0.0.1", port=host.bound_port)
        ok.start()
        _pump(host, ok, rounds=40)
        extra = NetworkSession(mode="client", host="127.0.0.1", port=host.bound_port)
        extra.start()
        try:
            _pump(host, ok, extra, rounds=40)
            assert ok.player_id == 1
            assert host.player_count == 2            # host + ok only
            assert extra.connection_lost is True
            assert "connection_lost" in [e[0] for e in extra.take_events()]
        finally:
            ok.close(); extra.close(); host.close()

    def test_protocol_version_mismatch_refused(self):
        host = NetworkSession(mode="host", port=0)
        host.start()
        raw = socket.create_connection(("127.0.0.1", host.bound_port))
        try:
            raw.sendall(b'{"t":"%s","name":"X","proto_ver":999}\n' % MSG_HELLO.encode())
            deadline = time.time() + 2.0
            got_bye = False
            buf = b""
            while time.time() < deadline and not got_bye:
                host.pump_before_step(); host.pump_after_update()
                raw.setblocking(False)
                try:
                    buf += raw.recv(4096)
                except BlockingIOError:
                    pass
                got_bye = MSG_BYE.encode() in buf
                time.sleep(0.01)
            assert got_bye
            assert host.player_count == 1
            assert host.roster == [(0, "Joueur")]
        finally:
            raw.close(); host.close()


class TestSharedVars:
    def test_host_write_reaches_client(self):
        host, client, _, _ = _connected_pair()
        try:
            host.set_shared("score", 5)
            _pump(host, client, rounds=20)
            assert client.get_shared("score") == 5
            assert client.shared["score"] == 5
        finally:
            client.close(); host.close()

    def test_client_write_reaches_host_and_echoes_back(self):
        host, client, _, _ = _connected_pair()
        c2 = NetworkSession(mode="client", host="127.0.0.1", port=host.bound_port)
        c2.start()
        try:
            _pump(host, client, c2, rounds=30)
            client.set_shared("choice", "B")
            _pump(host, client, c2, rounds=30)
            assert host.get_shared("choice") == "B"
            assert c2.get_shared("choice") == "B"
        finally:
            client.close(); c2.close(); host.close()

    def test_invalid_shared_name_ignored(self):
        host, client, _, _ = _connected_pair()
        try:
            host.set_shared("a+b", 1)
            host.set_shared("2bad", 2)
            _pump(host, client, rounds=10)
            assert "a+b" not in host.shared
            assert "2bad" not in host.shared
        finally:
            client.close(); host.close()

    def test_unserialisable_value_does_not_propagate_a_real_value(self):
        # sanitize_value({1,2,3}) -> None, and setting a shared var to None
        # is a no-op (absent stays absent) -- the client never sees a bogus
        # value like the string "set([1, 2, 3])".
        host, client, _, _ = _connected_pair()
        try:
            host.set_shared("weird", {1, 2, 3})       # a set
            _pump(host, client, rounds=20)
            assert "weird" not in host.shared
            assert client.get_shared("weird") is None
        finally:
            client.close(); host.close()


class TestMessages:
    def test_client_message_reaches_host_with_server_assigned_sender(self):
        host, client, hlog, _ = _connected_pair()
        try:
            client.send_message("buzz", {"n": 1})
            _pump(host, client, rounds=20)
            hlog.collect()
            msgs = hlog.find("network_message")
            assert ("network_message", "buzz", {"n": 1}, 1) in msgs
        finally:
            client.close(); host.close()

    def test_message_is_relayed_to_other_clients(self):
        host, c1, _, _ = _connected_pair()
        c2 = NetworkSession(mode="client", host="127.0.0.1", port=host.bound_port)
        c2.start()
        c2log = _EventLog(c2)
        try:
            _pump(host, c1, c2, rounds=30)
            c1.send_message("hello", "world")
            _pump(host, c1, c2, rounds=30)
            c2log.collect()
            assert ("network_message", "hello", "world", 1) in c2log.find("network_message")
        finally:
            c1.close(); c2.close(); host.close()

    def test_host_message_reaches_clients(self):
        host, client, hlog, clog = _connected_pair()
        try:
            host.send_message("go", 42)
            hlog.collect()
            assert ("network_message", "go", 42, 0) in hlog.find("network_message")
            _pump(host, client, rounds=20)
            clog.collect()
            assert ("network_message", "go", 42, 0) in clog.find("network_message")
        finally:
            client.close(); host.close()

    def test_target_host_is_not_relayed(self):
        host, c1, _, _ = _connected_pair()
        c2 = NetworkSession(mode="client", host="127.0.0.1", port=host.bound_port)
        c2.start()
        c2log = _EventLog(c2)
        try:
            _pump(host, c1, c2, rounds=30)
            c1.send_message("private", "x", target="host")
            _pump(host, c1, c2, rounds=30)
            c2log.collect()
            assert c2log.find("network_message") == []
        finally:
            c1.close(); c2.close(); host.close()


class TestLifecycle:
    def test_start_game_notifies_everyone(self):
        host, client, hlog, clog = _connected_pair()
        try:
            host.start_game()
            hlog.collect()
            assert host.started is True
            assert "network_game_started" in hlog.names()
            _pump(host, client, rounds=20)
            clog.collect()
            assert client.started is True
            assert "network_game_started" in clog.names()
        finally:
            client.close(); host.close()

    def test_client_leaving_fires_player_left_on_host(self):
        host, client, hlog, _ = _connected_pair()
        try:
            client.close()
            _pump(host, rounds=40)
            hlog.collect()
            assert ("player_left", 1, "Ada") in hlog.events
            assert host.player_count == 1
        finally:
            host.close()

    def test_host_going_away_fires_connection_lost_on_client(self):
        host, client, _, clog = _connected_pair()
        try:
            host.close()
            _pump(client, rounds=40)
            clog.collect()
            assert client.connection_lost is True
            assert "connection_lost" in clog.names()
        finally:
            client.close()

    def test_bad_mode_rejected(self):
        try:
            NetworkSession(mode="spectator")
            assert False, "should have raised"
        except ValueError:
            pass
