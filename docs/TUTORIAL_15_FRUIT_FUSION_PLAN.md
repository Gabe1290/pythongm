# Tutorial 15 — "Fruit Fusion": a merge game for first-time 8-9-year-old students

Written 2026-10-09. Ask: a brand-new in-app tutorial, aimed at the youngest
students (8-9), that they can complete **entirely unassisted** from a printed
handout, building a game in the style of popular mobile "merge" games
(Suika/"Fruit Merge Juicy Drop" genre) — catch matching fruit to grow it into
something bigger.

Settled scope decisions (asked and answered before starting):

1. **Placement: a new numbered Tutorial** (`15_fruit_fusion`), using the
   existing in-app Tutorials machinery (`Tutorials/index.json`,
   `Tutorials/<lang>/15_fruit_fusion/*.html`) and the existing handout
   pipeline (`docs/handouts/15_fruit_fusion/*.md` →
   `scripts/build_teacher_wiki.py`) — not a standalone sample.
2. **Mechanic: simplified merge**, not true merge-physics. No falling/rolling
   jar physics; matching fruits combine on catch, non-matching ones don't.
   Chosen specifically because full merge-physics (realistic stacking,
   collision resolution between dozens of rolling bodies) is some of the
   hardest content to build *and* the hardest to explain step-by-step to an
   8-9-year-old working alone — the genre's *feel* (grow a fruit by matching
   it) survives without the physics.
