# Thymio Robot Actions for PyGameMaker

## Overview

This document describes the Thymio robot actions available in PyGameMaker. These actions allow you to program Thymio robots using the familiar GameMaker event/action paradigm.

**Total Actions: 28**

## Action Categories

### 🤖 Motor Control (6 actions)

Control the Thymio's differential drive motors.

| Action | Icon | Description | Parameters |
|--------|------|-------------|------------|
| Set Motor Speeds | 🤖 | Set left and right motor speeds independently | `left_speed` (-500 to 500), `right_speed` (-500 to 500) |
| Move Forward | ⬆️ | Move forward at specified speed | `speed` (0 to 500) |
| Move Backward | ⬇️ | Move backward at specified speed | `speed` (0 to 500) |
| Turn Left | ↶ | Turn left in place | `speed` (0 to 500) |
| Turn Right | ↷ | Turn right in place | `speed` (0 to 500) |
| Stop Motors | 🛑 | Stop both motors | None |

**Note:** Motor speed units: 500 = ~20 cm/s

### 💡 LED Control (6 actions)

Control the Thymio's RGB LEDs and circle LEDs.

| Action | Icon | Description | Parameters |
|--------|------|-------------|------------|
| Set Top LED Color | 💡 | Set the top RGB LED | `red` (0-32), `green` (0-32), `blue` (0-32) |
| Set Bottom Left LED | 💡 | Set bottom left RGB LED | `red` (0-32), `green` (0-32), `blue` (0-32) |
| Set Bottom Right LED | 💡 | Set bottom right RGB LED | `red` (0-32), `green` (0-32), `blue` (0-32) |
| Set Circle LED | 🔆 | Set one of 8 circle LEDs | `led_index` (0-7), `intensity` (0-32) |
| Set All Circle LEDs | ⭕ | Set all 8 circle LEDs | `led0-7` (each 0-32) |
| Turn Off All LEDs | ⚫ | Turn off all LEDs | None |

**Note:** LED intensity range is 0-32 (0 = off, 32 = maximum)

### 🔊 Sound (3 actions)

Generate tones and play system sounds.

| Action | Icon | Description | Parameters |
|--------|------|-------------|------------|
| Play Tone | 🔊 | Play a tone at frequency | `frequency` (Hz), `duration` (1/60 sec units) |
| Play System Sound | 🔔 | Play built-in sound | `sound_id` (0-7: startup, shutdown, arrow, etc.) |
| Stop Sound | 🔇 | Stop playing sound | None |

**Note:** Duration is in 1/60 second units (60 = 1 second). Use -1 for continuous tone.

### 📡 Sensor Reading (3 actions)

Read sensor values and store in variables.

| Action | Icon | Description | Parameters |
|--------|------|-------------|------------|
| Read Proximity Sensor | 📡 | Read proximity sensor value | `sensor_index` (0-6), `variable` (name to store value) |
| Read Ground Sensor | ⬛ | Read ground sensor value | `sensor_index` (0-1), `variable` (name to store value) |
| Read Button State | 🔘 | Read button state | `button` (forward/backward/left/right/center), `variable` |

**Proximity Sensors:**
- 0: Front Left Far
- 1: Front Left
- 2: Front Center
- 3: Front Right
- 4: Front Right Far
- 5: Back Left
- 6: Back Right

**Ground Sensors:**
- 0: Left
- 1: Right

### 🎯 Sensor Conditions (6 actions)

Test sensor values with if/then logic.

| Action | Icon | Description | Parameters |
|--------|------|-------------|------------|
| If Proximity Detected | 🎯 | Check if obstacle detected | `sensor_index` (0-6), `threshold` (0-4000), `comparison` (>, <, ==, etc.) |
| If Ground is Dark | ⬛ | Check for dark surface | `sensor_index` (0-1), `threshold` (typically 300) |
| If Ground is Light | ⬜ | Check for light surface | `sensor_index` (0-1), `threshold` (typically 300) |
| If Button Pressed | 🔘 | Check if button pressed | `button` (forward/backward/left/right/center) |
| If Button Released | ⚪ | Check if button released | `button` (forward/backward/left/right/center) |
| If Variable | ❓ | Check variable value | `variable`, `comparison` (==, !=, <, >, etc.), `value` |

**Typical Thresholds:**
- Proximity detection: 2000 (close obstacle ~5cm)
- Ground dark: < 300 (on dark line)
- Ground light: >= 300 (on table/white surface)

### ⏱️ Timing (1 action)

Configure timers for periodic events.

| Action | Icon | Description | Parameters |
|--------|------|-------------|------------|
| Set Timer Period | ⏱️ | Set timer period | `timer_id` (0 or 1), `period` (milliseconds) |

**Note:** Timer events must be defined in the Events panel (on_timer_0, on_timer_1).

### 📝 Variables (3 actions)

