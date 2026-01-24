# Preset para Iniciantes

*[Home](Home_pt) | [Guia de Presets](Preset-Guide_pt) | [Preset Intermediario](Intermediate-Preset_pt)*

O preset **Iniciante** foi projetado para usuarios que sao novos no desenvolvimento de jogos. Ele fornece um conjunto selecionado de eventos e acoes essenciais que cobrem os fundamentos da criacao de jogos 2D simples sem sobrecarregar iniciantes com muitas opcoes.

## Visao Geral

O preset Iniciante inclui:
- **4 Tipos de Eventos** - Para responder a situacoes do jogo
- **17 Tipos de Acoes** - Para controlar o comportamento do jogo
- **6 Categorias** - Eventos, Movimento, Pontuacao/Vidas/Saude, Instancia, Sala, Saida

---

## Eventos

Eventos sao gatilhos que respondem a situacoes especificas no seu jogo. Quando um evento ocorre, as acoes que voce definiu para esse evento serao executadas.

### Evento Create
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_create` |
| **Categoria** | Eventos |
| **Descricao** | Disparado uma vez quando uma instancia e criada pela primeira vez |

**Quando e disparado:** Imediatamente quando uma instancia de objeto e colocada em uma sala ou criada com a acao "Criar Instancia".

**Usos comuns:**
- Inicializar variaveis
- Definir posicao inicial
- Definir velocidade ou direcao inicial
- Resetar pontuacao no inicio do jogo

---

### Evento Step
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_step` |
| **Categoria** | Eventos |
| **Descricao** | Disparado a cada quadro (tipicamente 60 vezes por segundo) |

**Quando e disparado:** Continuamente, a cada quadro do jogo.

**Usos comuns:**
- Movimento continuo
- Verificar condicoes
- Atualizar estado do jogo
- Controle de animacao

---

### Evento de Tecla Pressionada
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_keyboard_press` |
| **Categoria** | Eventos |
| **Descricao** | Disparado uma vez quando uma tecla especifica e pressionada |

**Quando e disparado:** Uma vez no momento em que uma tecla e pressionada (nao enquanto mantida).

**Teclas suportadas:** Teclas de seta (cima, baixo, esquerda, direita), Espaco, Enter, letras (A-Z), numeros (0-9)

**Usos comuns:**
- Controles de movimento do jogador
- Pular
- Atirar
- Navegacao de menu

---

### Evento de Colisao
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_collision` |
| **Categoria** | Eventos |
| **Descricao** | Disparado quando esta instancia colide com outro objeto |

**Quando e disparado:** A cada quadro em que duas instancias estao sobrepostas.

**Variavel especial:** Em um evento de colisao, `other` refere-se a instancia com a qual esta colidindo.

**Usos comuns:**
- Coletar itens (moedas, power-ups)
- Receber dano de inimigos
- Bater em paredes ou obstaculos
- Alcancar objetivos ou checkpoints

---

## Acoes

Acoes sao comandos que executam quando um evento e disparado. Multiplas acoes podem ser adicionadas a um unico evento e serao executadas em ordem.

---

## Acoes de Movimento

### Definir Velocidade Horizontal
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `set_hspeed` |
| **Nome do Bloco** | `move_set_hspeed` |
| **Categoria** | Movimento |
| **Icone** | ↔️ |

**Descricao:** Define a velocidade de movimento horizontal da instancia.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `value` | Numero | Velocidade em pixels por quadro. Positivo = direita, Negativo = esquerda |

**Exemplo:** Defina `value` como `4` para mover para a direita a 4 pixels por quadro, ou `-4` para mover para a esquerda.

---

### Definir Velocidade Vertical
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `set_vspeed` |
| **Nome do Bloco** | `move_set_vspeed` |
| **Categoria** | Movimento |
| **Icone** | ↕️ |

**Descricao:** Define a velocidade de movimento vertical da instancia.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `value` | Numero | Velocidade em pixels por quadro. Positivo = baixo, Negativo = cima |

**Exemplo:** Defina `value` como `-4` para mover para cima a 4 pixels por quadro, ou `4` para mover para baixo.

---

### Parar Movimento
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `stop_movement` |
| **Nome do Bloco** | `move_stop` |
| **Categoria** | Movimento |
| **Icone** | 🛑 |

**Descricao:** Para todo movimento definindo velocidade horizontal e vertical como zero.

**Parametros:** Nenhum

**Usos comuns:**
- Parar jogador ao bater em uma parede
- Parar inimigos ao alcancar um destino
- Pausar movimento temporariamente

---

### Saltar para Posicao
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `jump_to_position` |
| **Nome do Bloco** | `move_jump_to` |
| **Categoria** | Movimento |
| **Icone** | 📍 |

