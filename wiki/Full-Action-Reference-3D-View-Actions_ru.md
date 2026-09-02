# 3D-вид

*[Главная](Home_ru) | [Руководство по пресетам](Preset-Guide_ru) | [Справочник событий](Event-Reference_ru)*

> **Сгенерировано автоматически** из реестра действий IDE с помощью `tools/gen_action_reference.py` — не редактируйте вручную; повторно запустите генератор после изменения действий. Переводы взяты из `tools/action_ref_i18n.py`.

### Apply Gravity

| Свойство | Значение |
|----------|-------|
| **Имя** | `apply_gravity` |
| **Значок** | ⬇️ |
| **Категория** | 3D-вид |

Continuous falling/landing physics for the block-world camera -- bind in the Step event (not a keyboard-held event) so it runs every frame regardless of movement input. No-op unless Enable Block World View's Gravity parameter is set above 0

*Параметры:* нет

### Break Block

| Свойство | Значение |
|----------|-------|
| **Имя** | `break_block` |
| **Значок** | ⛏️ |
| **Категория** | 3D-вид |

Remove the block the camera is looking at -- also picks it up into the calling instance's inventory if Enable Block World View's Inventory is on, and refuses if the block is protected (Set Block Protection) and the required key isn't in inventory

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `reach` | Число | `5` | How many cells ahead you can reach, in grid cells; необязательно |

### Draw Block World HUD

| Свойство | Значение |
|----------|-------|
| **Имя** | `draw_block_world_hud` |
| **Значок** | 🧰 |
| **Категория** | 3D-вид |

Draw a crosshair plus a hotbar strip (the selected slot highlighted, with a count on each slot once Inventory is on) -- call from the player/camera object's own Draw event

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `slot_size` | Число | `40` | Width and height of each hotbar slot, in pixels; необязательно |
| `gap` | Число | `6` | Space between hotbar slots, in pixels; необязательно |
| `margin_bottom` | Число | `16` | Space between the hotbar and the bottom of the screen; необязательно |
| `back_color` | Цвет | `#202020` | Fill colour of an unselected slot; необязательно |
| `selected_color` | Цвет | `#ffd040` | Fill colour of the currently selected slot; необязательно |
| `border_color` | Цвет | `#ffffff` | Outline colour of every slot; необязательно |
| `text_color` | Цвет | `#ffffff` | Colour of each slot's block-type label; необязательно |
| `crosshair_size` | Число | `12` | Width and height of the centre crosshair, in pixels; необязательно |
| `crosshair_color` | Цвет | `#ffffff` | Colour of the centre crosshair; необязательно |

### Нарисовать HUD DOOM

| Свойство | Значение |
|----------|-------|
| **Имя** | `draw_doom_hud` |
| **Значок** | 🎯 |
| **Категория** | 3D-вид |

Нарисовать нижнюю полосу состояния в стиле DOOM (полоса здоровья + число, счёт, жизни, счётчик цели и реагирующая на здоровье иконка лица) поверх вида raycast

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `x` | Число | `0` | Левый край полосы, в экранных пикселях |
| `y` | Число | `-1` | Верхний край полосы; отрицательное значение автоматически выравнивает её к низу окна, под уменьшенной областью просмотра; необязательно |
| `width` | Число | `0` | Ширина полосы (0 = полная ширина окна); необязательно |
| `height` | Число | `42` | Высота полосы; согласуйте её с полосой viewport_height, зарезервированной в enable_raycast_view; необязательно |
| `back_color` | Цвет | `#101010` | Панель фона полосы; необязательно |
| `divider_color` | Цвет | `#505050` | Верхняя граница и подложка полосы здоровья; необязательно |
| `text_color` | Цвет | `#ffffff` | Цвет всего текста полосы; необязательно |
| `health_label` | Текст | `Health` | необязательно |
| `health_bar_width` | Число | `90` | необязательно |
| `health_bar_height` | Число | `14` | необязательно |
| `bar_color` | Цвет | `#20c020` | Цвет заполнения полосы здоровья; необязательно |
| `face_sprite` | Спрайт | — | Горизонтальная полоса кадров лица, самый здоровый первым (пусто = без иконки лица); необязательно |
| `face_frames` | Число | `4` | Сколько кадров имеет полоса лица; здоровье равномерно распределяется между ними; необязательно |
| `score_label` | Текст | `Score: ` | необязательно |
| `lives_sprite` | Спрайт | — | Спрайт, рисуемый один раз на каждую оставшуюся жизнь; необязательно |
| `lives_scale` | Число | `1.0` | необязательно |
| `objective_value` | Текст | `0` | Выражение, показываемое после метки цели (привяжите свою переменную ключа/квеста); необязательно |
| `objective_label` | Текст | `Keys: ` | необязательно |

