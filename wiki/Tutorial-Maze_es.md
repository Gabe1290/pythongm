# Tutorial: Crear un Juego de Laberinto

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Maze) | [Français](Tutorial-Maze_fr) | [Deutsch](Tutorial-Maze_de) | [Italiano](Tutorial-Maze_it) | [Español](Tutorial-Maze_es) | [Português](Tutorial-Maze_pt) | [Slovenščina](Tutorial-Maze_sl) | [Українська](Tutorial-Maze_uk) | [Русский](Tutorial-Maze_ru)

---

## Introducción

En este tutorial, crearás un **Juego de Laberinto** donde el jugador navega a través de pasillos para llegar a la salida mientras evita obstáculos y recoge monedas. Este tipo de juego clásico es perfecto para aprender movimiento fluido, detección de colisiones y diseño de niveles.

**Lo que aprenderás:**
- Movimiento fluido del jugador con entrada de teclado
- Manejo de colisiones con paredes
- Detección de objetivo (llegar a la salida)
- Objetos coleccionables
- Sistema de temporizador simple

**Dificultad:** Principiante
**Preset:** Preset Principiante

---

## Paso 1: Entender el Juego

### Reglas del Juego
1. El jugador se mueve por un laberinto usando las teclas de flecha
2. Las paredes bloquean el movimiento del jugador
3. Recoge monedas para puntos
4. Llega a la salida para completar el nivel
5. ¡Completa el laberinto lo más rápido posible!

### Lo Que Necesitamos

| Elemento | Propósito |
|----------|-----------|
| **Jugador** | El personaje que controlas |
| **Pared** | Obstáculos sólidos que bloquean el movimiento |
| **Salida** | Meta que termina el nivel |
| **Moneda** | Objetos coleccionables para puntuación |
| **Suelo** | Fondo visual (opcional) |

---

## Paso 2: Crear los Sprites

Todos los sprites de pared y suelo deben ser de 32x32 píxeles para crear una cuadrícula apropiada.

### 2.1 Sprite del Jugador

1. En el **Árbol de Recursos**, haz clic derecho en **Sprites** y selecciona **Crear Sprite**
2. Nómbralo `spr_player`
3. Haz clic en **Editar Sprite** para abrir el editor
4. Dibuja un pequeño personaje (círculo, persona o forma de flecha)
5. Usa un color brillante como azul o verde
6. Tamaño: 24x24 píxeles (más pequeño que las paredes para navegación más fácil)
7. Haz clic en **OK** para guardar

### 2.2 Sprite de Pared

1. Crea un nuevo sprite llamado `spr_wall`
2. Dibuja un patrón sólido de ladrillo o piedra
3. Usa colores grises u oscuros
4. Tamaño: 32x32 píxeles

### 2.3 Sprite de Salida

1. Crea un nuevo sprite llamado `spr_exit`
2. Dibuja una puerta, bandera o marcador de meta brillante
3. Usa colores verdes o dorados
4. Tamaño: 32x32 píxeles

### 2.4 Sprite de Moneda

1. Crea un nuevo sprite llamado `spr_coin`
2. Dibuja un pequeño círculo amarillo/dorado
3. Tamaño: 16x16 píxeles

### 2.5 Sprite de Suelo (Opcional)

1. Crea un nuevo sprite llamado `spr_floor`
2. Dibuja un patrón simple de baldosa
3. Usa un color neutro claro
4. Tamaño: 32x32 píxeles

---

## Paso 3: Crear el Objeto Pared

La pared bloquea el movimiento del jugador.

1. Haz clic derecho en **Objetos** y selecciona **Crear Objeto**
2. Nómbralo `obj_wall`
3. Establece el sprite como `spr_wall`
4. **Marca la casilla "Sólido"**
5. No se necesitan eventos

---

## Paso 4: Crear el Objeto Salida

La salida termina el nivel cuando el jugador la alcanza.

1. Crea un nuevo objeto llamado `obj_exit`
2. Establece el sprite como `spr_exit`

**Evento: Colisión con obj_player**
1. Agregar Evento → Colisión → obj_player
2. Agregar Acción: **Main2** → **Mostrar Mensaje**
   - Mensaje: `¡Ganaste! Tiempo: ` + string(floor(global.timer)) + ` segundos`
3. Agregar Acción: **Main1** → **Siguiente Room** (o **Reiniciar Room** para un solo nivel)

---

## Paso 5: Crear el Objeto Moneda

Las monedas añaden al puntaje cuando se recogen.

1. Crea un nuevo objeto llamado `obj_coin`
2. Establece el sprite como `spr_coin`