Manage variables (Thymio uses 16-bit integers only).

| Action | Icon | Description | Parameters |
|--------|------|-------------|------------|
| Set Variable | 📝 | Set variable value | `variable` (name), `value` (-32768 to 32767) |
| Increase Variable | ➕ | Increase variable | `variable` (name), `amount` (default 1) |
| Decrease Variable | ➖ | Decrease variable | `variable` (name), `amount` (default 1) |

**Important:** Thymio only supports 16-bit signed integers (-32768 to 32767). No floating-point numbers.

---

## Usage in PyGameMaker

### 1. Creating a Thymio Object

1. Create a new object in PyGameMaker
2. In the Events panel, add Thymio-specific events:
   - `on_create` - Initialization
   - `on_button_center` - Center button pressed
   - `on_proximity_update` - Proximity sensors updated (10 Hz)
   - `on_timer_0` - Timer 0 event
   - etc.

### 2. Adding Thymio Actions

1. Select an event in the Events panel
2. Click the "Thymio" tab in the Actions panel (🤖 icon)
3. Drag actions into the event
4. Configure parameters

### 3. Example: Simple Movement

**Event: on_button_center**
- Action: `thymio_move_forward(200)`

**Event: on_button_backward**
- Action: `thymio_stop_motors()`

### 4. Example: Obstacle Avoidance

**Event: on_proximity_update**
- Action: `thymio_if_proximity(2, 2000, >)`
  - Then: `thymio_turn_left(300)`
- Action: `else`
  - Then: `thymio_move_forward(200)`

### 5. Example: Line Following

**Event: on_proximity_update**
- Action: `thymio_if_ground_dark(0)`
  - Then: `thymio_turn_right(150)` (adjust to stay on line)
- Action: `thymio_if_ground_dark(1)`
  - Then: `thymio_turn_left(150)`
- Action: `else`
  - Then: `thymio_move_forward(200)`

---

## Simulation in PyGameMaker

When you run your Thymio project in PyGameMaker:

1. **Visual Simulation**: Thymio robot appears in the room with differential drive physics
2. **Sensor Simulation**:
   - Proximity sensors detect obstacles via raycasting
   - Ground sensors detect dark/light sprites
   - Buttons mapped to keyboard (Arrow keys, Space)
3. **LED Visualization**: LED states shown as colored overlays on robot
4. **Motor Physics**: Realistic differential drive movement

---

## Export to Aseba

When ready to deploy to real Thymio:

1. **File → Export → Aseba (.aesl)**
2. Opens Aseba Studio with exported code
3. Upload to Thymio robot
4. Test on real hardware

**Translation Examples:**

| PyGameMaker | Aseba Code |
|-------------|------------|
| `thymio_set_motor_speed(200, 200)` | `motor.left.target = 200`<br>`motor.right.target = 200` |
| `thymio_set_led_top(32, 0, 0)` | `call leds.top(32, 0, 0)` |
| `thymio_if_proximity(2, 2000)` | `if prox.horizontal[2] > 2000 then` |
| `on_proximity_update` event | `onevent prox` |
| `on_button_center` event | `onevent button.center` |

---

## Thymio Robot Specifications

### Sensors
- **Proximity (7)**: Horizontal IR sensors, 0-4000 range, ~10cm max distance, 10 Hz update
- **Ground (2)**: Reflective IR sensors for line following, 10 Hz update
- **Buttons (5)**: Capacitive touch buttons, 20 Hz update
- **Accelerometer**: 3-axis, 16 Hz update (tap detection)
- **Microphone**: Sound intensity with threshold trigger
- **Temperature**: Internal temperature sensor, 1 Hz update

### Actuators
- **Motors (2)**: Differential drive, -500 to 500 speed range
- **LEDs**: Top RGB, bottom RGB (left/right), 8-LED circle, sensor indicators
- **Sound**: Tone generator (frequency + duration) or system sounds

### Physical
- **Size**: 110mm × 110mm × 50mm
- **Speed**: 500 units ≈ 20 cm/s
- **Wheel Base**: ~95mm (for turning calculations)

---

## Next Steps

1. ✅ **Thymio Actions Defined** (28 actions)
2. 🔲 **Thymio Events** (Define event types)
3. 🔲 **Simulator** (Visual Thymio simulation in runtime)
4. 🔲 **Aseba Exporter** (Export to .aesl format)
5. 🔲 **Example Projects** (Line follower, obstacle avoider, etc.)

---

## Resources

- [Thymio Official Website](https://www.thymio.org/)
- [Aseba Language Documentation](https://mobsya.github.io/aseba/aseba-language.html)
- [Thymio API Documentation](https://mobsya.github.io/aseba/thymio-api.html)
- [PyGameMaker Thymio Tutorial](./THYMIO_TUTORIAL.md) *(coming soon)*

---

*Generated for PyGameMaker v0.11.0-alpha*
