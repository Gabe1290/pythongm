# Thymio Robot Events for PyGameMaker

## Overview

This document describes the Thymio robot events available in PyGameMaker. These events are triggered by Thymio's sensors, buttons, and timers, allowing you to create reactive robot behaviors.

**Total Events: 14**

## Event Categories

### 🔘 Button Events (6 events)

Triggered by Thymio's 5 capacitive touch buttons. Updated at 20 Hz.

| Event | Icon | Description | Aseba Mapping | Keyboard (Simulation) |
|-------|------|-------------|---------------|----------------------|
| Button Forward | ⬆️ | Forward button pressed | `onevent button.forward` | Arrow Up |
| Button Backward | ⬇️ | Backward button pressed | `onevent button.backward` | Arrow Down |
| Button Left | ⬅️ | Left button pressed | `onevent button.left` | Arrow Left |
| Button Right | ➡️ | Right button pressed | `onevent button.right` | Arrow Right |
| Button Center | ⏺️ | Center button pressed | `onevent button.center` | Space |
| Any Button | 🔘 | Any button state changes | `onevent buttons` | Any arrow/space |

**Usage Notes:**
- Button events fire when button state changes (press or release)
- Use `thymio_if_button_pressed` action to check current state
- In simulation, keyboard arrow keys and space map to buttons
- Real Thymio: capacitive touch sensors (no physical press needed)

### 📡 Sensor Events (4 events)

Triggered by Thymio's sensors. Proximity and ground sensors update at 10 Hz (every 100ms).

| Event | Icon | Description | Aseba Mapping | Update Rate |
|-------|------|-------------|---------------|-------------|
| Proximity Sensors Update | 📡 | All proximity sensors updated | `onevent prox` | 10 Hz |
| Ground Sensors Update | ⬛ | Ground sensors updated | `onevent prox` | 10 Hz |
| Tap/Shock Detected | 💥 | Accelerometer shock detected | `onevent tap` | Event-driven |
| Sound Detected | 🔊 | Microphone threshold exceeded | `onevent mic` | Event-driven |

**Usage Notes:**
- **Proximity Update**: Check all 7 proximity sensors for obstacles
- **Ground Update**: Check 2 ground sensors for line following
- **Tap**: Triggered on sudden acceleration (shake, collision, drop)
- **Sound**: Triggered when sound intensity > threshold (configurable)

### ⏱️ Timer Events (2 events)

Configurable periodic events. Set period with `thymio_set_timer_period` action.

| Event | Icon | Description | Aseba Mapping | Period |
|-------|------|-------------|---------------|--------|
| Timer 0 | ⏱️ | Timer 0 expired | `onevent timer0` | User-defined |
| Timer 1 | ⏲️ | Timer 1 expired | `onevent timer1` | User-defined |

**Usage Notes:**
- Configure period with `thymio_set_timer_period(timer_id, milliseconds)`
- Period range: 1ms to 32767ms (32.7 seconds)
- Useful for periodic behaviors (LED blinking, state checks, etc.)
- Example: `thymio_set_timer_period(0, 1000)` = 1 second timer

### 🔊 Sound Events (1 event)

Triggered by sound playback completion.

| Event | Icon | Description | Aseba Mapping |
|-------|------|-------------|---------------|
| Sound Finished | 🔇 | Sound playback completed | `onevent sound.finished` |

**Usage Notes:**
- Fires when tone or system sound finishes playing
- Useful for sequencing sounds or actions after sound

### 📡 Communication Events (1 event)

Advanced: Inter-robot communication via IR.

| Event | Icon | Description | Aseba Mapping |
|-------|------|-------------|---------------|
| Message Received | 📨 | IR message received from another Thymio | `onevent prox.comm` |

**Usage Notes:**
- For multi-robot scenarios
- Range: ~10cm between robots
- 11-bit message size
- Use `prox.comm.rx` to read received value

---

## Usage Examples

### Example 1: Button-Controlled Movement

**Event: thymio_button_forward**
```
Actions:
- thymio_move_forward(200)
- thymio_set_led_top(0, 32, 0)  // Green LED
```

**Event: thymio_button_center**
```
Actions:
- thymio_stop_motors()
- thymio_set_led_top(32, 0, 0)  // Red LED
```

### Example 2: Obstacle Avoidance

