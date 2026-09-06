# Частки

*[Головна](Home_uk) | [Посібник із пресетів](Preset-Guide_uk) | [Довідник подій](Event-Reference_uk)*

> **Згенеровано автоматично** з реєстру дій IDE за допомогою `tools/gen_action_reference.py` — не редагуйте вручну; повторно запустіть генератор після зміни дій. Переклади взято з `tools/action_ref_i18n.py`.

### Випустити частки

| Властивість | Значення |
|----------|-------|
| **Назва** | `burst_particles` |
| **Значок** | 💥 |
| **Категорія** | Частки |

Випускає одиничний залп часток з останнього створеного випромінювача

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `particle_type` | Число | `0` | Particle type id (from Create Particle Type) |
| `number` | Число | `10` | Number of particles to emit |

### Очистити частки

| Властивість | Значення |
|----------|-------|
| **Назва** | `clear_particles` |
| **Значок** | 🧹 |
| **Категорія** | Частки |

Вилучає всі активні частки, але зберігає типи часток і випромінювачі

*Параметри:* немає

### Створити випромінювач

| Властивість | Значення |
|----------|-------|
| **Назва** | `create_emitter` |
| **Значок** | 🌀 |
| **Категорія** | Частки |

Створює область-випромінювач часток (повернений ідентифікатор запам'ятовується для наступної дії, що використовує випромінювач)

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `x` | Число | `0` | Emitter center X (room coordinates) |
| `y` | Число | `0` | Emitter center Y (room coordinates) |
| `width` | Число | `0` | Emitter area width |
| `height` | Число | `0` | Emitter area height |
| `shape` | Вибір | `rectangle` | Shape of the emitter area particles spawn within; Варіанти: `rectangle`, `ellipse`, `diamond`, `line` |

### Створити систему часток

| Властивість | Значення |
|----------|-------|
| **Назва** | `create_particle_system` |
| **Значок** | ✨ |
| **Категорія** | Частки |

Створює систему часток, прив'язану до цього екземпляра (замінює наявну)

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `depth` | Число | `0` | Drawing depth for the particle system (not yet used for cross-instance sort order) |

### Створити тип часток

| Властивість | Значення |
|----------|-------|
| **Назва** | `create_particle_type` |
| **Значок** | ⚙️ |
| **Категорія** | Частки |

Визначає новий вигляд або поведінку часток (повернений ідентифікатор типу запам'ятовується для наступної дії, що використовує тип часток)

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

### Видалити випромінювач

| Властивість | Значення |
|----------|-------|
| **Назва** | `destroy_emitter` |
| **Значок** | 💥 |
| **Категорія** | Частки |

Вилучає останній створений випромінювач

*Параметри:* немає

### Видалити систему часток

| Властивість | Значення |
|----------|-------|
| **Назва** | `destroy_particle_system` |
| **Значок** | 💥 |
| **Категорія** | Частки |

Вилучає систему часток цього екземпляра разом з усіма частками та випромінювачами

*Параметри:* немає

### Випускати частки потоком

| Властивість | Значення |
|----------|-------|
| **Назва** | `stream_particles` |
| **Значок** | 🌊 |
| **Категорія** | Частки |

Безперервно випускає частки на кожному кроці з останнього створеного випромінювача (0 — зупинити)

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
- [Мережа](Full-Action-Reference-Network-Actions_uk) (15)

[← Назад до Повного Довідника Дій](Full-Action-Reference_uk)
