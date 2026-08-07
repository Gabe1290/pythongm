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
**Preset:** Preset Intermedio (la acción Execute Code usada para el
temporizador no está en el preset Principiante)

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

1. En el **Árbol de Recursos**, haz clic derecho en **Sprites** y selecciona **Create Sprite**
2. Nómbralo `spr_player`
3. Haz clic en **Edit Sprite** para abrir el editor
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

1. Haz clic derecho en **Objects** y selecciona **Create Object**
2. Nómbralo `obj_wall`
3. Establece el sprite como `spr_wall`
4. **Marca la casilla "Solid"**
5. No se necesitan eventos

---

## Paso 4: Crear el Objeto Salida

La salida termina el nivel cuando el jugador la alcanza.

1. Crea un nuevo objeto llamado `obj_exit`
2. Establece el sprite como `spr_exit`

**Evento: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Output** → **Show Message**
   - Message: `You Win!`
3. Add Action: **Room** → **Next Room** (o **Restart Room** para un solo nivel)

El texto de Show Message es una cadena fija — no puede incluir un valor
en vivo como el tiempo transcurrido. El temporizador permanece visible
en el HUD (Paso 7) hasta la victoria, así que el jugador ya ha visto su
tiempo.

---

## Paso 5: Crear el Objeto Moneda

Las monedas añaden al puntaje cuando se recogen.

1. Crea un nuevo objeto llamado `obj_coin`
2. Establece el sprite como `spr_coin`

**Evento: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Score** → **Set Score**
   - New Score: `10`
   - Marca "Relative" para añadir 10 puntos
3. Add Action: **Instance** → **Destroy Instance**
   - Applies to: Self

---

## Paso 6: Crear el Objeto Jugador

El jugador se mueve fluidamente usando las teclas de flecha.

1. Crea un nuevo objeto llamado `obj_player`
2. Establece el sprite como `spr_player`

### 6.1 Movimiento

Agrega cuatro eventos **Keyboard (held)** más un evento **No Key**,
cada uno con una acción **Move** → **Set Horizontal/Vertical Speed**:

| Evento | Acción |
|---|---|
| Keyboard (held) → Right Arrow | Set Horizontal Speed a `4` |
| Keyboard (held) → Left Arrow | Set Horizontal Speed a `-4` |
| Keyboard (held) → Down Arrow | Set Vertical Speed a `4` |
| Keyboard (held) → Up Arrow | Set Vertical Speed a `-4` |
| Keyboard: No Key | Set Horizontal Speed a `0` **y** Set Vertical Speed a `0` |

### 6.2 Detenerse en las Paredes

**Evento: Collision with obj_wall**
1. Add Event → Collision → `obj_wall`
2. Add Action: **Move** → **Stop Movement**

No hace falta código manual para comprobar la posición aquí. El bucle
de movimiento de este motor ya evita que una instancia se mueva dentro
de un objeto sólido antes de dibujar el fotograma (`obj_wall` es
Solid), así que el jugador nunca puede superponerse realmente con una
pared — el evento de colisión arriba solo pone a cero cualquier
velocidad restante, para que el jugador no siga "empujando" contra
ella.

---

## Paso 7: Crear el Game Controller

El game controller gestiona el temporizador y muestra información.

1. Crea un nuevo objeto llamado `obj_game_controller`
2. No se necesita sprite

**Evento: Create** — inicia el temporizador, usando **Control** →
**Execute Code** (la acción Execute Code de este proyecto ejecuta
Python real, no GameMaker Language):

```python
self.timer = 0.0
```

**Evento: Step** — lo incrementa cada fotograma:

```python
self.timer += 1.0 / game.fps
```

**Evento: Draw** — construye el HUD con comandos reales de la cola de
dibujo. Agrega tres acciones **Draw** → **Draw Text**:

| Acción Draw Text | Texto | Posición |
|---|---|---|
| 1ª | `Score:` | X `10`, Y `10` |
| 2ª | `Time:` | X `10`, Y `30` |
| 3ª | `Coins:` | X `10`, Y `50` |

luego tres acciones **Draw** → **Draw Variable** justo después, para
mostrar los valores en vivo junto a cada etiqueta:

| Acción Draw Variable | Variable | Posición |
|---|---|---|
| 1ª | `score` | X `70`, Y `10` |
| 2ª | `self.timer` | X `70`, Y `30` |
| 3ª | *(ver abajo)* | X `70`, Y `50` |

No existe un contador integrado de "monedas restantes" al que apuntar
Draw Variable — agrega otra acción **Control** → **Execute Code**,
justo antes de las acciones Draw Variable, para calcularlo en una
variable de instancia que Draw Variable pueda leer después:

```python
self.coins_left = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_coin'
)
```

(luego establece el campo Variable de la 3ª acción Draw Variable en `self.coins_left`).

---

## Paso 8: Diseñar Tu Laberinto

