# 3D-вигляд

*[Головна](Home_uk) | [Посібник із пресетів](Preset-Guide_uk) | [Довідник подій](Event-Reference_uk)*

> **Згенеровано автоматично** з реєстру дій IDE за допомогою `tools/gen_action_reference.py` — не редагуйте вручну; повторно запустіть генератор після зміни дій. Переклади взято з `tools/action_ref_i18n.py`.

### Apply Gravity

| Властивість | Значення |
|----------|-------|
| **Назва** | `apply_gravity` |
| **Значок** | ⬇️ |
| **Категорія** | 3D-вигляд |

Continuous falling/landing physics for the block-world camera -- bind in the Step event (not a keyboard-held event) so it runs every frame regardless of movement input. No-op unless Enable Block World View's Gravity parameter is set above 0

*Параметри:* немає

### Break Block

| Властивість | Значення |
|----------|-------|
| **Назва** | `break_block` |
| **Значок** | ⛏️ |
| **Категорія** | 3D-вигляд |

Remove the block the camera is looking at -- also picks it up into the calling instance's inventory if Enable Block World View's Inventory is on, and refuses if the block is protected (Set Block Protection) and the required key isn't in inventory

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `reach` | Число | `5` | How many cells ahead you can reach, in grid cells; необов'язково |

### Draw Block World HUD

| Властивість | Значення |
|----------|-------|
| **Назва** | `draw_block_world_hud` |
| **Значок** | 🧰 |
| **Категорія** | 3D-вигляд |

Draw a crosshair plus a hotbar strip (the selected slot highlighted, with a count on each slot once Inventory is on) -- call from the player/camera object's own Draw event

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `slot_size` | Число | `40` | Width and height of each hotbar slot, in pixels; необов'язково |
| `gap` | Число | `6` | Space between hotbar slots, in pixels; необов'язково |
| `margin_bottom` | Число | `16` | Space between the hotbar and the bottom of the screen; необов'язково |
| `back_color` | Колір | `#202020` | Fill colour of an unselected slot; необов'язково |
| `selected_color` | Колір | `#ffd040` | Fill colour of the currently selected slot; необов'язково |
| `border_color` | Колір | `#ffffff` | Outline colour of every slot; необов'язково |
| `text_color` | Колір | `#ffffff` | Colour of each slot's block-type label; необов'язково |
| `crosshair_size` | Число | `12` | Width and height of the centre crosshair, in pixels; необов'язково |
| `crosshair_color` | Колір | `#ffffff` | Colour of the centre crosshair; необов'язково |

### Намалювати HUD DOOM

| Властивість | Значення |
|----------|-------|
| **Назва** | `draw_doom_hud` |
| **Значок** | 🎯 |
| **Категорія** | 3D-вигляд |

