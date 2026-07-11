# Changelog

All notable changes to PyGameMaker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-07-11

**The export release.** Every export target was verified end-to-end for
the first time — by actually building and playing the results — and the
gaps that surfaced were closed. All nine bundled samples are now covered
by an enforced feature-parity matrix
(`tests/test_export_feature_matrix.py`) across the desktop runtime, the
HTML5 export, and the Kivy/Android export.

### Added
- **New bundled sample: `match3_1`** — the first sample authored natively
  in the pygm2 format (Welcome tab: "Match-3 — Level 1", translated into
  all seven locales). One controller object drives a full match-3 game:
  click/tap-swap, match flash, visible cascade slide, scoring. Fully
  documented in `samples/match3_1/README.md` (gameplay, architecture,
  roadmap for match3_2/3) with CC0 art credits.
- **HTML5 export: Python games run in the browser.** Projects using
  `execute_code` load the Pyodide runtime on demand and execute their
  Python events with the IDE's semantics; pure-action games stay fully
  offline. Taps/clicks dispatch as mouse events (phone-friendly
  `touchstart` included), the draw queue renders to canvas, and sounds
  are embedded and played (wav/mp3/ogg/m4a).
- **HTML5 export: full engine parity for the bundled samples** — the
  action vocabulary (draw family, instance creation cluster,
  `set_sprite`, `play_sound`, `move_to_contact`, variables/conditionals,
  …), the event set (`destroy`, `game_start`, `no_more_lives`,
  `outside_room`), GM-correct flat conditional semantics (a question
  gates the next action/block; `exit_event` aborts the event), and
  sprite-strip animation with `animation_end`. Verified in headless
  Chromium: all nine samples boot and play with zero errors.
- **Kivy/Android export: parity batch.** Draw queue + draw events, touch
  dispatched as mouse events with room-coordinate `mouse_x`/`mouse_y`,
  the draw family and creation cluster, sprite `animation_end`,
  `no_more_lives`, and a virtual D-pad that appears only for
  keyboard-driven games.
- **Android APK builds actually finish.** Buildozer now runs in a
  persistent per-project workspace (`~/pygm_builds/<project>`) that
  survives retries and login sessions — an interrupted first build
  resumes instead of restarting — with hang-failsafe timeouts instead of
  the old 40-minute kill. Verified end-to-end on Windows/WSL with a real
  42 MB APK of the match-3 sample. New classroom-oriented guide:
  `docs/ANDROID_EXPORT.md`.

### Fixed
- HTML5 exports of `maze_1`–`maze_3` and `plateforme_1`–`5` were broken
  in ways nobody had seen (the player couldn't move in maze_1; all 120
  plateforme_1 instances crashed the loader; conditional branches
  over-ran). All nine samples now play in the browser.
- The Kivy exports of `maze_3` and `plateforme_4`/`5` had never compiled
  (an orphaned `else` from GMK mis-imports; an object name containing a
  space). Every module of every sample's Kivy export is now
  compile-gated in CI.
- The exporters read stale object data from `project.json`'s embedded
  copies; they now merge the authoritative `objects/*.json` side files
  like the project loader does.
- `maze_3`, `plateforme_4`, and `plateforme_5` still carried their GMK
  working names ("maze3_reimport", "*_refresh2") in `project.json`.
- The About dialog reported "1.0.0-rc.13": `utils`/`core` carried their
  own stale `__version__`; they are now bumped by the release script.

## [1.0.0] - 2026-06-28

**First stable release.** PyGameMaker 1.0 ships as a focused, game-only IDE:
visual event/action programming, Google Blockly, built-in sprite and room
editors, a tutorial set, and export to Windows / macOS / Linux / HTML5 /
Kivy (mobile + desktop).

The Thymio robot and Open Roberta tooling are **hidden** from the 1.0 UI —
the Tools "Thymio Programming" submenu, "Configure Thymio Blocks…", the File
menu's Aseba export and Open Roberta import, the toolbar quick-add, the
Welcome-tab import entry, and the Playgrounds asset-tree category. The
underlying code is retained behind `# [1.0]` markers for a planned post-1.0
extension (see `docs/POST_1_0_REFACTOR.md`).

This promotes `1.0.0-rc.14` to stable with no functional changes beyond the
version bump. See the release-candidate entries below for the full pre-1.0
history — most notably the complete 2026-06-11 audit (15 high / 61 medium /
35 low, all closed with regression tests) and the Kivy/Android export now
writing UTF-8 source files.

### Changed
- Version promoted to **1.0.0** across `__init__.py`, `pyproject.toml`, the
  Windows exe metadata (`version_info.txt`), the README badge, the language
  flyers, and the platform test checklists.

## [1.0.0-rc.14] - 2026-06-27

Release-candidate ahead of the 1.0 stable cut. Hides the Thymio robot and
Open Roberta entry points from the UI so 1.0 ships a focused, game-only
IDE; the underlying code is retained for a planned post-1.0 Thymio
extension (see `docs/POST_1_0_REFACTOR.md`).

### Removed
- **Thymio robot menu entries.** The `🤖 Thymio Programming` submenu (Tools),
  `Configure Thymio Blocks...` (Tools), `Export Aseba (Thymio) code...`
  (File), and the `Thymio` toolbar quick-add button are commented out in
  `core/ide_window.py`. All underlying methods (`show_thymio_playground`,
  `show_thymio_event_selector`, `configure_thymio`, `export_aseba_code`,
  etc.) and the `runtime/` / `export/Aseba/` / `dialogs/` Thymio code are
  left intact for the future extension. Object-editor context-menu Thymio
  entries were already gated behind `project_has_playgrounds()` and stay
  hidden for normal projects.
- **Open Roberta menu entries.** `Import Open Roberta XML...` (both the File
  menu copy and the Thymio-submenu copy) is hidden; `import_roberta_xml` and
  `importers/roberta_importer.py` are retained for the extension.
- **Committee Demo edition** and its dedicated `minimal` Blockly preset. The
  edition existed only to gate the IDE down to a curated demo for committee
  approval; with the project accepted it's no longer needed. The
  `09_catch_the_coins` tutorial it showcased is kept as standalone content.
  Projects previously saved under the `minimal` preset load fine — an unknown
  preset name falls back to the saved/global toolbox config.

### Changed
- Version bumped to **1.0.0-rc.14** across `__init__.py`, `pyproject.toml`,
  the Windows exe metadata (`version_info.txt`), and the README badge.

## [1.0.0-rc.13] - 2026-06-15

Stabilization release. Closes the complete, adversarially-verified
full-codebase audit (`docs/FULL_AUDIT_2026-06-11.md`): **111 findings
(15 high / 61 medium / 35 low), every one fixed with a regression test.**
No new features — correctness, data-integrity and robustness only.

### Fixed

Highlights across subsystems (see the audit registry for the full per-finding
list, all checkboxes closed, and the `tests/test_audit_*` regression tests):

