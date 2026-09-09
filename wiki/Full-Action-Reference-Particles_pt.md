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
| `particle_type` | Número | `0` | Identificador do tipo de partícula (de «Criar tipo de partícula») |
| `number` | Número | `10` | Número de partículas a lançar |

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
| `x` | Número | `0` | X do centro do emissor (coordenadas da sala) |
| `y` | Número | `0` | Y do centro do emissor (coordenadas da sala) |
| `width` | Número | `0` | Largura da zona emissora |
| `height` | Número | `0` | Altura da zona emissora |
| `shape` | Escolha | `rectangle` | Forma da zona emissora dentro da qual nascem as partículas; Opções: `rectangle`, `ellipse`, `diamond`, `line` |

### Criar sistema de partículas

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_particle_system` |
| **Ícone** | ✨ |
| **Categoria** | Partículas |

Cria um sistema de partículas ligado a esta instância (substitui o que existir)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `depth` | Número | `0` | Profundidade de desenho do sistema de partículas (ainda não usada para ordenar entre instâncias) |

### Criar tipo de partícula

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_particle_type` |
| **Ícone** | ⚙️ |
| **Categoria** | Partículas |

Define um novo aspeto ou comportamento de partícula (o identificador de tipo devolvido fica guardado para a próxima ação que use um tipo de partícula)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite com que cada partícula é desenhada; deixa vazio para um simples círculo colorido; opcional |
| `size_min` | Número | `1.0` | Tamanho mínimo da partícula (fator de escala) |
| `size_max` | Número | `1.0` | Tamanho máximo da partícula (fator de escala) |
| `size_increase` | Número | `0.0` | Variação de tamanho por passo (negativo encolhe, com 0 como mínimo) |
| `color` | Cor | `#FFFFFF` | Cor da partícula (usada quando não há sprite definido) |
| `alpha` | Número | `1.0` | Transparência (0 = invisível, 1 = opaca) |
| `speed_min` | Número | `0.0` | Velocidade de movimento mínima |
| `speed_max` | Número | `0.0` | Velocidade de movimento máxima |
| `direction_min` | Número | `0` | Ângulo de direção mínimo (0 = direita, 90 = cima) |
| `direction_max` | Número | `360` | Ângulo de direção máximo |
| `life_min` | Número | `100` | Duração mínima, em passos |
| `life_max` | Número | `100` | Duração máxima, em passos |

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
| `particle_type` | Número | `0` | Identificador do tipo de partícula (de «Criar tipo de partícula») |
| `number` | Número | `1` | Partículas emitidas por passo (0 para a emissão) |

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
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (18)
- [Rede](Full-Action-Reference-Network-Actions_pt) (15)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
