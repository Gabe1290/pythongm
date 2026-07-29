# Preset para Iniciantes

*[Home](Home_pt) | [Guia de Presets](Preset-Guide_pt) | [Preset Intermediário](Intermediate-Preset_pt)*

O preset **Iniciante** foi projetado para usuários que são novos no desenvolvimento de jogos. Ele fornece um conjunto selecionado de eventos e ações essenciais que cobrem os fundamentos da criação de jogos 2D simples sem sobrecarregar iniciantes com muitas opções.

## Visão Geral

O preset Iniciante inclui:
- **4 Tipos de Eventos** - Para responder a situações do jogo
- **17 Tipos de Ações** - Para controlar o comportamento do jogo
- **6 Categorias** - Eventos, Movimento, Pontuação/Vidas/Saúde, Instancia, Sala, Saida

---

## Eventos

Eventos são gatilhos que respondem a situações específicas no seu jogo. Quando um evento ocorre, as ações que você definiu para esse evento serao executadas.

### Evento Create
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_create` |
| **Categoria** | Eventos |
| **Descrição** | Disparado uma vez quando uma instância é criada pela primeira vez |

**Quando é disparado:** Imediatamente quando uma instância de objeto é colocada em uma sala ou criada com a acao "Criar Instancia".

**Usos comuns:**
- Inicializar variáveis
- Definir posição inicial
- Definir velocidade ou direção inicial
- Resetar pontuação no inicio do jogo

---

### Evento Step
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_step` |
| **Categoria** | Eventos |
| **Descrição** | Disparado a cada quadro (tipicamente 60 vezes por segundo) |

**Quando é disparado:** Continuamente, a cada quadro do jogo.

**Usos comuns:**
- Movimento continuo
- Verificar condições
- Atualizar estado do jogo
- Controle de animação

---

