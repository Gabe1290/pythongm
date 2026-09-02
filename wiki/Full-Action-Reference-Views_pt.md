# Vistas

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Ativar vistas

| Propriedade | Valor |
|----------|-------|
| **Nome** | `enable_views` |
| **Ícone** | 🎥 |
| **Categoria** | Vistas |

Ativar ou desativar o sistema de câmera/vista da sala (permite que um nível role quando é maior que a janela)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `enable` | Sim/Não | Sim | Ativado = vistas de câmera; desativado = desenhar a sala inteira de uma vez |

### Configurar vista

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_view` |
| **Ícone** | 🎥 |
| **Categoria** | Vistas |

Configurar uma vista de câmera: qual parte da sala mostra, onde é desenhada na tela e um objeto a seguir

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `view` | Escolha | `0` | Qual das 8 vistas configurar; Opções: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` |
| `visible` | Sim/Não | Sim | Desenhar esta vista |
| `view_x` | Número | `0` | Borda esquerda da região da sala mostrada |
| `view_y` | Número | `0` | Borda superior da região da sala mostrada |
| `view_w` | Número | `800` | Largura da região da sala mostrada |
| `view_h` | Número | `600` | Altura da região da sala mostrada |
| `port_x` | Número | `0` | Borda esquerda na tela |
| `port_y` | Número | `0` | Borda superior na tela |
| `port_w` | Número | `800` | Largura desenhada na tela |
| `port_h` | Número | `600` | Altura desenhada na tela |
| `follow` | Objeto | — | Objeto que a câmera segue (vazio = vista fixa); opcional |
| `hborder` | Número | `32` | Borda horizontal antes de a câmera rolar |
| `vborder` | Número | `32` | Borda vertical antes de a câmera rolar |
| `hspeed` | Número | `-1` | Velocidade máxima de rolagem horizontal (-1 = instantâneo) |
| `vspeed` | Número | `-1` | Velocidade máxima de rolagem vertical (-1 = instantâneo) |

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
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (16)
- [Particles](Full-Action-Reference-Particles_pt) (8)
- [Réseau](Full-Action-Reference-Network-Actions_pt) (15)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
