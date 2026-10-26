# micro:bit

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Clear Display

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_clear_display` |
| **Ícone** | ⬛ |
| **Categoria** | micro:bit |

Turn every LED off and drop anything still queued

*Parâmetros:* nenhum

### If Button Pressed

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_if_button` |
| **Ícone** | 🔘 |
| **Categoria** | micro:bit |

True while the button is held down (A+B = both)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `button` | Escolha | `a` | Opções: `a`, `b`, `ab`, `logo` |

### If Gesture

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_if_gesture` |
| **Ícone** | 🤝 |
| **Categoria** | micro:bit |

True while the board is in this gesture or posture

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `gesture` | Escolha | `shake` | Opções: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### If LED Brightness

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_if_pixel` |
| **Ícone** | 🔍 |
| **Categoria** | micro:bit |

Compare one LED's brightness (0-9) with a value; the default asks "is it lit?"

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `comparison` | Escolha | `>` | Opções: `<`, `<=`, `==`, `>=`, `>`, `!=`; opcional |
| `value` | Texto | `0` | opcional |

### If Tilt

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_if_tilt` |
| **Ícone** | 📐 |
| **Categoria** | micro:bit |

Compare an accelerometer axis (milli-g, -2048..2048) with a value

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `axis` | Escolha | `x` | Opções: `x`, `y`, `z` |
| `comparison` | Escolha | `>` | Opções: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Texto | `300` |  |

### Play Melody

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_play_melody` |
| **Ícone** | 🎵 |
| **Categoria** | micro:bit |

Play a built-in melody (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, RINGTONE, FUNK, BLUES, BIRTHDAY, WEDDING, FUNERAL, PUNCHLINE, PYTHON, BADDY, CHASE, BA_DING, WAWAWAWAA, JUMP_UP, JUMP_DOWN, POWER_UP, POWER_DOWN) or your own notes such as "C4:4 E G C5:8 R:4" (note, octave, :length; R is a rest)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `melody` | Texto | `DADADADUM` | Built-in name, or notes separated by spaces |
| `tempo` | Texto | `120` | opcional |

### Play Tone

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_play_tone` |
| **Ícone** | 🔔 |
| **Categoria** | micro:bit |

Beep at a frequency for a number of milliseconds. Sounds queue and play one after another

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `frequency` | Texto | `440` | Pitch in hertz (440 = the note A) |
| `duration` | Texto | `500` | opcional |

### Read Sensor

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_read_sensor` |
| **Ícone** | 📡 |
| **Categoria** | micro:bit |

Read a micro:bit sensor into a variable of this object (or a global variable if the name starts with "global.")

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sensor` | Escolha | `accelerometer x` | Opções: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Texto | `sensor_value` | Variable that receives the reading |

### Scroll Text

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_scroll_text` |
| **Ícone** | 🔤 |
| **Categoria** | micro:bit |

Scroll text across the LED display. Put literal text in double quotes ("Hello"); otherwise a dash or plus is read as arithmetic. Accented letters show as ? as on the real board

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `text` | Texto | `"Hello"` | Text or expression to scroll |
| `delay` | Número | `150` | Scroll speed (MicroPython default 150); opcional |

### Send Radio Message

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_radio_send` |
| **Ícone** | 📻 |
| **Categoria** | micro:bit |

Send a number or text to the other micro:bits in the same group (not to this one). They get the Radio Message Received event, with the value in radio_number and radio_string. Put literal text in double quotes; text is cut to 32 characters

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Texto | `1` | A number, an expression or quoted text |

### Set Display Brightness

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_set_brightness` |
| **Ícone** | 🔆 |
| **Categoria** | micro:bit |

Overall LED brightness, 0 (dark) to 255 (full)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `brightness` | Texto | `255` |  |

### Set LED

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_set_pixel` |
| **Ícone** | 💡 |
| **Categoria** | micro:bit |

Light one LED now (x and y are 0-4, brightness 0-9)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `brightness` | Texto | `9` | opcional |

### Set Radio Group

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_radio_set_group` |
| **Ícone** | 📡 |
| **Categoria** | micro:bit |

Choose the radio group (0-255). Only micro:bits in the same group hear each other; every board starts in group 0

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `group` | Texto | `0` |  |

### Show Image

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_show_image` |
| **Ícone** | ❤️ |
| **Categoria** | micro:bit |

Show an image on the LED display: a built-in name (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL...) or five rows of brightness digits such as "09090:99999:99999:09990:00900". Display actions queue and play one after another

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `image` | Texto | `HEART` | Built-in image name, or 5 rows of 5 digits (0-9) separated by colons |
| `hold` | Número | `0` | How long it stays before the next queued item (0 = until something else is shown); opcional |

### Show Number

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_show_number` |
| **Ícone** | 🔢 |
| **Categoria** | micro:bit |

Show a number: one digit stays still, longer numbers scroll

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Texto | `0` | Number or expression |

### Stop Sound

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_stop_sound` |
| **Ícone** | 🔇 |
| **Categoria** | micro:bit |

Silence the speaker and drop any queued sounds

*Parâmetros:* nenhum

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (21)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (6)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (8)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (14)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (3)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (18)
- [Desenho](Full-Action-Reference-Drawing_pt) (11)
- [Rede](Full-Action-Reference-Network-Actions_pt) (22)
- [Partículas](Full-Action-Reference-Particles_pt) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_pt) (5)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
