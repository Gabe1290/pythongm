# Plan: closing the "organically maintained" languages' unfinished-translation gap

Status: **in progress.** Written 2026-08-10, right after
`tests/test_extension_ui_translations.py` (commit `051de39`) found that
German's shipped catalogs carry 151 never-completed
`<translation type="unfinished"></translation>` entries — the Preferences
dialog's own "General" tab has never been translated to German at all.
User asked to scope and address the same gap in the other six
"organically maintained" languages (es/fr/it/ru/sl/uk), not just German.

## What "organically maintained" means here, and why this gap exists

Unlike pt/ja/zh — each built **complete** from a clean reference via
`scripts/gen_translation_ts.py` and verified 1369/1369 active messages in
the 2026-08-09 i18n arc (`docs/I18N_CLEANUP_2026-08-06.md` Section H) — the
other seven languages (de/es/fr/it/ru/sl/uk) were maintained incrementally
over many sessions, each adding whatever strings that session's feature
touched. Nothing ever swept them for 100% completeness against current
source the way pt/ja/zh were. `lupdate`-style tooling (this repo runs
`lrelease` only, never `lupdate` — see `CLAUDE.md`) marks any source string
it can't find an existing translation for as
`<translation type="unfinished"></translation>` — an empty stub that
`lrelease` compiles as-is, so Qt's `QTranslator` falls back to the English
source at runtime. These are all **active** strings (every one has a
`<location>` tag, i.e. still referenced by current source — confirmed via
script, zero "vanished" false positives), not dead entries safe to ignore.

## Confirmed counts (2026-08-10, counted directly against each shipped file)

| Language | Shipped file(s) | Empty `unfinished` entries |
|---|---|---|
| de | `pygm2_de_{core,editors,actions,blockly,dialogs,misc}.ts` | 151 |
| it | same split, `_it_` | 151 |
| ru | same split, `_ru_` | 153 |
| sl | same split, `_sl_` | 153 |
| uk | same split, `_uk_` | 152 |
| fr | `pygm2_fr.ts` (monolithic) | 47 |
| es | `pygm2_es.ts` (monolithic) | 294 |

**Total: 1101 active, empty, real gaps.** For scale: comparable to roughly
80% of pt's *entire* from-scratch UI catalog (1369 messages) — this is a
multi-session undertaking, not a same-session fix. Counted via
`<translation type="unfinished"></translation>` string match (empty stub)
AND cross-checked that `type="unfinished"` entries WITH real content inside
(a rarer, less severe "needs review" state, not a hard gap) are excluded —
158/158/158/158/158/58/360 is the raw `type="unfinished"` count including
those; the empty-only numbers above are the real target.

## The five split languages share almost the same list

de/it/ru/sl/uk's missing-string SETS overlap almost completely: **146
sources common to all five**, **148 in the union** (only 2 outliers). This
means the split-language gap is functionally **one shared ~148-string
list**, independently untranslated into 5 languages — not 5 unrelated
problems. Work language-by-language still (can't share the translation
itself across languages), but the SOURCE list and its context/location
metadata only needs deriving once and can be reused for all five.

fr's 47 overlap 37/41 (distinct sources) with that shared list — fr is
mostly "the same shared gap, already 3/4 filled in" plus a handful of
fr-specific misses. es's 294 overlap only 130/294 with the shared list — es
has a substantially larger INDEPENDENT gap beyond what the others are
missing (~164 es-only gaps), consistent with es being the least
"organically maintained" of the seven historically.

## Recommended work order

Smallest-and-cleanest first, to establish and verify the workflow before
the bigger units, then largest remaining gap last (es):

1. ~~**fr (47 entries, 1 file)**~~ — smallest, single monolithic file, good
   first slice to prove the extraction→translation→verification pipeline
   end to end.
2. **de (151), it (151), ru (153), sl (153), uk (152)** — the shared
   ~148-string list, one language at a time (five units, each its own
   commit or small batch of commits depending on how it goes — pt's own
   precedent was 1-10 contexts / 10-80 strings per commit for a much
   bigger catalog, so each of these fits in 1-3 commits).
3. **es (294)** — largest remaining, tackle last, likely needs its own
   multi-commit pass given size (compare: pt's full 1369-message catalog
   took ~24 commits: `scripts/gen_translation_ts.py`'s own docstring cites
   this history).

