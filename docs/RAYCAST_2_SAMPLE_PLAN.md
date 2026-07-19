# Plan: `raycast_2` — a "Level 2" for the Doom-style raycast sample

Status: **PLAN (2026-07-19).** Not started. This is a **sample-authoring**
project, not engine work — the raycast 2.5D engine is fully complete on all
three targets (walls, panning sky, textured floor casting, occlusion-clipped
billboards; see `RAYCAST_2_5D_PLAN.md`, closed). `raycast_2` showcases
mechanics `raycast_1` doesn't, using only features that already exist.

## Concept

`raycast_1` is a maze_1-derived Doom-style corridor maze: turn-in-place FPS
controls, thin edge-walls, textured walls/sky/floor, and a single billboard
(the goal). It teaches *the first-person view itself*.

`raycast_2` is the next level up — a bigger maze with **things happening in the
3D view**:

1. **Collectible gems + score** — several billboard gems scattered through the
   maze; walking into one adds to the score and destroys it.
2. **A patrolling enemy** — a billboard monster that walks the corridors and
   bounces off walls; touching the player costs a life and sends them back to
   the start.
3. **A gated exit** — the goal only advances the room once *all* gems are
   collected; otherwise it shows a "collect all the gems first" message.
4. *(optional)* **A second, differently-themed room** — room1 uses a different
   wall/sky/floor texture set, proving the raycast config is per-room.

Delta taught vs `raycast_1`: multiple billboards, **moving** billboards, score,
lives, collision→destroy / collision→restart, and an instance-count conditional
gate — all standard 2D GameMaker mechanics, now experienced in first person.

## Engine-risk assessment — NONE required

Every mechanic maps to a shipped feature. Verified against the code before
writing this plan:

| Mechanic | Existing feature it rides on |
|---|---|
| Gems/monster as 3D sprites | `_render_raycast_view`'s billboard pass draws **every** visible, non-solid, sprited instance at its live `x/y` each frame (`game_runner.py:2086`) — moving instances included, zero extra work |
| Monster patrol + wall bounce | Runtime AABB collision fires between any two sprited instances regardless of `solid`; a `collision_with_obj_wall_*` handler reverses direction — exactly how maze_2/maze_3 monsters work |
| Gem pickup → score | `set_score`/score HUD + `collision` event + `destroy_instance` (all registered, all export-parity-tested) |
| Enemy hit → lose life + restart | `set_lives`/lives HUD + collision event + `restart_room`/goto-room (H3/M51 covered) |
| Gated exit | `test_instance_count` conditional (H6/H7 gave it GM skip-next scoping on all three targets; part of the 3-target parity suite) |
| Per-room theme | `enable_raycast_view` is a per-room create-event action with its own texture params |

Because it's all engine features that already pass the 3-target parity tests,
`raycast_2` renders on **desktop + HTML5 + Kivy** with no new engine code.

## Assets

**Reuse from `raycast_1` (proven):** `obj_person` (player/camera), `obj_wall_h`,
`obj_wall_v`, and their sprites; `spr_wall_texture`, `spr_sky`, `spr_floor`,
`spr_person`.

**New billboards needed:**
- `spr_gem` — the collectible. Small new art, or reuse a coin/star from a
  match3 sample.
- `spr_monster` — the patrolling enemy. Can reuse `samples/maze_3/sprites/
  sprite_monster1.png` (already a billboard-friendly single sprite) or new art.

Art is the one thing that may want the user (the user authors sprite art in the
IDE). The plan can bootstrap with reused sprites and let the user reskin later —
none of the code/logic depends on the specific art.

**French:** the README and every in-game message (e.g. the gated-exit prompt
"Ramasse toutes les gemmes !") must carry proper accents.

## Level design

Derive room geometry from **maze_2** (medium size — keeps the "raycast is the
same maze family, seen in first person" relationship that `raycast_1`↔`maze_1`
established) using the same topology-preserving thin-edge-wall conversion
documented in `RAYCAST_2_5D_PLAN.md` ("Complete rethink" section: every open
maze cell becomes a floor cell; walls become 8-px `obj_wall_h`/`obj_wall_v`
edges on the grid lines between an open cell and a blocked neighbour). Then
hand-place gems, the monster spawn, and the goal.

## Unit sequence (one commit each — session-limit discipline)

