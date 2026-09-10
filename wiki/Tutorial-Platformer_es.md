# Tutorial: Crear un Juego de Plataformas

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Platformer) | [Français](Tutorial-Platformer_fr) | [Deutsch](Tutorial-Platformer_de) | [Italiano](Tutorial-Platformer_it) | [Español](Tutorial-Platformer_es) | [Português](Tutorial-Platformer_pt) | [Slovenščina](Tutorial-Platformer_sl) | [Українська](Tutorial-Platformer_uk) | [Русский](Tutorial-Platformer_ru)

---

## Introducción

En este tutorial, crearás un **Juego de Plataformas** - un juego de acción de desplazamiento lateral donde el jugador corre, salta y navega por plataformas mientras evita peligros y recoge monedas. Este género clásico es perfecto para aprender gravedad, mecánicas de salto y colisión con plataformas.

**Lo que aprenderás:**
- Gravedad y física de caída
- Mecánicas de salto con detección del suelo
- Colisión con plataformas (aterrizar encima)
- Movimiento izquierda/derecha
- Coleccionables y peligros

**Dificultad:** Principiante
**Preset:** Preset Intermedio (las acciones Execute Code de la sección Mejoras no están en el preset Principiante; el tutorial base hasta el Paso 10 solo necesita acciones del preset Principiante)

---

## Paso 1: Entender el Juego

### Mecánicas del Juego
1. El jugador es afectado por la gravedad y cae
2. El jugador puede moverse a izquierda y derecha
3. El jugador puede saltar cuando está en el suelo
4. Las plataformas evitan que el jugador caiga a través
5. Recoge monedas para puntos
6. Alcanza la bandera para completar el nivel

### Lo Que Necesitamos

| Elemento | Propósito |
|----------|-----------|
| **Jugador** | El personaje que controlas |
| **Suelo/Plataforma** | Superficies sólidas para pararse |
| **Moneda** | Objetos coleccionables para puntuación |
| **Pico** | Peligro que daña al jugador |
| **Bandera** | Meta que termina el nivel |

---

## Paso 2: Crear los Sprites

### 2.1 Sprite del Jugador

1. En el **Árbol de Recursos**, haz clic derecho en **Sprites** y selecciona **Create Sprite**
2. Nómbralo `spr_player`
3. Haz clic en **Edit Sprite** para abrir el editor de sprites
4. Dibuja un personaje simple (rectángulo con cara, o monigote)
5. Usa un color vivo como azul o rojo
6. Tamaño: 32x48 píxeles (más alto que ancho para un personaje)
7. Haz clic en **OK** para guardar

### 2.2 Sprite del Suelo

1. Crea un nuevo sprite llamado `spr_ground`
2. Dibuja una baldosa de plataforma de hierba/tierra
3. Usa colores marrón y verde
4. Tamaño: 32x32 píxeles

### 2.3 Sprite de Plataforma

1. Crea un nuevo sprite llamado `spr_platform`
2. Dibuja una plataforma flotante (madera o piedra)
3. Tamaño: 64x16 píxeles (ancha y fina)

### 2.4 Sprite de Moneda

1. Crea un nuevo sprite llamado `spr_coin`
2. Dibuja un pequeño círculo amarillo/dorado
3. Tamaño: 16x16 píxeles

### 2.5 Sprite de Pico

1. Crea un nuevo sprite llamado `spr_spike`
2. Dibuja picos triangulares apuntando hacia arriba
3. Usa colores grises o rojos
4. Tamaño: 32x32 píxeles

### 2.6 Sprite de Bandera

1. Crea un nuevo sprite llamado `spr_flag`
2. Dibuja una bandera en un poste
3. Usa colores vivos (bandera verde, poste marrón)
4. Tamaño: 32x64 píxeles

![The Sprite Editor with spr_player open (32x48), origin centered; spr_player, spr_ground, spr_platform, spr_coin, spr_spike and spr_flag in the resource tree](images/tutorial-platformer-02-sprites.png)

---

## Paso 3: Crear el Objeto Suelo

El suelo es una plataforma sólida que impide que el jugador caiga.

1. Haz clic derecho en **Objects** y selecciona **Create Object**
2. Nómbralo `obj_ground`
3. Establece el sprite en `spr_ground`
4. **Marca la casilla "Solid"**
5. No se necesitan eventos

