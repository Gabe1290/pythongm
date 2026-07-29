# Preset Intermediário

*[Inicio](Home_pt) | [Guia de Presets](Preset-Guide_pt) | [Preset Iniciante](Beginner-Preset_pt)*

O preset **Intermediário** se baseia no [Preset Iniciante](Beginner-Preset_pt) adicionando eventos e ações mais avançados. É projetado para usuários que dominaram o básico e querem criar jogos mais complexos com recursos como eventos temporizados, som, vidas e sistemas de saúde.

## Visão Geral

O preset Intermediário inclui tudo do Iniciante, mais:
- **4 Tipos de Eventos Adicionais** - Desenho, Destruição, Mouse, Alarme
- **12 Tipos de Ações Adicionais** - Vidas, Saúde, Som, Temporização e mais opções de movimento
- **3 Categorias Adicionais** - Temporização, Som, Desenho

---

## Eventos Adicionais (Além do Iniciante)

### Evento de Desenho
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_draw` |
| **Categoria** | Desenho |
| **Ícone** | 🎨 |
| **Descrição** | Acionado quando o objeto precisa ser renderizado |

**Quando é acionado:** A cada quadro durante a fase de desenho, após todos os eventos step.

**Importante:** Quando você adiciona um evento de Desenho, o desenho padrão do sprite é desabilitado. Você deve desenhar manualmente o sprite se quiser que ele seja visível.

**Usos comuns:**
- Renderização personalizada
- Desenhar barras de saúde
- Exibir texto
- Desenhar formas e efeitos
- Elementos de interface

---

### Evento de Destruição
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_destroy` |
| **Categoria** | Objeto |
| **Ícone** | 💥 |
| **Descrição** | Acionado quando a instância é destruída |

**Quando é acionado:** Logo antes da instância ser removida do jogo.

**Usos comuns:**
- Criar efeitos de explosão
- Soltar itens
- Tocar som de morte
- Atualizar pontuação
- Gerar partículas

---

### Evento de Mouse
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_mouse` |
| **Categoria** | Entrada |
| **Ícone** | 🖱️ |
| **Descrição** | Acionado em interações com o mouse |

**Tipos de eventos de mouse:**
- Botão esquerdo (pressionar, soltar, mantido)
- Botão direito (pressionar, soltar, mantido)
- Botão do meio (pressionar, soltar, mantido)
- Mouse entra (cursor entra na instância)
- Mouse sai (cursor sai da instância)
- Eventos de mouse globais (em qualquer lugar da tela)

**Usos comuns:**
- Botões clicáveis
- Arrastar e soltar
- Efeitos de hover
- Interações de menu

---

### Evento de Alarme
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_alarm` |
| **Categoria** | Temporização |
| **Ícone** | ⏰ |
| **Descrição** | Acionado quando um temporizador de alarme chega a zero |

**Quando é acionado:** Quando a contagem regressiva do alarme correspondente chega a 0.

**Alarmes disponíveis:** 12 alarmes independentes (0-11)

**Usos comuns:**
- Geração temporizada
- Ações atrasadas
- Tempos de recarga
- Temporização de animação
- Eventos periódicos

---

## Ações Adicionais (Além do Iniciante)

### Ações de Movimento

#### Mover em Direção
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `move_direction` |
| **Nome do Bloco** | `move_direction` |
| **Categoria** | Movimento |

**Descrição:** Definir movimento usando direção (0-360 graus) e velocidade.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `direction` | Número | Direção em graus (0=direita, 90=cima, 180=esquerda, 270=baixo) |
| `speed` | Número | Velocidade de movimento |

---

#### Mover Para um Ponto
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `move_towards_point` |
| **Nome do Bloco** | `move_towards_point` |
| **Categoria** | Movimento |

**Descrição:** Mover-se em direção a uma posição específica.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `x` | Número/Expressão | Coordenada X alvo |
| `y` | Número/Expressão | Coordenada Y alvo |
| `speed` | Número | Velocidade de movimento |

---

### Ações de Temporização

#### Definir Alarme
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `set_alarm` |
| **Nome do Bloco** | `set_alarm` |
| **Categoria** | Temporização |
| **Ícone** | ⏰ |

**Descrição:** Definir um alarme para disparar após um número de passos.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `alarm` | Número | Número do alarme (0-11) |
| `steps` | Número | Passos até o alarme disparar (a 60 FPS, 60 passos = 1 segundo) |

**Exemplo:** Definir alarme 0 para 180 passos para um atraso de 3 segundos.

---

### Ações de Vidas

#### Definir Vidas
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `set_lives` |
| **Nome do Bloco** | `lives_set` |
| **Categoria** | Pontuação/Vidas/Saúde |
| **Ícone** | ❤️ |

**Descrição:** Definir o número de vidas.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `value` | Número | Valor das vidas |
| `relative` | Booleano | Se verdadeiro, adiciona as vidas atuais |

---

#### Adicionar Vidas
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `add_lives` |
| **Nome do Bloco** | `lives_add` |
| **Categoria** | Pontuação/Vidas/Saúde |
| **Ícone** | ➕❤️ |

**Descrição:** Adicionar ou subtrair vidas.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `value` | Número | Quantidade a adicionar (negativo para subtrair) |

**Nota:** Quando as vidas chegam a 0, o evento `no_more_lives` é acionado.

---

