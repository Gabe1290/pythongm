# Preset Principiante

*[Inicio](Home_es) | [Guia de Presets](Preset-Guide_es) | [Preset Intermedio](Intermediate-Preset_es)*

El preset **Principiante** esta disenado para usuarios que son nuevos en el desarrollo de juegos. Proporciona un conjunto seleccionado de eventos y acciones esenciales que cubren los fundamentos de la creacion de juegos 2D simples sin abrumar a los principiantes con demasiadas opciones.

## Descripcion General

El preset Principiante incluye:
- **4 Tipos de Eventos** - Para responder a situaciones del juego
- **17 Tipos de Acciones** - Para controlar el comportamiento del juego
- **6 Categorias** - Eventos, Movimiento, Puntuacion/Vidas/Salud, Instancia, Sala, Salida

---

## Eventos

Los eventos son disparadores que responden a situaciones especificas en tu juego. Cuando ocurre un evento, las acciones que has definido para ese evento se ejecutaran.

### Evento Create

| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_create` |
| **Categoria** | Eventos |
| **Descripcion** | Se activa una vez cuando una instancia es creada por primera vez |

**Cuando se activa:** Inmediatamente cuando una instancia de objeto se coloca en una sala o se crea con la accion "Crear Instancia".

**Usos comunes:**
- Inicializar variables
- Establecer posicion inicial
- Establecer velocidad o direccion inicial
- Reiniciar puntuacion al inicio del juego

---

### Evento Step

| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_step` |
| **Categoria** | Eventos |
| **Descripcion** | Se activa cada fotograma (tipicamente 60 veces por segundo) |

**Cuando se activa:** Continuamente, cada fotograma del juego.

**Usos comunes:**
- Movimiento continuo
- Verificar condiciones
- Actualizar estado del juego
- Control de animacion

---

### Evento Tecla Presionada

| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_keyboard_press` |
| **Categoria** | Eventos |
| **Descripcion** | Se activa una vez cuando una tecla especifica es presionada |

**Cuando se activa:** Una vez en el momento en que se presiona una tecla (no mientras se mantiene presionada).

**Teclas soportadas:** Teclas de flecha (arriba, abajo, izquierda, derecha), Espacio, Enter, letras (A-Z), numeros (0-9)

**Usos comunes:**
- Controles de movimiento del jugador
- Saltar
- Disparar
- Navegacion de menu

---

### Evento Colision

| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_collision` |
| **Categoria** | Eventos |
| **Descripcion** | Se activa cuando esta instancia colisiona con otro objeto |

**Cuando se activa:** Cada fotograma en que dos instancias se superponen.

**Variable especial:** En un evento de colision, `other` se refiere a la instancia con la que se colisiona.

**Usos comunes:**
- Recolectar objetos (monedas, potenciadores)
- Recibir dano de enemigos
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
| **Nombre de Accion** | `set_hspeed` |
| **Nombre del Bloque** | `move_set_hspeed` |
| **Categoria** | Movimiento |
| **Icono** | ↔️ |

**Descripcion:** Establece la velocidad de movimiento horizontal de la instancia.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `value` | Numero | Velocidad en pixeles por fotograma. Positivo = derecha, Negativo = izquierda |

**Ejemplo:** Establece `value` a `4` para moverse a la derecha a 4 pixeles por fotograma, o `-4` para moverse a la izquierda.

---

### Establecer Velocidad Vertical

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `set_vspeed` |
| **Nombre del Bloque** | `move_set_vspeed` |
| **Categoria** | Movimiento |
| **Icono** | ↕️ |

**Descripcion:** Establece la velocidad de movimiento vertical de la instancia.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `value` | Numero | Velocidad en pixeles por fotograma. Positivo = abajo, Negativo = arriba |

**Ejemplo:** Establece `value` a `-4` para moverse hacia arriba a 4 pixeles por fotograma, o `4` para moverse hacia abajo.

---

### Detener Movimiento

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `stop_movement` |
| **Nombre del Bloque** | `move_stop` |
| **Categoria** | Movimiento |
| **Icono** | 🛑 |

**Descripcion:** Detiene todo el movimiento estableciendo tanto la velocidad horizontal como vertical a cero.

**Parametros:** Ninguno

**Usos comunes:**
- Detener al jugador cuando golpea una pared
- Detener a los enemigos cuando alcanzan un destino
- Pausar el movimiento temporalmente

---

### Saltar a Posicion

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `jump_to_position` |
| **Nombre del Bloque** | `move_jump_to` |
| **Categoria** | Movimiento |
| **Icono** | 📍 |

**Descripcion:** Mueve instantaneamente la instancia a una posicion especifica (sin movimiento suave).

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `x` | Numero | Coordenada X objetivo |
| `y` | Numero | Coordenada Y objetivo |

