# Tutorial / Blockly wording audit — 2026-10-16

User-reported: tutorial text must say what the real Blockly block says
("the tutorial says 'When created' but the Block says 'When object is
created' — also it is not an object being created but an instance").
Scope confirmed: fix across **all 16 tutorials, English + French**; also
fix the related i18n issue if found to be real.

## How this was checked

Every claim below was verified against the **real**
`editors/object_editor/blockly/blockly_workspace.html`, headless, the same
way as the 2026-10-08 Blockly block audit: every registered block type
instantiated and read back via `block.toString(Infinity, false)`, once
with `window.BLOCKLY_LANG = 'en'` and once with `'fr'`. That is the single
source of truth this doc compares tutorial text against — not
`blockly_blocks.js`, which loads first and is silently overridden by
`blockly_workspace.html`'s own (later-loaded) definitions for ~62 block
types, including both bugs found so far.

An automated fuzzy-matching pass (strip digits/booleans/identifiers/
quoted strings, compare normalized text) was used as a **lead generator
only** — it has a high false-positive rate (dropdown option text like
"Left Arrow"/"W"/"up" reads as a mismatch against the default-rendered
block, and French apostrophes/compound words trip the normalizer) — every
item below was individually re-confirmed before being listed as real.

## Part A — Root cause, FIXED (`e49134f9`)

`event_create` / `event_step`'s English fallback text in
`blockly_workspace.html` said "When object is created" / "Every frame
(step)" — every other shipped language's translation already used the
simpler wording ("Quand créé", "Wenn erstellt", ...), so English was the
outlier, not blockly_blocks.js's (dead, overridden) correct copy. Fixed
at the source: `"When created"` / `"Every step"`, plus the tooltip's
"object instance" → "instance", plus `config/blockly_config.py`'s
`BLOCK_REGISTRY` description for `event_create` (separate, same wrong
text, feeds the block-preset picker dialog).

This alone makes most tutorials correct with zero edits, since most
already said "When created" / "Every step" (apparently written against
the dead-but-correct `blockly_blocks.js`, or against an earlier, already-
fixed version of the live page).

**Correction to an earlier claim in this session:** I initially also
suspected the Collision event (`event_collision`) had zero translation in
any language — **false alarm**, found via grepping the wrong i18n key
name (`event_collision` instead of the real `event_collision_prefix`).
Verified directly on the live page with `BLOCKLY_LANG='fr'`: it correctly
renders `"Quand collision avec (aucun)"`. No fix needed there.

## Part B — Confirmed wording mismatches (tutorial text wrong, not the block)

### B1. "Create Event" / "Draw Event" instead of "When created" / "When drawing"

Real text: EN `"When created"` / `"When drawing"`; FR `"Quand créé"` /
`"Quand dessiner"`.

- [ ] `Tutorials/02_first_game/03_falling_stars.html` (EN) — "Create Event" ×2
- [ ] `Tutorials/02_first_game/04_scoring.html` (EN) — "Create Event", "Draw Event"
- [ ] `Tutorials/03_pong/02_paddles_and_ball.html` (EN) — "Create Event"
- [ ] `Tutorials/03_pong/04_score_display.html` (EN) — "Create Event", "Draw Event"
- [ ] `Tutorials/04_breakout/03_paddle_and_ball.html` (EN) — "Create Event"
- [ ] `Tutorials/04_breakout/07_game_controller.html` (EN) — "Create Event", "Draw Event"
- [ ] `Tutorials/06_maze/04_game_controller.html` (EN) — "Create Event", "Draw Event"
- [ ] `Tutorials/fr/02_first_game/03_falling_stars.html` (FR) — "Événement Création"
- [ ] `Tutorials/fr/02_first_game/04_scoring.html` (FR) — "Événement Création"
- [ ] `Tutorials/fr/03_pong/02_paddles_and_ball.html` (FR) — "Événement Création"
- [ ] `Tutorials/fr/03_pong/04_score_display.html` (FR) — "Événement Création"
- [ ] `Tutorials/fr/04_breakout/03_paddle_and_ball.html` (FR) — "Événement Créer"
- [ ] `Tutorials/fr/04_breakout/07_game_controller.html` (FR) — "Événement Créer"
- [ ] `Tutorials/fr/06_maze/04_game_controller.html` (FR) — "Événement Création"
- [ ] `Tutorials/fr/06_maze/05_bonus_2_5d.html` (FR) — "À la création" (yet a THIRD distinct wrong variant — confirms this isn't one typo copy-pasted, it's drifted independently in several places)
- [ ] `Tutorials/fr/10_file_exchange_multiplayer/02_the_board.html` (FR) — "À la création"

### B2. "Collision with X" instead of "When colliding with X"

Real text: EN `"When colliding with"` + object name. (FR already correct
everywhere checked: `"Quand collision avec"` — no FR fix needed for this
one.)

- [ ] `Tutorials/09_catch_the_coins/04_catching_and_crashing.html` ×2
- [ ] `Tutorials/11_raycast_first_steps/03_camera_and_controls.html` ×1
- [ ] `Tutorials/13_raycast_goals_monsters/02_gems_and_score.html` ×1
- [ ] `Tutorials/13_raycast_goals_monsters/03_monster_and_lives.html` ×2
- [ ] `Tutorials/13_raycast_goals_monsters/04_the_exit.html` ×1
- [ ] `Tutorials/16_fruit_basket/04_catching_and_avoiding.html` ×2

### B3. "Outside Room" should be "Other event: Outside Room"

`outside_room` has no dedicated hand-written block — it's the generic
`event_other` block (EVENT_NAME dropdown prefixed `"Other event: "`).
Confirmed real text, both languages: EN `"Other event: Outside Room"`;
FR `"Autre événement : Hors de la salle"`
(`event_other_prefix` + `event_other_opt_outside_room` in
`blockly_i18n.js`).

- [ ] `Tutorials/02_first_game/04_scoring.html` (EN) — "Outside Room"
- [ ] `Tutorials/09_catch_the_coins/03_coins_and_enemy.html` (EN) — "Outside Room"
- [ ] `Tutorials/15_fruit_fusion/03_first_fusion.html` (EN) — "Outside room" (lowercase "r" too)
- [ ] `Tutorials/15_fruit_fusion/04_second_fusion.html` (EN) — "Outside room"
- [ ] `Tutorials/15_fruit_fusion/05_winning.html` (EN) — "Outside room"
- [ ] `Tutorials/fr/02_first_game/04_scoring.html` (FR) — "Hors de la salle"
- [ ] `Tutorials/fr/09_catch_the_coins/03_coins_and_enemy.html` (FR) — "Hors de la salle"
- [ ] `Tutorials/fr/15_fruit_fusion/03_first_fusion.html` / `04_second_fusion.html` / `05_winning.html` (FR) — "Hors de la salle"

**Open question for whoever picks this up:** `"Other event: Outside Room"`
is clunky for an 8-9-year-old audience (Tutorial 15/16's own target).
Worth asking whether `outside_room` deserves a real hand-written block
(like the B3 audit's `event_other` consolidation, but giving this one
specific, very commonly-needed event — "a thing left the room" — its own
clean label) rather than making every tutorial show the generic-dropdown
phrasing verbatim. Not done here; flagged, not fixed.

### B4. Tutorial 13 (FR): event_other dropdown options shown in English

`Tutorials/fr/13_raycast_goals_monsters/02_gems_and_score.html` shows
"Destroy" and "Game Start" in English, inside an otherwise-French page.
These ARE translated in `blockly_i18n.js` — "Destroy" is `event_destroy`
(a dedicated block, confirmed FR text `"Quand détruit"`), "Game Start" is
`event_other`'s `game_start` option (confirmed FR text
`"Autre événement : Début du jeu"`, via the same `event_other_prefix` +
`event_other_opt_game_start` pair as B3 above). This is a tutorial-
authoring gap (the French tutorial text just used the English words),
not a missing translation in the block itself.

- [ ] `Tutorials/fr/13_raycast_goals_monsters/02_gems_and_score.html` — "Destroy" → "Quand détruit"; "Game Start" → "Autre événement : Début du jeu"
- [ ] `Tutorials/fr/13_raycast_goals_monsters/03_monster_and_lives.html` — "No More Lives" → "Autre événement : Plus de vies" (confirmed: `event_other_opt_no_more_lives` = "Plus de vies")

## Part C — Deeper problems, NOT simple wording fixes (flagged, not resolved)

### C1. Tutorial 5 (Sokoban): the crate-on-target check uses an action with no real Blockly block

`tools/tutorial_reference_projects.py`'s `build_t05` uses
`act("if_collision", x=0, y=0, object="obj_target")` — a real runtime
action, but one the 2026-10-08 Blockly audit already found has **no
hand-written Blockly block at all** (`createActionBlock` unwraps it to
its first nested action, discarding the condition entirely — logged
there as unfixed, needs a new block). The tutorial's mockup ("If
colliding with obj_target" / "Si en collision avec obj_target") doesn't
match ANY real block, because there currently isn't one a student could
actually drag into Blockly to reproduce this check.

This is bigger than a wording fix — it needs either (a) a real
`if_collision_at` Blockly block (the audit's own suggested direction), or
(b) rewriting this one step to use a condition Blockly already supports
well (`if_condition` with `position_check`, or restructuring as a
collision EVENT on the crate rather than a condition on the player) —
both are judgment calls beyond "match the existing words". **Needs a
decision before touching this page.**

**Refinement, found while fixing Part B in this same tutorial (left
untouched, same as the rest of C1):** the mockup's visual class is
`block-control` (a conditional, like `if_condition`), not `block-event` —
so this is specifically `if_condition`'s `collision_check` sub-type being
depicted, not the dead `if_collision` action, OR the tutorial is
depicting a THIRD, different thing ("Check Collision" from a "Control"
category) that hasn't been identified yet. `if_condition`'s
`collision_check` *does* have real Blockly support now (this session's
own B2 follow-up fix) — its real rendered text is `"If collision at
offset with <object> offset x: <n> y: <n> then ... else ..."`, which the
tutorial's "If colliding with obj_target" / "Check Collision" wording
doesn't match either way. Whoever resolves C1 should first determine
which of these three (dead `if_collision`, working `if_condition`
`collision_check`, or something else named "Check Collision") the
tutorial is actually supposed to describe, since the fix differs for
each.

### C2. Tutorial 13: "Start block" / "End block" depict an action-list-only convention that doesn't exist in Blockly

`start_block` / `end_block` are **not real Blockly block types at all**
(confirmed: absent from the live `Blockly.Blocks` registry in both
languages). They're a traditional-action-list-editor convention for
grouping several actions inside a single "then" slot when the list editor
has no real nesting — Blockly's `if_condition` already provides a real
statement input for its then/else branches, so a Blockly-authored
version of this step needs no wrapper actions at all; the nested actions
just sit directly inside the if-block's "then" slot.

`Tutorials/13_raycast_goals_monsters/04_the_exit.html` (and its French
page) currently teach the wrong mental model for Blockly specifically
(showing "Start block" / "End block" as if they were draggable blocks).
**Needs a content rewrite** (remove the wrapper mockups, show the actions
nested directly), not a word substitution — flagged, not done.

## Part B — DONE (2026-10-16, commits `51815239`, `a8258360` + one more
untagged follow-up in the same session). B1-B4 fixed across every file
listed, both languages. Extra findings caught while fixing B1-B4 that
weren't in the original list (same patterns, more instances than first
spotted) — all fixed in the same pass:

- `event_alarm`'s real text is `"When alarm <n> triggers"` /
  `"Quand alarme <n> se déclenche"` — several mockups just said `"Alarm
  0"` / `"Alarme 0"` (tutorials 2, 15).
- `event_other`'s `"Other event: "` / `"Autre événement : "` prefix was
  missing from more `No More Lives` / `Game Start` mockups than first
  found (tutorials 4, 7, 13) — same root cause as B3/B4, just more
  instances.
- French `"Collision avec X"` (missing the `"Quand"` prefix entirely —
  distinct from B2's `"En collision avec"` variant) across 11 more
  files (tutorials 4, 5, 6, 7, 8).
- French `"Au dessin"` (a third, different wrong wording for
  `event_draw`, distinct from `"Événement Dessin"`) in tutorial 10.
- Several bare `"in Create"` / lowercase `"draw event"` prepositional
  leftovers that case-sensitive/exact-phrase greps missed on the first
  pass (tutorials 2, 7, 11, 13, 14) — found by a second, case-insensitive
  sweep. **Lesson for whoever does Part D: a single grep pass is not
  enough for this kind of find — case variations and short prepositional
  references ("in Create", "dans Créer") hide from phrase-exact
  searches.**

One item from the original list intentionally NOT done: "Round
Resolved" (`Tutorials/10_file_exchange_multiplayer/05_winning_and_playing_again.html`,
the `multiplayer_files` extension's own custom event,
`extensions/multiplayer_files/__init__.py`'s `round_resolved`
`EventType`) could not be confirmed either way — no dedicated Blockly
block was found in the static files, consistent with the same
dynamic-custom-block registration gap that hid `end_game` from the
earlier Blockly audit's own tooling. Left as-is (plausibly correct: the
extension-event mechanism gives its own events clean direct labels,
unlike the core `event_other` fallback), not confirmed.

## Part D — Still unverified

The automated scan (`Part A`'s method) flagged roughly 150 more phrases
per language across all 16 tutorials that were NOT individually hand-
verified (most are very likely false positives — dropdown option text,
quoted strings, negative numbers the normalizer mishandled — but not
confirmed one by one). Re-run the scan after Part B/C are resolved and
triage what's left; don't assume Part B+C is the complete list.

## Suggested order

1. Part B1-B3 (mechanical text fixes, EN+FR, one tutorial-language pair
   per commit — 8 tutorials × up to 2 languages).
2. Part B4 (2 pages, needs the exact real FR text confirmed first).
3. Decide and act on C1/C2 (or explicitly defer them as their own units).
4. Re-run the automated scan for Part D and triage.
