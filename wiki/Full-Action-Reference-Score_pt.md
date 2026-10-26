# Pontuação

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Desenhar barra de saúde

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_health_bar` |
| **Ícone** | 🩺 |
| **Categoria** | Pontuação |

Desenhar a saúde atual como uma barra de duas cores

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x1` | Número | `0` | X esquerda |
| `y1` | Número | `0` | Y superior |
| `x2` | Número | `100` | X direita |
| `y2` | Número | `20` | Y inferior |
| `back_color` | Cor | `#FF0000` | Cor de fundo (vazio) |
| `bar_color` | Cor | `#00FF00` | Cor de preenchimento (saúde) |

### Desenhar vidas

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_lives` |
| **Ícone** | 🖍️❤️ |
| **Categoria** | Pontuação |

Desenhar o número de vidas atual como imagens de sprite repetidas

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `sprite` | Sprite | — | Sprite desenhado uma vez por vida restante; opcional |
| `scale` | Número | `1.0` | Fator de escala uniforme para o ícone de vida (1.0 = tamanho nativo); opcional |
| `relative` | Sim/Não | Não | Desenhar em relação à posição desta instância em vez de coordenadas de tela absolutas; opcional |

### Desenhar pontuação

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_score` |
| **Ícone** | 🖍️🏆 |
| **Categoria** | Pontuação |

Desenhar a pontuação atual na tela

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `caption` | Texto | `Score: ` | Texto mostrado antes do valor da pontuação; opcional |
| `relative` | Sim/Não | Não | Desenhar em relação à posição desta instância em vez de coordenadas de tela absolutas; opcional |

### Definir saúde

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_health` |
| **Ícone** | 💚 |
| **Categoria** | Pontuação |

Definir a saúde, ou somar a ela com «Relativo»

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Número | `100` | Valor de saúde (0-100) |
| `relative` | Sim/Não | Não | Somar à saúde atual em vez de substituí-la |

### Definir vidas

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_lives` |
| **Ícone** | ❤️ |
| **Categoria** | Pontuação |

Definir as vidas, ou somar a elas com «Relativo»

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Número | `3` | Número de vidas |
| `relative` | Sim/Não | Não | Somar às vidas atuais em vez de substituí-las |

### Definir pontuação

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_score` |
| **Ícone** | 🏆 |
| **Categoria** | Pontuação |

Definir a pontuação, ou somar a ela com «Relativo»

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Número | `0` | Valor de pontuação a definir |
| `relative` | Sim/Não | Não | Somar à pontuação atual em vez de substituí-la |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (21)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (8)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (14)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (3)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (18)
- [Desenho](Full-Action-Reference-Drawing_pt) (11)
- [Rede](Full-Action-Reference-Network-Actions_pt) (22)
- [Partículas](Full-Action-Reference-Particles_pt) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_pt) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_pt) (16)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
