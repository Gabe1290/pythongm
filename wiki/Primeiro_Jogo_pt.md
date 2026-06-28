# Criar o seu primeiro jogo

> [English](Creating-Your-First-Game) | [Français](Premier_Jeu_fr) | [Deutsch](Erstes_Spiel_de) | [Italiano](Primo_Gioco_it) | [Español](Primer_Juego_es) | [Português](Primeiro_Jogo_pt) | [Slovenščina](Prva_Igra_sl) | [Українська](Persha_Gra_uk) | [Русский](Pervaya_Igra_ru)

---

[Voltar ao Inicio](Home_pt)

Neste guia vai criar um jogo simples para aprender os conceitos basicos do pyGM.

## Visao geral

Vamos criar um jogo simples com:
- Uma personagem jogador que se pode mover
- Um objeto colecionavel
- Um sistema de pontuacao

## Passo 1: Criar um novo projeto

1. Inicie o pyGM
2. Selecione "Novo Projeto"
3. Introduza um nome para o projeto
4. Escolha uma localizacao para guardar

## Passo 2: Criar sprites

### Sprite do jogador
1. Clique direito em "Sprites" na arvore de recursos
2. Selecione "Novo Sprite"
3. Use o editor integrado ou importe uma imagem
4. Nomeie-o "spr_jogador"

### Sprite do objeto colecionavel
1. Crie outro sprite
2. Nomeie-o "spr_moeda"

## Passo 3: Criar objetos

### Objeto jogador
1. Clique direito em "Objetos"
2. Selecione "Novo Objeto"
3. Nomeie-o "obj_jogador"
4. Atribua "spr_jogador" como sprite

### Adicionar movimento
1. Adicione o evento "Pressao de tecla"
2. Use acoes para o movimento:
   - Seta para cima: Mover para cima
   - Seta para baixo: Mover para baixo
   - Seta para a esquerda: Mover para a esquerda
   - Seta para a direita: Mover para a direita

### Objeto moeda
1. Crie "obj_moeda"
2. Atribua "spr_moeda"
3. Adicione evento de colisao com o jogador
4. Acao: Destruir instancia e adicionar pontos

## Passo 4: Criar uma sala

1. Clique direito em "Salas"
2. Selecione "Nova Sala"
3. Nomeie-a "rm_nivel1"
4. Coloque os objetos:
   - Um jogador
   - Varias moedas

## Passo 5: Testar o jogo

1. Clique em "Executar jogo" ou pressione F5
2. Teste o movimento
3. Recolha as moedas

## Ideias de expansao

- Adicionar obstaculos
- Implementar um sistema de tempo
- Criar diferentes niveis
- Adicionar efeitos sonoros

## Proximos passos

- [Aprofundar Eventos e Acoes](Eventos_e_Acoes_pt)
- [Aprender Programacao Visual](Programacao_Visual_pt)
- [Exportar Jogos](Exportar_Jogos_pt)
