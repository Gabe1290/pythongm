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

### Definir fundo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_background` |
| **Ícone** | 🖼️ |
| **Categoria** | Sala |

Definir a imagem de fundo da sala atual, com opções de mosaico e deslocamento

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `background` | Texto | — | Nome do recurso de fundo ou sprite |
| `visible` | Sim/Não | Sim | Mostrar o fundo; opcional |
| `foreground` | Sim/Não | Não | Desenhar à frente das instâncias em vez de atrás; opcional |
| `tiled_h` | Sim/Não | Não | Repetir o fundo ao longo da largura da sala; opcional |
| `tiled_v` | Sim/Não | Não | Repetir o fundo ao longo da altura da sala; opcional |
| `hspeed` | Número | `0` | Velocidade de deslocamento automático horizontal em pixels/quadro; opcional |
| `vspeed` | Número | `0` | Velocidade de deslocamento automático vertical em pixels/quadro; opcional |

### Definir cor de fundo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_background_color` |
| **Ícone** | 🎨 |
| **Categoria** | Sala |

Alterar a cor de fundo da sala atual

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `color` | Cor | `#87CEEB` | Cor de fundo |
| `show_color` | Sim/Não | Sim | Se a cor de fundo é visível (desativado preenche com preto); opcional |

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

### Definir persistência da sala

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_room_persistent` |
| **Ícone** | 💾 |
| **Categoria** | Sala |

Se a sala atual mantém o seu estado ativo (posições das instâncias, instâncias destruídas, etc.) quando o jogador a deixa e depois regressa, em vez de a reconstruir do zero a partir do seu layout original a cada visita

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `persistent` | Sim/Não | Sim | Manter o estado desta sala ao regressar a ela |

### Definir velocidade da sala

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_room_speed` |
| **Ícone** | ⏱️ |
| **Categoria** | Sala |

Alterar a taxa de quadros do jogo (quadros por segundo)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `30` | Quadros por segundo alvo (1-240) |

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
