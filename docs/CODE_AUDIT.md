# Code Audit — Duplicate & Dead Code

**Date:** 2026-05-17
**Status:** Findings reference for pre-1.0 testing. §0, §1 fixed 2026-05-17.
§2 dead-symbol removal completed 2026-05-18 (65 symbols, ~800 lines). §3
platform-exporter cluster and the entire room-editor render cluster (colour,
placeholder, sprite resolution, background-image loader, icon abbreviation)
consolidated 2026-05-17/18; the Blockly/Thymio config-dialog cluster
consolidated 2026-05-19 onto a shared `BaseBlockConfigDialog`, and the
editor float/attach cluster the same day onto a shared
`FloatableEditorMixin`, and the tutorial path helper the same day onto a
shared `localized_tutorials_path` (the audit's paired `load_tutorial_list`
claim was inaccurate — see §3 note), and the pygame keymap onto a shared
`runtime/_keymap.py::pygame_key_name`, and the Thymio `event_to_regions`
map onto a shared `events.thymio_events.EVENT_TO_REGIONS`. §4 re-verified
still accurate (it is a non-actionable false-positive guard list, not a
task). **All §3 duplicate-code hazards are now resolved**, including the
once-deferred project_manager/game_runner/base_exporter loaders: their
byte-identical merge kernel is single-sourced in `utils/project_file_merge.py`
(2026-05-19, hot-path behaviour proven HEAD-identical), with the
divergent-by-design orchestration intentionally left. Both "Medium"
sub-items are now also resolved: the exe/linux/macos **dependency-error
strings** were a genuine duplicate → single-sourced to
`BaseKivyExporter._require_kivy_dependencies` (behaviour proven HEAD-identical);
the **key/mouse selector dialogs** are evidence-based won't-do (their only
byte-identical method is a one-line undriftable delegate, everything else
genuinely diverges — see §3). Nothing in §1–§3 remains open.

