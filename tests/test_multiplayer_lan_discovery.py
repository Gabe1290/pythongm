"""LAN multiplayer v2 -- UDP server discovery (Phase 6.1).

extensions/multiplayer_lan/discovery.py. Codec tests are pure; the
beacon/listener integration uses a directed datagram to 127.0.0.1 (real
broadcast isn't exercised in CI).
"""
import socket
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.multiplayer_lan.discovery import (  # noqa: E402
    DiscoveryBeacon, DiscoveryListener, decode_beacon, encode_beacon,
)
from extensions.multiplayer_lan.state import DISCOVERY_MAGIC  # noqa: E402


class TestBeaconCodec:
    def test_round_trip(self):
        raw = encode_beacon("Quiz de classe", 45782, 3, 8)
        got = decode_beacon(raw, "10.0.0.7")
        assert got == {"ip": "10.0.0.7", "port": 45782,
                       "name": "Quiz de classe", "players": 3, "max": 8}

    def test_name_is_sanitised(self):
        raw = encode_beacon("Bad\nName\x00", 45782, 1, 2)
        assert decode_beacon(raw, "1.2.3.4")["name"] == "BadName"

    def test_rejects_non_magic(self):
        assert decode_beacon(b'{"m":"something-else","port":1}', "1.2.3.4") is None

    def test_rejects_garbage(self):
        for bad in (b"", b"not json", b"[1,2,3]", b'"a string"', b"\xff\xfe"):
            assert decode_beacon(bad, "1.2.3.4") is None

    def test_rejects_bad_port(self):
        assert decode_beacon(
            ('{"m":"%s","port":0,"name":"x","players":1,"max":2}' % DISCOVERY_MAGIC).encode(),
            "1.2.3.4") is None
        assert decode_beacon(
            ('{"m":"%s","port":99999,"name":"x","players":1,"max":2}' % DISCOVERY_MAGIC).encode(),
            "1.2.3.4") is None

    def test_negative_counts_clamped(self):
        raw = ('{"m":"%s","port":45782,"name":"x","players":-5,"max":-1}'
               % DISCOVERY_MAGIC).encode()
        got = decode_beacon(raw, "1.2.3.4")
        assert got["players"] == 0 and got["max"] == 0

    def test_oversized_datagram_rejected(self):
        assert decode_beacon(b"x" * 4096, "1.2.3.4") is None


class TestListenerDirect:
    """Feed the listener a directed datagram (no broadcast)."""

    def _send(self, port, raw):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(raw, ("127.0.0.1", port))
        s.close()

    def test_listener_collects_a_server(self):
        listener = DiscoveryListener(port=0, ttl=5.0)
        listener.start()
        try:
            self._send(listener.bound_port, encode_beacon("Salle", 45782, 2, 6))
            deadline = time.time() + 2.0
            while time.time() < deadline and not listener.servers():
                time.sleep(0.02)
            servers = listener.servers()
            assert len(servers) == 1
            assert servers[0]["name"] == "Salle"
            assert servers[0]["port"] == 45782
            assert servers[0]["players"] == 2
            assert "_seen" not in servers[0]
        finally:
            listener.stop()

    def test_entry_is_pruned_after_ttl(self):
        listener = DiscoveryListener(port=0, ttl=0.3)
        listener.start()
        try:
            self._send(listener.bound_port, encode_beacon("Éphémère", 45782, 1, 2))
            deadline = time.time() + 2.0
            while time.time() < deadline and not listener.servers():
                time.sleep(0.02)
            assert listener.servers()
            time.sleep(0.5)
            assert listener.servers() == []
        finally:
            listener.stop()

    def test_garbage_datagram_is_ignored(self):
        listener = DiscoveryListener(port=0, ttl=5.0)
        listener.start()
        try:
            self._send(listener.bound_port, b"totally not a beacon")
            time.sleep(0.2)
            assert listener.servers() == []
        finally:
            listener.stop()


class TestBeaconListenerIntegration:
    def test_beacon_reaches_listener(self):
        listener = DiscoveryListener(port=0, ttl=5.0)
        listener.start()
        beacon = DiscoveryBeacon(
            "Récolte en équipe", 45782, players=1, max_players=4,
            target=("127.0.0.1", listener.bound_port), interval=0.1)
        beacon.start()
        try:
            deadline = time.time() + 3.0
            while time.time() < deadline and not listener.servers():
                time.sleep(0.05)
            servers = listener.servers()
            assert servers and servers[0]["name"] == "Récolte en équipe"

            beacon.update(players=3)
            deadline = time.time() + 3.0
            while time.time() < deadline and listener.servers()[0]["players"] != 3:
                time.sleep(0.05)
            assert listener.servers()[0]["players"] == 3
        finally:
            beacon.stop()
            listener.stop()

    def test_stop_is_clean_and_idempotent(self):
        beacon = DiscoveryBeacon("x", 1, target=("127.0.0.1", 45999), interval=0.05)
        beacon.start()
        time.sleep(0.15)
        beacon.stop()
        beacon.stop()                       # must not raise
        listener = DiscoveryListener(port=0)
        listener.start()
        listener.stop()
        listener.stop()
