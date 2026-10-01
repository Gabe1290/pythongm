# Середній Пресет

*[Головна](Home_uk) | [Посібник з Пресетів](Preset-Guide_uk) | [Пресет для Початківців](Beginner-Preset_uk)*

> **Автоматично згенеровано** з `get_intermediate()` у `config/blockly_config.py` за допомогою `tools/gen_preset_docs.py` — не редагуйте вручну; запустіть генератор знову після зміни пресету.

> **Що цей пресет насправді обмежує:** цей пресет фільтрує ОДНОЧАСНО візуальну палітру блоків Blockly ТА меню «Додати подію»/«Додати дію» структурованої панелі Події/Дії — незалежно від того, який редактор ви використовуєте, з'являються лише події/дії, перелічені нижче. Пресет *проєкту* встановлюється двома способами: **`Налаштування > IDE Edition`** вибирає типовий пресет для *нових* проєктів (видання Початківець -> цей пресет; наявні проєкти ніколи не змінюються при перемиканні видання), а **`Інструменти > Налаштувати блоки дій...`** змінює пресет *поточно відкритого* проєкту в будь-який момент. Типове видання IDE — Початківець, тому нові проєкти чистої інсталяції починаються саме з цього списку.

## Огляд

Цей пресет вмикає **21** типів подій і **118** типів дій.

---

## Події

| Подія | Назва Блоку | Категорія | Опис |
|-------|------------|----------|-------------|
| Create | `create` | Об'єкт | Виконується один раз, коли екземпляр вперше створюється |
| Destroy | `destroy` | Об'єкт | Виконується, коли екземпляр знищується |
| Step | `step` | Об'єкт | Виконується щокадру (використовуйте для безперервних перевірок) |
| Keyboard (held) | `keyboard` | Введення | Виконується безперервно, поки клавіша утримується (для плавного руху) |
| Keyboard <No Key> | `keyboard_no_key` | Введення | Виконується, коли наразі не натиснуто жодної клавіші |
| Keyboard Press | `keyboard_press` | Введення | Виконується один раз, коли клавішу вперше натиснуто (для руху по сітці) |
| Collision With... | `collision` | Зіткнення | Виконується при зіткненні з іншим об'єктом |
| Begin Step | `begin_step` | Крок | Виконується на початку кожного кроку, перед іншими подіями |
| End Step | `end_step` | Крок | Виконується наприкінці кожного кроку, після зіткнень, але перед малюванням |
| Alarm | `alarm` | Час | Виконується, коли таймер будильника досягає нуля |
| Draw | `draw` | Малювання | Виконується під час малювання об'єкта (замінює стандартне малювання спрайту) |
| Draw GUI | `draw_gui` | Малювання | Малюється поверх усього іншого (не залежить від камери/вигляду). Використовуйте для HUD, рахунку, життів. |
| Room End | `room_end` | Кімната | Виконується, коли кімната завершується |
| Room Start | `room_start` | Кімната | Виконується, коли кімната починається (після подій Create) |
| Game End | `game_end` | Гра | Виконується, коли гра завершується |
| Game Start | `game_start` | Гра | Виконується, коли гра починається (лише у першій кімнаті) |
| Animation End | `animation_end` | Інше | Спрацьовує, коли анімація спрайту досягає останнього кадру і повторюється |
| Intersect Boundary | `intersect_boundary` | Інше | Виконується, коли екземпляр торкається межі кімнати |
| No More Health | `no_more_health` | Інше | Виконується, коли здоров'я досягає 0 або менше |
| No More Lives | `no_more_lives` | Інше | Виконується, коли життя досягають 0 або менше |
| Outside Room | `outside_room` | Інше | Виконується, коли екземпляр повністю за межами кімнати |

---

## Дії

### Рух

| Дія | Назва Блоку | Параметри |
|--------|------------|------------|
| Відскок | `bounce` | — |
| Перейти до позиції | `jump_to_position` | `x`, `y`, `relative` |
| Перейти до випадкової позиції | `jump_to_random` | `snap_h`, `snap_v` |
| Перейти до стартової позиції | `jump_to_start` | — |
| Рух по сітці | `move_grid` | `direction`, `grid_size` |
| Рух до точки | `move_towards_point` | `x`, `y`, `speed` |
| Рух до контакту | `move_to_contact` | `direction`, `max_distance`, `object` |
| Обернути горизонтально | `reverse_horizontal` | — |
| Обернути вертикально | `reverse_vertical` | — |
| Задати напрямок і швидкість | `set_direction_speed` | `direction`, `speed` |
| Задати тертя | `set_friction` | `friction` |
| Задати гравітацію | `set_gravity` | `direction`, `gravity` |
| Задати горизонтальну швидкість | `set_hspeed` | `speed` |
| Задати вертикальну швидкість | `set_vspeed` | `speed` |
| Почати рух (напрямок) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Зупинити рух | `stop_movement` | — |

