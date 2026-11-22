# Configure Blocks dialog: pl / pt / ja / zh (2026-11-22)

**Problem.** The Configure Blocks dialog (`dialogs/_block_config_dialog_base.py`) names
categories and blocks through `config/blockly_translations.py`
(`CATEGORY_TRANSLATIONS`, `BLOCK_TRANSLATIONS`), which covered only de/es/fr/it/ru/sl/uk.
For Polish, Portuguese, Japanese and Chinese the whole dialog was English: 13 categories,
121 blocks (name + description) = 255 strings per language.

**Method.** One module per language, `config/blockly_block_i18n_<lang>.py`, holding
`CATEGORIES = {category: text}` and `BLOCKS = {block_type: (name, description)}`; merged into
the two tables at the bottom of `blockly_translations.py`. Terminology follows each language's
existing Qt catalogue (`translations/pygm2_<lang>.ts`) and, where present, its
`blockly_i18n.js` workspace labels. The guard
`tests/test_blockly_config_dialog_all_blocks_i18n.py` gains each language as it lands.
Scope: the core registry only (Thymio's own dialog tables are separate).

## Queue (one commit each)

- [x] U1 pl
- [x] U2 pt (Brazilian, as the pt catalogue)
- [x] U3 ja
- [x] U4 zh
- [x] U5 close: TODO.md entry, guard covers all eleven languages

**Done 2026-11-22.** All four languages landed (`e9c1d8ba`, `aa887f4c`, `bbea712f`, and the zh commit). No native speaker has read them.
