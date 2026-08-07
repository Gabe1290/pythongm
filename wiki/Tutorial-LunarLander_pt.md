# Tutorial: Criar um Jogo de Pouso Lunar

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Introdução

Neste tutorial, você criará um **Jogo de Pouso Lunar** - um jogo arcade clássico onde você controla uma espaçonave descendo em uma plataforma de pouso. Você deve gerenciar seu impulso para contrapor a gravidade e pousar suavemente sem bater. Este jogo é perfeito para aprender conceitos físicos como gravidade, impulso, velocidade e gerenciamento de combustível.

**O que você aprenderá:**
- Física de gravidade e impulso
- Detecção de pouso baseada em velocidade
- Sistema de gerenciamento de combustível
- Controle de rotação ou direcional
- Zonas de pouso seguro

**Dificuldade:** Iniciante
**Preset:** Preset Intermediário (a física de impulso/combustível
depende inteiramente de Execute Code, que não está no preset Iniciante)

---

## Passo 1: Entender o Jogo

### Mecânicas do Jogo
1. O módulo é puxado para baixo pela gravidade
2. Pressionar CIMA aplica impulso para cima (usa combustível)
3. ESQUERDA/DIREITA controla rotação ou movimento
4. Pouse suavemente na plataforma para vencer
5. Você bate se pousar muito rápido ou errar a plataforma
6. Sem combustível você não pode desacelerar!

### O Que Precisamos

| Elemento | Propósito |
|----------|-----------|
| **Módulo** | A nave que você controla |
| **Plataforma** | Zona segura para pousar |
| **Solo** | Terreno que causa a batida |
| **Display Combustível** | Mostra o combustível restante |
| **Display Velocidade** | Mostra a velocidade atual |

---

## Passo 2: Criar os Sprites

### Sprites
- `spr_lander` (32x32 pixels) - nave espacial simples
- `spr_pad` (64x16 pixels) - plataforma de pouso
- `spr_ground` (32x32 pixels) - terreno rochoso
- `spr_flame` (16x16 pixels) - chama de propulsão (opcional)

---

## Passo 3-4: Criar Objetos de Solo e Plataforma

**obj_ground** e **obj_pad**: Defina o sprite, marque "Solid"

---

## Passo 5: Criar o Objeto Módulo

O módulo é o objeto principal controlado pelo jogador. Diferente dos
outros tutoriais de movimento deste wiki, seus controles precisam
acumular velocidade gradualmente e rastrear um recurso de combustível,
então este objeto depende mais de **Control** → **Execute Code**
(Python real — `self` é a instância atual, `game` é o executor do
jogo, `keyboard.check(name)` indica se uma tecla está pressionada) do
que os tutoriais de movimento anteriores, mas ainda usa uma ação
estruturada onde for possível.

### 5.1 Gravidade e Variáveis Iniciais

**Evento: Create**
1. Ação: **Move** → **Set Gravity** (Direction: `270`, Gravity: `0.05`)
   — uma leve puxada para baixo; o motor a soma automaticamente à
   velocidade vertical do módulo a cada quadro, como no tutorial de
   Plataforma, só que mais fraca.
2. Ação: **Control** → **Execute Code**:

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

O sistema de movimento deste motor já rastreia a velocidade através de
`self.hspeed`/`self.vspeed` e move a instância por essa quantidade a
cada quadro (com colisão sólida integrada) — não é necessário criar
variáveis separadas `hsp`/`vsp` como faria uma simulação física manual.

### 5.2 Evento Step — Impulso e Controles

**Evento: Step** — Ação: **Control** → **Execute Code**:

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

    # Impede que o módulo saia pelas laterais ou pelo topo da sala
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

O bloco inteiro está dentro de `if not self.landed and not
self.crashed:` para que o impulso e o controle parem no instante em
que o jogo termina — o objeto não tem uma forma de interromper um
evento no meio (nenhum `exit` como em GML); um `if` em torno do
restante do código cumpre a mesma função.

### 5.3 Colisão com a Plataforma

**Evento: Collision with obj_pad**
1. Ação: **Control** → **Test Expression**
   - Expression: `(self.hspeed**2 + self.vspeed**2)**0.5 <=
     self.safe_speed` — a velocidade de pouso é o comprimento do vetor
     velocidade (teorema de Pitágoras), não uma variável `speed` (neste
     motor `speed` é a *velocidade de animação* do sprite, não a
     magnitude do movimento — uma armadilha real para quem vem do
     GameMaker).
   - Then Actions:
     1. **Control** → **Set Variable** (Variable: `landed`, Value: `true`, Scope: `self`)
     2. **Move** → **Stop Movement**
     3. **Move** → **Set Gravity** (Direction: `270`, Gravity: `0`) —
        impede que a gravidade volte a acumular velocidade vertical
        silenciosamente em um módulo que já pousou
     4. **Output** → **Show Message** (Message: `Pouso Perfeito! Você Venceu!`)
   - Else Actions:
     1. **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
     2. **Output** → **Show Message** (Message: `Batida! Muito rápido!`)
     3. **Room** → **Restart Room**

O texto de Show Message é uma string fixa — não pode mostrar a
velocidade real de pouso. O HUD (Passo 7) já mostra a velocidade em
tempo real até o momento do toque, então o jogador já viu o número.

### 5.4 Colisão com o Solo

**Evento: Collision with obj_ground**
1. Ação: **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
2. Ação: **Output** → **Show Message** (Message: `Batida no terreno!`)
3. Ação: **Room** → **Restart Room**

---

## Passo 6-7: Game Controller

**obj_game_controller** — Evento Draw: encontra o módulo através de um
loop sobre `game.current_room.instances` (o mesmo padrão do contador
de moedas do tutorial do Labirinto), calcula combustível/velocidade
arredondados em um **Execute Code**, e então os mostra com **Draw
Text**/**Draw Variable**; veja a [versão em inglês](Tutorial-LunarLander)
para os detalhes completos ação por ação.

---

## Passo 8: Projete Seu Nível

1. Crie `room_game` (640x480)
2. Fundo preto (espaço)
3. Coloque o solo embaixo com uma abertura
4. Coloque a plataforma na abertura
5. Coloque o módulo no topo
6. Coloque o game controller

---

## O Que Você Aprendeu

- **Física de impulso** - Ajustar `self.vspeed` contra uma puxada contínua de Set Gravity
- **Gerenciamento de velocidade** - Calcular a velocidade a partir de `hspeed`/`vspeed` com o teorema de Pitágoras
- **Sistema de combustível** - Gerenciamento de recursos com uma variável de instância simples
- **Detecção de colisões** - Resultados diferentes para plataforma e solo, escolhidos com Test Expression

---

## Veja Também

- [Tutoriais](Tutorials_pt) - Mais tutoriais
- [Tutorial: Platformer](Tutorial-Platformer_pt) - Criar um jogo de plataforma
