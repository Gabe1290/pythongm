# Время

*[Главная](Home_ru) | [Руководство по пресетам](Preset-Guide_ru) | [Справочник событий](Event-Reference_ru)*

> **Сгенерировано автоматически** из реестра действий IDE с помощью `tools/gen_action_reference.py` — не редактируйте вручную; повторно запустите генератор после изменения действий. Переводы взяты из `tools/action_ref_i18n.py`.

### Pause Timeline

| Свойство | Значение |
|----------|-------|
| **Имя** | `pause_timeline` |
| **Значок** | ⏸️ |
| **Категория** | Время |

Pause timeline playback at the current position

*Параметры:* нет

### Установить будильник

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_alarm` |
| **Значок** | ⏰ |
| **Категория** | Время |

Установить будильник

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `alarm_number` | Число | `0` | Какой будильник (0-11) |
| `steps` | Число | `30` | Количество шагов до срабатывания будильника (30 = 0,5 с при 60 FPS) |

### Set Timeline

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_timeline` |
| **Значок** | ⏱️ |
| **Категория** | Время |

Set this instance's timeline label and reset its position to 0 (bookkeeping only — see category note)

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `timeline` | Текст | — | A label for your own reference; not a resource lookup |

### Set Timeline Position

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_timeline_position` |
| **Значок** | ⏱️ |
| **Категория** | Время |

Set (or offset) this instance's timeline position

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `position` | Число | `0` | Position in steps |
| `relative` | Да/Нет | Нет | Add to the current position instead of setting it absolutely |

### Set Timeline Speed

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_timeline_speed` |
| **Значок** | ⏱️ |
| **Категория** | Время |

Set the timeline playback speed multiplier

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `speed` | Число | `1.0` | 1.0=normal, 0.5=half speed, 2.0=double speed |

### Пауза

| Свойство | Значение |
|----------|-------|
| **Имя** | `sleep` |
| **Значок** | 💤 |
| **Категория** | Время |

Приостановить игру на определённое количество миллисекунд, затем продолжить. Звуки продолжают воспроизводиться во время паузы (например, чтобы звук завершился перед сменой комнаты). Примечание: рендеринг и ввод заморожены во время паузы, поэтому держите длительность короткой

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `milliseconds` | Число | `1000` | Длительность паузы в миллисекундах (1000 = 1 секунда) |

### Start Timeline

| Свойство | Значение |
|----------|-------|
| **Имя** | `start_timeline` |
| **Значок** | ▶️ |
| **Категория** | Время |

Begin or resume timeline playback from the current position

*Параметры:* нет

### Stop Timeline

| Свойство | Значение |
|----------|-------|
| **Имя** | `stop_timeline` |
| **Значок** | ⏹️ |
| **Категория** | Время |

Stop timeline playback and reset the position to 0

*Параметры:* нет

---

## Другие Категории

- [Движение](Full-Action-Reference-Movement_ru) (20)
- [Экземпляр](Full-Action-Reference-Instance_ru) (12)
- [Счёт](Full-Action-Reference-Score_ru) (11)
- [Комната](Full-Action-Reference-Room_ru) (13)
- [Аудио](Full-Action-Reference-Audio_ru) (6)
- [Игра](Full-Action-Reference-Game_ru) (25)
- [Управление](Full-Action-Reference-Control_ru) (19)
- [Сетка](Full-Action-Reference-Grid_ru) (4)
- [Виды](Full-Action-Reference-Views_ru) (2)
- [3D-вид](Full-Action-Reference-3D-View-Actions_ru) (16)
- [Particles](Full-Action-Reference-Particles_ru) (8)
- [Réseau](Full-Action-Reference-Network-Actions_ru) (15)

[← Назад к Полному Справочнику Действий](Full-Action-Reference_ru)
