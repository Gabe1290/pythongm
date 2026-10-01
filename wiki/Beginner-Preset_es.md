# Preajuste Principiante

*[Inicio](Home_es) | [Guía de Preajustes](Preset-Guide_es) | [Preajuste Intermedio](Intermediate-Preset_es)*

> **Generado automáticamente** a partir de `get_beginner()` en `config/blockly_config.py` por `tools/gen_preset_docs.py` — no editar a mano; vuelve a ejecutar el generador después de cambiar el preajuste.

> **Qué restringe realmente este preajuste:** este preajuste filtra TANTO la paleta de bloques visuales Blockly COMO los menús "Añadir Evento"/"Añadir Acción" del panel estructurado Eventos/Acciones — sea cual sea el editor que uses, solo aparecen los eventos/acciones listados abajo. El preajuste de un *proyecto* se define de dos formas: **`Preferencias > IDE Edition`** elige el predeterminado para los proyectos *nuevos* (edición Principiante -> este preajuste; los proyectos existentes nunca cambian al cambiar de edición), y **`Herramientas > Configurar bloques de acción...`** cambia el preajuste del proyecto *actualmente abierto* en cualquier momento. La edición predeterminada del IDE es Principiante, así que los proyectos nuevos de una instalación limpia empiezan exactamente en esta lista.

## Resumen

Este preajuste habilita **19** tipos de eventos y **54** tipos de acciones.

---

## Eventos

| Evento | Nombre del Bloque | Categoría | Descripción |
|-------|------------|----------|-------------|
| Create | `create` | Objeto | Se ejecuta una vez cuando la instancia se crea por primera vez |
| Step | `step` | Objeto | Se ejecuta en cada fotograma (úsalo para comprobaciones continuas) |
| Keyboard (held) | `keyboard` | Entrada | Se ejecuta continuamente mientras se mantiene pulsada una tecla (para movimiento suave) |
| Keyboard <No Key> | `keyboard_no_key` | Entrada | Se ejecuta cuando no hay ninguna tecla pulsada actualmente |
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
| Saltar a la posición inicial | `jump_to_start` | — |
| Mover hasta el contacto | `move_to_contact` | `direction`, `max_distance`, `object` |
| Invertir horizontal | `reverse_horizontal` | — |
| Invertir vertical | `reverse_vertical` | — |
| Establecer dirección y velocidad | `set_direction_speed` | `direction`, `speed` |
| Establecer gravedad | `set_gravity` | `direction`, `gravity` |
| Establecer velocidad horizontal | `set_hspeed` | `speed` |
| Establecer velocidad vertical | `set_vspeed` | `speed` |
| Empezar a moverse (dirección) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Detener movimiento | `stop_movement` | — |

### Cuadrícula

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Comprobar alineación a la cuadrícula | `test_alignment` | `hsnap`, `vsnap` |

### Instancia

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Cambiar instancia | `change_instance` | `object`, `perform_events` |
| Crear instancia | `create_instance` | `object`, `x`, `y`, `relative` |
| Destruir instancia | `destroy_instance` | — |
| Destruir en posición | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Comprobar número de instancias | `test_instance_count` | `object`, `number`, `operation` |

### Puntuación

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Dibujar vidas | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Dibujar puntuación | `draw_score` | `x`, `y`, `caption`, `relative` |
| Establecer vidas | `set_lives` | `value`, `relative` |
| Establecer puntuación | `set_score` | `value`, `relative` |
| Mostrar tabla de récords | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |

### Tiempo

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Establecer alarma | `set_alarm` | `alarm_number`, `steps` |
| Pausa | `sleep` | `milliseconds` |

### Sala

| Acción | Nombre del Bloque | Parámetros |
|--------|------------|------------|
| Finalizar juego | `game_end` | — |
| Si existe sala siguiente | `if_next_room_exists` | `then_actions`, `else_actions` |
| Si existe sala anterior | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Reiniciar sala | `restart_room` | — |
| Establecer fondo | `set_background` | `background`, `visible`, `foreground`, `tiled_h`, `tiled_v`, `hspeed`, `vspeed` |

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
| Dibujar texto | `draw_text` | `text`, `x`, `y`, `relative`, `color` |
| Reiniciar juego | `restart_game` | — |
| Establecer color de dibujo | `set_draw_color` | `color` |
| Establecer título de ventana | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
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
| Si colisión | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Si el objeto existe | `if_object_exists` | `object`, `not_flag` |
| Inicio de bloque | `start_block` | — |
| Comprobar probabilidad | `test_chance` | `sides` |
| Comprobar expresión | `test_expression` | `expression`, `then_actions`, `else_actions` |
| Comprobar variable | `test_variable` | `variable`, `value`, `scope`, `operation` |

---

## Ver También

- [Guía de Preajustes](Preset-Guide_es) — qué son los preajustes y cómo cambiarlos
- [Referencia de Eventos](Event-Reference_es) — descripción completa de cada evento
- [Referencia Completa de Acciones](Full-Action-Reference_es) — detalles completos de los parámetros de cada acción
- [Preajuste Intermedio](Intermediate-Preset_es) — el siguiente nivel