**Evento: Colisión con obj_player**
1. Agregar Evento → Colisión → obj_player
2. Agregar Acción: **Score** → **Establecer Score**
   - Nuevo Score: `10`
   - Marca "Relativo" para añadir 10 puntos
3. Agregar Acción: **Main1** → **Destruir Instancia**
   - Se aplica a: Self

---

## Paso 6: Crear el Objeto Jugador

El jugador se mueve fluidamente usando las teclas de flecha.

1. Crea un nuevo objeto llamado `obj_player`
2. Establece el sprite como `spr_player`

### 6.1 Evento Create - Inicializar Variables

**Evento: Create**
1. Agregar Evento → Create
2. Agregar Acción: **Control** → **Establecer Variable**
   - Variable: `move_speed`
   - Valor: `4`

### 6.2 Movimiento con Colisión

**Evento: Step**
1. Agregar Evento → Step → Step
2. Agregar Acción: **Control** → **Ejecutar Código**

```gml
// Movimiento horizontal
var hspd = 0;
if (keyboard_check(vk_right)) hspd = move_speed;
if (keyboard_check(vk_left)) hspd = -move_speed;

// Movimiento vertical
var vspd = 0;
if (keyboard_check(vk_down)) vspd = move_speed;
if (keyboard_check(vk_up)) vspd = -move_speed;

// Verificación de colisión horizontal
if (!place_meeting(x + hspd, y, obj_wall)) {
    x += hspd;
} else {
    // Moverse tan cerca de la pared como sea posible
    while (!place_meeting(x + sign(hspd), y, obj_wall)) {
        x += sign(hspd);
    }
}

// Verificación de colisión vertical
if (!place_meeting(x, y + vspd, obj_wall)) {
    y += vspd;
} else {
    // Moverse tan cerca de la pared como sea posible
    while (!place_meeting(x, y + sign(vspd), obj_wall)) {
        y += sign(vspd);
    }
}
```

### 6.3 Alternativa: Movimiento Simple por Bloques

Si prefieres usar bloques de acción en lugar de código:

**Evento: Tecla Presionada - Flecha Derecha**
1. Agregar Evento → Teclado → \<Derecha\>
2. Agregar Acción: **Control** → **Probar Colisión**
   - Objeto: `obj_wall`
   - X: `4`
   - Y: `0`
   - Verificar: NOT
3. Agregar Acción: **Movimiento** → **Saltar a Posición**
   - X: `4`
   - Y: `0`
   - Marca "Relativo"

Repite para Izquierda (-4, 0), Arriba (0, -4) y Abajo (0, 4).

---

## Paso 7: Crear el Controlador del Juego

El controlador del juego gestiona el temporizador y muestra información.

1. Crea un nuevo objeto llamado `obj_game_controller`
2. No se necesita sprite

**Evento: Create**
1. Agregar Evento → Create
2. Agregar Acción: **Control** → **Establecer Variable**
   - Variable: `global.timer`
   - Valor: `0`

**Evento: Step**
1. Agregar Evento → Step → Step
2. Agregar Acción: **Control** → **Establecer Variable**
   - Variable: `global.timer`
   - Valor: `1/room_speed`
   - Marca "Relativo"

**Evento: Draw**
1. Agregar Evento → Draw → Draw
2. Agregar Acción: **Control** → **Ejecutar Código**

```gml
// Dibujar puntuación
draw_set_color(c_white);
draw_text(10, 10, "Puntos: " + string(score));

// Dibujar temporizador
draw_text(10, 30, "Tiempo: " + string(floor(global.timer)) + "s");

// Dibujar monedas restantes
var coins_left = instance_number(obj_coin);
draw_text(10, 50, "Monedas: " + string(coins_left));
```

---

## Paso 8: Diseñar Tu Laberinto

1. Haz clic derecho en **Rooms** y selecciona **Crear Room**
2. Nómbrala `room_maze`
3. Establece el tamaño de la room (ej: 640x480)
4. Habilita "Ajustar a Cuadrícula" y establece la cuadrícula en 32x32

### Colocación de Objetos

Construye tu laberinto siguiendo estas directrices:

1. **Crea el borde** - Rodea la room con paredes
2. **Construye pasillos** - Crea caminos a través del laberinto
3. **Coloca la salida** - Ponla al final del laberinto
4. **Dispersa monedas** - Colócalas a lo largo de los caminos
5. **Coloca al jugador** - Cerca de la entrada
6. **Añade el controlador del juego** - En cualquier lugar (es invisible)

### Ejemplo de Diseño de Laberinto

