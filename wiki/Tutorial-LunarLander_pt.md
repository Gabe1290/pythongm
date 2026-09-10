# Tutorial: Criar um Jogo de Pouso Lunar

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Introdução

Neste tutorial, você vai criar um **Jogo de Pouso Lunar** - um jogo de arcade clássico onde você controla uma nave espacial descendo até uma plataforma de pouso. Você precisa gerir seu empuxo para contrariar a gravidade e pousar suavemente sem se espatifar. Este jogo é perfeito para aprender conceitos de física como gravidade, empuxo, velocidade e gestão de combustível.

**O que você vai aprender:**
- Física de gravidade e empuxo
- Detecção de pouso baseada na velocidade
- Sistema de gestão de combustível
- Controlo de rotação ou direcional
- Zonas de pouso seguras

**Dificuldade:** Iniciante
**Preset:** Preset Intermediário (a física de empuxo/combustível apoia-se em Execute Code o tempo todo, que não está no preset Iniciante)

---

## Passo 1: Entender o Jogo

### Mecânicas do Jogo
1. O módulo é puxado para baixo pela gravidade
2. Pressionar CIMA aplica empuxo para cima (usa combustível)
3. ESQUERDA/DIREITA controlam a rotação ou o movimento do módulo
4. Pouse suavemente na plataforma para vencer
5. Espatifa-se se pousar rápido demais ou errar a plataforma
6. Se ficar sem combustível, não consegue mais frear!

### O Que Precisamos

| Elemento | Finalidade |
|----------|------------|
| **Módulo** | A nave espacial que você controla |
| **Plataforma de Pouso** | Zona segura para pousar |
| **Solo** | Terreno que causa um acidente |
| **Indicador de Combustível** | Mostra o combustível restante |
| **Indicador de Velocidade** | Mostra a velocidade atual |

---

## Passo 2: Criar os Sprites

### 2.1 Sprite do Módulo

1. Na **Árvore de Recursos**, clique com o botão direito em **Sprites** e selecione **Create Sprite**
2. Nomeie-o `spr_lander`
3. Clique em **Edit Sprite** para abrir o editor de sprites
4. Desenhe uma nave espacial simples (triângulo ou forma de módulo clássica)
5. Tamanho: 32x32 pixels
6. **Importante:** defina a origem como centro-baixo para um pouso correto

### 2.2 Sprite da Plataforma de Pouso

1. Crie um novo sprite chamado `spr_pad`
2. Desenhe uma plataforma plana com marcações (como um "H")
3. Use cores vivas (amarelo/verde)
4. Tamanho: 64x16 pixels

### 2.3 Sprite do Solo

1. Crie um novo sprite chamado `spr_ground`
2. Desenhe um terreno rochoso/acidentado
3. Use cores cinza/marrom
4. Tamanho: 32x32 pixels

### 2.4 Sprite da Chama (Opcional)

1. Crie um novo sprite chamado `spr_flame`
2. Desenhe uma pequena chama/jato de escape
3. Use cores laranja/amarelo
4. Tamanho: 16x16 pixels

![The Sprite Editor with spr_lander open, Origin set to Center-Bottom (X 16, Y 32); spr_lander, spr_pad, spr_ground and spr_flame in the resource tree](images/tutorial-lunarlander-02-sprites.png)

---

## Passo 3: Criar o Objeto Solo

O solo é um terreno perigoso que causa um acidente.

1. Clique com o botão direito em **Objects** e selecione **Create Object**
2. Nomeie-o `obj_ground`
3. Defina o sprite como `spr_ground`
4. **Marque a caixa "Solid"**
5. Nenhum evento necessário

