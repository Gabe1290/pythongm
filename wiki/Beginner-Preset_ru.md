# Пресет для Начинающих

*[Главная](Home_ru) | [Руководство по Пресетам](Preset-Guide_ru) | [Средний Пресет](Intermediate-Preset_ru)*

> **Автоматически сгенерировано** из `get_beginner()` в `config/blockly_config.py` с помощью `tools/gen_preset_docs.py` — не редактируйте вручную; запустите генератор заново после изменения пресета.

> **Что этот пресет на самом деле ограничивает:** этот пресет фильтрует ОДНОВРЕМЕННО визуальную палитру блоков Blockly И меню «Добавить событие»/«Добавить действие» структурированной панели События/Действия — независимо от того, каким редактором вы пользуетесь, появляются только события/действия, перечисленные ниже. Пресет *проекта* задаётся двумя способами: **`Настройки > IDE Edition`** выбирает пресет по умолчанию для *новых* проектов (издание Начинающий -> этот пресет; существующие проекты никогда не меняются при смене издания), а **`Инструменты > Настроить блоки действий...`** меняет пресет *текущего открытого* проекта в любой момент. Издание IDE по умолчанию — Начинающий, поэтому новые проекты чистой установки начинаются именно с этого списка.

## Обзор

Этот пресет включает **19** типов событий и **83** типов действий.

---

## События

| Событие | Имя Блока | Категория | Описание |
|-------|------------|----------|-------------|
| Create | `create` | Объект | Выполняется один раз при первом создании экземпляра |
| Step | `step` | Объект | Выполняется на каждом кадре (используйте для непрерывных проверок) |
| Keyboard (held) | `keyboard` | Ввод | Выполняется непрерывно, пока клавиша удерживается (для плавного движения) |
| Keyboard <No Key> | `keyboard_no_key` | Ввод | Выполняется, когда в данный момент не нажата ни одна клавиша |
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
| Движение к точке | `move_towards_point` | `x`, `y`, `speed` |
| Обратить горизонтально | `reverse_horizontal` | — |
| Обратить вертикально | `reverse_vertical` | — |
| Задать направление и скорость | `set_direction_speed` | `direction`, `speed` |
| Задать гравитацию | `set_gravity` | `direction`, `gravity` |
| Задать горизонтальную скорость | `set_hspeed` | `speed` |
| Задать вертикальную скорость | `set_vspeed` | `speed` |
| Начать движение (направление) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Остановить движение | `stop_movement` | — |

### Сетка

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
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
| Запустить анимацию | `start_animation` | — |
| Остановить анимацию | `stop_animation` | — |
| Проверить количество экземпляров | `test_instance_count` | `object`, `number`, `operation` |

### Счёт

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Очистить таблицу рекордов | `clear_highscore` | — |
| Нарисовать жизни | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Нарисовать счёт | `draw_score` | `x`, `y`, `caption`, `relative` |
| Задать жизни | `set_lives` | `value`, `relative` |
| Задать счёт | `set_score` | `value`, `relative` |
| Показать таблицу рекордов | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |
| Проверить здоровье | `test_health` | `operation`, `value` |
| Проверить жизни | `test_lives` | `value`, `operation` |
| Проверить счёт | `test_score` | `value`, `operation` |

### Время

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Установить будильник | `set_alarm` | `alarm_number`, `steps` |
| Пауза | `sleep` | `milliseconds` |

### Комната

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Проверить комнату | `check_room` | `room`, `not_flag` |
| Завершить игру | `game_end` | — |
| Если следующая комната существует | `if_next_room_exists` | `then_actions`, `else_actions` |
| Если предыдущая комната существует | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Перезапустить комнату | `restart_room` | — |
| Задать заголовок комнаты | `set_room_caption` | `caption` |

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
| Нарисовать текст | `draw_text` | `text`, `x`, `y`, `relative` |
| Нарисовать переменную | `draw_variable` | `x`, `y`, `variable` |
| Заполнить экран цветом | `fill_color` | `color` |
| Открыть веб-страницу | `open_webpage` | `url` |
| Перезапустить игру | `restart_game` | — |
| Задать цвет | `set_color` | `color`, `alpha` |
| Задать цвет рисования | `set_draw_color` | `color` |
| Задать шрифт рисования | `set_draw_font` | `font`, `halign`, `valign` |
| Задать заголовок окна | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Показать информацию об игре | `show_info` | — |
| Показать сообщение | `show_message` | `message` |

### Управление

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Комментарий | `comment` | `text` |
| Иначе | `else_action` | — |
| Конец блока | `end_block` | — |
| Выполнить код | `execute_code` | `code` |
| Выполнить скрипт | `execute_script` | `script`, `arg0`, `arg1`, `arg2`, `arg3`, `arg4` |
| Выйти из события | `exit_event` | — |
| Если столкновение | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Если объект существует | `if_object_exists` | `object`, `not_flag` |
| Начало блока | `start_block` | — |
| Проверить шанс | `test_chance` | `sides` |
| Задать вопрос | `test_question` | `question` |
| Проверить переменную | `test_variable` | `variable`, `value`, `scope`, `operation` |

### Виды

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Включить виды | `enable_views` | `enable` |
| Настроить вид | `set_view` | `view`, `visible`, `view_x`, `view_y`, `view_w`, `view_h`, `port_x`, `port_y`, `port_w`, `port_h`, `follow`, `hborder`, `vborder`, `hspeed`, `vspeed` |

### 3D-вид

| Действие | Имя Блока | Параметры |
|--------|------------|------------|
| Нарисовать HUD DOOM | `draw_doom_hud` | `x`, `y`, `width`, `height`, `back_color`, `divider_color`, `text_color`, `health_label`, `health_bar_width`, `health_bar_height`, `bar_color`, `face_sprite`, `face_frames`, `score_label`, `lives_sprite`, `lives_scale`, `objective_value`, `objective_label` |
| Нарисовать миникарту | `draw_minimap` | `x`, `y`, `size`, `back_color`, `wall_color`, `player_color` |
| Включить вид Raycast | `enable_raycast_view` | `enable`, `camera_object`, `fov`, `render_distance`, `cell_size`, `columns`, `wall_color`, `floor_color`, `ceiling_color`, `wall_texture`, `sky_texture`, `floor_texture`, `ceiling_texture`, `wall_textured`, `floor_cast_res`, `viewport_height` |
| Задать угол взгляда | `set_facing_angle` | `angle`, `relative` |

---

## Смотрите Также

- [Руководство по Пресетам](Preset-Guide_ru) — что такое пресеты и как их изменить
- [Справочник Событий](Event-Reference_ru) — полное описание каждого события
- [Полный Справочник Действий](Full-Action-Reference_ru) — полные сведения о параметрах для каждого действия
- [Средний Пресет](Intermediate-Preset_ru) — следующий уровень
