#!/usr/bin/env python3
"""A hand-rolled WebSocket listener, so the desktop host also accepts
connections from an HTML5-exported (browser) client -- no pip dependency,
per docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 7.1.

Runs *alongside* the existing raw-TCP ``NetworkHost`` (network.py), on the
next port up, speaking the exact same JSON message vocabulary
(``state.py``'s ``MSG_*`` types) -- just carried as one RFC 6455 WebSocket
text frame per message instead of newline-delimited bytes on a raw socket.
``DualHost`` composes the two under one connection-id space so
``session.py`` drives a host with browser clients exactly like one with
only desktop clients: same ``poll()``/``send()``/``broadcast()`` contract
as ``NetworkHost``.

Scope, deliberately: unfragmented text (and binary, treated identically --
either way the payload is decoded as UTF-8 JSON) frames only. A JSON
message here is a few hundred bytes at most (``state.py``'s own
``SOFT_FRAME_BYTES``/``MAX_FRAME_BYTES`` caps), and every WebSocket client
implementation (browsers included) sends a message that size as a single
unfragmented frame by default -- so continuation frames (opcode 0x0) are
not handled. Ping/pong/close are handled (a browser tab's own WebSocket
implementation sends pings automatically); everything else is answered
correctly enough for a classroom LAN, not written to survive an adversarial
peer.
"""

import base64
import hashlib
import json
import re
import socket
from typing import Optional

from core.logger import get_logger
from .framing import RateLimiter
from .network import CONN_CLOSED, CONN_OPENED, NetworkHost
from .state import MAX_FRAME_BYTES

logger = get_logger(__name__)

_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
_MAX_HANDSHAKE_BYTES = 8192
_MAX_OUTBUF_BYTES = 262144
_RECV_CHUNK = 65536

_SEC_WS_KEY_RE = re.compile(rb"[Ss]ec-[Ww]eb[Ss]ocket-[Kk]ey:[ \t]*([^\r\n]+)")

_OP_CONT = 0x0
_OP_TEXT = 0x1
_OP_BINARY = 0x2
_OP_CLOSE = 0x8
_OP_PING = 0x9
_OP_PONG = 0xA


class WSFrameOverflow(Exception):
    """A peer declared a WebSocket frame payload larger than
    ``MAX_FRAME_BYTES`` -- same broken/hostile-peer condition as
    ``framing.FrameOverflow``, just for the WS transport."""


def _ws_accept_key(key: str) -> str:
    digest = hashlib.sha1((key + _WS_GUID).encode("ascii")).digest()
    return base64.b64encode(digest).decode("ascii")


def _encode_ws_frame(payload: bytes, opcode: int = _OP_TEXT) -> bytes:
    """Server -> client frame: FIN=1, never masked (RFC 6455 forbids a
    server from masking)."""
    header = bytearray()
    header.append(0x80 | (opcode & 0x0F))
    length = len(payload)
    if length < 126:
        header.append(length)
    elif length < 65536:
        header.append(126)
        header += length.to_bytes(2, "big")
    else:
        header.append(127)
        header += length.to_bytes(8, "big")
    return bytes(header) + payload


def _try_parse_ws_frame(buf: bytearray):
    """Parse one complete frame off the front of ``buf`` and remove it,
    returning ``(opcode, payload)``. ``None`` if ``buf`` doesn't yet hold a
    complete frame -- wait for more bytes. Raises ``WSFrameOverflow`` for a
    declared length over the cap (checked as soon as the length is known,
    before waiting on the payload)."""
    if len(buf) < 2:
        return None
    b0, b1 = buf[0], buf[1]
    opcode = b0 & 0x0F
    masked = bool(b1 & 0x80)
    length = b1 & 0x7F
    pos = 2
    if length == 126:
        if len(buf) < pos + 2:
            return None
        length = int.from_bytes(bytes(buf[pos:pos + 2]), "big")
        pos += 2
    elif length == 127:
        if len(buf) < pos + 8:
            return None
        length = int.from_bytes(bytes(buf[pos:pos + 8]), "big")
        pos += 8
    if length > MAX_FRAME_BYTES:
        raise WSFrameOverflow(f"{length} byte WS frame exceeds cap")
    mask_key = None
    if masked:
        if len(buf) < pos + 4:
            return None
        mask_key = bytes(buf[pos:pos + 4])
        pos += 4
    if len(buf) < pos + length:
        return None
    raw_payload = bytes(buf[pos:pos + length])
    if masked:
        payload = bytes(raw_payload[i] ^ mask_key[i % 4] for i in range(length))
    else:
        payload = raw_payload
    del buf[:pos + length]
    return opcode, payload


class _WSConn:
    __slots__ = ("sock", "addr", "handshaken", "hbuf", "fbuf", "outbuf",
                 "limiter", "alive")

    def __init__(self, sock: socket.socket, addr):
        self.sock = sock
        self.addr = addr
        self.handshaken = False
        self.hbuf = bytearray()      # raw HTTP handshake bytes, pre-upgrade
        self.fbuf = bytearray()      # raw WS frame bytes, post-upgrade
        self.outbuf = bytearray()
        self.limiter = RateLimiter()
        self.alive = True


