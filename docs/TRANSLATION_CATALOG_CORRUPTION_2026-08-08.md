# Translation-catalog corruption: es/sl/ru UI strings (found 2026-08-08)

Discovered while verifying real menu/UI text for the Section L (in-app
Tutorials i18n) work in `docs/I18N_CLEANUP_2026-08-06.md` — a lesson can't
accurately describe "right-click Sprites → Create New Sprite" in Spanish if
the actual live Spanish string is wrong. Checking the real `.ts` catalog
against source turned up a much bigger, pre-existing, live bug unrelated to
Tutorials: large fractions of the Spanish, Slovenian, and Russian UI
catalogs are not real translations at all.

## The bug

Two distinct corruption patterns, found in the `.ts` files that are
**actually loaded by the running app** (see "Which files are live" below):

1. **French-copy contamination** — the `<translation>` for a source string
   is verbatim identical to the French translation of that same string,
   not a Spanish/Slovenian/Russian translation. Example (`pygm2_es.ts`):
   ```xml
   <source>➕ Create New {0}...</source>
   <translation>➕ Créer un nouveau {0}...</translation>
   ```
   `Créer un nouveau` is French for "Create new" — a Spanish speaker gets
   French menu text. This is the dominant failure mode for **es** (406/452
   bad entries) and **sl** (391/421).
2. **Untranslated English passthrough** — `<translation>` is byte-identical
   to `<source>`, i.e. never translated at all (not a `type="unfinished"`
   stub — a normal-looking, apparently-complete entry that just repeats the
   English). Dominant failure mode for **ru** (307/332 bad entries).

