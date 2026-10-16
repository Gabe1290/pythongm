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

## Part C — RE-INVESTIGATED (2026-10-16, later session): both original claims were wrong

Before touching either page, both C1 and C2's premises were checked against
the REAL live page (same `QWebEngineView` + `loadEventsData`/
`generatePythonCode` round-trip technique `tests/
test_blockly_block_audit_roundtrip.py` already uses, run as a throwaway
script — not the earlier doc's fuzzy-scan/manual-grep method). **Both
"has no real Blockly block" claims were factually wrong** — both blocks
exist and round-trip perfectly. The real problem in both cases is
`display_name`-level wording drift, the same class as every Part B fix,
plus one genuinely new, much bigger finding made along the way. See
"Part E" below before fixing anything described here.

### C1, corrected: `if_collision` IS a real, working block — the audit named the wrong action

`if_collision` (what `build_t05` actually uses) was confused with
`if_collision_at` (a genuinely different action, the one the 2026-10-08
Blockly audit found really is broken — `createActionBlock` unwraps it to
its first nested action; `build_t05` never uses it at all). Verified live:
`if_collision` → `custom_if_collision` round-trips the crate's full step
event (if_collision/start_block/set_sprite/end_block/else_action/
start_block/set_sprite/end_block) byte-for-byte, no data loss.

Real rendered text (identical in EN and FR — see Part E):
`"❓💥 If Collision X Offset: 0 Y Offset: 0 Against: obj_target Negate: ☐"`
— nothing like the page's "If colliding with obj_target" mockup, and the
prose's own instruction to "find **Check Collision** in the *Control*
category" points at an action that doesn't exist anywhere in `ACTION_TYPES`
at all (confirmed: `"check_collision" not in ACTION_TYPES`; it only
appears as a dangling entry in `events/action_types.py`'s *other*,
toolbox-visibility-only map, `ACTION_TO_BLOCKLY_MAP`).

**Fix: a wording correction** (same shape as B1-B4), not a new block or a
restructure. Update `Tutorials/05_sokoban/04_targets_and_controller.html`'s
mockup + prose to depict the real 4-field block and drop the "Check
Collision" reference.

*(Side note, not blocking: four separate fields — X/Y Offset, Against,
Negate — is a lot of surface for "is this crate exactly on a target," the
same kind of clunky-for-the-audience tension B3 flagged for "Other event:
Outside Room." A nicer dedicated block is a legitimate future idea, not
required here.)*

### C2, corrected: `start_block`/`end_block` ARE real blocks — AND a bigger, separate wording bug found on the same page

Verified live: `Blockly.Blocks['custom_start_block']` /
`['custom_end_block']` both exist, both round-trip correctly (confirmed
as part of the C1 check above — the crate step event's real XML
literally contains `<block type="custom_start_block">`). The
`if_condition`-less "test, then a start/end-wrapped group, optionally an
else and a second start/end-wrapped group" pattern Tutorials 5/9/13/16 all
use for a multi-action branch IS the real, correct, working way to author
this in Blockly today — not a fictional convention, contrary to the
original claim.

Real text: `"📂 Start Block"` / `"📁 End Block"` (capitalized, with icons) —
`Tutorials/13_raycast_goals_monsters/04_the_exit.html` shows lowercase
"Start block" / "End block" with no icon. Minor, same wording-fix class.

**Bigger finding on the same page, NOT in the original audit's list at
all:** the step's real action is `test_instance_count` (confirmed from
`build_t13`'s actual JSON: `{"action": "test_instance_count", "object":
"obj_gem", "number": "0", "operation": "equal"}`), whose real rendered
text is `"❓🔢 Test Instance Count Object: obj_gem Number: 0 Comparison:
equal"` — not "If count of obj_gem is equal to 0" as the EN page (and
Tutorial 9's, and Tutorial 16's own) mockup says. This exact "If count of
X is/is equal to N" phrasing is used identically across:

- `Tutorials/09_catch_the_coins/05_winning.html` **and its 8 translated
  variants** (de/es/fr/it/pt/ru/sl/uk — Tutorial 9 is one of the older,
  fully-translated-into-10-languages tutorials)
