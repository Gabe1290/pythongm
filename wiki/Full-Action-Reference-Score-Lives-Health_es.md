# Score/Lives/Health

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Borrar tabla de récords

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `clear_highscore` |
| **Icono** | 🗑️🏆 |
| **Categoría** | Score/Lives/Health |

Borrar todas las entradas de la tabla de récords

*Parámetros:* ninguno

### Mostrar tabla de récords

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `show_highscore` |
| **Icono** | 🏆 |
| **Categoría** | Score/Lives/Health |

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
| **Categoría** | Score/Lives/Health |

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
| **Categoría** | Score/Lives/Health |

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
| **Categoría** | Score/Lives/Health |

Condición: comparar la puntuación con un valor

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `value` | Número | `0` | Valor de comparación |
| `operation` | Elección | `equal` | Operador de comparación; Opciones: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (21)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (6)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (8)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (14)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (3)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (18)
- [Dibujo](Full-Action-Reference-Drawing_es) (11)
- [Red](Full-Action-Reference-Network-Actions_es) (22)
- [Partículas](Full-Action-Reference-Particles_es) (8)
- [micro:bit](Full-Action-Reference-Microbit-Actions_es) (16)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
