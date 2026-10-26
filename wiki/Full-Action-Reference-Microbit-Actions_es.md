# micro:bit

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Clear Display

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_clear_display` |
| **Icono** | ⬛ |
| **Categoría** | micro:bit |

Turn every LED off and drop anything still queued

*Parámetros:* ninguno

### If Button Pressed

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_if_button` |
| **Icono** | 🔘 |
| **Categoría** | micro:bit |

True while the button is held down (A+B = both)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `button` | Elección | `a` | Opciones: `a`, `b`, `ab`, `logo` |

### If Gesture

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_if_gesture` |
| **Icono** | 🤝 |
| **Categoría** | micro:bit |

True while the board is in this gesture or posture

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `gesture` | Elección | `shake` | Opciones: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### If LED Brightness

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_if_pixel` |
| **Icono** | 🔍 |
| **Categoría** | micro:bit |

Compare one LED's brightness (0-9) with a value; the default asks "is it lit?"

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `comparison` | Elección | `>` | Opciones: `<`, `<=`, `==`, `>=`, `>`, `!=`; opcional |
| `value` | Texto | `0` | opcional |

### If Tilt

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_if_tilt` |
| **Icono** | 📐 |
| **Categoría** | micro:bit |

Compare an accelerometer axis (milli-g, -2048..2048) with a value

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `axis` | Elección | `x` | Opciones: `x`, `y`, `z` |
| `comparison` | Elección | `>` | Opciones: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Texto | `300` |  |

### Play Melody

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_play_melody` |
| **Icono** | 🎵 |
| **Categoría** | micro:bit |

Play a built-in melody (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, RINGTONE, FUNK, BLUES, BIRTHDAY, WEDDING, FUNERAL, PUNCHLINE, PYTHON, BADDY, CHASE, BA_DING, WAWAWAWAA, JUMP_UP, JUMP_DOWN, POWER_UP, POWER_DOWN) or your own notes such as "C4:4 E G C5:8 R:4" (note, octave, :length; R is a rest)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `melody` | Texto | `DADADADUM` | Built-in name, or notes separated by spaces |
| `tempo` | Texto | `120` | opcional |

### Play Tone

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_play_tone` |
| **Icono** | 🔔 |
| **Categoría** | micro:bit |

Beep at a frequency for a number of milliseconds. Sounds queue and play one after another

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `frequency` | Texto | `440` | Pitch in hertz (440 = the note A) |
| `duration` | Texto | `500` | opcional |

### Read Sensor

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_read_sensor` |
| **Icono** | 📡 |
| **Categoría** | micro:bit |

Read a micro:bit sensor into a variable of this object (or a global variable if the name starts with "global.")

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sensor` | Elección | `accelerometer x` | Opciones: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Texto | `sensor_value` | Variable that receives the reading |

### Scroll Text

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_scroll_text` |
| **Icono** | 🔤 |
| **Categoría** | micro:bit |

Scroll text across the LED display. Put literal text in double quotes ("Hello"); otherwise a dash or plus is read as arithmetic. Accented letters show as ? as on the real board

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `text` | Texto | `"Hello"` | Text or expression to scroll |
| `delay` | Número | `150` | Scroll speed (MicroPython default 150); opcional |

### Send Radio Message

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_radio_send` |
| **Icono** | 📻 |
| **Categoría** | micro:bit |

Send a number or text to the other micro:bits in the same group (not to this one). They get the Radio Message Received event, with the value in radio_number and radio_string. Put literal text in double quotes; text is cut to 32 characters

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `value` | Texto | `1` | A number, an expression or quoted text |

### Set Display Brightness

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_set_brightness` |
| **Icono** | 🔆 |
| **Categoría** | micro:bit |

Overall LED brightness, 0 (dark) to 255 (full)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `brightness` | Texto | `255` |  |

### Set LED

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_set_pixel` |
| **Icono** | 💡 |
| **Categoría** | micro:bit |

Light one LED now (x and y are 0-4, brightness 0-9)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `brightness` | Texto | `9` | opcional |

### Set Radio Group

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_radio_set_group` |
| **Icono** | 📡 |
| **Categoría** | micro:bit |

Choose the radio group (0-255). Only micro:bits in the same group hear each other; every board starts in group 0

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `group` | Texto | `0` |  |

### Show Image

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_show_image` |
| **Icono** | ❤️ |
| **Categoría** | micro:bit |

Show an image on the LED display: a built-in name (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL...) or five rows of brightness digits such as "09090:99999:99999:09990:00900". Display actions queue and play one after another

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `image` | Texto | `HEART` | Built-in image name, or 5 rows of 5 digits (0-9) separated by colons |
| `hold` | Número | `0` | How long it stays before the next queued item (0 = until something else is shown); opcional |

### Show Number

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_show_number` |
| **Icono** | 🔢 |
| **Categoría** | micro:bit |

Show a number: one digit stays still, longer numbers scroll

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `value` | Texto | `0` | Number or expression |

### Stop Sound

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_stop_sound` |
| **Icono** | 🔇 |
| **Categoría** | micro:bit |

Silence the speaker and drop any queued sounds

*Parámetros:* ninguno

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (21)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (6)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (8)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (14)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (3)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (18)
- [Dibujo](Full-Action-Reference-Drawing_es) (11)
- [Red](Full-Action-Reference-Network-Actions_es) (22)
- [Partículas](Full-Action-Reference-Particles_es) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_es) (5)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
