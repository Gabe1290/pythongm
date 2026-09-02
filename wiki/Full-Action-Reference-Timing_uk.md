# Час

*[Головна](Home_uk) | [Посібник із пресетів](Preset-Guide_uk) | [Довідник подій](Event-Reference_uk)*

> **Згенеровано автоматично** з реєстру дій IDE за допомогою `tools/gen_action_reference.py` — не редагуйте вручну; повторно запустіть генератор після зміни дій. Переклади взято з `tools/action_ref_i18n.py`.

### Pause Timeline

| Властивість | Значення |
|----------|-------|
| **Назва** | `pause_timeline` |
| **Значок** | ⏸️ |
| **Категорія** | Час |

Pause timeline playback at the current position

*Параметри:* немає

### Встановити будильник

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_alarm` |
| **Значок** | ⏰ |
| **Категорія** | Час |

Встановити будильник

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `alarm_number` | Число | `0` | Який будильник (0-11) |
| `steps` | Число | `30` | Кількість кроків до спрацювання будильника (30 = 0,5 с при 60 FPS) |

### Set Timeline

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_timeline` |
| **Значок** | ⏱️ |
| **Категорія** | Час |

Set this instance's timeline label and reset its position to 0 (bookkeeping only — see category note)

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `timeline` | Текст | — | A label for your own reference; not a resource lookup |

### Set Timeline Position

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_timeline_position` |
| **Значок** | ⏱️ |
| **Категорія** | Час |

Set (or offset) this instance's timeline position

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `position` | Число | `0` | Position in steps |
| `relative` | Так/Ні | Ні | Add to the current position instead of setting it absolutely |

### Set Timeline Speed

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_timeline_speed` |
| **Значок** | ⏱️ |
| **Категорія** | Час |

Set the timeline playback speed multiplier

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `speed` | Число | `1.0` | 1.0=normal, 0.5=half speed, 2.0=double speed |

### Пауза

| Властивість | Значення |
|----------|-------|
| **Назва** | `sleep` |
| **Значок** | 💤 |
| **Категорія** | Час |

Призупинити гру на певну кількість мілісекунд, потім продовжити. Звуки продовжують відтворюватися під час паузи (наприклад, щоб звук завершився перед зміною кімнати). Примітка: рендеринг та введення заморожені під час паузи, тому тримайте тривалість короткою

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `milliseconds` | Число | `1000` | Тривалість паузи в мілісекундах (1000 = 1 секунда) |

### Start Timeline

| Властивість | Значення |
|----------|-------|
| **Назва** | `start_timeline` |
| **Значок** | ▶️ |
| **Категорія** | Час |

Begin or resume timeline playback from the current position

*Параметри:* немає

### Stop Timeline

| Властивість | Значення |
|----------|-------|
| **Назва** | `stop_timeline` |
| **Значок** | ⏹️ |
| **Категорія** | Час |

Stop timeline playback and reset the position to 0

*Параметри:* немає

---

## Інші Категорії

- [Рух](Full-Action-Reference-Movement_uk) (20)
- [Екземпляр](Full-Action-Reference-Instance_uk) (12)
- [Рахунок](Full-Action-Reference-Score_uk) (11)
- [Кімната](Full-Action-Reference-Room_uk) (13)
- [Аудіо](Full-Action-Reference-Audio_uk) (6)
- [Гра](Full-Action-Reference-Game_uk) (25)
- [Керування](Full-Action-Reference-Control_uk) (19)
- [Сітка](Full-Action-Reference-Grid_uk) (4)
- [Вигляди](Full-Action-Reference-Views_uk) (2)
- [3D-вигляд](Full-Action-Reference-3D-View-Actions_uk) (16)
- [Particles](Full-Action-Reference-Particles_uk) (8)
- [Réseau](Full-Action-Reference-Network-Actions_uk) (15)

[← Назад до Повного Довідника Дій](Full-Action-Reference_uk)
