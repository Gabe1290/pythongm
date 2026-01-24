# Introdução à Criação de Videojogos com PyGameMaker

*[Home](Home_pt) | [Beginner Preset](Beginner-Preset_pt) | [English](Getting-Started-Breakout) | [Français](Getting-Started-Breakout_fr)*

**Pela Equipa PyGameMaker**

---

Neste tutorial, vamos aprender as noções básicas de criação de jogos com PyGameMaker. Como é um software relativamente completo com muitas funcionalidades, vamos concentrar-nos apenas naquelas que nos vão ajudar durante este tutorial.

Vamos criar um jogo simples estilo Breakout que terá este aspecto:

![Conceito do Jogo Breakout](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

Este tutorial é para ti, mesmo que não tenhas conhecimentos de programação, pois o PyGameMaker permite que iniciantes criem jogos facilmente, independentemente do seu nível de competência.

Muito bem, vamos começar a desenhar o nosso jogo!

---

## Passo 1: Começar

Começa por abrir o PyGameMaker. Deves ver a interface principal com o painel **Assets** no lado esquerdo, listando diferentes categorias de recursos: Sprites, Sounds, Backgrounds, Fonts, Objects e Rooms.

Antes de mais, num videojogo, a primeira coisa que o jogador nota é o que vê no ecrã. Esta é na verdade a base de um jogo: um jogo sem gráficos não existe (ou é um caso muito especial). Vamos portanto começar por inserir imagens no nosso jogo, que serão a representação gráfica dos objetos que o jogador verá no ecrã. Na terminologia de desenvolvimento de jogos, estas imagens chamam-se **Sprites**.

---

## Passo 2: Criar os Sprites

### 2.1 Criar o Sprite da Raquete

1. Clica com o botão direito na pasta **Sprites** no topo da coluna esquerda
2. Clica em **Create Sprite**
3. Uma janela chamada **Sprite Properties** vai abrir - é aqui que vais definir todas as características do teu sprite
4. Usa o editor integrado para desenhar um retângulo horizontal (cerca de 64x16 pixels) numa cor à tua escolha
5. **Importante:** Clica em **Center** para definir a origem no centro do teu sprite
   > A origem de um sprite é o seu ponto central, as suas coordenadas X:0 e Y:0. Estas são as suas coordenadas base.
6. Altera o nome do teu sprite usando o campo de texto no topo, e escreve `spr_paddle`
   > Isto não tem impacto técnico - é apenas para te ajudar a navegar melhor nos teus ficheiros quando tiveres mais. Podes escolher qualquer nome que queiras; isto é apenas um exemplo.
7. Clica **OK**

Acabaste de criar o teu primeiro sprite! Esta é a tua raquete, o objeto que o jogador vai controlar para apanhar a bola.

### 2.2 Criar o Sprite da Bola

Vamos continuar e adicionar mais sprites. Repete o mesmo processo:

1. Clica com o botão direito em **Sprites** → **Create Sprite**
2. Desenha um pequeno círculo (cerca de 16x16 pixels)
3. Clica em **Center** para definir a origem
4. Dá-lhe o nome `spr_ball`
5. Clica **OK**

### 2.3 Criar os Sprites dos Tijolos

Precisamos de três tipos de tijolos. Cria-os um a um:

**Primeiro Tijolo (Destrutível):**
1. Cria um novo sprite
2. Desenha um retângulo (cerca de 48x24 pixels) - usa uma cor viva como vermelho
3. Clica em **Center**, dá-lhe o nome `spr_brick_1`
4. Clica **OK**

**Segundo Tijolo (Destrutível):**
1. Cria um novo sprite
2. Desenha um retângulo (mesmo tamanho) - usa uma cor diferente como azul
3. Clica em **Center**, dá-lhe o nome `spr_brick_2`
4. Clica **OK**

**Terceiro Tijolo (Parede Indestrutível):**
1. Cria um novo sprite
2. Desenha um retângulo (mesmo tamanho) - usa uma cor mais escura como cinzento
3. Clica em **Center**, dá-lhe o nome `spr_brick_3`
4. Clica **OK**

Agora deves ter todos os sprites para o nosso jogo:
- `spr_paddle` - A raquete do jogador
- `spr_ball` - A bola que salta
- `spr_brick_1` - Primeiro tijolo destrutível
- `spr_brick_2` - Segundo tijolo destrutível
- `spr_brick_3` - Tijolo de parede indestrutível

> **Nota:** Nos jogos, existem geralmente duas fontes principais de renderização gráfica: **Sprites** e **Backgrounds**. É tudo o que compõe o que vês no ecrã. Um Background é, como o nome indica, uma imagem de fundo.

---

## Passo 3: Compreender Objetos e Eventos

O que dissemos no início? A primeira coisa que o jogador nota é o que vê no ecrã. Já tratámos disso com os nossos sprites. Mas um jogo feito apenas de imagens não é um jogo - é uma pintura! Vamos agora passar à próxima etapa: **Objects**.

Um Object é uma entidade no teu jogo que pode ter comportamentos, responder a eventos e interagir com outros objetos. O sprite é apenas a representação visual; o objeto é o que lhe dá vida.

### Como Funciona a Lógica do Jogo

Tudo na programação de jogos segue este padrão: **Se isto acontece, então executo aquilo.**

- Se o jogador carrega numa tecla, então faço isto
- Se esta variável é igual a este valor, então faço aquilo
- Se dois objetos colidem, então acontece algo

Isto é o que chamamos **Events** e **Actions** no PyGameMaker:
- **Events** = Coisas que podem acontecer (pressionar tecla, colisão, temporizador, etc.)
- **Actions** = Coisas que queres fazer quando os eventos ocorrem (mover, destruir, alterar pontuação, etc.)

---

## Passo 4: Criar o Objeto Raquete

Vamos criar o objeto que o jogador vai controlar: a raquete.

### 4.1 Criar o Objeto

1. Clica com o botão direito na pasta **Objects** → **Create Object**
2. Dá-lhe o nome `obj_paddle`
3. No menu dropdown **Sprite**, seleciona `spr_paddle` - agora o nosso objeto tem uma aparência visual!
4. Marca a caixa **Solid** (vamos precisar disto para as colisões)

### 4.2 Programar o Movimento

Num jogo Breakout, precisamos de mover a raquete para impedir que a bola escape por baixo. Vamos controlá-la com o teclado.

**Mover para a Direita:**
1. Clica em **Add Event** → **Keyboard** → **Right Arrow**
2. No painel de ações à direita, adiciona a ação **Set Horizontal Speed**
3. Define o **value** para `5`
4. Clica **OK**

Isto significa: "Quando a tecla Seta Direita é pressionada, define a velocidade horizontal para 5 (movendo para a direita)."

**Mover para a Esquerda:**
1. Clica em **Add Event** → **Keyboard** → **Left Arrow**
2. Adiciona a ação **Set Horizontal Speed**
3. Define o **value** para `-5`
4. Clica **OK**

**Parar Quando as Teclas São Libertadas:**

Se testarmos agora, a raquete continuaria a mover-se mesmo depois de largar a tecla! Vamos corrigir isso:

1. Clica em **Add Event** → **Keyboard Release** → **Right Arrow**
2. Adiciona a ação **Set Horizontal Speed** com valor `0`
3. Clica **OK**

4. Clica em **Add Event** → **Keyboard Release** → **Left Arrow**
5. Adiciona a ação **Set Horizontal Speed** com valor `0`
6. Clica **OK**

Agora a nossa raquete move-se quando as teclas são pressionadas e para quando são libertadas. Terminamos com este objeto por agora!

---

## Passo 5: Criar o Objeto Tijolo Parede

Vamos criar um tijolo de parede indestrutível - isto vai formar os limites da nossa área de jogo.

1. Cria um novo objeto com o nome `obj_brick_3`
2. Atribui o sprite `spr_brick_3`
3. Marca a caixa **Solid**

A bola vai saltar deste tijolo. Como é apenas uma parede, não precisamos de eventos - só precisa de ser sólido. Clica **OK** para guardar.

---

## Passo 6: Criar o Objeto Bola

Agora vamos criar a bola, o elemento essencial do nosso jogo.

### 6.1 Criar o Objeto

1. Cria um novo objeto com o nome `obj_ball`
2. Atribui o sprite `spr_ball`
3. Marca a caixa **Solid**

### 6.2 Movimento Inicial

Queremos que a bola se mova sozinha desde o início. Vamos dar-lhe uma velocidade e direção inicial.

1. Clica em **Add Event** → **Create**
   > O evento Create executa ações quando o objeto aparece no jogo, ou seja, quando entra em cena.
2. Adiciona a ação **Set Horizontal Speed** com valor `4`
3. Adiciona a ação **Set Vertical Speed** com valor `-4`
4. Clica **OK**

Isto dá à bola um movimento diagonal (direita e para cima) no início do jogo.

### 6.3 Saltar da Raquete

Precisamos que a bola salte quando bate na raquete.

1. Clica em **Add Event** → **Collision** → seleciona `obj_paddle`
   > Este evento dispara quando a bola colide com a raquete.
2. Adiciona a ação **Reverse Vertical**
   > Isto inverte a direção vertical, fazendo a bola saltar.
3. Clica **OK**

### 6.4 Saltar das Paredes

Mesma operação para os tijolos parede:

1. Clica em **Add Event** → **Collision** → seleciona `obj_brick_3`
2. Adiciona a ação **Reverse Vertical**
3. Adiciona a ação **Reverse Horizontal**
   > Adicionamos ambos porque a bola pode bater na parede de diferentes ângulos.
4. Clica **OK**

---

## Passo 7: Testar o Nosso Progresso - Criar uma Room

Depois dos Sprites e Objects, chegam as **Rooms**. Uma room é onde o jogo acontece: é um mapa, um nível. É aqui que colocas todos os elementos do teu jogo, onde organizas o que vai aparecer no ecrã.

### 7.1 Criar a Room

1. Clica com o botão direito em **Rooms** → **Create Room**
2. Dá-lhe o nome `room_game`

### 7.2 Colocar os Teus Objetos

Agora coloca os teus objetos usando o rato:
- **Clique esquerdo** para colocar um objeto
- **Clique direito** para apagar um objeto

Seleciona o objeto a colocar no menu dropdown no editor de room.

**Constrói o teu nível:**
1. Coloca instâncias de `obj_brick_3` à volta das bordas (topo, esquerda, direita) - deixa o fundo aberto!
2. Coloca `obj_paddle` no centro em baixo
3. Coloca `obj_ball` algures no meio

### 7.3 Testar o Jogo!

Clica no botão **Play** (seta verde) na barra de ferramentas. Isto permite-te testar o teu jogo a qualquer momento.

Já podes divertir-te a fazer a bola saltar das paredes e da raquete!

É mínimo, mas já é um bom começo - tens a base do teu jogo!

---

## Passo 8: Adicionar Tijolos Destrutíveis

Vamos adicionar alguns tijolos para partir, para tornar o nosso jogo mais divertido.

### 8.1 Primeiro Tijolo Destrutível

1. Cria um novo objeto com o nome `obj_brick_1`
2. Atribui o sprite `spr_brick_1`
3. Marca **Solid**

Vamos adicionar o comportamento para se destruir quando atingido pela bola:

1. Clica em **Add Event** → **Collision** → seleciona `obj_ball`
2. Adiciona a ação **Destroy Instance** com target **self**
   > Esta ação remove um objeto durante o jogo - aqui, o próprio tijolo.
3. Clica **OK**

E assim, tens o teu novo tijolo destrutível!

### 8.2 Segundo Tijolo Destrutível (Usando Parent)

Agora vamos criar um segundo tijolo destrutível, mas sem ter de o reprogramar. Vamos torná-lo um "clone" usando a funcionalidade **Parent**.

1. Cria um novo objeto com o nome `obj_brick_2`
2. Atribui o sprite `spr_brick_2`
3. Marca **Solid**
4. No menu dropdown **Parent**, seleciona `obj_brick_1`

O que significa isto? Simplesmente que o que programámos em `obj_brick_1` será herdado por `obj_brick_2`, sem termos de o reproduzir nós próprios. A relação pai-filho permite que objetos partilhem comportamentos!

Clica **OK** para guardar.

### 8.3 Fazer a Bola Saltar dos Novos Tijolos

Reabre `obj_ball` fazendo duplo clique nele, e adiciona eventos de colisão para os nossos novos tijolos:

1. Clica em **Add Event** → **Collision** → seleciona `obj_brick_1`
2. Adiciona a ação **Reverse Vertical**
3. Clica **OK**

4. Clica em **Add Event** → **Collision** → seleciona `obj_brick_2`
5. Adiciona a ação **Reverse Vertical**
6. Clica **OK**

---

## Passo 9: Game Over - Reiniciar a Room

Precisamos de reiniciar o nível se a bola escapar do ecrã (se o jogador não conseguir apanhá-la).

Em `obj_ball`:

1. Clica em **Add Event** → **Other** → **Outside Room**
2. Adiciona a ação **Restart Room**
   > Esta ação reinicia a room atual durante o jogo.
3. Clica **OK**

---

## Passo 10: Design Final do Nível

Agora coloca tudo na tua room para criar o teu nível final de Breakout:

1. Abre `room_game`
2. Organiza as paredes `obj_brick_3` à volta do topo e dos lados
3. Coloca linhas de `obj_brick_1` e `obj_brick_2` em padrões no topo
4. Mantém `obj_paddle` no centro em baixo
5. Coloca `obj_ball` acima da raquete

**Exemplo de layout:**
```
[3][3][3][3][3][3][3][3][3][3]
[3][1][1][2][2][1][1][2][2][3]
[3][2][2][1][1][2][2][1][1][3]
[3][1][1][2][2][1][1][2][2][3]
[3]                        [3]
[3]                        [3]
[3]         (bola)         [3]
[3]                        [3]
[3]       [raquete]        [3]
```

---

## Parabéns!

O teu jogo Breakout está completo! Agora podes desfrutar do teu trabalho jogando o jogo que acabaste de criar!

Também podes refiná-lo ainda mais, como adicionar:
- **Efeitos sonoros** para os saltos e destruição de tijolos
- **Contagem de pontos** usando a ação Add Score
- **Tipos de tijolos adicionais** com comportamentos diferentes
- **Múltiplos níveis** com layouts diferentes

---

## Resumo do Que Aprendeste

| Conceito | Descrição |
|----------|-----------|
| **Sprites** | Imagens visuais que representam objetos no teu jogo |
| **Objects** | Entidades de jogo com comportamentos, combinando sprites com eventos e ações |
| **Events** | Gatilhos que executam ações (Create, Keyboard, Collision, etc.) |
| **Actions** | Operações a realizar (Move, Destroy, Bounce, etc.) |
| **Solid** | Propriedade que permite deteção de colisões |
| **Parent** | Permite que objetos herdem comportamentos de outros objetos |
| **Rooms** | Níveis de jogo onde colocas instâncias de objetos |

---

## Resumo dos Objetos

| Objeto | Sprite | Solid | Eventos |
|--------|--------|-------|---------|
| `obj_paddle` | `spr_paddle` | Sim | Keyboard (Left/Right), Keyboard Release |
| `obj_ball` | `spr_ball` | Sim | Create, Collision (paddle, bricks), Outside Room |
| `obj_brick_1` | `spr_brick_1` | Sim | Collision (ball) - Destroy self |
| `obj_brick_2` | `spr_brick_2` | Sim | Herda de `obj_brick_1` |
| `obj_brick_3` | `spr_brick_3` | Sim | Nenhum (apenas uma parede) |

---

## Ver Também

- [Beginner Preset](Beginner-Preset_pt) - Eventos e ações disponíveis para iniciantes
- [Event Reference](Event-Reference_pt) - Lista completa de todos os eventos
- [Full Action Reference](Full-Action-Reference_pt) - Lista completa de todas as ações
- [Tutorial: Breakout](Tutorial-Breakout_pt) - Versão mais curta deste tutorial

---

Estás agora iniciado nas noções básicas de criação de videojogos com PyGameMaker. Agora é a tua vez de criar os teus próprios jogos!