- **Runtime / game loop.** GMK-imported games no longer run at double speed
  (`settings['room_speed']` is honoured); instances created during an event are
  no longer processed the same frame; persistent instances survive a room
  restart; re-entering a visited room no longer re-fires `create` events;
  collision push-back lands flush with nonzero sprite origins; the
  `if_condition` `mouse_check` (button / over-object) actually evaluates.
- **Editors.** Sprite-editor frame add/duplicate/delete and room-editor
  Clear All / Shift All are now undoable; the eyedropper no longer paints when
  dragged; a same-named asset of a different type no longer collides on one
  editor slot; playground robots each get a distinct port.
- **Export.** Kivy/Android code generation emits valid Python (conditional
  scoping, keyboard handlers, a defined `check_collision_at`, message
  escaping); Aseba `.aesl` output fixes; EXE export reports real
  success/failure; project names containing quotes no longer break the build.
- **Importers.** GMK and Roberta import hardened against malformed / oversized
  input; GMK resource names guarded against path traversal.
- **IDE / project.** New Project description is persisted; asset rename keeps
  room order and updates nested references; zip projects reopen from Recent;
  Auto-Save settings persist; asset delete / refresh no longer discard unsaved
  in-memory work.

### Changed

- Version bumped to **1.0.0-rc.13** across all `__version__` declarations,
  `pyproject.toml`, the Windows exe metadata (`version_info.txt`), the README
  badge, and the user manuals / flyers (which were still labelled rc.9).

## [1.0.0-rc.12] - 2026-05-23

Bundles three tracks of work on top of rc.11. First, the Phase 2 features
the rc.11 trajectory was held open for — pixel-perfect collision and the
views/camera system. Second, a full pre-1.0 audit: fixed cross-platform
gaps, removed dead code, consolidated duplicated export paths, narrowed
silent exception swallowers, and wired the standalone Aseba code exporter
into the File menu. Third, a focused IDE visual pass: redesigned Welcome
tab, empty-state hints in the asset tree and right panel, toolbar tooltips
with shortcut hints, theme-aware window title, dialog button-bar
consistency.

### Added
- **Pixel-perfect collision (static-only).** Opt-in per sprite via a new
  `precise` field on the sprite asset (`sprite_data['precise'] = True`).
  When enabled, `GameSprite` builds a `pygame.mask` per frame at load
  time. Collision checks (`instances_overlap`,
  `check_collision_at_position`, `check_movement_collision_with_blocker`,
  and the per-tick collision-event detector that consumes them) refine
  AABB hits via `mask.overlap()`. Rotated or non-unity-scaled instances
  fall back to AABB — that's the honest documented static-only
  limitation. GMK imports honor the source project's per-sprite precise
  flag (pre-v800 `_precise` bool; v800+ `shape == 0`). Removes the
  corresponding `TODO.md` entry at `runtime/action_executor.py:497`.
- **Sprite editor: `Precise Collision` checkbox.** The sprite editor
  now exposes a checkbox below the origin spinboxes that toggles the
  per-sprite `precise` flag — the same field already honored by the
  runtime (Phase 2a) and the GMK importer. Round-trips through
  `load_data` / `get_data` and emits `data_modified` on toggle.
- **Views / camera system (Phase 2b–2c).** The 8-view data structure
  that's been declared on every `GameRoom` since the views action was
  first added is now actually read by the renderer.
  - **Phase 2b — single-view minimum.** When `room.views_enabled` is
    True and at least one view is visible, `GameRoom.render()` clips to
    each view's port rect and translates room coords so the view's
    top-left maps to the port's top-left. View 0 is visible by
    default. `GameRoom.update_views()` (called per frame from
    `GameRunner.render()`) handles follow targets: when a view's
    `follow` names an instance, the view nudges so the target stays
    inside `(hborder, vborder)` of the view edges, clamped to the
    room. With `views_enabled=False` (the default) behaviour is
    byte-identical to before — the new `view_offset` parameter on
    `GameInstance.render`, `render_tiles`, `_render_legacy_background`,
    and `_render_bg_layers` defaults to `(0, 0)`.
  - **Phase 2c — multi-view / split-screen.** `GameRoom.render()` now
    loops over every visible view in index order (0 first, 7 last)
    instead of just rendering the first one. The bg color fills the
    whole screen once before the loop so areas not covered by any port
    show the bg color, not stale pixels. Two players side-by-side with
    independent cameras now works: configure `view_0` and `view_1`
    with adjacent ports. Per-view follow shifts now respect the
    `hspeed` / `vspeed` clamp from the view config — positive values
    cap the per-frame camera movement (GameMaker convention; `-1` =
    instant). `GameRoom.current_view_index` is set during render so
    future draw events can query the active camera. The `set_view`
    action handler (already defined in
    `runtime/action_executor.py:3841`) is unchanged but now actually
    affects what's drawn.
- **Aseba (Thymio) code export wired into the File menu.** The existing
  `AsebaExporter` class is now reachable from `File → Export →
  Export Aseba (Thymio) code…`. Runs synchronously (it just writes
  `.aesl` text files), defaults the output directory to
  `<Desktop>/<project>_aseba`, and offers to open the output folder on
  success. The class previously only existed as a `__main__` CLI; the
  menu wiring closes audit item B3.
- **Welcome tab redesigned.** Two-column layout replacing the small
  "Quick Actions" frame. Left column: visible New Project and Open
  Project buttons, plus a "More options" dropdown for Open ZIP /
  Import GMK / Import Roberta, and a "Choose a sample" dropdown that
  imports any of the bundled `.gmk` files into a user-chosen output
  folder. Right column: inline `QListWidget` of up to 8 recent projects
  with "N days ago" timestamps; previously this required a click into
  a popup menu. Footer links: Documentation / Tutorials / About.
  Styling is palette-driven so both light and dark themes render
  cleanly.
- **Asset tree empty-state hint.** When no project is loaded, the asset
  tree paints an italic, palette-aware hint below the category list
  ("No project loaded. Use File → New / Open Project to begin.") so
  the panel doesn't read as a blank clickable surface on first launch.
- **Right panel empty-state placeholder.** The Asset Information /
  Properties / Preview group boxes are hidden when no project is
  loaded; a single centred explanatory label takes their place.
  Switches back to the full panel on project load via the new
  `EnhancedPropertiesPanel.set_project_loaded(bool)` hook.
- **Toolbar tooltips with shortcut hints.** Every toolbar action now
  has a descriptive `setToolTip(...)` (e.g. "Save Project (Ctrl+S)",
  "Test Game (F5)"). The toolbar now reuses the menu's stored QAction
  references, so enable/disable state from `update_ui_state()` applies
  to both menu and toolbar through a single call.
- **`utils.desktop_dir()` / `utils.documents_dir()` helpers.** Wrap
  `QStandardPaths.writableLocation(...)` with sensible fallbacks. The
  IDE now defaults export and project-save dialogs to the localised
  user folder (Bureau / Schreibtisch on Linux, OneDrive-redirected
  Desktop on Windows). Closes audit item X3.