**Event: thymio_proximity_update**
```
Actions:
- thymio_if_proximity(2, 2000, >)  // Center sensor detects obstacle
  - thymio_turn_left(300)
  - thymio_set_led_top(32, 16, 0)  // Orange LED (warning)
- else
  - thymio_move_forward(200)
  - thymio_set_led_top(0, 32, 0)  // Green LED (OK)
```

### Example 3: Line Following

**Event: thymio_ground_update**
```
Actions:
- thymio_if_ground_dark(0)  // Left sensor on line
  - thymio_turn_right(150)  // Adjust right to stay on line
- thymio_if_ground_dark(1)  // Right sensor on line
  - thymio_turn_left(150)   // Adjust left to stay on line
- else  // Both sensors on light surface
  - thymio_move_forward(200)
```

### Example 4: Blinking LED with Timer

**Event: create**
```
Actions:
- thymio_set_timer_period(0, 500)  // 500ms = 0.5 seconds
- thymio_set_variable(led_state, 0)
```

**Event: thymio_timer_0**
```
Actions:
- thymio_if_variable(led_state, ==, 0)
  - thymio_set_led_top(32, 0, 0)  // Red
  - thymio_set_variable(led_state, 1)
- else
  - thymio_set_led_top(0, 0, 32)  // Blue
  - thymio_set_variable(led_state, 0)
```

### Example 5: Sound Reaction

**Event: thymio_sound_detected**
```
Actions:
- thymio_play_tone(880, 30)  // Play A5 note for 0.5 seconds
- thymio_set_led_circle_all(32, 32, 32, 32, 32, 32, 32, 32)  // All LEDs on
```

**Event: thymio_sound_finished**
```
Actions:
- thymio_leds_off()  // Turn off LEDs when sound finishes
```

### Example 6: Tap Detection (Collision Response)

**Event: thymio_tap**
```
Actions:
- thymio_stop_motors()
- thymio_play_system_sound(5)  // Collision sound
- thymio_set_led_top(32, 0, 0)  // Red LED
- thymio_move_backward(200)
- thymio_set_timer_period(1, 1000)  // Back up for 1 second
```

**Event: thymio_timer_1**
```
Actions:
- thymio_stop_motors()
- thymio_turn_left(300)  // Turn away
```

---

## Event Update Rates

Understanding update rates helps you design efficient robot behaviors:

| Event Type | Rate | Period | Notes |
|------------|------|--------|-------|
| Proximity Sensors | 10 Hz | 100ms | Checks every 0.1 seconds |
| Ground Sensors | 10 Hz | 100ms | Checks every 0.1 seconds |
| Button Events | 20 Hz | 50ms | Very responsive |
| Timer 0/1 | Variable | User-defined | 1ms to 32767ms |
| Tap | Event-driven | N/A | Only when shock detected |
| Sound Detected | Event-driven | N/A | Only when threshold exceeded |
| Sound Finished | Event-driven | N/A | Only when sound completes |

**Design Tips:**
- Don't do heavy processing in 10Hz or 20Hz events (keep them fast)
- Use timers for slower periodic tasks (LED animations, state checks)
- Combine sensor events with conditionals for efficient logic

---

## Simulation vs Real Thymio

### In PyGameMaker Simulation

**Button Events:**
- Keyboard arrow keys → Direction buttons
- Space key → Center button
- Visual button indicators on robot sprite

**Sensor Events:**
- Proximity: Raycasting to detect obstacles (walls, objects)
- Ground: Check sprite pixel color (dark = line)
- Tap: Simulated on collision
- Sound: Keyboard key as trigger (e.g., 'S')

**Timer Events:**
- Game loop timer (same as real Thymio)

### On Real Thymio

**Button Events:**
- Capacitive touch buttons (no physical press)
- Sensitive to touch proximity

**Sensor Events:**
- Proximity: IR sensors (affected by color, surface)
- Ground: IR reflection (works best on white surface with black line)
- Tap: 3-axis accelerometer
- Sound: Microphone with adjustable threshold

**Timer Events:**
- Hardware timers (precise timing)

---

## Event-Driven Programming Tips

### 1. Keep Events Focused

**Good:**
```
Event: thymio_button_center
- thymio_set_variable(mode, 1)
```

**Bad (too much logic):**
```
Event: thymio_button_center
- 50 lines of complex logic
```

