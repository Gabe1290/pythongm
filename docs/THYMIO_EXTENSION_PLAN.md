# Thymio extension plan

Status: **planning only — nothing in this doc has been implemented.** Written
2026-09-28 to answer "make a plan to develop a Thymio extension" without
touching code. Follow the staging below when the work actually starts; keep
this doc as the resume state and delete it once closed (repo convention —
see `RAYCAST_EXTENSION_PLAN.md`'s and `MULTIPLAYER_LAN_V2_PLAN.md`'s fate in
`docs/PROJECT_STATUS.md`'s closed-docs index).

## Goal

Turn Thymio-robot support from **core code with its UI entry points commented
out** (`docs/POST_1_0_REFACTOR.md`'s `# [1.0]` markers, see
`[[thymio-hidden-for-1.0]]`-style note in CLAUDE.md) into a **real, optional
folder extension** — `extensions/thymio/` — with the same properties
`raycast_2_5d`, `multiplayer_lan`, and `block_world` already have:

- core carries **no Thymio-specific code**, only generic seams every
  extension can use;
- the feature can be disabled (`"extensions": {"thymio": false}`) or, if the
  folder is deleted outright, the rest of the IDE and every non-Thymio sample
  keeps working with zero errors;
- it ships with its own `extension.json`, `README.md`, and its own test
  suite living in `tests/` the way the others' do (no separate test root).

## Non-goals

- No behavior change to the simulator, sensors, motors, Aseba/Roberta
  import-export, or the playground editor. This is a **relocation**, proven
  behavior-preserving the same way every audit-cleanup and Stage-B raycast
  move in this repo's history was — not a redesign, not a feature add.
- Not deciding here whether Thymio comes back **visible by default** in the
  shipped 1.0/1.x product — that's a separate product call. This plan makes
  it possible to flip on; see "Open decision" at the end.
- No Kivy/HTML5 export parity work. Confirmed by grep: Thymio has **zero**
  references in `export/Kivy/` or `export/HTML5/` today. It is desktop-only
  (drives a physical robot or a screen simulation via the pygame runtime),
  and this plan keeps it that way — there is no "export the robot to a
  browser" requirement anywhere in the current feature.

## Why this is a bigger job than the last three extractions

`raycast_2_5d` needed one new hook (room renderer) and `multiplayer_lan`
needed one more (frame updates) — both landed with **zero** other core
changes. Thymio doesn't fit either precedent alone. Inventory of what
currently exists, grounded in the actual code (2026-09-28):

| Area | Files | ~LOC | Notes |
|---|---|---:|---|
| Actions (schemas) | `actions/thymio_actions.py` | 800 | already `ActionType`/`ActionParameter`-shaped |
| Handlers | `runtime/thymio_action_handlers.py` | 489 | already `register_thymio_actions(executor)`-shaped |
| Events | `events/thymio_events.py` | 323 | `THYMIO_EVENT_TYPES` — fits `PLUGIN_EVENTS` as-is |
| Simulator | `runtime/thymio_simulator.py` | 536 | pure physics/sensor logic, no Qt, minimal core coupling |
| Renderer | `runtime/thymio_renderer.py` | 460 | draws the robot **inside an ordinary top-down room**, plus on-screen button hit-testing |
| Playground design-time editor | `editors/playground_editor/{canvas,elements,properties}.py` | 697+97+312 | a second, arena-authoring editor, parallel to the room editor |
| Playground live/test window | `widgets/thymio_playground.py` | 1339 | largest single file in the whole feature |
| Playground runner | `runtime/playground_runner.py` | 483 | a second, parallel `GameRunner`-like loop, playground-only |
| Diagram widget | `widgets/thymio_diagram_widget.py` | 498 | sensor/pinout diagram shown in the config dialog |
| Config/selector dialogs | `dialogs/thymio_config_dialog.py`, `thymio_action_selector.py`, `thymio_event_selector.py` | 212+436+314 | `thymio_config_dialog.py` shares a base class with `blockly_config_dialog.py` (`dialogs/_block_config_dialog_base.py`) |
| Object-editor integration | `editors/object_editor/thymio_events_panel.py` (443) + direct wiring in `object_editor_main.py` | ~443+ | a whole second tab ("Standard" vs "Thymio") **hardwired into `ObjectEditorMain.__init__`**, not a registered panel |
| Aseba export | `export/Aseba/{aseba_exporter,playground_exporter}.py` | 658+121 | compiles authored logic to real `.aesl` for the physical robot |
| Open Roberta interop | `export/Roberta/roberta_exporter.py`, `importers/roberta_importer.py` | 458+630 | XML import/export for the Open Roberta Lab block environment |
| Blockly toolbox | `config/blockly_config.py` ("Thymio Events"/"Thymio Motors"/… dicts), `config/blockly_translations.py` | partial | **hardcoded** category dict, not derived from `PLUGIN_ACTIONS`/`PLUGIN_EVENTS` the way ordinary extension actions auto-generate blocks |
| Core engine hooks | `runtime/game_runner.py` (45 refs), `runtime/input_handler.py` (37 refs), `runtime/room.py` (15), `runtime/instance.py` (2: `is_thymio`, `thymio_simulator` attrs) | — | see gap analysis below |
| IDE chrome (hidden) | `core/ide/_menu_builder.py`, `_dialogs.py`, `_export.py`, `widgets/welcome_tab.py`, `widgets/asset_tree/asset_tree_widget.py` | — | already marked `# [1.0]`, currently just commented-out direct calls |
| Asset-type plumbing | `core/project_manager.py` (`_SAVE_MANAGED_NAMES`, `_load_playgrounds_from_files`, `_save_playgrounds_to_files`) | — | "Playgrounds" is a **hardcoded first-class asset category**, file-per-asset like rooms/objects/sprites |
| Tooling | `tools/action_ref_i18n.py`, `tools/gen_preset_docs.py`, `scripts/gen_translation_ts.py` | — | already Thymio-aware; verify they stay correct once actions live under `extensions/thymio/` (they already handle raycast/block_world/multiplayer this way) |
| Tests | ~22 `test_thymio_*` + ~12 Roberta/Aseba + some of the 16 `*playground*` files | — | migrate alongside their subject, keep filenames (grep-ability matters more than directory purity in this repo) |

Total: **~9,300 LOC** across the files above, before counting the core
call-sites. For comparison, the raycast renderer Stage B2 extraction moved
~547 lines with zero new hook types. This job is roughly an order of
magnitude larger and touches categories of integration (input handling, a
second asset type, a second design-time editor, IDE-chrome contribution)
none of the three prior extensions needed at all.

## Gap analysis: extension-contract primitives that don't exist yet

`runtime/extension_hooks.py` currently offers exactly three things (verified
against the file): `PLUGIN_ROOM_RENDERERS`, `PLUGIN_FRAME_UPDATES` (phases
`before_step`/`after_update`), `PLUGIN_ROOM_CHANGE_HOOKS`. Plus the
long-standing `PLUGIN_ACTIONS`/`PLUGIN_EVENTS` from `events/plugin_loader.py`.
Six things Thymio needs that aren't covered by any of those:

1. **Per-instance state, not per-room.** `raycast_2_5d` stores its state on
   `room.extension_state[...]`; Thymio needs it on the **instance**
   (`instance.is_thymio`, `instance.thymio_simulator` are literal attributes
   on the core `Instance` class today — `runtime/instance.py:73-74`). There
   is no `instance.extension_state` dict to redirect them into.
2. **Per-instance rendering, not whole-room rendering.** A Thymio robot is
   one sprite among ordinary sprites in a normal top-down room — the
   opposite shape from raycast's "I drew the whole room, skip your top-down
   pass." `PLUGIN_ROOM_RENDERERS`' `(room, screen) -> bool` "first claim
   wins" contract doesn't fit "draw this one instance, then let the engine
   keep drawing everything else normally."
3. **Input handling.** Keyboard-to-button mapping and mouse hit-testing for
   the robot's on-screen buttons live directly inside
   `InputHandler.handle_keyboard_press/release` and
   `handle_mouse_press/release` (`runtime/input_handler.py`, ~37 references).
   No extension has ever needed to intercept raw input before; there is no
   hook for it.
4. **A second asset type.** "Playgrounds" (the robot's arena) is saved and
   loaded as a first-class category by `core/project_manager.py` —
   `_SAVE_MANAGED_NAMES = ("rooms", "objects", "sprites", "playgrounds",
   PROJECT_FILE)`, with its own `_load_playgrounds_from_files`/
   `_save_playgrounds_to_files`, file-per-asset like rooms/objects/sprites.
   No extension has ever added a new *kind* of asset before (they've all
   reused rooms + actions); `ProjectManager`/`AssetManager` have no
   registration point for one.
5. **IDE-chrome contribution.** Menu items, the Tools submenu, the asset-tree
   "Playgrounds" category, and the Welcome-tab import entry are currently
   hidden by **commenting the direct calls out** (`# [1.0]`) in
   `core/ide/_menu_builder.py`/`_dialogs.py`/`_export.py`,
   `widgets/welcome_tab.py`, `widgets/asset_tree/asset_tree_widget.py`. An
   extension today can only contribute actions/events/renderers/frame
   updates/room-change hooks — never a menu entry, a dialog, or an
   asset-tree category. There's also the **deepest** coupling point: the
   object editor's "Standard vs Thymio" tab is a direct unconditional
   `from .thymio_events_panel import ThymioEventsPanel` inside
   `ObjectEditorMain.__init__` (`editors/object_editor/object_editor_main.py`)
   — if the extension folder were absent, this import would break the whole
   object editor, not just hide a tab. (It does already have *one* generic
   piece: `Config.get('show_thymio_tab', False)` gates visibility — that
   config-driven show/hide is reusable, only the import itself needs to
   become conditional/registered.)
6. **Blockly toolbox categories.** Ordinary extension/plugin actions
   auto-generate their Blockly blocks from `PLUGIN_ACTIONS`/`PLUGIN_EVENTS`
   (the audio-actions precedent CLAUDE.md documents: "basic audio... 
   auto-generates its Blockly blocks into an always-visible Audio
   category"). Thymio instead has a **hand-curated, preset-driven** block
   registry (`config/blockly_config.py`'s `"Thymio Events"`/`"Thymio
   Motors"`/… dicts) with its own dedicated `ThymioConfigDialog`, deliberately
   different from the generic `BlocklyConfigDialog` it shares a base class
   with. This curation is a real, intentional design (teachers pick a
   Thymio-only or mixed preset), not an oversight — but the category data
   itself is hardcoded into a core config file today and needs a
   registration point instead of a core-file edit.

## Design decisions: the new seams

Each of the six gaps gets a **generic**, non-Thymio-named primitive — same
spirit as `register_frame_update`/`room.extension_state`, so a future
extension (a second robot platform, a third editor-style feature) gets to
reuse them instead of Thymio re-growing bespoke coupling.

1. **`Instance.extension_state: Dict[str, Any] = {}`** on `runtime/instance.py`
   — the exact pattern `GameRoom.extension_state` already established.
   Thymio stores `{"simulator": ThymioSimulator(...), "is_thymio": True}`
   under `instance.extension_state["thymio"]` instead of dedicated attrs.
2. **`PLUGIN_INSTANCE_RENDERERS`** in `runtime/extension_hooks.py`:
   `(instance, screen) -> bool`, tried per-instance during the normal sprite
   draw pass (return `True` = "I drew this instance, skip the engine's own
   sprite blit for it"; `False` = draw normally). Same
   try/except-log-and-skip-on-raise contract the other hook runners use.
   This is the most load-bearing new primitive — it's the one thing that
   makes "a robot renders itself specially inside an otherwise ordinary
   room" possible without a whole-room takeover.
3. **`PLUGIN_INPUT_HANDLERS`** in `runtime/extension_hooks.py`: four optional
   callables per extension (`on_key_down`, `on_key_up`, `on_mouse_down`,
   `on_mouse_up`), each `(event_data) -> bool` — `True` means "handled,
   caller should swallow this input," mirroring
   `_handle_thymio_button_press`'s existing return-True-to-swallow
   contract almost exactly. `InputHandler` tries registered handlers before
   its own generic keyboard/mouse dispatch, the same "first claim wins,
   fall through to normal behavior" shape as room renderers.
4. **A pluggable asset-type registry** on `ProjectManager`/`AssetManager`:
   `register_asset_type(name, *, load_fn, save_fn, dir_name)` replacing the
   hardcoded `_SAVE_MANAGED_NAMES` tuple with "core's own 4 types +
   whatever's registered." This is the single largest, most novel piece of
   core-generalization in this plan — bigger than anything the three prior
   extensions needed — because it changes a save/load code path every
   project touches, not just an optional draw/input path. Needs its own
   behavior-preserving proof pass (round-trip every bundled sample's save
   before/after) independent of anything Thymio-specific.
5. **An IDE-chrome extension-point module**, `core/ide_extension_points.py`
   (new — deliberately separate from `runtime/extension_hooks.py`, which is
   "dependency-free, imports nothing from the engine" by design; IDE chrome
   needs Qt). Three registries:
   - `register_menu_contribution(menu_path, action_factory)` — an extension
     adds a QAction under an existing menu (Tools, File) without
     `_menu_builder.py` naming it.
   - `register_asset_tree_category(name, icon, ...)` — so
     `asset_tree_widget.py` doesn't hardcode "Playgrounds."
   - `register_object_editor_panel(tab_label, widget_factory, visibility_fn)`
     — `ObjectEditorMain` iterates registered panels instead of importing
     `ThymioEventsPanel` directly; `visibility_fn` replaces the existing
     `Config.get('show_thymio_tab', False)` check so that mechanism is
     preserved, just made generic.
   Loaded the same place `events/plugin_loader.py` already loads
   `PLUGIN_ACTIONS`/`PLUGIN_ROOM_RENDERERS`, so there's one load point to
   reason about, not two.
6. **`PLUGIN_BLOCK_CATEGORIES`** — an extension contributes named Blockly
   category dicts (same shape as today's hand-authored `"Thymio Events"`
   entries) that `config/blockly_config.py` merges into `BLOCK_REGISTRY` at
   load time, instead of the categories being written directly into that
   file. `ThymioConfigDialog` keeps its dedicated-dialog identity (that's a
   real UX choice, not incidental coupling) — only the *data* moves.

All six are additive to core, generic in name and shape, and — per this
repo's standing methodology — each needs its own throwaway
behavior-preserving proof (an offscreen-Qt/headless harness exercising the
seam with **no** Thymio code loaded yet) before Thymio itself starts moving
onto it. That order matters: it means Stage 0 is fully verifiable in
isolation, and a bug found there can't be blamed on "something in the
9,300-line move."

## Staged plan

One unit = one commit, full-suite gate + push after each, per this repo's
session-limit discipline (`[[session-limit-task-sizing]]`). Work top to
bottom; each stage after Stage 0 depends on the seam(s) named.

### Stage 0 — the six core seams, Thymio-free

- [x] 0.1 `Instance.extension_state`. (`tests/test_extension_seams.py`)
- [x] 0.2 `PLUGIN_INSTANCE_OVERLAYS` + call site in `GameRunner.render`.
    **Shape changed from the design section above while implementing:** the
    engine draws Thymio robots *after* `room.render()`, in screen space with
    no view offset, on top of every sprite (`game_runner.py` `render()`),
    not inside the depth-sorted per-instance blit. A "claim and skip the
    sprite" hook would therefore have changed behavior (a robot object with
    a sprite draws both today). The seam is an **overlay**:
    `(instance, screen) -> None`, no claim, run for every instance of the
    current room between `room.render()` and the `draw_gui` pass — the
    exact spot the Thymio loop occupies, so Stage B1 is a one-loop swap.
- [x] 0.3 `PLUGIN_INPUT_HANDLERS` + call sites in `InputHandler`. Shape as
    designed, with one precision from the code: keyboard hooks are
    **per instance, inside the instance loop** (`(instance, key)`), because
    the Thymio key→button mapping runs interleaved with each instance's own
    `keyboard_press`/`release` dispatch today and moving it after the loop
    would reorder events between instances; mouse hooks are once-per-click
    `(runner, button, x, y) -> bool` in raw screen space, placed directly
    after the existing `_handle_thymio_button_press` precedence check so
    Stage B2 replaces that call with the hook in place.
- [x] 0.4 Pluggable asset-type registry: `core/asset_types.py`
    (`SideFileAssetType`, `register_side_file_asset_type`,
    `side_file_type_names`, `PLUGIN_ASSET_TYPES` in the loader). Generic
    `_load/_save_registered_types_*` replaced the playground-specific
    loaders in `ProjectManager`; the delete/rename/duplicate side-file
    tuples in `AssetManager`/`asset_operations.py` derive from the registry;
    `_project_structure()` slots registered types after "rooms" so a
    project.json's asset-key order is unchanged. **Playgrounds still
    register from `core/asset_types.py` itself** until Stage C5 moves that
    one call — so core's on-disk behaviour today is byte-identical. Proof:
    scratch script loaded+saved all 27 bundled samples, a synthetic
    3-playground project (full entry, legacy string entry, side-file-only
    payload) and a fresh `create_new_project`, hashing every file with the
    `modified` timestamp normalized — 969/969 lines identical HEAD vs. new.
    Note: the "rooms/objects/playgrounds" *import-menu exclusion* in
    `asset_tree_widget.py` is IDE chrome, left for 0.5.
- [ ] 0.5 `core/ide_extension_points.py` — split into three units while
    implementing, each its own commit:
  - [x] 0.5a menus + toolbar: `PLUGIN_IDE_MENUS = [(menu_key, build)]` /
        `PLUGIN_IDE_TOOLBAR = [build]`, builders get the live `QMenu`/
        `QToolBar` after the built-in entries; `_menu_builder.py` now stores
        `self._extension_menus` and applies contributions at the end of
        `create_menu_bar`/`create_toolbar`. Proven by constructing the real
        `PyGameMakerIDE` offscreen with dummy builders
        (`tests/test_ide_extension_points.py`).
  - [x] 0.5b asset-tree categories: `AssetTreeCategory` +
        `PLUGIN_ASSET_TREE_CATEGORIES`. Registration enters the type in
        `ASSET_TYPE_REGISTRY` with an `open_editor` callable (dispatch and
        `_verify_asset_editor_registry` accept that alongside the core
        `editor_method` strings); `setup_categories` slots it after
        "Rooms"; `asset_tree_item`/`get_asset_icon_emoji` use its icon;
        `create_asset_with_data` uses its `new_asset_template`; the
        import-menu exclusion derives from `importable`;
        `_canonical_category` now reads the registry live rather than at
        class-definition time. Playgrounds' static entries stay until C5.
  - [x] 0.5c object-editor panels: `ObjectEditorPanel` +
        `PLUGIN_OBJECT_EDITOR_PANELS`. `ObjectEditorMain` builds one tab per
        registered spec (`_add_extension_panel`), with generic
        `set_extension_panel_visible` / `switch_to_extension_panel` /
        `_on_extension_panel_modified` (merge-back + drop of owned events)
        / `_on_extension_event_selected` / `_sync_extension_panels` from
        `load_data`. The hardcoded Thymio tab still sits alongside until
        Stage E2 swaps it onto this seam.
- [x] 0.6 `PLUGIN_BLOCK_CATEGORIES` / `PLUGIN_BLOCKLY_PRESETS` /
    `PLUGIN_BLOCK_CATEGORY_TRANSLATIONS` / `PLUGIN_BLOCK_TRANSLATIONS`:
    `register_block_categories` + `register_blockly_presets` in
    `config/blockly_config.py` (first name wins; "full"/"implemented_only"
    presets rebuilt), `register_category_translations` +
    `register_block_translations` in `config/blockly_translations.py`;
    loader `_load_block_categories` at all three sites. The Thymio
    categories, preset and translations stay inline until Stage F1.

**Stage 0 is complete.** Every seam is generic, dummy-proven, and Thymio's
code is untouched — Stage A can start on any machine from clean `main`.

Each of 0.1–0.6 ships with its own test file proving the seam works with a
synthetic/dummy registrant (not Thymio) — mirrors how `test_raycast_extension.py`
proved the room-renderer/frame-update hooks generically before Stage B moved
real code onto them.

### Stage A — pure logic (lowest risk, no new seam needed)

- [x] A1. `actions/thymio_actions.py` → `extensions/thymio/actions.py`.
    **Not as `PLUGIN_ACTIONS`** — investigation showed the Thymio schemas
    are `actions.core.ActionDefinition`s for the GM80 action *dialog*
    (a separate schema system from `events.action_types.ActionType` /
    `ACTION_TYPES`; Thymio actions were never in `ACTION_TYPES` and the
    runtime dispatches them by registered handler name). Moved verbatim,
    keeping the shape; consumers (`thymio_events_panel`,
    `thymio_action_selector`, one test) now import
    `extensions.thymio.actions`. The GM80 "Thymio" tab left
    `actions/core.py` too: new `register_action_tabs()` merge point, the
    extension registers `THYMIO_TAB` on import. `extension.json` declares
    all 28 actions in `provides_actions`, so a Thymio project saved from
    now on records `requires_extensions: ["thymio"]` (the standard
    extension dependency line; no bundled sample uses a Thymio action).
    `tests/test_thymio_extension.py` pins the move.
- [x] A2. `runtime/thymio_action_handlers.py` → `extensions/thymio/handlers.py`.
    The closure-based `register_thymio_actions(executor)` moved verbatim
    (the playground runner, which has no plugin loader, still calls it);
    a `PluginExecutor` built by *capturing* what that function registers
    gives the loader its `execute_<name>_action` attributes without a
    second copy of any handler. `GameRunner.__init__` dropped its explicit
    registration — `load_all_plugins(self.action_executor)` on the next
    line now supplies the same 28 handlers.
- [x] A3. `events/thymio_events.py` → `extensions/thymio/events.py` as
    `PLUGIN_EVENTS`. The module's private `EventType` copy (a circular-
    import dodge) became the real `events.event_types.EventType` — same
    fields. `event_types.py` no longer imports or splices the 14 events;
    they arrive through the loader. **One new generic loader attribute,
    `PLUGIN_EVENT_BLOCKLY_MAP`** (`{event: block_type}` merged into
    `EVENT_TO_BLOCKLY_MAP`), because core used to map every Thymio event to
    a same-named Blockly block so the Blockly *config* gates them — an
    extension event with no entry is always available (the multiplayer
    precedent), which would have silently un-gated Thymio events. Core
    consumers (`_panel.py`, `_event_crud.py`, `object_editor_main.py`, the
    event selector/panel, the Aseba exporter) import the new path until
    their own stages. Landmine: `EVENT_TYPES` only contains `thymio_*`
    after `load_all_plugins()` — the same class as the `play_sound`
    gotcha.
- [x] A4. `runtime/thymio_simulator.py` → `extensions/thymio/simulator.py`
    unchanged. `runtime/room.py` (robot-instance creation) and
    `runtime/playground_runner.py` import the new path for now — the
    room.py one is the temporary core→extension import Stage B removes.
- [x] A5. `update_thymio_robots()`'s body → `extensions/thymio/runtime.py`,
    run through `PLUGIN_FRAME_UPDATES`. **Not at `after_update` as
    planned**: the engine called it between `update()` (movement +
    collision) and the end-step/destroy loop, and `after_update` runs
    after destroy cleanup — moving it there would have given end-step
    handlers a one-frame-stale robot position and skipped sensor events
    for a robot destroyed that frame. Added a third generic phase,
    `"after_collision"`, at the exact old call site instead. Still reads
    `inst.is_thymio`/`thymio_simulator` (Stage B moves those into
    `extension_state`).

### Stage B — rendering + input (needs seams 0.2, 0.3)

- [x] B1. `runtime/thymio_renderer.py` → `extensions/thymio/renderer.py`;
    `draw_robot` registered via `PLUGIN_INSTANCE_OVERLAYS` replaces the
    robot loop in `GameRunner.render` (same spot, same order). A
    module-level `shared_renderer()` gives the overlay and — until B2 —
    `GameRunner.thymio_renderer` (the input hit-test) one instance.
- [x] B2. The button-press/hit-test logic inside `InputHandler` →
    `extensions/thymio/input.py`, wired through `PLUGIN_INPUT_HANDLERS`;
    `_thymio_mouse_presses` and `GameRunner.thymio_renderer` are gone from
    core (extension-local dict + `shared_renderer()`). `input_handler.py`
    and `game_runner.py` now contain **zero** Thymio references (pinned by
    a test). The B3 grep sweep therefore folded into B2; what remains for
    Stage B is the state/creation seam below.
- [x] B3 (re-scoped). Two more generic seams: `PLUGIN_INSTANCE_CREATED`
    (`(instance, instance_data, room)`, run once at `GameRoom`'s
    instance-build site — the only place the engine ever attached robot
    state) and `GameInstance.custom_rendered` (the sprite pass and both
    draw-event passes skip it; an overlay draws it). `is_thymio` /
    `thymio_simulator` are gone from `GameInstance`; the robot's state is
    `instance.extension_state["thymio"]["simulator"]`, reached only via
    `extensions/thymio/state.py`'s `simulator_of`. `room.py` and
    `instance.py` now contain zero Thymio references (pinned). The
    `is_thymio` **room-JSON flag** (written by the Roberta importer) is
    project data and still honoured — by the extension's hook.
    **Stage B complete: `runtime/` has no Thymio code left except
    `playground_runner.py`, which is Stage C2.**

Proof method for B1/B2, per this repo's established pattern for exactly this
class of move (`test_raycast_view.py`'s note about needing a real
`GameRunner.run()` loop, not a hand-initialized room): drive a real
`GameRunner` through a Thymio-bearing sample pre- and post-move and diff
rendered frames / dispatched events, not just source structure.

### Stage C — the playground editor, runner, and window (needs seam 0.4, 0.5)

The biggest chunk of UI code in the whole feature; treat it as its own
sub-arc.

- [x] C1. `editors/playground_editor/*` → `extensions/thymio/editor/` (all
    seven modules, `git mv`); the package's absolute self-imports became
    relative so it also works under the loader's synthetic package name.
    `core/ide/_editor_lifecycle.py`'s `open_playground_editor` imports the
    new path until C5 hands opening to the asset-tree category.
- [x] C2. `runtime/playground_runner.py` → `extensions/thymio/playground_runner.py`
    (`git mv`, no content changes — it already imported everything it
    needed from `extensions.thymio.*` and core's `ActionExecutor`, so this
    was a pure relocation). The editor's own opener
    (`extensions/thymio/editor/__init__.py`'s "Run" button) now uses a
    relative `..playground_runner` import; the two test files that
    constructed the window import the new absolute path.
- [x] C3a (found while starting C3, not in the original plan). Before
    moving the file: `editors/block_world_editor/window.py` — a
    **different** extension's editor — imports `PygameWidget` from
    `widgets/thymio_playground.py` verbatim ("it has zero Thymio-specific
    code", its own docstring says). Moving the whole file into
    `extensions/thymio/` would have made Block World depend on the Thymio
    extension, which breaks independent enable/disable. `PygameWidget`
    (a generic pygame-surface-to-QPixmap Qt widget, confirmed zero Thymio
    references) extracted to new `widgets/pygame_widget.py` (core, shared);
    `widgets/thymio_playground.py` and `block_world_editor/window.py` both
    import it from there now. Same "keep the generic part in core"
    judgment call the raycast Stage B2 precedent already established for
    `_render_draw_events`/`_sprite_top_left`/`_find_first_instance`.
- [x] C3b. `widgets/thymio_playground.py` (now `EditMode` +
    `ThymioPlaygroundWindow` only, ~1,250 lines) →
    `extensions/thymio/playground_window.py` via `git mv`, no further
    content changes (splitting it further stays a later, optional
    cleanup, not part of this move). `core/ide/_dialogs.py`'s
    `show_thymio_playground` and every test importer moved to the new
    path; `widgets/__init__.py`'s lazy `ThymioPlaygroundWindow`
    `__getattr__` accessor removed (nothing outside this file used it —
    every real caller already imported the class directly). Translation
    safety confirmed: `.tr()` resolves by runtime **class name**
    (`ThymioPlaygroundWindow`), not file path, so the move doesn't affect
    any shipped language's translations (same rule this doc's landmines
    section already carries from the i18n session notes).
- [x] C4. `widgets/thymio_diagram_widget.py` → `extensions/thymio/diagram_widget.py`
    via `git mv`, no content changes (pure Qt/`QPainter`, no pygame — was
    the one thing `widgets/__init__.py` imported eagerly, not lazily).
    `dialogs/thymio_action_selector.py`, `thymio_event_selector.py` and
    `editors/object_editor/thymio_events_panel.py` import the new path;
    `widgets/__init__.py` drops the eager import and the `__all__` entry
    entirely (no package-level `from widgets import ThymioDiagramWidget`
    caller existed to keep even a lazy accessor for). No dedicated test
    file existed for this widget before or after.
- [x] C5. "Playgrounds" wired fully through the Stage-0.4/0.5 registries;
    every hardcoded core entry deleted, not just `core/project_manager.py`
    (already generic since Stage 0.4) — the actual remaining hardcodes
    turned out to be `core/asset_types.py`'s module-level registration call
    (→ `extensions/thymio/__init__.py`'s `PLUGIN_ASSET_TYPES`),
    `widgets/asset_tree/asset_utils.py`'s static `ASSET_TYPE_REGISTRY`
    entry, `widgets/asset_tree/asset_tree_item.py`'s icon-map/elif
    branches (both already had generic `get_asset_tree_category()`
    fallbacks from Stage 0.5b — just needed the shadowing hardcodes
    removed), `core/ide/_assets.py`'s default-template `elif` branch, and
    **`core/ide/_editor_lifecycle.py`'s whole `open_playground_editor`
    method** — moved verbatim to a free function
    `extensions/thymio/editor/open_playground_editor(ide, name, data)`
    (the `AssetTreeCategory.open_editor` contract exists precisely so an
    extension can implement this without living in core; confirmed
    `ide.tr()` still resolves under the `PyGameMakerIDE` context regardless
    of which module the call site is in). New `PLUGIN_ASSET_TREE_CATEGORIES`
    registers the category with that opener + a `new_asset_template`
    matching the old hardcoded default arena/colors JSON exactly.
    **Landmine hit and fixed**: three pre-existing tests
    (`test_asset_type_registry.py`'s eight/dispatch tests,
    `test_asset_side_file_cleanup.py`, `test_duplicate_asset_side_file.py`)
    assumed "playgrounds" was always present/`editor_method`-shaped without
    calling `load_all_plugins()` first — same class as the long-standing
    `play_sound` gotcha; added the `editor_method`-or-`open_editor` branch
    and `autouse` `load_all_plugins()` fixtures. **Also found and fixed a
    real test bug of my own** (not a production regression): a C5 pin test
    left a real `PyGameMakerIDE()` with `current_project_data` still
    `None` and only `deleteLater()`'d (schedules, doesn't destroy) — a
    later, unrelated test's pytest-qt event pump delivered a deferred
    `changeEvent` to the lingering window and crashed on
    `current_project_data['name']`. Same landmine class as the Stage-C1
    native-crash note above; fixed by initializing
    `current_project_data` in the test, not by touching production code.
- [x] C6. Config dialogs — `dialogs/thymio_config_dialog.py`,
    `thymio_action_selector.py`, `thymio_event_selector.py` →
    `extensions/thymio/dialogs/` via `git mv`, no content changes (all
    three already imported their dependencies from `extensions.thymio.*`
    or core, with no cross-imports among themselves).
    `dialogs/_block_config_dialog_base.py` **stayed in core** exactly as
    planned — `THYMIO_CATEGORIES` is genuinely defined there and both
    `ThymioConfigDialog` and (unrelated, core-owned) `BlocklyConfigDialog`
    import it from that one shared place, so moving the Thymio dialog
    creates no cross-extension dependency. `core/ide_window.py` had one
    dead top-level `ThymioConfigDialog` import (unused outside
    `core/ide/_dialogs.py`'s own local import) — removed as an
    in-scope cleanup, not scope creep, since leaving a reference to the
    now-wrong old path would have been actively broken.
    `dialogs/__init__.py` drops its three eager re-exports (same "nothing
    outside this file used the package-level name" pattern as C4).
    **Stage C is now fully closed** (C1–C6).

### Stage D — external interop (self-contained, low risk)

- [x] D1. `export/Aseba/{aseba_exporter,playground_exporter}.py` →
    `extensions/thymio/export/{aseba_exporter,playground_exporter}.py`
    via `git mv`, kept as two files (they're genuinely separate concerns —
    whole-project export vs. one playground's export — merging would have
    been restructuring, not a move). Both already depended on nothing but
    stdlib + `core.logger`. `export/Aseba/` had no `__init__.py` (an
    implicit namespace package) and is now fully deleted.
- [x] D2. `export/Roberta/roberta_exporter.py` + `importers/roberta_importer.py`
    → `extensions/thymio/export/{roberta_exporter,roberta_importer}.py`
    (kept the original basenames for grep-ability, matching every other
    stage's convention, rather than the `roberta.py`/`import_roberta.py`
    names sketched here originally). `export/Roberta/__init__.py` (which
    only re-exported `RobertaExporter`, no other content in that dir) is
    deleted with it. **Landmine caught by a test, not by inspection**:
    `core/logger.get_logger(__name__)` bakes the *module path* into the
    logger name (`pygm.<name>`) — moving `roberta_importer.py` changed its
    logger from `pygm.importers.roberta_importer` to
    `pygm.extensions.thymio.export.roberta_importer`, silently breaking
    `test_audit_roberta_led.py`'s `logging.getLogger(<old name>)` capture
    shim (would have made that regression test always pass vacuously,
    capturing nothing, rather than failing loudly — caught only because
    the test suite was run, not from reading the diff).
- [x] D3. Wired "Export Aseba (Thymio) code…" / "Import Open Roberta XML…"
    through `PLUGIN_IDE_MENUS` (Stage 0.5a), replacing the `# [1.0]`
    comments in `core/ide/_menu_builder.py`. Both method **bodies** moved
    into `extensions/thymio/export/__init__.py` as free functions
    (`export_aseba_code(ide)`/`import_roberta_xml(ide)`, `self`→`ide`,
    same pattern as C5's `open_playground_editor`) — not left as thin core
    wrappers, since they're genuinely Thymio-specific, unlike the
    `open_*_editor` methods every asset type needs. Two things the naive
    move would have silently broken, both fixed by **attaching the
    callables to `ide` under their exact pre-hidden method names**
    (`ide.export_aseba_code`, `ide.import_roberta_xml` — Python doesn't
    care that they're lambdas now, not bound methods) rather than only
    wiring the new QActions: (1) `core/ide_window.py`'s existing generic
    `update_ui_state()` already has `if hasattr(self,
    'export_aseba_action'): ...` — storing the QAction as
    `ide.export_aseba_action` (matching the original attribute name) means
    that **zero-line-changed** core code keeps disabling it correctly with
    no project open; (2) `widgets/welcome_tab.py`'s `_on_import_roberta`
    already does `hasattr(self.main_window, 'import_roberta_xml')` — same
    zero-core-change reuse. The Roberta-import action needs
    `pygm_always_enabled` (it creates a project, must work with none
    open) — reused the existing generic property `update_ui_state()`
    already checks for `WelcomeTab`'s own buttons, rather than adding a
    new exemption mechanism. Un-hid `widgets/welcome_tab.py`'s "More
    options" Roberta-import entry as part of the same commit (it was the
    other explicitly-named `# [1.0]` site in this plan's D3 description).
    **Deliberately out of scope, left commented**: the whole Tools→Thymio
    Programming submenu (`show_thymio_playground`/
    `show_thymio_event_selector`/`show_thymio_action_selector`/
    `configure_thymio`/`toggle_thymio_tab` and their toolbar button) —
    none of those are File-menu Aseba/Roberta actions, so they weren't
    named in D3's scope; they're either a small D4 or fold into Stage G's
    re-enable pass.

### Stage E — the object-editor tab (needs seam 0.5; do this one last among the UI stages — it's the deepest coupling point)

- [x] E1. `editors/object_editor/thymio_events_panel.py` →
    `extensions/thymio/object_editor_panel.py` via `git mv`, no content
    changes (already imported everything from `extensions.thymio.*` plus
    the genuinely-shared `editors/object_editor/gm80_action_dialog.py`,
    which stays in core).
- [x] E2. `ObjectEditorMain`'s hardcoded Tab-2 construction, the whole
    `_on_thymio_events_modified`/`_on_thymio_event_selected`/
    `switch_to_thymio_mode` methods, and the `self.thymio_tab`/
    `self.thymio_events_panel`/`self.thymio_tab_index` state are all
    **deleted** — the already-shipped Stage-0.5c `PLUGIN_OBJECT_EDITOR_PANELS`
    loop (`for spec in get_object_editor_panels(): self._add_extension_panel(spec)`,
    already running since Stage 0.5c) now supplies the Thymio tab too,
    with `extensions/thymio`'s new `ObjectEditorPanel(key="thymio", ...)`
    reproducing `Config.get('show_thymio_tab', ...)` exactly via its
    `is_visible` callable. `set_thymio_tab_visible` stays as a **one-line
    named wrapper** (`self.set_extension_panel_visible('thymio', visible)`)
    — `core/ide/_dialogs.py`'s still-hidden `toggle_thymio_tab` duck-types
    this exact method name, and that method is out of D's/E's scope (the
    Tools→Thymio Programming submenu, deferred). The `blockly_preset ==
    'thymio'` auto-switch (`object_editor_main.py`) is the other
    deliberately-kept named exception, now calling
    `self.switch_to_extension_panel('thymio')` — the plan's own G5 bar
    anticipates a small number of exactly these ("the handful of named
    generic call sites").
  - **Real, shipped-stage bug found and fixed, not just this stage's own
    regression**: the Stage-0.5c seam itself (`_add_extension_panel`/
    `set_extension_panel_visible`) added a tab via
    `self.events_tab_widget.addTab(tab, spec.label)` — a **raw, never-`.tr()`'d
    string**. The original hardcoded Thymio tab used `self.tr("🤖 Thymio")`,
    a real, shipped, catalogued translation (confirmed in `translations/*.ts`,
    `<source>🤖 Thymio</source>`, context `ObjectEditorMain`) — moving it onto
    the untranslated seam would have silently reverted every non-English
    IDE to an English-only tab label. Fixed at the **seam**, not the call
    site: both spots now do `self.tr(spec.label)`. Safe because `.tr()`
    resolves by the *runtime class of the object it's called on*
    (`ObjectEditorMain` here, matching the original call site exactly) and
    because this repo ships hand-maintained `.ts`/`.qm` files with no
    `lupdate` re-extraction step, so a non-literal `.tr()` argument is not
    a hazard here the way it would be in a project relying on automatic
    string extraction. **Investigated the analogous C5 seam
    (`AssetTreeCategory.label`, "Playgrounds") for the same bug and found
    it's not one** — `AssetTreeItem` (a bare `QTreeWidgetItem`, no `.tr()`
    available at all) already renders every BUILT-IN category's emoji
    label from a hardcoded, never-translated Python dict; the `self.tr(...)`
    call in `asset_tree_widget.py`'s `setup_categories` computes a value
    that is unpacked and then **never actually used** (a pre-existing,
    unrelated dead-code path, confirmed by reading it — not something this
    plan's work touched or should fix). "Playgrounds" behaves exactly like
    every other asset-tree category already did; no regression, nothing to
    fix there.
  - Regression gate re-run, not just trusted from the diff, per this
    stage's own instruction: `test_object_events_panel_thymio_lossless_rewrite.py`
    and `test_thymio_else_preserved.py` both green (neither references the
    moved file path directly — they test the Python↔JSON event parser,
    unaffected by where the Qt panel widget lives).

### Stage F — Blockly toolbox (needs seam 0.6) — CLOSED

- [x] F1. Moved the 8 `"Thymio Events"`/`"Thymio Motors"`/… category dicts
      out of `config/blockly_config.py`'s `BLOCK_REGISTRY` into
      `extensions/thymio/blockly_categories.py` as `PLUGIN_BLOCK_CATEGORIES`
      (byte-identical dicts); moved the matching 8 per-language entries out
      of `config/blockly_translations.py`'s `CATEGORY_TRANSLATIONS` into
      `PLUGIN_BLOCK_CATEGORY_TRANSLATIONS`, keeping the existing
      `{lang: {category: text}}` shape (no new structure invented — matches
      what `register_category_translations()` already expected from Stage
      0.6). `BLOCK_TRANSLATIONS` had zero Thymio entries to move (verified
      by grep before starting — only category *names* were ever translated,
      not individual Thymio block names/descriptions).
  - **Ordering bug found and designed around before writing any code, not
    after.** `BlocklyConfig.get_thymio()`'s old body built the preset with
    `config.enable_category("Thymio Motors")` etc. — but `enable_category()`
    only populates `enabled_blocks` when the category is already a key in
    the *global* `BLOCK_REGISTRY` (`if category in BLOCK_REGISTRY: ...`),
    and an extension's `PLUGIN_BLOCKLY_PRESETS` dict is evaluated at
    *import* time, which is strictly before `events/plugin_loader.py`'s
    `_load_block_categories` calls `register_block_categories()` to merge
    `PLUGIN_BLOCK_CATEGORIES` into `BLOCK_REGISTRY` (both calls happen in
    the same loader method, category-merge first, preset-merge second, but
    the *module-level* preset object was already built — wrongly — before
    either ran). Built the naive way, the preset would have silently ended
    up with the right `enabled_categories` but an almost-empty
    `enabled_blocks` — the toolbox would show the 8 Thymio category headers
    with nothing inside them. Fixed by having
    `extensions/thymio/blockly_categories.py`'s `_build_thymio_preset()`
    read block types directly from the *local* `PLUGIN_BLOCK_CATEGORIES`
    dict instead of going through `enable_category()`/the global registry —
    sidesteps the ordering hazard entirely without touching the already-
    shipped Stage 0.6 `register_blockly_presets()` contract.
  - `THYMIO_CATEGORIES` (just the 8 category *names*, used by
    `dialogs/_block_config_dialog_base.py` for exclusion filtering) stays in
    core as originally decided — it's plain string data with no Thymio
    logic, and core's own `BlocklyConfigDialog` needs it too.
  - Two test call sites relied on the now-removed `BlocklyConfig.get_thymio()`
    classmethod directly: `tests/test_audit_regressions.py`'s
    `TestThymioPresetEnablesElseAction` and `tests/test_thymio_extension.py`'s
    `test_events_register_through_the_loader_with_blockly_gating`. Both
    switched to `load_all_plugins()` + `PRESETS["thymio"]`.
  - New pin tests in `tests/test_thymio_extension.py` (Stage F section):
    core's source no longer defines the categories/preset; the extension's
    `PLUGIN_BLOCK_CATEGORIES` matches `BLOCK_REGISTRY` byte-for-byte once
    loaded; the loaded preset's `enabled_blocks` is the *exact*
    `get_thymio()` set (event_create + every category's block types +
    start_block/end_block/else_action) — not just "categories enabled",
    since that weaker assertion is exactly what the ordering bug above
    would have passed vacuously; the 7-language translations register and
    resolve through `get_translated_category`; `THYMIO_CATEGORIES` stays in
    core and matches the extension's category names; and confirmation that
    the pre-existing `register_block_categories()` mechanism (which already
    rebuilds `PRESETS["full"]`/`"implemented_only"` whenever new categories
    are merged in) picks the Thymio categories back up automatically, with
    no changes needed there.
  - One test-writing landmine hit and fixed immediately: a first draft of
    `test_core_no_longer_carries_the_thymio_categories_or_preset` also
    asserted against the runtime `BLOCK_REGISTRY`/`PRESETS` dicts, which
    failed under the full suite (not in isolation) because those dicts are
    process-global and an earlier test in the same session had already
    called `load_all_plugins()`, merging the categories in — exactly the
    behaviour the next test checks for. Narrowed to a source-text-only
    check; the runtime-state assertions live in the "registers through the
    extension" test instead, which calls `load_all_plugins()` itself first.
- [x] F2. Confirmed `ThymioConfigDialog` (`extensions/thymio/dialogs/
      thymio_config_dialog.py`) needed no code change — it never called
      `get_thymio()` directly; it reads `BLOCK_REGISTRY` at dialog-open time
      (always after `load_all_plugins()` has run in the real IDE) and
      receives its starting `BlocklyConfig` from `core/ide/_dialogs.py`'s
      `configure_thymio()`, which already goes through `PRESETS[project_preset]`
      / `load_config()` — both now correctly see the extension-registered
      `"thymio"` preset once loaded.
  - Verification: targeted tests (`test_thymio_extension.py`,
    `test_audit_regressions.py`, `test_extension_seams.py`,
    `test_thymio_config_preset_name.py`, `test_blockly_i18n_uk.py`,
    `test_blockly_sub_actions.py`, `test_blockly_workspace_xml.py`) all
    green, then the full suite in three alphabetical sub-batches (this
    box's established RAM-safe pattern): a-g 2492 passed/0 failed, h-p 1671
    passed/0 failed, q-z 1366 passed/0 failed (2 pre-existing order-
    dependent `test_zip_save_state.py` failures under the full q-z batch,
    confirmed unrelated to this stage and passing clean in isolation —
    same flakiness class CLAUDE.md already documents for this suite, not a
    regression).

### Stage G — re-enable, remove the `# [1.0]` markers, tests/tooling sweep

- [x] **G1 (partial — UI-visibility product decision resolved, markers
      removed).** Asked the user explicitly before touching this, since it's
      the exact "product call, not architecture" fork this plan's Non-goals/
      Open-decision sections already flagged: literally deleting the 3
      `# [1.0]` marker comments in `core/ide/_menu_builder.py` means
      uncommenting the Tools→Thymio Programming submenu, the Configure
      Thymio Blocks menu item, and the toolbar button. **Decision: keep it
      hidden** — matches the standing 1.0 decision (memory:
      `thymio-hidden-for-1.0`), reversing it is out of scope for a
      relocation. Confirmed via `git grep -n '^\s*# \[1\.0\]'`: the
      convention had exactly one user (Thymio) — zero markers remain
      anywhere in the repo now, not just non-Thymio ones. What actually
      landed: the 5 Tools-menu/toolbar action handlers
      (`configure_thymio`, `toggle_thymio_tab`, `show_thymio_playground`,
      `show_thymio_event_selector`, `show_thymio_action_selector`) moved
      from `core/ide/_dialogs.py` into new `extensions/thymio/tools_menu.py`
      (free functions, `self`→`ide`, same pattern as `extensions/thymio/
      export`'s `export_aseba_code`/`import_roberta_xml`). New
      `_build_tools_menu`/`_build_toolbar` in `extensions/thymio/__init__.py`
      build the same UI the commented-out core code used to, wired through
      the existing `PLUGIN_IDE_MENUS`/`PLUGIN_IDE_TOOLBAR` seam (Stage 0.5) —
      **still gated by the same `show_thymio_tab` config flag** that already
      gates the object-editor tab, so build nothing on a default install;
      core now carries the hiding decision as *data* (one config default),
      not as commented-out code naming Thymio. Flipping that one flag later
      (the "Open decision" section's promised one-line follow-up) brings the
      tab, the Tools-menu entries and the toolbar button back together.
  - **Generalized a second thing found en route**: `core/ide_window.py`'s
    `update_ui_state()` also hardcoded three Thymio action-attribute names
    directly (`thymio_add_event_action`/`thymio_add_action_action`/
    `thymio_toolbar_action` — enable-with-project; `thymio_import_roberta_action`
    — always-enabled; plus `export_aseba_action` — enable-with-project, a
    Stage-D leftover). All five are real `QAction`s parented to `ide` via
    `ide.create_action(...)`, so they're already visited by
    `update_ui_state()`'s existing `findChildren(QAction)` sweep — added two
    new QAction-property checks there (`pygm_requires_project`, alongside
    the existing `pygm_always_enabled`) so an extension flags its own
    actions instead of core naming them. All five hardcoded hasattr blocks
    deleted; `_build_tools_menu`/`_build_file_menu` set the property on the
    actions they build instead. This is the same class of generalization
    `pygm_always_enabled` itself already established for the Welcome-tab
    dropdown (2026-06-26) — reusing precedent, not inventing new
    architecture.
  - New tests in `tests/test_thymio_extension.py`'s "G — Tools menu /
    toolbar" section: the 5 methods live in the extension and not on
    `DialogsMixin`; zero real `# [1.0]` markers repo-wide (`git grep`, exit
    code 1 = no matches); `_build_tools_menu`/`_build_toolbar` build nothing
    when `show_thymio_tab` is False (default) and build the full UI —
    correct actions, correct `pygm_requires_project`/`pygm_always_enabled`
    properties — when True; `update_ui_state()` actually gates those
    properties correctly end-to-end (disabled with no project, enabled with
    one, roberta-import always enabled); `core/ide_window.py`'s source no
    longer contains any of the five hardcoded action-attribute names. Also
    moved `test_audit_ide_window_leaks.py`'s L4 test (`show_thymio_playground`
    reuse/`WA_DeleteOnClose`) into this file, updated to call the now-free
    function — that file's docstring/scope trimmed to just L3.
  - **Test-harness landmine, not a production bug** (cost real debugging
    time, worth remembering): a `QMenu` parented to a *Python-subclassed*
    `QMainWindow` (even a trivial `class Stub(QMainWindow): pass`) hits a
    PySide6/shiboken wrapper-ownership quirk if `QAction.menu()` is called
    **twice** on the same action (e.g. once in a list-comprehension's filter
    condition, once for its value) — the second lookup raises `RuntimeError:
    Internal C++ object (QMenu) already deleted`, even though the submenu's
    Qt-level C++ parent (the containing menu) is still alive and referenced.
    Confirmed via a from-scratch minimal repro that a QMenu parented to a
    **plain, non-subclassed** `QMainWindow()` does NOT hit this — subclassing
    is the trigger. Real production code is unaffected (`_build_tools_menu`
    only ever calls `.addMenu()`'s return value once and keeps that single
    reference); fixed the test by looking up `.menu()` exactly once into a
    local per action instead of a double-evaluated comprehension.
  - Suite verified in three alphabetical sub-batches after this unit: a-g
    2491 passed/0 failed, h-p 1671 passed/0 failed, q-z 1372 passed/0 failed
    (the same 2 pre-existing order-dependent `test_zip_save_state.py`
    failures as Stage F, re-confirmed passing in isolation — not a
    regression).
  - **G1 is NOT fully closed** — see G5's new sub-item below for the
    remaining, much larger piece.

- [x] G2. Turned out to already be done — each prior stage (A–F) updated its
      own tests' imports as it moved the code they exercised, the same
      "tests stay in `tests/`, only their imports change" pattern this item
      anticipated, just executed incrementally rather than as one pass at
      the end. Verified rather than migrated: grepped all 22
      Thymio/Roberta/Aseba/playground test files (`test_aseba_*`,
      `test_audit_aseba_*`, `test_audit_playground_*`,
      `test_audit_roberta_*`, `test_audit_thymio_*`,
      `test_object_events_panel_thymio_*`, `test_playground_*` — the
      Thymio-relevant subset, `test_roberta_*`, `test_thymio_*`) for any
      import from an old pre-move path (`runtime.thymio_*`,
      `actions.thymio_*`, `events.thymio_*`, `widgets.thymio_*`,
      `dialogs.thymio_*`, `editors.playground_editor`, `export.Aseba`,
      `export.Roberta`, `importers.roberta_importer`) — zero hits. Also
      confirmed the specific landmine this item called out (the
      `PluginExecutor`-not-`ActionExecutor` dispatch pattern) is already
      correctly handled: `test_audit_thymio_simulator_guard.py` builds a
      bare `ActionExecutor` and populates its `action_handlers` via
      `extensions.thymio.handlers.register_thymio_actions(ex)`, not by
      calling `ActionExecutor.execute_thymio_*_action` directly. Full
      22-file battery: 106 passed, 0 failed. New pin test
      (`test_thymio_behavioural_tests_import_from_the_extension_not_old_paths`)
      locks this in for future stages, since without it a regression here
      would be silent (a stale import only breaks if something actually
      still exists at the old path to accidentally satisfy it, or errors
      obscurely if not — worth a real check).
- [x] G3. Verified `tools/action_ref_i18n.py`, `tools/gen_preset_docs.py`,
      `scripts/gen_translation_ts.py` — no code changes needed.
  - **Real architectural fact worth recording, not a bug**: Thymio's 28
    actions have **never** registered into the generic `ACTION_TYPES`
    registry, before or after this plan. `extensions/thymio/__init__.py`
    exposes `THYMIO_ACTIONS` (built from `actions.core.ActionDefinition` —
    the older GM80-dialog schema `THYMIO_TAB` reads) but deliberately no
    `PLUGIN_ACTIONS` (the `events.action_types.ActionType`-based dict
    `plugin_loader._load_actions` merges into `ACTION_TYPES`). Confirmed by
    running `load_all_plugins()` then checking `ACTION_TYPES` directly: 0
    `thymio_*` entries. `PluginExecutor` (the runtime handlers) still
    registers fine — `plugin_loader` checks for it independently of
    `PLUGIN_ACTIONS` — so gameplay is unaffected; only the *generic*
    action-picker/Blockly-auto-block/wiki-reference machinery never sees
    these 28 actions, exactly as before this stage. Confirmed against the
    live wiki: `wiki/Full-Action-Reference.md`'s current 161-action count
    sums its 13 listed categories exactly, with zero Thymio content and no
    Thymio category — this generator has *always* excluded Thymio, not a
    regression from the move.
  - `tools/gen_preset_docs.py` already explicitly filters `thymio_` events
    out of its beginner/intermediate preset docs (a pre-existing defensive
    filter, unrelated to and unaffected by the move); ran it — completes
    cleanly, zero `thymio_` entries in its missing-translation report.
  - `tools/gen_action_reference.py` (the generator `action_ref_i18n.py`
    feeds) ran cleanly for English; confirmed zero Thymio leakage in the
    output. **Found, but explicitly out of scope here**: the run also
    picked up 7 pre-existing, unrelated new actions in the Network
    (multiplayer_lan) category (161 → 168 total) that had never been
    regenerated into the wiki — genuine drift from other sessions' work,
    nothing to do with Thymio. Reverted the regeneration (`git checkout --
    wiki/`) rather than publish an unrelated fix inside this stage's
    commit; regenerating+publishing the wiki is its own task for whoever
    picks up the Network category next, not logged as a new TODO item
    here since it isn't blocking anything.
  - `scripts/gen_translation_ts.py` has no dependency on `ACTION_TYPES` at
    all (it pulls source text from an existing reference `.ts` file, not
    by scanning live Python) — confirmed by grep (one unrelated historical
    comment) and a clean import.
- [x] G4. `extensions/thymio/extension.json` already existed (written back in
      an earlier stage, `enabled: true` — this is the *loader*-level flag,
      i.e. "existing Thymio-authored projects keep working," a different
      axis from the UI-visibility flag G1 resolved; the two are independent
      and both currently match pre-refactor behaviour). Wrote
      `extensions/thymio/README.md` (every sibling extension has one; it's
      the largest one yet, since Thymio is the worked example for nearly
      every seam `extensions/README.md` documents at once — actions,
      events, instance overlay, input handler, frame-update, instance-
      created, asset type, IDE menu/toolbar, object-editor panel, Blockly
      categories). Pin test (`test_readme_exists_and_matches_reality` in
      `tests/test_thymio_extension.py`) cross-checks its factual claims
      (action/event/sensor/LED counts) against the real
      `THYMIO_ACTIONS`/`THYMIO_EVENT_TYPES`/`ThymioSensorState`/
      `ThymioLEDState` — **caught a real error in the README's first
      draft** (wrote "5 proximity sensors"; the simulator actually has 7)
      before it was ever committed, the same "write the test, don't trust
      the prose" lesson `docs/EYEBALL_FIXES_2026-08-16.md`'s own README
      pin-test note already recorded.
G5. Full-repo grep sweep: zero `thymio`/`Thymio`/`aseba`/`Aseba`/`roberta`/
    `Roberta` references left in `core/`, `runtime/`, `editors/` (excluding
    `editors/object_editor/object_editor_main.py`'s now-generic panel-registry
    call site), `widgets/` (excluding the now-generic asset-tree/menu
    call sites), `dialogs/` (excluding `_block_config_dialog_base.py`'s
    still-accurate docstring mention, AND `dialogs/blockly_config_dialog.py`'s
    use of `THYMIO_CATEGORIES` purely to *exclude* those category names from
    the generic dialog — same already-decided "stays in core, it's just
    string data" reasoning, not previously written down as its own
    exception), `config/` (excluding the `PLUGIN_BLOCK_CATEGORIES` merge
    point) — this is the "fully independent" bar this plan is named for,
    made checkable by a single command rather than a judgment call.
  - **`core/`, `runtime/`, `widgets/`, `dialogs/`, `config/`: done as of
    this G1 unit** — re-ran the sweep after landing it; every remaining hit
    in those five trees is a pointer comment ("moved to extensions/thymio",
    a plan-doc/stage citation) or one of the two named exceptions above.
    Confirmed by `git grep -niE 'thymio|aseba|roberta'` per directory.
  - **`editors/`: NOT done — a real, previously-undiscovered gap, much
    bigger than a grep-and-delete.** Stage E's own docstring claim ("the
    whole Thymio-specific side of it now") only covered the *dedicated*
    object-editor Thymio tab (`ObjectEditorPanel`); the *Standard* event
    panel — reachable with the Thymio tab OFF, i.e. on every default
    install with a `thymio*`-named object in the project — has deep, never-
    before-touched Thymio awareness across six files:
    - `editors/object_editor/events/_panel.py` — imports
      `THYMIO_EVENT_CATEGORIES`/`is_thymio_event` from the extension;
      `execute_code`-parsing logic specifically detects and re-derives
      Thymio actions from Python source (the "lossless rewrite" guard —
      has its own dedicated regression suite,
      `tests/test_object_events_panel_thymio_lossless_rewrite.py`).
    - `editors/object_editor/events/_event_crud.py` — same imports; builds
      a whole "🤖 Thymio Events" submenu (grouped by category, sorted,
      "Visual Selector..." entry) inside the Standard panel's Add-Event
      context menu; `add_thymio_event_with_selector`.
    - `editors/object_editor/events/_action_crud.py` —
      `add_thymio_action_with_selector`/`add_thymio_action_to_sub_event`,
      importing `ThymioActionSelector` directly.
    - `editors/object_editor/events/_context_menu.py` — 4 call sites adding
      a "🤖 Thymio Action..." context-menu entry, gated on
      `panel.project_has_playgrounds()`.
    - `editors/object_editor/blockly_widget.py` — filters Thymio blocks/
      categories out of the Blockly toolbox when the project has no
      playground.
    - `editors/object_editor/python_code_parser.py` — the largest single
      piece: `THYMIO_METHOD_TO_ACTION`, per-action Python-code-template
      strings for every `thymio_*` action/event, and a family of
      `_try_parse_thymio_*` methods (call/assignment/aug-assignment/
      conditional/compare/button-check) implementing the Python↔action-JSON
      round-trip for Thymio code specifically.
    None of this was in scope for any A–F stage (they only ever touched the
    *dedicated* Thymio tab and its own panel/dialogs); it was found only by
    actually running G5's grep sweep, not anticipated when this plan was
    written. It's real, working, tested functionality (Standard-mode users
    can add Thymio events/actions without ever opening the dedicated tab),
    not dead code — moving it needs the same behaviour-preservation rigor
    every other stage used, and `python_code_parser.py`'s piece specifically
    carries real regression risk given its existing dedicated test suite.
    **Deliberately not attempted in the same session as G1** (this plan's
    own session-limit discipline: one commit-sized, reviewable unit at a
    time) — sized as its own follow-up pass, file by file, each with its
    own before/after proof and test run, the same way Stage C's file-by-file
    moves were sequenced. Whether this six-file sweep needs its own new
    seam (an "editor contributes Standard-mode event/action menu entries"
    extension point, mirroring `PLUGIN_OBJECT_EDITOR_PANELS`) or can move
    as free functions the way Stage D/G1 did is an open design question for
    that follow-up, not decided here.

### Stage G5b — the `editors/object_editor/` sweep (the design question above, answered)

Read all six files in full before writing this. **Four new seams needed** —
each one genuinely generic (any future extension with its own events/actions
hits the exact same four gaps), not Thymio-specific machinery in disguise.
All four live in `core/ide_extension_points.py` (same module Stage 0.5's
menu/toolbar/asset-tree/panel seams already live in), same `@dataclass` +
`register_*`/`get_*`/`clear_*` style as `ObjectEditorPanel`/`AssetTreeCategory`.

- [x] **G5b.1 — toolbox visibility filter** (`blockly_widget.py`,
      `apply_configuration`). Done, implemented exactly as drafted below
      (one refinement: `is_enabled` really does mean "True = show" per the
      dataclass's own docstring, so Thymio registers
      `is_enabled=_project_has_playgrounds` directly — no inversion needed,
      simpler than the draft's `lambda w: not _project_has_playgrounds(w)`).
  ```python
  @dataclass(frozen=True)
  class ToolboxVisibilityFilter:
      is_enabled: Callable       # (widget) -> bool; True = show, False = hide
      owns_block: Callable       # (block_type: str) -> bool
      owns_category: Callable    # (category: str) -> bool

  PLUGIN_TOOLBOX_VISIBILITY_FILTERS: List[ToolboxVisibilityFilter] = []
  def apply_toolbox_visibility_filters(enabled_blocks, enabled_categories, widget):
      for f in _toolbox_visibility_filters:
          if not f.is_enabled(widget):
              enabled_blocks = {b for b in enabled_blocks if not f.owns_block(b)}
              enabled_categories = {c for c in enabled_categories if not f.owns_category(c)}
      return enabled_blocks, enabled_categories
  ```
  `blockly_widget.py`'s `apply_configuration` calls
  `apply_toolbox_visibility_filters(enabled_blocks, enabled_categories, self)`
  instead of the inline `if not self.project_has_playgrounds(): ...` block;
  `project_has_playgrounds()` (the method) was deleted from
  `blockly_widget.py` entirely — the extension's own registered
  `is_enabled` closure does the identical parent-walk internally (moved,
  not shared, since `is_enabled` only ever needs the widget, not two
  copies of the same method on two different classes). Thymio registers:
  `is_enabled=_project_has_playgrounds`,
  `owns_block=lambda b: b.startswith("thymio_")`,
  `owns_category=lambda c: c.startswith("Thymio ")`.
  `_project_has_playgrounds(widget)` lives in `extensions/thymio/__init__.py`
  (not a new module — small enough to sit with the other registration
  helpers), written to be reused unchanged by G5b.2/G5b.3's `is_visible`
  checks later (same parent-walk contract works for the events panel too).
  - New generic seam tests (dummy registrant, before Thymio depends on it):
    `tests/test_extension_seams.py`'s "Toolbox visibility filters" section
    — validation, correct hide-only-when-disabled behavior, a raising
    filter is logged and skipped rather than corrupting the toolbox, and
    the loader wiring. **Fixture landmine caught by the full-suite gate,
    not the file run alone**: `clean_toolbox_filters` only snapshotted
    state for teardown, not setup — passed every time run file-by-file,
    then failed under the full `a-g` batch because an earlier test file
    had already called `load_all_plugins()`, so Thymio's real filter was
    already in the registry and an exact-equality assertion
    (`get_toolbox_visibility_filters() == [good]`) saw two entries, not
    one. Fixed by clearing at setup too, not just teardown — the same
    "run the whole batch, not just the new file" discipline this plan has
    hit before (the multiplayer-lan host-loss teardown bug, CLAUDE.md's
    2026-09-02/03 note).
  - Thymio-side pin tests in `tests/test_thymio_extension.py`'s new "G5b.1"
    section: `blockly_widget.py`'s source no longer has any
    `startswith("thymio_"/"Thymio ")` check, no `def project_has_playgrounds`,
    no direct `extensions.thymio` import; the registered filter hides/shows
    correctly through the generic function; and a real `BlocklyWidget()`
    instance's `apply_configuration()` — with `web_view.page().runJavaScript`
    intercepted to inspect the actual JSON payload sent to the toolbox JS —
    confirms `thymio_set_motor_speed`/`"Thymio Motors"` are excluded
    end-to-end while `move_free`/`"Movement"` survive.
  - Suite: three alphabetical sub-batches after the fixture fix, a-g 2494
    passed/0 failed, h-p 1671 passed/0 failed, q-z 1377 passed/0 failed (the
    2 pre-existing `test_zip_save_state.py` failures plus one NEW isolated
    flake, `test_tutorial_panel_i18n_verification.py::test_every_lesson_every_page_loads[pt]`
    — unrelated subject matter, confirmed passing clean in isolation
    (28/28), same pre-existing order-dependent-flakiness class as the zip
    one, not a regression from this unit).

- [x] **G5b.2 — add-event-menu contribution** (`_event_crud.py`,
      `show_add_event_menu`). Done, implemented as drafted below.
  ```python
  @dataclass(frozen=True)
  class AddEventMenuContribution:
      key: str                   # matches an ObjectEditorPanel.key, so
                                  # owned_events() can be reused rather than
                                  # duplicating "which events are mine"
      build: Callable            # (menu, panel, available_events) -> None
                                  # -- builds its own submenu/separator iff
                                  # it has anything to show; a no-op if not

  PLUGIN_ADD_EVENT_MENU_CONTRIBUTIONS: List[AddEventMenuContribution] = []
  ```
  `show_add_event_menu` splits `available_events` into "not owned by any
  registered contribution" (the existing standard-events loop, unchanged)
  and hands the FULL `available_events` list to each contribution's
  `build(menu, panel, available_events)` — the contribution itself filters
  by its own `owned_events()` (via `get_object_editor_panels()`, keyed by
  `key`) rather than the panel doing it. Thymio's `build` is
  `_event_crud.py`'s old inline Thymio submenu block, moved verbatim into
  new `extensions/thymio/panel_menus.py`, `self`→`panel`,
  `is_thymio_event`→membership in `owned_event_names("thymio")` (which
  reads the "thymio" `ObjectEditorPanel`'s own `owned_events()`, the exact
  same set `is_thymio_event` checked). `add_thymio_event_with_selector`
  moved to the same new module as a free function (`panel` param) rather
  than into `tools_menu.py` — that module is the IDE-chrome Tools-menu/
  toolbar side (deals with `ide`, gated by `show_thymio_tab`); this one is
  the Standard panel's own menus (deals with `panel`, gated by
  `_project_has_playgrounds`), different enough seams to earn a sibling
  module, per the plan text's own "or a new sibling module" option.
  Registered via a tiny `_thymio_add_event_menu_build` wrapper in
  `__init__.py` rather than passing `panel_menus.build_add_event_menu`
  directly — `panel_menus.py` imports PySide6 at module top level (same as
  every other Qt-touching module here), and `__init__.py`'s own
  `PLUGIN_ADD_EVENT_MENU_CONTRIBUTIONS = [...]` list is built eagerly at
  import time, so a direct reference would have made `import
  extensions.thymio` pull in PySide6 even in the game process — the
  wrapper's `from .panel_menus import ...` stays inside the function body,
  only importing the module when a menu is actually about to be built in a
  real IDE.
  - Also fixed as a direct, confirmed consequence: `extensions/thymio/
    tools_menu.py`'s `show_thymio_event_selector` had a dead `hasattr(...,
    'add_thymio_event_with_selector')` guard (never actually called the
    method — just used its presence as a type check); left unguarded it
    would have permanently short-circuited that code path once the method
    moved. Simplified to proceed directly, since the outer
    `hasattr(current_widget, 'events_panel')` check already establishes
    the right type. A second, already-fully-dead
    `from extensions.thymio.events import THYMIO_EVENT_CATEGORIES,
    is_thymio_event` import in `_panel.py` (unused anywhere in that file,
    predating this unit) was removed too, directly adjacent to this
    change.
  - New generic seam tests, dummy registrant, in `tests/
    test_extension_seams.py`'s "Add-event-menu contributions" section:
    dataclass validation, a raising contribution is logged and skipped
    without blocking the others, `owned_event_names()` against a real
    `ObjectEditorPanel`, and the loader wiring.
  - Thymio-side pin tests in `tests/test_thymio_extension.py`'s new
    "G5b.2" section: `_event_crud.py`'s source no longer mentions
    `extensions.thymio`, `is_thymio_event`, `THYMIO_EVENT_CATEGORIES`, or
    `add_thymio_event_with_selector`; the contribution registers under key
    `"thymio"`; `build_add_event_menu` hides/shows correctly with/without a
    playground, called directly; and a real end-to-end run through
    `ObjectEventsPanel.show_add_event_menu()` (the actual call site)
    confirms the submenu appears iff the project has a playground.
  - **Real landmine, caught by the full-suite gate, not the file run
    alone — worth remembering for any future test that opens a real Qt
    menu/dialog.** The end-to-end test's first draft called the real
    `menu.exec(...)`, scheduling a `QTimer.singleShot` to close it — the
    standard textbook way to drive a modal Qt call under test, and it
    passed every time run alone or with its own two sibling files. Under
    the full `q-z` batch it intermittently failed a DIFFERENT, unrelated
    later test
    (`test_toolbox_visibility.py::test_extension_action_shown_in_beginner_when_active_via_settings`)
    with `RuntimeError: Internal... QLabel already deleted` inside
    `core/ide_window.py`'s `QTimer.singleShot(3000, lambda: self.
    status_label.setText(...))`. Root cause: `menu.exec()` starts a real
    native Qt event loop, which dispatches EVERY due timer in the process,
    not just the one this test scheduled — by the time this test ran deep
    into the batch, an unrelated, already-stale 3-second status-bar timer
    left behind by some earlier IDE-window-constructing test was already
    overdue, and this test's `exec()` call was simply the first real
    nested event-loop opportunity after it went stale. Confirmed by
    bisection (clean HEAD: only the 2 already-known
    `test_zip_save_state.py` flakes; this branch before the fix: that plus
    the toolbox_visibility one; same batch after the fix: back to just the
    2 known flakes). **Fix**: monkeypatching `exec` on the `QMenu` *class*
    silently doesn't intercept the call at all (confirmed separately — it
    hung instead, the real blocking loop still ran); a per-**instance**
    `self.exec = lambda ...` assignment does shadow it (also confirmed),
    needs no event loop or wall-clock time, and sidesteps the whole class
    of "real nested loop processes unrelated stale timers" risk entirely.
    The underlying `core/ide_window.py` dangling-timer landmine itself was
    left alone — real, but a different, pre-existing bug outside this
    unit's scope.
  - Suite: `test_extension_seams.py` + `test_thymio_extension.py` +
    `test_toolbox_visibility.py` together, 106 passed/0 failed; full
    three-batch alphabetical run, 5589 passed/0 failed (beyond the 2
    pre-existing `test_zip_save_state.py` flakes, confirmed present
    identically on clean HEAD).

- [x] **G5b.3 — add-action-menu contribution** (`_context_menu.py`, 4 call
      sites; `_action_crud.py`'s two Thymio methods move with it). Done,
      implemented as drafted below.
  ```python
  @dataclass(frozen=True)
  class AddActionMenuContribution:
      label: str                                          # e.g. "🤖 Thymio Action..."
      is_visible: Callable                                # (panel) -> bool
      handler: Callable    # (panel, event_name, sub_event_key: Optional[str]) -> None

  PLUGIN_ADD_ACTION_MENU_CONTRIBUTIONS: List[AddActionMenuContribution] = []
  def apply_add_action_menu_contributions(add_action_menu, panel, event_name, sub_event_key=None):
      for c in _add_action_menu_contributions:
          if not c.is_visible(panel):
              continue
          add_action_menu.addSeparator()
          action = add_action_menu.addAction(panel.tr(c.label))
          action.triggered.connect(
              lambda checked=False, e=event_name, k=sub_event_key: c.handler(panel, e, k))
  ```
  Replaced all four near-identical
  `if panel.project_has_playgrounds(): add_action_menu.addSeparator(); ...`
  blocks in `_context_menu.py` with one call each:
  `apply_add_action_menu_contributions(add_action_menu, panel, event_name)`
  (three call sites) and `..., event_name, sub_event_key)` (the keyboard
  sub-event call site). `add_thymio_action_with_selector`/
  `add_thymio_action_to_sub_event` moved out of `_action_crud.py` into
  `panel_menus.py` (the same sibling module G5b.2's Thymio build lives in,
  not `tools_menu.py` — same reasoning as G5b.2's note) as free functions
  (`panel` param, verbatim bodies, `self`→`panel`). New
  `thymio_add_action_menu_handler(panel, event_name, sub_event_key)` is the
  actual `AddActionMenuContribution.handler` registered — it dispatches to
  one or the other based on whether `sub_event_key` is `None`. Reused
  G5b.1's `_project_has_playgrounds` helper for `is_visible` directly (no
  wrapper needed, unlike the `build`/`handler` callables themselves, which
  DO need a tiny lazy-import wrapper in `__init__.py` for the same
  PySide6-in-game-process reason as G5b.2).
  - Also removed, as a direct, confirmed consequence: `_panel.py`'s own
    `project_has_playgrounds` method, now dead — `_event_crud.py` stopped
    calling it in G5b.2 and `_context_menu.py` was its last remaining
    caller.
  - New generic seam tests in `tests/test_extension_seams.py`'s
    "Add-action-menu contributions" section: dataclass validation (all
    three ways an `AddActionMenuContribution` can be malformed), a raising
    `is_visible` is logged and skipped without blocking a later visible
    contribution (including a discovered detail worth noting: a visible
    contribution's own leading `addSeparator()` shows up in `menu.actions()`
    as an empty-text action — real Qt behavior, not a bug, and the test
    filters it out explicitly rather than special-casing it away), a real
    `QAction.trigger()` reaching the registered handler with the right
    `(event_name, sub_event_key)`, and the loader wiring.
  - Thymio-side pin tests in `tests/test_thymio_extension.py`'s new "G5b.3"
    section: `_context_menu.py`/`_action_crud.py`/`_panel.py` source checks;
    the contribution registers with a "Thymio Action" label; the dispatch
    function routes to the right underlying function with a monkeypatch-based
    unit test (no dialog/Qt involved at all); the gating behaves correctly
    through `apply_add_action_menu_contributions` directly; and a real
    end-to-end run through `_context_menu.build_context_menu()` (the actual
    call site) confirms the "Thymio Action..." entry appears in the real
    Add Action submenu iff the project has a playground.
  - **Second real landmine, also caught only by running under pytest (not
    a standalone script), worth remembering for any future test that reads
    a live Qt submenu object.** The end-to-end test's first draft returned
    the "Add Action" submenu's `QMenu` through a small local helper
    function (`_add_action_submenu(menu): ... return submenu`). Every
    single run under pytest — alone, in this file, in the full batch, even
    copy-pasted into a brand-new minimal standalone test file — raised
    `RuntimeError: Internal C++ object (QMenu) already deleted` on the very
    next line that touched the returned object, with 100% reproducibility.
    An otherwise byte-identical standalone `.py` script (no pytest
    involved) run directly never reproduced it, not even once, including
    under an explicit `gc.collect()`. Bisected by elimination (ruled out:
    the `monkeypatch` fixture itself, `try/finally` structure, intermediate
    `assert` statements, `built.clear()`) down to exactly one factor: a
    Qt-object lookup that crosses a Python function-call boundary and
    returns the live object, specifically under pytest's execution
    environment. Root cause not fully understood (presumably a PySide6/
    Shiboken ownership-tracking interaction with how pytest's own
    machinery holds frames/references, not a bug in this seam's own code,
    which is plain `.addMenu()`/`.addAction()`/`.actions()` calls no
    different from the rest of this codebase's existing menu-building
    tests) — not worth chasing further given it's a test-authoring
    landmine, not a product bug. **Fix, and the rule to carry forward**:
    look up and read a live Qt child object (a submenu, in this case) all
    in the SAME function frame where it's obtained — never pass it out
    through a nested helper function's return value.
  - Suite: `test_extension_seams.py` + `test_thymio_extension.py` together,
    99 passed/0 failed; full three-batch alphabetical run, 5600 passed/0
    failed (beyond the 2 pre-existing `test_zip_save_state.py` flakes).

- [ ] **G5b.4 — post-load events transform hook** (`_panel.py`,
      `_parse_execute_code_actions`, called from `load_events_data`). Do
      this LAST — it's the one with real regression risk
      (`tests/test_object_events_panel_thymio_lossless_rewrite.py` pins
      exact lossless-rewrite behavior; the "regenerate and re-parse to
      confirm the rewrite round-trips" guard is the load-bearing safety
      property, not incidental).
  ```python
  PLUGIN_EVENTS_DATA_TRANSFORMS: List[Callable] = []   # each: (panel) -> None
  def apply_events_data_transforms(panel):
      for fn in _events_data_transforms:
          try:
              fn(panel)
          except Exception:
              logger.exception(...)   # one broken extension can't corrupt load for the rest
  ```
  `load_events_data` calls `apply_events_data_transforms(self)` instead of
  `self._parse_execute_code_actions()` directly; the Thymio-specific
  method (the `'thymio.' in code` substring gate, the parse/regenerate/
  re-parse round-trip check, `PythonToActionsParser`/
  `ActionsToPythonGenerator` — both already-generic classes in
  `python_code_parser.py`, untouched) moves to
  `extensions/thymio/` as a free function taking `panel`. **Proof
  obligation before deleting the core copy**: run
  `test_object_events_panel_thymio_lossless_rewrite.py` and the parsing-
  specific subset of `test_thymio_*`/`test_audit_thymio_*` against BOTH
  the pre-move method (via `git show HEAD:...`) and the moved free
  function across the same input matrix, diff `current_events_data`
  byte-for-byte — this file's own established behavior-preservation bar,
  not a new one.
  - `python_code_parser.py`'s `THYMIO_METHOD_TO_ACTION` /
    `ACTION_TO_PYTHON_CODE`'s thymio_* entries / the event-name mapping /
    the `_try_parse_thymio_*` method family are the actual **parsing
    engine** G5b.4's transform calls into — NOT covered by a new seam
    here. Whether *that* also needs to move (a `PLUGIN_CODE_PARSERS`-style
    hook so `PythonToActionsParser`/`ActionsToPythonGenerator` themselves
    carry zero Thymio knowledge) is a **separate, larger design question**
    deliberately deferred past G5b — the four seams above are enough to
    get every *caller* of Thymio-specific logic out of the six files;
    `python_code_parser.py` moving its *engine* internals is optional
    follow-up work, not required to hit "core carries no Thymio-specific
    code" for the six files this sweep is about (the parser file itself
    would still be the one exception, same tier as `THYMIO_CATEGORIES`
    staying in `dialogs/_block_config_dialog_base.py` — shared machinery
    holding one extension's data, not core logic *about* Thymio).

Order matters: G5b.1 is fully independent; G5b.2/G5b.3 both need
`get_object_editor_panels()`'s `owned_events()` (already exists, Stage
0.5c/E) but are otherwise independent of each other; G5b.4 is independent
of the other three but riskiest, hence last. Each is its own commit, full
suite green after each, per this plan's standing discipline.

## Testing / verification strategy

Same discipline this repo has used for every prior consolidation
(`CLAUDE.md`'s "Audit-cleanup history" methodology, applied here):

- Every relocation is proven **behavior-preserving against pre-move HEAD**
  before the old copy is deleted — snapshot with `git show HEAD:path`,
  exercise old vs. new across a representative input matrix, diff observable
  state. For rendering, that means real pixel/frame comparison (the raycast
  precedent: pixel-sampling alone can't always distinguish pre/post states,
  intercept the actual call args when that matters).
- Each new Stage-0 seam gets its own generic test with a **dummy
  registrant**, proving the mechanism before Thymio code depends on it —
  isolates "the seam is wrong" from "the 9,300-line move is wrong."
- Full suite + push after every unit, not batched — this job is large enough
  that losing a mid-session run to the account's usage limit is a real risk;
  per-unit commits mean a stopped session resumes cleanly from
  `git log` + this doc's stage checkboxes (add checkboxes when work starts).
- `tests/test_ide_mixins_resolve.py`-style AST import-resolution scanning is
  worth running against `extensions/thymio/*.py` specifically once the move
  is done — the File-2 refactor's own landmine (a moved method silently
  dropping an import, caught only by a broad exception handler upstream) is
  exactly the failure mode a ~9,300-line multi-file relocation is most at
  risk of.
- Stage C/D/E need at least one **real two-window** manual check (playground
  editor open + a Thymio-bearing sample run through Test Game) before
  calling the arc done — this class of move has, historically in this repo,
  produced silent-until-clicked regressions (the `self.tr(f"...")` dead
  strings, the `self.ide` context bug) that only a live run surfaces.

## Risks and landmines to carry in

- **Pre-existing order-dependent test flake, not ours** (seen during 0.2,
  reproduced on clean HEAD): running `tests/test_raycast_view.py` *before*
  `tests/test_multiplayer_lan_ghosts.py` in one process fails
  `TestNamedInput::test_default_inputs_are_bound` with `KeyError:
  'input_binds'`; each file passes alone. Something raycast_view leaves in
  process-global hook/plugin state that the ghosts test assumes fresh. Don't
  chase it as a Stage-0 regression; re-run the ghosts file alone.

- **Pre-existing Qt native crash across a long chain of IDE-constructing
  tests, not ours** (found during C1, reproduced identically on clean
  Stage-B3 HEAD by stashing C1 and re-running the same file list). Running
  enough test files that each construct a real `PyGameMakerIDE()` in one
  pytest process — 15+ files deep, e.g. the combined
  `test_asset_trash.py` + `test_asset_type_registry.py` +
  `test_extension_action_i18n.py`, or separately
  `...+ test_extension_ui_translations.py` — sometimes crashes the whole
  process with `Windows fatal exception: access violation` inside
  `core/ide_window.py`'s `changeEvent`, called from `pytestqt.plugin.
  _process_events` during `pytest_runtest_setup`. Reads as a dangling/
  already-destroyed `QMainWindow` still receiving a queued Qt event from a
  prior test's window that wasn't torn down before the next test's `QApplication.
  processEvents()` ran. Non-deterministic — the exact same file combo
  sometimes crashes and sometimes instead produces ordinary (real,
  pre-existing, unrelated) i18n-resolution failures instead, consistent with
  reading unreliable freed memory rather than a logic bug. **Don't chase
  it as a Stage-C regression and don't try to fix the underlying window
  leak here** — it's out of scope for this plan and was confirmed
  pre-existing. Workaround used for this stage's gate: split a long
  IDE-window-heavy file list into sub-batches of ~4 files each; every
  sub-batch of the full 48-file Stage-C1 gate passed clean (388 passed, 0
  failed) run this way. If a future stage's gate hits the same crash,
  split further rather than treating it as a real failure — but it may be
  worth its own audit finding at some point (a real window leak, most
  likely a floated/detached editor or a test's `PyGameMakerIDE()` missing
  `deleteLater()` + an event-loop pump before the next test builds another).

- **Translation contexts.** `QObject.tr()` resolves its context from the
  *concrete runtime class* (verified for PySide6 6.9, documented in
  `dialogs/_block_config_dialog_base.py`'s own docstring and repeated
  throughout CLAUDE.md's i18n session notes). Moving `ThymioConfigDialog`
  into `extensions/thymio/dialogs/` **does not** break its `.tr()` calls —
  they still resolve under the class's own name — but any `self.tr()` call
  that got *hoisted* into a new shared helper during the move needs the same
  care the base-class-extraction rule already documents. Don't discover this
  the hard way like the `self.ide` and `self.tr(f"...")` bugs did.
- **`.trash`/zip-export exclusion.** If Stage 0.4's asset-type registry
  changes how playgrounds are discovered for save, double check
  `utils/project_compression.py`'s exclusion list and the rollback-snapshot
  allowlist (`_snapshot_for_rollback`) still cover the (possibly relocated)
  playgrounds directory — both were hardened for exactly this class of gap
  before (2026-08-09 Trash session note).
- **`plugin_loader` load order.** "Names are first-come... core wins over
  plugins, plugins win over extensions." Nothing here should collide, but
  verify no Thymio action name already exists as a core action before Stage
  A lands (the historical `f85e1ec`/`1ae8fbd` audio-actions shadowing bug is
  exactly this failure mode).
- **Frozen/export builds.** `plugin_loader` must resolve `extensions/` at
  `sys._MEIPASS` when the desktop build is frozen (`get_app_root()` — see
  the 2026-08-17 desktop-export session note). Thymio doesn't currently
  ship inside exported games (desktop-only, IDE-side feature), so this is
  likely moot, but confirm the desktop **IDE's own** Nuitka-frozen build
  (not game exports) still finds `extensions/thymio/` the same way it finds
  the other three extension folders today.

## Explicitly deferred / out of scope for this plan

- Splitting `widgets/thymio_playground.py` (1,339 lines) into smaller
  modules — do the relocation as a pure move first (Stage C3), split later
  if wanted.
- Redesigning the Blockly preset/category UX — Stage F only relocates data,
  it doesn't change how presets work.
- A "second robot platform" abstraction — the new seams (instance renderer,
  input handler, asset-type registry, IDE-chrome registries) are generic by
  name, but nothing here builds a shared "robot extension" base class ahead
  of a second real use case. Premature abstraction the codebase's own
  standing preference (CLAUDE.md's opening principles) argues against.

## Open decision: default `enabled` state

`extensions/README.md`'s own convention: `enabled: false` in the manifest
"ships the extension switched off — useful for something experimental that
people opt into." Two reasonable defaults once this plan is executed:

1. **`enabled: false`** — matches the 1.0 decision to keep the shipped
   product game-only by default; a teacher/robotics classroom flips it on
   via config, same one-line opt-in raycast/multiplayer already support.
2. **`enabled: true`** — reverses the 1.0 hiding decision outright, since
   the whole point of finishing this extraction is usually "bring the
   feature back."

This plan doesn't decide that — it's a product call, not an architecture
one — but **(1)** is the safer default to ship Stage G with, since it keeps
the current shipped behavior (Thymio invisible by default) exactly
unchanged even after the refactor lands, and flipping a manifest boolean
later is a one-line follow-up commit either way.
