# Post-1.0 refactor plan: splitting the four giant files

This document survives into the 1.1 phase. It captures the **why**, the
**when**, and a concrete **how** for breaking up the four files that
currently dominate pygm2's complexity surface. Companion read:
`ARCHITECTURE.md` (current shape).

## Status

**Re-verified 2026-09-05 — FILE 2 IS NOW COMPLETE.** File 1
(`object_events_panel.py`) is DONE (unchanged from below). **File 2
(`core/ide_window.py`): 5,316 → 955 LoC (-82%)**, fully split across a
skeleton + 9 mixins in `core/ide/` — `_samples.py`, `_edit_actions.py`,
`_dialogs.py`, `_test_game.py`, `_project_actions.py`, `_assets.py`,
`_editor_lifecycle.py`, `_export.py`, `_menu_builder.py` (the last
three all landed the same session; the `_assets.py` checkbox had gone
un-checked-off below despite being on disk and green the whole time — a
doc-lag, not a code gap, corrected in place). `PyGameMakerIDE` is now
`(Samples, EditActions, Dialogs, TestGame, ProjectActions, Assets,
EditorLifecycle, Export, MenuBuilder, QMainWindow)`. Two recurring
landmines this arc's later clusters kept hitting, both now well-precedented
for File 3/4: (1) source-string-scanning tests that `read_text()`
`ide_window.py` and slice out a method's body by name go silently empty
when the method moves — `_export.py`'s Progress entry has the first
instance and the fix pattern; (2) a moved method's own mixin file
missing an import it needs is an `AttributeError`-on-first-use bug, not
a load-time error — `tests/test_ide_mixins_resolve.py`'s AST-scan guard
(built during this arc specifically for this) caught one for real in
`_menu_builder.py` (`clear_recent_projects` needed `QMessageBox`) before
any manual testing was needed. **File 3 (`runtime/game_runner.py`) has
begun**: `GameSprite` → `runtime/sprite.py` (6,063 → 5,728 LoC), the
first of its five planned clusters — see its own Progress entry for the
"keep a re-export, don't force an import-path update" call this one
made (a genuine divergence from File 2's own precedent, reasoned through
there). File 4 (`runtime/action_executor.py`, 6,520 LoC) remains **not
started**.

**In progress (2026-09-03).** Sequencing step 2 (dead-code/logger
baseline) and **step 3 / File 1** (`object_events_panel.py` → an
`editors/object_editor/events/` mixin package, 2,111 → 800 LoC across
7 commits `e57d8d81`..`fd143b4c`) are **DONE**, batched full suite green
throughout. Next is step 4 — a stabilization pause (exercise the IDE)
before **File 2** (`core/ide_window.py`). Files 2–4 not started. See
`docs/PROJECT_STATUS.md` for the repo-wide picture and the per-file
"Progress" / sequencing notes below for detail.

**Re-verified 2026-09-03** — still not started (no DONE markers, no
`core/ide/`, `runtime/action_executor/`, `runtime/sprite.py` etc. on
disk), still the right plan. Line counts refreshed again below; all four
files grew a little more since the 2026-08-15 pass (object_events_panel
flat at 2,111; ide_window 5,295→5,316; game_runner 5,854→6,063;
action_executor 6,421→6,514). Two structural notes since 2026-08-15:
- **`runtime/game_runner.py` now carries the generic extension seam.**
  The raycast-2.5D and LAN-multiplayer extensions hang off
  `register_frame_update(...)` and the room-renderer `extension_hooks`
  registry that now live in `GameRunner` (~19 call sites). The raycast
  *renderer* itself was extracted to `extensions/raycast_2_5d/renderer.py`
  earlier, so File 3's `rendering.py` / `views.py` targets are now
  smaller than this doc's original estimate — but the hook *call sites*
  in the game loop are load-bearing for every extension and must move
  verbatim with whatever orchestration code surrounds them.
- **`export/Kivy/kivy_exporter.py` (5,689 LoC) is now the repo's 3rd
  largest file** but is deliberately **out of scope here** — it's a
  `.format()`-templated code-generator string, not a live-complexity
  hotspot, and splitting a template file has a different (lower) payoff.
  Noted so it doesn't get pulled in by "split the big files" scope creep.

**Re-verified 2026-08-15** (per the-then-current "everything remaining"
survey, since removed) — still not started, still the right plan, but
the line counts and two factual claims below were stale and are
corrected in place:
- All four files have grown further since this doc was written (see the
  updated table). The relative risk ordering is unchanged.