### Нарисовать миникарту

| Свойство | Значение |
|----------|-------|
| **Имя** | `draw_minimap` |
| **Значок** | 🗺️ |
| **Категория** | 3D-вид |

Нарисовать ориентированную на север миникарту стен комнаты raycast с меткой, показывающей, где камера и куда она смотрит

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `x` | Число | `0` | Левый край миникарты, в экранных пикселях |
| `y` | Число | `0` | Верхний край миникарты, в экранных пикселях |
| `size` | Число | `120` | Ширина и высота квадрата миникарты, в пикселях; необязательно |
| `back_color` | Цвет | `#101018` | Цвет панели за картой; необязательно |
| `wall_color` | Цвет | `#8080a0` | Цвет линий стен; необязательно |
| `player_color` | Цвет | `#ffd040` | Цвет метки камеры и её линии направления; необязательно |
| `mark_object` | Объект | — | Also dot every instance of this object onto the map (blank = show walls and player only); необязательно |
| `mark_color` | Цвет | `#40e0ff` | Colour of the Mark Object dots; необязательно |
| `mark_object_2` | Объект | — | A second object to dot on, in its own colour; необязательно |
| `mark_color_2` | Цвет | `#ff5050` | Colour of the Mark Object 2 dots; необязательно |

### Enable Block World View

| Свойство | Значение |
|----------|-------|
| **Имя** | `enable_block_world_view` |
| **Значок** | 🧱 |
| **Категория** | 3D-вид |

Render the room as a first-person voxel view (single layer) instead of the top-down view

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `enable` | Да/Нет | Да | On = first-person block view; off = normal top-down |
| `camera_object` | Объект | — | Объект, чья позиция + угол взгляда является камерой (пусто = объект, выполняющий это действие); необязательно |
| `z_layer` | Число | `0` | Which world layer to render (Phase 2a renders exactly one layer -- no looking up/down yet); необязательно |
| `fov` | Число | `66` | Горизонтальное поле зрения в градусах; необязательно |
| `render_distance` | Число | `20` | Макс. длина луча в клетках сетки; необязательно |
| `cell_size` | Число | `32` | Grid cell size in pixels (match the block-placement grid); необязательно |
| `columns` | Число | `320` | Столбцы экрана для raycast (меньше = быстрее/грубее); необязательно |
| `wall_color` | Цвет | `#8a8a8a` | Flat colour used only if Textured Blocks is off; необязательно |
| `floor_color` | Цвет | `#3a2f1c` | Flat floor colour (Phase 2a has no floor texturing yet); необязательно |
| `ceiling_color` | Цвет | `#87CEEB` | Flat ceiling/sky colour (Phase 2a has no sky yet); необязательно |
| `pitch` | Число | `0` | Degrees to look up (+) or down (-); 0 is level; необязательно |
| `wall_textured` | Да/Нет | Да | Off forces flat block colours even though real textures are available; необязательно |
| `top_cast_res` | Число | `4` | Top/bottom face texture detail: rows sampled per N screen rows (higher = faster + chunkier, 0 = flat average colour instead of texture); необязательно |
| `eye_height` | Число | `1.5` | Camera height above the layer it stands on, in cells (1.5 = a two-block-tall body, needed to see the top of a block on your own layer and stack onto it); необязательно |
| `gravity` | Число | `0` | Downward acceleration in cells/step^2 for the Jump action + gravity/falling (Tier 7a). 0 (default) keeps Move And Collide's original instant-footing behaviour with no jumping; a typical value is around 0.04; необязательно |
| `inventory` | Да/Нет | Нет | On = Break Block picks up what it breaks and Place Block consumes from that inventory (Tier 7c); off (default) = unlimited creative-mode placing, unchanged from before Tier 7c; необязательно |
| `generate` | Да/Нет | Нет | On = procedurally generate rolling terrain around the camera as it explores (Tier 7e), using Seed below; off (default) = only hand-placed/loaded blocks exist, unchanged from before Tier 7e; необязательно |
| `seed` | Число | `0` | World seed for Generate Terrain -- the same seed always produces the same terrain on this target. Ignored unless Generate Terrain is on; необязательно |

