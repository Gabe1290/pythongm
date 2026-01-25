# Tutorial: Criar um Jogo de Labirinto

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Maze) | [Français](Tutorial-Maze_fr) | [Deutsch](Tutorial-Maze_de) | [Italiano](Tutorial-Maze_it) | [Español](Tutorial-Maze_es) | [Português](Tutorial-Maze_pt) | [Slovenščina](Tutorial-Maze_sl) | [Українська](Tutorial-Maze_uk) | [Русский](Tutorial-Maze_ru)

---

## Introdução

Neste tutorial, você criará um **Jogo de Labirinto** onde o jogador navega através de corredores para alcançar a saída enquanto evita obstáculos e coleta moedas. Este tipo clássico de jogo é perfeito para aprender movimento suave, detecção de colisão e design de níveis.

**O que você aprenderá:**
- Movimento suave do jogador com entrada de teclado
- Tratamento de colisão com paredes
- Detecção de objetivo (alcançar a saída)
- Itens colecionáveis
- Sistema de cronômetro simples

**Dificuldade:** Iniciante
**Preset:** Preset Iniciante

---

## Passo 1: Entender o Jogo

### Regras do Jogo
1. O jogador se move pelo labirinto usando as teclas de seta
2. Paredes bloqueiam o movimento do jogador
3. Colete moedas para pontos
4. Alcance a saída para completar o nível
5. Complete o labirinto o mais rápido possível!

### O Que Precisamos

| Elemento | Propósito |
|----------|-----------|
| **Jogador** | O personagem que você controla |
| **Parede** | Obstáculos sólidos que bloqueiam movimento |
| **Saída** | Objetivo que termina o nível |
| **Moeda** | Itens colecionáveis para pontuação |
| **Chão** | Fundo visual (opcional) |

---

## Passo 2: Criar os Sprites

Todos os sprites de parede e chão devem ter 32x32 pixels para criar uma grade adequada.

### 2.1 Sprite do Jogador

1. Na **Árvore de Recursos**, clique com o botão direito em **Sprites** e selecione **Criar Sprite**
2. Nomeie como `spr_player`
3. Clique em **Editar Sprite** para abrir o editor
4. Desenhe um pequeno personagem (círculo, pessoa ou forma de seta)
5. Use uma cor brilhante como azul ou verde
6. Tamanho: 24x24 pixels (menor que as paredes para navegação mais fácil)
7. Clique em **OK** para salvar

### 2.2 Sprite da Parede

1. Crie um novo sprite chamado `spr_wall`
2. Desenhe um padrão sólido de tijolo ou pedra
3. Use cores cinza ou escuras
4. Tamanho: 32x32 pixels

### 2.3 Sprite da Saída

1. Crie um novo sprite chamado `spr_exit`
2. Desenhe uma porta, bandeira ou marcador de objetivo brilhante
3. Use cores verdes ou douradas
4. Tamanho: 32x32 pixels

### 2.4 Sprite da Moeda

1. Crie um novo sprite chamado `spr_coin`
2. Desenhe um pequeno círculo amarelo/dourado
3. Tamanho: 16x16 pixels

### 2.5 Sprite do Chão (Opcional)

1. Crie um novo sprite chamado `spr_floor`
2. Desenhe um padrão simples de piso
3. Use uma cor neutra clara
4. Tamanho: 32x32 pixels

---

## Passo 3: Criar o Objeto Parede

A parede bloqueia o movimento do jogador.

1. Clique com o botão direito em **Objetos** e selecione **Criar Objeto**
2. Nomeie como `obj_wall`
3. Defina o sprite como `spr_wall`
4. **Marque a caixa "Sólido"**
5. Nenhum evento necessário

---

## Passo 4: Criar o Objeto Saída

A saída termina o nível quando o jogador a alcança.

1. Crie um novo objeto chamado `obj_exit`
2. Defina o sprite como `spr_exit`

**Evento: Colisão com obj_player**
1. Adicionar Evento → Colisão → obj_player
2. Adicionar Ação: **Main2** → **Mostrar Mensagem**
   - Mensagem: `Você venceu! Tempo: ` + string(floor(global.timer)) + ` segundos`
3. Adicionar Ação: **Main1** → **Próxima Room** (ou **Reiniciar Room** para um único nível)

---

## Passo 5: Criar o Objeto Moeda

Moedas adicionam à pontuação quando coletadas.

1. Crie um novo objeto chamado `obj_coin`
2. Defina o sprite como `spr_coin`

**Evento: Colisão com obj_player**
1. Adicionar Evento → Colisão → obj_player
2. Adicionar Ação: **Score** → **Definir Score**
   - Novo Score: `10`
   - Marque "Relativo" para adicionar 10 pontos
