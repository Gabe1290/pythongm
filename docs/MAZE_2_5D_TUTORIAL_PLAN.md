# "Make it 2.5D" bonus page for Tutorial 6 (Maze) — plan

Written 2026-10-07. Status: **plan only, nothing implemented yet.**

## The ask

Students build a 2D top-down maze (Tutorial 6, or a `maze_1`-style project of
their own), then convert it into a first-person 2.5D game with "a few
commands" plus enabling the raycast extension. Prior investigation this
session (see the 2026-10-06/10-07 conversation) confirmed the engine side
already supports this with zero new code; this plan covers the teaching
content that makes it discoverable and walkable by a student.

## What already exists — confirmed, nothing to build here

- **Extension activation has a real UI already.** `docs/BLOCKLY_TOOLBOX_GATING_PLAN.md`
  closed 2026-10-01: `Project Settings → Extensions` has a per-project
  checkbox for each installed extension; checking "2.5D Raycast View" makes
  its 4 actions (`enable_raycast_view`, `set_facing_angle`, `draw_minimap`,
  `draw_doom_hud`) visible in every Blockly preset, **Beginner included**.
  This *is* "add the appropriate extension" — already shippable today.
- **Wall geometry transfers with zero changes.** `build_raycast_walls`'s
  "roughly square → block all 4 edges of its cell" fallback (see
  `extensions/raycast_2_5d/renderer.py`) exists specifically so an
  old-style full-cell-block maze (exactly what Tutorial 6 and `maze_1`–`4`
  build) renders correctly without redrawing walls as thin segments.
  `raycast_2`'s own maze generator already proved this pattern end to end.
