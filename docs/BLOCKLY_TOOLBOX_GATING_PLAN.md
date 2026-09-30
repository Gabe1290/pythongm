# Blockly toolbox gating: presets that actually filter + per-project extension activation

Written 2026-09-30. Status: **plan only — no unit started.**
Resume state = the checkboxes in the Units section.

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

- [ ] **U0 — this plan.** Commit + push.
- [ ] **U1 — resolver + tests, not wired.** `config/toolbox_visibility.py`
  with `active_extensions` / `visible_actions`. Tests pin: extension action
  hidden when inactive in every preset; shown when active in beginner;
  activation via `settings.active_extensions`; activation via usage; a
  globally disabled extension never active; Audio always; hand-written block
  gating unchanged. Pure — no Qt, no JS.
- [ ] **U2 — presets learn about generated actions.** Presets gain the core
  auto-generated action names (`Game`, `Particles`, `Score`, `Views`, `Grid`,
  plus the unmapped actions that merge into hardcoded categories).
  - `full`: all of them (keep the existing "full = everything" migration in
    `load_config`, extended to action names).
  - `intermediate` and the focused presets (`platformer`, `grid_rpg`,
    `sokoban`, `testing`, `code_editor`, `blockly_editor`): **behaviour-preserving**
    — all core generated actions they show today. Trimming those is a
    separate, later decision.
  - `beginner`: only what its tutorials and beginner-edition samples need.
    Newly hidden by the fix and used by beginner-edition samples:
    `restart_game` (maze_1/3/4, plateforme_3, treasure, sky_strike_1),
    `set_window_caption` (maze_2/3/4, plateforme_3, treasure),
    `set_draw_color` (maze_3/4), `set_draw_font` (maze_3/4),
    `draw_sprite` (sky_strike_1). **Decided (user, 2026-10-01):** add
    `restart_game`, `set_window_caption`, `set_draw_color`; leave
    `set_draw_font` and `draw_sprite` out (a sample opening with a block not
    in the toolbox still loads and runs — students just can't drag a new
    one).
  - Saved custom configs (`load_config`): a config saved before this change
    has no generated-action names; migrate it by adding all core generated
    actions (what the user saw before), marked with a config version field so
    it runs once.
  - Test: the `test_*preset*` suite + a test asserting every beginner
    tutorial / beginner-edition sample action is either enabled or on the
    explicit "loads but not in toolbox" list above.
- [ ] **U3 — Blockly toolbox uses the resolver.** `apply_configuration` sends
  the resolved set (after the existing Thymio visibility filter). JS: the
  unmerged-custom-category loop filters per block exactly like the merged
  path. Structural regex test on `blockly_workspace.html` (no JS engine in
  CI) + a Python test of the payload `apply_configuration` sends for
  beginner-with/without-raycast. Verify a workspace containing a
  now-hidden block still loads (block *definitions* are registered
  regardless of toolbox; check it in the real widget).
- [ ] **U4 — action-list editor uses the resolver.**
  `get_actions_by_category(config, project_data=None)`; callers
  (`_context_menu.py`, `action_editor.py`, `conditional_editor.py`) pass the
  open project. Regenerate `tools/gen_preset_docs.py` output; the wiki preset
  pages change (publishing to the live wiki needs explicit approval, as
  always).
- [ ] **U5 — project activation setting + UI.**
  `project_data["settings"]["active_extensions"]` (list of folder names,
  default empty; saved by the normal save path). `ProjectSettingsDialog`
  (`dialogs/project_dialogs.py`) gains an "Extensions" section: one checkbox
  per globally enabled extension. An extension the project already uses is
  shown checked and **disabled** with a note ("used by N actions") — turning
  it off would hide blocks the project still depends on. Toggling refreshes
  open Blockly editors and action menus live (no restart; unlike the global
  switch, nothing needs reloading — the actions are already registered).
  New UI strings go into **all 10 shipped languages'** `.ts` files, routed to
  the correct split/monolithic file, French with full accents (same process
  as the 2026-08-10 extension-UI strings; `tests/test_extension_ui_translations.py`
  is the pattern). Offscreen `grab()` screenshot of the dialog in fr/en.
- [ ] **U6 — docs + eyeball.** `wiki/Extensions*.md` and the preset pages:
  explain per-project activation (en + fr now; other languages via the
  generator where generated, otherwise deferred like prior wiki arcs).
  `docs/PROJECT_STATUS.md` index entry. Try an offscreen `grab()` of the
  real Blockly toolbox in beginner before/after (QtWebEngine offscreen may not
  finish loading — if not, list it as needs-human-eyes on a real display).

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
