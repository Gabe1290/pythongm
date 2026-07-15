# Maze — Level 2

A top-down grid maze game with two playable mazes plus a title screen:
collect candies for score, then reach the exit to advance. It builds on
`maze_1`'s single-room maze/goal loop with a start screen, a collectible
(scored candy), and a locked door that only opens once the room's candies
are cleared. This is a native pygm2 project (no sibling `.gmk` file — its
assets were originally brought in via a GameMaker 8.x import, per
`CREDITS.txt`, but the project itself is authored/saved in pygm2's own
JSON format).

**Where this fits:** part of the `maze_*` family — GameObjects + sprites,
plus (unlike `maze_1`) a static **background image** per room
(`background_main`), no room-level tiles. See
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
for how this compares to `plateforme_*` (adds tiled backgrounds) and
`match3_*` (pure-script, no built-in actions).

**Sound & music:** 4 sound files are bundled (`sound_background.mid`,
`sound_diamond`/`door`/`goal.wav`) but **none of them are actually wired
up** — no object references `play_sound`/`play_music` anywhere, so the
game is silent in practice despite carrying audio assets. (Contrast with
`maze_3`, where the same-shaped sound set is genuinely played.)

## How to play

- **Title screen (`room_start`):** press **SPACE** to start
  (`controller_start`'s `keyboard_press` action calls `next_room`).
- **Arrow keys** (up/down/left/right) move the player one grid cell (32px)
  at a time; movement is grid-snapped via `test_alignment`/`snap_to_grid`
  (32×32 grid), same pattern as `maze_1`.
- **Objective:** collect the candies (`obj_diamond`, sprite `sprite_bonbon`)
  scattered around each maze — each is worth +10 score — then reach the
  goal (`obj_goal`). In `room2`, the exit is additionally blocked by a
  locked door (`obj_door`) that only destroys itself once every
  `obj_diamond` in the room is gone.
- Touching the goal advances to the next room (+100 score) if one exists;
  touching it in the last room (`room2`) awards +100, opens the
  high-score entry screen, and ends the game.
- **No lose condition:** no life/health-affecting action appears anywhere
  in this sample's objects — `starting_lives: 3` is set in the project
  settings but is never displayed or decremented.

## Project structure

| File | Purpose |
|---|---|
| `project.json` | Project manifest — window/room settings and embedded copies of all assets |
| `rooms/room_start.json` | Title screen — 1 instance (`controller_start`) |
| `rooms/room1.json` | First maze — 134 instances (walls, player, goal, 4 candies, `controller_main`) |
| `rooms/room2.json` | Second maze — 112 instances (walls, player, goal, 21 candies, locked door, `controller_main`) |
| `objects/*.json` | 9 object definitions — checked against `project.json`'s embedded copies and identical in this sample (no staleness found) |
| `sprites/` | 7 sprites (`sprite_person`, `sprite_bonbon`, `sprite_door`, `sprite_goal`, `sprite_wall_corner`, `sprite_wall_horizontal`, `sprite_wall_vertical`) + metadata; `tiles.json` is an orphan side file (not registered in `project.json`, image file missing — unused) |
| `backgrounds/` | `background_start.png` (title screen), `background_tiles.png` (tiled maze floor) |
| `sounds/` | 4 sound files (see Assets below) |
| `CREDITS.txt` | Asset licensing notice for this sample |

## Objects

| Object | Role | Key events |
|---|---|---|
| `obj_person` | Player-controlled character; grid-based movement | keyboard (down, right, up, left, nokey), collision_with_wall_corner |
| `wall_corner` | Base solid maze wall; parent object for the other two wall types | (none — passive collider only) |
| `wall_horizontal` | Solid horizontal wall segment (inherits from `wall_corner`) | (none — passive collider only) |
| `wall_vertical` | Solid vertical wall segment (inherits from `wall_corner`) | (none — passive collider only) |
| `obj_diamond` | Collectible candy; adds score on pickup | destroy, collision_with_obj_person |
| `obj_door` | Locked exit gate (room2 only); opens once all candies are gone | step |
| `obj_goal` | Level exit; advances to the next room or ends the game | collision_with_obj_person |
| `controller_start` | Title-screen controller; waits for the player to begin | create, keyboard_press (SPACE) |
| `controller_main` | In-maze HUD controller; draws the score | draw |

## Assets

7 sprites (32×32, single-frame, pixel-precise collision except `sprite_goal`
which has no explicit `precise` flag), 2 backgrounds, 4 sounds
(`sound_background.mid`, `sound_diamond.wav`, `sound_door.wav`,
`sound_goal.wav`). Licensing/provenance for all of this sample's assets is
**undocumented** — see `CREDITS.txt` in this folder, which points to the
"Remaining maze assets" TODO in `docs/ASSET_LICENSES.md`. Do not assume CC0
or any other license for these files.

## Things to tweak

- Player move speed is `4` (grid cells/step) while the wall-bump stop uses
  speed `8` — both are hardcoded per-keypress action parameters in
  `obj_person`, same as `maze_1`.
- All 4 bundled sound files are unreferenced — no object currently calls
  `play_sound`; wiring one up for candy pickup / door open / goal reached
  would be a natural next pass.
- Rooms are `480×480`–`480×512` at `room_speed: 30` — small, single-screen
  mazes with no scrolling.
- `sprites/tiles.json` is a leftover side file not registered as a project
  asset (its `sprites/tiles.png` doesn't exist) — safe to remove or ignore.

## Export status

Covered by the headless smoke-test suite (`tools/smoke_run_samples.py`,
which lists `maze_2` and runs it for ~180 frames with injected keyboard
input); not individually re-verified per export target (Kivy/Web). Exposed
in the IDE's Welcome tab as "Maze — Level 2" (`widgets/welcome_tab.py`).