### 2. Use State Variables

Store state in variables, change state in button events, act on state in sensor events:

```
Event: thymio_button_forward
- thymio_set_variable(running, 1)

Event: thymio_button_center
- thymio_set_variable(running, 0)

Event: thymio_proximity_update
- thymio_if_variable(running, ==, 1)
  - [obstacle avoidance logic]
```

### 3. Separate Concerns

- **Button events**: Change modes/states
- **Sensor events**: React to environment
- **Timer events**: Periodic updates (animations, state checks)
- **Create event**: Initialization

### 4. Debouncing

Buttons can trigger multiple times. Use state variables to debounce:

```
Event: thymio_button_center
- thymio_if_variable(button_enabled, ==, 1)
  - [do action]
  - thymio_set_variable(button_enabled, 0)
  - thymio_set_timer_period(0, 500)  // 500ms cooldown

Event: thymio_timer_0
- thymio_set_variable(button_enabled, 1)
```

---

## Aseba Code Generation

When exporting to Aseba, PyGameMaker events are translated to `onevent` handlers:

| PyGameMaker Event | Aseba Code Structure |
|-------------------|---------------------|
| `thymio_button_center` | `onevent button.center`<br>&nbsp;&nbsp;`# actions here`<br>`end` |
| `thymio_proximity_update` | `onevent prox`<br>&nbsp;&nbsp;`# actions here`<br>`end` |
| `thymio_timer_0` | `onevent timer0`<br>&nbsp;&nbsp;`# actions here`<br>`end` |

**Example:**

**PyGameMaker:**
```
Event: thymio_button_center
  Actions:
    - thymio_move_forward(200)
    - thymio_set_led_top(0, 32, 0)
```

**Generated Aseba:**
```aseba
onevent button.center
    motor.left.target = 200
    motor.right.target = 200
    call leds.top(0, 32, 0)
end
```

---

## Event Combinations

Combine multiple events for complex behaviors:

### State Machine Pattern

```
Event: create
- thymio_set_variable(state, 0)  // 0=idle, 1=moving, 2=avoiding

Event: thymio_button_forward
- thymio_set_variable(state, 1)

Event: thymio_proximity_update
- thymio_if_variable(state, ==, 1)
  - thymio_if_proximity(2, 2000, >)
    - thymio_set_variable(state, 2)  // Switch to avoiding

Event: thymio_timer_0
- thymio_if_variable(state, ==, 1)
  - thymio_move_forward(200)
- thymio_if_variable(state, ==, 2)
  - thymio_turn_left(300)
```

### Event Sequencing

```
Event: thymio_button_center
- thymio_play_tone(440, 60)  // A4 for 1 second
- thymio_set_variable(sequence, 1)

Event: thymio_sound_finished
- thymio_if_variable(sequence, ==, 1)
  - thymio_play_tone(880, 60)  // A5 for 1 second
  - thymio_set_variable(sequence, 2)
- thymio_if_variable(sequence, ==, 2)
  - thymio_move_forward(200)
```

---

## Testing and Debugging

### Simulation Testing

1. **Run in PyGameMaker** - Test logic without hardware
2. **Use keyboard** - Arrow keys simulate buttons
3. **Visual feedback** - Watch LEDs and movement
4. **Debug output** - Use variables to track state

### Real Hardware Testing

1. **Export to Aseba** - Generate .aesl file
2. **Open in Aseba Studio** - Review generated code
3. **Upload to Thymio** - Test on real robot
4. **Iterate** - Refine in PyGameMaker and re-export

---

## Next Steps

1. ✅ **Thymio Events Defined** (14 events)
2. ✅ **Thymio Actions Defined** (28 actions)
3. 🔲 **Simulator** (Visual Thymio simulation in runtime)
4. 🔲 **Aseba Exporter** (Export to .aesl format)
5. 🔲 **Example Projects** (Complete robot programs)

---

## Resources

- [Thymio Official Website](https://www.thymio.org/)
- [Aseba Event Documentation](https://mobsya.github.io/aseba/aseba-language.html#events)
- [Thymio API Documentation](https://mobsya.github.io/aseba/thymio-api.html)
- [Thymio Actions Reference](./THYMIO_ACTIONS.md)

---

*Generated for PyGameMaker v0.11.0-alpha*
