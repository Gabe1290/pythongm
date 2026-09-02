# In-app Tutorials i18n — Section L of `docs/I18N_CLEANUP_2026-08-06.md`

> **DONE.** This doc's own closing "final pass ... not yet done" caveat
> (opening the Tutorial panel in the running IDE and confirming each
> lesson renders) was closed afterward by
> `tests/test_tutorial_panel_i18n_verification.py` — written after this
> doc, so it was never updated here. See `docs/PROJECT_STATUS.md` for the
> current picture.

Companion plan for the two Section L sub-problems: adding the missing
`09_catch_the_coins` lesson to de/es/it/ru/sl/uk, and building
`Tutorials/pt/` from scratch. Written now that this tier is actually being
worked (mirrors how `RAYCAST_2_SAMPLE_PLAN.md` was kept separate from its
parent plan).

## Loader contract (read this before touching any file)

`widgets/_tutorial_paths.py::localized_tutorials_path()` — if
`Tutorials/<lang>/index.json` exists, the loader uses that folder
**entirely**; otherwise it falls back to the whole English root. There is
**no per-lesson fallback** — a language folder that's missing a lesson
simply doesn't list it; nothing crashes. This is why the six-language
lesson addition is "additive, lower risk" (per the Update-3 sequencing
note in `I18N_CLEANUP_2026-08-06.md`): each language's existing 8 lessons
keep working untouched while lesson 9 is added.

`tutorial_panel.py::load_tutorial_list()` reads `index.json`'s
`"tutorials"` array — each entry is `{title, folder, description,
thumbnail, pages: [...]}`. `pages` lists HTML filenames inside `folder`,
resolved relative to the localized `tutorials_path`. `thumbnail` is
resolved against `base_tutorials_path` (the English root) in
`tutorial_dialog.py`, so **thumbnails are shared across languages** — no
new thumbnail image needed; `thumbnails/09_catch_the_coins.png` already
exists and every language's `index.json` entry points at the same path.

## The load-bearing finding: which languages can even show translated Blockly block text

The lesson HTML files illustrate Blockly blocks with hand-styled
`<span class="block ...">` mockups (not live screenshots) — e.g.
`<span class="block block-event">When created</span>`. Before translating
these mockups, verified against `editors/object_editor/blockly/blockly_i18n.js`
which languages the **live app** can even render translated block text in:

- `BLOCK_MESSAGES` (custom block field text — event/action blocks like
  "When created", "Set score to", "Go to room"): **only fr, de, it, uk**
  have entries. (uk's entries existed but were misplaced under
  `CATEGORY_MESSAGES.uk` until this session's fix, commit `cedb370` —
  see `docs/TRANSLATION_CATALOG_CORRUPTION_2026-08-08.md`'s "Related,
  already-fixed finding".) es, ru, sl, pt have **zero** entries —
  `getBlockMessage()` falls through to the English default, meaning a
  Spanish/Russian/Slovenian/Portuguese user's Blockly canvas shows
  **English block text regardless of app language**, even though the
  rest of the UI (menus, dialogs — see the corruption registry above,
  now fixed) is properly translated for es/ru/sl.
- `KEY_NAMES` (keyboard key display names inside key-event blocks, e.g.
  "Left Arrow" → "Flèche gauche"): **only fr, de, it**. Not uk, not
  es/ru/sl/pt. So even a Ukrainian block that otherwise translates (e.g.
  "Клавіатура: ... (утримується)") still shows the bare English key name
  in the middle, because `getKeyName()` has nothing to translate it to.
- The `if_condition` block ("If count of X == 0 then") is **hardcoded in
  `blockly_blocks.js`, unlocalized in every language including French** —
  confirmed by grep (zero `Blockly.Msg`/`getBlockMessage` calls touch it)
  and by French's own lesson literally keeping "If count of" in English
  (`Tutorials/fr/09_catch_the_coins/05_winning.html`). Every language's
  09 lesson keeps this block mockup in English, no exceptions.
- No Blockly block exists yet for "restart game" (`events/action_types.py`
  confirms `restart_game` is Add-Action-menu-only, no Blockly block/
  generator) — the block mockup for it in the lesson is illustrative
  shorthand, not a real translatable string. Free to translate for
  languages that translate the rest of their mockups (nothing to get
  "wrong" against).

**Resulting rule for lesson-9 block mockups, applied per language:**

| Language | Prose | Block mockup text |
|---|---|---|
| de, it | translate | translate, using the **real** `BLOCK_MESSAGES`/`KEY_NAMES` values above (verified, not guessed) |
| uk | translate | translate event/action wording from `BLOCK_MESSAGES.uk`, but **keep key names in English** (`KEY_NAMES` has no uk entry — this is what the live app actually shows) |
| es, ru, sl | translate | **keep in English verbatim** — matches what those users' Blockly canvas actually renders; a translated mockup would show the student text they will never see on screen |
| pt | translate | keep in English verbatim, same reasoning as es/ru/sl |

This is the same "technical identifiers stay in the reader's real
environment" discipline `docs/I18N_CLEANUP_2026-08-06.md` established for
sample READMEs, just resolved against a different ground truth (Blockly's
own, much sparser, translation coverage) instead of the general Qt `.ts`
catalog.

General UI strings referenced in prose (menu items like "Sprites" /
"➕ Create New {0}..." / event names in the **Add Event** dialog, as
opposed to the Blockly canvas) — these come from the general
`pygm2_<lang>.ts` catalog, which **is** complete for all six lesson-9
languages (es/ru/sl were the ones just fixed in the corruption registry
above; de/it/uk were never affected). Translate these normally; spot-check
against the real `.ts` entry when a exact menu/action name is quoted,
same discipline as Section K/J.

## Section 1: `09_catch_the_coins` for de/es/it/ru/sl/uk

5 HTML files (~524 English lines) + 1 `index.json` entry, per language.
Content: a 4-phase tutorial (moving player → coins/enemy → scoring/
collision → win condition) reusing the `maze_1`-style keyboard-movement
idiom.

Work order: one language per commit (5 files + 1 index.json edit each),
de → es → it → ru → sl → uk (arbitrary order, no dependency between
languages). Verify after each: `python3 -c "import json;
json.load(open('Tutorials/<lang>/index.json'))"` (valid JSON) and a
manual read confirming the new entry's `folder`/`pages` match the actual
files written.

## Section 2: `Tutorials/pt/` from scratch

9 lessons, ~5,123 English lines, all-new `index.json`. Highest risk item
in the whole plan (a malformed index or missing file reference could break
the Portuguese tutorial panel entirely, and there's no existing pt
sub-tree to diff against for sanity). Do this **after** Section 1, as its
own multi-commit arc — one lesson-folder per commit (9 commits), each
verified the same way as Section 1 plus a final pass opening the actual
Tutorial panel (via `tests/` widget harness or manual confirmation) once
all 9 are in place. `pt` has zero Blockly translation coverage
(`BLOCK_MESSAGES`/`KEY_NAMES` both absent — see table above), so **every**
block mockup across all 9 pt lessons stays in English; only prose
translates. This actually simplifies the pt work relative to de/it/uk —
no BLOCK_MESSAGES lookups needed, just faithful prose translation plus
copying the block-mockup HTML verbatim from the English source.

## Verification

- Per file: valid HTML (well-formed enough for `QTextBrowser` — no need
  for strict XML; spot-check the file renders by eye if in doubt).
- Per language: `index.json` parses and its `pages` arrays match real
  filenames in the corresponding folder.
- Final pass (after Section 2 completes, or sooner if convenient): open
  the Tutorial panel in the running IDE, switch language, confirm lesson
  9 (or the full pt curriculum) appears and each page loads — not just
  file/index existence. This is the check the original Section L note
  called out as necessary and is not yet done as of this plan's writing.
