# Tutorial: Criar um Jogo de Puzzle Sokoban

> **Selecione seu idioma / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Sokoban) | [Français](Tutorial-Sokoban_fr) | [Deutsch](Tutorial-Sokoban_de) | [Italiano](Tutorial-Sokoban_it) | [Español](Tutorial-Sokoban_es) | [Português](Tutorial-Sokoban_pt) | [Slovenščina](Tutorial-Sokoban_sl) | [Українська](Tutorial-Sokoban_uk) | [Русский](Tutorial-Sokoban_ru)

---

## Introdução

Neste tutorial, você criará um jogo de puzzle **Sokoban** - um clássico puzzle de empurrar caixas onde o jogador deve empurrar todas as caixas para os locais de destino. Sokoban (que significa "guardião do armazém" em japonês) é perfeito para aprender movimento baseado em grade e lógica de jogo de puzzle.

**O que você aprenderá:**
- Movimento baseado em grade (movimento em passos fixos)
- Mecânica de empurrar para mover objetos
- Detecção de colisão com múltiplos tipos de objetos
- Detecção de condição de vitória
- Design de nível para jogos de puzzle

**Dificuldade:** Iniciante
**Preset:** Preset Intermediário (a mecânica de empurrar e o movimento
baseado em grade usados aqui não estão no preset Iniciante)

---

## Passo 1: Entenda o Jogo

### Regras do Jogo
1. O jogador pode se mover para cima, baixo, esquerda ou direita
2. O jogador pode empurrar caixas (mas não puxá-las)
3. Apenas uma caixa pode ser empurrada por vez
4. As caixas não podem ser empurradas através de paredes ou outras caixas
5. O nível é concluído quando todas as caixas estão nos locais de destino

### O que Precisamos

| Elemento | Propósito |
|----------|-----------|
| **Jogador** | O guardião do armazém que você controla |
| **Caixa** | Caixas que o jogador empurra |
| **Parede** | Obstáculos sólidos que bloqueiam o movimento |
| **Destino** | Locais de objetivo onde as caixas devem ser colocadas |
| **Chão** | Terreno caminhável (visual opcional) |

---

## Passo 2: Crie os Sprites

Todos os sprites devem ter o mesmo tamanho (32x32 pixels funciona bem) para criar uma grade apropriada.

### 2.1 Sprite do Jogador

1. Na **Árvore de Recursos**, clique com o botão direito em **Sprites** e selecione **Create Sprite**
2. Nomeie-o como `spr_player`
3. Clique em **Edit Sprite** para abrir o editor de sprites
4. Desenhe um personagem simples (uma forma de pessoa ou robô)
5. Use uma cor distinta como azul ou verde
6. Tamanho: 32x32 pixels
7. Clique em **OK** para salvar

### 2.2 Sprite da Caixa

1. Crie um novo sprite nomeado `spr_crate`
2. Desenhe uma caixa de madeira ou forma de caixa
3. Use cores marrom ou laranja
4. Tamanho: 32x32 pixels

### 2.3 Sprite de Caixa no Destino

1. Crie um novo sprite nomeado `spr_crate_ok`
2. Desenhe a mesma caixa mas com uma cor diferente (verde) para mostrar que está corretamente colocada
3. Tamanho: 32x32 pixels

### 2.4 Sprite da Parede

1. Crie um novo sprite nomeado `spr_wall`
2. Desenhe um padrão sólido de tijolos ou pedra
3. Use cores cinza ou escuras
4. Tamanho: 32x32 pixels

### 2.5 Sprite do Destino

1. Crie um novo sprite nomeado `spr_target`
2. Desenhe uma marca X ou indicador de objetivo
3. Use uma cor brilhante como vermelho ou amarelo
4. Tamanho: 32x32 pixels

### 2.6 Sprite do Chão (Opcional)

1. Crie um novo sprite nomeado `spr_floor`
2. Desenhe um padrão simples de ladrilho de chão
3. Use uma cor neutra
4. Tamanho: 32x32 pixels

---

## Passo 3: Crie o Objeto Parede

A parede é o objeto mais simples - ela apenas bloqueia o movimento.

1. Clique com o botão direito em **Objects** e selecione **Create Object**
2. Nomeie-o como `obj_wall`
3. Defina o sprite como `spr_wall`
4. **Marque a caixa de seleção "Solid"**
5. Nenhum evento necessário

---

## Passo 4: Crie o Objeto Destino

Os destinos marcam onde as caixas devem ser colocadas.

1. Crie um novo objeto nomeado `obj_target`
2. Defina o sprite como `spr_target`
3. Nenhum evento necessário - é apenas um marcador
4. Deixe "Solid" desmarcado (jogador e caixas podem estar em cima dele)