- `CLAUDE.md` at the repo root: working notes for Claude / agent
  sessions — test baseline, audit-cleanup methodology, TODO.md
  conventions, and recent agent-session context. Travels with the repo
  across machines.

### Changed
- **Consolidated five platform export methods into one helper** (audit
  item B5). `export_windows_exe`, `export_linux_binary`,
  `export_macos_app`, `export_android_apk` and `export_ios_app` were
  ~100-line copy-paste implementations of the same flow. They now
  delegate to a shared `_run_export_with_progress(...)` helper plus
  two smaller helpers (`_require_open_project`, `_ask_export_dir`).
  Net: 430 lines removed, 187 added. New export targets are now ~25
  lines of shell rather than another 100-line copy. Behaviour preserved
  per a throwaway offscreen-Qt harness covering four scenarios per
  method (success, failure, cancel, no-project-open) — diff against
  pre-refactor HEAD was empty across all 17 exercised scenarios.
- **Window title format.** Was `"PyGameMaker - <Project>"`; now
  `"<Project> — PyGameMaker IDE"` (em dash, document name first) so
  the project name survives taskbar / Alt-Tab clipping. Trailing `*`
  marker now refreshes live as the user edits, via a new connection to
  `project_manager.dirty_changed`.
- **Tools menu greys out items that need a project.** Validate Project,
  Migrate to Modular Structure, and the Thymio Add Event/Action
  submenu items are disabled when no project is loaded. Items that
  legitimately work without a project (Preferences, Configure Action
  Blocks, Configure Thymio Blocks, Language, Open Playground, Import
  Open Roberta XML) stay enabled.
- **Dialog button bars use `QDialogButtonBox`.** `sprite_strip_dialog`
  and `_block_config_dialog_base` previously used hand-rolled
  `QHBoxLayout` button rows with hardcoded Cancel/OK or Save/Cancel
  ordering. Both now use `QDialogButtonBox`, which orders the standard
  buttons per host-platform convention (OK/Cancel on Windows + Linux,
  Cancel/OK on macOS).
- `runtime/action_executor.py`: extracted shared `_set_speed_component`
  kernel for `execute_set_hspeed_action` / `execute_set_vspeed_action`.
  Behaviour-preserving — same parameter precedence (`hspeed`/`vspeed` →
  `value` → `speed`), same log strings, same float-coercion path.
- `runtime/thymio_action_handlers.py`: reworded the
  `execute_thymio_play_system_sound_action` docstring to honestly describe
  the simulator's tone-only audio surface (was: *"placeholder - just play a
  tone"*). Sampled-audio playback remains a known limitation tracked in
  `TODO.md`.
