# Preajuste Intermedio

*[Inicio](Home_es) | [Guía de Preajustes](Preset-Guide_es) | [Preajuste Principiante](Beginner-Preset_es)*

> **Generado automáticamente** a partir de `get_intermediate()` en `config/blockly_config.py` por `tools/gen_preset_docs.py` — no editar a mano; vuelve a ejecutar el generador después de cambiar el preajuste.

> **Qué restringe realmente este preajuste:** este preajuste filtra TANTO la paleta de bloques visuales Blockly COMO los menús "Añadir Evento"/"Añadir Acción" del panel estructurado Eventos/Acciones — sea cual sea el editor que uses, solo aparecen los eventos/acciones listados abajo. El preajuste de un *proyecto* se define de dos formas: **`Preferencias > IDE Edition`** elige el predeterminado para los proyectos *nuevos* (edición Principiante -> este preajuste; los proyectos existentes nunca cambian al cambiar de edición), y **`Herramientas > Configurar bloques de acción...`** cambia el preajuste del proyecto *actualmente abierto* en cualquier momento. La edición predeterminada del IDE es Principiante, así que los proyectos nuevos de una instalación limpia empiezan exactamente en esta lista.

## Resumen

Este preajuste habilita **21** tipos de eventos y **94** tipos de acciones.

---

## Eventos

| Evento | Nombre del Bloque | Categoría | Descripción |
|-------|------------|----------|-------------|
| Create | `create` | Objeto | Se ejecuta una vez cuando la instancia se crea por primera vez |
| Destroy | `destroy` | Objeto | Se ejecuta cuando la instancia es destruida |
| Step | `step` | Objeto | Se ejecuta en cada fotograma (úsalo para comprobaciones continuas) |
| Keyboard (held) | `keyboard` | Entrada | Se ejecuta continuamente mientras se mantiene pulsada una tecla (para movimiento suave) |
| Keyboard <No Key> | `keyboard_no_key` | Entrada | Se ejecuta cuando no hay ninguna tecla pulsada actualmente |
| Keyboard Press | `keyboard_press` | Entrada | Se ejecuta una vez cuando se pulsa una tecla por primera vez (para movimiento basado en cuadrícula) |
| Collision With... | `collision` | Colisión | Se ejecuta al colisionar con otro objeto |
| Begin Step | `begin_step` | Paso | Se ejecuta al principio de cada paso, antes que los demás eventos |
| End Step | `end_step` | Paso | Se ejecuta al final de cada paso, después de las colisiones pero antes de dibujar |
| Alarm | `alarm` | Tiempo | Se ejecuta cuando una alarma llega a cero |
| Draw | `draw` | Dibujo | Se ejecuta al dibujar el objeto (reemplaza el dibujo automático del sprite) |
| Draw GUI | `draw_gui` | Dibujo | Se dibuja por encima de todo lo demás (no afectado por la cámara/vista). Úsalo para el HUD, puntuación, vidas. |
| Room End | `room_end` | Sala | Se ejecuta cuando termina la sala |
| Room Start | `room_start` | Sala | Se ejecuta cuando comienza la sala (después de los eventos Create) |
| Game End | `game_end` | Juego | Se ejecuta cuando termina el juego |
| Game Start | `game_start` | Juego | Se ejecuta cuando comienza el juego (solo en la primera sala) |
| Animation End | `animation_end` | Otro | Se activa cuando la animación del sprite llega al último fotograma y reinicia |
| Intersect Boundary | `intersect_boundary` | Otro | Se ejecuta cuando la instancia toca el borde de la sala |
| No More Health | `no_more_health` | Otro | Se ejecuta cuando la salud llega a 0 o menos |
| No More Lives | `no_more_lives` | Otro | Se ejecuta cuando las vidas llegan a 0 o menos |
| Outside Room | `outside_room` | Otro | Se ejecuta cuando la instancia está completamente fuera de la sala |

---

## Acciones

