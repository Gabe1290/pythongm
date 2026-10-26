# Juego

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

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
| `color` | Color | — | Color del texto (por ej. #ffffff). Vacío = el color de dibujo activo, o negro.; opcional |

### Cargar la partida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `load_game` |
| **Icono** | 📂 |
| **Categoría** | Juego |

Restaura la sala, la puntuación, las vidas, la salud, las variables globales y el estado de las instancias desde un archivo guardado

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `filename` | Texto | `savegame.sav` | Nombre del archivo guardado que se va a cargar (de la carpeta saves/ del proyecto) |

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

### Guardar la partida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `save_game` |
| **Icono** | 💾 |
| **Categoría** | Juego |

Guarda en un archivo la sala actual, la puntuación, las vidas, la salud, las variables globales y el estado de las instancias

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `filename` | Texto | `savegame.sav` | Nombre del archivo de guardado (se escribe en la carpeta saves/ del proyecto) |

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

### Mostrar un vídeo

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `show_video` |
| **Icono** | 🎬 |
| **Categoría** | Juego |

Reproduce un archivo de vídeo en el reproductor predeterminado del sistema: se abre en una ventana aparte, no se dibuja dentro del propio juego

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `filename` | Texto | — | Ruta al archivo de vídeo |
| `fullscreen` | Sí/No | No | Pedir reproducción a pantalla completa (depende del reproductor de tu sistema); opcional |

### Pantalla: mostrar imagen

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `splash_show_image` |
| **Icono** | 🖼️ |
| **Categoría** | Juego |

Muestra un sprite a pantalla completa y pausa el juego hasta que el jugador lo cierra

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `image` | Sprite | — | Sprite que se muestra a pantalla completa |

### Pantalla: mostrar texto

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `splash_show_text` |
| **Icono** | 💬 |
| **Categoría** | Juego |

Muestra un mensaje y pausa el juego hasta que el jugador lo cierra

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `text` | Texto | — | Mensaje que se muestra |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (21)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (6)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (8)
- [Audio](Full-Action-Reference-Audio_es) (6)
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
