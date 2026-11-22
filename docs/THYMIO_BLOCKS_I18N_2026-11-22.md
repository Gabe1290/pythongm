# Thymio Blockly blocks in the IDE language (2026-11-22)

**Decided by the owner:** the Thymio blocks follow the IDE language. Untouched on purpose: the
Thymio **events panel and action list** (`THYMIO_ACTIONS` / `THYMIO_EVENT_TYPES` display names),
which the French activity sheets name in English (`tests/test_thymio_fiches_docs.py`).

**Two surfaces:**
1. **Thymio's Configure dialog** (`ThymioConfigDialog`): 42 entries (28 blocks + 14 events), name +
   description, via the extension's `PLUGIN_BLOCK_TRANSLATIONS` (the loader already merges it). All
   eleven languages, like the core Configure dialog.
2. **The 28 Thymio blocks in the Blockly workspace** (`blockly_blocks.js`, hard-coded English): every
   label, tooltip and drop-down label goes through `thymioMsg("English")`, a lookup keyed by the
   English text in `THYMIO_BLOCK_MESSAGES` (`blockly_i18n.js`), falling back to English. Drop-down
   **values** do not change, so saved workspaces and generated code are unaffected. Languages: the five
   the workspace already has (`BLOCK_MESSAGES`: fr, pl, de, it, uk), so Thymio blocks match the core
   blocks beside them.

**Found while scoping, not in this plan:** the workspace's own table covers only fr/pl/de/it/uk, so in
es, ru, sl, pt, ja and zh **every** Blockly block (core too) shows English. Logged in TODO.md.

## Queue (one commit each)

- [x] U1 Configure dialog names, 42 entries x 11 languages
- [x] U2 workspace: `thymioMsg` wrapping + French
- [x] U3 workspace: de, it, pl, uk (landed with U2: one table, five languages)
- [x] U4 guards, TODO.md, QA checklist

**Done 2026-11-22.** No native speaker has read the new text.