Root cause not established (no `git blame`/session-note trail points to a
specific origin) — most likely an earlier automated/LLM-assisted
translation pass that got its per-language source lists crossed for es/sl
(both landed on fr's output) and simply skipped translating a large chunk
of ru. Not investigated further since it doesn't change the fix.

## Which files are live (read this before editing anything)

`core/language_manager.py::_get_translation_files` prefers the **split**
`pygm2_<lang>_<group>.qm` set (`TRANSLATION_GROUPS = ['core', 'editors',
'actions', 'dialogs', 'blockly', 'misc']`) over the monolithic
`pygm2_<lang>.qm` **whenever the split set exists** — it does not merge
the two. Compiled-`.qm` inventory as of this writing:

- **es**: no split `.qm` set → the app loads **monolithic
  `pygm2_es.ts`/`.qm` only**. Fix that one file.
- **sl**: split `.qm` set exists → the app loads the **6 split
  `pygm2_sl_<group>.ts` files**; the monolithic `pygm2_sl.ts` is NOT
  loaded and was excluded from this audit (may also be stale — not
  in scope here; note left for a future pass).
- **ru**: same as sl — **6 split `pygm2_ru_<group>.ts` files** are live;
  monolithic `pygm2_ru.ts` excluded, same caveat.

`scripts/compile_translations.py`'s own `should_compile()` encodes this
same rule (it's what stopped a naive "just compile everything" from
silently creating a new, mostly-empty split `.qm` set for a language that
should stay monolithic — see its docstring). Run
`python3 scripts/compile_translations.py` after every `.ts` edit in this
plan; it recompiles the whole `translations/` directory safely (confirmed
2026-08-08: a no-op run against the pre-fix files reproduced byte-identical
`.qm`s, no `git status` diff).

## Exact scope (post-filter)

Detection: for every live `.ts` file, flag a `<message>` whose
`<translation>` (excluding `type="vanished"` entries, which are dead by
design) either equals its own `<source>` verbatim (English passthrough) or
equals `pygm2_fr*.ts`'s translation of that same source (French copy). A
handful of matches were **content-free false positives** — sources with no
actual letters once placeholders/entities are stripped (e.g. `'🎨 {0}'`,
which is correctly identical in every language because there is nothing to
translate) — filtered out (47 across all three languages).

| Language | Live file(s) | French-copy | English-passthrough | Total to fix |
|---|---|---|---|---|
| es | `pygm2_es.ts` | 406 | 30 (46 raw − 16 no-op) | **436** |
| sl | `pygm2_sl_{core,editors,actions,dialogs,blockly}.ts` (misc: 0 bad) | 391 | 15 (30 raw − 15 no-op) | **406** |
| ru | `pygm2_ru_{core,editors,actions,dialogs,blockly,misc}.ts` | 25 | 291 (307 raw − 16 no-op) | **316** |
| **Total** | | | | **1,158** |

Per-file breakdown (raw counts before the no-op filter; the filter only
ever removes `english_passthrough` entries, so `french_copy` counts below
are already final):

- `pygm2_es.ts`: 452 raw (406 french_copy + 46 english_passthrough)
- `pygm2_sl_core.ts`: 100 · `pygm2_sl_editors.ts`: 125 · `pygm2_sl_actions.ts`: 4
  · `pygm2_sl_dialogs.ts`: 177 · `pygm2_sl_blockly.ts`: 15 (sl total 421 raw)
- `pygm2_ru_core.ts`: 11 · `pygm2_ru_editors.ts`: 128 · `pygm2_ru_actions.ts`: 5
  · `pygm2_ru_dialogs.ts`: 163 · `pygm2_ru_blockly.ts`: 20 · `pygm2_ru_misc.ts`: 5
  (ru total 332 raw)

This is comparable in size to the entire Section K sample-guide translation
tier (which took the rest of a long session for ~54 net-new files) — budget
it the same way: **multi-session, one file per commit, no shortcuts.**

## Methodology

1. **Never trust the corrupted language's existing `<translation>` as a
   starting point or reference** — translate fresh from `<source>` (the
   English original). fr's translation may be used as *context* for intent
   (what the string means, not what to write).
2. **Preserve exactly, byte-for-byte, inside the translated string:**
   - Qt positional placeholders: `%1`, `%2`, …
   - Python-style `.format()` placeholders baked into the source: `{0}`,
     `{1}`
   - XML entities: `&amp;`, `&apos;`, `&lt;`, `&gt;`, `&quot;`
   - Qt accelerator mnemonics: a literal `&` before a letter (encoded as
     `&amp;` in the XML) marks the Alt-key-underlined character in a menu
     — pick a sensible letter in the *translated* word, not necessarily
     the same letter as English/French.
   - Emoji/symbol prefixes (➕, 📋, 🎨, ✓, →, ←, ↺, …) — copy verbatim,
     don't translate or drop them.
   - Literal newlines inside multi-line `<source>` blocks (e.g. the
     About-dialog credits text) — match the line structure.
3. **Leave `<message>` structure, `<location>` tags, and any `type="..."`
   attribute completely untouched** — only the text content of
   `<translation>` changes. Entries with `type="vanished"` are dead
   (already excluded from the counts above) — don't touch them.
4. **One file = one commit.** Translate the file's full bad-entry list,
   apply, recompile (`python3 scripts/compile_translations.py`), run the
   full suite (`QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q`),
   spot-check a handful of the new strings by reading them back out of the
   `.ts`, commit + push. This mirrors the `docs/I18N_CLEANUP_2026-08-06.md`
   discipline exactly.
5. **Verification, not vibes:** after each file, re-run the same detection
   script (`french_copy`/`english_passthrough` scan against `pygm2_fr*`)
   against just that file and confirm zero remaining matches before
   committing — don't rely on "I translated N entries" bookkeeping alone.

## Work queue

- [x] `pygm2_es.ts` (436 entries) — commit `e7cb4a7`. Also found: 308
  entries with genuinely-empty `<translation>` (never attempted, not
  corrupted) — a separate, pre-existing incompleteness, out of this
  registry's scope; left untouched.
- [x] `pygm2_sl_dialogs.ts` (171 after no-op filter) — commit `a02608b`
- [x] `pygm2_sl_editors.ts` (117 after no-op filter) — commit `cd1755d`
- [x] `pygm2_sl_core.ts` (100) — commit `8d8f453`
- [x] `pygm2_sl_blockly.ts` (15) — commit `39892cf`
- [x] `pygm2_sl_actions.ts` (4) — commit `39892cf`. **Slovenian fully closed.**
- [x] `pygm2_ru_dialogs.ts` (157 after no-op filter) — commit `fb5347d`
- [ ] `pygm2_ru_editors.ts` (128) — 1 commit
- [ ] `pygm2_ru_blockly.ts` (20) — 1 commit
- [ ] `pygm2_ru_core.ts` (11) — 1 commit
- [ ] `pygm2_ru_misc.ts` (5) — 1 commit
- [ ] `pygm2_ru_actions.ts` (5) — 1 commit

12 file-units, ~1,158 individual strings. Work largest-impact-first within
each language (dialogs/editors carry the most user-visible surface); order
across languages doesn't matter.

## Relationship to Section L (Tutorials i18n)

This was found *because of* Section L, but is **not part of** Section L's
scope (`docs/I18N_CLEANUP_2026-08-06.md`, Tutorials HTML only) and is not
part of Section K either. User decision (2026-08-08): fix this catalog
corruption **before** resuming Section L, since Section L's lesson text
would otherwise need to describe UI strings that are currently wrong,
producing tutorials that are "accurate to a bug" instead of accurate to
the intended app. Resume Section L once this registry is closed (or if the
user redirects sooner).

## Related, already-fixed finding

While investigating this, a structurally different but adjacent bug was
found and fixed same-day: `editors/object_editor/blockly/blockly_i18n.js`
had a complete Ukrainian `BLOCK_MESSAGES` translation set pasted under
`CATEGORY_MESSAGES['uk']` instead of `BLOCK_MESSAGES['uk']`, making it
100% unreachable at runtime. Fixed and covered by
`tests/test_blockly_i18n_uk.py` (commit `cedb370`). Not part of this
registry's scope (JS Blockly-block text, not the Qt `.ts` UI catalog) but
recorded here since it was found in the same investigation and is the
same class of "translation exists but is unreachable/misfiled" bug.
