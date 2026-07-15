# Platform — Level 1

A minimal side-scrolling platformer imported from GameMaker 8.x
(`samples/plateforme_1.gmk`). The player-controlled ball (`obj_balle`) climbs
a single screen of brick platforms (`obj_brique`) using GameMaker-style
`if_collision` probes to move in 4px/frame steps and only fall under gravity
when nothing solid is directly beneath it — a hand-rolled AABB movement
scheme rather than the engine's built-in physics.

**Where this fits:** part of the `plateforme_*` family, but at its
minimum — unlike `plateforme_2`/`plateforme_3`, this level has no
background image and **no tiled background** (the room's `tiles` array is
empty); it's built from GameObjects + sprites only, same as `maze_1`. See
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
for how the family as a whole compares to `maze_*` and `match3_*`.

**Sound & music:** none — no sound files are bundled with this sample.

## How to play

- **Left / Right arrow** — move the ball 4px per keypress, blocked by solid
  bricks.
- **Up arrow** — jump (sets `vspeed` to -10), only while standing on a solid
  brick.
- There is no explicit goal object, coin, or exit in this level — it's a
  vertical brick maze to climb. There's also no monster/hazard object, so
  there is no lose condition; it's free exploration of the collision/gravity
  mechanic.

## Project structure

| File | Purpose |
|---|---|
| `project.json` | Project manifest — window/room settings, embedded asset copies (see note below). |
| `rooms/niveau_01.json` | The single room: 800×640, 120 instances (mostly `obj_brique` walls/platforms plus one `obj_balle`). |
| `objects/obj_balle.json` | Player ball logic (movement, gravity, jump). |
| `objects/obj_brique.json` | Static solid brick, no events. |
| `sprites/` | `spr_balle.png` (ball) and `spr_32x32_noir.png` (brick), each with a `.json` sidecar. |

`objects/*.json` and `rooms/niveau_01.json` are the current per-asset side
files; their content matches what's embedded in `project.json` for this
sample (no divergence found), but per repo convention the side files are
the source of truth if the two ever disagree.

## Objects

| Object | Role | Key events |
|---|---|---|
| `obj_balle` | Player-controlled ball; gravity, collision-aware movement, jump | create (none defined), step, collision_with_obj_brique, keyboard (left, right, up) |
| `obj_brique` | Static solid platform/wall tile | *(none — no events defined)* |

## Assets

2 sprites (`spr_balle`, `spr_32x32_noir`), 0 sounds. Both sprites are
derivative works of the Pingus game's artwork, GPL-3.0-or-later licensed —
see `CREDITS.txt` in this folder for the full notice and upstream artist
credits; do not treat them as covered by the IDE's MIT license.

## Things to tweak

- `obj_balle` step event: gravity is `0.45` px/frame² and vspeed is capped
  at `24` — raise/lower either to change fall weight and terminal velocity.
- Jump impulse is a flat `vspeed = -10` (keyboard "up") — higher magnitude
  jumps higher.
- Horizontal move step is `4` px per keypress (keyboard "left"/"right") —
  larger steps feel snappier but can tunnel through thin gaps.
- Room is 800×640 with `room_speed: 30`; the brick layout in
  `rooms/niveau_01.json` can be re-arranged freely since `obj_brique` has no
  logic of its own.

## Export status

This sample is listed in `tools/smoke_run_samples.py`'s `SAMPLES` list, so
it's covered by the headless smoke-test harness (runs the real game loop for
~180 frames with injected keyboard input). It has not been separately
verified against the Kivy or Web export targets. It is exposed in the IDE's
Welcome tab as **"Platform — Level 1"** (`widgets/welcome_tab.py`).
