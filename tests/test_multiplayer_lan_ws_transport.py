"""extensions/multiplayer_lan/ws_transport.py -- Phase 7.1: the hand-rolled
WebSocket listener that lets the desktop host also accept an HTML5-exported
(browser) client, alongside the existing raw-TCP NetworkHost.

Layered like the transport it tests:
  * pure frame codec (encode/decode/accept-key) against RFC 6455's own
    published test vector and round-trip properties -- no sockets.
  * WebSocketHost directly, over a real 127.0.0.1 socket, driven by a
    minimal hand-rolled WebSocket client written independently in this
    file (its own HTTP request text, its own frame masking/parsing) --
    not by importing the server's encode/decode helpers -- so this is a
    real protocol-conformance check, not a self-consistency check.
  * DualHost merging a raw NetworkClient and the minimal WS client under
    one connection-id space.
  * NetworkSession(mode="host") accepting a real WS hello/welcome exchange
    end to end -- the actual "loopback test with a minimal in-test WS
    client" the plan calls for.
"""
import base64
import hashlib
import json
import os
import socket
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.multiplayer_lan.network import CONN_CLOSED, CONN_OPENED, NetworkClient
from extensions.multiplayer_lan.session import NetworkSession
from extensions.multiplayer_lan.state import MSG_HELLO, MSG_WELCOME, PROTO_VER
from extensions.multiplayer_lan.ws_transport import (
    DualHost, WebSocketHost, WSFrameOverflow, _encode_ws_frame,
    _try_parse_ws_frame, _ws_accept_key,
)

