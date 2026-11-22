# Translating the core action and event names — plan (2026-11-22)

**Status: owner chose the recommendations (2026-11-22); in progress — see the checkboxes.** This is the second half of
`docs/THYMIO_PANEL_I18N_PLAN.md`: that plan built `core/ui_names.py` and used it for Thymio; this one
uses it for everything else in the Standard events panel.

## What a user sees today

The Standard events panel, its Add Event / Add Action menus and the action configure dialog show the
names from `events/action_types.py` / `events/event_types.py` (plus actions added by plugins and
extensions) through `self.tr(name)`. That only works when a `.ts` catalogue happens to hold the exact
text in the displaying class's context. Measured in the running app (2026-11-22): French translates
**49 of 186** action names and **7 of 73** event names; German **49** and **0**. Everything else is
English in every language.

Measured 2026-11-22, with every extension forced on (the micro:bit's 16 actions / 24 events, Thymio's
14 events and the 6 network events already have their own tables and are left out):

| Kind | Count | Words (English) |
|---|---|---|
| Action names + descriptions | 170 + 170 | |
| Parameter labels | 246 | 432 |
| Parameter descriptions | 345 | |
| Choice values shown in drop-downs | ~60 words (directions, `solid`/`any`, `host`/`client`, Block World materials…) of 107 values; operators, digits and `x`/`y` stay | |
| Core event names + descriptions | 23 + 23 | 231 |
| Categories (16 action, 7 event) | 23 | |
| **Total** | **~1,050 strings** | **~6,100** |

## What already exists — most of it

**The wiki's action reference already translates most of this, in 8 languages.**
`tools/action_ref_i18n.py` (used by `tools/gen_action_reference.py` to build
`wiki/Full-Action-Reference*`) holds, for fr / de / es / it / pt / ru / sl / uk:

- action name + description for **163 of the 170** actions (the 7 `*_files` multiplayer actions are
  missing; de and the others miss 23 in all),
- **326 of the 345** parameter descriptions,
- all categories (action and event),
- event *descriptions* for the core events (not their names).

It agrees with the existing `.ts` names: of 42 French actions named in both, 38 are identical; the 4
differences are listed under D1. **Not covered anywhere:** parameter labels (the wiki shows the
parameter's key, not its label), event names, choice values, and pl / ja / zh entirely.

## What depends on the names

- **Saved projects** store action/event *keys* and parameter *values*, never display names — except
  choice parameters: `ActionConfigDialog` (`events/action_editor.py`, lines 170/214) fills choice
  combos with `addItems(param.choices)` and restores with `setCurrentText`, so the shown text IS the
  stored value (`"right"`, `"solid"`). Same situation Thymio's U0 found; the fix is the same (show the
  translation, keep the value as item data). `ConditionalActionEditor` already does this
  (`_add_canonical_items`).
- **Documents that name actions.** Tutorials and handouts mostly use the *Blockly* block names (French
  Blockly is translated: « Quand créé », « Rebondir »), which are a separate vocabulary and do not
  change. But some non-English pages name actions in English (4 French wiki tutorial pages:
  `Tutorial-Maze_fr`, `Tutorial-Breakout_fr`, `Getting-Started-Breakout_fr`, `Tutorial-Platformer_fr`),
  and once the panel is translated those contradict the screen. To measure in U0 for every language.
- **The multiplayer actions are authored French-first** (`extensions/multiplayer_lan/actions.py`: their
  `display_name` IS French), so an English IDE shows French today (already in `TODO.md`). See D2.
- **The wiki action reference** is generated from the same names; if the panel and the wiki use two
  tables they will drift. See D1.

## Decisions for the owner

- **D1 — One vocabulary, one table.** *Recommended:* move the translations into the app
  (`config/ui_names/<lang>.py`, `{kind: {english: text}}`, registered with `register_ui_translations`
  at startup), **seeded mechanically from `tools/action_ref_i18n.py`**, and switch the wiki generator to
  read the new tables (proof: the regenerated wiki is byte-identical), then delete the duplicates from
  `action_ref_i18n.py`. The panel and the wiki then cannot disagree. The 4 French conflicts between
  the `.ts` and the wiki: *Set Volume* (.ts « Régler le volume », wiki « Définir le volume »), *Stop
  Sound* (« Arrêter un son » / « Arrêter le son »), *Set Network Mode (v1)* (.ts French, wiki
  English), *Enable Raycast View* (« Activer la vue 2.5 D » / « Activer la vue Raycast »).
  *Recommended:* the wiki's wording, except the two where the `.ts` is better (*Set Network Mode*,
  which the wiki leaves English, and « Activer la vue 2.5 D », the name the samples use).
  *Alternative:* the app reads `tools/action_ref_i18n.py` directly — `tools/` is not shipped in the
  packaged IDE, so no.