- `Tutorials/13_raycast_goals_monsters/04_the_exit.html` (EN only — the FR
  page already uses different, closer-to-real wording: *"Tester le nombre
  d'instances de obj_gem : égal à 0"*)
- `Tutorials/16_fruit_basket/05_winning.html` **and its FR page** (this
  tutorial's own `05_winning.html` was written this session, directly
  copying Tutorial 9's established "If count of" phrasing as precedent —
  so it inherited the same inaccuracy)

The original audit's automated fuzzy scan evidently treated this as a
near-enough match (shared keywords "count"/object name) and never
promoted it out of "Part D: still unverified" into the confirmed list —
a concrete example of exactly the false-negative risk Part D's own note
already warned about, just in the other direction (a miss, not a false
positive).

**This one needs a decision, not just a fix** (see "Suggested order,
updated" below) — "If count of X == N" is genuinely much friendlier
wording than the real block's 3-field label, used in a flagship,
10-language lesson. Unlike C1's offset/negate fields (truly optional
detail most students never touch), this phrasing choice is closer to
"deliberately simplified teaching language" than "inaccurate." Two real
options, not a forced wording-match:
  - **(a) Update every listed page to the real, verbose text** — fully
    accurate, same mechanical pattern as every other fix here, but a
    readability regression in a lesson aimed at young students, across 10
    languages for Tutorial 9 alone.
  - **(b) Give `test_instance_count` a real hand-written Blockly block**
    with clean, direct "If count of `<object>` `<op>` `<n>`" phrasing —
    matching what the tutorials already (and reasonably) describe, fixing
    the mismatch by making the block match the teaching text instead of
    the reverse. `if_condition`'s own `instance_count` `condition_type`
    sub-mode (added by the 2026-10-08 Blockly audit's B2 fix) already
    proves this exact clean phrasing is achievable in this engine — worth
    checking first whether `if_condition`/`instance_count` could be reused
    directly (one unified block, no start_block/end_block wrapper needed
    at all) rather than building a second, parallel mechanism.

## Part E — NEW finding, bigger than this whole audit: generated/custom Blockly blocks never localize, in any language

Found while verifying C1 (confirmed empirically, not inferred): every
action in `GENERATED_ACTION_NAMES` (`if_collision`, `test_instance_count`,
`start_block`, `end_block`, `else_action`, `restart_game`, every
Drawing/Game/Particles/Views action from this week's category-mismatch
work, dozens more) renders with **identical, English-only text regardless
of the IDE's selected language**. Root cause:
`blockly_widget.py`'s `_register_custom_blocks()` pushes each
`ActionType.display_name`/`description` straight from the Python
`ACTION_TYPES` dict (always English) to
`blockly_workspace.html`'s `registerCustomBlocks()`, which builds each
block's label directly from that raw string — zero calls to
`getBlockMessage()`/any per-language lookup anywhere in that function.
Verified directly: `if_collision`'s block face is byte-identical with
`BLOCKLY_LANG` set to `'en'` vs `'fr'`.

This is **categorically different and much bigger** than B1-B4/this
Part C's fixes, which are all about HAND-WRITTEN blocks (`event_create`,
`event_collision`, `score_set`, ...) — those genuinely do have real,
working per-language text via `BLOCK_MESSAGES`/`getBlockMessage()`,
confirmed accurate; nothing here contradicts Part A/B's work. The gap is
specifically the ~80-entry `GENERATED_ACTION_NAMES` set.

**Direct consequence for fixing any tutorial page that depicts a
generated block (C1, C2's `test_instance_count`, and likely more in Part
D):** the honest, accurate thing for a translated (FR, or any other
language) tutorial page's *mockup box* to show is the **real, English**
block text — even on a French page — since that is genuinely what a
French-language user's screen will show. Surrounding prose stays in the
page's own language; only the literal "this is what the block looks like"
box should show English for a generated action. This is a new rule Part
D's re-scan (and anyone fixing C1/C2) needs to apply, not previously
considered by the original audit.

**Not fixed here — logged as its own, separate, large TODO.md item**
(see there): deciding whether/how to localize generated blocks is a real
engineering question (per-action translated `display_name`/parameter
labels pushed per-language from Python, or a JS-side lookup table mirroring
`BLOCK_MESSAGES`) affecting every non-English IDE language, not scoped to
tutorials at all.

## Part C (original) — superseded by the re-investigation above, kept for
history:

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

### Re-scan attempt (2026-10-16, after C1/C2): tool built, output too
### unreliable to triage — needs a better matcher, not a bigger effort

Built a real ground-truth dump (`workspace.newBlock(type).toString(Infinity,
false)` for all 320 block types, in `en` and `fr`, via the same
`QWebEngineView` technique as the C1/C2 verification) and a regex-based
matcher comparing every tutorial `<span class="block ...">` against it
(EN pages checked against the `en` dump; FR pages against `fr` ∪ `en`,
applying Part E's rule that a generated block's mockup should show English
even on the FR page). **Result: 896 unmatched spans — overwhelmingly false
positives, not a usable triage list.** Root cause confirmed on a sample: a
block with a *statement* input (e.g. `event_create`'s "DO" slot for its
body) renders via `toString()` as `"When created false"` — a spurious
trailing `false` that isn't part of the real rendered label at all (pinned
by re-reading `event_create`'s `init()` directly: just a label +
`appendStatementInput("DO")`, nothing boolean). `toString(Infinity, false)`
evidently stringifies an empty/unrendered statement connection as `false`
when the block was built via `newBlock()` without a full `initSvg()`/render
pass — an artifact of the dump method, not a real UI string. The regex
matcher inherited this noise for every block with a body slot (most
control-flow blocks), which is why even definitely-correct strings like
`"When created"` and `"Every step"` failed to match.

