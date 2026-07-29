# Preset Principiante

*[Inicio](Home_es) | [Guia de Presets](Preset-Guide_es) | [Preset Intermedio](Intermediate-Preset_es)*

El preset **Principiante** esta diseñado para usuarios que son nuevos en el desarrollo de juegos. Proporciona un conjunto seleccionado de eventos y acciones esenciales que cubren los fundamentos de la creación de juegos 2D simples sin abrumar a los principiantes con demasiadas opciones.

## Descripción General

El preset Principiante incluye:
- **4 Tipos de Eventos** - Para responder a situaciones del juego
- **17 Tipos de Acciones** - Para controlar el comportamiento del juego
- **6 Categorías** - Eventos, Movimiento, Puntuación/Vidas/Salud, Instancia, Sala, Salida

---

## Eventos

Los eventos son disparadores que responden a situaciones específicas en tu juego. Cuando ocurre un evento, las acciones que has definido para ese evento se ejecutaran.

### Evento Create

| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_create` |
| **Categoría** | Eventos |
| **Descripción** | Se activa una vez cuando una instancia es creada por primera vez |

**Cuándo se activa:** Inmediatamente cuando una instancia de objeto se coloca en una sala o se crea con la acción "Crear Instancia".

**Usos comunes:**
- Inicializar variables
- Establecer posición inicial
- Establecer velocidad o dirección inicial
- Reiniciar puntuación al inicio del juego

---

### Evento Step

| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_step` |
| **Categoría** | Eventos |
| **Descripción** | Se activa cada fotograma (típicamente 60 veces por segundo) |

**Cuándo se activa:** Continuamente, cada fotograma del juego.

**Usos comunes:**
- Movimiento continuo
- Verificar condiciones
- Actualizar estado del juego
- Control de animación

---

### Evento Tecla Presionada

| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_keyboard_press` |
| **Categoría** | Eventos |
| **Descripción** | Se activa una vez cuando una tecla específica es presionada |

**Cuándo se activa:** Una vez en el momento en que se presiona una tecla (no mientras se mantiene presionada).

**Teclas soportadas:** Teclas de flecha (arriba, abajo, izquierda, derecha), Espacio, Enter, letras (A-Z), numeros (0-9)

**Usos comunes:**
- Controles de movimiento del jugador
- Saltar
- Disparar
- Navegación de menú

---

### Evento Colisión

| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_collision` |
| **Categoría** | Eventos |
| **Descripción** | Se activa cuando esta instancia colisiona con otro objeto |

**Cuándo se activa:** Cada fotograma en que dos instancias se superponen.

**Variable especial:** En un evento de colisión, `other` se refiere a la instancia con la que se colisiona.

**Usos comunes:**
- Recolectar objetos (monedas, potenciadores)
- Recibir daño de enemigos
- Golpear paredes u obstaculos
- Alcanzar metas o puntos de control

---

## Acciones

Las acciones son comandos que se ejecutan cuando se activa un evento. Se pueden agregar multiples acciones a un solo evento y se ejecutaran en orden.

---

## Acciones de Movimiento

### Establecer Velocidad Horizontal

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `set_hspeed` |
| **Nombre del Bloque** | `move_set_hspeed` |
| **Categoría** | Movimiento |
| **Icono** | ↔️ |

**Descripción:** Establece la velocidad de movimiento horizontal de la instancia.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `value` | Número | Velocidad en pixeles por fotograma. Positivo = derecha, Negativo = izquierda |

**Ejemplo:** Establece `value` a `4` para moverse a la derecha a 4 pixeles por fotograma, o `-4` para moverse a la izquierda.

---

### Establecer Velocidad Vertical

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `set_vspeed` |
| **Nombre del Bloque** | `move_set_vspeed` |
| **Categoría** | Movimiento |
| **Icono** | ↕️ |

**Descripción:** Establece la velocidad de movimiento vertical de la instancia.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `value` | Número | Velocidad en pixeles por fotograma. Positivo = abajo, Negativo = arriba |

**Ejemplo:** Establece `value` a `-4` para moverse hacia arriba a 4 pixeles por fotograma, o `4` para moverse hacia abajo.

---

### Detener Movimiento

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `stop_movement` |
| **Nombre del Bloque** | `move_stop` |
| **Categoría** | Movimiento |
| **Icono** | 🛑 |

**Descripción:** Detiene todo el movimiento estableciendo tanto la velocidad horizontal como vertical a cero.

**Parámetros:** Ninguno

**Usos comunes:**
- Detener al jugador cuando golpea una pared
- Detener a los enemigos cuando alcanzan un destino
- Pausar el movimiento temporalmente

---

### Saltar a Posición

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `jump_to_position` |
| **Nombre del Bloque** | `move_jump_to` |
| **Categoría** | Movimiento |
| **Icono** | 📍 |

