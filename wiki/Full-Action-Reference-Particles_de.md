# Particles

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Burst Particles

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `burst_particles` |
| **Symbol** | 💥 |
| **Kategorie** | Particles |

Emit a one-time burst of particles from the most recently created emitter

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `particle_type` | Zahl | `0` | Particle type id (from Create Particle Type) |
| `number` | Zahl | `10` | Number of particles to emit |

### Clear Particles

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `clear_particles` |
| **Symbol** | 🧹 |
| **Kategorie** | Particles |

Remove all active particles but keep particle types and emitters

*Parameter:* keine

### Create Emitter

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `create_emitter` |
| **Symbol** | 🌀 |
| **Kategorie** | Particles |

Create a particle emitter area (returned id is stored for the next emitter-using action)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | Emitter center X (room coordinates) |
| `y` | Zahl | `0` | Emitter center Y (room coordinates) |
| `width` | Zahl | `0` | Emitter area width |
| `height` | Zahl | `0` | Emitter area height |
| `shape` | Auswahl | `rectangle` | Shape of the emitter area particles spawn within; Auswahl: `rectangle`, `ellipse`, `diamond`, `line` |

### Create Particle System

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `create_particle_system` |
| **Symbol** | ✨ |
| **Kategorie** | Particles |

Create a particle system attached to this instance (replaces any existing one)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `depth` | Zahl | `0` | Drawing depth for the particle system (not yet used for cross-instance sort order) |

### Create Particle Type

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `create_particle_type` |
| **Symbol** | ⚙️ |
| **Kategorie** | Particles |

Define a new particle appearance/behavior (returned type id is stored for the next particle_type-using action)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite to draw each particle as; leave empty for a plain colored circle; optional |
| `size_min` | Zahl | `1.0` | Minimum particle size (scale factor) |
| `size_max` | Zahl | `1.0` | Maximum particle size (scale factor) |
| `size_increase` | Zahl | `0.0` | Size change per step (negative shrinks, floored at 0) |
| `color` | Farbe | `#FFFFFF` | Particle color (used when no sprite is set) |
| `alpha` | Zahl | `1.0` | Transparency (0=invisible, 1=opaque) |
| `speed_min` | Zahl | `0.0` | Minimum movement speed |
| `speed_max` | Zahl | `0.0` | Maximum movement speed |
| `direction_min` | Zahl | `0` | Minimum direction angle (0=right, 90=up) |
| `direction_max` | Zahl | `360` | Maximum direction angle |
| `life_min` | Zahl | `100` | Minimum lifetime in steps |
| `life_max` | Zahl | `100` | Maximum lifetime in steps |

### Destroy Emitter

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `destroy_emitter` |
| **Symbol** | 💥 |
| **Kategorie** | Particles |

Destroy the most recently created emitter

*Parameter:* keine

### Destroy Particle System

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `destroy_particle_system` |
| **Symbol** | 💥 |
| **Kategorie** | Particles |

Remove this instance's particle system, clearing all particles and emitters

*Parameter:* keine

### Stream Particles

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `stream_particles` |
| **Symbol** | 🌊 |
| **Kategorie** | Particles |

Continuously emit particles every step from the most recently created emitter (0 to stop)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `particle_type` | Zahl | `0` | Particle type id (from Create Particle Type) |
| `number` | Zahl | `1` | Particles to emit per step (0 stops streaming) |

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (8)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (25)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (16)
- [Réseau](Full-Action-Reference-Network-Actions_de) (15)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