### Включить вид Raycast

| Свойство | Значение |
|----------|-------|
| **Имя** | `enable_raycast_view` |
| **Значок** | 🕹️ |
| **Категория** | 3D-вид |

Отображать комнату как 3D-вид от первого лица в стиле Doom/Wolfenstein (стены, небо, пол) вместо вида сверху

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `enable` | Да/Нет | Да | Вкл. = вид raycast от первого лица; выкл. = обычный вид сверху |
| `camera_object` | Объект | — | Объект, чья позиция + угол взгляда является камерой (пусто = объект, выполняющий это действие); необязательно |
| `fov` | Число | `66` | Горизонтальное поле зрения в градусах; необязательно |
| `render_distance` | Число | `20` | Макс. длина луча в клетках сетки; необязательно |
| `cell_size` | Число | `32` | Размер клетки сетки в пикселях (соответствует сетке размещения стен); необязательно |
| `columns` | Число | `320` | Столбцы экрана для raycast (меньше = быстрее/грубее); необязательно |
| `wall_color` | Цвет | `#993333` | Сплошной цвет стен, когда текстура стены не задана; необязательно |
| `floor_color` | Цвет | `#464632` | Сплошной цвет пола, когда текстура пола не задана; необязательно |
| `ceiling_color` | Цвет | `#87CEEB` | Сплошной цвет потолка, когда текстура неба/потолка не задана; необязательно |
| `wall_texture` | Спрайт | — | Спрайт для текстурирования каждой стены (пусто = сплошной цвет); необязательно |
| `sky_texture` | Спрайт | — | Спрайт для панорамного неба над потолком (пусто = сплошной); необязательно |
| `floor_texture` | Спрайт | — | Спрайт, проецируемый на пол (пусто = сплошной цвет); необязательно |
| `ceiling_texture` | Спрайт | — | Спрайт, проецируемый на потолок, когда небо не задано; необязательно |
| `wall_textured` | Да/Нет | Да | Выкл. принудительно задаёт сплошные цвета стен, даже когда задана текстура; необязательно |
| `floor_cast_res` | Число | `4` | Уменьшение дискретизации пола (больше = быстрее + грубее); необязательно |
| `viewport_height` | Число | `0` | Ограничить 3D-вид до этой высоты в пикселях (леттербокс), зарезервировав полосу ниже для полосы состояния в стиле DOOM (0 = полная высота окна, без изменений); необязательно |

### Jump

| Свойство | Значение |
|----------|-------|
| **Имя** | `jump` |
| **Значок** | ⬆️ |
| **Категория** | 3D-вид |

Give the block-world camera upward velocity -- only while standing on solid ground (no double/air jumps). Needs Gravity configured (Enable Block World View) and Apply Gravity bound in the Step event, or nothing brings it back down

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `speed` | Число | `0.35` | Initial upward velocity, in cells/step; необязательно |

### Load Block World

| Свойство | Значение |
|----------|-------|
| **Имя** | `load_block_world` |
| **Значок** | 📂 |
| **Категория** | 3D-вид |

Load a pre-authored world (blocks placed by a generator or hand-authored file) into the current room, replacing whatever blocks are there

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `data_file` | Текст | — | Path to a block-world JSON file, relative to the project folder (e.g. blocks/room1.json) |

