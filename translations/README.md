# PyGameMaker IDE Translations

This directory contains translation files for PyGameMaker IDE.

## File Format

- `.ts` files: XML source files (human-readable, edited by translators)
- `.qm` files: Binary compiled files (used by the application)

## Naming

Files use the `pygm2_<lang>[_<group>].ts`/`.qm` scheme, not the older
`pygamemaker_<lang>.qm` naming this file used to document (that scheme is
unreachable dead code as of 2026-08-06 — nothing in the app loads it; see
`core/language_manager.py::_discover_languages()`, which only globs `*.qm`,
and `scripts/compile_translations.py`, which only compiles the `pygm2_*`
naming).

A language ships either as one monolithic `pygm2_<lang>.ts`/`.qm`, or split
across `pygm2_<lang>_core.ts`, `_actions.ts`, `_blockly.ts`, `_dialogs.ts`,
`_editors.ts`, `_misc.ts` (each compiling to its own `.qm`) — the language
manager loads whichever set exists for a given language; the two forms
aren't mixed for the same language.

## Available Languages

Reflects what's actually compiled as of 2026-08-09 (`ls translations/*.qm`):

- English (en) - built-in default, no translation file
- French (fr) - `pygm2_fr.qm` (monolithic)
- Spanish (es) - `pygm2_es.qm` (monolithic)
- Portuguese (pt) - `pygm2_pt.qm` (monolithic) - fully translated as of
  2026-08-08 (1369/1369 real distinct UI strings; see
  `docs/I18N_CLEANUP_2026-08-06.md` Section H). The old pre-`pygm2`
  `pygamemaker_pt.ts` stub (289 entries, all untranslated) was deleted
  once this real replacement existed.
- Japanese (ja) - `pygm2_ja.qm` (monolithic) - fully translated as of
  2026-08-09 (1369/1369 real distinct UI strings, built from
  `pygm2_pt.ts` via `scripts/gen_translation_ts.py` per
  `docs/JA_ZH_I18N_PLAN.md`). The old pre-`pygm2` `pygamemaker_ja.ts`
  stub (289 entries, all untranslated) was deleted once this real
  replacement existed.
- German (de) - `pygm2_de*.qm` (split)
- Italian (it) - `pygm2_it*.qm` (split)
- Slovenian (sl) - `pygm2_sl*.qm` (split)
- Ukrainian (uk) - `pygm2_uk*.qm` (split)
- Russian (ru) - `pygm2_ru*.qm` (split)
- Chinese (zh) - `.ts` source exists (`pygamemaker_zh.ts`, pre-`pygm2`-
  naming, 289 untranslated entries) but is not yet compiled to `.qm`,
  so it doesn't currently appear in the app's Tools > Language menu.
  See `docs/JA_ZH_I18N_PLAN.md` for the ja precedent to follow —
  source-string list (`pygm2_pt.ts`), generator-script approach
  (`scripts/gen_translation_ts.py`), per-context verification
  discipline.

## Compiling

```bash
python scripts/compile_translations.py
```

Finds every `.ts` in this directory and compiles it via `lrelease`
(bundled with PySide6). A split `pygm2_<lang>_<group>.ts` is only compiled
when that language already has a split `.qm` set — see the function
docstring in `scripts/compile_translations.py` for why (compiling a sparse
split set for a language that ships a complete monolithic `.qm` would
hijack the language manager's preference away from the complete file).

**Note:** this repo runs `lrelease` only, never `lupdate` — `.ts` source
strings are maintained by hand, not auto-extracted from `**/*.py`. Existing
`type="vanished"` entries in a `.ts` file are stale bookkeeping from before
that convention was settled, not evidence a string is unused.
