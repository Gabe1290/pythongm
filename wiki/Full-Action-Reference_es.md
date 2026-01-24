# Referencia Completa de Acciones

*[Inicio](Home_es) | [Guía de Presets](Preset-Guide_es) | [Referencia de Eventos](Event-Reference_es)*

Esta página documenta todas las acciones disponibles en PyGameMaker. Las acciones son comandos que se ejecutan cuando se activan los eventos.

## Categorías de Acciones

- [Acciones de Movimiento](#acciones-de-movimiento)
- [Acciones de Instancia](#acciones-de-instancia)
- [Acciones de Puntuación, Vidas y Salud](#acciones-de-puntuación-vidas-y-salud)
- [Acciones de Sala](#acciones-de-sala)
- [Acciones de Temporización](#acciones-de-temporización)
- [Acciones de Sonido](#acciones-de-sonido)
- [Acciones de Dibujo](#acciones-de-dibujo)
- [Acciones de Control de Flujo](#acciones-de-control-de-flujo)
- [Acciones de Salida](#acciones-de-salida)

---

## Acciones de Movimiento

### Establecer Velocidad Horizontal
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `set_hspeed` |
| **Icono** | ↔️ |
| **Preset** | Principiante |

**Descripción:** Establece la velocidad de movimiento horizontal.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `value` | Número | 0 | Velocidad en píxeles/frame. Positivo=derecha, Negativo=izquierda |

---

### Establecer Velocidad Vertical
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `set_vspeed` |
| **Icono** | ↕️ |
| **Preset** | Principiante |

**Descripción:** Establece la velocidad de movimiento vertical.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `value` | Número | 0 | Velocidad en píxeles/frame. Positivo=abajo, Negativo=arriba |

---

### Detener Movimiento
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `stop_movement` |
| **Icono** | 🛑 |
| **Preset** | Principiante |

**Descripción:** Detiene todo el movimiento (establece hspeed y vspeed a 0).

**Parámetros:** Ninguno

---

### Saltar a Posición
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `jump_to_position` |
| **Icono** | 📍 |
| **Preset** | Principiante |

**Descripción:** Se mueve instantáneamente a una posición específica.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `x` | Número | 0 | Coordenada X destino |
| `y` | Número | 0 | Coordenada Y destino |

---

### Movimiento Fijo
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `move_fixed` |
| **Icono** | ➡️ |
| **Preset** | Avanzado |

**Descripción:** Se mueve en una de las 8 direcciones fijas.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `directions` | Opción | right | Dirección(es) de movimiento |
| `speed` | Número | 4 | Velocidad de movimiento |

**Opciones de dirección:** left, right, up, down, up-left, up-right, down-left, down-right, stop

---

### Movimiento Libre
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `move_free` |
| **Icono** | 🧭 |
| **Preset** | Avanzado |

**Descripción:** Se mueve en cualquier dirección (0-360 grados).

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `direction` | Número | 0 | Dirección en grados (0=derecha, 90=arriba) |
| `speed` | Número | 4 | Velocidad de movimiento |

---

### Mover Hacia
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `move_towards` |
| **Icono** | 🎯 |
| **Preset** | Intermedio |

**Descripción:** Se mueve hacia una posición objetivo.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `x` | Expresión | 0 | X objetivo (puede usar expresiones como `other.x`) |
| `y` | Expresión | 0 | Y objetivo |
| `speed` | Número | 4 | Velocidad de movimiento |

---

### Establecer Velocidad
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `set_speed` |
| **Icono** | ⚡ |
| **Preset** | Avanzado |

**Descripción:** Establece la magnitud de la velocidad (mantiene la dirección).

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `speed` | Número | 0 | Magnitud de la velocidad |

---

### Establecer Dirección
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `set_direction` |
| **Icono** | 🧭 |
| **Preset** | Avanzado |

**Descripción:** Establece la dirección del movimiento (mantiene la velocidad).

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `direction` | Número | 0 | Dirección en grados |

---

### Invertir Horizontal
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `reverse_horizontal` |
| **Icono** | ↔️ |
| **Preset** | Avanzado |

**Descripción:** Invierte la dirección horizontal (multiplica hspeed por -1).

**Parámetros:** Ninguno

---

### Invertir Vertical
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `reverse_vertical` |
| **Icono** | ↕️ |
| **Preset** | Avanzado |

**Descripción:** Invierte la dirección vertical (multiplica vspeed por -1).

**Parámetros:** Ninguno

---

### Establecer Gravedad
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `set_gravity` |
| **Icono** | ⬇️ |
| **Preset** | Platformer |

**Descripción:** Aplica gravedad a la instancia.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `direction` | Número | 270 | Dirección de la gravedad (270=abajo) |
| `gravity` | Número | 0.5 | Fuerza de la gravedad |

---

### Establecer Fricción
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `set_friction` |
| **Icono** | 🛑 |
| **Preset** | Avanzado |

**Descripción:** Aplica fricción (desaceleración gradual).

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `friction` | Número | 0.1 | Cantidad de fricción |

---

## Acciones de Instancia

### Destruir Instancia
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `destroy_instance` |
| **Icono** | 💥 |
| **Preset** | Principiante |

**Descripción:** Elimina una instancia del juego.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `target` | Opción | self | `self` u `other` (en eventos de colisión) |

---

### Crear Instancia
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `create_instance` |
| **Icono** | ✨ |
| **Preset** | Principiante |

**Descripción:** Crea una nueva instancia de un objeto.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `object` | Objeto | - | Tipo de objeto a crear |
| `x` | Número | 0 | Posición X |
| `y` | Número | 0 | Posición Y |

---

### Establecer Sprite
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `set_sprite` |
| **Icono** | 🖼️ |
| **Preset** | Avanzado |

**Descripción:** Cambia el sprite de la instancia.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `sprite` | Sprite | - | Nuevo sprite |

---

## Acciones de Puntuación, Vidas y Salud

### Establecer Puntuación
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `set_score` |
| **Icono** | 🏆 |
| **Preset** | Principiante |

**Descripción:** Establece o modifica la puntuación.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `value` | Número | 0 | Valor de puntuación |
| `relative` | Booleano | false | Si es verdadero, suma a la puntuación actual |

---

### Añadir Puntuación (Atajo)
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `add_score` |
| **Icono** | ➕🏆 |
| **Preset** | Principiante |

**Descripción:** Añade puntos a la puntuación.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `value` | Número | 10 | Puntos a añadir (negativo para restar) |

---

### Establecer Vidas
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `set_lives` |
| **Icono** | ❤️ |
| **Preset** | Intermedio |

**Descripción:** Establece o modifica el conteo de vidas.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `value` | Número | 3 | Valor de vidas |
| `relative` | Booleano | false | Si es verdadero, suma a las vidas actuales |

**Nota:** Activa el evento `no_more_lives` cuando llega a 0.

---

### Añadir Vidas (Atajo)
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `add_lives` |
| **Icono** | ➕❤️ |
| **Preset** | Intermedio |

**Descripción:** Añade o quita vidas.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `value` | Número | 1 | Vidas a añadir (negativo para restar) |

---

### Establecer Salud
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `set_health` |
| **Icono** | 💚 |
| **Preset** | Intermedio |

**Descripción:** Establece o modifica la salud (0-100).

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `value` | Número | 100 | Valor de salud |
| `relative` | Booleano | false | Si es verdadero, suma a la salud actual |

**Nota:** Activa el evento `no_more_health` cuando llega a 0.

---

### Añadir Salud (Atajo)
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `add_health` |
| **Icono** | ➕💚 |
| **Preset** | Intermedio |

**Descripción:** Añade o quita salud.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `value` | Número | 10 | Salud a añadir (negativo para daño) |

---

### Dibujar Puntuación
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `draw_score` |
| **Icono** | 🖼️🏆 |
| **Preset** | Principiante |

**Descripción:** Muestra la puntuación en pantalla.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `x` | Número | 10 | Posición X |
| `y` | Número | 10 | Posición Y |
| `caption` | Cadena | "Score: " | Texto antes de la puntuación |

---

### Dibujar Vidas
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `draw_lives` |
| **Icono** | 🖼️❤️ |
| **Preset** | Intermedio |

**Descripción:** Muestra las vidas en pantalla.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `x` | Número | 10 | Posición X |
| `y` | Número | 30 | Posición Y |
| `sprite` | Sprite | - | Sprite de icono de vida opcional |

---

### Dibujar Barra de Salud
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `draw_health_bar` |
| **Icono** | 📊💚 |
| **Preset** | Intermedio |

**Descripción:** Dibuja una barra de salud.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `x1` | Número | 10 | X izquierda |
| `y1` | Número | 50 | Y superior |
| `x2` | Número | 110 | X derecha |
| `y2` | Número | 60 | Y inferior |
| `back_color` | Color | gray | Color de fondo |
| `bar_color` | Color | green | Color de la barra |

---

## Acciones de Sala

### Siguiente Sala
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `next_room` |
| **Icono** | ➡️ |
| **Preset** | Principiante |

**Descripción:** Ir a la siguiente sala en el orden de salas.

**Parámetros:** Ninguno

---

### Sala Anterior
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `previous_room` |
| **Icono** | ⬅️ |
| **Preset** | Principiante |

**Descripción:** Ir a la sala anterior en el orden de salas.

**Parámetros:** Ninguno

---

### Reiniciar Sala
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `restart_room` |
| **Icono** | 🔄 |
| **Preset** | Principiante |

**Descripción:** Reinicia la sala actual.

**Parámetros:** Ninguno

---

### Ir a Sala
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `goto_room` |
| **Icono** | 🚪 |
| **Preset** | Principiante |

**Descripción:** Ir a una sala específica.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `room` | Sala | - | Sala destino |

---

### Si Existe Siguiente Sala
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `if_next_room_exists` |
| **Icono** | ❓➡️ |
| **Preset** | Principiante |

**Descripción:** Condicional - ejecuta acciones solo si existe una siguiente sala.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `then_actions` | Lista de Acciones | Acciones si existe siguiente sala |
| `else_actions` | Lista de Acciones | Acciones si no hay siguiente sala |

---

### Si Existe Sala Anterior
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `if_previous_room_exists` |
| **Icono** | ❓⬅️ |
| **Preset** | Principiante |

**Descripción:** Condicional - ejecuta acciones solo si existe una sala anterior.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `then_actions` | Lista de Acciones | Acciones si existe sala anterior |
| `else_actions` | Lista de Acciones | Acciones si no hay sala anterior |

---

## Acciones de Temporización

### Establecer Alarma
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `set_alarm` |
| **Icono** | ⏰ |
| **Preset** | Intermedio |

**Descripción:** Establece una alarma que se activa después de un retraso.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `alarm` | Número | 0 | Número de alarma (0-11) |
| `steps` | Número | 60 | Pasos hasta que se active la alarma |

**Nota:** A 60 FPS, 60 pasos = 1 segundo.

---

## Acciones de Sonido

### Reproducir Sonido
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `play_sound` |
| **Icono** | 🔊 |
| **Preset** | Intermedio |

**Descripción:** Reproduce un efecto de sonido.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `sound` | Sonido | - | Recurso de sonido |
| `loop` | Booleano | false | Repetir el sonido en bucle |

---

### Reproducir Música
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `play_music` |
| **Icono** | 🎵 |
| **Preset** | Intermedio |

**Descripción:** Reproduce música de fondo.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `sound` | Sonido | - | Recurso de música |
| `loop` | Booleano | true | Repetir la música en bucle |

---

### Detener Música
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `stop_music` |
| **Icono** | 🔇 |
| **Preset** | Intermedio |

**Descripción:** Detiene toda la música en reproducción.

**Parámetros:** Ninguno

---

### Establecer Volumen
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `set_volume` |
| **Icono** | 🔉 |
| **Preset** | Avanzado |

**Descripción:** Establece el volumen de audio.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `volume` | Número | 1.0 | Nivel de volumen (0.0 a 1.0) |

---

## Acciones de Dibujo

### Dibujar Texto
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `draw_text` |
| **Icono** | 📝 |
| **Preset** | Avanzado |

**Descripción:** Dibuja texto en pantalla.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `x` | Número | 0 | Posición X |
| `y` | Número | 0 | Posición Y |
| `text` | Cadena | "" | Texto a dibujar |
| `color` | Color | white | Color del texto |

---

### Dibujar Rectángulo
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `draw_rectangle` |
| **Icono** | ⬛ |
| **Preset** | Avanzado |

**Descripción:** Dibuja un rectángulo.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `x1` | Número | 0 | X izquierda |
| `y1` | Número | 0 | Y superior |
| `x2` | Número | 32 | X derecha |
| `y2` | Número | 32 | Y inferior |
| `color` | Color | white | Color de relleno |
| `outline` | Booleano | false | Solo contorno |

---

### Dibujar Círculo
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `draw_circle` |
| **Icono** | ⚪ |
| **Preset** | Avanzado |

**Descripción:** Dibuja un círculo.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `x` | Número | 0 | Centro X |
| `y` | Número | 0 | Centro Y |
| `radius` | Número | 16 | Radio |
| `color` | Color | white | Color de relleno |
| `outline` | Booleano | false | Solo contorno |

---

### Establecer Alfa
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `set_alpha` |
| **Icono** | 👻 |
| **Preset** | Avanzado |

**Descripción:** Establece la transparencia del dibujo.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `alpha` | Número | 1.0 | Transparencia (0.0=invisible, 1.0=opaco) |

---

## Acciones de Control de Flujo

### Si Colisión En
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `if_collision_at` |
| **Icono** | 🎯 |
| **Preset** | Avanzado |

**Descripción:** Comprueba colisión en una posición.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `x` | Expresión | Posición X a comprobar |
| `y` | Expresión | Posición Y a comprobar |
| `object_type` | Opción | `any` o `solid` |
| `then_actions` | Lista de Acciones | Si se encuentra colisión |
| `else_actions` | Lista de Acciones | Si no hay colisión |

---

## Acciones de Salida

### Mostrar Mensaje
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `show_message` |
| **Icono** | 💬 |
| **Preset** | Principiante |

**Descripción:** Muestra un mensaje emergente.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `message` | Cadena | "Hello!" | Texto del mensaje |

**Nota:** El juego se pausa mientras se muestra el mensaje.

---

### Ejecutar Código
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `execute_code` |
| **Icono** | 💻 |
| **Preset** | Principiante |

**Descripción:** Ejecuta código Python personalizado.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `code` | Código | "" | Código Python a ejecutar |

**Advertencia:** Característica avanzada. Usar con precaución.

---

### Terminar Juego
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `end_game` |
| **Icono** | 🚪 |
| **Preset** | Avanzado |

**Descripción:** Termina el juego y cierra la ventana.

**Parámetros:** Ninguno

---

### Reiniciar Juego
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `restart_game` |
| **Icono** | 🔄 |
| **Preset** | Avanzado |

**Descripción:** Reinicia el juego desde la primera sala.

**Parámetros:** Ninguno

---

## Acciones por Preset

| Preset | Cantidad de Acciones | Categorías |
|--------|---------------------|------------|
| **Principiante** | 17 | Movimiento, Instancia, Puntuación, Sala, Salida |
| **Intermedio** | 29 | + Vidas, Salud, Sonido, Temporización |
| **Avanzado** | 40+ | + Dibujo, Control de Flujo, Juego |

---

## Ver También

- [Referencia de Eventos](Event-Reference_es) - Lista completa de eventos
- [Preset Principiante](Beginner-Preset_es) - Acciones esenciales para principiantes
- [Preset Intermedio](Intermediate-Preset_es) - Acciones adicionales
- [Eventos y Acciones](Events-and-Actions_es) - Visión general de conceptos básicos
