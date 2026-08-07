# Tutorial: Crear un Juego Breakout

*[Home](Home_es) | [Beginner Preset](Beginner-Preset_es) | [English](Tutorial-Breakout) | [Español](Tutorial-Breakout_es)*

Este tutorial te guiará a través de la creación de un juego clásico de Breakout. ¡Es un primer proyecto perfecto para aprender PyGameMaker!

![Breakout Game Concept](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

---

## Lo que aprenderás

- Crear y usar sprites
- Configurar objetos de juego con eventos y acciones
- Controles de teclado para el movimiento del jugador
- Detección de colisiones y rebotes
- Destruir objetos en colisión
- Construir una sala de juego

---

## Paso 1: Crear los Sprites

Primero, necesitamos crear los elementos visuales para nuestro juego.

### 1.1 Crear el Sprite del Paddle
1. En el panel **Assets**, clic derecho en **Sprites** -> **Create Sprite**
2. Nómbralo `spr_paddle`
3. Dibuja un rectángulo horizontal (aproximadamente 64x16 píxeles)
4. **Importante:** Haz clic en **Center** para establecer el origen en el centro

### 1.2 Crear el Sprite de la Pelota
1. Crea otro sprite llamado `spr_ball`
2. Dibuja un círculo pequeño (aproximadamente 16x16 píxeles)
3. Haz clic en **Center** para establecer el origen

### 1.3 Crear el Sprite del Ladrillo
1. Crea un sprite llamado `spr_brick`
2. Dibuja un rectángulo (aproximadamente 48x24 píxeles)
3. Haz clic en **Center** para establecer el origen

### 1.4 Crear el Sprite de la Pared
1. Crea un sprite llamado `spr_wall`
2. Dibuja un cuadrado (aproximadamente 32x32 píxeles) - este será el límite
3. Haz clic en **Center** para establecer el origen

### 1.5 Crear un Fondo (Opcional)
1. Clic derecho en **Backgrounds** -> **Create Background**
2. Nómbralo `bg_game`
3. Dibuja o carga una imagen de fondo

---

## Paso 2: Crear el Objeto Paddle

Ahora programemos el paddle que el jugador controla.

### 2.1 Crear el Objeto
1. Clic derecho en **Objects** -> **Create Object**
2. Nómbralo `obj_paddle`
3. Establece el **Sprite** como `spr_paddle`
4. Marca la casilla **Solid**

### 2.2 Agregar Movimiento con Flecha Derecha
1. Haz clic en **Add Event** -> **Keyboard** -> selecciona **Right Arrow**
2. Agrega la acción **Set Horizontal Speed**
3. Establece **value** en `5` (o cualquier velocidad que prefieras)

### 2.3 Agregar Movimiento con Flecha Izquierda
1. Haz clic en **Add Event** -> **Keyboard** -> selecciona **Left Arrow**
2. Agrega la acción **Set Horizontal Speed**
3. Establece **value** en `-5`

### 2.4 Detenerse Cuando se Sueltan las Teclas
¡El paddle sigue moviéndose incluso después de soltar la tecla! Arreglemos eso.

1. Haz clic en **Add Event** -> **Keyboard Release** -> selecciona **Right Arrow**
2. Agrega la acción **Set Horizontal Speed**
3. Establece **value** en `0`

4. Haz clic en **Add Event** -> **Keyboard Release** -> selecciona **Left Arrow**
5. Agrega la acción **Set Horizontal Speed**
6. Establece **value** en `0`

Ahora el paddle se detiene cuando sueltas las teclas de flecha.

---

## Paso 3: Crear el Objeto Pelota

### 3.1 Crear el Objeto
1. Crea un nuevo objeto llamado `obj_ball`
2. Establece el **Sprite** como `spr_ball`
3. Marca la casilla **Solid**

### 3.2 Establecer Movimiento Inicial
1. Haz clic en **Add Event** -> **Create**
2. Agrega la acción **Start Moving (Direction)** (o **Set Horizontal/Vertical Speed**)
3. Establece una dirección diagonal con velocidad `5`
   - Por ejemplo: **hspeed** = `4`, **vspeed** = `-4`

Esto hace que la pelota comience a moverse cuando el juego inicia.

### 3.3 Rebotar en el Paddle
1. Haz clic en **Add Event** -> **Collision** -> selecciona `obj_paddle`
2. Agrega la acción **Reverse Vertical** (para rebotar)

### 3.4 Rebotar en las Paredes
1. Haz clic en **Add Event** -> **Collision** -> selecciona `obj_wall`
2. Agrega la acción **Reverse Horizontal** o **Reverse Vertical** según sea necesario
   - O usa ambas para manejar rebotes en esquinas

---

## Paso 4: Crear el Objeto Ladrillo

### 4.1 Crear el Objeto
1. Crea un nuevo objeto llamado `obj_brick`
2. Establece el **Sprite** como `spr_brick`
3. Marca la casilla **Solid**

### 4.2 Destruir en Colisión con la Pelota
1. Haz clic en **Add Event** -> **Collision** -> selecciona `obj_ball`
2. Agrega la acción **Destroy Instance** con objetivo **self**

¡Esto destruye el ladrillo cuando la pelota lo golpea!

### 4.3 Hacer Rebotar la Pelota
**Reverse Vertical** siempre se aplica a la instancia en cuyo evento se
encuentra — no tiene una opción "aplicar a other" — así que esta acción
debe ir en la pelota, no en el ladrillo:

1. Regresa a `obj_ball` y agrega:
2. **Add Event** -> **Collision** -> selecciona `obj_brick`
3. Agrega la acción **Reverse Vertical**

---

## Paso 5: Crear el Objeto Pared

### 5.1 Crear el Objeto
1. Crea un nuevo objeto llamado `obj_wall`
2. Establece el **Sprite** como `spr_wall`
3. Marca la casilla **Solid**

Eso es todo - la pared solo necesita ser sólida para que la pelota rebote.

---

## Paso 6: Crear la Sala de Juego

### 6.1 Crear la Sala
1. Clic derecho en **Rooms** -> **Create Room**
2. Nómbrala `room_game`

### 6.2 Establecer el Fondo (Opcional)
1. En la configuración de la sala, encuentra **Background**
2. Selecciona tu fondo `bg_game`
3. Marca **Stretch** si quieres que llene la sala

### 6.3 Colocar los Objetos

Ahora coloca tus objetos en la sala:

1. **Coloca el Paddle:** Pon `obj_paddle` en el centro inferior de la sala

2. **Coloca las Paredes:** Pon instancias de `obj_wall` alrededor de los bordes:
   - A lo largo de la parte superior
   - A lo largo del lado izquierdo
   - A lo largo del lado derecho
   - Deja la parte inferior abierta (¡aquí es donde la pelota puede escapar!)

3. **Coloca la Pelota:** Pon `obj_ball` en algún lugar del centro

4. **Coloca los Ladrillos:** Organiza instancias de `obj_brick` en filas en la parte superior de la sala

---

## Paso 7: ¡Prueba tu Juego!

1. Haz clic en el botón **Play** (flecha verde)
2. Usa las teclas de flecha **Izquierda** y **Derecha** para mover el paddle
3. ¡Intenta rebotar la pelota para destruir todos los ladrillos!
4. Presiona **Escape** para salir

---

## ¿Qué Sigue?

¡Tu juego básico de Breakout está completo! Aquí hay algunas mejoras para probar:

### Agregar un Sistema de Vidas
- Agrega un evento **No More Lives** para mostrar "Game Over"
- Pierde una vida cuando la pelota sale por abajo

### Agregar Puntuación
- Usa la acción **Add Score** al destruir ladrillos
- Muestra la puntuación con **Draw Score**

### Agregar Múltiples Niveles
- Crea más salas con diferentes disposiciones de ladrillos
- Usa **Next Room** cuando todos los ladrillos sean destruidos

### Agregar Efectos de Sonido
- Agrega sonidos para rebotes y destrucción de ladrillos
- Usa la acción **Play Sound**

---

## Resumen de Objetos

| Objeto | Sprite | Solid | Eventos |
|--------|--------|-------|---------|
| `obj_paddle` | `spr_paddle` | Sí | Keyboard (Left/Right), Keyboard Release |
| `obj_ball` | `spr_ball` | Sí | Create, Collision (paddle, wall, brick) |
| `obj_brick` | `spr_brick` | Sí | Collision (ball) - Destroy self |
| `obj_wall` | `spr_wall` | Sí | Ninguno necesario |

---

## Ver También

- [Beginner Preset](Beginner-Preset_es) - Eventos y acciones usadas en este tutorial
- [Event Reference](Event-Reference_es) - Todos los eventos disponibles
- [Full Action Reference](Full-Action-Reference_es) - Todas las acciones disponibles