**Descripción:** Mueve instantaneamente la instancia a una posición específica (sin movimiento suave).

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `x` | Número | Coordenada X objetivo |
| `y` | Número | Coordenada Y objetivo |

**Ejemplo:** Salta a la posición (100, 200) para teletransportar al jugador a esa ubicación.

---

## Acciones de Instancia

### Destruir Instancia

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `destroy_instance` |
| **Nombre del Bloque** | `instance_destroy` |
| **Categoría** | Instancia |
| **Icono** | 💥 |

**Descripción:** Elimina una instancia del juego.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `target` | Elección | `self` = destruir esta instancia, `other` = destruir la instancia que colisiona |

**Usos comunes:**
- Eliminar monedas recolectadas (`target: other` en evento de colisión)
- Destruir balas cuando golpean algo
- Eliminar enemigos cuando son derrotados

---

### Crear Instancia

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `create_instance` |
| **Nombre del Bloque** | `instance_create` |
| **Categoría** | Instancia |
| **Icono** | ✨ |

**Descripción:** Crea una nueva instancia de un objeto en una posición especificada.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `object` | Objeto | El tipo de objeto a crear |
| `x` | Número | Coordenada X para la nueva instancia |
| `y` | Número | Coordenada Y para la nueva instancia |

**Ejemplo:** Crear una bala en la posición del jugador cuando se presiona Espacio.

---

## Acciones de Puntuación

### Establecer Puntuación

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `set_score` |
| **Nombre del Bloque** | `score_set` |
| **Categoría** | Puntuación/Vidas/Salud |
| **Icono** | 🏆 |

**Descripción:** Establece la puntuación a un valor específico, o suma/resta de la puntuación actual.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `value` | Número | El valor de puntuación |
| `relative` | Booleano | Si es verdadero, suma el valor a la puntuación actual. Si es falso, establece la puntuación al valor |

**Ejemplos:**
- Reiniciar puntuación: `value: 0`, `relative: false`
- Agregar 10 puntos: `value: 10`, `relative: true`
- Restar 5 puntos: `value: -5`, `relative: true`

---

### Agregar a Puntuación

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `add_score` |
| **Nombre del Bloque** | `score_add` |
| **Categoría** | Puntuación/Vidas/Salud |
| **Icono** | ➕🏆 |

**Descripción:** Agrega un valor a la puntuación actual (atajo para set_score con relative=true).

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `value` | Número | Puntos a agregar (puede ser negativo para restar) |

---

### Dibujar Puntuación

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `draw_score` |
| **Nombre del Bloque** | `draw_score` |
| **Categoría** | Puntuación/Vidas/Salud |
| **Icono** | 🖼️🏆 |

**Descripción:** Muestra la puntuación actual en pantalla.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `x` | Número | Posición X para dibujar la puntuación |
| `y` | Número | Posición Y para dibujar la puntuación |
| `caption` | Cadena | Texto a mostrar antes de la puntuación (ej: "Puntos: ") |

**Nota:** Esto debe usarse en un evento Draw (disponible en el preset Intermedio).

---

## Acciones de Sala

### Ir a la Siguiente Sala

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `next_room` |
| **Nombre del Bloque** | `room_goto_next` |
| **Categoría** | Sala |
| **Icono** | ➡️ |

**Descripción:** Transiciona a la siguiente sala en el orden de salas.

**Parámetros:** Ninguno

**Nota:** Si ya esta en la ultima sala, esta acción no tiene efecto (use "Si Existe Siguiente Sala" para verificar primero).

---

### Ir a la Sala Anterior

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `previous_room` |
| **Nombre del Bloque** | `room_goto_previous` |
| **Categoría** | Sala |
| **Icono** | ⬅️ |

**Descripción:** Transiciona a la sala anterior en el orden de salas.

**Parámetros:** Ninguno

**Nota:** Si ya esta en la primera sala, esta acción no tiene efecto.

---

### Reiniciar Sala

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `restart_room` |
| **Nombre del Bloque** | `room_restart` |
| **Categoría** | Sala |
| **Icono** | 🔄 |

**Descripción:** Reinicia la sala actual, restableciendo todas las instancias a su estado inicial.

**Parámetros:** Ninguno

**Usos comunes:**
- Reiniciar nivel después de que el jugador muere
- Restablecer puzzle después de fallar
- Repetir minijuego

---

### Ir a Sala

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `goto_room` |
| **Nombre del Bloque** | `room_goto` |
| **Categoría** | Sala |
| **Icono** | 🚪 |

**Descripción:** Transiciona a una sala específica por nombre.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `room` | Sala | La sala a la que ir |

---

### Si Existe Siguiente Sala

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `if_next_room_exists` |
| **Nombre del Bloque** | `room_if_next_exists` |
| **Categoría** | Sala |
| **Icono** | ❓➡️ |

**Descripción:** Bloque condicional que solo ejecuta las acciones contenidas si existe una siguiente sala.

**Parámetros:** Ninguno (las acciones se colocan dentro del bloque)

