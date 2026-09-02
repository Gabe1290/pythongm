#!/usr/bin/env python3
"""Stream framing + codec + rate limiting for the LAN multiplayer transport.

Pure logic, no socket import -- network.py (Phase 4.2b) owns the sockets and
uses these helpers to turn a byte stream into frames and back.

docs/MULTIPLAYER_LAN_V2_PLAN.md "Wire protocol v2": every frame is one
newline-terminated JSON object (``{"t": <type>, ...}``) over a TCP stream.
Three concerns live here:

* ``encode_frame`` -- dict -> bytes.
* ``FrameBuffer`` -- accumulate bytes off ``recv()`` and yield the complete
  frames, tolerating partial reads, multiple frames per read, and the odd
  malformed line. A buffer that grows past the hard cap with no terminator
  raises ``FrameOverflow`` -- that peer is dropped.
* ``RateLimiter`` -- a token bucket bounding how fast a client can push
  frames at the host.
"""

import json
import time

from core.logger import get_logger
from .state import INBOUND_FRAME_RATE, MAX_FRAME_BYTES, SOFT_FRAME_BYTES

logger = get_logger(__name__)


class FrameOverflow(Exception):
    """A peer sent more than ``MAX_FRAME_BYTES`` with no frame terminator.
    Not recoverable -- the caller drops the connection."""


def encode_frame(msg: dict) -> bytes:
    """A dict -> one newline-terminated JSON line (UTF-8, non-ASCII kept so
    accented text stays readable in a capture). A line over the soft cap is
    logged but still returned -- an author's oversized custom message should
    be visible in the log, not silently dropped."""
    data = (json.dumps(msg, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
    if len(data) > SOFT_FRAME_BYTES:
        logger.warning(
            "multiplayer: outbound frame %d bytes (soft cap %d, t=%r)",
            len(data), SOFT_FRAME_BYTES, msg.get("t"))
    return data


class FrameBuffer:
    """Turns the byte stream from one socket into complete frames.

    ``feed(chunk)`` appends and returns every whole frame now available, as
    parsed dicts, in arrival order. A partial trailing frame is retained
    for the next call. A line that is not valid UTF-8 JSON, is not a JSON
    object, or carries no ``"t"`` key is dropped with a log line -- one bad
    frame must not kill the connection. A buffer past ``MAX_FRAME_BYTES``
    with no ``\\n`` raises ``FrameOverflow``.
    """

    def __init__(self):
        self._buf = bytearray()

    def feed(self, chunk: bytes) -> list:
        if not chunk:
            return []
        self._buf.extend(chunk)

        if b"\n" not in self._buf:
            if len(self._buf) > MAX_FRAME_BYTES:
                raise FrameOverflow(
                    f"{len(self._buf)} bytes buffered with no frame terminator")
            return []

        *lines, rest = self._buf.split(b"\n")
        self._buf = bytearray(rest)
        if len(self._buf) > MAX_FRAME_BYTES:
            # A partial frame after the split is still oversized -- same
            # broken/hostile-peer condition.
            raise FrameOverflow(
                f"{len(self._buf)} bytes of partial frame after split")

        out = []
        for line in lines:
            if not line:
                continue
            if len(line) > MAX_FRAME_BYTES:
                logger.warning("multiplayer: dropping inbound frame, %d bytes", len(line))
                continue
            try:
                msg = json.loads(line.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                logger.warning("multiplayer: dropping unparseable inbound frame")
                continue
            if not isinstance(msg, dict) or "t" not in msg:
                logger.warning("multiplayer: dropping inbound frame with no 't'")
                continue
            out.append(msg)
        return out


class RateLimiter:
    """Token bucket: ``capacity`` tokens, refilled ``rate``/second. ``allow()``
    consumes one and returns whether it was available. Defaults to
    ``INBOUND_FRAME_RATE`` for both, so a fresh limiter tolerates a short
    burst but holds the sustained rate at the ceiling.

    ``_clock`` is injectable so tests drive time deterministically.
    """

    def __init__(self, rate: float = INBOUND_FRAME_RATE,
                 capacity: float = INBOUND_FRAME_RATE, _clock=time.monotonic):
        self._rate = float(rate)
        self._capacity = float(capacity)
        self._tokens = float(capacity)
        self._clock = _clock
        self._last = _clock()

    def allow(self) -> bool:
        now = self._clock()
        elapsed = now - self._last
        if elapsed > 0:
            self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
            self._last = now
        if self._tokens >= 1.0:
            self._tokens -= 1.0
            return True
        return False
