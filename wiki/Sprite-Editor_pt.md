# Editor de Sprites

> [English](Sprite-Editor) | [Français](Sprite-Editor_fr) | [Deutsch](Sprite-Editor_de) | [Italiano](Sprite-Editor_it) | [Español](Sprite-Editor_es) | [Português](Sprite-Editor_pt) | [Русский](Sprite-Editor_ru)

---

> [Voltar ao Início](Home_pt)

Os sprites são as imagens e animações associadas aos objetos. O Editor
de Sprites é uma ferramenta de pixel art integrada — desenhe sprites
diretamente no PyGameMaker, sem necessidade de um editor de imagens
externo.

---

## Abrir o Editor de Sprites

1. Clique duas vezes num sprite existente na árvore de recursos, ou
2. Clique com o botão direito em **Sprites** > **Criar Sprite**

![O Editor de Sprites: ferramentas de desenho e tamanho do pincel à
esquerda, abaixo o seletor de origem e a opção Precise Collision, uma
paleta de cores, a área de desenho ao centro mostrando uma personagem em
pixel art com um zoom de 10x, e a tira de fotogramas em baixo (8
fotogramas, botão Play, adicionar/duplicar/eliminar fotograma)](images/sprite-editor.png)

---

## Ferramentas de Desenho

| Ferramenta | Atalho | O que faz |
|------|----------|---------------|
| **Lápis** | P | Desenhar pixels individuais |
| **Borracha** | E | Apagar pixels (transparência) |
| **Conta-gotas** | I | Recolher uma cor da área de desenho |
| **Preenchimento** | G | Preencher uma área conectada (balde de tinta) |
| **Linha** | L | Desenhar uma linha reta |
| **Retângulo** | R | Desenhar um retângulo (alterna **Preenchido** para sólido/contorno) |
| **Elipse** | O | Desenhar uma elipse (também respeita **Preenchido**) |
| **Seleção** | S | Seleção retangular — mover, copiar, cortar, colar ou eliminar os pixels selecionados |

**O tamanho do pincel** aplica-se ao Lápis, à Borracha e aos contornos
de linhas/formas. A paleta de cores contém um conjunto de cores de
trabalho mais a paleta rápida padrão de 12 cores; clique numa amostra
para escolher, ou use o Conta-gotas para recolher uma cor diretamente do
sprite.

---

## Operações na Área de Desenho

- **Espelhar H / Espelhar V** — inverte o fotograma atual horizontal ou verticalmente
- **Redimensionar** — abre uma caixa de diálogo com dois modos distintos:
  - **Escalar Imagem** — estica o conteúdo existente para um novo tamanho
  - **Redimensionar Tela** — mantém o conteúdo no seu tamanho original e adiciona/corta espaço em redor, ancorado a um canto, borda ou o centro à escolha
- **Grelha** — ativa/desativa uma sobreposição de grelha ao nível dos pixels (não afeta a imagem guardada)
- **Aumentar Zoom / Diminuir Zoom** — a área de desenho trabalha frequentemente a 10x ou mais, já que os sprites costumam ser pequenos (16×16 a 64×64 é comum)
- **Exportar PNG…** — guarda o fotograma atual como um ficheiro `.png` autónomo
- Clique com o botão direito na área de desenho para **Copiar / Cortar / Colar / Eliminar / Desselecionar / Selecionar Tudo** (atalhos padrão: Ctrl+C / Ctrl+X / Ctrl+V / Del / Esc)

---

## Fotogramas e Animação

Um sprite pode conter vários fotogramas, reproduzidos como animação
durante a execução do jogo. A tira de fotogramas na parte inferior do
editor:

| Controlo | Efeito |
|---------|--------|
| **+** | Adicionar um novo fotograma em branco |
| **D** | Duplicar o fotograma atual |
| **-** | Eliminar o fotograma atual |
| **Play** | Pré-visualizar a animação no editor à taxa de fotogramas do sprite |

Clique numa miniatura de fotograma para saltar para lá e desenhar especificamente nesse fotograma.

---

## Origem e Colisão

- **Origem** — o ponto que os objetos que usam este sprite consideram
  como a sua posição `(x, y)`. Predefinições: Superior-Esquerda,
  Superior-Centro, Centro, Centro-Inferior, Inferior-Esquerda,
  Inferior-Direita, ou **Personalizada** (X/Y exatos). A maioria das
  personagens de plataformas/vista superior usa **Centro-Inferior** para
  que os pés do sprite fiquem na posição Y do objeto.
- **Precise Collision** — quando ativada, as colisões contra este sprite
  testam os pixels não transparentes reais em vez da caixa delimitadora
  do sprite. Mais precisa para sprites de forma irregular, mais
  dispendiosa de calcular — deixe desativada para formas simples
  (paredes, moedas) e reserve-a para sprites onde uma colisão por caixa
  delimitadora pareceria visivelmente errada.

---

## Próximos Passos

- [[Editor_Objetos_pt|Editor de Objetos]] - Associar um sprite a um objeto de jogo
- [[Editor_Salas_pt|Editor de Salas]] - Colocar instâncias de objeto que usam o seu sprite
- [[Primeiro_Jogo_pt|Crie o Seu Primeiro Jogo]] - Um tutorial completo que começa a desenhar sprites
