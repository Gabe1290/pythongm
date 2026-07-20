# Raycast — Level 3

The third Doom/Wolfenstein-style first-person level, built on the same **raycast
2.5D engine** as [`raycast_1`](../raycast_1/README.md) and
[`raycast_2`](../raycast_2/README.md) — complete on all three export targets
(desktop, HTML5, native/Kivy): textured walls, a panning sky, low-res textured
floor casting, and camera-facing billboard sprites.

Where `raycast_1` teaches *the first-person view itself* and `raycast_2` adds
*things happening in the view* (gems, a patrolling enemy, a gated exit),
`raycast_3` is about **state you can see while you play**: monsters cost
**health** rather than a life outright, medkits give it back, and a
**heads-up display** composited over the 3D view shows score, lives and a
health bar at all times.

That HUD is the reason this sample exists. Until 2026-07-20 the engine drew the
first-person view and then stopped, so a raycast game's score and lives appeared
only in the desktop window caption — invisible on the HTML5 and Kivy exports.
See [`docs/RAYCAST_HUD_PLAN.md`](../../docs/RAYCAST_HUD_PLAN.md) for that work
and [`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) for the engine.

A complete two-level game: cross each maze in first person, collect every gem
while surviving the monsters, and reach the gem-gated exit — the first (warm
brick) room leads to a second (cool crystal-cavern) room, and clearing that
wins. Available from the IDE's Welcome tab (*"Raycast — Level 3"*).

**Sound & music:** none — no sound files are bundled with this sample.

## How to play

- **Up / Down** — move forward / backward in whichever direction you're facing
  (continuous, not grid-snapped; walls block you).
- **Left / Right** — turn in place (rotates `facing_angle`, independent of
  movement — you can turn while standing still).
- **Collect the gems** — each adds 10 to the score, shown top-left.
- **Avoid the monsters** — touching one costs **25 health**, not a life. After a
  hit you get a short window of invulnerability (45 steps) so a monster walking
  through you can't drain the whole bar at once.
- **Grab the medkits** — the red cross boxes restore **40 health**, capped at
  full.
- **Run out of health** and you lose one life, the bar refills and the room
  restarts. Run out of **lives** and the game restarts.
- **Objective** — collect *all* the gems in a room, then reach its exit.
  Reaching it early just prompts you to collect the rest.

## The HUD

`obj_hud` draws it, in **screen space**, over the finished 3D frame:

| Element | Corner | Action |
|---|---|---|
| Score | top-left | `draw_score` |
| Lives | top-right | `draw_text` + `draw_lives` |
| Health bar | bottom-left | `draw_health_bar` |

Score and health sit in **opposite** corners on purpose: a health bar is wide
and a score string grows as you play, so stacking them invites a collision.

**`obj_hud` is `visible: true`, and that matters.** GameMaker does not run an
invisible instance's draw event — so the HUD cannot simply live on the
invisible camera controller (`obj_cam0`/`obj_cam1`). If you build your own HUD
and nothing appears, check that flag first.

## Project structure

| File | Purpose |
|---|---|
| `project.json` | Manifest — 640×480 window, both rooms, embedded asset copies |
| `rooms/room0.json` | Warm-brick maze: 15×15 cells / 480×480, 8 gems, 3 monsters, 3 medkits |
| `rooms/room1.json` | Crystal-cavern maze: the harder half — 10 gems, 5 monsters, only 2 medkits |
| `objects/obj_person.json` | Player/camera — movement, health damage + invulnerability alarm, death handling |
| `objects/obj_hud.json` | The heads-up display (see above) |
| `objects/obj_cam0.json`, `obj_cam1.json` | Per-room camera controllers, each carrying that room's texture theme |
| `objects/obj_gem.json` | Collectible, +10 score |
| `objects/obj_medkit.json` | Restores 40 health |
| `objects/obj_monster.json` | Patrolling billboard enemy |
| `objects/obj_goal.json`, `obj_goal_final.json` | Gem-gated exits: advance, and win |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Thin wall segments (32×8 and 8×32) |
| `sprites/` | 13 sprites, reused from `raycast_2` plus `spr_medkit` |

## The maze is generated, not hand-placed

`tools/gen_raycast_3_maze.py` builds both rooms with a recursive-backtracker
maze run through `raycast_1`'s thin edge-wall placement — 8px partitions centred
on cell boundaries, not 32px blocks filling a cell. Re-running it reproduces the
shipped rooms exactly, and a test asserts they haven't drifted, so the level
design stays reviewable and tweakable rather than being opaque data.
(`raycast_2`'s maze came from a throwaway script that was never committed, so
its rooms can't be regenerated — this one fixes that.)

The seeds are **chosen, not arbitrary**: `check_start()` asserts that the start
cell opens east (the player spawns there facing east, so a walled start means
beginning the game nose-to-wall) and that every cell is reachable.

## Things to tweak

- **Damage and healing:** `-25` in `obj_person`'s `collision_with_obj_monster`,
  `+40` in `obj_medkit`'s `destroy` event.
- **Invulnerability window:** the `45` steps on `alarm_0`. Shorter makes the
  game harsher; remove it and a monster overlapping you repeatedly will shred
  the bar.
- **Difficulty balance:** the per-room `counts` in the generator — monsters
  versus medkits is the main dial.
- **HUD layout:** the coordinates in `obj_hud`'s draw event. Keep score and
  health in opposite corners.
- **Themes:** the texture parameters on `obj_cam0`/`obj_cam1`.

## A note on collision timing

The runtime fires a collision event when two instances **start** overlapping,
not every frame they remain overlapping. Standing inside a monster therefore
costs one hit, not a hit per frame. The invulnerability alarm still earns its
place: it covers the repeated touch/untouch of a monster patrolling *through*
you, which is the case you actually meet while playing.

## Export status

Runs on all three targets. Covered by the headless smoke suite
(`tools/smoke_run_samples.py`) and by `tests/test_raycast_3_sample.py`, which
drives the real game loop: damage, the invulnerability window opening and
closing, death costing exactly one life, medkit healing and its cap, the
gem-gated exit, the room transition into the ice theme, and the HUD rendering
over the first-person view in **both** rooms.

The Kivy and HTML5 exports were verified to carry the whole loop —
`no_more_health`, `alarm_0`, `draw_health_bar`, `obj_hud` and `spr_medkit` all
survive codegen — but the per-target *visual* playtest is worth doing by eye
before a release.
