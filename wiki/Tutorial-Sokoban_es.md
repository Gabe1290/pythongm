# Tutorial: Crear un Juego de Rompecabezas Sokoban

> **Selecciona tu idioma / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Sokoban) | [Français](Tutorial-Sokoban_fr) | [Deutsch](Tutorial-Sokoban_de) | [Italiano](Tutorial-Sokoban_it) | [Español](Tutorial-Sokoban_es) | [Português](Tutorial-Sokoban_pt) | [Slovenščina](Tutorial-Sokoban_sl) | [Українська](Tutorial-Sokoban_uk) | [Русский](Tutorial-Sokoban_ru)

---

## Introducción

En este tutorial, crearás un juego de rompecabezas **Sokoban** - un clásico juego donde el jugador debe empujar todas las cajas a ubicaciones objetivo. Sokoban (que significa "guardián del almacén" en japonés) es perfecto para aprender movimiento basado en cuadrículas y lógica de juegos de rompecabezas.

**Lo que aprenderás:**
- Movimiento basado en cuadrículas (movimiento en pasos fijos)
- Mecánicas de empuje para mover objetos
- Detección de colisiones con múltiples tipos de objetos
- Detección de condición de victoria
- Diseño de niveles para juegos de rompecabezas

**Dificultad:** Principiante
**Preset:** Preset Intermedio (la mecánica de empuje y el movimiento
basado en cuadrículas usados aquí no están en el preset Principiante)

---

## Paso 1: Entender el Juego

### Reglas del Juego
1. El jugador puede moverse hacia arriba, abajo, izquierda o derecha
2. El jugador puede empujar cajas (pero no tirar de ellas)
3. Solo se puede empujar una caja a la vez
4. Las cajas no pueden ser empujadas a través de paredes u otras cajas
5. El nivel se completa cuando todas las cajas están en lugares objetivo

### Lo que Necesitamos

| Elemento | Propósito |
|---------|---------|
| **Jugador** | El guardián del almacén que controlas |
| **Caja** | Cajas que el jugador empuja |
| **Pared** | Obstáculos sólidos que bloquean el movimiento |
| **Objetivo** | Lugares objetivo donde las cajas deben colocarse |
| **Piso** | Terreno transitable (visual opcional) |

---

## Paso 2: Crear los Sprites

Todos los sprites deben tener el mismo tamaño (32x32 píxeles funciona bien) para crear una cuadrícula adecuada.

### 2.1 Sprite del Jugador

1. En el **Árbol de Recursos**, haz clic derecho en **Sprites** y selecciona **Create Sprite**
2. Nómbralo `spr_player`
3. Haz clic en **Edit Sprite** para abrir el editor de sprites
4. Dibuja un personaje simple (una forma de persona o robot)
5. Usa un color distintivo como azul o verde
6. Tamaño: 32x32 píxeles
7. Haz clic en **OK** para guardar

### 2.2 Sprite de Caja

1. Crea un nuevo sprite llamado `spr_crate`
2. Dibuja una caja de madera o forma de caja
3. Usa colores marrón o naranja
4. Tamaño: 32x32 píxeles

### 2.3 Sprite de Caja en Objetivo

1. Crea un nuevo sprite llamado `spr_crate_ok`
2. Dibuja la misma caja pero con un color diferente (verde) para mostrar que está correctamente colocada
3. Tamaño: 32x32 píxeles

### 2.4 Sprite de Pared

1. Crea un nuevo sprite llamado `spr_wall`
2. Dibuja un patrón de ladrillo sólido o piedra
3. Usa colores gris o oscuro
4. Tamaño: 32x32 píxeles

### 2.5 Sprite Objetivo

1. Crea un nuevo sprite llamado `spr_target`
2. Dibuja una marca X o un indicador de objetivo
3. Usa un color brillante como rojo o amarillo
4. Tamaño: 32x32 píxeles

### 2.6 Sprite de Piso (Opcional)

1. Crea un nuevo sprite llamado `spr_floor`
2. Dibuja un patrón de baldosa de piso simple
3. Usa un color neutral
4. Tamaño: 32x32 píxeles

---

## Paso 3: Crear el Objeto Pared

La pared es el objeto más simple - simplemente bloquea el movimiento.

1. Haz clic derecho en **Objects** y selecciona **Create Object**
2. Nómbralo `obj_wall`
3. Establece el sprite en `spr_wall`
4. **Marca la casilla "Solid"**
5. No se necesitan eventos

---

## Paso 4: Crear el Objeto Objetivo

Los objetivos marcan dónde deben colocarse las cajas.

1. Crea un nuevo objeto llamado `obj_target`
2. Establece el sprite en `spr_target`
3. No se necesitan eventos - es solo un marcador
4. Deja "Solid" sin marcar (el jugador y las cajas pueden estar encima)

