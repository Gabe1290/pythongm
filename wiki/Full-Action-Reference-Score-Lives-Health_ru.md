# Score/Lives/Health

*[Главная](Home_ru) | [Руководство по пресетам](Preset-Guide_ru) | [Справочник событий](Event-Reference_ru)*

> **Сгенерировано автоматически** из реестра действий IDE с помощью `tools/gen_action_reference.py` — не редактируйте вручную; повторно запустите генератор после изменения действий. Переводы взяты из `tools/action_ref_i18n.py`.

### Очистить таблицу рекордов

| Свойство | Значение |
|----------|-------|
| **Имя** | `clear_highscore` |
| **Значок** | 🗑️🏆 |
| **Категория** | Score/Lives/Health |

Очистить все записи таблицы рекордов

*Параметры:* нет

### Показать таблицу рекордов

| Свойство | Значение |
|----------|-------|
| **Имя** | `show_highscore` |
| **Значок** | 🏆 |
| **Категория** | Score/Lives/Health |

Показать диалог таблицы рекордов

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `background` | Цвет | `#FFFFDD` | Цвет фона диалога; необязательно |
| `new_color` | Цвет | `#FF0000` | Цвет для новой (квалифицированной) записи; необязательно |
| `other_color` | Цвет | `#000000` | Цвет для остальных записей; необязательно |
| `allow_new_entry` | Да/Нет | Да | Запросить имя, если текущий счёт квалифицируется |

### Проверить здоровье

| Свойство | Значение |
|----------|-------|
| **Имя** | `test_health` |
| **Значок** | ❓💚 |
| **Категория** | Score/Lives/Health |

Условие: сравнить текущее здоровье со значением

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `operation` | Выбор | `equal` | Оператор сравнения; Варианты: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |
| `value` | Число | `0` | Значение для сравнения |

### Проверить жизни

| Свойство | Значение |
|----------|-------|
| **Имя** | `test_lives` |
| **Значок** | ❓❤️ |
| **Категория** | Score/Lives/Health |

Условие: сравнить количество жизней со значением

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `value` | Число | `0` | Значение для сравнения |
| `operation` | Выбор | `equal` | Оператор сравнения; Варианты: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

### Проверить счёт

| Свойство | Значение |
|----------|-------|
| **Имя** | `test_score` |
| **Значок** | ❓🏆 |
| **Категория** | Score/Lives/Health |

Условие: сравнить счёт со значением

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `value` | Число | `0` | Значение для сравнения |
| `operation` | Выбор | `equal` | Оператор сравнения; Варианты: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

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
- [micro:bit](Full-Action-Reference-Microbit-Actions_ru) (16)

[← Назад к Полному Справочнику Действий](Full-Action-Reference_ru)
