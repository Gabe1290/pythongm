#!/usr/bin/env python3
"""Pure data for the LAN multiplayer extension -- no socket/pygame import,
matching every other extension's state.py staying import-light so the IDE
can load it for schemas alone (see extensions/block_world/state.py's own
docstring for the same reasoning).

Per-room network state lives at ``room.extension_state["multiplayer_lan"]``,
mirroring extensions/raycast_2_5d and extensions/block_world's own camera-
config pattern -- sync IDs are assigned per the CURRENT room's instance
list, so this is naturally room-scoped state, not GameRunner-scoped. This
also keeps GameRunner completely unaware of networking; the only
core-visible trace of this extension existing is the generic frame-update
hook it registers (runtime/extension_hooks.py).

This module also holds the v2 wire-protocol vocabulary and the inbound
sanitizers (docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 4.1). Everything here is
pure -- the transport in network.py builds/parses frames using these
constants, and every field that arrives over the wire (a custom message's
``data``, a shared variable's ``value``, a synced instance's ``vars``) is
passed through ``sanitize_value`` before the engine ever sees it. Nothing
from the wire reaches ``_parse_value`` / ``eval``; a shared-variable name
is checked against ``is_valid_shared_name`` so a name containing an
operator can never reach the expression evaluator (the ``_parse_value``
landmine in CLAUDE.md).
"""

import re

MULTIPLAYER_KEY = "multiplayer_lan"

# Matches the stashed 2026-05-02 prototype's own default (see
# docs/MULTIPLAYER_LAN_PLAN.md) -- an arbitrary-but-fixed port in the
# unprivileged range, unlikely to collide with common LAN services.
DEFAULT_PORT = 45782

# ---------------------------------------------------------------------------
# v2 wire protocol (docs/MULTIPLAYER_LAN_V2_PLAN.md "Wire protocol v2")
#
# Still TCP, still one JSON object per line (newline-delimited) over the
# stream -- debuggable in a packet capture, and LAN bandwidth was never the
# constraint. Every frame is ``{"t": <type>, ...}``.
# ---------------------------------------------------------------------------

# Bumped when the frame vocabulary changes incompatibly. v1 (the shipped
# spectator slice) carried no version field at all; hello/welcome exchange
# this and a mismatch is refused with a `bye` carrying a reason.
PROTO_VER = 2

# Control frames (reliable, any time).
MSG_HELLO = "hello"            # client -> host on connect: {t, name, proto_ver}
MSG_WELCOME = "welcome"        # host -> client: {t, player_id, player_count, shared, roster, tick}
MSG_JOIN = "join"             # host -> all: {t, player_id, name}
MSG_LEAVE = "leave"           # host -> all: {t, player_id, name}
MSG_BYE = "bye"              # graceful disconnect / refusal: {t, reason}
MSG_MSG = "msg"              # custom message, either way: {t, event, data, sender, target}
MSG_SHARED_SET = "shared_set"  # client->host request / host->all echo: {t, name, value}
MSG_INPUT = "input"           # client -> host, on change: {t, held: [name, ...]}
MSG_GAME_START = "game_start"  # host -> all: {t}

# State frames.
MSG_SNAP = "snap"             # host -> all, ~20Hz: {t, tick, time, shared, spawn, i, despawn}
MSG_OWN = "own"              # client -> host, once/frame: {t, i: [{nid, x, y, r, f, v}, ...]}

# Back-compat alias: v1's network.py / handlers.py / test_multiplayer_lan.py
# import SNAPSHOT_MSG_TYPE and compare against the literal "snap".
SNAPSHOT_MSG_TYPE = MSG_SNAP

# Bounds applied by sanitize_value. Sized for classroom data (a list of a
# few answers, a small inventory), not arbitrary payloads; the frame-size
# caps below are the real backstop against a hostile/broken peer.
MAX_STR_LEN = 4096
MAX_COLLECTION_LEN = 256
MAX_VALUE_DEPTH = 3

# Frame-size limits, enforced in framing.py. A single JSON line over the
# soft cap is logged but still sent/received (an author's oversized custom
# message stays visible rather than silently vanishing); a stream buffer
# that grows past the hard cap with no newline terminator is a broken or
# hostile peer and the connection is dropped.
SOFT_FRAME_BYTES = 4096
MAX_FRAME_BYTES = 65536

# Client -> host frame rate ceiling (token bucket in framing.RateLimiter).
INBOUND_FRAME_RATE = 60.0