**Descricao:** Move a instancia instantaneamente para uma posicao especifica (sem movimento suave).

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `x` | Numero | Coordenada X de destino |
| `y` | Numero | Coordenada Y de destino |

**Exemplo:** Saltar para posicao (100, 200) para teletransportar o jogador para aquela localizacao.

---

## Acoes de Instancia

### Destruir Instancia
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `destroy_instance` |
| **Nome do Bloco** | `instance_destroy` |
| **Categoria** | Instancia |
| **Icone** | 💥 |

**Descricao:** Remove uma instancia do jogo.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `target` | Escolha | `self` = destruir esta instancia, `other` = destruir a instancia colidida |

**Usos comuns:**
- Remover moedas coletadas (`target: other` no evento de colisao)
- Destruir balas ao atingir algo
- Remover inimigos quando derrotados

---

### Criar Instancia
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `create_instance` |
| **Nome do Bloco** | `instance_create` |
| **Categoria** | Instancia |
| **Icone** | ✨ |

**Descricao:** Cria uma nova instancia de um objeto em uma posicao especificada.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `object` | Objeto | O tipo de objeto a criar |
| `x` | Numero | Coordenada X para a nova instancia |
| `y` | Numero | Coordenada Y para a nova instancia |

**Exemplo:** Criar uma bala na posicao do jogador quando Espaco e pressionado.

---

## Acoes de Pontuacao

### Definir Pontuacao
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `set_score` |
| **Nome do Bloco** | `score_set` |
| **Categoria** | Pontuacao/Vidas/Saude |
| **Icone** | 🏆 |

**Descricao:** Define a pontuacao para um valor especifico, ou adiciona/subtrai da pontuacao atual.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `value` | Numero | O valor da pontuacao |
| `relative` | Booleano | Se verdadeiro, adiciona valor a pontuacao atual. Se falso, define pontuacao como valor |

**Exemplos:**
- Resetar pontuacao: `value: 0`, `relative: false`
- Adicionar 10 pontos: `value: 10`, `relative: true`
- Subtrair 5 pontos: `value: -5`, `relative: true`

---

### Adicionar a Pontuacao
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `add_score` |
| **Nome do Bloco** | `score_add` |
| **Categoria** | Pontuacao/Vidas/Saude |
| **Icone** | ➕🏆 |

**Descricao:** Adiciona um valor a pontuacao atual (atalho para set_score com relative=true).

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `value` | Numero | Pontos a adicionar (pode ser negativo para subtrair) |

---

### Desenhar Pontuacao
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `draw_score` |
| **Nome do Bloco** | `draw_score` |
| **Categoria** | Pontuacao/Vidas/Saude |
| **Icone** | 🖼️🏆 |

**Descricao:** Exibe a pontuacao atual na tela.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `x` | Numero | Posicao X para desenhar a pontuacao |
| `y` | Numero | Posicao Y para desenhar a pontuacao |
| `caption` | String | Texto a exibir antes da pontuacao (ex: "Pontuacao: ") |

**Nota:** Isso deve ser usado em um evento Draw (disponivel no preset Intermediario).

---

## Acoes de Sala

### Ir para Proxima Sala
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `next_room` |
| **Nome do Bloco** | `room_goto_next` |
| **Categoria** | Sala |
| **Icone** | ➡️ |

**Descricao:** Transiciona para a proxima sala na ordem das salas.

**Parametros:** Nenhum

**Nota:** Se ja estiver na ultima sala, esta acao nao tem efeito (use "Se Proxima Sala Existe" para verificar primeiro).

---

### Ir para Sala Anterior
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `previous_room` |
| **Nome do Bloco** | `room_goto_previous` |
| **Categoria** | Sala |
| **Icone** | ⬅️ |

**Descricao:** Transiciona para a sala anterior na ordem das salas.

**Parametros:** Nenhum

**Nota:** Se ja estiver na primeira sala, esta acao nao tem efeito.

---

### Reiniciar Sala
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `restart_room` |
| **Nome do Bloco** | `room_restart` |
| **Categoria** | Sala |
| **Icone** | 🔄 |

**Descricao:** Reinicia a sala atual, resetando todas as instancias para seu estado inicial.

**Parametros:** Nenhum

**Usos comuns:**
- Reiniciar nivel apos jogador morrer
- Resetar quebra-cabeca apos falha
- Repetir mini-jogo

---

### Ir para Sala
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `goto_room` |
| **Nome do Bloco** | `room_goto` |
| **Categoria** | Sala |
| **Icone** | 🚪 |

**Descricao:** Transiciona para uma sala especifica pelo nome.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `room` | Sala | A sala para onde ir |

---

### Se Proxima Sala Existe
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `if_next_room_exists` |
| **Nome do Bloco** | `room_if_next_exists` |
| **Categoria** | Sala |
| **Icone** | ❓➡️ |

