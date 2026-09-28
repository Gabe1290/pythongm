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
# Instance-overlay hooks: draw something FOR an instance, on top of the room.
#
# A room renderer replaces the whole top-down pass. Some features instead
# want one ordinary instance in an otherwise ordinary room to get extra
# drawing -- a simulated robot body with its on-screen buttons, say
# (docs/THYMIO_EXTENSION_PLAN.md, Stage 0.2). The engine draws the room
# normally, then offers every instance of the current room to each overlay,
# in screen space (no view offset -- matches where the engine composites
# HUD/GUI layers), before the draw_gui pass. An overlay decides for itself
# whether an instance is its business (typically by looking in
# instance.extension_state[<its key>]) and simply returns; there is no
# "claim" -- several overlays may each draw on the same instance.
#
#     def my_overlay(instance, screen):
#         st = instance.extension_state.get("my_ext")
#         if st: ...draw...
#
#     PLUGIN_INSTANCE_OVERLAYS = [my_overlay]
# ---------------------------------------------------------------------------

# Registered (instance, screen) -> None overlays, in registration order.
_instance_overlays = []


def register_instance_overlay(func) -> None:
    """Register an ``(instance, screen) -> None`` instance overlay."""
    if not callable(func):
        logger.error(f"Instance overlay is not callable: {func!r}")
        return
    if func in _instance_overlays:
        return                      # idempotent: the loader may re-run
    _instance_overlays.append(func)
    logger.debug(f"Registered instance overlay: {getattr(func, '__name__', func)}")


def get_instance_overlays() -> list:
    """The registered overlays (a copy — callers must not mutate the list)."""
    return list(_instance_overlays)


def clear_instance_overlays() -> None:
    """Drop every registered overlay. For tests and for reloading extensions."""
    _instance_overlays.clear()


def run_instance_overlays(instance, screen) -> None:
    """Offer one instance to every registered overlay.

    An overlay that raises is logged and skipped, same "a broken extension
    must not take the game down" contract the other runners have.
    """
    for func in _instance_overlays:
        try:
            func(instance, screen)
        except Exception as exc:
            logger.error(
                f"Instance overlay {getattr(func, '__name__', func)} failed: {exc}")


# ---------------------------------------------------------------------------
# Input hooks: see raw keyboard/mouse input before the engine's own dispatch.
#
# A simulated robot has on-screen buttons a player clicks, and keyboard keys
# that map to those buttons (docs/THYMIO_EXTENSION_PLAN.md, Stage 0.3).
# Neither is an authored keyboard/mouse EVENT, so actions can't express it.
# An extension declares a dict of optional callables:
#
#     PLUGIN_INPUT_HANDLERS = [{
#         "key_down":   lambda instance, key: ...,     # -> bool: fired something
#         "key_up":     lambda instance, key: ...,     # -> None
#         "mouse_down": lambda runner, button, x, y: ...,  # -> bool: swallow
#         "mouse_up":   lambda runner, button, x, y: ...,  # -> bool: swallow
#     }]
#
# Keyboard hooks run PER INSTANCE, inside InputHandler's instance loop,
# right after that instance's own keyboard_press/release events -- so
# ordering between instances is exactly what it is for authored events.
# Mouse hooks run ONCE per click, BEFORE the per-instance mouse events, with
# raw screen coordinates (no view offset -- an on-screen widget lives in
# screen space); returning True swallows the click so no mouse event fires,
# mirroring how a click on a robot button already behaves.
# ---------------------------------------------------------------------------

_INPUT_KINDS = ("key_down", "key_up", "mouse_down", "mouse_up")

# Registered handler dicts, in registration order.
_input_handlers = []


def register_input_handler(handlers: dict) -> None:
    """Register a dict of optional ``key_down``/``key_up``/``mouse_down``/
    ``mouse_up`` callables (see the module comment for signatures)."""
    if not isinstance(handlers, dict):
        logger.error(f"Input handler is not a dict: {handlers!r}")
        return
    unknown = set(handlers) - set(_INPUT_KINDS)
    if unknown:
        logger.error(f"Input handler has unknown kinds {sorted(unknown)}")
        return
    if any(not callable(f) for f in handlers.values()):
        logger.error(f"Input handler has a non-callable entry: {handlers!r}")
        return
    if handlers in _input_handlers:
        return                      # idempotent: the loader may re-run
    _input_handlers.append(handlers)
    logger.debug(f"Registered input handler: {sorted(handlers)}")


def get_input_handlers() -> list:
    """The registered handler dicts (a copy — callers must not mutate)."""
    return list(_input_handlers)


def clear_input_handlers() -> None:
    """Drop every registered input handler. For tests and for reloading extensions."""
    _input_handlers.clear()


def _run_input(kind: str, *args) -> bool:
    """Run every handler of ``kind``; True if any returned truthy. A handler
    that raises is logged and skipped, same contract as the other runners."""
    hit = False
    for handlers in _input_handlers:
        func = handlers.get(kind)
        if func is None:
            continue
        try:
            if func(*args):
                hit = True
        except Exception as exc:
            logger.error(
                f"Input handler {kind} {getattr(func, '__name__', func)} failed: {exc}")
    return hit


def run_key_down(instance, key: str) -> bool:
    """Per-instance key press. True if some handler fired an event."""
    return _run_input("key_down", instance, key)


def run_key_up(instance, key: str) -> None:
    """Per-instance key release."""
    _run_input("key_up", instance, key)


def run_mouse_down(game_runner, button: int, x: int, y: int) -> bool:
    """Once per click, before mouse events. True = swallow the click."""
    return _run_input("mouse_down", game_runner, button, x, y)