- **`runtime/collision_system.py` no longer exists.** It was deleted
  entirely on 2026-06-09 (see `CLAUDE.md`'s "Audit follow-through" note)
  — the dead `CollisionMixin` this doc's File 3 section and Companion
  Cleanup item 2 describe "deleting after building a replacement" is
  already gone. File 3's `collision.py` extraction target should be built
  fresh; there is no old file to delete alongside it anymore, and
  Companion Cleanup item 2 is moot.
- **Companion-cleanup finding, re-verified 2026-09-03 — the earlier
  "`particle_handlers.py` is fully dead" claim was WRONG** (classic
  audit-is-a-lead miss; corrected here rather than acted on). Actual
  picture from an introspection pass over `ActionExecutor`'s 127
  `execute_*_action` methods vs. every `*_HANDLERS` dict in
  `runtime/action_handlers/`:
  - `ActionExecutor.__init__`'s two-phase registration does skip any
    modular handler whose action name a `execute_*_action` method already
    covers — that part of the claim holds.
  - **Only `game_handlers.py` is fully shadowed**: its sole entry
    `sleep` → `handle_sleep` is covered by `execute_sleep_action`
    (`action_executor.py:2480`), which is the one that actually runs
    (`sleep` is used across `treasure` / `maze_4` / `plateforme_3`). So
    `game_handlers.py` is genuinely dead-by-shadowing and safe to delete.
  - `particle_handlers.py` registers `emitter_burst` / `emitter_stream`,
    and there is **no** `execute_emitter_*_action` — so those are *not*
    shadowed. They are almost certainly dead for a different reason
    (**no producer**: absent from `ACTION_TYPES`, every sample
    `project.json`/`objects/*.json`, the GMK importer, the Python code
    parser, and the Blockly config), but that is "unreachable", not
    "shadowed", and wants its own explicit sign-off before deletion.
  - Across the whole package, **75 modular-only action names** (reachable
    only via `action_handlers/`, not via an `execute_*` method). Of
    those, exactly **5 are reachable** — `comment`, `move_free`,
    `set_direction`, `set_speed` (all in `events/action_types.py` /
    Blockly config) and `play_sound` (plugin-owned, overridden at
    runtime by `plugins/audio_actions.py` via `register_custom_action`).
    The other **70 have zero producers anywhere** (same five-source check
    as above) and are strong deletion candidates — but per this doc's
    own methodology, each `*_handlers.py` file needs its own
    "no producer, confirmed" note in the commit body, not a blanket
    sweep. `base.py` stays regardless — `game_runner.py:3581` imports
    `snap_to_grid` from it directly.

## Why this is post-1.0

Three reasons it didn't happen before 1.0:

1. **Stability priority.** The user explicitly chose stability over
   features for the rc.11→1.0 window. Refactoring the runtime under a
   testing pass would introduce regressions on top of bugs still being
   surfaced (see commit `bc7725d`, `5ad9191`, `8ae3a7a`, `e3c0cc5`,
   `649084d`, `45dc3fe` from the rc.12 user-testing session).
2. **Bidirectional call graph in `ActionExecutor`.** Recorded in
   `CLAUDE.md`: *"B6 ActionExecutor split deferred to post-1.0 — 130
   execute_* methods / 4604 lines, bidirectional call graph with the
   registry. Don't attempt mid-audit."* Splitting in the middle of a
   call graph that runs in both directions risks subtle dispatch bugs.
3. **Behaviour-preservation methodology.** The earlier pre-1.0 audit
   established a hard requirement: every consolidation must be *proven
   behaviour-preserving against
   pre-refactor HEAD* via a throwaway offscreen-Qt harness, with the
   proof documented in the commit body. That's the right standard but
   it takes time and discipline; combining it with a release crunch is
   asking for cut corners.

## The four files

| File                                    | LoC (2026-09-03) | Risk to split | Order |
| --------------------------------------- | ------ | ------------- | ----- |
| `editors/object_editor/object_events_panel.py` | 2,111  | **Low**       | 1st   |
| `core/ide_window.py`                    | 5,316  | Medium        | 2nd   |
| `runtime/game_runner.py`                | 6,063  | Medium-high   | 3rd   |
| `runtime/action_executor.py`            | 6,514  | **High**      | 4th (last) |

Risk ranking weights three factors: how isolated the file's surface
area is, how much state is shared across the call sites, and how
visible a bug introduced by the split would be (UI bugs are visible;
runtime collision bugs hide).

---

## Mandatory methodology (re-read before starting any split)

Cribbed from the earlier pre-1.0 audit's own methodology and `CLAUDE.md`:

1. **Snapshot pre-refactor HEAD** with `git show HEAD:path` to a temp
   file before extracting anything.
2. **Build an offscreen-Qt harness** that exercises the old vs new
   implementations across a representative-to-exhaustive input matrix.
   For the runtime side, drive it through the existing samples
   (`maze_1`, `maze_2`, `maze_3`) — they collectively touch ~78 of the
   ~207 runtime actions.
3. **Diff observable state** between old and new — not just return
   values, also side effects on `instance.x/y/hspeed/vspeed`,
   `current_room.instances`, `assets_cache`, `is_dirty_flag`.
4. **Document the proof in the commit body.** "Verified against pre-
   refactor HEAD over the maze_1/2/3 sample suite, 0 state diffs across
   30 frames of each room."
5. **One cluster per commit on `main`.** No long-lived branches; each
   step ships independently so a regression is bisectable.
6. **Translation safety**: PySide6 `self.tr()` takes context from the
   *concrete runtime class*, so moving `tr()` calls into a shared
   base/mixin is runtime-safe. Keep divergent strings lexically in
   subclass hooks if extracting common UI scaffolding.
7. **`pyflakes` is not installed** — substitute `py_compile` + import
   sanity. Always run `py -3.12 -m pytest tests/ -q` (Windows) before
   committing.

If you can't satisfy any of these for a particular extraction, leave
the code where it is.

---

## File 1 — `editors/object_editor/object_events_panel.py` (2,111 LoC)

### Current shape

One class `ObjectEventsPanel(QWidget)` holds:
- Tree widget setup
- The massive `show_context_menu` (collision/mouse/keyboard/regular event branches)
- `add_event`, `add_sub_event`, `add_keyboard_event_with_selector`, `add_alarm_event`, `add_mouse_event_with_selector`, `add_collision_event_with_selector`
- `add_action_to_event`, `add_action_to_sub_event`, `add_action_to_collision_event`, `add_action_to_mouse_event`, `add_thymio_action_with_selector`
- `edit_action`, `remove_action`, `remove_event`, `remove_sub_event`
- `refresh_events_display` (the giant render method)
- Several legacy/duplicate `ACTION_ALIASES` map (see §"Consolidation"
  below — this dup lives here).

### Proposed split

```
editors/object_editor/events/
  __init__.py           re-export ObjectEventsPanel for backwards compat
  _panel.py             ObjectEventsPanel — shell + tree widget + signals
  _context_menu.py      build_context_menu(panel, item) — pure dispatch on item shape
  _event_crud.py        add_event / add_sub_event / remove_event / remove_sub_event
  _action_crud.py       add_action_to_event / add_action_to_sub_event /
                        add_action_to_collision_event / add_action_to_mouse_event /
                        edit_action / remove_action
  _render.py            refresh_events_display + AssetTreeItem-style helpers
```

### Why first

- Isolated. Only `ObjectEditor` instantiates this; nothing else
  touches its internals.
- No multithreading, no async. Pure Qt slot/signal flow.
- The recent `649084d` (`_CONTAINER_EVENT_HINTS` guard) and `7c0192c`
  (contextual sub-event adder) already shaped the action-add code into
  clean, separable functions. Most of the extraction is already done
  conceptually.

### Risk callouts

- `show_context_menu` switches on tree-item shape (parent vs no parent,
  string vs dict UserRole). Extract the dispatch table first into
  `_context_menu.py` as a pure function `build_menu_for(item) → QMenu`,
  *before* moving the per-branch handlers out. Otherwise you fragment
  the dispatch logic.
- `_CONTAINER_EVENT_HINTS` is a class attribute that both
  `add_action_to_event` and `show_context_menu` consult — keep it on
  the panel class (or move to a constants module) so both sides see
  the same table.

### Reconnaissance (2026-09-03) — do this before the first extraction commit

Mapped every consumer so the package move isn't a naive `git mv` + shim
(which would silently break `mock.patch` targets):

- **Production importers (only two):** `editors/object_editor/
  object_editor_main.py:25` (`from .object_events_panel import
  ObjectEventsPanel`) and `editors/object_editor/__init__.py:8`
  (re-export). Both must keep resolving.
- **`tests/test_extension_action_ui.py` patches module-internal names by
  string path** — `editors.object_editor.object_events_panel.get_action_type`,
  `.QMessageBox`, `.create_action_dialog` (5 `patch()` sites). A
  re-export shim patches the *shim's* binding, not the one the moved
  code actually calls, so those tests would pass-through-fail. The
  package-move commit **must** also repoint these five patch targets at
  wherever the code lands (`…events._panel.*`), or keep all three names
  bound in the old module.
- **Class attributes tests mutate directly — must stay on
  `ObjectEventsPanel`, not migrate to a helper module:**
  `_action_clipboard` (`test_action_copy_paste.py`, ~20 refs, incl.
  `ObjectEventsPanel._action_clipboard = None`), `_CONTAINER_EVENT_HINTS`
  (already flagged), and `_parse_execute_code_actions` is called as an
  unbound method on a fake host by `test_thymio_else_preserved.py:97`.
- **Module-level, `self`-free, cleanest leaf:** `ACTION_ALIASES` +
  the `get_action_type()` wrapper (lines 26–48). Safe to lift into
  `events/_action_lookup.py` — but it's one of the patched names above,
  so that move still touches `test_extension_action_ui.py`.
- **Relative imports inside the file** that shift a level under
  `events/`: `from .object_actions_formatter import …`,
  `from .python_code_parser import …` → `from ..`.

**Revised first commit:** package skeleton (`events/__init__.py` re-export
+ `_panel.py`) **plus** the `test_extension_action_ui.py` patch-path
update, in one commit — it can't be split. Prove HEAD-identity with an
offscreen-Qt harness that builds `ObjectEventsPanel()`, feeds a
representative `events_data` (collision + keyboard + alarm + mouse +
Thymio + a container event with sub-actions), and snapshots the rendered
`QTreeWidget` text/structure and the `show_context_menu` output for each
item shape — diff old vs new before committing.

### Progress

- [x] **Skeleton — `e57d8d81`.** `git mv object_events_panel.py →
  events/_panel.py`; `events/__init__.py` re-exports
  `ObjectEventsPanel`/`ACTION_ALIASES`/`get_action_type`;
  `object_events_panel.py` is now a compat shim; two relative imports
  went `.` → `..`; `test_extension_action_ui.py`'s 5 `patch()` paths
  repointed to `events._panel`. Harness dump identical except
  `__module__` (inherent to the move). Full suite 4247 passed.
- [x] **`show_context_menu` → `events/_context_menu.py` — `c445d2e4`.**
  175-line body moved verbatim (byte-identical after dedent + `self` →
  `panel` + docstring strip); `show_context_menu` is a 2-line lazy-import
  delegate. Batched full run 4246/4247 (the one miss,
  `test_raycast_view.py::…turn_a_corner…`, is a load-sensitive raycast
  smoke test — passes clean in isolation, cannot be touched by an
  object-editor change).
  All later clusters became **mixins** rather than free-function modules
  (verbatim move, no `self`→`panel` churn, no delegate stubs; `self.tr()`
  context stays `ObjectEventsPanel`). Each verified with: AST verbatim
  diff vs the prior commit + a method/tree-dump harness (identical) +
  targeted test files + a batched full gate (4247 passed every time).
- [x] **`_event_crud.py` — `ffea7b56`.** `EventCrudMixin`, 10 methods
  (`add_event`, `show_add_event_menu`, `add_sub_event`, the 4
  `add_*_with_selector`, `add_alarm_event`, `remove_selected_event`,
  `remove_sub_event`). 2111→1575.
- [x] **`_action_crud.py` + `_action_lookup.py` — `de6dc9a4`.**
  `ActionCrudMixin` (9 methods: `add_action_to_*`, `edit_action`,
  `remove_action`, `_locate_action_list`, `add_thymio_action_*`); the
  alias-aware `get_action_type` wrapper + `ACTION_ALIASES` lifted into
  `_action_lookup.py` as the single patch target for action resolution.
  `test_extension_action_ui.py` patch paths repointed
  (`_action_lookup` for render, `_action_crud` for `edit_action`).
  1575→1181.
- [x] **`_render.py` — `69897b9d`.** `RenderMixin` (`refresh_events_display`,
  `_set_action_item_text`, `_collect_expanded_keys`,
  `_restore_expanded_keys`). 1181→945.
- [x] **`_clipboard.py` — `8550820e`.** `ClipboardMixin` (12 copy/paste
  helpers). Verbatim except the two `ObjectEventsPanel._action_clipboard`
  refs → `type(self)._action_clipboard` (avoids a `_clipboard`↔`_panel`
  cycle; the `= None` class attr stays on `ObjectEventsPanel`). 945→800.
- [x] **Retired the shim — `fd143b4c`.** `object_editor_main.py` +
  `object_editor/__init__.py` + 4 test files moved onto
  `editors.object_editor.events`; `object_events_panel.py` deleted.
  Remaining `object_events_panel` mentions are stale comments only.
- Optional further (not blocking File 2): a `_reorder.py` mixin for the
  drag/drop + move-up/down cluster; fold `add_collision_event` /
  `remove_collision_event` / `remove_mouse_event` into `EventCrudMixin`.

**File 1 DONE (2026-09-03).** `ObjectEventsPanel` is now
`(EventCrudMixin, ActionCrudMixin, RenderMixin, ClipboardMixin, QWidget)`;
`_panel.py` is **800 lines**, down from 2,111 (**-62%**) — just the shell
(`__init__`/`setup_ui`/`setup_shortcuts`), drag/drop + reorder,
selection/double-click, load/save (`load_events_data`,
`_parse_execute_code_actions`, `get_events_data`), and the
collision/mouse-event helpers. New package modules: `_context_menu.py`
(195), `_event_crud.py` (392), `_action_crud.py` (~400),
`_action_lookup.py` (43), `_render.py` (~265), `_clipboard.py` (~190).
Batched full suite **4247 passed / 0 failed** after every one of the 7
commits. **Next: step 4 (stabilization pause — exercise the IDE) before
File 2.**

**Env note (machine-specific, see `CLAUDE.md` "Running tests"):** the
box this refactor work is being done on has only 8 GB RAM. Even the
`test_[a-g]*` / `[h-p]*` / `[q-z]*` batch split peaks ~2 000 tests per
process and has OOM-killed the desktop (VS Code + browser) mid-run, so
from File 2 onward the full-suite gate is **GitHub CI** (`tests.yml` runs
on every push to `main`); local runs per cluster are just the ~6–15
`ide_window` test files a change touches, plus the AST verbatim diff +
MRO check + offscreen-Qt harness. Not a project rule — on adequate RAM,
run the whole suite locally.

---

## File 2 — `core/ide_window.py` (5,316 LoC)

### Current shape

One class `PyGameMakerIDE(QMainWindow)` holds:
- UI scaffolding: `setup_ui`, `create_menu_bar`, `create_toolbar`, `create_main_widget`, `create_status_bar` (~500 LoC, mostly QAction wiring)
- Project lifecycle: `new_project`, `open_project`, `save_project`, `save_project_as`, `close_project`, `load_project`
- Asset CRUD wrappers around `ProjectManager.update_asset` etc.
- Editor lifecycle: `open_room_editor`, `open_object_editor`, `open_sprite_editor`, `open_playground_editor`, `open_script_editor`, `close_editor_tab`, `close_editor_by_name`, `float_editor`, `reattach_editor`, `_focus_detached_editor`, `_destroy_detached_editor`
- Test Game / Build subprocess management
- Editor → IDE signal handlers: `on_editor_save_requested`, `on_editor_close_requested`, `on_editor_data_modified`, `on_editor_data_modified`
- Recent projects + Welcome tab interaction
- Samples auto-promotion: `_is_samples_path`, `_promote_samples_to_working_copy`, `_strip_samples_from_recent_projects`
- Properties panel + asset tree integration
- Misc: import/export wrappers, config integration, dirty-state UI updates

### Proposed split

```
core/ide/
  __init__.py              re-export PyGameMakerIDE
  window.py                PyGameMakerIDE main class — pure shell
  _menu_builder.py         build_menu_bar(ide), build_toolbar(ide)
  _editor_lifecycle.py     open_*_editor / close_editor_* / float / reattach /
                           on_editor_save_requested / on_editor_data_modified
  _project_actions.py      new/open/save/close as thin delegators
  _samples.py              _is_samples_path / _promote_samples_to_working_copy /
                           _strip_samples_from_recent_projects
  _test_game.py            test_game + subprocess plumbing
```

### Why second

- Visible UI surface — any regression shows up immediately when the
  user clicks a menu item.
- Lots of inter-method coupling on `self` (the QMainWindow). Real
  extraction means converting many methods into free functions taking
  `ide: PyGameMakerIDE` as their first arg, or using mixins.
- Many of these methods are already thin wrappers; the heavy logic
  lives in `ProjectManager` / `AssetManager`. Extraction gains: the
  file stops being the catch-all for "anything top-level."

### Risk callouts

- **Signal connections live in `setup_connections`** — if you move
  handlers out, the connections still need to find them. Easiest path
  is a partial-class style: `from ._editor_lifecycle import *` adds
  methods to the class via module-level injection (or use mixins).
- The `auto_save_timer` is on `ProjectManager`, but several IDE methods
  also touch dirty state. Audit dirty-state mutations during the split.

### Reconnaissance (2026-09-03) — do this before the first extraction commit

File 1's mixin approach transfers, but File 2's consumer/patch surface is
**much** bigger — this is why the plan gates it behind step 4.

- **`PyGameMakerIDE(QMainWindow)`** is ~5,150 of the file's 5,316 lines,
  **~150 methods**. Two small helper classes at the top stay put:
  `ExportThread(QThread)` and `_ExportProgressDialog(QDialog)` (the latter
  is imported directly by `tests/test_export_progress_dialog.py`), plus
  module-level `_green_play_icon` / `_contrasting_icon_color` /
  `_tinted_standard_icon` (imported by `tests/test_ide_polish_fixes.py`).
- **Production importers (few):** `main.py:229/364`, `core/__init__.py:21`,
  and `__init__.py:45` (`importlib.import_module("main").PyGameMakerIDE`).
- **~40 test files** import `PyGameMakerIDE` from `core.ide_window` — all
  import the class, so a re-export from `core/ide_window.py` keeps them
  working (as the File 1 shim did). The real work is the patch targets.
- **`mock.patch("core.ide_window.<NAME>")` targets** used by method-level
  tests — these break the moment the method using `<NAME>` moves to a
  sibling module whose own `from … import <NAME>` binding the patch
  doesn't touch: `QMessageBox` (**many** sites, spread across export /
  import / dialog / project methods → will land in several mixins),
  `ExportThread`, `Config`, `logger`, `ObjectEditor`, `RoomEditor`,
  `SpriteEditor`, `os.startfile`. Each extraction commit must repoint the
  patch sites for the methods it moves (the File 1 `test_extension_
  action_ui.py` pattern, but bigger). `tests/test_ide_polish_fixes.py:310`
  does `import core.ide_window as ide_mod` and pokes module attributes —
  check what it touches before moving anything it relies on.
