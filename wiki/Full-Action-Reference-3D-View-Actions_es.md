# Vista 3D

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Aplicar gravedad

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `apply_gravity` |
| **Icono** | ⬇️ |
| **Categoría** | Vista 3D |

Física continua de caída y aterrizaje para la cámara de Block World: colócala en el evento Paso (no en un evento de tecla mantenida) para que se ejecute en cada fotograma, haya o no entrada de movimiento. No hace nada si el parámetro Gravedad de «Activar vista Block World» no es mayor que 0

*Parámetros:* ninguno

### Romper bloque

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `break_block` |
| **Icono** | ⛏️ |
| **Categoría** | Vista 3D |

Quita el bloque al que apunta la cámara; además lo recoge en el inventario de la instancia que llama la acción si el inventario de «Activar vista Block World» está activado, y se niega a quitarlo si el bloque está protegido («Definir protección de bloques») y la llave necesaria no está en el inventario

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `reach` | Número | `5` | Hasta dónde alcanzas hacia delante, en celdas de la rejilla; opcional |

### Fabricar objeto

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `craft_item` |
| **Icono** | ⚗️ |
| **Categoría** | Vista 3D |

Intenta fabricar la salida de una receta registrada a partir del inventario de la instancia que llama: todo o nada — consume todos los ingredientes a la vez, o ninguno si falta alguno. No hace nada silenciosamente si no hay receta registrada para la salida, o si el parámetro Inventario de «Activar vista Block World» no está activo

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `output` | Elección | `brick` | Which registered recipe to attempt, by its output block type; Opciones: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Dibujar HUD de Block World

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_block_world_hud` |
| **Icono** | 🧰 |
| **Categoría** | Vista 3D |

Dibuja una mira y una barra de acceso rápido (con la casilla seleccionada resaltada y un contador en cada casilla cuando el inventario está activo): llámala desde el evento Dibujar del propio objeto jugador o cámara

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `slot_size` | Número | `40` | Anchura y altura de cada casilla de la barra, en píxeles; opcional |
| `gap` | Número | `6` | Separación entre las casillas de la barra, en píxeles; opcional |
| `margin_bottom` | Número | `16` | Separación entre la barra y la parte inferior de la pantalla; opcional |
| `back_color` | Color | `#202020` | Color de relleno de una casilla no seleccionada; opcional |
| `selected_color` | Color | `#ffd040` | Color de relleno de la casilla seleccionada; opcional |
| `border_color` | Color | `#ffffff` | Color del contorno de todas las casillas; opcional |
| `text_color` | Color | `#ffffff` | Color de la etiqueta de tipo de bloque de cada casilla; opcional |
| `crosshair_size` | Número | `12` | Anchura y altura de la mira central, en píxeles; opcional |
| `crosshair_color` | Color | `#ffffff` | Color de la mira central; opcional |

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
| `mark_object` | Objeto | — | Marcar además con un punto en el mapa cada instancia de este objeto (vacío = mostrar solo muros y jugador); opcional |
| `mark_color` | Color | `#40e0ff` | Color de los puntos de «Marcar objeto»; opcional |
| `mark_object_2` | Objeto | — | Un segundo objeto que se marca con un color propio; opcional |
| `mark_color_2` | Color | `#ff5050` | Color de los puntos de «Marcar objeto 2»; opcional |

### Activar vista Block World

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `enable_block_world_view` |
| **Icono** | 🧱 |
| **Categoría** | Vista 3D |

