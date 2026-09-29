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
C6. Config dialogs — `dialogs/thymio_config_dialog.py`,
    `thymio_action_selector.py`, `thymio_event_selector.py` →
    `extensions/thymio/dialogs/`. `dialogs/_block_config_dialog_base.py`
    **stays in core** (it's the genuinely shared base with
    `BlocklyConfigDialog`); only the Thymio subclass moves, importing the
    base from core same as `BlocklyConfigDialog` does.

### Stage D — external interop (self-contained, low risk)

D1. `export/Aseba/{aseba_exporter,playground_exporter}.py` →
    `extensions/thymio/export/aseba.py` (+ split if that reads better).
D2. `export/Roberta/roberta_exporter.py` + `importers/roberta_importer.py` →
    `extensions/thymio/export/roberta.py` / `.../import_roberta.py`.
D3. Wire the "Export Aseba (Thymio) code…" / "Import Open Roberta XML…" menu
    entries through the Stage-0.5 menu-contribution registry, replacing the
    `# [1.0]`-commented direct calls in `core/ide/_export.py` and
    `widgets/welcome_tab.py`.

### Stage E — the object-editor tab (needs seam 0.5; do this one last among the UI stages — it's the deepest coupling point)

E1. `editors/object_editor/thymio_events_panel.py` →
    `extensions/thymio/object_editor_panel.py`.
E2. Replace `ObjectEditorMain`'s direct `from .thymio_events_panel import
    ThymioEventsPanel` + hardcoded tab-add/signal-wiring with the Stage-0.5
    object-editor-panel registry, preserving the existing
    `Config.get('show_thymio_tab', ...)` visibility behavior exactly (this
    is the unit most likely to regress something subtle — the existing
    `test_object_events_panel_thymio_lossless_rewrite.py` and
    `test_thymio_else_preserved.py` are the regression gate; re-run them,
    don't just trust the diff).

### Stage F — Blockly toolbox (needs seam 0.6)

F1. Move the `"Thymio Events"`/`"Thymio Motors"`/… category dicts out of
    `config/blockly_config.py` into `extensions/thymio/blockly_categories.py`
    as `PLUGIN_BLOCK_CATEGORIES`; move the matching entries out of
    `config/blockly_translations.py` the same way (check first whether
    translations need to move per-language file or can stay centralized —
    follow whatever `config/blockly_translations.py`'s existing
    per-language structure already does for consistency, don't invent a new
    shape).
F2. Confirm `ThymioConfigDialog` (now `extensions/thymio/dialogs/...`) still
    resolves categories/presets correctly reading from the merged registry.

### Stage G — re-enable, remove the `# [1.0]` markers, tests/tooling sweep

G1. Grep the whole repo for `# \[1\.0\]` and confirm every remaining hit is
    non-Thymio (there may be other 1.0-deferred features under the same
    marker convention — don't touch those). Delete the Thymio-specific
    markers now that the code they guarded no longer lives in core to hide.
G2. Migrate the ~22 `test_thymio_*` + ~12 Roberta/Aseba + the Thymio-relevant
    subset of the ~16 `*playground*` test files to import from
    `extensions.thymio.*` (same "tests stay in `tests/`, only their imports
    change" pattern every prior extension move used — see the
    `PluginExecutor`-not-`ActionExecutor` dispatch-pattern landmine noted
    for the raycast move, item 1 in its landmines list: these tests likely
    need the same `load_all_plugins(ex)` + dispatch-through-`action_handlers`
    rewrite).
G3. Verify `tools/action_ref_i18n.py`, `tools/gen_preset_docs.py`,
    `scripts/gen_translation_ts.py` still produce correct output once
    Thymio actions load from `extensions/thymio/` instead of
    `actions/thymio_actions.py` — they already handle raycast/block_world/
    multiplayer this way (post-`load_all_plugins()` `ACTION_TYPES`), so this
    should be a verification pass, not new code.
G4. Write `extensions/thymio/README.md` and `extensions/thymio/extension.json`
    (see "Open decision" below for the `enabled` default).
G5. Full-repo grep sweep: zero `thymio`/`Thymio`/`aseba`/`Aseba`/`roberta`/
    `Roberta` references left in `core/`, `runtime/`, `editors/` (excluding
    `editors/object_editor/object_editor_main.py`'s now-generic panel-registry
    call site), `widgets/` (excluding the now-generic asset-tree/menu
    call sites), `dialogs/` (excluding `_block_config_dialog_base.py`'s
    still-accurate docstring mention), `config/` (excluding the
    `PLUGIN_BLOCK_CATEGORIES` merge point) — this is the "fully independent"
    bar this plan is named for, made checkable by a single command rather
    than a judgment call.

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