**Not fixed, not triaged — the 896-line output was discarded rather than
acted on**, since treating that noise as real findings risks "fixing"
tutorial text that was never wrong. A trustworthy re-scan needs either (a)
rendering each block for real (`initSvg()` + a workspace actually inserted
into the DOM, which the `getFieldValue`-based round-trip tests already do
for the small cases checked by hand) rather than flattening `toString()`,
or (b) extracting each block's field sequence structurally (walk
`block.inputList`/`field` objects and join only real field text, skipping
statement/value connections entirely) instead of string-matching the
rendered label. Scoped as its own follow-up tool-building task, not
resumed this session — the C1/C2 fixes already closed the two concretely
known issues; this re-scan was specifically for finding *more*, and didn't
produce anything trustworthy to add to that list.

### Re-scan v2 (2026-10-16, same session, continued): the structural
### matcher built, trustworthy, landed real fixes — 278 unmatched spans
### remain, mostly one well-scoped cluster

Built approach (b) from the note above for real. `block.inputList`/
`fieldRow` walked directly, with a principled per-field-type rule:
`FieldLabel` → literal text; `FieldDropdown` → a full alternation over
*every* option (`field.getOptions(false)`, not just whichever one
happens to be the field's default — the first concrete bug this caught:
`event_keyboard_held`'s default option is "Right Arrow", so a template
built from only the default failed to match a mockup legitimately using
"Left Arrow"), with asset-name dropdowns (`createAssetField`, populated
from the live project, not a fixed vocabulary) detected and treated as a
wildcard instead; `FieldCheckbox` → an alternation over how a checked/
unchecked box can render as text; everything else (`FieldTextInput`,
value inputs) → an explicit wildcard slot, present whether or not it has
a default value (a plain "fields present but empty" case silently
vanishing from the flattened text was the second bug — `custom_
test_instance_count`'s "Object:" field disappeared entirely rather than
leaving a slot to match against). A nested-optional suffix lets a mockup
stop at any *prefix* of a block's real field sequence (tutorials
routinely show only a block's primary field, omitting secondary/default
params like `set_sprite`'s frame/speed — confirmed this is a deliberate,
reasonable simplification throughout, not a wording bug, so the matcher
needed to accept it rather than flag every such mockup).

Also found and fixed a second, independent bug in the *scan's own span
extractor*, not the matcher: the original regex-based extractor
(`<span class="block[^"]*">(.*?)</span>`) is non-greedy, so on a mockup
line with a nested value-highlighting span (`block-num`/`block-text`/
`block-val`/`block-str`, e.g. `Draw text <span class="block-text">"Hi"
</span> at x: <span class="block-num">10</span>`) it matched the
*inner* span's closing tag, manufacturing a bogus standalone "10" or
"obj_x" fragment in addition to (and polluting matching for) the real
full-line text. Replaced with a proper `html.parser.HTMLParser`-based
walker that tracks span-nesting depth and only emits text for the
outermost line-level span (`block-event`/`block-move`/`block-control`/
`block-instance`/`block-score`/`block-draw`/`block-view`/`block-game`/
`block-room`/`block-network`/`block-output`), concatenating everything
nested inside it. This alone cut the unmatched count from 896 to 382
before any real fix landed — most of the first attempt's "noise" was
actually this bug's fragments, not the `toString()` artifact diagnosed
above (that artifact was real too, but smaller than this one).

**Refinement sequence: 896 → 382 (span extractor fix) → 346 (strip the
decorative icon prefix real blocks carry that mockups never show,
confirmed zero emoji anywhere in `Tutorials/*.html`) → 284 (require a
template's first token to be literal text, else a leading-wildcard
template degenerates to matching any string once combined with the
trailing-optional suffix) → 278 (after landing the fixes below).**

