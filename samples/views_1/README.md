# Views — Level 1

A camera-scrolling demo: the room (2400×800) is **three times wider than the
800×600 window**, so a single screen can't show it all. The camera (view 0)
follows the player as they walk right, revealing the level a screen at a time —
the whole point of GameMaker-style **views**. Explore the wide room and collect
all 18 coins.

**Where this fits:** this is the fourth sample family, distinct from the three
authoring-technique families (`maze_*` → `plateforme_*` → `match3_*`). What it
introduces is not a new authoring *style* but a new engine capability: a
**room larger than the window** with a **scrolling camera**. See
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
for the full progression. Mechanically it reuses `maze_1`'s grid movement
(built-in `test_alignment`/`snap_to_grid`/`start_moving_direction` actions) and
adds exactly one new thing: the camera, enabled from the player's **create**
event with the registered `enable_views` + `set_view` actions.

**Sound & music:** none — no sound files are bundled with this sample.

## How to play

- **Arrow keys** move the player one grid cell (32px) at a time (grid-snapped
  movement, same as `maze_1`).
- Walls (`obj_wall`) line the room border and form a few interior pillars;
  they are solid and stop the player.
- The **camera follows the player**: walk toward a screen edge and the view
  scrolls to keep you in frame, clamping at the room edges so you never see
  past the wall border.
- **Objective:** collect all 18 coins (`obj_coin`). Each is worth 10 points
  (shown in the window caption).

## How the camera is set up

The player's **create** event runs two registered actions (no raw
`execute_code`):

1. `enable_views` — turns the view system on for the room.
2. `set_view` — configures **view 0**: `view_w`/`view_h` `800×600`, port at
   `(0,0)` sized `800×600`, `follow` = `obj_player`, `hborder` 240 /
   `vborder` 180 (the dead-zone before the camera scrolls), no scroll-speed
   cap. The same config is also baked into the room's `views` block, so the
   camera is correct from the first frame on every export target.

## Project structure

| File | Purpose |
|---|---|
| `project.json` | Project manifest — window/room settings, embedded asset copies, and the room's `views` config |
| `rooms/room0.json` | The 2400×800 room (245 instances: wall border + pillars, player, 18 coins) and its `views` block |
| `objects/obj_player.json` | Player: grid movement + the create-event camera setup |
| `objects/obj_coin.json` | Collectible: destroyed on player touch, adds 10 to the score |
| `objects/obj_wall.json` | Static solid wall |
| `sprites/` | `spr_player.png`, `spr_wall.png`, `spr_coin.png` + their `.json` metadata |
| `CREDITS.txt` | Asset licensing notice |

## Objects

| Object | Role | Key events |
|---|---|---|
| `obj_player` | Player character; grid movement + enables/configures the camera | create (`enable_views`, `set_view`), keyboard (down/right/up/left/nokey), collision_with_obj_wall |
| `obj_coin` | Collectible worth 10 points | collision_with_obj_player (`destroy_instance` self), destroy (`set_score` +10) |
| `obj_wall` | Static solid wall / camera-clamp boundary | (none — passive collider) |

## Assets

3 sprites (`spr_player`, `spr_wall`, `spr_coin`, each 32×32, single-frame,
pixel-precise collision), 0 sounds. All three are simple flat-color CC0 art
generated for this sample — see `CREDITS.txt`.

## Things to tweak

- **Room size** (`2400×800` in `rooms/room0.json`) — make it wider/taller to
  scroll further; the camera clamps to whatever the room is.
- **Borders** (`hborder` 240 / `vborder` 180 in the `set_view` action *and*
  the room's `views` block) — smaller borders let the player get closer to the
  edge before the camera moves; larger keeps them more centered.
- **Scroll speed** — `hspeed`/`vspeed` are `-1` (instant follow). Set them to a
  positive pixels-per-step value for a lagging, smoothed camera.
- **Coins** — add/remove `obj_coin` instances in `rooms/room0.json`.

## Export status

- **Desktop (pygame):** the reference target — verified by
  `tests/test_views_1_sample.py`, which loads this sample, runs the player's
  create event, and asserts the camera scrolls and clamps as the player walks
  the full width.
- **Web (HTML5):** the exported `engine.js` carries the same 8-view camera
  (`tests/test_html5_views.py`, Chromium-verified during development); this
  sample's `views` config and create-event `set_view` both round-trip into the
  export.
- **Mobile (Kivy/Android):** the exported scene renders the whole room into an
  Fbo and blits each visible view's region into its screen port, with the OS
  window sized to the view (not the room) so the camera shows a true scrolling
  slice and supports multiple viewports (`tests/test_kivy_views.py`). *Known
  limitation:* the Kivy code generator does not yet emit the
  `enable_views`/`set_view` **actions** themselves, so a game that reconfigures
  the camera dynamically at runtime (rather than via the baked room config, as
  this sample does) would not update on Kivy. The baked static follow this
  sample uses works.
- Cross-target agreement on the scroll math is pinned by
  `tests/test_views_export_parity.py`.

Exposed in the IDE's Welcome tab as "Views — Level 1"
(`widgets/welcome_tab.py`).
