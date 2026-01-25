# Tutorial: Criar um Jogo Clássico de Pong

> **Selecione seu idioma / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Pong) | [Français](Tutorial-Pong_fr) | [Deutsch](Tutorial-Pong_de) | [Italiano](Tutorial-Pong_it) | [Español](Tutorial-Pong_es) | [Português](Tutorial-Pong_pt) | [Slovenščina](Tutorial-Pong_sl) | [Українська](Tutorial-Pong_uk) | [Русский](Tutorial-Pong_ru)

---

## Introdução

Neste tutorial, você criará um clássico jogo de **Pong** - um dos primeiros videogames já criados! Pong é um jogo de dois jogadores onde cada jogador controla uma raquete e tenta acertar a bola passando pela raquete do adversário para marcar pontos.

**O que você aprenderá:**
- Criar sprites para raquetes, bola e paredes
- Lidar com entrada de teclado para dois jogadores
- Fazer objetos colidirem e ricochetearem
- Rastrear e exibir pontuações de ambos os jogadores
- Usar variáveis globais

**Dificuldade:** Iniciante
**Preset:** Preset para Iniciantes

---

## Etapa 1: Planeje Seu Jogo

Antes de começarmos, vamos entender o que precisamos:

| Elemento | Propósito |
|---------|---------|
| **Bola** | Ricocheteio entre os jogadores |
| **Raquete Esquerda** | Jogador 1 controla com as teclas W/S |
| **Raquete Direita** | Jogador 2 controla com as setas para Cima/Baixo |
| **Paredes** | Limites superior e inferior |
| **Gols** | Áreas invisíveis atrás de cada raquete para detectar pontuação |
| **Exibição de Pontuação** | Mostra as pontuações de ambos os jogadores |

---

## Etapa 2: Criar os Sprites

### 2.1 Sprite da Bola

1. Na **Árvore de Recursos**, clique com o botão direito em **Sprites** e selecione **Criar Sprite**
2. Nomeie como `spr_ball`
3. Clique em **Editar Sprite** para abrir o editor de sprites
4. Desenhe um pequeno círculo branco (aproximadamente 16x16 pixels)
5. Clique em **OK** para salvar

### 2.2 Sprites das Raquetes

Criaremos duas raquetes - uma para cada jogador:

**Raquete Esquerda (Jogador 1):**
1. Crie um novo sprite nomeado `spr_paddle_left`
2. Desenhe um retângulo alto e fino curvado como um parêntese ")" - cor azul recomendada
3. Tamanho: aproximadamente 16x64 pixels

**Raquete Direita (Jogador 2):**
1. Crie um novo sprite nomeado `spr_paddle_right`
2. Desenhe um retângulo alto e fino curvado como um parêntese "(" - cor vermelha recomendada
3. Tamanho: aproximadamente 16x64 pixels

### 2.3 Sprite da Parede

1. Crie um novo sprite nomeado `spr_wall`
2. Desenhe um retângulo sólido (cinza ou branco)
3. Tamanho: 32x32 pixels (esticaremos na sala)

### 2.4 Sprite do Gol (Invisível)

1. Crie um novo sprite nomeado `spr_goal`
2. Faça com 32x32 pixels
3. Deixe-o transparente ou faça uma cor sólida (ficará invisível no jogo)

---

## Etapa 3: Criar o Objeto Parede

O objeto parede cria limites na parte superior e inferior da área de jogo.

1. Clique com o botão direito em **Objetos** e selecione **Criar Objeto**
2. Nomeie como `obj_wall`
3. Defina o sprite para `spr_wall`
4. **Marque a caixa "Sólido"** - isto é importante para o ricocheteio!
5. Nenhum evento necessário - a parede apenas fica ali

---

## Etapa 4: Criar os Objetos de Raquete

### 4.1 Raquete Esquerda (Jogador 1)

1. Crie um novo objeto nomeado `obj_paddle_left`
2. Defina o sprite para `spr_paddle_left`
3. **Marque a caixa "Sólido"**

**Adicione Eventos de Teclado para Movimento:**

**Evento: Pressão da Tecla W**
1. Adicionar Evento → Teclado → Pressionar W
2. Adicionar Ação: **Mover** → **Definir Velocidade Vertical**
3. Defina a velocidade vertical para `-8` (move para cima)

**Evento: Soltura da Tecla W**
1. Adicionar Evento → Teclado → Soltar W
2. Adicionar Ação: **Mover** → **Definir Velocidade Vertical**
3. Defina a velocidade vertical para `0` (para de se mover)

**Evento: Pressão da Tecla S**
1. Adicionar Evento → Teclado → Pressionar S
2. Adicionar Ação: **Mover** → **Definir Velocidade Vertical**
3. Defina a velocidade vertical para `8` (move para baixo)

