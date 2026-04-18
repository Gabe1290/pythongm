# Changelog

All notable changes to PyGameMaker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
