# Partículas

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Lançar partículas

| Propriedade | Valor |
|----------|-------|
| **Nome** | `burst_particles` |
| **Ícone** | 💥 |
| **Categoria** | Partículas |

Lança uma rajada única de partículas a partir do emissor criado mais recentemente

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `particle_type` | Número | `0` | Particle type id (from Create Particle Type) |
| `number` | Número | `10` | Number of particles to emit |

### Limpar partículas

| Propriedade | Valor |
|----------|-------|
| **Nome** | `clear_particles` |
| **Ícone** | 🧹 |
| **Categoria** | Partículas |

Remove todas as partículas ativas, mas mantém os tipos de partícula e os emissores

*Parâmetros:* nenhum

### Criar emissor

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_emitter` |
| **Ícone** | 🌀 |
| **Categoria** | Partículas |

Cria uma zona emissora de partículas (o identificador devolvido fica guardado para a próxima ação que use um emissor)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Emitter center X (room coordinates) |
| `y` | Número | `0` | Emitter center Y (room coordinates) |
| `width` | Número | `0` | Emitter area width |
| `height` | Número | `0` | Emitter area height |
| `shape` | Escolha | `rectangle` | Shape of the emitter area particles spawn within; Opções: `rectangle`, `ellipse`, `diamond`, `line` |

### Criar sistema de partículas

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_particle_system` |
| **Ícone** | ✨ |
| **Categoria** | Partículas |

Cria um sistema de partículas ligado a esta instância (substitui o que existir)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `depth` | Número | `0` | Drawing depth for the particle system (not yet used for cross-instance sort order) |

### Criar tipo de partícula

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_particle_type` |
| **Ícone** | ⚙️ |
| **Categoria** | Partículas |

Define um novo aspeto ou comportamento de partícula (o identificador de tipo devolvido fica guardado para a próxima ação que use um tipo de partícula)

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

### Destruir emissor

| Propriedade | Valor |
|----------|-------|
| **Nome** | `destroy_emitter` |
| **Ícone** | 💥 |
| **Categoria** | Partículas |

Destrói o emissor criado mais recentemente

*Parâmetros:* nenhum

### Destruir sistema de partículas

| Propriedade | Valor |
|----------|-------|
| **Nome** | `destroy_particle_system` |
| **Ícone** | 💥 |
| **Categoria** | Partículas |

Remove o sistema de partículas desta instância, apagando todas as suas partículas e emissores

*Parâmetros:* nenhum

### Emitir partículas em contínuo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `stream_particles` |
| **Ícone** | 🌊 |
| **Categoria** | Partículas |

Emite partículas continuamente, a cada passo, a partir do emissor criado mais recentemente (0 para parar)

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
- [Rede](Full-Action-Reference-Network-Actions_pt) (15)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
