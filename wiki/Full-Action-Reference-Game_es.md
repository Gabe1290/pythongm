# Juego

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

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

### Load Game

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `load_game` |
| **Icono** | 📂 |
| **Categoría** | Juego |

Restore room, score/lives/health, global variables, and instance states from a save file

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `filename` | Texto | `savegame.sav` | Save file name to load (from the project's saves/ folder) |

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

### Save Game

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `save_game` |
| **Icono** | 💾 |
| **Categoría** | Juego |

Save the current room, score/lives/health, global variables, and instance states to a file

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `filename` | Texto | `savegame.sav` | Save file name (written to the project's saves/ folder) |

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

### Show Video

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `show_video` |
| **Icono** | 🎬 |
| **Categoría** | Juego |

Play a video file in your system's default video player -- opens as a separate window, not rendered inside the game itself

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `filename` | Texto | — | Path to the video file |
| `fullscreen` | Sí/No | No | Request fullscreen playback (support depends on your system's player); opcional |

### Splash: Show Image

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `splash_show_image` |
| **Icono** | 🖼️ |
| **Categoría** | Juego |

Show a sprite full-screen and pause the game until the player dismisses it

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `image` | Sprite | — | Sprite to display full-screen |

### Splash: Show Text

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `splash_show_text` |
| **Icono** | 💬 |
| **Categoría** | Juego |

Show a message and pause the game until the player dismisses it

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `text` | Texto | — | Message to display |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (8)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (16)
- [Particles](Full-Action-Reference-Particles_es) (8)
- [Réseau](Full-Action-Reference-Network-Actions_es) (15)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
