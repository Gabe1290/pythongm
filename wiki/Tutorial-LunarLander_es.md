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
**Preset:** Preset Principiante

---

## Paso 1: Entender el Juego

### Mecánicas del Juego
1. El módulo es atraído hacia abajo por la gravedad
2. Presionar ARRIBA aplica impulso hacia arriba (usa combustible)
3. IZQUIERDA/DERECHA controla rotación o movimiento
4. Aterriza suavemente en la plataforma para ganar
5. Choque si aterrizas muy rápido o fallas la plataforma
6. ¡Sin combustible no puedes frenar!

### Lo Que Necesitamos

| Elemento | Propósito |
|----------|-----------|
| **Módulo** | La nave que controlas |
| **Plataforma** | Zona segura para aterrizar |
| **Suelo** | Terreno que causa choque |
| **Display Combustible** | Muestra combustible restante |
| **Display Velocidad** | Muestra velocidad actual |

---

## Paso 2: Crear los Sprites

### Sprites
- `spr_lander` (32x32 píxeles) - nave espacial simple
- `spr_pad` (64x16 píxeles) - plataforma de aterrizaje
- `spr_ground` (32x32 píxeles) - terreno rocoso
- `spr_flame` (16x16 píxeles) - llama de propulsión (opcional)

---

## Paso 3-4: Crear Objetos de Suelo y Plataforma

**obj_ground** y **obj_pad**: Establecer sprite, marcar "Sólido"

---

## Paso 5: Crear el Objeto Módulo

### Evento Create
```gml
gravity_force = 0.05;
thrust_force = 0.1;
max_speed = 5;
hsp = 0;
vsp = 0;
fuel = 100;
fuel_use = 0.5;
landed = false;
crashed = false;
safe_speed = 2;
```

### Evento Step
```gml
if (landed || crashed) exit;

vsp += gravity_force;

if (keyboard_check(vk_up) && fuel > 0) {
    vsp -= thrust_force;
    fuel -= fuel_use;
    if (fuel < 0) fuel = 0;
}

if (keyboard_check(vk_left)) hsp -= 0.05;
if (keyboard_check(vk_right)) hsp += 0.05;

hsp = clamp(hsp, -max_speed, max_speed);
vsp = clamp(vsp, -max_speed, max_speed);

x += hsp;
y += vsp;

if (x < 16) { x = 16; hsp = 0; }
if (x > room_width - 16) { x = room_width - 16; hsp = 0; }
if (y < 16) { y = 16; vsp = 0; }
```

### Colisión con obj_pad
```gml
var total_speed = sqrt(hsp*hsp + vsp*vsp);

if (total_speed <= safe_speed) {
    landed = true;
    hsp = 0;
    vsp = 0;
    show_message("¡Aterrizaje Perfecto! ¡Ganaste!");
} else {
    crashed = true;
    show_message("¡Choque! ¡Muy rápido!");
    room_restart();
}
```

### Colisión con obj_ground
```gml
crashed = true;
show_message("¡Choque contra el terreno!");
room_restart();
```

---

## Paso 6-7: Controlador del Juego

**obj_game_controller** - Evento Draw: Mostrar combustible, velocidad, instrucciones

---

## Paso 8: Diseña Tu Nivel

1. Crea `room_game` (640x480)
2. Fondo negro (espacio)
3. Coloca suelo abajo con una abertura
4. Coloca plataforma en la abertura
5. Coloca módulo arriba
6. Coloca controlador del juego

---

## Lo Que Aprendiste

- **Física de impulso** - Contrarrestar la gravedad
- **Gestión de velocidad** - Controlar la velocidad
- **Sistema de combustible** - Gestión de recursos
- **Detección de colisiones** - Diferentes resultados

---

## Ver También

- [Tutoriales](Tutorials_es) - Más tutoriales
- [Tutorial: Platformer](Tutorial-Platformer_es) - Crear un juego de plataformas