---

## Passo 5: Crie o Objeto Caixa

A caixa é empurrada pelo jogador e muda de aparência quando está em um destino.

1. Crie um novo objeto nomeado `obj_crate`
2. Defina o sprite como `spr_crate`
3. **Marque a caixa de seleção "Solid"**

**Evento: Step**
1. Add Event → Step → Step
2. Add Action: **Control** → **If Collision**
   - X Offset: `0`
   - Y Offset: `0`
   - Against: `obj_target`
3. Add Action: **Instance** → **Set Sprite**
   - Sprite: `spr_crate_ok`
4. Add Action: **Control** → **Else**
5. Add Action: **Instance** → **Set Sprite**
   - Sprite: `spr_crate`

Isso faz a caixa ficar verde quando está em um local de destino —
**If Collision** com ambos os deslocamentos em `0` verifica se a
posição *atual* da caixa se sobrepõe a um `obj_target`.

---

## Passo 6: Crie o Objeto Jogador

O jogador se move exatamente uma célula da grade por vez e empurra as caixas em que esbarra.

1. Crie um novo objeto nomeado `obj_player`
2. Defina o sprite como `spr_player`

### 6.1 Movimento em Grade

Adicione um evento **Key Press** por direção, cada um com uma ação **Move** → **Move Grid**:

| Evento | Ação Move Grid |
|---|---|
| Key Press → Right Arrow | Direction: `right`, Grid Size: `32` |
| Key Press → Left Arrow | Direction: `left`, Grid Size: `32` |
| Key Press → Up Arrow | Direction: `up`, Grid Size: `32` |
| Key Press → Down Arrow | Direction: `down`, Grid Size: `32` |

**Move Grid** move a instância exatamente uma célula da grade e já
detecta colisões por conta própria — não moverá o jogador para dentro
de um `obj_wall` sólido, então não é necessária uma verificação de
parede adicional aqui.

### 6.2 Parar nas Paredes

**Evento: Collision with obj_wall**
1. Add Event → Collision → `obj_wall`
2. Add Action: **Move** → **Stop Movement**

### 6.3 Empurrar Caixas

**Evento: Collision with obj_crate**
1. Add Event → Collision → `obj_crate`
2. Add Action: **Control** → **If Can Push**
   - Direction: `facing`
   - Object Type: `obj_crate`
   - Then Action: `push_and_move`

**If Can Push** verifica se o espaço atrás da caixa (na direção em que
o jogador está se movendo) está livre e, se estiver, empurra a caixa
uma célula e move o jogador para o lugar dela, tudo em uma única ação.
Se o espaço atrás da caixa estiver bloqueado por uma parede ou outra
caixa, nada se move.

---

## Passo 7: Crie o Verificador de Condição de Vitória

Precisamos de um controlador invisível que observe se cada caixa está em um destino.

1. Crie um novo objeto nomeado `obj_game_controller`
2. Nenhum sprite necessário

**Evento: Create** — define a contagem de destinos uma única vez,
usando **Control** → **Execute Code** (a ação Execute Code deste
projeto executa Python real, não GameMaker Language — `self` é a
instância atual, `game` é o executor do jogo):

```python
# Conta quantos destinos existem na sala
self.total_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_target'
)
```

**Evento: Step** — verifica a cada quadro se todas as caixas estão em um destino:

```python
# Conta as caixas que atualmente se sobrepõem a um destino
crates_on_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_crate'
    and game.check_collision_at_position(inst, inst.x, inst.y, 'obj_target')
)

if self.total_targets > 0 and crates_on_targets >= self.total_targets:
    self.restart_room_flag = True
```

`self.restart_room_flag = True` é a forma como um bloco Execute Code
bruto aciona o mesmo reinício de sala que a ação **Restart Room**
realiza — o loop principal verifica isso a cada quadro. Adicione uma
ação **Show Message** (de **Output**, mensagem `Level Complete!`)
logo após o bloco Execute Code se quiser mostrar um popup antes do
reinício.

**Evento: Draw**
1. Add Event → Draw
2. Add Action: **Draw** → **Draw Text**
   - Text: `Sokoban - Push all crates to targets!`
   - X: `10`
   - Y: `10`

---

## Passo 9: Projete Seu Nível

1. Clique com o botão direito em **Rooms** e selecione **Create Room**
2. Nomeie-a como `room_level1`
3. Defina o tamanho da sala como um múltiplo de 32 (por ex., 640x480)
4. Ative "Snap to Grid" e defina a grade como 32x32

### Colocando Objetos