**Evento: Soltura da Tecla S**
1. Adicionar Evento → Teclado → Soltar S
2. Adicionar Ação: **Mover** → **Definir Velocidade Vertical**
3. Defina a velocidade vertical para `0` (para de se mover)

**Evento: Colisão com obj_wall**
1. Adicionar Evento → Colisão → obj_wall
2. Adicionar Ação: **Mover** → **Ricocheteio Contra Objetos**
3. Selecione "Contra objetos sólidos"

### 4.2 Raquete Direita (Jogador 2)

1. Crie um novo objeto nomeado `obj_paddle_right`
2. Defina o sprite para `spr_paddle_right`
3. **Marque a caixa "Sólido"**

**Adicione Eventos de Teclado para Movimento:**

**Evento: Pressão da Seta para Cima**
1. Adicionar Evento → Teclado → Pressionar Cima
2. Adicionar Ação: **Mover** → **Definir Velocidade Vertical**
3. Defina a velocidade vertical para `-8`

**Evento: Soltura da Seta para Cima**
1. Adicionar Evento → Teclado → Soltar Cima
2. Adicionar Ação: **Mover** → **Definir Velocidade Vertical**
3. Defina a velocidade vertical para `0`

**Evento: Pressão da Seta para Baixo**
1. Adicionar Evento → Teclado → Pressionar Baixo
2. Adicionar Ação: **Mover** → **Definir Velocidade Vertical**
3. Defina a velocidade vertical para `8`

**Evento: Soltura da Seta para Baixo**
1. Adicionar Evento → Teclado → Soltar Baixo
2. Adicionar Ação: **Mover** → **Definir Velocidade Vertical**
3. Defina a velocidade vertical para `0`

**Evento: Colisão com obj_wall**
1. Adicionar Evento → Colisão → obj_wall
2. Adicionar Ação: **Mover** → **Ricocheteio Contra Objetos**
3. Selecione "Contra objetos sólidos"

---

## Etapa 5: Criar o Objeto Bola

1. Crie um novo objeto nomeado `obj_ball`
2. Defina o sprite para `spr_ball`

**Evento: Criar**
1. Adicionar Evento → Criar
2. Adicionar Ação: **Mover** → **Começar Movimento em Direção**
3. Escolha uma direção diagonal (não reto para cima ou para baixo)
4. Defina a velocidade para `6`

**Evento: Colisão com obj_paddle_left**
1. Adicionar Evento → Colisão → obj_paddle_left
2. Adicionar Ação: **Mover** → **Ricocheteio Contra Objetos**
3. Selecione "Contra objetos sólidos"

**Evento: Colisão com obj_paddle_right**
1. Adicionar Evento → Colisão → obj_paddle_right
2. Adicionar Ação: **Mover** → **Ricocheteio Contra Objetos**
3. Selecione "Contra objetos sólidos"

**Evento: Colisão com obj_wall**
1. Adicionar Evento → Colisão → obj_wall
2. Adicionar Ação: **Mover** → **Ricocheteio Contra Objetos**
3. Selecione "Contra objetos sólidos"

---

## Etapa 6: Criar os Objetos de Gol

Gols são áreas invisíveis atrás de cada raquete. Quando a bola entra em um gol, o jogador adversário marca pontos.

### 6.1 Gol Esquerdo

1. Crie um novo objeto nomeado `obj_goal_left`
2. Defina o sprite para `spr_goal`
3. **Desmarque "Visível"** - o gol deve ser invisível
4. **Marque "Sólido"**

### 6.2 Gol Direito

1. Crie um novo objeto nomeado `obj_goal_right`
2. Defina o sprite para `spr_goal`
3. **Desmarque "Visível"**
4. **Marque "Sólido"**

### 6.3 Adicionar Eventos de Colisão de Gol à Bola

Volte para `obj_ball` e adicione estes eventos:

**Evento: Colisão com obj_goal_left**
1. Adicionar Evento → Colisão → obj_goal_left
2. Adicionar Ação: **Mover** → **Saltar para Posição Inicial** (reseta a bola)
3. Adicionar Ação: **Pontuação** → **Definir Pontuação**
   - Variável: `global.p2score`
   - Valor: `1`
   - Marque "Relativo" (adiciona 1 à pontuação atual)

**Evento: Colisão com obj_goal_right**
1. Adicionar Evento → Colisão → obj_goal_right
2. Adicionar Ação: **Mover** → **Saltar para Posição Inicial**
3. Adicionar Ação: **Pontuação** → **Definir Pontuação**
   - Variável: `global.p1score`
   - Valor: `1`
   - Marque "Relativo"

---

## Etapa 7: Criar o Objeto de Exibição de Pontuação

1. Crie um novo objeto nomeado `obj_score`
2. Nenhum sprite necessário

**Evento: Criar**
1. Adicionar Evento → Criar
2. Adicionar Ação: **Pontuação** → **Definir Pontuação**
   - Variável: `global.p1score`
   - Valor: `0`
