# Tutorial: Crear un Juego de Aterrizaje Lunar

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Introducción

En este tutorial, crearás un **Juego de Aterrizaje Lunar** - un juego arcade clásico donde controlas una nave espacial descendiendo hacia una plataforma de aterrizaje. Debes gestionar tu impulso para contrarrestar la gravedad y aterrizar suavemente sin estrellarte. Este juego es perfecto para aprender conceptos físicos como gravedad, impulso, velocidad y gestión de combustible.

**Lo que aprenderás:**
- Física de gravedad e impulso
- Detección de aterrizaje basada en velocidad
- Sistema de gestión de combustible
- Control de rotación o direccional
- Zonas de aterrizaje seguro

**Dificultad:** Principiante
**Preset:** Preset Intermedio (la física de impulso/combustible depende
por completo de Execute Code, que no está en el preset Principiante)

---

## Paso 1: Entender el Juego

### Mecánicas del Juego
1. El módulo es atraído hacia abajo por la gravedad
2. Presionar ARRIBA aplica impulso hacia arriba (usa combustible)
3. IZQUIERDA/DERECHA controla rotación o movimiento
4. Aterriza suavemente en la plataforma para ganar
5. Te estrellas si aterrizas muy rápido o fallas la plataforma
6. ¡Sin combustible no puedes frenar!

### Lo Que Necesitamos

| Elemento | Propósito |
|----------|-----------|
| **Módulo** | La nave que controlas |
| **Plataforma** | Zona segura para aterrizar |
| **Suelo** | Terreno que causa el choque |
| **Display Combustible** | Muestra el combustible restante |
| **Display Velocidad** | Muestra la velocidad actual |

---

## Paso 2: Crear los Sprites

### Sprites
- `spr_lander` (32x32 píxeles) - nave espacial simple
- `spr_pad` (64x16 píxeles) - plataforma de aterrizaje
- `spr_ground` (32x32 píxeles) - terreno rocoso
- `spr_flame` (16x16 píxeles) - llama de propulsión (opcional)

---

## Paso 3-4: Crear Objetos de Suelo y Plataforma

**obj_ground** y **obj_pad**: Establece el sprite, marca "Solid"

---

## Paso 5: Crear el Objeto Módulo

El módulo es el objeto principal controlado por el jugador. A
diferencia de los demás tutoriales de movimiento de este wiki, sus
controles necesitan acumular velocidad gradualmente y llevar un
registro de un recurso de combustible, así que este objeto depende más
de **Control** → **Execute Code** (Python real — `self` es la
instancia actual, `game` es el gestor del juego, `keyboard.check(name)`
indica si una tecla está presionada) que los tutoriales de movimiento
anteriores, pero sigue usando una acción estructurada donde es posible.

### 5.1 Gravedad y Variables Iniciales

**Evento: Create**
1. Acción: **Move** → **Set Gravity** (Direction: `270`, Gravity:
   `0.05`) — una atracción suave hacia abajo; el motor la suma
   automáticamente a la velocidad vertical del módulo en cada
   fotograma, igual que en el tutorial de Plataformas, solo que más
   débil.
2. Acción: **Control** → **Execute Code**:

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

El sistema de movimiento de este motor ya rastrea la velocidad mediante
`self.hspeed`/`self.vspeed` y mueve la instancia esa cantidad en cada
fotograma (con colisión sólida integrada) — no hace falta crear
variables separadas `hsp`/`vsp` como haría una simulación física
manual.

### 5.2 Evento Step — Impulso y Controles

**Evento: Step** — Acción: **Control** → **Execute Code**:

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

    # Evita que el módulo se salga por los lados o por arriba de la sala
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

Todo el bloque está envuelto en `if not self.landed and not
self.crashed:` para que el impulso y el control se detengan en el
instante en que el juego termina — el objeto no tiene forma de
interrumpir un evento a medio camino (no hay `exit` como en GML); un
`if` alrededor del resto del código cumple la misma función.

### 5.3 Colisión con la Plataforma

**Evento: Collision with obj_pad**
1. Acción: **Control** → **Test Expression**
   - Expression: `(self.hspeed**2 + self.vspeed**2)**0.5 <=
     self.safe_speed` — la velocidad de aterrizaje es la longitud del
     vector velocidad (teorema de Pitágoras), no una variable `speed`
     (en este motor `speed` es la *velocidad de animación* del sprite,
     no la magnitud del movimiento — una trampa real para quienes
     vienen de GameMaker).
   - Then Actions:
     1. **Control** → **Set Variable** (Variable: `landed`, Value: `true`, Scope: `self`)
     2. **Move** → **Stop Movement**
     3. **Move** → **Set Gravity** (Direction: `270`, Gravity: `0`) —
        evita que la gravedad vuelva a acumular velocidad vertical sin
        que nadie lo note en un módulo que ya aterrizó
     4. **Output** → **Show Message** (Message: `¡Aterrizaje Perfecto! ¡Ganaste!`)
   - Else Actions:
     1. **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
     2. **Output** → **Show Message** (Message: `¡Choque! ¡Muy rápido!`)
     3. **Room** → **Restart Room**

El texto de Show Message es una cadena fija — no puede mostrar la
velocidad de aterrizaje real. El HUD (Paso 7) ya muestra la velocidad
en vivo hasta el momento del contacto, así que el jugador ya ha visto
el número.

### 5.4 Colisión con el Suelo

**Evento: Collision with obj_ground**
1. Acción: **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
2. Acción: **Output** → **Show Message** (Message: `¡Choque contra el terreno!`)
3. Acción: **Room** → **Restart Room**

---

## Paso 6-7: Game Controller

**obj_game_controller** — Evento Draw: encuentra el módulo mediante un
bucle sobre `game.current_room.instances` (el mismo patrón que el
contador de monedas del tutorial del Laberinto), calcula el
combustible/velocidad redondeados en un **Execute Code**, y luego los
muestra con **Draw Text**/**Draw Variable**; consulta la [versión en
inglés](Tutorial-LunarLander) para los detalles completos acción por
acción.

---

## Paso 8: Diseña Tu Nivel

1. Crea `room_game` (640x480)
2. Fondo negro (espacio)
3. Coloca el suelo abajo con una abertura
4. Coloca la plataforma en la abertura
5. Coloca el módulo arriba
6. Coloca el game controller

---

## Lo Que Aprendiste

- **Física de impulso** - Ajustar `self.vspeed` contra una atracción continua de Set Gravity
- **Gestión de velocidad** - Calcular la velocidad a partir de `hspeed`/`vspeed` con el teorema de Pitágoras
- **Sistema de combustible** - Gestión de recursos con una simple variable de instancia
- **Detección de colisiones** - Resultados diferentes para plataforma y suelo, elegidos con Test Expression

---

## Ver También

- [Tutoriales](Tutorials_es) - Más tutoriales
- [Tutorial: Platformer](Tutorial-Platformer_es) - Crear un juego de plataformas
