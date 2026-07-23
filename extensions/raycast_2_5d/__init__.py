#!/usr/bin/env python3
"""2.5D raycast view, packaged as a folder extension.

This is the worked example the extension mechanism exists for
(docs/RAYCAST_EXTENSION_PLAN.md): a real engine feature living outside core,
hooked in through the same declarative contract a single-file plugin uses.

The one hook this extension declares is a room renderer
(runtime/extension_hooks.py): when a room's ``raycast_camera`` says the
first-person view is on, ``render_room`` claims the room and draws it instead
of the engine's top-down pass. The engine still composites per-instance draw
events afterwards, so HUD actions (draw_score, draw_doom_hud, ...) land on top.

The heavy lifting lives in ``renderer.py`` and is imported lazily, on the
first claimed frame: the IDE loads extensions only for their schemas (see
events/plugin_loader.load_all_plugins) and never renders a room, so it should
not pay for -- or depend on -- a pygame import (same reason
plugins/audio_actions.py keeps pygame out of module scope).

This extension contributes, through the same declarative contract a single-file
plugin uses:

* ``PLUGIN_ACTIONS`` (actions.py) + ``PluginExecutor`` (handlers.py) — all four
  raycast actions (``set_facing_angle``, ``enable_raycast_view``,
  ``draw_minimap``, ``draw_doom_hud``), plus their HUD builders (hud.py), moved
  out of core in Stage B3;
* ``PLUGIN_ROOM_RENDERERS`` (below) — the room-render hook.

All raycast state (the camera config + the derived wall-edge caches) lives under
``room.extension_state["raycast"]`` (state.py, Stage B3b), so ``GameRoom`` holds
nothing raycast-specific. The one thing left in core by design is
``facing_angle`` — a general ``GameInstance`` look-direction property, not
inherently 3D (B4).
"""

from .actions import PLUGIN_ACTIONS
from .handlers import PluginExecutor
from .state import peek_camera


def render_room(room, screen):
    """Room-renderer hook: claim the room iff its raycast camera is enabled.

    Uses a NON-creating peek at room.extension_state — this runs for every room
    in the game, raycast or not, and must not stamp raycast state onto rooms
    that never enabled the view.
    """
    cfg = peek_camera(room)
    if not cfg or not cfg.get('enabled'):
        return False                     # not a raycast room -- engine draws it
    from . import renderer
    renderer.render_raycast_view(room, screen)
    return True


PLUGIN_ROOM_RENDERERS = [render_room]