_RFC6455_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def _connect_raw_socket(port, timeout=5.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect(("127.0.0.1", port))
    return sock


def _minimal_ws_handshake(sock, path="/", pump=None, timeout=5.0):
    """A from-scratch (not reusing ws_transport.py) client-side upgrade
    request + response parse, so this actually validates RFC 6455
    conformance rather than the server agreeing with itself.

    ``pump``, if given, is called between non-blocking read attempts --
    the server side only progresses the handshake (and everything else)
    when something calls its own ``poll()``/frame-pump method, and this
    single test thread does both sides."""
    key_bytes = os.urandom(16)
    key = base64.b64encode(key_bytes).decode("ascii")
    request = (
        f"GET {path} HTTP/1.1\r\n"
        "Host: 127.0.0.1\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    ).encode("ascii")
    sock.sendall(request)

    buf = b""
    deadline = time.monotonic() + timeout
    sock.settimeout(0.05)
    while b"\r\n\r\n" not in buf:
        if pump is not None:
            pump()
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            chunk = None
        if chunk == b"":
            raise ConnectionError("peer closed during handshake")
        if chunk:
            buf += chunk
        if time.monotonic() > deadline:
            raise TimeoutError("handshake response never arrived")
    header_end = buf.find(b"\r\n\r\n")
    headers = buf[:header_end].decode("ascii", "ignore")
    leftover = buf[header_end + 4:]

    assert headers.startswith("HTTP/1.1 101"), headers
    accept = None
    for line in headers.split("\r\n")[1:]:
        if ":" not in line:
            continue
        name, _, value = line.partition(":")
        if name.strip().lower() == "sec-websocket-accept":
            accept = value.strip()
    expected = base64.b64encode(
        hashlib.sha1((key + _RFC6455_GUID).encode("ascii")).digest()
    ).decode("ascii")
    assert accept == expected, (accept, expected)
    return leftover


def _client_send_text(sock, obj):
    """A masked client->server text frame, built independently of
    ws_transport._encode_ws_frame."""
    payload = json.dumps(obj).encode("utf-8")
    mask = os.urandom(4)
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    header = bytearray([0x80 | 0x1])  # FIN=1, opcode=text
    length = len(payload)
    if length < 126:
        header.append(0x80 | length)
    elif length < 65536:
        header.append(0x80 | 126)
        header += length.to_bytes(2, "big")
    else:
        header.append(0x80 | 127)
        header += length.to_bytes(8, "big")
    sock.sendall(bytes(header) + mask + masked)


def _client_recv_frames(sock, leftover=b"", timeout=5.0, want=1, pump=None):
    """Reads (and independently parses -- masked-server-frame check
    included) until ``want`` text-frame payloads have arrived, returning
    ``(list_of_dicts, remaining_leftover_bytes)``. ``pump`` is called
    between non-blocking read attempts (see ``_minimal_ws_handshake``)."""
    buf = bytearray(leftover)
    out = []
    deadline = time.monotonic() + timeout
    sock.settimeout(0.05)
    while len(out) < want:
        while True:
            parsed = _parse_one_client_side(buf)
            if parsed is None:
                break
            opcode, payload = parsed
            if opcode == 0x1:
                out.append(json.loads(payload.decode("utf-8")))
        if len(out) >= want:
            break
        if pump is not None:
            pump()
        try:
            chunk = sock.recv(65536)
        except socket.timeout:
            chunk = None
        if chunk == b"":
            raise ConnectionError("peer closed")
        if chunk:
            buf.extend(chunk)
        if time.monotonic() > deadline:
            raise TimeoutError("did not receive expected WS frames in time")
    return out, bytes(buf)


def _parse_one_client_side(buf: bytearray):
    """Independent frame parser (client side): asserts the server frame is
    NEVER masked, per RFC 6455 -- a real conformance check the server-side
    parser (which only ever unmasks) can't catch itself."""
    if len(buf) < 2:
        return None
    b0, b1 = buf[0], buf[1]
    opcode = b0 & 0x0F
    assert not (b1 & 0x80), "server must not mask its frames"
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
    if len(buf) < pos + length:
        return None
    payload = bytes(buf[pos:pos + length])
    del buf[:pos + length]
    return opcode, payload


# ---------------------------------------------------------------------------
# Pure codec
# ---------------------------------------------------------------------------

class TestFrameCodec:
    def test_accept_key_matches_the_rfc6455_published_test_vector(self):
        # https://datatracker.ietf.org/doc/html/rfc6455#section-1.3
        assert _ws_accept_key("dGhlIHNhbXBsZSBub25jZQ==") == "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="

    def test_encode_decode_round_trip_small_payload(self):
        payload = b'{"t":"hello"}'
        frame = _encode_ws_frame(payload)
        buf = bytearray(frame)
        opcode, decoded = _try_parse_ws_frame(buf)
        assert opcode == 0x1
        assert decoded == payload
        assert len(buf) == 0

    def test_encode_decode_round_trip_16bit_length(self):
        payload = b"x" * 5000
        frame = _encode_ws_frame(payload)
        assert frame[1] == 126
        buf = bytearray(frame)
        opcode, decoded = _try_parse_ws_frame(buf)
        assert decoded == payload

    def test_partial_frame_returns_none_until_complete(self):
        payload = b'{"t":"x"}'
        frame = _encode_ws_frame(payload)
        buf = bytearray(frame[:3])
        assert _try_parse_ws_frame(buf) is None
        buf.extend(frame[3:])
        opcode, decoded = _try_parse_ws_frame(buf)
        assert decoded == payload

    def test_masked_client_frame_decodes_correctly(self):
        payload = b'{"t":"input"}'
        mask = b"\x01\x02\x03\x04"
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        frame = bytearray([0x81, 0x80 | len(payload)]) + mask + masked
        opcode, decoded = _try_parse_ws_frame(frame)
        assert decoded == payload

    def test_oversized_declared_length_raises_overflow(self):
        from extensions.multiplayer_lan.state import MAX_FRAME_BYTES
        huge = MAX_FRAME_BYTES + 1
        header = bytearray([0x81, 127]) + huge.to_bytes(8, "big")
        try:
            _try_parse_ws_frame(header)
            assert False, "expected WSFrameOverflow"
        except WSFrameOverflow:
            pass


# ---------------------------------------------------------------------------
# WebSocketHost, direct
# ---------------------------------------------------------------------------

class TestWebSocketHostDirect:
    def test_handshake_and_message_round_trip(self):
        host = WebSocketHost(0)
        host.start()
        try:
            sock = _connect_raw_socket(host.bound_port)
            try:
                # The handshake's own pump() calls are the ones that will
                # actually emit CONN_OPENED (the moment the handshake
                # completes) -- collect across all of them, or a poll()
                # loop starting only after the handshake returns misses it.
                collected = []
                leftover = _minimal_ws_handshake(
                    sock, pump=lambda: collected.extend(host.poll()))
                deadline = time.monotonic() + 5.0
                cid = None
                while cid is None:
                    for c, frame in collected:
                        if frame.get("t") == CONN_OPENED:
                            cid = c
                    collected.clear()
                    if cid is None:
                        collected.extend(host.poll())
                    if time.monotonic() > deadline:
                        raise TimeoutError("no CONN_OPENED observed")
                    time.sleep(0.02)

                _client_send_text(sock, {"t": "hello", "name": "Nav"})
                deadline = time.monotonic() + 5.0
                seen = None
                while seen is None:
                    for c, frame in host.poll():
                        if frame.get("t") == "hello":
                            seen = frame
                    if time.monotonic() > deadline:
                        raise TimeoutError("hello frame never arrived at the host")
                    time.sleep(0.02)
                assert seen["name"] == "Nav"

                host.send(cid, {"t": "welcome", "player_id": 3})
                msgs, leftover = _client_recv_frames(sock, leftover)
                assert msgs == [{"t": "welcome", "player_id": 3}]
            finally:
                sock.close()
        finally:
            host.close()

    def test_non_websocket_request_is_refused(self):
        host = WebSocketHost(0)
        host.start()
        try:
            sock = _connect_raw_socket(host.bound_port)
            try:
                sock.sendall(b"GET / HTTP/1.1\r\nHost: x\r\n\r\n")
                deadline = time.monotonic() + 5.0
                closed = False
                while not closed:
                    for _cid, frame in host.poll():
                        pass  # a refused pre-handshake peer never gets a CONN_OPENED/CLOSED
                    try:
                        sock.settimeout(0.1)
                        chunk = sock.recv(1)
                        if chunk == b"":
                            closed = True
                    except (socket.timeout, ConnectionResetError, OSError):
                        pass
                    if time.monotonic() > deadline:
                        raise TimeoutError("bad handshake was never rejected")
            finally:
                sock.close()
        finally:
            host.close()

    def test_close_frame_triggers_conn_closed(self):
        host = WebSocketHost(0)
        host.start()
        try:
            sock = _connect_raw_socket(host.bound_port)
            try:
                collected = []
                leftover = _minimal_ws_handshake(
                    sock, pump=lambda: collected.extend(host.poll()))
                deadline = time.monotonic() + 5.0
                cid = None
                while cid is None:
                    for c, frame in collected:
                        if frame.get("t") == CONN_OPENED:
                            cid = c
                    collected.clear()
                    if cid is None:
                        collected.extend(host.poll())
                    if time.monotonic() > deadline:
                        raise TimeoutError()
                    time.sleep(0.02)

                sock.sendall(bytes([0x88, 0x80, 0, 0, 0, 0]))  # masked empty close frame
                deadline = time.monotonic() + 5.0
                closed = False
                while not closed:
                    for c, frame in host.poll():
                        if frame.get("t") == CONN_CLOSED:
                            closed = True
                    if time.monotonic() > deadline:
                        raise TimeoutError("CONN_CLOSED never observed")
                    time.sleep(0.02)
            finally:
                sock.close()
        finally:
            host.close()


# ---------------------------------------------------------------------------
# DualHost
# ---------------------------------------------------------------------------

class TestDualHost:
    def test_raw_and_ws_clients_share_one_broadcast(self):
        host = DualHost(0)
        host.start()
        try:
            assert host.bound_ws_port != 0
            assert host.bound_ws_port != host.port

            raw_client = NetworkClient("127.0.0.1", host.port)
            raw_client.connect()
            ws_sock = _connect_raw_socket(host.bound_ws_port)
            collected = []
            leftover = _minimal_ws_handshake(
                ws_sock, pump=lambda: collected.extend(host.poll()))
            try:
                ids = set()
                deadline = time.monotonic() + 5.0
                while len(ids) < 2:
                    for cid, frame in collected:
                        if frame.get("t") == CONN_OPENED:
                            ids.add(cid)
                    collected.clear()
                    collected.extend(host.poll())
                    if time.monotonic() > deadline:
                        raise TimeoutError(f"only saw {ids}")
                    time.sleep(0.02)
                raw_id = min(ids)
                ws_id = max(ids)
                assert ws_id >= 1_000_000_000
                assert raw_id < 1_000_000_000

                host.broadcast({"t": "ping", "n": 1})

                deadline = time.monotonic() + 5.0
                got_raw = False
                while not got_raw:
                    frame = raw_client.poll()
                    raw_client.flush()
                    for f in raw_client.take_frames():
                        if f.get("t") == "ping":
                            got_raw = True
                    if time.monotonic() > deadline:
                        raise TimeoutError("raw client never saw the broadcast")
                    time.sleep(0.02)

                msgs, leftover = _client_recv_frames(ws_sock, leftover)
                assert {"t": "ping", "n": 1} in msgs

                host.send(ws_id, {"t": "only_ws"})
                msgs, leftover = _client_recv_frames(ws_sock, leftover)
                assert {"t": "only_ws"} in msgs
            finally:
                raw_client.close()
                ws_sock.close()
        finally:
            host.close()

    def test_bound_ws_port_is_zero_before_start(self):
        host = DualHost(0)
        assert host.bound_ws_port == 0


# ---------------------------------------------------------------------------
# NetworkSession end to end -- the plan's "loopback test with a minimal
# in-test WS client"
# ---------------------------------------------------------------------------

class TestSessionOverWebSocket:
    def test_browser_style_client_completes_hello_welcome(self):
        session = NetworkSession(mode="host", port=0, player_name="Prof")
        session.start()
        try:
            ws_port = session.bound_ws_port
            assert ws_port != 0

            sock = _connect_raw_socket(ws_port)
            try:
                def _pump():
                    session.pump_before_step()
                    session.pump_after_update()

                leftover = _minimal_ws_handshake(sock, pump=_pump)

                # host must poll (pump_before_step) to accept + relay the
                # WS CONN_OPENED into its own hello/welcome bookkeeping
                deadline = time.monotonic() + 5.0
                while True:
                    session.pump_before_step()
                    session.pump_after_update()
                    if session._pending or session._roster:
                        break
                    if time.monotonic() > deadline:
                        raise TimeoutError("host never observed the WS connection")
                    time.sleep(0.02)

                _client_send_text(sock, {
                    "t": MSG_HELLO, "name": "Élève", "proto_ver": PROTO_VER,
                })

                deadline = time.monotonic() + 5.0
                welcome = None
                msgs = []
                while welcome is None:
                    session.pump_before_step()
                    session.pump_after_update()
                    try:
                        sock.settimeout(0.05)
                        chunk = sock.recv(65536)
                        if chunk:
                            leftover += chunk
                    except socket.timeout:
                        pass
                    while True:
                        buf = bytearray(leftover)
                        parsed = _parse_one_client_side(buf)
                        if parsed is None:
                            break
                        opcode, payload = parsed
                        leftover = bytes(buf)
                        if opcode == 0x1:
                            msg = json.loads(payload.decode("utf-8"))
                            msgs.append(msg)
                            if msg.get("t") == MSG_WELCOME:
                                welcome = msg
                    if time.monotonic() > deadline:
                        raise TimeoutError(f"no welcome yet, saw {msgs}")

                assert welcome["player_id"] == 1
                assert welcome["player_count"] == 2
                assert session.roster[-1][1] == "Élève"
            finally:
                sock.close()
        finally:
            session.close()


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
