# Partículas

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Lanzar partículas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `burst_particles` |
| **Icono** | 💥 |
| **Categoría** | Partículas |

Lanza una ráfaga única de partículas desde el emisor creado más recientemente

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `particle_type` | Número | `0` | Particle type id (from Create Particle Type) |
| `number` | Número | `10` | Number of particles to emit |

### Borrar partículas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `clear_particles` |
| **Icono** | 🧹 |
| **Categoría** | Partículas |

Elimina todas las partículas activas, pero conserva los tipos de partícula y los emisores

*Parámetros:* ninguno

### Crear emisor

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_emitter` |
| **Icono** | 🌀 |
| **Categoría** | Partículas |

Crea una zona emisora de partículas (el identificador devuelto se guarda para la siguiente acción que use un emisor)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Emitter center X (room coordinates) |
| `y` | Número | `0` | Emitter center Y (room coordinates) |
| `width` | Número | `0` | Emitter area width |
| `height` | Número | `0` | Emitter area height |
| `shape` | Elección | `rectangle` | Shape of the emitter area particles spawn within; Opciones: `rectangle`, `ellipse`, `diamond`, `line` |

### Crear sistema de partículas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_particle_system` |
| **Icono** | ✨ |
| **Categoría** | Partículas |

Crea un sistema de partículas asociado a esta instancia (sustituye cualquier otro existente)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `depth` | Número | `0` | Drawing depth for the particle system (not yet used for cross-instance sort order) |

### Crear tipo de partícula

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_particle_type` |
| **Icono** | ⚙️ |
| **Categoría** | Partículas |

Define una nueva apariencia o comportamiento de partícula (el identificador de tipo devuelto se guarda para la siguiente acción que use un tipo de partícula)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite to draw each particle as; leave empty for a plain colored circle; opcional |
| `size_min` | Número | `1.0` | Minimum particle size (scale factor) |
| `size_max` | Número | `1.0` | Maximum particle size (scale factor) |
| `size_increase` | Número | `0.0` | Size change per step (negative shrinks, floored at 0) |
| `color` | Color | `#FFFFFF` | Particle color (used when no sprite is set) |
| `alpha` | Número | `1.0` | Transparency (0=invisible, 1=opaque) |
| `speed_min` | Número | `0.0` | Minimum movement speed |
| `speed_max` | Número | `0.0` | Maximum movement speed |
| `direction_min` | Número | `0` | Minimum direction angle (0=right, 90=up) |
| `direction_max` | Número | `360` | Maximum direction angle |
| `life_min` | Número | `100` | Minimum lifetime in steps |
| `life_max` | Número | `100` | Maximum lifetime in steps |

### Destruir emisor

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `destroy_emitter` |
| **Icono** | 💥 |
| **Categoría** | Partículas |

Destruye el emisor creado más recientemente

*Parámetros:* ninguno

### Destruir sistema de partículas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `destroy_particle_system` |
| **Icono** | 💥 |
| **Categoría** | Partículas |

Elimina el sistema de partículas de esta instancia, borrando todas sus partículas y emisores

*Parámetros:* ninguno

### Emitir partículas en continuo

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stream_particles` |
| **Icono** | 🌊 |
| **Categoría** | Partículas |

Emite partículas de forma continua en cada paso desde el emisor creado más recientemente (0 para detenerlo)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `particle_type` | Número | `0` | Particle type id (from Create Particle Type) |
| `number` | Número | `1` | Particles to emit per step (0 stops streaming) |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
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
- [Red](Full-Action-Reference-Network-Actions_es) (15)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
