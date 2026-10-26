# Score/Lives/Health

*[Головна](Home_uk) | [Посібник із пресетів](Preset-Guide_uk) | [Довідник подій](Event-Reference_uk)*

> **Згенеровано автоматично** з реєстру дій IDE за допомогою `tools/gen_action_reference.py` — не редагуйте вручну; повторно запустіть генератор після зміни дій. Переклади взято з `tools/action_ref_i18n.py`.

### Очистити таблицю рекордів

| Властивість | Значення |
|----------|-------|
| **Назва** | `clear_highscore` |
| **Значок** | 🗑️🏆 |
| **Категорія** | Score/Lives/Health |

Очистити всі записи таблиці рекордів

*Параметри:* немає

### Показати таблицю рекордів

| Властивість | Значення |
|----------|-------|
| **Назва** | `show_highscore` |
| **Значок** | 🏆 |
| **Категорія** | Score/Lives/Health |

Показати діалог таблиці рекордів

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `background` | Колір | `#FFFFDD` | Колір тла діалогу; необов'язково |
| `new_color` | Колір | `#FF0000` | Колір для нового (кваліфікованого) запису; необов'язково |
| `other_color` | Колір | `#000000` | Колір для інших записів; необов'язково |
| `allow_new_entry` | Так/Ні | Так | Запитати ім'я, якщо поточний рахунок кваліфікується |

### Перевірити здоров'я

| Властивість | Значення |
|----------|-------|
| **Назва** | `test_health` |
| **Значок** | ❓💚 |
| **Категорія** | Score/Lives/Health |

Умова: порівняти поточне здоров'я зі значенням

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `operation` | Вибір | `equal` | Оператор порівняння; Варіанти: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |
| `value` | Число | `0` | Значення для порівняння |

### Перевірити життя

| Властивість | Значення |
|----------|-------|
| **Назва** | `test_lives` |
| **Значок** | ❓❤️ |
| **Категорія** | Score/Lives/Health |

Умова: порівняти кількість життів зі значенням

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `value` | Число | `0` | Значення для порівняння |
| `operation` | Вибір | `equal` | Оператор порівняння; Варіанти: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

### Перевірити рахунок

| Властивість | Значення |
|----------|-------|
| **Назва** | `test_score` |
| **Значок** | ❓🏆 |
| **Категорія** | Score/Lives/Health |

Умова: порівняти рахунок зі значенням

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `value` | Число | `0` | Значення для порівняння |
| `operation` | Вибір | `equal` | Оператор порівняння; Варіанти: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

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
- [micro:bit](Full-Action-Reference-Microbit-Actions_uk) (16)

[← Назад до Повного Довідника Дій](Full-Action-Reference_uk)
