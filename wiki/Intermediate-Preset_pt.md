# Preset Intermediario

*[Inicio](Home_pt) | [Guia de Presets](Preset-Guide_pt) | [Preset Iniciante](Beginner-Preset_pt)*

O preset **Intermediario** se baseia no [Preset Iniciante](Beginner-Preset_pt) adicionando eventos e acoes mais avancados. E projetado para usuarios que dominaram o basico e querem criar jogos mais complexos com recursos como eventos temporizados, som, vidas e sistemas de saude.

## Visao Geral

O preset Intermediario inclui tudo do Iniciante, mais:
- **4 Tipos de Eventos Adicionais** - Desenho, Destruicao, Mouse, Alarme
- **12 Tipos de Acoes Adicionais** - Vidas, Saude, Som, Temporizacao e mais opcoes de movimento
- **3 Categorias Adicionais** - Temporizacao, Som, Desenho

---

## Eventos Adicionais (Alem do Iniciante)

### Evento de Desenho
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_draw` |
| **Categoria** | Desenho |
| **Icone** | 🎨 |
| **Descricao** | Acionado quando o objeto precisa ser renderizado |

**Quando e acionado:** A cada quadro durante a fase de desenho, apos todos os eventos step.

**Importante:** Quando voce adiciona um evento de Desenho, o desenho padrao do sprite e desabilitado. Voce deve desenhar manualmente o sprite se quiser que ele seja visivel.

**Usos comuns:**
- Renderizacao personalizada
- Desenhar barras de saude
- Exibir texto
- Desenhar formas e efeitos
- Elementos de interface

---

### Evento de Destruicao
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_destroy` |
| **Categoria** | Objeto |
| **Icone** | 💥 |
| **Descricao** | Acionado quando a instancia e destruida |

**Quando e acionado:** Logo antes da instancia ser removida do jogo.

**Usos comuns:**
- Criar efeitos de explosao
- Soltar itens
- Tocar som de morte
- Atualizar pontuacao
- Gerar particulas

---

### Evento de Mouse
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_mouse` |
| **Categoria** | Entrada |
| **Icone** | 🖱️ |
| **Descricao** | Acionado em interacoes com o mouse |

**Tipos de eventos de mouse:**
- Botao esquerdo (pressionar, soltar, mantido)
- Botao direito (pressionar, soltar, mantido)
- Botao do meio (pressionar, soltar, mantido)
- Mouse entra (cursor entra na instancia)
- Mouse sai (cursor sai da instancia)
- Eventos de mouse globais (em qualquer lugar da tela)

**Usos comuns:**
- Botoes clicaveis
- Arrastar e soltar
- Efeitos de hover
- Interacoes de menu

---

### Evento de Alarme
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_alarm` |
| **Categoria** | Temporizacao |
| **Icone** | ⏰ |
| **Descricao** | Acionado quando um temporizador de alarme chega a zero |

**Quando e acionado:** Quando a contagem regressiva do alarme correspondente chega a 0.

**Alarmes disponiveis:** 12 alarmes independentes (0-11)

**Usos comuns:**
- Geracao temporizada
- Acoes atrasadas
- Tempos de recarga
- Temporizacao de animacao
- Eventos periodicos

---

## Acoes Adicionais (Alem do Iniciante)

### Acoes de Movimento

#### Mover em Direcao
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `move_direction` |
| **Nome do Bloco** | `move_direction` |
| **Categoria** | Movimento |

**Descricao:** Definir movimento usando direcao (0-360 graus) e velocidade.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `direction` | Numero | Direcao em graus (0=direita, 90=cima, 180=esquerda, 270=baixo) |
| `speed` | Numero | Velocidade de movimento |

---

#### Mover Para um Ponto
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `move_towards` |
| **Nome do Bloco** | `move_towards` |
| **Categoria** | Movimento |

**Descricao:** Mover-se em direcao a uma posicao especifica.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `x` | Numero/Expressao | Coordenada X alvo |
| `y` | Numero/Expressao | Coordenada Y alvo |
| `speed` | Numero | Velocidade de movimento |

---

### Acoes de Temporizacao

#### Definir Alarme
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `set_alarm` |
| **Nome do Bloco** | `set_alarm` |
| **Categoria** | Temporizacao |
| **Icone** | ⏰ |

**Descricao:** Definir um alarme para disparar apos um numero de passos.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `alarm` | Numero | Numero do alarme (0-11) |
| `steps` | Numero | Passos ate o alarme disparar (a 60 FPS, 60 passos = 1 segundo) |

**Exemplo:** Definir alarme 0 para 180 passos para um atraso de 3 segundos.

---

### Acoes de Vidas

#### Definir Vidas
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `set_lives` |
| **Nome do Bloco** | `lives_set` |
| **Categoria** | Pontuacao/Vidas/Saude |
| **Icone** | ❤️ |

**Descricao:** Definir o numero de vidas.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `value` | Numero | Valor das vidas |
| `relative` | Booleano | Se verdadeiro, adiciona as vidas atuais |

---

