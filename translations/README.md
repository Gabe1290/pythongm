# PyGameMaker IDE Translations

This directory contains translation files for PyGameMaker IDE.

## File Format

- `.ts` files: XML source files (human-readable, used by translators)
- `.qm` files: Binary compiled files (used by the application)

## Available Languages

- English (en) - Built-in default
- French (fr) - pygamemaker_fr.qm
- Spanish (es) - pygamemaker_es.qm
- German (de) - pygamemaker_de.qm
- Italian (it) - pygamemaker_it.qm
- Portuguese (pt) - pygamemaker_pt.qm
- Russian (ru) - pygamemaker_ru.qm
- Chinese (zh) - pygamemaker_zh.qm
- Japanese (ja) - pygamemaker_ja.qm

## Creating Translations

1. Extract translatable strings:
```bash
   pylupdate6 **/*.py -ts translations/pygamemaker_LANG.ts