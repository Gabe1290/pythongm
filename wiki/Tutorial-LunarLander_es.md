# Tutorial: Crear un Juego de Alunizaje

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Introducción

En este tutorial, crearás un **Juego de Alunizaje** - un juego de arcade clásico donde controlas una nave espacial que desciende hacia una plataforma de aterrizaje. Debes gestionar tu empuje para contrarrestar la gravedad y aterrizar suavemente sin estrellarte. Este juego es perfecto para aprender conceptos de física como gravedad, empuje, velocidad y gestión de combustible.

**Lo que aprenderás:**
- Física de gravedad y empuje
- Detección de aterrizaje basada en la velocidad
- Sistema de gestión de combustible
- Control de rotación o direccional
- Zonas de aterrizaje seguras

**Dificultad:** Principiante
**Preset:** Preset Intermedio (la física de empuje/combustible se apoya en Execute Code en todo momento, que no está en el preset Principiante)

---

## Paso 1: Entender el Juego

### Mecánicas del Juego
1. El módulo es empujado hacia abajo por la gravedad
2. Pulsar ARRIBA aplica empuje hacia arriba (usa combustible)
3. IZQUIERDA/DERECHA controlan la rotación o el movimiento del módulo
4. Aterriza suavemente en la plataforma para ganar
5. Te estrellas si aterrizas demasiado rápido o fallas la plataforma
6. ¡Si te quedas sin combustible no puedes frenar!

### Lo Que Necesitamos

| Elemento | Propósito |
|----------|-----------|
| **Módulo** | La nave espacial que controlas |
| **Plataforma de Aterrizaje** | Zona segura para aterrizar |
| **Suelo** | Terreno que provoca un choque |
| **Indicador de Combustible** | Muestra el combustible restante |
| **Indicador de Velocidad** | Muestra la velocidad actual |

---

## Paso 2: Crear los Sprites

### 2.1 Sprite del Módulo

1. En el **Árbol de Recursos**, haz clic derecho en **Sprites** y selecciona **Create Sprite**
2. Nómbralo `spr_lander`
3. Haz clic en **Edit Sprite** para abrir el editor de sprites
4. Dibuja una nave espacial simple (triángulo o forma de módulo clásica)
5. Tamaño: 32x32 píxeles
6. **Importante:** establece el origen en centro-abajo para un aterrizaje correcto

### 2.2 Sprite de la Plataforma de Aterrizaje

1. Crea un nuevo sprite llamado `spr_pad`
2. Dibuja una plataforma plana con marcas (como una "H")
3. Usa colores vivos (amarillo/verde)
4. Tamaño: 64x16 píxeles

### 2.3 Sprite del Suelo

1. Crea un nuevo sprite llamado `spr_ground`
2. Dibuja un terreno rocoso/áspero
3. Usa colores gris/marrón
4. Tamaño: 32x32 píxeles

### 2.4 Sprite de Llama (Opcional)

1. Crea un nuevo sprite llamado `spr_flame`
2. Dibuja una pequeña llama/chorro de escape
3. Usa colores naranja/amarillo
4. Tamaño: 16x16 píxeles

![The Sprite Editor with spr_lander open, Origin set to Center-Bottom (X 16, Y 32); spr_lander, spr_pad, spr_ground and spr_flame in the resource tree](images/tutorial-lunarlander-02-sprites.png)

---

## Paso 3: Crear el Objeto Suelo

El suelo es terreno peligroso que provoca un choque.

1. Haz clic derecho en **Objects** y selecciona **Create Object**
2. Nómbralo `obj_ground`
3. Establece el sprite en `spr_ground`
4. **Marca la casilla "Solid"**
5. No se necesitan eventos

