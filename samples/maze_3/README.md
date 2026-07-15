# Maze — Level 3

A five-maze grid dungeon crawl preceded by a title screen — the largest of
the three maze samples (17 objects / 6 rooms, vs. maze_2's 9 objects / 3
rooms). It keeps maze_2's collect-diamonds-then-reach-the-goal loop and
diamond-gated locked door, and adds three new mechanics that show up
progressively across the rooms: a push-block-into-hole puzzle (room5),
three patrol-monster archetypes that kill on touch (rooms 3–5), and a
hidden bomb trap that detonates a blast radius (room4). Unlike `maze_1`/
`maze_2`, this sample **is** a raw GameMaker 8.x import — its sibling
`samples/maze_3.gmk` is checked into the repo (no `.gmk` file exists for
`maze_1`/`maze_2`), and the pygm2 project alongside it is the converted
result.

**Where this fits:** part of the `maze_*` family — GameObjects + sprites
plus a static **background image** per room (like `maze_2`), no
room-level tiles. See
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
for how this compares to `plateforme_*` (adds tiled backgrounds) and
`match3_*` (pure-script, no built-in actions).

**Sound & music:** 8 sound files, and — unlike `maze_2`'s bundled-but-silent
set — genuinely wired up: 11 `play_sound`/`play_music` call sites across
`sound_background` (music), `sound_diamond`, `sound_door`, `sound_goal`,
`sound_dead`, `sound_explode`, `sound_hole`, and `sound_push`.

## How to play

- **Title screen (`room_start`):** press **SPACE** to start.
- **Arrow keys** move the player one 32px grid cell at a time
  (`test_alignment`/`snap_to_grid`, same pattern as `maze_1`/`maze_2`).
- **Objective:** collect diamonds (`obj_diamond`, +5 score each) and reach
  each room's `obj_goal`. Rooms 2–4 additionally gate the exit behind a
  locked `obj_door` that self-destroys only once every diamond in that room
  is gone (room3 has 4 doors that all open together). Room5 swaps diamonds
  for a push-block puzzle: walk into an `obj_block` to slide it one cell, or
  push it into an `obj_hole` to fill the pit (both are destroyed).
- **Hazards:** three monster archetypes patrol rooms 3–5 and kill on
  contact — `monster_all` bounces off walls in any of 4 directions,
  `monster_lr`/`monster_ud` patrol a single axis and reverse on a wall hit.
  Room4 also hides an `obj trigger` plate that, once touched, arms a nearby
  `obj_bomb` into an `obj_explosion` — its 16-frame blast destroys any
  non-solid instance (including the player) within a 64px radius.
- **Lose condition:** touching a monster costs a life (`sound_dead` +
  `set_lives -1` + `restart_room`); reaching 0 lives shows the high-score
  entry screen and restarts the game. Touching the last room's goal instead
  shows a congratulations message, awards +100, and ends the run the same
  way.
