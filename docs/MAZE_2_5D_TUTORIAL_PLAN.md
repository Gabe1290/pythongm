# "Make it 2.5D" bonus page for Tutorial 6 (Maze) — plan

Written 2026-10-07, revised 2026-10-07 (scope grew after a user discussion —
see "Decisions settled" #3). Status: **implemented 2026-10-07, all units
U1-U7 done.** Not published to the live wiki (needs explicit approval,
per the standing rule) — `wiki/` here means the local staging copy only.

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
- **Wall sprites texture the 3D view automatically, for free.** Confirmed
  separately this session: when `enable_raycast_view`'s `wall_texture`
  parameter is left empty, each wall strip is textured with *the sprite of
  the instance that built it* (`build_raycast_walls` remembers it per edge),
  identically across all three renderers. A maze using more than one wall
  object/sprite for visual variety already shows that variety in 3D with no
  extra authoring — worth a one-line mention in the bonus page, not a whole
  step.
- **The 2026-10-06 raycast render-cache bug (fixed, `d416e0d9`)** means a
  wall or coin created/destroyed at runtime now shows up in the first-person
  view immediately — relevant if a future lesson has students spawn/destroy
  maze pieces at runtime, not required for this plan.

## The real "gap": camera facing — and why it's not actually a new concept

Tutorial 6's player (confirmed by reading `Tutorials/06_maze/02_player_and_maze.html`)
uses **held-key, continuous movement**: `Set Horizontal/Vertical Speed` on
each arrow key, `Stop Movement` on `No key`/collision. The raycast camera
reads a persistent `facing_angle` instance property, and GameMaker's
built-in `direction` (`runtime/instance.py`) is a **read-only** value derived
from `hspeed`/`vspeed` that returns `0.0` the instant the instance is
stationary — which is most frames once a key is released. It can't be bound
once as a live "facing = direction" link; a student needs to set an explicit
angle on each directional key, same as every bundled raycast sample already
does.

**User's observation, checked and correct:** this is the exact same shape of
problem as the common 2D pattern "show a different picture depending on
which way the character is facing" (`spr_player_up`/`_down`/`_left`/`_right`)
— both need the game to *remember which way you're pointed* on each
directional key, then *do something* with that memory (swap an image vs.
write an angle). **Checked against the curriculum and it is NOT currently
taught anywhere**: grepped all 14 in-app tutorials for directional player
sprites, `image_xscale` flipping, or any "facing direction" language — zero
hits. Sokoban (Tutorial 5) comes closest (`If Can Push` reads "the direction
the player is moving") but that's consumed internally by the action, never
something the student tracks or acts on themselves.

**Decided (see below): add the real prerequisite**, not just an analogy —
teach directional player sprites as a genuine step in Tutorial 6 itself,
immediately after movement is built (same page), so the bonus page's
`set_facing_angle` wiring is explicitly "the same four event blocks you just
touched, one more action, different job" rather than a cold-start idea.

## Design

### Part A (NEW, core curriculum) — directional player sprites, Tutorial 6 page 2

Inserted into the existing `02_player_and_maze.html`, right after the
movement step (Step 3) that already builds the 4 directional "(held)"
keyboard events + the `No key`/collision events — reusing those same event
blocks rather than adding new ones:

| Event (already exists, built in Step 3) | Existing action | NEW action added here |
|---|---|---|
| Keyboard: Right Arrow (held) | Set Horizontal Speed 4 | Set Sprite to `spr_player_right` |
| Keyboard: Left Arrow (held) | Set Horizontal Speed −4 | Set Sprite to `spr_player_left` |
| Keyboard: Up Arrow (held) | Set Vertical Speed −4 | Set Sprite to `spr_player_up` |
| Keyboard: Down Arrow (held) | Set Vertical Speed 4 | Set Sprite to `spr_player_down` |

- `No key`/wall-collision events are untouched — the sprite simply stays on
  whichever direction was last pressed (the player keeps "facing" the way it
  last moved), the same semantics the bonus page's `facing_angle` will have
  later.
- **New art needed**: 4 sprites, `spr_player_up/down/left/right.png`, 32×32,
  same style as the existing `spr_player.png` (a simple character, each
  variant just distinguishable enough to show direction — e.g. eyes/an arrow
  pointing the right way). Follows the page's existing "Option A — draw it
  yourself / Option B — load the sample sprite" pattern; Option B needs the
  4 files added to `Tutorials/06_maze/assets/` (currently has
  `spr_coin.png`, `spr_exit.png`, `spr_player.png`, `spr_wall.png`).
  `spr_player` itself stays as `obj_player`'s initial/default sprite (shown
  before the first key press).
- New vocabulary term for the page's existing glossary pattern: **"facing
  direction."**
- Page count, structure: no new page — this lands inside the existing
  4-page core lesson, so no `index.json`/page-count change for Part A.
  Modest time-estimate bump (a handful of minutes: 4 new sprites to
  create/import + 4 action blocks reusing events the student already built)
  — not a new phase of the lesson, folded into the existing "Phase 1: Player
  and Maze" timing.

### Part B (as originally planned) — the 2.5D bonus page

New page `Tutorials/06_maze/05_bonus_2_5d.html` (+ `fr/06_maze/`), registered
as the 5th entry in `index.json`'s `"pages"` list — **EN+FR only**, matching
the repeated precedent of every prior new-content arc in this repo (tutorial
lessons 11–14, the teacher-resources package, the sample guides) deferring
the other 7 shipped languages (de/es/it/pt/ru/sl/uk). Each language has its
own `index.json`, so the other 7 simply keep their 4 pages (now including
Part A's content) — nothing breaks, nothing needs a fallback.

Five actions total, added to objects/events the student already built — no
new objects, no grid-size parameter (default `cell_size` 32 already matches
`spr_wall`/`spr_player`'s 32×32):

| Event (already exists) | Existing action(s) | New action to add |
|---|---|---|
| `obj_player` → Create (new event) | — | `enable_raycast_view` (camera_object defaults to the caller) |
| Keyboard: Right Arrow (held) | Set Horizontal Speed 4, Set Sprite `spr_player_right` | `set_facing_angle` angle **0** |
| Keyboard: Left Arrow (held) | Set Horizontal Speed −4, Set Sprite `spr_player_left` | `set_facing_angle` angle **180** |
| Keyboard: Up Arrow (held) | Set Vertical Speed −4, Set Sprite `spr_player_up` | `set_facing_angle` angle **90** |
| Keyboard: Down Arrow (held) | Set Vertical Speed 4, Set Sprite `spr_player_down` | `set_facing_angle` angle **270** |

(GM angle convention confirmed in `extensions/raycast_2_5d/actions.py`:
0=right, 90=up, 180=left, 270=down.)

- Content: opens by naming the callback explicitly ("Remember how your
  player showed a different picture for each direction? `set_facing_angle`
  does the same job — instead of swapping a picture, it tells the camera
  which way to look"), then the 5-step table above as a walkthrough, a
  **"You should see"** checkpoint (first-person view, walls render solid,
  turning snaps to face the arrow you're holding), a short **Stuck?** table
  (wrong angle sign; forgot the Create event; "nothing changed" → extension
  not active in Project Settings), and the wall-texture-for-free + billboard
  callouts from "What already exists" above.
- Page 4's existing **"Challenge Ideas"** list gets one new bullet pointing
  to the bonus page, matching that list's existing one-line-prompt tone.

### Shared follow-through (both parts)

- `docs/handouts/06_maze/{student,teacher}.{en,fr}.md`: add "facing
  direction" to the vocabulary list (Part A, lands in the core lesson so it
  belongs in the main body, not just the bonus note); page-count claim
  reworded to lead with **"5 pages (4 core + 1 optional bonus)"** — the
  guard test `test_page_count_claim_matches_the_tutorial_index`
  regex-matches the *first* "`<N> pages`" occurrence against
  `len(index.json["pages"])`, so the claim must become numerically true.
  Teacher guide gets a short "If Time Allows" bonus-page summary (Tutorial
  1's guide already established this pattern for optional content), not a
  timing-table slot.
- `tools/tutorial_reference_projects.py`'s `build_t06`: Part A's directional
  sprites must be added to the existing `"player_and_maze"` phase (not a new
  phase) so the phase-1 checkpoint stays an accurate "what the student
  should have at this point" project; `T06_PHASES` then gains one new 4th
  phase, `"bonus_2_5d"`, building the finished-and-converted checkpoint —
  reuses the existing builder/truth-test infrastructure so teachers get a
  ready "answer key" project and the test suite gets a real `GameRunner`
  proof the recipe actually plays.

## Decisions settled with the user (2026-10-07)

1. **Pure teaching content.** No conversion wizard, no one-click helper
   action, no new engine/IDE code — matches how every other raycast feature
   in this repo has been delivered (teach the real actions, don't hide them
   behind magic).
2. **Delivered as a new, explicitly optional page on Tutorial 6**, not a
   new numbered tutorial and not a sample-only drop with no in-app guide.
3. **(Revision) Add the real directional-sprite prerequisite, not just an
   analogy.** Checked first (no such content exists in the curriculum
   today); then decided to genuinely teach facing-direction + sprite
   switching as a step in Tutorial 6's own core lesson (Part A above),
   immediately before the bonus page reuses the identical pattern for
   `facing_angle` — a real scope increase (new art + new core-lesson
   content + handout/reference-project updates), not a documentation-only
   tweak.

## Guard tests

- A real `GameRunner` smoke test: build T06 through the Part-A phase,
  confirm each directional keypress sets the expected sprite (mirrors
  existing per-event action tests elsewhere in the suite); build through the
  new bonus phase, confirm `peek_camera(room)['enabled']` is `True`, confirm
  the border/internal walls resolve to the expected `v_walls`/`h_walls`
  edges (same assertion style as `test_raycast_view.py`'s
  `TestBuildRaycastWalls`), confirm the coin/goal instance renders as a
  billboard, confirm each directional keypress also produces the expected
  `facing_angle` (mirroring `test_raycast_tutorial_lessons.py`'s existing
  pattern).
- `test_teacher_resources.py`'s existing page-count / EN-FR structure-parity
  / French-accent guards cover the updated handout files automatically —
  they already iterate every tutorial directory generically, no new test
  code needed there.
- `tests/test_tutorial_panel_i18n_verification.py`-style check that both the
  edited page 2 and the new page 5 actually render (substantial content, no
  placeholder/error branch) for both `en` and `fr`.

## Not in scope

- Any new IDE UI, wizard, or helper action (explicitly decided against).
- Translating either Part A or the bonus page into the other 7 shipped
  languages — deferred, same precedent as every prior new-content arc.
- Changing the Beginner edition's `tutorial_folders` to add Tutorial 6
  itself. Tutorial 6 is already reachable in Advanced/Development editions
  today; whether to also surface it in Beginner is a separate, pre-existing
  decision this plan doesn't revisit.
- A dedicated new Welcome-tab sample (e.g. "maze_2_5d") — the in-tutorial
  checkpoint project already serves as the worked example.
- `draw_minimap` / `draw_doom_hud` — left out to keep the "few commands"
  promise; at most a one-line "want more?" mention, not built out here.
- Retrofitting directional sprites into any *other* tutorial (Sokoban,
  Platformer, …) — scoped to Tutorial 6 only, where it directly feeds the
  bonus page.

## Units of work (one commit each, session-sized)

- [x] U1 — Part A: 4 new sprite assets + EN page-2 content update (new
      step, reusing the 4 existing keyboard events) + handout vocabulary.
- [x] U2 — Part A: FR translation of the same.
- [x] U3 — Part B: EN bonus page content + `index.json` entry + page-4
      cross-link.
- [x] U4 — Part B: FR translation of the same.
- [x] U5 — `tools/tutorial_reference_projects.py`: Part A folded into the
      existing `player_and_maze` phase; new `bonus_2_5d` phase 4 + its truth
      test.
- [x] U6 — `docs/handouts/06_maze/{student,teacher}.{en,fr}.md` updates
      (vocabulary, page count, bonus section, teacher "If Time Allows"
      note); regenerate `wiki/` locally (**not** published without explicit
      approval, per the standing publishing rule).
- [x] U7 — guard tests (Part A per-key sprite test; tutorial-panel renders
      page 2 + page 5 for en/fr; facing-angle-per-key; raycast-renders-
      through-the-converted-maze smoke test).

## Cost estimate

Larger than the original bonus-page-only scope (Lessons 11–14 ran ~8–12% of
a session each for a whole new 4-page EN+FR tutorial, for comparison): Part
A touches core-lesson art + content + the reference-project builder, Part B
is the original single page + checkpoint phase. Rough estimate ~6–9% of a
session across the two parts — comfortably one sitting, 5–7 commits per the
units above.