---

## Paso 5: Crear el Objeto Caja

La caja es empujada por el jugador y cambia de apariencia cuando está en un objetivo.

1. Crea un nuevo objeto llamado `obj_crate`
2. Establece el sprite en `spr_crate`
3. **Marca la casilla "Solid"**

**Evento: Step**
1. Add Event → Step → Step
2. Add Action: **Control** → **If Collision**
   - X Offset: `0`
   - Y Offset: `0`
   - Against: `obj_target`
3. Add Action: **Instance** → **Set Sprite**
   - Sprite: `spr_crate_ok`
4. Add Action: **Control** → **Else**
5. Add Action: **Instance** → **Set Sprite**
   - Sprite: `spr_crate`

Esto hace que la caja se vuelva verde cuando está en un lugar objetivo —
**If Collision** con ambos desplazamientos en `0` comprueba si la
posición *actual* de la caja se superpone con un `obj_target`.

---

## Paso 6: Crear el Objeto Jugador

El jugador se mueve exactamente una celda de la cuadrícula a la vez y empuja las cajas contra las que se topa.

1. Crea un nuevo objeto llamado `obj_player`
2. Establece el sprite en `spr_player`

### 6.1 Movimiento en Cuadrícula

Agrega un evento **Key Press** por dirección, cada uno con una acción **Move** → **Move Grid**:

| Evento | Acción Move Grid |
|---|---|
| Key Press → Right Arrow | Direction: `right`, Grid Size: `32` |
| Key Press → Left Arrow | Direction: `left`, Grid Size: `32` |
| Key Press → Up Arrow | Direction: `up`, Grid Size: `32` |
| Key Press → Down Arrow | Direction: `down`, Grid Size: `32` |

**Move Grid** mueve la instancia exactamente una celda de la cuadrícula
y ya detecta colisiones por sí sola — no moverá al jugador hacia un
`obj_wall` sólido, por lo que no hace falta una comprobación de pared
adicional aquí.

### 6.2 Detenerse en las Paredes

**Evento: Collision with obj_wall**
1. Add Event → Collision → `obj_wall`
2. Add Action: **Move** → **Stop Movement**

### 6.3 Empujar Cajas

**Evento: Collision with obj_crate**
1. Add Event → Collision → `obj_crate`
2. Add Action: **Control** → **If Can Push**
   - Direction: `facing`
   - Object Type: `obj_crate`
   - Then Action: `push_and_move`

**If Can Push** comprueba si el espacio detrás de la caja (en la
dirección en la que se mueve el jugador) está libre y, si es así,
empuja la caja una celda y mueve al jugador a su lugar, todo en una
sola acción. Si el espacio detrás de la caja está bloqueado por una
pared u otra caja, nada se mueve.

---

## Paso 7: Crear el Verificador de Condición de Victoria

Necesitamos un controlador invisible que observe si cada caja está en un objetivo.

1. Crea un nuevo objeto llamado `obj_game_controller`
2. No se necesita sprite

**Evento: Create** — establece el conteo de objetivos una sola vez,
usando **Control** → **Execute Code** (la acción Execute Code de este
proyecto ejecuta Python real, no GameMaker Language — `self` es la
instancia actual, `game` es el gestor del juego):

```python
# Cuenta cuántos objetivos existen en la sala
self.total_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_target'
)
```

**Evento: Step** — comprueba cada fotograma si todas las cajas están en un objetivo:

```python
# Cuenta las cajas que actualmente se superponen con un objetivo
crates_on_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_crate'
    and game.check_collision_at_position(inst, inst.x, inst.y, 'obj_target')
)

if self.total_targets > 0 and crates_on_targets >= self.total_targets:
    self.restart_room_flag = True
```

`self.restart_room_flag = True` es la forma en que un bloque Execute
Code crudo activa el mismo reinicio de sala que realiza la acción
**Restart Room** — el bucle principal lo comprueba cada fotograma.
Agrega una acción **Show Message** (de **Output**, mensaje `Level
Complete!`) justo después del bloque Execute Code si quieres mostrar un
popup antes del reinicio.

**Evento: Draw**
1. Add Event → Draw
2. Add Action: **Draw** → **Draw Text**
   - Text: `Sokoban - Push all crates to targets!`
   - X: `10`
   - Y: `10`

---

## Paso 9: Diseña Tu Nivel

1. Haz clic derecho en **Rooms** y selecciona **Create Room**
2. Nómbrala `room_level1`
3. Establece el tamaño de la sala en un múltiplo de 32 (por ejemplo, 640x480)
4. Habilita "Snap to Grid" y establece la cuadrícula en 32x32

### Colocación de Objetos

Construye tu nivel siguiendo estas directrices:

