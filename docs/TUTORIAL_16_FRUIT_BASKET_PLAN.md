# Tutorial 16 — "Fruit Basket": a complete game with zero variables

Written 2026-10-13. Ask: the user asked whether a very basic tutorial in the
spirit of Tutorial 15 ("Fruit Fusion") could be built *without* the concept
of a variable at all — variables are a genuinely hard abstraction for 9-10
year olds, and Fruit Fusion's merge mechanic needs one (a held-fruit level,
compared with if/else). This is that tutorial.

Settled scope decisions (asked and answered before starting):

1. **A new Tutorial 16, not a rewrite of Tutorial 15.** Fruit Fusion stays
   exactly as it is — it's shipped, tested, and published to the wiki, and
   its variable-based merge is a deliberate teaching point for an 8-9-year
   old audience one small step further along. Tutorial 16 is a new, even
   simpler rung added below/alongside it, for students who aren't ready for
   "the basket remembers what it's holding" yet.
2. **Zero authored variables, anywhere, in the base build.** No
   `set_variable`, no `if_condition`/`test_expression` comparing an
   instance's own value, no held/remembered state of any kind. Every
   mechanic is built from single, pre-wired, fire-and-forget actions:
   movement (`set_hspeed`/`stop_movement`), collision (`destroy_instance`),
   feedback (`set_score`/`draw_score`, which the whole curriculum already
   treats as a single opaque "add points" action, never something read back
   or compared — see CLAUDE.md's 2026-10-13 note), room control
   (`restart_room`, `goto_room`), and exactly one *built-in* check action,
   `test_instance_count` (not an authored expression), for the win
   condition — the same action Tutorial 9 already uses the same way.
3. **Design that makes zero variables possible: everything is static, not
   falling.** Tutorial 9's falling coins/enemies need `set_variable` to
   recycle a missed object back to the top (`y = 0` on Outside Room).
   Tutorial 15's merge needs a held-fruit variable. Tutorial 16 sidesteps
   both: fruit and bombs are placed once in the room (like Sokoban's crates
   or Maze's coins) and never move or respawn mid-game. The basket just
   walks left/right along the bottom row and touches them. This is strictly
   simpler to build *and* to explain than "things fall from the sky" — nothing
   needs recycling, so nothing needs a variable to recycle it.
4. **Languages: English + French**, matching every tutorial added since the
   2.5D series.

## The game, as simplified

A basket moves left and right along the bottom of the room. Fruit (green
apples) and bombs are both already sitting in the room when it starts —
nothing falls, nothing spawns.

- Touch a fruit → it disappears and you gain 10 points. (`destroy_instance`
  on the fruit + `set_score` relative, exactly Tutorial 9's catch pattern.)
- Touch a bomb → the room instantly restarts (`restart_room`). Nothing is
  permanently lost — all the fruit you'd already caught comes back too — so
  touching a bomb is a small "oops, try again," never a punishing game-over.
  This is also *why* no lives/game-over screen is needed: there is nothing
  to track across a restart.
- Catch every fruit → you win (`test_instance_count` on the fruit object
  reaching zero → `goto_room room_win`), exactly Tutorial 9's win check,
  reused verbatim.
- The two bombs sit near the room's left and right edges, well clear of
  every fruit, so winning never *requires* going near one — avoiding them
  is about not wandering too far, not about threading a needle between
  pickups.

### Objects / sprites (final)

| Object | Sprite | Role |
|---|---|---|
| `obj_player` | `spr_basket` (plain bowl, generated art) | the basket; never changes sprite — no merge, so no sprite-swap concept at all |
| `obj_fruit` | `spr_fruit` (green circle) | static, placed directly in the room |
| `obj_bomb` | `spr_bomb` (dark circle) | static, placed directly in the room, near the two edges |
| `obj_win_text` | none | win-room message + SPACE to restart (verbatim Tutorial 9 pattern) |

One fruit object, one bomb object — no need for several fruit *kinds* the
way Fruit Fusion needs three tiers, since there's no merge to differentiate
them by.

### Room layout (`room_main`, 640×480)

- `obj_player` at (304, 430).
- `obj_fruit` × 5 at y=430, x = 60, 170, 400, 480, 540 — chosen to stay
  clear of the basket's own 56px-wide starting box (a first draft placed a
  fruit at x=300, 4px from the basket's start, so the basket "caught" it
  just by existing — fixed by keeping every fruit at least one full
  basket-width away from x=304).
- `obj_bomb` × 2 at y=430, x = 10 and 600 — each at least 24px clear of the
  nearest fruit, so normal fruit-collecting movement never brushes a bomb
  by accident; touching one is a deliberate wander off the edge, not a
  hazard you have to dodge mid-collection.

### Phases (5 build-phase pages + 1 optional bonus, matching Tutorial 9's
and Tutorial 15's exact shape: intro + 4 build phases + an "import
ready-made art" bonus page — the closest existing analog, since this is
"Catch the Coins" restructured as static pickups with no recycling)

1. **Introduction** — what you'll build, screenshot of the finished game.
2. **Moving Basket** — room, `obj_player`, left/right/no-key movement.
   Testable alone (same shape as every other tutorial's phase 1).
3. **Fruit and Bombs** — place `obj_fruit` × 5 and `obj_bomb` × 2 in the
   room. No behavior yet — just objects sitting there, same teaching beat
   as Tutorial 9's `03_coins_and_enemy` (place first, wire up next page).
4. **Catching and Avoiding** — collision behavior: fruit → destroy + score,
   bomb → restart room. The score display (`draw_score`) lands here too.
5. **Winning** — the `test_instance_count` win check + win room, verbatim
   Tutorial 9 pattern with `obj_fruit` in place of `obj_coin`.
6. **Bonus: Import Ready-Made Art** — optional, points at the three
   generated sprites under `Tutorials/16_fruit_basket/assets/`, verbatim
   Tutorial 15's bonus-page pattern scaled down to 3 sprites.

### Reference implementation

`tools/tutorial_reference_projects.py` gets `build_t16(root, phase)`, built
with the same `Project`/`act()` helpers every other builder uses, verified
against the real `GameRunner` in `tests/test_tutorial_reference_projects.py`
(movement, catching a fruit, touching a bomb restarts the room, winning
once all fruit are gone, and — the one thing worth a dedicated regression
test — that the generated project genuinely contains **no `set_variable`
action and no `if_condition`/`test_expression` action anywhere**, so this
guarantee can't silently regress on a future edit).

## Handout

Same four documents as every other tutorial, EN + FR:
`docs/handouts/16_fruit_basket/{student,teacher,worksheet,answer_key}.<en|fr>.md`,
generated to `.pdf`/`.odt` and published through `scripts/build_teacher_wiki.py`
the same way as Tutorial 15.

## Where it lives in the app

- Added to `Tutorials/index.json` (and `Tutorials/fr/index.json`) as
  tutorial 16.
- Added to the beginner edition's `tutorial_folders` whitelist in
  `config/editions.py`, alongside 15 — this tutorial's whole point is being
  reachable by an even-younger first-time student than Fruit Fusion, who is
  by definition on the beginner edition.
- Not added as a Welcome-tab sample, matching Tutorial 15's own precedent.

## Units of work (one commit each)

- [ ] **U1 — Reference project + regression tests**, including the
      no-`set_variable`/no-conditional guard test.
- [ ] **U2 — In-app tutorial pages, EN** (5 pages) + generated sprites +
      thumbnail + `Tutorials/index.json` entry + beginner-edition whitelist.
- [ ] **U3 — In-app tutorial pages, FR** (5 pages) + `Tutorials/fr/index.json`.
- [ ] **U4 — Handouts (student/teacher/worksheet/answer_key, EN+FR) + wiki
      build + guard tests.**
- [ ] **U5 — Publish** (`scripts/sync_wiki.sh push`), only after explicit
      approval — outward-facing, same as every prior publish step.

## Not in scope

A lose/game-over screen with lives (the restart-on-bomb-touch mechanic
replaces it, and needs no variable to track remaining lives); multiple
fruit *kinds* (no merge means no reason to differentiate them); any
language beyond EN/FR; falling/moving fruit or bombs (the whole point is
that nothing needs recycling).
