# Particles

*[Главная](Home_ru) | [Руководство по пресетам](Preset-Guide_ru) | [Справочник событий](Event-Reference_ru)*

> **Сгенерировано автоматически** из реестра действий IDE с помощью `tools/gen_action_reference.py` — не редактируйте вручную; повторно запустите генератор после изменения действий. Переводы взяты из `tools/action_ref_i18n.py`.

### Burst Particles

| Свойство | Значение |
|----------|-------|
| **Имя** | `burst_particles` |
| **Значок** | 💥 |
| **Категория** | Particles |

Emit a one-time burst of particles from the most recently created emitter

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `particle_type` | Число | `0` | Particle type id (from Create Particle Type) |
| `number` | Число | `10` | Number of particles to emit |

### Clear Particles

| Свойство | Значение |
|----------|-------|
| **Имя** | `clear_particles` |
| **Значок** | 🧹 |
| **Категория** | Particles |

Remove all active particles but keep particle types and emitters

*Параметры:* нет

### Create Emitter

| Свойство | Значение |
|----------|-------|
| **Имя** | `create_emitter` |
| **Значок** | 🌀 |
| **Категория** | Particles |

Create a particle emitter area (returned id is stored for the next emitter-using action)

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `x` | Число | `0` | Emitter center X (room coordinates) |
| `y` | Число | `0` | Emitter center Y (room coordinates) |
| `width` | Число | `0` | Emitter area width |
| `height` | Число | `0` | Emitter area height |
| `shape` | Выбор | `rectangle` | Shape of the emitter area particles spawn within; Варианты: `rectangle`, `ellipse`, `diamond`, `line` |

### Create Particle System

| Свойство | Значение |
|----------|-------|
| **Имя** | `create_particle_system` |
| **Значок** | ✨ |
| **Категория** | Particles |

Create a particle system attached to this instance (replaces any existing one)

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `depth` | Число | `0` | Drawing depth for the particle system (not yet used for cross-instance sort order) |

### Create Particle Type

| Свойство | Значение |
|----------|-------|
| **Имя** | `create_particle_type` |
| **Значок** | ⚙️ |
| **Категория** | Particles |

Define a new particle appearance/behavior (returned type id is stored for the next particle_type-using action)

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `sprite` | Спрайт | — | Sprite to draw each particle as; leave empty for a plain colored circle; необязательно |
| `size_min` | Число | `1.0` | Minimum particle size (scale factor) |
| `size_max` | Число | `1.0` | Maximum particle size (scale factor) |
| `size_increase` | Число | `0.0` | Size change per step (negative shrinks, floored at 0) |
| `color` | Цвет | `#FFFFFF` | Particle color (used when no sprite is set) |
| `alpha` | Число | `1.0` | Transparency (0=invisible, 1=opaque) |
| `speed_min` | Число | `0.0` | Minimum movement speed |
| `speed_max` | Число | `0.0` | Maximum movement speed |
| `direction_min` | Число | `0` | Minimum direction angle (0=right, 90=up) |
| `direction_max` | Число | `360` | Maximum direction angle |
| `life_min` | Число | `100` | Minimum lifetime in steps |
| `life_max` | Число | `100` | Maximum lifetime in steps |

### Destroy Emitter

| Свойство | Значение |
|----------|-------|
| **Имя** | `destroy_emitter` |
| **Значок** | 💥 |
| **Категория** | Particles |

Destroy the most recently created emitter

*Параметры:* нет

### Destroy Particle System

| Свойство | Значение |
|----------|-------|
| **Имя** | `destroy_particle_system` |
| **Значок** | 💥 |
| **Категория** | Particles |

Remove this instance's particle system, clearing all particles and emitters

*Параметры:* нет

### Stream Particles

| Свойство | Значение |
|----------|-------|
| **Имя** | `stream_particles` |
| **Значок** | 🌊 |
| **Категория** | Particles |

Continuously emit particles every step from the most recently created emitter (0 to stop)

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `particle_type` | Число | `0` | Particle type id (from Create Particle Type) |
| `number` | Число | `1` | Particles to emit per step (0 stops streaming) |

---

## Другие Категории

- [Движение](Full-Action-Reference-Movement_ru) (20)
- [Экземпляр](Full-Action-Reference-Instance_ru) (12)
- [Счёт](Full-Action-Reference-Score_ru) (11)
- [Комната](Full-Action-Reference-Room_ru) (13)
- [Время](Full-Action-Reference-Timing_ru) (8)
- [Аудио](Full-Action-Reference-Audio_ru) (6)
- [Игра](Full-Action-Reference-Game_ru) (25)
- [Управление](Full-Action-Reference-Control_ru) (19)
- [Сетка](Full-Action-Reference-Grid_ru) (4)
- [Виды](Full-Action-Reference-Views_ru) (2)
- [3D-вид](Full-Action-Reference-3D-View-Actions_ru) (16)
- [Réseau](Full-Action-Reference-Network-Actions_ru) (15)

[← Назад к Полному Справочнику Действий](Full-Action-Reference_ru)
