# Eventos y Acciones

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

> [Volver al Inicio](Home_es)

Esta es una referencia completa de todos los eventos y acciones disponibles en PyGameMaker.

---

## Referencia de Eventos

### Evento Create
**Cuándo:** Una vez, cuando se crea una instancia
**Uso:** Inicialización, establecer variables, iniciar temporizadores

### Evento Destroy
**Cuándo:** Cuando la instancia es destruida
**Uso:** Limpieza, generar efectos, otorgar puntos

### Eventos Step

| Evento | Cuándo |
|-----------|-------|
| **Step** | En cada fotograma (60 veces por segundo) |
| **Begin Step** | Antes de las comprobaciones de colisión |
| **End Step** | Después de todos los demás eventos |

### Eventos Alarm

| Evento | Cuándo |
|-----------|-------|
| **Alarm[0-11]** | Cuando el contador llega a 0 |

Usa la acción `Set Alarm` para iniciar una cuenta regresiva. Los valores de alarma están en fotogramas (60 = 1 segundo a 60 FPS).

### Eventos de Teclado

| Evento | Cuándo |
|-----------|-------|
| **Keyboard [Tecla]** | Mientras la tecla se mantiene presionada (repetido) |
| **Key Press [Tecla]** | Una vez, cuando la tecla se presiona |
| **Key Release [Tecla]** | Una vez, cuando la tecla se suelta |
| **No Key** | Cuando ninguna tecla está presionada |

Teclas disponibles: letras (A-Z), números (0-9), teclas de flecha, barra espaciadora, Enter, Mayús, Ctrl, Alt, teclas de función (F1-F12)

### Eventos de Ratón

| Evento | Cuándo |
|-----------|-------|
| **Left Button** | Clic con el botón izquierdo sobre la instancia |
| **Right Button** | Clic con el botón derecho sobre la instancia |
| **Middle Button** | Clic con el botón central sobre la instancia |
| **Left Press** | Botón izquierdo presionado (una vez) |
| **Left Release** | Botón izquierdo soltado (una vez) |
| **Mouse Enter** | El cursor entra en la instancia |
| **Mouse Leave** | El cursor sale de la instancia |
| **Global Left Button** | Clic izquierdo en cualquier lugar |
| **Global Right Button** | Clic derecho en cualquier lugar |

### Eventos de Colisión

| Evento | Cuándo |
|-----------|-------|
| **Collision with [Objeto]** | Al contacto con el objeto especificado |

Las comprobaciones de colisión ocurren entre los eventos Step y Draw.

### Otros Eventos

| Evento | Cuándo |
|-----------|-------|
| **Outside Room** | La instancia está completamente fuera de la sala |
| **Intersect Boundary** | La instancia toca el borde de la sala |
| **Game Start** | El juego se inicia (se carga la primera sala) |
| **Game End** | El juego termina |
| **Room Start** | Al entrar en una sala |
| **Room End** | Al salir de una sala |
| **No More Lives** | Las vidas llegan a 0 |
| **No More Health** | La salud llega a 0 |
| **Animation End** | La animación del sprite se completa |

### Eventos Draw

| Evento | Cuándo |
|-----------|-------|
| **Draw** | Durante la fase de renderizado |
| **Draw GUI** | Después de dibujar la sala (espacio de pantalla) |

---

## Referencia de Acciones

### Acciones de Movimiento

| Acción | Descripción | Parámetros |
|--------|-------------|------------|
| **Establecer velocidad** | Establece la velocidad de movimiento | velocidad, relativo |
| **Establecer dirección** | Establece la dirección | dirección (0-360), relativo |
| **Set Horizontal Speed** | Establece hspeed | hspeed, relativo |
| **Set Vertical Speed** | Establece vspeed | vspeed, relativo |
| **Set Gravity** | Establece la gravedad | gravity, direction |
| **Set Friction** | Establece la fricción | friction |
| **Mover hacia un punto** | Mover hacia coordenadas | x, y, velocidad |
| **Empezar a moverse (dirección)** | Muévete en una dirección | direction, velocidad |
| **Jump To Position** | Teletransportar a coordenadas | x, y, relativo |
| **Saltar a la posición inicial** | Volver a la posición de creación | - |
| **Saltar a posición aleatoria** | Teletransporte a una posición completamente aleatoria (ambos ejes; ajustable a la cuadrícula) | snap_h, snap_v |
| **Rebotar** | Rebota en objetos sólidos | precise |

### Acciones de Instancia

| Acción | Descripción | Parámetros |
|--------|-------------|------------|
| **Create Instance** | Crea un nuevo objeto | object, x, y, relativo |
| **Create Moving Instance** | Crea con velocidad | object, x, y, speed, direction |
| **Destroy Instance** | Elimina la instancia | - |
| **Change Instance** | Se transforma en otro objeto | object, perform_events |

### Acciones de Temporización

| Acción | Descripción | Parámetros |
|--------|-------------|------------|
| **Set Alarm** | Inicia una cuenta regresiva | alarm_number, steps |
| **Sleep** | Pausa la ejecución | milisegundos |

### Acciones Score/Lives/Health