```
W W W W W W W W W W W W W W W W W W W W
W P . . . . W . . . . . . . W . . . . W
W . W W W . W . W W W W W . W . W W . W
W . W . . . . . . . . . . . . . . W . W
W . W . W W W W W . W W W W W W . W . W
W . . . W . . . . . . . . C . W . . . W
W W W . W . W W W W W W W . . W W W . W
W C . . . . W . . . . . W . . . . . . W
W . W W W W W . W W W . W W W W W W . W
W . . . . . . . . C . . . . . . . . . W
W . W W W W W W W W W . W W W W W W . W
W . . . . . . . . . . . W . . . . . . W
W W W W W W W W W W W . W . W W W W . W
W . . . . . . . . . . . . . W . C . E W
W W W W W W W W W W W W W W W W W W W W

W = Pared    P = Jugador    E = Salida    C = Moneda    . = Vacío
```

---

## Paso 9: ¡Prueba Tu Juego!

1. Haz clic en **Ejecutar** o presiona **F5** para probar
2. Usa las teclas de flecha para navegar por el laberinto
3. Recoge monedas para puntos
4. ¡Encuentra la salida para ganar!

---

## Mejoras (Opcional)

### Añadir Enemigos

Crea un enemigo patrullador simple:

1. Crea `spr_enemy` (color rojo, 24x24)
2. Crea `obj_enemy` con sprite `spr_enemy`

**Evento: Create**
```gml
hspeed = 2;  // Se mueve horizontalmente
```

**Evento: Colisión con obj_wall**
```gml
hspeed = -hspeed;  // Invertir dirección
```

**Evento: Colisión con obj_player**
```gml
room_restart();  // El jugador pierde
```

### Añadir Sistema de Vidas

En el evento Create de `obj_game_controller`:
```gml
global.lives = 3;
```

Cuando el jugador toca un enemigo (en lugar de reiniciar):
```gml
global.lives -= 1;
if (global.lives <= 0) {
    show_message("¡Game Over!");
    game_restart();
} else {
    // Reaparecer jugador al inicio
    obj_player.x = start_x;
    obj_player.y = start_y;
}
```

### Añadir Llaves y Puertas Cerradas

1. Crea `obj_key` - desaparece al recogerse, establece `global.has_key = true`
2. Crea `obj_locked_door` - solo se abre cuando `global.has_key == true`

### Añadir Múltiples Niveles

1. Crea rooms adicionales (`room_maze2`, `room_maze3`)
2. En `obj_exit`, usa `room_goto_next()` en lugar de `room_restart()`

### Añadir Efectos de Sonido

Añade sonidos para:
- Recoger monedas
- Alcanzar la salida
- Tocar enemigos (si se añadieron)
- Música de fondo

---

## Solución de Problemas

| Problema | Solución |
|----------|----------|
| El jugador atraviesa paredes | Verifica que `obj_wall` tenga "Sólido" marcado |
| El jugador se atasca en paredes | Asegúrate de que el sprite del jugador sea más pequeño que los huecos de las paredes |
| Las monedas no desaparecen | Verifica que el evento de colisión destruya Self, no Other |
| El temporizador no funciona | Asegúrate de que el controlador del juego esté colocado en la room |
| El movimiento se siente brusco | Ajusta el valor de `move_speed` (prueba 3-5) |

---

## Lo Que Aprendiste

¡Felicitaciones! ¡Has creado un juego de laberinto! Aprendiste:

- **Movimiento fluido** - Verificar estado de tecla presionada para movimiento continuo
- **Detección de colisiones** - Usar `place_meeting` para verificar antes de moverse
- **Colisión pixel-perfect** - Moverse tan cerca de las paredes como sea posible
- **Coleccionables** - Crear objetos que aumentan el puntaje y desaparecen
- **Sistema de temporizador** - Rastrear tiempo transcurrido con variables
- **Diseño de niveles** - Crear diseños de laberinto navegables

---

## Ideas de Desafíos

1. **Contra Reloj** - Añade un temporizador de cuenta regresiva. ¡Llega a la salida antes de que se acabe el tiempo!
2. **Puntaje Perfecto** - Requiere recoger todas las monedas antes de que se abra la salida
3. **Laberinto Aleatorio** - Investiga generación procedimental de laberintos
4. **Niebla de Guerra** - Solo muestra el área alrededor del jugador
5. **Minimapa** - Muestra una pequeña vista general del laberinto

---

## Ver También

- [Tutoriales](Tutorials_es) - Más tutoriales de juegos
- [Preset Principiante](Beginner-Preset_es) - Resumen de características para principiantes
- [Tutorial: Pong](Tutorial-Pong_es) - Crear un juego de dos jugadores
- [Tutorial: Breakout](Tutorial-Breakout_es) - Crear un juego de romper ladrillos
- [Tutorial: Sokoban](Tutorial-Sokoban_es) - Crear un puzzle de empujar cajas
- [Referencia de Eventos](Event-Reference_es) - Documentación completa de eventos