- **D2 — The French-first multiplayer actions.** *Recommended:* give them English `display_name`s in
  code (from the wiki's existing `EN_OVERRIDES`) and put the French in the French table, so an English
  IDE shows English. Saved projects store keys, so nothing breaks; the generator's `EN_OVERRIDES`
  then disappears.
- **D3 — Which choice values are translated.** *Recommended:* words only (directions, `solid`/`any`,
  `self`/`other`/`global`, `host`/`client`, shapes, micro:bit gestures and sensors, Block World
  materials); operators, digits and axis letters stay. Always shown translated, saved as the English
  value.
- **D4 — Languages.** *Recommended:* all ten, like the rest of the interface. The 8 wiki languages
  only need their gaps filled; **pl, ja and zh start from nothing** (about 1,050 strings each).
- **D5 — Documents that name actions in English.** *Recommended:* fix them in the same release (U8),
  so a French reader never sees an English action name that the French IDE does not show.
- **D6 — The `.ts` entries for these names.** *Recommended:* keep `tr()` as a fallback after the table
  for now (the 49 that work keep working), and remove the then-unused `.ts` entries in U9 once the
  tables cover everything.

## Units (one commit each, assuming the recommendations)

- [x] **U0 — Audit.** Confirm the choice-storage finding for every choice parameter (open each in the
  dialog, save, compare); list every display site (known: `editors/object_editor/events/_render.py`,
  `_event_crud.py`, `_context_menu.py`, `events/action_editor.py` (title, description, parameter labels,
  choices, the nested action tree, the Add Action menu), `events/conditional_editor.py` (menus),
  the keyboard/mouse sub-event names in `_render.py` and `events/mouse_events_complete.py`); count, per
  language, the documents that name an action or event in English (wiki, `Tutorials/<lang>`,
  `docs/handouts`, `docs/junior`).
  *Done 2026-11-22:*
  - **Choices:** confirmed in code. `ActionConfigDialog.get_parameter_values` saves
    `widget.currentText()` for every combo (`events/action_editor.py` ~line 830), including the
    *editable* object combos that put `any` / `solid` before the project's object names (lines 132–182,
    where a typed object name must still be saved as typed). `multi_choice` already shows
    `self.tr(choice)` and saves the choice. So U3: item data for the fixed choices, and for an editable
    combo save the data only when the shown text is still that item's text.
  - **Display sites:** as listed above; all go through `self.tr(...)` / `panel.tr(...)` today, so one
    helper replaces each call. `create_action_dialog` routes `if_condition` to
    `ConditionalActionEditor` (its condition combos already store canonical values) and everything
    else to `ActionConfigDialog`.
  - **Documents:** far more than the 4 pages seen while planning. Two-word-or-longer English action and
    event names, outside the generated action reference: **4,027 mentions in 199 wiki pages**, **322 in
    114 in-app tutorial pages** (`Tutorials/<lang>`, shipped in the IDE) and **36 in 10 handouts**,
    spread evenly over the 8 languages (464–618 each; most frequent: *Execute Code*, *Set Horizontal
    Speed*, *Draw Text*, *Set Variable*, *Show Message*). Most are mechanical (`**Set Horizontal Speed**`
    → the table's name), like the Thymio sheets' conversion script, but U8 is now the largest unit:
    split it by document set (in-app tutorials first, then handouts, then the wiki), one language per
    commit.
  - **Design consequence:** actions and events are keyed by KEY in the tables (`core.action` /
    `set_hspeed`), not English name: *Stop Sound* is both `stop_sound` and `microbit_stop_sound`, with
    different French names. Kinds are prefixed `core.` so they never mix with an extension's
    English-keyed table.
- [x] **U1 — Tables, seeded.** `config/ui_names/` with one module per language, generated once from
  `tools/action_ref_i18n.py` (actions, descriptions, parameter descriptions, categories, event
  descriptions) plus the French `.ts` names chosen in D1; registered at startup. Test: every seeded
  entry equals its wiki source; French accents; no French text in another language's table.
  *Done 2026-11-22:* `config/ui_names/{fr,de,es,it,pt,ru,sl,uk}.py` (`NAMES = {kind: {key: text}}`),
  generated once from `tools/action_ref_i18n.py` and proven equal to it entry by entry (0 mismatches;
  micro:bit actions left to the extension's own table). Kinds `core.action`, `core.action_description`
  (by key), `core.param_description`, `core.category` (by English), `core.event_description` (by key).
  `core.ui_names` loads them on first lookup -- no registration step. The D1 French choices are applied
  in U2, after the byte-identity proof. Plain imports, not importlib, so a frozen IDE bundles them.
  Guard: `tests/test_core_ui_names.py`.
- [x] **U2 — The wiki reads them.** `tools/gen_action_reference.py` takes names, descriptions, notes and
  categories from `config/ui_names`; regenerate all nine languages; **byte-identical** wiki output is
  the proof; delete the now-duplicated tables from `action_ref_i18n.py` (its page chrome stays).
  *Done 2026-11-22:* `tools/action_ref_i18n.py` no longer holds names (4,434 → ~560 lines): its
  `ACTIONS_<LANG>` / `NOTES_` / `CATEGORIES_` / `EVENTS_` are views built from `config/ui_names`, so both
  wiki generators (`gen_action_reference.py`, `gen_preset_docs.py`) follow automatically. Proof: both
  regenerated all nine languages **byte-identical** to the committed wiki, with identical "untranslated"
  reports. Then D1: French *Set Network Mode (v1)* → « Définir le mode réseau (v1) » (one wiki page
  changes). **Correction to D1:** « Activer la vue 2.5 D » was *not* applied — the French Blockly block
  and the raycast handouts (11, 12, 14) all say « Activer la vue Raycast », so the wiki's wording stays
  and the `.ts` one goes. Found for U4: `config/blockly_generated_block_i18n.py` already holds 119
  French parameter labels (`PARAM_LABEL_TRANSLATIONS`) for the generated Blockly blocks -- reuse them.
- [ ] **U3 — Show it.** One helper (`ui_name`, then `tr()`, then English — the `_name` pattern of
  `gm80_action_dialog.py`) at every U0 display site; choice combos show the translation with the
  English value as item data, select by data, save the data. Real-widget tests in French and Japanese
  (the panel tree, both menus, the configure dialog); **every choice parameter of every action opened
  in French and saved returns the same value**; a sample project opened and saved in French is
  byte-identical.
- [ ] **U4 — Fill the 8 wiki languages' gaps.** Parameter labels (246), event names (23), choice words
  (~60), the 7–23 missing actions and their parameter descriptions; one commit per language
  (fr, de, es, it, pt, ru, sl, uk). Guard test: every kind complete in every language.
- [ ] **U5 — Polish.** The whole set (~1,050 strings).
- [ ] **U6 — Japanese.** Same; check widths in the configure dialog (the junior-theme clipping test).
- [ ] **U7 — Chinese.** Same.
- [ ] **U8 — D2 and D5.** English names for the multiplayer actions; the documents from U0 renamed to
  the names their language's IDE now shows (wiki pages, tutorials, handouts), PDFs/ODTs regenerated
  where they exist; a guard test like `test_thymio_fiches_docs.py` for any document that names actions.
- [ ] **U9 — Close.** Retire the unused `.ts` entries (D6), wiki regenerated and, with the owner's
  approval, published; QA checklist §17 item; `TODO.md`; `CLAUDE.md` note.

## Risks

- **Choice values** (U3) — the one way this can break saved projects. Covered by the open-and-save
  test over every choice parameter, run before anything else in U3 lands.
- **Two vocabularies** — avoided by D1 (one table for the panel and the wiki). The Blockly block names
  remain a separate vocabulary on purpose (blocks are phrased differently: « Quand créé »).
- **Size.** About 6,100 English words. From the 2026-07-20 measurement (one language ≈ 40% of a
  session for 13,500 words), each full language (pl, ja, zh) is roughly a fifth of a session, the gap
  fills smaller — but with tests and verification, plan **one session for U0–U3** and **one for
  U4–U7**, then U8–U9 (U8's size depends on U0's document count).
- **No native-speaker review**, as for every translation added this month: the QA item says so.