### Movimiento

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Rebotar | `bounce` | — |
| Saltar a posición | `jump_to_position` | `x`, `y`, `relative` |
| Saltar a posición aleatoria | `jump_to_random` | `snap_h`, `snap_v` |
| Saltar a la posición inicial | `jump_to_start` | — |
| Mover hacia un punto | `move_towards_point` | `x`, `y`, `speed` |
| Invertir horizontal | `reverse_horizontal` | — |
| Invertir vertical | `reverse_vertical` | — |
| Establecer dirección y velocidad | `set_direction_speed` | `direction`, `speed` |
| Establecer fricción | `set_friction` | `friction` |
| Establecer gravedad | `set_gravity` | `direction`, `gravity` |
| Establecer velocidad horizontal | `set_hspeed` | `speed` |
| Establecer velocidad vertical | `set_vspeed` | `speed` |
| Empezar a moverse (dirección) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Detener movimiento | `stop_movement` | — |

### Cuadrícula

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Si en la cuadrícula | `if_on_grid` | `grid_size`, `then_actions`, `else_actions` |
| Ajustar a la cuadrícula | `snap_to_grid` | `grid_size` |
| Comprobar alineación a la cuadrícula | `test_alignment` | `hsnap`, `vsnap` |

### Instancia

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Cambiar instancia | `change_instance` | `object`, `perform_events` |
| Crear instancia | `create_instance` | `object`, `x`, `y`, `relative` |
| Crear instancia en movimiento | `create_moving_instance` | `object`, `x`, `y`, `speed`, `direction` |
| Crear instancia aleatoria | `create_random_instance` | `x`, `y`, `object1`, `object2`, `object3`, `object4` |
| Destruir instancia | `destroy_instance` | — |
| Destruir en posición | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Establecer índice de imagen | `set_image_index` | `frame` |
| Establecer velocidad de imagen | `set_image_speed` | `speed` |
| Establecer sprite | `set_sprite` | `sprite`, `subimage`, `speed` |
| Iniciar animación | `start_animation` | — |
| Detener animación | `stop_animation` | — |
| Comprobar número de instancias | `test_instance_count` | `object`, `number`, `operation` |

### Puntuación

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Borrar tabla de récords | `clear_highscore` | — |
| Dibujar barra de salud | `draw_health_bar` | `x1`, `y1`, `x2`, `y2`, `back_color`, `bar_color` |
| Dibujar vidas | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Dibujar puntuación | `draw_score` | `x`, `y`, `caption`, `relative` |
| Establecer salud | `set_health` | `value`, `relative` |
| Establecer vidas | `set_lives` | `value`, `relative` |
| Establecer puntuación | `set_score` | `value`, `relative` |
| Mostrar tabla de récords | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |
| Comprobar salud | `test_health` | `operation`, `value` |
| Comprobar vidas | `test_lives` | `value`, `operation` |
| Comprobar puntuación | `test_score` | `value`, `operation` |

### Tiempo

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Establecer alarma | `set_alarm` | `alarm_number`, `steps` |
| Pausa | `sleep` | `milliseconds` |

### Sala

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Comprobar sala | `check_room` | `room`, `not_flag` |
| Finalizar juego | `game_end` | — |
| Ir a la sala | `goto_room` | `room`, `transition` |
| Si existe sala siguiente | `if_next_room_exists` | `then_actions`, `else_actions` |
| Si existe sala anterior | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Sala siguiente | `next_room` | — |
| Sala anterior | `previous_room` | — |
| Reiniciar sala | `restart_room` | — |
| Establecer título de sala | `set_room_caption` | `caption` |

### Audio

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Comprobar reproducción de sonido | `check_sound` | `sound`, `not_flag` |
| Reproducir música | `play_music` | `music`, `loop`, `volume` |
| Reproducir sonido | `play_sound` | `sound`, `volume` |
| Establecer volumen | `set_volume` | `volume` |
| Detener música | `stop_music` | — |
| Detener sonido | `stop_sound` | `sound` |

