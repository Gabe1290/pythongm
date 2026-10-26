# Score/Lives/Health

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Limpar tabela de recordes

| Propriedade | Valor |
|----------|-------|
| **Nome** | `clear_highscore` |
| **Ícone** | 🗑️🏆 |
| **Categoria** | Score/Lives/Health |

Limpar todas as entradas da tabela de recordes

*Parâmetros:* nenhum

### Mostrar tabela de recordes

| Propriedade | Valor |
|----------|-------|
| **Nome** | `show_highscore` |
| **Ícone** | 🏆 |
| **Categoria** | Score/Lives/Health |

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
| **Categoria** | Score/Lives/Health |

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
| **Categoria** | Score/Lives/Health |

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
| **Categoria** | Score/Lives/Health |

Condição: comparar a pontuação com um valor

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Número | `0` | Valor de comparação |
| `operation` | Escolha | `equal` | Operador de comparação; Opções: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (21)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (6)
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
- [micro:bit](Full-Action-Reference-Microbit-Actions_pt) (16)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