**Real findings fixed** (commit `a54c5e3f`), each confirmed against the
live block text before touching any file:
- `else_action`'s real text is `"Else"` (generated/custom, never
  localizes per Part E) — Tutorial 15 (Fruit Fusion) called it
  `"Otherwise"` in EN and `"Sinon"` in FR, in both the mockup span and
  the prose, across all 3 phase pages (`03_first_fusion.html`,
  `04_second_fusion.html`, `05_winning.html`), both languages.
- `custom_bounce`'s real text is just `"Bounce"` — zero parameters at
  all (confirmed in `events/action_types.py`: `description="Bounce off
  solid objects"`, `parameters=[]`). Tutorial 3 (Pong) mockups in both
  EN and FR quoted that *description* as if it were the block's label:
  `"Bounce against solid objects"` / `"Rebondir contre les objets
  solides"`, 3 occurrences each in `02_paddles_and_ball.html`.
- `instance_destroy_other`'s real FR text is `"Détruire autre
  instance"` (no `"l'"`) and `reverse_horizontal`/`reverse_vertical`'s
  real FR text omits the article (`"Inverser mouvement horizontal/
  vertical"`, not `"le"`/`"la"`) — French mockups across Tutorials 2, 4,
  7, and 15 had each independently added the definite article the real
  block doesn't carry. Confirmed this is a real app-translation fact
  (checked `blockly_i18n.js` directly), not a stylistic tutorial choice.

**UPDATE (same session, continued): the "niveau vs salle" cluster above
is now FIXED (commit `21e18c43`).** Every FR tutorial's
`room_goto_next`/`room_goto_previous`/`room_restart`/`room_goto`
block-label and category-name reference now says "niveau", matching
`blockly_i18n.js`'s deliberate choice; generic room-concept prose was
left untouched. Two more confirmed findings landed in the same commit
while in the area: Tutorial 13's "Set lives to -1 (Relative)" (EN+FR)
described a UI state that doesn't exist — `set_lives` with
`relative=True` swaps in an entirely different block (`lives_add`,
"Add to lives"), it doesn't add a "(Relative)" note to the same
block — and `restart_game` (generated/custom, never localizes per
Part E) was rendered as "Redémarrer le jeu" in 5 French tutorials
instead of the real literal "Restart Game". Count: 278 → 251 unmatched.

**Open, next concrete items — NOT fixed here, deliberately deferred as
their own units of work.** Re-scanning after the above found the
remaining ~251 unmatched spans split into two further clusters, each
sizable enough to deserve its own pass rather than a rushed sweep in the
same session as everything above:

1. **French mockups routinely add a definite article the real block
   text omits.** Confirmed on several instances already (`"Inverser
   le/la mouvement..."` vs real `"Inverser mouvement..."`,
   `"Détruire l'autre instance"` vs real `"Détruire autre instance"` —
   both already fixed where found) but the *same* pattern recurs on
   `draw_score`/`draw_lives` (real FR: `"Afficher score à x:.../Afficher
   vies à x:..."`, no `"le"/"les"`) and very likely `move_set_hspeed`/
   `move_set_vspeed` and others not yet individually checked. Worth a
   single systematic grep-and-fix pass across all FR tutorials rather
   than fixing one at a time as encountered (which is how the ones above
   were found — opportunistically, not exhaustively).
2. **`set_variable`'s real rendered block is far more verbose than most
   tutorial mockups show.** `set_variable` is unmapped in
   `actionToBlockType` (confirmed by grep), so it always goes through
   the generated path — real text is `"📝 Set Variable Variable: X
   Value: Y Scope: self Relative: non"` (never localizes, per Part E) —
   but mockups like `"Définir variable global.p2score relative +1"`
   (Tutorial 3) show a drastically simplified form with none of the
   Variable:/Value:/Scope: labels. Same shape as the `test_instance_
   count` fix already landed for Tutorials 9/13/16 (C2), but
   `set_variable` is used far more pervasively across the curriculum, so
   this needs its own scoping pass to find every occurrence before
   deciding whether to match the real verbose text everywhere (as
   `test_instance_count` did) or something else — don't assume the
   `test_instance_count` precedent transfers without checking the actual
   footprint first.

The remainder past these two clusters is the already-documented Part E
generated-block localization gap.

### UPDATE (new session, 2026-10-16): both clusters substantially fixed — 251 → 122 unmatched

