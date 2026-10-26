# Сетка

*[Главная](Home_ru) | [Руководство по пресетам](Preset-Guide_ru) | [Справочник событий](Event-Reference_ru)*

> **Сгенерировано автоматически** из реестра действий IDE с помощью `tools/gen_action_reference.py` — не редактируйте вручную; повторно запустите генератор после изменения действий. Переводы взяты из `tools/action_ref_i18n.py`.

### Если на сетке

| Свойство | Значение |
|----------|-------|
| **Имя** | `if_on_grid` |
| **Значок** | ▦ |
| **Категория** | Сетка |

Проверить, выровнен ли объект по сетке

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `grid_size` | Число | `32` | Размер клетки сетки в пикселях |
| `then_actions` | Список действий | — | Действия, если на сетке |
| `else_actions` | Список действий | — | Действия, если не на сетке |

### Привязать к сетке

| Свойство | Значение |
|----------|-------|
| **Имя** | `snap_to_grid` |
| **Значок** | ▦ |
| **Категория** | Сетка |

Выровнять позицию экземпляра по сетке

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `grid_size` | Число | `32` | Размер клетки сетки в пикселях |

### Остановить, если нет нажатых клавиш

| Свойство | Значение |
|----------|-------|
| **Имя** | `stop_if_no_keys` |
| **Значок** | ▦ |
| **Категория** | Сетка |

Остановить движение по сетке, когда не нажата ни одна клавиша движения (идеально для плавной привязки к сетке)

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `grid_size` | Число | `32` | Размер клетки сетки в пикселях |

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
- [Виды](Full-Action-Reference-Views_ru) (2)
- [3D-вид](Full-Action-Reference-3D-View-Actions_ru) (18)
- [Рисование](Full-Action-Reference-Drawing_ru) (11)
- [Сеть](Full-Action-Reference-Network-Actions_ru) (22)
- [Частицы](Full-Action-Reference-Particles_ru) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_ru) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_ru) (16)

[← Назад к Полному Справочнику Действий](Full-Action-Reference_ru)