Construa seu nível seguindo estas diretrizes:

1. **Cerque o nível com paredes** - Crie uma borda
2. **Adicione paredes internas** - Crie a estrutura do puzzle
3. **Coloque destinos** - Onde as caixas precisam ir
4. **Coloque caixas** - Mesmo número que destinos!
5. **Coloque o jogador** - Posição inicial
6. **Coloque o game controller** - Em qualquer lugar (é invisível)

### Exemplo de Layout de Nível

```
W W W W W W W W W W
W . . . . . . . . W
W . P . . . C . . W
W . . W W . . . . W
W . . W T . . C . W
W . . . . . W W . W
W . T . . . . . . W
W . . . . . . . . W
W W W W W W W W W W

W = Parede
P = Jogador
C = Caixa
T = Destino
. = Chão vazio
```

**Importante:** Sempre tenha o mesmo número de caixas e destinos!

---

## Passo 10: Teste Seu Jogo!

1. Clique em **Run** ou pressione **F5** para testar
2. Use as setas para se mover
3. Empurre as caixas para os destinos X vermelhos
4. Quando todas as caixas estiverem nos destinos, você vence!

---

## Melhorias (Opcional)

### Adicionar um Contador de Movimentos

No evento **Create** de `obj_game_controller`, adicione **Control** →
**Set Variable** (Variable: `global.moves`, Value: `0`, Scope: `global`).

Em cada um dos quatro eventos Key Press de `obj_player`, adicione uma
segunda ação logo após Move Grid: **Control** → **Set Variable**
(Variable: `global.moves`, Value: `1`, Scope: `global`, **Relative**
marcado) — isso soma 1 ao contador a cada pressionamento de tecla,
independentemente de o movimento ter sido realmente bloqueado por uma
parede.

No evento **Draw** de `obj_game_controller`, adicione **Draw** →
**Draw Variable** (Variable: `global.moves`, X: `10`, Y: `30`).

### Adicionar Recurso de Desfazer

Armazene posições anteriores e permita pressionar Z para desfazer o último movimento.

### Adicionar Múltiplos Níveis

Crie mais salas (`room_level2`, `room_level3`, etc.) e use a ação
**Next Room** (categoria Room) em vez de **Restart Room** no bloco
Execute Code de verificação de vitória (`self.next_room_flag = True`
em vez de `self.restart_room_flag = True`) ao completar um nível.

### Adicionar Efeitos Sonoros

Adicione sons para:
- Jogador se movendo
- Empurrando uma caixa
- Caixa caindo em um destino
- Nível completo

---

## Solução de Problemas

| Problema | Solução |
|----------|---------|
| Jogador se move através de paredes | Verifique se `obj_wall` tem "Solid" marcado |
| Caixa não muda de cor | Verifique se a ação **If Collision** do evento Step aponta para `obj_target` |
| Pode empurrar caixa através de parede | Verifique a detecção de colisão antes de mover a caixa |
| Mensagem de vitória aparece imediatamente | Certifique-se de que os destinos foram colocados separadamente das caixas |
| Jogador se move vários quadrados | Use o evento Keyboard Press, não o evento Keyboard |

---

## O que Você Aprendeu

Parabéns! Você criou um jogo de puzzle Sokoban completo! Você aprendeu:

- **Movimento baseado em grade** - Movimento em passos fixos de 32 pixels
- **Mecânica de empurrar** - Detectar e mover objetos que o jogador empurra
- **Lógica de colisão complexa** - Verificar múltiplas condições antes de permitir movimento
- **Mudanças de estado** - Mudar sprite baseado na posição do objeto
- **Condições de vitória** - Verificar quando todos os objetivos são completados
- **Design de nível** - Criar layouts de puzzle solucionáveis

---

## Desafio: Projete Seus Próprios Níveis!

A diversão real do Sokoban é projetar puzzles. Tente criar níveis que:
- Comecem fáceis e fiquem progressivamente mais difíceis
- Exijam planejamento antecipado
- Tenham apenas uma solução
- Usem espaço mínimo eficientemente

Lembre-se: um bom puzzle Sokoban deve ser desafiador mas justo!

---

## Veja Também

- [Tutoriais](Tutorials_pt) - Mais tutoriais de jogos
- [Intermediate Preset](Intermediate-Preset_pt) - Visão geral do preset necessário para este tutorial
- [Tutorial: Pong](Tutorial-Pong_pt) - Criar um jogo para dois jogadores
- [Tutorial: Breakout](Tutorial-Breakout_pt) - Criar um jogo de quebrador de tijolos
- [Referência de Eventos](Event-Reference_pt) - Documentação completa de eventos
