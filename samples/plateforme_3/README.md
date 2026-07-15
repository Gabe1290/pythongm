# Platform — Level 3

A side-scrolling platformer imported from GameMaker 8.x (`samples/plateforme_3.gmk`).
It's the largest of the three platform samples by far: 2 objects
(plateforme_1) → 4 objects (plateforme_2) → **15 objects** here, adding
patrolling ground and flying monsters (with stomp-to-kill and runtime-spawned
corpse/splat variants), an invisible instant-death hazard, two collectible
types, and an exit object that advances to the next room or shows the
high-score table and restarts.

**Where this fits:** part of the `plateforme_*` family — like
`plateforme_2`, uses a **tiled background** (125 tile chunks under the
solid brick objects, plus the `fond_degrade` gradient image), the step
this family adds beyond `maze_*`. See
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
for the full progression.

**Sound & music:** 4 sound files, genuinely wired up: 7 `play_sound` call
sites for `son_bonus` (pickup), `son_monstre_mort` (stomp kill),
`son_personnage_mort` (player death), and `son_niveaufini` (level
complete).

## How to play

- **Left / Right arrow** — move Pingus (`obj_pingus`) left/right.
- **Up arrow** — jump, but only while standing on something solid (checked
  one pixel below the player).
- **Objective** — collect `obj_bonus` (+5 score) and `obj_power` (+20 score)
  pickups while crossing `niveau_01` to reach `obj_sortie`; touching it plays
  a jingle and either advances to a next room (none exists in this sample, so
  it falls through to the high-score/restart branch) or shows the high-score
  table and restarts the game.
- **Monsters** — landing on top of `obj_monstre` or `obj_monstre_volant`
  (`vspeed > 0` and above the monster) kills it and scores 50 points; hitting
  one from the side or below costs a life and restarts the room. Note:
  collision with `obj_monstre_volant` is a no-op (the flying monster can't
  hurt or be hurt) until `obj_power` has been collected — see Things to tweak.
- **Lose condition** — touching `obj_mortel` (an invisible instant-death
  zone) or a monster the wrong way costs a life and restarts the room;
  running out of lives (`no_more_lives`) shows the high-score table and
  restarts the whole game. Starting lives: 3 (`project.json` settings).

## Project structure

| File | Purpose |
| --- | --- |
| `project.json` | Project manifest — window/room settings, embedded asset copies. |
| `rooms/niveau_01.json` | The one room: 800×640, 194 instances + 125 background tiles. Source of truth for room contents (`project.json`'s embedded `instances` list is empty, same pattern as plateforme_2). |
| `objects/*.json` | Per-object side files for all 15 objects; identical to `project.json`'s embedded copies as of this writing (verified byte-for-byte, unlike plateforme_2's room file). |
| `sprites/` | 18 sprite assets (walk/fly strips, death sprites, platform blocks, pickups, exit, marker). |
| `sounds/` | 4 sound effects (monster death, player death, bonus pickup, level complete). |
| `backgrounds/` | Snow tileset (`tuiles_neige.png`, autotile source for the 125 room tiles) and a vertical gradient (`fond_degrade.png`) as the room background. |
| `CREDITS.txt` | Licensing notice for the sprite/background art (see Assets below). |

## Objects

15 objects, grouped by role. Room placement counts (of 194 instances) shown
where the object appears in `niveau_01`; "runtime-spawned" objects only
appear via `change_instance` during play.

| Object | Role | Key events |
| --- | --- | --- |
| `obj_pingus` | Player — movement, jump, gravity, all collision/lose/win handling | create, step, keyboard (left/right/up), keyboard_release, collision_with_obj_brique/obj_monstre/obj_monstre_volant/obj_mortel/obj_bonus/obj_power/obj_sortie/obj_marqueur, game_start, no_more_lives |
| `obj_brique` | Base solid platform block, 32×32 (109 placed) | none (solid flag only) |
| `obj_brique_h` | Wide platform variant, 32×16, child of `obj_brique` (15 placed) | none |
| `obj_brique_v` | Narrow platform variant, 16×32, child of `obj_brique`; defined but not placed in `niveau_01` | none |
| `obj_brique_c` | Small platform variant, 16×16, child of `obj_brique` (1 placed) | none |
| `obj_monstre` | Ground monster — patrols left/right, reverses on wall contact (3 placed) | create, collision_with_obj_brique |
| `obj_monstre_mort` | Runtime-spawned monster corpse after a stomp kill; inherits `obj_brique` (becomes a solid step) | create |
| `obj_monstre_volant` | Flying monster — patrols right, bounces off walls (2 placed) | create, collision_with_obj_brique |
| `obj_monstre_volant_mort` | Runtime-spawned flying-monster corpse; falls with a capped gravity, lands on platforms/markers | step, collision_with_obj_brique, collision_with_obj_marqueur |
| `obj_mortel` | Invisible instant-death hazard zone (4 placed) | none (handled from `obj_pingus`'s collision event) |
| `obj_splat` | Runtime-spawned player-death animation, restarts the room on animation end | create, animation_end |
| `obj_bonus` | Minor collectible, +5 score, random idle frame (52 placed) | create |
| `obj_power` | Major collectible, +20 score; also gates whether flying monsters can hurt/be killed (1 placed) | create |
| `obj_sortie` | Level exit — plays a jingle, then next room or high-score + restart (1 placed) | none (handled from `obj_pingus`'s collision event) |
| `obj_marqueur` | Invisible, non-solid room-design marker; collisions explicitly no-op (5 placed) | none |

## Assets

18 sprites, 4 sounds, 2 backgrounds. Sprite/background art is adapted from
the Pingus project (GPL-3.0-or-later) — see `CREDITS.txt` for full
attribution and license terms; this README does not restate or add to those
claims.

## Things to tweak

- The `obj_pingus` vs. `obj_monstre`/`obj_monstre_volant` stomp test used to
  be `vspeed > 0 and y < other.y+8`, which a fast fall could overshoot (the
  8px window is checked against the *post-move* position) and cost a life on
  what looked like a clean stomp. It's now `vspeed > 0 and y - vspeed <
  other.y+8`, which checks the window against the pre-move position instead.
- The `obj_power` pickup silently gates all interaction with
  `obj_monstre_volant` (via `if_object_exists(obj_power, not_flag=true)`
  around the stomp/death logic in `obj_pingus`) — worth making visible to
  players (e.g. a sprite/palette change) rather than an invisible rule.
- Player horizontal speed is a flat `hspeed = 4`; jump impulse is
  `vspeed = -10`; fall gravity is `0.5` with a `vspeed = 24` terminal cap.
- Room size is 800×640 at `room_speed = 30`.

## Export status

This sample is listed in `tools/smoke_run_samples.py`'s `SAMPLES` list, so it
gets a headless smoke pass (the real game loop run for ~180 frames with
injected keyboard input) on every run of that harness. No per-export-target
(Kivy/HTML5) verification has been done for this sample specifically. It is
exposed in the IDE's Welcome tab as "Platform — Level 3"
(`widgets/welcome_tab.py`).
