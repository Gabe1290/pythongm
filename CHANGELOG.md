# Changelog

All notable changes to PyGameMaker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
