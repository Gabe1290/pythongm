# Средний Пресет

*[Главная](Home_ru) | [Руководство по Пресетам](Preset-Guide_ru) | [Пресет для Начинающих](Beginner-Preset_ru)*

> **Автоматически сгенерировано** из `get_intermediate()` в `config/blockly_config.py` с помощью `tools/gen_preset_docs.py` — не редактируйте вручную; запустите генератор заново после изменения пресета.

> **Что этот пресет на самом деле ограничивает:** этот пресет фильтрует ОДНОВРЕМЕННО визуальную палитру блоков Blockly И меню «Добавить событие»/«Добавить действие» структурированной панели События/Действия — независимо от того, каким редактором вы пользуетесь, появляются только события/действия, перечисленные ниже. Пресет *проекта* задаётся двумя способами: **`Настройки > IDE Edition`** выбирает пресет по умолчанию для *новых* проектов (издание Начинающий -> этот пресет; существующие проекты никогда не меняются при смене издания), а **`Инструменты > Настроить блоки действий...`** меняет пресет *текущего открытого* проекта в любой момент. Издание IDE по умолчанию — Начинающий, поэтому новые проекты чистой установки начинаются именно с этого списка.

## Обзор

Этот пресет включает **21** типов событий и **118** типов действий.

---

## События

| Событие | Имя Блока | Категория | Описание |
|-------|------------|----------|-------------|
| Create | `create` | Объект | Выполняется один раз при первом создании экземпляра |
| Destroy | `destroy` | Объект | Выполняется при уничтожении экземпляра |
| Step | `step` | Объект | Выполняется на каждом кадре (используйте для непрерывных проверок) |
| Keyboard (held) | `keyboard` | Ввод | Выполняется непрерывно, пока клавиша удерживается (для плавного движения) |
| Keyboard <No Key> | `keyboard_no_key` | Ввод | Выполняется, когда в данный момент не нажата ни одна клавиша |
| Keyboard Press | `keyboard_press` | Ввод | Выполняется один раз при первом нажатии клавиши (для движения по сетке) |
| Collision With... | `collision` | Столкновение | Выполняется при столкновении с другим объектом |
| Begin Step | `begin_step` | Шаг | Выполняется в начале каждого шага, перед другими событиями |
| End Step | `end_step` | Шаг | Выполняется в конце каждого шага, после столкновений, но перед отрисовкой |
| Alarm | `alarm` | Время | Выполняется, когда таймер будильника достигает нуля |
| Draw | `draw` | Рисование | Выполняется при отрисовке объекта (заменяет стандартную отрисовку спрайта) |
| Draw GUI | `draw_gui` | Рисование | Рисуется поверх всего остального (не зависит от камеры/вида). Используйте для HUD, счёта, жизней. |
| Room End | `room_end` | Комната | Выполняется при завершении комнаты |
| Room Start | `room_start` | Комната | Выполняется при запуске комнаты (после событий Create) |
| Game End | `game_end` | Игра | Выполняется при завершении игры |
| Game Start | `game_start` | Игра | Выполняется при запуске игры (только в первой комнате) |
| Animation End | `animation_end` | Другое | Срабатывает, когда анимация спрайта достигает последнего кадра и начинается заново |
| Intersect Boundary | `intersect_boundary` | Другое | Выполняется, когда экземпляр касается границы комнаты |
| No More Health | `no_more_health` | Другое | Выполняется, когда здоровье достигает 0 или меньше |
| No More Lives | `no_more_lives` | Другое | Выполняется, когда жизни достигают 0 или меньше |
| Outside Room | `outside_room` | Другое | Выполняется, когда экземпляр полностью за пределами комнаты |

---

## Действия

### Движение

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Отскок | `bounce` | — |
| Перейти к позиции | `jump_to_position` | `x`, `y`, `relative` |
| Перейти в случайную позицию | `jump_to_random` | `snap_h`, `snap_v` |
| Перейти к стартовой позиции | `jump_to_start` | — |
| Движение по сетке | `move_grid` | `direction`, `grid_size` |
| Движение к точке | `move_towards_point` | `x`, `y`, `speed` |
| Движение до контакта | `move_to_contact` | `direction`, `max_distance`, `object` |
| Обратить горизонтально | `reverse_horizontal` | — |
| Обратить вертикально | `reverse_vertical` | — |
| Задать направление и скорость | `set_direction_speed` | `direction`, `speed` |
| Задать трение | `set_friction` | `friction` |
| Задать гравитацию | `set_gravity` | `direction`, `gravity` |
| Задать горизонтальную скорость | `set_hspeed` | `speed` |
| Задать вертикальную скорость | `set_vspeed` | `speed` |
| Начать движение (направление) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Остановить движение | `stop_movement` | — |

