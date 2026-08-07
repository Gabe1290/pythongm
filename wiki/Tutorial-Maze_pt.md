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
**Preset:** Preset Intermediário (a ação Execute Code usada para o
cronômetro não está no preset Iniciante)

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

1. Na **Árvore de Recursos**, clique com o botão direito em **Sprites** e selecione **Create Sprite**
2. Nomeie como `spr_player`
3. Clique em **Edit Sprite** para abrir o editor
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

1. Clique com o botão direito em **Objects** e selecione **Create Object**
2. Nomeie como `obj_wall`
3. Defina o sprite como `spr_wall`
4. **Marque a caixa "Solid"**
5. Nenhum evento necessário

---

## Passo 4: Criar o Objeto Saída

A saída termina o nível quando o jogador a alcança.

1. Crie um novo objeto chamado `obj_exit`
2. Defina o sprite como `spr_exit`

**Evento: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Output** → **Show Message**
   - Message: `You Win!`
3. Add Action: **Room** → **Next Room** (ou **Restart Room** para um único nível)

O texto de Show Message é uma string fixa — não pode incluir um valor
dinâmico como o tempo decorrido. O cronômetro permanece visível no HUD
(Passo 7) até a vitória, então o jogador já viu seu tempo.

---

## Passo 5: Criar o Objeto Moeda

Moedas adicionam à pontuação quando coletadas.

1. Crie um novo objeto chamado `obj_coin`
2. Defina o sprite como `spr_coin`

**Evento: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Score** → **Set Score**
   - New Score: `10`
   - Marque "Relative" para adicionar 10 pontos
3. Add Action: **Instance** → **Destroy Instance**
   - Applies to: Self

---

## Passo 6: Criar o Objeto Jogador

O jogador se move suavemente usando as teclas de seta.

1. Crie um novo objeto chamado `obj_player`
2. Defina o sprite como `spr_player`

### 6.1 Movimento

Adicione quatro eventos **Keyboard (held)** mais um evento **No Key**,
cada um com uma ação **Move** → **Set Horizontal/Vertical Speed**:

| Evento | Ação |
|---|---|
| Keyboard (held) → Right Arrow | Set Horizontal Speed para `4` |
| Keyboard (held) → Left Arrow | Set Horizontal Speed para `-4` |
| Keyboard (held) → Down Arrow | Set Vertical Speed para `4` |
| Keyboard (held) → Up Arrow | Set Vertical Speed para `-4` |
| Keyboard: No Key | Set Horizontal Speed para `0` **e** Set Vertical Speed para `0` |

### 6.2 Parar nas Paredes

**Evento: Collision with obj_wall**
1. Add Event → Collision → `obj_wall`
2. Add Action: **Move** → **Stop Movement**

Nenhum código manual de verificação de posição é necessário aqui. O
loop de movimento deste motor já impede que uma instância se mova para
dentro de um objeto sólido antes de o quadro ser desenhado (`obj_wall`
é Solid), então o jogador nunca pode realmente se sobrepor a uma
parede — o evento de colisão acima apenas zera qualquer velocidade
restante, para que o jogador não continue "empurrando" contra ela.

---

## Passo 7: Criar o Game Controller

O game controller gerencia o cronômetro e exibe informações.

1. Crie um novo objeto chamado `obj_game_controller`
2. Nenhum sprite necessário

**Evento: Create** — inicia o cronômetro, usando **Control** →
**Execute Code** (a ação Execute Code deste projeto executa Python
real, não GameMaker Language):

```python
self.timer = 0.0
```

**Evento: Step** — incrementa a cada quadro:

```python
self.timer += 1.0 / game.fps
```

**Evento: Draw** — constrói o HUD com comandos reais da fila de
desenho. Adicione três ações **Draw** → **Draw Text**:

| Ação Draw Text | Texto | Posição |
|---|---|---|
| 1ª | `Score:` | X `10`, Y `10` |
| 2ª | `Time:` | X `10`, Y `30` |
| 3ª | `Coins:` | X `10`, Y `50` |

depois três ações **Draw** → **Draw Variable** logo em seguida, para
mostrar os valores em tempo real ao lado de cada rótulo:

| Ação Draw Variable | Variável | Posição |
|---|---|---|
| 1ª | `score` | X `70`, Y `10` |
| 2ª | `self.timer` | X `70`, Y `30` |
| 3ª | *(veja abaixo)* | X `70`, Y `50` |

Não existe um contador integrado de "moedas restantes" para o Draw
Variable apontar — adicione mais uma ação **Control** → **Execute
Code**, logo antes das ações Draw Variable, para calculá-lo em uma
variável de instância que o Draw Variable possa então ler:

```python
self.coins_left = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_coin'
)
```

(depois defina o campo Variable da 3ª ação Draw Variable como `self.coins_left`).

---

