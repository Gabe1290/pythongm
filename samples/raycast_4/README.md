# Raycast — Level 4

The fourth Doom/Wolfenstein-style first-person level, and the first built
**around a permanent bottom status bar** — the DOOM aesthetic rather than
`raycast_3`'s corner overlays. The 3D view is deliberately **shorter**
(letterboxed) to make room for the bar; that's part of the look, not a bug.

Where `raycast_3` proved a corner HUD and health-as-a-resource, `raycast_4`
shows the two engine features built for a DOOM bar:

- **`viewport_height`** on `enable_raycast_view` shrinks the first-person view
  into the top of the window and reserves the band below it.
- **`draw_doom_hud`** fills that band: a health bar + number, a **health-reactive
  face portrait**, score, lives, and a key counter — all from ordinary draw
  commands, so it renders on desktop, HTML5 and native (Kivy) alike.

See [`docs/RAYCAST_DOOM_HUD_PLAN.md`](../../docs/RAYCAST_DOOM_HUD_PLAN.md) for the
engineering, and [`raycast_3`](../raycast_3/README.md) for the corner-HUD
alternative it deliberately doesn't retrofit.

**Indoor feel.** Two things make this read as a corridor inside a building
rather than an open maze: it casts a **stone ceiling** (`spr_ceiling`) instead
of the panning sky the other raycast samples use — set via `ceiling_texture`
with `sky_texture` left blank — and the walls render **taller**. That wall
height (`RAYCAST_WALL_HEIGHT`, 1.5× a cube) is a global engine default, so
every raycast game gets the taller walls; the ceiling is this sample's own
choice.

**Sound & music:** none — no sound files are bundled with this sample.

## How to play

- **Up / Down** — move forward / backward in whichever direction you're facing.
- **Left / Right** — turn in place.
- **Collect the keys** — each scores 25 and ticks the **KEYS** counter in the
  bar up by one. There are three.
- **Avoid the monsters** — touching one costs **25 health** (with a short
  invulnerability window afterwards). Watch the **face**: it winces as your
  health drops, before you've even read the number.
- **Run out of health** → lose a life, health refills, the room restarts.
  **Run out of lives** → the game restarts.
- **Reach the exit** once you've found **all three keys**. Touching it early
  just tells you the gate is locked.

## The status bar (`draw_doom_hud`)

`obj_person` draws it every frame, in screen space, over the finished 3D view.
Left to right:

| Zone | Shows |
|---|---|
| Left | `HEALTH` label + a proportional health bar + the number |
| Centre | the **face portrait**, a 4-frame strip that reacts to health |
| Right | `SCORE` over `LIVES` |
| Far right | the `KEYS` counter |

The face is the point of the whole sample. Its frame is chosen by an
even-bucket map over health — frame 0 (calm) near full, the last frame (dying)
near empty — so the portrait tells you how you're doing before the number does,
exactly like DOOM's own bar.

**`obj_person` is both the camera *and* the HUD drawer.** That's deliberate: the
key counter is then just an instance variable on `obj_person` (`keys`), so
`draw_doom_hud`'s objective expression reads the same value identically on all
three export targets. A separate invisible camera object (as in `raycast_3`)
couldn't carry a variable the visible HUD needs.

## The letterbox (`viewport_height`)

`enable_raycast_view` runs in `obj_person`'s `create` with
`viewport_height: 400` in a 640×480 window — so the 3D view is 400px tall and
the bottom **80px** is reserved, filled black by the engine, and painted over by
the bar. Set `viewport_height` to `0` (the default) and the view fills the whole
window with no reserved band, exactly as `raycast_1`–`3` do.

The horizon moves up with the shorter view, and walls/sky/floor all scale to it —
it's a true letterbox, not a bar laid over a full-height view. (On Kivy, which is
y-up, the reserved band is at the bottom of the window all the same; the engine
handles the inversion.)

## Project structure

| File | Purpose |
|---|---|
| `project.json` | Manifest — 640×480 window, one room |
| `rooms/room0.json` | The maze: 15×15 cells, 3 keys, 4 monsters, a key-gated exit |
| `objects/obj_person.json` | Player + camera + status bar — movement, health, keys, `draw_doom_hud` |
| `objects/obj_key.json` | A key (passive; `obj_person`'s collision handles it) |
| `objects/obj_monster.json` | Patrolling billboard enemy |
| `objects/obj_goal.json` | Key-gated exit (opens when no `obj_key` remains) |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Thin wall segments |
| `sprites/` | Reused wall/floor/person/monster art, a new **`spr_ceiling`** (indoor stone ceiling, replacing the sky), plus new `spr_face` (4-frame portrait) and `spr_key` |

## The maze is generated

`tools/gen_raycast_4_maze.py` builds the room by **delegating to `raycast_3`'s
committed generator** — same recursive-backtracker maze, same thin edge-walls,
same chosen-seed discipline (the spawn opens east, every cell reachable). It
differs only in what's scattered (keys, not gems/medkits) and that `obj_person`
is the camera. Re-running reproduces the shipped room; a test pins it.

## Things to tweak

- **Bar height vs. viewport:** the `height` on `draw_doom_hud` (80) should match
  the reserved band (`640×480 − viewport_height 400 = 80`). Change one, change
  the other.
- **Face reactivity:** `face_frames` (4) buckets health across the strip. A
  5-frame strip with `face_frames: 5` gives finer expressions.
- **Damage / keys:** `-25` in `obj_person`'s `collision_with_obj_monster`; the
  3 keys and 4 monsters in the generator's `counts`.
- **Bar colours and labels:** the `draw_doom_hud` parameters on `obj_person`'s
  draw event.

## Export status

Runs on all three targets. Covered by the headless smoke suite
(`tools/smoke_run_samples.py`) and `tests/test_raycast_4_sample.py`, which drives
the real loop: the bar renders all its parts over the shrunk view, bottom-aligned
to the reserved band; the **face frame tracks health** (100/75/50/25 →
0/1/2/3); a key pickup counts, scores and is destroyed.

The Kivy and HTML5 exports were verified to carry the whole thing — the
letterbox `viewport_height` in the camera config, `draw_doom_hud`, the
multi-frame face — but the per-target **visual** playtest is the last step and is
worth doing by eye: this is the first raycast sample whose *view shape* changes,
so it's the one most worth watching render in a browser and on Android.