### Сетка

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Если на сетке | `if_on_grid` | `grid_size`, `then_actions`, `else_actions` |
| Привязать к сетке | `snap_to_grid` | `grid_size` |
| Проверить выравнивание по сетке | `test_alignment` | `hsnap`, `vsnap` |

### Экземпляр

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Изменить экземпляр | `change_instance` | `object`, `perform_events` |
| Создать экземпляр | `create_instance` | `object`, `x`, `y`, `relative` |
| Создать движущийся экземпляр | `create_moving_instance` | `object`, `x`, `y`, `speed`, `direction` |
| Создать случайный экземпляр | `create_random_instance` | `x`, `y`, `object1`, `object2`, `object3`, `object4` |
| Уничтожить экземпляр | `destroy_instance` | — |
| Уничтожить в позиции | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Задать индекс изображения | `set_image_index` | `frame` |
| Задать скорость изображения | `set_image_speed` | `speed` |
| Задать спрайт | `set_sprite` | `sprite`, `subimage`, `speed` |
| Запустить анимацию | `start_animation` | — |
| Остановить анимацию | `stop_animation` | — |
| Проверить количество экземпляров | `test_instance_count` | `object`, `number`, `operation` |

### Счёт

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Очистить таблицу рекордов | `clear_highscore` | — |
| Нарисовать полосу здоровья | `draw_health_bar` | `x1`, `y1`, `x2`, `y2`, `back_color`, `bar_color` |
| Нарисовать жизни | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Нарисовать счёт | `draw_score` | `x`, `y`, `caption`, `relative` |
| Задать здоровье | `set_health` | `value`, `relative` |
| Задать жизни | `set_lives` | `value`, `relative` |
| Задать счёт | `set_score` | `value`, `relative` |
| Показать таблицу рекордов | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |
| Проверить здоровье | `test_health` | `operation`, `value` |
| Проверить жизни | `test_lives` | `value`, `operation` |
| Проверить счёт | `test_score` | `value`, `operation` |

### Время

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Приостановить шкалу | `pause_timeline` | — |
| Установить будильник | `set_alarm` | `alarm_number`, `steps` |
| Задать временную шкалу | `set_timeline` | `timeline` |
| Задать позицию на шкале | `set_timeline_position` | `position`, `relative` |
| Задать скорость шкалы | `set_timeline_speed` | `speed` |
| Пауза | `sleep` | `milliseconds` |
| Запустить шкалу | `start_timeline` | — |
| Остановить шкалу | `stop_timeline` | — |

### Комната

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Проверить комнату | `check_room` | `room`, `not_flag` |
| Завершить игру | `game_end` | — |
| Перейти в комнату | `goto_room` | `room`, `transition` |
| Если следующая комната существует | `if_next_room_exists` | `then_actions`, `else_actions` |
| Если предыдущая комната существует | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Следующая комната | `next_room` | — |
| Предыдущая комната | `previous_room` | — |
| Перезапустить комнату | `restart_room` | — |
| Задать фон | `set_background` | `background`, `visible`, `foreground`, `tiled_h`, `tiled_v`, `hspeed`, `vspeed` |
| Задать цвет фона | `set_background_color` | `color`, `show_color` |
| Задать заголовок комнаты | `set_room_caption` | `caption` |
| Задать постоянство комнаты | `set_room_persistent` | `persistent` |
| Задать скорость комнаты | `set_room_speed` | `speed` |

### Аудио

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Проверить воспроизведение звука | `check_sound` | `sound`, `not_flag` |
| Воспроизвести музыку | `play_music` | `music`, `loop`, `volume` |
| Воспроизвести звук | `play_sound` | `sound`, `volume` |
| Задать громкость | `set_volume` | `volume` |
| Остановить музыку | `stop_music` | — |
| Остановить звук | `stop_sound` | `sound` |