Picked back up with the rebuilt scan tool (scripts still in the
scratchpad from the prior session — not committed, rebuild per the
"Re-scan v2" section above if a future session needs them again). Four
more commits, each gated by the focused test subset
(`test_tutorial_panel_i18n_verification.py`, `test_sample_visible_text.py`,
`test_raycast_tutorial_lessons.py`) and pushed immediately:

- `dc9a8144` — the French article-insertion cluster: `move_set_hspeed`/
  `move_set_vspeed`/`draw_score`/`draw_lives`'s real text omits "la"/
  "le"/"les"; 36 occurrences across 12 files. 246 → 214.
- `2668cb56` — a **new, bigger finding**, not previously logged: every
  colon-suffixed French hand-written block
  (`event_keyboard_held`/`_press`/`_release`) renders with **no space
  before the colon** (`"Clavier:"`, not `"Clavier :"`) — confirmed this
  is `blockly_i18n.js`'s consistent style throughout (every other
  colon-suffixed FR label in that file does the same, e.g.
  `draw_score_prefix: "Afficher score à x:"`), diverging from strict
  French print typography but deliberate and uniform. Tutorials across
  18 files had added the typographically "correct" space, making them
  the actual outlier. ~60 occurrences fixed. 214 → 168.
- `b13fb638` — `score_set`/`lives_set`/`set_sprite`'s same French-article
  pattern (12 more files); `set_alarm`'s real text has a trailing unit
  word (EN "steps"/FR "pas") most mockups dropped, plus FR mockups had
  a stray "l'" the real text doesn't have; `score_set`'s real EN text is
  "Set score to {val}" — 3 tutorials dropped "to"; `set_draw_color` is
  generated/custom (never localizes, Part E) with real text "Set Draw
  Color Color: {val}" — 4 EN tutorials used a different, wrong-case,
  missing-field form, and the same 4 FR tutorials fully translated it.
  168 → 128.
- `506a4083` — Tutorial 8 (Lunar Lander) used the internal
  variable-name shorthand "Set hspeed"/"Set vspeed" instead of the real
  "Set horizontal/vertical speed to {val}"; Tutorial 4 (Breakout, FR)
  used the wrong verb for `move_jump_to` ("Aller à x:" instead of the
  real "Sauter à x:"). 128 → 122.

**Remaining 122, triaged by folder — NOT fixed, next session's starting
point:**

1. **Tutorial 10 (File Exchange Multiplayer) alone accounts for 38 of
   the 122** (28 FR + 10 EN) — by far the largest remaining concentration.
   Spot-checked: a mix of the still-open `set_variable` cluster, the
   Mouse event's dropdown options never being localized (a `Part
   E`-shaped gap on a *hand-written* block, not generated — `event_
   mouse`'s real FR text is `"Quand souris"` + the option itself
   literally in English, e.g. `"Left Button Pressed"` — confirmed via
   the dump; not investigated further this session), and this
   extension's own `"Héberger une partie (échange de fichiers)"` /
   `"Rejoindre une partie (échange de fichiers)"` actions, which may be
   authored French-first the same way `extensions/multiplayer_lan/
   actions.py` is (per the 2026-09-02/03 session notes in `CLAUDE.md`) —
   **not verified**, needs its own look at `extensions/multiplayer_file_
   exchange/actions.py` (or wherever this extension actually lives)
   before assuming the same root cause applies.
2. **The raycast/HUD multi-field macro actions** (`Enable Raycast
   View`/`Activer la vue Raycast`, `Draw Minimap`/`Dessiner la
   mini-carte`, `Set Direction & Speed`/`Définir direction et vitesse`,
   `Set Gravity`/`Définir la gravité`, `Set Facing Angle`/`Définir
   l'angle de vue`) — **likely scan-tool limitation, not real bugs**.
   These mockups use an em-dash (`—`) to show a deliberately partial
   subset of a many-parameter action's fields (`enable_raycast_view` has
   a dozen+ params: textures, viewport height, render distance, ...) —
   a reasonable pedagogical simplification this repo's own convention
   already accepts elsewhere (`set_sprite` dropping frame/speed). The
   regex matcher's nested-optional-suffix only allows stopping at a
   *prefix* of the real field sequence, not an arbitrary subset with its
   own separator punctuation, so it can't confirm these are fine the way
   it confirmed `set_sprite` is — before spending more time here, a
   smarter matcher (or just eyeballing each one by hand against its real
   `events/action_types.py` parameter list) should resolve whether any
   of these are genuinely wrong field names versus just untestable by
   the current tool.
