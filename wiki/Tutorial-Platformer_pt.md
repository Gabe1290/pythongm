# Tutorial: Criar um Jogo de Plataforma

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Platformer) | [Français](Tutorial-Platformer_fr) | [Deutsch](Tutorial-Platformer_de) | [Italiano](Tutorial-Platformer_it) | [Español](Tutorial-Platformer_es) | [Português](Tutorial-Platformer_pt) | [Slovenščina](Tutorial-Platformer_sl) | [Українська](Tutorial-Platformer_uk) | [Русский](Tutorial-Platformer_ru)

---

## Introdução

Neste tutorial, você criará um **Jogo de Plataforma** - um jogo de ação de rolagem lateral onde o jogador corre, pula e navega por plataformas enquanto evita perigos e coleta moedas. Este gênero clássico é perfeito para aprender gravidade, mecânicas de pulo e colisão com plataformas.

**O que você aprenderá:**
- Gravidade e física de queda
- Mecânicas de pulo com detecção de chão
- Colisão com plataformas (aterrissar em cima)
- Movimento esquerda/direita
- Colecionáveis e perigos

**Dificuldade:** Iniciante
**Preset:** Preset Iniciante

---

## Passo 1: Entender o Jogo

### Mecânicas do Jogo
1. O jogador é afetado pela gravidade e cai
2. O jogador pode se mover para esquerda e direita
3. O jogador pode pular quando está no chão
4. Plataformas impedem o jogador de cair através
5. Colete moedas para pontos
6. Alcance a bandeira para completar o nível

### O Que Precisamos

| Elemento | Propósito |
|----------|-----------|
| **Jogador** | O personagem que você controla |
| **Chão/Plataforma** | Superfícies sólidas para ficar em pé |
| **Moeda** | Itens colecionáveis para pontuação |
| **Espinho** | Perigo que machuca o jogador |
| **Bandeira** | Meta que termina o nível |

---

## Passo 2: Criar os Sprites

### 2.1 Sprite do Jogador
- Nome: `spr_player`
- Desenhe um personagem simples
- Tamanho: 32x48 pixels

### 2.2 Sprite do Chão
- Nome: `spr_ground`
- Desenhe um bloco de grama/terra
- Tamanho: 32x32 pixels

### 2.3 Sprite da Plataforma
- Nome: `spr_platform`
- Desenhe uma plataforma flutuante
- Tamanho: 64x16 pixels

### 2.4 Sprite da Moeda
- Nome: `spr_coin`
- Pequeno círculo amarelo/dourado
- Tamanho: 16x16 pixels

### 2.5 Sprite do Espinho
- Nome: `spr_spike`
- Triângulos apontando para cima
- Tamanho: 32x32 pixels

### 2.6 Sprite da Bandeira
- Nome: `spr_flag`
- Bandeira em um mastro
- Tamanho: 32x64 pixels

---

## Passo 3: Criar o Objeto Chão

O chão é uma plataforma sólida que impede o jogador de cair.

1. Clique com o botão direito em **Objects** e selecione **Create Object**
2. Nomeie como `obj_ground`
3. Defina o sprite como `spr_ground`
4. **Marque a caixa "Solid"**
5. Nenhum evento necessário

---

## Passo 4: Criar o Objeto Plataforma

Plataformas funcionam como o chão, mas podem ser colocadas no ar.

1. Crie um novo objeto chamado `obj_platform`
2. Defina o sprite como `spr_platform`
3. **Marque a caixa "Solid"**

---

## Passo 5: Criar o Objeto Jogador

O jogador é o objeto mais complexo, com gravidade, pulo e movimento.

1. Crie um novo objeto chamado `obj_player`
2. Defina o sprite como `spr_player`

### 5.1 Gravidade

**Evento: Create** — Add Action: **Move** → **Set Gravity**
(Direction: `270`, Gravity: `0.5`) — 270° é diretamente para baixo; o
valor é somado à velocidade vertical do jogador a cada quadro, então o
jogador acelera para baixo sozinho a partir daqui.

### 5.2 Movimento, Pulo e Colisão com o Chão

Adicione estes eventos, seguindo o mesmo padrão que os tutoriais
anteriores deste wiki já usam:

| Evento | Ação |
|---|---|
| Keyboard (held) → Left Arrow | Set Horizontal Speed para `-4` |
| Keyboard (held) → Right Arrow | Set Horizontal Speed para `4` |
| Keyboard: No Key | Set Horizontal Speed para `0` |
| Key Press → Up Arrow | Set Vertical Speed para `-10` |
| Collision with obj_ground | Stop Movement |

Dois detalhes que fazem tudo parecer certo:

- **No Key define APENAS a velocidade horizontal como 0** — nunca use
  Stop Movement aqui, porque Stop Movement também zera a velocidade
  vertical, o que anularia a gravidade toda vez que o jogador soltasse
  uma tecla de direção.
- **Key Press (não held)** é o que faz Up ser um único impulso de
  pulo, em vez de lançar o jogador para cima a cada quadro em que é
  mantido pressionado. **Stop Movement** ao aterrissar anula esse
  impulso, para que o jogador não continue subindo depois de aterrissar
  — a colisão sólida integrada do motor (o Passo 3 já tornou
  `obj_ground` Solid) já impede que o jogador afunde no chão; o evento
  aqui apenas limpa a velocidade de queda restante.

---

## Passo 6-8: Colecionáveis e Perigos

**obj_coin** - Colisão com obj_player: Pontuação +10, destruir Self

**obj_spike** - Colisão com obj_player: Mostrar mensagem, reiniciar a sala

**obj_flag** - Colisão com obj_player: Mostrar mensagem, próxima sala

---

## Passo 9: Projete Seu Nível

1. Crie `room_level1` (800x480)
2. Ative ajuste à grade (32x32)
3. Coloque o chão embaixo, plataformas no ar
4. Adicione moedas, espinhos
5. Coloque a bandeira no final, o jogador no início

---

## O Que Você Aprendeu

- **Física de gravidade** - Set Gravity aplica uma força constante para baixo a cada quadro
- **Mecânicas de pulo** - Um evento Key Press (não held) dá um único impulso de velocidade para cima
- **Colisão sólida integrada** - O chão bloqueia o jogador automaticamente uma vez marcado como Solid, sem código manual de verificação de posição

---

## Veja Também

- [Tutoriais](Tutorials_pt) - Mais tutoriais de jogos
- [Tutorial: Labirinto](Tutorial-Maze_pt) - Criar um jogo de labirinto
