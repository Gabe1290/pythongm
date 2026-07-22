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

Still in core for now (Stage B3 moves them): the four raycast actions
(enable_raycast_view, set_facing_angle, draw_minimap, draw_doom_hud) and the
``raycast_camera`` / wall-cache state they keep on the room.
"""


def render_room(room, screen):
    """Room-renderer hook: claim the room iff its raycast camera is enabled."""
    cfg = getattr(room, 'raycast_camera', None)
    if not cfg or not cfg.get('enabled'):
        return False                     # not a raycast room -- engine draws it
    from . import renderer
    renderer.render_raycast_view(room, screen)
    return True


PLUGIN_ROOM_RENDERERS = [render_room]
