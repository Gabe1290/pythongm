# Translating the Thymio events panel and action list — plan (2026-11-22)

**Status: owner chose the recommendations (2026-11-22); in progress — see the checkboxes.** Asked for by the owner after the Thymio Blockly blocks
and Configure dialog were translated (`docs/THYMIO_BLOCKS_I18N_2026-11-22.md`). Decisions D1–D4 below
need the owner's answer before U1 starts.

## What a user sees today

The Thymio tab of the object editor (`extensions/thymio/object_editor_panel.py`), its event and action
pickers (`dialogs/thymio_event_selector.py`, `dialogs/thymio_action_selector.py`), the Thymio entries
in the Standard events panel's Add Event menu (`panel_menus.py`) and the action configure dialog all
show the English names from `THYMIO_ACTIONS` / `THYMIO_EVENT_TYPES`, in every language.

| Kind | Count | Where it comes from |
|---|---|---|
| Actions: name + description | 28 + 28 | `extensions/thymio/actions.py` |
| Action parameters: name + description | 54 + 54 | same |
| Parameter choice labels | 36 values, ~25 with words (`0 - Front Left Far`, `0 - Startup`) | same |
| Events: name + description | 14 + 14 | `extensions/thymio/events.py` |
| Category labels | 5 event + 7 action | `THYMIO_EVENT_CATEGORIES`, `THYMIO_ACTION_CATEGORIES` |
| **Distinct strings** | **~186** | |

**Why:** the names are *data*. Where they are shown at all through Qt they go through `self.tr(name)`,
which only works if the catalogue happens to hold that exact text in that exact class's context, and
for Thymio it never does. The Thymio tab itself does not even call `tr()` (`object_editor_panel.py`
lines 158/180/201 show `display_name` raw).

**The same gap exists for core, and is larger (measured 2026-11-22, live in the running app):** in the
Standard events panel, French translates **49 of 186** action names and **7 of 73** event names; German
**49** and **0**. So this plan builds the mechanism that core will need too (see D2).

## What depends on the English names

- **The French activity sheets** (`docs/thymio_fiches/fiche_1..9.fr.md`, `corrige.fr.md`) name each
  action and event exactly as the IDE shows it, pinned by
  `tests/test_thymio_fiches_docs.py::test_every_action_and_event_of_the_solutions_is_named_as_the_ide_shows_it`.
  Once a French IDE shows French names, the sheets must use the French names, or they contradict the
  screen. Their PDF/ODT copies (`docs/thymio_fiches/pdf`, `odt`) and the Thymio-tab screenshot
  `img/fiche_1_onglet_thymio.png` change with them.
- **Saved projects** store action/event *keys* (`thymio_set_motor_speed`) and parameter *values*, never
  display names — to verify for every parameter whose choice text is also its stored value (`0 - Left`?).
  If any choice's text IS the value, the combo box must show the translation and keep the value as
  item data, or old projects would no longer match.
- **The Aseba export, simulator and Send to Thymio** use keys and values only: unaffected, to verify.
- `samples/thymio_hw_test/README.md` / `.fr.md`: contain no action names (checked).

## Decisions for the owner

- **D1 — Where the translations live.** *Recommended:* the extension carries its own table
  (`extensions/thymio/ui_translations.py`, `{kind: {english: {lang: text}}}`), like the micro:bit's
  `translations_<lang>.py`, exposed as `PLUGIN_UI_TRANSLATIONS`; a small core helper
  `ui_name(kind, english)` looks there first and then in the Qt catalogue. Keeps the extension
  self-contained (a folder extension cannot ship `.ts` files) and is testable without Qt. *Alternative:*
  `.ts` entries under one fixed context (e.g. `"ThymioNames"`) — fits core better but ties the
  extension to core's catalogues.
- **D2 — Scope.** *Recommended:* Thymio now, with the helper written so core's 186 actions / 73 events
  can use it in a follow-up plan (the measured gap above). *Alternative:* do core in the same effort
  (about 3x the strings; core action names also appear in the Blockly Configure dialog and the wiki's
  generated action reference, which already has its own tables in `tools/action_ref_i18n.py` — worth
  reusing).
- **D3 — The French sheets.** *Recommended:* switch them to the French names the French IDE will
  show, retake the one screenshot, regenerate PDF/ODT, and change the test to check the French names.
  *Alternative:* keep English names in the sheets and tell teachers to switch the IDE to English —
  not recommended for 8–12-year-old French speakers.
- **D4 — Languages.** *Recommended:* all eleven, like the rest of the IDE text (the Blockly workspace's
  own five-language limit does not apply to panels).

## Units (one commit each, assuming the recommendations)

- [x] **U0 — DONE 2026-11-22: choice text IS the stored value.** `GM80ActionDialog` (the configure
  dialog every Thymio action uses) fills choice combos with `addItems(options)` and saves
  `currentText()`; on reopen it calls `setCurrentText(saved)`. So a project stores the full English
  label (`"0 - Startup"`, `"2 - Front Center"`), and both readers recover the index from it: the Aseba
  exporter (`_choice_index`, split on `" - "`) and the simulator (`handlers._CHOICE_LABEL_RE`,
  `^\d+ - [A-Za-z]` -- a Latin letter, so a Cyrillic or Japanese label would silently fall back). **U3
  must therefore show the translation but keep the English label as the item's data, save the data, and
  select by data on reopen.** Projects keep storing English labels; nothing else changes.
- [x] **U1 — The helper** (`core/ui_names.py`, done; extension tables then English -- the Qt-catalogue step is left for the core follow-up, which is the only user). `ui_name(kind, english)` in core (extension tables, then Qt catalogue, then
  English) + the plugin-loader hook for `PLUGIN_UI_TRANSLATIONS`. Tests: lookup order, fallback,
  unknown language.
- [ ] **U2 — Thymio's table, eleven languages.** ~186 strings. Reuse the wording already chosen for the
  Configure dialog (`block_translations.py`) where the same thing is named, so the dialog, the blocks
  and the panel agree. Guard test: every name, description, parameter label, choice label and category
  has all eleven languages; French accents; same-word list explicit.
- [ ] **U3 — Show it.** Route every display site through `ui_name`: the Thymio tab (event/action trees,
  category buttons and menus), both selectors, `panel_menus.py`, the action configure dialog's title and
  parameter labels, choice combos (with item data if U0 says so). Real-widget test in French and
  Japanese: build each panel/dialog and read what it shows; no English left except the listed same
  words; a project saved before still loads, shows the same selections and exports the same Aseba code
  (byte-identical `.aesl` before/after).
- [ ] **U4 — The sheets (D3).** French names in `fiche_1..9` and `corrige`, re-shot screenshot, PDF/ODT
  regenerated (the ODT generator never overwrites: delete first), test switched to the French names.
- [ ] **U5 — Close.** QA checklist §11b/§17 items, TODO.md, and a note in `extensions/thymio/README.md`.

## Risks

- **Stored values that are display text** (U0) — the one way this could break saved projects or the
  export. Checked before anything else.
- **Two vocabularies drifting** — the Configure dialog, the Blockly blocks and the panel each name the
  same action. U2 reuses one wording; a test can pin that the panel's action name equals the Configure
  dialog's entry where both exist.
- **The sheets** must change in the same release as U3, or a French classroom sees French buttons and
  English instructions.

**Rough size:** U0–U1 small; U2 ~186 strings x 11 languages (about the size of the Configure-dialog
work); U3 moderate (5 display sites, careful with combos); U4 nine sheets + corrigé.
