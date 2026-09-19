# 2.5D (raycast) tutorial series — plan

Written 2026-09-19 on an explicit ask ("we need to develop a series of
tutorials for the 2.5D"). Scope decided with the user: **in-app Tutorials
panel** (same HTML-page format as `09_catch_the_coins` /
`10_file_exchange_multiplayer`), **4 lessons, one per capability**,
**English + French shipped together** (other languages fall back to the
English root automatically). Not started beyond this plan.

## Ground rules (from the existing tutorial pipeline — don't re-derive)

- A lesson is `Tutorials/<NN>_<slug>/NN_page.html` (English) +
  `Tutorials/fr/<NN>_<slug>/` (same filenames), an entry in **both**
  `Tutorials/index.json` and `Tutorials/fr/index.json`, and one
  `Tutorials/thumbnails/<NN>_<slug>.png` (280×210, shared by every
  language — there is no per-language thumbnails folder).
- Pages copy the CSS/mockup vocabulary of `09_catch_the_coins`
  (`.step`, `.blockly-group`, `.block-event`, `.block-control`, …); block
  labels are translated in French, identifiers (`obj_person`, `spr_wall`)
  stay English.
- The beginner edition's `tutorial_folders` is an explicit whitelist
  (01–04), so new lessons are hidden from it with **no code change**.
- `tests/test_tutorial_panel_i18n_verification.py` walks every page of every
  lesson in every language folder automatically; add a per-lesson pin
  (index entry shape, thumbnail exists, English root pages load) like
  `TestTutorial10FileExchangeMultiplayer`.

## The four lessons

| # | Folder | Teaches | Modelled on |
|---|---|---|---|
| 11 | `11_raycast_first_steps` | `Enable Raycast View`, the camera object, `facing_angle`, turning + walking with `Set Facing Angle` / `Set Direction Speed`, solid blocks becoming walls | new small room, controls from `raycast_1` |
| 12 | `12_raycast_textures` | `wall_texture`, `sky_texture`, `floor_texture`, flat colours as the fallback, `fov`/`render_distance`/`columns` trade-offs | `raycast_1` |
| 13 | `13_raycast_goals_monsters` | non-solid objects draw as **billboards**; gems + score, a patrolling monster + lives, a gem-gated exit (`test_instance_count`), per-room camera controllers | `raycast_2` |
| 14 | `14_raycast_hud_minimap` | `draw_score`/`draw_lives`/health over the view, `Draw Minimap`, `viewport_height` + `Draw DOOM HUD` status bar | `raycast_3` / `raycast_4` |

## Verified engine facts the lessons must respect

(Read from `extensions/raycast_2_5d/` and the bundled samples 2026-09-19.)

- The camera is the object that runs `enable_raycast_view` in its **Create**
  event (or the one named in `camera_object`); `restart_room` re-runs Create,
  so score/lives setup belongs in `game_start`, not Create (raycast_2 landmine).
- Walls are derived from **every solid instance**: a sprite wider than tall
  ×1.5 is a horizontal thin wall on a grid line, taller than wide a vertical
  one, and **a roughly square solid instance blocks all four edges of its
  cell**. So lesson 11 can use plain 32×32 solid blocks (no thin-wall
  sprites) — much easier to place by hand. `cell_size` (default 32) must match
  the placement grid. Walls are read once at room load (static).
- raycast_1's control set is the reference: Up/Down =
  `set_direction_speed` with `facing_angle` / `facing_angle+180`, Left/Right =
  `set_facing_angle` ±3 relative, no-key = speed 0. The player is a
  non-solid object; solid blocking comes from the wall objects' `solid` flag.
- Non-solid, visible, sprited instances render as camera-facing billboards
  with per-column wall occlusion (goal, gems, monsters).
- Textures are plain sprite assets chosen in the action's parameters; flat
  `wall_color`/`floor_color`/`ceiling_color` are the fallback when blank.
- Lesson 14's bar needs `viewport_height`, and the HUD drawer object must be
  **visible** (an invisible HUD object silently draws nothing).

## Verification method (per lesson, before it ships)

Every lesson's build-along steps get a throwaway builder script that creates
the same project in a scratch folder **exactly as the lesson describes it**
and smoke-runs it through the real `GameRunner` (the
`tools/smoke_run_samples.py` / `tools/capture_tutorial_screenshots.py`
approach), asserting the camera config is set and a frame renders — so no
page teaches something the engine can't do. Render one frame to PNG to make
the thumbnail from the real result.

## Units (one commit each, full-suite gate after each)

- [x] **Unit 1 — Lesson 11 (DONE 2026-09-19; `tests/test_raycast_tutorial_lessons.py` rebuilds the lesson and runs it through the real GameRunner)** (pages: introduction, the room and walls, the
      camera and controls, testing/tuning) + thumbnail + EN/FR + index +
      test pin.
- [ ] **Unit 2 — Lesson 12** (textures, sky, floor, fov/columns).
- [ ] **Unit 3 — Lesson 13** (billboards, gems/score, monster/lives,
      gem-gated exit).
- [ ] **Unit 4 — Lesson 14** (HUD text, minimap, DOOM bar).
- [ ] **Unit 5 — wrap-up:** cross-links from `wiki/3D-View.md`,
      `samples/raycast_*` READMEs ("follow the tutorial"), PROJECT_STATUS note.

## Out of scope

Block World (voxel) tutorials — a separate series if wanted; HTML5/Kivy
export walkthroughs (the tutorials build and test on desktop, with one
closing note that the same project exports); wiki write-ups of the lessons;
the seven other UI languages.

## Findings recorded while building Lesson 11

- **Solid walls only stop an object that has a collision event for them —
  even an empty one.** Without `collision_with_obj_wall` on the player, it
  walked straight out of the room (verified, y = -401); with the empty event
  it stopped at the border. raycast_1 has exactly these empty events for the
  same reason. The lesson says so in a "Don't skip this!" box, and the test
  file pins both directions.
- The game window takes the **room's** size (a 320x320 room -> 320x320 view),
  not the project's `window_width/height`.
- A plain 32x32 solid block works as a wall (all four edges) — no thin-wall
  sprites needed for a first lesson.
- Room-editor grid defaults to 32 and snaps; the toolbar button is
  `Grid` / `Grille`.
