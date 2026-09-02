# Particles

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Burst Particles

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `burst_particles` |
| **Icono** | 💥 |
| **Categoría** | Particles |

Emit a one-time burst of particles from the most recently created emitter

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `particle_type` | Número | `0` | Particle type id (from Create Particle Type) |
| `number` | Número | `10` | Number of particles to emit |

### Clear Particles

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `clear_particles` |
| **Icono** | 🧹 |
| **Categoría** | Particles |

Remove all active particles but keep particle types and emitters

*Parámetros:* ninguno

### Create Emitter

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_emitter` |
| **Icono** | 🌀 |
| **Categoría** | Particles |

Create a particle emitter area (returned id is stored for the next emitter-using action)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Emitter center X (room coordinates) |
| `y` | Número | `0` | Emitter center Y (room coordinates) |
| `width` | Número | `0` | Emitter area width |
| `height` | Número | `0` | Emitter area height |
| `shape` | Elección | `rectangle` | Shape of the emitter area particles spawn within; Opciones: `rectangle`, `ellipse`, `diamond`, `line` |

### Create Particle System

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_particle_system` |
| **Icono** | ✨ |
| **Categoría** | Particles |

Create a particle system attached to this instance (replaces any existing one)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `depth` | Número | `0` | Drawing depth for the particle system (not yet used for cross-instance sort order) |

### Create Particle Type

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_particle_type` |
| **Icono** | ⚙️ |
| **Categoría** | Particles |

Define a new particle appearance/behavior (returned type id is stored for the next particle_type-using action)

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

### Destroy Emitter

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `destroy_emitter` |
| **Icono** | 💥 |
| **Categoría** | Particles |

Destroy the most recently created emitter

*Parámetros:* ninguno

### Destroy Particle System

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `destroy_particle_system` |
| **Icono** | 💥 |
| **Categoría** | Particles |

Remove this instance's particle system, clearing all particles and emitters

*Parámetros:* ninguno

### Stream Particles

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stream_particles` |
| **Icono** | 🌊 |
| **Categoría** | Particles |

Continuously emit particles every step from the most recently created emitter (0 to stop)

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
- [Réseau](Full-Action-Reference-Network-Actions_es) (15)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