3. Adicionar Ação: **Main1** → **Destruir Instância**
   - Aplica-se a: Self

---

## Passo 6: Criar o Objeto Jogador

O jogador se move suavemente usando as teclas de seta.

1. Crie um novo objeto chamado `obj_player`
2. Defina o sprite como `spr_player`

### 6.1 Evento Create - Inicializar Variáveis

**Evento: Create**
1. Adicionar Evento → Create
2. Adicionar Ação: **Controle** → **Definir Variável**
   - Variável: `move_speed`
   - Valor: `4`

### 6.2 Movimento com Colisão

**Evento: Step**
1. Adicionar Evento → Step → Step
2. Adicionar Ação: **Controle** → **Executar Código**

```gml
// Movimento horizontal
var hspd = 0;
if (keyboard_check(vk_right)) hspd = move_speed;
if (keyboard_check(vk_left)) hspd = -move_speed;

// Movimento vertical
var vspd = 0;
if (keyboard_check(vk_down)) vspd = move_speed;
if (keyboard_check(vk_up)) vspd = -move_speed;

// Verificação de colisão horizontal
if (!place_meeting(x + hspd, y, obj_wall)) {
    x += hspd;
} else {
    // Mover o mais perto possível da parede
    while (!place_meeting(x + sign(hspd), y, obj_wall)) {
        x += sign(hspd);
    }
}

// Verificação de colisão vertical
if (!place_meeting(x, y + vspd, obj_wall)) {
    y += vspd;
} else {
    // Mover o mais perto possível da parede
    while (!place_meeting(x, y + sign(vspd), obj_wall)) {
        y += sign(vspd);
    }
}
```

### 6.3 Alternativa: Movimento Simples por Blocos

Se você preferir usar blocos de ação em vez de código:

**Evento: Tecla Pressionada - Seta Direita**
1. Adicionar Evento → Teclado → \<Direita\>
2. Adicionar Ação: **Controle** → **Testar Colisão**
   - Objeto: `obj_wall`
   - X: `4`
   - Y: `0`
   - Verificar: NOT
3. Adicionar Ação: **Movimento** → **Saltar para Posição**
   - X: `4`
   - Y: `0`
   - Marque "Relativo"

Repita para Esquerda (-4, 0), Cima (0, -4) e Baixo (0, 4).

---

## Passo 7: Criar o Controlador do Jogo

O controlador do jogo gerencia o cronômetro e exibe informações.

1. Crie um novo objeto chamado `obj_game_controller`
2. Nenhum sprite necessário

**Evento: Create**
1. Adicionar Evento → Create
2. Adicionar Ação: **Controle** → **Definir Variável**
   - Variável: `global.timer`
   - Valor: `0`

**Evento: Step**
1. Adicionar Evento → Step → Step
2. Adicionar Ação: **Controle** → **Definir Variável**
   - Variável: `global.timer`
   - Valor: `1/room_speed`
   - Marque "Relativo"

**Evento: Draw**
1. Adicionar Evento → Draw → Draw
2. Adicionar Ação: **Controle** → **Executar Código**

```gml
// Desenhar pontuação
draw_set_color(c_white);
draw_text(10, 10, "Pontos: " + string(score));

// Desenhar cronômetro
draw_text(10, 30, "Tempo: " + string(floor(global.timer)) + "s");

// Desenhar moedas restantes
var coins_left = instance_number(obj_coin);
draw_text(10, 50, "Moedas: " + string(coins_left));
```

---

## Passo 8: Projete Seu Labirinto

1. Clique com o botão direito em **Rooms** e selecione **Criar Room**
2. Nomeie como `room_maze`
3. Defina o tamanho da room (ex: 640x480)
4. Ative "Alinhar à Grade" e defina a grade como 32x32

### Posicionamento de Objetos

Construa seu labirinto seguindo estas diretrizes:

1. **Crie a borda** - Cerque a room com paredes
2. **Construa corredores** - Crie caminhos através do labirinto
3. **Posicione a saída** - Coloque-a no final do labirinto
4. **Espalhe moedas** - Posicione-as ao longo dos caminhos
5. **Posicione o jogador** - Perto da entrada
6. **Adicione o controlador do jogo** - Em qualquer lugar (é invisível)

### Exemplo de Layout de Labirinto