- **`create_menu_bar` (~220 lines) wires ~100 `QAction`s to `self.<slot>`
  methods** that will end up scattered across mixins. Because a mixin
  method resolves on the concrete `PyGameMakerIDE` via MRO,
  `self.export_game` etc. keep working from `create_menu_bar` wherever it
  lives — so the menu builder can move to `_menu_builder.py` (or stay)
  independently of the slots. But do the menu builder *last*, after the
  slot clusters, so a missed slot surfaces as an `AttributeError` at
  construction (loud) rather than mid-refactor.

**Cluster map (each → a `*Mixin` in `core/ide/_<name>.py`, verbatim moves):**
| Module | Rough method set | Notes |
| --- | --- | --- |
| `_export.py` | `export_*`, `build_game`/`build_and_run`, `_run_export_with_progress`, `_build_desktop`, `_launch_built_game`, `_ask_export_dir`, `_current_export_options` | biggest; needs its own `QMessageBox`/`ExportThread` imports; most patch-site churn |
| `_test_game.py` | `test_game`, `_run_project_json`, `test_object`, `_check_game_process`, `_drain_game_stderr`, `stop_game`, `debug_game`, `_show_validation_warnings` | subprocess plumbing; `QTimer` poll |
| `_assets.py` | `import_*`, `create_object/room/script/font/asset`, `create_asset_with_data`, `on_asset_renamed/deleted/imported/selected/double_clicked`, `find_renamed_asset`, `_refresh_*` | `ObjectEditor`/`RoomEditor`/`SpriteEditor` patch targets live here |
| `_project_actions.py` | `new/open/open_recent/load/save/save_as/close_project`, `project_settings`, `on_project_loaded/saved`, `add_to_recent_projects`, `_require_open_project`, `ensure_project_loaded`, `_show_load_failure_message`, `_warn_missing_extensions` | |
| `_editor_lifecycle.py` | `open_*_editor` (8), `close_editor_*`, `float_editor`, `reattach_editor`, `_focus/_destroy_detached_editor`, `on_editor_save/close/modified_requested`, `_flush/_iter_open_editors`, `_active_editor`, `_editor_key`/`_open_key`/`_forget_open_editor`/`_canonical_category`, `toggle/set_window_mode` | largest by count |
| `_edit_actions.py` | `undo/redo/cut/copy/paste/duplicate`, `find`, `find_replace`, `_show_find_dialog`, `_find_target_text_edit` | |
| `_samples.py` | `_samples_dir`, `_is_samples_path`, `_promote_samples_to_working_copy`, `_strip_samples_from_recent_projects` | smallest — good first cluster |
| `_dialogs.py` | `preferences`, `configure_blockly/thymio`, `about`, `show_documentation`/`show_online_documentation`, `show_trash/unused_assets/orphaned_files_dialog`, `clean_project`, `validate_project`, `show_thymio_*` | |
| `_menu_builder.py` | `create_menu_bar`, `create_language_menu`, `create_toolbar`, `create_action`, `create_status_bar`, `update_recent_projects_menu`, `clear_recent_projects` | **last** |
| `_panel.py` (`window.py`) | `__init__`, `setup_ui`, `create_main_widget`, `setup_connections`, `closeEvent`/`changeEvent`, `update_ui_state`, `update_window_title`, tab handlers, right-panel collapse | the shell — stays |

