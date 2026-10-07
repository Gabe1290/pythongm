# Polish (`pl`) translation — plan

Written 2026-10-07. Status: **plan only, nothing implemented yet.**

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

### Phase 1 — Qt UI catalog (1849 messages / 73 contexts)

- [ ] P1.0 — this plan, committed first.
- [ ] P1.1 — the ~60 small/medium contexts `fr` and pt/ja/zh both already
      have (re-derive each one's source strings from `fr`, not pt, since
      `fr` is a strict superset — several of these contexts also grew
      beyond pt's old counts).
- [ ] P1.2 — the 11 contexts that only exist in `fr`: `AboutDialog`,
      `BackgroundEditor`, `BlockWorldEditorWindow`, `EventActionWidget`,
      `FindReplaceDialog`, `FontEditor`, `GM80EventsPanel`,
      `OrphanedFilesDialog`, `SoundEditor`, `TrashDialog`,
      `UnusedAssetsDialog` — no pt/ja/zh precedent to crib structure from,
      budget as first-time work.
- [ ] P1.3 — `PyGameMakerIDE` (361 messages: menus + mnemonics, toolbar,
      status bar, every File/Edit/Assets/Build/Tools/Help flow, the Export
      dialog's per-platform strings, the About dialog's HTML blocks) via
      several `add_partial_context` batches.
- [ ] P1.4 — check for a legacy `translations/pygamemaker_pl.ts` stub (the
      kind pt/ja/zh each had and deleted once superseded) — delete it only
      if one actually exists; Polish may never have had one.
- [ ] P1.5 — add `"pl"` to every hardcoded per-language test list (see
      Guard tests); confirm `pl` is discoverable in
      `LanguageManager._discover_languages()` once the `.qm` compiles.
- [ ] P1.6 — guard tests: diacritics sweep, unfinished-entry sweep, live
      `QTranslator` resolution across a representative sample, full suite
      green.

### Phase 2 — Blockly block-level translation (~240 entries)

- [ ] P2.1 — `BLOCK_MESSAGES['pl']`: port `fr`'s 231 entries (event/action
      block labels + tooltips) into `blockly_i18n.js` as a new top-level
      language block.
- [ ] P2.2 — `KEY_NAMES['pl']`: port `fr`'s 9 entries.
- [ ] P2.3 — count/key-set parity guard test against `fr`.
- [ ] P2.4 — a real offscreen screenshot of the Blockly toolbox/workspace
      with `pl` selected, same technique as Phase 1's Preferences check,
      if feasible in this environment.

### Phase 3 — Tutorials curriculum (14 lessons / 63 pages / ~34,500 English words)

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

- [ ] P3.1 — Lessons 1-9 (core curriculum: Getting Started through Catch
      the Coins).
- [ ] P3.2 — Lessons 11-14 (the 2.5D raycast series) — `fr`'s own Tutorial
      11-14 content and block-view mockup conventions are the structural
      template, same ones this session's Tutorial 6 bonus page reused.
- [ ] P3.3 — Lesson 10 (file-exchange multiplayer) and Tutorial 6's new
      bonus page (`05_bonus_2_5d.html`, added this session) — the newest
      content; don't let it fall through the cracks between the "pt did
      1-9" and "fr did 11-14" precedents.
- [ ] P3.4 — `Tutorials/pl/index.json` registering all 14 lessons with
      their real current per-lesson page lists (confirm each from the
      English `index.json`, not from memory).
- [ ] P3.5 — guard test: `pl` added to
      `test_tutorial_panel_i18n_verification.py`'s `LOCALIZED_LANGUAGES`;
      every lesson's every page renders through the real `TutorialPanel`
      widget with no error-branch marker and substantial content.

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