#### Desenhar Vidas
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `draw_lives` |
| **Nome do Bloco** | `draw_lives` |
| **Categoria** | Pontuação/Vidas/Saúde |
| **Ícone** | 🖼️❤️ |

**Descrição:** Exibir vidas na tela.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `x` | Número | Posição X |
| `y` | Número | Posição Y |
| `sprite` | Sprite | Sprite opcional para usar como ícone de vida |

---

### Ações de Saúde

#### Definir Saúde
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `set_health` |
| **Nome do Bloco** | `health_set` |
| **Categoria** | Pontuação/Vidas/Saúde |
| **Ícone** | 💚 |

**Descrição:** Definir o valor da saúde (0-100).

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `value` | Número | Valor da saúde (0-100) |
| `relative` | Booleano | Se verdadeiro, adiciona a saúde atual |

---

#### Adicionar Saúde
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `add_health` |
| **Nome do Bloco** | `health_add` |
| **Categoria** | Pontuação/Vidas/Saúde |
| **Ícone** | ➕💚 |

**Descrição:** Adicionar ou subtrair saúde.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `value` | Número | Quantidade a adicionar (negativo para dano) |

**Nota:** Quando a saúde chega a 0, o evento `no_more_health` é acionado.

---

#### Desenhar Barra de Saúde
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `draw_health_bar` |
| **Nome do Bloco** | `draw_health_bar` |
| **Categoria** | Pontuação/Vidas/Saúde |
| **Ícone** | 📊💚 |

**Descrição:** Desenhar uma barra de saúde na tela.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `x1` | Número | Posição X esquerda |
| `y1` | Número | Posição Y superior |
| `x2` | Número | Posição X direita |
| `y2` | Número | Posição Y inferior |
| `back_color` | Cor | Cor de fundo |
| `bar_color` | Cor | Cor da barra de saúde |

---

### Ações de Som

#### Reproduzir Som
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `play_sound` |
| **Nome do Bloco** | `sound_play` |
| **Categoria** | Som |
| **Ícone** | 🔊 |

**Descrição:** Reproduzir um efeito sonoro.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `sound` | Som | Recurso de som a reproduzir |
| `loop` | Booleano | Se o som deve repetir em loop |

---

#### Reproduzir Música
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `play_music` |
| **Nome do Bloco** | `music_play` |
| **Categoria** | Som |
| **Ícone** | 🎵 |

**Descrição:** Reproduzir música de fundo.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `sound` | Som | Recurso de música a reproduzir |
| `loop` | Booleano | Se deve repetir (geralmente verdadeiro para música) |

---

#### Parar Música
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `stop_music` |
| **Nome do Bloco** | `music_stop` |
| **Categoria** | Som |
| **Ícone** | 🔇 |

**Descrição:** Parar toda a música em reprodução.

**Parâmetros:** Nenhum

---

## Lista Completa de Recursos

### Eventos no Preset Intermediário

| Evento | Categoria | Descrição |
|--------|-----------|-----------|
| Create | Objeto | Instancia criada |
| Step | Objeto | Cada quadro |
| Destroy | Objeto | Instancia destruída |
| Draw | Desenho | Fase de renderização |
| Keyboard Press | Entrada | Tecla pressionada uma vez |
| Mouse | Entrada | Interações de mouse |
| Collision | Colisão | Sobreposição de instâncias |
| Alarm | Temporização | Temporizador chegou a zero |

### Ações no Preset Intermediário

| Categoria | Ações |
|-----------|-------|
| **Movimento** | Set H/V Speed, Stop, Jump To, Move Direction, Move Towards Point |
| **Instancia** | Create, Destroy |
| **Pontuação** | Set Score, Add Score, Draw Score |
| **Vidas** | Set Lives, Add Lives, Draw Lives |
| **Saúde** | Set Health, Add Health, Draw Health Bar |
| **Sala** | Next, Previous, Restart, Go To, If Next/Previous Exists |
| **Temporização** | Set Alarm |
| **Som** | Play Sound, Play Music, Stop Music |
| **Saida** | Show Message, Execute Code |

---

## Exemplo: Jogo de Tiro com Vidas

### Objeto Jogador

**Create:**
- Set Lives: 3

**Keyboard Press (Espaco):**
- Create Instance: obj_bullet em (x, y-20)
- Set Alarm: 0 para 15 (tempo de recarga)

**Colisão com obj_enemy:**
- Add Lives: -1
- Play Sound: snd_hurt
- Jump to Position: (320, 400)

**No More Lives:**
- Show Message: "Game Over!"
- Restart Room

### Objeto Inimigo

**Create:**
- Set Alarm: 0 para 60

**Alarm 0:**
- Create Instance: obj_enemy_bullet em (x, y+20)
- Set Alarm: 0 para 60 (repetir)

**Colisão com obj_bullet:**
- Add Score: 100
- Play Sound: snd_explosion
- Destroy Instance: self

---

## Atualizando para Presets Avancados

Quando precisar de mais recursos, considere:
- **Preset Plataforma** - Gravidade, pulo, mecanicas de plataforma
- **Preset Completo** - Todos os eventos e ações disponíveis

---

## Veja Tambem

- [Preset Iniciante](Beginner-Preset_pt) - Comece aqui se for novo
- [Referencia Completa de Ações](Full-Action-Reference_pt) - Lista completa de ações
- [Referencia de Eventos](Event-Reference_pt) - Lista completa de eventos
- [Eventos e Ações](Eventos_e_Acoes_pt) - Conceitos básicos