- **Debug keys** live on `controller_main`: **R** instantly costs a life and
  restarts the room; **N**/**P** jump to the next/previous room outright —
  useful for testing, but also a level-skip a player could stumble into.

## Project structure

| File | Purpose |
|---|---|
| `project.json` | Project manifest — window/room settings and embedded asset copies. Object copies match their side files exactly, but **room copies are stale**: each embedded room entry has 0 instances and an `_external_file` marker — the real instance data lives only in `rooms/*.json` |
| `rooms/room_start.json` | Title screen — 1 instance (`controller_start`) |
| `rooms/room1.json` | Maze 1 — 134 instances (walls, 4 diamonds, goal, player, controller) |
| `rooms/room2.json` | Maze 2 — 96 instances (+20 diamonds, 1 locked door) |
| `rooms/room3.json` | Maze 3 — 105 instances (+16 diamonds, 4 locked doors, all 3 monster archetypes, 6 monsters total) |
| `rooms/room4.json` | Maze 4 — 95 instances (+14 diamonds, 1 door, 4 `monster_lr`, 2 trigger/bomb trap pairs) |
| `rooms/room5.json` | Maze 5 — 99 instances (4 pushable blocks, 3 holes, 2 goals, 2 `monster_lr` — no diamonds or door) |
| `objects/*.json` | 17 object definitions — checked against `project.json`'s embedded copies and identical (no staleness). Note: `objects/obj trigger.json` has a literal space in its filename |
| `sprites/` | 16 sprites + metadata (see Assets) |
| `sounds/` | 8 sound files, all referenced from at least one object |
| `backgrounds/` | 2 backgrounds (`background_start.png` for the title room, `background_main.png` for the mazes) |
| `CREDITS.txt` | Asset licensing notice for this sample |

## Objects

**Player & controllers**

| Object | Role | Key events |
|---|---|---|
| `obj_person` | Player-controlled character; grid movement | keyboard (up/down/left/right/nokey), collision_with_obj_block, collision_with_monster_all/_lr/_ud, collision_with_wall_corner |
| `controller_start` | Title-screen controller; sets score/lives, starts music | create, keyboard (SPACE) |
| `controller_main` | In-maze HUD + debug keys; draws score/lives, ends the run on 0 lives | keyboard (R restart-cheat), no_more_lives, draw, keyboard_press (N/P room skip) |

**Walls & tiles**

| Object | Role | Key events |
|---|---|---|
| `wall_corner` | Base solid wall; parent of the other two wall types | (none — passive collider) |
| `wall_horizontal` | Horizontal wall segment (inherits `wall_corner`) | (none) |
| `wall_vertical` | Vertical wall segment (inherits `wall_corner`) | (none) |

**Collectibles, doors, goals & push-block puzzle (room5)**

| Object | Role | Key events |
|---|---|---|
| `obj_diamond` | Collectible; +5 score on pickup | destroy, collision_with_obj_person |
| `obj_door` | Locked gate; self-destroys once every diamond in the room is gone | step |
| `obj_goal` | Level exit; advances rooms or ends the game on the last room | collision_with_obj_person |
| `obj_block` | Pushable crate; slides one cell when walked into, or falls into a hole | collision_with_obj_person |
| `obj_hole` | Pit; destroys itself and any block pushed into it | collision_with_obj_block |

**Monsters & bomb trap (room4)**

| Object | Role | Key events |
|---|---|---|
| `monster_all` | Bounces off walls in any of 4 directions | create, collision_with_wall_corner |
| `monster_lr` | Patrols left-right, reverses on wall contact | create, collision_with_wall_corner |
| `monster_ud` | Patrols up-down, reverses on wall contact | create, collision_with_wall_corner |
| `obj trigger` | Hidden plate; on touch plays the explosion sound, morphs the paired `obj_bomb` into `obj_explosion`, self-destroys | collision_with_obj_person |
| `obj_bomb` | Inert placeholder standing in for an armed bomb until a trigger fires | (none) |
| `obj_explosion` | 16-frame blast; on spawn destroys non-solid instances within 64px, self-destroys at animation end | create, animation_end |

## Assets

16 sprites (mostly 32×32 single-frame, pixel-precise; `sprite_explosion` is
a 1536×96 16-frame strip with no precise flag), 2 backgrounds, 8 sounds —
all 8 sounds are referenced from at least one object, unlike `maze_2` where
none were wired up. Licensing/provenance for this sample's assets is
**undocumented** — see `CREDITS.txt` in this folder, which points to the
"Remaining maze assets" TODO in `docs/ASSET_LICENSES.md`. Do not assume CC0
or any other license for these files.

## Things to tweak

- `sprite_lives` (16×16) is a registered asset that's never drawn —
  `controller_main`'s `draw_lives` action actually uses `sprite_person` at
  0.7 scale, leaving `sprite_lives` orphaned (same category as `maze_2`'s
  `tiles.json`).
- The bomb trap's blast (`obj_explosion`'s create event) destroys the
  player via a plain `destroy_instance` in its radius check, bypassing the
  `sound_dead`/`set_lives`/`restart_room` path monsters use — catching the
  player leaves the run in an odd state rather than a clean death/restart.
- Monster speed is hardcoded `32/6` px/step across all three archetypes
  while the player moves at `4` — monsters aren't grid-snapped the way the
  player is, so their motion doesn't stay cell-aligned over time.
- The `R`/`N`/`P` debug keys on `controller_main` are live in the shipped
  controller (see How to play) — worth gating behind a debug flag if this
  sample is ever polished further.

## Export status

Covered by the headless smoke-test suite (`tools/smoke_run_samples.py`,
which lists `maze_3` and runs it for a fixed number of frames with injected
keyboard input); not individually re-verified per export target
(Kivy/Web). Exposed in the IDE's Welcome tab as "Maze — Level 3"
(`widgets/welcome_tab.py`).