![obj_ground's Object Events panel: empty -- Solid checked is all it needs](images/tutorial-lunarlander-03-ground-object.png)

---

## Passo 4: Criar o Objeto Plataforma de Pouso

A plataforma de pouso é onde o jogador deve pousar em segurança.

1. Crie um novo objeto chamado `obj_pad`
2. Defina o sprite como `spr_pad`
3. **Marque a caixa "Solid"**
4. Nenhum evento necessário (a colisão é tratada pelo módulo)

![obj_pad's Object Events panel: empty, with Solid checked](images/tutorial-lunarlander-04-pad-object.png)

---

## Passo 5: Criar o Objeto Módulo

O módulo é o principal objeto controlado pelo jogador, com física. Ao
contrário dos outros tutoriais de movimento deste wiki, seus controles
precisam acumular velocidade gradualmente e acompanhar um recurso de
combustível, então este objeto apoia-se mais em **Control** → **Execute
Code** (Python real — `self` é a instância atual, `game` é o game runner,
`keyboard.check(nome)` informa uma tecla mantida pressionada) do que
apenas em ações estruturadas. Onde uma ação estruturada resolve, este
tutorial ainda usa uma.

1. Crie um novo objeto chamado `obj_lander`
2. Defina o sprite como `spr_lander`

### 5.1 Gravidade e Variáveis Iniciais

**Evento: Create**
1. Adicione a ação **Move** → **Set Gravity** (Direction: `270`, Gravity: `0.05`)
   — uma puxada suave para baixo; o motor a adiciona automaticamente à
   velocidade vertical do módulo a cada passo, igual à gravidade do
   tutorial de Plataforma, só que mais fraca.
2. Adicione a ação **Control** → **Execute Code**:

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

O sistema de movimento deste projeto já acompanha a velocidade via
`self.hspeed`/`self.vspeed` e move a instância nessa quantidade a cada
frame (com a colisão sólida integrada) — não é preciso criar variáveis
`hsp`/`vsp` separadas como faria uma simulação física crua.

### 5.2 Evento Step — Empuxo e Controles

**Evento: Step** — Adicione a ação **Control** → **Execute Code**:

```python
if not self.landed and not self.crashed:
    if keyboard.check('up') and self.fuel > 0:
        self.vspeed -= self.thrust_force
        self.fuel -= self.fuel_use
        if self.fuel < 0:
            self.fuel = 0

    if keyboard.check('left'):
        self.hspeed -= 0.05
    if keyboard.check('right'):
        self.hspeed += 0.05

    # Limita a velocidade máxima
    self.hspeed = max(-self.max_speed, min(self.max_speed, self.hspeed))
    self.vspeed = max(-self.max_speed, min(self.max_speed, self.vspeed))

    # Impede o módulo de sair pelas laterais ou acima da room
    room = game.current_room
    if self.x < 16:
        self.x = 16
        self.hspeed = 0
    if self.x > room.width - 16:
        self.x = room.width - 16
        self.hspeed = 0
    if self.y < 16:
        self.y = 16
        self.vspeed = 0
```

O bloco inteiro está envolto em `if not self.landed and not self.crashed:`
para que empuxo e direção parem no instante em que a partida termina — o
objeto `self` não tem como abandonar um evento no meio (não há `exit` no
estilo GML), então um `if` em torno do resto do código é o equivalente.

### 5.3 Colisão com a Plataforma de Pouso

**Evento: Collision with obj_pad**
1. Adicione a ação **Control** → **Test Expression**
   - Expression: `(self.hspeed**2 + self.vspeed**2)**0.5 <= self.safe_speed`
     — a velocidade de pouso é o comprimento do vetor velocidade;
     Pitágoras, não uma variável `speed` (neste motor, `speed` é a
     *velocidade de animação do sprite*, não a magnitude do movimento —
     uma armadilha real para quem vem do GameMaker).
   - Then Actions:
     1. **Control** → **Set Variable** (Variable: `landed`, Value: `true`, Scope: `self`)
     2. **Move** → **Stop Movement**
     3. **Move** → **Set Gravity** (Direction: `270`, Gravity: `0`) — impede
        a gravidade de voltar a acumular silenciosamente velocidade
        vertical num módulo que já pousou
     4. **Output** → **Show Message** (Message: `Perfect Landing! You Win!`)
   - Else Actions:
     1. **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
     2. **Output** → **Show Message** (Message: `Crashed! Too fast!`)
     3. **Room** → **Restart Room**

O texto de Show Message é uma string fixa — ele não pode embutir a
velocidade real de pouso. O HUD (Passo 7) já exibe a velocidade ao vivo
até o momento do contato, então o jogador já viu o número.

### 5.4 Colisão com o Solo

**Evento: Collision with obj_ground**
1. Adicione a ação **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
2. Adicione a ação **Output** → **Show Message** (Message: `Crashed into terrain!`)
3. Adicione a ação **Room** → **Restart Room**

![obj_lander's Object Events panel: Create (Set Gravity + Execute Code), Step (Execute Code), Collision with obj_pad (the Test Expression landing check), Collision with obj_ground (Set Variable + Show Message + Restart Room)](images/tutorial-lunarlander-05-lander-object.png)

---

## Passo 6: Criar o Objeto Chama (Opcional)

Retorno visual ao aplicar empuxo.

1. Crie um novo objeto chamado `obj_flame`
2. Defina o sprite como `spr_flame`

Ele será criado pelo módulo ao aplicar empuxo (recurso avançado). Para uma
abordagem mais simples, você pode desenhar a chama no evento Draw do
módulo.

![obj_flame's Object Events panel: empty -- it just needs the spr_flame sprite](images/tutorial-lunarlander-06-flame-object.png)

---

## Passo 7: Criar o Controlador de Jogo

O controlador de jogo exibe combustível, velocidade e instruções lendo-os
da instância do módulo a cada frame.

1. Crie um novo objeto chamado `obj_game_controller`
2. Nenhum sprite necessário

**Evento: Draw**
1. Adicione a ação **Control** → **Execute Code** — encontra o módulo e
   calcula os valores que as ações Draw abaixo vão exibir:

```python
lander = None
for inst in game.current_room.instances:
    if inst.object_name == 'obj_lander':
        lander = inst
        break

if lander is not None:
    self.fuel_display = round(lander.fuel)
    self.speed_display = round((lander.hspeed ** 2 + lander.vspeed ** 2) ** 0.5, 2)
    self.too_fast = self.speed_display > lander.safe_speed
    self.no_fuel = lander.fuel <= 0
else:
    self.fuel_display = 0
    self.speed_display = 0.0
    self.too_fast = False
    self.no_fuel = False
```

2. Adicione a ação **Game** → **Set Draw Color** (Color: `#FFFFFF`)
3. Adicione a ação **Game** → **Draw Text** (Text: `LUNAR LANDER`, X: `10`, Y: `10`)
4. Adicione a ação **Game** → **Draw Text** (Text: `Fuel:`, X: `10`, Y: `30`)
5. Adicione a ação **Game** → **Draw Variable** (Variable: `self.fuel_display`, X: `70`, Y: `30`)
6. Adicione a ação **Game** → **Draw Text** (Text: `Speed:`, X: `10`, Y: `50`)
7. Adicione a ação **Game** → **Draw Variable** (Variable: `self.speed_display`, X: `70`, Y: `50`)
8. Adicione a ação **Game** → **Draw Text** (Text: `Safe Speed: < 2`, X: `10`, Y: `70`)

Depois as duas linhas de aviso, cada uma condicionada por **Control** →
**Test Expression** (nenhum Else necessário — nada é desenhado quando a
condição é falsa):

9. **Control** → **Test Expression** (Expression: `self.too_fast`)
   - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
     **Draw Text** (`TOO FAST!`, X `10`, Y `90`)
   - Else Actions: **Game** → **Set Draw Color** (`#00FF00`), **Game** →
     **Draw Text** (`Speed OK`, X `10`, Y `90`)
10. **Control** → **Test Expression** (Expression: `self.no_fuel`)
    - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
      **Draw Text** (`NO FUEL!`, X `10`, Y `110`)

11. Adicione a ação **Game** → **Set Draw Color** (Color: `#808080`)
12. Adicione a ação **Game** → **Draw Text** (Text: `UP: Thrust | LEFT/RIGHT: Move`,
    X: `10`, Y: `440`) — escolha um Y perto da parte inferior do tamanho
    de room que você usar no Passo 8.

![obj_game_controller's Object Events panel: a Draw event with 12 actions -- the Execute Code HUD-value calculation, then the Set Draw Color / Draw Text / Draw Variable chain and the two Test Expression warning blocks -- with no sprite set](images/tutorial-lunarlander-07-controller-object.png)

---

## Passo 8: Projetar o Seu Nível

1. Clique com o botão direito em **Rooms** e selecione **Create Room**
2. Nomeie-a `room_game`
3. Defina o tamanho da room (ex.: 640x480)
4. Defina a cor de fundo como preto (o espaço)

### Colocando os Objetos

Construa o seu nível seguindo estas orientações:

1. **Solo** - Coloque `obj_ground` ao longo da parte inferior para criar o terreno
2. **Plataforma de pouso** - Coloque `obj_pad` numa lacuna do terreno
3. **Módulo** - Coloque `obj_lander` no topo da room
4. **Controlador de jogo** - Coloque `obj_game_controller` em qualquer lugar

### Exemplo de Layout de Nível

```
    L                          <- O módulo começa aqui




GGG    GGG    PPPP    GGG    GGG
GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG

G = Solo    L = Módulo    P = Plataforma de pouso
```

![The Room Editor for room_game: a solid terrain row along the bottom with rocky chunks above it, a yellow landing pad in a clear gap, the white lander near the top-left, and the obj_game_controller marker near the top-right, all on a black space background](images/tutorial-lunarlander-08-room.png)

---

## Passo 9: Teste o Seu Jogo!

1. Clique em **Executar** ou pressione **F5** para testar
2. Use a seta **CIMA** para o empuxo (fique de olho no combustível!)
3. Use as setas **ESQUERDA/DIREITA** para dirigir
4. Pouse suavemente na plataforma (a velocidade deve ser inferior a 2)
5. Evite o terreno rochoso!

---

## Melhorias (Opcional)

### Adicionar Controlo de Rotação

Em vez do movimento esquerda/direita, gire o módulo e aplique empuxo na
direção para a qual ele aponta. As instâncias deste motor têm um atributo
`rotation` real (graus, 0 = direita, crescente no sentido anti-horário)
usado para girar o sprite — não é preciso
`image_angle`/`lengthdir_x`/`lengthdir_y`, já que `math` já está
disponível em Execute Code:

Substitua o código do evento Create do 5.1 por:
```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
self.rotation = 90  # apontando para cima
self.rotation_speed = 3
```

Substitua as linhas de direção do 5.2 (o bloco `left`/`right` → `hspeed`)
por:
```python
if keyboard.check('left'):
    self.rotation -= self.rotation_speed
if keyboard.check('right'):
    self.rotation += self.rotation_speed
```

E substitua as linhas de empuxo por:
```python
if keyboard.check('up') and self.fuel > 0:
    rad = math.radians(self.rotation)
    self.hspeed += self.thrust_force * math.cos(rad)
    self.vspeed -= self.thrust_force * math.sin(rad)
    self.fuel -= self.fuel_use
    if self.fuel < 0:
        self.fuel = 0
```

(o `-=` em `vspeed` corresponde ao código de gravidade do próprio motor —
o eixo Y da tela aumenta para baixo, então "cima" é velocidade vertical
negativa).

### Adicionar Várias Plataformas de Pouso

Crie plataformas de tamanhos diferentes com valores de pontos diferentes:
- Plataforma pequena = 100 pontos (mais difícil)
- Plataforma grande = 50 pontos (mais fácil)

### Adicionar Recargas de Combustível

1. Crie `obj_fuel` que flutua no ar
2. Ao colidir com o módulo, adicione combustível e destrua

### Adicionar Níveis

Crie várias rooms com terreno cada vez mais difícil e plataformas de pouso
menores.

### Adicionar Vento

Adicione um pequeno empurrão horizontal constante. No código do evento
Create de `obj_lander`, adicione `self.wind_force = 0.02`; depois, no
início do bloco `if not self.landed and not self.crashed:` do evento Step,
adicione:
```python
self.hspeed += self.wind_force
```

---

## Solução de Problemas

| Problema | Solução |
|----------|---------|
| O módulo cai rápido demais | Diminua o valor `Gravity` de Set Gravity, ou aumente `thrust_force` no código do evento Create |
| Não consigo frear o suficiente | Aumente `thrust_force`, ou aumente `safe_speed` |
| O combustível acaba rápido demais | Diminua `fuel_use`, ou aumente o `fuel` inicial |
| O módulo sai da tela | Verifique o bloco de limites no fim do código do evento Step |
| O pouso não é registrado | Certifique-se de que `obj_pad` tem "Solid" marcado |

---

## O Que Você Aprendeu

Parabéns! Você criou um jogo de pouso lunar! Você aprendeu:

- **Física de empuxo** - Ajustar `self.vspeed` contra uma puxada contínua de Set Gravity
- **Gestão de velocidade** - Calcular a velocidade a partir de `hspeed`/`vspeed` com o teorema de Pitágoras
- **Sistema de combustível** - Jogabilidade de gestão de recursos com uma simples variável de instância
- **Detecção de colisão** - Resultados diferentes para plataforma vs solo, escolhidos com Test Expression
- **Exibição de HUD** - Calcular os valores a exibir em Execute Code e depois mostrá-los com Draw Text/Draw Variable

---

## Ideias de Desafio

1. **Rotação Realista** - Girar e aplicar empuxo na direção para a qual se aponta
2. **Vários Níveis** - Terreno cada vez mais difícil
3. **Sistema de Pontuação** - Pontos com base no combustível restante e na precisão do pouso
4. **Asteroides** - Adicionar perigos móveis a evitar
5. **Modo de Dois Jogadores** - Corrida para pousar primeiro

---

## Veja Também

- [Tutoriais](Tutorials_pt) - Mais tutoriais de jogos
- [Preset Intermediário](Intermediate-Preset_pt) - Visão geral do preset de que este tutorial precisa
- [Tutorial: Plataforma](Tutorial-Platformer_pt) - Criar um jogo de saltos de plataforma
- [Tutorial: Labirinto](Tutorial-Maze_pt) - Criar um jogo de navegação em labirinto
- [Referência de Eventos](Event-Reference_pt) - Documentação completa de eventos
