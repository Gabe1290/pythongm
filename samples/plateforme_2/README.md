# Platform — Level 2

A side-scrolling platformer imported from GameMaker 8.x (`samples/plateforme_2.gmk`).
Compared to a minimal first level, this one steps up the object roster from a
lone player + single block to four objects (a base platform plus horizontal and
vertical size variants inheriting from it) arranged into a 126-instance room
built from a snow-themed autotile tileset, rather than a couple of hand-placed
blocks.

**Where this fits:** part of the `plateforme_*` family, and — unlike the
minimal `plateforme_1` — this is where the **tiled background** shows up:
127 individually-placed background tile chunks (the room's `tiles` array)
plus a gradient background image (`fond_degrade`), layered under the solid
brick *objects* that still handle collision. This is the step
`plateforme_*` adds beyond `maze_*`; see
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
for the full progression.

**Sound & music:** none — no sound files are bundled with this sample.

## How to play

- **Left / Right arrow** — move the penguin (`obj_personnage`) left/right.
- **Up arrow** — jump, but only while standing on a solid platform (checked via
  a collision test one pixel below the player).
- **Objective** — there is no goal/flag object in this sample; it's a
  platforming layout to explore/traverse across the `obj_brique*` platforms.
- **Lose condition** — none is defined (no hazards, no killer objects, no
  fall-death check); the room's bottom row of bricks acts as a floor.

## Project structure

| File | Purpose |
| --- | --- |
| `project.json` | Project manifest — window/room settings, embedded asset copies. |
| `rooms/niveau_01.json` | The one room: 800×640, 126 instances + 127 background tiles. Source of truth for room contents (`project.json`'s embedded `instances` list is empty). |
| `objects/*.json` | Per-object side files for the 4 objects; identical to `project.json`'s embedded copies as of this writing. |
| `sprites/` | 5 sprite assets (player walk strips + solid platform blocks). |
| `backgrounds/` | Snow tileset (`tuiles_neige.png`, used as an autotile source) and a small vertical gradient (`fond_degrade.png`) stretched as the room background. |
| `CREDITS.txt` | Licensing notice for the sprite/background art (see Assets below). |

## Objects

| Object | Role | Key events |
| --- | --- | --- |
| `obj_personnage` | Player (penguin) — movement, jump, gravity, ground detection | create, step, collision_with_obj_brique, keyboard (left, right, up), keyboard_release (LEFT, RIGHT) |
| `obj_brique` | Base solid platform block (32×32) | none (no events; solid flag only) |
| `obj_brique_h` | Wide solid platform variant (32×16), child of `obj_brique` | none |
| `obj_brique_v` | Narrow solid platform variant (8×16), child of `obj_brique`; defined but not placed in `niveau_01` | none |

## Assets

5 sprites (`spr_pingus_dr`/`spr_pingus_ga` 8-frame walk strips, plus three
solid-color placeholder blocks at 32×32 / 32×16 / 8×16) and 2 backgrounds; no
sounds. The sprite and background art is adapted from the Pingus project
(GPL-3.0-or-later) — see `CREDITS.txt` for full attribution and license
terms; this README does not restate or add to those claims.

## Things to tweak

- Player horizontal speed is a flat `hspeed = 4` in the keyboard events.
- Jump impulse is `vspeed = -10`; fall gravity is `0.45` (applied only while
  airborne), with a terminal-velocity cap at `vspeed = 24`.
- Room size is 800×640 at `room_speed = 30`.

## Export status

This sample is listed in `tools/smoke_run_samples.py`'s `SAMPLES` list, so it
gets a headless smoke pass (the real game loop run for ~180 frames with
injected keyboard input) on every run of that harness. No per-export-target
(Kivy/HTML5) verification has been done for this sample specifically. It is
exposed in the IDE's Welcome tab as "Platform — Level 2"
(`widgets/welcome_tab.py`).
