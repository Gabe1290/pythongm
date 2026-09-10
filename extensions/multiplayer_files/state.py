#!/usr/bin/env python3
"""Pure data for the file-exchange multiplayer extension -- no socket/
pygame/filesystem-write import, matching extensions/multiplayer_lan/
state.py's own "the IDE can load this for schemas alone" discipline.
Filesystem I/O lives in fileio.py; this module only defines the shape of
the data and the filenames involved.

Per-room file-exchange session state lives at
``room.extension_state["multiplayer_files"]``, the same room-scoped
``extension_state`` pattern multiplayer_lan/block_world/raycast_2_5d all
use -- see any of their state.py modules for the same reasoning.

See docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md for the full design. This is
Phase 1 only: host_game_files / join_game_files / leave_game_files, the
join/welcome handshake, set_shared_var_files / get_shared_var_files /
end_turn, host-authoritative round advancement with a deadline, and the
identity/status globals + lifecycle events.
``send_network_message_files`` (Phase 2) is not built yet.

Sanitizers below are DUPLICATED from extensions/multiplayer_lan/state.py,
not imported -- a deliberate decision recorded in the plan doc's "Reused
pieces" section: importing would make this extension's CODE depend on
multiplayer_lan's internals in a way the extension install/enable-warning
system (events/plugin_loader.py's missing_extensions_for_project /
not_installed_extensions_for_project) can't see, since it tracks
dependencies from which ACTIONS a project uses, not from one extension's
code importing another's. A project using only multiplayer_files would
never record multiplayer_lan as a requirement, so disabling/removing
multiplayer_lan alone -- plausible here specifically, since a school that
wants the firewall-safe option may deliberately not want the socket one
enabled -- would then break multiplayer_files with a bare ImportError and
none of the "missing extension" warnings that exist to catch exactly this.
Keep these two copies in sync by hand if either one changes; there is no
third caller yet to justify a shared low-level module.
"""

import re

MULTIPLAYER_FILES_KEY = "multiplayer_files"

# ---------------------------------------------------------------------------
# File layout (docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md "What '1990s DOS
# file-exchange' actually means here"). Every filename below is written by
# exactly ONE logical writer over its lifetime -- the client id or round
# number is baked into the name -- except session.json, written only ever
# by the host. That is the whole corruption-safety story: no two
# processes ever write the same filename, so there is no write race to
# defend against by locking.
# ---------------------------------------------------------------------------
SESSION_FILE = "session.json"


def join_file_name(client_id: str) -> str:
    return f"join_{client_id}.json"


def welcome_file_name(client_id: str) -> str:
    return f"welcome_{client_id}.json"


def leave_file_name(client_id: str) -> str:
    return f"left_{client_id}.json"


def move_file_name(slot: int, round_number: int) -> str:
    return f"move_p{slot}_r{round_number}.json"


# How often a session actually touches disk, regardless of how often the
# owning frame-update hook runs (~60 times a second). A real
# network-drive read/write commonly costs 5-50ms; polling every frame
# would hammer the file server for no benefit -- see the plan's "Why this
# is a real option, and why it's a different thing from multiplayer_lan".
POLL_INTERVAL = 1.0

DEFAULT_MAX_PLAYERS = 8
DEFAULT_ROUND_DEADLINE = 30.0
MIN_ROUND_DEADLINE = 2.0

# A shared folder that fails this many consecutive polls (read OR write)
# is treated as gone -- unmounted drive, revoked permission, and so on --
# and flags file_session_lost. More than one so a single transient
# hiccup (the same kind of brief lock fileio.atomic_write_json already
# retries through) doesn't flap the whole session.
CONSECUTIVE_FAILURES_BEFORE_LOST = 3

# ---------------------------------------------------------------------------
# Sanitizers -- duplicated from multiplayer_lan/state.py, see module
# docstring. Kept the same shape/behaviour as that copy.
# ---------------------------------------------------------------------------
MAX_STR_LEN = 4096
MAX_COLLECTION_LEN = 256
MAX_VALUE_DEPTH = 3
MAX_NAME_LEN = 24
DEFAULT_PLAYER_NAME = "Joueur"
MAX_SHARED_NAME_LEN = 64

_SHARED_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")

# Identity/status globals _apply_session_state (handlers.py) writes on
# every machine every frame -- reserved so a shared variable can never
# shadow one (the same M10 lesson multiplayer_lan/state.py documents).
# network_sender / network_player_name mirror multiplayer_lan's own
# player_joined payload globals -- set just before player_joined_files /
# player_skipped_round fire, so an author reacting to those events can
# tell who joined or was skipped the same way they already can for the
# socket version's player_joined.
RESERVED_SHARED_NAMES = frozenset({
    "player_id", "player_count", "is_host", "round_number", "turn_ready",
    "waiting_for_players", "network_sender", "network_player_name",
})


def is_valid_shared_name(name) -> bool:
    """True if ``name`` is a safe shared-variable identifier: a non-empty
    plain identifier (letter/underscore start, then word chars) no longer
    than ``MAX_SHARED_NAME_LEN``, and not one of the reserved identity/
    event global names. Anything else -- an operator, a dot, a space, a
    leading digit, a non-str, a reserved name -- is rejected."""
    if not isinstance(name, str) or not name or len(name) > MAX_SHARED_NAME_LEN:
        return False
    if name in RESERVED_SHARED_NAMES:
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
    """Return a JSON-safe, bounded copy of ``value`` for writing to a file
    or handing to the engine after reading one back.

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
    rather than rejecting the whole write.
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
        "session": None,
    }


def _peek_state(room):
    """This room's file-exchange state dict if it already exists, else
    None. Does NOT create it -- mirrors block_world's state.peek_camera /
    multiplayer_lan's state.peek_multiplayer: the frame-update hooks run
    for EVERY room, networked or not, and must not stamp state onto rooms
    that never enabled it."""
    es = getattr(room, "extension_state", None)
    return es.get(MULTIPLAYER_FILES_KEY) if es else None


def multiplayer_files_state(room):
    """This room's file-exchange state, creating it (and extension_state)
    if absent. Use from code that legitimately owns/mutates it (the
    host_game_files / join_game_files actions)."""
    es = getattr(room, "extension_state", None)
    if es is None:
        es = {}
        setattr(room, "extension_state", es)
    st = es.get(MULTIPLAYER_FILES_KEY)
    if st is None:
        st = _fresh()
        es[MULTIPLAYER_FILES_KEY] = st
    return st


def peek_multiplayer_files(room):
    """This room's file-exchange state if it already exists, else None."""
    return _peek_state(room)
