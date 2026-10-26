# Desenho

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Desenhar seta

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_arrow` |
| **Ícone** | ➡️ |
| **Categoria** | Desenho |

Desenhar uma seta de um ponto a outro

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x1` | Número | `0` | X inicial |
| `y1` | Número | `0` | Y inicial |
| `x2` | Número | `100` | X ponta |
| `y2` | Número | `100` | Y ponta |
| `tip_size` | Número | `10` | Tamanho da ponta da seta em pixels |

### Desenhar fundo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_background` |
| **Ícone** | 🌄 |
| **Categoria** | Desenho |

Desenhar uma imagem de fundo, opcionalmente ladrilhada por toda a tela

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `background` | Texto | — | Nome do recurso de fundo |
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `tiled` | Sim/Não | Não | Ladrilhar por toda a tela; opcional |

### Desenhar elipse

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_ellipse` |
| **Ícone** | 🥚 |
| **Categoria** | Desenho |

Desenhar uma elipse preenchida ou apenas contorno dentro de uma caixa

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x1` | Número | `0` | X esquerda |
| `y1` | Número | `0` | Y superior |
| `x2` | Número | `100` | X direita |
| `y2` | Número | `100` | Y inferior |
| `filled` | Sim/Não | Sim | Preenchido ou apenas contorno; opcional |

### Desenhar linha

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_line` |
| **Ícone** | 📏 |
| **Categoria** | Desenho |

Desenhar uma linha entre dois pontos

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x1` | Número | `0` | X inicial |
| `y1` | Número | `0` | Y inicial |
| `x2` | Número | `100` | X final |
| `y2` | Número | `100` | Y final |

### Desenhar texto escalado

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_scaled_text` |
| **Ícone** | 🖍️ |
| **Categoria** | Desenho |

Desenhar texto em uma escala arbitrária

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `text` | Texto | — | Texto a desenhar |
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `xscale` | Número | `1.0` | Fator de escala horizontal |
| `yscale` | Número | `1.0` | Fator de escala vertical |

### Desenhar sprite

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_sprite` |
| **Ícone** | 🖼️ |
| **Categoria** | Desenho |

Desenhar um quadro de sprite em uma posição

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite a desenhar |
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `subimage` | Número | `0` | Índice do quadro a desenhar |

### Desenhar variável

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_variable` |
| **Ícone** | 🔢 |
| **Categoria** | Desenho |

Desenhar o valor de uma variável na tela

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `variable` | Texto | — | Nome da variável (self.var, global.var ou nome simples) |

### Preencher tela com cor

| Propriedade | Valor |
|----------|-------|
| **Nome** | `fill_color` |
| **Ícone** | 🪣 |
| **Categoria** | Desenho |

Preencher toda a área de visualização com uma cor uniforme

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `color` | Cor | `#000000` | Cor RGB hexadecimal |

### Definir cor

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_color` |
| **Ícone** | 🎨 |
| **Categoria** | Desenho |

Definir a cor e a transparência de desenho para os desenhos seguintes

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `color` | Cor | `#FFFFFF` | Cor RGB hexadecimal |
| `alpha` | Número | `1.0` | Opacidade 0.0–1.0; opcional |

### Definir cor de desenho

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_draw_color` |
| **Ícone** | 🎨 |
| **Categoria** | Desenho |

Definir a cor usada pelas ações draw_* seguintes

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `color` | Cor | `#000000` | Cor RGB hexadecimal |

### Definir fonte de desenho

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_draw_font` |
| **Ícone** | 🔤 |
| **Categoria** | Desenho |

Definir a fonte e o alinhamento para o desenho de texto seguinte

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `font` | Texto | — | Nome do recurso de fonte (vazio = fonte padrão); opcional |
| `halign` | Escolha | `left` | Alinhamento horizontal do texto; Opções: `left`, `center`, `right` |
| `valign` | Escolha | `top` | Alinhamento vertical do texto; Opções: `top`, `middle`, `bottom` |

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
- [Rede](Full-Action-Reference-Network-Actions_pt) (22)
- [Partículas](Full-Action-Reference-Particles_pt) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_pt) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_pt) (16)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