### Evento de Tecla Pressionada
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_keyboard_press` |
| **Categoria** | Eventos |
| **Descrição** | Disparado uma vez quando uma tecla específica é pressionada |

**Quando é disparado:** Uma vez no momento em que uma tecla é pressionada (não enquanto mantida).

**Teclas suportadas:** Teclas de seta (cima, baixo, esquerda, direita), Espaco, Enter, letras (A-Z), numeros (0-9)

**Usos comuns:**
- Controles de movimento do jogador
- Pular
- Atirar
- Navegação de menu

---

### Evento de Colisão
| Propriedade | Valor |
|-------------|-------|
| **Nome do Bloco** | `event_collision` |
| **Categoria** | Eventos |
| **Descrição** | Disparado quando esta instância colide com outro objeto |

**Quando é disparado:** A cada quadro em que duas instâncias estao sobrepostas.

**Variavel especial:** Em um evento de colisão, `other` refere-se a instância com a qual esta colidindo.

**Usos comuns:**
- Coletar itens (moedas, power-ups)
- Receber dano de inimigos
- Bater em paredes ou obstaculos
- Alcancar objetivos ou checkpoints

---

## Ações

Ações são comandos que executam quando um evento é disparado. Multiplas ações podem ser adicionadas a um único evento e serao executadas em ordem.

---

## Ações de Movimento

### Definir Velocidade Horizontal
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `set_hspeed` |
| **Nome do Bloco** | `move_set_hspeed` |
| **Categoria** | Movimento |
| **Ícone** | ↔️ |

**Descrição:** Define a velocidade de movimento horizontal da instância.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `value` | Número | Velocidade em pixels por quadro. Positivo = direita, Negativo = esquerda |

**Exemplo:** Defina `value` como `4` para mover para a direita a 4 pixels por quadro, ou `-4` para mover para a esquerda.

---

### Definir Velocidade Vertical
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `set_vspeed` |
| **Nome do Bloco** | `move_set_vspeed` |
| **Categoria** | Movimento |
| **Ícone** | ↕️ |

**Descrição:** Define a velocidade de movimento vertical da instância.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `value` | Número | Velocidade em pixels por quadro. Positivo = baixo, Negativo = cima |

**Exemplo:** Defina `value` como `-4` para mover para cima a 4 pixels por quadro, ou `4` para mover para baixo.

---

### Parar Movimento
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `stop_movement` |
| **Nome do Bloco** | `move_stop` |
| **Categoria** | Movimento |
| **Ícone** | 🛑 |

**Descrição:** Para todo movimento definindo velocidade horizontal e vertical como zero.

**Parâmetros:** Nenhum

**Usos comuns:**
- Parar jogador ao bater em uma parede
- Parar inimigos ao alcancar um destino
- Pausar movimento temporariamente

---

### Saltar para Posição
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `jump_to_position` |
| **Nome do Bloco** | `move_jump_to` |
| **Categoria** | Movimento |
| **Ícone** | 📍 |

**Descrição:** Move a instância instantaneamente para uma posição específica (sem movimento suave).

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `x` | Número | Coordenada X de destino |
| `y` | Número | Coordenada Y de destino |

**Exemplo:** Saltar para posição (100, 200) para teletransportar o jogador para aquela localização.

---

## Ações de Instancia

### Destruir Instancia
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `destroy_instance` |
| **Nome do Bloco** | `instance_destroy` |
| **Categoria** | Instancia |
| **Ícone** | 💥 |

**Descrição:** Remove uma instância do jogo.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `target` | Escolha | `self` = destruir esta instância, `other` = destruir a instância colidida |

**Usos comuns:**
- Remover moedas coletadas (`target: other` no evento de colisão)
- Destruir balas ao atingir algo
- Remover inimigos quando derrotados

---

### Criar Instancia
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `create_instance` |
| **Nome do Bloco** | `instance_create` |
| **Categoria** | Instancia |
| **Ícone** | ✨ |

**Descrição:** Cria uma nova instância de um objeto em uma posição especificada.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `object` | Objeto | O tipo de objeto a criar |
| `x` | Número | Coordenada X para a nova instância |
| `y` | Número | Coordenada Y para a nova instância |

**Exemplo:** Criar uma bala na posição do jogador quando Espaco é pressionado.

---

## Ações de Pontuação

### Definir Pontuação
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `set_score` |
| **Nome do Bloco** | `score_set` |
| **Categoria** | Pontuação/Vidas/Saúde |
| **Ícone** | 🏆 |

**Descrição:** Define a pontuação para um valor específico, ou adiciona/subtrai da pontuação atual.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `value` | Número | O valor da pontuação |
| `relative` | Booleano | Se verdadeiro, adiciona valor a pontuação atual. Se falso, define pontuação como valor |

**Exemplos:**
- Resetar pontuação: `value: 0`, `relative: false`
- Adicionar 10 pontos: `value: 10`, `relative: true`
- Subtrair 5 pontos: `value: -5`, `relative: true`

---

### Adicionar a Pontuação
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `add_score` |
| **Nome do Bloco** | `score_add` |
| **Categoria** | Pontuação/Vidas/Saúde |
| **Ícone** | ➕🏆 |

**Descrição:** Adiciona um valor a pontuação atual (atalho para set_score com relative=true).

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `value` | Número | Pontos a adicionar (pode ser negativo para subtrair) |

---

### Desenhar Pontuação
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `draw_score` |
| **Nome do Bloco** | `draw_score` |
| **Categoria** | Pontuação/Vidas/Saúde |
| **Ícone** | 🖼️🏆 |

**Descrição:** Exibe a pontuação atual na tela.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `x` | Número | Posição X para desenhar a pontuação |
| `y` | Número | Posição Y para desenhar a pontuação |
| `caption` | String | Texto a exibir antes da pontuação (ex: "Pontuação: ") |

**Nota:** Isso deve ser usado em um evento Draw (disponível no preset Intermediário).

---

## Ações de Sala

### Ir para Proxima Sala
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `next_room` |
| **Nome do Bloco** | `room_goto_next` |
| **Categoria** | Sala |
| **Ícone** | ➡️ |

**Descrição:** Transiciona para a proxima sala na ordem das salas.

**Parâmetros:** Nenhum

**Nota:** Se ja estiver na última sala, esta acao não tem efeito (use "Se Proxima Sala Existe" para verificar primeiro).

---

### Ir para Sala Anterior
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `previous_room` |
| **Nome do Bloco** | `room_goto_previous` |
| **Categoria** | Sala |
| **Ícone** | ⬅️ |

**Descrição:** Transiciona para a sala anterior na ordem das salas.

**Parâmetros:** Nenhum

**Nota:** Se ja estiver na primeira sala, esta acao não tem efeito.

---

### Reiniciar Sala
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `restart_room` |
| **Nome do Bloco** | `room_restart` |
| **Categoria** | Sala |
| **Ícone** | 🔄 |

**Descrição:** Reinicia a sala atual, resetando todas as instâncias para seu estado inicial.

**Parâmetros:** Nenhum

**Usos comuns:**
- Reiniciar nível após jogador morrer
- Resetar quebra-cabeça após falha
- Repetir mini-jogo

---

### Ir para Sala
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `goto_room` |
| **Nome do Bloco** | `room_goto` |
| **Categoria** | Sala |
| **Ícone** | 🚪 |

**Descrição:** Transiciona para uma sala específica pelo nome.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `room` | Sala | A sala para onde ir |

---

### Se Proxima Sala Existe
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `if_next_room_exists` |
| **Nome do Bloco** | `room_if_next_exists` |
| **Categoria** | Sala |
| **Ícone** | ❓➡️ |

**Descrição:** Bloco condicional que so executa ações contidas se houver uma proxima sala.

**Parâmetros:** Nenhum (ações são colocadas dentro do bloco)

**Usos comuns:**
- Verificar antes de ir para proxima sala
- Mostrar mensagem "Você Venceu!" se não houver mais salas

---

### Se Sala Anterior Existe
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `if_previous_room_exists` |
| **Nome do Bloco** | `room_if_previous_exists` |
| **Categoria** | Sala |
| **Ícone** | ❓⬅️ |

**Descrição:** Bloco condicional que so executa ações contidas se houver uma sala anterior.

**Parâmetros:** Nenhum (ações são colocadas dentro do bloco)

---

## Ações de Saida

### Mostrar Mensagem
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `show_message` |
| **Nome do Bloco** | `output_message` |
| **Categoria** | Saida |
| **Ícone** | 💬 |

**Descrição:** Exibe uma caixa de dialogo popup para o jogador.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `message` | String | O texto a exibir |

**Nota:** O jogo pausa enquanto a mensagem é exibida. O jogador deve clicar OK para continuar.

**Usos comuns:**
- Instruções do jogo
- Dialogo da história
- Mensagens de vitoria/derrota
- Informações de debug

---

### Executar Código
| Propriedade | Valor |
|-------------|-------|
| **Nome da Ação** | `execute_code` |
| **Nome do Bloco** | `execute_code` |
| **Categoria** | Saida |
| **Ícone** | 💻 |

**Descrição:** Executa código Python personalizado.

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `code` | String | Código Python a executar |

**Nota:** Este é um recurso avançado. Use com cautela pois código incorreto pode causar erros.

---

## Resumo das Categorias

| Categoria | Eventos | Ações |
|-----------|---------|-------|
| **Eventos** | Create, Step, Tecla Pressionada, Colisão | - |
| **Movimento** | - | Definir Velocidade Horizontal, Definir Velocidade Vertical, Parar Movimento, Saltar para Posição |
| **Instancia** | - | Destruir Instancia, Criar Instancia |
| **Pontuação/Vidas/Saúde** | - | Definir Pontuação, Adicionar Pontuação, Desenhar Pontuação |
| **Sala** | - | Proxima Sala, Sala Anterior, Reiniciar Sala, Ir para Sala, Se Proxima Sala Existe, Se Sala Anterior Existe |
| **Saida** | - | Mostrar Mensagem, Executar Código |

---

## Exemplo: Jogo Simples de Coletar Moedas

Veja como configurar um jogo básico de coleta de moedas usando apenas recursos do preset Iniciante:

### Objeto do Jogador (obj_player)

**Tecla Pressionada (Seta Esquerda):**
- Definir Velocidade Horizontal: -4

**Tecla Pressionada (Seta Direita):**
- Definir Velocidade Horizontal: 4

**Tecla Pressionada (Seta Cima):**
- Definir Velocidade Vertical: -4

**Tecla Pressionada (Seta Baixo):**
- Definir Velocidade Vertical: 4

**Colisão com obj_coin:**
- Definir Pontuação: 10 (relative: true)
- Destruir Instancia: other

**Colisão com obj_wall:**
- Parar Movimento

**Colisão com obj_goal:**
- Definir Pontuação: 100 (relative: true)
- Proxima Sala

### Objeto Moeda (obj_coin)
Nenhum evento necessario - apenas um item coletavel.

### Objeto Parede (obj_wall)
Nenhum evento necessario - apenas um obstaculo sólido.

### Objeto Objetivo (obj_goal)
Nenhum evento necessario - dispara conclusão do nível quando jogador colide.

---

## Atualizando para Intermediário

Quando estiver confortavel com o preset Iniciante, considere atualizar para **Intermediário** para acessar:
- Evento Draw (para renderização personalizada)
- Evento Destroy (limpeza quando instância é destruída)
- Eventos de Mouse (detecção de clique)
- Eventos de Alarme (ações temporizadas)
- Sistemas de Vidas e Saúde
- Ações de Som e Música
- Mais opções de movimento (direção, mover em direção)

---

## Veja Tambem

- [Tutoriais](Tutorials_pt) - Todos os tutoriais em um so lugar
- [Preset Intermediário](Intermediate-Preset_pt) - Recursos do próximo nível
- [Referencia Completa de Ações](Full-Action-Reference_pt) - Lista completa de ações
- [Referencia de Eventos](Event-Reference_pt) - Lista completa de eventos
- [Eventos e Ações](Eventos_e_Acoes_pt) - Conceitos fundamentais
- [Criando Seu Primeiro Jogo](Primeiro_Jogo_pt) - Tutorial passo a passo
- [Tutorial Pong](Tutorial-Pong_pt) - Crie um jogo Pong classico para dois jogadores
- [Tutorial Breakout](Tutorial-Breakout_pt) - Crie um jogo Breakout classico
- [Introdução a Criação de Jogos](Getting-Started-Breakout_pt) - Tutorial completo para iniciantes