```
W W W W W W W W W W W W W W W W W W W W
W P . . . . W . . . . . . . W . . . . W
W . W W W . W . W W W W W . W . W W . W
W . W . . . . . . . . . . . . . . W . W
W . W . W W W W W . W W W W W W . W . W
W . . . W . . . . . . . . C . W . . . W
W W W . W . W W W W W W W . . W W W . W
W C . . . . W . . . . . W . . . . . . W
W . W W W W W . W W W . W W W W W W . W
W . . . . . . . . C . . . . . . . . . W
W . W W W W W W W W W . W W W W W W . W
W . . . . . . . . . . . W . . . . . . W
W W W W W W W W W W W . W . W W W W . W
W . . . . . . . . . . . . . W . C . E W
W W W W W W W W W W W W W W W W W W W W

W = Parede    P = Jogador    E = Saída    C = Moeda    . = Vazio
```

---

## Passo 9: Teste Seu Jogo!

1. Clique em **Executar** ou pressione **F5** para testar
2. Use as teclas de seta para navegar pelo labirinto
3. Colete moedas para pontos
4. Encontre a saída para vencer!

---

## Melhorias (Opcional)

### Adicionar Inimigos

Crie um inimigo patrulhador simples:

1. Crie `spr_enemy` (cor vermelha, 24x24)
2. Crie `obj_enemy` com sprite `spr_enemy`

**Evento: Create**
```gml
hspeed = 2;  // Move horizontalmente
```

**Evento: Colisão com obj_wall**
```gml
hspeed = -hspeed;  // Inverter direção
```

**Evento: Colisão com obj_player**
```gml
room_restart();  // Jogador perde
```

### Adicionar Sistema de Vidas

No evento Create de `obj_game_controller`:
```gml
global.lives = 3;
```

Quando o jogador toca um inimigo (em vez de reiniciar):
```gml
global.lives -= 1;
if (global.lives <= 0) {
    show_message("Game Over!");
    game_restart();
} else {
    // Reaparecer jogador no início
    obj_player.x = start_x;
    obj_player.y = start_y;
}
```

### Adicionar Chaves e Portas Trancadas

1. Crie `obj_key` - desaparece quando coletada, define `global.has_key = true`
2. Crie `obj_locked_door` - só abre quando `global.has_key == true`

### Adicionar Múltiplos Níveis

1. Crie rooms adicionais (`room_maze2`, `room_maze3`)
2. Em `obj_exit`, use `room_goto_next()` em vez de `room_restart()`

### Adicionar Efeitos Sonoros

Adicione sons para:
- Coletar moedas
- Alcançar a saída
- Tocar inimigos (se adicionados)
- Música de fundo

---

## Solução de Problemas

| Problema | Solução |
|----------|---------|
| Jogador atravessa paredes | Verifique se `obj_wall` tem "Sólido" marcado |
| Jogador fica preso nas paredes | Certifique-se de que o sprite do jogador é menor que os espaços entre paredes |
| Moedas não desaparecem | Verifique se o evento de colisão destrói Self, não Other |
| Cronômetro não funciona | Certifique-se de que o controlador do jogo está colocado na room |
| Movimento parece travado | Ajuste o valor de `move_speed` (tente 3-5) |

---

## O Que Você Aprendeu

Parabéns! Você criou um jogo de labirinto! Você aprendeu:

- **Movimento suave** - Verificar estado de tecla pressionada para movimento contínuo
- **Detecção de colisão** - Usar `place_meeting` para verificar antes de mover
- **Colisão pixel-perfect** - Mover o mais perto possível das paredes
- **Colecionáveis** - Criar itens que aumentam a pontuação e desaparecem
- **Sistema de cronômetro** - Rastrear tempo decorrido com variáveis
- **Design de níveis** - Criar layouts de labirinto navegáveis

---

## Ideias de Desafios

1. **Contra o Relógio** - Adicione um cronômetro de contagem regressiva. Alcance a saída antes do tempo acabar!
2. **Pontuação Perfeita** - Exija coletar todas as moedas antes da saída abrir
3. **Labirinto Aleatório** - Pesquise geração procedural de labirintos
4. **Névoa de Guerra** - Mostre apenas a área ao redor do jogador
5. **Minimapa** - Exiba uma pequena visão geral do labirinto

---

## Veja Também

- [Tutoriais](Tutorials_pt) - Mais tutoriais de jogos
- [Preset Iniciante](Beginner-Preset_pt) - Visão geral dos recursos para iniciantes
- [Tutorial: Pong](Tutorial-Pong_pt) - Criar um jogo de dois jogadores
- [Tutorial: Breakout](Tutorial-Breakout_pt) - Criar um jogo de quebrar tijolos
- [Tutorial: Sokoban](Tutorial-Sokoban_pt) - Criar um puzzle de empurrar caixas
- [Referência de Eventos](Event-Reference_pt) - Documentação completa de eventos
