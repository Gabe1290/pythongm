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

## Paso 3-4: Crear Objetos de Suelo y Plataforma

**obj_ground** y **obj_platform**: Establece sprite, marca "Sólido"

---

## Paso 5: Crear el Objeto Jugador

### Evento Create
```gml
hspeed_max = 4;
vspeed_max = 10;
jump_force = -10;
gravity_force = 0.5;
hsp = 0;
vsp = 0;
on_ground = false;
```

### Evento Step
```gml
var move_input = keyboard_check(vk_right) - keyboard_check(vk_left);
hsp = move_input * hspeed_max;

vsp += gravity_force;
if (vsp > vspeed_max) vsp = vspeed_max;

on_ground = place_meeting(x, y + 1, obj_ground);

if (on_ground && (keyboard_check_pressed(vk_up) || keyboard_check_pressed(vk_space))) {
    vsp = jump_force;
}

if (place_meeting(x + hsp, y, obj_ground)) {
    while (!place_meeting(x + sign(hsp), y, obj_ground)) x += sign(hsp);
    hsp = 0;
}
x += hsp;

if (place_meeting(x, y + vsp, obj_ground)) {
    while (!place_meeting(x, y + sign(vsp), obj_ground)) y += sign(vsp);
    vsp = 0;
}
y += vsp;
```

---

## Paso 6-8: Coleccionables y Peligros

**obj_coin** - Colisión con obj_player: Puntuación +10, destruir Self

**obj_spike** - Colisión con obj_player: Mostrar mensaje, reiniciar room

**obj_flag** - Colisión con obj_player: Mostrar mensaje, siguiente room

---

## Paso 9: Diseñar Tu Nivel

1. Crea `room_level1` (800x480)
2. Activa ajuste a cuadrícula (32x32)
3. Coloca suelo abajo, plataformas en el aire
4. Añade monedas, picos
5. Pon bandera al final, jugador al inicio

---

## Lo Que Aprendiste

- **Física de gravedad** - Fuerza constante hacia abajo
- **Mecánicas de salto** - Velocidad vertical negativa
- **Detección del suelo** - Usar `place_meeting`
- **Manejo de colisiones** - Mover píxel por píxel

---

## Ver También

- [Tutoriales](Tutorials_es) - Más tutoriales de juegos
- [Tutorial: Laberinto](Tutorial-Maze_es) - Crear un juego de laberinto
