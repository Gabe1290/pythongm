# Blockly toolbox gating: presets that actually filter + per-project extension activation

Written 2026-09-30. Status: **CLOSED (2026-10-01) — all units (U0-U6) done.**
Resume state = the checkboxes in the Units section, all checked.

## The bug

The beginner preset lists 40 blocks in 10 categories
(`config/blockly_config.py` `get_beginner`), but a beginner sees roughly
**120 blocks in ~18 categories**.

Cause: `editors/object_editor/blockly/blockly_workspace.html`
`reconfigureToolbox` builds the toolbox in two passes.

1. Hardcoded categories (`Events`, `Movement`, `Control`, …) are filtered by
   the preset, and auto-generated blocks whose category *name matches* one
   of them are merged in and filtered too.
2. Every other auto-generated category (`registerCustomBlocks` makes one
   block per `ACTION_TYPES` action that has no hand-written block) is
   appended **with no preset check at all** (the "Append dynamically
   registered custom categories" loop).

Measured 2026-09-30 (168 actions after `load_all_plugins()`), categories that
bypass every preset:

| Category | Blocks | Owner |
|---|---|---|
| Network | 22 | extensions `multiplayer_lan` (15) + `multiplayer_files` (7) |
| Game | 20 | core (`draw_line`, `draw_sprite`, `restart_game`, `set_window_caption`, `set_draw_color`…) |
| 3D View | 18 | extensions `block_world` (14) + `raycast_2_5d` (4) |
| Particles | 8 | core |
| Audio | 6 | plugin + core — **deliberately** always visible (CLAUDE.md) |
| Score | 5 | core — named "Score", the hardcoded category is "Score/Lives/Health", so the merge misses |
| Views | 2 | core |
| Grid | 1 | core |

The action-list editor has the **same bug by a different route**:
`events/action_types.py` `get_actions_by_category(config)` keeps any action
with no `ACTION_TO_BLOCKLY_MAP` entry "for backward compatibility", so the
right-click "add action" menu (`editors/object_editor/events/_context_menu.py`)
and `events/action_editor.py` / `events/conditional_editor.py` show the same
extra actions. `tools/gen_preset_docs.py` documents presets through that same
function, so the published `wiki/Beginner-Preset*.md` pages list them too.

Why presets can't simply be applied to these blocks today: presets only know
`BLOCK_REGISTRY` (86 hand-written blocks). The 82 auto-generated actions are
in no preset, so filtering them naively would also empty them out of `full`,
`intermediate` and every custom config.

## Decisions (settled with the user 2026-09-30)

1. **Extension activation is per project.** An extension's actions/blocks
   show only in a project that has it switched on, or that already uses its
   actions. A new beginner project therefore shows no 3D View / Network, with
   no teacher setup. The global Preferences → Extensions switch stays as the
   outer gate (disabled globally = never loaded, as today).
2. **Active overrides the preset.** When a project has an extension on, its
   categories show in every preset, beginner included.
3. Audio stays always visible (existing deliberate decision, not revisited).
4. Thymio keeps its own existing per-project gate ("project has
   playgrounds", `PLUGIN_TOOLBOX_VISIBILITY_FILTERS`, Stage G5b.1). Folding it
   into the generic activation is a possible follow-up, not part of this plan.

## Target rule — ONE Python resolver, both editors use it

New pure module `config/toolbox_visibility.py` (no Qt):

```
active_extensions(project_data) -> set[str]
    = globally enabled extensions ∩ (
          project_data.settings.active_extensions
        ∪ required_extensions_for_project(project_data)   # already uses them
      )

visible_actions(config, project_data) -> set[str]      # action names
    action shown iff
      - owned by an extension  → that extension ∈ active_extensions
                                 (preset ignored, decision 2)
      - else Audio category    → always
      - else                   → config enables it (its hand-written block,
                                 or the action name itself for auto blocks)
```

- `BlocklyWidget.apply_configuration` sends the resolved set (block types for
  hand-written blocks, `custom_<action>`/base names for generated ones) —
  replacing the ad-hoc merge rules scattered in the JS.
- `get_actions_by_category` takes the same resolver, deleting the
  "include if unmapped" bypass.
- Ownership comes from `plugin_loader.extension_for_action` (already exists).
- Deriving activation from `required_extensions_for_project` means **no
  migration**: every existing project and sample that uses raycast/network
  actions stays "active" for those extensions automatically.

## Units — one commit + push each, full-suite CI green before the next

- [x] **U0 — this plan.** Committed + pushed (9ec05067, d8b8f9b5).
- [x] **U1 — resolver + tests, not wired.** `config/toolbox_visibility.py`
  with `active_extensions` / `visible_actions`. Tests pin: extension action
  hidden when inactive in every preset; shown when active in beginner;
  activation via `settings.active_extensions`; activation via usage; a
  globally disabled extension never active; Audio always; hand-written block
  gating unchanged. Pure — no Qt, no JS.
  - Implementation detail worth recording: `visible_actions` resolves each
    action's block-type name via `ACTION_TO_BLOCKLY_MAP.get(name, name)`
    once and checks membership in `config.enabled_blocks` — this single
    lookup covers *both* the hand-written-block case (map has a real entry,
    e.g. `move_set_hspeed` → `set_hspeed`) and the not-yet-added
    auto-generated-action case (no map entry, falls back to the action name
    itself) with no separate OR-branch needed, since the map genuinely has
    no entry for any of the 82 currently-ungated actions.
  - Thymio needed no special-casing: its 28 actions were already confirmed
    (Stage G3 of `docs/THYMIO_EXTENSION_PLAN.md`) to never register into
    `ACTION_TYPES` at all (it uses the older GM80-dialog `ActionDefinition`
    schema, not `PLUGIN_ACTIONS`), so `visible_actions`'s iteration over
    `ACTION_TYPES.items()` never encounters a `thymio_*` name in the first
    place — decision 4 ("Thymio keeps its own gate") holds automatically,
    not by an explicit exclusion.
  - `tests/test_toolbox_visibility.py` (7 tests), using `raycast_2_5d`'s
    4 real actions as the extension-gating fixture (closest to a worked
    example already in the repo) rather than a dummy module, since the
    resolver's only real dependency (`plugin_loader.extension_for_action`
    reading `extension.json` manifests) needs real files on disk anyway.
  - Full suite: a-g 2494 passed, h-p 1671 passed, q-z split q-s/t-z (the
    documented pre-existing IDE-window access-violation landmine hit again
    partway through the full q-z run, unrelated to this change — pure-Python
    module, no Qt) 623 + 763 passed, 0 real failures throughout.
- [x] **U2 — presets learn about generated actions.** `config/blockly_config.py`'s
  new `GENERATED_ACTION_NAMES` frozenset (81 action names, computed by
  extracting the REAL hardcoded `<block type="...">` set out of
  `blockly_workspace.html`'s `categories` object and taking every
  non-extension, non-Audio `ACTION_TYPES` action whose resolved block type
  isn't in it — not derived from `BLOCK_REGISTRY`, which turned out to
  diverge from the real hardcoded set for categories like Particles that
  have config-dialog metadata but no actual hand-written block).
  - `full` and `intermediate`/`platformer`/`grid_rpg`/`sokoban`/`testing`/
    `code_editor`/`blockly_editor`: all 81, via one
    `config.enabled_blocks.update(GENERATED_ACTION_NAMES)` line each —
    behaviour-preserving as planned, including for `code_editor` (whose own
    docstring claims a narrower Python-parser-matched scope; the pre-fix
    bug showed everything there too, so trimming it is still a separate,
    later decision, not done here).
  - `beginner`: **the original 5-action audit (3 in, 2 out) was wrong —
    found and corrected before landing, not after.** A full per-sample
    audit (every beginner-edition sample's real `project.json`, not just
    what the plan doc listed) found **17 more** generated actions actually
    in use, several more widely used than the ones already decided on
    (`start_moving_direction` in 6 samples; `comment`/`if_collision` in 5
    each; `test_instance_count`/`sleep`/`move_to_contact`/`execute_code` in
    3 each; 10 more in 1-2). Presented the full list with per-action usage
    counts; **decided with the user, 2026-10-01: include all 17** (matches
    the plan's own stated principle — "only what tutorials/samples need" —
    rather than its incomplete original audit). Final beginner addition is
    20 actions total; `set_draw_font`/`draw_sprite` remain the only two
    deliberately excluded (sky_strike_1/maze_3/4 only, narrow usage, not
    revisited).
  - Saved custom configs (`load_config`): new `BlocklyConfig.config_version`
    field (default 2; `from_dict` reads a missing key as `1`, so every file
    saved before this unit is detected). `load_config()` now runs a
    version-gated migration — independent of the existing `preset_name ==
    "full"` one, which only ever covered `BLOCK_REGISTRY`-known blocks for
    the full preset — adding `GENERATED_ACTION_NAMES` to `enabled_blocks`
    and bumping to 2, for *any* saved preset_name, exactly once (verified:
    second `load_config()` call on the same file makes no further write).
  - **Drift guard, not just a one-time computation**:
    `tests/test_toolbox_visibility.py::test_generated_action_names_matches_the_real_js_hardcoded_set`
    re-extracts the JS hardcoded set the same way and asserts it against a
    freshly-recomputed "expected generated" set — if `blockly_workspace.html`
    ever gains or loses a hardcoded block without `GENERATED_ACTION_NAMES`
    being updated to match, this fails loudly instead of silently
    reintroducing a version of the exact bug this plan fixes.
  - `tests/test_blockly_preset_generated_actions.py` (5 tests): every
    "everything" preset has zero missing generated actions; beginner has
    exactly its 20 decided additions and not the 2 exclusions; every
    beginner-edition sample's actually-used generated actions are either
    visible or on the exclusion list (this is the test that caught the
    17-action undercount, by actually walking all 14 sample project.json
    files rather than trusting the plan doc's own list); the saved-config
    migration end to end (version bump, idempotent on reload, originally-
    enabled blocks preserved); a fresh config/preset is already
    `config_version == 2`.
  - Full suite: a-g 2499 passed, h-p 1671 passed, q-s 623 passed, t 626
    passed, u-z 138 passed (the t-z combined run hit the documented
    pre-existing IDE-window access-violation landmine partway through,
    split further — same non-deterministic-split-point behavior
    CLAUDE.md already documents, unrelated to this change), 0 real
    failures.
- [x] **U3 — Blockly toolbox uses the resolver.**
  - **Python** (`editors/object_editor/blockly_widget.py`,
    `apply_configuration`): resolves `visible_actions(config, project_data)`
    (`project_data` from a new `_find_project_data()` parent-walk, mirroring
    `_collect_project_assets`'s existing pattern but preferring the live
    in-memory dict), maps each visible action to its block type via
    `ACTION_TO_BLOCKLY_MAP`, and **replaces** (not unions) every
    action-governed entry in `config.enabled_blocks` with that answer —
    `action_block_types = {ACTION_TO_BLOCKLY_MAP.get(n, n) for n in
    ACTION_TYPES}` splits the preset's raw `enabled_blocks` into "non-action
    entries" (events, read-only value blocks, Thymio's own `thymio_*`
    preset entries — none of which `visible_actions` has an opinion on,
    since Thymio was never in `ACTION_TYPES`) kept as-is, and
    "action-governed entries" fully replaced. A plain union was considered
    and rejected: it can only ever ADD a block, never remove one
    `visible_actions` says should be hidden, which would have been a latent
    bug the moment any preset's `enabled_blocks` ever contained an inactive
    extension's action name. The existing Thymio `ToolboxVisibilityFilter`
    (Stage G5b.1) still runs last, unchanged.
  - **JS** (`blockly_workspace.html`'s `generateToolboxXml`): the "append
    dynamically registered custom categories (only those not merged)" loop
    — the actual bug this whole plan fixes — now filters each block exactly
    like the merged-category path already did
    (`enabledBlocks.has(blockType) || enabledBlocks.has(baseName)`), instead
    of pushing every block through with no check at all.
  - **"Block definitions registered regardless of toolbox"** verified
    structurally rather than by loading a real workspace (no JS engine in
    CI, consistent with this repo's established limit for this file):
    `_register_custom_blocks` sends `ACTION_TYPES` to `registerCustomBlocks`
    completely unfiltered — no preset, no `project_data`, called once at
    page setup, decoupled from `apply_configuration`'s per-reconfigure
    payload — and `registerCustomBlocks` itself never references
    `enabledBlocks`/`enabledCategories` (those names only exist inside
    `generateToolboxXml`). A saved workspace referencing a now-hidden block
    therefore still deserializes: `Blockly.Blocks[blockType]` exists
    independent of whether the toolbox palette currently shows it.
  - Tests: `tests/test_blockly_toolbox_js_filter.py` (4, the structural/regex
    tier for the JS fix — brace-balance on `generateToolboxXml`, the old
    unfiltered-push pattern is gone, the new per-block filter is present,
    the already-correct merged path untouched); `tests/test_toolbox_visibility.py`
    gained the Python payload tests (beginner with/without an active
    raycast extension; replace-not-union proven with a planted inactive
    extension action; the block-definitions-unconditional structural proof)
    — 11 tests in that file now. Found and fixed one stale assertion in
    `tests/test_thymio_extension.py`'s own G5b.1 test: it expected
    `apply_configuration`'s output to be a passthrough of the input
    `enabled_blocks` minus Thymio, but post-U3 it's the fully resolved set,
    so Audio actions (always-visible, independent of the config) now
    correctly appear too — the property that test actually cared about
    (Thymio stays excluded) still holds; updated the assertion rather than
    weaken it.
  - Full suite: a-g 2503 passed, h-p 1671 passed, q-s 623 passed, t 629
    passed, u-z 138 passed, 0 real failures.
- [x] **U4 — action-list editor uses the resolver.**
  `events/action_types.py`'s `get_actions_by_category(blockly_config=None,
  project_data=None)` now delegates entirely to `visible_actions` (lazy
  import, avoiding a circular import with `config/toolbox_visibility.py`
  importing this module at its own top level). `visible_actions` gained a
  `config=None` mode -- "no preset restriction on core actions" -- since
  `action_editor.py`/`conditional_editor.py` never passed a config at all;
  they keep that exact behaviour for core actions while gaining correct
  extension-activation gating, which is independent of a preset. Callers
  (`_context_menu.py`'s 4 call sites, `action_editor.py`,
  `conditional_editor.py`) each pass `project_data` via a new
  `_find_project_data()` helper -- same name, same parent-walk body, added
  to all three classes plus `ObjectEventsPanel` (`_panel.py`), matching
  `BlocklyWidget._find_project_data` from U3.
  - **Found and fixed a second, sibling bug in the same unit (decided with
    the user after regenerating the wiki docs surfaced it):**
    `events/event_types.py`'s `get_available_events` had the *identical*
    "no mapping → include anyway, for backward compatibility" bug, for
    events instead of actions -- all 12 multiplayer network events
    (`connection_lost`, `network_message`, `player_joined`, ...) showed in
    every preset's Add-Event menu unconditionally, regardless of preset or
    extension activation. Not in the plan's original U4 wording, but
    leaving it would have meant the Add-Event and Add-Action menus
    disagreed with each other (actions correctly gated, events not) right
    after fixing exactly that inconsistency for actions. Fixed the same
    way: new `config/toolbox_visibility.visible_events` (no Audio-style
    always-visible exception -- events have no equivalent), a new
    `plugin_loader.extension_for_event` (mirrors `extension_for_action`;
    `list_available_extensions()` now also reads each manifest's
    `provides_events`, which `multiplayer_lan`/`multiplayer_files` already
    declared but nothing read), `get_available_events` rewritten to
    delegate to it, and `_event_crud.py`'s one real caller
    (`show_add_event_menu`) updated to pass `project_data`. Extension
    activation reuses the existing action-based `active_extensions()`
    signal as-is -- not extended to detect event-only usage, since a
    project using an extension's events without ever calling one of its
    actions isn't a real scenario worth the complexity.
  - **Regenerated `tools/gen_preset_docs.py` output for all 9 shipped
    languages** (18 files: `Beginner-Preset[_<lang>].md` /
    `Intermediate-Preset[_<lang>].md`). The diff mixes two causes: the
    actions fix (beginner's doc actually shrank overall -- 83→54 action
    types -- because the old doc showed every unmapped action
    unconditionally, not just the ones beginner's own preset enables, so
    several actions nobody had actually decided beginner should show, like
    `jump_to_random`/`create_random_instance`, dropped out; intermediate's
    action count rose 94→118 as its own real generated-action set, U2's
    `GENERATED_ACTION_NAMES.update()`, became visible for the first time)
    and the events fix (intermediate's event count, inflated to 33 by the
    sibling bug on an unregenerated first pass, correctly returned to 21 --
    matching what the previously-committed doc already showed, confirming
    that doc predated the multiplayer events existing at all and was never
    actually wrong until a regen would have exposed the bug). French
    accents spot-checked intact. Not published to the live wiki (needs
    explicit approval, as always) -- these are local `wiki/*.md` commits
    only.
  - 7 new tests in `tests/test_toolbox_visibility.py` (now 18 total in
    that file across U1/U3/U4): `get_actions_by_category`/
    `get_available_events` both correctly gate extensions with no config at
    all and still gate core actions/events by a real preset;
    `extension_for_event` reads `provides_events` from the manifest; all
    three dialog callers' wiring confirmed structurally.
  - Full suite: a-g 2503 passed, h-p 1671 passed, q-s 623 passed, t 636
    passed, u-z 138 passed, 0 real failures.
- [x] **U5a — project activation setting + UI logic.** Done; U5b
  (translations, below) is its own follow-up commit, same session.
  `project_data["settings"]["active_extensions"]` (list of folder names,
  default empty; saved through `ProjectSettingsDialog.accept_settings`'s
  existing `self.project_data["settings"].update({...})` call, so it rides
  the normal save path with zero new persistence wiring). `ProjectSettingsDialog`
  (`dialogs/project_dialogs.py`) gains an "Extensions" section, built
  dynamically in a new `_populate_extensions()` (the checkbox *set* is
  data-driven from `list_available_extensions()`, unlike every other field
  in this dialog): one checkbox per globally-enabled extension whose
  actions actually appear in `ACTION_TYPES` (`provided & set(ACTION_TYPES)`
  -- Thymio is correctly excluded this way with no special-casing by name,
  since its actions were never in `ACTION_TYPES` at all, confirmed
  `THYMIO_EXTENSION_PLAN.md` Stage G3; decision 4, its own gate stays
  separate). An extension the project already uses
  (`collect_project_action_names(project_data) & provides_actions`) is
  shown checked and **disabled** with a `"used by {0} action(s)"` note —
  turning it off would hide blocks the project still depends on; `accept_settings`
  only writes the *manually* checked (enabled-checkbox) folders into
  `active_extensions`, since a disabled/used one is already detected by
  usage (`config.toolbox_visibility.active_extensions` combines both sets
  identically). Toggling refreshes live: `core/ide/_project_actions.py`'s
  `project_settings()` now calls the existing `self.refresh_event_panels_config()`
  after a successful accept — no new refresh mechanism needed, since
  `apply_config`/`apply_configuration` already re-resolve `visible_actions`/
  `visible_events` from the live `current_project_data` on every call (U3/U4).
  8 new tests in `tests/test_project_settings_extensions.py`: Thymio
  excluded; used-extension checked+disabled with the right count;
  unused-extension unchecked+enabled; a globally-disabled extension isn't
  listed at all; `accept_settings` persists only the manual selections;
  reopening restores a previous manual activation; the saved settings dict
  round-trips through the real resolver; `project_settings()`'s refresh
  call confirmed structurally. Full suite: a-g 2503 passed, h-p 1679
  passed, q-s 623 passed, t 636 passed, u-z 138 passed, 0 real failures.
- [x] **U5b — translations.** New `ProjectSettingsDialog` UI strings
  ("Extensions" group title, `"used by {0} action(s)"` note) added to all
  10 shipped languages' `.ts` files, routed to the correct split
  (de/it/ru/sl/uk → `pygm2_<lang>_dialogs.ts`, confirmed by checking where
  `ProjectSettingsDialog`'s existing context block already lived) or
  monolithic (es/fr/pt/ja/zh → `pygm2_<lang>.ts`) file, each compiled
  clean via `scripts/compile_translations.py` (35 files). "Extensions"
  reuses each language's already-correct translation from
  `PreferencesDialog`'s own context (extracted via the same `<source>` /
  `<translation>` regex `tests/test_extension_ui_translations.py` uses —
  Qt resolves by *context*, so it needs its own entry under
  `ProjectSettingsDialog` too, not just an identical source string);
  `"used by {0} action(s)"` is an original translation per language,
  matching each language's existing noun for "action" already established
  elsewhere in that language's catalog (verified against each language's
  own `"Edit Action"` translation first, not assumed) — de "Aktion", es
  "acción", fr "action", it "azione", pt "ação", ru "действие", sl
  "dejanje", uk "дія", ja "アクション" (katakana), zh "操作" (matching "Add/Edit/
  Remove Action", not the less-common "动作"). Pluralization simplified to
  the conventional parenthetical/generic-plural forms software
  localization normally uses for a template count, rather than attempting
  exact grammatical number agreement (most pointed in Slavic/Slovenian,
  which has 4 grammatical numbers) — French's "Extensions" stays the
  established cognate exception.
  - `tests/test_project_settings_extensions_translations.py` (3 tests,
    mirrors `test_extension_ui_translations.py`'s structure exactly):
    every source present in every language; every translation non-empty
    and actually translated (not a stray English copy); a live
    `QTranslator` resolves both strings in all 10 languages. Also re-ran
    the existing `test_i18n_unfinished_{de,es,fr,it,ru,sl,uk}.py` guards
    and `test_extension_ui_translations.py` itself — all still green,
    confirming the new entries didn't disturb anything already there.
  - **Offscreen `grab()` screenshot attempted, inconclusive on this
    box — a genuine environment limit, not a code issue.** Built a real
    `ProjectSettingsDialog` (with one extension pre-used, one manually
    checked) under `en`/`fr` via `get_language_manager().set_language()`
    and grabbed it; `QFontDatabase.families()` returns **zero** font
    families under this Windows box's offscreen Qt platform (confirmed
    directly, not inferred from the blank render), so every label painted
    as a string of placeholder boxes — a known class of Qt offscreen-
    platform limitation on Windows specifically (no DirectWrite/GDI font
    backend wired to `-platform offscreen` here), unrelated to this
    change. The screenshot's *shape* still confirmed the structural
    layout (4 group boxes; the Extensions group's 4 checkboxes showing
    the expected 2-unchecked / 1-manually-checked / 1-disabled-and-checked
    pattern), matching this plan's own documented fallback ("if not, list
    it as needs-human-eyes on a real display") — logged as still needing
    a real display, same standing caveat this whole arc has carried since
    raycast_3.
  - Full suite: a-g 2503 passed, h-p 1682 passed, q-s 623 passed, t 636
    passed, u-z 138 passed, 0 real failures.
- [x] **U6 — docs + eyeball.** Done at 91% session usage — scoped tight
  (docs only, no further investigation) per the standing "continue as
  safe as possible" instruction once usage got called out; each piece
  verified narrowly rather than re-running the full suite, since nothing
  here touches executable code paths already covered by U1-U5's own gates.
  - `wiki/Extensions.md`/`_fr.md`: new "Which extension actions show in
    the toolbox" / "Quelles actions d'extension apparaissent dans la
    palette" section, explaining the two-layer model (global enable/disable
    vs. this plan's new per-project activation) and that an active
    extension's actions show in every preset including Beginner.
  - `wiki/Beginner-Preset.md`/`Intermediate-Preset.md` + their `_fr`
    pairs: one added sentence in each language's `scope_note` template
    (`tools/gen_preset_docs.py` — these pages are generator output, never
    hand-edited) pointing to the new Extensions section; regenerated only
    `en fr` (not all 9 languages — matches the plan's own explicit scoping,
    "other languages via the generator where generated, otherwise deferred
    like prior wiki arcs"), confirmed via `git diff --stat` that exactly
    the intended one line changed per file (4 files, 4 insertions/4
    deletions total) with no unrelated regen drift.
  - `docs/PROJECT_STATUS.md` index entry **skipped, deliberately**: that
    doc's own stated convention is "closed work gets deleted outright, not
    listed as closed-but-present" (its currently-open-work list explicitly
    says "everything else... is done and has been deleted"), and this plan
    doc isn't being deleted right now (keeping the retrospective detail —
    the `GENERATED_ACTION_NAMES` derivation, the 17-action beginner
    undercount, the font-rendering environment finding — all have real
    future value; `THYMIO_EXTENSION_PLAN.md`, this session's other active
    plan, has the same not-yet-indexed gap). Forcing an entry into a
    closed-docs model that doesn't fit would be lower-value than leaving
    it for whoever next runs a doc-cleanup pass to fold the whole
    now-closed plan in at once.
  - Offscreen `grab()` of the real Blockly toolbox **not re-attempted** —
    U5b already found and confirmed `QFontDatabase.families()` returns
    zero fonts under this box's offscreen Qt platform, a system-level
    limitation that would affect any widget identically, not something
    specific to the toolbox; re-running it would reproduce the same
    inconclusive result for no new information. Still needs a real
    display, same standing caveat as U5b and every prior raycast/i18n
    arc's own "needs human eyes" note.

## Risks

- **Hidden-but-used blocks.** Opening a sample whose actions aren't in the
  preset: blocks load and run, but can't be added again from the toolbox.
  Acceptable (it's what already happens for the hand-written Control blocks
  today); U2's test makes the list explicit instead of accidental.
- **Custom configs lose blocks** if U2's migration is wrong — covered by a
  test loading a pre-change saved config.
- **Two gates for Thymio** (playgrounds + nothing else) vs one generic gate
  for the rest — acceptable; noted as follow-up.
- `test_edition_sample_filter` and the tutorial i18n test force editions;
  re-run them after U2/U4.