### Look Up / Down

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_look_pitch` |
| **Значок** | 🔭 |
| **Категория** | 3D-вид |

Tilt the block-world view up or down

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `pitch` | Число | `0` | Degrees to look up (+) or down (-); 0 is level |
| `relative` | Да/Нет | Нет | On = add to the current angle, for a look control you can hold down; off = set it outright; необязательно |

### Move And Collide

| Свойство | Значение |
|----------|-------|
| **Имя** | `move_and_collide` |
| **Значок** | 🚶 |
| **Категория** | 3D-вид |

Move this step, checked against the block grid, with automatic footing (step up one block, drop any distance) -- the camera's z_layer follows if this is the block-world camera

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `dx` | Число | `0` | How far to move on x this step, in pixels |
| `dy` | Число | `0` | How far to move on y this step, in pixels |
| `collide` | Да/Нет | Да | Off ignores the block grid entirely (flying/debug); необязательно |

### Place Block

| Свойство | Значение |
|----------|-------|
| **Имя** | `place_block` |
| **Значок** | 🧱 |
| **Категория** | 3D-вид |

Put a block in the empty cell the camera is looking at -- unlimited unless Enable Block World View's Inventory is on, which draws from what Break Block has picked up

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `block` | Выбор | `stone` | Which kind of block to place; Варианты: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `reach` | Число | `5` | How many cells ahead you can build, in grid cells; необязательно |

### Select Hotbar Slot

| Свойство | Значение |
|----------|-------|
| **Имя** | `select_hotbar_slot` |
| **Значок** | 🔢 |
| **Категория** | 3D-вид |

Choose which block the hotbar has selected, for place_block to build with -- bind Place Block's Block parameter to the expression "hotbar_block" to use it

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `index` | Число | `0` | Hotbar slot index, wrapping around at either end |
| `relative` | Да/Нет | Нет | On = add to the current slot, for cycling with [ ] / scroll-wheel style controls; off = jump to it; необязательно |

### Set Block Protection

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_block_protection` |
| **Значок** | 🔒 |
| **Категория** | 3D-вид |

Require a specific block type in inventory before Break Block can remove a chosen block type -- call once per protected type, needs Enable Block World View's Inventory on or the requirement can never be satisfied

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `block_type` | Выбор | `diamond_block` | Which block type becomes protected; Варианты: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `required_key` | Выбор | `gold_block` | Which block type must be in inventory to break it; Варианты: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Set Block Reward

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_block_reward` |
| **Значок** | 💎 |
| **Категория** | 3D-вид |

Award score when Break Block successfully removes a chosen block type -- call once per rewarded type (e.g. in the room's create event, right after Enable Block World View). A mine-to-collect ore/gem block: place it in the terrain, register its reward, and breaking it awards the points automatically

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `block_type` | Выбор | `diamond_block` | Which block type awards score when broken; Варианты: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `points` | Число | `10` | Score awarded per block of this type broken |

### Задать угол взгляда

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_facing_angle` |
| **Значок** | 🧭 |
| **Категория** | 3D-вид |

Задать направление взгляда экземпляра для камеры raycast (от первого лица) — независимо от скорости движения

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `angle` | Число | `0` | Градусы (0=вправо, 90=вверх, 180=влево, 270=вниз) |
| `relative` | Да/Нет | Нет | Добавить к текущему углу взгляда вместо замены; необязательно |

---

## Другие Категории

- [Движение](Full-Action-Reference-Movement_ru) (20)
- [Экземпляр](Full-Action-Reference-Instance_ru) (12)
- [Счёт](Full-Action-Reference-Score_ru) (11)
- [Комната](Full-Action-Reference-Room_ru) (13)
- [Время](Full-Action-Reference-Timing_ru) (8)
- [Аудио](Full-Action-Reference-Audio_ru) (6)
- [Игра](Full-Action-Reference-Game_ru) (25)
- [Управление](Full-Action-Reference-Control_ru) (19)
- [Сетка](Full-Action-Reference-Grid_ru) (4)
- [Виды](Full-Action-Reference-Views_ru) (2)
- [Particles](Full-Action-Reference-Particles_ru) (8)
- [Réseau](Full-Action-Reference-Network-Actions_ru) (15)

[← Назад к Полному Справочнику Действий](Full-Action-Reference_ru)