# Player display names: length-capped, control chars stripped, display only.
MAX_NAME_LEN = 24
DEFAULT_PLAYER_NAME = "Joueur"

# A shared-variable name must be a plain identifier -- this is the guard
# that keeps a wire-supplied name out of the expression evaluator (a name
# like "a+b" would otherwise be routed to eval() by _parse_value).
_SHARED_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
MAX_SHARED_NAME_LEN = 64

_SCALAR_TYPES = (bool, int, float, str)


def is_valid_shared_name(name) -> bool:
    """True if ``name`` is a safe shared-variable identifier: a non-empty
    plain identifier (letter/underscore start, then word chars) no longer
    than ``MAX_SHARED_NAME_LEN``. Anything else -- an operator, a dot, a
    space, a leading digit, a non-str -- is rejected."""
    if not isinstance(name, str) or not name or len(name) > MAX_SHARED_NAME_LEN:
        return False
    return _SHARED_NAME_RE.match(name) is not None


def sanitize_name(name) -> str:
    """A player display name reduced to something safe to render: printable
    characters only (control chars, including newlines/tabs, dropped),
    stripped, truncated to ``MAX_NAME_LEN``. Empty/blank/non-str input
    falls back to ``DEFAULT_PLAYER_NAME``."""
    if not isinstance(name, str):
        return DEFAULT_PLAYER_NAME
    cleaned = "".join(ch for ch in name if ch.isprintable()).strip()
    cleaned = cleaned[:MAX_NAME_LEN].strip()
    return cleaned or DEFAULT_PLAYER_NAME


def sanitize_value(value, _depth=0):
    """Return a JSON-safe, bounded copy of ``value`` for handing to the
    engine after it arrives over the wire.

    * scalars (bool/int/float/str/None) pass through; a str longer than
      ``MAX_STR_LEN`` is truncated; a non-finite float (nan/inf) becomes
      ``None``.
    * a list/tuple becomes a list of sanitized elements, truncated to
      ``MAX_COLLECTION_LEN``.
    * a dict becomes a dict of ``str`` keys (non-str keys dropped) to
      sanitized values, truncated to ``MAX_COLLECTION_LEN`` entries; a
      key longer than ``MAX_STR_LEN`` is truncated.
    * nesting past ``MAX_VALUE_DEPTH``, or any other type (a set, an
      object, complex, bytes, ...), becomes ``None``.

    Never raises -- unrepresentable input degrades to ``None`` in place
    rather than rejecting the whole frame.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        # json.dumps would emit NaN/Infinity, which isn't valid JSON and
        # isn't a value the engine has any use for.
        return value if -1e308 < value < 1e308 else None
    if isinstance(value, str):
        return value if len(value) <= MAX_STR_LEN else value[:MAX_STR_LEN]

    if _depth >= MAX_VALUE_DEPTH:
        return None

    if isinstance(value, (list, tuple)):
        return [sanitize_value(item, _depth + 1)
                for item in list(value)[:MAX_COLLECTION_LEN]]

    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if not isinstance(key, str):
                continue
            if len(key) > MAX_STR_LEN:
                key = key[:MAX_STR_LEN]
            out[key] = sanitize_value(item, _depth + 1)
            if len(out) >= MAX_COLLECTION_LEN:
                break
        return out

    return None


def _fresh():
    return {
        "enabled": False,
        "mode": None,       # "host" or "client"
        "host": None,       # NetworkHost instance, host mode only
        "client": None,     # NetworkClient instance, client mode only
        "sync_ids_assigned": False,
    }


def _peek_state(room):
    """This room's multiplayer state dict if it already exists, else None.
    Does NOT create it -- mirrors block_world's state.peek_camera: the
    frame-update hooks run for EVERY room, multiplayer or not, and must
    not stamp state onto rooms that never enabled it."""
    es = getattr(room, "extension_state", None)
    return es.get(MULTIPLAYER_KEY) if es else None


def multiplayer_state(room):
    """This room's multiplayer state, creating it (and extension_state) if
    absent. Use from code that legitimately owns/mutates it (the
    set_network_mode action)."""
    es = getattr(room, "extension_state", None)
    if es is None:
        es = {}
        setattr(room, "extension_state", es)
    st = es.get(MULTIPLAYER_KEY)
    if st is None:
        st = _fresh()
        es[MULTIPLAYER_KEY] = st
    return st


def peek_multiplayer(room):
    """This room's multiplayer state if it already exists, else None."""
    return _peek_state(room)
