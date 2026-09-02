# Jogo

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Desenhar seta

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_arrow` |
| **Ícone** | ➡️ |
| **Categoria** | Jogo |

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
| **Categoria** | Jogo |

Desenhar uma imagem de fundo, opcionalmente ladrilhada por toda a tela

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `background` | Texto | — | Nome do recurso de fundo |
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `tiled` | Sim/Não | Não | Ladrilhar por toda a tela; opcional |

### Desenhar círculo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_circle` |
| **Ícone** | ⭕ |
| **Categoria** | Jogo |

Desenhar um círculo preenchido ou apenas contorno

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | X centro |
| `y` | Número | `0` | Y centro |
| `radius` | Número | `50` | Raio do círculo |
| `filled` | Sim/Não | Sim | Preenchido ou apenas contorno; opcional |

### Desenhar elipse

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_ellipse` |
| **Ícone** | 🥚 |
| **Categoria** | Jogo |

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
| **Categoria** | Jogo |

Desenhar uma linha entre dois pontos

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x1` | Número | `0` | X inicial |
| `y1` | Número | `0` | Y inicial |
| `x2` | Número | `100` | X final |
| `y2` | Número | `100` | Y final |

### Desenhar retângulo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_rectangle` |
| **Ícone** | 🟥 |
| **Categoria** | Jogo |

Desenhar um retângulo preenchido ou apenas contorno

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x1` | Número | `0` | X esquerda |
| `y1` | Número | `0` | Y superior |
| `x2` | Número | `100` | X direita |
| `y2` | Número | `100` | Y inferior |
| `filled` | Sim/Não | Sim | Preenchido ou apenas contorno; opcional |

### Desenhar texto escalado

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_scaled_text` |
| **Ícone** | 🖍️ |
| **Categoria** | Jogo |

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
| **Categoria** | Jogo |

Desenhar um quadro de sprite em uma posição

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite a desenhar |
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `subimage` | Número | `0` | Índice do quadro a desenhar |

### Desenhar texto

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_text` |
| **Ícone** | 🖍️ |
| **Categoria** | Jogo |

Desenhar uma cadeia de texto em uma posição

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `text` | Texto | — | Texto a desenhar (suporta expressões) |
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `relative` | Sim/Não | Não | Desenhar em relação à posição desta instância em vez de coordenadas de tela absolutas; opcional |

### Desenhar variável

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_variable` |
| **Ícone** | 🔢 |
| **Categoria** | Jogo |

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
| **Categoria** | Jogo |

Preencher toda a área de visualização com uma cor uniforme

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `color` | Cor | `#000000` | Cor RGB hexadecimal |

### Load Game

| Propriedade | Valor |
|----------|-------|
| **Nome** | `load_game` |
| **Ícone** | 📂 |
| **Categoria** | Jogo |

Restore room, score/lives/health, global variables, and instance states from a save file

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `filename` | Texto | `savegame.sav` | Save file name to load (from the project's saves/ folder) |

### Abrir página web

| Propriedade | Valor |
|----------|-------|
| **Nome** | `open_webpage` |
| **Ícone** | 🌐 |
| **Categoria** | Jogo |

Abrir uma URL no navegador padrão

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `url` | Texto | — | Endereço web a abrir |

### Reiniciar jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `restart_game` |
| **Ícone** | 🔁🎮 |
| **Categoria** | Jogo |

Reiniciar o jogo a partir da sala inicial

*Parâmetros:* nenhum

### Save Game

| Propriedade | Valor |
|----------|-------|
| **Nome** | `save_game` |
| **Ícone** | 💾 |
| **Categoria** | Jogo |

Save the current room, score/lives/health, global variables, and instance states to a file

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `filename` | Texto | `savegame.sav` | Save file name (written to the project's saves/ folder) |

### Definir transparência

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_alpha` |
| **Ícone** | 🌫️ |
| **Categoria** | Jogo |

Definir a transparência de desenho para os desenhos seguintes

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `alpha` | Número | `1.0` | Opacidade de 0.0 (transparente) a 1.0 (opaco) |

### Definir cor

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_color` |
| **Ícone** | 🎨 |
| **Categoria** | Jogo |

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
| **Categoria** | Jogo |

Definir a cor usada pelas ações draw_* seguintes

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `color` | Cor | `#000000` | Cor RGB hexadecimal |

### Definir fonte de desenho

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_draw_font` |
| **Ícone** | 🔤 |
| **Categoria** | Jogo |

Definir a fonte e o alinhamento para o desenho de texto seguinte

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `font` | Texto | — | Nome do recurso de fonte (vazio = fonte padrão); opcional |
| `halign` | Escolha | `left` | Alinhamento horizontal do texto; Opções: `left`, `center`, `right` |
| `valign` | Escolha | `top` | Alinhamento vertical do texto; Opções: `top`, `middle`, `bottom` |

### Definir título da janela

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_window_caption` |
| **Ícone** | 🪟 |
| **Categoria** | Jogo |

Configurar a exibição de pontuação/vidas/saúde no título da janela

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `show_score` | Sim/Não | Sim | Adicionar a pontuação atual ao título da janela |
| `show_lives` | Sim/Não | Sim | Adicionar o número de vidas atual ao título da janela |
| `show_health` | Sim/Não | Não | Adicionar o valor de saúde atual ao título da janela |
| `caption` | Texto | — | Prefixo de título opcional mostrado antes dos contadores; opcional |

### Mostrar informações do jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `show_info` |
| **Ícone** | ℹ️ |
| **Categoria** | Jogo |

Mostrar a tela de informações do jogo

*Parâmetros:* nenhum

### Mostrar mensagem

| Propriedade | Valor |
|----------|-------|
| **Nome** | `show_message` |
| **Ícone** | 💬 |
| **Categoria** | Jogo |

Mostrar uma mensagem

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `message` | Texto | `Hello!` | Texto da mensagem |

### Show Video

| Propriedade | Valor |
|----------|-------|
| **Nome** | `show_video` |
| **Ícone** | 🎬 |
| **Categoria** | Jogo |

Play a video file in your system's default video player -- opens as a separate window, not rendered inside the game itself

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `filename` | Texto | — | Path to the video file |
| `fullscreen` | Sim/Não | Não | Request fullscreen playback (support depends on your system's player); opcional |

### Splash: Show Image

| Propriedade | Valor |
|----------|-------|
| **Nome** | `splash_show_image` |
| **Ícone** | 🖼️ |
| **Categoria** | Jogo |

Show a sprite full-screen and pause the game until the player dismisses it

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `image` | Sprite | — | Sprite to display full-screen |

### Splash: Show Text

| Propriedade | Valor |
|----------|-------|
| **Nome** | `splash_show_text` |
| **Ícone** | 💬 |
| **Categoria** | Jogo |

Show a message and pause the game until the player dismisses it

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `text` | Texto | — | Message to display |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (8)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (16)
- [Particles](Full-Action-Reference-Particles_pt) (8)
- [Réseau](Full-Action-Reference-Network-Actions_pt) (15)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
