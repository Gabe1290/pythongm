#!/usr/bin/env python3
"""LAN server discovery -- a hand-rolled UDP beacon, no zeroconf dependency.

docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 6.1. A host broadcasts a tiny JSON
datagram once a second; clients listen and keep a short-lived server list.
This is **best-effort** -- broadcast can be filtered on a school LAN, and
Wi-Fi client isolation blocks it entirely -- so the built-in connect
screen always also offers manual IP entry. Discovery just saves typing
when it works.

The two worker classes each own one daemon thread and one UDP socket:

* ``DiscoveryBeacon`` -- host side. ``start()`` / ``stop()`` / ``update()``.
* ``DiscoveryListener`` -- client side. ``start()`` / ``stop()`` /
  ``servers()`` (the current list, entries older than the TTL pruned).

Both stop cleanly: the loop uses a 0.5 s socket timeout so it checks the
stop flag regularly rather than relying on a blocking ``recvfrom`` being
interrupted by ``close()`` (which is platform-flaky).
"""

import json
import socket
import threading
import time

from core.logger import get_logger
from .state import (
    BEACON_INTERVAL, DISCOVERY_MAGIC, DISCOVERY_PORT, DISCOVERY_TTL,
    sanitize_name,
)

logger = get_logger(__name__)

_LOOP_TIMEOUT = 0.5
_MAX_DATAGRAM = 512


def encode_beacon(name: str, port: int, players: int, max_players: int) -> bytes:
    return json.dumps({
        "m": DISCOVERY_MAGIC,
        "name": sanitize_name(name),
        "port": int(port),
        "players": int(players),
        "max": int(max_players),
    }, separators=(",", ":")).encode("utf-8")


def decode_beacon(data: bytes, from_ip: str):
    """Parse a received datagram into a server dict, or ``None`` if it isn't
    one of ours. Every field is clamped / sanitized -- this is untrusted
    input off the network."""
    if not data or len(data) > _MAX_DATAGRAM:
        return None
    try:
        obj = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(obj, dict) or obj.get("m") != DISCOVERY_MAGIC:
        return None
    try:
        port = int(obj.get("port", 0))
        players = max(0, int(obj.get("players", 0)))
        max_players = max(0, int(obj.get("max", 0)))
    except (TypeError, ValueError):
        return None
    if not (0 < port < 65536):
        return None
    return {
        "ip": from_ip,
        "port": port,
        "name": sanitize_name(obj.get("name")),
        "players": players,
        "max": max_players,
    }


class DiscoveryBeacon:
    """Host: broadcast our presence every ``BEACON_INTERVAL`` seconds."""

    def __init__(self, game_name: str, tcp_port: int, players: int = 1,
                 max_players: int = 8, *, target=None, interval: float = BEACON_INTERVAL):
        self.game_name = game_name
        self.tcp_port = int(tcp_port)
        self._players = int(players)
        self._max = int(max_players)
        self._target = target or ("255.255.255.255", DISCOVERY_PORT)
        self._interval = float(interval)
        self._sock = None
        self._thread = None
        self._stop = threading.Event()

    def start(self) -> None:
        if self._thread is not None:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except OSError:
            pass
        self._sock = sock
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="pygm-beacon", daemon=True)
        self._thread.start()

    def update(self, players: int = None, max_players: int = None) -> None:
        if players is not None:
            self._players = int(players)
        if max_players is not None:
            self._max = int(max_players)

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self._sock.sendto(
                    encode_beacon(self.game_name, self.tcp_port, self._players, self._max),
                    self._target)
            except OSError as exc:
                logger.debug("multiplayer: beacon send failed: %s", exc)
            self._stop.wait(self._interval)

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None


class DiscoveryListener:
    """Client: collect beacons into a server list, pruned by TTL."""

    def __init__(self, *, port: int = DISCOVERY_PORT, ttl: float = DISCOVERY_TTL):
        self.port = int(port)
        self.ttl = float(ttl)
        self._sock = None
        self._thread = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._servers = {}            # (ip, port) -> {..., "_seen": monotonic}
        self.bound_port = 0

    def start(self) -> None:
        if self._thread is not None:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        for opt in ("SO_REUSEPORT",):     # lets several clients on one box listen
            if hasattr(socket, opt):
                try:
                    sock.setsockopt(socket.SOL_SOCKET, getattr(socket, opt), 1)
                except OSError:
                    pass
        sock.bind(("", self.port))
        sock.settimeout(_LOOP_TIMEOUT)
        self.bound_port = sock.getsockname()[1]
        self._sock = sock
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="pygm-discovery", daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                data, addr = self._sock.recvfrom(_MAX_DATAGRAM)
            except socket.timeout:
                continue
            except OSError:
                break
            server = decode_beacon(data, addr[0])
            if server is None:
                continue
            key = (server["ip"], server["port"])
            server["_seen"] = time.monotonic()
            with self._lock:
                self._servers[key] = server

    def servers(self) -> list:
        """Current servers, newest first, entries older than ``ttl`` dropped."""
        now = time.monotonic()
        with self._lock:
            for key in [k for k, s in self._servers.items() if now - s["_seen"] > self.ttl]:
                del self._servers[key]
            out = sorted(self._servers.values(), key=lambda s: -s["_seen"])
        return [{k: v for k, v in s.items() if k != "_seen"} for s in out]

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
