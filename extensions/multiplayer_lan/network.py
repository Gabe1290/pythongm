#!/usr/bin/env python3
"""TCP transport for LAN multiplayer.

v1 (docs/MULTIPLAYER_LAN_PLAN.md) shipped this one-directional: the host
broadcast snapshots and never read from a client. v2
(docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 4.2b) makes it bidirectional and
framed on ``framing.py`` -- a client sends intent (hello / input /
shared_set / msg / own / bye) up, the host reads it and can reply to one
client or broadcast to all. The v1 surface is preserved exactly
(``NetworkHost.start`` / ``.broadcast_snapshot`` / ``.close`` / the
``._listen_sock`` attribute; ``NetworkClient.connect`` / ``.poll`` ->
latest-snapshot-or-None / ``.close``) so the shipped spectator sample and
its tests are untouched; the new methods sit alongside for the Phase 5
session layer to build on.

Design decisions, unchanged from v1:
  - **TCP, not UDP.** Frames are small and infrequent; head-of-line
    blocking is a non-issue at LAN scale and TCP saves writing
    reliability from scratch.
  - **JSON lines, newline-delimited** over the stream -- readable in a
    capture; bandwidth was never the constraint.
  - **Never block.** Both sides are pumped once per frame from the game
    loop's frame-update hooks. Non-blocking sockets throughout; "no data
    yet" is the normal silent case. Outbound that can't be written
    immediately is queued and retried next pump; a peer that falls far
    enough behind on reads is dropped.
"""

import socket
from typing import Optional

from core.logger import get_logger
from .framing import FrameBuffer, FrameOverflow, RateLimiter, encode_frame
from .state import DEFAULT_PORT, MSG_SNAP

logger = get_logger(__name__)

# Synthetic frames NetworkHost.poll() emits for connection lifecycle. The
# "__" prefix cannot collide with a real MSG_* wire value.
CONN_OPENED = "__open__"
CONN_CLOSED = "__close__"

# A client whose queued-but-unwritten output passes this is too far behind
# to keep -- drop it rather than let the host's memory grow unbounded.
_MAX_OUTBUF_BYTES = 262144

_RECV_CHUNK = 65536


class _HostConn:
    """One accepted client, from the host's side."""

    __slots__ = ("sock", "addr", "buf", "limiter", "outbuf", "alive")

    def __init__(self, sock: socket.socket, addr):
        self.sock = sock
        self.addr = addr
        self.buf = FrameBuffer()
        self.limiter = RateLimiter()
        self.outbuf = bytearray()
        self.alive = True