3. **Languages: English + French**, matching every other tutorial added
   since the 2.5D series (`CLAUDE.md`'s "French text must always carry
   proper accents" rule applies to every French string here).
4. **Original art/IP, not a copy.** The game is inspired by the genre, not a
   clone — original name ("Fruit Fusion" / "Fusion de Fruits"), original
   (simple, generated) sprites, no attempt to reproduce a specific
   commercial game's assets or exact rules.

## The game, as simplified

A basket (the player) moves left/right along the bottom of the room and
catches fruit falling from the sky. The basket always holds exactly one
fruit (it starts already holding a cherry, so there is no "empty" state to
explain). Three fruit *tiers* fall from the sky — cherry, strawberry, orange
— each from its own spawner, at its own pace:

- Catch a falling fruit that **matches** what the basket is already
  holding → it merges: the held fruit grows one tier, the basket's sprite
  changes to show the new fruit, and the catch is worth a bonus (10/20/50
  points for the three merges).
- Catch a falling fruit that **doesn't match** → a small consolation point
  (+1), the held fruit is unchanged. Nothing is ever lost — missing or
  mismatching cannot end the game, which keeps the base game impossible to
  "lose" (appropriate for a first, unassisted build at this age; an
  optional lives/game-over variant is offered as a stretch challenge in the
  handout, not required for the base build).
- Merging an **orange** successfully produces a **watermelon** — the top
  tier, which never falls from the sky on its own — and that's the win:
  straight to a "YOU WIN!" room, SPACE to play again (same pattern as
  Tutorial 9's win screen).
- A fruit that falls past the basket without being caught is simply
  destroyed (Outside Room event); the spawner keeps producing more, so
  missing one is never a dead end.

Why each fruit type is its **own object** (`obj_fruit_cherry`,
`obj_fruit_strawberry`, `obj_fruit_orange`) rather than one object with a
random "level" variable: it means the collision event that fires already
tells the basket which tier was caught, with **zero conditionals needed at
spawn time** and no need to read a variable off the caught instance before
destroying it. The only conditional in the whole game is a single two-way
if/else per merge tier ("does this match what I'm holding?"), repeated
three times with one new fruit type added per phase — i.e. structurally
identical to how Tutorial 4 (Breakout) adds one new brick colour per phase,
and how Tutorial 9 (Catch the Coins) builds its win/lose pair. A student (or
reader) who has done either of those recognizes the pattern immediately.

### Objects / sprites (final)

| Object | Sprite | Role |
|---|---|---|
| `obj_player` | `spr_basket_empty` → `spr_basket_cherry` → `spr_basket_strawberry` → `spr_basket_orange` → `spr_basket_watermelon` | the basket; sprite swaps on each merge |
| `obj_fruit_cherry` | `spr_fruit_cherry` (red circle) | falls, vspeed 3 |
| `obj_fruit_strawberry` | `spr_fruit_strawberry` (pink-red circle, bigger) | falls, vspeed 3 |
| `obj_fruit_orange` | `spr_fruit_orange` (orange circle, biggest falling tier) | falls, vspeed 3 |
| `obj_spawn_cherry` / `_strawberry` / `_orange` | none (invisible) | one alarm-based spawner per fruit type, staggered intervals |
| `obj_win_text` | none | win-room message + SPACE to restart |

No watermelon *falling* sprite exists — it is reachable only as the held
fruit's final look, reinforcing that it's the goal, not something you catch
directly.

### Phases (mirrors the existing page-per-phase convention, 5 pages total)

1. **Introduction** — what you'll build, screenshot of the finished game.
2. **Moving Basket** — room, `obj_player`, left/right/no-key movement. No
   fruit yet; testable on its own (same shape as Tutorial 2 Phase 1).
3. **First Merge** — add `obj_fruit_cherry` + its spawner, scoring, and the
   held-fruit variable + the first if/else merge (cherry → strawberry).
4. **Second Merge** — add `obj_fruit_strawberry` + its spawner and repeat
   the *exact same* if/else pattern for strawberry → orange. The handout's
   explicit teaching point here is "notice this is the same four steps as
   last phase, with the names changed."
5. **Winning** — add `obj_fruit_orange` + its spawner, the final merge
   (orange → watermelon) which also triggers `goto_room room_win`, and the
   win room/text object.

### Reference implementation

`tools/tutorial_reference_projects.py`'s `build_t15(root, phase)` builds
each phase's checkpoint exactly like the other 13 builders (same `Project`/
`act()` helpers), verified against the real `GameRunner` in
`tests/test_tutorial_reference_projects.py` (movement, first/second/third
merge, mismatch consolation points, missed-fruit cleanup, the win
transition). This project is also the source of every screenshot in the
in-app tutorial pages and the student handout, and ships as the checkpoint
zip (`wiki/downloads/solutions/15_fruit_fusion_checkpoints.zip`) via the
existing `build_checkpoint_zips`.

## Handout (per `docs/TUTORIAL_HANDOUTS_PLAN.md`'s established shape)

Same four documents as every other tutorial, EN + FR:
`docs/handouts/15_fruit_fusion/{student,teacher,worksheet,answer_key}.<en|fr>.md`,
generated to `.pdf`/`.odt` by the existing scripts and published through
`scripts/build_teacher_wiki.py` the same way. The student handout leans
harder on illustrations than most (explicit ask): one screenshot per phase
checkpoint plus small inline fruit-sprite icons next to each merge step, so
a non-reading-heavy 8-9-year-old can match what's on their screen to the
page without relying on dense instructions.

## Where it lives in the app

- Added to `Tutorials/index.json` (and `Tutorials/fr/index.json`) as
  tutorial 15.
- Added to the **beginner edition**'s `tutorial_folders` whitelist in
  `config/editions.py` (currently only 1-4) — this tutorial's whole point
  is being reachable by a first-time young student, who by definition is on
  the beginner edition. Its action vocabulary (keyboard, collision, score,
  set_variable, a single if/else, alarms) is a subset of what Tutorials 1-9
  already use, so it adds no new prerequisite the beginner edition doesn't
  already expose.
- Not added as a Welcome-tab sample (decision #1 above) and not added to
  `config/editions.py`'s `sample_folders` list for the same reason.

## Units of work (one commit each)

- [ ] **U1 — Reference project + regression tests.** `build_t15` +
      sprites + `tests/test_tutorial_reference_projects.py` coverage +
      checkpoint-zip wiring. *(in progress)*
- [ ] **U2 — In-app tutorial pages, EN.** 5 HTML pages +
      `Tutorials/index.json` entry + thumbnail + `config/editions.py`
      whitelist entry.
- [ ] **U3 — In-app tutorial pages, FR** (translation, not new content) +
      `Tutorials/fr/index.json`.
- [ ] **U4 — Student handout + worksheet, EN + FR**, with real screenshots
      captured from the reference project (see the 2026-08-10 CLAUDE.md
      note on offscreen `QWidget.grab()` screenshots for the technique).
- [ ] **U5 — Teacher guide + answer key, EN + FR.**
- [ ] **U6 — Guard tests** (`tests/test_teacher_resources.py` extended the
      same way every other tutorial's set is covered) + PDF/ODT generation.
- [ ] **U7 — Publish** (wiki sync) — outward-facing, needs explicit
      approval first, same as every prior publish step in this repo.

## Not in scope

Real merge-physics (jar, stacking, rolling collisions); chain-reaction
merges in one catch; a lose condition in the base build (offered only as a
handout "push further" challenge); any language beyond EN/FR for this
tutorial (matches the project's precedent of translating new content to
EN+FR first and widening later only on request).
