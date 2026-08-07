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
**Preset:** Preset Principiante

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
- Nombre: `spr_player`
- Dibuja un personaje simple
- Tamaño: 32x48 píxeles

### 2.2 Sprite del Suelo
- Nombre: `spr_ground`
- Dibuja una baldosa de hierba/tierra
- Tamaño: 32x32 píxeles

### 2.3 Sprite de Plataforma
- Nombre: `spr_platform`
- Dibuja una plataforma flotante
- Tamaño: 64x16 píxeles

### 2.4 Sprite de Moneda
- Nombre: `spr_coin`
- Círculo amarillo/dorado pequeño
- Tamaño: 16x16 píxeles

### 2.5 Sprite de Pico
- Nombre: `spr_spike`
- Triángulos apuntando hacia arriba
- Tamaño: 32x32 píxeles

### 2.6 Sprite de Bandera
- Nombre: `spr_flag`
- Bandera en un poste
- Tamaño: 32x64 píxeles

---

## Paso 3: Crear el Objeto Suelo

El suelo es una plataforma sólida que impide que el jugador caiga.

1. Haz clic derecho en **Objects** y selecciona **Create Object**
2. Nómbralo `obj_ground`
3. Establece el sprite en `spr_ground`
4. **Marca la casilla "Solid"**
5. No se necesitan eventos

---

## Paso 4: Crear el Objeto Plataforma

Las plataformas funcionan como el suelo pero pueden colocarse en el aire.

1. Crea un nuevo objeto llamado `obj_platform`
2. Establece el sprite en `spr_platform`
3. **Marca la casilla "Solid"**

---

## Paso 5: Crear el Objeto Jugador

El jugador es el objeto más complejo, con gravedad, salto y movimiento.

1. Crea un nuevo objeto llamado `obj_player`
2. Establece el sprite en `spr_player`

### 5.1 Gravedad

**Evento: Create** — Add Action: **Move** → **Set Gravity**
(Direction: `270`, Gravity: `0.5`) — 270° es directamente hacia abajo;
el valor se suma a la velocidad vertical del jugador en cada fotograma,
así que el jugador acelera hacia abajo por sí solo a partir de aquí.

### 5.2 Movimiento, Salto y Colisión con el Suelo

Agrega estos eventos, siguiendo el mismo patrón que ya usan los
tutoriales anteriores de este wiki:

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

---

## Paso 6-8: Coleccionables y Peligros

**obj_coin** - Colisión con obj_player: Puntuación +10, destruir Self

**obj_spike** - Colisión con obj_player: Mostrar mensaje, reiniciar la sala

**obj_flag** - Colisión con obj_player: Mostrar mensaje, siguiente sala

---

## Paso 9: Diseñar Tu Nivel

1. Crea `room_level1` (800x480)
2. Activa ajuste a cuadrícula (32x32)
3. Coloca suelo abajo, plataformas en el aire
4. Añade monedas, picos
5. Pon bandera al final, jugador al inicio

---

## Lo Que Aprendiste

- **Física de gravedad** - Set Gravity aplica una fuerza constante hacia abajo en cada fotograma
- **Mecánicas de salto** - Un evento Key Press (no held) da un único impulso de velocidad hacia arriba
- **Colisión sólida integrada** - El suelo bloquea al jugador automáticamente una vez marcado como Solid, sin código manual de comprobación de posición

---

## Ver También

- [Tutoriales](Tutorials_es) - Más tutoriales de juegos
- [Tutorial: Laberinto](Tutorial-Maze_es) - Crear un juego de laberinto
