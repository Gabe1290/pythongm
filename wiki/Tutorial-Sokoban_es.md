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
**Preset:** Preset para Principiantes

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

1. En el **Árbol de Recursos**, haz clic derecho en **Sprites** y selecciona **Crear Sprite**
2. Nómbralo `spr_player`
3. Haz clic en **Editar Sprite** para abrir el editor de sprites
4. Dibuja un personaje simple (una forma de persona o robot)
5. Usa un color distintivo como azul o verde
6. Tamaño: 32x32 píxeles
7. Haz clic en **Aceptar** para guardar

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

1. Haz clic derecho en **Objetos** y selecciona **Crear Objeto**
2. Nómbralo `obj_wall`
3. Establece el sprite en `spr_wall`
4. **Marca la casilla "Sólido"**
5. No se necesitan eventos

---

## Paso 4: Crear el Objeto Objetivo

Los objetivos marcan dónde deben colocarse las cajas.

1. Crea un nuevo objeto llamado `obj_target`
2. Establece el sprite en `spr_target`
3. No se necesitan eventos - es solo un marcador
4. Deja "Sólido" sin marcar (el jugador y las cajas pueden estar encima)

---

## Paso 5: Crear el Objeto Caja

La caja es empujada por el jugador y cambia de apariencia cuando está en un objetivo.

1. Crea un nuevo objeto llamado `obj_crate`
2. Establece el sprite en `spr_crate`
3. **Marca la casilla "Sólido"**

**Evento: Step**
1. Agregar Evento → Step → Step
2. Agregar Acción: **Control** → **Prueba Variable**
   - Variable: `place_meeting(x, y, obj_target)`
   - Valor: `1`
   - Operación: Igual a
3. Agregar Acción: **Main1** → **Cambiar Sprite**
   - Sprite: `spr_crate_ok`
   - Subimagen: `0`
   - Velocidad: `1`
4. Agregar Acción: **Control** → **Si No**
5. Agregar Acción: **Main1** → **Cambiar Sprite**
   - Sprite: `spr_crate`
   - Subimagen: `0`
   - Velocidad: `1`

Esto hace que la caja se vuelva verde cuando está en un lugar objetivo.

---

## Paso 6: Crear el Objeto Jugador

El jugador es el objeto más complejo con movimiento basado en cuadrículas y mecánicas de empuje.

1. Crea un nuevo objeto llamado `obj_player`
2. Establece el sprite en `spr_player`

### 6.1 Movimiento a la Derecha

**Evento: Teclado Presionar Flecha Derecha**
1. Agregar Evento → Teclado → Presionar Derecha

Primero, comprueba si hay una pared en el camino:
2. Agregar Acción: **Control** → **Prueba Colisión**
   - Objeto: `obj_wall`
   - X: `32`
   - Y: `0`
   - Verificar: NO (significa "si NO hay pared")

Si no hay pared, comprueba si hay una caja:
3. Agregar Acción: **Control** → **Prueba Colisión**
   - Objeto: `obj_crate`
   - X: `32`
   - Y: `0`

Si hay una caja, necesitamos comprobar si podemos empujarla:
4. Agregar Acción: **Control** → **Prueba Colisión** (para el destino de la caja)
   - Objeto: `obj_wall`
   - X: `64`
   - Y: `0`
   - Verificar: NO

5. Agregar Acción: **Control** → **Prueba Colisión**
   - Objeto: `obj_crate`
   - X: `64`
   - Y: `0`
   - Verificar: NO

Si ambas comprobaciones pasan, empuja la caja:
6. Agregar Acción: **Control** → **Bloque de Código**
```
var crate = instance_place(x + 32, y, obj_crate);
if (crate != noone) {
    crate.x += 32;
}
```

Ahora mueve el jugador:
7. Agregar Acción: **Mover** → **Saltar a Posición**
   - X: `32`
   - Y: `0`
   - Marca "Relativo"

### 6.2 Movimiento a la Izquierda

**Evento: Teclado Presionar Flecha Izquierda**
Sigue el mismo patrón que el movimiento a la derecha, pero usa:
- Desplazamiento X: `-32` para verificar pared/caja
- Desplazamiento X: `-64` para verificar si la caja puede ser empujada
- Mover caja por `-32`
- Saltar a posición X: `-32`

### 6.3 Movimiento Hacia Arriba

**Evento: Teclado Presionar Flecha Arriba**
Sigue el mismo patrón, pero usa valores Y:
- Desplazamiento Y: `-32` para verificar
- Desplazamiento Y: `-64` para destino de caja
- Mover caja por Y: `-32`
- Saltar a posición Y: `-32`

### 6.4 Movimiento Hacia Abajo

**Evento: Teclado Presionar Flecha Abajo**
Usa:
- Desplazamiento Y: `32` para verificar
- Desplazamiento Y: `64` para destino de caja
- Mover caja por Y: `32`
- Saltar a posición Y: `32`

---

## Paso 7: Movimiento de Jugador Simplificado (Alternativa)