**Ejemplo:** Salta a la posicion (100, 200) para teletransportar al jugador a esa ubicacion.

---

## Acciones de Instancia

### Destruir Instancia

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `destroy_instance` |
| **Nombre del Bloque** | `instance_destroy` |
| **Categoria** | Instancia |
| **Icono** | 💥 |

**Descripcion:** Elimina una instancia del juego.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `target` | Eleccion | `self` = destruir esta instancia, `other` = destruir la instancia que colisiona |

**Usos comunes:**
- Eliminar monedas recolectadas (`target: other` en evento de colision)
- Destruir balas cuando golpean algo
- Eliminar enemigos cuando son derrotados

---

### Crear Instancia

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `create_instance` |
| **Nombre del Bloque** | `instance_create` |
| **Categoria** | Instancia |
| **Icono** | ✨ |

**Descripcion:** Crea una nueva instancia de un objeto en una posicion especificada.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `object` | Objeto | El tipo de objeto a crear |
| `x` | Numero | Coordenada X para la nueva instancia |
| `y` | Numero | Coordenada Y para la nueva instancia |

**Ejemplo:** Crear una bala en la posicion del jugador cuando se presiona Espacio.

---

## Acciones de Puntuacion

### Establecer Puntuacion

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `set_score` |
| **Nombre del Bloque** | `score_set` |
| **Categoria** | Puntuacion/Vidas/Salud |
| **Icono** | 🏆 |

**Descripcion:** Establece la puntuacion a un valor especifico, o suma/resta de la puntuacion actual.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `value` | Numero | El valor de puntuacion |
| `relative` | Booleano | Si es verdadero, suma el valor a la puntuacion actual. Si es falso, establece la puntuacion al valor |

**Ejemplos:**
- Reiniciar puntuacion: `value: 0`, `relative: false`
- Agregar 10 puntos: `value: 10`, `relative: true`
- Restar 5 puntos: `value: -5`, `relative: true`

---

### Agregar a Puntuacion

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `add_score` |
| **Nombre del Bloque** | `score_add` |
| **Categoria** | Puntuacion/Vidas/Salud |
| **Icono** | ➕🏆 |

**Descripcion:** Agrega un valor a la puntuacion actual (atajo para set_score con relative=true).

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `value` | Numero | Puntos a agregar (puede ser negativo para restar) |

---

### Dibujar Puntuacion

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `draw_score` |
| **Nombre del Bloque** | `draw_score` |
| **Categoria** | Puntuacion/Vidas/Salud |
| **Icono** | 🖼️🏆 |

**Descripcion:** Muestra la puntuacion actual en pantalla.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `x` | Numero | Posicion X para dibujar la puntuacion |
| `y` | Numero | Posicion Y para dibujar la puntuacion |
| `caption` | Cadena | Texto a mostrar antes de la puntuacion (ej: "Puntos: ") |

**Nota:** Esto debe usarse en un evento Draw (disponible en el preset Intermedio).

---

## Acciones de Sala

### Ir a la Siguiente Sala

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `next_room` |
| **Nombre del Bloque** | `room_goto_next` |
| **Categoria** | Sala |
| **Icono** | ➡️ |

**Descripcion:** Transiciona a la siguiente sala en el orden de salas.

**Parametros:** Ninguno

**Nota:** Si ya esta en la ultima sala, esta accion no tiene efecto (use "Si Existe Siguiente Sala" para verificar primero).

---

### Ir a la Sala Anterior

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `previous_room` |
| **Nombre del Bloque** | `room_goto_previous` |
| **Categoria** | Sala |
| **Icono** | ⬅️ |

**Descripcion:** Transiciona a la sala anterior en el orden de salas.

**Parametros:** Ninguno

**Nota:** Si ya esta en la primera sala, esta accion no tiene efecto.

---

### Reiniciar Sala

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `restart_room` |
| **Nombre del Bloque** | `room_restart` |
| **Categoria** | Sala |
| **Icono** | 🔄 |

**Descripcion:** Reinicia la sala actual, restableciendo todas las instancias a su estado inicial.

**Parametros:** Ninguno

**Usos comunes:**
- Reiniciar nivel despues de que el jugador muere
- Restablecer puzzle despues de fallar
- Repetir minijuego

---

### Ir a Sala

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `goto_room` |
| **Nombre del Bloque** | `room_goto` |
| **Categoria** | Sala |
| **Icono** | 🚪 |

**Descripcion:** Transiciona a una sala especifica por nombre.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `room` | Sala | La sala a la que ir |

---

### Si Existe Siguiente Sala

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `if_next_room_exists` |
| **Nombre del Bloque** | `room_if_next_exists` |
| **Categoria** | Sala |
| **Icono** | ❓➡️ |

