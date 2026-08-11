# Vista 3D

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Desenhar HUD DOOM

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_doom_hud` |
| **Ícone** | 🎯 |
| **Categoria** | Vista 3D |

Desenhar uma barra de status inferior no estilo DOOM (barra de saúde + número, pontuação, vidas, um contador de objetivo e um ícone de rosto que reage à saúde) sobre a vista raycast

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Borda esquerda da barra, em pixels de tela |
| `y` | Número | `-1` | Borda superior da barra; um valor negativo a alinha automaticamente à parte inferior da janela, sob a vista reduzida; opcional |
| `width` | Número | `0` | Largura da barra (0 = largura total da janela); opcional |
| `height` | Número | `42` | Altura da barra; mantenha-a coerente com a faixa viewport_height reservada em enable_raycast_view; opcional |
| `back_color` | Cor | `#101010` | Painel de fundo da barra; opcional |
| `divider_color` | Cor | `#505050` | Borda superior e fundo da barra de saúde; opcional |
| `text_color` | Cor | `#ffffff` | Cor de todo o texto da barra; opcional |
| `health_label` | Texto | `Health` | opcional |
| `health_bar_width` | Número | `90` | opcional |
| `health_bar_height` | Número | `14` | opcional |
| `bar_color` | Cor | `#20c020` | Cor de preenchimento da barra de saúde; opcional |
| `face_sprite` | Sprite | — | Faixa horizontal de quadros de rosto, o mais saudável primeiro (vazio = sem ícone de rosto); opcional |
| `face_frames` | Número | `4` | Quantos quadros a faixa de rosto tem; a saúde é distribuída uniformemente entre eles; opcional |
| `score_label` | Texto | `Score: ` | opcional |
| `lives_sprite` | Sprite | — | Sprite desenhado uma vez por vida restante; opcional |
| `lives_scale` | Número | `1.0` | opcional |
| `objective_value` | Texto | `0` | Expressão mostrada após o rótulo de objetivo (associe sua própria variável de chave/missão); opcional |
| `objective_label` | Texto | `Keys: ` | opcional |

### Desenhar minimapa

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_minimap` |
| **Ícone** | 🗺️ |
| **Categoria** | Vista 3D |

Desenhar um minimapa orientado ao norte dos muros da sala raycast, com um marcador que mostra onde está a câmera e para onde ela olha

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Borda esquerda do minimapa, em pixels de tela |
| `y` | Número | `0` | Borda superior do minimapa, em pixels de tela |
| `size` | Número | `120` | Largura e altura do quadrado do minimapa, em pixels; opcional |
| `back_color` | Cor | `#101018` | Cor do painel atrás do mapa; opcional |
| `wall_color` | Cor | `#8080a0` | Cor das linhas dos muros; opcional |
| `player_color` | Cor | `#ffd040` | Cor do marcador da câmera e sua linha de direção; opcional |

### Ativar vista Raycast

| Propriedade | Valor |
|----------|-------|
| **Nome** | `enable_raycast_view` |
| **Ícone** | 🕹️ |
| **Categoria** | Vista 3D |

Renderizar a sala como uma vista 3D em primeira pessoa no estilo Doom/Wolfenstein (muros, céu, chão) em vez da vista de cima

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `enable` | Sim/Não | Sim | Ativado = vista raycast em primeira pessoa; desativado = vista de cima normal |
| `camera_object` | Objeto | — | Objeto cuja posição + ângulo de visão é a câmera (vazio = o objeto que executa esta ação); opcional |
| `fov` | Número | `66` | Campo de visão horizontal em graus; opcional |
| `render_distance` | Número | `20` | Comprimento máximo do raio em células da grade; opcional |
| `cell_size` | Número | `32` | Tamanho da célula da grade em pixels (corresponde à grade de posicionamento dos muros); opcional |
| `columns` | Número | `320` | Colunas da tela para raycast (menos = mais rápido/mais grosseiro); opcional |
| `wall_color` | Cor | `#993333` | Cor uniforme dos muros quando não há textura de muro; opcional |
| `floor_color` | Cor | `#464632` | Cor uniforme do chão quando não há textura de chão; opcional |
| `ceiling_color` | Cor | `#87CEEB` | Cor uniforme do teto quando não há textura de céu/teto; opcional |
| `wall_texture` | Sprite | — | Sprite para texturizar cada muro (vazio = cor uniforme); opcional |
| `sky_texture` | Sprite | — | Sprite para um céu panorâmico sobre o teto (vazio = uniforme); opcional |
| `floor_texture` | Sprite | — | Sprite projetado no chão (vazio = cor uniforme); opcional |
| `ceiling_texture` | Sprite | — | Sprite projetado no teto quando não há céu; opcional |
| `wall_textured` | Sim/Não | Sim | Desativado força cores uniformes dos muros mesmo quando há uma textura; opcional |
| `floor_cast_res` | Número | `4` | Subamostragem do chão projetado (maior = mais rápido + mais grosseiro); opcional |
| `viewport_height` | Número | `0` | Reduz a vista 3D para esta altura em pixels (letterbox), reservando a faixa inferior para uma barra de status no estilo DOOM (0 = altura total da janela, inalterado); opcional |

### Definir ângulo de visão

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_facing_angle` |
| **Ícone** | 🧭 |
| **Categoria** | Vista 3D |

Definir a direção do olhar da instância para uma câmera raycast (em primeira pessoa) — independente da velocidade de movimento

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `angle` | Número | `0` | Graus (0=direita, 90=cima, 180=esquerda, 270=baixo) |
| `relative` | Sim/Não | Não | Somar ao ângulo de visão atual em vez de substituí-lo; opcional |

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
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
