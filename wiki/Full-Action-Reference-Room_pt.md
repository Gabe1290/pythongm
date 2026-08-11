# Sala

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Verificar sala

| Propriedade | Valor |
|----------|-------|
| **Nome** | `check_room` |
| **Ícone** | ❓🚪 |
| **Categoria** | Sala |

Condição: verdadeiro se a sala atual corresponde

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `room` | Sala | — | Sala a comparar |
| `not_flag` | Sim/Não | Não | Inverter o resultado; opcional |

### Encerrar jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `game_end` |
| **Ícone** | 🛑🎮 |
| **Categoria** | Sala |

Encerrar o jogo

*Parâmetros:* nenhum

### Ir para a sala

| Propriedade | Valor |
|----------|-------|
| **Nome** | `goto_room` |
| **Ícone** | 🚪 |
| **Categoria** | Sala |

Mudar para uma sala específica

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `room` | Sala | — | Nome da sala de destino |
| `transition` | Escolha | `none` | Efeito de transição (atualmente aceito mas não renderizado); Opções: `none`; opcional |

### Se existe sala seguinte

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_next_room_exists` |
| **Ícone** | ❓➡️ |
| **Categoria** | Sala |

Verificar se há uma sala seguinte após a atual

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `then_actions` | Lista de ações | — | Ações se existe a sala seguinte |
| `else_actions` | Lista de ações | — | Ações se a sala seguinte não existe |

### Se existe sala anterior

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_previous_room_exists` |
| **Ícone** | ❓⬅️ |
| **Categoria** | Sala |

Verificar se há uma sala anterior antes da atual

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `then_actions` | Lista de ações | — | Ações se existe a sala anterior |
| `else_actions` | Lista de ações | — | Ações se a sala anterior não existe |

### Sala seguinte

| Propriedade | Valor |
|----------|-------|
| **Nome** | `next_room` |
| **Ícone** | ➡️ |
| **Categoria** | Sala |

Ir para a sala seguinte

*Parâmetros:* nenhum

### Sala anterior

| Propriedade | Valor |
|----------|-------|
| **Nome** | `previous_room` |
| **Ícone** | ⬅️ |
| **Categoria** | Sala |

Ir para a sala anterior

*Parâmetros:* nenhum

### Reiniciar sala

| Propriedade | Valor |
|----------|-------|
| **Nome** | `restart_room` |
| **Ícone** | 🔄 |
| **Categoria** | Sala |

Reiniciar a sala atual

*Parâmetros:* nenhum

### Set Background

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_background` |
| **Ícone** | 🖼️ |
| **Categoria** | Sala |

Set the current room's background image, with tiling and scrolling options

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `background` | Texto | — | Background or sprite asset name |
| `visible` | Sim/Não | Sim | Show the background; opcional |
| `foreground` | Sim/Não | Não | Draw in front of instances instead of behind them; opcional |
| `tiled_h` | Sim/Não | Não | Repeat the background across the width of the room; opcional |
| `tiled_v` | Sim/Não | Não | Repeat the background across the height of the room; opcional |
| `hspeed` | Número | `0` | Horizontal auto-scroll speed in pixels/frame; opcional |
| `vspeed` | Número | `0` | Vertical auto-scroll speed in pixels/frame; opcional |

### Set Background Color

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_background_color` |
| **Ícone** | 🎨 |
| **Categoria** | Sala |

Change the current room's background color

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `color` | Cor | `#87CEEB` | Background color |
| `show_color` | Sim/Não | Sim | Whether the background color is visible (off fills black instead); opcional |

### Definir título da sala

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_room_caption` |
| **Ícone** | 🏷️ |
| **Categoria** | Sala |

Definir o título da janela do jogo

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `caption` | Texto | — | Texto do título da janela |

### Set Room Persistent

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_room_persistent` |
| **Ícone** | 💾 |
| **Categoria** | Sala |

Whether the current room keeps its live state (instance positions, destroyed instances, etc.) when the player leaves and later returns to it, instead of rebuilding fresh from its authored layout every revisit

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `persistent` | Sim/Não | Sim | Keep this room's state across a revisit |

### Set Room Speed

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_room_speed` |
| **Ícone** | ⏱️ |
| **Categoria** | Sala |

Change the game's frame rate (frames per second)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `30` | Target frames per second (1-240) |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Tempo](Full-Action-Reference-Timing_pt) (2)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (20)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (4)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