Muestra la sala como una vista de vóxeles en primera persona (una sola capa) en lugar de la vista cenital

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `enable` | Sí/No | Sí | Activado = vista de bloques en primera persona; desactivado = vista cenital normal |
| `camera_object` | Objeto | — | Objeto cuya posición + ángulo de mirada es la cámara (vacío = el objeto que ejecuta esta acción); opcional |
| `z_layer` | Número | `0` | Qué capa del mundo se dibuja (la fase 2a dibuja exactamente una capa: todavía no se mira arriba ni abajo); opcional |
| `fov` | Número | `66` | Campo de visión horizontal en grados; opcional |
| `render_distance` | Número | `10` | Max ray length in grid cells (lower = faster; distance fog hides where the world ends); opcional |
| `cell_size` | Número | `32` | Tamaño de la celda de la rejilla, en píxeles (que coincida con la rejilla donde se colocan los bloques); opcional |
| `columns` | Número | `160` | Columnas de pantalla para raycast (menos = más rápido/más tosco); opcional |
| `fog` | Sí/No | Sí | Fade distant blocks into the sky so the edge of the view looks like haze instead of a hard cut. Off restores the old flat look; opcional |
| `fog_color` | Color | — | Colour the distance fades to; empty follows the Sky Color (a cave might want its own); opcional |
| `wall_color` | Color | `#8a8a8a` | Color plano, usado solo si los bloques con textura están desactivados; opcional |
| `floor_color` | Color | `#3a2f1c` | Color plano del suelo (la fase 2a todavía no textura el suelo); opcional |
| `ceiling_color` | Color | `#87CEEB` | Color plano del techo o cielo (la fase 2a todavía no tiene cielo); opcional |
| `pitch` | Número | `0` | Grados para mirar hacia arriba (+) o hacia abajo (−); 0 es la horizontal; opcional |
| `wall_textured` | Sí/No | Sí | Desactivado fuerza colores planos de bloque aunque haya texturas reales disponibles; opcional |
| `top_cast_res` | Número | `4` | Detalle de textura de las caras superior e inferior: filas muestreadas por cada N filas de pantalla (más alto = más rápido y más tosco; 0 = color medio plano en lugar de textura); opcional |
| `eye_height` | Número | `1.5` | Altura de la cámara sobre la capa en la que se apoya, en celdas (1,5 = un cuerpo de dos bloques de alto, necesario para ver la cara superior de un bloque de tu propia capa y subirte a él); opcional |
| `gravity` | Número | `0` | Aceleración hacia abajo, en celdas/paso², para la acción «Saltar» y para la gravedad y las caídas (nivel 7a). 0 (por omisión) mantiene el apoyo instantáneo original de «Mover con colisión», sin saltos; un valor típico ronda 0,04; opcional |
| `inventory` | Sí/No | No | Activado = «Romper bloque» recoge lo que rompe y «Colocar bloque» gasta de ese inventario (nivel 7c); desactivado (por omisión) = colocación ilimitada, como en modo creativo, igual que antes del nivel 7c; opcional |
| `generate` | Sí/No | No | Activado = genera terreno ondulado por procedimientos alrededor de la cámara según explora (nivel 7e), usando la Semilla de abajo; desactivado (por omisión) = solo existen los bloques colocados a mano o cargados, igual que antes del nivel 7e; opcional |
| `seed` | Número | `0` | Semilla del mundo para «Generar terreno»: la misma semilla produce siempre el mismo terreno en esta plataforma. Se ignora si «Generar terreno» está desactivado; opcional |

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

### Saltar

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `jump` |
| **Icono** | ⬆️ |
| **Categoría** | Vista 3D |

Da a la cámara de Block World velocidad hacia arriba, solo cuando está apoyada en suelo sólido (sin saltos dobles ni en el aire). Necesita la Gravedad configurada («Activar vista Block World») y «Aplicar gravedad» en el evento Paso, o nada la hará bajar de nuevo

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0.35` | Velocidad inicial hacia arriba, en celdas por paso; opcional |

### Cargar Block World

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `load_block_world` |
| **Icono** | 📂 |
| **Categoría** | Vista 3D |

Carga un mundo ya preparado (bloques colocados por un generador o escritos a mano) en la sala actual, sustituyendo los bloques que hubiera

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `data_file` | Texto | — | Ruta a un archivo JSON de mundo de bloques, relativa a la carpeta del proyecto (por ej. blocks/room1.json) |

### Mirar arriba / abajo

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_look_pitch` |
| **Icono** | 🔭 |
| **Categoría** | Vista 3D |

Inclina la vista de Block World hacia arriba o hacia abajo

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `pitch` | Número | `0` | Grados para mirar hacia arriba (+) o hacia abajo (−); 0 es la horizontal |
| `relative` | Sí/No | No | Activado = sumar al ángulo actual, para un control de vista que se mantiene pulsado; desactivado = fijarlo directamente; opcional |

### Mover con colisión

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `move_and_collide` |
| **Icono** | 🚶 |
| **Categoría** | Vista 3D |

