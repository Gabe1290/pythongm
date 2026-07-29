# Referência completa de ações

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

Esta página lista todas as **109** ações disponíveis no PyGameMaker, exatamente como aparecem no seletor de ações do IDE (incluindo o plugin Audio e a extensão Vista 3D). Ações são comandos que são executados quando um evento é acionado.

## Categorias

- [Movimento](#movement) (20)
- [Instância](#instance) (12)
- [Pontuação](#score) (11)
- [Sala](#room) (9)
- [Tempo](#timing) (2)
- [Áudio](#audio) (6)
- [Jogo](#game) (20)
- [Controle](#control) (19)
- [Grade](#grid) (4)
- [Vistas](#views) (2)
- [Vista 3D](#3d-view) (4)

---

<a id="movement"></a>
## Movimento

### Quicar

| Propriedade | Valor |
|----------|-------|
| **Nome** | `bounce` |
| **Categoria** | Movimento |

Quicar em objetos sólidos

*Parâmetros:* nenhum

### Saltar para posição

| Propriedade | Valor |
|----------|-------|
| **Nome** | `jump_to_position` |
| **Ícone** | 📍 |
| **Categoria** | Movimento |

Mover instantaneamente para uma posição

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `relative` | Sim/Não | Não | Somar à posição atual em vez de definir uma absoluta |

### Saltar para posição aleatória

| Propriedade | Valor |
|----------|-------|
| **Nome** | `jump_to_random` |
| **Ícone** | 🎲↪️ |
| **Categoria** | Movimento |

Teletransportar para uma posição aleatória (opcionalmente ajustada à grade)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `snap_h` | Número | `1` | Ajuste horizontal à grade (1 = sem ajuste) |
| `snap_v` | Número | `1` | Ajuste vertical à grade (1 = sem ajuste) |

### Saltar para a posição inicial

| Propriedade | Valor |
|----------|-------|
| **Nome** | `jump_to_start` |
| **Ícone** | ↩️ |
| **Categoria** | Movimento |

Retornar a instância à sua posição de criação

*Parâmetros:* nenhum

### Movimento livre

| Propriedade | Valor |
|----------|-------|
| **Nome** | `move_free` |
| **Ícone** | 🧭 |
| **Categoria** | Movimento |

Mover em uma direção precisa (0-360 graus)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `0` | Direção em graus (0=direita, 90=cima, anti-horário) |
| `speed` | Número | `4.0` | Velocidade de movimento |

### Mover pela grade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `move_grid` |
| **Ícone** | ▦ |
| **Categoria** | Movimento |

Mover uma célula da grade na direção indicada

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Escolha | `right` | Direção de movimento; Opções: `left`, `right`, `up`, `down` |
| `grid_size` | Número | `32` | Tamanho da célula da grade em pixels |

### Mover em direção a um ponto

| Propriedade | Valor |
|----------|-------|
| **Nome** | `move_towards_point` |
| **Ícone** | 🎯 |
| **Categoria** | Movimento |

Mover em direção a um ponto a uma dada velocidade

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | X de destino |
| `y` | Número | `0` | Y de destino |
| `speed` | Número | `4.0` | Velocidade de movimento |

### Mover até o contato

| Propriedade | Valor |
|----------|-------|
| **Nome** | `move_to_contact` |
| **Ícone** | 🎯 |
| **Categoria** | Movimento |

Mover em uma direção até tocar um objeto (ou a distância máxima)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Texto | `direction` | Direção em graus (0=direita, 90=cima, 180=esquerda, 270=baixo) ou uma expressão. Padrão «direction» = a orientação atual da instância (ajuste à colisão). |
| `max_distance` | Número | `1000` | Distância máxima de movimento, em pixels |
| `object` | Objeto | `all` | Parar ao contato com: «all» todas as instâncias, «solid» apenas objetos sólidos, ou um nome de objeto específico.; Opções: `all`, `solid`; opcional |

### Inverter horizontal

| Propriedade | Valor |
|----------|-------|
| **Nome** | `reverse_horizontal` |
| **Ícone** | ↔️ |
| **Categoria** | Movimento |

Inverter a direção do movimento horizontal

*Parâmetros:* nenhum

### Inverter vertical

| Propriedade | Valor |
|----------|-------|
| **Nome** | `reverse_vertical` |
| **Ícone** | ↕️ |
| **Categoria** | Movimento |

Inverter a direção do movimento vertical

*Parâmetros:* nenhum

### Definir direção

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_direction` |
| **Ícone** | 🧭 |
| **Categoria** | Movimento |

Definir a direção do movimento

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `0` | Direção em graus (0=direita, 90=cima) |

### Definir direção e velocidade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_direction_speed` |
| **Ícone** | 🧭 |
| **Categoria** | Movimento |

Definir a direção (em graus) e a magnitude da velocidade da instância

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `0` | Direção em graus (0=direita, 90=cima) |
| `speed` | Número | `4.0` | Velocidade em pixels por quadro |

### Definir atrito

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_friction` |
| **Ícone** | 🛑 |
| **Categoria** | Movimento |

Definir o atrito (desaceleração)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `friction` | Número | `0.1` | Quantidade de atrito (subtraída da velocidade a cada passo) |

### Definir gravidade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_gravity` |
| **Ícone** | ⬇️ |
| **Categoria** | Movimento |

Definir a direção e a intensidade da gravidade

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `270` | Direção da gravidade em graus (270=baixo) |
| `gravity` | Número | `0.5` | Intensidade da gravidade (adicionada a cada passo) |

### Definir velocidade horizontal

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_hspeed` |
| **Ícone** | ↔️ |
| **Categoria** | Movimento |

Definir a velocidade de movimento horizontal

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0` | Velocidade em pixels por quadro |

### Definir velocidade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_speed` |
| **Ícone** | ⚡ |
| **Categoria** | Movimento |

Definir a velocidade de movimento (magnitude)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0` | Velocidade de movimento |

### Definir velocidade vertical

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_vspeed` |
| **Ícone** | ↕️ |
| **Categoria** | Movimento |

Definir a velocidade de movimento vertical

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0` | Velocidade em pixels por quadro |

### Começar a mover (direção)

| Propriedade | Valor |
|----------|-------|
| **Nome** | `start_moving_direction` |
| **Ícone** | ➡️ |
| **Categoria** | Movimento |

Começar a mover em uma direção a uma dada velocidade

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `directions` | Escolha múltipla | right | Direção(ões) de movimento — marque uma, ou várias para escolher uma aleatória a cada passo. A célula central é parar.; Opções: `up-left`, `up`, `up-right`, `left`, `stop`, `right`, `down-left`, `down`, `down-right` |
| `direction_expr` | Texto | — | Alternativa: expressão livre avaliada como graus; opcional |
| `speed` | Número | `4.0` | Velocidade em pixels por quadro |

### Parar movimento

| Propriedade | Valor |
|----------|-------|
| **Nome** | `stop_movement` |
| **Ícone** | 🛑 |
| **Categoria** | Movimento |

Zerar ambas as velocidades

*Parâmetros:* nenhum

### Envolver ao redor da sala

| Propriedade | Valor |
|----------|-------|
| **Nome** | `wrap_around_room` |
| **Ícone** | 🔄 |
| **Categoria** | Movimento |

Reaparecer no lado oposto da sala

*Parâmetros:* nenhum

---

<a id="instance"></a>
## Instância

### Mudar instância

| Propriedade | Valor |
|----------|-------|
| **Nome** | `change_instance` |
| **Ícone** | 🔄 |
| **Categoria** | Instância |
| **Aplica-se a** | self / other / object |

Transformar em outro tipo de objeto

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Novo tipo de objeto |
| `perform_events` | Sim/Não | Sim | Executar os eventos destruir/criar |

### Criar instância

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_instance` |
| **Ícone** | ✨ |
| **Categoria** | Instância |

Criar uma nova instância

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Objeto a criar |
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `relative` | Sim/Não | Não | Posição relativa à instância atual |

### Criar instância em movimento

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_moving_instance` |
| **Ícone** | ✨➡️ |
| **Categoria** | Instância |

Criar uma instância e iniciá-la em uma direção

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Objeto a criar |
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `speed` | Número | `0` | Magnitude da velocidade inicial |
| `direction` | Número | `0` | Direção inicial em graus |

### Criar instância aleatória

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_random_instance` |
| **Ícone** | 🎲 |
| **Categoria** | Instância |

Criar um de vários tipos de objeto escolhido aleatoriamente

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `object1` | Objeto | — | Primeiro objeto candidato; opcional |
| `object2` | Objeto | — | Segundo objeto candidato; opcional |
| `object3` | Objeto | — | Terceiro objeto candidato; opcional |
| `object4` | Objeto | — | Quarto objeto candidato; opcional |

### Destruir instância

| Propriedade | Valor |
|----------|-------|
| **Nome** | `destroy_instance` |
| **Ícone** | 💥 |
| **Categoria** | Instância |
| **Aplica-se a** | self / other / object |

Destruir uma instância

*Parâmetros:* nenhum

### Destruir na posição

| Propriedade | Valor |
|----------|-------|
| **Nome** | `destroy_at_position` |
| **Ícone** | 💣 |
| **Categoria** | Instância |

Destruir instâncias dentro de um raio de (x, y)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | `all` | Qual tipo de objeto destruir. «all» destrói cada instância no raio; «solid» apenas as sólidas (ex. muros); «non-solid» tudo exceto os sólidos.; Opções: `all`, `solid`, `non-solid` |
| `x` | Texto | `self.x` | Posição X (expressão permitida, ex. self.x) |
| `y` | Texto | `self.y` | Posição Y (expressão permitida, ex. self.y) |
| `relative` | Sim/Não | Não | Tratar X/Y como deslocamentos da posição desta instância em vez de coordenadas absolutas; opcional |
| `radius` | Número | `32` | Raio em pixels ao redor de (x, y). Padrão 32 = ~uma célula da grade. |

### Definir índice de imagem

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_image_index` |
| **Ícone** | 🖼️ |
| **Categoria** | Instância |

Definir o quadro de animação atual do sprite da instância

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `frame` | Número | `0` | Índice do quadro |

### Definir velocidade de imagem

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_image_speed` |
| **Ícone** | ⏩ |
| **Categoria** | Instância |

Definir a velocidade de reprodução da animação do sprite da instância

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `1.0` | Quadros avançados por passo (0 = em pausa) |

### Definir sprite

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_sprite` |
| **Ícone** | 🖼️ |
| **Categoria** | Instância |

Mudar o sprite e/ou o quadro/velocidade de animação de uma instância

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sprite` | Sprite | `<self>` | Sprite a usar (ou «<self>» para manter o atual) |
| `subimage` | Número | `-1` | Índice do quadro a definir; -1 deixa inalterado |
| `speed` | Número | `-1` | Velocidade de animação; -1 deixa inalterada |

### Iniciar animação

| Propriedade | Valor |
|----------|-------|
| **Nome** | `start_animation` |
| **Ícone** | ▶️ |
| **Categoria** | Instância |

Retomar a animação do sprite da instância (image_speed = 1)

*Parâmetros:* nenhum

### Parar animação

| Propriedade | Valor |
|----------|-------|
| **Nome** | `stop_animation` |
| **Ícone** | ⏸️ |
| **Categoria** | Instância |

Pausar a animação do sprite da instância (image_speed = 0)

*Parâmetros:* nenhum

### Testar número de instâncias

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_instance_count` |
| **Ícone** | ❓🔢 |
| **Categoria** | Instância |

Condição: comparar o número de instâncias de um objeto

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Objeto a contar |
| `number` | Número | `0` | Valor de comparação |
| `operation` | Escolha | `equal` | Operador de comparação; Opções: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="score"></a>
## Pontuação

### Limpar tabela de recordes

| Propriedade | Valor |
|----------|-------|
| **Nome** | `clear_highscore` |
| **Ícone** | 🗑️🏆 |
| **Categoria** | Pontuação |

Limpar todas as entradas da tabela de recordes

*Parâmetros:* nenhum

### Desenhar barra de saúde

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_health_bar` |
| **Ícone** | 🩺 |
| **Categoria** | Pontuação |

Desenhar a saúde atual como uma barra de duas cores

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x1` | Número | `0` | X esquerda |
| `y1` | Número | `0` | Y superior |
| `x2` | Número | `100` | X direita |
| `y2` | Número | `20` | Y inferior |
| `back_color` | Cor | `#FF0000` | Cor de fundo (vazio) |
| `bar_color` | Cor | `#00FF00` | Cor de preenchimento (saúde) |

### Desenhar vidas

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_lives` |
| **Ícone** | 🖍️❤️ |
| **Categoria** | Pontuação |

Desenhar o número de vidas atual como imagens de sprite repetidas

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `sprite` | Sprite | — | Sprite desenhado uma vez por vida restante; opcional |
| `scale` | Número | `1.0` | Fator de escala uniforme para o ícone de vida (1.0 = tamanho nativo); opcional |
| `relative` | Sim/Não | Não | Desenhar em relação à posição desta instância em vez de coordenadas de tela absolutas; opcional |

### Desenhar pontuação

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_score` |
| **Ícone** | 🖍️🏆 |
| **Categoria** | Pontuação |

Desenhar a pontuação atual na tela

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `caption` | Texto | `Score: ` | Texto mostrado antes do valor da pontuação; opcional |
| `relative` | Sim/Não | Não | Desenhar em relação à posição desta instância em vez de coordenadas de tela absolutas; opcional |

### Definir saúde

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_health` |
| **Ícone** | 💚 |
| **Categoria** | Pontuação |

Definir a saúde, ou somar a ela com «Relativo»

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Número | `100` | Valor de saúde (0-100) |
| `relative` | Sim/Não | Não | Somar à saúde atual em vez de substituí-la |

### Definir vidas

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_lives` |
| **Ícone** | ❤️ |
| **Categoria** | Pontuação |

Definir as vidas, ou somar a elas com «Relativo»

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Número | `3` | Número de vidas |
| `relative` | Sim/Não | Não | Somar às vidas atuais em vez de substituí-las |

### Definir pontuação

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_score` |
| **Ícone** | 🏆 |
| **Categoria** | Pontuação |

Definir a pontuação, ou somar a ela com «Relativo»

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Número | `0` | Valor de pontuação a definir |
| `relative` | Sim/Não | Não | Somar à pontuação atual em vez de substituí-la |

### Mostrar tabela de recordes

| Propriedade | Valor |
|----------|-------|
| **Nome** | `show_highscore` |
| **Ícone** | 🏆 |
| **Categoria** | Pontuação |

Mostrar a caixa de diálogo da tabela de recordes

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `background` | Cor | `#FFFFDD` | Cor de fundo da caixa de diálogo; opcional |
| `new_color` | Cor | `#FF0000` | Cor usada para a nova entrada (qualificada); opcional |
| `other_color` | Cor | `#000000` | Cor usada para as outras entradas; opcional |
| `allow_new_entry` | Sim/Não | Sim | Pedir o nome se a pontuação atual se qualifica |

### Testar saúde

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_health` |
| **Ícone** | ❓💚 |
| **Categoria** | Pontuação |

Condição: comparar a saúde atual com um valor

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `operation` | Escolha | `equal` | Operador de comparação; Opções: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |
| `value` | Número | `0` | Valor de comparação |

### Testar vidas

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_lives` |
| **Ícone** | ❓❤️ |
| **Categoria** | Pontuação |

Condição: comparar o número de vidas com um valor

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Número | `0` | Valor de comparação |
| `operation` | Escolha | `equal` | Operador de comparação; Opções: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

### Testar pontuação

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_score` |
| **Ícone** | ❓🏆 |
| **Categoria** | Pontuação |

Condição: comparar a pontuação com um valor

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Número | `0` | Valor de comparação |
| `operation` | Escolha | `equal` | Operador de comparação; Opções: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="room"></a>
## Sala

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

---

<a id="timing"></a>
## Tempo

### Definir alarme

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_alarm` |
| **Ícone** | ⏰ |
| **Categoria** | Tempo |

Definir um alarme

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `alarm_number` | Número | `0` | Qual alarme (0-11) |
| `steps` | Número | `30` | Número de passos até o alarme disparar (30 = 0,5 s a 60 FPS) |

### Pausa

| Propriedade | Valor |
|----------|-------|
| **Nome** | `sleep` |
| **Ícone** | 💤 |
| **Categoria** | Tempo |

Pausar o jogo por um número de milissegundos e depois continuar. Os sons continuam tocando durante a pausa (por exemplo, para deixar um som terminar antes de mudar de sala). Nota: a renderização e a entrada ficam congeladas durante a pausa, então mantenha durações curtas

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `milliseconds` | Número | `1000` | Duração da pausa, em milissegundos (1000 = 1 segundo) |

---

<a id="audio"></a>
## Áudio

### Verificar reprodução de som

| Propriedade | Valor |
|----------|-------|
| **Nome** | `check_sound` |
| **Ícone** | ❓🔊 |
| **Categoria** | Áudio |

Condição: verdadeiro se o som indicado está sendo reproduzido no momento

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sound` | Som | — | Som a verificar |
| `not_flag` | Sim/Não | Não | Inverter o resultado; opcional |

### Reproduzir música

| Propriedade | Valor |
|----------|-------|
| **Nome** | `play_music` |
| **Ícone** | 🎵 |
| **Categoria** | Áudio |

Reproduzir música de fundo (em loop)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `music` | Som | — | Arquivo de música a reproduzir |
| `loop` | Sim/Não | Sim | Reproduzir a música em loop |
| `volume` | Número | `0.7` | Volume (de 0.0 a 1.0) |

### Reproduzir som

| Propriedade | Valor |
|----------|-------|
| **Nome** | `play_sound` |
| **Ícone** | 🔊 |
| **Categoria** | Áudio |

Reproduzir um efeito sonoro uma vez

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sound` | Som | — | Som a reproduzir |
| `volume` | Número | `1.0` | Volume (de 0.0 a 1.0) |

### Definir volume

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_volume` |
| **Ícone** | 🔉 |
| **Categoria** | Áudio |

Definir o volume geral de som/música

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `volume` | Número | `1.0` | Volume (de 0.0 a 1.0) |

### Parar música

| Propriedade | Valor |
|----------|-------|
| **Nome** | `stop_music` |
| **Ícone** | 🔇 |
| **Categoria** | Áudio |

Parar a música de fundo

*Parâmetros:* nenhum

### Parar som

| Propriedade | Valor |
|----------|-------|
| **Nome** | `stop_sound` |
| **Ícone** | 🔇 |
| **Categoria** | Áudio |

Parar um som em reprodução

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sound` | Som | — | Som a parar |

---

<a id="game"></a>
## Jogo

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

---

<a id="control"></a>
## Controle

### Verificar se vazio

| Propriedade | Valor |
|----------|-------|
| **Nome** | `check_empty` |
| **Ícone** | 🔍 |
| **Categoria** | Controle |

Verdadeiro quando (x, y) está livre de colisões. Use com start_block/end_block para condicionar a(s) ação(ões) seguinte(s), no estilo GM

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `self.x` | Posição X a verificar (expressão permitida, ex. self.x + 32) |
| `y` | Texto | `self.y` | Posição Y a verificar (expressão permitida, ex. self.y + 32) |
| `relative` | Sim/Não | Não | Tratar X/Y como deslocamentos da posição desta instância em vez de coordenadas absolutas; opcional |
| `objects` | Escolha | `solid` | Quais instâncias contam como ocupando a posição; Opções: `solid`, `all` |

### Comentário

| Propriedade | Valor |
|----------|-------|
| **Nome** | `comment` |
| **Ícone** | ⚠️ |
| **Categoria** | Controle |

Um comentário na lista de ações (sem efeito em execução)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `text` | Texto | — | Texto de comentário livre; opcional |

### Senão

| Propriedade | Valor |
|----------|-------|
| **Nome** | `else_action` |
| **Ícone** | ⚡ |
| **Categoria** | Controle |

Marca o ramo «senão» de uma condição

*Parâmetros:* nenhum

### Fim de bloco

| Propriedade | Valor |
|----------|-------|
| **Nome** | `end_block` |
| **Ícone** | 📁 |
| **Categoria** | Controle |

Terminar um bloco de ações

*Parâmetros:* nenhum

### Executar código

| Propriedade | Valor |
|----------|-------|
| **Nome** | `execute_code` |
| **Ícone** | 📜 |
| **Categoria** | Controle |

Executar um bloco de código Python integrado

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `code` | Código | — | Código Python a avaliar em relação à instância |

### Executar script

| Propriedade | Valor |
|----------|-------|
| **Nome** | `execute_script` |
| **Ícone** | 📜 |
| **Categoria** | Controle |

Executar um dos scripts do projeto

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `script` | Script | — | Nome do script do projeto a executar |
| `arg0` | Texto | — | Disponível no script como argument0; opcional |
| `arg1` | Texto | — | Disponível no script como argument1; opcional |
| `arg2` | Texto | — | Disponível no script como argument2; opcional |
| `arg3` | Texto | — | Disponível no script como argument3; opcional |
| `arg4` | Texto | — | Disponível no script como argument4; opcional |

### Sair do evento

| Propriedade | Valor |
|----------|-------|
| **Nome** | `exit_event` |
| **Ícone** | 🚪 |
| **Categoria** | Controle |

Interromper a execução das ações restantes neste evento

*Parâmetros:* nenhum

### Se pode empurrar

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_can_push` |
| **Ícone** | 📦 |
| **Categoria** | Controle |

Verificar se uma caixa/objeto pode ser empurrado na direção atual (estilo Sokoban)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Escolha | `facing` | Direção a verificar para o empurrão; Opções: `facing` |
| `object_type` | Texto | `box` | Tipo de objeto sendo empurrado |
| `then_action` | Escolha | `push_and_move` | Ação se o empurrão é possível; Opções: `push_and_move`, `none` |
| `else_action` | Escolha | `stop_movement` | Ação se o empurrão está bloqueado; Opções: `stop_movement`, `none` |

### Se colisão

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_collision` |
| **Ícone** | ❓💥 |
| **Categoria** | Controle |

Condição: verdadeiro se a instância colidiria no deslocamento (x, y)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Deslocamento horizontal a testar |
| `y` | Número | `0` | Deslocamento vertical a testar |
| `object` | Texto | `any` | «any», «solid» ou um nome de objeto; Opções: `any`, `solid`; opcional |
| `not_flag` | Sim/Não | Não | Negar o resultado; opcional |

### Se colisão em

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_collision_at` |
| **Ícone** | 🎯 |
| **Categoria** | Controle |

Verificar uma colisão em uma posição

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `self.x + 32` | Expressão da posição X |
| `y` | Texto | `self.y` | Expressão da posição Y |
| `object_type` | Escolha | `any` | Tipo de objeto a verificar; Opções: `any`, `solid` |
| `then_actions` | Lista de ações | — | Ações se colisão encontrada |
| `else_actions` | Lista de ações | — | Ações se nenhuma colisão |

### Se condição

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_condition` |
| **Ícone** | ❓ |
| **Categoria** | Controle |

Verificação condicional com ações então/senão

*Parâmetros:* nenhum

### Se o objeto existe

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_object_exists` |
| **Ícone** | ❓ |
| **Categoria** | Controle |

Condição: verdadeiro se existir pelo menos uma instância do objeto

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Tipo de objeto a verificar |
| `not_flag` | Sim/Não | Não | Negar o resultado (agir quando o objeto NÃO existe); opcional |

### Repetir

| Propriedade | Valor |
|----------|-------|
| **Nome** | `repeat` |
| **Ícone** | 🔁 |
| **Categoria** | Controle |

Repetir a ação/o bloco seguinte N vezes

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `times` | Número | `10` | Número de repetições |
| `actions` | Lista de ações | — | Ações a repetir |

### Definir variável

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_variable` |
| **Ícone** | 📝 |
| **Categoria** | Controle |

Definir uma variável de instância ou global

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `variable` | Texto | — | Nome da variável |
| `value` | Texto | `0` | Valor (número, cadeia ou expressão) |
| `scope` | Escolha | `self` | Escopo da variável; Opções: `self`, `other`, `global` |
| `relative` | Sim/Não | Não | Somar ao valor atual em vez de substituí-lo |

### Início de bloco

| Propriedade | Valor |
|----------|-------|
| **Nome** | `start_block` |
| **Ícone** | 📂 |
| **Categoria** | Controle |

Iniciar um bloco de ações (para agrupar)

*Parâmetros:* nenhum

### Testar probabilidade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_chance` |
| **Ícone** | 🎲❓ |
| **Categoria** | Controle |

Condição: verdadeiro com probabilidade 1 em «sides»

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sides` | Número | `6` | Uma chance de 1 em N de ser verdadeiro |

### Testar expressão

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_expression` |
| **Ícone** | ❓ |
| **Categoria** | Controle |

Testar se uma expressão é verdadeira

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `expression` | Texto | — | Expressão a avaliar (verdadeiro se >= 0.5) |
| `then_actions` | Lista de ações | — | Ações se verdadeiro |
| `else_actions` | Lista de ações | — | Ações se falso |

### Fazer uma pergunta

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_question` |
| **Ícone** | ❓💬 |
| **Categoria** | Controle |

Condição: mostrar uma caixa de diálogo sim/não; verdadeiro se o usuário responder sim

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `question` | Texto | `Continue?` | Pergunta mostrada ao jogador |

### Testar variável

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_variable` |
| **Ícone** | ❓ |
| **Categoria** | Controle |

Testar o valor de uma variável de instância ou global

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `variable` | Texto | — | Nome da variável |
| `value` | Texto | `0` | Valor a comparar |
| `scope` | Escolha | `self` | Escopo da variável; Opções: `self`, `other`, `global` |
| `operation` | Escolha | `equal` | Operador de comparação; Opções: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="grid"></a>
## Grade

### Se na grade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_on_grid` |
| **Ícone** | ▦ |
| **Categoria** | Grade |

Verificar se o objeto está alinhado à grade

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `grid_size` | Número | `32` | Tamanho da célula da grade em pixels |
| `then_actions` | Lista de ações | — | Ações se na grade |
| `else_actions` | Lista de ações | — | Ações se não na grade |

### Ajustar à grade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `snap_to_grid` |
| **Ícone** | ▦ |
| **Categoria** | Grade |

Alinhar a posição da instância à grade

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `grid_size` | Número | `32` | Tamanho da célula da grade em pixels |

### Parar se nenhuma tecla pressionada

| Propriedade | Valor |
|----------|-------|
| **Nome** | `stop_if_no_keys` |
| **Ícone** | ▦ |
| **Categoria** | Grade |

Parar o movimento na grade quando nenhuma tecla de movimento é pressionada (perfeito para um ajuste suave à grade)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `grid_size` | Número | `32` | Tamanho da célula da grade em pixels |

### Testar alinhamento à grade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_alignment` |
| **Ícone** | ❓▦ |
| **Categoria** | Grade |

Condição: verdadeiro se a instância está alinhada a uma grade

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `hsnap` | Número | `32` | Espaçamento horizontal da grade em pixels |
| `vsnap` | Número | `32` | Espaçamento vertical da grade em pixels |

---

<a id="views"></a>
## Vistas

### Ativar vistas

| Propriedade | Valor |
|----------|-------|
| **Nome** | `enable_views` |
| **Ícone** | 🎥 |
| **Categoria** | Vistas |

Ativar ou desativar o sistema de câmera/vista da sala (permite que um nível role quando é maior que a janela)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `enable` | Sim/Não | Sim | Ativado = vistas de câmera; desativado = desenhar a sala inteira de uma vez |

### Configurar vista

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_view` |
| **Ícone** | 🎥 |
| **Categoria** | Vistas |

Configurar uma vista de câmera: qual parte da sala mostra, onde é desenhada na tela e um objeto a seguir

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `view` | Escolha | `0` | Qual das 8 vistas configurar; Opções: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` |
| `visible` | Sim/Não | Sim | Desenhar esta vista |
| `view_x` | Número | `0` | Borda esquerda da região da sala mostrada |
| `view_y` | Número | `0` | Borda superior da região da sala mostrada |
| `view_w` | Número | `800` | Largura da região da sala mostrada |
| `view_h` | Número | `600` | Altura da região da sala mostrada |
| `port_x` | Número | `0` | Borda esquerda na tela |
| `port_y` | Número | `0` | Borda superior na tela |
| `port_w` | Número | `800` | Largura desenhada na tela |
| `port_h` | Número | `600` | Altura desenhada na tela |
| `follow` | Objeto | — | Objeto que a câmera segue (vazio = vista fixa); opcional |
| `hborder` | Número | `32` | Borda horizontal antes de a câmera rolar |
| `vborder` | Número | `32` | Borda vertical antes de a câmera rolar |
| `hspeed` | Número | `-1` | Velocidade máxima de rolagem horizontal (-1 = instantâneo) |
| `vspeed` | Número | `-1` | Velocidade máxima de rolagem vertical (-1 = instantâneo) |

---

<a id="3d-view"></a>
## Vista 3D

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

## Veja também

- [Referência de eventos](Event-Reference_pt) — os eventos que acionam as ações
- [Guia de predefinições](Preset-Guide_pt) — quais ações cada predefinição/edição expõe
- [Vista 3D](3D-View_pt) — as ações de vista em primeira pessoa (raycast)
- [Extensões](Extensions_pt) — como as ações da Vista 3D são fornecidas
