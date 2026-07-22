#!/usr/bin/env python3
"""Hooks that let an extension participate in the engine, not just add actions.

Actions are enough for most plugins. A feature like the 2.5D raycast view is
different: it *replaces how a room is drawn*. This module is the seam for that.

Deliberately dependency-free — it imports nothing from the engine — so both
``events/plugin_loader`` (which registers hooks) and ``runtime/game_runner``
(which calls them) can import it with no risk of a cycle.

An extension declares renderers the same declarative way it declares actions::

    # extensions/my_view/__init__.py
    def render_room(room, screen):
        cfg = room.extension_state.get("my_view")
        if not cfg or not cfg.get("enabled"):
            return False              # not mine — let the engine draw normally
        ...draw...
        return True                   # I drew this room

    PLUGIN_ROOM_RENDERERS = [render_room]

Contract for a room renderer:

* signature ``(room, screen) -> bool``;
* return **True** only if it actually drew the room. The engine then skips its
  own top-down pass but still runs the per-instance draw-event pass, so HUD
  actions (draw_score, draw_text, ...) composite on top exactly as usual;
* return **False** to decline, and the engine draws the room normally;
* store per-room state in ``room.extension_state[<your key>]`` rather than
  adding attributes to engine classes.

Renderers are tried in registration order; the first to return True wins.
"""

from core.logger import get_logger

logger = get_logger(__name__)

# Registered room renderers, in registration order.
_room_renderers = []


def register_room_renderer(func) -> None:
    """Register a ``(room, screen) -> bool`` room renderer."""
    if not callable(func):
        logger.error(f"Room renderer is not callable: {func!r}")
        return
    if func in _room_renderers:
        return                      # idempotent: the loader may re-run
    _room_renderers.append(func)
    logger.debug(f"Registered room renderer: {getattr(func, '__name__', func)}")


def get_room_renderers() -> list:
    """The registered renderers (a copy — callers must not mutate the list)."""
    return list(_room_renderers)


def clear_room_renderers() -> None:
    """Drop every registered renderer. For tests and for reloading extensions."""
    _room_renderers.clear()


def render_room(room, screen) -> bool:
    """Give each extension first refusal on drawing this room.

    Returns True as soon as one claims it. A renderer that raises is logged and
    skipped — a broken extension must not take the game down with it, and the
    engine falls back to its own rendering.
    """
    for func in _room_renderers:
        try:
            if func(room, screen):
                return True
        except Exception as exc:
            logger.error(
                f"Room renderer {getattr(func, '__name__', func)} failed: {exc}")
    return False
