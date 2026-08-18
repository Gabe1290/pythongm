#!/usr/bin/env python3
"""Hooks that let an extension participate in the engine, not just add actions.

Actions are enough for most plugins. Some features need more:

* A feature like the 2.5D raycast view *replaces how a room is drawn* —
  see the room-renderer hooks below.
* A feature like LAN multiplayer needs code that runs *every frame,
  unconditionally*, not gated on whatever actions the game author happened
  to bind — see the frame-update hooks further down.

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


# ---------------------------------------------------------------------------
# Frame-update hooks: run every frame, unconditional on any authored action.
#
# A room renderer only runs during the draw pass, for whichever room is
# currently being drawn. Some extensions need something different: code that
# must run exactly once per frame regardless of what actions the game author
# wrote — LAN multiplayer's broadcast/apply-inbound being the motivating case
# (docs/MULTIPLAYER_LAN_PLAN.md Phase 0). Block World's gravity feature
# (Tier 7a) worked around not having this by requiring the author to bind an
# `apply_gravity` action in Step -- workable for a per-object physics
# feature an author opts an object into, but not for something that must run
# unconditionally even in a project with no Step-event objects at all.
#
# An extension declares frame updates the same declarative way it declares
# room renderers::
#
#     # extensions/my_ext/__init__.py
#     def my_frame_update(game_runner):
#         ...
#
#     PLUGIN_FRAME_UPDATES = [(my_frame_update, "before_step")]
#
# `phase` is one of the two points in GameRunner.run_game_loop this module
# knows about: "before_step" (top of the frame, before begin-step/alarm/step
# events) or "after_update" (after movement/collision/destroy cleanup, right
# before the frame is drawn). Named phases rather than a single generic
# "runs once a frame" hook, because WHEN in the frame a hook runs is
# load-bearing for anything doing client/host-style state sync -- a client
# must apply inbound state before Step runs against it; a host must
# broadcast only after the frame's state has actually settled.
# ---------------------------------------------------------------------------

_VALID_PHASES = ("before_step", "after_update")

# Registered (func, phase) pairs, in registration order.
_frame_updates = []


def register_frame_update(func, phase: str) -> None:
    """Register a ``(game_runner) -> None`` function to run every frame at
    the given ``phase`` ("before_step" or "after_update")."""
    if not callable(func):
        logger.error(f"Frame update is not callable: {func!r}")
        return
    if phase not in _VALID_PHASES:
        logger.error(f"Invalid frame-update phase {phase!r} for {func!r}")
        return
    entry = (func, phase)
    if entry in _frame_updates:
        return                      # idempotent: the loader may re-run
    _frame_updates.append(entry)
    logger.debug(f"Registered frame update: {getattr(func, '__name__', func)} @ {phase}")


def get_frame_updates() -> list:
    """The registered (func, phase) pairs (a copy — callers must not mutate)."""
    return list(_frame_updates)


def clear_frame_updates() -> None:
    """Drop every registered frame update. For tests and for reloading extensions."""
    _frame_updates.clear()


def run_frame_updates(game_runner, phase: str) -> None:
    """Run every registered frame-update function whose phase matches.

    A function that raises is logged and skipped, same "a broken extension
    must not take the game down" contract render_room has -- one bad
    extension must not stop the whole game loop.
    """
    for func, func_phase in _frame_updates:
        if func_phase != phase:
            continue
        try:
            func(game_runner)
        except Exception as exc:
            logger.error(
                f"Frame update {getattr(func, '__name__', func)} failed: {exc}")
