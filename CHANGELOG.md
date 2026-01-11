# Changelog

All notable changes to PyGameMaker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

PyGameMaker follows semantic versioning during alpha development:
- **0.X.0** - Major feature additions
- **0.X.Y** - Minor features and bug fixes
- **-alpha** suffix indicates pre-release status
