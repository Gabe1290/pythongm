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
**Preset:** Beginner Preset

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
| **Chão** | Terra caminhável (visual opcional) |

---

## Passo 2: Crie os Sprites

Todos os sprites devem ter o mesmo tamanho (32x32 pixels funcionam bem) para criar uma grade apropriada.

### 2.1 Sprite do Jogador

1. Na **Árvore de Recursos**, clique com botão direito em **Sprites** e selecione **Criar Sprite**
2. Nomeie-o como `spr_player`
3. Clique em **Editar Sprite** para abrir o editor de sprites
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
3. Use cores cinza ou escuro
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

1. Clique com botão direito em **Objetos** e selecione **Criar Objeto**
2. Nomeie-o como `obj_wall`
3. Defina o sprite como `spr_wall`
4. **Marque a caixa de seleção "Sólido"**
5. Nenhum evento necessário

---

## Passo 4: Crie o Objeto Destino

Os destinos marcam onde as caixas devem ser colocadas.

1. Crie um novo objeto nomeado `obj_target`
2. Defina o sprite como `spr_target`
3. Nenhum evento necessário - é apenas um marcador
4. Deixe "Sólido" desmarcado (jogador e caixas podem estar em cima dele)

---

## Passo 5: Crie o Objeto Caixa

A caixa é empurrada pelo jogador e muda de aparência quando em um destino.

1. Crie um novo objeto nomeado `obj_crate`
2. Defina o sprite como `spr_crate`
3. **Marque a caixa de seleção "Sólido"**

**Evento: Passo**
1. Adicione Evento → Passo → Passo
2. Adicione Ação: **Controle** → **Testar Variável**
   - Variável: `place_meeting(x, y, obj_target)`
   - Valor: `1`
   - Operação: Igual a
3. Adicione Ação: **Main1** → **Mudar Sprite**
   - Sprite: `spr_crate_ok`
   - Subimagem: `0`
   - Velocidade: `1`
4. Adicione Ação: **Controle** → **Senão**
5. Adicione Ação: **Main1** → **Mudar Sprite**
   - Sprite: `spr_crate`
   - Subimagem: `0`
   - Velocidade: `1`

Isto faz a caixa ficar verde quando está em um local de destino.

---

## Passo 6: Crie o Objeto Jogador

O jogador é o objeto mais complexo com movimento baseado em grade e mecânica de empurrar.

1. Crie um novo objeto nomeado `obj_player`
2. Defina o sprite como `spr_player`

### 6.1 Movimentar-se para a Direita

**Evento: Pressionar Seta Direita**
1. Adicione Evento → Teclado → Pressionar Direita

Primeiro, verifique se há uma parede no caminho:
2. Adicione Ação: **Controle** → **Testar Colisão**
   - Objeto: `obj_wall`
   - X: `32`
   - Y: `0`
   - Verificar: NÃO (significado "se NÃO há parede")

Se não houver parede, verifique se há uma caixa:
3. Adicione Ação: **Controle** → **Testar Colisão**
   - Objeto: `obj_crate`
   - X: `32`
   - Y: `0`

Se há uma caixa, precisamos verificar se podemos empurrá-la:
4. Adicione Ação: **Controle** → **Testar Colisão** (para o destino da caixa)
   - Objeto: `obj_wall`
   - X: `64`
   - Y: `0`
   - Verificar: NÃO

5. Adicione Ação: **Controle** → **Testar Colisão**
   - Objeto: `obj_crate`
   - X: `64`
   - Y: `0`
   - Verificar: NÃO

Se ambas as verificações passarem, empurre a caixa:
6. Adicione Ação: **Controle** → **Bloco de Código**
```
var crate = instance_place(x + 32, y, obj_crate);
if (crate != noone) {
    crate.x += 32;
}
```

Agora mova o jogador:
7. Adicione Ação: **Mover** → **Pular para Posição**
   - X: `32`
   - Y: `0`
   - Marque "Relativo"

### 6.2 Movimentar-se para a Esquerda

**Evento: Pressionar Seta Esquerda**
Siga o mesmo padrão que mover para a direita, mas use:
- Deslocamento X: `-32` para verificar parede/caixa
- Deslocamento X: `-64` para verificar se a caixa pode ser empurrada
- Mover caixa por `-32`
- Pular para posição X: `-32`

### 6.3 Movimentar-se para Cima

**Evento: Pressionar Seta para Cima**
Siga o mesmo padrão, mas use valores Y:
- Deslocamento Y: `-32` para verificar
- Deslocamento Y: `-64` para destino da caixa
- Mover caixa por Y: `-32`
- Pular para posição Y: `-32`

### 6.4 Movimentar-se para Baixo

**Evento: Pressionar Seta para Baixo**
Use:
- Deslocamento Y: `32` para verificar
- Deslocamento Y: `64` para destino da caixa
- Mover caixa por Y: `32`
- Pular para posição Y: `32`

---

## Passo 7: Movimento do Jogador Simplificado (Alternativa)

Se a abordagem baseada em blocos acima parecer complexa, aqui está uma abordagem mais simples baseada em código para cada direção:

**Evento: Pressionar Seta Direita**
Adicione Ação: **Controle** → **Executar Código**
```
// Verificar se podemos nos mover para a direita
if (!place_meeting(x + 32, y, obj_wall)) {
    // Verificar se há uma caixa
    var crate = instance_place(x + 32, y, obj_crate);
    if (crate != noone) {
        // Há uma caixa - podemos empurrá-la?
        if (!place_meeting(x + 64, y, obj_wall) && !place_meeting(x + 64, y, obj_crate)) {
            crate.x += 32;
            x += 32;
        }
    } else {
        // Sem caixa, apenas mova
        x += 32;
    }
}
```

Repita para outras direções com mudanças de coordenadas apropriadas.

---

## Passo 8: Crie o Verificador de Condição de Vitória

Precisamos de um objeto para verificar se todas as caixas estão em destinos.

1. Crie um novo objeto nomeado `obj_game_controller`
2. Nenhum sprite necessário

**Evento: Criar**
1. Adicione Evento → Criar
2. Adicione Ação: **Pontuação** → **Definir Variável**
   - Variável: `global.total_targets`
   - Valor: `0`
3. Adicione Ação: **Controle** → **Executar Código**
```
// Contar quantos destinos existem
global.total_targets = instance_number(obj_target);
```

**Evento: Passo**
1. Adicione Evento → Passo → Passo
2. Adicione Ação: **Controle** → **Executar Código**
```
// Contar caixas que estão em destinos
var crates_on_targets = 0;
with (obj_crate) {
    if (place_meeting(x, y, obj_target)) {
        crates_on_targets += 1;
    }
}

// Verificar se todos os destinos têm caixas
if (crates_on_targets >= global.total_targets && global.total_targets > 0) {
    // Nível completo!
    show_message("Nível Completo!");
    room_restart();
}
```

**Evento: Desenhar**
1. Adicione Evento → Desenhar
2. Adicione Ação: **Desenhar** → **Desenhar Texto**
   - Texto: `Sokoban - Empurre todas as caixas para os destinos!`
   - X: `10`
   - Y: `10`

---

## Passo 9: Projete Seu Nível

1. Clique com botão direito em **Salas** e selecione **Criar Sala**
2. Nomeie-a como `room_level1`
3. Defina o tamanho da sala como um múltiplo de 32 (por ex., 640x480)
4. Ative "Encaixar na Grade" e defina a grade como 32x32

### Colocando Objetos

Construa seu nível seguindo estas diretrizes:

1. **Cerque o nível com paredes** - Crie uma borda
2. **Adicione paredes internas** - Crie a estrutura do puzzle
3. **Coloque destinos** - Onde as caixas precisam ir
4. **Coloque caixas** - Mesmo número que destinos!
5. **Coloque o jogador** - Posição inicial
6. **Coloque o controlador de jogo** - Em qualquer lugar (é invisível)

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

1. Clique em **Executar** ou pressione **F5** para testar
2. Use as setas para se mover
3. Empurre as caixas para os destinos X vermelho
4. Quando todas as caixas estão nos destinos, você vence!

---

## Melhorias (Opcional)

### Adicionar um Contador de Movimentos

Em `obj_game_controller`:

**Evento: Criar** - Adicione:
```
global.moves = 0;
```

Em `obj_player`, após cada movimento bem-sucedido, adicione:
```
global.moves += 1;
```

Em `obj_game_controller` **Evento: Desenhar** - Adicione:
```
draw_text(10, 30, "Movimentos: " + string(global.moves));
```

### Adicionar Recurso de Desfazer

Armazene posições anteriores e permita pressionar Z para desfazer o último movimento.

### Adicionar Múltiplos Níveis

Crie mais salas (`room_level2`, `room_level3`, etc.) e use:
```
room_goto_next();
```
em vez de `room_restart()` ao completar um nível.

### Adicionar Efeitos Sonoros

Adicione sons para:
- Jogador se movendo
- Empurrando uma caixa
- Caixa caindo em destino
- Nível completo

---

## Solução de Problemas

| Problema | Solução |
|----------|---------|
| Jogador se move através de paredes | Verifique se `obj_wall` tem "Sólido" marcado |
| Caixa não muda de cor | Verifique se o evento Passo verifica `place_meeting` corretamente |
| Pode empurrar caixa através de parede | Verifique detecção de colisão antes de mover caixa |
| Mensagem de vitória aparece imediatamente | Certifique-se de que destinos foram colocados separadamente das caixas |
| Jogador se move múltiplos quadrados | Use evento Pressionar Teclado, não evento Teclado |

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

Lembre-se: Um bom puzzle Sokoban deve ser desafiador mas justo!

---

## Veja Também

- [Tutoriais](Tutorials_pt) - Mais tutoriais de jogos
- [Beginner Preset](Beginner-Preset_pt) - Visão geral dos recursos iniciantes
- [Tutorial: Pong](Tutorial-Pong_pt) - Criar um jogo para dois jogadores
- [Tutorial: Breakout](Tutorial-Breakout_pt) - Criar um jogo de quebrador de tijolos
- [Referência de Eventos](Event-Reference_pt) - Documentação completa de eventos