- **Narrowed 20 silent `except Exception: pass` swallowers** across 10
  files (audit item B4). 18 sites narrowed to specific exception
  classes (e.g. `(OSError, ValueError)` for PIL image reads,
  `(TypeError, RuntimeError, AttributeError)` for Qt signal disconnect)
  or replaced with `logger.debug(...exc_info=True)`. 2 sites kept as
  broad `pass` with explanatory comments (the crash-log writer inside
  the object-editor crash handler; the keyboard-handler unbind in the
  exported Kivy game's `_do_room_switch`).

### Fixed
- **Cross-platform export "open folder" prompts** (audit item X1).
  `export_linux_binary` previously called only `xdg-open` (crashes on
  Windows / macOS); `export_ios_app` called only `open` (crashes on
  Windows / Linux). Both now use the proper 3-way `platform.system()`
  switch matching the other export methods.
- **Stale `precise` parameter in `execute_bounce_action` docstring**
  (audit item B1). The docstring claimed a `precise` parameter the
  function had never read. Removed the misleading line.
- **Windows console flash when launching the game from the IDE in dev**
  (audit item X5). `subprocess.Popen` now passes
  `creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)` — the
  getattr keeps the same call working as a no-op on POSIX.
- **Test fixtures read JSON without `encoding='utf-8'`** (audit item
  X4). Five sites across `tests/conftest.py`, `tests/test_config.py`
  and `tests/test_project_manager.py` were relying on the default
  platform encoding, which is `cp1252` on Windows and would have
  silently mis-decoded any non-ASCII fixture data.
- `editors/object_editor/object_events_panel.py`: defensive
  `try / except RuntimeError` around the `QTimer.singleShot(100, ...)`
  column-width callback. The closure captured `self.events_tree`; when
  the panel was destroyed before the 100 ms timer fired (common in
  fast test teardown), calling `.viewport()` on the freed-C++
  `QTreeWidget` raised. Surfaced once new sprite-editor tests were
  added; root cause is the deferred callback, not the new tests.
- **CI: widget-tests and integration-tests jobs no longer wedge on
  QtWebEngine sandbox.** Added `QTWEBENGINE_DISABLE_SANDBOX=1` and
  `--no-sandbox --disable-gpu --disable-dev-shm-usage` Chromium flags,
  per-test `--timeout=60 --timeout-method=thread`, job-level
  `timeout-minutes` ceilings, and the missing Chromium runtime libs
  (`libnss3`, `libxcomposite1`, `libxdamage1`, etc.) for the GitHub
  Actions Ubuntu runner.
- **CI: widget-test teardown deadlock.** `tests/conftest.py` now
  auto-dismisses `QMessageBox.question / information / warning /
  critical` during widget tests so pytest-qt's automatic
  `widget.close()` teardown can't hit a modal "Save changes?" prompt
  with no user to click it.
- **README version badge bumped from `1.0.0-rc.6` to `1.0.0-rc.11`**
  (was factually wrong on `main` after the rc.11 release; bumped again
  to `rc.12` for this release).

### Removed
- **Dead duplicate `Config` class** in `utils/__init__.py` (84 lines,
  audit item X2). No production code imported it. Its `get_config_path()`
  pointed to `~/.gamemaker_ide/config.json`, a different location from
  the real `utils.config.Config` (`~/.pygamemaker/config.json`) — would
  have silently split user settings across two locations if anything
  had ever imported it.
- **Dead `VisualCanvas` / `VisualCodeGenerator` stub subsystem** in
  `editors/object_editor/object_editor_main.py` (68 lines, audit item
  B2). The real `visual_programming` module was commented out long ago
  and replaced with stubs that returned `None` / `{}`. Five methods and
  the paired project-save/load branches all gated on
  `hasattr(self, 'visual_canvas')`, which was never True anywhere in
  the codebase. The active Blockly path (`create_visual_programming_tab`,
  `blockly_tab`, `blockly_workspace`) is unrelated and untouched.

## [1.0.0-rc.11] - 2026-05-21

Three tracks bundled in this entry. First, a relicensing pass: the project is
now MIT-licensed for the source code and CC BY 4.0 for the documentation (see
License section below) — and the new licensing is surfaced in the About
dialog so users see it without leaving the app. Second, follow-up to rc.10's
encoding audit: the rc.10 fix only covered the runtime's split-file readers,
but the same locale-dependent `open()` pattern was still present in 25+ other
sites across the IDE, exporters, and runtime. This pass closes the rest of
the cluster, hardens project-file writes against partial-write corruption,
and narrows the bare `except:` clauses in shipped Kivy runtime code. Third,
a UX truth-in-advertising sweep: every menu item that used to open a "Not
Implemented" placeholder dialog has been removed, the deferred features are
now tracked in a top-level `TODO.md`, and a macOS-specific Qt menu-role bug
that was silently hijacking the App-menu Preferences slot was fixed. All
behaviour-preserving; the full test suite stays green (502 tests, including
extended encoding regressions and new atomic-write tests).

### License
- **Source code relicensed from GPLv3 to the MIT License.** The author is the
  sole copyright holder (sole git contributor across the repo's history) and
  chose to drop the copyleft for a permissive license that requires attribution
  only. Verified no dependency required GPL compatibility: `QScintilla` was
  declared in `requirements.txt` but had **zero imports** anywhere in the
  source — it has been removed (and with it the transitive `PyQt5` / `PyQt5-Qt5`
  / `PyQt5-sip` chain). PySide6 (LGPLv3) and Pygame (LGPLv2.1) remain compatible
  with MIT via dynamic linking; Pillow / Blockly / Kivy / watchdog / Jinja2 /
  PyInstaller (runtime-exception) are all permissive-compatible.
- **Documentation relicensed under Creative Commons Attribution 4.0
  International (CC BY 4.0).** Covers everything under `docs/`, `wiki/`, the
  in-app tutorial content, the README, the CHANGELOG, the manuals and the
  flyers. Teachers and other adopters can now remix the documentation into
  class handouts under a single attribution requirement. The CC license
  applies to content only; the IDE source code stays MIT. New `LICENSE-docs`
  file added at the repo root with the CC BY 4.0 notice, attribution text and
  canonical URL.
- **Required attribution form: "Gabriel Thullen, 2025-2026".** Both licenses
  require attribution. Use this exact form in any reuse or derivative work.
  The standard MIT `LICENSE` file contains a `Copyright (c) 2025-2026 Gabriel
  Thullen` line because the license format requires identifying the
  rights-holder; informational/attribution lines elsewhere in the project
  (file docstrings, About dialog, flyer footers, manual footers, wiki license
  sections) use the bare `Gabriel Thullen, 2025-2026` form per author
  preference.
- **Previously released versions (`1.0.0-rc.10` and earlier) remain under
  GPLv3.** A retroactive license change is not possible for copies already
  distributed under the prior license; only the current `main` branch and
  future releases are MIT + CC BY 4.0.
- Touches: `LICENSE` (rewritten as MIT + dual-license note + updated third-
  party list), new `LICENSE-docs`, `pyproject.toml` (license field), `main.py`
  (GPL preamble stripped from module docstring), `dialogs/about.py` (credits
  text), `version_info.txt` (Windows `LegalCopyright` suffix), `README.md`
  (license badge + License section rewritten), `requirements.txt` (QScintilla
  removed), 8 × `docs/USER_MANUAL*.md` (localized footers), 8 ×
  `docs/FLYER*.md` (localized license bullets), 9 × `wiki/Home*.md` (localized
  License sections in EN, FR, DE, ES, IT, PT, RU, SL, UK).

### Fixed
- **Encoding gaps closed across the IDE, exporters and runtime.** rc.10 added
  `encoding='utf-8'` to the runtime's split rooms/objects/sprites readers; this
  pass extends the same fix to every remaining text-mode `open()` that touches
  project, config, save-state, highscore, log, or generated-launcher files —
  approximately 30 sites across `runtime/game_runner.py`,
  `runtime/action_executor.py` (`save_state` / `load_state`), every desktop
  exporter (`exe`, `linux`, `macos`, `android`, `ios`, `Aseba`), the Kivy
  exporter's emitted state file, every editor and asset-tree widget that reads
  project.json directly, `utils/config.py`, `utils/theme_manager.py`,
  `config/blockly_config.py`, and the IDE crash log. The encoding regression
  test now also exercises `project.json` and the highscore save/load round-
  trip under the hostile-locale subprocess, not just the split files.
- **Project saves are now atomic.** `core/project_manager.py` previously wrote
  `project.json` and every external `rooms/*.json`, `objects/*.json`,
  `sprites/*.json`, `playgrounds/*.json` with a plain `open(..., 'w')` →
  `json.dump(...)`. A crash, kernel panic, or power loss mid-write could leave
  the user with a truncated, unparseable project. A single
  `_atomic_write_json(path, data)` helper now backs all nine save sites: it
  writes to `path.tmp`, `fsync`s, and `os.replace`s into the final name (atomic
  on POSIX and Windows). On any failure the `.tmp` is unlinked and the original
  file is left untouched. Added tests covering the success path, the no-stray-
  tmp invariant, and the crash-during-replace scenario.
- **Bare `except:` clauses in shipped Kivy runtime code narrowed.** Four
  in `export/Kivy/kivy_exporter.py` (DPI-awareness probe, DPI-scale lookup,
  crash-log write, and stale-state-file cleanup) and two in
  `export/Kivy/template/scene.py.template` (color parser and keyboard unbind)
  were swallowing `KeyboardInterrupt` and `SystemExit` along with the
  exception they actually meant to handle. Each is now narrowed to specific
  expected types (`(OSError, AttributeError)`, `Exception` at the outer
  boundary, `(OSError, ValueError)`, `OSError`, `(ValueError, IndexError,
  TypeError)`, `(AttributeError, KeyError)` respectively), matching the
  pattern rc.9 established for the two `hex_to_rgb` helpers.
- **Spatial-grid full-rebuild on destroy replaced with incremental removal.**
  After each frame's destroy pass, `runtime/game_runner.py` rebuilt the entire
  spatial grid from scratch — O(n) over every surviving instance, even when
  only one was destroyed. Bullet/explosion patterns with many simultaneous
  destroys paid this cost repeatedly. The destroy pass now calls the existing
  `_remove_from_grid()` (O(k) per instance via the `_instance_cells` reverse
  map) only for the instances actually being removed, walks the instance list
  exactly once to filter, and flips `_depth_dirty` directly. Net: O(destroyed
  × cells) instead of O(surviving).

### Changed
- **Single `_hex_to_rgb` helper.** Two scope-local copies inside
  `runtime/action_executor.py` (in `execute_show_highscore_action` and
  `execute_set_draw_color_action`) collapsed to one module-level function.
  Behavior preserved; ~25 LOC removed.
- **Single module-level `ExportThread`.** The same five-line `QThread`
  subclass was defined inline inside each of the five platform-export methods
  in `core/ide_window.py` (`export_exe`, `export_linux_binary`,
  `export_macos`, `export_android`, `export_ios`). All five copies are
  byte-identical. Pulled to one module-level class; ~85 LOC removed.
- **Removed dead `actions/__init__.py` re-exports.** `get_action_v2` and
  `get_actions_by_tab_v2` were `GM80_ALL_ACTIONS`-prebound wrappers from a
  long-completed migration; no callers in the source tree. Deleted along with
  their `__all__` entries and the now-unused `typing.List` import.
- **Platform-exporter preamble single-sourced.** The exe / linux / macOS /
  Android exporters each repeated the same 15-line `export_project` preamble
  verbatim — set ``self.project_path`` / ``output_path`` / ``export_settings``,
  branch on file-vs-directory project paths, read ``project.json`` as UTF-8,
  call ``_load_rooms_from_files`` and ``_load_objects_from_files``. Lifted to
  ``BaseKivyExporter._load_project()``; each subclass now calls it on a single
  line. Removed the now-unused ``json`` module import from all four
  subclasses. ~60 LOC removed; encoding fixes propagate automatically.
- **`ThemeManager` switched from `print()` to logger.** Seven raw stdout
  prints (theme-load warnings, fallback-theme notice, "applied X theme"
  confirmations) routed through `core.logger.get_logger(__name__)` to match
  the rest of the codebase. Removes the last `print()` outside generated /
  exported game code.
- **`parse_color` clusters single-sourced to `utils/color.py`.** The runtime
  (``runtime/action_handlers/base.py``) and the Kivy exporter
  (``export/Kivy/project_adapter.py``) each defined a ``parse_color`` with
  the same shape but different output (0-255 ints vs 0-1 floats). Both now
  delegate to `to_rgb255` / `to_kivy_rgba` in a new ``utils/color.py``
  module; the existing import names are preserved so the 10+ runtime call
  sites don't churn. The unit gap between the two flavours is now explicit
  in one place instead of duplicated.
- **`action_types` alias self-mapping derived, not enumerated.** The
  four-entry ``ACTION_TO_BLOCKLY_MAP.update({...})`` literal that kept the
  picker UI from leaking block-style room aliases past preset gating is now
  generated from the intersection of ``BLOCKLY_TO_ACTION_MAP`` and
  ``ACTION_TYPES``. Adding a new room alias requires editing only the two
  source dicts; the self-mapping follows automatically.
- **Test fixture writers now write UTF-8.** Thirteen ``open(..., 'w')`` /
  ``open(..., 'r')`` sites across ``tests/conftest.py``, ``test_exporters.py``,
  ``test_game_runner.py`` and ``test_integration.py`` now specify
  ``encoding='utf-8'`` (with ``ensure_ascii=False`` on the ``json.dump``s),
  bringing the test fixtures into parity with the runtime/IDE encoding pass.

### Added
- **About dialog now surfaces the new licensing.** The About PyGameMaker
  dialog (`core/ide_window.py`) gained a License section listing the
  MIT-licensed source code and CC BY 4.0-licensed documentation, with a one-
  line note about the GPLv3 → MIT/CC BY 4.0 relicensing rationale (lowering
  the barrier to reuse for educators, students, and downstream projects).
  The new section is wrapped in its own `self.tr(...)` call rather than
  appended to the existing About body, so previously translated locales
  (FR/DE/IT/RU/SL/UK) keep working unchanged — only the License paragraph
  itself needs to be picked up by translators per locale.
- **French translation for the new License paragraph** added to
  `pygm2_fr.ts` (the source compiled to `pygm2_fr.qm`, the .qm French users
  actually load) and mirrored in the split `pygm2_fr_core.ts`.
- **`TODO.md` at the repo root** lists every deferred feature with scope,
  current workaround, and the file path where the stub used to live. Created
  to replace the "Not Implemented" placeholder dialogs (see Removed below)
  so deferred work isn't lost now that the lying UI is gone.

### Removed
- **User-visible "Not Implemented" placeholder dialogs.** Every menu item or
  button that produced a `QMessageBox` saying "X is not yet implemented" has
  been removed along with its handler and any enable/disable references:
  `Edit → Find...` (Ctrl+F), `Edit → Find and Replace...` (Ctrl+H),
  `Build → Build Game...` (F7), `Build → Build and Run` (F8),
  `Tools → Asset Manager...`, `Tools → Clean Project`. Two defensive
  fallback dialogs (`open_asset_editor`'s unknown-asset-type branch and
  `asset_tree`'s create-asset fallback) were demoted to silent
  `logger.warning` since they were catch-alls the user shouldn't normally
  hit. The orphaned `test_object` method in the Object Editor (no UI
  element called it; the planned "Play Object" toolbar button was never
  wired) is also gone. All of these are tracked in the new `TODO.md`.
- ~190 lines of dead handler code removed; net diff including `TODO.md` and
  the macOS Preferences fix was −49 lines.

### macOS
- **App-menu Preferences no longer hijacked by `Configure Thymio Blocks...`.**
  On macOS, Qt auto-promotes `QAction`s to the App menu by matching the
  action text against keywords like `preferences`, `settings`, `config`,
  `setup` (case-insensitive contains-match). `Configure &Thymio Blocks...`
  was matching the `config` substring and getting promoted to the App-menu
  Preferences slot — silently shadowing the real `&Preferences...` action,
  so on Mac the App-menu Preferences opened the Thymio block configurator
  instead of the multi-tab PreferencesDialog (with the IDE Edition
  selector, etc.). Linux/Windows were unaffected because they don't have
  the App-menu merge mechanism. Fixed by explicitly setting
  `QAction.PreferencesRole` on the real Preferences action and
  `QAction.NoRole` on the two `Configure ...` actions, bypassing Qt's
  text heuristic. Bug was reproducible from both git clone and the rc.10
  release build.

## [1.0.0-rc.10] - 2026-05-19

Completes the pre-1.0 codebase audit (duplicate- and dead-code pass) and fixes a
latent UTF-8 bug that affected exported games. No intentional feature changes in
the audit work — every consolidation is behaviour-preserving and was proven
identical to the previous release before landing; the full test suite stays green.

### Fixed
- **Exported games could corrupt or fail to load on non-UTF-8 locales.** The
  game runtime read the split `rooms/`, `objects/` and `sprites/` JSON files with
  the OS-default text encoding, while the editor writes them as UTF-8. On end-user
  systems whose locale is not UTF-8 (e.g. some Windows code pages), any project
  containing non-ASCII instance data, event scripts or asset filenames could
  mojibake or crash on load. The runtime now reads these files as UTF-8, matching
  the editor and exporters. Added a regression test that reproduces a non-UTF-8
  end-user locale.
- **Exported games could fail to *start* on non-UTF-8 locales** (regression
  surfaced by the new encoding test). `utils.config` ran `Config.load()` eagerly
  at module-import time and printed decorative emojis (`📄`, `❌`, …) to stdout
  for first-run / error paths. When `sys.stdout.encoding` was `ascii` (LC_ALL=C,
  minimal Windows code page, stripped CI runner), the prints raised
  `UnicodeEncodeError`, the exception handler raised the same on its own emoji
  print, and the second crash escaped — aborting the entire `runtime.game_runner`
  import chain. All such prints now route through a `_safe_print` helper that
  falls back to `errors='replace'`, so decorative output degrades to `?` instead
  of taking down the runtime.
- **French translation regression**: removed a spurious `pygm2_fr_misc.qm` and
  hardened the translation loader so it can no longer be reintroduced.

### Added
- **Dockable tutorial panel** with editor-style detach/re-dock (and translated
  Float / Re-dock strings for DE/ES/FR/IT/RU/SL/UK).
- Per-platform pre-1.0 IDE test-checklist PDF generator (developer tooling).

### Changed
- **Pre-1.0 codebase audit (§0–§3) completed.** Fixed a broken package root,
  removed 10 orphaned modules and 65 verified-dead symbols (~800 lines), and
  single-sourced every remaining duplicate-code cluster onto shared bases/helpers:
  Kivy platform exporters, the room-editor rendering stack, the Blockly/Thymio
  configuration dialogs, the editor Float/Attach toolbar, the tutorials-path
  helper, the pygame keymap, the Thymio event→region map, the split-project-file
  merge kernel, and the exe/linux/macOS dependency-check messages. All
  behaviour-preserving, each proven against the prior release.

## [1.0.0-rc.9] - 2026-05-09

Pre-1.0 codebase audit pass. No new features — focus is correctness, lifecycle, and parity for the floating-window infrastructure introduced in rc.8.

### Added
- **Playground editor floating-window support**: 🪟 Float button in the toolbar, `update_window_title()` method so the floating title bar reflects modification state, and connection plumbing in `open_playground_editor`. Brings parity with Object/Sprite/Room editors.
- **Cross-window CI release pipeline**: pushing a `v*.*.*` tag now builds Windows / macOS Intel / macOS ARM / Linux / Python sdist and creates the GitHub Release automatically using the relevant `CHANGELOG.md` section as the release body.

### Fixed
- **Crash on Object editor load** (NameError): `load_project_assets` referenced `project_data` after a try-block that could leave it unbound; `load_data` referenced `events_data` from a branch that could skip its assignment. Both initialised before the relevant block.
- **Crash on exporter timeout** (NameError): `process` was referenced from `subprocess.TimeoutExpired` / generic-except branches before `Popen` had bound it. Affected android, exe, linux, and macos exporters; all four initialise `process = None` up front so the existing `if process:` guards behave.
- **Movement runtime crash** (NameError): `handle_move_free` called the undefined `handle_set_direction_speed`; now delegates to `ctx.execute_set_direction_speed_action`.
- **Bare `except:` in two `hex_to_rgb` helpers** narrowed to `(ValueError, IndexError, TypeError)` so they no longer swallow `KeyboardInterrupt` / `SystemExit`.
- **Connection leak**: `close_editor_tab` now disconnects `float_requested` / `reattach_requested` (parity with `_destroy_detached_editor`), so closing and reopening editors no longer accumulates stale connections.
- **Detached editors ignored Undo / Redo / Cut / Copy / Paste / Duplicate**: the IDE menu actions always dispatched to the active *tab*. They now use a focus-aware `_active_editor()` helper that finds the editor whether it lives in a tab or a detached window.
- **`refresh_object_sprites` skipped detached editors**: a sprite assignment change now propagates to floated room editors immediately.
- **Asset rename didn't follow detached editors**: renaming an asset that's open in a floating window now rekeys `open_editors` / `detached_editor_windows`, updates the editor's `asset_name`, refreshes its window title, and updates tab text in lockstep.
- **`auto_save_timer` could fire after a widget was deleted**: stopped in `BaseEditor.closeEvent`. Five `QTimer` instances (BaseEditor, EditorStatusWidget, ProjectManager, RoomEditor, PlaygroundEditor) now have explicit Qt parents so they don't outlive their owners.
- **Restored `QLabel` import** in `runtime/playground_runner.py` that the rc.8 unused-import sweep mistakenly removed (it was used as a base class).
- **Floating window minimum height** halved (Object editor's `center_tabs` and Blockly's `web_view` minimums) so floated windows can be made meaningfully smaller for side-by-side comparison.

### Changed
- **Removed dead orphan signals**: `actionSelected` / `eventSelected` on `EventActionWidget`, `sprite_editor_activated` on `SpriteEditor`, `playground_editor_activated` on `PlaygroundEditor` — none had any consumers.
- **Lint cleanup**: 98 unused imports removed (auto-fixed across 41 files); 15 F841 unused-locals addressed (gmk_parser binary-stream reads renamed to `_var` per Python convention; placeholder tests cleaned); 13 E741 ambiguous variable names (`l` → `line` / `layer`); 2 multi-statement-on-one-line splits.
- **Removed dead `is_solid` read** in `runtime/game_runner.py` movement collision loop — comment already said solid no longer auto-blocks.

## [1.0.0-rc.8] - 2026-05-09

### Added
- **Floating editor windows**: Object, Sprite, and Room editors can be popped out of the tab strip into independent movable windows for side-by-side comparison. Each editor's toolbar has a "🪟 Float" button; closing the floating window reattaches it. Floating window title bars track the editor's modification state.
- **Global window-mode toolbar button**: single click toggles every open editor between Tabbed and Floating mode. Doubles as the recovery affordance — when a floating window has been dragged off-screen, the toggle pulls every detached editor back into tabs. The chosen mode is persisted across sessions and applied to newly opened editors.
- **Cross-editor asset sync**: saving in one editor now broadcasts to siblings, so floated/tabbed Object editors refresh their Blockly asset dropdowns immediately rather than waiting for the next manual refresh.

### Changed
- **Object editor toolbar streamlined**: `Sync from Events`, `Clear All`, `Reload`, and `Configure Blocks…` buttons removed (Events / Blockly / Python now auto-sync, so they were dead weight). The Detach button remains.
- **Object editor default layout**: events panel narrower by default. Switching to the Blockly tab snaps the events panel to its minimum width to give Blockly maximum working space; switching back to Event List or Code Editor restores the default split.
- **Blockly action coverage**: alarm events route through the same nested-subtype format as keyboard events; `grid_move` and `if_can_push` action mappings are now wired up.

### Fixed
- Removed dead `core/event_system.py` module and the malformed `events/__init__,py` file (typo'd filename — was unused).
- Eliminated duplicate inline copies of the Blockly code generators that had drifted out of sync with `blockly_generators.js`.
- Hardcoded asset preset names (`spr_player`, `snd_jump`, `bgm_main`, `obj_bullet`, `room0`) removed from Blockly toolbox / `createAssetField` defaults so dropdowns reflect the current project rather than ghost names.
- Floating editor window now reparents and shows the editor explicitly — `QTabWidget.removeTab` hides the page widget without reparenting it, which previously caused the floated window to appear blank.

## [1.0.0-rc.7] - 2026-05-05

### Added
- **IDE editions system**: Beginner, Advanced, and Development modes with per-edition Blockly toolbox presets and event-panel filtering. Switch via `Tools > Edition`. Includes a one-click Committee Demo edition for committee approvals, plus a "Catch the Coins" tutorial tailored to it.
- **GameMaker 8.0 import**: `File > Import GameMaker .gmk File...` brings legacy `.gmk` projects in. v800 parser now handles double-precision triggers/constants timestamps, with per-phase progress logging.
- **Object editor: parent-property inheritance**. A child object now inherits any property its ancestors define that the child itself doesn't set (closest parent wins, walks up to 10 levels). `sprite`, `visible`, `solid`, and `persistent` are deliberately child-only — they never come from a parent. Events already inherited; this completes the picture for non-event properties.
- **Object events**: alarm event support (`alarm_0` through `alarm_11`) in the events panel.
- **Blockly actions**: `bounce`, `move_to_contact`, `wrap_around_room`, `move_free`, `set_speed`, `set_direction`. Closes 12 of the previously unmapped action pickers.
- **Tutorials**: rewritten with a progressive "play early" approach; new Game Over starter template; French translations updated for the redesigned tutorials.
- **Packaging**: Python source distribution support (`pip install`); `pyproject.toml` version bumped to `1.0.0rc7` (was still `1.0.0rc6`).

### Translations
- Full French resync: `pygm2_fr.ts` re-run through `lupdate`, picking up 389 new strings added since rc.6, with all 311 unfinished entries translated by hand. The monolithic `pygm2_fr.qm` is regenerated (1399 finished entries) and the six split French `.qm` files (`actions`, `blockly`, `core`, `dialogs`, `editors`, `misc`) are removed — they were 4–7 weeks stale and were overriding the monolithic file at runtime, so the IDE was actually loading outdated French. French is now monolithic-only; other languages still use their split files.

### Changed
- **Object editor UI** (Blockly tab): removed the `Test Object` toolbar action (not implemented), removed the duplicate `View Code` controls (the Code Editor tab supersedes them), removed the bottom status strip (`Loaded:` / `Saved` line), moved the Auto-save indicator to the right end of the toolbar, put the Sprite and Parent dropdowns on a single row, and removed the "Visual Block Programming / Drag blocks…" header — all to recover vertical space when working with Blockly.
- Lazy-import the Blockly widget and defer QtWebEngine initialization until the tab is selected, reducing startup cost.
- Asset relative paths normalised to forward slashes for cross-platform project portability.
- Language change now shows a manual-restart message instead of attempting auto-restart (which crashed under PyInstaller).

### Fixed
- Asset rename propagation, parent-event inheritance, and collision blocking — multiple regressions resolved.
- Alarm system: parameter-name mismatch and wrong data structure caused alarms to silently no-op.
- Action editing not saving in some flows; ball stuck above death zone in Breakout; Sokoban walking through `Box_Stored` after `change_instance`.
- Grid-based push mechanics: pushers now land on-grid after pushing a blocker; cross-object movement actions added.
- PyInstaller builds: object editor crash on launch, app restart crash on language change, restart in one-file builds (now fully detaches the new process).
- GMK v800 parse failure on triggers/constants timestamps.
- Import-as-new-project menu items being silently disabled.
- Blockly toolbox and events panel ignoring project preset on startup.
- Asset dropdowns in Blockly now refresh when assets change.
- HTML5 engine.js test fixture forced to UTF-8.
- Monospace font rendering and ASCII-art alignment in tutorial layouts.

### Performance
- Eliminated per-frame `hasattr()` checks on three hot paths.
- Short-circuit movement collision check when no collision targets exist.
- Skip Thymio per-frame work when no Thymio instances are in the room.
- Removed 113 dead modular action handlers (set_variable, test_variable, and Phase 2 priority losers) — runtime bytecode footprint and dispatch table both shrunk.

### Removed
- `dialogs/new_project.py` (dead prototype) and the broken `drawing_actions` example plugin.

## [1.0.0-rc.6] - 2026-04-18

### Added
- Thymio playground simulation: ground sensor support for line following, mirroring Aseba Studio's playground. Two virtual sensors sample pixel brightness under the robot and expose the Aseba-style 0–1020 range via `ground_delta`.
- Blockly/event actions: `read ground`, `if ground dark`, `if ground light` (threshold at 300).
- Playground editor and exporter: ground texture stored in arena metadata and bundled in `.playground` ZIP.

## [1.0.0-rc.4] - 2026-03-05

### Added
- Sprite editor: origin crosshair marker with preset dropdown (Top-Left, Center, Center-Bottom, etc.) and X/Y spinboxes
- Object editor: parent object selector with runtime collision inheritance (walks parent chain up to 10 levels)
- Draw GUI event type for HUD rendering in screen coordinates (not affected by camera)
- Tutorial window is now a detached floating dialog that can be moved freely, no longer blocking the right-hand properties panel

### Changed
- Rewrote Sokoban, Platformer, and Lunar Lander tutorials from GML code to Blockly visual blocks
- Tutorials now reference only actually implemented Blockly blocks (move_grid, if_can_push, set_gravity, draw_text, etc.)

### Fixed
- PyInstaller spec: guard Tree() calls against missing gitignored directories (fixes CI build)
- Sokoban win condition tutorial: use Draw event instead of non-existent Draw GUI Blockly block

## [1.0.0-rc.3] - 2026-03-04

### Added

#### 100% Action Implementation
- All 120 game actions now fully implemented across all tabs:
  - Draw Tab: `draw_circle`, `set_alpha`, `draw_scaled_text`, `draw_background`
  - Main1/Main2 Tabs: 6 actions including score, lives, and health management
  - Rooms Tab: 3 room transition and lifecycle actions
  - Info Tab: 5 information display actions
  - Resources Tab: Dynamic asset loading at runtime
  - Extra Tab: 3 utility actions including `execute_script`
  - Particles Tab: 8 particle effect actions
  - Timing Tab: 6 timing and alarm actions

#### Sprite Editor
- Full pixel-art editor with pencil, eraser, fill, and selection tools
- Tool icons and brush cursor overlay
- Selection clipboard with copy/paste
- Context menu and undo/redo support
- Lightened canvas background for better visibility

#### Export Improvements
- macOS application export (.app bundles)
- Android APK export via WSL on Windows (with buildozer)
- Auto-install Android build-tools 33.0.2 for aidl compatibility
- Live buildozer output in the export progress dialog
- Fixed Linux binary export (black window issue)
- Fixed Android crash on room change in Kivy export
- Android fullscreen and touch controls
- Various WSL build fixes (filesystem, encoding, permissions)

#### Tutorials
- 7 in-IDE tutorials: Introduction to Game Creation, Pong, Breakout, Sokoban, Maze, Platformer, Lunar Lander
- All tutorials translated to 9 languages (EN, FR, DE, ES, IT, PT, SL, UK, RU)
- Resizable tutorial panel
- Breakout and Maze tutorials rewritten with Blockly
- Sample sprites for tutorials included in builds

#### GMK Importer
- Import GameMaker project files into PyGameMaker

#### Blockly Enhancements
- `grid_move` and `if_can_push` blocks for Sokoban-style mechanics
- `wrap_around_room` block
- Dynamic block registration system
- Fixed keyboard event deduplication

#### Code Editor
- Python code templates for all action types
- Bidirectional sync improvements

#### Thymio Enhancements
- Dedicated Thymio panel in object editor
- Thymio Programming Window with visual robot diagram

### Changed
- Runtime engine rewritten with modular architecture and performance optimizations
- Sound system integrated into game runner
- Room lifecycle events (create, destroy) properly implemented
- Animated GIF support for sprites (static and animated)
- Centralized logging replacing debug print statements
- Project migration tool for upgrading older projects
- IDE memory improvements
- All translations synchronized and completed to 100%

### Fixed
- Sprite transparency for static and animated GIFs
- `destroy_instance` in collision events
- `if_condition` with `instance_count` and `create_instance` in Kivy export
- Blockly widget attach/detach and event sync
- Persistent object handling and `keyboard_release` events across room changes
- Multiple runtime action and draw event system fixes
- Various test failures and CI workflow issues

---

## [0.12.0-alpha] - 2026-01-11

### Added - Thymio Educational Robot Support

This major update introduces complete support for the Thymio educational robot, enabling students to visually program robots, test with a real-time simulator, and deploy to real hardware.

#### Visual Programming Interface
- **28 new Thymio actions**:
  - Motor control: `set_motor_speed`, `move_forward`, `move_backward`, `turn_left`, `turn_right`, `stop_motors`
  - LED control: `set_led_top`, `set_led_bottom_left`, `set_led_bottom_right`, `set_led_circle`, `set_led_circle_all`, `leds_off`
  - Sound: `play_tone`, `play_system_sound`, `stop_sound`
  - Sensor reading: `read_proximity`, `read_ground`, `read_button`
  - Conditionals: `if_proximity`, `if_ground_dark`, `if_ground_light`, `if_button_pressed`, `if_button_released`, `if_variable`
  - Timers: `set_timer_period`
  - Variables: `set_variable`, `increase_variable`, `decrease_variable`

- **14 new Thymio events**:
  - Button events: `thymio_button_forward`, `thymio_button_backward`, `thymio_button_left`, `thymio_button_right`, `thymio_button_center`
  - Sensor events: `thymio_proximity_update`, `thymio_ground_update`
  - Timer events: `thymio_timer_0`, `thymio_timer_1`
  - Special events: `thymio_tap`, `thymio_sound_detected`, `thymio_sound_finished`, `thymio_any_button`, `thymio_message_received`

#### Real-Time Simulator
- Physics engine with differential drive kinematics
- 7 proximity sensors using raycasting (0-4000 range, 10 Hz update)
- 2 ground sensors with pixel color sampling (0-1020 range, 10 Hz update)
- 5 button simulation via keyboard (Arrow keys + Space)
- LED system: top RGB, bottom left/right RGB, 8 circle LEDs
- Sound playback tracking
- Timer systems (2 configurable timers)
- 60 FPS smooth rendering
- Visual sensor feedback (proximity rays, ground indicators)
- LED glow effects

#### Aseba Code Export
- Complete translator for all 28 actions to Aseba syntax
- Event mapping: PyGameMaker events → Aseba `onevent` handlers
- Automatic variable declaration scanning
- Control flow handling (if/else/end) with proper indentation
- README generation with upload instructions
- Command-line interface for batch export
- Generates valid `.aesl` files for Aseba Studio

#### GameRunner Integration
- Automatic Thymio object detection (by name prefix or `is_thymio` flag)
- Simulator lifecycle management in game loop
- Event triggering at correct update rates
- Keyboard button mapping
- Position synchronization between simulator and game instances
- Visual rendering integration

#### New Files
- `actions/thymio_actions.py` - 28 action definitions (340 lines)
- `events/thymio_events.py` - 14 event definitions (165 lines)
- `runtime/thymio_simulator.py` - Physics and sensor simulation (515 lines)
- `runtime/thymio_renderer.py` - Visual rendering engine (303 lines)
- `runtime/thymio_action_handlers.py` - Action execution handlers (424 lines)
- `export/Aseba/aseba_exporter.py` - Aseba code generator (900+ lines)

#### Test Scripts
- `test_thymio_actions.py` - Verify action loading
- `test_thymio_events.py` - Verify event loading
- `test_thymio_simulator.py` - Interactive physics/rendering test
- `test_thymio_integration.py` - Full GameRunner integration test
- `test_aseba_export.py` - Aseba exporter validation

#### Documentation
- `docs/THYMIO_COMPLETE.md` - Complete overview and quick start guide
- `docs/THYMIO_RELEASE_NOTES.md` - Detailed release notes
- `docs/THYMIO_ACTIONS.md` - All 28 actions with examples
- `docs/THYMIO_EVENTS.md` - All 14 events with code samples
- `docs/THYMIO_SIMULATOR.md` - Technical specifications
- `docs/THYMIO_GAMERUNNER_INTEGRATION.md` - Integration guide
- `docs/THYMIO_PHASE_2_COMPLETE.md` - Simulator completion summary
- `docs/THYMIO_PHASE_4_COMPLETE.md` - Exporter completion summary
- `docs/THYMIO_IMPLEMENTATION_STATUS.md` - Overall progress tracker

### Changed
- `actions/__init__.py` - Registered Thymio actions
- `actions/core.py` - Added Thymio tab to action palette
- `events/event_types.py` - Registered Thymio events
- `runtime/game_runner.py` - Integrated Thymio simulator lifecycle
- `__init__.py` - Updated version to 0.12.0-alpha, added Thymio to description

### Technical Details
- Robot size: 110×110 pixels (11×11 cm at 10px = 1cm scale)
- Motor speed range: -500 to 500 (500 = 20 cm/s)
- Proximity sensors: 7 sensors, 100px range, raycasting at 2px steps
- Ground sensors: 2 sensors, pixel color sampling
- Update rates: 60 Hz physics, 10 Hz sensors, 20 Hz buttons
- LED intensity: 0-32 per channel (mapped to 0-255 for rendering)

### Statistics
- Total new code: ~7,736 lines
- Implementation: ~4,500 lines
- Documentation: ~2,000 lines
- Tests: ~1,000 lines
- Files created: 22
- Files modified: 5

### Educational Benefits
- Visual programming eliminates syntax errors
- Immediate feedback through simulation
- Safe testing environment before hardware deployment
- Real robot deployment via Aseba Studio
- Event-driven programming concepts
- Sensor-based reactive logic

---

## [0.11.0-alpha] - 2026-01-09

### Added
- Python Code Editor with bidirectional synchronization
- Code Editor test projects for comprehensive validation

### Changed
- Removed hardcoded keyboard shortcuts and behaviors from game engine
- Removed hardcoded game over logic from engine

---

## [0.10.1-alpha] - Previous Release

Earlier development versions - see git history for details.

---

## Version Numbering

PyGameMaker follows semantic versioning:
- **1.0.0** - First stable release
- **-rc.N** suffix indicates release candidate
- **-beta.N** suffix indicates beta pre-release
- **-alpha** suffix indicates alpha pre-release
