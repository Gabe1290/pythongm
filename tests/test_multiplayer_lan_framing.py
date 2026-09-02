"""LAN multiplayer v2 -- stream framing / codec / rate limiter unit tests.

docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 4.2a: extensions/multiplayer_lan/
framing.py. Pure logic, no sockets -- the bytes-in / frames-out layer the
Phase 4.2b bidirectional transport is built on.
"""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.multiplayer_lan.framing import (  # noqa: E402
    FrameBuffer, FrameOverflow, RateLimiter, encode_frame,
)
from extensions.multiplayer_lan.state import (  # noqa: E402
    MAX_FRAME_BYTES, INBOUND_FRAME_RATE,
)


# ---------------------------------------------------------------------------
# encode_frame
# ---------------------------------------------------------------------------

class TestEncodeFrame:
    def test_newline_terminated_json(self):
        out = encode_frame({"t": "hello", "name": "Bob"})
        assert out.endswith(b"\n")
        assert json.loads(out) == {"t": "hello", "name": "Bob"}

    def test_no_embedded_newline(self):
        # The frame delimiter must be unambiguous.
        out = encode_frame({"t": "msg", "data": "a\tb"})
        assert out.count(b"\n") == 1

    def test_accents_preserved_readable(self):
        out = encode_frame({"t": "join", "name": "Amélie"})
        assert "Amélie" in out.decode("utf-8")
        assert json.loads(out)["name"] == "Amélie"

    def test_roundtrips_through_framebuffer(self):
        fb = FrameBuffer()
        assert fb.feed(encode_frame({"t": "snap", "i": []})) == [{"t": "snap", "i": []}]


# ---------------------------------------------------------------------------
# FrameBuffer
# ---------------------------------------------------------------------------

class TestFrameBuffer:
    def test_single_complete_frame(self):
        fb = FrameBuffer()
        assert fb.feed(b'{"t":"a"}\n') == [{"t": "a"}]

    def test_empty_feed(self):
        assert FrameBuffer().feed(b"") == []

    def test_partial_then_completed(self):
        fb = FrameBuffer()
        assert fb.feed(b'{"t":"a",') == []
        assert fb.feed(b'"x":1}\n') == [{"t": "a", "x": 1}]

    def test_byte_at_a_time(self):
        fb = FrameBuffer()
        raw = encode_frame({"t": "input", "held": ["jump", "left"]})
        results = []
        for i in range(len(raw)):
            results.extend(fb.feed(raw[i:i + 1]))
        assert results == [{"t": "input", "held": ["jump", "left"]}]

    def test_multiple_frames_one_chunk_in_order(self):
        fb = FrameBuffer()
        chunk = b'{"t":"a"}\n{"t":"b"}\n{"t":"c"}\n'
        assert fb.feed(chunk) == [{"t": "a"}, {"t": "b"}, {"t": "c"}]

    def test_trailing_partial_retained(self):
        fb = FrameBuffer()
        assert fb.feed(b'{"t":"a"}\n{"t":"b"') == [{"t": "a"}]
        assert fb.feed(b'}\n') == [{"t": "b"}]

    def test_malformed_json_line_skipped_neighbours_survive(self):
        fb = FrameBuffer()
        out = fb.feed(b'{"t":"good1"}\nnot json at all\n{"t":"good2"}\n')
        assert out == [{"t": "good1"}, {"t": "good2"}]

    def test_non_object_json_skipped(self):
        fb = FrameBuffer()
        assert fb.feed(b'[1,2,3]\n"a string"\n5\ntrue\n') == []

    def test_object_without_type_key_skipped(self):
        fb = FrameBuffer()
        assert fb.feed(b'{"x":1}\n{"t":"ok"}\n') == [{"t": "ok"}]

    def test_blank_lines_skipped(self):
        fb = FrameBuffer()
        assert fb.feed(b'\n\n{"t":"a"}\n\n') == [{"t": "a"}]

    def test_invalid_utf8_line_skipped(self):
        fb = FrameBuffer()
        assert fb.feed(b'\xff\xfe bad bytes\n{"t":"ok"}\n') == [{"t": "ok"}]

    def test_overflow_no_terminator_raises(self):
        fb = FrameBuffer()
        with pytest.raises(FrameOverflow):
            fb.feed(b"x" * (MAX_FRAME_BYTES + 1))

    def test_overflow_accumulates_across_feeds(self):
        fb = FrameBuffer()
        half = b"x" * (MAX_FRAME_BYTES // 2 + 1)
        assert fb.feed(half) == []
        with pytest.raises(FrameOverflow):
            fb.feed(half)

    def test_huge_but_terminated_line_dropped_not_raised(self):
        fb = FrameBuffer()
        line = b'{"t":"x","p":"' + b"a" * (MAX_FRAME_BYTES + 10) + b'"}\n' + b'{"t":"ok"}\n'
        # The oversized frame is dropped with a log line; the good one after it survives.
        assert fb.feed(line) == [{"t": "ok"}]

    def test_just_under_hard_cap_ok(self):
        fb = FrameBuffer()
        payload = "a" * (MAX_FRAME_BYTES - 200)
        raw = encode_frame({"t": "msg", "p": payload})
        assert len(raw) < MAX_FRAME_BYTES
        assert fb.feed(raw) == [{"t": "msg", "p": payload}]


# ---------------------------------------------------------------------------
# RateLimiter
# ---------------------------------------------------------------------------

class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class TestRateLimiter:
    def test_burst_up_to_capacity_then_denied(self):
        clk = FakeClock()
        rl = RateLimiter(rate=60.0, capacity=10.0, _clock=clk)
        assert sum(rl.allow() for _ in range(10)) == 10
        assert rl.allow() is False

    def test_refills_over_time(self):
        clk = FakeClock()
        rl = RateLimiter(rate=10.0, capacity=5.0, _clock=clk)
        assert sum(rl.allow() for _ in range(5)) == 5
        assert rl.allow() is False
        clk.t += 1.0                       # +10 tokens worth of time...
        assert sum(rl.allow() for _ in range(5)) == 5   # ...but capped at capacity
        assert rl.allow() is False

    def test_partial_refill(self):
        clk = FakeClock()
        rl = RateLimiter(rate=10.0, capacity=10.0, _clock=clk)
        for _ in range(10):
            rl.allow()
        assert rl.allow() is False
        clk.t += 0.25                      # 2.5 tokens
        assert rl.allow() is True
        assert rl.allow() is True
        assert rl.allow() is False

    def test_never_exceeds_capacity(self):
        clk = FakeClock()
        rl = RateLimiter(rate=1000.0, capacity=3.0, _clock=clk)
        clk.t += 100.0
        assert sum(rl.allow() for _ in range(50)) == 3

    def test_defaults_to_plan_ceiling(self):
        rl = RateLimiter()
        assert sum(rl.allow() for _ in range(int(INBOUND_FRAME_RATE))) == int(INBOUND_FRAME_RATE)