Mueve este paso comprobándolo contra la rejilla de bloques, con apoyo automático (sube un bloque, baja cualquier altura); la capa z_layer de la cámara lo sigue si esta es la cámara de Block World

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `dx` | Número | `0` | Cuánto moverse en x en este paso, en píxeles |
| `dy` | Número | `0` | Cuánto moverse en y en este paso, en píxeles |
| `collide` | Sí/No | Sí | Desactivado ignora por completo la rejilla de bloques (vuelo o depuración); opcional |

### Colocar bloque

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `place_block` |
| **Icono** | 🧱 |
| **Categoría** | Vista 3D |

Coloca un bloque en la celda vacía a la que apunta la cámara: sin límite, salvo que el inventario de «Activar vista Block World» esté activado, en cuyo caso se toma de lo que haya recogido «Romper bloque»

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `block` | Elección | `stone` | Qué clase de bloque se coloca; Opciones: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `reach` | Número | `5` | Hasta dónde puedes construir hacia delante, en celdas de la rejilla; opcional |

### Elegir casilla de la barra

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `select_hotbar_slot` |
| **Icono** | 🔢 |
| **Categoría** | Vista 3D |

Elige qué bloque tiene seleccionado la barra de acceso rápido, para que «Colocar bloque» construya con él: pon la expresión «hotbar_block» en el parámetro Bloque de «Colocar bloque» para usarlo

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `index` | Número | `0` | Índice de la casilla de la barra, que da la vuelta en ambos extremos |
| `relative` | Sí/No | No | Activado = sumar a la casilla actual, para ir pasando con [ ] o con la rueda del ratón; desactivado = saltar directamente a ella; opcional |

### Definir protección de bloques

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_block_protection` |
| **Icono** | 🔒 |
| **Categoría** | Vista 3D |

Exige un tipo de bloque concreto en el inventario antes de que «Romper bloque» pueda quitar un tipo de bloque elegido: llámala una vez por cada tipo protegido; necesita el inventario de «Activar vista Block World» activado o la condición nunca podrá cumplirse

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `block_type` | Elección | `diamond_block` | Qué tipo de bloque queda protegido; Opciones: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `required_key` | Elección | `gold_block` | Qué tipo de bloque debe estar en el inventario para poder romperlo; Opciones: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Definir recompensa de bloque

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_block_reward` |
| **Icono** | 💎 |
| **Categoría** | Vista 3D |

Concede puntos cuando «Romper bloque» quita con éxito un tipo de bloque elegido: llámala una vez por cada tipo recompensado (por ejemplo en el evento Crear de la sala, justo después de «Activar vista Block World»). Un bloque de mineral o gema que se pica para recoger: colócalo en el terreno, registra su recompensa y romperlo dará los puntos automáticamente

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `block_type` | Elección | `diamond_block` | Qué tipo de bloque da puntos al romperlo; Opciones: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `points` | Número | `10` | Puntos concedidos por cada bloque de este tipo roto |

### Definir receta de fabricación

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_crafting_recipe` |
| **Icono** | 🛠️ |
| **Categoría** | Vista 3D |

Registra una receta que «Fabricar objeto» puede usar: llámala una vez por cada tipo de salida (por ejemplo en el evento Crear de la sala, justo después de «Activar vista Block World»). Hasta tres ranuras de ingredientes; deja vacías las ranuras 2/3 si la receta solo necesita uno o dos

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `output` | Elección | `brick` | Which block type this recipe produces; Opciones: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `output_count` | Número | `1` | How many of Output Block one craft produces |
| `input_1` | Elección | `stone` | First required block type; Opciones: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `input_1_count` | Número | `1` | How many of Input 1 the recipe consumes |
| `input_2` | Elección | — | Second required block type (blank = unused); Opciones: ``, `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow`; opcional |
| `input_2_count` | Número | `1` | How many of Input 2 the recipe consumes; opcional |
| `input_3` | Elección | — | Third required block type (blank = unused); Opciones: ``, `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow`; opcional |
| `input_3_count` | Número | `1` | How many of Input 3 the recipe consumes; opcional |

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
- [Red](Full-Action-Reference-Network-Actions_es) (15)
- [Partículas](Full-Action-Reference-Particles_es) (8)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