![obj_ground's Object Events panel: empty -- Solid checked is all it needs](images/tutorial-platformer-03-ground-object.png)

---

## Paso 4: Crear el Objeto Plataforma

Las plataformas funcionan como el suelo pero pueden colocarse en el aire.

1. Crea un nuevo objeto llamado `obj_platform`
2. Establece el sprite en `spr_platform`
3. **Marca la casilla "Solid"**
4. No se necesitan eventos

**Consejo:** puedes hacer que la plataforma sea hija de `obj_ground` para compartir el mismo comportamiento de colisión.

![obj_platform's Object Events panel: empty, with Solid checked -- a wide, thin sprite is the only difference from obj_ground](images/tutorial-platformer-04-platform-object.png)

---

## Paso 5: Crear el Objeto Jugador

El jugador es el objeto más complejo, con gravedad, salto y movimiento.

1. Crea un nuevo objeto llamado `obj_player`
2. Establece el sprite en `spr_player`

### 5.1 Gravedad

**Evento: Create** — Añade la acción **Move** → **Set Gravity**
(Direction: `270`, Gravity: `0.5`) — 270° es directamente hacia abajo;
el valor se suma a la velocidad vertical del jugador en cada paso, así
que el jugador acelera hacia abajo por sí solo a partir de aquí.

### 5.2 Movimiento, Salto y Colisión con el Suelo

Añade estos eventos, siguiendo el mismo patrón que ya usan los tutoriales
anteriores de este wiki:

| Evento | Acción |
|---|---|
| Keyboard (held) → Left Arrow | Set Horizontal Speed a `-4` |
| Keyboard (held) → Right Arrow | Set Horizontal Speed a `4` |
| Keyboard: No Key | Set Horizontal Speed a `0` |
| Key Press → Up Arrow | Set Vertical Speed a `-10` |
| Collision with obj_ground | Stop Movement |

Dos detalles que hacen que se sienta bien:

- **No Key solo pone a cero la velocidad horizontal** — nunca uses
  Stop Movement ahí, porque Stop Movement también pone a cero la
  velocidad vertical, lo que anularía la gravedad cada vez que el
  jugador suelta una tecla de dirección.
- **Key Press (no held)** es lo que hace que Up sea un único impulso de
  salto, en lugar de lanzar al jugador hacia arriba en cada fotograma
  en que se mantiene presionado. **Stop Movement** al aterrizar anula
  ese impulso, para que el jugador no siga subiendo tras aterrizar — la
  colisión sólida integrada del motor (el Paso 3 ya hizo `obj_ground`
  Solid) evita que el jugador se hunda en el suelo; el evento aquí solo
  limpia la velocidad de caída restante.

![obj_player's Object Events panel: Create (Set Gravity), Keyboard (held) with two Set Horizontal Speed actions, Keyboard <No Key>, Keyboard Press with the Up-Arrow jump, and Collision with obj_ground (Stop Movement)](images/tutorial-platformer-05-player-object.png)

---

## Paso 6: Crear el Objeto Moneda

Las monedas suman a la puntuación cuando se recogen.

1. Crea un nuevo objeto llamado `obj_coin`
2. Establece el sprite en `spr_coin`

**Evento: Collision with obj_player**
1. Añadir Evento → Collision → obj_player
2. Añade la acción **Score** → **Set Score**
   - New Score: `10`
   - Marca "Relative"
3. Añade la acción **Main1** → **Destroy Instance**
   - Applies to: Self

![obj_coin's Object Events panel: a Collision with obj_player event holding Set Score (Relative) and Destroy Instance](images/tutorial-platformer-06-coin-object.png)

---

## Paso 7: Crear el Objeto Pico

Los picos dañan al jugador y reinician el nivel.

1. Crea un nuevo objeto llamado `obj_spike`
2. Establece el sprite en `spr_spike`

**Evento: Collision with obj_player**
1. Añadir Evento → Collision → obj_player
2. Añade la acción **Main2** → **Show Message**
   - Message: `Ouch! You hit a spike!`
3. Añade la acción **Main1** → **Restart Room**

![obj_spike's Object Events panel: a Collision with obj_player event holding Show Message and Restart Room](images/tutorial-platformer-07-spike-object.png)

---

## Paso 8: Crear el Objeto Bandera

La bandera termina el nivel cuando el jugador la alcanza.

1. Crea un nuevo objeto llamado `obj_flag`
2. Establece el sprite en `spr_flag`

**Evento: Collision with obj_player**
1. Añadir Evento → Collision → obj_player
2. Añade la acción **Output** → **Show Message**
   - Message: `Level Complete!`
3. Añade la acción **Room** → **Next Room** (o **Restart Room** para un solo nivel)

El texto de Show Message es una cadena fija — no puede incrustar un valor
en vivo como la puntuación. El HUD del controlador de juego (Paso 9) ya
muestra la puntuación en pantalla durante todo el nivel, así que el
jugador ya la ha visto.

![obj_flag's Object Events panel: a Collision with obj_player event holding Show Message and Next Room](images/tutorial-platformer-08-flag-object.png)

---

## Paso 9: Crear el Controlador de Juego

El controlador de juego muestra la puntuación.

1. Crea un nuevo objeto llamado `obj_game_controller`
2. No se necesita sprite

**Evento: Draw**
1. Añadir Evento → Draw → Draw
2. Añade la acción **Draw** → **Draw Text** (Text: `Score:`, X: `10`, Y: `10`)
3. Añade la acción **Draw** → **Draw Variable** (Variable: `score`, X: `70`, Y: `10`)

Opcional: añade un par **Draw Text** (`Lives:`, X `10`, Y `30`) + **Draw
Variable** (`lives`, X `70`, Y `30`) de la misma manera, una vez que la
mejora Sistema de Vidas de abajo esté en su sitio.

![obj_game_controller's Object Events panel: a Draw event with one Draw Text and one Draw Variable action, with no sprite set](images/tutorial-platformer-09-controller-object.png)

---

## Paso 10: Diseñar Tu Nivel

1. Haz clic derecho en **Rooms** y selecciona **Create Room**
2. Nómbralo `room_level1`
3. Establece el tamaño de la room (p. ej. 800x480)
4. Activa "Snap to Grid" y ajusta la cuadrícula a 32x32

### Colocar los Objetos

Construye tu nivel siguiendo estas pautas:

1. **Crea el suelo** - Coloca `obj_ground` a lo largo de la parte inferior
2. **Añade plataformas** - Coloca `obj_platform` en el aire para desafíos de salto
3. **Añade huecos** - Deja espacios en el suelo (fosos)
4. **Coloca monedas** - Espárcelas por las plataformas y en lugares difíciles de alcanzar
5. **Añade picos** - Cerca de los fosos o sobre las plataformas para el desafío
6. **Coloca la bandera** - Al final del nivel
7. **Coloca al jugador** - Al principio (lado izquierdo)
8. **Añade el controlador de juego** - En cualquier parte (es invisible)

### Ejemplo de Diseño de Nivel

```
                                        F
                                      ===
                          C       C
                        =====   =====
            C                           C
          ===== X     X         X     =====
    P                   C
  ====== === ===   ===   === === ===== ======
  GGGGGG     GGG   GGG   GGG         GGGGGGGG

G = Suelo    P = Jugador    F = Bandera    C = Moneda
X = Pico    === = Plataforma
```

![The Room Editor for room_level1: a brown ground row with two pit gaps, four tan floating platforms at rising heights, gold coins on and above them, two grey spikes on the ground, the red player at the far left and the green flag at the far right](images/tutorial-platformer-10-room.png)

---

## Paso 11: ¡Prueba Tu Juego!

1. Haz clic en **Ejecutar** o pulsa **F5** para probar
2. Usa las flechas **Izquierda/Derecha** para moverte
3. Pulsa **Arriba** o **Espacio** para saltar
4. Recoge monedas para puntos
5. ¡Evita los picos!
6. ¡Alcanza la bandera para ganar!

---

## Mejoras (Opcional)

### Añadir Altura de Salto Variable

Añade un evento **Step** a `obj_player` con **Control** → **Execute Code**
(Python real — `self` es la instancia actual, `keyboard` te permite
comprobar una tecla mantenida por su nombre):

```python
# Corta el salto si se suelta Up mientras aún se sube
if self.vspeed < 0 and not keyboard.check('up'):
    self.vspeed = max(self.vspeed, -5)  # mitad del impulso de salto -10
```

### Añadir Doble Salto

Esto se puede hacer enteramente con acciones estructuradas — sin código.

**Evento: Create** — Añade la acción **Control** → **Set Variable**
(Variable: `jumps_left`, Value: `2`)

**Evento: Collision with obj_ground** — después de **Stop Movement**,
añade **Control** → **Set Variable** (Variable: `jumps_left`, Value: `2`)
para rellenar ambos saltos al aterrizar.

Reemplaza la única acción del evento **Key Press → Up Arrow** existente
por tres, en orden:
1. **Control** → **Test Variable** (Variable: `jumps_left`, Value: `0`,
   Operation: `greater`)
2. **Control** → **Start Block**
3. **Move** → **Set Vertical Speed** (`-10`)
4. **Control** → **Set Variable** (Variable: `jumps_left`, Value: `-1`,
   **Relative** marcado)
5. **Control** → **End Block**

El par Start/End Block significa que ambas acciones de dentro solo se
ejecutan cuando el Test Variable de encima es verdadero — el mismo patrón
de bloque protegido que los tutoriales de Sokoban y Laberinto usan para
sus propias condiciones.

### Añadir Plataformas Móviles

1. Crea `obj_moving_platform` como hija de `obj_platform`

**Evento: Create** — Añade la acción **Control** → **Execute Code**:

```python
self.start_x = self.x
self.hspeed = 2
```

**Evento: Step** — Añade la acción **Control** → **Execute Code**:

```python
if self.x > self.start_x + 100:
    self.hspeed = -2
elif self.x < self.start_x:
    self.hspeed = 2
```

### Añadir Enemigo

1. Crea `obj_enemy` con una IA simple

**Evento: Create** — Añade la acción **Move** → **Start Moving Direction**
(Directions: `right`, Speed: `2`)

**Evento: Collision with obj_ground** — Añade la acción **Move** →
**Reverse Horizontal** (da la vuelta en las paredes; combinado con que
`obj_ground` es Solid, el enemigo nunca puede salirse del borde de una
plataforma hacia el suelo de abajo ni atravesar una pared)

**Evento: Collision with obj_player** — este evento se dispara en
`obj_enemy`, así que `self` es el enemigo y `other` es el jugador. Añade
la acción **Control** → **Test Expression**, con acciones Then/Else
anidadas (el mismo patrón que el ejemplo incluido `plateforme_3` usa para
exactamente esta comprobación de "pisotón", solo que reflejado porque la
comprobación vive en el enemigo aquí en lugar del jugador):
   - Expression: `other.vspeed > 0 and other.y - other.vspeed < y - 16`
   - Then Actions: **Control** → **Execute Code** con `other.vspeed = -5`
     (un pequeño rebote para el jugador — `set_vspeed` no tiene opción
     "applies to other", así que este es el único sitio que necesita una
     línea de Python real en lugar de una acción estructurada), luego
     **Instance** → **Destroy Instance** (self)
   - Else Actions: **Room** → **Restart Room** (el jugador muere)

`other.vspeed > 0 and other.y - other.vspeed < y - 16` comprueba la
posición *del jugador* de antes del movimiento de caída de este fotograma
(usando el propio `vspeed` del jugador, ya que es él quien cae), de modo
que una caída rápida no puede atravesar la ventana de pisotón de 16 px en
un solo paso — consulta el README de `plateforme_3` para la historia
completa de por qué la versión ingenua `other.y < y - 16` es frágil.

### Añadir Sistema de Vidas

En el evento **Create** de `obj_game_controller`, añade **Score** → **Set
Lives** (Value: `3`).

Cuando el jugador muere (la colisión con el pico y la rama Else del
enemigo de arriba), reemplaza **Restart Room** por **Score** → **Set
Lives** (Value: `-1`, **Relative** marcado) — la room se reinicia
automáticamente porque el evento **No More Lives** solo se dispara una vez
que las vidas llegan realmente a 0. Añade ese evento a
`obj_game_controller`: **Other Events** → **No More Lives** → **Output** →
**Show Message** (`Game Over!`) → **Room** → **Restart Game**.

---

## Solución de Problemas

| Problema | Solución |
|----------|----------|
| El jugador cae a través del suelo | Comprueba que `obj_ground` tiene "Solid" marcado |
| El jugador no puede saltar | Verifica que el evento Key Press → Up Arrow existe y que Set Vertical Speed es negativo |
| El jugador sigue subiendo tras aterrizar | Asegúrate de que Collision with obj_ground tiene una acción Stop Movement |
| El salto se siente flotante | Aumenta el valor Gravity de Set Gravity, o haz el valor de salto de Set Vertical Speed más negativo |
| El salto se siente demasiado débil | Disminuye el valor Gravity de Set Gravity, o haz el valor de salto de Set Vertical Speed más negativo |

---

## Lo Que Aprendiste

¡Felicidades! ¡Has creado un juego de plataformas! Aprendiste:

- **Física de gravedad** - Set Gravity aplica una fuerza descendente constante en cada paso
- **Mecánicas de salto** - Un evento Key Press (no held) da un único impulso de velocidad hacia arriba
- **Colisión sólida integrada** - El suelo bloquea al jugador automáticamente una vez marcado Solid, sin código manual de comprobación de posición
- **Peligros** - Crear objetos que reinician el nivel
- **Diseño de niveles** - Construir desafíos de plataformas

---

## Ideas de Desafío

1. **Salto de Pared** - Permitir saltar desde las paredes
2. **Movimiento de Dash** - Un breve impulso horizontal de velocidad
3. **Plataformas que se Desmoronan** - Plataformas que caen tras pisarlas
4. **Puntos de Control** - Guardar el progreso a mitad de nivel
5. **Combate de Jefe** - Añadir un enemigo final con varios golpes

---

## Ver También

- [Tutoriales](Tutorials_es) - Más tutoriales de juegos
- [Preset Intermedio](Intermediate-Preset_es) - Resumen del preset que necesita la sección Mejoras
- [Tutorial: Laberinto](Tutorial-Maze_es) - Crear un juego de navegación por laberinto
- [Tutorial: Breakout](Tutorial-Breakout_es) - Crear un juego de rompe-ladrillos
- [Referencia de Eventos](Event-Reference_es) - Documentación completa de eventos