Work the queue one unit at a time; commit + push after each so a mid-session
limit loses nothing and the next session resumes from clean `main`.

- **Unit 0 — this plan doc.** Commit first (done — `f914992`).
- **Unit 1 — geometry + baseline. DONE 2026-07-19.** maze_2's wall system
  (corner/horizontal/vertical segments) doesn't map cleanly to raycast_1's edge
  model, so instead of converting maze_2 the geometry is a **hand-controlled
  recursive-backtracker maze** (15×15 cells / 480×480, seed 42 for
  reproducibility, +10 extra knocked-through walls for loops) run through
  raycast_1's exact edge-wall placement (`obj_wall_h` at `(c*32, r*32-4)`,
  `obj_wall_v` at `(c*32-4, r*32)`) — 80 h-walls + 116 v-walls + player + goal,
  198 instances (same shape as raycast_1). `samples/raycast_2/` was seeded by
  copying raycast_1's asset tree (objects/sprites reused verbatim, incl.
  `obj_person`'s create-event `enable_raycast_view` and the empty
  `collision_with_obj_wall_*` handlers that gate wall-blocking); `project.json`
  renamed, single room0. README rewritten (honest WIP). Verified through the
  real `GameRunner.run()` loop: renders the textured first-person camera, turns
  on input, and the player is blocked by walls. `tests/test_raycast_2_sample.py`
  (3). **The "derive from maze_2" note in the Concept/Level-design sections is
  superseded by this hand-built approach.**
- **Unit 2 — gems + score. LEAN PASS DONE 2026-07-19** (committed under a tight
  session budget). `obj_gem` (non-solid, sprited → billboard) with maze_2's
  collect pattern (`collision_with_obj_person` → `destroy_instance self`;
  `destroy` → `set_score +10 relative`); 8 gems scattered at deterministic open
  cells by the regenerated maze script; `obj_gem` + `spr_gem` registered in
  `project.json`. `spr_gem` is a **reused 88×88 match3 gem** (`spr_gem_blue.png`,
  centred origin). Verified: `tests/test_raycast_2_sample.py` +2 (data wiring +
  a behavioural collision→`score==10`→gem-destroyed run through the real loop).
  **Full-Unit-2 completion 2026-07-19 (next session, full budget):**
  1. ✅ Full suite gated: **1952 passed, 0 failed** (was 1950 pre-Unit-2).
  2. ✅ Score-HUD: added `set_score 0` to `obj_person`'s create event → the
     window caption shows the score from frame 1 (`show_score_in_caption`
     auto-enabled). **In-view `draw_score` is NOT possible without engine work**
     — `_render_room` early-returns after `_render_raycast_view`, skipping the
     HUD draw-queue pass (confirmed in code). Logged as a tracked 3-target
     engine follow-up in `RAYCAST_2_5D_PLAN.md` ("in-view HUD compositing"), per
     the plan's "no engine changes in the sample" rule.
  3. ✅ Gem art resized 88×88 → 32×32 (centred origin) for billboard proportion.
