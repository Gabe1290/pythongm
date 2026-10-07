# Polish (`pl`) translation — plan

Written 2026-10-07. Status: **ALL THREE PHASES COMPLETE** as of
2026-10-07 — the full plan finished in one extended session (the user's
own "two sessions, if necessary" framing turned out not to be needed).
Phase 1: all 70 real contexts / 1562 located-active messages in
`translations/pygm2_pl.ts`, byte-identical in coverage to `fr`. Phase 2:
all 4 `blockly_i18n.js` translation tables (377 entries), key-set-
identical to `fr`. Phase 3: all 14 lessons / 63 pages of the Tutorials
curriculum translated, `Tutorials/pl/index.json` registers all 14 with
real current page lists, `pl` added to
`test_tutorial_panel_i18n_verification.py`'s `LOCALIZED_LANGUAGES` (34
tests passing, incl. every lesson/every page walked through the real
`TutorialPanel` widget), and all 63 HTML files + `index.json` confirmed
to carry real Polish diacritics. Full suite green throughout (only 3
pre-existing, unrelated failures from an in-progress Thymio-extension
refactor on `main`, untouched by this work). One unplanned detour: a
user bug report mid-session (the Blockly `instance_create` block
silently producing no action at all — see the session note in
CLAUDE.md) was investigated and fixed, since it directly affected
Tutorial 2 and Tutorial 9's "Create instance" steps in every language,
Polish included.

