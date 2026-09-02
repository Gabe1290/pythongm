# Particles

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Burst Particles

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `burst_particles` |
| **Ikona** | 💥 |
| **Kategorija** | Particles |

Emit a one-time burst of particles from the most recently created emitter

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `particle_type` | Število | `0` | Particle type id (from Create Particle Type) |
| `number` | Število | `10` | Number of particles to emit |

### Clear Particles

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `clear_particles` |
| **Ikona** | 🧹 |
| **Kategorija** | Particles |

Remove all active particles but keep particle types and emitters

*Parametri:* brez

### Create Emitter

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `create_emitter` |
| **Ikona** | 🌀 |
| **Kategorija** | Particles |

Create a particle emitter area (returned id is stored for the next emitter-using action)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Emitter center X (room coordinates) |
| `y` | Število | `0` | Emitter center Y (room coordinates) |
| `width` | Število | `0` | Emitter area width |
| `height` | Število | `0` | Emitter area height |
| `shape` | Izbira | `rectangle` | Shape of the emitter area particles spawn within; Izbire: `rectangle`, `ellipse`, `diamond`, `line` |

### Create Particle System

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `create_particle_system` |
| **Ikona** | ✨ |
| **Kategorija** | Particles |

Create a particle system attached to this instance (replaces any existing one)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `depth` | Število | `0` | Drawing depth for the particle system (not yet used for cross-instance sort order) |

### Create Particle Type

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `create_particle_type` |
| **Ikona** | ⚙️ |
| **Kategorija** | Particles |

Define a new particle appearance/behavior (returned type id is stored for the next particle_type-using action)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite to draw each particle as; leave empty for a plain colored circle; neobvezno |
| `size_min` | Število | `1.0` | Minimum particle size (scale factor) |
| `size_max` | Število | `1.0` | Maximum particle size (scale factor) |
| `size_increase` | Število | `0.0` | Size change per step (negative shrinks, floored at 0) |
| `color` | Barva | `#FFFFFF` | Particle color (used when no sprite is set) |
| `alpha` | Število | `1.0` | Transparency (0=invisible, 1=opaque) |
| `speed_min` | Število | `0.0` | Minimum movement speed |
| `speed_max` | Število | `0.0` | Maximum movement speed |
| `direction_min` | Število | `0` | Minimum direction angle (0=right, 90=up) |
| `direction_max` | Število | `360` | Maximum direction angle |
| `life_min` | Število | `100` | Minimum lifetime in steps |
| `life_max` | Število | `100` | Maximum lifetime in steps |

### Destroy Emitter

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `destroy_emitter` |
| **Ikona** | 💥 |
| **Kategorija** | Particles |

Destroy the most recently created emitter

*Parametri:* brez

### Destroy Particle System

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `destroy_particle_system` |
| **Ikona** | 💥 |
| **Kategorija** | Particles |

Remove this instance's particle system, clearing all particles and emitters

*Parametri:* brez

### Stream Particles

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `stream_particles` |
| **Ikona** | 🌊 |
| **Kategorija** | Particles |

Continuously emit particles every step from the most recently created emitter (0 to stop)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `particle_type` | Število | `0` | Particle type id (from Create Particle Type) |
| `number` | Število | `1` | Particles to emit per step (0 stops streaming) |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (20)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (11)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (8)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (25)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (16)
- [Réseau](Full-Action-Reference-Network-Actions_sl) (15)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