#### Adicionar Vidas
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `add_lives` |
| **Nome do Bloco** | `lives_add` |
| **Categoria** | Pontuacao/Vidas/Saude |
| **Icone** | ➕❤️ |

**Descricao:** Adicionar ou subtrair vidas.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `value` | Numero | Quantidade a adicionar (negativo para subtrair) |

**Nota:** Quando as vidas chegam a 0, o evento `no_more_lives` e acionado.

---

#### Desenhar Vidas
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `draw_lives` |
| **Nome do Bloco** | `draw_lives` |
| **Categoria** | Pontuacao/Vidas/Saude |
| **Icone** | 🖼️❤️ |

**Descricao:** Exibir vidas na tela.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `x` | Numero | Posicao X |
| `y` | Numero | Posicao Y |
| `sprite` | Sprite | Sprite opcional para usar como icone de vida |

---

### Acoes de Saude

#### Definir Saude
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `set_health` |
| **Nome do Bloco** | `health_set` |
| **Categoria** | Pontuacao/Vidas/Saude |
| **Icone** | 💚 |

**Descricao:** Definir o valor da saude (0-100).

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `value` | Numero | Valor da saude (0-100) |
| `relative` | Booleano | Se verdadeiro, adiciona a saude atual |

---

#### Adicionar Saude
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `add_health` |
| **Nome do Bloco** | `health_add` |
| **Categoria** | Pontuacao/Vidas/Saude |
| **Icone** | ➕💚 |

**Descricao:** Adicionar ou subtrair saude.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `value` | Numero | Quantidade a adicionar (negativo para dano) |

**Nota:** Quando a saude chega a 0, o evento `no_more_health` e acionado.

---

#### Desenhar Barra de Saude
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `draw_health_bar` |
| **Nome do Bloco** | `draw_health_bar` |
| **Categoria** | Pontuacao/Vidas/Saude |
| **Icone** | 📊💚 |

**Descricao:** Desenhar uma barra de saude na tela.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `x1` | Numero | Posicao X esquerda |
| `y1` | Numero | Posicao Y superior |
| `x2` | Numero | Posicao X direita |
| `y2` | Numero | Posicao Y inferior |
| `back_color` | Cor | Cor de fundo |
| `bar_color` | Cor | Cor da barra de saude |

---

### Acoes de Som

#### Reproduzir Som
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `play_sound` |
| **Nome do Bloco** | `sound_play` |
| **Categoria** | Som |
| **Icone** | 🔊 |

**Descricao:** Reproduzir um efeito sonoro.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `sound` | Som | Recurso de som a reproduzir |
| `loop` | Booleano | Se o som deve repetir em loop |

---

#### Reproduzir Musica
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `play_music` |
| **Nome do Bloco** | `music_play` |
| **Categoria** | Som |
| **Icone** | 🎵 |

**Descricao:** Reproduzir musica de fundo.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `sound` | Som | Recurso de musica a reproduzir |
| `loop` | Booleano | Se deve repetir (geralmente verdadeiro para musica) |

---

#### Parar Musica
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `stop_music` |
| **Nome do Bloco** | `music_stop` |
| **Categoria** | Som |
| **Icone** | 🔇 |

**Descricao:** Parar toda a musica em reproducao.

**Parametros:** Nenhum

---

## Lista Completa de Recursos

### Eventos no Preset Intermediario

| Evento | Categoria | Descricao |
|--------|-----------|-----------|
| Create | Objeto | Instancia criada |
| Step | Objeto | Cada quadro |
| Destroy | Objeto | Instancia destruida |
| Draw | Desenho | Fase de renderizacao |
| Keyboard Press | Entrada | Tecla pressionada uma vez |
| Mouse | Entrada | Interacoes de mouse |
| Collision | Colisao | Sobreposicao de instancias |
| Alarm | Temporizacao | Temporizador chegou a zero |

### Acoes no Preset Intermediario

| Categoria | Acoes |
|-----------|-------|
| **Movimento** | Set H/V Speed, Stop, Jump To, Move Direction, Move Towards |
| **Instancia** | Create, Destroy |
| **Pontuacao** | Set Score, Add Score, Draw Score |
| **Vidas** | Set Lives, Add Lives, Draw Lives |
| **Saude** | Set Health, Add Health, Draw Health Bar |
| **Sala** | Next, Previous, Restart, Go To, If Next/Previous Exists |
| **Temporizacao** | Set Alarm |
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

**Colisao com obj_enemy:**
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

**Colisao com obj_bullet:**
- Add Score: 100
- Play Sound: snd_explosion
- Destroy Instance: self

---

## Atualizando para Presets Avancados

Quando precisar de mais recursos, considere:
- **Preset Plataforma** - Gravidade, pulo, mecanicas de plataforma
- **Preset Completo** - Todos os eventos e acoes disponiveis

---

## Veja Tambem

- [Preset Iniciante](Beginner-Preset_pt) - Comece aqui se for novo
- [Referencia Completa de Acoes](Full-Action-Reference_pt) - Lista completa de acoes
- [Referencia de Eventos](Event-Reference_pt) - Lista completa de eventos
- [Eventos e Acoes](Events-and-Actions_pt) - Conceitos basicos
