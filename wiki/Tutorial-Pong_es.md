# Tutorial: Crear un Juego Pong Clásico

> **Selecciona tu idioma / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Pong) | [Français](Tutorial-Pong_fr) | [Deutsch](Tutorial-Pong_de) | [Italiano](Tutorial-Pong_it) | [Español](Tutorial-Pong_es) | [Português](Tutorial-Pong_pt) | [Slovenščina](Tutorial-Pong_sl) | [Українська](Tutorial-Pong_uk) | [Русский](Tutorial-Pong_ru)

---

## Introducción

En este tutorial, crearás un juego clásico **Pong** - ¡uno de los primeros videojuegos jamás creados! Pong es un juego para dos jugadores donde cada jugador controla una paleta e intenta golpear la pelota pasando la paleta de su oponente para anotar puntos.

**Lo que aprenderás:**
- Crear sprites para paletas, pelota y paredes
- Manejar entrada de teclado para dos jugadores
- Hacer que los objetos reboten entre sí
- Rastrear y mostrar puntuaciones de ambos jugadores
- Usar variables globales

**Dificultad:** Principiante
**Preset:** Preset para Principiantes

---

## Paso 1: Planifica Tu Juego

Antes de comenzar, entendamos lo que necesitamos:

| Elemento | Propósito |
|---------|---------|
| **Pelota** | Rebota entre jugadores |
| **Paleta Izquierda** | Jugador 1 controla con teclas W/S |
| **Paleta Derecha** | Jugador 2 controla con flechas Arriba/Abajo |
| **Paredes** | Límites superior e inferior |
| **Zonas de Gol** | Áreas invisibles detrás de cada paleta para detectar puntuaciones |
| **Marcador** | Muestra las puntuaciones de ambos jugadores |

---

## Paso 2: Crea los Sprites

### 2.1 Sprite de la Pelota

1. En el **Árbol de Recursos**, haz clic derecho en **Sprites** y selecciona **Crear Sprite**
2. Nómbralo `spr_ball`
3. Haz clic en **Editar Sprite** para abrir el editor de sprites
4. Dibuja un pequeño círculo blanco (aproximadamente 16x16 píxeles)
5. Haz clic en **Aceptar** para guardar

### 2.2 Sprites de las Paletas

Crearemos dos paletas, una para cada jugador:

**Paleta Izquierda (Jugador 1):**
1. Crea un nuevo sprite nombrado `spr_paddle_left`
2. Dibuja un rectángulo alto y delgado curvado como un paréntesis ")" - se recomienda color azul
3. Tamaño: aproximadamente 16x64 píxeles

**Paleta Derecha (Jugador 2):**
1. Crea un nuevo sprite nombrado `spr_paddle_right`
2. Dibuja un rectángulo alto y delgado curvado como un paréntesis "(" - se recomienda color rojo
3. Tamaño: aproximadamente 16x64 píxeles

### 2.3 Sprite de Pared

1. Crea un nuevo sprite nombrado `spr_wall`
2. Dibuja un rectángulo sólido (gris o blanco)
3. Tamaño: 32x32 píxeles (lo estiraremos en la sala)

### 2.4 Sprite de Zona de Gol (Invisible)

1. Crea un nuevo sprite nombrado `spr_goal`
2. Hazlo de 32x32 píxeles
3. Déjalo transparente o hazlo de un color sólido (será invisible en el juego)

---

## Paso 3: Crea el Objeto Pared

El objeto pared crea límites en la parte superior e inferior del área de juego.

1. Haz clic derecho en **Objetos** y selecciona **Crear Objeto**
2. Nómbralo `obj_wall`
3. Establece el sprite en `spr_wall`
4. **Marca la casilla "Sólido"** - ¡esto es importante para el rebote!
5. No se necesitan eventos - la pared solo está ahí

---

## Paso 4: Crea los Objetos Paleta

### 4.1 Paleta Izquierda (Jugador 1)

1. Crea un nuevo objeto nombrado `obj_paddle_left`
2. Establece el sprite en `spr_paddle_left`
3. **Marca la casilla "Sólido"**

**Agrega Eventos de Teclado para Movimiento:**

**Evento: Presionar Tecla W**
1. Agregar Evento → Teclado → Presionar W
2. Agregar Acción: **Movimiento** → **Establecer Velocidad Vertical**
3. Establece la velocidad vertical en `-8` (se mueve hacia arriba)

**Evento: Soltar Tecla W**
1. Agregar Evento → Teclado → Soltar W
2. Agregar Acción: **Movimiento** → **Establecer Velocidad Vertical**
3. Establece la velocidad vertical en `0` (deja de moverse)

**Evento: Presionar Tecla S**
1. Agregar Evento → Teclado → Presionar S
2. Agregar Acción: **Movimiento** → **Establecer Velocidad Vertical**
3. Establece la velocidad vertical en `8` (se mueve hacia abajo)

