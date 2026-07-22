# 2.5D Raycast View — a worked extension

This folder is a real PyGameMaker feature that lives **outside** the core
engine: the Doom/Wolfenstein-style first-person view the `raycast_1`–`raycast_4`
samples use. It is here to be read. If you want to see how someone adds a whole
new way of drawing a room to an IDE, open the four files below top to bottom.

## What it does

A normal PyGameMaker room is drawn top-down: backgrounds, tiles, then each
instance's sprite. This extension replaces that picture, for rooms that ask for
it, with a first-person 3D projection cast from the player's position and facing
direction — walls as vertical strips, a textured floor and ceiling, a panning
sky, and billboard sprites for pickups and monsters. The game's *logic*
(movement, collisions, events) is untouched; only the picture changes.

## The files

| File | What's in it |
|---|---|
| `extension.json` | The manifest. Name, version, and `enabled: true`. Its presence is what marks this folder as an extension. |
| `__init__.py` | The entry point — ~30 lines. Declares the one hook this extension uses and decides, per room, whether to claim the drawing. |
| `renderer.py` | The drawing itself: the DDA raycaster, wall/floor/sky/billboard passes, and the shared shading constants. This is the big file, and it is ordinary Python. |
| `README.md` | This file. |

## How it hooks in

Most plugins only add **actions**. Drawing a room is different, so core grew one
extra seam for it — a *room renderer* (see `runtime/extension_hooks.py`). An
extension declares one the same declarative way it declares actions:

```python
# __init__.py
def render_room(room, screen):
    cfg = getattr(room, 'raycast_camera', None)
    if not cfg or not cfg.get('enabled'):
        return False          # not a raycast room — let the engine draw it
    from . import renderer
    renderer.render_raycast_view(room, screen)
    return True               # I drew this room

PLUGIN_ROOM_RENDERERS = [render_room]
```

The contract is small:

- return **`True`** only if you actually drew the room. Core then skips its own
  top-down pass but **still runs the per-instance draw-event pass afterwards**,
  so HUD actions (`draw_score`, `draw_doom_hud`, …) composite on top;
- return **`False`** to decline, and core draws the room the normal way;
- a renderer that raises is logged and skipped — a broken extension can't take
  the game down. Core just falls back to its own rendering.

That is the whole integration surface. Everything else in `renderer.py` is the
feature.

## What this extension reads from `room`

The renderer takes a `room` and draws into a `screen`. Everything it needs is
ordinary `GameRoom` API — none of it is owned by this extension:

- `room.instances`, `room.parse_color(...)`, `room._find_first_instance(...)`,
  `room._sprite_top_left(...)`, `room._all_sprites` — generic engine helpers;
- `room.raycast_camera` plus the derived wall-edge caches
  (`_raycast_v_walls` / `_raycast_h_walls` / the parallel sprite maps /
  `_raycast_cell_size`). Those are still set by the four raycast **actions**,
  which — for now — remain in core (`runtime/action_executor.py`):
  `enable_raycast_view`, `set_facing_angle`, `draw_minimap`, `draw_doom_hud`.
  A later stage moves the actions here too, with their state living in
  `room.extension_state` instead.

## What is deliberately NOT here

- **The actions.** They are still core, so a game's saved JSON keeps working and
  the exporters (which key off action *names*, not this code) are untouched.
- **The HTML5 and Kivy renderers.** Each export target hand-writes its own copy
  of this raycaster (`export/HTML5/templates/engine.js`,
  `export/Kivy/kivy_exporter.py`). They are pinned to this file's numbers by
  `tests/test_raycast_export_parity.py`. Moving them here is a possible later
  step; it is build-system plumbing, not a readable example, so it was left out.

See `docs/RAYCAST_EXTENSION_PLAN.md` for the full staging and the rationale.

## Turning it off

It ships enabled. To switch it off without editing files, set the `extensions`
config key (see `extensions/README.md`):

```json
"extensions": { "raycast_2_5d": false }
```

With it disabled, a room that enables the raycast camera simply renders
top-down — the actions still exist, but nothing claims the drawing.