3. Adicionar Ação: **Pontuação** → **Definir Pontuação**
   - Variável: `global.p2score`
   - Valor: `0`

**Evento: Desenhar**
1. Adicionar Evento → Desenhar
2. Adicionar Ação: **Desenhar** → **Desenhar Texto**
   - Texto: `Jogador 1:`
   - X: `10`
   - Y: `10`
3. Adicionar Ação: **Desenhar** → **Desenhar Variável**
   - Variável: `global.p1score`
   - X: `100`
   - Y: `10`
4. Adicionar Ação: **Desenhar** → **Desenhar Texto**
   - Texto: `Jogador 2:`
   - X: `10`
   - Y: `30`
5. Adicionar Ação: **Desenhar** → **Desenhar Variável**
   - Variável: `global.p2score`
   - X: `100`
   - Y: `30`

---

## Etapa 8: Projetar a Sala

1. Clique com o botão direito em **Salas** e selecione **Criar Sala**
2. Nomeie como `room_pong`
3. Defina o tamanho da sala (p. ex., 640x480)

**Coloque os objetos:**

1. **Paredes**: Coloque instâncias de `obj_wall` ao longo das bordas superior e inferior da sala
2. **Raquete Esquerda**: Coloque `obj_paddle_left` perto da borda esquerda, centralizada verticalmente
3. **Raquete Direita**: Coloque `obj_paddle_right` perto da borda direita, centralizada verticalmente
4. **Bola**: Coloque `obj_ball` no centro da sala
5. **Gols**:
   - Coloque instâncias de `obj_goal_left` ao longo da borda esquerda (atrás de onde a raquete está)
   - Coloque instâncias de `obj_goal_right` ao longo da borda direita
6. **Exibição de Pontuação**: Coloque `obj_score` em qualquer lugar (não tem sprite, apenas desenha texto)

**Exemplo de Layout da Sala:**
```
[PAREDE PAREDE PAREDE PAREDE PAREDE PAREDE PAREDE PAREDE PAREDE PAREDE]
[GOL]  [RAQUETE_E]            [BOLA]            [RAQUETE_D]  [GOL]
[GOL]  [RAQUETE_E]                              [RAQUETE_D]  [GOL]
[GOL]                                                      [GOL]
[PAREDE PAREDE PAREDE PAREDE PAREDE PAREDE PAREDE PAREDE PAREDE PAREDE]
```

---

## Etapa 9: Teste Seu Jogo!

1. Clique em **Executar** ou pressione **F5** para testar seu jogo
2. Jogador 1 usa **W** (para cima) e **S** (para baixo)
3. Jogador 2 usa **Seta para Cima** e **Seta para Baixo**
4. Tente acertar a bola passando pela raquete do seu adversário!

---

## Melhorias (Opcional)

### Aumentar Velocidade
Faça a bola ficar mais rápida cada vez que acertar uma raquete adicionando aos eventos de colisão:
- Após a ação de ricocheteio, adicione **Mover** → **Definir Velocidade**
- Defina a velocidade para `speed + 0.5` com "Relativo" marcado

### Efeitos Sonoros
Adicione sons quando:
- A bola acerta uma raquete
- A bola acerta uma parede
- Um jogador marca pontos

### Condição de Vitória
Adicione uma verificação no evento Desenhar:
- Se `global.p1score >= 10`, exiba "Jogador 1 Vence!"
- Se `global.p2score >= 10`, exiba "Jogador 2 Vence!"

---

## Solução de Problemas

| Problema | Solução |
|---------|----------|
| A bola passa através da raquete | Certifique-se de que as raquetes têm "Sólido" marcado |
| A raquete não para nas paredes | Adicione evento de colisão com obj_wall |
| A pontuação não se atualiza | Verifique se os nomes das variáveis correspondem exatamente (global.p1score, global.p2score) |
| A bola não se move | Verifique se o evento Criar tem a ação de movimento |

---

## O que Você Aprendeu

Parabéns! Você criou um jogo completo de Pong para dois jogadores! Você aprendeu:

- Como lidar com entrada de teclado para dois jogadores diferentes
- Como usar eventos de Soltura de Tecla para parar o movimento
- Como fazer objetos colidirem e ricochetearem
- Como usar variáveis globais para rastrear pontuações
- Como exibir texto e variáveis na tela

---

## Veja Também

- [Preset para Iniciantes](Beginner-Preset_pt) - Visão geral dos recursos para iniciantes
- [Tutorial: Breakout](Tutorial-Breakout_pt) - Criar um jogo de quebrador de blocos
- [Referência de Eventos](Event-Reference_pt) - Documentação completa de eventos
- [Referência Completa de Ações](Full-Action-Reference_pt) - Todas as ações disponíveis
