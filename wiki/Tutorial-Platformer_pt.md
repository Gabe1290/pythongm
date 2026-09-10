# Tutorial: Criar um Jogo de Plataforma

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Platformer) | [Français](Tutorial-Platformer_fr) | [Deutsch](Tutorial-Platformer_de) | [Italiano](Tutorial-Platformer_it) | [Español](Tutorial-Platformer_es) | [Português](Tutorial-Platformer_pt) | [Slovenščina](Tutorial-Platformer_sl) | [Українська](Tutorial-Platformer_uk) | [Русский](Tutorial-Platformer_ru)

---

## Introdução

Neste tutorial, você vai criar um **Jogo de Plataforma** - um jogo de ação com rolagem lateral onde o jogador corre, salta e navega por plataformas enquanto evita perigos e coleta moedas. Este gênero clássico é perfeito para aprender gravidade, mecânicas de salto e colisão com plataformas.

**O que você vai aprender:**
- Gravidade e física de queda
- Mecânicas de salto com detecção do chão
- Colisão com plataformas (aterrissar em cima)
- Movimento esquerda/direita
- Coletáveis e perigos

**Dificuldade:** Iniciante
**Preset:** Preset Intermediário (as ações Execute Code da seção Melhorias não estão no preset Iniciante; o tutorial base até o Passo 10 só precisa de ações do preset Iniciante)

---

## Passo 1: Entender o Jogo

### Mecânicas do Jogo
1. O jogador é afetado pela gravidade e cai
2. O jogador pode se mover para a esquerda e para a direita
3. O jogador pode saltar quando está no chão
4. As plataformas impedem o jogador de cair através
5. Colete moedas por pontos
6. Alcance a bandeira para completar o nível

### O Que Precisamos

| Elemento | Finalidade |
|----------|------------|
| **Jogador** | O personagem que você controla |
| **Chão/Plataforma** | Superfícies sólidas para ficar em pé |
| **Moeda** | Itens coletáveis para pontuação |
| **Espinho** | Perigo que fere o jogador |
| **Bandeira** | Objetivo que termina o nível |

---

## Passo 2: Criar os Sprites

### 2.1 Sprite do Jogador

1. Na **Árvore de Recursos**, clique com o botão direito em **Sprites** e selecione **Create Sprite**
2. Nomeie-o `spr_player`
3. Clique em **Edit Sprite** para abrir o editor de sprites
4. Desenhe um personagem simples (retângulo com rosto, ou boneco palito)
5. Use uma cor viva como azul ou vermelho
6. Tamanho: 32x48 pixels (mais alto que largo para um personagem)
7. Clique em **OK** para salvar

### 2.2 Sprite do Chão

1. Crie um novo sprite chamado `spr_ground`
2. Desenhe um bloco de plataforma de grama/terra
3. Use cores marrom e verde
4. Tamanho: 32x32 pixels

### 2.3 Sprite da Plataforma

1. Crie um novo sprite chamado `spr_platform`
2. Desenhe uma plataforma flutuante (madeira ou pedra)
3. Tamanho: 64x16 pixels (larga e fina)

### 2.4 Sprite da Moeda

1. Crie um novo sprite chamado `spr_coin`
2. Desenhe um pequeno círculo amarelo/dourado
3. Tamanho: 16x16 pixels

### 2.5 Sprite do Espinho

1. Crie um novo sprite chamado `spr_spike`
2. Desenhe espinhos triangulares apontando para cima
3. Use cores cinza ou vermelho
4. Tamanho: 32x32 pixels

### 2.6 Sprite da Bandeira

1. Crie um novo sprite chamado `spr_flag`
2. Desenhe uma bandeira em um mastro
3. Use cores vivas (bandeira verde, mastro marrom)
4. Tamanho: 32x64 pixels

![The Sprite Editor with spr_player open (32x48), origin centered; spr_player, spr_ground, spr_platform, spr_coin, spr_spike and spr_flag in the resource tree](images/tutorial-platformer-02-sprites.png)

---

## Passo 3: Criar o Objeto Chão

O chão é uma plataforma sólida que impede o jogador de cair.

1. Clique com o botão direito em **Objects** e selecione **Create Object**
2. Nomeie-o `obj_ground`
3. Defina o sprite como `spr_ground`
4. **Marque a caixa "Solid"**
5. Nenhum evento necessário

