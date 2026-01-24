# Tutorial: Crear un Juego Breakout

*[Home](Home_es) | [Beginner Preset](Beginner-Preset_es) | [English](Tutorial-Breakout) | [Espanol](Tutorial-Breakout_es)*

Este tutorial te guiara a traves de la creacion de un juego clasico de Breakout. Es un primer proyecto perfecto para aprender PyGameMaker!

![Breakout Game Concept](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

---

## Lo que aprenderas

- Crear y usar sprites
- Configurar objetos de juego con eventos y acciones
- Controles de teclado para el movimiento del jugador
- Deteccion de colisiones y rebotes
- Destruir objetos en colision
- Construir una sala de juego

---

## Paso 1: Crear los Sprites

Primero, necesitamos crear los elementos visuales para nuestro juego.

### 1.1 Crear el Sprite del Paddle
1. En el panel **Assets**, clic derecho en **Sprites** -> **Create Sprite**
2. Nombralo `spr_paddle`
3. Dibuja un rectangulo horizontal (aproximadamente 64x16 pixeles)
4. **Importante:** Haz clic en **Center** para establecer el origen en el centro

### 1.2 Crear el Sprite de la Pelota
1. Crea otro sprite llamado `spr_ball`
2. Dibuja un circulo pequeno (aproximadamente 16x16 pixeles)
3. Haz clic en **Center** para establecer el origen

### 1.3 Crear el Sprite del Ladrillo
1. Crea un sprite llamado `spr_brick`
2. Dibuja un rectangulo (aproximadamente 48x24 pixeles)
3. Haz clic en **Center** para establecer el origen

### 1.4 Crear el Sprite de la Pared
1. Crea un sprite llamado `spr_wall`
2. Dibuja un cuadrado (aproximadamente 32x32 pixeles) - este sera el limite
3. Haz clic en **Center** para establecer el origen

### 1.5 Crear un Fondo (Opcional)
1. Clic derecho en **Backgrounds** -> **Create Background**
2. Nombralo `bg_game`
3. Dibuja o carga una imagen de fondo

---

## Paso 2: Crear el Objeto Paddle

Ahora programemos el paddle que el jugador controla.

### 2.1 Crear el Objeto
1. Clic derecho en **Objects** -> **Create Object**
2. Nombralo `obj_paddle`
3. Establece el **Sprite** como `spr_paddle`
4. Marca la casilla **Solid**

### 2.2 Agregar Movimiento con Flecha Derecha
1. Haz clic en **Add Event** -> **Keyboard** -> selecciona **Right Arrow**
2. Agrega la accion **Set Horizontal Speed**
3. Establece **value** en `5` (o cualquier velocidad que prefieras)

### 2.3 Agregar Movimiento con Flecha Izquierda
1. Haz clic en **Add Event** -> **Keyboard** -> selecciona **Left Arrow**
2. Agrega la accion **Set Horizontal Speed**
3. Establece **value** en `-5`

### 2.4 Detenerse Cuando se Sueltan las Teclas
El paddle sigue moviendose incluso despues de soltar la tecla! Arreglemos eso.

1. Haz clic en **Add Event** -> **Keyboard Release** -> selecciona **Right Arrow**
2. Agrega la accion **Set Horizontal Speed**
3. Establece **value** en `0`

4. Haz clic en **Add Event** -> **Keyboard Release** -> selecciona **Left Arrow**
5. Agrega la accion **Set Horizontal Speed**
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
2. Agrega la accion **Move in Direction** (o **Set Horizontal/Vertical Speed**)
3. Establece una direccion diagonal con velocidad `5`
   - Por ejemplo: **hspeed** = `4`, **vspeed** = `-4`

Esto hace que la pelota comience a moverse cuando el juego inicia.

### 3.3 Rebotar en el Paddle
1. Haz clic en **Add Event** -> **Collision** -> selecciona `obj_paddle`
2. Agrega la accion **Reverse Vertical** (para rebotar)

### 3.4 Rebotar en las Paredes
1. Haz clic en **Add Event** -> **Collision** -> selecciona `obj_wall`
2. Agrega la accion **Reverse Horizontal** o **Reverse Vertical** segun sea necesario
   - O usa ambas para manejar rebotes en esquinas

---

## Paso 4: Crear el Objeto Ladrillo

### 4.1 Crear el Objeto
1. Crea un nuevo objeto llamado `obj_brick`
2. Establece el **Sprite** como `spr_brick`
3. Marca la casilla **Solid**

### 4.2 Destruir en Colision con la Pelota
1. Haz clic en **Add Event** -> **Collision** -> selecciona `obj_ball`
2. Agrega la accion **Destroy Instance** con objetivo **self**

Esto destruye el ladrillo cuando la pelota lo golpea!

### 4.3 Hacer Rebotar la Pelota
En el mismo evento de colision, tambien agrega:
1. Agrega la accion **Reverse Vertical** (aplicada a **other** - la pelota)

O regresa a `obj_ball` y agrega:
1. **Add Event** -> **Collision** -> selecciona `obj_brick`
2. Agrega la accion **Reverse Vertical**

---

## Paso 5: Crear el Objeto Pared

### 5.1 Crear el Objeto
1. Crea un nuevo objeto llamado `obj_wall`
2. Establece el **Sprite** como `spr_wall`
3. Marca la casilla **Solid**

Eso es todo - la pared solo necesita ser solida para que la pelota rebote.

---

## Paso 6: Crear la Sala de Juego

### 6.1 Crear la Sala
1. Clic derecho en **Rooms** -> **Create Room**
2. Nombrala `room_game`

### 6.2 Establecer el Fondo (Opcional)
1. En la configuracion de la sala, encuentra **Background**
2. Selecciona tu fondo `bg_game`
3. Marca **Stretch** si quieres que llene la sala

### 6.3 Colocar los Objetos

Ahora coloca tus objetos en la sala:

1. **Coloca el Paddle:** Pon `obj_paddle` en el centro inferior de la sala

2. **Coloca las Paredes:** Pon instancias de `obj_wall` alrededor de los bordes:
   - A lo largo de la parte superior
   - A lo largo del lado izquierdo
   - A lo largo del lado derecho
   - Deja la parte inferior abierta (aqui es donde la pelota puede escapar!)

3. **Coloca la Pelota:** Pon `obj_ball` en algun lugar del centro

4. **Coloca los Ladrillos:** Organiza instancias de `obj_brick` en filas en la parte superior de la sala

---

## Paso 7: Prueba tu Juego!

1. Haz clic en el boton **Play** (flecha verde)
2. Usa las teclas de flecha **Izquierda** y **Derecha** para mover el paddle
3. Intenta rebotar la pelota para destruir todos los ladrillos!
4. Presiona **Escape** para salir

---

## Que Sigue?

Tu juego basico de Breakout esta completo! Aqui hay algunas mejoras para probar:

### Agregar un Sistema de Vidas
- Agrega un evento **No More Lives** para mostrar "Game Over"
- Pierde una vida cuando la pelota sale por abajo

### Agregar Puntuacion
- Usa la accion **Add Score** al destruir ladrillos
- Muestra la puntuacion con **Draw Score**

### Agregar Multiples Niveles
- Crea mas salas con diferentes disposiciones de ladrillos
- Usa **Next Room** cuando todos los ladrillos sean destruidos

### Agregar Efectos de Sonido
- Agrega sonidos para rebotes y destruccion de ladrillos
- Usa la accion **Play Sound**

---

## Resumen de Objetos

| Objeto | Sprite | Solid | Eventos |
|--------|--------|-------|---------|
| `obj_paddle` | `spr_paddle` | Si | Keyboard (Left/Right), Keyboard Release |
| `obj_ball` | `spr_ball` | Si | Create, Collision (paddle, wall, brick) |
| `obj_brick` | `spr_brick` | Si | Collision (ball) - Destroy self |
| `obj_wall` | `spr_wall` | Si | Ninguno necesario |

---

## Ver Tambien

- [Beginner Preset](Beginner-Preset_es) - Eventos y acciones usadas en este tutorial
- [Event Reference](Event-Reference_es) - Todos los eventos disponibles
- [Full Action Reference](Full-Action-Reference_es) - Todas las acciones disponibles
