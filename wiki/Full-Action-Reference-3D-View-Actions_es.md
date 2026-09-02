# Vista 3D

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Apply Gravity

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `apply_gravity` |
| **Icono** | ⬇️ |
| **Categoría** | Vista 3D |

Continuous falling/landing physics for the block-world camera -- bind in the Step event (not a keyboard-held event) so it runs every frame regardless of movement input. No-op unless Enable Block World View's Gravity parameter is set above 0

*Parámetros:* ninguno

### Break Block

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `break_block` |
| **Icono** | ⛏️ |
| **Categoría** | Vista 3D |

Remove the block the camera is looking at -- also picks it up into the calling instance's inventory if Enable Block World View's Inventory is on, and refuses if the block is protected (Set Block Protection) and the required key isn't in inventory

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `reach` | Número | `5` | How many cells ahead you can reach, in grid cells; opcional |

### Draw Block World HUD

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_block_world_hud` |
| **Icono** | 🧰 |
| **Categoría** | Vista 3D |

Draw a crosshair plus a hotbar strip (the selected slot highlighted, with a count on each slot once Inventory is on) -- call from the player/camera object's own Draw event

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `slot_size` | Número | `40` | Width and height of each hotbar slot, in pixels; opcional |
| `gap` | Número | `6` | Space between hotbar slots, in pixels; opcional |
| `margin_bottom` | Número | `16` | Space between the hotbar and the bottom of the screen; opcional |
| `back_color` | Color | `#202020` | Fill colour of an unselected slot; opcional |
| `selected_color` | Color | `#ffd040` | Fill colour of the currently selected slot; opcional |
| `border_color` | Color | `#ffffff` | Outline colour of every slot; opcional |
| `text_color` | Color | `#ffffff` | Colour of each slot's block-type label; opcional |
| `crosshair_size` | Número | `12` | Width and height of the centre crosshair, in pixels; opcional |
| `crosshair_color` | Color | `#ffffff` | Colour of the centre crosshair; opcional |

### Dibujar HUD DOOM

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_doom_hud` |
| **Icono** | 🎯 |
| **Categoría** | Vista 3D |

Dibujar una barra de estado inferior al estilo DOOM (barra de salud + número, puntuación, vidas, un contador de objetivo y un icono de rostro que reacciona a la salud) sobre la vista raycast

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Borde izquierdo de la barra, en píxeles de pantalla |
| `y` | Número | `-1` | Borde superior de la barra; un valor negativo la alinea automáticamente al fondo de la ventana, bajo la vista reducida; opcional |
| `width` | Número | `0` | Ancho de la barra (0 = ancho completo de la ventana); opcional |
| `height` | Número | `42` | Altura de la barra; mantenla coherente con la franja viewport_height reservada en enable_raycast_view; opcional |
| `back_color` | Color | `#101010` | Panel de fondo de la barra; opcional |
| `divider_color` | Color | `#505050` | Borde superior y fondo de la barra de salud; opcional |
| `text_color` | Color | `#ffffff` | Color de todo el texto de la barra; opcional |
| `health_label` | Texto | `Health` | opcional |
| `health_bar_width` | Número | `90` | opcional |
| `health_bar_height` | Número | `14` | opcional |
| `bar_color` | Color | `#20c020` | Color de relleno de la barra de salud; opcional |
| `face_sprite` | Sprite | — | Tira horizontal de fotogramas de rostro, el más sano primero (vacío = sin icono de rostro); opcional |
| `face_frames` | Número | `4` | Cuántos fotogramas tiene la tira de rostro; la salud se distribuye uniformemente entre ellos; opcional |
| `score_label` | Texto | `Score: ` | opcional |
| `lives_sprite` | Sprite | — | Sprite dibujado una vez por cada vida restante; opcional |
| `lives_scale` | Número | `1.0` | opcional |
| `objective_value` | Texto | `0` | Expresión mostrada después de la etiqueta de objetivo (asocia tu propia variable de llave/misión); opcional |
| `objective_label` | Texto | `Keys: ` | opcional |

### Dibujar minimapa

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_minimap` |
| **Icono** | 🗺️ |
| **Categoría** | Vista 3D |

Dibujar un minimapa orientado al norte de los muros de la sala raycast, con un marcador que muestra dónde está la cámara y hacia dónde mira

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Borde izquierdo del minimapa, en píxeles de pantalla |
| `y` | Número | `0` | Borde superior del minimapa, en píxeles de pantalla |
| `size` | Número | `120` | Ancho y alto del cuadrado del minimapa, en píxeles; opcional |
| `back_color` | Color | `#101018` | Color del panel detrás del mapa; opcional |
| `wall_color` | Color | `#8080a0` | Color de las líneas de los muros; opcional |
| `player_color` | Color | `#ffd040` | Color del marcador de la cámara y su línea de dirección; opcional |
| `mark_object` | Objeto | — | Also dot every instance of this object onto the map (blank = show walls and player only); opcional |
| `mark_color` | Color | `#40e0ff` | Colour of the Mark Object dots; opcional |
| `mark_object_2` | Objeto | — | A second object to dot on, in its own colour; opcional |
| `mark_color_2` | Color | `#ff5050` | Colour of the Mark Object 2 dots; opcional |