**Method:** pyflakes + vulture + symilar (pylint's duplicate detector) over 179 app
files (~80k LOC), then three verification passes that grep-checked every finding
against the whole repo (tests, JSON, HTML/JS bridges, dynamic dispatch) to strip
false positives. Raw tool output was saved to `/tmp/vulture_full.txt`,
`/tmp/pyflakes_full.txt`, `/tmp/symilar_full.txt` (regenerate as needed).
Overall duplicate density is low (~1.05%); issues are concentrated, not pervasive.

---

## 0. Latent bug found during the audit — ✅ FIXED 2026-05-17

- **Was:** `__init__.py:22` did `from .main import GameMakerIDE`, but `main.py`
  defines **`PyGameMakerIDE`** (and `main()`), not `GameMakerIDE`. Importing the
  project as a package raised `ImportError`; fixing only the name then hit
  `ModuleNotFoundError: No module named 'core'`, because the whole codebase uses
  top-level absolute imports that only resolve when run as `python main.py` with
  the project root on `sys.path`. The old eager relative import could never have
  worked.
- **Fix:** the eager import was replaced with a lazy PEP 562 `__getattr__` that
  puts the project root on `sys.path` (the same condition the script runtime
  relies on) only when the class is requested, plus a
  `GameMakerIDE = PyGameMakerIDE` backward-compatible alias.
- **Verified:** `import pygm2` now succeeds, is cheap, and side-effect-free
  (PySide6/Qt not loaded for metadata access); `pygm2.PyGameMakerIDE` and
  `pygm2.GameMakerIDE` both resolve to `core.ide_window.PyGameMakerIDE`; the
  `python main.py` runtime is unaffected (`main.py` untouched).

---

## 1. Orphaned modules — entire files never used — ✅ FIXED 2026-05-17

All 10 files below were deleted. Two package `__init__.py` files referenced
orphans and were corrected first: `widgets/asset_tree/__init__.py` was
repointed from the dead `tree_main` to the live `asset_tree_widget` (so
`from widgets.asset_tree import AssetTreeWidget` now yields the real class);
`widgets/__init__.py` had its `event_actions` import, the `EventActionsPanel`
alias, and the two related `__all__` entries removed. Verified: full app
import graph OK, `import pygm2` OK, whole source byte-compiles, no dangling
references. (Original findings retained below for reference.)

Each verified as never imported anywhere in the app (apparent "matches" were
same-named symbols in different files):

| Module | Note |
|---|---|
| `widgets/asset_tree/tree_main.py` | **872-line dead duplicate** of the live `widgets/asset_tree/asset_tree_widget.py`. `widgets/asset_tree/__init__.py` exports `AssetTreeWidget` from `tree_main`, but the app + tests import from `asset_tree_widget`. The two copies have already drifted. Biggest single cleanup target. |
| `runtime/room_preview.py` | Live preview is `utils/room_preview_generator.py`; this whole file (incl. `RoomPreviewRunner`) is dead. |
| `events/gm80_events.py` | 0 imports (the `gm80_action_dialog.py` matches are a different module). |
| `utils/asset_utils.py` | 0 imports (the 4 `asset_utils` imports target `widgets/asset_tree/asset_utils.py`). |
| `utils/file_utils.py` | 0 imports anywhere. |
| `utils/icon_helper.py` | 0 imports anywhere (re-verified). |
| `utils/logger.py` | 0 imports; the whole app uses `core.logger` (70 importers). |
| `export/Kivy/asset_bundler.py` | `AssetBundler` referenced only in docs. |
| `export/Kivy/action_converter.py` | `ActionConverter` never referenced in code. |
| `widgets/event_actions.py` | 27-line stub, 0 consumers. |

Also: `widgets/__init__.py`'s eager imports/aliases/`__getattr__` are never
triggered — every consumer imports submodules directly (e.g.
`widgets.thymio_playground`), so the package `__init__` machinery is effectively dead.

---

## 2. Individually dead symbols — ✅ DONE 2026-05-18

Re-verified every listed symbol against the *current* tree (a fresh repo-wide
pass — grep across py/json/js, dynamic-dispatch, Qt signals, tests; the audit
is a lead, not ground truth). Result: 65 symbols removed (~800 lines) via an
AST-precise tool + targeted edits for the `_zip_handler`/`modified_editors`
attributes and the duplicate `import_dialogs` aliases. `on_action_selected`
was **kept** — re-verification flagged it RISKY (a textbook Qt slot matching
existing `action_selected` signals), so it needs a human decision, not blind
removal. Orphaned imports left by the removals were cleaned; one real
regression (a re-exported `DEFAULT_GRID_SIZE`) was caught by the app-import
check and fixed at the true source. Validated: pyflakes clean, byte-compiles,
full app/handler import, **498 tests pass**. (Original list retained below.)

### Original list (verified, 0 refs repo-wide incl. tests/JSON)

High-confidence dead functions/methods/classes:

- `core/project_manager.py`: `get_is_dirty` (722), `get_original_zip_path` (1350),
  `is_auto_save_as_zip` (1359), and the `_zip_handler` attribute (only ever set to `None`).
- `core/asset_manager.py`: `get_all_assets` (697), `get_asset_info` (809),
  `validate_project_assets` (862), `clean_unused_files` (906).
- `core/language_manager.py`: `refresh_available_languages`, `get_current_language_name`,
  `load_current_language`, `get_translation_file_path(s)`.
- `core/ide_window.py:871` `modified_editors` (set, never read).
- `editors/base_editor.py`: `set_auto_save_delay` (343), `add_undo_command` (429),
  `set_read_only` (438), `get_project_asset_path` (444).
- `editors/object_editor/object_editor_main.py`: `ObjectChangeCommand` class (52) +
  the removed visual-node-canvas remnants (`add_node_to_canvas`, `on_visual_node_*`,
  `switch_to_standard_mode`, `on_action_selected`).
- `editors/room_editor/room_canvas.py`: singular instance ops superseded by plural
  versions (`select_instance`, `deselect_all`, `get_primary_selected_instance`,
  `copy/cut/duplicate_selected_instance`, `clear_sprite_cache`).
- `editors/room_undo_commands.py:137` `ChangeInstancePropertyCommand` (never instantiated).
- `runtime/action_handlers/base.py`: `parse_value`, `get_room_dimensions`,
  `get_instance_dimensions`, `point_distance`, `point_direction`, `is_on_grid`,
  `get_collision_speeds` (none imported by any handler).
- `runtime/game_runner.py`: `update_instance_grid_position` (1105),
  `create_default_sprite_for_object` (1203), `check_movement_collision` (2773, thin
  unused wrapper), `show_debug_info` (3771); `runtime/collision_system.py:37` same pattern.
- `utils/project_compression.py:174` `ZipProjectHandler` class (139 lines, never
  referenced; live class is `ProjectCompressor`).
- `utils/config.py`: `save_window_geometry` (323), `restore_window_geometry` (338).
- `events/event_types.py`: `get_keyboard_event_by_key_code`,
  `get_mouse_event_by_button_code`; `events/thymio_events.py` lookup helpers
  (`get_thymio_event`, `get_aseba_event_name`, `get_keyboard_mapping`,
  `get_event_update_rate`, etc.); `events/action_types.py:1249 get_available_actions`.
- `config/blockly_config.py:248 is_category_enabled`.
- Dead getters on dialogs: `blockly_config_dialog.get_config` (consumers use
  `.config` attr), `thymio_config_dialog.get_config`,
  `thymio_action_selector.get_selected_action/get_configured_parameters`,
  `import_dialogs.get_asset_names` + the `AssetImportDialog`/`ImportDialog` aliases.

**Unused import:** only one real one — `import textwrap` in
`scripts/generate_platform_test_pdfs.py:15`. The `try: import
PyInstaller/kivy/PIL/buildozer` "unused" flags in exporters are intentional
availability checks (already `# noqa`).

---

## 3. Duplicate code — high-severity clusters (maintenance/divergence hazards)

> **Platform-exporter cluster — ✅ CONSOLIDATED 2026-05-17.** Added
> `export/base_exporter.py::BaseKivyExporter(QObject)` holding the verified
> byte-identical members (signals, `__init__`, `_load_rooms_from_files`,
> `_load_objects_from_files`, `_check_pyinstaller/_check_kivy/_check_pillow`,
> `_generate_kivy_game`). `exe/linux/macos` now subclass it (their identical
> copies deleted); `android` subclasses it but keeps its legitimately
> divergent loaders/`_generate_kivy_game`/`__init__` and only dedups
> signals + `_check_kivy`. `ios` left untouched (genuinely divergent —
> Xcode/kivy-ios flow). Behaviour preserved: each refactored exporter was
> proven AST-identical to its pre-refactor HEAD (62 method equivalences),
> full suite stays 498-pass, net −517 LOC across the 4 files vs a 205-line
> base. **Deferred follow-up — ✅ RESOLVED 2026-05-19 (kernel only).** The
> same loaders also live in `core/project_manager.py` and
> `runtime/game_runner.py`. Whole-method consolidation was correctly rejected:
> the three are *divergent by design* (different signatures/data source;
> project_manager handles string-path refs + OrderedDict ordering + marker
> cleanup; game_runner is lean read-only and opens files without
> `encoding='utf-8'` — a separate pre-existing inconsistency, left as-is, not
> silently changed; logging differs per loader). **But** the actual drift
> hazard — the fixed list of room/object property keys copied from the split
> file (6 room keys, 11 object keys) plus the instance/event merge — was
> byte-identical in all three and is now single-sourced in
> `utils/project_file_merge.py::merge_room_file/merge_object_file` (pure,
> no I/O, no logging). Each loader keeps its own orchestration + logging and
> just calls the kernel. Behaviour-preserving on this hot path: proven vs
> pre-refactor HEAD by a harness over 16 scenarios (3 loaders × rooms/objects
> × dir-present/absent + the project_manager/exporter string-ref path) that
> deep-compares both the mutated `project_data` *and* the exact per-loader
> log call sequence; full suite stays 481-pass. Divergent orchestration
> deliberately left intact (not a hazard).

> **Blockly/Thymio config-dialog cluster — ✅ CONSOLIDATED 2026-05-19.**
> Added `dialogs/_block_config_dialog_base.py::BaseBlockConfigDialog(QDialog)`
> holding the verified-identical scaffold (`config_changed` signal,
> `_detect_language`, `_is_dark_color`, `_get_block_name`, `setup_ui`,
> `populate_tree`, `on_item_changed`, `load_config_to_ui`, `check_dependencies`
> + extracted `_render_dependency_warning` tail, `save_and_close`). Both
> dialogs now subclass it and override only the genuinely divergent template
> hooks (window title/size, preset list, category filter/colours,
> preset-index detection, missing-deps computation + message,
> `update_info_label`, `on_preset_changed`, `select_all/none`, plus Thymio's
> `_is_/_apply_thymio_*`). `THYMIO_CATEGORIES` is single-sourced in the base
> and re-exported by both modules (no external importers; verified). Net
> −125 LOC (866→741) and, more importantly, the ~6 duplicated blocks are now
> single-sourced instead of drift-prone copies. **Behaviour-preserving** —
> proven against pre-refactor HEAD by an offscreen-Qt harness over 36
> scenarios (9 configs × 2 dialogs: construction, every preset change,
> select-all/none, `on_item_changed` for category+block, reload round-trip,
> and the `save_and_close` emit/accept path under both prompt responses),
> comparing full tree structure (text, check state, flags, brushes,
> tooltips, expansion), preset combo, labels and window geometry; full suite
> stays 481-pass (1 pre-existing env-only failure unrelated to dialogs).
> **Translation note (no regression):** PySide6 `QObject.tr()` resolves its
> context from the *concrete* runtime class (empirically verified), so the
> moved `tr()` calls still look up under `BlocklyConfigDialog` /
> `ThymioConfigDialog` and the existing .qm files keep working unchanged;
> divergent strings were kept lexically inside subclass hooks. The project
> ships .ts/.qm by hand and runs no `lupdate` (only `lrelease` via
> `scripts/compile_translations.py`), so nothing reassigns the context; a
> *future* manual `lupdate` would file the ~12 shared UI strings under a
> `BaseBlockConfigDialog` context — a translation-maintenance follow-up, not
> a runtime change.

| Cluster | Where | Issue |
|---|---|---|
| ~~Platform exporters are structural clones~~ ✅ done | `export/{exe,linux,macos,android}` now share `export/base_exporter.py`; `ios` intentionally separate | Resolved (see note above). *Correction (2026-05-17): the previously-noted "Android `export_project` docstring still says 'macOS .app bundle'" was an audit inaccuracy — verified at HEAD and working tree, that docstring correctly reads "Export the project as an Android APK using Kivy + Buildozer"; no such leftover exists. Nothing to fix.* |
| ~~`_load_rooms_from_files` / `_load_objects_from_files`~~ ✅ done 2026-05-19 | merge kernel in `utils/project_file_merge.py`; per-loader orchestration kept | Exporter copies unified via base (earlier); the byte-identical merge kernel (6 room keys / 11 object keys + instance/event merge) now single-sourced and shared by `project_manager`, `game_runner` and `base_exporter`. Divergent orchestration (signatures, string-ref handling, logging, file-open encoding) is divergent-by-design and intentionally left. Hot-path behaviour proven HEAD-identical over a 16-scenario data+log harness. |
| `tree_main.py` vs `asset_tree_widget.py` | widgets/asset_tree | Two `AssetTreeWidget` classes, overlapping `add/remove/clear/refresh/rename`; already drifted (see §1). |
| ~~Blockly vs Thymio config dialogs~~ ✅ done 2026-05-19 | shared `dialogs/_block_config_dialog_base.py::BaseBlockConfigDialog` | Resolved (see note above). The ~6 duplicated blocks (`_detect_language`, `_is_dark_color`, `_get_block_name`, tree population, button bar, `on_item_changed`, save-confirm) are now single-sourced; subclasses keep only the divergent hooks. Behaviour proven HEAD-identical over 36 harness scenarios; translation-safe. |
| ~~room_editor sprite/pixmap helpers~~ ✅ done 2026-05-17/18 | shared `editors/room_editor/object_render.py` | Extracted to `object_render`: `object_color`, `draw_object_placeholder`, `create_default_sprite`, `resolve_object_sprite`. **Behaviour-preserving** for canvas/palette — proven vs HEAD: 5006-name colour check, pixel-identical placeholder (6 cases) and default-sprite, functional-identical sprite resolver (10 cases), 498 tests. **Approved visual change to room-preview thumbnails:** `room_preview_generator` now uses the shared colour/placeholder *and* sprite resolver, so previews render identically to the editor canvas (curated palette instead of arbitrary hash colours; objects without a sprite now show a default-sprite pixmap + 64px cap instead of a bare placeholder/None). **Background-image loader + icon abbreviation now also consolidated (2026-05-18, behaviour-preserving):** `load_image_asset` shared by `load_background_image`/`_load_background_image` — each caller still passes its own cache-key (`name` vs `bg_{name}`) and error sink (`logger.error` vs `print`), so behaviour is unchanged (proven over 12 cases, both variants). `create_default_sprite` gained `abbrev_over`/`abbrev_keep` params (default 6/4 = canvas/preview unchanged); `object_palette.create_default_icon` delegates with 4/2 → pixel-identical to before. Whole room-editor render cluster is now single-sourced. |
| ~~Editor float/attach toolbar~~ ✅ done 2026-05-19 | shared `editors/_floatable_editor.py::FloatableEditorMixin` | Resolved. **Audit undercounted:** the verbatim `float_requested`/`reattach_requested` signals + `_on_float_clicked`/`set_floating_state` were cloned in *three* independent `QWidget` editors — `base_editor.py`, `room_editor/__init__.py` **and** `playground_editor/__init__.py` (the audit named only the first two; re-verified AST-byte-identical across all three). All three are unrelated `QWidget` subclasses (RoomEditor is **not** a BaseEditor subclass — the original "redefines instead of inheriting" framing was inaccurate), so extraction is a mixin, not a base. `widgets/tutorial_panel.py::set_floating_state` is genuinely divergent (different signature/button/strings, no signals) and was correctly left untouched. Behaviour-preserving: AST byte-identity of all removed copies + an 8-scenario HEAD-vs-mixin functional matrix (signal emit/sender, `_is_floating`, button text/tooltip, `hasattr` early-return) + real-class wiring checks (PySide6 mixin-Signal coexistence/sender and concrete-class `tr()` context empirically verified); full suite stays 481-pass. |
| ~~Tutorial path/list logic~~ ✅ done 2026-05-19 (partial — correction) | shared `widgets/_tutorial_paths.py::localized_tutorials_path` | `_get_localized_tutorials_path` **was** byte-identical in both → extracted to a shared pure function; each widget keeps a thin wrapper (unrelated QDialog/QWidget classes, so a function not a base). Proven HEAD-identical to **both** copies over a 21-case path×language matrix (incl. the `except` path and localized-folder branches); full suite stays 481-pass. **Audit inaccuracy corrected:** `load_tutorial_list` is **not** duplicated — the two implementations diverge materially (panel reads `tutorial.json` in the folder fallback, dialog only scans `*.html` and strips leading numbers; dialog disables placeholder list items and resets a description label; different `folder` values). Folding it would change behaviour, not preserve it, so it was correctly left untouched. |
| ~~pygame keymap~~ ✅ done 2026-05-19 | shared `runtime/_keymap.py::pygame_key_name` | Resolved. The 44-line keycode→name mapping was **AST-identical** in `game_runner.GameRunner._get_key_name` and `input_handler.InputMixin._get_key_name` (differing only by input_handler's `_PYGAME_AVAILABLE` guard + type hint). Extracted to a pure `pygame_key_name(key)`; both methods now delegate (input_handler keeps its guard). `_keymap` imports pygame defensively (mirrors input_handler) so input_handler stays importable without pygame; game_runner imports pygame unconditionally so its behaviour is unchanged. `GameRunner` does **not** actually inherit `InputMixin` (no bases; InputMixin only re-exported in `runtime/__init__.py`), so the two methods are independent — delegation is behaviour-preserving for both. **Exhaustively proven**: byte-identical to both HEAD methods over 467 keys (every `pygame.K_*` constant + dense 0–399 + negative/huge/boundary ints); full suite stays 481-pass. |

**Medium:** Thymio selector/panel trio
(`thymio_action_selector`/`thymio_event_selector`/`thymio_events_panel`).
✅ **`event_to_regions` map done 2026-05-19** — single-sourced to
`events.thymio_events.EVENT_TO_REGIONS` (was a verbatim duplicate in
`thymio_event_selector` and `thymio_events_panel`; `event_selector`'s 5 extra
`[]`-valued keys were behaviourally inert — `.get(name, [])` makes absence and
explicit `[]` equivalent under the `if regions:` guard). Proven by a 36-case
HEAD-vs-refactored diagram call-trace check over the full event universe;
suite stays 481-pass. **Audit overstated the rest:** the trio does **not**
"share UI scaffold" in any byte-identical sense — a per-method AST identity
matrix shows `setup_ui`/`__init__`/`on_diagram_clicked`/`accept_selection`/
`filter_by_category` all materially diverge across the three (different
bases: 2×`QDialog`, 1×`QWidget`); folding them would change behaviour.
`on_diagram_hovered` *is* identical across all three but it is an inert
`pass` stub (no drift hazard — boilerplate, not a task). `action_to_regions`
is single-use (only `thymio_action_selector`), so not a duplicate.

✅ **Dependency-error strings done 2026-05-19** — the
PyInstaller→Kivy→Pillow dependency-check failure blocks in
`export_project` were verbatim-duplicated across the `exe`/`linux`/`macos`
exporters (PyInstaller block byte-identical; Kivy/Pillow differing *only* by
a platform phrase). Single-sourced to
`BaseKivyExporter._require_kivy_dependencies(platform_label)` (they already
share that base); each `export_project` now calls
`if not self._require_kivy_dependencies("Linux exporter"): return False`.
macOS keeps its extra `_check_xcode_tools` block. Behaviour proven
byte-identical to HEAD (emitted message + abort/proceed) over 3 platforms ×
all 8 pyinstaller/kivy/pillow combinations, with HEAD messages AST-extracted
from the pre-refactor snapshots (not retyped); suite stays 481-pass.

❌ **Key/mouse selector dialogs — won't-do (evidence-based).** A per-method
AST identity matrix of `KeySelectorDialog` ↔ `MouseEventSelectorDialog`
(both `QDialog`, different domains) shows the **only** byte-identical method
is `on_item_double_clicked`, and that is a one-line
`self.accept_selection()` delegate — an inert stub that cannot meaningfully
drift (same category as Thymio `on_diagram_hovered`). `__init__`,
`setup_ui`, `accept_selection` and the key-vs-event filters/getters all
genuinely diverge. A shared mixin here would add import+MRO indirection to
save one undriftable line — net-negative. Correctly left as-is.
**Low (boilerplate, not hazards):** `get_logger(__name__)` init (~70),
`QMessageBox.critical` shape (~111), ad-hoc JSON load try/except (~35),
ancestor-walk `while parent:` idiom.

---

## 4. Do NOT treat these as dead (vulture flagged them, but they're reachable)

> **This section is a guard list, not a task.** There is nothing to "do" — it
> documents vulture false positives that must NOT be removed. Re-verified
> 2026-05-18 after the §2 removal: every item below is still present and
> reachable (dispatch registries, `_DRAW_HANDLERS`, plugin importlib loader,
> `onBlocksChanged` JS bridge, test-only APIs, ~117 `gmk_parser` `_`-locals);
> the §2 work touched none of them.

If anyone acts on the raw vulture output, these will look dead and are **not**:

- **All ~130 `execute_*_action` methods** in `runtime/action_executor.py` —
  auto-registered by `_register_action_handlers()` via `dir(self)` and dispatched
  by name from project JSON, plus an `ACTION_ALIASES` map. Never statically called
  by design.
- **`_draw_*` methods** in `runtime/game_runner.py` — dispatched via the
  `_DRAW_HANDLERS` dict + `getattr`.
- `plugins/audio_actions.py` — runtime-loaded by `events/plugin_loader.py` via
  `importlib`, not orphaned.
- Qt event overrides (`paintEvent`, `mousePressEvent`, `keyReleaseEvent`,
  `sizeHint`, `leaveEvent`, etc.) — called by the Qt C++ framework.
- `editors/object_editor/blockly_widget.py:47 onBlocksChanged` — invoked from JS
  via the WebChannel bridge (`blockly_workspace.html`).
- The ~100 `_`-prefixed locals in `importers/gmk_parser.py` — intentional, they
  document the binary GMK field sequence.
- Test-only APIs: `project_manager.close_project`,
  `asset_manager.import_multiple_assets`, `utils/config.add_recent_project`,
  `export_to_kivy`, `actions/core.py` dataclass fields — used by `tests/`.

---

## Suggested cleanup priority (if/when acted on later)

1. Fix the broken root `__init__.py` (§0).
2. Delete the orphaned modules in §1 (biggest LOC win, lowest risk).
3. Exporter base-class consolidation in §3 (highest divergence risk).
4. The verified dead symbols in §2.

Re-run the scans after any change:

```
venv/bin/python -m pyflakes <dirs>
venv/bin/vulture <dirs> --min-confidence 60
symilar --duplicates=10 --ignore-comments --ignore-docstrings --ignore-imports <files>
```