### Сітка

| Дія | Назва Блоку | Параметри |
|--------|------------|------------|
| Якщо на сітці | `if_on_grid` | `grid_size`, `then_actions`, `else_actions` |
| Прив'язати до сітки | `snap_to_grid` | `grid_size` |
| Перевірити вирівнювання по сітці | `test_alignment` | `hsnap`, `vsnap` |

### Екземпляр

| Дія | Назва Блоку | Параметри |
|--------|------------|------------|
| Змінити екземпляр | `change_instance` | `object`, `perform_events` |
| Створити екземпляр | `create_instance` | `object`, `x`, `y`, `relative` |
| Створити рухомий екземпляр | `create_moving_instance` | `object`, `x`, `y`, `speed`, `direction` |
| Створити випадковий екземпляр | `create_random_instance` | `x`, `y`, `object1`, `object2`, `object3`, `object4` |
| Знищити екземпляр | `destroy_instance` | — |
| Знищити в позиції | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Задати індекс зображення | `set_image_index` | `frame` |
| Задати швидкість зображення | `set_image_speed` | `speed` |
| Задати спрайт | `set_sprite` | `sprite`, `subimage`, `speed` |
| Запустити анімацію | `start_animation` | — |
| Зупинити анімацію | `stop_animation` | — |
| Перевірити кількість екземплярів | `test_instance_count` | `object`, `number`, `operation` |

### Рахунок

| Дія | Назва Блоку | Параметри |
|--------|------------|------------|
| Очистити таблицю рекордів | `clear_highscore` | — |
| Намалювати смугу здоров'я | `draw_health_bar` | `x1`, `y1`, `x2`, `y2`, `back_color`, `bar_color` |
| Намалювати життя | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Намалювати рахунок | `draw_score` | `x`, `y`, `caption`, `relative` |
| Задати здоров'я | `set_health` | `value`, `relative` |
| Задати життя | `set_lives` | `value`, `relative` |
| Задати рахунок | `set_score` | `value`, `relative` |
| Показати таблицю рекордів | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |
| Перевірити здоров'я | `test_health` | `operation`, `value` |
| Перевірити життя | `test_lives` | `value`, `operation` |
| Перевірити рахунок | `test_score` | `value`, `operation` |

### Час

| Дія | Назва Блоку | Параметри |
|--------|------------|------------|
| Призупинити шкалу | `pause_timeline` | — |
| Встановити будильник | `set_alarm` | `alarm_number`, `steps` |
| Задати часову шкалу | `set_timeline` | `timeline` |
| Задати позицію на шкалі | `set_timeline_position` | `position`, `relative` |
| Задати швидкість шкали | `set_timeline_speed` | `speed` |
| Пауза | `sleep` | `milliseconds` |
| Запустити шкалу | `start_timeline` | — |
| Зупинити шкалу | `stop_timeline` | — |

### Кімната

| Дія | Назва Блоку | Параметри |
|--------|------------|------------|
| Перевірити кімнату | `check_room` | `room`, `not_flag` |
| Завершити гру | `game_end` | — |
| Перейти до кімнати | `goto_room` | `room`, `transition` |
| Якщо існує наступна кімната | `if_next_room_exists` | `then_actions`, `else_actions` |
| Якщо існує попередня кімната | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Наступна кімната | `next_room` | — |
| Попередня кімната | `previous_room` | — |
| Перезапустити кімнату | `restart_room` | — |
| Задати фон | `set_background` | `background`, `visible`, `foreground`, `tiled_h`, `tiled_v`, `hspeed`, `vspeed` |
| Задати колір фону | `set_background_color` | `color`, `show_color` |
| Задати заголовок кімнати | `set_room_caption` | `caption` |
| Задати постійність кімнати | `set_room_persistent` | `persistent` |
| Задати швидкість кімнати | `set_room_speed` | `speed` |

### Аудіо

| Дія | Назва Блоку | Параметри |
|--------|------------|------------|
| Перевірити відтворення звуку | `check_sound` | `sound`, `not_flag` |
| Відтворити музику | `play_music` | `music`, `loop`, `volume` |
| Відтворити звук | `play_sound` | `sound`, `volume` |
| Задати гучність | `set_volume` | `volume` |
| Зупинити музику | `stop_music` | — |
| Зупинити звук | `stop_sound` | `sound` |

### Гра