### Enable Block World View

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `enable_block_world_view` |
| **Icono** | 🧱 |
| **Categoría** | Vista 3D |

Render the room as a first-person voxel view (single layer) instead of the top-down view

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `enable` | Sí/No | Sí | On = first-person block view; off = normal top-down |
| `camera_object` | Objeto | — | Objeto cuya posición + ángulo de mirada es la cámara (vacío = el objeto que ejecuta esta acción); opcional |
| `z_layer` | Número | `0` | Which world layer to render (Phase 2a renders exactly one layer -- no looking up/down yet); opcional |
| `fov` | Número | `66` | Campo de visión horizontal en grados; opcional |
| `render_distance` | Número | `20` | Longitud máxima del rayo en celdas de la cuadrícula; opcional |
| `cell_size` | Número | `32` | Grid cell size in pixels (match the block-placement grid); opcional |
| `columns` | Número | `320` | Columnas de pantalla para raycast (menos = más rápido/más tosco); opcional |
| `wall_color` | Color | `#8a8a8a` | Flat colour used only if Textured Blocks is off; opcional |
| `floor_color` | Color | `#3a2f1c` | Flat floor colour (Phase 2a has no floor texturing yet); opcional |
| `ceiling_color` | Color | `#87CEEB` | Flat ceiling/sky colour (Phase 2a has no sky yet); opcional |
| `pitch` | Número | `0` | Degrees to look up (+) or down (-); 0 is level; opcional |
| `wall_textured` | Sí/No | Sí | Off forces flat block colours even though real textures are available; opcional |
| `top_cast_res` | Número | `4` | Top/bottom face texture detail: rows sampled per N screen rows (higher = faster + chunkier, 0 = flat average colour instead of texture); opcional |
| `eye_height` | Número | `1.5` | Camera height above the layer it stands on, in cells (1.5 = a two-block-tall body, needed to see the top of a block on your own layer and stack onto it); opcional |
| `gravity` | Número | `0` | Downward acceleration in cells/step^2 for the Jump action + gravity/falling (Tier 7a). 0 (default) keeps Move And Collide's original instant-footing behaviour with no jumping; a typical value is around 0.04; opcional |
| `inventory` | Sí/No | No | On = Break Block picks up what it breaks and Place Block consumes from that inventory (Tier 7c); off (default) = unlimited creative-mode placing, unchanged from before Tier 7c; opcional |
| `generate` | Sí/No | No | On = procedurally generate rolling terrain around the camera as it explores (Tier 7e), using Seed below; off (default) = only hand-placed/loaded blocks exist, unchanged from before Tier 7e; opcional |
| `seed` | Número | `0` | World seed for Generate Terrain -- the same seed always produces the same terrain on this target. Ignored unless Generate Terrain is on; opcional |

### Habilitar vista Raycast

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `enable_raycast_view` |
| **Icono** | 🕹️ |
| **Categoría** | Vista 3D |

Renderizar la sala como una vista 3D en primera persona al estilo Doom/Wolfenstein (muros, cielo, suelo) en lugar de la vista cenital

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `enable` | Sí/No | Sí | Activado = vista raycast en primera persona; desactivado = vista cenital normal |
| `camera_object` | Objeto | — | Objeto cuya posición + ángulo de mirada es la cámara (vacío = el objeto que ejecuta esta acción); opcional |
| `fov` | Número | `66` | Campo de visión horizontal en grados; opcional |
| `render_distance` | Número | `20` | Longitud máxima del rayo en celdas de la cuadrícula; opcional |
| `cell_size` | Número | `32` | Tamaño de la celda de la cuadrícula en píxeles (coincide con la cuadrícula de colocación de muros); opcional |
| `columns` | Número | `320` | Columnas de pantalla para raycast (menos = más rápido/más tosco); opcional |
| `wall_color` | Color | `#993333` | Color uniforme de los muros cuando no hay textura de muro; opcional |
| `floor_color` | Color | `#464632` | Color uniforme del suelo cuando no hay textura de suelo; opcional |
| `ceiling_color` | Color | `#87CEEB` | Color uniforme del techo cuando no hay textura de cielo/techo; opcional |
| `wall_texture` | Sprite | — | Sprite para texturizar cada muro (vacío = color uniforme); opcional |
| `sky_texture` | Sprite | — | Sprite para un cielo panorámico sobre el techo (vacío = uniforme); opcional |
| `floor_texture` | Sprite | — | Sprite proyectado sobre el suelo (vacío = color uniforme); opcional |
| `ceiling_texture` | Sprite | — | Sprite proyectado sobre el techo cuando no hay cielo; opcional |
| `wall_textured` | Sí/No | Sí | Desactivado fuerza colores uniformes de muros incluso cuando hay una textura; opcional |
| `floor_cast_res` | Número | `4` | Submuestreo del suelo proyectado (mayor = más rápido + más tosco); opcional |
| `viewport_height` | Número | `0` | Reduce la vista 3D a esta altura en píxeles (letterbox), reservando la franja inferior para una barra de estado al estilo DOOM (0 = altura completa de la ventana, sin cambios); opcional |

