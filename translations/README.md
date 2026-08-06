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

Reflects what's actually compiled as of 2026-08-06 (`ls translations/*.qm`):

- English (en) - built-in default, no translation file
- French (fr) - `pygm2_fr.qm` (monolithic)
- Spanish (es) - `pygm2_es.qm` (monolithic)
- German (de) - `pygm2_de*.qm` (split)
- Italian (it) - `pygm2_it*.qm` (split)
- Slovenian (sl) - `pygm2_sl*.qm` (split)
- Ukrainian (uk) - `pygm2_uk*.qm` (split)
- Russian (ru) - `pygm2_ru*.qm` (split)
- Portuguese (pt), Japanese (ja), Chinese (zh) - `.ts` source exists
  (`pygamemaker_pt.ts`/`_ja.ts`/`_zh.ts`, pre-`pygm2`-naming) but is not yet
  compiled to `.qm`, so none of the three currently appear in the app's
  Tools > Language menu. See `docs/I18N_CLEANUP_2026-08-06.md` Section H.

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
