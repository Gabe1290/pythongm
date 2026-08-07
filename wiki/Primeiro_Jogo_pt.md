# Criar o seu primeiro jogo

> [English](Creating-Your-First-Game) | [Français](Premier_Jeu_fr) | [Deutsch](Erstes_Spiel_de) | [Italiano](Primo_Gioco_it) | [Español](Primer_Juego_es) | [Português](Primeiro_Jogo_pt) | [Slovenščina](Prva_Igra_sl) | [Українська](Persha_Gra_uk) | [Русский](Pervaya_Igra_ru)

---

[Voltar ao Início](Home_pt)

Neste tutorial, vamos criar um jogo simples "Apanha as Estrelas" em que o jogador se move para recolher estrelas que caem.

---

## O Que Vai Aprender

- Criar sprites
- Criar objetos com eventos e ações
- Usar o editor de salas
- Executar e testar o seu jogo

---

## Passo 1: Criar um Novo Projeto

1. Inicie o PyGameMaker
2. Vá a **File > New Project**
3. Dê ao seu projeto o nome "CatchTheStars"
4. Clique em **Create**

---

## Passo 2: Criar o Sprite do Jogador

1. Clique com o botão direito em **Sprites** na árvore de recursos
2. Selecione **Create Sprite**
3. Dê-lhe o nome `spr_player`
4. Clique em **Edit Sprite** para abrir o editor de sprites
5. Desenhe uma personagem simples (ou use um retângulo colorido 32x32)
6. Clique em **Save**

---

## Passo 3: Criar o Sprite da Estrela

1. Clique com o botão direito em **Sprites** > **Create Sprite**
2. Dê-lhe o nome `spr_star`
3. Desenhe uma forma de estrela (ou use um círculo amarelo)
4. Clique em **Save**

---

## Passo 4: Criar o Objeto Jogador

1. Clique com o botão direito em **Objects** na árvore de recursos
2. Selecione **Create Object**
3. Dê-lhe o nome `obj_player`
4. Defina o **Sprite** como `spr_player`

### Adicionar os Eventos de Teclado

**Seta Esquerda:**
1. Clique em **Add Event** > **Keyboard** > **Left**
2. Adicione a ação: **Set Horizontal Speed** com valor `-4`

**Seta Direita:**
1. Clique em **Add Event** > **Keyboard** > **Right**
2. Adicione a ação: **Set Horizontal Speed** com valor `4`

**Nenhuma Tecla Pressionada:**
1. Clique em **Add Event** > **Keyboard** > **No Key**
2. Adicione a ação: **Set Horizontal Speed** com valor `0`

---

## Passo 5: Criar o Objeto Estrela

1. Clique com o botão direito em **Objects** > **Create Object**
2. Dê-lhe o nome `obj_star`
3. Defina o **Sprite** como `spr_star`

### Adicionar o Evento Create
1. Clique em **Add Event** > **Create**
2. Adicione a ação: **Set Vertical Speed** com valor `3`
3. Adicione a ação: **Jump To Position** com X `irandom(600)`, Y `20`
   — `irandom(n)` escolhe um número inteiro aleatório de 0 a `n`,
   então isto espalha a estrela num ponto aleatório perto do topo de
   uma sala com 640 pixels de largura sempre que (re)aparece

### Adicionar o Evento Outside Room
1. Clique em **Add Event** > **Other** > **Outside Room**
2. Adicione a ação: **Jump to Start Position**
3. Adicione a ação: **Set Score** com valor `1` e **Relative** marcado

### Adicionar a Colisão com o Jogador
1. Clique em **Add Event** > **Collision** > selecione `obj_player`
2. Adicione a ação: **Set Score** com valor `10` e **Relative** marcado
3. Adicione a ação: **Play Sound** (opcional, se tiver um som)
4. Adicione a ação: **Jump to Random Position**

---

## Passo 6: Criar a Sala

1. Clique com o botão direito em **Rooms** na árvore de recursos
2. Selecione **Create Room**
3. Dê-lhe o nome `room_game`
4. Defina o tamanho da sala como **640 x 480**

### Colocar os Objetos
1. Selecione a aba **Objects** no editor de salas
2. Clique em `obj_player` e coloque-o no centro inferior da sala
3. Clique em `obj_star` e coloque de 5 a 10 estrelas espalhadas no topo

---

## Passo 7: Mostrar a Pontuação

1. Abra `obj_player`
2. Clique em **Add Event** > **Draw**
3. Adicione a ação: **Draw Score** na posição (10, 10)

---

## Passo 8: Execute o Seu Jogo!

1. Prima **F5** ou vá a **Build > Test Game**
2. Use as teclas de seta esquerda e direita para se mover
3. Apanhe as estrelas que caem para aumentar a sua pontuação!

---

## Melhorias para Experimentar

### Adicionar Vidas
1. Crie um objeto de "game over" que aparece quando as vidas chegam a 0
2. Adicione um evento de colisão com um objeto "mau" que reduz as vidas

### Adicionar Níveis
1. Crie várias salas
2. Use a ação **Next Room** quando a pontuação atingir um limiar

### Adicionar Som
1. Importe ficheiros de áudio no recurso Sounds
2. Adicione ações **Play Sound** aos eventos

### Usar a Programação Visual
1. Abra um objeto
2. Clique na aba **Blockly** para a programação de arrastar e soltar
3. Construa a mesma lógica visualmente com blocos

---

## Estrutura Completa do Projeto

Depois de concluir este tutorial, o seu projeto deverá ter:

- **Sprites:** spr_player, spr_star
- **Objetos:** obj_player, obj_star
- **Salas:** room_game

---

## Próximos Passos

- [[Editor_Objetos_pt]] - Saiba mais sobre as propriedades dos objetos
- [[Eventos_e_Acoes_pt]] - Explore todos os eventos e ações disponíveis
- [[Programacao_Visual_pt]] - Experimente construir com blocos Blockly
- [[Exportar_Jogos_pt]] - Partilhe o seu jogo com outros
