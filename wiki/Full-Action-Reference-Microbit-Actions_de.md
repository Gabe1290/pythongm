# micro:bit

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Clear Display

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_clear_display` |
| **Symbol** | ⬛ |
| **Kategorie** | micro:bit |

Turn every LED off and drop anything still queued

*Parameter:* keine

### If Button Pressed

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_if_button` |
| **Symbol** | 🔘 |
| **Kategorie** | micro:bit |

True while the button is held down (A+B = both)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `button` | Auswahl | `a` | Auswahl: `a`, `b`, `ab`, `logo` |

### If Gesture

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_if_gesture` |
| **Symbol** | 🤝 |
| **Kategorie** | micro:bit |

True while the board is in this gesture or posture

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `gesture` | Auswahl | `shake` | Auswahl: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### If LED Brightness

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_if_pixel` |
| **Symbol** | 🔍 |
| **Kategorie** | micro:bit |

Compare one LED's brightness (0-9) with a value; the default asks "is it lit?"

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Text | `0` |  |
| `y` | Text | `0` |  |
| `comparison` | Auswahl | `>` | Auswahl: `<`, `<=`, `==`, `>=`, `>`, `!=`; optional |
| `value` | Text | `0` | optional |

### If Tilt

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_if_tilt` |
| **Symbol** | 📐 |
| **Kategorie** | micro:bit |

Compare an accelerometer axis (milli-g, -2048..2048) with a value

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `axis` | Auswahl | `x` | Auswahl: `x`, `y`, `z` |
| `comparison` | Auswahl | `>` | Auswahl: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Text | `300` |  |

### Play Melody

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_play_melody` |
| **Symbol** | 🎵 |
| **Kategorie** | micro:bit |

Play a built-in melody (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, RINGTONE, FUNK, BLUES, BIRTHDAY, WEDDING, FUNERAL, PUNCHLINE, PYTHON, BADDY, CHASE, BA_DING, WAWAWAWAA, JUMP_UP, JUMP_DOWN, POWER_UP, POWER_DOWN) or your own notes such as "C4:4 E G C5:8 R:4" (note, octave, :length; R is a rest)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `melody` | Text | `DADADADUM` | Built-in name, or notes separated by spaces |
| `tempo` | Text | `120` | optional |

### Play Tone

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_play_tone` |
| **Symbol** | 🔔 |
| **Kategorie** | micro:bit |

Beep at a frequency for a number of milliseconds. Sounds queue and play one after another

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `frequency` | Text | `440` | Pitch in hertz (440 = the note A) |
| `duration` | Text | `500` | optional |

### Read Sensor

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_read_sensor` |
| **Symbol** | 📡 |
| **Kategorie** | micro:bit |

Read a micro:bit sensor into a variable of this object (or a global variable if the name starts with "global.")

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `sensor` | Auswahl | `accelerometer x` | Auswahl: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Text | `sensor_value` | Variable that receives the reading |

### Scroll Text

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_scroll_text` |
| **Symbol** | 🔤 |
| **Kategorie** | micro:bit |

Scroll text across the LED display. Put literal text in double quotes ("Hello"); otherwise a dash or plus is read as arithmetic. Accented letters show as ? as on the real board

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `text` | Text | `"Hello"` | Text or expression to scroll |
| `delay` | Zahl | `150` | Scroll speed (MicroPython default 150); optional |

### Send Radio Message

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_radio_send` |
| **Symbol** | 📻 |
| **Kategorie** | micro:bit |

Send a number or text to the other micro:bits in the same group (not to this one). They get the Radio Message Received event, with the value in radio_number and radio_string. Put literal text in double quotes; text is cut to 32 characters

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `value` | Text | `1` | A number, an expression or quoted text |

### Set Display Brightness

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_set_brightness` |
| **Symbol** | 🔆 |
| **Kategorie** | micro:bit |

Overall LED brightness, 0 (dark) to 255 (full)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `brightness` | Text | `255` |  |

### Set LED

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_set_pixel` |
| **Symbol** | 💡 |
| **Kategorie** | micro:bit |

Light one LED now (x and y are 0-4, brightness 0-9)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Text | `0` |  |
| `y` | Text | `0` |  |
| `brightness` | Text | `9` | optional |

### Set Radio Group

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_radio_set_group` |
| **Symbol** | 📡 |
| **Kategorie** | micro:bit |

Choose the radio group (0-255). Only micro:bits in the same group hear each other; every board starts in group 0

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `group` | Text | `0` |  |

### Show Image

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_show_image` |
| **Symbol** | ❤️ |
| **Kategorie** | micro:bit |

Show an image on the LED display: a built-in name (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL...) or five rows of brightness digits such as "09090:99999:99999:09990:00900". Display actions queue and play one after another

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `image` | Text | `HEART` | Built-in image name, or 5 rows of 5 digits (0-9) separated by colons |
| `hold` | Zahl | `0` | How long it stays before the next queued item (0 = until something else is shown); optional |

### Show Number

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_show_number` |
| **Symbol** | 🔢 |
| **Kategorie** | micro:bit |

Show a number: one digit stays still, longer numbers scroll

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `value` | Text | `0` | Number or expression |

### Stop Sound

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_stop_sound` |
| **Symbol** | 🔇 |
| **Kategorie** | micro:bit |

Silence the speaker and drop any queued sounds

*Parameter:* keine

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (21)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (6)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (8)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (14)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (3)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (18)
- [Zeichnen](Full-Action-Reference-Drawing_de) (11)
- [Netzwerk](Full-Action-Reference-Network-Actions_de) (22)
- [Partikel](Full-Action-Reference-Particles_de) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_de) (5)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