**Evento: Soltar Tecla S**
1. Agregar Evento → Teclado → Soltar S
2. Agregar Acción: **Movimiento** → **Establecer Velocidad Vertical**
3. Establece la velocidad vertical en `0` (deja de moverse)

**Evento: Colisión con obj_wall**
1. Agregar Evento → Colisión → obj_wall
2. Agregar Acción: **Movimiento** → **Rebotar Contra Objetos**
3. Selecciona "Contra objetos sólidos"

### 4.2 Paleta Derecha (Jugador 2)

1. Crea un nuevo objeto nombrado `obj_paddle_right`
2. Establece el sprite en `spr_paddle_right`
3. **Marca la casilla "Sólido"**

**Agrega Eventos de Teclado para Movimiento:**

**Evento: Presionar Flecha Arriba**
1. Agregar Evento → Teclado → Presionar Arriba
2. Agregar Acción: **Movimiento** → **Establecer Velocidad Vertical**
3. Establece la velocidad vertical en `-8`

**Evento: Soltar Flecha Arriba**
1. Agregar Evento → Teclado → Soltar Arriba
2. Agregar Acción: **Movimiento** → **Establecer Velocidad Vertical**
3. Establece la velocidad vertical en `0`

**Evento: Presionar Flecha Abajo**
1. Agregar Evento → Teclado → Presionar Abajo
2. Agregar Acción: **Movimiento** → **Establecer Velocidad Vertical**
3. Establece la velocidad vertical en `8`

**Evento: Soltar Flecha Abajo**
1. Agregar Evento → Teclado → Soltar Abajo
2. Agregar Acción: **Movimiento** → **Establecer Velocidad Vertical**
3. Establece la velocidad vertical en `0`

**Evento: Colisión con obj_wall**
1. Agregar Evento → Colisión → obj_wall
2. Agregar Acción: **Movimiento** → **Rebotar Contra Objetos**
3. Selecciona "Contra objetos sólidos"

---

## Paso 5: Crea el Objeto Pelota

1. Crea un nuevo objeto nombrado `obj_ball`
2. Establece el sprite en `spr_ball`

**Evento: Crear**
1. Agregar Evento → Crear
2. Agregar Acción: **Movimiento** → **Comenzar a Moverse en Dirección**
3. Elige una dirección diagonal (no recta hacia arriba o abajo)
4. Establece la velocidad en `6`

**Evento: Colisión con obj_paddle_left**
1. Agregar Evento → Colisión → obj_paddle_left
2. Agregar Acción: **Movimiento** → **Rebotar Contra Objetos**
3. Selecciona "Contra objetos sólidos"

**Evento: Colisión con obj_paddle_right**
1. Agregar Evento → Colisión → obj_paddle_right
2. Agregar Acción: **Movimiento** → **Rebotar Contra Objetos**
3. Selecciona "Contra objetos sólidos"

**Evento: Colisión con obj_wall**
1. Agregar Evento → Colisión → obj_wall
2. Agregar Acción: **Movimiento** → **Rebotar Contra Objetos**
3. Selecciona "Contra objetos sólidos"

---

## Paso 6: Crea los Objetos de Zona de Gol

Las zonas de gol son áreas invisibles detrás de cada paleta. Cuando la pelota entra en una zona de gol, el jugador opuesto anota.

### 6.1 Zona de Gol Izquierda

1. Crea un nuevo objeto nombrado `obj_goal_left`
2. Establece el sprite en `spr_goal`
3. **Desmarca "Visible"** - la zona de gol debe ser invisible
4. **Marca "Sólido"**

### 6.2 Zona de Gol Derecha

1. Crea un nuevo objeto nombrado `obj_goal_right`
2. Establece el sprite en `spr_goal`
3. **Desmarca "Visible"**
4. **Marca "Sólido"**

### 6.3 Agrega Eventos de Colisión de Zona de Gol a la Pelota

Vuelve a `obj_ball` y agrega estos eventos:

**Evento: Colisión con obj_goal_left**
1. Agregar Evento → Colisión → obj_goal_left
2. Agregar Acción: **Movimiento** → **Saltar a Posición de Inicio** (reinicia la pelota)
3. Agregar Acción: **Puntuación** → **Establecer Puntuación**
   - Variable: `global.p2score`
   - Valor: `1`
   - Marca "Relativo" (suma 1 a la puntuación actual)

**Evento: Colisión con obj_goal_right**
1. Agregar Evento → Colisión → obj_goal_right
2. Agregar Acción: **Movimiento** → **Saltar a Posición de Inicio**
3. Agregar Acción: **Puntuación** → **Establecer Puntuación**
   - Variable: `global.p1score`
   - Valor: `1`
   - Marca "Relativo"

---

## Paso 7: Crea el Objeto Marcador

1. Crea un nuevo objeto nombrado `obj_score`
2. No se necesita sprite