**Usos comunes:**
- Verificar antes de ir a la siguiente sala
- Mostrar mensaje "Has Ganado!" si no hay más salas

---

### Si Existe Sala Anterior

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `if_previous_room_exists` |
| **Nombre del Bloque** | `room_if_previous_exists` |
| **Categoría** | Sala |
| **Icono** | ❓⬅️ |

**Descripción:** Bloque condicional que solo ejecuta las acciones contenidas si existe una sala anterior.

**Parámetros:** Ninguno (las acciones se colocan dentro del bloque)

---

## Acciones de Salida

### Mostrar Mensaje

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `show_message` |
| **Nombre del Bloque** | `output_message` |
| **Categoría** | Salida |
| **Icono** | 💬 |

**Descripción:** Muestra un dialogo emergente de mensaje al jugador.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `message` | Cadena | El texto a mostrar |

**Nota:** El juego se pausa mientras se muestra el mensaje. El jugador debe hacer clic en OK para continuar.

**Usos comunes:**
- Instrucciones del juego
- Dialogos de historia
- Mensajes de victoria/derrota
- Información de depuración

---

### Ejecutar Código

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `execute_code` |
| **Nombre del Bloque** | `execute_code` |
| **Categoría** | Salida |
| **Icono** | 💻 |

**Descripción:** Ejecuta código Python personalizado.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `code` | Cadena | Código Python a ejecutar |

**Nota:** Esta es una función avanzada. Use con precaución ya que código incorrecto puede causar errores.

---

## Resumen de Categorías

| Categoría | Eventos | Acciones |
|-----------|---------|----------|
| **Eventos** | Create, Step, Tecla Presionada, Colisión | - |
| **Movimiento** | - | Establecer Velocidad Horizontal, Establecer Velocidad Vertical, Detener Movimiento, Saltar a Posición |
| **Instancia** | - | Destruir Instancia, Crear Instancia |
| **Puntuación/Vidas/Salud** | - | Establecer Puntuación, Agregar Puntuación, Dibujar Puntuación |
| **Sala** | - | Siguiente Sala, Sala Anterior, Reiniciar Sala, Ir a Sala, Si Existe Siguiente Sala, Si Existe Sala Anterior |
| **Salida** | - | Mostrar Mensaje, Ejecutar Código |

---

## Ejemplo: Juego Simple de Recolección de Monedas

Aqui se muestra como configurar un juego básico de recolección de monedas usando solo las características del preset Principiante:

### Objeto Jugador (obj_player)

**Tecla Presionada (Flecha Izquierda):**
- Establecer Velocidad Horizontal: -4

**Tecla Presionada (Flecha Derecha):**
- Establecer Velocidad Horizontal: 4

**Tecla Presionada (Flecha Arriba):**
- Establecer Velocidad Vertical: -4

**Tecla Presionada (Flecha Abajo):**
- Establecer Velocidad Vertical: 4

**Colisión con obj_coin:**
- Establecer Puntuación: 10 (relative: true)
- Destruir Instancia: other

**Colisión con obj_wall:**
- Detener Movimiento

**Colisión con obj_goal:**
- Establecer Puntuación: 100 (relative: true)
- Siguiente Sala

### Objeto Moneda (obj_coin)
No se necesitan eventos - solo un objeto recolectable.

### Objeto Pared (obj_wall)
No se necesitan eventos - solo un obstaculo sólido.

### Objeto Meta (obj_goal)
No se necesitan eventos - activa la finalización del nivel cuando el jugador colisiona.

---

## Actualizar a Intermedio

Cuando te sientas comodo con el preset Principiante, considera actualizar a **Intermedio** para acceder a:
- Evento Draw (para renderizado personalizado)
- Evento Destroy (limpieza cuando una instancia es destruida)
- Eventos de Ratón (detección de clics)
- Eventos de Alarma (acciones temporizadas)
- Sistemas de Vidas y Salud
- Acciones de Sonido y Música
- Más opciones de movimiento (dirección, mover hacia)

---

## Ver Tambien

- [Tutoriales](Tutorials_es) - Todos los tutoriales en un solo lugar
- [Preset Intermedio](Intermediate-Preset_es) - Caracteristicas del siguiente nivel
- [Referencia Completa de Acciones](Full-Action-Reference_es) - Lista completa de acciones
- [Referencia de Eventos](Event-Reference_es) - Lista completa de eventos
- [Eventos y Acciones](Events-and-Actions_es) - Conceptos fundamentales
- [Creando Tu Primer Juego](Creating-Your-First-Game_es) - Tutorial paso a paso
- [Tutorial Pong](Tutorial-Pong_es) - Crea un juego Pong clasico para dos jugadores
- [Tutorial Breakout](Tutorial-Breakout_es) - Crea un juego Breakout clasico
- [Introducción a la Creación de Juegos](Getting-Started-Breakout_es) - Tutorial completo para principiantes
