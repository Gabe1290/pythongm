# 2.5D Raycast View — a worked extension

This folder is a real PyGameMaker feature that lives **outside** the core
engine: the Doom/Wolfenstein-style first-person view the `raycast_1`–`raycast_5`
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
| `actions.py` | The "3D View" action **schemas** (`PLUGIN_ACTIONS`): `set_facing_angle`, `enable_raycast_view`, `draw_minimap`, `draw_doom_hud`, `set_billboard_rotation`, `set_floor_height`, `set_ceiling_height`, `set_floor_texture`, `go_to_room_seamlessly`. |
| `handlers.py` | The action **handlers** — what each of those does at runtime. |
| `hud.py` | The minimap + DOOM-bar geometry builders (`build_minimap_commands`, `build_doom_hud_commands`), the single source the exports mirror. |
| `state.py` | The per-room state helper — all raycast state lives under `room.extension_state["raycast"]`. |
| `heights.py` | Stairs: the floor-height map built every frame from the step instances (`set_floor_height`), and the vertical model (eye height, wall height, texture tile). No pygame. |
| `climbing.py` | Stairs: the climbing rule (`max_step`, sliding along ledges, eased view height, and the view never rising above a low ceiling) as two frame hooks (`PLUGIN_FRAME_UPDATES`). No pygame. |
| `teleport.py` | **Go to Room Seamlessly**: the pending arrival and the `after_collision` hook that applies it before the new room's first frame is drawn. No pygame. |
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

## Stairs

A room with at least one **step** (a non-solid instance that ran
`set_floor_height`) is drawn by a front-to-back *column walk* instead of "one
wall strip per column": the ray keeps going past steps, each rise in floor
height is drawn as a riser, a drop hides the lower floor behind its edge, and
the wall that stops the ray is drawn only down to what stands in front of it.
The floor of such a room is cast column by column, each pixel at its own
tread's height. A room without steps never takes this path — it renders
byte-for-byte as before. Climbing (`climbing.py`) is a pure frame hook: it
undoes a move whose floor rises more than `max_step`, one axis at a time.
The HTML5 and Kivy ports follow the same structure and are pinned by
`tests/test_html5_raycast_stairs.py` and `tests/test_kivy_raycast_stairs.py`.
The design, the decisions and the proofs are in
`docs/RAYCAST_STAIRS_PLAN.md`; the `raycast_5` sample is built around it.

## Floor textures by area

A **Set Floor Texture** patch (`heights.build_floor_textures`: cell -> sprite name,
later patch wins, blank and solid ignored) gives ground-level cells their own floor
texture. It does NOT switch to the column walk: a flat room casts through
`_cast_floor_cells` (`cast_floor_plane`'s rows with a per-cell lookup; the original
loop runs unchanged when there are no patches), a room with steps reads the patch in
`cast_stairs_floor` for ground treads only (raised cells keep the step's Top
Texture). Patches are geometry (`is_geometry`): never billboards, never movers.
HTML5: `buildFloorTextures` / `castFloorCells`; Kivy: `_raycast_build_floor_textures`
/ `_floor_cells_buffer`.

## Low ceilings and the seamless jump

A **Set Ceiling Height** marker (`heights.build_ceiling_heights`: lowest marker wins,
each cell clamped to floor + eye + 4 px) switches a room to a *two-clip* column walk
(`layout_column_ceilings`): ceiling spans and lintels from the top, treads and
risers from the bottom. Only the lowered spans are cast textured
(`cast_ceiling_spans`); the room's own flat / sky / plane ceiling pass stays
underneath. **Go to Room Seamlessly** (`teleport.py`) records the camera's offset
from a marker object, its facing, speed, held keys and eased view height, asks for
an ordinary instant room change, and applies the arrival in the `after_collision`
hook of the iteration that changes room -- after the new room's Create events and
before the frame is drawn (the first `before_step` of the new room is too late on
desktop). The HTML5 port applies it once the new room has run its Create step and
shows the pre-change frame in between; the Kivy port applies it at the head of the
scene constructor's first overlay call. Design, decisions, corrections and proofs:
`docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md`; the `raycast_6` sample uses both.

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