## Passo 8: Projete Seu Labirinto

1. Clique com o botão direito em **Rooms** e selecione **Create Room**
2. Nomeie como `room_maze`
3. Defina o tamanho da sala (ex: 640x480)
4. Ative "Snap to Grid" e defina a grade como 32x32

### Posicionamento de Objetos

Construa seu labirinto seguindo estas diretrizes:

1. **Crie a borda** - Cerque a sala com paredes
2. **Construa corredores** - Crie caminhos através do labirinto
3. **Posicione a saída** - Coloque-a no final do labirinto
4. **Espalhe moedas** - Posicione-as ao longo dos caminhos
5. **Posicione o jogador** - Perto da entrada
6. **Adicione o game controller** - Em qualquer lugar (é invisível)

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

1. Clique em **Run** ou pressione **F5** para testar
2. Use as teclas de seta para navegar pelo labirinto
3. Colete moedas para pontos
4. Encontre a saída para vencer!

---

## Melhorias (Opcional)

### Adicionar Inimigos

Crie um inimigo patrulhador simples:

1. Crie `spr_enemy` (cor vermelha, 24x24)
2. Crie `obj_enemy` com sprite `spr_enemy`

**Evento: Create** — Add Action: **Move** → **Start Moving Direction**
(Directions: `right`, Speed: `2`)

**Evento: Collision with obj_wall** — Add Action: **Move** → **Reverse
Horizontal** (faz o inimigo virar ao bater em uma parede — nenhum
código necessário; combinado com a colisão sólida integrada do Passo
6.2, o inimigo nunca consegue atravessar uma parede)

**Evento: Collision with obj_player** — Add Action: **Room** →
**Restart Room**

### Adicionar Sistema de Vidas

No evento **Create** de `obj_game_controller`, adicione **Score** →
**Set Lives** (Value: `3`).

No evento **Collision with obj_player** de `obj_enemy`, substitua
**Restart Room** por duas ações: **Score** → **Set Lives** (Value:
`-1`, **Relative** marcado), depois **Move** → **Jump to Start
Position** (aplicada ao jogador via **Applies to: Other**) para
reaparecer o jogador em vez de reiniciar todo o labirinto.

Adicione mais um evento a `obj_game_controller`: **Other Events** →
**No More Lives** — isso é acionado automaticamente assim que as vidas
chegam a 0, então você não precisa verificar isso manualmente. Adicione
**Output** → **Show Message** (`Game Over!`) seguido de **Room** →
**Restart Game**.

### Adicionar Chaves e Portas Trancadas

1. Crie `obj_key` — ao colidir com `obj_player`, **Set Variable**
   (Variable: `global.has_key`, Value: `true`, Scope: `global`), depois
   **Destroy Instance** (self).
2. Crie `obj_locked_door`, com Solid marcado. Dê a ele um evento
   **Step** com **Control** → **Test Variable** (Variable:
   `global.has_key`, Value: `true`, Scope: `global`) → **Instance** →
   **Destroy Instance** (self) — a porta desaparece (e para de
   bloquear) assim que a chave é coletada.

### Adicionar Múltiplos Níveis

1. Crie salas adicionais (`room_maze2`, `room_maze3`)
2. Em `obj_exit`, use a ação **Next Room** em vez de **Restart Room**

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
| Jogador atravessa paredes | Verifique se `obj_wall` tem "Solid" marcado |
| Jogador fica preso nas paredes | Certifique-se de que o sprite do jogador é menor que os espaços entre paredes |
| Moedas não desaparecem | Verifique se o evento de colisão destrói Self, não Other |
| Cronômetro não funciona | Certifique-se de que o game controller está colocado na sala |
| Movimento parece travado | Ajuste o valor de velocidade nas ações Set Horizontal/Vertical Speed (tente 3-5) |

---

## O Que Você Aprendeu

Parabéns! Você criou um jogo de labirinto! Você aprendeu:

- **Movimento suave** - Verificar estado de tecla mantida para movimento contínuo
- **Colisão sólida integrada** - Paredes bloqueiam o movimento automaticamente uma vez marcadas como Solid, sem código manual de verificação de posição
- **Colecionáveis** - Criar itens que aumentam a pontuação e desaparecem
- **Sistema de cronômetro** - Rastrear tempo decorrido com variáveis de instância
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
- [Intermediate Preset](Intermediate-Preset_pt) - Visão geral do preset necessário para este tutorial
- [Tutorial: Pong](Tutorial-Pong_pt) - Criar um jogo de dois jogadores
- [Tutorial: Breakout](Tutorial-Breakout_pt) - Criar um jogo de quebrar tijolos
- [Tutorial: Sokoban](Tutorial-Sokoban_pt) - Criar um puzzle de empurrar caixas
- [Referência de Eventos](Event-Reference_pt) - Documentação completa de eventos