Si el enfoque basado en bloques anterior parece complejo, aquí hay un enfoque más simple basado en código para cada dirección:

**Evento: Teclado Presionar Flecha Derecha**
Agregar Acción: **Control** → **Ejecutar Código**
```
// Check if we can move right
if (!place_meeting(x + 32, y, obj_wall)) {
    // Check if there's a crate
    var crate = instance_place(x + 32, y, obj_crate);
    if (crate != noone) {
        // There's a crate - can we push it?
        if (!place_meeting(x + 64, y, obj_wall) && !place_meeting(x + 64, y, obj_crate)) {
            crate.x += 32;
            x += 32;
        }
    } else {
        // No crate, just move
        x += 32;
    }
}
```

Repite para otras direcciones con cambios de coordenadas apropiados.

---

## Paso 8: Crear el Verificador de Condición de Victoria

Necesitamos un objeto para comprobar si todas las cajas están en objetivos.

1. Crea un nuevo objeto llamado `obj_game_controller`
2. No se necesita sprite

**Evento: Crear**
1. Agregar Evento → Crear
2. Agregar Acción: **Puntuación** → **Establecer Variable**
   - Variable: `global.total_targets`
   - Valor: `0`
3. Agregar Acción: **Control** → **Ejecutar Código**
```
// Count how many targets exist
global.total_targets = instance_number(obj_target);
```

**Evento: Step**
1. Agregar Evento → Step → Step
2. Agregar Acción: **Control** → **Ejecutar Código**
```
// Count crates that are on targets
var crates_on_targets = 0;
with (obj_crate) {
    if (place_meeting(x, y, obj_target)) {
        crates_on_targets += 1;
    }
}

// Check if all targets have crates
if (crates_on_targets >= global.total_targets && global.total_targets > 0) {
    // Level complete!
    show_message("Level Complete!");
    room_restart();
}
```

**Evento: Dibujar**
1. Agregar Evento → Dibujar
2. Agregar Acción: **Dibujar** → **Dibujar Texto**
   - Texto: `Sokoban - ¡Empuja todas las cajas a los objetivos!`
   - X: `10`
   - Y: `10`

---

## Paso 9: Diseña Tu Nivel

1. Haz clic derecho en **Habitaciones** y selecciona **Crear Habitación**
2. Nómbrala `room_level1`
3. Establece el tamaño de la habitación en un múltiplo de 32 (por ejemplo, 640x480)
4. Habilita "Ajustar a Cuadrícula" y establece la cuadrícula en 32x32

### Colocación de Objetos

Construye tu nivel siguiendo estas directrices:

1. **Rodea el nivel con paredes** - Crea un borde
2. **Agrega paredes internas** - Crea la estructura del rompecabezas
3. **Coloca objetivos** - Dónde las cajas necesitan ir
4. **Coloca cajas** - ¡El mismo número que objetivos!
5. **Coloca el jugador** - Posición inicial
6. **Coloca el controlador del juego** - En cualquier lugar (es invisible)

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

1. Haz clic en **Ejecutar** o presiona **F5** para probar
2. Usa las flechas del teclado para moverte
3. Empuja las cajas hacia los objetivos rojo X
4. ¡Cuando todas las cajas están en objetivos, ¡ganas!

---

## Mejoras (Opcional)

### Agregar un Contador de Movimientos

En `obj_game_controller`:

**Evento: Crear** - Agrega:
```
global.moves = 0;
```

En `obj_player`, después de cada movimiento exitoso, agrega:
```
global.moves += 1;
```

En `obj_game_controller` **Evento: Dibujar** - Agrega:
```
draw_text(10, 30, "Moves: " + string(global.moves));
```

### Agregar Función Deshacer

Almacena posiciones anteriores y permite presionar Z para deshacer el último movimiento.

### Agregar Múltiples Niveles

Crea más habitaciones (`room_level2`, `room_level3`, etc.) y usa:
```
room_goto_next();
```
en lugar de `room_restart()` al completar un nivel.

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
| El jugador se mueve a través de paredes | Verifica que `obj_wall` tenga "Sólido" marcado |
| La caja no cambia de color | Verifica que el evento Step compruebe `place_meeting` correctamente |
| Puedes empujar una caja a través de la pared | Verifica la detección de colisiones antes de mover la caja |
| El mensaje de victoria aparece inmediatamente | Asegúrate de que los objetivos se coloquen separados de las cajas |
| El jugador se mueve múltiples cuadrados | Usa evento Teclado Presionar, no evento Teclado |

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

- [Tutoriales](Tutorials) - Más tutoriales de juegos
- [Preset para Principiantes](Beginner-Preset) - Descripción general de características para principiantes
- [Tutorial: Pong](Tutorial-Pong_es) - Crear un juego multijugador
- [Tutorial: Breakout](Tutorial-Breakout_es) - Crear un juego de rompimiento de ladrillos
- [Referencia de Eventos](Event-Reference) - Documentación completa de eventos
