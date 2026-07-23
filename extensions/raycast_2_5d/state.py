#!/usr/bin/env python3
"""Per-room raycast state, namespaced into ``room.extension_state`` (Stage B3b).

Before this, ``GameRoom.__init__`` initialised six raycast attributes
(``raycast_camera`` + the derived wall-edge caches). That was the last place
core "knew about" the raycast feature. Now all of it lives under
``room.extension_state["raycast"]`` — the per-room namespace the extension
mechanism provides (see ``runtime/extension_hooks.py``) — so ``GameRoom`` carries
nothing raycast-specific and the extension owns its own state end to end.

The state dict holds:

* ``camera``  — the camera config the ``enable_raycast_view`` action sets
  (``{'enabled': False}`` until then);
* ``v_walls`` / ``h_walls`` — derived thin wall-edge sets (None until built);
* ``v_sprites`` / ``h_sprites`` — the sprite per edge, for wall texturing;
* ``cell_size`` — the grid size the caches were built against.
"""

RAYCAST_KEY = "raycast"


def _fresh():
    return {
        "camera": {"enabled": False},
        "v_walls": None,
        "h_walls": None,
        "v_sprites": {},
        "h_sprites": {},
        "cell_size": 32,
    }


def raycast_state(room):
    """This room's raycast state, creating it (and ``extension_state``) if absent.

    Use from the renderer/actions, which legitimately own and mutate the state.
    ``extension_state`` is guaranteed on a real ``GameRoom``; the getattr guard
    covers bare ``GameRoom.__new__`` objects that some unit tests build.
    """
    es = getattr(room, "extension_state", None)
    if es is None:
        es = {}
        setattr(room, "extension_state", es)
    st = es.get(RAYCAST_KEY)
    if st is None:
        st = _fresh()
        es[RAYCAST_KEY] = st
    return st


def peek_camera(room):
    """The camera config if this room already has raycast state, else None.

    Does NOT create state — the render hook runs for EVERY room (raycast or
    not), and it must not stamp raycast state onto every room in the game.
    """
    es = getattr(room, "extension_state", None)
    st = es.get(RAYCAST_KEY) if es else None
    return st["camera"] if st else None
