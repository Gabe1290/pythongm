# Sala

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

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

### Set Background

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_background` |
| **Icono** | 🖼️ |
| **Categoría** | Sala |

Set the current room's background image, with tiling and scrolling options

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `background` | Texto | — | Background or sprite asset name |
| `visible` | Sí/No | Sí | Show the background; opcional |
| `foreground` | Sí/No | No | Draw in front of instances instead of behind them; opcional |
| `tiled_h` | Sí/No | No | Repeat the background across the width of the room; opcional |
| `tiled_v` | Sí/No | No | Repeat the background across the height of the room; opcional |
| `hspeed` | Número | `0` | Horizontal auto-scroll speed in pixels/frame; opcional |
| `vspeed` | Número | `0` | Vertical auto-scroll speed in pixels/frame; opcional |

### Set Background Color

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_background_color` |
| **Icono** | 🎨 |
| **Categoría** | Sala |

Change the current room's background color

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `color` | Color | `#87CEEB` | Background color |
| `show_color` | Sí/No | Sí | Whether the background color is visible (off fills black instead); opcional |

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

### Set Room Persistent

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_room_persistent` |
| **Icono** | 💾 |
| **Categoría** | Sala |

Whether the current room keeps its live state (instance positions, destroyed instances, etc.) when the player leaves and later returns to it, instead of rebuilding fresh from its authored layout every revisit

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `persistent` | Sí/No | Sí | Keep this room's state across a revisit |

### Set Room Speed

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_room_speed` |
| **Icono** | ⏱️ |
| **Categoría** | Sala |

Change the game's frame rate (frames per second)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `30` | Target frames per second (1-240) |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Tiempo](Full-Action-Reference-Timing_es) (2)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (20)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (4)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