![obj_ground's Object Events panel: empty -- Solid checked is all it needs](images/tutorial-lunarlander-03-ground-object.png)

---

## Paso 4: Crear el Objeto Plataforma de Aterrizaje

La plataforma de aterrizaje es donde el jugador debe aterrizar de forma segura.

1. Crea un nuevo objeto llamado `obj_pad`
2. Establece el sprite en `spr_pad`
3. **Marca la casilla "Solid"**
4. No se necesitan eventos (la colisión la gestiona el módulo)

![obj_pad's Object Events panel: empty, with Solid checked](images/tutorial-lunarlander-04-pad-object.png)

---

## Paso 5: Crear el Objeto Módulo

El módulo es el principal objeto controlado por el jugador, con física. A
diferencia de los otros tutoriales de movimiento de este wiki, sus
controles necesitan acumular velocidad gradualmente y hacer seguimiento
de un recurso de combustible, así que este objeto se apoya más en
**Control** → **Execute Code** (Python real — `self` es la instancia
actual, `game` es el motor del juego, `keyboard.check(nombre)` informa de
una tecla mantenida) que solo en acciones estructuradas. Donde una acción
estructurada hace el trabajo, este tutorial sigue usando una.

1. Crea un nuevo objeto llamado `obj_lander`
2. Establece el sprite en `spr_lander`

### 5.1 Gravedad y Variables Iniciales

**Evento: Create**
1. Añade la acción **Move** → **Set Gravity** (Direction: `270`, Gravity: `0.05`)
   — una atracción suave hacia abajo; el motor la añade automáticamente a
   la velocidad vertical del módulo en cada paso, igual que la gravedad
   del tutorial de Plataformas, solo que más débil.
2. Añade la acción **Control** → **Execute Code**:

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

El sistema de movimiento de este proyecto ya hace seguimiento de la
velocidad mediante `self.hspeed`/`self.vspeed` y mueve la instancia esa
cantidad en cada fotograma (con la colisión sólida integrada) — no hace
falta crear variables `hsp`/`vsp` separadas como haría una simulación
física manual.

### 5.2 Evento Step — Empuje y Controles

**Evento: Step** — Añade la acción **Control** → **Execute Code**:

```python
if not self.landed and not self.crashed:
    if keyboard.check('up') and self.fuel > 0:
        self.vspeed -= self.thrust_force
        self.fuel -= self.fuel_use
        if self.fuel < 0:
            self.fuel = 0

    if keyboard.check('left'):
        self.hspeed -= 0.05
    if keyboard.check('right'):
        self.hspeed += 0.05

    # Limita la velocidad máxima
    self.hspeed = max(-self.max_speed, min(self.max_speed, self.hspeed))
    self.vspeed = max(-self.max_speed, min(self.max_speed, self.vspeed))

    # Evita que el módulo se salga por los lados o por encima de la room
    room = game.current_room
    if self.x < 16:
        self.x = 16
        self.hspeed = 0
    if self.x > room.width - 16:
        self.x = room.width - 16
        self.hspeed = 0
    if self.y < 16:
        self.y = 16
        self.vspeed = 0
```

Todo el bloque está envuelto en `if not self.landed and not self.crashed:`
para que el empuje y la dirección se detengan en el instante en que
termina la partida — el objeto `self` no tiene forma de abandonar un
evento a mitad (no hay `exit` al estilo GML), así que un `if` alrededor
del resto del código es el equivalente.

### 5.3 Colisión con la Plataforma de Aterrizaje

**Evento: Collision with obj_pad**
1. Añade la acción **Control** → **Test Expression**
   - Expression: `(self.hspeed**2 + self.vspeed**2)**0.5 <= self.safe_speed`
     — la velocidad de aterrizaje es la longitud del vector de velocidad;
     Pitágoras, no una variable `speed` (en este motor, `speed` es la
     *velocidad de animación del sprite*, no la magnitud del movimiento —
     una trampa real viniendo de GameMaker).
   - Then Actions:
     1. **Control** → **Set Variable** (Variable: `landed`, Value: `true`, Scope: `self`)
     2. **Move** → **Stop Movement**
     3. **Move** → **Set Gravity** (Direction: `270`, Gravity: `0`) — evita
        que la gravedad vuelva a acumular velocidad vertical de forma
        silenciosa en un módulo que ya ha aterrizado
     4. **Output** → **Show Message** (Message: `Perfect Landing! You Win!`)
   - Else Actions:
     1. **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
     2. **Output** → **Show Message** (Message: `Crashed! Too fast!`)
     3. **Room** → **Restart Room**

El texto de Show Message es una cadena fija — no puede incrustar la
velocidad real de aterrizaje. El HUD (Paso 7) ya muestra la velocidad en
vivo hasta el momento del contacto, así que el jugador ya ha visto el
número.

### 5.4 Colisión con el Suelo

**Evento: Collision with obj_ground**
1. Añade la acción **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
2. Añade la acción **Output** → **Show Message** (Message: `Crashed into terrain!`)
3. Añade la acción **Room** → **Restart Room**

![obj_lander's Object Events panel: Create (Set Gravity + Execute Code), Step (Execute Code), Collision with obj_pad (the Test Expression landing check), Collision with obj_ground (Set Variable + Show Message + Restart Room)](images/tutorial-lunarlander-05-lander-object.png)

---

## Paso 6: Crear el Objeto Llama (Opcional)

Retroalimentación visual al aplicar empuje.

1. Crea un nuevo objeto llamado `obj_flame`
2. Establece el sprite en `spr_flame`

Lo creará el módulo al aplicar empuje (característica avanzada). Para un
enfoque más simple, puedes dibujar la llama en el evento Draw del módulo.

![obj_flame's Object Events panel: empty -- it just needs the spr_flame sprite](images/tutorial-lunarlander-06-flame-object.png)

---

## Paso 7: Crear el Controlador de Juego

El controlador de juego muestra combustible, velocidad e instrucciones
leyéndolos de la instancia del módulo en cada fotograma.

1. Crea un nuevo objeto llamado `obj_game_controller`
2. No se necesita sprite

**Evento: Draw**
1. Añade la acción **Control** → **Execute Code** — encuentra el módulo y
   calcula los valores que mostrarán las acciones Draw de abajo:

```python
lander = None
for inst in game.current_room.instances:
    if inst.object_name == 'obj_lander':
        lander = inst
        break

if lander is not None:
    self.fuel_display = round(lander.fuel)
    self.speed_display = round((lander.hspeed ** 2 + lander.vspeed ** 2) ** 0.5, 2)
    self.too_fast = self.speed_display > lander.safe_speed
    self.no_fuel = lander.fuel <= 0
else:
    self.fuel_display = 0
    self.speed_display = 0.0
    self.too_fast = False
    self.no_fuel = False
```

2. Añade la acción **Game** → **Set Draw Color** (Color: `#FFFFFF`)
3. Añade la acción **Game** → **Draw Text** (Text: `LUNAR LANDER`, X: `10`, Y: `10`)
4. Añade la acción **Game** → **Draw Text** (Text: `Fuel:`, X: `10`, Y: `30`)
5. Añade la acción **Game** → **Draw Variable** (Variable: `self.fuel_display`, X: `70`, Y: `30`)
6. Añade la acción **Game** → **Draw Text** (Text: `Speed:`, X: `10`, Y: `50`)
7. Añade la acción **Game** → **Draw Variable** (Variable: `self.speed_display`, X: `70`, Y: `50`)
8. Añade la acción **Game** → **Draw Text** (Text: `Safe Speed: < 2`, X: `10`, Y: `70`)

Luego las dos líneas de aviso, cada una condicionada por **Control** →
**Test Expression** (no hace falta Else — no se dibuja nada cuando la
condición es falsa):

9. **Control** → **Test Expression** (Expression: `self.too_fast`)
   - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
     **Draw Text** (`TOO FAST!`, X `10`, Y `90`)
   - Else Actions: **Game** → **Set Draw Color** (`#00FF00`), **Game** →
     **Draw Text** (`Speed OK`, X `10`, Y `90`)
10. **Control** → **Test Expression** (Expression: `self.no_fuel`)
    - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
      **Draw Text** (`NO FUEL!`, X `10`, Y `110`)

11. Añade la acción **Game** → **Set Draw Color** (Color: `#808080`)
12. Añade la acción **Game** → **Draw Text** (Text: `UP: Thrust | LEFT/RIGHT: Move`,
    X: `10`, Y: `440`) — elige una Y cerca de la parte inferior del tamaño
    de room que uses en el Paso 8.

![obj_game_controller's Object Events panel: a Draw event with 12 actions -- the Execute Code HUD-value calculation, then the Set Draw Color / Draw Text / Draw Variable chain and the two Test Expression warning blocks -- with no sprite set](images/tutorial-lunarlander-07-controller-object.png)

---

## Paso 8: Diseñar Tu Nivel

1. Haz clic derecho en **Rooms** y selecciona **Create Room**
2. Nómbrala `room_game`
3. Establece el tamaño de la room (p. ej. 640x480)
4. Establece el color de fondo en negro (espacio)

### Colocar los Objetos

Construye tu nivel siguiendo estas pautas:

1. **Suelo** - Coloca `obj_ground` a lo largo de la parte inferior para crear el terreno
2. **Plataforma de aterrizaje** - Coloca `obj_pad` en un hueco del terreno
3. **Módulo** - Coloca `obj_lander` en la parte superior de la room
4. **Controlador de juego** - Coloca `obj_game_controller` en cualquier parte

### Ejemplo de Diseño de Nivel

```
    L                          <- El módulo empieza aquí




GGG    GGG    PPPP    GGG    GGG
GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG

G = Suelo    L = Módulo    P = Plataforma de aterrizaje
```

![The Room Editor for room_game: a solid terrain row along the bottom with rocky chunks above it, a yellow landing pad in a clear gap, the white lander near the top-left, and the obj_game_controller marker near the top-right, all on a black space background](images/tutorial-lunarlander-08-room.png)

---

## Paso 9: ¡Prueba Tu Juego!

1. Haz clic en **Ejecutar** o pulsa **F5** para probar
2. Usa la flecha **ARRIBA** para el empuje (¡vigila tu combustible!)
3. Usa las flechas **IZQUIERDA/DERECHA** para dirigir
4. Aterriza suavemente en la plataforma (la velocidad debe ser inferior a 2)
5. ¡Evita el terreno rocoso!

---

## Mejoras (Opcional)

### Añadir Control de Rotación

En lugar de movimiento izquierda/derecha, rota el módulo y aplica empuje
en la dirección a la que apunta. Las instancias de este motor tienen un
atributo `rotation` real (grados, 0 = derecha, creciente en sentido
antihorario) que se usa para girar el sprite — no hace falta
`image_angle`/`lengthdir_x`/`lengthdir_y`, ya que `math` ya está
disponible en Execute Code:

Reemplaza el código del evento Create del 5.1 por:
```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
self.rotation = 90  # apuntando hacia arriba
self.rotation_speed = 3
```

Reemplaza las líneas de dirección del 5.2 (el bloque `left`/`right` →
`hspeed`) por:
```python
if keyboard.check('left'):
    self.rotation -= self.rotation_speed
if keyboard.check('right'):
    self.rotation += self.rotation_speed
```

Y reemplaza las líneas de empuje por:
```python
if keyboard.check('up') and self.fuel > 0:
    rad = math.radians(self.rotation)
    self.hspeed += self.thrust_force * math.cos(rad)
    self.vspeed -= self.thrust_force * math.sin(rad)
    self.fuel -= self.fuel_use
    if self.fuel < 0:
        self.fuel = 0
```

(el `-=` en `vspeed` coincide con el código de gravedad del propio motor —
el eje Y de la pantalla aumenta hacia abajo, así que "arriba" es
velocidad vertical negativa).

### Añadir Varias Plataformas de Aterrizaje

Crea plataformas de distintos tamaños con distintos valores de puntos:
- Plataforma pequeña = 100 puntos (más difícil)
- Plataforma grande = 50 puntos (más fácil)

### Añadir Recargas de Combustible

1. Crea `obj_fuel` que flote en el aire
2. Al colisionar con el módulo, añade combustible y destrúyelo

### Añadir Niveles

Crea varias rooms con terreno cada vez más difícil y plataformas de
aterrizaje más pequeñas.

### Añadir Viento

Añade un pequeño empuje horizontal constante. En el código del evento
Create de `obj_lander`, añade `self.wind_force = 0.02`; luego, al principio
del bloque `if not self.landed and not self.crashed:` del evento Step,
añade:
```python
self.hspeed += self.wind_force
```

---

## Solución de Problemas

| Problema | Solución |
|----------|----------|
| El módulo cae demasiado rápido | Disminuye el valor `Gravity` de Set Gravity, o aumenta `thrust_force` en el código del evento Create |
| No puedo frenar lo suficiente | Aumenta `thrust_force`, o aumenta `safe_speed` |
| El combustible se agota demasiado rápido | Disminuye `fuel_use`, o aumenta el `fuel` inicial |
| El módulo se sale de la pantalla | Comprueba el bloque de límites al final del código del evento Step |
| El aterrizaje no se registra | Asegúrate de que `obj_pad` tiene "Solid" marcado |

---

## Lo Que Aprendiste

¡Felicidades! ¡Has creado un juego de alunizaje! Aprendiste:

- **Física de empuje** - Ajustar `self.vspeed` contra una atracción continua de Set Gravity
- **Gestión de velocidad** - Calcular la velocidad a partir de `hspeed`/`vspeed` con el teorema de Pitágoras
- **Sistema de combustible** - Jugabilidad de gestión de recursos con una simple variable de instancia
- **Detección de colisión** - Resultados diferentes para plataforma vs suelo, elegidos con Test Expression
- **Visualización de HUD** - Calcular los valores a mostrar en Execute Code y luego mostrarlos con Draw Text/Draw Variable

---

## Ideas de Desafío

1. **Rotación Realista** - Rotar y aplicar empuje en la dirección a la que se apunta
2. **Varios Niveles** - Terreno cada vez más difícil
3. **Sistema de Puntuación** - Puntos según el combustible restante y la precisión del aterrizaje
4. **Asteroides** - Añadir peligros móviles que esquivar
5. **Modo de Dos Jugadores** - Carrera por aterrizar primero

---

## Ver También

- [Tutoriales](Tutorials_es) - Más tutoriales de juegos
- [Preset Intermedio](Intermediate-Preset_es) - Resumen del preset que necesita este tutorial
- [Tutorial: Plataformas](Tutorial-Platformer_es) - Crear un juego de saltos de plataforma
- [Tutorial: Laberinto](Tutorial-Maze_es) - Crear un juego de navegación por laberinto
- [Referencia de Eventos](Event-Reference_es) - Documentación completa de eventos