| Дія | Назва Блоку | Параметри |
|--------|------------|------------|
| Намалювати стрілку | `draw_arrow` | `x1`, `y1`, `x2`, `y2`, `tip_size` |
| Намалювати тло | `draw_background` | `background`, `x`, `y`, `tiled` |
| Намалювати еліпс | `draw_ellipse` | `x1`, `y1`, `x2`, `y2`, `filled` |
| Намалювати лінію | `draw_line` | `x1`, `y1`, `x2`, `y2` |
| Намалювати масштабований текст | `draw_scaled_text` | `text`, `x`, `y`, `xscale`, `yscale` |
| Намалювати спрайт | `draw_sprite` | `sprite`, `x`, `y`, `subimage` |
| Намалювати текст | `draw_text` | `text`, `x`, `y`, `relative`, `color` |
| Намалювати змінну | `draw_variable` | `x`, `y`, `variable` |
| Заповнити екран кольором | `fill_color` | `color` |
| Завантажити гру | `load_game` | `filename` |
| Відкрити вебсторінку | `open_webpage` | `url` |
| Перезапустити гру | `restart_game` | — |
| Зберегти гру | `save_game` | `filename` |
| Задати колір | `set_color` | `color`, `alpha` |
| Задати колір малювання | `set_draw_color` | `color` |
| Задати шрифт малювання | `set_draw_font` | `font`, `halign`, `valign` |
| Задати заголовок вікна | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Показати інформацію про гру | `show_info` | — |
| Показати повідомлення | `show_message` | `message` |
| Показати відео | `show_video` | `filename`, `fullscreen` |
| Заставка: показати зображення | `splash_show_image` | `image` |
| Заставка: показати текст | `splash_show_text` | `text` |

### Керування

| Дія | Назва Блоку | Параметри |
|--------|------------|------------|
| Перевірити на порожнечу | `check_empty` | `x`, `y`, `relative`, `objects` |
| Коментар | `comment` | `text` |
| Інакше | `else_action` | — |
| Кінець блоку | `end_block` | — |
| Виконати код | `execute_code` | `code` |
| Виконати скрипт | `execute_script` | `script`, `arg0`, `arg1`, `arg2`, `arg3`, `arg4` |
| Вийти з події | `exit_event` | — |
| Якщо можна штовхнути | `if_can_push` | `direction`, `object_type`, `then_action`, `else_action` |
| Якщо зіткнення | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Якщо зіткнення в | `if_collision_at` | `x`, `y`, `object_type`, `then_actions`, `else_actions` |
| Якщо об'єкт існує | `if_object_exists` | `object`, `not_flag` |
| Повторити | `repeat` | `times`, `actions` |
| Початок блоку | `start_block` | — |
| Перевірити шанс | `test_chance` | `sides` |
| Перевірити вираз | `test_expression` | `expression`, `then_actions`, `else_actions` |
| Поставити запитання | `test_question` | `question` |
| Перевірити змінну | `test_variable` | `variable`, `value`, `scope`, `operation` |

### Вигляди

| Дія | Назва Блоку | Параметри |
|--------|------------|------------|
| Увімкнути вигляди | `enable_views` | `enable` |
| Налаштувати вигляд | `set_view` | `view`, `visible`, `view_x`, `view_y`, `view_w`, `view_h`, `port_x`, `port_y`, `port_w`, `port_h`, `follow`, `hborder`, `vborder`, `hspeed`, `vspeed` |

### Частки

| Дія | Назва Блоку | Параметри |
|--------|------------|------------|
| Випустити частки | `burst_particles` | `particle_type`, `number` |
| Очистити частки | `clear_particles` | — |
| Створити випромінювач | `create_emitter` | `x`, `y`, `width`, `height`, `shape` |
| Створити систему часток | `create_particle_system` | `depth` |
| Створити тип часток | `create_particle_type` | `sprite`, `size_min`, `size_max`, `size_increase`, `color`, `alpha`, `speed_min`, `speed_max`, `direction_min`, `direction_max`, `life_min`, `life_max` |
| Видалити випромінювач | `destroy_emitter` | — |
| Видалити систему часток | `destroy_particle_system` | — |
| Випускати частки потоком | `stream_particles` | `particle_type`, `number` |

---

## Дивіться Також

- [Посібник з Пресетів](Preset-Guide_uk) — що таке пресети і як їх змінити
- [Довідник Подій](Event-Reference_uk) — повний опис кожної події
- [Повний Довідник Дій](Full-Action-Reference_uk) — повні деталі параметрів для кожної дії
- [Пресет для Початківців](Beginner-Preset_uk) — рівень нижче цього