### Juego

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Dibujar flecha | `draw_arrow` | `x1`, `y1`, `x2`, `y2`, `tip_size` |
| Dibujar fondo | `draw_background` | `background`, `x`, `y`, `tiled` |
| Dibujar elipse | `draw_ellipse` | `x1`, `y1`, `x2`, `y2`, `filled` |
| Dibujar línea | `draw_line` | `x1`, `y1`, `x2`, `y2` |
| Dibujar texto escalado | `draw_scaled_text` | `text`, `x`, `y`, `xscale`, `yscale` |
| Dibujar sprite | `draw_sprite` | `sprite`, `x`, `y`, `subimage` |
| Dibujar texto | `draw_text` | `text`, `x`, `y`, `relative` |
| Dibujar variable | `draw_variable` | `x`, `y`, `variable` |
| Rellenar pantalla con color | `fill_color` | `color` |
| Abrir página web | `open_webpage` | `url` |
| Reiniciar juego | `restart_game` | — |
| Establecer color | `set_color` | `color`, `alpha` |
| Establecer color de dibujo | `set_draw_color` | `color` |
| Establecer fuente de dibujo | `set_draw_font` | `font`, `halign`, `valign` |
| Establecer título de ventana | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Mostrar información del juego | `show_info` | — |
| Mostrar mensaje | `show_message` | `message` |

### Control

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Comprobar si vacío | `check_empty` | `x`, `y`, `relative`, `objects` |
| Comentario | `comment` | `text` |
| Si no | `else_action` | — |
| Fin de bloque | `end_block` | — |
| Ejecutar código | `execute_code` | `code` |
| Ejecutar script | `execute_script` | `script`, `arg0`, `arg1`, `arg2`, `arg3`, `arg4` |
| Salir del evento | `exit_event` | — |
| Si se puede empujar | `if_can_push` | `direction`, `object_type`, `then_action`, `else_action` |
| Si colisión | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Si el objeto existe | `if_object_exists` | `object`, `not_flag` |
| Inicio de bloque | `start_block` | — |
| Comprobar probabilidad | `test_chance` | `sides` |
| Hacer una pregunta | `test_question` | `question` |
| Comprobar variable | `test_variable` | `variable`, `value`, `scope`, `operation` |

### Vistas

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Habilitar vistas | `enable_views` | `enable` |
| Configurar vista | `set_view` | `view`, `visible`, `view_x`, `view_y`, `view_w`, `view_h`, `port_x`, `port_y`, `port_w`, `port_h`, `follow`, `hborder`, `vborder`, `hspeed`, `vspeed` |

### Vista 3D

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Dibujar HUD DOOM | `draw_doom_hud` | `x`, `y`, `width`, `height`, `back_color`, `divider_color`, `text_color`, `health_label`, `health_bar_width`, `health_bar_height`, `bar_color`, `face_sprite`, `face_frames`, `score_label`, `lives_sprite`, `lives_scale`, `objective_value`, `objective_label` |
| Dibujar minimapa | `draw_minimap` | `x`, `y`, `size`, `back_color`, `wall_color`, `player_color` |
| Habilitar vista Raycast | `enable_raycast_view` | `enable`, `camera_object`, `fov`, `render_distance`, `cell_size`, `columns`, `wall_color`, `floor_color`, `ceiling_color`, `wall_texture`, `sky_texture`, `floor_texture`, `ceiling_texture`, `wall_textured`, `floor_cast_res`, `viewport_height` |
| Establecer ángulo de mirada | `set_facing_angle` | `angle`, `relative` |

---

## Ver También

- [Guía de Preajustes](Preset-Guide_es) — qué son los preajustes y cómo cambiarlos
- [Referencia de Eventos](Event-Reference_es) — descripción completa de cada evento
- [Referencia Completa de Acciones](Full-Action-Reference_es) — detalles completos de los parámetros de cada acción
- [Preajuste Principiante](Beginner-Preset_es) — el nivel por debajo de este