**Descricao:** Bloco condicional que so executa acoes contidas se houver uma proxima sala.

**Parametros:** Nenhum (acoes sao colocadas dentro do bloco)

**Usos comuns:**
- Verificar antes de ir para proxima sala
- Mostrar mensagem "Voce Venceu!" se nao houver mais salas

---

### Se Sala Anterior Existe
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `if_previous_room_exists` |
| **Nome do Bloco** | `room_if_previous_exists` |
| **Categoria** | Sala |
| **Icone** | ❓⬅️ |

**Descricao:** Bloco condicional que so executa acoes contidas se houver uma sala anterior.

**Parametros:** Nenhum (acoes sao colocadas dentro do bloco)

---

## Acoes de Saida

### Mostrar Mensagem
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `show_message` |
| **Nome do Bloco** | `output_message` |
| **Categoria** | Saida |
| **Icone** | 💬 |

**Descricao:** Exibe uma caixa de dialogo popup para o jogador.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `message` | String | O texto a exibir |

**Nota:** O jogo pausa enquanto a mensagem e exibida. O jogador deve clicar OK para continuar.

**Usos comuns:**
- Instrucoes do jogo
- Dialogo da historia
- Mensagens de vitoria/derrota
- Informacoes de debug

---

### Executar Codigo
| Propriedade | Valor |
|-------------|-------|
| **Nome da Acao** | `execute_code` |
| **Nome do Bloco** | `execute_code` |
| **Categoria** | Saida |
| **Icone** | 💻 |

**Descricao:** Executa codigo Python personalizado.

**Parametros:**
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `code` | String | Codigo Python a executar |

**Nota:** Este e um recurso avancado. Use com cautela pois codigo incorreto pode causar erros.

---

## Resumo das Categorias

| Categoria | Eventos | Acoes |
|-----------|---------|-------|
| **Eventos** | Create, Step, Tecla Pressionada, Colisao | - |
| **Movimento** | - | Definir Velocidade Horizontal, Definir Velocidade Vertical, Parar Movimento, Saltar para Posicao |
| **Instancia** | - | Destruir Instancia, Criar Instancia |
| **Pontuacao/Vidas/Saude** | - | Definir Pontuacao, Adicionar Pontuacao, Desenhar Pontuacao |
| **Sala** | - | Proxima Sala, Sala Anterior, Reiniciar Sala, Ir para Sala, Se Proxima Sala Existe, Se Sala Anterior Existe |
| **Saida** | - | Mostrar Mensagem, Executar Codigo |

---

## Exemplo: Jogo Simples de Coletar Moedas

Veja como configurar um jogo basico de coleta de moedas usando apenas recursos do preset Iniciante:

### Objeto do Jogador (obj_player)

**Tecla Pressionada (Seta Esquerda):**
- Definir Velocidade Horizontal: -4

**Tecla Pressionada (Seta Direita):**
- Definir Velocidade Horizontal: 4

**Tecla Pressionada (Seta Cima):**
- Definir Velocidade Vertical: -4

**Tecla Pressionada (Seta Baixo):**
- Definir Velocidade Vertical: 4

**Colisao com obj_coin:**
- Definir Pontuacao: 10 (relative: true)
- Destruir Instancia: other

**Colisao com obj_wall:**
- Parar Movimento

**Colisao com obj_goal:**
- Definir Pontuacao: 100 (relative: true)
- Proxima Sala

### Objeto Moeda (obj_coin)
Nenhum evento necessario - apenas um item coletavel.

### Objeto Parede (obj_wall)
Nenhum evento necessario - apenas um obstaculo solido.

### Objeto Objetivo (obj_goal)
Nenhum evento necessario - dispara conclusao do nivel quando jogador colide.

---

## Atualizando para Intermediario

Quando estiver confortavel com o preset Iniciante, considere atualizar para **Intermediario** para acessar:
- Evento Draw (para renderizacao personalizada)
- Evento Destroy (limpeza quando instancia e destruida)
- Eventos de Mouse (deteccao de clique)
- Eventos de Alarme (acoes temporizadas)
- Sistemas de Vidas e Saude
- Acoes de Som e Musica
- Mais opcoes de movimento (direcao, mover em direcao)

---

## Veja Tambem

- [Preset Intermediario](Intermediate-Preset_pt) - Recursos do proximo nivel
- [Referencia Completa de Acoes](Full-Action-Reference_pt) - Lista completa de acoes
- [Referencia de Eventos](Event-Reference_pt) - Lista completa de eventos
- [Eventos e Acoes](Events-and-Actions_pt) - Conceitos fundamentais
- [Criando Seu Primeiro Jogo](Creating-Your-First-Game_pt) - Tutorial passo a passo