**Skeleton — done (`<commit>`).** Unlike File 1, `core/ide_window.py` is
**not** moved to a shim: the ~30 `mock.patch("core.ide_window.<NAME>")`
sites (see the patch-target list above) would all need repointing in the
skeleton commit for zero functional gain, and would then need repointing
*again* per cluster as their methods move. So the skeleton is just an
empty `core/ide/__init__.py` (imports nothing — `core/ide_window.py`
imports `core/ide/_<name>` at class-definition time, so a re-export in
`__init__` would be circular). `core/ide_window.py` stays as the
authoritative module and shrinks in place = the plan's `window.py`.

**Per cluster:** new `core/ide/_<name>.py` with `<Name>Mixin` (verbatim
method moves), add it to `class PyGameMakerIDE(...)`, delete the bodies
from `ide_window.py`, repoint *that cluster's* patch sites
(`core.ide_window.X` → `core.ide._<name>.X`), verify with AST verbatim
diff + MRO check + targeted `ide_window` test files. Full-suite gate =
CI (`tests.yml` on push) — see the env note above.

**Gotcha found in cluster 1:** a moved method that did
`Path(__file__).resolve().parent.parent` (relying on `ide_window.py`
being exactly one dir under the repo root) resolves one level short from
`core/ide/_<name>.py`. Grep each cluster for `__file__` before moving and
bump to `.parents[2]`. Bit `_samples_dir` (`bebb7ddf`, regression from
`9a189e6b` — no test asserted the path, so the suite stayed green) and
`show_tutorials` (caught pre-push in `194e72ff`).

### Progress

- [x] **Skeleton — `b01e663b`.** `core/ide/__init__.py` (empty). No file
  move / shim (see above).
- [x] **`_samples.py` — `9a189e6b`** (+ path fix `bebb7ddf`). `SamplesMixin`,
  4 methods. No patch targets.
- [x] **`_edit_actions.py` — `505373ba`.** `EditActionsMixin`, 11 methods
  (`_active_editor`, undo/redo/cut/copy/paste/duplicate, find family). No
  patch targets.
- [x] **`_dialogs.py` — `194e72ff`.** `DialogsMixin`, 21 methods
  (preferences, configure_*, the Thymio show_*, validate_project, the
  trash/unused/orphaned/clean dialogs, docs/tutorials/about).
  `QMessageBox` patch sites repointed in 4 test files; `show_tutorials`
  path-depth adjusted.
- [x] **`_test_game.py` — `ca87d744`.** `TestGameMixin`, 8 methods.
  `logger`×2 + `QMessageBox`×3 patch targets repointed. `_run_project_json`
  `game_script` path bumped to `.parents[2]`.
- [x] **`_project_actions.py` — `a18c32e6`.** `ProjectActionsMixin`, 16
  methods (fully verbatim), `ide_window.py` → 3,625. **Fresh-look boundary
  calls:** `_require_open_project` + `_ask_export_dir` have callers *only*
  in the export methods → they go to `_export`, not here.
  `update_recent_projects_menu` / `clear_recent_projects` → `_menu_builder`.
  `update_window_title` / `_on_dirty_changed` / `closeEvent` → stay in the
  shell (`closeEvent` calls `self.save_project()` and uses its own
  `Config`/`QMessageBox`, so `test_modified_editor_preservation`'s patch
  sites were left as `core.ide_window.*`). Repointed:
  `test_recent_zip_reopen` (Config×3 + QMessageBox×3, `load_project`),
  `test_project_format_guard` (QMessageBox×2, `_show_load_failure_message`).