class WebSocketHost:
    """Same shape as ``network.NetworkHost`` (``start``/``poll``/``send``/
    ``broadcast``/``disconnect``/``close``/``connection_ids``/
    ``_listen_sock``), but each accepted TCP connection first completes an
    HTTP -> WebSocket upgrade handshake before it's treated as a peer; the
    synthetic ``CONN_OPENED`` event fires once that handshake completes
    (not on raw accept), since a browser can't send/receive real frames
    before then."""

    def __init__(self, port: int):
        self.port = port
        self._listen_sock: Optional[socket.socket] = None
        self._conns = {}
        self._next_id = 1

    def start(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", self.port))
        sock.listen(16)
        sock.setblocking(False)
        self._listen_sock = sock
        self.port = sock.getsockname()[1]

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
    def bound_port(self) -> int:
        if self._listen_sock is not None:
            return self._listen_sock.getsockname()[1]
        return 0

    @property
    def connection_ids(self) -> list:
        """Live, fully-handshaken connection ids -- a socket mid-upgrade
        isn't a peer yet."""
        return [cid for cid, c in self._conns.items() if c.alive and c.handshaken]

    def poll(self) -> list:
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
            self._conns[cid] = _WSConn(sock, addr)
            # No CONN_OPENED yet -- deferred to a completed handshake.

    def _read_conn(self, cid: int, conn: _WSConn, events: list) -> None:
        try:
            while True:
                chunk = conn.sock.recv(_RECV_CHUNK)
                if not chunk:
                    self._kill(cid, conn, events, "peer closed")
                    return
                if not conn.handshaken:
                    conn.hbuf.extend(chunk)
                    if len(conn.hbuf) > _MAX_HANDSHAKE_BYTES:
                        self._kill(cid, conn, events, "handshake too large")
                        return
                    if b"\r\n\r\n" not in conn.hbuf:
                        continue
                    if not self._complete_handshake(cid, conn, events):
                        return
                else:
                    conn.fbuf.extend(chunk)
                    if not self._drain_ws_frames(cid, conn, events):
                        return
        except BlockingIOError:
            return
        except OSError:
            self._kill(cid, conn, events, "recv error")

    def _complete_handshake(self, cid: int, conn: _WSConn, events: list) -> bool:
        header_end = conn.hbuf.find(b"\r\n\r\n")
        headers = bytes(conn.hbuf[:header_end])
        leftover = bytes(conn.hbuf[header_end + 4:])
        conn.hbuf = bytearray()
        match = _SEC_WS_KEY_RE.search(headers)
        if not match:
            self._kill(cid, conn, events, "not a websocket upgrade request")
            return False
        key = match.group(1).decode("ascii", "ignore").strip()
        accept = _ws_accept_key(key)
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Accept: " + accept + "\r\n"
            "\r\n"
        ).encode("ascii")
        conn.outbuf.extend(response)
        conn.handshaken = True
        self._flush_conn(cid, conn, events)
        if not conn.alive:
            return False
        events.append((cid, {"t": CONN_OPENED, "addr": conn.addr[0] if conn.addr else ""}))
        if leftover:
            conn.fbuf.extend(leftover)
            return self._drain_ws_frames(cid, conn, events)
        return True

    def _drain_ws_frames(self, cid: int, conn: _WSConn, events: list) -> bool:
        """Returns False if the connection was killed mid-drain (caller
        must stop reading it)."""
        while True:
            try:
                parsed = _try_parse_ws_frame(conn.fbuf)
            except WSFrameOverflow:
                self._kill(cid, conn, events, "frame overflow")
                return False
            if parsed is None:
                return True
            opcode, payload = parsed
            if opcode == _OP_CLOSE:
                conn.outbuf.extend(_encode_ws_frame(b"", opcode=_OP_CLOSE))
                self._flush_conn(cid, conn, events)
                self._kill(cid, conn, events, "client closed")
                return False
            elif opcode == _OP_PING:
                conn.outbuf.extend(_encode_ws_frame(payload, opcode=_OP_PONG))
                continue
            elif opcode == _OP_PONG:
                continue
            elif opcode in (_OP_TEXT, _OP_BINARY):
                try:
                    msg = json.loads(payload.decode("utf-8"))
                except (ValueError, UnicodeDecodeError):
                    logger.warning("multiplayer: dropping unparseable WS frame")
                    continue
                if not isinstance(msg, dict) or "t" not in msg:
                    logger.warning("multiplayer: dropping WS frame with no 't'")
                    continue
                if conn.limiter.allow():
                    events.append((cid, msg))
                else:
                    logger.warning("multiplayer: rate-limited a WS frame from %s", conn.addr)
            # opcode 0x0 (continuation) or a reserved opcode: unsupported,
            # silently ignored -- see the module docstring's scope note.

    def _flush_conn(self, cid: int, conn: _WSConn, events: list) -> None:
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

    def _kill(self, cid: int, conn: _WSConn, events: list, why: str) -> None:
        if not conn.alive:
            return
        conn.alive = False
        try:
            conn.sock.close()
        except OSError:
            pass
        if conn.handshaken:
            events.append((cid, {"t": CONN_CLOSED, "reason": why}))

    def send(self, conn_id: int, msg: dict) -> None:
        conn = self._conns.get(conn_id)
        if conn is None or not conn.alive or not conn.handshaken:
            return
        data = json.dumps(msg, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        conn.outbuf.extend(_encode_ws_frame(data))
        self._flush_conn(conn_id, conn, [])

    def broadcast(self, msg: dict, exclude: Optional[int] = None) -> None:
        data = json.dumps(msg, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        frame = _encode_ws_frame(data)
        for cid, conn in list(self._conns.items()):
            if not conn.alive or not conn.handshaken or cid == exclude:
                continue
            conn.outbuf.extend(frame)
            self._flush_conn(cid, conn, [])

    def disconnect(self, conn_id: int) -> None:
        conn = self._conns.get(conn_id)
        if conn is not None:
            self._kill(conn_id, conn, [], "host closed connection")
            self._conns.pop(conn_id, None)


# The raw-TCP cid counter (network.NetworkHost) and this module's cid
# counter each start at 1 independently -- offsetting WS ids well clear of
# any realistic raw-TCP connection count keeps a single int cid always
# naming exactly one connection regardless of which transport it arrived
# on.
_WS_ID_OFFSET = 1_000_000_000


class DualHost:
    """Presents the exact ``NetworkHost`` surface ``session.py`` drives
    (``start``/``close``/``poll``/``send``/``broadcast``/``disconnect``/
    ``connection_ids``/``_listen_sock``), but runs the original raw-TCP
    listener *and* a ``WebSocketHost`` side by side -- so one host accepts
    both desktop/exported-native clients and HTML5-exported browser
    clients, merged under one connection-id space.

    The WebSocket listener binds one port above the raw one when an
    explicit port was requested (matching ``state.DISCOVERY_PORT``'s own
    "one above" convention for the UDP beacon -- no collision risk, it's a
    different protocol/socket namespace); with the ephemeral ``port=0`` a
    test uses, it independently asks the OS for its own free port.

    A WebSocket bind failure (port in use, permission, ...) is logged and
    disables browser support for this session rather than failing the
    whole host -- the raw-TCP side already works and is what every sample
    exercises; losing HTML5-only reachability shouldn't block hosting for
    everyone else.
    """

    def __init__(self, port: int):
        self._requested_port = port
        self.port = port
        self._raw = NetworkHost(port)
        self._ws: Optional[WebSocketHost] = None

    def start(self) -> None:
        self._raw.start()
        self.port = self._raw._listen_sock.getsockname()[1]
        # A requested port of 0 (tests) asks the OS for an independent free
        # WS port too, rather than the raw side's OS-assigned port + 1,
        # which could just as easily already be taken by something else.
        ws_port = 0 if self._requested_port == 0 else self._requested_port + 1
        ws = WebSocketHost(ws_port)
        try:
            ws.start()
            self._ws = ws
        except OSError as exc:
            logger.warning(
                "multiplayer: could not start the WebSocket (browser) listener "
                "on port %s -- native clients are unaffected: %s", ws_port, exc)
            self._ws = None

    def close(self) -> None:
        self._raw.close()
        if self._ws is not None:
            self._ws.close()
            self._ws = None

    @property
    def _listen_sock(self):
        return self._raw._listen_sock

    @property
    def bound_ws_port(self) -> int:
        return self._ws.bound_port if self._ws is not None else 0

    @property
    def connection_ids(self) -> list:
        ids = list(self._raw.connection_ids)
        if self._ws is not None:
            ids.extend(cid + _WS_ID_OFFSET for cid in self._ws.connection_ids)
        return ids

    def poll(self) -> list:
        events = self._raw.poll()
        if self._ws is not None:
            events.extend((cid + _WS_ID_OFFSET, frame) for cid, frame in self._ws.poll())
        return events

    def send(self, conn_id: int, msg: dict) -> None:
        if conn_id >= _WS_ID_OFFSET:
            if self._ws is not None:
                self._ws.send(conn_id - _WS_ID_OFFSET, msg)
        else:
            self._raw.send(conn_id, msg)

    def broadcast(self, msg: dict, exclude: Optional[int] = None) -> None:
        raw_exclude = ws_exclude = None
        if exclude is not None:
            if exclude >= _WS_ID_OFFSET:
                ws_exclude = exclude - _WS_ID_OFFSET
            else:
                raw_exclude = exclude
        self._raw.broadcast(msg, exclude=raw_exclude)
        if self._ws is not None:
            self._ws.broadcast(msg, exclude=ws_exclude)

    def disconnect(self, conn_id: int) -> None:
        if conn_id >= _WS_ID_OFFSET:
            if self._ws is not None:
                self._ws.disconnect(conn_id - _WS_ID_OFFSET)
        else:
            self._raw.disconnect(conn_id)