### Jump

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `jump` |
| **Icono** | ⬆️ |
| **Categoría** | Vista 3D |

Give the block-world camera upward velocity -- only while standing on solid ground (no double/air jumps). Needs Gravity configured (Enable Block World View) and Apply Gravity bound in the Step event, or nothing brings it back down

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0.35` | Initial upward velocity, in cells/step; opcional |

### Load Block World

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `load_block_world` |
| **Icono** | 📂 |
| **Categoría** | Vista 3D |

Load a pre-authored world (blocks placed by a generator or hand-authored file) into the current room, replacing whatever blocks are there

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `data_file` | Texto | — | Path to a block-world JSON file, relative to the project folder (e.g. blocks/room1.json) |

### Look Up / Down

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_look_pitch` |
| **Icono** | 🔭 |
| **Categoría** | Vista 3D |

Tilt the block-world view up or down

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `pitch` | Número | `0` | Degrees to look up (+) or down (-); 0 is level |
| `relative` | Sí/No | No | On = add to the current angle, for a look control you can hold down; off = set it outright; opcional |

### Move And Collide

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `move_and_collide` |
| **Icono** | 🚶 |
| **Categoría** | Vista 3D |

Move this step, checked against the block grid, with automatic footing (step up one block, drop any distance) -- the camera's z_layer follows if this is the block-world camera

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `dx` | Número | `0` | How far to move on x this step, in pixels |
| `dy` | Número | `0` | How far to move on y this step, in pixels |
| `collide` | Sí/No | Sí | Off ignores the block grid entirely (flying/debug); opcional |

### Place Block

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `place_block` |
| **Icono** | 🧱 |
| **Categoría** | Vista 3D |

Put a block in the empty cell the camera is looking at -- unlimited unless Enable Block World View's Inventory is on, which draws from what Break Block has picked up

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `block` | Elección | `stone` | Which kind of block to place; Opciones: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `reach` | Número | `5` | How many cells ahead you can build, in grid cells; opcional |

### Select Hotbar Slot

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `select_hotbar_slot` |
| **Icono** | 🔢 |
| **Categoría** | Vista 3D |

Choose which block the hotbar has selected, for place_block to build with -- bind Place Block's Block parameter to the expression "hotbar_block" to use it

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `index` | Número | `0` | Hotbar slot index, wrapping around at either end |
| `relative` | Sí/No | No | On = add to the current slot, for cycling with [ ] / scroll-wheel style controls; off = jump to it; opcional |

### Set Block Protection

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_block_protection` |
| **Icono** | 🔒 |
| **Categoría** | Vista 3D |

Require a specific block type in inventory before Break Block can remove a chosen block type -- call once per protected type, needs Enable Block World View's Inventory on or the requirement can never be satisfied

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `block_type` | Elección | `diamond_block` | Which block type becomes protected; Opciones: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `required_key` | Elección | `gold_block` | Which block type must be in inventory to break it; Opciones: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Set Block Reward

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_block_reward` |
| **Icono** | 💎 |
| **Categoría** | Vista 3D |

Award score when Break Block successfully removes a chosen block type -- call once per rewarded type (e.g. in the room's create event, right after Enable Block World View). A mine-to-collect ore/gem block: place it in the terrain, register its reward, and breaking it awards the points automatically

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `block_type` | Elección | `diamond_block` | Which block type awards score when broken; Opciones: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `points` | Número | `10` | Score awarded per block of this type broken |

### Establecer ángulo de mirada

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_facing_angle` |
| **Icono** | 🧭 |
| **Categoría** | Vista 3D |

Establecer la dirección de mirada de la instancia para una cámara raycast (en primera persona) — independiente de la velocidad de movimiento

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `angle` | Número | `0` | Grados (0=derecha, 90=arriba, 180=izquierda, 270=abajo) |
| `relative` | Sí/No | No | Sumar al ángulo de mirada actual en lugar de reemplazarlo; opcional |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (8)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (25)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Particles](Full-Action-Reference-Particles_es) (8)
- [Réseau](Full-Action-Reference-Network-Actions_es) (15)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
