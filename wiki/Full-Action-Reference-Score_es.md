# Puntuación

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

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

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (21)
- [Instancia](Full-Action-Reference-Instance_es) (12)
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
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_es) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_es) (16)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