**Evento: Crear**
1. Agregar Evento → Crear
2. Agregar Acción: **Puntuación** → **Establecer Puntuación**
   - Variable: `global.p1score`
   - Valor: `0`
3. Agregar Acción: **Puntuación** → **Establecer Puntuación**
   - Variable: `global.p2score`
   - Valor: `0`

**Evento: Dibujar**
1. Agregar Evento → Dibujar
2. Agregar Acción: **Dibujo** → **Dibujar Texto**
   - Texto: `Jugador 1:`
   - X: `10`
   - Y: `10`
3. Agregar Acción: **Dibujo** → **Dibujar Variable**
   - Variable: `global.p1score`
   - X: `100`
   - Y: `10`
4. Agregar Acción: **Dibujo** → **Dibujar Texto**
   - Texto: `Jugador 2:`
   - X: `10`
   - Y: `30`
5. Agregar Acción: **Dibujo** → **Dibujar Variable**
   - Variable: `global.p2score`
   - X: `100`
   - Y: `30`

---

## Paso 8: Diseña la Sala

1. Haz clic derecho en **Salas** y selecciona **Crear Sala**
2. Nómbrala `room_pong`
3. Establece el tamaño de la sala (por ejemplo, 640x480)

**Coloca los objetos:**

1. **Paredes**: Coloca instancias de `obj_wall` a lo largo de los bordes superior e inferior de la sala
2. **Paleta Izquierda**: Coloca `obj_paddle_left` cerca del borde izquierdo, centrada verticalmente
3. **Paleta Derecha**: Coloca `obj_paddle_right` cerca del borde derecho, centrada verticalmente
4. **Pelota**: Coloca `obj_ball` en el centro de la sala
5. **Zonas de Gol**:
   - Coloca instancias de `obj_goal_left` a lo largo del borde izquierdo (detrás de donde está la paleta)
   - Coloca instancias de `obj_goal_right` a lo largo del borde derecho
6. **Marcador**: Coloca `obj_score` en cualquier lugar (no tiene sprite, solo dibuja texto)

**Ejemplo de Diseño de Sala:**
```
[PARED PARED PARED PARED PARED PARED PARED PARED PARED PARED]
[GOL]  [PALETA_I]            [PELOTA]            [PALETA_D]  [GOL]
[GOL]  [PALETA_I]                              [PALETA_D]  [GOL]
[GOL]                                                      [GOL]
[PARED PARED PARED PARED PARED PARED PARED PARED PARED PARED]
```

---

## Paso 9: ¡Prueba Tu Juego!

1. Haz clic en **Ejecutar** o presiona **F5** para probar tu juego
2. Jugador 1 usa **W** (arriba) y **S** (abajo)
3. Jugador 2 usa **Flecha Arriba** y **Flecha Abajo**
4. ¡Intenta golpear la pelota pasando la paleta de tu oponente!

---

## Mejoras (Opcional)

### Aumento de Velocidad
Haz que la pelota sea más rápida cada vez que golpea una paleta añadiendo a los eventos de colisión:
- Después de la acción de rebote, agrega **Movimiento** → **Establecer Velocidad**
- Establece la velocidad en `speed + 0.5` con "Relativo" marcado

### Efectos de Sonido
Agrega sonidos cuando:
- La pelota golpea una paleta
- La pelota golpea una pared
- Un jugador anota

### Condición de Victoria
Agrega una verificación en el evento Dibujar:
- Si `global.p1score >= 10`, muestra "¡Jugador 1 Gana!"
- Si `global.p2score >= 10`, muestra "¡Jugador 2 Gana!"

---

## Solución de Problemas

| Problema | Solución |
|---------|----------|
| La pelota pasa a través de la paleta | Asegúrate de que las paletas tengan "Sólido" marcado |
| La paleta no se detiene en las paredes | Agrega evento de colisión con obj_wall |
| La puntuación no se actualiza | Verifica que los nombres de las variables coincidan exactamente (global.p1score, global.p2score) |
| La pelota no se mueve | Verifica que el evento Crear tenga la acción de movimiento |

---

## Lo Que Aprendiste

¡Felicidades! ¡Has creado un juego Pong completo para dos jugadores! Aprendiste:

- Cómo manejar entrada de teclado para dos jugadores diferentes
- Cómo usar eventos de Soltar Tecla para detener el movimiento
- Cómo hacer que los objetos reboten entre sí
- Cómo usar variables globales para rastrear puntuaciones
- Cómo mostrar texto y variables en la pantalla

---

## Ver También

- [Preset para Principiantes](Beginner-Preset_es) - Descripción general de características para principiantes
- [Tutorial: Breakout](Tutorial-Breakout_es) - Crear un juego de rompecabezas de ladrillos
- [Referencia de Eventos](Event-Reference_es) - Documentación completa de eventos
- [Referencia Completa de Acciones](Full-Action-Reference_es) - Todas las acciones disponibles
