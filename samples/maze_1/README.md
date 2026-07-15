# Maze — Level 1

A top-down grid maze game: guide the player sprite through a wall-lined maze
to reach the goal tile, which advances to the next room. This is a native
pygm2 project (no sibling `.gmk` file — its assets were originally brought in
via a GameMaker 8.x import, per CREDITS.txt, but the project itself is
authored/saved in pygm2's own JSON format).

**Where this fits:** `maze_*` is the first of three sample families in a
rough authoring-technique progression (built-in objects/sprites →
`plateforme_*`'s added tiled backgrounds → `match3_*`'s pure-script
`execute_code` games) — see [`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
for the full picture. This sample uses only GameObjects + sprites, no
background image and no room-level tiles.

**Sound & music:** none — no sound files are bundled with this sample.

## How to play

- **Arrow keys** (up/down/left/right) move the player one grid cell (32px) at
  a time; movement is grid-snapped via `test_alignment`/`snap_to_grid`
  (32×32 grid).
- Walls (`obj_wall`) are solid — walking into one stops the player and
  re-snaps them to the grid.
- **Objective:** reach the goal tile (`obj_goal`). Touching it advances to
  the next room if one exists, or restarts the game if there isn't one.
- **Debug shortcuts:** pressing `N` on the goal jumps to the next room (if
  any); pressing `P` jumps to the previous room (if any) — same
  advance/restart logic as touching the goal.
- No lives/score/health tracking is used in this sample (health is reset via
  `set_health` on room advance, but never displayed).

## Project structure

| File | Purpose |
|---|---|
| `project.json` | Project manifest — window/room settings and embedded copies of all assets |
| `rooms/room0.json` | Maze layout for room 0 (131 instances: walls, player start, goal) |
| `rooms/room1.json` | Maze layout for room 1 (130 instances) |
| `objects/obj_person.json` | Player object definition (source of truth; matches the embedded copy in `project.json`) |
| `objects/obj_goal.json` | Goal object definition |
| `objects/obj_wall.json` | Wall object definition |
| `sprites/` | `spr_person.png`, `spr_wall.png`, `spr_goal.png` + their `.json` metadata |
| `CREDITS.txt` | Asset licensing notice for this sample |

The `objects/*.json` side files were checked against `project.json`'s
embedded copies and are identical in this sample — no staleness found.

## Objects

| Object | Role | Key events |
|---|---|---|
| `obj_person` | Player-controlled character; grid-based movement | create-implicit via keyboard, keyboard (down, right, up, left, nokey), collision_with_obj_wall |
| `obj_goal` | Level exit; advances/restarts on touch or debug key | collision_with_obj_person, keyboard_press (p, n) |
| `obj_wall` | Static solid maze wall, blocks movement | (none — passive collider only) |

## Assets

3 sprites (`spr_person`, `spr_wall`, `spr_goal`, each 32×32, single-frame,
pixel-precise collision), 0 sounds. Licensing: `spr_person.png` and
`spr_wall.png` are CC0 (public domain) works by the pygm2 author;
`spr_goal.png`'s provenance is not yet documented — see `CREDITS.txt` in
this folder and `docs/ASSET_LICENSES.md` in the repo root for the full
picture.

## Things to tweak

- Player move speed is `4` (grid cells/step) while the wall-bump stop uses
  speed `8` — both are hardcoded per-keypress action parameters in
  `obj_person`.
- Grid size is `32` (matches the 32×32 sprites); changing it needs matching
  edits to `snap_to_grid`/`test_alignment` calls and the room layouts.
- Rooms are `480×480` at `room_speed: 30` — small, single-screen mazes with
  no scrolling.
- The `N`/`P` debug keys on `obj_goal` let you skip between room0/room1
  without touching the goal — handy for testing but easy to trip over
  accidentally during play.

## Export status

Covered by the headless smoke-test suite (`tools/smoke_run_samples.py`,
which lists `maze_1` and runs it for ~180 frames with injected keyboard
input); not individually re-verified per export target (Kivy/Web). Exposed
in the IDE's Welcome tab as "Maze — Level 1" (`widgets/welcome_tab.py`).
