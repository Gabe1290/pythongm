# Jogo

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

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
| `color` | Cor | — | Cor do texto (por ex. #ffffff). Vazio = a cor de desenho ativa, ou preto.; opcional |

### Carregar o jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `load_game` |
| **Ícone** | 📂 |
| **Categoria** | Jogo |

Repõe a sala, a pontuação, as vidas, a saúde, as variáveis globais e o estado das instâncias a partir de um ficheiro guardado

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `filename` | Texto | `savegame.sav` | Nome do ficheiro guardado a carregar (da pasta saves/ do projeto) |

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

### Guardar o jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `save_game` |
| **Ícone** | 💾 |
| **Categoria** | Jogo |

Guarda num ficheiro a sala atual, a pontuação, as vidas, a saúde, as variáveis globais e o estado das instâncias

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `filename` | Texto | `savegame.sav` | Nome do ficheiro de gravação (escrito na pasta saves/ do projeto) |

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

### Mostrar um vídeo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `show_video` |
| **Ícone** | 🎬 |
| **Categoria** | Jogo |

Reproduz um ficheiro de vídeo no leitor de vídeo predefinido do sistema: abre numa janela separada, não é desenhado dentro do próprio jogo

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `filename` | Texto | — | Caminho para o ficheiro de vídeo |
| `fullscreen` | Sim/Não | Não | Pedir reprodução em ecrã inteiro (depende do leitor do teu sistema); opcional |

### Ecrã: mostrar imagem

| Propriedade | Valor |
|----------|-------|
| **Nome** | `splash_show_image` |
| **Ícone** | 🖼️ |
| **Categoria** | Jogo |

Mostra um sprite em ecrã inteiro e põe o jogo em pausa até o jogador o fechar

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `image` | Sprite | — | Sprite a mostrar em ecrã inteiro |

### Ecrã: mostrar texto

| Propriedade | Valor |
|----------|-------|
| **Nome** | `splash_show_text` |
| **Ícone** | 💬 |
| **Categoria** | Jogo |

Mostra uma mensagem e põe o jogo em pausa até o jogador a fechar

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `text` | Texto | — | Mensagem a mostrar |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (21)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (6)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (8)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
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
