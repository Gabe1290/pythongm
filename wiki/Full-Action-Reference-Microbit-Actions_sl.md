# micro:bit

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Clear Display

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_clear_display` |
| **Ikona** | ⬛ |
| **Kategorija** | micro:bit |

Turn every LED off and drop anything still queued

*Parametri:* brez

### If Button Pressed

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_if_button` |
| **Ikona** | 🔘 |
| **Kategorija** | micro:bit |

True while the button is held down (A+B = both)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `button` | Izbira | `a` | Izbire: `a`, `b`, `ab`, `logo` |

### If Gesture

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_if_gesture` |
| **Ikona** | 🤝 |
| **Kategorija** | micro:bit |

True while the board is in this gesture or posture

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `gesture` | Izbira | `shake` | Izbire: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### If LED Brightness

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_if_pixel` |
| **Ikona** | 🔍 |
| **Kategorija** | micro:bit |

Compare one LED's brightness (0-9) with a value; the default asks "is it lit?"

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Besedilo | `0` |  |
| `y` | Besedilo | `0` |  |
| `comparison` | Izbira | `>` | Izbire: `<`, `<=`, `==`, `>=`, `>`, `!=`; neobvezno |
| `value` | Besedilo | `0` | neobvezno |

### If Tilt

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_if_tilt` |
| **Ikona** | 📐 |
| **Kategorija** | micro:bit |

Compare an accelerometer axis (milli-g, -2048..2048) with a value

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `axis` | Izbira | `x` | Izbire: `x`, `y`, `z` |
| `comparison` | Izbira | `>` | Izbire: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Besedilo | `300` |  |

### Play Melody

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_play_melody` |
| **Ikona** | 🎵 |
| **Kategorija** | micro:bit |

Play a built-in melody (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, RINGTONE, FUNK, BLUES, BIRTHDAY, WEDDING, FUNERAL, PUNCHLINE, PYTHON, BADDY, CHASE, BA_DING, WAWAWAWAA, JUMP_UP, JUMP_DOWN, POWER_UP, POWER_DOWN) or your own notes such as "C4:4 E G C5:8 R:4" (note, octave, :length; R is a rest)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `melody` | Besedilo | `DADADADUM` | Built-in name, or notes separated by spaces |
| `tempo` | Besedilo | `120` | neobvezno |

### Play Tone

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_play_tone` |
| **Ikona** | 🔔 |
| **Kategorija** | micro:bit |

Beep at a frequency for a number of milliseconds. Sounds queue and play one after another

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `frequency` | Besedilo | `440` | Pitch in hertz (440 = the note A) |
| `duration` | Besedilo | `500` | neobvezno |

### Read Sensor

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_read_sensor` |
| **Ikona** | 📡 |
| **Kategorija** | micro:bit |

Read a micro:bit sensor into a variable of this object (or a global variable if the name starts with "global.")

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sensor` | Izbira | `accelerometer x` | Izbire: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Besedilo | `sensor_value` | Variable that receives the reading |

### Scroll Text

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_scroll_text` |
| **Ikona** | 🔤 |
| **Kategorija** | micro:bit |

Scroll text across the LED display. Put literal text in double quotes ("Hello"); otherwise a dash or plus is read as arithmetic. Accented letters show as ? as on the real board

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `text` | Besedilo | `"Hello"` | Text or expression to scroll |
| `delay` | Število | `150` | Scroll speed (MicroPython default 150); neobvezno |

### Send Radio Message

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_radio_send` |
| **Ikona** | 📻 |
| **Kategorija** | micro:bit |

Send a number or text to the other micro:bits in the same group (not to this one). They get the Radio Message Received event, with the value in radio_number and radio_string. Put literal text in double quotes; text is cut to 32 characters

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Besedilo | `1` | A number, an expression or quoted text |

### Set Display Brightness

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_set_brightness` |
| **Ikona** | 🔆 |
| **Kategorija** | micro:bit |

Overall LED brightness, 0 (dark) to 255 (full)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `brightness` | Besedilo | `255` |  |

### Set LED

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_set_pixel` |
| **Ikona** | 💡 |
| **Kategorija** | micro:bit |

Light one LED now (x and y are 0-4, brightness 0-9)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Besedilo | `0` |  |
| `y` | Besedilo | `0` |  |
| `brightness` | Besedilo | `9` | neobvezno |

### Set Radio Group

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_radio_set_group` |
| **Ikona** | 📡 |
| **Kategorija** | micro:bit |

Choose the radio group (0-255). Only micro:bits in the same group hear each other; every board starts in group 0

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `group` | Besedilo | `0` |  |

### Show Image

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_show_image` |
| **Ikona** | ❤️ |
| **Kategorija** | micro:bit |

Show an image on the LED display: a built-in name (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL...) or five rows of brightness digits such as "09090:99999:99999:09990:00900". Display actions queue and play one after another

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `image` | Besedilo | `HEART` | Built-in image name, or 5 rows of 5 digits (0-9) separated by colons |
| `hold` | Število | `0` | How long it stays before the next queued item (0 = until something else is shown); neobvezno |

### Show Number

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_show_number` |
| **Ikona** | 🔢 |
| **Kategorija** | micro:bit |

Show a number: one digit stays still, longer numbers scroll

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Besedilo | `0` | Number or expression |

### Stop Sound

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_stop_sound` |
| **Ikona** | 🔇 |
| **Kategorija** | micro:bit |

Silence the speaker and drop any queued sounds

*Parametri:* brez

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (21)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (6)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (8)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (14)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (3)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (18)
- [Risanje](Full-Action-Reference-Drawing_sl) (11)
- [Omrežje](Full-Action-Reference-Network-Actions_sl) (22)
- [Delci](Full-Action-Reference-Particles_sl) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_sl) (5)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