![obj_ground's Object Events panel: empty -- Solid checked is all it needs](images/tutorial-platformer-03-ground-object.png)

---

## Passo 4: Criar o Objeto Plataforma

As plataformas funcionam como o chão, mas podem ser colocadas no ar.

1. Crie um novo objeto chamado `obj_platform`
2. Defina o sprite como `spr_platform`
3. **Marque a caixa "Solid"**
4. Nenhum evento necessário

**Dica:** você pode fazer da plataforma um filho de `obj_ground` para compartilhar o mesmo comportamento de colisão.

![obj_platform's Object Events panel: empty, with Solid checked -- a wide, thin sprite is the only difference from obj_ground](images/tutorial-platformer-04-platform-object.png)

---

## Passo 5: Criar o Objeto Jogador

O jogador é o objeto mais complexo, com gravidade, salto e movimento.

1. Crie um novo objeto chamado `obj_player`
2. Defina o sprite como `spr_player`

### 5.1 Gravidade

**Evento: Create** — Adicione a ação **Move** → **Set Gravity**
(Direction: `270`, Gravity: `0.5`) — 270° é diretamente para baixo; o
valor é somado à velocidade vertical do jogador a cada passo, então o
jogador acelera para baixo sozinho a partir daqui.

### 5.2 Movimento, Salto e Colisão com o Chão

Adicione estes eventos, seguindo o mesmo padrão que os tutoriais
anteriores deste wiki já usam:

| Evento | Ação |
|---|---|
| Keyboard (held) → Left Arrow | Set Horizontal Speed para `-4` |
| Keyboard (held) → Right Arrow | Set Horizontal Speed para `4` |
| Keyboard: No Key | Set Horizontal Speed para `0` |
| Key Press → Up Arrow | Set Vertical Speed para `-10` |
| Collision with obj_ground | Stop Movement |

Dois detalhes que fazem a sensação ficar certa:

- **No Key zera APENAS a velocidade horizontal** — nunca use
  Stop Movement aí, porque Stop Movement zera a velocidade vertical
  também, o que cancelaria a gravidade toda vez que o jogador soltasse
  uma tecla de direção.
- **Key Press (não held)** é o que faz Up ser um único impulso de salto,
  em vez de lançar o jogador para cima a cada frame em que é mantido
  pressionado. **Stop Movement** na aterrissagem então cancela esse
  impulso, para que o jogador não continue subindo depois de pousar — a
  colisão sólida integrada do motor (o Passo 3 já tornou `obj_ground`
  Solid) já impede o jogador de afundar no chão; o evento aqui apenas
  limpa a velocidade de queda restante.

![obj_player's Object Events panel: Create (Set Gravity), Keyboard (held) with two Set Horizontal Speed actions, Keyboard <No Key>, Keyboard Press with the Up-Arrow jump, and Collision with obj_ground (Stop Movement)](images/tutorial-platformer-05-player-object.png)

---

## Passo 6: Criar o Objeto Moeda

As moedas somam à pontuação quando coletadas.

1. Crie um novo objeto chamado `obj_coin`
2. Defina o sprite como `spr_coin`

**Evento: Collision with obj_player**
1. Adicionar Evento → Collision → obj_player
2. Adicione a ação **Score** → **Set Score**
   - New Score: `10`
   - Marque "Relative"
3. Adicione a ação **Main1** → **Destroy Instance**
   - Applies to: Self

![obj_coin's Object Events panel: a Collision with obj_player event holding Set Score (Relative) and Destroy Instance](images/tutorial-platformer-06-coin-object.png)

---

## Passo 7: Criar o Objeto Espinho

Os espinhos ferem o jogador e reiniciam o nível.

1. Crie um novo objeto chamado `obj_spike`
2. Defina o sprite como `spr_spike`

**Evento: Collision with obj_player**
1. Adicionar Evento → Collision → obj_player
2. Adicione a ação **Main2** → **Show Message**
   - Message: `Ouch! You hit a spike!`
3. Adicione a ação **Main1** → **Restart Room**

![obj_spike's Object Events panel: a Collision with obj_player event holding Show Message and Restart Room](images/tutorial-platformer-07-spike-object.png)

---

## Passo 8: Criar o Objeto Bandeira

A bandeira termina o nível quando o jogador a alcança.

1. Crie um novo objeto chamado `obj_flag`
2. Defina o sprite como `spr_flag`

**Evento: Collision with obj_player**
1. Adicionar Evento → Collision → obj_player
2. Adicione a ação **Output** → **Show Message**
   - Message: `Level Complete!`
3. Adicione a ação **Room** → **Next Room** (ou **Restart Room** para um único nível)

O texto de Show Message é uma string fixa — ele não pode embutir um valor
ao vivo como a pontuação. O HUD do controlador de jogo (Passo 9) já mostra
a pontuação na tela durante todo o nível, então o jogador já a viu.

![obj_flag's Object Events panel: a Collision with obj_player event holding Show Message and Next Room](images/tutorial-platformer-08-flag-object.png)

---

## Passo 9: Criar o Controlador de Jogo

O controlador de jogo exibe a pontuação.

1. Crie um novo objeto chamado `obj_game_controller`
2. Nenhum sprite necessário

**Evento: Draw**
1. Adicionar Evento → Draw → Draw
2. Adicione a ação **Draw** → **Draw Text** (Text: `Score:`, X: `10`, Y: `10`)
3. Adicione a ação **Draw** → **Draw Variable** (Variable: `score`, X: `70`, Y: `10`)

Opcional: adicione um par **Draw Text** (`Lives:`, X `10`, Y `30`) +
**Draw Variable** (`lives`, X `70`, Y `30`) da mesma forma, assim que a
melhoria Sistema de Vidas abaixo estiver no lugar.

![obj_game_controller's Object Events panel: a Draw event with one Draw Text and one Draw Variable action, with no sprite set](images/tutorial-platformer-09-controller-object.png)

---

## Passo 10: Projetar o Seu Nível

1. Clique com o botão direito em **Rooms** e selecione **Create Room**
2. Nomeie-a `room_level1`
3. Defina o tamanho da room (ex.: 800x480)
4. Ative "Snap to Grid" e defina a grade como 32x32

### Colocando os Objetos

Construa o seu nível seguindo estas orientações:

1. **Crie o chão** - Coloque `obj_ground` ao longo da parte inferior
2. **Adicione plataformas** - Coloque `obj_platform` no ar para desafios de salto
3. **Adicione buracos** - Deixe espaços no chão (poços)
4. **Coloque moedas** - Espalhe-as pelas plataformas e em pontos difíceis de alcançar
5. **Adicione espinhos** - Perto dos poços ou nas plataformas como desafio
6. **Coloque a bandeira** - No fim do nível
7. **Coloque o jogador** - No início (lado esquerdo)
8. **Adicione o controlador de jogo** - Em qualquer lugar (ele é invisível)

### Exemplo de Layout de Nível

```
                                        F
                                      ===
                          C       C
                        =====   =====
            C                           C
          ===== X     X         X     =====
    P                   C
  ====== === ===   ===   === === ===== ======
  GGGGGG     GGG   GGG   GGG         GGGGGGGG

G = Chão    P = Jogador    F = Bandeira    C = Moeda
X = Espinho    === = Plataforma
```

![The Room Editor for room_level1: a brown ground row with two pit gaps, four tan floating platforms at rising heights, gold coins on and above them, two grey spikes on the ground, the red player at the far left and the green flag at the far right](images/tutorial-platformer-10-room.png)

---

## Passo 11: Teste o Seu Jogo!

1. Clique em **Executar** ou pressione **F5** para testar
2. Use as setas **Esquerda/Direita** para se mover
3. Pressione **Cima** ou **Espaço** para saltar
4. Colete moedas por pontos
5. Evite os espinhos!
6. Alcance a bandeira para vencer!

---

## Melhorias (Opcional)

### Adicionar Altura de Salto Variável

Adicione um evento **Step** a `obj_player` com **Control** → **Execute
Code** (Python real — `self` é a instância atual, `keyboard` permite
verificar uma tecla mantida pressionada pelo nome):

```python
# Corta o salto se Up for solto enquanto ainda estiver subindo
if self.vspeed < 0 and not keyboard.check('up'):
    self.vspeed = max(self.vspeed, -5)  # metade do impulso de salto -10
```

### Adicionar Salto Duplo

Isso pode ser feito inteiramente com ações estruturadas — nenhum código
necessário.

**Evento: Create** — Adicione a ação **Control** → **Set Variable**
(Variable: `jumps_left`, Value: `2`)

**Evento: Collision with obj_ground** — depois de **Stop Movement**,
adicione **Control** → **Set Variable** (Variable: `jumps_left`, Value:
`2`) para recarregar ambos os saltos na aterrissagem.

Substitua a única ação do evento **Key Press → Up Arrow** existente por
três, em ordem:
1. **Control** → **Test Variable** (Variable: `jumps_left`, Value: `0`,
   Operation: `greater`)
2. **Control** → **Start Block**
3. **Move** → **Set Vertical Speed** (`-10`)
4. **Control** → **Set Variable** (Variable: `jumps_left`, Value: `-1`,
   **Relative** marcado)
5. **Control** → **End Block**

O par Start/End Block significa que ambas as ações dentro dele só são
executadas quando o Test Variable acima é verdadeiro — o mesmo padrão de
bloco protegido que os tutoriais Sokoban e Labirinto usam para suas
próprias condições.

### Adicionar Plataformas Móveis

1. Crie `obj_moving_platform` como filho de `obj_platform`

**Evento: Create** — Adicione a ação **Control** → **Execute Code**:

```python
self.start_x = self.x
self.hspeed = 2
```

**Evento: Step** — Adicione a ação **Control** → **Execute Code**:

```python
if self.x > self.start_x + 100:
    self.hspeed = -2
elif self.x < self.start_x:
    self.hspeed = 2
```

### Adicionar Inimigo

1. Crie `obj_enemy` com uma IA simples

**Evento: Create** — Adicione a ação **Move** → **Start Moving Direction**
(Directions: `right`, Speed: `2`)

**Evento: Collision with obj_ground** — Adicione a ação **Move** →
**Reverse Horizontal** (dá meia-volta nas paredes; combinado com o fato
de `obj_ground` ser Solid, o inimigo nunca pode sair da borda de uma
plataforma para o chão abaixo nem atravessar uma parede)

**Evento: Collision with obj_player** — este evento dispara em
`obj_enemy`, então `self` é o inimigo e `other` é o jogador. Adicione a
ação **Control** → **Test Expression**, com ações Then/Else aninhadas (o
mesmo padrão que o exemplo incluído `plateforme_3` usa exatamente para
esta verificação de "pisão", apenas espelhado porque a verificação vive
no inimigo aqui em vez do jogador):
   - Expression: `other.vspeed > 0 and other.y - other.vspeed < y - 16`
   - Then Actions: **Control** → **Execute Code** com `other.vspeed = -5`
     (um pequeno quique para o jogador — `set_vspeed` não tem opção
     "applies to other", então este é o único ponto que precisa de uma
     linha de Python real em vez de uma ação estruturada), depois
     **Instance** → **Destroy Instance** (self)
   - Else Actions: **Room** → **Restart Room** (o jogador morre)

`other.vspeed > 0 and other.y - other.vspeed < y - 16` verifica a posição
*do jogador* de antes do movimento de queda deste frame (usando o próprio
`vspeed` do jogador, já que é ele quem está caindo), então uma queda
rápida não pode atravessar a janela de pisão de 16 px em um único passo —
veja o README de `plateforme_3` para a história completa de por que a
versão ingênua `other.y < y - 16` é frágil.

### Adicionar Sistema de Vidas

No evento **Create** de `obj_game_controller`, adicione **Score** → **Set
Lives** (Value: `3`).

Quando o jogador morre (a colisão com o espinho e o ramo Else do inimigo
acima), substitua **Restart Room** por **Score** → **Set Lives** (Value:
`-1`, **Relative** marcado) — a room reinicia automaticamente porque o
evento **No More Lives** só dispara quando as vidas realmente chegam a 0.
Adicione esse evento a `obj_game_controller`: **Other Events** → **No More
Lives** → **Output** → **Show Message** (`Game Over!`) → **Room** →
**Restart Game**.

---

## Solução de Problemas

| Problema | Solução |
|----------|---------|
| O jogador cai através do chão | Verifique se `obj_ground` tem "Solid" marcado |
| O jogador não consegue saltar | Verifique se o evento Key Press → Up Arrow existe e se Set Vertical Speed é negativo |
| O jogador continua subindo após a aterrissagem | Certifique-se de que Collision with obj_ground tem uma ação Stop Movement |
| O salto parece flutuante | Aumente o valor Gravity de Set Gravity, ou torne o valor de salto de Set Vertical Speed mais negativo |
| O salto parece fraco demais | Diminua o valor Gravity de Set Gravity, ou torne o valor de salto de Set Vertical Speed mais negativo |

---

## O Que Você Aprendeu

Parabéns! Você criou um jogo de plataforma! Você aprendeu:

- **Física da gravidade** - Set Gravity aplica uma força constante para baixo a cada passo
- **Mecânicas de salto** - Um evento Key Press (não held) dá um único impulso de velocidade para cima
- **Colisão sólida integrada** - O chão bloqueia o jogador automaticamente assim que marcado Solid, sem código manual de verificação de posição
- **Perigos** - Criar objetos que reiniciam o nível
- **Design de níveis** - Construir desafios de plataforma

---

## Ideias de Desafio

1. **Salto na Parede** - Permitir saltar das paredes
2. **Movimento de Dash** - Um breve impulso horizontal de velocidade
3. **Plataformas que Desmoronam** - Plataformas que caem depois de pisadas
4. **Pontos de Verificação** - Salvar o progresso no meio do nível
5. **Batalha de Chefe** - Adicionar um inimigo final com vários golpes

---

## Veja Também

- [Tutoriais](Tutorials_pt) - Mais tutoriais de jogos
- [Preset Intermediário](Intermediate-Preset_pt) - Visão geral do preset de que a seção Melhorias precisa
- [Tutorial: Labirinto](Tutorial-Maze_pt) - Criar um jogo de navegação em labirinto
- [Tutorial: Breakout](Tutorial-Breakout_pt) - Criar um jogo de quebra-blocos
- [Referência de Eventos](Event-Reference_pt) - Documentação completa de eventos