**Correction (2026-10-07, same day):** the counts below (1849 messages /
73 contexts) were the plan's original naive count — a straight
non-`vanished` scan of `pygm2_fr.ts` that didn't additionally filter for
the `<location>` tag `TranslationBuilder._parse_source_context` actually
requires (same filter `gen_translation_ts.py`'s own docstring describes).
Applying that filter, the **true** total actually usable by the tool is
**1562 messages across 70 contexts** — confirmed by completing Phase 1
and cross-checking the result context-for-context and message-for-message
against a matching `<location>`-filtered scan of `fr` (zero missing, zero
extra). Of the "73 contexts" figure, 3 (`AboutDialog`, `EventActionWidget`,
`GM80EventsPanel`) turned out to have zero located-active messages (their
classes no longer exist in the codebase) and are correctly absent from
`pygm2_pl.ts`. Numbers elsewhere in this doc (e.g. `PyGameMakerIDE`'s "361
messages") are likewise the naive count; the real, tool-usable number for
that context was 357. Left the historical numbers below as originally
written rather than silently rewriting history, with this note as the
correction of record.

## The ask

A complete Polish translation of the IDE. Decided with the user (2026-10-07),
scope is the full stack, not just the app chrome:

1. **The Qt UI catalog** — every `self.tr()`-driven string: main window,
   menus, every dialog and editor panel.
2. **Blockly workspace block-level translation** (`blockly_i18n.js`) — block
   labels, tooltips, key names shown in the visual programming workspace
   itself.
3. **The in-app Tutorials curriculum** (14 lessons) — the lesson prose
   students read, not just the surrounding app.

Explicitly **not** in scope (see "Not in scope" below): the wiki.

## Key finding: the established reference language is now stale — use French, not Portuguese

Every prior new-language arc (pt, then ja, then zh) used
`translations/pygm2_pt.ts` as the source-string reference, and
`scripts/gen_translation_ts.py`'s `TranslationBuilder` still defaults to it.
That default is now **wrong** for a new language. Counted directly (2026-10-07):

| File | Active messages | Contexts |
|---|---|---|
| `pygm2_pt.ts` / `_ja.ts` / `_zh.ts` | 1488 | 62 |
| `pygm2_fr.ts` | **1849** | **73** |
| `pygm2_es.ts` | 1514 | 65 |
| `pygm2_de_*.ts` (split set, summed) | 1151 | 53 |

pt/ja/zh were completed 2026-08-09/10 and never backfilled since. Eleven
whole dialogs added after that date exist only in `fr` (a strict superset of
`es`, and of the `de` split set bar one stray context):
`AboutDialog`, `BackgroundEditor`, `BlockWorldEditorWindow`,
`EventActionWidget`, `FindReplaceDialog`, `FontEditor`, `GM80EventsPanel`,
`OrphanedFilesDialog`, `SoundEditor`, `TrashDialog`, `UnusedAssetsDialog` —
plus substantially more content within contexts both share, e.g.
`PyGameMakerIDE` 361 (fr) vs 310 (pt), `ActionConfigDialog` 151 vs 64,
`ObjectEventsPanel` 196 vs 106. Building Polish from pt would silently bake
in that gap on day one. **`pygm2_fr.ts` is the source-string reference for
this plan** — pass it explicitly:
`TranslationBuilder("pl", source_ts="translations/pygm2_fr.ts")`.

`fr` is also already clean of the two historical bugs pt was built to fix
(the `self.ide` wrong-translation-context bug; the `ThymioPlaygroundWindow`
`self.tr(f"...")` f-string bug) — both were fixed repo-wide, fr included, at
the time they were found, confirmed by grep (no `self.ide` context, no
f-string `tr()` calls remain). No need to rediscover either.

This gap in the older languages is a real, separate finding — logged under
"Not in scope" below, not bundled into this plan.

## Monolithic file, not the split-group convention

Build `translations/pygm2_pl.ts` as **one monolithic file**, matching
pt/ja/zh (not the `de`/`it`/`ru`/`sl`/`uk` `_core`/`_editors`/`_actions`/
`_dialogs`/`_blockly`/`_misc` split). Reason, unchanged from the pt arc:
`scripts/compile_translations.py`'s `should_compile` only compiles a split
group once `pygm2_<lang>_core.qm` already exists — a chicken-and-egg problem
for a brand-new language the monolithic form sidesteps entirely.

## Tooling (all already exists, zero new code needed)

- `scripts/gen_translation_ts.py`'s `TranslationBuilder`:
  - `add_contexts({...})` — a whole small/medium context in one call, the
    dict must cover every active (non-vanished, has `<location>`) message.
  - `add_partial_context(name, {...})` — for huge contexts (`PyGameMakerIDE`
    is 361 messages now, bigger than pt's 287 was); call repeatedly with
    whatever subset is translated so far, already-present sources are
    skipped, safe to re-run.
  - Source dict **keys** must match the reference's `<source>` text
    byte-for-byte, entity-escaped form (`&amp;` `&lt;` `&gt;` `&apos;`
    `&quot;`) and all — copy via a `grep`/small Python dump, never retype by
    hand. Translation **values** must be real unescaped characters; the
    tool escapes them for you (see the zh double-escaping landmine below).
- `scripts/compile_translations.py` — compile to `.qm` after each batch.
- A live `QTranslator` spot-check after each batch (resolve a sampled
  handful of strings for real) — the established per-batch verification
  that caught real bugs in every prior arc; cheaper than it sounds and
  worth never skipping.

## Landmines carried forward from the pt/ja/zh arcs (expect all of these again)

1. **XML double-escaping (zh's own landmine).** `TranslationBuilder`
   XML-escapes the translation *value* for you. A value must use real `>`
   `<` `&` characters, never the source's already-escaped `&gt;` form
   copied over by habit — that double-escapes to `&amp;gt;`, which is
   valid XML, compiles clean, and silently shows literal `&gt;` to the
   user. Only source dict *keys* need the escaped form.
2. Leading/trailing-space sources, literal tab characters (5 Sprite Editor
   shortcut strings), `{0}`/`%1` placeholders, HTML markup preservation
   (the About/License dialog's rich text) — all reproduced identically
   across pt → ja → zh; budget for them, don't be surprised.
3. **Menu mnemonics (`&File`) — Polish uses the Latin alphabet**, so
   (unlike ja/zh's CJK "keep the English letter in parentheses" rule)
   embedding `&` directly in the translated word is the normal, correct
   approach — matching fr/de/es/it, not the CJK pattern. Pick the
   mnemonic letter that's natural for the Polish word (e.g. `&Plik` for
   File), don't default to reusing the English letter blindly.
4. **Diacritics (ą ć ę ł ń ó ś ź ż) must survive** — the exact same
   non-negotiable rule this repo already enforces for French accents
   (CLAUDE.md: "French text must always carry proper accents... missing
   accents are unacceptable"), extended here to Polish. Spot-check every
   batch; build a stripped-diacritic regression test once the catalog is
   complete (see Guard tests).
5. **Pluralization**: Polish has a 3-way count-dependent plural system
   (1 / 2-4 / 5+, further complicated by case) — more complex than
   Slovenian's already-documented 4-number system. Follow the same
   pragmatic simplification already decided for Slovenian: a generic
   parenthetical/template form for the handful of count-driven strings
   (e.g. `"used by {0} action(s)"`-equivalent), not grammatically-exact
   agreement — this was an explicit, deliberate choice, not a shortcut
   nobody considered.
6. **No existing terminology anchor.** Every prior language cross-checked
   new UI nouns ("extension", "action") against that language's own
   already-translated wiki page (`wiki/Extensions_<lang>.md`). Polish has
   **no wiki pages at all** (never part of the 2026-07-29 nine-language
   sweep) — there is nothing to anchor against. Keep a running glossary
   (a scratch note, not a deliverable) of chosen terms as you go and reuse
   it across every batch/phase, so "extension"/"action"/"event"/etc. stay
   consistent from the first context to the last.
7. **Blockly's partial-coverage precedent**: `uk` has `BLOCK_MESSAGES`
   entries but no `KEY_NAMES` at all, and `de`/`it` (214 each) are already
   behind `fr` (231) — verify **count AND key-set parity against `fr`**
   specifically before considering Phase 2 done, not just "some entries
   exist."
8. **Source escaping is genuinely inconsistent WITHIN `pygm2_fr.ts` itself**
   (not a uniform rule) — some apostrophes are written as `&apos;`, others
   as a literal `'`, in otherwise-similar strings in the same context.
   `TranslationBuilder._parse_source_context` matches dict keys against
   the raw, un-decoded `<source>` bytes, so a key must match whichever
   form that specific string happens to use — copy it, don't assume. Hit
   for real in `ObjectEventsPanel` (two "needs the extension" strings used
   a literal apostrophe while the rest of the context used `&apos;`),
   fixed by re-deriving the exact bytes rather than guessing. For a large
   or entity-heavy context (HTML blocks, `&amp;` mnemonics), the safer
   approach is to not retype `<source>` text as dict keys at all: call
   `_parse_source_context(name)` once, get its exact `(src, locs)` tuples,
   and `zip()` them against an ordered translation list by index — this
   is what the `PyGameMakerIDE` batch (357 messages, several multi-line
   and HTML-entity-heavy) used, and it has zero escaping-mismatch risk by
   construction. Separately: **`lrelease` DOES decode XML entities when
   compiling to `.qm`**, so a live `QTranslator`/`QCoreApplication.translate`
   spot-check must look up the *decoded* real-character form (`&File`,
   `<h3>...`), not the raw escaped `.ts` text (`&amp;File`,
   `&lt;h3&gt;...`) — only the `_parse_source_context`/dict-key side of
   the pipeline needs the raw escaped form; the runtime-resolution side
   needs the decoded form. Conflating the two wastes a debugging cycle.

## Guard tests

- A `tests/test_i18n_unfinished_pl.py`, mirroring the existing
  `test_i18n_unfinished_{de,es,fr,it,ru,sl,uk}.py` pattern: every source
  has a real, non-empty, non-English, non-stripped-accent translation,
  resolves via a live `QTranslator`.
- Any test with a hardcoded per-language list needs `"pl"` added once its
  catalog exists: `test_extension_ui_translations.py`,
  `test_project_settings_extensions_translations.py`, and
  `test_tutorial_panel_i18n_verification.py`'s `LOCALIZED_LANGUAGES` (the
  last one then automatically exercises every Tutorials/pl/ page for
  free, once Phase 3 lands — same mechanism this session's own Tutorial 6
  work relied on).
- A real offscreen `QWidget.grab()` screenshot spot-check of
  `PreferencesDialog` + the main window with `pl` selected (the technique
  validated 2026-08-10: genuinely renders real Qt layout headlessly, a
  stronger check than string-resolution alone) — not committed, a
  throwaway dev-time verification like every prior language's own pass.
- Blockly: no Node.js in CI, so a structural/count-parity test (key-set
  equality against `fr`'s `BLOCK_MESSAGES`/`KEY_NAMES`), matching this
  repo's established "no JS engine in CI" tier for `blockly_i18n.js`/
  `engine.js` edits.

## Units of work (one commit + push per batch, matching standing discipline)

### Phase 1 — Qt UI catalog (1562 messages / 70 contexts — see correction note) — **COMPLETE 2026-10-07**

- [x] P1.0 — this plan, committed first.
- [x] P1.1 — the ~60 small/medium contexts `fr` and pt/ja/zh both already
      have (re-derived each one's source strings from `fr`, not pt).
- [x] P1.2 — the contexts that only exist in `fr` (`BackgroundEditor`,
      `BlockWorldEditorWindow`, `FindReplaceDialog`, `FontEditor`,
      `OrphanedFilesDialog`, `SoundEditor`, `TrashDialog`,
      `UnusedAssetsDialog`, etc.) — done alongside P1.1, no separate pass
      needed in practice.
- [x] P1.3 — `PyGameMakerIDE` (357 located-active messages: menus +
      mnemonics, toolbar, status bar, every File/Edit/Assets/Build/Tools/
      Help flow, the Export dialog's per-platform strings, the About/
      License dialogs' HTML blocks) via 3 `add_partial_context` batches of
      120/120/117, built by zipping an ordered Polish translation list
      against `_parse_source_context`'s own parsed `(src, locs)` tuples by
      index rather than hand-retyping entity-escaped `<source>` text —
      avoided the escaping-mismatch risk hit once in `ObjectEventsPanel`
      (see landmine 8 below).
- [x] P1.4 — checked for a legacy `translations/pygamemaker_pl.ts` stub —
      none exists; Polish never had one.
- [ ] P1.5 — add `"pl"` to every hardcoded per-language test list (see
      Guard tests); confirm `pl` is discoverable in
      `LanguageManager._discover_languages()`.
- [ ] P1.6 — guard tests: diacritics sweep, unfinished-entry sweep
      (`tests/test_i18n_unfinished_pl.py`), live `QTranslator` resolution
      across a representative sample, full suite green.

### Phase 2 — Blockly block-level translation — **COMPLETE 2026-10-07**

**Scope correction, found while implementing:** `blockly_i18n.js` actually
holds **four** top-level translation tables, not two. `BLOCK_MESSAGES`
(231 entries) and `KEY_NAMES` (37, not the originally-estimated 9 — that
was `fr`'s single-word-key subset only, undercounted the same way Phase
1's naive scan was) are the two this section originally scoped. Also
found: `CATEGORY_MESSAGES` (12 — the toolbox category labels: Events,
Movement, Timing, Drawing, Score/Lives/Health, Instance, Room, Values,
Sound, Output, Math, Logic) and `BLOCKLY_MSG_TRANSLATIONS` (97 — overrides
for Blockly's own built-in Math/Logic/Text block labels and the
right-click/toolbar menu: "Duplicate", "Delete Block", "Undo", etc.).
Both are genuinely "shown in the visual programming workspace" per this
plan's own scope statement, so both got real translations rather than
being left as an English/stale fallback — true Phase 2 total: **377
entries across 4 tables**, not ~240.

- [x] P2.1 — `BLOCK_MESSAGES['pl']`: ported `fr`'s 231 entries.
- [x] P2.2 — `KEY_NAMES['pl']`: ported `fr`'s 37 entries. Physical key
      labels (`Enter`, `Escape`, `Tab`, `Backspace`, `Delete`, `Home`,
      `End`, `Page Up/Down`, `Insert`) kept in English, matching what's
      actually printed on a Polish (QWERTY) keyboard — unlike French,
      which translates these because AZERTY keycaps print `Suppr`,
      `Échap`, `Maj`, etc. for real. `Left`/`Right` modifier sides and
      arrow directions are translated (`Lewy Shift`, `Strzałka w prawo`).
- [x] P2.1b/P2.2b (added) — `CATEGORY_MESSAGES['pl']` (12) and
      `BLOCKLY_MSG_TRANSLATIONS['pl']` (97).
- [x] P2.3 — count/key-set parity guard test against `fr`:
      `tests/test_blockly_i18n_pl.py` (7 tests, covers all 4 tables,
      following `test_blockly_i18n_uk.py`'s established structural-parse
      pattern since no Node.js is available in this environment).
- [x] P2.3b — added `pl` to the `supportedLangs` gate array (the
      IDE-language → Blockly-iframe `?lang=` query param allowlist) —
      without this, selecting Polish in the IDE would silently leave the
      embedded Blockly workspace in English even with a fully-populated
      `BLOCK_MESSAGES['pl']`.
- [ ] P2.4 — a real offscreen screenshot of the Blockly toolbox/workspace
      with `pl` selected (deferred — Blockly runs inside a `QWebEngineView`
      rendering real HTML/JS, a materially different and heavier
      verification path than Phase 1's native-Qt-widget
      `QWidget.grab()` technique; not attempted this session).

**Verification method** (no Node.js in this environment, consistent with
the repo's established "no JS engine in CI" tier): built via a one-off
Python script (not committed) that parses each table's `'fr': {...}`
block with a tolerant regex into ordered `(key, value)` pairs, asserted
the parsed count against each table's real total, then substituted in a
hand-translated Polish dict keyed by the SAME source keys (not the fr
values) and inserted the generated `'pl': {...}` block immediately after
`'fr'` in each table — eliminating any risk of inserting a value under
the wrong key. Verified post-insertion: brace/paren balance across the
whole file, key-set equality against `fr` in all 4 tables (377/377, zero
missing/extra), non-empty values, diacritics present, and the existing
`test_blockly_i18n_uk.py` (which independently parses the same file)
still passes unchanged.

### Phase 3 — Tutorials curriculum (14 lessons / 63 pages / ~34,500 English words) — **COMPLETE 2026-10-07**

Follow the pt Tutorials workflow precedent exactly (2026-08-08 session):
read the **current** English lesson content page by page (page counts have
shifted since pt was built — e.g. Tutorial 6 just gained a 5th page this
session — don't trust a stale count), translate prose, keep technical
identifiers (object/file/action/attribute names, JSON keys) in English so
the lesson keeps matching what the IDE and repo actually show. **Unlike
pt** (which kept Blockly block-label mockups in English because pt had no
Blockly coverage at all), Polish's mockups should show the **real Polish
block labels from Phase 2** — matching the precedent this session's own
Tutorial 6 bonus page set for French (its mockups use the real,
catalog-verified `Activer la vue Raycast` etc., not English placeholders).
This is why Phase 2 is sequenced before Phase 3: Tutorial translation
reuses Phase 2's already-decided terminology instead of inventing it twice.

- [x] P3.1 — Lessons 1-9 (core curriculum: Getting Started through Catch
      the Coins).
- [x] P3.2 — Lessons 11-14 (the 2.5D raycast series), including the
      `05_bonus_2_5d.html` bonus page bundled with Lesson 6.
- [x] P3.3 — Lesson 10 (file-exchange multiplayer).
- [x] P3.4 — `Tutorials/pl/index.json` registering all 14 lessons with
      their real current per-lesson page lists, confirmed against the
      English `index.json` directly (not from memory).
- [x] P3.5 — guard test: `pl` added to
      `test_tutorial_panel_i18n_verification.py`'s `LOCALIZED_LANGUAGES`;
      all 34 tests pass, every lesson's every page renders through the
      real `TutorialPanel` widget with no error-branch marker and
      substantial content. All 63 HTML files + `index.json` additionally
      confirmed to contain real Polish diacritics (a direct sweep, not
      just the generic "some file somewhere" check).

**Workflow actually used, differs from the original plan slightly:**
mockups mostly use the REAL Phase 2 Polish block labels where a block
genuinely has one (`Gdy utworzony`, `Ustaw prędkość horyzontalną na`,
`Gdy kolizja z X`, etc.), but several lessons' mockups reference actions
*outside* the 377-entry Phase 2 set entirely — the raycast `3D View`
category (Enable Raycast View, Set Facing Angle, Draw Minimap, Draw DOOM
HUD), the `Game`/`Output` categories (Show Highscore, End Game, Restart
Game), the File-Exchange multiplayer extension's own actions, and the
traditional (non-Blockly) action editor's Test-Instance-Count block —
none of these were ever in scope for Phase 2's BLOCK_MESSAGES/
CATEGORY_MESSAGES/BLOCKLY_MSG_TRANSLATIONS/KEY_NAMES tables (those cover
only the original 231+37+12+97 "core" Blockly set). For all of these,
translated naturally and consistently (cross-checked against `fr`'s own
tutorial text where available), matching the precedent `fr` itself
already established of not requiring byte-exact BLOCK_MESSAGES matches
in free-form tutorial prose. Raycast/HUD/multiplayer *parameter* names
(Field of View, Cell Size, Render Distance, Viewport Height, Wall/Sky/
Floor/Ceiling Texture, Wall/Floor/Ceiling Color, Columns, Floor Detail,
Health/Score/Objective Label, Face Sprite, Face Frames, Camera Object)
were kept in English throughout, matching `fr`'s own explicit note that
these stay English in the IDE itself.

## Not in scope

- **The wiki** (Teacher Resources, Action Reference, sample guides,
  Network/3D-View/Extensions pages) — a separate, nine-language-only
  effort (en/fr/de/uk/ru/it/es/pt/sl) from 2026-07-29 that Polish was
  never part of even as one of the originals. A full wiki translation
  arc of its own, not bundled here.
- **Refreshing es/pt/ja/zh/`de`-split's own staleness against `fr`** (the
  11-context/hundreds-of-messages gap this plan's investigation found) —
  real, legitimate, worth a `TODO.md` entry, but it's "fix drift in other
  languages," not "translate to Polish." Not touched by this plan.
- Hunting for and fixing any *new* dead-translation-context bugs the way
  the pt arc found `self.ide` and the f-string issue — `fr` is already
  confirmed clean of both known ones; if something new turns up while
  building from `fr`, fix it for `fr` (and everyone) too, same as pt did,
  but that's opportunistic, not a planned phase.

## Honest cost estimate (the user's own "two sessions, if necessary" framing)

- **Phase 1** (1849 messages): the closest precedent, ja's 1369-message
  build, ran one full session (~20 commits). Polish needs 35% more
  messages plus 11 brand-new contexts with no prior non-French language
  to crib from. Estimate: **~1 session**, possibly spilling a little.
- **Phase 2** (~240 entries, mechanical block-label translation, no prose):
  small. Estimate: **~10-15% of a session**.
- **Phase 3** (~34,500 words of lesson prose): the nearest anchor is the
  French sample-guide effort — ~13,500 English words ≈ 40% of a session —
  but that number includes a Romance-language speed advantage Polish does
  not get (same reasoning already established for ja/zh vs pt). Scaled up
  by word count alone, with no language-family discount: **~1.5-2 full
  sessions**, realistically.
- **Total: roughly 2.5-3+ sessions**, not 2. If the two sessions the user
  is budgeting need to produce the most usable result possible, do
  **Phases 1 and 2 first** (a fully Polish running app, menus and Blockly
  workspace both) — that alone is a complete, shippable "the IDE is
  translated into Polish" outcome matching the literal request, even if
  Phase 3 (lesson content) needs a third session. Phase 3 is the most
  likely phase to carry over.

## Session checkpoint discipline

One commit per context-batch/phase-unit, pushed immediately — matching
every prior language arc and this repo's standing "size every task to the
session limit, commit after each" preference. At the end of any session
(even mid-phase), update this doc's checkboxes and status line before
stopping, so a different session (or machine) resumes from exactly the
right place: the next unchecked box, nothing re-derived from scratch.