1. **Rodea el nivel con paredes** - Crea un borde
2. **Agrega paredes internas** - Crea la estructura del rompecabezas
3. **Coloca objetivos** - Dónde las cajas necesitan ir
4. **Coloca cajas** - ¡El mismo número que objetivos!
5. **Coloca el jugador** - Posición inicial
6. **Coloca el game controller** - En cualquier lugar (es invisible)

### Ejemplo de Diseño de Nivel

```
W W W W W W W W W W
W . . . . . . . . W
W . P . . . C . . W
W . . W W . . . . W
W . . W T . . C . W
W . . . . . W W . W
W . T . . . . . . W
W . . . . . . . . W
W W W W W W W W W W

W = Pared
P = Jugador
C = Caja
T = Objetivo
. = Piso vacío
```

**Importante:** ¡Siempre ten el mismo número de cajas y objetivos!

---

## Paso 10: ¡Prueba Tu Juego!

1. Haz clic en **Run** o presiona **F5** para probar
2. Usa las flechas del teclado para moverte
3. Empuja las cajas hacia los objetivos rojo X
4. ¡Cuando todas las cajas están en objetivos, ganas!

---

## Mejoras (Opcional)

### Agregar un Contador de Movimientos

En el evento **Create** de `obj_game_controller`, agrega **Control** →
**Set Variable** (Variable: `global.moves`, Value: `0`, Scope: `global`).

En cada uno de los cuatro eventos Key Press de `obj_player`, agrega una
segunda acción justo después de Move Grid: **Control** → **Set
Variable** (Variable: `global.moves`, Value: `1`, Scope: `global`,
**Relative** marcado) — esto suma 1 al contador en cada pulsación de
tecla, sin importar si el movimiento fue realmente bloqueado por una
pared.

En el evento **Draw** de `obj_game_controller`, agrega **Draw** →
**Draw Variable** (Variable: `global.moves`, X: `10`, Y: `30`).

### Agregar Función Deshacer

Almacena posiciones anteriores y permite presionar Z para deshacer el último movimiento.

### Agregar Múltiples Niveles

Crea más salas (`room_level2`, `room_level3`, etc.) y usa la acción
**Next Room** (categoría Room) en lugar de **Restart Room** en el
bloque Execute Code de comprobación de victoria (`self.next_room_flag =
True` en lugar de `self.restart_room_flag = True`) al completar un
nivel.

### Agregar Efectos de Sonido

Agrega sonidos para:
- Movimiento del jugador
- Empujar una caja
- Caja aterrizando en un objetivo
- Nivel completado

---

## Solución de Problemas

| Problema | Solución |
|---------|----------|
| El jugador se mueve a través de paredes | Verifica que `obj_wall` tenga "Solid" marcado |
| La caja no cambia de color | Verifica que la acción **If Collision** del evento Step apunte a `obj_target` |
| Puedes empujar una caja a través de la pared | Verifica la detección de colisiones antes de mover la caja |
| El mensaje de victoria aparece inmediatamente | Asegúrate de que los objetivos se coloquen separados de las cajas |
| El jugador se mueve varias casillas | Usa el evento Keyboard Press, no el evento Keyboard |

---

## Lo que Aprendiste

¡Felicidades! ¡Has creado un juego de rompecabezas Sokoban completo! Aprendiste:

- **Movimiento basado en cuadrículas** - Movimiento en pasos fijos de 32 píxeles
- **Mecánicas de empuje** - Detectar y mover objetos que el jugador empuja
- **Lógica de colisión compleja** - Verificar múltiples condiciones antes de permitir movimiento
- **Cambios de estado** - Cambiar sprite basado en la posición del objeto
- **Condiciones de victoria** - Verificar cuándo se completan todos los objetivos
- **Diseño de niveles** - Crear diseños de rompecabezas solubles

---

## Desafío: ¡Diseña Tus Propios Niveles!

La verdadera diversión de Sokoban es diseñar rompecabezas. Intenta crear niveles que:
- Comiencen fácil y se vuelvan progresivamente más difíciles
- Requieran planificación anticipada
- Tengan solo una solución
- Usen el espacio mínimo de manera eficiente

Recuerda: ¡Un buen rompecabezas de Sokoban debe ser desafiante pero justo!

---

## Ver También

- [Tutoriales](Tutorials_es) - Más tutoriales de juegos
- [Preset Intermedio](Intermediate-Preset_es) - Descripción general del preset que necesita este tutorial
- [Tutorial: Pong](Tutorial-Pong_es) - Crear un juego multijugador
- [Tutorial: Breakout](Tutorial-Breakout_es) - Crear un juego de rompimiento de ladrillos
- [Referencia de Eventos](Event-Reference_es) - Documentación completa de eventos