class NetworkHost:
    """Authoritative side: listens, accepts clients, reads their frames,
    sends to one or all. ``poll()`` is the single pump -- accept, read,
    flush -- and returns everything that arrived this pump."""

    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self._listen_sock: Optional[socket.socket] = None
        self._conns = {}                 # conn_id -> _HostConn
        self._next_id = 1

    # -- lifecycle -------------------------------------------------------

    def start(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", self.port))
        sock.listen(16)
        sock.setblocking(False)
        self._listen_sock = sock

    def close(self) -> None:
        for conn in self._conns.values():
            try:
                conn.sock.close()
            except OSError:
                pass
        self._conns.clear()
        if self._listen_sock is not None:
            try:
                self._listen_sock.close()
            except OSError:
                pass
            self._listen_sock = None

    @property
    def connection_ids(self) -> list:
        """Live connection ids, in accept order."""
        return [cid for cid, c in self._conns.items() if c.alive]

    # -- pump ----------------------------------------------------------

    def poll(self) -> list:
        """Accept pending connections, drain each client, flush queued
        output. Returns ``[(conn_id, frame), ...]`` -- real inbound frames
        plus synthetic ``{"t": "__open__", "addr": ip}`` /
        ``{"t": "__close__", "reason": str}`` lifecycle frames, in the
        order they happened. Never blocks."""
        events: list = []
        self._accept(events)
        for cid, conn in list(self._conns.items()):
            if conn.alive:
                self._read_conn(cid, conn, events)
        for cid, conn in list(self._conns.items()):
            if conn.alive and conn.outbuf:
                self._flush_conn(cid, conn, events)
        for cid in [c for c, k in self._conns.items() if not k.alive]:
            self._conns.pop(cid, None)
        return events

    def _accept(self, events: list) -> None:
        if self._listen_sock is None:
            return
        while True:
            try:
                sock, addr = self._listen_sock.accept()
            except BlockingIOError:
                return
            except OSError:
                return
            sock.setblocking(False)
            cid = self._next_id
            self._next_id += 1
            self._conns[cid] = _HostConn(sock, addr)
            events.append((cid, {"t": CONN_OPENED, "addr": addr[0] if addr else ""}))

    def _read_conn(self, cid: int, conn: _HostConn, events: list) -> None:
        try:
            while True:
                chunk = conn.sock.recv(_RECV_CHUNK)
                if not chunk:
                    self._kill(cid, conn, events, "peer closed")
                    return
                try:
                    frames = conn.buf.feed(chunk)
                except FrameOverflow:
                    self._kill(cid, conn, events, "frame overflow")
                    return
                for frame in frames:
                    if conn.limiter.allow():
                        events.append((cid, frame))
                    else:
                        logger.warning(
                            "multiplayer: rate-limited a frame from %s", conn.addr)
        except BlockingIOError:
            return
        except OSError:
            self._kill(cid, conn, events, "recv error")

    def _flush_conn(self, cid: int, conn: _HostConn, events: list) -> None:
        if conn.outbuf:
            try:
                sent = conn.sock.send(conn.outbuf)
                del conn.outbuf[:sent]
            except BlockingIOError:
                pass
            except OSError:
                self._kill(cid, conn, events, "send error")
                return
        if len(conn.outbuf) > _MAX_OUTBUF_BYTES:
            self._kill(cid, conn, events, "client too far behind")

    def _kill(self, cid: int, conn: _HostConn, events: list, why: str) -> None:
        if not conn.alive:
            return
        conn.alive = False
        try:
            conn.sock.close()
        except OSError:
            pass
        events.append((cid, {"t": CONN_CLOSED, "reason": why}))

    # -- send --------------------------------------------------------

    def send(self, conn_id: int, msg: dict) -> None:
        """Queue a frame to one client and try to flush immediately."""
        conn = self._conns.get(conn_id)
        if conn is None or not conn.alive:
            return
        conn.outbuf.extend(encode_frame(msg))
        self._flush_conn(conn_id, conn, [])

    def broadcast(self, msg: dict, exclude: Optional[int] = None) -> None:
        """Queue a frame to every live client (optionally excluding one)."""
        data = encode_frame(msg)
        for cid, conn in list(self._conns.items()):
            if not conn.alive or cid == exclude:
                continue
            conn.outbuf.extend(data)
            self._flush_conn(cid, conn, [])

    def broadcast_snapshot(self, rows) -> None:
        """v1 surface: send one position snapshot to every client. Pumps
        first so a client that connected since the last call is accepted
        (v1 callers only ever loop on this method)."""
        self.poll()
        self.broadcast({"t": MSG_SNAP, "i": [list(row) for row in rows]})

    def disconnect(self, conn_id: int) -> None:
        conn = self._conns.get(conn_id)
        if conn is not None:
            self._kill(conn_id, conn, [], "host closed connection")
            self._conns.pop(conn_id, None)


class NetworkClient:
    """Client side: connects to a host, sends intent up, pulls frames down.

    ``poll()`` keeps the v1 contract -- return the single most recent
    snapshot dict, or ``None`` -- so the shipped spectator path is
    unchanged. ``take_frames()`` returns every buffered frame (snapshots
    included) for the Phase 5 session layer, which needs the control
    frames too.
    """

    def __init__(self, host: str, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self._sock: Optional[socket.socket] = None
        self._buf = FrameBuffer()
        self._inbox: list = []
        self._outbuf = bytearray()
        self._closed = False

    def connect(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)          # bounded wait for the initial handshake only
        sock.connect((self.host, self.port))
        sock.setblocking(False)       # every read after this is via a pump, never blocking
        self._sock = sock
        self._closed = False

    @property
    def connected(self) -> bool:
        return self._sock is not None and not self._closed

    def _pump(self) -> None:
        """Drain the socket into ``self._inbox`` and retry queued output.
        Never blocks. A closed/broken peer sets ``self._closed`` and stops
        further I/O."""
        if self._sock is None:
            return
        if self._outbuf:
            try:
                sent = self._sock.send(self._outbuf)
                del self._outbuf[:sent]
            except BlockingIOError:
                pass
            except OSError:
                self._fail()
                return
        try:
            while True:
                chunk = self._sock.recv(_RECV_CHUNK)
                if not chunk:
                    self._fail()
                    return
                try:
                    self._inbox.extend(self._buf.feed(chunk))
                except FrameOverflow:
                    self._fail()
                    return
        except BlockingIOError:
            return
        except OSError:
            self._fail()

    def _fail(self) -> None:
        self._closed = True
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    def poll(self) -> Optional[dict]:
        """v1 contract: the latest snapshot frame, or None. Non-snapshot
        frames stay in the inbox for ``take_frames()``. Never blocks; a
        closed connection is the silent normal case, not an error."""
        self._pump()
        if not self._inbox:
            return None
        latest = None
        keep = []
        for frame in self._inbox:
            if frame.get("t") == MSG_SNAP:
                latest = frame
            else:
                keep.append(frame)
        self._inbox = keep
        return latest

    def take_frames(self) -> list:
        """Every buffered frame since the last call, in arrival order,
        then clear. For the session layer, which needs control frames."""
        self._pump()
        frames, self._inbox = self._inbox, []
        return frames

    def flush(self) -> None:
        """Retry any queued outbound and read pending inbound (into the
        buffer for the next ``poll``/``take_frames``). Never blocks."""
        self._pump()

    def send(self, msg: dict) -> None:
        """Queue a frame to the host and try to flush immediately."""
        if self._sock is None:
            return
        self._outbuf.extend(encode_frame(msg))
        self._pump()

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
        self._sock = None
        self._closed = True
