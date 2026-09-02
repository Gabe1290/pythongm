# Pontuação

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Limpar tabela de recordes

| Propriedade | Valor |
|----------|-------|
| **Nome** | `clear_highscore` |
| **Ícone** | 🗑️🏆 |
| **Categoria** | Pontuação |

Limpar todas as entradas da tabela de recordes

*Parâmetros:* nenhum

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

### Mostrar tabela de recordes

| Propriedade | Valor |
|----------|-------|
| **Nome** | `show_highscore` |
| **Ícone** | 🏆 |
| **Categoria** | Pontuação |

Mostrar a caixa de diálogo da tabela de recordes

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `background` | Cor | `#FFFFDD` | Cor de fundo da caixa de diálogo; opcional |
| `new_color` | Cor | `#FF0000` | Cor usada para a nova entrada (qualificada); opcional |
| `other_color` | Cor | `#000000` | Cor usada para as outras entradas; opcional |
| `allow_new_entry` | Sim/Não | Sim | Pedir o nome se a pontuação atual se qualifica |

### Testar saúde

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_health` |
| **Ícone** | ❓💚 |
| **Categoria** | Pontuação |

Condição: comparar a saúde atual com um valor

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `operation` | Escolha | `equal` | Operador de comparação; Opções: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |
| `value` | Número | `0` | Valor de comparação |

### Testar vidas

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_lives` |
| **Ícone** | ❓❤️ |
| **Categoria** | Pontuação |

Condição: comparar o número de vidas com um valor

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Número | `0` | Valor de comparação |
| `operation` | Escolha | `equal` | Operador de comparação; Opções: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

### Testar pontuação

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_score` |
| **Ícone** | ❓🏆 |
| **Categoria** | Pontuação |

Condição: comparar a pontuação com um valor

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Número | `0` | Valor de comparação |
| `operation` | Escolha | `equal` | Operador de comparação; Opções: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (8)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (25)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (16)
- [Particles](Full-Action-Reference-Particles_pt) (8)
- [Réseau](Full-Action-Reference-Network-Actions_pt) (15)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
