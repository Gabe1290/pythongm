# micro:bit

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Borrar la pantalla

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_clear_display` |
| **Icono** | ⬛ |
| **Categoría** | micro:bit |

Apagar todos los LED y descartar lo que estaba en espera

*Parámetros:* ninguno

### Si el botón está pulsado

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_if_button` |
| **Icono** | 🔘 |
| **Categoría** | micro:bit |

Verdadero mientras se mantiene pulsado el botón (A+B = los dos)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `button` | Elección | `a` | Opciones: `a`, `b`, `ab`, `logo` |

### Si hay un gesto

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_if_gesture` |
| **Icono** | 🤝 |
| **Categoría** | micro:bit |

Verdadero mientras la placa está en ese gesto o posición

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `gesture` | Elección | `shake` | Opciones: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### Si el brillo del LED

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_if_pixel` |
| **Icono** | 🔍 |
| **Categoría** | micro:bit |

Comparar el brillo de un LED (0 a 9) con un valor; por defecto, la pregunta es «¿está encendido?»

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `comparison` | Elección | `>` | Opciones: `<`, `<=`, `==`, `>=`, `>`, `!=`; opcional |
| `value` | Texto | `0` | opcional |

### Si hay inclinación

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_if_tilt` |
| **Icono** | 📐 |
| **Categoría** | micro:bit |

Comparar un eje del acelerómetro (mili-g, de -2048 a 2048) con un valor

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `axis` | Elección | `x` | Opciones: `x`, `y`, `z` |
| `comparison` | Elección | `>` | Opciones: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Texto | `300` |  |

### Tocar una melodía

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_play_melody` |
| **Icono** | 🎵 |
| **Categoría** | micro:bit |

Tocar una melodía incorporada (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, POWER_UP…) o tus propias notas como «C4:4 E G C5:8 R:4» (nota, octava, :duración; R es un silencio)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `melody` | Texto | `DADADADUM` | Built-in name, or notes separated by spaces |
| `tempo` | Texto | `120` | opcional |

### Tocar una nota

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_play_tone` |
| **Icono** | 🔔 |
| **Categoría** | micro:bit |

Emitir un pitido a una frecuencia durante un número de milisegundos. Los sonidos se ponen en cola

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `frequency` | Texto | `440` | Pitch in hertz (440 = the note A) |
| `duration` | Texto | `500` | opcional |

### Leer un sensor

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_read_sensor` |
| **Icono** | 📡 |
| **Categoría** | micro:bit |

Leer un sensor de la micro:bit en una variable de este objeto (o en una variable global si el nombre empieza por «global.»)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sensor` | Elección | `accelerometer x` | Opciones: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Texto | `sensor_value` | Variable that receives the reading |

### Desplazar un texto

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_scroll_text` |
| **Icono** | 🔤 |
| **Categoría** | micro:bit |

Desplazar un texto por la pantalla de LED. Pon el texto entre comillas ("Hola"); si no, un guion o un signo más se lee como un cálculo. Las letras con acento se muestran como ? igual que en la placa real

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `text` | Texto | `"Hello"` | Text or expression to scroll |
| `delay` | Número | `150` | Scroll speed (MicroPython default 150); opcional |

### Enviar un mensaje por radio

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_radio_send` |
| **Icono** | 📻 |
| **Categoría** | micro:bit |

Enviar un número o un texto a las demás micro:bit del mismo grupo (no a esta). Reciben el evento «Mensaje de radio recibido», con el valor en radio_number y radio_string. Pon el texto entre comillas; se corta a 32 caracteres

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `value` | Texto | `1` | A number, an expression or quoted text |

### Brillo de la pantalla

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_set_brightness` |
| **Icono** | 🔆 |
| **Categoría** | micro:bit |

Brillo general de los LED, de 0 (apagado) a 255 (máximo)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `brightness` | Texto | `255` |  |

### Encender un LED

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_set_pixel` |
| **Icono** | 💡 |
| **Categoría** | micro:bit |

Encender un LED al instante (x e y de 0 a 4, brillo de 0 a 9)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `brightness` | Texto | `9` | opcional |

### Elegir el grupo de radio

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_radio_set_group` |
| **Icono** | 📡 |
| **Categoría** | micro:bit |

Elegir el grupo de radio (0 a 255). Solo las micro:bit del mismo grupo se oyen entre sí; cada placa empieza en el grupo 0

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `group` | Texto | `0` |  |

### Mostrar una imagen

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_show_image` |
| **Icono** | ❤️ |
| **Categoría** | micro:bit |

Mostrar una imagen en los LED: un nombre (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL…) o cinco filas de cifras de brillo como «09090:99999:99999:09990:00900». Las imágenes se ponen en cola

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `image` | Texto | `HEART` | Built-in image name, or 5 rows of 5 digits (0-9) separated by colons |
| `hold` | Número | `0` | How long it stays before the next queued item (0 = until something else is shown); opcional |

### Mostrar un número

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_show_number` |
| **Icono** | 🔢 |
| **Categoría** | micro:bit |

Mostrar un número: una cifra se queda fija, un número más largo se desplaza

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `value` | Texto | `0` | Number or expression |

### Detener el sonido

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `microbit_stop_sound` |
| **Icono** | 🔇 |
| **Categoría** | micro:bit |

Apagar el altavoz y descartar los sonidos en espera

*Parámetros:* ninguno

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
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (20)
- [Dibujo](Full-Action-Reference-Drawing_es) (11)
- [Red](Full-Action-Reference-Network-Actions_es) (22)
- [Partículas](Full-Action-Reference-Particles_es) (8)
- [Puntuación/Vidas/Salud](Full-Action-Reference-Score-Lives-Health_es) (5)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