### Игра

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Нарисовать стрелку | `draw_arrow` | `x1`, `y1`, `x2`, `y2`, `tip_size` |
| Нарисовать фон | `draw_background` | `background`, `x`, `y`, `tiled` |
| Нарисовать эллипс | `draw_ellipse` | `x1`, `y1`, `x2`, `y2`, `filled` |
| Нарисовать линию | `draw_line` | `x1`, `y1`, `x2`, `y2` |
| Нарисовать масштабированный текст | `draw_scaled_text` | `text`, `x`, `y`, `xscale`, `yscale` |
| Нарисовать спрайт | `draw_sprite` | `sprite`, `x`, `y`, `subimage` |
| Нарисовать текст | `draw_text` | `text`, `x`, `y`, `relative`, `color` |
| Нарисовать переменную | `draw_variable` | `x`, `y`, `variable` |
| Заполнить экран цветом | `fill_color` | `color` |
| Загрузить игру | `load_game` | `filename` |
| Открыть веб-страницу | `open_webpage` | `url` |
| Перезапустить игру | `restart_game` | — |
| Сохранить игру | `save_game` | `filename` |
| Задать цвет | `set_color` | `color`, `alpha` |
| Задать цвет рисования | `set_draw_color` | `color` |
| Задать шрифт рисования | `set_draw_font` | `font`, `halign`, `valign` |
| Задать заголовок окна | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Показать информацию об игре | `show_info` | — |
| Показать сообщение | `show_message` | `message` |
| Показать видео | `show_video` | `filename`, `fullscreen` |
| Заставка: показать изображение | `splash_show_image` | `image` |
| Заставка: показать текст | `splash_show_text` | `text` |

### Управление

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Проверить на пустоту | `check_empty` | `x`, `y`, `relative`, `objects` |
| Комментарий | `comment` | `text` |
| Иначе | `else_action` | — |
| Конец блока | `end_block` | — |
| Выполнить код | `execute_code` | `code` |
| Выполнить скрипт | `execute_script` | `script`, `arg0`, `arg1`, `arg2`, `arg3`, `arg4` |
| Выйти из события | `exit_event` | — |
| Если можно толкнуть | `if_can_push` | `direction`, `object_type`, `then_action`, `else_action` |
| Если столкновение | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Если столкновение в | `if_collision_at` | `x`, `y`, `object_type`, `then_actions`, `else_actions` |
| Если объект существует | `if_object_exists` | `object`, `not_flag` |
| Повторить | `repeat` | `times`, `actions` |
| Начало блока | `start_block` | — |
| Проверить шанс | `test_chance` | `sides` |
| Проверить выражение | `test_expression` | `expression`, `then_actions`, `else_actions` |
| Задать вопрос | `test_question` | `question` |
| Проверить переменную | `test_variable` | `variable`, `value`, `scope`, `operation` |

### Виды

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Включить виды | `enable_views` | `enable` |
| Настроить вид | `set_view` | `view`, `visible`, `view_x`, `view_y`, `view_w`, `view_h`, `port_x`, `port_y`, `port_w`, `port_h`, `follow`, `hborder`, `vborder`, `hspeed`, `vspeed` |

### Частицы

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Выпустить частицы | `burst_particles` | `particle_type`, `number` |
| Очистить частицы | `clear_particles` | — |
| Создать источник | `create_emitter` | `x`, `y`, `width`, `height`, `shape` |
| Создать систему частиц | `create_particle_system` | `depth` |
| Создать тип частиц | `create_particle_type` | `sprite`, `size_min`, `size_max`, `size_increase`, `color`, `alpha`, `speed_min`, `speed_max`, `direction_min`, `direction_max`, `life_min`, `life_max` |
| Удалить источник | `destroy_emitter` | — |
| Удалить систему частиц | `destroy_particle_system` | — |
| Испускать частицы потоком | `stream_particles` | `particle_type`, `number` |

---

## Смотрите Также

- [Руководство по Пресетам](Preset-Guide_ru) — что такое пресеты и как их изменить
- [Справочник Событий](Event-Reference_ru) — полное описание каждого события
- [Полный Справочник Действий](Full-Action-Reference_ru) — полные сведения о параметрах для каждого действия
- [Пресет для Начинающих](Beginner-Preset_ru) — уровень ниже этого
