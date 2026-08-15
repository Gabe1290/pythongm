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
"""

MULTIPLAYER_KEY = "multiplayer_lan"

# Matches the stashed 2026-05-02 prototype's own default (see
# docs/MULTIPLAYER_LAN_PLAN.md) -- an arbitrary-but-fixed port in the
# unprivileged range, unlikely to collide with common LAN services.
DEFAULT_PORT = 45782

# The wire message shape, documented here as the single source of truth for
# both network.py (which builds/parses it) and any future test. A snapshot
# message:
#   {"t": "snap", "i": [[sync_id, x, y, rotation, image_index, visible], ...]}
# One JSON object per line (newline-delimited), sent over the TCP stream.
SNAPSHOT_MSG_TYPE = "snap"


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
