# micro:bit

*[Главная](Home_ru) | [Руководство по пресетам](Preset-Guide_ru) | [Справочник событий](Event-Reference_ru)*

> **Сгенерировано автоматически** из реестра действий IDE с помощью `tools/gen_action_reference.py` — не редактируйте вручную; повторно запустите генератор после изменения действий. Переводы взяты из `tools/action_ref_i18n.py`.

### Clear Display

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_clear_display` |
| **Значок** | ⬛ |
| **Категория** | micro:bit |

Turn every LED off and drop anything still queued

*Параметры:* нет

### If Button Pressed

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_if_button` |
| **Значок** | 🔘 |
| **Категория** | micro:bit |

True while the button is held down (A+B = both)

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `button` | Выбор | `a` | Варианты: `a`, `b`, `ab`, `logo` |

### If Gesture

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_if_gesture` |
| **Значок** | 🤝 |
| **Категория** | micro:bit |

True while the board is in this gesture or posture

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `gesture` | Выбор | `shake` | Варианты: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### If LED Brightness

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_if_pixel` |
| **Значок** | 🔍 |
| **Категория** | micro:bit |

Compare one LED's brightness (0-9) with a value; the default asks "is it lit?"

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `x` | Текст | `0` |  |
| `y` | Текст | `0` |  |
| `comparison` | Выбор | `>` | Варианты: `<`, `<=`, `==`, `>=`, `>`, `!=`; необязательно |
| `value` | Текст | `0` | необязательно |

### If Tilt

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_if_tilt` |
| **Значок** | 📐 |
| **Категория** | micro:bit |

Compare an accelerometer axis (milli-g, -2048..2048) with a value

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `axis` | Выбор | `x` | Варианты: `x`, `y`, `z` |
| `comparison` | Выбор | `>` | Варианты: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Текст | `300` |  |

### Play Melody

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_play_melody` |
| **Значок** | 🎵 |
| **Категория** | micro:bit |

Play a built-in melody (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, RINGTONE, FUNK, BLUES, BIRTHDAY, WEDDING, FUNERAL, PUNCHLINE, PYTHON, BADDY, CHASE, BA_DING, WAWAWAWAA, JUMP_UP, JUMP_DOWN, POWER_UP, POWER_DOWN) or your own notes such as "C4:4 E G C5:8 R:4" (note, octave, :length; R is a rest)

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `melody` | Текст | `DADADADUM` | Built-in name, or notes separated by spaces |
| `tempo` | Текст | `120` | необязательно |

### Play Tone

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_play_tone` |
| **Значок** | 🔔 |
| **Категория** | micro:bit |

Beep at a frequency for a number of milliseconds. Sounds queue and play one after another

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `frequency` | Текст | `440` | Pitch in hertz (440 = the note A) |
| `duration` | Текст | `500` | необязательно |

### Read Sensor

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_read_sensor` |
| **Значок** | 📡 |
| **Категория** | micro:bit |

Read a micro:bit sensor into a variable of this object (or a global variable if the name starts with "global.")

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `sensor` | Выбор | `accelerometer x` | Варианты: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Текст | `sensor_value` | Variable that receives the reading |

### Scroll Text

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_scroll_text` |
| **Значок** | 🔤 |
| **Категория** | micro:bit |

Scroll text across the LED display. Put literal text in double quotes ("Hello"); otherwise a dash or plus is read as arithmetic. Accented letters show as ? as on the real board

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `text` | Текст | `"Hello"` | Text or expression to scroll |
| `delay` | Число | `150` | Scroll speed (MicroPython default 150); необязательно |

### Send Radio Message

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_radio_send` |
| **Значок** | 📻 |
| **Категория** | micro:bit |

Send a number or text to the other micro:bits in the same group (not to this one). They get the Radio Message Received event, with the value in radio_number and radio_string. Put literal text in double quotes; text is cut to 32 characters

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `value` | Текст | `1` | A number, an expression or quoted text |

### Set Display Brightness

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_set_brightness` |
| **Значок** | 🔆 |
| **Категория** | micro:bit |

Overall LED brightness, 0 (dark) to 255 (full)

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `brightness` | Текст | `255` |  |

### Set LED

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_set_pixel` |
| **Значок** | 💡 |
| **Категория** | micro:bit |

Light one LED now (x and y are 0-4, brightness 0-9)

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `x` | Текст | `0` |  |
| `y` | Текст | `0` |  |
| `brightness` | Текст | `9` | необязательно |

### Set Radio Group

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_radio_set_group` |
| **Значок** | 📡 |
| **Категория** | micro:bit |

Choose the radio group (0-255). Only micro:bits in the same group hear each other; every board starts in group 0

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `group` | Текст | `0` |  |

### Show Image

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_show_image` |
| **Значок** | ❤️ |
| **Категория** | micro:bit |

Show an image on the LED display: a built-in name (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL...) or five rows of brightness digits such as "09090:99999:99999:09990:00900". Display actions queue and play one after another

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `image` | Текст | `HEART` | Built-in image name, or 5 rows of 5 digits (0-9) separated by colons |
| `hold` | Число | `0` | How long it stays before the next queued item (0 = until something else is shown); необязательно |

### Show Number

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_show_number` |
| **Значок** | 🔢 |
| **Категория** | micro:bit |

Show a number: one digit stays still, longer numbers scroll

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `value` | Текст | `0` | Number or expression |

### Stop Sound

| Свойство | Значение |
|----------|-------|
| **Имя** | `microbit_stop_sound` |
| **Значок** | 🔇 |
| **Категория** | micro:bit |

Silence the speaker and drop any queued sounds

*Параметры:* нет

---

## Другие Категории

- [Движение](Full-Action-Reference-Movement_ru) (21)
- [Экземпляр](Full-Action-Reference-Instance_ru) (12)
- [Счёт](Full-Action-Reference-Score_ru) (6)
- [Комната](Full-Action-Reference-Room_ru) (13)
- [Время](Full-Action-Reference-Timing_ru) (8)
- [Аудио](Full-Action-Reference-Audio_ru) (6)
- [Игра](Full-Action-Reference-Game_ru) (14)
- [Управление](Full-Action-Reference-Control_ru) (19)
- [Сетка](Full-Action-Reference-Grid_ru) (3)
- [Виды](Full-Action-Reference-Views_ru) (2)
- [3D-вид](Full-Action-Reference-3D-View-Actions_ru) (18)
- [Рисование](Full-Action-Reference-Drawing_ru) (11)
- [Сеть](Full-Action-Reference-Network-Actions_ru) (22)
- [Частицы](Full-Action-Reference-Particles_ru) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_ru) (5)

[← Назад к Полному Справочнику Действий](Full-Action-Reference_ru)