- [x] **`_assets.py` — `39411b79`.** `AssetsMixin`, 22 methods (fully
  verbatim): the 4 `import_*_package/file` methods, the 4
  `import_sprite/sound/background/asset`, `on_asset_renamed/_deleted/
  _selected/_imported/_double_clicked`, `find_renamed_asset`,
  `_refresh_blockly_asset_lists`, `_refresh_room_editor_objects`, and the
  6 `create_*`/`create_asset_with_data`. No patch targets moved —
  `ObjectEditor` appears here only as a `__class__.__name__` string; the
  real `RoomEditor`/`ObjectEditor`/`SpriteEditor` patch sites in
  `test_reopen_modified_editor`/`test_open_editors_composite_key` belong
  to `open_*_editor` (→ `_editor_lifecycle`, next).
  `test_asset_type_editors`'s source-grep helper widened to scan the
  whole `core/ide/` package, not just `ide_window.py`.
- [x] **`_editor_lifecycle.py`.** `EditorLifecycleMixin`, 26 methods (fully
  verbatim, AST-diff-clean against pre-refactor HEAD): the 8
  `open_*_editor` (room/playground/object/sprite/script/sound/background/
  font), `close_editor_tab`/`close_editor_by_name`, `float_editor`/
  `reattach_editor`/`_on_detached_reattach_requested`/
  `_focus_detached_editor`/`_destroy_detached_editor`,
  `on_editor_save_requested`/`on_editor_close_requested`/
  `on_editor_data_modified`, `_flush_open_editors`, `_editor_key`/
  `_open_key`/`_forget_open_editor`/`_canonical_category`,
  `toggle_window_mode`/`set_window_mode`/
  `_update_window_mode_action_label`. `ide_window.py`: 3,009 → **2,164**
  (-59% from the 5,316 File-2 start). `PyGameMakerIDE` is now `(Samples,
  EditActions, Dialogs, TestGame, ProjectActions, Assets,
  EditorLifecycle, QMainWindow)`. **Fresh-look boundary calls** (same
  discipline as `_project_actions`'s): `on_room_editor_activated`/
  `on_object_editor_activated` and the right-panel/properties helpers
  (`clear_properties_contexts`/`_collapse_right_panel`/
  `_restore_right_panel`) stay in the shell — despite sitting physically
  inside this method range, they're a properties-panel-sync concern
  driven mainly by `on_tab_changed`, not editor-open/close/float
  tracking; `_iter_open_editors` and `_add_welcome_tab` also stay
  (shared with `_assets`/`_test_game`/general UI setup, per the
  `_assets` commit's own precedent). Patch targets moved:
  `core.ide_window.RoomEditor`/`ObjectEditor`/`SpriteEditor` →
  `core.ide._editor_lifecycle.*` in `test_reopen_modified_editor.py`
  (4 sites) and `test_open_editors_composite_key.py` (1 site) — these
  three editor classes are constructed directly inside
  `open_room_editor`/`open_object_editor`/`open_sprite_editor`; the
  other five `open_*_editor` methods import their editor class locally
  and needed no patch-target change. `QMessageBox`/`Config` are used
  throughout but no test patches either for a method in this cluster
  (the three existing `core.ide_window.QMessageBox` patch sites all
  belong to `closeEvent`/`toggle_auto_save`/`_run_export_with_progress`,
  none of which moved) — confirmed by an exhaustive search across
  `tests/` for every method name in this cluster before editing, not
  assumed.
  Verified: AST-structural diff of all 26 methods against `git show
  HEAD:core/ide_window.py` is clean; MRO resolves all 26 (+ the
  now-8-mixin chain); the two directly-affected test files plus 6
  peripheral ones referencing these method names all green; full suite
  gated.
- [x] **`_export.py` — biggest, done.** `ExportMixin`, 19 methods +
  2 module-level classes (fully verbatim, AST-diff-clean against
  pre-refactor HEAD): `export_html5`/`export_kivy`/`export_project`/
  `export_project_zip` (thin menu-entry delegates, physically separate
  from the rest of the cluster but the same concern —
  `export_project`/`export_project_zip` are literal `export_*` matches
  the plan's own wildcard already named), `export_game`,
  `_current_export_options`, the five `export_windows_exe`/
  `_linux_binary`/`_macos_app`/`_android_apk`/`_ios_app`, `export_aseba_code`,
  `build_game`/`build_and_run`, `_require_open_project`, `_ask_export_dir`,
  `_run_export_with_progress`, `_build_desktop`, `_launch_built_game`, plus
  the module-level `ExportThread(QThread)` and `_ExportProgressDialog(QDialog)`
  helper classes `_run_export_with_progress` builds on (used nowhere else,
  so they move with it). `ide_window.py`: 2,164 → **1,504** (-72% from the
  5,316 File-2 start). `PyGameMakerIDE` is now `(Samples, EditActions,
  Dialogs, TestGame, ProjectActions, Assets, EditorLifecycle, Export,
  QMainWindow)`. Dead imports removed from `ide_window.py`: `os`,
  `sys`, `subprocess`, `QThread`, `QDialog`, `QFileDialog`, `QPushButton`,
  `QHBoxLayout` — all confirmed zero remaining real usages (not just
  "moved code doesn't need it"; checked the whole file, since e.g.
  `QProgressBar` looked similarly export-only but turned out to have a
  second, unrelated use in `create_status_bar`).
  **Patch targets moved** (found by an exhaustive `tests/` search across
  every method/class name in this cluster before editing, matching the
  `_editor_lifecycle` discipline): `core.ide_window.QMessageBox` /
  `.ExportThread` / `.os.startfile` → `core.ide._export.*` in
  `test_build_game.py` (3 sites); `from core.ide_window import
  _ExportProgressDialog` → `core.ide._export` in
  `test_export_progress_dialog.py`. **A second, previously-unseen class
  of breakage this cluster hit for the first time**: four tests
  (`test_export_dialog_routing.py` ×2, `test_export_dialog_options.py`,
  `test_export_registry.py`) don't patch anything — they `read_text()`
  `core/ide_window.py`'s raw source and string-search inside it (e.g.
  slicing out `export_game`'s own body to assert it never routes on
  translated combo text — the M13 regression the test exists to catch).
  Moving the methods silently emptied that slice, so these failed with
  `IndexError`/false assertion misses rather than an import error —
  caught by the full targeted-file run, not the AST/MRO checks (which
  only prove the method CONTENT is intact, not that every test locates
  it correctly). Fixed by repointing each `read_text()` call at
  `core/ide/_export.py`, matching `test_asset_type_editors.py`'s own
  established fix for this exact class of test one cluster earlier.
  Verified: AST-structural diff of all 19 methods + 2 classes against
  `git show HEAD:core/ide_window.py` is clean; MRO resolves all 19
  methods through the now-9-mixin chain; every test file referencing a
  moved name (11 files across the two failure classes above) green;
  full suite gated.
- [x] **`_menu_builder.py` — last, done. FILE 2 IS NOW COMPLETE.**
  `MenuBuilderMixin`, 7 methods + 3 module-level icon-helper functions
  (fully verbatim, AST-diff-clean against pre-refactor HEAD):
  `create_menu_bar`/`create_language_menu` (contiguous — the whole menu
  bar plus its Language submenu), `create_toolbar`, `create_status_bar`,
  `create_action` (the generic `QAction` builder every menu/toolbar item
  above calls), `update_recent_projects_menu`/`clear_recent_projects`,
  plus `_green_play_icon`/`_contrasting_icon_color`/`_tinted_standard_icon`
  (used only by `create_toolbar`/`create_action`, moved with them — same
  precedent as `_export.py`'s `ExportThread`/`_ExportProgressDialog`).
  Done genuinely last, per this doc's own sequencing rationale: this
  cluster calls `self.<name>` for nearly every action on every other
  mixin (`self.new_project`, `self.export_game`, `self.build_and_run`,
  `self.test_game`, ...) — had any earlier extraction dropped a method,
  it would have surfaced here as a loud `AttributeError` at menu
  construction, not stayed silently masked.
  `ide_window.py`: 1,504 → **955** (-82% from the 5,316 File-2 start).
  `PyGameMakerIDE` is now `(Samples, EditActions, Dialogs, TestGame,
  ProjectActions, Assets, EditorLifecycle, Export, MenuBuilder,
  QMainWindow)` — 9 extracted mixins plus the shell.
  Dead imports removed: `QProgressBar`/`QLabel`/`QStyle`/`QSize`
  (confirmed zero remaining real usage — all were exclusively used by
  the methods/functions that just moved) plus, found in the same sweep,
  two imports that were **already** dead before this cluster
  (`QApplication`, `QInputDialog` — leftover from an earlier extraction
  that nobody had cleaned up; removed here since the audit was already
  in progress, not because this cluster caused them).
  **No patch-target moves needed** — confirmed by searching `tests/` for
  every method/function name in this cluster before editing; nothing
  mocks any of it. **One real bug this cluster's own new guard-test run
  caught before it could ship**: `clear_recent_projects` uses
  `QMessageBox.question`/`.Yes`/`.No`, and the first draft's header
  simply forgot to import `QMessageBox` into `_menu_builder.py` — an
  `AttributeError`-on-first-use bug that `tests/test_ide_mixins_resolve.py`
  (the AST-scan guard built specifically for this recurring class of
  mistake, see its own docstring) caught immediately as an unresolved
  name, before any manual testing was needed. Also found (source-scan
  class, not patch-target class, matching `_export.py`'s discovery):
  `test_ide_polish_fixes.py` directly imports `_green_play_icon`/
  `_contrasting_icon_color`/`_tinted_standard_icon` from `core.ide_window`
  (not a `mock.patch`, a real `from ... import`) — repointed to
  `core.ide._menu_builder`.
  Verified: AST-structural diff of all 7 methods + 3 functions against
  `git show HEAD:core/ide_window.py` is clean; MRO resolves all 7
  methods through the now-10-mixin chain; every test file referencing a
  moved name green; full suite gated.

`ide_window.py`: 5,316 → 3,625 after `_project_actions` → 3,009 after
`_assets` → 2,164 after `_editor_lifecycle` → 1,504 after `_export` →
**955** after `_menu_builder` (**-82%**). `PyGameMakerIDE` is now
`(Samples, EditActions, Dialogs, TestGame, ProjectActions, Assets,
EditorLifecycle, Export, MenuBuilder, QMainWindow)`. **File 2 is
complete** — the remaining shell is genuinely just the window's own
lifecycle and cross-cutting glue: `__init__`/`setup_ui`/
`setup_connections`, `create_main_widget`/`create_center_panel_with_editors`,
tab/right-panel handlers (`on_tab_changed`, `on_room_editor_activated`/
`on_object_editor_activated`, `clear_properties_contexts`/
`_collapse_right_panel`/`_restore_right_panel`), `update_ui_state`/
`update_window_title`, `_on_dirty_changed`, `closeEvent`/`changeEvent`,
`_iter_open_editors`/`_add_welcome_tab` (shared across several mixins,
correctly left in the shell throughout this arc), `restore_geometry`,
`safe_disconnect_signal`, `update_status`,
`refresh_open_object_editors`/`refresh_object_sprites`, `change_language`,
and the small auto-save toggles (`toggle_auto_save*` /
`show_auto_save_settings`). None of these are natural candidates for a
tenth cluster — they're either genuinely `__init__`-adjacent, or shared
by enough of the extracted mixins that splitting them out would just
reintroduce a cross-file coupling this arc spent its whole effort
removing.

---

## File 3 — `runtime/game_runner.py` (6,063 LoC)

### Current shape

Four classes:
- **`GameSprite`** (~400 LoC) — image loading, mask building, frame
  retrieval. Mostly self-contained.
- **`GameInstance`** (~500 LoC) — per-instance state: position, speed,
  alarms, keys_pressed, sprite ref, step() method. Touches sprite,
  action_executor, and the room's spatial grid.
- **`GameRoom`** (~150 LoC) — instance list, spatial grid, collision
  listened-types cache. Self-contained.
- **`GameRunner`** (~3,500 LoC) — orchestration: load, sprites, rooms,
  game loop, collision detection methods (overriding `CollisionMixin`),
  rendering, input dispatch, Thymio integration, view/camera system,
  outside_room events, end-of-game flow, restart logic.

### Proposed split

```
runtime/
  sprite.py               GameSprite (already nearly self-contained)
  instance.py             GameInstance (mostly data, light coupling)
  room.py                 GameRoom + spatial grid helpers
  input_handler.py        handle_keyboard_press / handle_keyboard_release /
                          handle_mouse_press / handle_mouse_release /
                          handle_mouse_motion / _process_held_keys
                          (already partially exists — empty shell)
  collision.py            Replace CollisionMixin (currently dead — see §6
                          of ARCHITECTURE.md) with a working module that
                          GameRunner actually delegates to.
                          Methods: check_movement_collision_with_blocker,
                          detect_collisions_for_instance, instances_overlap,
                          check_collision_at_position, _precise_refine,
                          _resolve_collision_event, _object_matches_target,
                          separate_overlapping_instances, push_back_instance.
  rendering.py            render() + draw queue processing + view offset math
  views.py                update_views + view/camera Phase 2b-2c code
  game_runner.py          GameRunner — orchestration only (game loop,
                          load_project_data_only, find_starting_room,
                          run_game_loop, change_room, restart_room, etc.)
```

### Why third

- The runtime is **less visible** than the IDE — a bug here may hide
  for frames before manifesting. Pure-Python testability is harder
  (needs the pygame display + a project to drive). Compensate with the
  offscreen-Qt + sample-driven harness from the methodology section.
- `GameSprite` and `GameRoom` are easy. `GameInstance` is medium.
  `collision.py` is the load-bearing part — wire the long-dead
  `CollisionMixin` correctly this time.

### Risk callouts

- **`CollisionMixin` no longer exists at all** (see the 2026-08-15 Status
  update above — `runtime/collision_system.py` was deleted 2026-06-09).
  There is nothing to delete or revive; `collision.py` should be written
  fresh, with the collision *methods themselves* (still live on
  `GameRunner` today, never moved) as the extraction source instead.
- The recent collision invariants (commits `8ae3a7a`, `e3c0cc5`) need
  to be **carried into the new module verbatim** with the comment
  blocks intact. The "AABB-only for movement blocking" comment and the
  "parent-chain match symmetry" comment are load-bearing and survived
  multiple bug-hunts.
- `_process_held_keys` has a subtle `is_grid_moving` check that depends
  on `instance.intended_x/y == instance.x/y`. The post-collision
  re-sync at the end of `update()` makes this invariant hold. Both
  pieces must move together — extract `update()` and
  `_process_held_keys` in the same commit.

### Progress

- [x] **`sprite.py` — done (2026-09-05).** `GameSprite` moved fully
  verbatim (AST-diff-clean against pre-refactor HEAD) to `runtime/sprite.py`
  — confirmed genuinely self-contained first: no reference to
  `GameInstance`/`GameRoom`/`GameRunner` or to any of `game_runner.py`'s
  module-level helpers/constants (`resolve_parent_inheritance`,
  `_CHILD_ONLY_OBJECT_PROPS`, `CAPTION_TRANSLATIONS`, etc.), and
  instantiated in exactly one place in the whole codebase
  (`GameRunner`'s sprite-loading code). `game_runner.py`: 6,063 → 5,728.
  **Deliberately kept a re-export** (`from runtime.sprite import
  GameSprite` near the top of `game_runner.py`) rather than requiring
  every caller to update its import path — unlike the `core/ide/` mixin
  extractions (internal inheritance pieces of one class, no shim by
  design), this is an ordinary module-level class relocation with real
  external call sites: **11+ tests** do
  `from runtime.game_runner import GameSprite` directly, and a plain
  re-export is the standard, lowest-churn way to move a class to its
  own module in Python. Confirmed by running the full suite with **zero
  test changes** — every existing import path kept resolving to the
  identical class object (`is` check passed). Dead imports removed from
  `game_runner.py`: `from PIL import Image` (was GIF-loading-only,
  confirmed zero remaining usage).
  Verified: AST-structural diff of the whole class against
  `git show HEAD:runtime/game_runner.py` is clean; `runtime.game_runner.
  GameSprite is runtime.sprite.GameSprite` (literally the same object,
  not just equivalent); full suite gated (one isolated re-run needed —
  `test_raycast_view.py`'s `TestRaycast1SampleSmoke`/`TestFloorCasting`
  flaked under CPU contention from a parallel targeted-file run, exactly
  CLAUDE.md's documented timing-sensitivity caveat for that file, not a
  regression — confirmed by re-running that file alone, 51/51 green).
- [ ] `room.py` — `GameRoom` + spatial grid helpers. Next (per the
  plan's own "easy" ordering).
- [ ] `instance.py` — `GameInstance`. Medium risk (see the
  `_process_held_keys`/`update()` coupling risk callout above).
- [ ] `input_handler.py`, `collision.py`, `rendering.py`, `views.py`,
  and the `game_runner.py` orchestration-only remainder — not started.

---

## File 4 — `runtime/action_executor.py` (6,514 LoC) — last and hardest

### Current shape

One class `ActionExecutor` with 130+ `execute_<X>_action` methods,
plus:
- `ACTION_ALIASES` map (~25 entries)
- Auto-registration of `execute_*_action` methods (init scan, ~30 LoC)
- Modular-handler integration via `runtime.action_handlers` package
- `execute_action`, `execute_action_list` (conditional-flow + skip_next),
  `execute_event`, `execute_collision_event`, `execute_collision_action_list`
- Per-action helpers: `_parse_value`, `_evaluate_expression`,
  `_handle_repeat_action`, `_find_matching_end_block`,
  `_dispatch_room_test`, `_room_neighbor_exists`
- Shared state: `self.game_runner`, `self._collision_other`,
  `self._collision_speeds`, `self._event_depth`,
  `self._deferred_create_events`

### Why hardest

- **Bidirectional call graph.** Actions call `execute_action_list`
  recursively (then/else_actions, repeat blocks). The dispatcher and
  the action methods reference each other through `self`.
- **Shared state on `self`.** Splitting into category modules means
  every extracted function needs the executor passed in, OR the
  category modules need to be subclasses/mixins. Mixins multiply the
  inheritance graph; passing the executor in changes every call site
  inside the action methods.
- **130 methods × representative input matrix** is a non-trivial test
  harness.

### Proposed split (one option — alternatives encouraged)

Mixin-based, because passing `executor` into every method would touch
~2000 call sites:

```
runtime/action_executor/
  __init__.py               re-export ActionExecutor
  _base.py                  ActionExecutor — registration, dispatch,
                            execute_action / execute_action_list /
                            execute_event / execute_collision_event,
                            shared state attrs
  _flow.py                  ConditionalFlowMixin — if_*, repeat, else,
                            start_block / end_block, _handle_repeat_action
  _movement.py              MovementMixin — start_moving_direction,
                            set_hspeed/vspeed, move_grid, jump_to_*,
                            snap_to_grid, set_speed, set_direction,
                            move_towards, bounce, reverse_*, etc.
  _drawing.py               DrawingMixin — draw_text, draw_rectangle,
                            draw_circle, draw_sprite, draw_score, etc.
  _score_lives_health.py    ScoreLivesHealthMixin
  _room_nav.py              RoomNavMixin — next_room, previous_room,
                            goto_room, restart_room, if_next_room_exists,
                            if_previous_room_exists, _room_neighbor_exists,
                            _dispatch_room_test
  _spawn.py                 SpawnMixin — create_instance, destroy,
                            change_instance, deferred create events
  _vars.py                  VarsMixin — set_variable, test_variable,
                            _parse_value, _evaluate_expression
  _alarms.py                AlarmsMixin — set_alarm, alarm event firing
  _misc.py                  Misc actions that don't fit a category
```

Each mixin inherits from `object`, defines its `execute_*_action`
methods, and gets composed in by `_base.py`:

```python
class ActionExecutor(
    ConditionalFlowMixin,
    MovementMixin,
    DrawingMixin,
    ScoreLivesHealthMixin,
    RoomNavMixin,
    SpawnMixin,
    VarsMixin,
    AlarmsMixin,
    MiscMixin,
):
    ...
```

The auto-registration scan in `__init__` walks `dir(self)` and picks up
all `execute_*_action` methods regardless of which mixin contributed
them — so it continues to work unchanged.

### Risk callouts

- The mixin inheritance order matters for any method-resolution-order
  collisions. None today, but the split should not introduce any.
- The `ACTION_ALIASES` class attribute on the base must stay on the
  base — mixins shouldn't define their own ALIASES dicts because that
  would split the aliasing surface.
- `_parse_value` and `_evaluate_expression` are called from *many*
  action methods — they're appropriate on the base (`_base.py`) or
  on a shared `_expression_eval.py` that all mixins import as a free
  function. Don't put them on `VarsMixin` only.
- The modular `runtime.action_handlers/` package already exists as a
  parallel handler source. Decide before starting: do new actions go
  into the mixin file or the modular package? Pick one direction and
  document it; the current parallel-systems situation is technical debt.

---

## Companion cleanup (not file splits, but adjacent)

These are smaller items worth tackling alongside the split work:

1. ~~**Consolidate `ACTION_ALIASES` to a single source of truth.**~~
   **Won't do — re-verified 2026-09-03, the three are NOT duplicates.**
   - `editors/object_editor/object_events_panel.py:ACTION_ALIASES` (8
     entries) feeds `get_action_type()` — it maps a legacy action name to
     whichever name the **UI ActionType registry** is keyed under, so the
     editor can show metadata for an action authored under an old name.
   - `runtime/action_executor.py:ActionExecutor.ACTION_ALIASES` (17
     entries) is consulted at **dispatch** time and maps a legacy name to
     the **handler-registry** key. For `goto_room` / `game_end` /
     `game_restart` it maps in the **opposite direction** from the panel's
     dict (the canonical name differs between the two registries), and it
     deliberately **omits `if_collision`** (there's a load-bearing comment:
     `if_collision` has its own immediate handler and must not alias to the
     deferred `if_collision_at`) — which the panel's dict *does* alias.
     Merging would break dispatch and that special-case.
   - `events/action_types.py:BLOCKLY_TO_ACTION_MAP` (~86 entries) is a
     Blockly-block-type → action-type table (`"move_set_hspeed"` →
     `"set_hspeed"`), not a legacy-alias map at all.
   Three different concerns, two opposite directions, one hard
   special-case. "Define once and import" would be a behaviour-changing
   regression, not a cleanup. Left as-is.
2. ~~Delete the dead `CollisionMixin`~~ **Already done** — `runtime/
   collision_system.py` was deleted entirely 2026-06-09. In its place:
   **tear down the near-dead `runtime/action_handlers/` package** so it
   is not carried into File 4's mixin structure. Verified sub-plan
   (see the corrected 2026-09-03 finding in the Status section for the
   full analysis):
   - [x] **Deleted `game_handlers.py`** (`ab39a009`) — its only entry
     (`sleep`) was fully shadowed by `execute_sleep_action`. Dispatch
     table byte-identical; suite 4247/0.
   - [x] **Per-file "no producer" deletion** (`af56b25d`) — removed 9
     modules whose every action name appears in **none** of:
     `events/action_types.py` `ACTION_TYPES`, any `samples/**/*.json`
     `"action"` field, `importers/gmk_converter.py`,
     `editors/object_editor/python_code_parser.py`,
     `config/blockly_config.py`, `export/**/*.{py,js}`, `tests/`:
     `instance_`, `draw_`, `score_`, `room_`, `timing_`, `particle_`,
     `extra_`, `info_`, `resource_handlers`. ~58 dead dispatch entries
     (live table 202 → 144). Two regression tests
     (`test_dead_placeholder_handlers_are_gone`) that *read* the
     now-deleted `extra_handlers.py` were updated to tolerate its
     absence.
   - [~] **`control_handlers.py` + `sound_handlers.py` — KEEP, not a
     clean delete.** Ran the rigorous check (ACTION_TYPES post
     `load_all_plugins()`, `events/conditional_editor.py`,
     `gmk_converter.py`, samples, Blockly, `python_code_parser.py`,
     `tests/`, `export/`). Result: none of these names is a *live* action
     in the desktop UI, **but the HTML5 engine (`export/HTML5/templates/
     engine.js`) still honours several as legacy aliases** —
     `case 'if_condition': case 'if_variable':` (three sites; `if_variable`
     is the pre-`if_condition` name for the same first-class conditional)
     and a real `case 'stop_all_sounds':` audio handler. On desktop
     `if_variable` currently routes to `control_handlers.handle_if_variable`,
     whose param shape (`operation`/`variable`) is the *old, incompatible*
     one — not `execute_if_condition_action`'s `condition_type` dispatch.
     So deleting these files is **not** pure dead-code removal: it's a
     decision about whether to keep loading pre-`if_condition` /
     legacy-audio-name projects on desktop, and if so whether to
     re-point those names at the modern handlers via `ACTION_ALIASES`
     (a behaviour change needing the offscreen-Qt proof). Deferred out
     of the teardown as its own scoped task. `play_sound` here is a
     shadowed fallback for the plugin-owned action — leave it regardless.
   - [ ] **Keep** the reachable modular-only actions — `comment`
     (`variable_handlers`), `move_free` / `set_direction` / `set_speed`
     (`movement_handlers`; in ACTION_TYPES + Blockly config). If a home
     file is otherwise emptied, fold these into an `execute_*_action`
     method rather than keeping a one-entry handler file alive.
   - [ ] **Keep `base.py`** — `game_runner.py:3581` imports `snap_to_grid`
     from it directly; that helper needs a new home (or stays) before
     `base.py` can go.
   - [ ] Once the package is empty of live handlers, delete Phase 2 of
     `_register_action_handlers` and the `runtime.action_handlers`
     import entirely — one final commit. **Blocked** on the
     `control_`/`sound_handlers` decision above; `movement_`/`variable_`
     still carry the reachable 4 (`comment` / `move_free` /
     `set_direction` / `set_speed`) which must be re-homed first.
     Package went from 14 handler modules to **5** (`base` + `movement`
     + `control` + `variable` + `sound`) — the mixin-structure risk this
     item was guarding against is largely defused already.
3. ~~**Audit-era `# DEBUG:` comments.**~~ **Done (`4875d734`)** — only
   3 remained (`asset_tree_widget.py`, `action_executor.py` ×2), each a
   redundant label directly above a legitimate `logger.debug(...)` call.
   Removed the label lines; logging unchanged.
4. ~~**`logger.info` emoji noise.**~~ **Done (`61001945`)** — 54
   emoji-prefixed info logs demoted to `debug` (runtime: `action_executor`
   ×23, `game_runner` ×18, `thymio` ×1; IDE: `project_manager`,
   `language_manager`, `ide_window`, `roberta_exporter`). Kept 9 genuine
   user-facing ones (`project_manager` save-success trio, `ide_window`
   "Save completed successfully" + preset-persist confirmations,
   `android_exporter` WSL detection). No test captures INFO-level logs.
5. ~~**Earlier audit §4 follow-ups.**~~ **Nothing to do** — retrieved the
   last `docs/CODE_AUDIT.md` (`git show ccc5e153~1:docs/CODE_AUDIT.md`).
   Its §4 is explicitly *"a guard list, not a task"* — a vulture
   false-positive list (the `execute_*_action` auto-registration via
   `dir(self)`, `_DRAW_HANDLERS` `getattr` dispatch, the plugin
   `importlib` loader, Qt event overrides, `gmk_parser` `_`-locals). §1–§3
   were all confirmed closed there. That guard list is worth re-reading
   before File 4 (it names the dynamic-dispatch patterns the mixin split
   must preserve), but it is not itself work.

---

## Suggested sequencing

1. Ship 1.0 on the current structure. **Done** (repo is at 1.2.0).
2. ~~Logger noise purge + dead-code deletion (1–2 days). Sets baseline.~~
   **Done 2026-09-03** (`ab39a009` `af56b25d` `4875d734` `2f145fb4`
   `61001945`) — 10 dead handler modules gone, `# DEBUG` labels gone, 54
   emoji `logger.info` demoted; `runtime/action_handlers/` down from 14
   modules to 5. Companion-cleanup §2's remaining piece (the
   `control_`/`sound_handlers` legacy-alias question) and the final
   Phase-2 removal are deferred as a scoped compat task, not a blocker
   for the file splits. Full suite green (4247 passed) at every step.
3. ~~File 1 (`object_events_panel.py`) — practice the methodology on the
   low-risk file.~~ **DONE 2026-09-03** — `_panel.py` 2,111 → 800 LoC
   across 7 commits (`e57d8d81`..`fd143b4c`), suite green throughout.
   See File 1's own "DONE" note above.
4. **Stabilization pause** — actually use the IDE for a week. If the
   split introduced regressions you missed in tests, this is when
   you'll find them.
5. File 2 (`ide_window.py`) — apply lessons from #3 (5–7 days).
6. Stabilization pause (1 week).
7. File 3 (`game_runner.py`) — the runtime needs the offscreen-Qt +
   samples harness from the methodology section. The hardest part is
   building the harness; once built, the splits are mechanical
   (7–10 days for split + harness).
8. Stabilization pause (2 weeks — runtime bugs hide).
9. File 4 (`action_executor.py`) — only after the harness from #7 is
   battle-tested. Plan 2–3 weeks; the bidirectional call graph means
   per-mixin testing is required, not just end-to-end.

Total: ~3 months of focused work, plus stabilization windows. Compress
at your risk.

---

## When to STOP a split mid-flight

Abort criteria:
- Test suite goes from green to red and you can't identify the cause
  within 30 minutes.
- A user-facing bug (or one of the samples) starts behaving differently
  than HEAD.
- The "diff observable state" check from the methodology shows
  divergence you didn't expect.
- You find yourself wanting to "just fix this small thing" inside a
  refactor commit. That's how regressions slip in.

Abort means: `git reset --hard HEAD~N`, take a break, write up what
you learned in this doc, try again later. Sunk-cost into a bad split
ships bugs.
