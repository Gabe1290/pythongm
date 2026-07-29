# Referencia completa de acciones

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

Esta página enumera todas las **109** acciones disponibles en PyGameMaker, exactamente como aparecen en el selector de acciones del IDE (incluido el complemento Audio y la extensión Vista 3D). Las acciones son comandos que se ejecutan cuando se activa un evento.

## Categorías

- [Movimiento](#movement) (20)
- [Instancia](#instance) (12)
- [Puntuación](#score) (11)
- [Sala](#room) (9)
- [Tiempo](#timing) (2)
- [Audio](#audio) (6)
- [Juego](#game) (20)
- [Control](#control) (19)
- [Cuadrícula](#grid) (4)
- [Vistas](#views) (2)
- [Vista 3D](#3d-view) (4)

---

<a id="movement"></a>
## Movimiento

### Rebotar

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `bounce` |
| **Categoría** | Movimiento |

Rebotar en objetos sólidos

*Parámetros:* ninguno

### Saltar a posición

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `jump_to_position` |
| **Icono** | 📍 |
| **Categoría** | Movimiento |

Mover instantáneamente a una posición

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `relative` | Sí/No | No | Sumar a la posición actual en lugar de establecer una absoluta |

### Saltar a posición aleatoria

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `jump_to_random` |
| **Icono** | 🎲↪️ |
| **Categoría** | Movimiento |

Teletransportar a una posición aleatoria (opcionalmente ajustada a la cuadrícula)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `snap_h` | Número | `1` | Ajuste horizontal a la cuadrícula (1 = sin ajuste) |
| `snap_v` | Número | `1` | Ajuste vertical a la cuadrícula (1 = sin ajuste) |

### Saltar a la posición inicial

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `jump_to_start` |
| **Icono** | ↩️ |
| **Categoría** | Movimiento |

Devolver la instancia a su posición de creación

*Parámetros:* ninguno

### Movimiento libre

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `move_free` |
| **Icono** | 🧭 |
| **Categoría** | Movimiento |

Mover en una dirección precisa (0-360 grados)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `0` | Dirección en grados (0=derecha, 90=arriba, antihorario) |
| `speed` | Número | `4.0` | Velocidad de movimiento |

### Mover por cuadrícula

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `move_grid` |
| **Icono** | ▦ |
| **Categoría** | Movimiento |

Mover una celda de la cuadrícula en la dirección indicada

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Elección | `right` | Dirección de movimiento; Opciones: `left`, `right`, `up`, `down` |
| `grid_size` | Número | `32` | Tamaño de la celda de la cuadrícula en píxeles |

### Mover hacia un punto

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `move_towards_point` |
| **Icono** | 🎯 |
| **Categoría** | Movimiento |

Mover hacia un punto a una velocidad dada

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | X de destino |
| `y` | Número | `0` | Y de destino |
| `speed` | Número | `4.0` | Velocidad de movimiento |

### Mover hasta el contacto

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `move_to_contact` |
| **Icono** | 🎯 |
| **Categoría** | Movimiento |

Mover en una dirección hasta tocar un objeto (o la distancia máxima)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Texto | `direction` | Dirección en grados (0=derecha, 90=arriba, 180=izquierda, 270=abajo) o una expresión. Predeterminado «direction» = el rumbo actual de la instancia (ajuste a la colisión). |
| `max_distance` | Número | `1000` | Distancia máxima de movimiento, en píxeles |
| `object` | Objeto | `all` | Detenerse al contacto con: «all» todas las instancias, «solid» solo objetos sólidos, o un nombre de objeto específico.; Opciones: `all`, `solid`; opcional |

### Invertir horizontal

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `reverse_horizontal` |
| **Icono** | ↔️ |
| **Categoría** | Movimiento |

Invertir la dirección del movimiento horizontal

*Parámetros:* ninguno

### Invertir vertical

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `reverse_vertical` |
| **Icono** | ↕️ |
| **Categoría** | Movimiento |

Invertir la dirección del movimiento vertical

*Parámetros:* ninguno

### Establecer dirección

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_direction` |
| **Icono** | 🧭 |
| **Categoría** | Movimiento |

Establecer la dirección del movimiento

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `0` | Dirección en grados (0=derecha, 90=arriba) |

### Establecer dirección y velocidad

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_direction_speed` |
| **Icono** | 🧭 |
| **Categoría** | Movimiento |

Establecer la dirección (en grados) y la magnitud de velocidad de la instancia

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `0` | Dirección en grados (0=derecha, 90=arriba) |
| `speed` | Número | `4.0` | Velocidad en píxeles por fotograma |

### Establecer fricción

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_friction` |
| **Icono** | 🛑 |
| **Categoría** | Movimiento |

Establecer la fricción (desaceleración)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `friction` | Número | `0.1` | Cantidad de fricción (se resta de la velocidad en cada paso) |

### Establecer gravedad

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_gravity` |
| **Icono** | ⬇️ |
| **Categoría** | Movimiento |

Establecer la dirección y la fuerza de la gravedad

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `270` | Dirección de la gravedad en grados (270=abajo) |
| `gravity` | Número | `0.5` | Fuerza de la gravedad (se añade en cada paso) |

### Establecer velocidad horizontal

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_hspeed` |
| **Icono** | ↔️ |
| **Categoría** | Movimiento |

Establecer la velocidad de movimiento horizontal

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0` | Velocidad en píxeles por fotograma |

### Establecer velocidad

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_speed` |
| **Icono** | ⚡ |
| **Categoría** | Movimiento |

Establecer la velocidad de movimiento (magnitud)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0` | Velocidad de movimiento |

### Establecer velocidad vertical

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_vspeed` |
| **Icono** | ↕️ |
| **Categoría** | Movimiento |

Establecer la velocidad de movimiento vertical

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0` | Velocidad en píxeles por fotograma |

### Empezar a moverse (dirección)

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `start_moving_direction` |
| **Icono** | ➡️ |
| **Categoría** | Movimiento |

Empezar a moverse en una dirección a una velocidad dada

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `directions` | Elección múltiple | right | Dirección(es) de movimiento — marca una, o varias para elegir una al azar en cada paso. La celda central es detenerse.; Opciones: `up-left`, `up`, `up-right`, `left`, `stop`, `right`, `down-left`, `down`, `down-right` |
| `direction_expr` | Texto | — | Alternativa: expresión libre evaluada como grados; opcional |
| `speed` | Número | `4.0` | Velocidad en píxeles por fotograma |

### Detener movimiento

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stop_movement` |
| **Icono** | 🛑 |
| **Categoría** | Movimiento |

Poner ambas velocidades a cero

*Parámetros:* ninguno

### Envolver alrededor de la sala

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `wrap_around_room` |
| **Icono** | 🔄 |
| **Categoría** | Movimiento |

Reaparecer en el lado opuesto de la sala

*Parámetros:* ninguno

---

<a id="instance"></a>
## Instancia

### Cambiar instancia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `change_instance` |
| **Icono** | 🔄 |
| **Categoría** | Instancia |
| **Se aplica a** | self / other / object |

Transformar en otro tipo de objeto

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Nuevo tipo de objeto |
| `perform_events` | Sí/No | Sí | Ejecutar los eventos destruir/crear |

### Crear instancia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_instance` |
| **Icono** | ✨ |
| **Categoría** | Instancia |

Crear una nueva instancia

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Objeto a crear |
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `relative` | Sí/No | No | Posición relativa a la instancia actual |

### Crear instancia en movimiento

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_moving_instance` |
| **Icono** | ✨➡️ |
| **Categoría** | Instancia |

Crear una instancia e iniciarla en una dirección

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Objeto a crear |
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `speed` | Número | `0` | Magnitud de velocidad inicial |
| `direction` | Número | `0` | Dirección inicial en grados |

### Crear instancia aleatoria

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_random_instance` |
| **Icono** | 🎲 |
| **Categoría** | Instancia |

Crear uno de varios tipos de objeto elegido al azar

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `object1` | Objeto | — | Primer objeto candidato; opcional |
| `object2` | Objeto | — | Segundo objeto candidato; opcional |
| `object3` | Objeto | — | Tercer objeto candidato; opcional |
| `object4` | Objeto | — | Cuarto objeto candidato; opcional |

### Destruir instancia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `destroy_instance` |
| **Icono** | 💥 |
| **Categoría** | Instancia |
| **Se aplica a** | self / other / object |

Destruir una instancia

*Parámetros:* ninguno

### Destruir en posición

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `destroy_at_position` |
| **Icono** | 💣 |
| **Categoría** | Instancia |

Destruir instancias dentro de un radio de (x, y)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | `all` | Qué tipo de objeto destruir. «all» destruye cada instancia en el radio; «solid» solo las sólidas (p. ej. muros); «non-solid» todo excepto los sólidos.; Opciones: `all`, `solid`, `non-solid` |
| `x` | Texto | `self.x` | Posición X (expresión permitida, p. ej. self.x) |
| `y` | Texto | `self.y` | Posición Y (expresión permitida, p. ej. self.y) |
| `relative` | Sí/No | No | Tratar X/Y como desplazamientos desde la posición de esta instancia en lugar de coordenadas absolutas; opcional |
| `radius` | Número | `32` | Radio en píxeles alrededor de (x, y). Predeterminado 32 = ~una celda de la cuadrícula. |

### Establecer índice de imagen

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_image_index` |
| **Icono** | 🖼️ |
| **Categoría** | Instancia |

Establecer el fotograma de animación actual del sprite de la instancia

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `frame` | Número | `0` | Índice de fotograma |

### Establecer velocidad de imagen

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_image_speed` |
| **Icono** | ⏩ |
| **Categoría** | Instancia |

Establecer la velocidad de reproducción de la animación del sprite de la instancia

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `1.0` | Fotogramas avanzados por paso (0 = en pausa) |

### Establecer sprite

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_sprite` |
| **Icono** | 🖼️ |
| **Categoría** | Instancia |

Cambiar el sprite y/o el fotograma/velocidad de animación de una instancia

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sprite` | Sprite | `<self>` | Sprite a usar (o «<self>» para mantener el actual) |
| `subimage` | Número | `-1` | Índice de fotograma a establecer; -1 lo deja sin cambios |
| `speed` | Número | `-1` | Velocidad de animación; -1 la deja sin cambios |

### Iniciar animación

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `start_animation` |
| **Icono** | ▶️ |
| **Categoría** | Instancia |

Reanudar la animación del sprite de la instancia (image_speed = 1)

*Parámetros:* ninguno

### Detener animación

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stop_animation` |
| **Icono** | ⏸️ |
| **Categoría** | Instancia |

Pausar la animación del sprite de la instancia (image_speed = 0)

*Parámetros:* ninguno

### Comprobar número de instancias

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_instance_count` |
| **Icono** | ❓🔢 |
| **Categoría** | Instancia |

Condición: comparar el número de instancias de un objeto

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Objeto a contar |
| `number` | Número | `0` | Valor de comparación |
| `operation` | Elección | `equal` | Operador de comparación; Opciones: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="score"></a>
## Puntuación

### Borrar tabla de récords

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `clear_highscore` |
| **Icono** | 🗑️🏆 |
| **Categoría** | Puntuación |

Borrar todas las entradas de la tabla de récords

*Parámetros:* ninguno

### Dibujar barra de salud

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_health_bar` |
| **Icono** | 🩺 |
| **Categoría** | Puntuación |

Dibujar la salud actual como una barra de dos colores

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x1` | Número | `0` | X izquierda |
| `y1` | Número | `0` | Y superior |
| `x2` | Número | `100` | X derecha |
| `y2` | Número | `20` | Y inferior |
| `back_color` | Color | `#FF0000` | Color de fondo (vacío) |
| `bar_color` | Color | `#00FF00` | Color de relleno (salud) |

### Dibujar vidas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_lives` |
| **Icono** | 🖍️❤️ |
| **Categoría** | Puntuación |

Dibujar el número de vidas actual como imágenes de sprite repetidas

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `sprite` | Sprite | — | Sprite dibujado una vez por cada vida restante; opcional |
| `scale` | Número | `1.0` | Factor de escala uniforme para el icono de vida (1.0 = tamaño nativo); opcional |
| `relative` | Sí/No | No | Dibujar respecto a la posición de esta instancia en lugar de coordenadas de pantalla absolutas; opcional |

### Dibujar puntuación

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_score` |
| **Icono** | 🖍️🏆 |
| **Categoría** | Puntuación |

Dibujar la puntuación actual en la pantalla

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `caption` | Texto | `Score: ` | Texto mostrado antes del valor de la puntuación; opcional |
| `relative` | Sí/No | No | Dibujar respecto a la posición de esta instancia en lugar de coordenadas de pantalla absolutas; opcional |

### Establecer salud

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_health` |
| **Icono** | 💚 |
| **Categoría** | Puntuación |

Establecer la salud, o sumarle con «Relativo»

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `value` | Número | `100` | Valor de salud (0-100) |
| `relative` | Sí/No | No | Sumar a la salud actual en lugar de reemplazarla |

### Establecer vidas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_lives` |
| **Icono** | ❤️ |
| **Categoría** | Puntuación |

Establecer las vidas, o sumarles con «Relativo»

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `value` | Número | `3` | Número de vidas |
| `relative` | Sí/No | No | Sumar a las vidas actuales en lugar de reemplazarlas |

### Establecer puntuación

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_score` |
| **Icono** | 🏆 |
| **Categoría** | Puntuación |

Establecer la puntuación, o sumarle con «Relativo»

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `value` | Número | `0` | Valor de puntuación a establecer |
| `relative` | Sí/No | No | Sumar a la puntuación actual en lugar de reemplazarla |

### Mostrar tabla de récords

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `show_highscore` |
| **Icono** | 🏆 |
| **Categoría** | Puntuación |

Mostrar el diálogo de la tabla de récords

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `background` | Color | `#FFFFDD` | Color de fondo del diálogo; opcional |
| `new_color` | Color | `#FF0000` | Color usado para la nueva entrada (que califica); opcional |
| `other_color` | Color | `#000000` | Color usado para las demás entradas; opcional |
| `allow_new_entry` | Sí/No | Sí | Pedir el nombre si la puntuación actual califica |

### Comprobar salud

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_health` |
| **Icono** | ❓💚 |
| **Categoría** | Puntuación |

Condición: comparar la salud actual con un valor

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `operation` | Elección | `equal` | Operador de comparación; Opciones: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |
| `value` | Número | `0` | Valor de comparación |

### Comprobar vidas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_lives` |
| **Icono** | ❓❤️ |
| **Categoría** | Puntuación |

Condición: comparar el número de vidas con un valor

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `value` | Número | `0` | Valor de comparación |
| `operation` | Elección | `equal` | Operador de comparación; Opciones: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

### Comprobar puntuación

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_score` |
| **Icono** | ❓🏆 |
| **Categoría** | Puntuación |

Condición: comparar la puntuación con un valor

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `value` | Número | `0` | Valor de comparación |
| `operation` | Elección | `equal` | Operador de comparación; Opciones: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="room"></a>
## Sala

### Comprobar sala

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `check_room` |
| **Icono** | ❓🚪 |
| **Categoría** | Sala |

Condición: verdadero si la sala actual coincide

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `room` | Sala | — | Sala a comparar |
| `not_flag` | Sí/No | No | Invertir el resultado; opcional |

### Finalizar juego

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `game_end` |
| **Icono** | 🛑🎮 |
| **Categoría** | Sala |

Finalizar el juego

*Parámetros:* ninguno

### Ir a la sala

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `goto_room` |
| **Icono** | 🚪 |
| **Categoría** | Sala |

Cambiar a una sala específica

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `room` | Sala | — | Nombre de la sala de destino |
| `transition` | Elección | `none` | Efecto de transición (actualmente aceptado pero no renderizado); Opciones: `none`; opcional |

### Si existe sala siguiente

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_next_room_exists` |
| **Icono** | ❓➡️ |
| **Categoría** | Sala |

Comprobar si hay una sala siguiente después de la actual

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `then_actions` | Lista de acciones | — | Acciones si existe la sala siguiente |
| `else_actions` | Lista de acciones | — | Acciones si la sala siguiente no existe |

### Si existe sala anterior

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_previous_room_exists` |
| **Icono** | ❓⬅️ |
| **Categoría** | Sala |

Comprobar si hay una sala anterior antes de la actual

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `then_actions` | Lista de acciones | — | Acciones si existe la sala anterior |
| `else_actions` | Lista de acciones | — | Acciones si la sala anterior no existe |

### Sala siguiente

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `next_room` |
| **Icono** | ➡️ |
| **Categoría** | Sala |

Ir a la sala siguiente

*Parámetros:* ninguno

### Sala anterior

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `previous_room` |
| **Icono** | ⬅️ |
| **Categoría** | Sala |

Ir a la sala anterior

*Parámetros:* ninguno

### Reiniciar sala

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `restart_room` |
| **Icono** | 🔄 |
| **Categoría** | Sala |

Reiniciar la sala actual

*Parámetros:* ninguno

### Establecer título de sala

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_room_caption` |
| **Icono** | 🏷️ |
| **Categoría** | Sala |

Establecer el título de la ventana del juego

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `caption` | Texto | — | Texto del título de la ventana |

---

<a id="timing"></a>
## Tiempo

### Establecer alarma

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_alarm` |
| **Icono** | ⏰ |
| **Categoría** | Tiempo |

Establecer una alarma

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `alarm_number` | Número | `0` | Qué alarma (0-11) |
| `steps` | Número | `30` | Número de pasos hasta que salte la alarma (30 = 0,5 s a 60 FPS) |

### Pausa

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `sleep` |
| **Icono** | 💤 |
| **Categoría** | Tiempo |

Pausar el juego durante un número de milisegundos y luego continuar. Los sonidos siguen sonando durante la pausa (por ejemplo, para dejar que un sonido termine antes de cambiar de sala). Nota: el renderizado y la entrada se congelan durante la pausa, así que mantén duraciones cortas

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `milliseconds` | Número | `1000` | Duración de la pausa, en milisegundos (1000 = 1 segundo) |

---

<a id="audio"></a>
## Audio

### Comprobar reproducción de sonido

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `check_sound` |
| **Icono** | ❓🔊 |
| **Categoría** | Audio |

Condición: verdadero si el sonido indicado se está reproduciendo actualmente

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sound` | Sonido | — | Sonido a comprobar |
| `not_flag` | Sí/No | No | Invertir el resultado; opcional |

### Reproducir música

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `play_music` |
| **Icono** | 🎵 |
| **Categoría** | Audio |

Reproducir música de fondo (en bucle)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `music` | Sonido | — | Archivo de música a reproducir |
| `loop` | Sí/No | Sí | Reproducir la música en bucle |
| `volume` | Número | `0.7` | Volumen (de 0.0 a 1.0) |

### Reproducir sonido

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `play_sound` |
| **Icono** | 🔊 |
| **Categoría** | Audio |

Reproducir un efecto de sonido una vez

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sound` | Sonido | — | Sonido a reproducir |
| `volume` | Número | `1.0` | Volumen (de 0.0 a 1.0) |

### Establecer volumen

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_volume` |
| **Icono** | 🔉 |
| **Categoría** | Audio |

Establecer el volumen general de sonido/música

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `volume` | Número | `1.0` | Volumen (de 0.0 a 1.0) |

### Detener música

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stop_music` |
| **Icono** | 🔇 |
| **Categoría** | Audio |

Detener la música de fondo

*Parámetros:* ninguno

### Detener sonido

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stop_sound` |
| **Icono** | 🔇 |
| **Categoría** | Audio |

Detener un sonido en reproducción

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sound` | Sonido | — | Sonido a detener |

---

<a id="game"></a>
## Juego

### Dibujar flecha

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_arrow` |
| **Icono** | ➡️ |
| **Categoría** | Juego |

Dibujar una flecha de un punto a otro

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x1` | Número | `0` | X inicial |
| `y1` | Número | `0` | Y inicial |
| `x2` | Número | `100` | X punta |
| `y2` | Número | `100` | Y punta |
| `tip_size` | Número | `10` | Tamaño de la punta de la flecha en píxeles |

### Dibujar fondo

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_background` |
| **Icono** | 🌄 |
| **Categoría** | Juego |

Dibujar una imagen de fondo, opcionalmente en mosaico por toda la pantalla

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `background` | Texto | — | Nombre del recurso de fondo |
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `tiled` | Sí/No | No | En mosaico por toda la pantalla; opcional |

### Dibujar círculo

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_circle` |
| **Icono** | ⭕ |
| **Categoría** | Juego |

Dibujar un círculo relleno o solo contorno

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | X centro |
| `y` | Número | `0` | Y centro |
| `radius` | Número | `50` | Radio del círculo |
| `filled` | Sí/No | Sí | Relleno o solo contorno; opcional |

### Dibujar elipse

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_ellipse` |
| **Icono** | 🥚 |
| **Categoría** | Juego |

Dibujar una elipse rellena o solo contorno dentro de un recuadro

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x1` | Número | `0` | X izquierda |
| `y1` | Número | `0` | Y superior |
| `x2` | Número | `100` | X derecha |
| `y2` | Número | `100` | Y inferior |
| `filled` | Sí/No | Sí | Relleno o solo contorno; opcional |

### Dibujar línea

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_line` |
| **Icono** | 📏 |
| **Categoría** | Juego |

Dibujar una línea entre dos puntos

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x1` | Número | `0` | X inicial |
| `y1` | Número | `0` | Y inicial |
| `x2` | Número | `100` | X final |
| `y2` | Número | `100` | Y final |

### Dibujar rectángulo

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_rectangle` |
| **Icono** | 🟥 |
| **Categoría** | Juego |

Dibujar un rectángulo relleno o solo contorno

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x1` | Número | `0` | X izquierda |
| `y1` | Número | `0` | Y superior |
| `x2` | Número | `100` | X derecha |
| `y2` | Número | `100` | Y inferior |
| `filled` | Sí/No | Sí | Relleno o solo contorno; opcional |

### Dibujar texto escalado

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_scaled_text` |
| **Icono** | 🖍️ |
| **Categoría** | Juego |

Dibujar texto a una escala arbitraria

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `text` | Texto | — | Texto a dibujar |
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `xscale` | Número | `1.0` | Factor de escala horizontal |
| `yscale` | Número | `1.0` | Factor de escala vertical |

### Dibujar sprite

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_sprite` |
| **Icono** | 🖼️ |
| **Categoría** | Juego |

Dibujar un fotograma de sprite en una posición

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite a dibujar |
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `subimage` | Número | `0` | Índice de fotograma a dibujar |

### Dibujar texto

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_text` |
| **Icono** | 🖍️ |
| **Categoría** | Juego |

Dibujar una cadena de texto en una posición

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `text` | Texto | — | Texto a dibujar (admite expresiones) |
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `relative` | Sí/No | No | Dibujar respecto a la posición de esta instancia en lugar de coordenadas de pantalla absolutas; opcional |

### Dibujar variable

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_variable` |
| **Icono** | 🔢 |
| **Categoría** | Juego |

Dibujar el valor de una variable en la pantalla

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `variable` | Texto | — | Nombre de variable (self.var, global.var o nombre simple) |

### Rellenar pantalla con color

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `fill_color` |
| **Icono** | 🪣 |
| **Categoría** | Juego |

Rellenar toda el área de visualización con un color uniforme

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `color` | Color | `#000000` | Color RGB hexadecimal |

### Abrir página web

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `open_webpage` |
| **Icono** | 🌐 |
| **Categoría** | Juego |

Abrir una URL en el navegador predeterminado

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `url` | Texto | — | Dirección web a abrir |

### Reiniciar juego

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `restart_game` |
| **Icono** | 🔁🎮 |
| **Categoría** | Juego |

Reiniciar el juego desde la sala inicial

*Parámetros:* ninguno

### Establecer transparencia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_alpha` |
| **Icono** | 🌫️ |
| **Categoría** | Juego |

Establecer la transparencia de dibujo para los siguientes dibujos

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `alpha` | Número | `1.0` | Opacidad de 0.0 (transparente) a 1.0 (opaco) |

### Establecer color

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_color` |
| **Icono** | 🎨 |
| **Categoría** | Juego |

Establecer el color y la transparencia de dibujo para los siguientes dibujos

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `color` | Color | `#FFFFFF` | Color RGB hexadecimal |
| `alpha` | Número | `1.0` | Opacidad 0.0–1.0; opcional |

### Establecer color de dibujo

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_draw_color` |
| **Icono** | 🎨 |
| **Categoría** | Juego |

Establecer el color usado por las siguientes acciones draw_*

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `color` | Color | `#000000` | Color RGB hexadecimal |

### Establecer fuente de dibujo

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_draw_font` |
| **Icono** | 🔤 |
| **Categoría** | Juego |

Establecer la fuente y la alineación para el siguiente dibujo de texto

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `font` | Texto | — | Nombre del recurso de fuente (vacío = fuente predeterminada); opcional |
| `halign` | Elección | `left` | Alineación horizontal del texto; Opciones: `left`, `center`, `right` |
| `valign` | Elección | `top` | Alineación vertical del texto; Opciones: `top`, `middle`, `bottom` |

### Establecer título de ventana

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_window_caption` |
| **Icono** | 🪟 |
| **Categoría** | Juego |

Configurar la visualización de puntuación/vidas/salud en el título de la ventana

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `show_score` | Sí/No | Sí | Añadir la puntuación actual al título de la ventana |
| `show_lives` | Sí/No | Sí | Añadir el número de vidas actual al título de la ventana |
| `show_health` | Sí/No | No | Añadir el valor de salud actual al título de la ventana |
| `caption` | Texto | — | Prefijo de título opcional mostrado antes de los contadores; opcional |

### Mostrar información del juego

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `show_info` |
| **Icono** | ℹ️ |
| **Categoría** | Juego |

Mostrar la pantalla de información del juego

*Parámetros:* ninguno

### Mostrar mensaje

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `show_message` |
| **Icono** | 💬 |
| **Categoría** | Juego |

Mostrar un mensaje

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `message` | Texto | `Hello!` | Texto del mensaje |

---

<a id="control"></a>
## Control

### Comprobar si vacío

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `check_empty` |
| **Icono** | 🔍 |
| **Categoría** | Control |

Verdadero cuando (x, y) está libre de colisiones. Usa con start_block/end_block para condicionar la(s) acción(es) siguiente(s), al estilo GM

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `self.x` | Posición X a comprobar (expresión permitida, p. ej. self.x + 32) |
| `y` | Texto | `self.y` | Posición Y a comprobar (expresión permitida, p. ej. self.y + 32) |
| `relative` | Sí/No | No | Tratar X/Y como desplazamientos desde la posición de esta instancia en lugar de coordenadas absolutas; opcional |
| `objects` | Elección | `solid` | Qué instancias cuentan como ocupantes de la posición; Opciones: `solid`, `all` |

### Comentario

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `comment` |
| **Icono** | ⚠️ |
| **Categoría** | Control |

Un comentario en la lista de acciones (sin efecto en ejecución)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `text` | Texto | — | Texto de comentario libre; opcional |

### Si no

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `else_action` |
| **Icono** | ⚡ |
| **Categoría** | Control |

Marca la rama «si no» de una condición

*Parámetros:* ninguno

### Fin de bloque

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `end_block` |
| **Icono** | 📁 |
| **Categoría** | Control |

Terminar un bloque de acciones

*Parámetros:* ninguno

### Ejecutar código

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `execute_code` |
| **Icono** | 📜 |
| **Categoría** | Control |

Ejecutar un bloque de código Python integrado

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `code` | Código | — | Código Python a evaluar respecto a la instancia |

### Ejecutar script

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `execute_script` |
| **Icono** | 📜 |
| **Categoría** | Control |

Ejecutar uno de los scripts del proyecto

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `script` | Script | — | Nombre del script del proyecto a ejecutar |
| `arg0` | Texto | — | Disponible en el script como argument0; opcional |
| `arg1` | Texto | — | Disponible en el script como argument1; opcional |
| `arg2` | Texto | — | Disponible en el script como argument2; opcional |
| `arg3` | Texto | — | Disponible en el script como argument3; opcional |
| `arg4` | Texto | — | Disponible en el script como argument4; opcional |

### Salir del evento

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `exit_event` |
| **Icono** | 🚪 |
| **Categoría** | Control |

Detener la ejecución de las acciones restantes en este evento

*Parámetros:* ninguno

### Si se puede empujar

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_can_push` |
| **Icono** | 📦 |
| **Categoría** | Control |

Comprobar si se puede empujar una caja/objeto en la dirección actual (estilo Sokoban)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Elección | `facing` | Dirección a comprobar para el empuje; Opciones: `facing` |
| `object_type` | Texto | `box` | Tipo de objeto empujado |
| `then_action` | Elección | `push_and_move` | Acción si el empuje es posible; Opciones: `push_and_move`, `none` |
| `else_action` | Elección | `stop_movement` | Acción si el empuje está bloqueado; Opciones: `stop_movement`, `none` |

### Si colisión

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_collision` |
| **Icono** | ❓💥 |
| **Categoría** | Control |

Condición: verdadero si la instancia colisionaría en el desplazamiento (x, y)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Desplazamiento horizontal a comprobar |
| `y` | Número | `0` | Desplazamiento vertical a comprobar |
| `object` | Texto | `any` | «any», «solid» o un nombre de objeto; Opciones: `any`, `solid`; opcional |
| `not_flag` | Sí/No | No | Negar el resultado; opcional |

### Si colisión en

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_collision_at` |
| **Icono** | 🎯 |
| **Categoría** | Control |

Comprobar una colisión en una posición

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `self.x + 32` | Expresión de la posición X |
| `y` | Texto | `self.y` | Expresión de la posición Y |
| `object_type` | Elección | `any` | Tipo de objeto a comprobar; Opciones: `any`, `solid` |
| `then_actions` | Lista de acciones | — | Acciones si se encuentra colisión |
| `else_actions` | Lista de acciones | — | Acciones si no hay colisión |

### Si condición

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_condition` |
| **Icono** | ❓ |
| **Categoría** | Control |

Comprobación condicional con acciones entonces/si no

*Parámetros:* ninguno

### Si el objeto existe

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_object_exists` |
| **Icono** | ❓ |
| **Categoría** | Control |

Condición: verdadero si existe al menos una instancia del objeto

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Tipo de objeto a comprobar |
| `not_flag` | Sí/No | No | Negar el resultado (actuar cuando el objeto NO existe); opcional |

### Repetir

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `repeat` |
| **Icono** | 🔁 |
| **Categoría** | Control |

Repetir la acción/el bloque siguiente N veces

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `times` | Número | `10` | Número de repeticiones |
| `actions` | Lista de acciones | — | Acciones a repetir |

### Establecer variable

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_variable` |
| **Icono** | 📝 |
| **Categoría** | Control |

Establecer una variable de instancia o global

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `variable` | Texto | — | Nombre de la variable |
| `value` | Texto | `0` | Valor (número, cadena o expresión) |
| `scope` | Elección | `self` | Ámbito de la variable; Opciones: `self`, `other`, `global` |
| `relative` | Sí/No | No | Sumar al valor actual en lugar de reemplazarlo |

### Inicio de bloque

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `start_block` |
| **Icono** | 📂 |
| **Categoría** | Control |

Iniciar un bloque de acciones (para agrupar)

*Parámetros:* ninguno

### Comprobar probabilidad

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_chance` |
| **Icono** | 🎲❓ |
| **Categoría** | Control |

Condición: verdadero con probabilidad 1 entre «sides»

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sides` | Número | `6` | Una probabilidad de 1 entre N de ser verdadero |

### Comprobar expresión

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_expression` |
| **Icono** | ❓ |
| **Categoría** | Control |

Comprobar si una expresión es verdadera

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `expression` | Texto | — | Expresión a evaluar (verdadero si >= 0.5) |
| `then_actions` | Lista de acciones | — | Acciones si verdadero |
| `else_actions` | Lista de acciones | — | Acciones si falso |

### Hacer una pregunta

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_question` |
| **Icono** | ❓💬 |
| **Categoría** | Control |

Condición: mostrar un diálogo sí/no; verdadero si el usuario responde sí

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `question` | Texto | `Continue?` | Pregunta mostrada al jugador |

### Comprobar variable

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_variable` |
| **Icono** | ❓ |
| **Categoría** | Control |

Comprobar el valor de una variable de instancia o global

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `variable` | Texto | — | Nombre de la variable |
| `value` | Texto | `0` | Valor a comparar |
| `scope` | Elección | `self` | Ámbito de la variable; Opciones: `self`, `other`, `global` |
| `operation` | Elección | `equal` | Operador de comparación; Opciones: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="grid"></a>
## Cuadrícula

### Si en la cuadrícula

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_on_grid` |
| **Icono** | ▦ |
| **Categoría** | Cuadrícula |

Comprobar si el objeto está alineado a la cuadrícula

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `grid_size` | Número | `32` | Tamaño de la celda de la cuadrícula en píxeles |
| `then_actions` | Lista de acciones | — | Acciones si en la cuadrícula |
| `else_actions` | Lista de acciones | — | Acciones si no en la cuadrícula |

### Ajustar a la cuadrícula

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `snap_to_grid` |
| **Icono** | ▦ |
| **Categoría** | Cuadrícula |

Alinear la posición de la instancia a la cuadrícula

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `grid_size` | Número | `32` | Tamaño de la celda de la cuadrícula en píxeles |

### Detener si no hay teclas pulsadas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stop_if_no_keys` |
| **Icono** | ▦ |
| **Categoría** | Cuadrícula |

Detener el movimiento en la cuadrícula cuando no se pulsa ninguna tecla de movimiento (perfecto para un ajuste suave a la cuadrícula)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `grid_size` | Número | `32` | Tamaño de la celda de la cuadrícula en píxeles |

### Comprobar alineación a la cuadrícula

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_alignment` |
| **Icono** | ❓▦ |
| **Categoría** | Cuadrícula |

Condición: verdadero si la instancia está alineada a una cuadrícula

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `hsnap` | Número | `32` | Espaciado horizontal de la cuadrícula en píxeles |
| `vsnap` | Número | `32` | Espaciado vertical de la cuadrícula en píxeles |

---

<a id="views"></a>
## Vistas

### Habilitar vistas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `enable_views` |
| **Icono** | 🎥 |
| **Categoría** | Vistas |

Activar o desactivar el sistema de cámara/vista de la sala (permite que un nivel se desplace cuando es más grande que la ventana)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `enable` | Sí/No | Sí | Activado = vistas de cámara; desactivado = dibujar toda la sala de una vez |

### Configurar vista

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_view` |
| **Icono** | 🎥 |
| **Categoría** | Vistas |

Configurar una vista de cámara: qué parte de la sala muestra, dónde se dibuja en pantalla y un objeto a seguir

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `view` | Elección | `0` | Cuál de las 8 vistas configurar; Opciones: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` |
| `visible` | Sí/No | Sí | Dibujar esta vista |
| `view_x` | Número | `0` | Borde izquierdo de la región de la sala mostrada |
| `view_y` | Número | `0` | Borde superior de la región de la sala mostrada |
| `view_w` | Número | `800` | Ancho de la región de la sala mostrada |
| `view_h` | Número | `600` | Alto de la región de la sala mostrada |
| `port_x` | Número | `0` | Borde izquierdo en pantalla |
| `port_y` | Número | `0` | Borde superior en pantalla |
| `port_w` | Número | `800` | Ancho dibujado en pantalla |
| `port_h` | Número | `600` | Alto dibujado en pantalla |
| `follow` | Objeto | — | Objeto que sigue la cámara (vacío = vista fija); opcional |
| `hborder` | Número | `32` | Borde horizontal antes de que la cámara se desplace |
| `vborder` | Número | `32` | Borde vertical antes de que la cámara se desplace |
| `hspeed` | Número | `-1` | Velocidad máxima de desplazamiento horizontal (-1 = instantáneo) |
| `vspeed` | Número | `-1` | Velocidad máxima de desplazamiento vertical (-1 = instantáneo) |

---

<a id="3d-view"></a>
## Vista 3D

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

## Véase también

- [Referencia de eventos](Event-Reference_es) — los eventos que activan las acciones
- [Guía de preajustes](Preset-Guide_es) — qué acciones expone cada preajuste/edición
- [Vista 3D](3D-View_es) — las acciones de vista en primera persona (raycast)
- [Extensiones](Extensions_es) — cómo se proporcionan las acciones de la Vista 3D