- **Pickups/goals need no changes either.** Any visible, non-solid, sprited
  instance (Tutorial 6's `obj_goal`/coins) automatically draws as a
  camera-facing billboard — confirmed in the renderer, no per-object
  opt-in needed.
- **The 2026-10-06 raycast render-cache bug (fixed, `d416e0d9`)** means a
  wall or coin created/destroyed at runtime now shows up in the first-person
  view immediately — relevant if a future lesson has students spawn/destroy
  maze pieces at runtime, not required for this plan.

## The real gap: camera facing

Tutorial 6's player (confirmed by reading `Tutorials/06_maze/02_player_and_maze.html`)
uses **held-key, continuous movement**: `Set Horizontal/Vertical Speed` on
each arrow key, `Stop Movement` on `No key`/collision — not the grid-snapped
instant movement `maze_1`'s sample uses, but the same core problem either
way: the player never sets `facing_angle`, and GameMaker's built-in
`direction` (`runtime/instance.py`) is a **read-only** property derived from
`hspeed`/`vspeed` that returns `0.0` the instant the instance is stationary
— which is most frames once a key is released. It cannot be bound once as a
"facing = direction" live link; a student needs to set an explicit angle on
each directional key, same as every bundled raycast sample already does.

## The recipe (verified against Tutorial 6's actual taught object/sprite/event names)

Five actions total, added to objects/events the student already built —
no new objects, no grid-size parameter (default `cell_size` 32 already
matches `spr_wall`/`spr_player`'s 32×32):

| Event (already exists) | Existing action | New action to add |
|---|---|---|
| `obj_player` → Create (new event) | — | `enable_raycast_view` (camera_object defaults to the caller) |
| Keyboard: Right Arrow (held) | Set Horizontal Speed 4 | `set_facing_angle` angle **0** |
| Keyboard: Left Arrow (held) | Set Horizontal Speed −4 | `set_facing_angle` angle **180** |
| Keyboard: Up Arrow (held) | Set Vertical Speed −4 | `set_facing_angle` angle **90** |
| Keyboard: Down Arrow (held) | Set Vertical Speed 4 | `set_facing_angle` angle **270** |

(GM angle convention confirmed in `extensions/raycast_2_5d/actions.py`:
0=right, 90=up, 180=left, 270=down.)

## Decisions settled with the user (2026-10-07)

1. **Pure teaching content.** No conversion wizard, no one-click helper
   action, no new engine/IDE code — matches how every other raycast feature
   in this repo has been delivered (teach the real actions, don't hide them
   behind magic).
2. **Delivered as a new, explicitly optional page on Tutorial 6**, not a
   new numbered tutorial and not a sample-only drop with no in-app guide.

## Design

- New page `Tutorials/06_maze/05_bonus_2_5d.html` (+ `fr/06_maze/`),
  registered as the 5th entry in `index.json`'s `"pages"` list — **EN+FR
  only**, matching the repeated, explicit precedent of every prior
  new-content arc in this repo (tutorial lessons 11–14, the teacher-resources
  package, the sample guides) deferring the other 7 shipped languages
  (de/es/it/pt/ru/sl/uk) rather than blocking on them. Each language has its
  own `index.json`, so the other 7 simply keep 4 pages — nothing breaks,
  nothing needs a fallback.
- Content: a short "why" intro with a before/after screenshot, the 5-step
  table above written as a walkthrough (matching the existing page's own
  step style), a **"You should see"** checkpoint (first-person view, walls
  render solid, turning snaps to face the arrow you're holding), a short
  **Stuck?** table (wrong angle sign; forgot the Create event; "nothing
  changed" → extension not active in Project Settings), and an explicit
  callout that coins/goal need no changes at all.
- Page 4's existing **"Challenge Ideas"** list gets one new bullet pointing
  to the bonus page, matching that list's existing tone (one-line prompts
  for Multiple levels / Timer / Enemies / Keys and doors).
- `docs/handouts/06_maze/{student,teacher}.{en,fr}.md` currently open with
  "(**Help > Tutorials > Maze: Navigate to the Exit**, 4 pages)". Reworded
  to lead with **"5 pages (4 core + 1 optional bonus)"** — the guard test
  `test_page_count_claim_matches_the_tutorial_index` regex-matches the
  *first* "`<N> pages`" occurrence against `len(index.json["pages"])`, so
  the claim must become numerically true, not just gain a mention. Teacher
  guide gets a short "If Time Allows" bonus summary (the pattern Tutorial
  1's guide already established for optional content), not a timing-table
  slot, since it's explicitly stretch material.
- `tools/tutorial_reference_projects.py`'s `T06_PHASES` gains a 4th phase
  (`"bonus_2_5d"`, `phase=4`) building the finished-and-converted checkpoint
  project — reuses the existing builder/truth-test infrastructure so
  teachers get a ready "answer key" project and the test suite gets a real
  `GameRunner` proof the recipe actually plays, the same methodology every
  other raycast lesson's reference project already uses.

## Guard tests

- A real `GameRunner` smoke test: build T06 to the new bonus phase, confirm
  `peek_camera(room)['enabled']` is `True`, confirm the border/internal
  walls resolve to the expected `v_walls`/`h_walls` edges (same assertion
  style as `test_raycast_view.py`'s `TestBuildRaycastWalls`), confirm the
  coin/goal instance renders as a billboard.
- A facing-angle-per-key test (right/left/up/down keypresses each produce
  the expected `facing_angle`), mirroring `test_raycast_tutorial_lessons.py`'s
  existing pattern.
- `test_teacher_resources.py`'s existing page-count / EN-FR structure-parity
  / French-accent guards cover the updated handout files automatically —
  they already iterate every tutorial directory generically, no new test
  code needed there.
- `tests/test_tutorial_panel_i18n_verification.py`-style check that the new
  page 5 actually renders (substantial content, no placeholder/error branch)
  for both `en` and `fr`.

## Not in scope

- Any new IDE UI, wizard, or helper action (explicitly decided against).
- Translating the bonus page into the other 7 shipped languages — deferred,
  same precedent as every prior new-content arc.
- Changing the Beginner edition's `tutorial_folders` to add Tutorial 6
  itself. Tutorial 6 is already reachable in Advanced/Development editions
  today; whether to also surface it in Beginner is a separate, pre-existing
  decision this plan doesn't revisit.
- A dedicated new Welcome-tab sample (e.g. "maze_2_5d") — the in-tutorial
  checkpoint project already serves as the worked example.
- `draw_minimap` / `draw_doom_hud` — left out to keep the "few commands"
  promise; at most a one-line "want more?" mention, not built out here.

## Units of work (one commit each, session-sized)

- [ ] U1 — EN bonus page content + `index.json` entry + page-4 cross-link.
- [ ] U2 — FR translation of the same.
- [ ] U3 — `tools/tutorial_reference_projects.py` phase 4 (`bonus_2_5d`) +
      its truth test.
- [ ] U4 — `docs/handouts/06_maze/{student,teacher}.{en,fr}.md` updates
      (page count, bonus section, teacher "If Time Allows" note); regenerate
      `wiki/` locally (**not** published without explicit approval, per the
      standing publishing rule).
- [ ] U5 — guard tests (tutorial-panel renders page 5 for en/fr;
      facing-angle-per-key; raycast-renders-through-the-converted-maze smoke
      test).

## Cost estimate

Smaller than a full new lesson (Lessons 11–14 ran ~8–12% of a session each
for a whole new 4-page EN+FR tutorial): this is one page plus one reference-
project phase, roughly 3–5% of a session — one sitting, one or two commits.
