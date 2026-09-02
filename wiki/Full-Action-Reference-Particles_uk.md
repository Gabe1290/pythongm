# Particles

*[Головна](Home_uk) | [Посібник із пресетів](Preset-Guide_uk) | [Довідник подій](Event-Reference_uk)*

> **Згенеровано автоматично** з реєстру дій IDE за допомогою `tools/gen_action_reference.py` — не редагуйте вручну; повторно запустіть генератор після зміни дій. Переклади взято з `tools/action_ref_i18n.py`.

### Burst Particles

| Властивість | Значення |
|----------|-------|
| **Назва** | `burst_particles` |
| **Значок** | 💥 |
| **Категорія** | Particles |

Emit a one-time burst of particles from the most recently created emitter

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `particle_type` | Число | `0` | Particle type id (from Create Particle Type) |
| `number` | Число | `10` | Number of particles to emit |

### Clear Particles

| Властивість | Значення |
|----------|-------|
| **Назва** | `clear_particles` |
| **Значок** | 🧹 |
| **Категорія** | Particles |

Remove all active particles but keep particle types and emitters

*Параметри:* немає

### Create Emitter

| Властивість | Значення |
|----------|-------|
| **Назва** | `create_emitter` |
| **Значок** | 🌀 |
| **Категорія** | Particles |

Create a particle emitter area (returned id is stored for the next emitter-using action)

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `x` | Число | `0` | Emitter center X (room coordinates) |
| `y` | Число | `0` | Emitter center Y (room coordinates) |
| `width` | Число | `0` | Emitter area width |
| `height` | Число | `0` | Emitter area height |
| `shape` | Вибір | `rectangle` | Shape of the emitter area particles spawn within; Варіанти: `rectangle`, `ellipse`, `diamond`, `line` |

### Create Particle System

| Властивість | Значення |
|----------|-------|
| **Назва** | `create_particle_system` |
| **Значок** | ✨ |
| **Категорія** | Particles |

Create a particle system attached to this instance (replaces any existing one)

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `depth` | Число | `0` | Drawing depth for the particle system (not yet used for cross-instance sort order) |

### Create Particle Type

| Властивість | Значення |
|----------|-------|
| **Назва** | `create_particle_type` |
| **Значок** | ⚙️ |
| **Категорія** | Particles |

Define a new particle appearance/behavior (returned type id is stored for the next particle_type-using action)

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `sprite` | Спрайт | — | Sprite to draw each particle as; leave empty for a plain colored circle; необов'язково |
| `size_min` | Число | `1.0` | Minimum particle size (scale factor) |
| `size_max` | Число | `1.0` | Maximum particle size (scale factor) |
| `size_increase` | Число | `0.0` | Size change per step (negative shrinks, floored at 0) |
| `color` | Колір | `#FFFFFF` | Particle color (used when no sprite is set) |
| `alpha` | Число | `1.0` | Transparency (0=invisible, 1=opaque) |
| `speed_min` | Число | `0.0` | Minimum movement speed |
| `speed_max` | Число | `0.0` | Maximum movement speed |
| `direction_min` | Число | `0` | Minimum direction angle (0=right, 90=up) |
| `direction_max` | Число | `360` | Maximum direction angle |
| `life_min` | Число | `100` | Minimum lifetime in steps |
| `life_max` | Число | `100` | Maximum lifetime in steps |

### Destroy Emitter

| Властивість | Значення |
|----------|-------|
| **Назва** | `destroy_emitter` |
| **Значок** | 💥 |
| **Категорія** | Particles |

Destroy the most recently created emitter

*Параметри:* немає

### Destroy Particle System

| Властивість | Значення |
|----------|-------|
| **Назва** | `destroy_particle_system` |
| **Значок** | 💥 |
| **Категорія** | Particles |

Remove this instance's particle system, clearing all particles and emitters

*Параметри:* немає

### Stream Particles

| Властивість | Значення |
|----------|-------|
| **Назва** | `stream_particles` |
| **Значок** | 🌊 |
| **Категорія** | Particles |

Continuously emit particles every step from the most recently created emitter (0 to stop)

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `particle_type` | Число | `0` | Particle type id (from Create Particle Type) |
| `number` | Число | `1` | Particles to emit per step (0 stops streaming) |

---

## Інші Категорії

- [Рух](Full-Action-Reference-Movement_uk) (20)
- [Екземпляр](Full-Action-Reference-Instance_uk) (12)
- [Рахунок](Full-Action-Reference-Score_uk) (11)
- [Кімната](Full-Action-Reference-Room_uk) (13)
- [Час](Full-Action-Reference-Timing_uk) (8)
- [Аудіо](Full-Action-Reference-Audio_uk) (6)
- [Гра](Full-Action-Reference-Game_uk) (25)
- [Керування](Full-Action-Reference-Control_uk) (19)
- [Сітка](Full-Action-Reference-Grid_uk) (4)
- [Вигляди](Full-Action-Reference-Views_uk) (2)
- [3D-вигляд](Full-Action-Reference-3D-View-Actions_uk) (16)
- [Réseau](Full-Action-Reference-Network-Actions_uk) (15)

[← Назад до Повного Довідника Дій](Full-Action-Reference_uk)