3. The rest is small (`Terminer le tour`/`Round Resolved`, a couple of
   `draw_line` calls, assorted 1-2 count stragglers) — likely one-at-a-
   time spot-checks like the ones already fixed, not another cluster.

**Part D is NOT closed** — 122 is real progress from 896, but item 1
above (Tutorial 10) needs its own investigation before it can be fixed,
and item 2 needs either a better tool or manual verification before
concluding it's fine. Next session: start with Tutorial 10's extension
(`extensions/multiplayer_file_exchange/` or equivalent — locate it
first, don't assume the path), since it's the largest remaining chunk
and the only one with a clear next action.

### UPDATE (continued, same thread): Tutorial 10 investigated and fixed — 122 → 99 unmatched

The extension is `extensions/multiplayer_files/` (not `_file_exchange`).
Confirmed via `extensions/multiplayer_files/actions.py` and a live dump:
none of its 6 actions (`host_game_files`, `join_game_files`,
`leave_game_files`, `set_shared_var_files`, `get_shared_var_files`,
`end_turn_files`) are in `blockly_workspace.html`'s hardcoded
`actionToBlockType` map, so — unlike the LAN multiplayer extension,
which turned out to be authored French-first — these are all
generated/custom blocks that never localize (Part E): real text is
always the literal English `display_name` + field labels (e.g. `"Host
a Game (File Exchange) Shared folder: X Max players: Y Player name:
Z"`). The FR tutorial had fully translated every one of these action
names and field labels across all 5 pages; fixed throughout, both in
mockup spans and `<strong>` prose naming the block (commit `0b003160`).
Also fixed in the same commit: `event_mouse`'s dropdown OPTIONS are
never localized either (a hand-written block with an untranslated
option list, not generated) — EN used `"Mouse: X"` instead of the real
`"When mouse X"`; FR fully translated an option that never localizes.

Two more small, concrete fixes landed right after (`a25e7b19`,
`4b265728`): Tutorial 5 (Sokoban)'s core push mechanic was authored as
**two** blocks (`"If Can Push facing"` containing a nested `"Push Other
Instance 32"`), but `if_can_push` is a single, self-contained action
with `object_type`/`direction`/`then_action`/`else_action` choice
params — `"Push Other Instance"` was never a real action at all
(confirmed: `push_back_instance` is a `runtime/collision.py`-internal
physics function, not a Blockly action). Rewrote both EN and FR to the
real one-block structure. Also caught a leftover `reverse_horizontal`
miss from the earlier article sweep (Tutorial 13's `"Inverser
horizontalement"`), and fixed `draw_line` (generated/custom, real text
`"Draw Line X1: {val} Y1: {val} X2: {val} Y2: {val}"`) in Tutorial 10,
which both languages had rendered as an unrelated `"from x:... to
x:..."` structure.

**Remaining 99, re-triaged:**

1. **`set_variable` verbosity cluster is now the largest single group**
   (~20 occurrences, concentrated in Tutorial 10 and scattered
   elsewhere — Pong, Catch the Coins, Fruit Fusion). Still exactly the
   scope question logged earlier: real text is `"📝 Set Variable
   Variable: X Value: Y Scope: self Relative: non"`, far more verbose
   than every tutorial's simplified `"Set variable X to Y"`/`"Définir
   la variable X à Y"`. Not started.
2. **`draw_variable` (generated, real text `"Draw Variable X: {val} Y:
   {val} Variable: {val}"`)** — same shape as the now-fixed
   `draw_line`, a handful of occurrences (Pong's score display,
   File Exchange's cell/turn displays). Not started, but mechanically
   identical to the `draw_line` fix just landed — probably the single
   cheapest remaining win.
3. **`show_message`/`output_message` quoting inconsistency** — real
   field is a free-text wildcard (`"Show message {val}"`), so a bare
   `"You win!"` vs a quoted `"\"You win!\""` are both structurally valid
   matches; the handful still flagged are flagged for a different
   reason (worth a second look — possibly a stray punctuation/encoding
   difference, not a real wording bug). Not investigated.
4. **`draw_score`/`draw_lives` with a trailing `caption`/`sprite` field**
   (`14_raycast_hud_minimap/02_score_and_lives.html`) — these two
   actions may have more real parameters than the `x`/`y` pair fixed
   earlier in this session; needs checking against
   `events/action_types.py` before assuming the tutorial is wrong (it
   might be the dump/matcher that's incomplete here, same caution as
   item 2 below).
5. **The raycast/HUD multi-field macro actions — still the likely
   scan-tool-limitation group from the prior note**, unchanged:
   `Enable Raycast View`/`Draw Minimap`/`Set Direction & Speed`/`Set
   Gravity`/`Set Facing Angle`, all using an em-dash to show a
   deliberately partial field subset. Still not resolved either way.
6. A handful of genuine one-offs left (`Round Resolved`, `Quitter
   l'événement`, a `… (score and lives as before)` placeholder) —
   worth individual spot-checks, not a cluster.

Session total this thread: **896 → 99 unmatched spans**, 9 commits, full
focused-test gate before every push. Good stopping point — the
remaining items are smaller and more scattered than anything fixed so
far, so progress from here will be slower per commit.

### UPDATE (continued, same thread): another seven commits, 99 → 73, and two items resolved for good

- `draw_variable` fixed (`68dbdc1f`): same shape as `draw_line`, real
  text `"Draw Variable X: {val} Y: {val} Variable: {val}"`; EN+FR Pong
  score display used an unrelated structure.
- **Item 3 above (the `show_message`/`output_message` "quoting"
  flags) was a false lead — the real cause was the same French
  article-insertion pattern as everywhere else**, just not checked
  against this specific action yet: `output_message`'s real FR text is
  `"Afficher message {val}"` (no `"un"`); 12 occurrences across 5 files
  had `"Afficher UN message"` (`3e15ab37`). Lesson: when several
  "unmatched" spans for one action cluster around a single language,
  check the simple article/verb-drift hypothesis before assuming
  something more exotic (quoting, encoding) is going on.
- **Item 4 above (`draw_score`/`draw_lives` extra fields) resolved,
  and it was real, not a dump gap** (`842528cf`): `events/
  action_types.py` genuinely declares `caption`/`relative` on
  `draw_score` and `sprite`/`relative` on `draw_lives`, but the
  HAND-WRITTEN Blockly block for both (`blockly_workspace.html`) only
  ever wires up X/Y — the extra `ActionParameter`s exist in the data
  model with no visual field at all (the established "B5" pattern this
  repo's own audit history already named). Confirmed no bundled sample
  (`tools/tutorial_reference_projects.py`) ever sets `draw_lives`'s
  sprite, and every `draw_score` caption value matches the
  default — so dropping both from the mockup loses nothing. Also
  fixed, same commits: `"Dessiner du texte"` → `"Dessiner texte"` (3
  files) and a French-only translation artifact rendering `draw_text`'s
  x/y as English `"at 10, 10"` instead of `"à x: 10 y: 10"`.
- `exit_event` (generated, never localizes) was translated to
  `"Quitter l'événement"` in Tutorial 10; real text is `"Exit Event"`
  (`b6bc3a32`, same commit as 5 more `"Dessiner le texte"` → `"Dessiner
  texte"` instances found in the same tutorial).
- `score_add`'s real FR word order is label-then-value (`"Ajouter au
  score {val}"`, confirmed directly from the block's `init()`: the
  label is a plain field, the value is a *separate* `appendValueInput`
  after it) — two tutorials had the value sandwiched in the middle
  (`"Ajouter 1 au score"`) (`0c110098`).

**New finding, NOT a tutorial-wording bug — a real Blockly round-trip
gap, logged for its own fix, not touched here:** investigating
`"Start moving in direction 45 at speed 6"` (Tutorial 3/Pong) found
that `start_moving_direction`'s real data model supports an arbitrary
numeric `direction_expr` (confirmed: `tools/tutorial_reference_
projects.py`'s `build_t03` authors exactly `direction_expr="45"`, and
`CLAUDE.md` documents HTML5/Kivy export parity work for this exact
parameter), but the hand-written `move_direction` Blockly block
(`blockly_workspace.html`) has **no field for it at all** — only a
3×3 grid of compass-direction checkboxes, plus one `setVisible(false)`
hidden legacy field that exists purely to silently absorb pre-B13
saved data and tick a matching checkbox. A project authored with
`direction_expr="45"` has no visual representation in the Blockly
editor whatsoever — opening it would show every checkbox unticked,
with the actual 45° value invisible and inert. The tutorial's mockup
is honestly describing what the *sample* does, which is why this
isn't a wording fix: rewriting the mockup to match "what the real
block shows" would mean describing an unticked checkbox grid, which
teaches nothing. This needs an actual decision (add a free-angle field
to the Blockly block, or stop using `direction_expr` in bundled
samples / the Blockly-authored curriculum) before any tutorial text
changes — flagging for its own item, not fixing here. The matching
`"Commencer à bouger (direction) : gauche, droite — Speed 2"` mockup in
Tutorial 13 is a *different*, unrelated case (ticking the real `DIR_L`/
`DIR_R` checkboxes is genuinely representable) and is not affected by
this finding.

**The raycast/HUD multi-field macro actions (item 5) are now
confirmed, not just suspected, to be a scan-tool limitation, not a
bug.** Checked `enable_raycast_view`'s real parameter count directly
(`extensions/raycast_2_5d/actions.py`): **16 parameters** (enable,
camera_object, fov, render_distance, cell_size, columns, 3 colors, 4
textures, wall_textured, floor_cast_res, viewport_height). A mockup
showing all 16 labeled fields would be unreadable in a tutorial; the
existing em-dash-separated 2-4-field summaries are a necessary,
deliberate compression, not an error — and they don't even preserve
the real declared parameter order (`"Field of View, Cell Size, Render
Distance"` vs. the real `fov, render_distance, cell_size`), which a
stricter tool would also need to ignore. **Conclusion: do not attempt
to "fix" these by matching real field order/count — leave as-is.**
Future re-scans of this tutorial set should exclude
`enable_raycast_view`/`draw_doom_hud`/`draw_minimap`/`set_direction_speed`/
`set_gravity`/`set_facing_angle` from automated matching entirely
rather than re-flagging them.

**Remaining 73, re-triaged once more:**

1. **`set_variable` verbosity is now by far the largest remaining
   group** (~20 occurrences: Tutorial 10 heavily, plus Pong, Catch the
   Coins, Fruit Fusion). Still the same open scoping question from
   before: real text is `"📝 Set Variable Variable: X Value: Y Scope:
   self Relative: non"`, far more verbose than every tutorial's
   `"Set variable X to Y"`. **Do not blanket-apply the
   `test_instance_count` "match real text everywhere" precedent without
   asking first** — that decision was scoped to a handful of
   occurrences across 3 tutorials; `set_variable` is used dozens of
   times across nearly the entire curriculum, and rewriting every
   instance to the 4-field verbose form would be a much larger
   readability trade-off that deserves its own explicit confirmation,
   not an assumed extension of a narrower earlier decision.
2. **The `direction_expr` Blockly round-trip gap above** — needs a
   design decision, not a wording fix.
3. Everything else remaining is the already-resolved-as-fine raycast/
   HUD group (item 5) plus a handful of genuine one-offs (`Round
   Resolved` — confirmed a false positive, the dump simply doesn't
   enumerate event blocks the same way; `… (score and lives as
   before)` placeholder text) not worth individual tracking.

Session total this thread (both continuations combined): **896 → 73
unmatched spans**, 16 commits, full focused-test gate before every
push. The two genuinely open items (`set_variable` verbosity,
`direction_expr`'s missing Blockly field) both need a decision from
the user before more tutorial text changes, not more investigation —
a good natural stopping point for this audit.

## Suggested order (superseded version below is current)

1. ~~Part B1-B3~~ DONE. ~~Part B4~~ DONE.
2. ~~Decide and act on C1/C2~~ — superseded, see "Part C — RE-INVESTIGATED" above.
3. ~~Re-run the automated scan for Part D and triage.~~ — still open.

## Suggested order, updated (2026-10-16, after the C1/C2 re-investigation)

1. **C1** — straightforward wording fix, ready now: `Tutorials/05_sokoban/
   04_targets_and_controller.html` (EN only — Tutorial 5 has no FR page).
2. **C2, the start_block/end_block casing half** — straightforward wording
   fix, ready now: `Tutorials/13_raycast_goals_monsters/04_the_exit.html`
   EN + FR.
3. **C2, the `test_instance_count` half — needs the (a)/(b) decision above
   before touching anything.** Affects `09_catch_the_coins/05_winning.html`
   (EN + 8 translated variants), `13_raycast_goals_monsters/
   04_the_exit.html` (EN; FR already closer to correct, re-check once the
   decision is made), `16_fruit_basket/05_winning.html` (EN + FR).
4. Re-run the automated scan for Part D, now explicitly applying Part E's
   rule (a generated-block mockup should show English even on a
   translated page) so the re-scan's own diffing doesn't flag correctly-
   English generated-block mockups on FR/DE/... pages as mismatches.
5. **Part E (generated blocks never localize) is its own large, separate
   item — see its own `TODO.md` entry, not sequenced here.**
