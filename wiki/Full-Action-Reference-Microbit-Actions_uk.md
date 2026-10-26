# micro:bit

*[Головна](Home_uk) | [Посібник із пресетів](Preset-Guide_uk) | [Довідник подій](Event-Reference_uk)*

> **Згенеровано автоматично** з реєстру дій IDE за допомогою `tools/gen_action_reference.py` — не редагуйте вручну; повторно запустіть генератор після зміни дій. Переклади взято з `tools/action_ref_i18n.py`.

### Clear Display

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_clear_display` |
| **Значок** | ⬛ |
| **Категорія** | micro:bit |

Turn every LED off and drop anything still queued

*Параметри:* немає

### If Button Pressed

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_if_button` |
| **Значок** | 🔘 |
| **Категорія** | micro:bit |

True while the button is held down (A+B = both)

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `button` | Вибір | `a` | Варіанти: `a`, `b`, `ab`, `logo` |

### If Gesture

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_if_gesture` |
| **Значок** | 🤝 |
| **Категорія** | micro:bit |

True while the board is in this gesture or posture

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `gesture` | Вибір | `shake` | Варіанти: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### If LED Brightness

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_if_pixel` |
| **Значок** | 🔍 |
| **Категорія** | micro:bit |

Compare one LED's brightness (0-9) with a value; the default asks "is it lit?"

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `x` | Текст | `0` |  |
| `y` | Текст | `0` |  |
| `comparison` | Вибір | `>` | Варіанти: `<`, `<=`, `==`, `>=`, `>`, `!=`; необов'язково |
| `value` | Текст | `0` | необов'язково |

### If Tilt

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_if_tilt` |
| **Значок** | 📐 |
| **Категорія** | micro:bit |

Compare an accelerometer axis (milli-g, -2048..2048) with a value

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `axis` | Вибір | `x` | Варіанти: `x`, `y`, `z` |
| `comparison` | Вибір | `>` | Варіанти: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Текст | `300` |  |

### Play Melody

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_play_melody` |
| **Значок** | 🎵 |
| **Категорія** | micro:bit |

Play a built-in melody (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, RINGTONE, FUNK, BLUES, BIRTHDAY, WEDDING, FUNERAL, PUNCHLINE, PYTHON, BADDY, CHASE, BA_DING, WAWAWAWAA, JUMP_UP, JUMP_DOWN, POWER_UP, POWER_DOWN) or your own notes such as "C4:4 E G C5:8 R:4" (note, octave, :length; R is a rest)

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `melody` | Текст | `DADADADUM` | Built-in name, or notes separated by spaces |
| `tempo` | Текст | `120` | необов'язково |

### Play Tone

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_play_tone` |
| **Значок** | 🔔 |
| **Категорія** | micro:bit |

Beep at a frequency for a number of milliseconds. Sounds queue and play one after another

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `frequency` | Текст | `440` | Pitch in hertz (440 = the note A) |
| `duration` | Текст | `500` | необов'язково |

### Read Sensor

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_read_sensor` |
| **Значок** | 📡 |
| **Категорія** | micro:bit |

Read a micro:bit sensor into a variable of this object (or a global variable if the name starts with "global.")

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `sensor` | Вибір | `accelerometer x` | Варіанти: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Текст | `sensor_value` | Variable that receives the reading |

### Scroll Text

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_scroll_text` |
| **Значок** | 🔤 |
| **Категорія** | micro:bit |

Scroll text across the LED display. Put literal text in double quotes ("Hello"); otherwise a dash or plus is read as arithmetic. Accented letters show as ? as on the real board

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `text` | Текст | `"Hello"` | Text or expression to scroll |
| `delay` | Число | `150` | Scroll speed (MicroPython default 150); необов'язково |

### Send Radio Message

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_radio_send` |
| **Значок** | 📻 |
| **Категорія** | micro:bit |

Send a number or text to the other micro:bits in the same group (not to this one). They get the Radio Message Received event, with the value in radio_number and radio_string. Put literal text in double quotes; text is cut to 32 characters

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `value` | Текст | `1` | A number, an expression or quoted text |

### Set Display Brightness

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_set_brightness` |
| **Значок** | 🔆 |
| **Категорія** | micro:bit |

Overall LED brightness, 0 (dark) to 255 (full)

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `brightness` | Текст | `255` |  |

### Set LED

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_set_pixel` |
| **Значок** | 💡 |
| **Категорія** | micro:bit |

Light one LED now (x and y are 0-4, brightness 0-9)

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `x` | Текст | `0` |  |
| `y` | Текст | `0` |  |
| `brightness` | Текст | `9` | необов'язково |

### Set Radio Group

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_radio_set_group` |
| **Значок** | 📡 |
| **Категорія** | micro:bit |

Choose the radio group (0-255). Only micro:bits in the same group hear each other; every board starts in group 0

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `group` | Текст | `0` |  |

### Show Image

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_show_image` |
| **Значок** | ❤️ |
| **Категорія** | micro:bit |

Show an image on the LED display: a built-in name (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL...) or five rows of brightness digits such as "09090:99999:99999:09990:00900". Display actions queue and play one after another

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `image` | Текст | `HEART` | Built-in image name, or 5 rows of 5 digits (0-9) separated by colons |
| `hold` | Число | `0` | How long it stays before the next queued item (0 = until something else is shown); необов'язково |

### Show Number

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_show_number` |
| **Значок** | 🔢 |
| **Категорія** | micro:bit |

Show a number: one digit stays still, longer numbers scroll

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `value` | Текст | `0` | Number or expression |

### Stop Sound

| Властивість | Значення |
|----------|-------|
| **Назва** | `microbit_stop_sound` |
| **Значок** | 🔇 |
| **Категорія** | micro:bit |

Silence the speaker and drop any queued sounds

*Параметри:* немає

---

## Інші Категорії

- [Рух](Full-Action-Reference-Movement_uk) (21)
- [Екземпляр](Full-Action-Reference-Instance_uk) (12)
- [Рахунок](Full-Action-Reference-Score_uk) (6)
- [Кімната](Full-Action-Reference-Room_uk) (13)
- [Час](Full-Action-Reference-Timing_uk) (8)
- [Аудіо](Full-Action-Reference-Audio_uk) (6)
- [Гра](Full-Action-Reference-Game_uk) (14)
- [Керування](Full-Action-Reference-Control_uk) (19)
- [Сітка](Full-Action-Reference-Grid_uk) (3)
- [Вигляди](Full-Action-Reference-Views_uk) (2)
- [3D-вигляд](Full-Action-Reference-3D-View-Actions_uk) (18)
- [Малювання](Full-Action-Reference-Drawing_uk) (11)
- [Мережа](Full-Action-Reference-Network-Actions_uk) (22)
- [Частки](Full-Action-Reference-Particles_uk) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_uk) (5)

[← Назад до Повного Довідника Дій](Full-Action-Reference_uk)
