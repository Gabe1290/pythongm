# Grade

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Se na grade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_on_grid` |
| **Ícone** | ▦ |
| **Categoria** | Grade |

Verificar se o objeto está alinhado à grade

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `grid_size` | Número | `32` | Tamanho da célula da grade em pixels |
| `then_actions` | Lista de ações | — | Ações se na grade |
| `else_actions` | Lista de ações | — | Ações se não na grade |

### Ajustar à grade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `snap_to_grid` |
| **Ícone** | ▦ |
| **Categoria** | Grade |

Alinhar a posição da instância à grade

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `grid_size` | Número | `32` | Tamanho da célula da grade em pixels |

### Parar se nenhuma tecla pressionada

| Propriedade | Valor |
|----------|-------|
| **Nome** | `stop_if_no_keys` |
| **Ícone** | ▦ |
| **Categoria** | Grade |

Parar o movimento na grade quando nenhuma tecla de movimento é pressionada (perfeito para um ajuste suave à grade)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `grid_size` | Número | `32` | Tamanho da célula da grade em pixels |

### Testar alinhamento à grade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_alignment` |
| **Ícone** | ❓▦ |
| **Categoria** | Grade |

Condição: verdadeiro se a instância está alinhada a uma grade

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `hsnap` | Número | `32` | Espaçamento horizontal da grade em pixels |
| `vsnap` | Número | `32` | Espaçamento vertical da grade em pixels |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (2)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (20)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (4)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
