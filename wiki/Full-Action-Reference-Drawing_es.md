# Dibujo

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Dibujar flecha

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_arrow` |
| **Icono** | ➡️ |
| **Categoría** | Dibujo |

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
| **Categoría** | Dibujo |

Dibujar una imagen de fondo, opcionalmente en mosaico por toda la pantalla

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `background` | Texto | — | Nombre del recurso de fondo |
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `tiled` | Sí/No | No | En mosaico por toda la pantalla; opcional |

### Dibujar elipse

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_ellipse` |
| **Icono** | 🥚 |
| **Categoría** | Dibujo |

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
| **Categoría** | Dibujo |

Dibujar una línea entre dos puntos

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x1` | Número | `0` | X inicial |
| `y1` | Número | `0` | Y inicial |
| `x2` | Número | `100` | X final |
| `y2` | Número | `100` | Y final |

### Dibujar texto escalado

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_scaled_text` |
| **Icono** | 🖍️ |
| **Categoría** | Dibujo |

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
| **Categoría** | Dibujo |

Dibujar un fotograma de sprite en una posición

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite a dibujar |
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `subimage` | Número | `0` | Índice de fotograma a dibujar |

### Dibujar variable

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_variable` |
| **Icono** | 🔢 |
| **Categoría** | Dibujo |

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
| **Categoría** | Dibujo |

Rellenar toda el área de visualización con un color uniforme

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `color` | Color | `#000000` | Color RGB hexadecimal |

### Establecer color

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_color` |
| **Icono** | 🎨 |
| **Categoría** | Dibujo |

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
| **Categoría** | Dibujo |

Establecer el color usado por las siguientes acciones draw_*

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `color` | Color | `#000000` | Color RGB hexadecimal |

### Establecer fuente de dibujo

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_draw_font` |
| **Icono** | 🔤 |
| **Categoría** | Dibujo |

Establecer la fuente y la alineación para el siguiente dibujo de texto

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `font` | Texto | — | Nombre del recurso de fuente (vacío = fuente predeterminada); opcional |
| `halign` | Elección | `left` | Alineación horizontal del texto; Opciones: `left`, `center`, `right` |
| `valign` | Elección | `top` | Alineación vertical del texto; Opciones: `top`, `middle`, `bottom` |

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
- [Red](Full-Action-Reference-Network-Actions_es) (22)
- [Partículas](Full-Action-Reference-Particles_es) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_es) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_es) (16)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