**Descripcion:** Bloque condicional que solo ejecuta las acciones contenidas si existe una siguiente sala.

**Parametros:** Ninguno (las acciones se colocan dentro del bloque)

**Usos comunes:**
- Verificar antes de ir a la siguiente sala
- Mostrar mensaje "Has Ganado!" si no hay mas salas

---

### Si Existe Sala Anterior

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `if_previous_room_exists` |
| **Nombre del Bloque** | `room_if_previous_exists` |
| **Categoria** | Sala |
| **Icono** | ❓⬅️ |

**Descripcion:** Bloque condicional que solo ejecuta las acciones contenidas si existe una sala anterior.

**Parametros:** Ninguno (las acciones se colocan dentro del bloque)

---

## Acciones de Salida

### Mostrar Mensaje

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `show_message` |
| **Nombre del Bloque** | `output_message` |
| **Categoria** | Salida |
| **Icono** | 💬 |

**Descripcion:** Muestra un dialogo emergente de mensaje al jugador.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `message` | Cadena | El texto a mostrar |

**Nota:** El juego se pausa mientras se muestra el mensaje. El jugador debe hacer clic en OK para continuar.

**Usos comunes:**
- Instrucciones del juego
- Dialogos de historia
- Mensajes de victoria/derrota
- Informacion de depuracion

---

### Ejecutar Codigo

| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `execute_code` |
| **Nombre del Bloque** | `execute_code` |
| **Categoria** | Salida |
| **Icono** | 💻 |

**Descripcion:** Ejecuta codigo Python personalizado.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `code` | Cadena | Codigo Python a ejecutar |

**Nota:** Esta es una funcion avanzada. Use con precaucion ya que codigo incorrecto puede causar errores.

---

## Resumen de Categorias

| Categoria | Eventos | Acciones |
|-----------|---------|----------|
| **Eventos** | Create, Step, Tecla Presionada, Colision | - |
| **Movimiento** | - | Establecer Velocidad Horizontal, Establecer Velocidad Vertical, Detener Movimiento, Saltar a Posicion |
| **Instancia** | - | Destruir Instancia, Crear Instancia |
| **Puntuacion/Vidas/Salud** | - | Establecer Puntuacion, Agregar Puntuacion, Dibujar Puntuacion |
| **Sala** | - | Siguiente Sala, Sala Anterior, Reiniciar Sala, Ir a Sala, Si Existe Siguiente Sala, Si Existe Sala Anterior |
| **Salida** | - | Mostrar Mensaje, Ejecutar Codigo |

---

## Ejemplo: Juego Simple de Recoleccion de Monedas

Aqui se muestra como configurar un juego basico de recoleccion de monedas usando solo las caracteristicas del preset Principiante:

### Objeto Jugador (obj_player)

**Tecla Presionada (Flecha Izquierda):**
- Establecer Velocidad Horizontal: -4

**Tecla Presionada (Flecha Derecha):**
- Establecer Velocidad Horizontal: 4

**Tecla Presionada (Flecha Arriba):**
- Establecer Velocidad Vertical: -4

**Tecla Presionada (Flecha Abajo):**
- Establecer Velocidad Vertical: 4

**Colision con obj_coin:**
- Establecer Puntuacion: 10 (relative: true)
- Destruir Instancia: other

**Colision con obj_wall:**
- Detener Movimiento

**Colision con obj_goal:**
- Establecer Puntuacion: 100 (relative: true)
- Siguiente Sala

### Objeto Moneda (obj_coin)
No se necesitan eventos - solo un objeto recolectable.

### Objeto Pared (obj_wall)
No se necesitan eventos - solo un obstaculo solido.

### Objeto Meta (obj_goal)
No se necesitan eventos - activa la finalizacion del nivel cuando el jugador colisiona.

---

## Actualizar a Intermedio

Cuando te sientas comodo con el preset Principiante, considera actualizar a **Intermedio** para acceder a:
- Evento Draw (para renderizado personalizado)
- Evento Destroy (limpieza cuando una instancia es destruida)
- Eventos de Raton (deteccion de clics)
- Eventos de Alarma (acciones temporizadas)
- Sistemas de Vidas y Salud
- Acciones de Sonido y Musica
- Mas opciones de movimiento (direccion, mover hacia)

---

## Ver Tambien

- [Preset Intermedio](Intermediate-Preset_es) - Caracteristicas del siguiente nivel
- [Referencia Completa de Acciones](Full-Action-Reference_es) - Lista completa de acciones
- [Referencia de Eventos](Event-Reference_es) - Lista completa de eventos
- [Eventos y Acciones](Events-and-Actions_es) - Conceptos fundamentales
- [Creando Tu Primer Juego](Creating-Your-First-Game_es) - Tutorial paso a paso
