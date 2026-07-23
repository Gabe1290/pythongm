# 2.5D Raycast View — a worked extension

This folder is a real PyGameMaker feature that lives **outside** the core
engine: the Doom/Wolfenstein-style first-person view the `raycast_1`–`raycast_4`
samples use. It is here to be read. If you want to see how someone adds a whole
new way of drawing a room to an IDE — and export it to the web and Android too —
open the files below top to bottom.

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
| `__init__.py` | The entry point. Declares the room-renderer hook and decides, per room, whether to claim the drawing. |
| `renderer.py` | The drawing itself: the DDA raycaster, wall/floor/sky/billboard passes, and the shared shading constants. The big file, ordinary Python. |
| `actions.py` | The four "3D View" action **schemas** (`PLUGIN_ACTIONS`). |
| `handlers.py` | The action **handlers** — what `enable_raycast_view` / `set_facing_angle` / `draw_minimap` / `draw_doom_hud` do at runtime. |
| `hud.py` | The minimap + DOOM-bar geometry builders (`build_minimap_commands`, `build_doom_hud_commands`), the single source the exports mirror. |
| `state.py` | The per-room state helper — all raycast state lives under `room.extension_state["raycast"]`. |
| `export_html5.js` | The **HTML5** port of the renderer + actions, injected into the exported `engine.js` (Stage C). |
| `export_kivy.py` | The **Kivy** port: `SCENE_CODE` (renderer), `BASE_OBJECT_CODE` (`_draw_minimap`), and `ACTION_CODEGEN` (the action codegen), injected into the Kivy export. |
| `README.md` | This file. |

## How it hooks in

Most plugins only add **actions**. Drawing a room is different, so core grew one
extra seam for it — a *room renderer* (see `runtime/extension_hooks.py`). An
extension declares one the same declarative way it declares actions:

```python
# __init__.py
def render_room(room, screen):
    cfg = peek_camera(room)   # non-creating read of room.extension_state["raycast"]
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
- `room.extension_state["raycast"]` — everything raycast-specific: the camera
  config the actions set, plus the derived wall-edge caches. Reached through
  `state.py`'s `raycast_state(room)` (get-or-create) / `peek_camera(room)`
  (non-creating). Core's `GameRoom` carries **nothing** raycast-specific.

## The whole feature is here now

Later stages moved everything that used to be in core into this folder:

- **The actions** — schemas (`actions.py`), handlers (`handlers.py`) and the HUD
  builders (`hud.py`). They register through the ordinary plugin mechanism, so
  core's `ACTION_TYPES` enumerates no raycast action.
- **The per-room state** — under `room.extension_state["raycast"]` (`state.py`).
- **The HTML5 and Kivy export renderers** — `export_html5.js` and
  `export_kivy.py`. Each export engine grew a *generic* seam (a room-renderer
  registry + an action registry/codegen hook + a code-injection marker), and the
  raycast port lives here, injected at export time. `engine.js`,
  `kivy_exporter.py` and `code_generator.py` now name no raycast code.
  `tests/test_raycast_export_parity.py` still pins the three ports to the same
  numbers; `tests/test_export_raycast_ownership.py` guards that none of it
  leaks back into an export engine.

## What is deliberately NOT here

- **`facing_angle`.** It stays a plain `GameInstance` attribute in core — a
  persistent look direction isn't inherently 3D, and the expression parser
  references it by name (`set_direction_speed(direction="facing_angle")`). The
  *action* that writes it (`set_facing_angle`) moved here; the attribute did not.

See `docs/RAYCAST_EXTENSION_PLAN.md` for the full staging and the rationale.

## Turning it off

It ships enabled. To switch it off without editing files, set the `extensions`
config key (see `extensions/README.md`):

```json
"extensions": { "raycast_2_5d": false }
```

With it disabled, a room that enables the raycast camera simply renders
top-down — the actions still exist, but nothing claims the drawing.
