# Particles

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

### Burst Particles

| Property | Value |
|----------|-------|
| **Name** | `burst_particles` |
| **Icon** | 💥 |
| **Category** | Particles |

Emit a one-time burst of particles from the most recently created emitter

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `particle_type` | Number | `0` | Particle type id (from Create Particle Type) |
| `number` | Number | `10` | Number of particles to emit |

### Clear Particles

| Property | Value |
|----------|-------|
| **Name** | `clear_particles` |
| **Icon** | 🧹 |
| **Category** | Particles |

Remove all active particles but keep particle types and emitters

*Parameters:* none

### Create Emitter

| Property | Value |
|----------|-------|
| **Name** | `create_emitter` |
| **Icon** | 🌀 |
| **Category** | Particles |

Create a particle emitter area (returned id is stored for the next emitter-using action)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | Emitter center X (room coordinates) |
| `y` | Number | `0` | Emitter center Y (room coordinates) |
| `width` | Number | `0` | Emitter area width |
| `height` | Number | `0` | Emitter area height |
| `shape` | Choice | `rectangle` | Shape of the emitter area particles spawn within; Choices: `rectangle`, `ellipse`, `diamond`, `line` |

### Create Particle System

| Property | Value |
|----------|-------|
| **Name** | `create_particle_system` |
| **Icon** | ✨ |
| **Category** | Particles |

Create a particle system attached to this instance (replaces any existing one)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `depth` | Number | `0` | Drawing depth for the particle system (not yet used for cross-instance sort order) |

### Create Particle Type

| Property | Value |
|----------|-------|
| **Name** | `create_particle_type` |
| **Icon** | ⚙️ |
| **Category** | Particles |

Define a new particle appearance/behavior (returned type id is stored for the next particle_type-using action)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite to draw each particle as; leave empty for a plain colored circle; optional |
| `size_min` | Number | `1.0` | Minimum particle size (scale factor) |
| `size_max` | Number | `1.0` | Maximum particle size (scale factor) |
| `size_increase` | Number | `0.0` | Size change per step (negative shrinks, floored at 0) |
| `color` | Color | `#FFFFFF` | Particle color (used when no sprite is set) |
| `alpha` | Number | `1.0` | Transparency (0=invisible, 1=opaque) |
| `speed_min` | Number | `0.0` | Minimum movement speed |
| `speed_max` | Number | `0.0` | Maximum movement speed |
| `direction_min` | Number | `0` | Minimum direction angle (0=right, 90=up) |
| `direction_max` | Number | `360` | Maximum direction angle |
| `life_min` | Number | `100` | Minimum lifetime in steps |
| `life_max` | Number | `100` | Maximum lifetime in steps |

### Destroy Emitter

| Property | Value |
|----------|-------|
| **Name** | `destroy_emitter` |
| **Icon** | 💥 |
| **Category** | Particles |

Destroy the most recently created emitter

*Parameters:* none

### Destroy Particle System

| Property | Value |
|----------|-------|
| **Name** | `destroy_particle_system` |
| **Icon** | 💥 |
| **Category** | Particles |

Remove this instance's particle system, clearing all particles and emitters

*Parameters:* none

### Stream Particles

| Property | Value |
|----------|-------|
| **Name** | `stream_particles` |
| **Icon** | 🌊 |
| **Category** | Particles |

Continuously emit particles every step from the most recently created emitter (0 to stop)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `particle_type` | Number | `0` | Particle type id (from Create Particle Type) |
| `number` | Number | `1` | Particles to emit per step (0 stops streaming) |

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (20)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (11)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (8)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (25)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (4)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (16)
- [Network](Full-Action-Reference-Network-Actions) (15)

[← Back to Full Action Reference](Full-Action-Reference)
