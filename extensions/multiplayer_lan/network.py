#!/usr/bin/env python3
"""TCP transport for LAN multiplayer -- the actual rewrite of what
``runtime/network/`` used to be before its untracked source was deleted
(see docs/MULTIPLAYER_LAN_PLAN.md for the full history).

Design decisions this file makes, per the plan doc's own recommendations:
  - **TCP, not UDP.** Position snapshots are small and infrequent (one per
    frame, a handful of instances) -- head-of-line blocking is unlikely to
    matter at LAN scale, and TCP avoids writing packet-loss/reordering
    handling from scratch for a first cut.
  - **Multi-client from day one**, even though a first playtest only
    exercises one client -- broadcasting to a list of sockets instead of a
    single one costs nothing extra now and avoids a bigger retrofit later.
  - **JSON lines, newline-delimited**, over the raw TCP stream. Not the
    most bandwidth-efficient framing available, but this was never
    bandwidth-constrained, and it stays trivially debuggable (readable in
    a packet capture, a log, or by hand).

``NetworkClient.poll()`` is called once per frame from inside the game
loop's ``before_step`` frame-update hook -- it must NEVER block waiting on
the socket, or every client frame stalls on network I/O. Non-blocking
sockets throughout; a "no data yet" condition is expected and silent, not
an error.
"""

import json
import socket
from typing import List, Optional, Sequence, Tuple

from .state import DEFAULT_PORT, SNAPSHOT_MSG_TYPE

# Snapshot rows: (sync_id, x, y, rotation, image_index, visible)
SnapshotRow = Tuple[int, float, float, float, float, bool]


def _encode(rows: Sequence[SnapshotRow]) -> bytes:
    msg = {"t": SNAPSHOT_MSG_TYPE, "i": [list(row) for row in rows]}
    return (json.dumps(msg, separators=(",", ":")) + "\n").encode("utf-8")


class NetworkHost:
    """Authoritative side: listens for client connections, broadcasts
    position snapshots to all of them. Never reads from clients in this
    first cut -- host state is authoritative, clients are pure observers
    (see docs/MULTIPLAYER_LAN_PLAN.md's "Explicitly out of scope": no
    server-side input validation/anti-cheat, no clients sending state back)."""

    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self._listen_sock: Optional[socket.socket] = None
        self._clients: List[socket.socket] = []

    def start(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", self.port))
        sock.listen(8)
        sock.setblocking(False)
        self._listen_sock = sock

    def _accept_pending(self) -> None:
        """Accept any client connections waiting, without blocking. Called
        internally before every broadcast so new players can join
        mid-game, not just at startup."""
        if self._listen_sock is None:
            return
        while True:
            try:
                conn, _addr = self._listen_sock.accept()
            except BlockingIOError:
                return
            except OSError:
                return
            conn.setblocking(True)
            conn.settimeout(0.2)  # bound how long a stalled client can hang a broadcast
            self._clients.append(conn)

    def broadcast_snapshot(self, rows: Sequence[SnapshotRow]) -> None:
        """Send the current snapshot to every connected client. A client
        that fails to receive it (disconnected, timed out) is dropped
        silently -- a departed player must not crash the host."""
        self._accept_pending()
        if not self._clients:
            return
        payload = _encode(rows)
        surviving = []
        for conn in self._clients:
            try:
                conn.sendall(payload)
                surviving.append(conn)
            except OSError:
                try:
                    conn.close()
                except OSError:
                    pass
        self._clients = surviving

    def close(self) -> None:
        for conn in self._clients:
            try:
                conn.close()
            except OSError:
                pass
        self._clients = []
        if self._listen_sock is not None:
            try:
                self._listen_sock.close()
            except OSError:
                pass
            self._listen_sock = None


class NetworkClient:
    """Observer side: connects to a host, polls for the latest snapshot."""

    def __init__(self, host: str, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self._sock: Optional[socket.socket] = None
        self._buffer = b""

    def connect(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)          # a bounded wait for the initial handshake only
        sock.connect((self.host, self.port))
        sock.setblocking(False)       # every subsequent read is via poll(), never blocking
        self._sock = sock

    def poll(self) -> Optional[dict]:
        """Drain whatever is available on the socket and return the LATEST
        complete message, or None if nothing new arrived. Never blocks --
        a socket with nothing to read is the normal, silent case, not an
        error, since this runs once per frame."""
        if self._sock is None:
            return None
        try:
            while True:
                chunk = self._sock.recv(65536)
                if not chunk:
                    # Peer closed the connection -- stop trying to read it.
                    self._sock = None
                    break
                self._buffer += chunk
        except BlockingIOError:
            pass
        except OSError:
            self._sock = None

        if b"\n" not in self._buffer:
            return None

        # Keep only the LAST complete line -- stale snapshots from earlier
        # frames don't matter once a newer one has arrived (this is
        # deliberately a "latest state wins" protocol, not a reliable
        # ordered stream the app needs every message from).
        lines = self._buffer.split(b"\n")
        self._buffer = lines[-1]     # partial trailing data, if any
        complete_lines = [line for line in lines[:-1] if line]
        if not complete_lines:
            return None

        try:
            return json.loads(complete_lines[-1].decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
