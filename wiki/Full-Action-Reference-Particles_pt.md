# Particles

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Burst Particles

| Propriedade | Valor |
|----------|-------|
| **Nome** | `burst_particles` |
| **Ícone** | 💥 |
| **Categoria** | Particles |

Emit a one-time burst of particles from the most recently created emitter

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `particle_type` | Número | `0` | Particle type id (from Create Particle Type) |
| `number` | Número | `10` | Number of particles to emit |

### Clear Particles

| Propriedade | Valor |
|----------|-------|
| **Nome** | `clear_particles` |
| **Ícone** | 🧹 |
| **Categoria** | Particles |

Remove all active particles but keep particle types and emitters

*Parâmetros:* nenhum

### Create Emitter

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_emitter` |
| **Ícone** | 🌀 |
| **Categoria** | Particles |

Create a particle emitter area (returned id is stored for the next emitter-using action)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Emitter center X (room coordinates) |
| `y` | Número | `0` | Emitter center Y (room coordinates) |
| `width` | Número | `0` | Emitter area width |
| `height` | Número | `0` | Emitter area height |
| `shape` | Escolha | `rectangle` | Shape of the emitter area particles spawn within; Opções: `rectangle`, `ellipse`, `diamond`, `line` |

### Create Particle System

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_particle_system` |
| **Ícone** | ✨ |
| **Categoria** | Particles |

Create a particle system attached to this instance (replaces any existing one)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `depth` | Número | `0` | Drawing depth for the particle system (not yet used for cross-instance sort order) |

### Create Particle Type

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_particle_type` |
| **Ícone** | ⚙️ |
| **Categoria** | Particles |

Define a new particle appearance/behavior (returned type id is stored for the next particle_type-using action)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite to draw each particle as; leave empty for a plain colored circle; opcional |
| `size_min` | Número | `1.0` | Minimum particle size (scale factor) |
| `size_max` | Número | `1.0` | Maximum particle size (scale factor) |
| `size_increase` | Número | `0.0` | Size change per step (negative shrinks, floored at 0) |
| `color` | Cor | `#FFFFFF` | Particle color (used when no sprite is set) |
| `alpha` | Número | `1.0` | Transparency (0=invisible, 1=opaque) |
| `speed_min` | Número | `0.0` | Minimum movement speed |
| `speed_max` | Número | `0.0` | Maximum movement speed |
| `direction_min` | Número | `0` | Minimum direction angle (0=right, 90=up) |
| `direction_max` | Número | `360` | Maximum direction angle |
| `life_min` | Número | `100` | Minimum lifetime in steps |
| `life_max` | Número | `100` | Maximum lifetime in steps |

### Destroy Emitter

| Propriedade | Valor |
|----------|-------|
| **Nome** | `destroy_emitter` |
| **Ícone** | 💥 |
| **Categoria** | Particles |

Destroy the most recently created emitter

*Parâmetros:* nenhum

### Destroy Particle System

| Propriedade | Valor |
|----------|-------|
| **Nome** | `destroy_particle_system` |
| **Ícone** | 💥 |
| **Categoria** | Particles |

Remove this instance's particle system, clearing all particles and emitters

*Parâmetros:* nenhum

### Stream Particles

| Propriedade | Valor |
|----------|-------|
| **Nome** | `stream_particles` |
| **Ícone** | 🌊 |
| **Categoria** | Particles |

Continuously emit particles every step from the most recently created emitter (0 to stop)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `particle_type` | Número | `0` | Particle type id (from Create Particle Type) |
| `number` | Número | `1` | Particles to emit per step (0 stops streaming) |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (8)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (25)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (16)
- [Réseau](Full-Action-Reference-Network-Actions_pt) (15)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
