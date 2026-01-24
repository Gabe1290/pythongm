# Referência Completa de Ações

*[Início](Home_pt) | [Guia de Presets](Preset-Guide_pt) | [Referência de Eventos](Event-Reference_pt)*

Esta página documenta todas as ações disponíveis no PyGameMaker. Ações são comandos que são executados quando eventos são acionados.

## Categorias de Ações

- [Ações de Movimento](#ações-de-movimento)
- [Ações de Instância](#ações-de-instância)
- [Ações de Pontuação, Vidas e Saúde](#ações-de-pontuação-vidas-e-saúde)
- [Ações de Sala](#ações-de-sala)
- [Ações de Temporização](#ações-de-temporização)
- [Ações de Som](#ações-de-som)
- [Ações de Desenho](#ações-de-desenho)
- [Ações de Controle de Fluxo](#ações-de-controle-de-fluxo)
- [Ações de Saída](#ações-de-saída)

---

## Ações de Movimento

### Definir Velocidade Horizontal
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `set_hspeed` |
| **Ícone** | ↔️ |
| **Preset** | Iniciante |

**Descrição:** Define a velocidade de movimento horizontal.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `value` | Número | 0 | Velocidade em pixels/frame. Positivo=direita, Negativo=esquerda |

---

### Definir Velocidade Vertical
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `set_vspeed` |
| **Ícone** | ↕️ |
| **Preset** | Iniciante |

**Descrição:** Define a velocidade de movimento vertical.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `value` | Número | 0 | Velocidade em pixels/frame. Positivo=baixo, Negativo=cima |

---

### Parar Movimento
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `stop_movement` |
| **Ícone** | 🛑 |
| **Preset** | Iniciante |

**Descrição:** Para todo o movimento (define hspeed e vspeed como 0).

**Parâmetros:** Nenhum

---

### Saltar para Posição
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `jump_to_position` |
| **Ícone** | 📍 |
| **Preset** | Iniciante |

**Descrição:** Move-se instantaneamente para uma posição específica.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `x` | Número | 0 | Coordenada X de destino |
| `y` | Número | 0 | Coordenada Y de destino |

---

### Movimento Fixo
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `move_fixed` |
| **Ícone** | ➡️ |
| **Preset** | Avançado |

**Descrição:** Move-se em uma das 8 direções fixas.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `directions` | Escolha | right | Direção(ões) de movimento |
| `speed` | Número | 4 | Velocidade de movimento |

**Opções de direção:** left, right, up, down, up-left, up-right, down-left, down-right, stop

---

### Movimento Livre
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `move_free` |
| **Ícone** | 🧭 |
| **Preset** | Avançado |

**Descrição:** Move-se em qualquer direção (0-360 graus).

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `direction` | Número | 0 | Direção em graus (0=direita, 90=cima) |
| `speed` | Número | 4 | Velocidade de movimento |

---

### Mover Em Direção A
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `move_towards` |
| **Ícone** | 🎯 |
| **Preset** | Intermediário |

**Descrição:** Move-se em direção a uma posição alvo.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `x` | Expressão | 0 | X alvo (pode usar expressões como `other.x`) |
| `y` | Expressão | 0 | Y alvo |
| `speed` | Número | 4 | Velocidade de movimento |

---

### Definir Velocidade
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `set_speed` |
| **Ícone** | ⚡ |
| **Preset** | Avançado |

**Descrição:** Define a magnitude da velocidade (mantém a direção).

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `speed` | Número | 0 | Magnitude da velocidade |

---

### Definir Direção
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `set_direction` |
| **Ícone** | 🧭 |
| **Preset** | Avançado |

**Descrição:** Define a direção do movimento (mantém a velocidade).

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `direction` | Número | 0 | Direção em graus |

---

### Inverter Horizontal
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `reverse_horizontal` |
| **Ícone** | ↔️ |
| **Preset** | Avançado |

**Descrição:** Inverte a direção horizontal (multiplica hspeed por -1).

**Parâmetros:** Nenhum

---

### Inverter Vertical
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `reverse_vertical` |
| **Ícone** | ↕️ |
| **Preset** | Avançado |

**Descrição:** Inverte a direção vertical (multiplica vspeed por -1).

**Parâmetros:** Nenhum

---

### Definir Gravidade
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `set_gravity` |
| **Ícone** | ⬇️ |
| **Preset** | Platformer |

**Descrição:** Aplica gravidade à instância.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `direction` | Número | 270 | Direção da gravidade (270=baixo) |
| `gravity` | Número | 0.5 | Força da gravidade |

---

### Definir Atrito
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `set_friction` |
| **Ícone** | 🛑 |
| **Preset** | Avançado |

**Descrição:** Aplica atrito (desaceleração gradual).

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `friction` | Número | 0.1 | Quantidade de atrito |

---

## Ações de Instância

### Destruir Instância
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `destroy_instance` |
| **Ícone** | 💥 |
| **Preset** | Iniciante |

**Descrição:** Remove uma instância do jogo.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `target` | Escolha | self | `self` ou `other` (em eventos de colisão) |

---

### Criar Instância
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `create_instance` |
| **Ícone** | ✨ |
| **Preset** | Iniciante |

**Descrição:** Cria uma nova instância de um objeto.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `object` | Objeto | - | Tipo de objeto a criar |
| `x` | Número | 0 | Posição X |
| `y` | Número | 0 | Posição Y |

---

### Definir Sprite
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `set_sprite` |
| **Ícone** | 🖼️ |
| **Preset** | Avançado |

**Descrição:** Altera o sprite da instância.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `sprite` | Sprite | - | Novo sprite |

---

## Ações de Pontuação, Vidas e Saúde

### Definir Pontuação
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `set_score` |
| **Ícone** | 🏆 |
| **Preset** | Iniciante |

**Descrição:** Define ou modifica a pontuação.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `value` | Número | 0 | Valor da pontuação |
| `relative` | Booleano | false | Se verdadeiro, adiciona à pontuação atual |

---

### Adicionar Pontuação (Atalho)
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `add_score` |
| **Ícone** | ➕🏆 |
| **Preset** | Iniciante |

**Descrição:** Adiciona pontos à pontuação.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `value` | Número | 10 | Pontos a adicionar (negativo para subtrair) |

---

### Definir Vidas
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `set_lives` |
| **Ícone** | ❤️ |
| **Preset** | Intermediário |

**Descrição:** Define ou modifica a contagem de vidas.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `value` | Número | 3 | Valor das vidas |
| `relative` | Booleano | false | Se verdadeiro, adiciona às vidas atuais |

**Nota:** Aciona o evento `no_more_lives` quando chega a 0.

---

### Adicionar Vidas (Atalho)
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `add_lives` |
| **Ícone** | ➕❤️ |
| **Preset** | Intermediário |

**Descrição:** Adiciona ou remove vidas.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `value` | Número | 1 | Vidas a adicionar (negativo para subtrair) |

---

### Definir Saúde
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `set_health` |
| **Ícone** | 💚 |
| **Preset** | Intermediário |

**Descrição:** Define ou modifica a saúde (0-100).

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `value` | Número | 100 | Valor da saúde |
| `relative` | Booleano | false | Se verdadeiro, adiciona à saúde atual |

**Nota:** Aciona o evento `no_more_health` quando chega a 0.

---

### Adicionar Saúde (Atalho)
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `add_health` |
| **Ícone** | ➕💚 |
| **Preset** | Intermediário |

**Descrição:** Adiciona ou remove saúde.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `value` | Número | 10 | Saúde a adicionar (negativo para dano) |

---

### Desenhar Pontuação
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `draw_score` |
| **Ícone** | 🖼️🏆 |
| **Preset** | Iniciante |

**Descrição:** Exibe a pontuação na tela.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `x` | Número | 10 | Posição X |
| `y` | Número | 10 | Posição Y |
| `caption` | String | "Score: " | Texto antes da pontuação |

---

### Desenhar Vidas
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `draw_lives` |
| **Ícone** | 🖼️❤️ |
| **Preset** | Intermediário |

**Descrição:** Exibe as vidas na tela.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `x` | Número | 10 | Posição X |
| `y` | Número | 30 | Posição Y |
| `sprite` | Sprite | - | Sprite de ícone de vida opcional |

---

### Desenhar Barra de Saúde
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `draw_health_bar` |
| **Ícone** | 📊💚 |
| **Preset** | Intermediário |

**Descrição:** Desenha uma barra de saúde.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `x1` | Número | 10 | X esquerda |
| `y1` | Número | 50 | Y superior |
| `x2` | Número | 110 | X direita |
| `y2` | Número | 60 | Y inferior |
| `back_color` | Cor | gray | Cor de fundo |
| `bar_color` | Cor | green | Cor da barra |

---

## Ações de Sala

### Próxima Sala
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `next_room` |
| **Ícone** | ➡️ |
| **Preset** | Iniciante |

**Descrição:** Ir para a próxima sala na ordem das salas.

**Parâmetros:** Nenhum

---

### Sala Anterior
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `previous_room` |
| **Ícone** | ⬅️ |
| **Preset** | Iniciante |

**Descrição:** Ir para a sala anterior na ordem das salas.

**Parâmetros:** Nenhum

---

### Reiniciar Sala
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `restart_room` |
| **Ícone** | 🔄 |
| **Preset** | Iniciante |

**Descrição:** Reinicia a sala atual.

**Parâmetros:** Nenhum

---

### Ir para Sala
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `goto_room` |
| **Ícone** | 🚪 |
| **Preset** | Iniciante |

**Descrição:** Ir para uma sala específica.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `room` | Sala | - | Sala de destino |

---

### Se Próxima Sala Existe
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `if_next_room_exists` |
| **Ícone** | ❓➡️ |
| **Preset** | Iniciante |

**Descrição:** Condicional - executa ações apenas se existe uma próxima sala.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `then_actions` | Lista de Ações | Ações se a próxima sala existe |
| `else_actions` | Lista de Ações | Ações se não há próxima sala |

---

### Se Sala Anterior Existe
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `if_previous_room_exists` |
| **Ícone** | ❓⬅️ |
| **Preset** | Iniciante |

**Descrição:** Condicional - executa ações apenas se existe uma sala anterior.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `then_actions` | Lista de Ações | Ações se a sala anterior existe |
| `else_actions` | Lista de Ações | Ações se não há sala anterior |

---

## Ações de Temporização

### Definir Alarme
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `set_alarm` |
| **Ícone** | ⏰ |
| **Preset** | Intermediário |

**Descrição:** Define um alarme para disparar após um atraso.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `alarm` | Número | 0 | Número do alarme (0-11) |
| `steps` | Número | 60 | Passos até o alarme disparar |

**Nota:** A 60 FPS, 60 passos = 1 segundo.

---

## Ações de Som

### Reproduzir Som
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `play_sound` |
| **Ícone** | 🔊 |
| **Preset** | Intermediário |

**Descrição:** Reproduz um efeito sonoro.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `sound` | Som | - | Recurso de som |
| `loop` | Booleano | false | Repetir o som em loop |

---

### Reproduzir Música
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `play_music` |
| **Ícone** | 🎵 |
| **Preset** | Intermediário |

**Descrição:** Reproduz música de fundo.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `sound` | Som | - | Recurso de música |
| `loop` | Booleano | true | Repetir a música em loop |

---

### Parar Música
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `stop_music` |
| **Ícone** | 🔇 |
| **Preset** | Intermediário |

**Descrição:** Para toda a música em reprodução.

**Parâmetros:** Nenhum

---

### Definir Volume
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `set_volume` |
| **Ícone** | 🔉 |
| **Preset** | Avançado |

**Descrição:** Define o volume de áudio.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `volume` | Número | 1.0 | Nível de volume (0.0 a 1.0) |

---

## Ações de Desenho

### Desenhar Texto
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `draw_text` |
| **Ícone** | 📝 |
| **Preset** | Avançado |

**Descrição:** Desenha texto na tela.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `x` | Número | 0 | Posição X |
| `y` | Número | 0 | Posição Y |
| `text` | String | "" | Texto a desenhar |
| `color` | Cor | white | Cor do texto |

---

### Desenhar Retângulo
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `draw_rectangle` |
| **Ícone** | ⬛ |
| **Preset** | Avançado |

**Descrição:** Desenha um retângulo.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `x1` | Número | 0 | X esquerda |
| `y1` | Número | 0 | Y superior |
| `x2` | Número | 32 | X direita |
| `y2` | Número | 32 | Y inferior |
| `color` | Cor | white | Cor de preenchimento |
| `outline` | Booleano | false | Apenas contorno |

---

### Desenhar Círculo
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `draw_circle` |
| **Ícone** | ⚪ |
| **Preset** | Avançado |

**Descrição:** Desenha um círculo.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `x` | Número | 0 | Centro X |
| `y` | Número | 0 | Centro Y |
| `radius` | Número | 16 | Raio |
| `color` | Cor | white | Cor de preenchimento |
| `outline` | Booleano | false | Apenas contorno |

---

### Definir Alfa
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `set_alpha` |
| **Ícone** | 👻 |
| **Preset** | Avançado |

**Descrição:** Define a transparência do desenho.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `alpha` | Número | 1.0 | Transparência (0.0=invisível, 1.0=opaco) |

---

## Ações de Controle de Fluxo

### Se Colisão Em
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `if_collision_at` |
| **Ícone** | 🎯 |
| **Preset** | Avançado |

**Descrição:** Verifica colisão em uma posição.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `x` | Expressão | Posição X a verificar |
| `y` | Expressão | Posição Y a verificar |
| `object_type` | Escolha | `any` ou `solid` |
| `then_actions` | Lista de Ações | Se colisão encontrada |
| `else_actions` | Lista de Ações | Se não há colisão |

---

## Ações de Saída

### Mostrar Mensagem
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `show_message` |
| **Ícone** | 💬 |
| **Preset** | Iniciante |

**Descrição:** Exibe uma mensagem popup.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `message` | String | "Hello!" | Texto da mensagem |

**Nota:** O jogo pausa enquanto a mensagem é exibida.

---

### Executar Código
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `execute_code` |
| **Ícone** | 💻 |
| **Preset** | Iniciante |

**Descrição:** Executa código Python personalizado.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `code` | Código | "" | Código Python a executar |

**Aviso:** Recurso avançado. Use com cautela.

---

### Terminar Jogo
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `end_game` |
| **Ícone** | 🚪 |
| **Preset** | Avançado |

**Descrição:** Termina o jogo e fecha a janela.

**Parâmetros:** Nenhum

---

### Reiniciar Jogo
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `restart_game` |
| **Ícone** | 🔄 |
| **Preset** | Avançado |

**Descrição:** Reinicia o jogo a partir da primeira sala.

**Parâmetros:** Nenhum

---

## Ações por Preset

| Preset | Contagem de Ações | Categorias |
|--------|-------------------|------------|
| **Iniciante** | 17 | Movimento, Instância, Pontuação, Sala, Saída |
| **Intermediário** | 29 | + Vidas, Saúde, Som, Temporização |
| **Avançado** | 40+ | + Desenho, Controle de Fluxo, Jogo |

---

## Veja Também

- [Referência de Eventos](Event-Reference_pt) - Lista completa de eventos
- [Preset Iniciante](Beginner-Preset_pt) - Ações essenciais para iniciantes
- [Preset Intermediário](Intermediate-Preset_pt) - Ações adicionais
- [Eventos e Ações](Events-and-Actions_pt) - Visão geral dos conceitos básicos
