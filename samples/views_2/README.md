# Views — Level 2

A **split-screen co-op** demo: the 2400×800 room is shown as two side-by-side
cameras in one 800×600 window. The **left half** (view 0) follows **player 1**
(orange, arrow keys); the **right half** (view 1) follows **player 2** (teal,
WASD). Each player explores the shared room in their own lane and collects
coins — you watch both at once.

**Where this fits:** the fourth sample family's second level. `views_1`
introduced a single scrolling camera; `views_2` introduces **multiple
viewports at once** — the other headline capability of GameMaker views. See
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
for the full progression. Movement reuses the grid idiom from `maze_1`/`views_1`.

**Sound & music:** none — no sound files are bundled with this sample.

## How to play

- **Player 1 (orange):** arrow keys — moves in the **left** view.
- **Player 2 (teal):** `W` `A` `S` `D` — moves in the **right** view.
- Both move one grid cell (32px) at a time; walls (`obj_wall`) are solid. A
  central divider with gaps separates the two lanes.
- **Objective:** collect the 18 coins (`obj_coin`) — either player can grab
  any coin; each is worth 10 points (shown in the window caption).

## Why two players stop independently (a real gotcha)

Grid movement normally stops on the `nokey` event (fires when *no* key is
pressed). But key state is tracked globally across all instances, so with two
players `nokey` only fires when **both** release everything — player 2 would
keep gliding while player 1 holds a key. So each player instead stops via
**`keyboard_release`** for **its own** keys (arrows for P1, WASD for P2), which
fires per-key and per-object. That's the difference from `views_1`'s single
player, which can use `nokey` safely.

## How the split screen is set up

An invisible controller, `obj_camera`, configures both views in its **create**
event (registered `enable_views` + two `set_view` actions), and the same config
is baked into the room's `views` block for frame-0 correctness on export:

- **view 0** — `view`/`port` `400×600`, `port_x` 0 (left half), `follow`
  `obj_player1`.
- **view 1** — `view`/`port` `400×600`, `port_x` 400 (right half), `follow`
  `obj_player2`.

Both views are **1:1** (view size == port size) and split **left/right**
(`port_y` 0, full height). That matters for cross-target consistency: desktop
and HTML5 render each view 1:1 (they clip + offset, they do **not** scale a
view to its port), and a left/right split avoids the Kivy (y-up) vs
desktop/HTML5 (y-down) `port_y` flip. A zoomed-out minimap (view larger than
its port) is deliberately **not** used here — it would only scale correctly on
Kivy.

## Project structure

| File | Purpose |
|---|---|
| `project.json` | Manifest — window/room settings, embedded assets, and the two-view `views` config |
| `rooms/room0.json` | The 2400×800 room (284 instances: camera, walls, 2 players, 18 coins) + its `views` block |
| `objects/obj_camera.json` | Invisible controller: create-event `enable_views` + two `set_view` |
| `objects/obj_player1.json` | Player 1 (arrow keys); grid movement + `keyboard_release` stop |
| `objects/obj_player2.json` | Player 2 (WASD); grid movement + `keyboard_release` stop |
| `objects/obj_coin.json` | Collectible — destroyed by either player, adds 10 |
| `objects/obj_wall.json` | Static solid wall |
| `sprites/` | `spr_player1.png` (orange), `spr_player2.png` (teal), `spr_wall.png`, `spr_coin.png` + `.json` metadata |
| `CREDITS.txt` | Asset licensing notice |

## Objects

| Object | Role | Key events |
|---|---|---|
| `obj_camera` | Invisible controller; enables + configures both views | create (`enable_views`, 2× `set_view`) |
| `obj_player1` | Left-view player (arrows) | keyboard (up/down/left/right/nokey), keyboard_release (per key), collision_with_obj_wall |
| `obj_player2` | Right-view player (WASD) | keyboard (w/a/s/d/nokey), keyboard_release (per key), collision_with_obj_wall |
| `obj_coin` | Collectible worth 10 | collision_with_obj_player1, collision_with_obj_player2, destroy (`set_score` +10) |
| `obj_wall` | Static solid wall / camera boundary | (none — passive collider) |

## Assets

4 sprites (`spr_player1`, `spr_player2`, `spr_wall`, `spr_coin`, each 32×32,
single-frame, pixel-precise), 0 sounds. All flat-color CC0 art generated for
this sample — see `CREDITS.txt`.

## Things to tweak

- **Split direction** — this uses a left/right split (`port_x` 0 and 400,
  `port_y` 0, full height). A top/bottom split would put the halves at
  different `port_y`; note that renders at a different vertical position on
  Kivy (y-up) vs desktop/HTML5 (y-down), so left/right is the portable choice.
- **View width** — each view is `400` wide (half the window). Widen the window
  or narrow the views to change how much room each player sees.
- **Borders** — `hborder` 120 / `vborder` 150 set each camera's dead-zone.

## Export status

- **Desktop (pygame):** the reference — `tests/test_views_2_sample.py` loads the
  sample, runs `obj_camera`'s create event, and asserts the two cameras scroll
  **independently** (moving one player doesn't move the other's view) and clamp
  at the room edge, plus coin scoring and the per-player `keyboard_release` stop.
- **Web (HTML5):** `engine.js` renders every visible view (per-view clip +
  1:1 translate); the two-view config round-trips into the export.
- **Mobile (Kivy/Android):** the exporter renders the room into an Fbo and
  blits each visible view's region into its screen port
  (`tests/test_kivy_views.py` covers the multi-view render). Same *Known
  limitation* as `views_1`: the Kivy code generator doesn't emit the
  `enable_views`/`set_view` actions themselves, so the camera is driven by the
  baked room config (which this sample provides).
- Cross-target scroll-math agreement is pinned by
  `tests/test_views_export_parity.py`.

Exposed in the IDE's Welcome tab as "Views — Level 2" (`widgets/welcome_tab.py`).
