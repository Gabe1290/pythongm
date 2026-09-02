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

### Establecer fondo

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_background` |
| **Icono** | 🖼️ |
| **Categoría** | Sala |

Establecer la imagen de fondo de la sala actual, con opciones de mosaico y desplazamiento

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `background` | Texto | — | Nombre del recurso de fondo o sprite |
| `visible` | Sí/No | Sí | Mostrar el fondo; opcional |
| `foreground` | Sí/No | No | Dibujar delante de las instancias en lugar de detrás; opcional |
| `tiled_h` | Sí/No | No | Repetir el fondo a lo largo del ancho de la sala; opcional |
| `tiled_v` | Sí/No | No | Repetir el fondo a lo largo de la altura de la sala; opcional |
| `hspeed` | Número | `0` | Velocidad de desplazamiento automático horizontal en píxeles/fotograma; opcional |
| `vspeed` | Número | `0` | Velocidad de desplazamiento automático vertical en píxeles/fotograma; opcional |

### Establecer color de fondo

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_background_color` |
| **Icono** | 🎨 |
| **Categoría** | Sala |

Cambiar el color de fondo de la sala actual

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `color` | Color | `#87CEEB` | Color de fondo |
| `show_color` | Sí/No | Sí | Si el color de fondo es visible (desactivado rellena de negro); opcional |

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

### Establecer persistencia de la sala

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_room_persistent` |
| **Icono** | 💾 |
| **Categoría** | Sala |

Si la sala actual conserva su estado activo (posiciones de instancias, instancias destruidas, etc.) cuando el jugador la abandona y vuelve más tarde, en lugar de reconstruirla desde cero según su diseño original cada vez

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `persistent` | Sí/No | Sí | Mantener el estado de esta sala al volver a visitarla |

### Establecer velocidad de la sala

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_room_speed` |
| **Icono** | ⏱️ |
| **Categoría** | Sala |

Cambiar la velocidad de fotogramas del juego (fotogramas por segundo)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `30` | Fotogramas por segundo objetivo (1-240) |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Tiempo](Full-Action-Reference-Timing_es) (8)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (25)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (16)
- [Particles](Full-Action-Reference-Particles_es) (8)
- [Réseau](Full-Action-Reference-Network-Actions_es) (15)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
