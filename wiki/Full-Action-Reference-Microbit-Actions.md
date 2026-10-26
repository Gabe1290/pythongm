# micro:bit

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

### Clear Display

| Property | Value |
|----------|-------|
| **Name** | `microbit_clear_display` |
| **Icon** | ⬛ |
| **Category** | micro:bit |

Turn every LED off and drop anything still queued

*Parameters:* none

### If Button Pressed

| Property | Value |
|----------|-------|
| **Name** | `microbit_if_button` |
| **Icon** | 🔘 |
| **Category** | micro:bit |

True while the button is held down (A+B = both)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `button` | Choice | `a` | Choices: `a`, `b`, `ab`, `logo` |

### If Gesture

| Property | Value |
|----------|-------|
| **Name** | `microbit_if_gesture` |
| **Icon** | 🤝 |
| **Category** | micro:bit |

True while the board is in this gesture or posture

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `gesture` | Choice | `shake` | Choices: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### If LED Brightness

| Property | Value |
|----------|-------|
| **Name** | `microbit_if_pixel` |
| **Icon** | 🔍 |
| **Category** | micro:bit |

Compare one LED's brightness (0-9) with a value; the default asks "is it lit?"

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Text | `0` |  |
| `y` | Text | `0` |  |
| `comparison` | Choice | `>` | Choices: `<`, `<=`, `==`, `>=`, `>`, `!=`; optional |
| `value` | Text | `0` | optional |

### If Tilt

| Property | Value |
|----------|-------|
| **Name** | `microbit_if_tilt` |
| **Icon** | 📐 |
| **Category** | micro:bit |

Compare an accelerometer axis (milli-g, -2048..2048) with a value

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `axis` | Choice | `x` | Choices: `x`, `y`, `z` |
| `comparison` | Choice | `>` | Choices: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Text | `300` |  |

### Play Melody

| Property | Value |
|----------|-------|
| **Name** | `microbit_play_melody` |
| **Icon** | 🎵 |
| **Category** | micro:bit |

Play a built-in melody (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, RINGTONE, FUNK, BLUES, BIRTHDAY, WEDDING, FUNERAL, PUNCHLINE, PYTHON, BADDY, CHASE, BA_DING, WAWAWAWAA, JUMP_UP, JUMP_DOWN, POWER_UP, POWER_DOWN) or your own notes such as "C4:4 E G C5:8 R:4" (note, octave, :length; R is a rest)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `melody` | Text | `DADADADUM` | Built-in name, or notes separated by spaces |
| `tempo` | Text | `120` | optional |

### Play Tone

| Property | Value |
|----------|-------|
| **Name** | `microbit_play_tone` |
| **Icon** | 🔔 |
| **Category** | micro:bit |

Beep at a frequency for a number of milliseconds. Sounds queue and play one after another

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `frequency` | Text | `440` | Pitch in hertz (440 = the note A) |
| `duration` | Text | `500` | optional |

### Read Sensor

| Property | Value |
|----------|-------|
| **Name** | `microbit_read_sensor` |
| **Icon** | 📡 |
| **Category** | micro:bit |

Read a micro:bit sensor into a variable of this object (or a global variable if the name starts with "global.")

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `sensor` | Choice | `accelerometer x` | Choices: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Text | `sensor_value` | Variable that receives the reading |

### Scroll Text

| Property | Value |
|----------|-------|
| **Name** | `microbit_scroll_text` |
| **Icon** | 🔤 |
| **Category** | micro:bit |

Scroll text across the LED display. Put literal text in double quotes ("Hello"); otherwise a dash or plus is read as arithmetic. Accented letters show as ? as on the real board

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `text` | Text | `"Hello"` | Text or expression to scroll |
| `delay` | Number | `150` | Scroll speed (MicroPython default 150); optional |

### Send Radio Message

| Property | Value |
|----------|-------|
| **Name** | `microbit_radio_send` |
| **Icon** | 📻 |
| **Category** | micro:bit |

Send a number or text to the other micro:bits in the same group (not to this one). They get the Radio Message Received event, with the value in radio_number and radio_string. Put literal text in double quotes; text is cut to 32 characters

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `value` | Text | `1` | A number, an expression or quoted text |

### Set Display Brightness

| Property | Value |
|----------|-------|
| **Name** | `microbit_set_brightness` |
| **Icon** | 🔆 |
| **Category** | micro:bit |

Overall LED brightness, 0 (dark) to 255 (full)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `brightness` | Text | `255` |  |

### Set LED

| Property | Value |
|----------|-------|
| **Name** | `microbit_set_pixel` |
| **Icon** | 💡 |
| **Category** | micro:bit |

Light one LED now (x and y are 0-4, brightness 0-9)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Text | `0` |  |
| `y` | Text | `0` |  |
| `brightness` | Text | `9` | optional |

### Set Radio Group

| Property | Value |
|----------|-------|
| **Name** | `microbit_radio_set_group` |
| **Icon** | 📡 |
| **Category** | micro:bit |

Choose the radio group (0-255). Only micro:bits in the same group hear each other; every board starts in group 0

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `group` | Text | `0` |  |

### Show Image

| Property | Value |
|----------|-------|
| **Name** | `microbit_show_image` |
| **Icon** | ❤️ |
| **Category** | micro:bit |

Show an image on the LED display: a built-in name (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL...) or five rows of brightness digits such as "09090:99999:99999:09990:00900". Display actions queue and play one after another

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `image` | Text | `HEART` | Built-in image name, or 5 rows of 5 digits (0-9) separated by colons |
| `hold` | Number | `0` | How long it stays before the next queued item (0 = until something else is shown); optional |

### Show Number

| Property | Value |
|----------|-------|
| **Name** | `microbit_show_number` |
| **Icon** | 🔢 |
| **Category** | micro:bit |

Show a number: one digit stays still, longer numbers scroll

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `value` | Text | `0` | Number or expression |

### Stop Sound

| Property | Value |
|----------|-------|
| **Name** | `microbit_stop_sound` |
| **Icon** | 🔇 |
| **Category** | micro:bit |

Silence the speaker and drop any queued sounds

*Parameters:* none

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (21)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (6)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (8)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (14)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (3)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (18)
- [Drawing](Full-Action-Reference-Drawing) (11)
- [Network](Full-Action-Reference-Network-Actions) (22)
- [Particles](Full-Action-Reference-Particles) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health) (5)

[← Back to Full Action Reference](Full-Action-Reference)
