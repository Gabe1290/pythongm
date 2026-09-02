# Movimiento

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Rebotar

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `bounce` |
| **Categoría** | Movimiento |

Rebotar en objetos sólidos

*Parámetros:* ninguno

### Saltar a posición

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `jump_to_position` |
| **Icono** | 📍 |
| **Categoría** | Movimiento |

Mover instantáneamente a una posición

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `relative` | Sí/No | No | Sumar a la posición actual en lugar de establecer una absoluta |

### Saltar a posición aleatoria

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `jump_to_random` |
| **Icono** | 🎲↪️ |
| **Categoría** | Movimiento |

Teletransportar a una posición aleatoria (opcionalmente ajustada a la cuadrícula)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `snap_h` | Número | `1` | Ajuste horizontal a la cuadrícula (1 = sin ajuste) |
| `snap_v` | Número | `1` | Ajuste vertical a la cuadrícula (1 = sin ajuste) |

### Saltar a la posición inicial

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `jump_to_start` |
| **Icono** | ↩️ |
| **Categoría** | Movimiento |

Devolver la instancia a su posición de creación

*Parámetros:* ninguno

### Movimiento libre

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `move_free` |
| **Icono** | 🧭 |
| **Categoría** | Movimiento |

Mover en una dirección precisa (0-360 grados)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `0` | Dirección en grados (0=derecha, 90=arriba, antihorario) |
| `speed` | Número | `4.0` | Velocidad de movimiento |

### Mover por cuadrícula

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `move_grid` |
| **Icono** | ▦ |
| **Categoría** | Movimiento |

Mover una celda de la cuadrícula en la dirección indicada

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Elección | `right` | Dirección de movimiento; Opciones: `left`, `right`, `up`, `down` |
| `grid_size` | Número | `32` | Tamaño de la celda de la cuadrícula en píxeles |

### Mover hacia un punto

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `move_towards_point` |
| **Icono** | 🎯 |
| **Categoría** | Movimiento |

Mover hacia un punto a una velocidad dada

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | X de destino |
| `y` | Número | `0` | Y de destino |
| `speed` | Número | `4.0` | Velocidad de movimiento |

### Mover hasta el contacto

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `move_to_contact` |
| **Icono** | 🎯 |
| **Categoría** | Movimiento |

Mover en una dirección hasta tocar un objeto (o la distancia máxima)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Texto | `direction` | Dirección en grados (0=derecha, 90=arriba, 180=izquierda, 270=abajo) o una expresión. Predeterminado «direction» = el rumbo actual de la instancia (ajuste a la colisión). |
| `max_distance` | Número | `1000` | Distancia máxima de movimiento, en píxeles |
| `object` | Objeto | `all` | Detenerse al contacto con: «all» todas las instancias, «solid» solo objetos sólidos, o un nombre de objeto específico.; Opciones: `all`, `solid`; opcional |

### Invertir horizontal

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `reverse_horizontal` |
| **Icono** | ↔️ |
| **Categoría** | Movimiento |

Invertir la dirección del movimiento horizontal

*Parámetros:* ninguno

### Invertir vertical

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `reverse_vertical` |
| **Icono** | ↕️ |
| **Categoría** | Movimiento |

Invertir la dirección del movimiento vertical

*Parámetros:* ninguno

### Establecer dirección

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_direction` |
| **Icono** | 🧭 |
| **Categoría** | Movimiento |

Establecer la dirección del movimiento

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `0` | Dirección en grados (0=derecha, 90=arriba) |

### Establecer dirección y velocidad

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_direction_speed` |
| **Icono** | 🧭 |
| **Categoría** | Movimiento |

Establecer la dirección (en grados) y la magnitud de velocidad de la instancia

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `0` | Dirección en grados (0=derecha, 90=arriba) |
| `speed` | Número | `4.0` | Velocidad en píxeles por fotograma |

### Establecer fricción

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_friction` |
| **Icono** | 🛑 |
| **Categoría** | Movimiento |

Establecer la fricción (desaceleración)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `friction` | Número | `0.1` | Cantidad de fricción (se resta de la velocidad en cada paso) |

### Establecer gravedad

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_gravity` |
| **Icono** | ⬇️ |
| **Categoría** | Movimiento |

Establecer la dirección y la fuerza de la gravedad

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `270` | Dirección de la gravedad en grados (270=abajo) |
| `gravity` | Número | `0.5` | Fuerza de la gravedad (se añade en cada paso) |

### Establecer velocidad horizontal

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_hspeed` |
| **Icono** | ↔️ |
| **Categoría** | Movimiento |

Establecer la velocidad de movimiento horizontal

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0` | Velocidad en píxeles por fotograma |

### Establecer velocidad

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_speed` |
| **Icono** | ⚡ |
| **Categoría** | Movimiento |

Establecer la velocidad de movimiento (magnitud)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0` | Velocidad de movimiento |

### Establecer velocidad vertical

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_vspeed` |
| **Icono** | ↕️ |
| **Categoría** | Movimiento |

Establecer la velocidad de movimiento vertical

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0` | Velocidad en píxeles por fotograma |

### Empezar a moverse (dirección)

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `start_moving_direction` |
| **Icono** | ➡️ |
| **Categoría** | Movimiento |

Empezar a moverse en una dirección a una velocidad dada

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `directions` | Elección múltiple | right | Dirección(es) de movimiento — marca una, o varias para elegir una al azar en cada paso. La celda central es detenerse.; Opciones: `up-left`, `up`, `up-right`, `left`, `stop`, `right`, `down-left`, `down`, `down-right` |
| `direction_expr` | Texto | — | Alternativa: expresión libre evaluada como grados; opcional |
| `speed` | Número | `4.0` | Velocidad en píxeles por fotograma |

### Detener movimiento

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stop_movement` |
| **Icono** | 🛑 |
| **Categoría** | Movimiento |

Poner ambas velocidades a cero

*Parámetros:* ninguno

### Envolver alrededor de la sala

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `wrap_around_room` |
| **Icono** | 🔄 |
| **Categoría** | Movimiento |

Reaparecer en el lado opuesto de la sala

*Parámetros:* ninguno

---

## Otras Categorías

- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (8)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (25)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (16)
- [Particles](Full-Action-Reference-Particles_es) (8)
- [Réseau](Full-Action-Reference-Network-Actions_es) (15)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
