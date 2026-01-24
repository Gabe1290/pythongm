# Tutorial: Criar um Jogo Breakout

*[Home](Home_pt) | [Beginner Preset](Beginner-Preset_pt) | [English](Tutorial-Breakout)*

Este tutorial vai guia-lo na criacao de um jogo classico de Breakout. E um primeiro projeto perfeito para aprender PyGameMaker!

![Conceito do Jogo Breakout](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

---

## O Que Vai Aprender

- Criar e usar sprites
- Configurar objetos de jogo com eventos e acoes
- Controlos de teclado para movimento do jogador
- Detecao de colisoes e ricochete
- Destruir objetos em colisao
- Construir uma sala de jogo

---

## Passo 1: Criar os Sprites

Primeiro, precisamos criar os elementos visuais para o nosso jogo.

### 1.1 Criar o Sprite da Raquete
1. No painel **Assets**, clique com o botao direito em **Sprites** → **Create Sprite**
2. Nomeie-o `spr_paddle`
3. Desenhe um retangulo horizontal (cerca de 64x16 pixels)
4. **Importante:** Clique em **Center** para definir a origem no centro

### 1.2 Criar o Sprite da Bola
1. Crie outro sprite chamado `spr_ball`
2. Desenhe um pequeno circulo (cerca de 16x16 pixels)
3. Clique em **Center** para definir a origem

### 1.3 Criar o Sprite do Tijolo
1. Crie um sprite chamado `spr_brick`
2. Desenhe um retangulo (cerca de 48x24 pixels)
3. Clique em **Center** para definir a origem

### 1.4 Criar o Sprite da Parede
1. Crie um sprite chamado `spr_wall`
2. Desenhe um quadrado (cerca de 32x32 pixels) - este sera o limite
3. Clique em **Center** para definir a origem

### 1.5 Criar um Fundo (Opcional)
1. Clique com o botao direito em **Backgrounds** → **Create Background**
2. Nomeie-o `bg_game`
3. Desenhe ou carregue uma imagem de fundo

---

## Passo 2: Criar o Objeto Raquete

Agora vamos programar a raquete que o jogador controla.

### 2.1 Criar o Objeto
1. Clique com o botao direito em **Objects** → **Create Object**
2. Nomeie-o `obj_paddle`
3. Defina o **Sprite** como `spr_paddle`
4. Marque a caixa **Solid**

### 2.2 Adicionar Movimento para Seta Direita
1. Clique em **Add Event** → **Keyboard** → selecione **Right Arrow**
2. Adicione a acao **Set Horizontal Speed**
3. Defina **value** como `5` (ou qualquer velocidade que preferir)

### 2.3 Adicionar Movimento para Seta Esquerda
1. Clique em **Add Event** → **Keyboard** → selecione **Left Arrow**
2. Adicione a acao **Set Horizontal Speed**
3. Defina **value** como `-5`

### 2.4 Parar Quando as Teclas Sao Libertadas
A raquete continua a mover-se mesmo apos libertar a tecla! Vamos corrigir isso.

1. Clique em **Add Event** → **Keyboard Release** → selecione **Right Arrow**
2. Adicione a acao **Set Horizontal Speed**
3. Defina **value** como `0`

4. Clique em **Add Event** → **Keyboard Release** → selecione **Left Arrow**
5. Adicione a acao **Set Horizontal Speed**
6. Defina **value** como `0`

Agora a raquete para quando liberta as teclas de seta.

---

## Passo 3: Criar o Objeto Bola

### 3.1 Criar o Objeto
1. Crie um novo objeto chamado `obj_ball`
2. Defina o **Sprite** como `spr_ball`
3. Marque a caixa **Solid**

### 3.2 Definir Movimento Inicial
1. Clique em **Add Event** → **Create**
2. Adicione a acao **Move in Direction** (ou **Set Horizontal/Vertical Speed**)
3. Defina uma direcao diagonal com velocidade `5`
   - Por exemplo: **hspeed** = `4`, **vspeed** = `-4`

Isto faz a bola comecar a mover-se quando o jogo comeca.

### 3.3 Ricochete na Raquete
1. Clique em **Add Event** → **Collision** → selecione `obj_paddle`
2. Adicione a acao **Reverse Vertical** (para ricochete)

### 3.4 Ricochete nas Paredes
1. Clique em **Add Event** → **Collision** → selecione `obj_wall`
2. Adicione a acao **Reverse Horizontal** ou **Reverse Vertical** conforme necessario
   - Ou use ambos para lidar com ricochetes nos cantos

---

## Passo 4: Criar o Objeto Tijolo

### 4.1 Criar o Objeto
1. Crie um novo objeto chamado `obj_brick`
2. Defina o **Sprite** como `spr_brick`
3. Marque a caixa **Solid**

### 4.2 Destruir na Colisao com a Bola
1. Clique em **Add Event** → **Collision** → selecione `obj_ball`
2. Adicione a acao **Destroy Instance** com alvo **self**

Isto destroi o tijolo quando a bola o atinge!

### 4.3 Fazer a Bola Ricochete
No mesmo evento de colisao, adicione tambem:
1. Adicione a acao **Reverse Vertical** (aplicada a **other** - a bola)

Ou volte a `obj_ball` e adicione:
1. **Add Event** → **Collision** → selecione `obj_brick`
2. Adicione a acao **Reverse Vertical**

---

## Passo 5: Criar o Objeto Parede

### 5.1 Criar o Objeto
1. Crie um novo objeto chamado `obj_wall`
2. Defina o **Sprite** como `spr_wall`
3. Marque a caixa **Solid**

E so isso - a parede so precisa de ser solida para a bola ricochete.

---

## Passo 6: Criar a Sala de Jogo

### 6.1 Criar a Sala
1. Clique com o botao direito em **Rooms** → **Create Room**
2. Nomeie-a `room_game`

### 6.2 Definir o Fundo (Opcional)
1. Nas definicoes da sala, encontre **Background**
2. Selecione o seu fundo `bg_game`
3. Marque **Stretch** se quiser que preencha a sala

### 6.3 Colocar os Objetos

Agora coloque os seus objetos na sala:

1. **Colocar a Raquete:** Ponha `obj_paddle` no centro inferior da sala

2. **Colocar as Paredes:** Ponha instancias de `obj_wall` a volta das bordas:
   - Ao longo do topo
   - Ao longo do lado esquerdo
   - Ao longo do lado direito
   - Deixe o fundo aberto (e por aqui que a bola pode escapar!)

3. **Colocar a Bola:** Ponha `obj_ball` algures no meio

4. **Colocar os Tijolos:** Arranje instancias de `obj_brick` em filas no topo da sala

---

## Passo 7: Testar o Seu Jogo!

1. Clique no botao **Play** (seta verde)
2. Use as teclas de seta **Esquerda** e **Direita** para mover a raquete
3. Tente fazer a bola ricochete para destruir todos os tijolos!
4. Pressione **Escape** para sair

---

## O Que Vem a Seguir?

O seu jogo basico de Breakout esta completo! Aqui estao algumas melhorias para tentar:

### Adicionar um Sistema de Vidas
- Adicione um evento **No More Lives** para mostrar "Game Over"
- Perca uma vida quando a bola sai pelo fundo

### Adicionar Pontuacao
- Use a acao **Add Score** ao destruir tijolos
- Mostre a pontuacao com **Draw Score**

### Adicionar Multiplos Niveis
- Crie mais salas com diferentes disposicoes de tijolos
- Use **Next Room** quando todos os tijolos forem destruidos

### Adicionar Efeitos Sonoros
- Adicione sons para ricochete e destruicao de tijolos
- Use a acao **Play Sound**

---

## Resumo dos Objetos

| Objeto | Sprite | Solido | Eventos |
|--------|--------|--------|---------|
| `obj_paddle` | `spr_paddle` | Sim | Keyboard (Left/Right), Keyboard Release |
| `obj_ball` | `spr_ball` | Sim | Create, Collision (paddle, wall, brick) |
| `obj_brick` | `spr_brick` | Sim | Collision (ball) - Destruir self |
| `obj_wall` | `spr_wall` | Sim | Nenhum necessario |

---

## Ver Tambem

- [Beginner Preset](Beginner-Preset_pt) - Eventos e acoes usados neste tutorial
- [Event Reference](Event-Reference_pt) - Todos os eventos disponiveis
- [Full Action Reference](Full-Action-Reference_pt) - Todas as acoes disponiveis