- **Unit 3 — patrolling enemy. DONE 2026-07-19.** `obj_monster` (non-solid,
  sprited → billboard; `spr_monster` = maze_3's `sprite_monster1`, 32×32), using
  maze_3's patrol pattern: `create` → `start_moving_direction ['up','down']`
  speed 2; `collision_with_obj_wall_h` → `reverse_vertical`,
  `collision_with_obj_wall_v` → `reverse_horizontal` (bounces off both wall
  orientations). 2 monsters placed at open cells with a vertical run.
  `obj_person` gained `collision_with_obj_monster` → `set_lives -1 relative` +
  `restart_room`, and `no_more_lives` → `restart_game`. **Design fix caught by
  the collision test:** score/lives init moved from `create` to **`game_start`**
  — `create` re-runs on `restart_room`, so a death would reset lives to 3 (and
  score to 0); `game_start` fires once and survives a room restart, so only
  `restart_game` resets them. `enable_raycast_view` stays in `create` (the
  camera must re-arm on every room entry — `restart_room` builds a fresh room
  whose `raycast_camera` is None). `tests/test_raycast_2_sample.py` +5 (monster
  wiring/patrol/lives-init/collision-costs-a-life, + the corrected
  score/lives-in-`game_start` test). Suite 1952→1957.
- **Unit 4 — gated exit. DONE 2026-07-19.** `obj_goal`'s
  `collision_with_obj_person` rewritten (dropping raycast_1's inherited
  next-room/set_health cruft + the single-room-irrelevant `keyboard_press`
  debug keys) as maze_3's `test_instance_count` + `start_block`/`end_block`
  gate: `test_instance_count(obj_gem == 0)` → win block (`show_message` "Bravo !
  Tu as trouvé la sortie avec toutes les gemmes." + `restart_game`);
  `test_instance_count(obj_gem > 0)` → prompt block (`show_message` "Ramasse
  toutes les gemmes avant de sortir !"). Param key is `number` (not maze_3's
  `count`, which the desktop runtime actually ignores — works there only by the
  0-default coincidence); `number` is read by all three targets (HTML5 reads
  `number`, Kivy reads `number`→`count`, desktop reads `number`). French
  messages verified as real UTF-8 (bytes `c3 a9` = é, no mojibake).
  `tests/test_raycast_2_sample.py` +2 (the gate blocks/opens; accented-French
  assertion). Suite 1957→1959.
- **Unit 5 (optional) — second themed room. DONE 2026-07-19.** A second room1
  (recursive-backtracker, seed 99) with a **cool "crystal cavern" theme** — blue-
  tinted `*_ice` variants of the wall/sky/floor textures (PIL multiply-tint).
  **Per-room theming architecture:** `enable_raycast_view` moved OFF `obj_person`
  (whose `create` is now empty) onto tiny invisible camera-controller objects —
  `obj_cam0` (warm) in room0, `obj_cam1` (ice) in room1 — each naming
  `obj_person` as the camera via the action's `camera_object` param (verified all
  three targets honor an explicit `camera_object`: runtime line 4433, HTML5
  `params.camera_object || this.name`, Kivy `_find_raycast_camera` name lookup).
  **Room transition (no shared-goal if/else):** `obj_goal` (room0) → `next_room`;
  a separate `obj_goal_final` (room1) → win (`show_message` "Bravo ! Tu as
  terminé les deux niveaux…" + `restart_game`) — both gem-gated. `room_order`
  now `[room0, room1]`. Verified through the real loop: room0 warm + `obj_person`
  camera → collect gems + goal → room1 ice theme. `tests/test_raycast_2_sample.py`
  +2, and the two Unit-4 goal tests updated for the advance/win split. Suite
  1959→1961.
- **Unit 6 — ship. DONE 2026-07-19.** Added to the Welcome-tab
  `SAMPLE_PROJECTS` ("Raycast — Level 2") + the `add_sample_name_translations.py`
  term table (`("Raycast", 2)` → "Lancer de rayons — Niveau 2" etc.), all 13
  `.ts` updated + `.qm` recompiled; added to `tools/smoke_run_samples.py`;
  `tests/test_sample_docs_dialog.py` asserts the label. README finalised (drops
  the WIP banner). **Per-target playtest all green:** desktop smoke
  `[OK]` at 120 frames (15/15 samples clean); HTML5 export carries both rooms +
  the ice sprites + camera objects; Kivy export's `room0`/`room1` scenes compile,
  the ice/gem/monster textures copy, and `obj_cam1` enables the ice theme naming
  `obj_person`. **The raycast_2 sample is complete (Units 1–6).**

## Testing per unit

- Desktop: the runtime smoke harness (real `GameRunner.run()` loop with injected
  keys + `_FakeClock`, matching `TestRaycast1SampleSmoke`) — the raycast render
  path needs `set_sprites_for_instances` to have run, so tests must go through
  the real `run()` startup, not a hand-built room (landmine from the 2026-07-17
  raycast bug hunt).
- Export parity is already locked by `tests/test_raycast_export_parity.py`
  (desktop↔Kivy exact `_cast_ray`, HTML5 structural) — `raycast_2` is content,
  so it inherits that guarantee; a per-target manual playtest at Unit 6 confirms
  the sample plays, not the engine.

## Out of scope (do NOT expand into)

- No engine changes. If a desired mechanic needs one, it's a separate
  `RAYCAST_2_5D_PLAN.md` item, not this sample.
- No new raycast features (sprite facing/rotation, alpha blending, vertical
  look) — those remain deferred engine work, unrelated to this sample.
- No multi-agent workflows — single-thread authoring, one commit-sized unit at
  a time (account session-limit discipline).