Намалювати нижню смугу стану у стилі DOOM (смуга здоров'я + число, рахунок, життя, лічильник цілі та реагуюча на здоров'я іконка обличчя) поверх вигляду raycast

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `x` | Число | `0` | Лівий край смуги, в екранних пікселях |
| `y` | Число | `-1` | Верхній край смуги; від'ємне значення автоматично вирівнює її до низу вікна, під зменшеною областю перегляду; необов'язково |
| `width` | Число | `0` | Ширина смуги (0 = повна ширина вікна); необов'язково |
| `height` | Число | `42` | Висота смуги; узгоджуйте її зі смугою viewport_height, зарезервованою в enable_raycast_view; необов'язково |
| `back_color` | Колір | `#101010` | Панель тла смуги; необов'язково |
| `divider_color` | Колір | `#505050` | Верхня межа та підкладка смуги здоров'я; необов'язково |
| `text_color` | Колір | `#ffffff` | Колір усього тексту смуги; необов'язково |
| `health_label` | Текст | `Health` | необов'язково |
| `health_bar_width` | Число | `90` | необов'язково |
| `health_bar_height` | Число | `14` | необов'язково |
| `bar_color` | Колір | `#20c020` | Колір заповнення смуги здоров'я; необов'язково |
| `face_sprite` | Спрайт | — | Горизонтальна смуга кадрів обличчя, найздоровіший спочатку (порожньо = без іконки обличчя); необов'язково |
| `face_frames` | Число | `4` | Скільки кадрів має смуга обличчя; здоров'я рівномірно розподіляється між ними; необов'язково |
| `score_label` | Текст | `Score: ` | необов'язково |
| `lives_sprite` | Спрайт | — | Спрайт, що малюється один раз на кожне життя, що залишилося; необов'язково |
| `lives_scale` | Число | `1.0` | необов'язково |
| `objective_value` | Текст | `0` | Вираз, що показується після мітки цілі (прив'яжіть власну змінну ключа/квесту); необов'язково |
| `objective_label` | Текст | `Keys: ` | необов'язково |

### Намалювати мінікарту

| Властивість | Значення |
|----------|-------|
| **Назва** | `draw_minimap` |
| **Значок** | 🗺️ |
| **Категорія** | 3D-вигляд |

Намалювати орієнтовану на північ мінікарту стін кімнати raycast із позначкою, що показує, де камера і куди вона дивиться

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `x` | Число | `0` | Лівий край мінікарти, в екранних пікселях |
| `y` | Число | `0` | Верхній край мінікарти, в екранних пікселях |
| `size` | Число | `120` | Ширина і висота квадрата мінікарти, у пікселях; необов'язково |
| `back_color` | Колір | `#101018` | Колір панелі за картою; необов'язково |
| `wall_color` | Колір | `#8080a0` | Колір ліній стін; необов'язково |
| `player_color` | Колір | `#ffd040` | Колір позначки камери та її лінії напрямку; необов'язково |
| `mark_object` | Об'єкт | — | Also dot every instance of this object onto the map (blank = show walls and player only); необов'язково |
| `mark_color` | Колір | `#40e0ff` | Colour of the Mark Object dots; необов'язково |
| `mark_object_2` | Об'єкт | — | A second object to dot on, in its own colour; необов'язково |
| `mark_color_2` | Колір | `#ff5050` | Colour of the Mark Object 2 dots; необов'язково |

### Enable Block World View

| Властивість | Значення |
|----------|-------|
| **Назва** | `enable_block_world_view` |
| **Значок** | 🧱 |
| **Категорія** | 3D-вигляд |

Render the room as a first-person voxel view (single layer) instead of the top-down view

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `enable` | Так/Ні | Так | On = first-person block view; off = normal top-down |
| `camera_object` | Об'єкт | — | Об'єкт, чия позиція + кут погляду є камерою (порожньо = об'єкт, що виконує цю дію); необов'язково |
| `z_layer` | Число | `0` | Which world layer to render (Phase 2a renders exactly one layer -- no looking up/down yet); необов'язково |
| `fov` | Число | `66` | Горизонтальне поле зору в градусах; необов'язково |
| `render_distance` | Число | `20` | Макс. довжина променя в клітинках сітки; необов'язково |
| `cell_size` | Число | `32` | Grid cell size in pixels (match the block-placement grid); необов'язково |
| `columns` | Число | `320` | Стовпці екрана для raycast (менше = швидше/грубіше); необов'язково |
| `wall_color` | Колір | `#8a8a8a` | Flat colour used only if Textured Blocks is off; необов'язково |
| `floor_color` | Колір | `#3a2f1c` | Flat floor colour (Phase 2a has no floor texturing yet); необов'язково |
| `ceiling_color` | Колір | `#87CEEB` | Flat ceiling/sky colour (Phase 2a has no sky yet); необов'язково |
| `pitch` | Число | `0` | Degrees to look up (+) or down (-); 0 is level; необов'язково |
| `wall_textured` | Так/Ні | Так | Off forces flat block colours even though real textures are available; необов'язково |
| `top_cast_res` | Число | `4` | Top/bottom face texture detail: rows sampled per N screen rows (higher = faster + chunkier, 0 = flat average colour instead of texture); необов'язково |
| `eye_height` | Число | `1.5` | Camera height above the layer it stands on, in cells (1.5 = a two-block-tall body, needed to see the top of a block on your own layer and stack onto it); необов'язково |
| `gravity` | Число | `0` | Downward acceleration in cells/step^2 for the Jump action + gravity/falling (Tier 7a). 0 (default) keeps Move And Collide's original instant-footing behaviour with no jumping; a typical value is around 0.04; необов'язково |
| `inventory` | Так/Ні | Ні | On = Break Block picks up what it breaks and Place Block consumes from that inventory (Tier 7c); off (default) = unlimited creative-mode placing, unchanged from before Tier 7c; необов'язково |
| `generate` | Так/Ні | Ні | On = procedurally generate rolling terrain around the camera as it explores (Tier 7e), using Seed below; off (default) = only hand-placed/loaded blocks exist, unchanged from before Tier 7e; необов'язково |
| `seed` | Число | `0` | World seed for Generate Terrain -- the same seed always produces the same terrain on this target. Ignored unless Generate Terrain is on; необов'язково |

### Увімкнути вигляд Raycast

| Властивість | Значення |
|----------|-------|
| **Назва** | `enable_raycast_view` |
| **Значок** | 🕹️ |
| **Категорія** | 3D-вигляд |

Відображати кімнату як 3D-вигляд від першої особи у стилі Doom/Wolfenstein (стіни, небо, підлога) замість вигляду згори

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `enable` | Так/Ні | Так | Увімк. = вигляд raycast від першої особи; вимк. = звичайний вигляд згори |
| `camera_object` | Об'єкт | — | Об'єкт, чия позиція + кут погляду є камерою (порожньо = об'єкт, що виконує цю дію); необов'язково |
| `fov` | Число | `66` | Горизонтальне поле зору в градусах; необов'язково |
| `render_distance` | Число | `20` | Макс. довжина променя в клітинках сітки; необов'язково |
| `cell_size` | Число | `32` | Розмір клітинки сітки в пікселях (відповідає сітці розміщення стін); необов'язково |
| `columns` | Число | `320` | Стовпці екрана для raycast (менше = швидше/грубіше); необов'язково |
| `wall_color` | Колір | `#993333` | Суцільний колір стін, коли текстуру стіни не задано; необов'язково |
| `floor_color` | Колір | `#464632` | Суцільний колір підлоги, коли текстуру підлоги не задано; необов'язково |
| `ceiling_color` | Колір | `#87CEEB` | Суцільний колір стелі, коли текстуру неба/стелі не задано; необов'язково |
| `wall_texture` | Спрайт | — | Спрайт для текстурування кожної стіни (порожньо = суцільний колір); необов'язково |
| `sky_texture` | Спрайт | — | Спрайт для панорамного неба над стелею (порожньо = суцільний); необов'язково |
| `floor_texture` | Спрайт | — | Спрайт, спроєктований на підлогу (порожньо = суцільний колір); необов'язково |
| `ceiling_texture` | Спрайт | — | Спрайт, спроєктований на стелю, коли неба не задано; необов'язково |
| `wall_textured` | Так/Ні | Так | Вимк. примусово задає суцільні кольори стін, навіть коли задано текстуру; необов'язково |
| `floor_cast_res` | Число | `4` | Зменшення дискретизації підлоги (більше = швидше + грубіше); необов'язково |
| `viewport_height` | Число | `0` | Обмежити 3D-вигляд до цієї висоти в пікселях (леттербокс), зарезервувавши смугу нижче для смуги стану у стилі DOOM (0 = повна висота вікна, без змін); необов'язково |

### Jump

| Властивість | Значення |
|----------|-------|
| **Назва** | `jump` |
| **Значок** | ⬆️ |
| **Категорія** | 3D-вигляд |

Give the block-world camera upward velocity -- only while standing on solid ground (no double/air jumps). Needs Gravity configured (Enable Block World View) and Apply Gravity bound in the Step event, or nothing brings it back down

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `speed` | Число | `0.35` | Initial upward velocity, in cells/step; необов'язково |

### Load Block World

| Властивість | Значення |
|----------|-------|
| **Назва** | `load_block_world` |
| **Значок** | 📂 |
| **Категорія** | 3D-вигляд |

Load a pre-authored world (blocks placed by a generator or hand-authored file) into the current room, replacing whatever blocks are there

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `data_file` | Текст | — | Path to a block-world JSON file, relative to the project folder (e.g. blocks/room1.json) |

### Look Up / Down

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_look_pitch` |
| **Значок** | 🔭 |
| **Категорія** | 3D-вигляд |

Tilt the block-world view up or down

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `pitch` | Число | `0` | Degrees to look up (+) or down (-); 0 is level |
| `relative` | Так/Ні | Ні | On = add to the current angle, for a look control you can hold down; off = set it outright; необов'язково |

### Move And Collide

| Властивість | Значення |
|----------|-------|
| **Назва** | `move_and_collide` |
| **Значок** | 🚶 |
| **Категорія** | 3D-вигляд |

Move this step, checked against the block grid, with automatic footing (step up one block, drop any distance) -- the camera's z_layer follows if this is the block-world camera

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `dx` | Число | `0` | How far to move on x this step, in pixels |
| `dy` | Число | `0` | How far to move on y this step, in pixels |
| `collide` | Так/Ні | Так | Off ignores the block grid entirely (flying/debug); необов'язково |

### Place Block

| Властивість | Значення |
|----------|-------|
| **Назва** | `place_block` |
| **Значок** | 🧱 |
| **Категорія** | 3D-вигляд |

Put a block in the empty cell the camera is looking at -- unlimited unless Enable Block World View's Inventory is on, which draws from what Break Block has picked up

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `block` | Вибір | `stone` | Which kind of block to place; Варіанти: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `reach` | Число | `5` | How many cells ahead you can build, in grid cells; необов'язково |

### Select Hotbar Slot

| Властивість | Значення |
|----------|-------|
| **Назва** | `select_hotbar_slot` |
| **Значок** | 🔢 |
| **Категорія** | 3D-вигляд |

Choose which block the hotbar has selected, for place_block to build with -- bind Place Block's Block parameter to the expression "hotbar_block" to use it

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `index` | Число | `0` | Hotbar slot index, wrapping around at either end |
| `relative` | Так/Ні | Ні | On = add to the current slot, for cycling with [ ] / scroll-wheel style controls; off = jump to it; необов'язково |

### Set Block Protection

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_block_protection` |
| **Значок** | 🔒 |
| **Категорія** | 3D-вигляд |

Require a specific block type in inventory before Break Block can remove a chosen block type -- call once per protected type, needs Enable Block World View's Inventory on or the requirement can never be satisfied

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `block_type` | Вибір | `diamond_block` | Which block type becomes protected; Варіанти: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `required_key` | Вибір | `gold_block` | Which block type must be in inventory to break it; Варіанти: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Set Block Reward

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_block_reward` |
| **Значок** | 💎 |
| **Категорія** | 3D-вигляд |

Award score when Break Block successfully removes a chosen block type -- call once per rewarded type (e.g. in the room's create event, right after Enable Block World View). A mine-to-collect ore/gem block: place it in the terrain, register its reward, and breaking it awards the points automatically

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `block_type` | Вибір | `diamond_block` | Which block type awards score when broken; Варіанти: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `points` | Число | `10` | Score awarded per block of this type broken |

### Задати кут погляду

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_facing_angle` |
| **Значок** | 🧭 |
| **Категорія** | 3D-вигляд |

Задати напрямок погляду екземпляра для камери raycast (від першої особи) — незалежно від швидкості руху

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `angle` | Число | `0` | Градуси (0=праворуч, 90=вгору, 180=ліворуч, 270=вниз) |
| `relative` | Так/Ні | Ні | Додати до поточного кута погляду замість заміни; необов'язково |

---

## Інші Категорії

- [Рух](Full-Action-Reference-Movement_uk) (20)
- [Екземпляр](Full-Action-Reference-Instance_uk) (12)
- [Рахунок](Full-Action-Reference-Score_uk) (11)
- [Кімната](Full-Action-Reference-Room_uk) (13)
- [Час](Full-Action-Reference-Timing_uk) (8)
- [Аудіо](Full-Action-Reference-Audio_uk) (6)
- [Гра](Full-Action-Reference-Game_uk) (25)
- [Керування](Full-Action-Reference-Control_uk) (19)
- [Сітка](Full-Action-Reference-Grid_uk) (4)
- [Вигляди](Full-Action-Reference-Views_uk) (2)
- [Particles](Full-Action-Reference-Particles_uk) (8)
- [Réseau](Full-Action-Reference-Network-Actions_uk) (15)

[← Назад до Повного Довідника Дій](Full-Action-Reference_uk)
