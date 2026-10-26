# micro:bit

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Clear Display

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_clear_display` |
| **Icona** | ⬛ |
| **Categoria** | micro:bit |

Turn every LED off and drop anything still queued

*Parametri:* nessuno

### If Button Pressed

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_if_button` |
| **Icona** | 🔘 |
| **Categoria** | micro:bit |

True while the button is held down (A+B = both)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `button` | Scelta | `a` | Scelte: `a`, `b`, `ab`, `logo` |

### If Gesture

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_if_gesture` |
| **Icona** | 🤝 |
| **Categoria** | micro:bit |

True while the board is in this gesture or posture

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `gesture` | Scelta | `shake` | Scelte: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### If LED Brightness

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_if_pixel` |
| **Icona** | 🔍 |
| **Categoria** | micro:bit |

Compare one LED's brightness (0-9) with a value; the default asks "is it lit?"

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Testo | `0` |  |
| `y` | Testo | `0` |  |
| `comparison` | Scelta | `>` | Scelte: `<`, `<=`, `==`, `>=`, `>`, `!=`; facoltativo |
| `value` | Testo | `0` | facoltativo |

### If Tilt

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_if_tilt` |
| **Icona** | 📐 |
| **Categoria** | micro:bit |

Compare an accelerometer axis (milli-g, -2048..2048) with a value

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `axis` | Scelta | `x` | Scelte: `x`, `y`, `z` |
| `comparison` | Scelta | `>` | Scelte: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Testo | `300` |  |

### Play Melody

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_play_melody` |
| **Icona** | 🎵 |
| **Categoria** | micro:bit |

Play a built-in melody (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, RINGTONE, FUNK, BLUES, BIRTHDAY, WEDDING, FUNERAL, PUNCHLINE, PYTHON, BADDY, CHASE, BA_DING, WAWAWAWAA, JUMP_UP, JUMP_DOWN, POWER_UP, POWER_DOWN) or your own notes such as "C4:4 E G C5:8 R:4" (note, octave, :length; R is a rest)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `melody` | Testo | `DADADADUM` | Built-in name, or notes separated by spaces |
| `tempo` | Testo | `120` | facoltativo |

### Play Tone

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_play_tone` |
| **Icona** | 🔔 |
| **Categoria** | micro:bit |

Beep at a frequency for a number of milliseconds. Sounds queue and play one after another

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `frequency` | Testo | `440` | Pitch in hertz (440 = the note A) |
| `duration` | Testo | `500` | facoltativo |

### Read Sensor

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_read_sensor` |
| **Icona** | 📡 |
| **Categoria** | micro:bit |

Read a micro:bit sensor into a variable of this object (or a global variable if the name starts with "global.")

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `sensor` | Scelta | `accelerometer x` | Scelte: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Testo | `sensor_value` | Variable that receives the reading |

### Scroll Text

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_scroll_text` |
| **Icona** | 🔤 |
| **Categoria** | micro:bit |

Scroll text across the LED display. Put literal text in double quotes ("Hello"); otherwise a dash or plus is read as arithmetic. Accented letters show as ? as on the real board

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `text` | Testo | `"Hello"` | Text or expression to scroll |
| `delay` | Numero | `150` | Scroll speed (MicroPython default 150); facoltativo |

### Send Radio Message

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_radio_send` |
| **Icona** | 📻 |
| **Categoria** | micro:bit |

Send a number or text to the other micro:bits in the same group (not to this one). They get the Radio Message Received event, with the value in radio_number and radio_string. Put literal text in double quotes; text is cut to 32 characters

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `value` | Testo | `1` | A number, an expression or quoted text |

### Set Display Brightness

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_set_brightness` |
| **Icona** | 🔆 |
| **Categoria** | micro:bit |

Overall LED brightness, 0 (dark) to 255 (full)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `brightness` | Testo | `255` |  |

### Set LED

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_set_pixel` |
| **Icona** | 💡 |
| **Categoria** | micro:bit |

Light one LED now (x and y are 0-4, brightness 0-9)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Testo | `0` |  |
| `y` | Testo | `0` |  |
| `brightness` | Testo | `9` | facoltativo |

### Set Radio Group

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_radio_set_group` |
| **Icona** | 📡 |
| **Categoria** | micro:bit |

Choose the radio group (0-255). Only micro:bits in the same group hear each other; every board starts in group 0

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `group` | Testo | `0` |  |

### Show Image

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_show_image` |
| **Icona** | ❤️ |
| **Categoria** | micro:bit |

Show an image on the LED display: a built-in name (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL...) or five rows of brightness digits such as "09090:99999:99999:09990:00900". Display actions queue and play one after another

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `image` | Testo | `HEART` | Built-in image name, or 5 rows of 5 digits (0-9) separated by colons |
| `hold` | Numero | `0` | How long it stays before the next queued item (0 = until something else is shown); facoltativo |

### Show Number

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_show_number` |
| **Icona** | 🔢 |
| **Categoria** | micro:bit |

Show a number: one digit stays still, longer numbers scroll

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `value` | Testo | `0` | Number or expression |

### Stop Sound

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_stop_sound` |
| **Icona** | 🔇 |
| **Categoria** | micro:bit |

Silence the speaker and drop any queued sounds

*Parametri:* nessuno

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (21)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (6)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (8)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (14)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (3)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (18)
- [Disegno](Full-Action-Reference-Drawing_it) (11)
- [Rete](Full-Action-Reference-Network-Actions_it) (22)
- [Particelle](Full-Action-Reference-Particles_it) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_it) (5)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
