# Code Audit — Duplicate & Dead Code

**Date:** 2026-05-17
**Status:** Findings reference for pre-1.0 testing. §0, §1 fixed 2026-05-17.
§2 dead-symbol removal completed 2026-05-18 (65 symbols, ~800 lines). §3
platform-exporter cluster and the entire room-editor render cluster (colour,
placeholder, sprite resolution, background-image loader, icon abbreviation)
consolidated 2026-05-17/18. §4 re-verified still accurate (it is a
non-actionable false-positive guard list, not a task). Remaining §3 clusters
(config dialogs, float/attach, tutorial paths, pygame keymap, Thymio
selectors) untouched.

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
> base. **Deferred (not done):** the same loaders also live in
> `core/project_manager.py:217,266` and `runtime/game_runner.py:1548,1584`
> with different signatures/logging and no test coverage — folding those in
> touches the game-runtime/project-load hot path and is out of scope for an
> exporter-only consolidation; tracked as a separate follow-up.

| Cluster | Where | Issue |
|---|---|---|
| ~~Platform exporters are structural clones~~ ✅ done | `export/{exe,linux,macos,android}` now share `export/base_exporter.py`; `ios` intentionally separate | Resolved (see note above). *Correction (2026-05-17): the previously-noted "Android `export_project` docstring still says 'macOS .app bundle'" was an audit inaccuracy — verified at HEAD and working tree, that docstring correctly reads "Export the project as an Android APK using Kivy + Buildozer"; no such leftover exists. Nothing to fix.* |
| `_load_rooms_from_files` / `_load_objects_from_files` — partially done | ✅ unified for the 4 exporters via base; **still 3×** in `core/project_manager.py:217,266` + `runtime/game_runner.py:1548,1584` | Exporter copies removed; the project_manager/game_runner copies deferred (see note — different signatures, no tests, runtime hot path). |
| `tree_main.py` vs `asset_tree_widget.py` | widgets/asset_tree | Two `AssetTreeWidget` classes, overlapping `add/remove/clear/refresh/rename`; already drifted (see §1). |
| Blockly vs Thymio config dialogs | `dialogs/blockly_config_dialog.py` ↔ `dialogs/thymio_config_dialog.py` | `_detect_language`, `_is_dark_color`, `_get_block_name`, tree population, button bar, `on_item_changed`, save-confirm duplicated (~6 blocks). Thymio is Blockly filtered by category. |
| ~~room_editor sprite/pixmap helpers~~ ✅ done 2026-05-17/18 | shared `editors/room_editor/object_render.py` | Extracted to `object_render`: `object_color`, `draw_object_placeholder`, `create_default_sprite`, `resolve_object_sprite`. **Behaviour-preserving** for canvas/palette — proven vs HEAD: 5006-name colour check, pixel-identical placeholder (6 cases) and default-sprite, functional-identical sprite resolver (10 cases), 498 tests. **Approved visual change to room-preview thumbnails:** `room_preview_generator` now uses the shared colour/placeholder *and* sprite resolver, so previews render identically to the editor canvas (curated palette instead of arbitrary hash colours; objects without a sprite now show a default-sprite pixmap + 64px cap instead of a bare placeholder/None). **Background-image loader + icon abbreviation now also consolidated (2026-05-18, behaviour-preserving):** `load_image_asset` shared by `load_background_image`/`_load_background_image` — each caller still passes its own cache-key (`name` vs `bg_{name}`) and error sink (`logger.error` vs `print`), so behaviour is unchanged (proven over 12 cases, both variants). `create_default_sprite` gained `abbrev_over`/`abbrev_keep` params (default 6/4 = canvas/preview unchanged); `object_palette.create_default_icon` delegates with 4/2 → pixel-identical to before. Whole room-editor render cluster is now single-sourced. |
| Editor float/attach toolbar | `editors/base_editor.py:184-204` duplicated verbatim in `editors/room_editor/__init__.py:204-223` | RoomEditor redefines instead of inheriting `set_floating_state`/`_on_float_clicked` (recent feature — will drift). |
| Tutorial path/list logic | `widgets/tutorial_dialog.py` ↔ `widgets/tutorial_panel.py` | `_get_localized_tutorials_path` + `load_tutorial_list` duplicated; tutorial was just made dockable, so these are actively drifting. |
| pygame keymap | `runtime/game_runner.py:2068-2119` ↔ `runtime/input_handler.py:282-332` | 44-line keycode→name table duplicated. |

**Medium:** Thymio selector/panel trio
(`thymio_action_selector`/`thymio_event_selector`/`thymio_events_panel` share UI
scaffold + `event_to_regions` map), key/mouse selector dialogs,
dependency-error strings.
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