def run_mouse_up(game_runner, button: int, x: int, y: int) -> bool:
    """Once per release, before mouse-release events. True = swallow it."""
    return _run_input("mouse_up", game_runner, button, x, y)


# ---------------------------------------------------------------------------
# Instance-created hooks: attach per-instance state when a room builds an
# instance. A simulated robot needs its simulator to exist before the
# instance's create event can run its first robot action
# (docs/THYMIO_EXTENSION_PLAN.md, Stage B3). Runs once per instance, right
# after GameRoom constructs it from the room's instance data (not for
# instances an action creates later -- the engine never attached robot
# state to those either).
#
#     def on_instance_created(instance, instance_data, room):
#         if instance_data.get("is_robot"):
#             instance.extension_state["my_ext"] = {...}
#             instance.custom_rendered = True   # my overlay draws it
#
#     PLUGIN_INSTANCE_CREATED = [on_instance_created]
# ---------------------------------------------------------------------------

_instance_created_hooks = []


def register_instance_created_hook(func) -> None:
    """Register an ``(instance, instance_data, room) -> None`` hook."""
    if not callable(func):
        logger.error(f"Instance-created hook is not callable: {func!r}")
        return
    if func in _instance_created_hooks:
        return                      # idempotent: the loader may re-run
    _instance_created_hooks.append(func)
    logger.debug(f"Registered instance-created hook: {getattr(func, '__name__', func)}")


def get_instance_created_hooks() -> list:
    return list(_instance_created_hooks)


def clear_instance_created_hooks() -> None:
    _instance_created_hooks.clear()


def run_instance_created(instance, instance_data, room) -> None:
    """Offer a freshly built instance to every registered hook. A hook that
    raises is logged and skipped, same contract as the other runners."""
    for func in _instance_created_hooks:
        try:
            func(instance, instance_data, room)
        except Exception as exc:
            logger.error(
                f"Instance-created hook {getattr(func, '__name__', func)} failed: {exc}")


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
# `phase` is one of the three points in GameRunner.run_game_loop this module
# knows about: "before_step" (top of the frame, before begin-step/alarm/step
# events), "after_collision" (after movement and collision events, before
# end-step/destroy -- where a simulated device advances its physics and
# fires its sensor events, docs/THYMIO_EXTENSION_PLAN.md Stage A5) or
# "after_update" (after movement/collision/destroy cleanup, right before the
# frame is drawn). Named phases rather than a single generic "runs once a
# frame" hook, because WHEN in the frame a hook runs is load-bearing for
# anything doing client/host-style state sync -- a client must apply
# inbound state before Step runs against it; a host must broadcast only
# after the frame's state has actually settled.
# ---------------------------------------------------------------------------

_VALID_PHASES = ("before_step", "after_collision", "after_update")

# Registered (func, phase) pairs, in registration order.
_frame_updates = []


def register_frame_update(func, phase: str) -> None:
    """Register a ``(game_runner) -> None`` function to run every frame at
    the given ``phase`` ("before_step", "after_collision" or "after_update")."""
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


# ---------------------------------------------------------------------------
# Room-change hooks: notified whenever GameRunner switches rooms (change_room
# or a same-room rebuild via restart_current_room), so an extension whose
# per-room state is really a cross-room, process-lifetime resource -- LAN
# multiplayer's live network session being the motivating case (M1,
# docs/FULL_AUDIT_2026-09-07.md) -- can migrate it onto the new room object
# itself, instead of it being silently orphaned on a room nothing points at
# any more. Extension state otherwise lives in ``room.extension_state``
# (see the room-renderer contract above), which is naturally per-room and
# does NOT survive a rebuild; most extensions (the 2.5D raycast view, say)
# correctly WANT that -- a new room should get fresh state, not inherit the
# old one's. A hook is how the rare extension that wants otherwise opts in,
# without core knowing anything about what any specific extension stores.
#
# An extension declares one the same declarative way it declares the hooks
# above::
#
#     # extensions/my_ext/__init__.py
#     def my_room_change_hook(old_room, new_room):
#         ...
#
#     PLUGIN_ROOM_CHANGE_HOOKS = [my_room_change_hook]
#
# Called AFTER the engine has already pointed ``self.current_room`` at
# ``new_room``, but before any frame-update hook or event runs against it --
# so a migrated resource is fully live again before anything reads it.
# ``old_room`` is the room being left (``None`` on a game's very first room);
# ``new_room`` is never ``None``.
# ---------------------------------------------------------------------------

# Registered (old_room, new_room) -> None hooks, in registration order.
_room_change_hooks = []


def register_room_change_hook(func) -> None:
    """Register an ``(old_room, new_room) -> None`` room-change hook."""
    if not callable(func):
        logger.error(f"Room-change hook is not callable: {func!r}")
        return
    if func in _room_change_hooks:
        return                      # idempotent: the loader may re-run
    _room_change_hooks.append(func)
    logger.debug(f"Registered room-change hook: {getattr(func, '__name__', func)}")


def get_room_change_hooks() -> list:
    """The registered hooks (a copy — callers must not mutate the list)."""
    return list(_room_change_hooks)


def clear_room_change_hooks() -> None:
    """Drop every registered room-change hook. For tests and for reloading extensions."""
    _room_change_hooks.clear()


def run_room_change_hooks(old_room, new_room) -> None:
    """Notify every registered hook that the room changed.

    A hook that raises is logged and skipped, same "a broken extension must
    not take the game down" contract render_room/run_frame_updates have.
    """
    for func in _room_change_hooks:
        try:
            func(old_room, new_room)
        except Exception as exc:
            logger.error(
                f"Room-change hook {getattr(func, '__name__', func)} failed: {exc}")