| Acción | Descripción | Parámetros |
|--------|-------------|------------|
| **Set Score** | Cambia la puntuación | value, relativo |
| **Set Lives** | Cambia las vidas | value, relativo |
| **Set Health** | Cambia la salud | value, relativo |
| **Dibujar puntuación** | Muestra la puntuación | x, y, caption |
| **Dibujar vidas** | Muestra las vidas como imágenes de sprite repetidas | x, y, sprite, scale, tiled |
| **Dibujar barra de salud** | Muestra la salud como barra de dos colores | x1, y1, x2, y2, back_color, bar_color |

### Acciones de Dibujo

| Acción | Descripción | Parámetros |
|--------|-------------|------------|
| **Draw Sprite** | Dibuja un sprite | sprite, x, y, subimage |
| **Draw Text** | Muestra texto | x, y, text |
| **Draw Rectangle** | Dibuja un rectángulo | x1, y1, x2, y2, filled |
| **Draw Circle** | Dibuja un círculo | x, y, radius, filled |
| **Draw Line** | Dibuja una línea | x1, y1, x2, y2 |
| **Establecer color de dibujo** | Establece el color para los siguientes Draw Text/Draw Rectangle/etc. | color |
| **Establecer color** | Establece el tinte y la transparencia de un sprite (no el color de dibujo de arriba) | color, alpha |
| **Establecer fuente de dibujo** | Establece la fuente y alineación para el siguiente dibujo de texto | font, halign, valign |

### Acciones de Sala

| Acción | Descripción | Parámetros |
|--------|-------------|------------|
| **Next Room** | Va a la siguiente sala | transition |
| **Previous Room** | Va a la sala anterior | transition |
| **Restart Room** | Reinicia la sala | - |
| **Go to Room** | Salta a una sala específica | room, transition |
| **If Next Room Exists** | Comprueba si existe una siguiente sala | - |
| **If Previous Room Exists** | Comprueba si existe una sala anterior | - |

### Acciones Sound

| Acción | Descripción | Parámetros |
|--------|-------------|------------|
| **Play Sound** | Reproduce un efecto de sonido | sound, loop |
| **Stop Sound** | Detiene un sonido | sound |
| **Check Sound Playing** | Comprueba si un sonido se está reproduciendo | sound |
| **Play Music** | Reproduce música de fondo | music, loop |
| **Stop Music** | Detiene toda la música | - |

### Acciones Variables

| Acción | Descripción | Parámetros |
|--------|-------------|------------|
| **Establecer variable** | Asigna un valor | variable, value, relativo |
| **Comprobar variable** | Verifica un valor | variable, value, operation |
| **Dibujar variable** | Muestra una variable | x, y, variable |

### Acciones de Control de Flujo

| Acción | Descripción | Parámetros |
|--------|-------------|------------|
| **Comprobar expresión** | Verificación condicional (una expresión booleana de Python) | expression |
| **Si no** | Rama alternativa | - |
| **Start Block** | Inicia un grupo de acciones | - |
| **End Block** | Termina un grupo de acciones | - |
| **Repeat** | Repite N veces | count |
| **Exit Event** | Detiene el evento actual | - |

### Otras Acciones

| Acción | Descripción | Parámetros |
|--------|-------------|------------|
| **Show Message** | Muestra un mensaje emergente | message |
| **Restart Game** | Reinicia el juego | - |
| **End Game** | Cierra el juego | - |

---

## Variables Integradas

Estas variables están disponibles para todas las instancias:

| Variable | Descripción |
|----------|-------------|
| `x` | Posición horizontal |
| `y` | Posición vertical |
| `xstart` | Posición x inicial |
| `ystart` | Posición y inicial |
| `hspeed` | Velocidad horizontal |
| `vspeed` | Velocidad vertical |
| `speed` | Velocidad de animación del sprite (fotogramas por segundo) — **no** la velocidad de movimiento. No existe una variable integrada para la "velocidad total"; calcúlala tú mismo a partir de `hspeed`/`vspeed`, p. ej. `(hspeed**2 + vspeed**2)**0.5` |
| `direction` | Dirección de movimiento (0-360) |
| `gravity` | Gravedad |
| `gravity_direction` | Dirección de la gravedad |
| `friction` | Fricción de movimiento |
| `image_index` | Fotograma de animación actual |
| `image_speed` | Velocidad de animación |
| `image_xscale` | Escala horizontal |
| `image_yscale` | Escala vertical |
| `image_angle` | Ángulo de rotación |
| `visible` | Si se dibuja |
| `solid` | Si es sólido para colisiones |
| `depth` | Profundidad de dibujo |
| `sprite_index` | Sprite actual |
| `alarm[0-11]` | Temporizadores de alarma |

### Variables Globales

| Variable | Descripción |
|----------|-------------|
| `score` | Puntuación del juego |
| `lives` | Vidas del jugador |
| `health` | Salud del jugador (0-100) |
| `room` | Sala actual |
| `room_width` | Ancho de la sala actual |
| `room_height` | Alto de la sala actual |
| `mouse_x` | Posición X del ratón |
| `mouse_y` | Posición Y del ratón |

---

## Próximos Pasos

- [[Programacion_Visual_es]] - Usa bloques Blockly para la misma lógica
- [[Editor_Objetos_es]] - Aplica eventos y acciones a los objetos
- [[Primer_Juego_es]] - Ve los eventos en acción