## Method (same tooling as the extension-UI fix, commit `051de39`)

Extract missing `(context, source, locations)` triples directly from each
target `.ts` file with a small script (not `scripts/gen_translation_ts.py`
— that tool pulls source text FROM an existing reference `.ts` context, but
these sources already exist in the SAME file, just with an empty
`<translation type="unfinished">` — so the fix is an in-place **replace**,
not an **append**). For each language:

1. Regex out every `(context, source, locations)` where the message has
   `<translation type="unfinished"></translation>` and at least one
   `<location>`.
2. Translate each source string, cross-checking terminology against:
   - that language's own already-translated neighboring strings in the
     same context (voice/register consistency),
   - that language's translated wiki pages (`wiki/*_<lang>.md`) for
     established nouns/verbs when the string touches a documented concept
     (extensions, tutorials, editions, etc.) — this is what caught the
     French "Extensions" cognate false-positive in the previous commit's
     test,
   - pt/ja/zh's own already-complete translations of the SAME source
     string (available since those three are 100% complete) as a
     cross-language sanity check on meaning, not as a literal source to
     translate from.
3. Replace `<translation type="unfinished"></translation>` in place with
   `<translation>{translated text}</translation>` (drop the
   `type="unfinished"` attribute — that's what marks it done to `lrelease`
   and to any future `lupdate`-style tooling).
4. Recompile via `scripts/compile_translations.py`.
5. Regression test per language/batch: every targeted source now has a
   non-empty, non-English-copy translation (with the same per-language
   cognate exceptions the extension-UI test established, e.g. fr's
   "Extensions"), a live `QTranslator` resolves a sample directly, and (for
   at least one language per batch, budget permitting) a screenshot spike
   of a widget that surfaces some of the fixed strings — same
   `QWidget.grab()` under `QT_QPA_PLATFORM=offscreen` technique the
   extension-UI fix introduced.
6. Full-suite gate, commit, push. One commit per language (or a few for the
   larger ones), immediately, per this repo's standing session-limit
   discipline — never batch multiple languages into one commit.

## Verification landmines already known (carry forward from prior i18n work)

- XML entity-escaped source text must match EXACTLY (`&amp;`, `&apos;`,
  `&quot;`, `&lt;`, `&gt;`) — copy the literal `<source>` text, don't
  retype by hand.
- Translation VALUES must use real unescaped characters — the
  `TranslationBuilder`/any hand-rolled writer must XML-escape them; a
  double-escaped value (`&amp;gt;` instead of `&gt;`) passes XML validity
  and `lrelease` silently and only shows up as literal escaped text at
  runtime (caught once already in the zh work, per `CLAUDE.md`).
- CJK menu mnemonics keep the original English letter in parentheses
  (`"&File"` → `"ファイル(&F)"`) — not relevant here (this batch is
  de/es/fr/it/ru/sl/uk, no CJK), but the general lesson (check for existing
  per-language conventions before assuming a pattern transfers) applies to
  any string with a `&` mnemonic.
- `self.tr(f"...")` f-strings are dead on arrival (interpolated before
  `tr()` ever sees them) — if any of these 1101 gaps turn out to be an
  f-string bug rather than a genuinely-missing translation, fix the source
  code first (matching the `self.ide` and `ThymioPlaygroundWindow`
  precedents), not just add a translation that can never be reached.
- Recompile and spot-check via a live `QTranslator` every batch — don't
  trust that "XML looks right" means "resolves at runtime."

## Registry (flip to DONE with the commit hash as each unit lands)

- [x] **fr** (47 entries) — DONE 2026-08-10. `tests/test_i18n_unfinished_fr.py`
      (3 tests: XML presence, live-QTranslator resolution for all 47).
      Terminology cross-checked against fr's own existing translations for
      repeated menu items (Fichier/Nouveau projet/Ouvrir un projet/
      Enregistrer le projet/Tester le jeu/Déboguer le jeu/Exporter le jeu).
- [ ] **de** (151 entries, shared list) —
- [ ] **it** (151 entries, shared list) —
- [ ] **ru** (153 entries, shared list) —
- [ ] **sl** (153 entries, shared list) —
- [ ] **uk** (152 entries, shared list) —
- [ ] **es** (294 entries, largest independent gap) —