1. Haz clic derecho en **Rooms** y selecciona **Create Room**
2. Nómbrala `room_maze`
3. Establece el tamaño de la sala (ej: 640x480)
4. Habilita "Snap to Grid" y establece la cuadrícula en 32x32

### Colocación de Objetos

Construye tu laberinto siguiendo estas directrices:

1. **Crea el borde** - Rodea la sala con paredes
2. **Construye pasillos** - Crea caminos a través del laberinto
3. **Coloca la salida** - Ponla al final del laberinto
4. **Dispersa monedas** - Colócalas a lo largo de los caminos
5. **Coloca al jugador** - Cerca de la entrada
6. **Añade el game controller** - En cualquier lugar (es invisible)

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

1. Haz clic en **Run** o presiona **F5** para probar
2. Usa las teclas de flecha para navegar por el laberinto
3. Recoge monedas para puntos
4. ¡Encuentra la salida para ganar!

---

## Mejoras (Opcional)

### Añadir Enemigos

Crea un enemigo patrullador simple:

1. Crea `spr_enemy` (color rojo, 24x24)
2. Crea `obj_enemy` con sprite `spr_enemy`

**Evento: Create** — Add Action: **Move** → **Start Moving Direction**
(Directions: `right`, Speed: `2`)

**Evento: Collision with obj_wall** — Add Action: **Move** → **Reverse
Horizontal** (hace girar al enemigo cuando choca con una pared — no
hace falta código; combinado con la colisión sólida integrada del Paso
6.2, el enemigo nunca puede atravesar una pared)

**Evento: Collision with obj_player** — Add Action: **Room** →
**Restart Room**

### Añadir Sistema de Vidas

En el evento **Create** de `obj_game_controller`, agrega **Score** →
**Set Lives** (Value: `3`).

En el evento **Collision with obj_player** de `obj_enemy`, reemplaza
**Restart Room** por dos acciones: **Score** → **Set Lives** (Value:
`-1`, **Relative** marcado), luego **Move** → **Jump to Start
Position** (aplicada al jugador mediante **Applies to: Other**) para
reaparecer al jugador en lugar de reiniciar todo el laberinto.

Agrega otro evento a `obj_game_controller`: **Other Events** → **No
More Lives** — esto se activa automáticamente en cuanto las vidas
llegan a 0, así que no hace falta comprobarlo manualmente. Agrega
**Output** → **Show Message** (`Game Over!`) seguido de **Room** →
**Restart Game**.

### Añadir Llaves y Puertas Cerradas

1. Crea `obj_key` — al chocar con `obj_player`, **Set Variable**
   (Variable: `global.has_key`, Value: `true`, Scope: `global`), luego
   **Destroy Instance** (self).
2. Crea `obj_locked_door`, con Solid marcado. Dale un evento **Step**
   con **Control** → **Test Variable** (Variable: `global.has_key`,
   Value: `true`, Scope: `global`) → **Instance** → **Destroy
   Instance** (self) — la puerta desaparece (y deja de bloquear) en
   cuanto se recoge la llave.

### Añadir Múltiples Niveles

1. Crea salas adicionales (`room_maze2`, `room_maze3`)
2. En `obj_exit`, usa la acción **Next Room** en lugar de **Restart Room**

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
| El jugador atraviesa paredes | Verifica que `obj_wall` tenga "Solid" marcado |
| El jugador se atasca en paredes | Asegúrate de que el sprite del jugador sea más pequeño que los huecos de las paredes |
| Las monedas no desaparecen | Verifica que el evento de colisión destruya Self, no Other |
| El temporizador no funciona | Asegúrate de que el game controller esté colocado en la sala |
| El movimiento se siente brusco | Ajusta el valor de velocidad en las acciones Set Horizontal/Vertical Speed (prueba 3-5) |

---

## Lo Que Aprendiste

¡Felicitaciones! ¡Has creado un juego de laberinto! Aprendiste:

- **Movimiento fluido** - Verificar estado de tecla mantenida para movimiento continuo
- **Colisión sólida integrada** - Las paredes bloquean el movimiento automáticamente una vez marcadas como Solid, sin código manual de comprobación de posición
- **Coleccionables** - Crear objetos que aumentan el puntaje y desaparecen
- **Sistema de temporizador** - Rastrear tiempo transcurrido con variables de instancia
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
- [Preset Intermedio](Intermediate-Preset_es) - Descripción general del preset que necesita este tutorial
- [Tutorial: Pong](Tutorial-Pong_es) - Crear un juego de dos jugadores
- [Tutorial: Breakout](Tutorial-Breakout_es) - Crear un juego de romper ladrillos
- [Tutorial: Sokoban](Tutorial-Sokoban_es) - Crear un puzzle de empujar cajas
- [Referencia de Eventos](Event-Reference_es) - Documentación completa de eventos
