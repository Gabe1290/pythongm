# Platform — Nível 2

Um plataforma de rolagem lateral importado do GameMaker 8.x
(`samples/plateforme_2.gmk`). Comparado a um primeiro nível mínimo,
este eleva a lista de objetos de um único jogador + um bloco para
quatro objetos (uma plataforma base mais variantes horizontal e
vertical que herdam dela) dispostos em uma sala de 126 instâncias
construída a partir de um conjunto de tiles automáticos com tema de
neve, em vez de alguns blocos colocados à mão.

**Onde isso se encaixa:** parte da família `plateforme_*`, e —
diferente do mínimo `plateforme_1` — é aqui que aparece o **fundo em
tiles**: 127 pedaços de tiles de fundo colocados individualmente (o
array `tiles` da sala) mais uma imagem de fundo em degradê
(`fond_degrade`), em camadas sob os *objetos* de tijolo sólido que
ainda cuidam da colisão. Este é o passo que `plateforme_*` adiciona
além de `maze_*`; veja
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para a progressão completa.

**Som e música:** nenhum — nenhum arquivo de som é incluído com esta amostra.

## Como jogar

- **Seta esquerda/direita** — move o pinguim (`obj_personnage`) esquerda/direita.
- **Seta cima** — pulo, mas apenas enquanto parado sobre uma
  plataforma sólida (verificado via um teste de colisão um pixel
  abaixo do jogador).
- **Objetivo** — não há um objeto objetivo/bandeira nesta amostra; é
  um layout de plataformas para explorar/atravessar sobre as
  plataformas `obj_brique*`.
- **Condição de derrota** — nenhuma está definida (sem perigos, sem
  objetos letais, sem verificação de morte por queda); a fileira
  inferior de tijolos da sala atua como chão.

## Estrutura do projeto

| Arquivo | Propósito |
| --- | --- |
| `project.json` | Manifesto do projeto — configurações de janela/sala, cópias de recursos incorporadas. |
| `rooms/niveau_01.json` | A única sala: 800×640, 126 instâncias + 127 tiles de fundo. Fonte da verdade para o conteúdo da sala (a lista `instances` incorporada de `project.json` está vazia). |
| `objects/*.json` | Arquivos colaterais por objeto dos 4 objetos; idênticos às cópias incorporadas em `project.json` até esta data. |
| `sprites/` | 5 recursos sprite (tiras de caminhada do jogador e blocos de plataforma sólidos). |
| `backgrounds/` | Conjunto de tiles de neve (`tuiles_neige.png`, usado como fonte de tiles automáticos) e um pequeno degradê vertical (`fond_degrade.png`) esticado como fundo de sala. |
| `CREDITS.txt` | Aviso de licenciamento para a arte de sprites/fundo (veja Recursos abaixo). |

## Objetos

| Objeto | Papel | Eventos-chave |
| --- | --- | --- |
| `obj_personnage` | Jogador (pinguim) — movimento, pulo, gravidade, detecção de chão | create, step, collision_with_obj_brique, keyboard (left, right, up), keyboard_release (LEFT, RIGHT) |
| `obj_brique` | Bloco de plataforma sólida base (32×32) | nenhum (sem eventos; apenas bandeira sólida) |
| `obj_brique_h` | Variante larga de plataforma sólida (32×16), filha de `obj_brique` | nenhum |
| `obj_brique_v` | Variante estreita de plataforma sólida (8×16), filha de `obj_brique`; definida mas não colocada em `niveau_01` | nenhum |

## Recursos

5 sprites (`spr_pingus_dr`/`spr_pingus_ga` tiras de caminhada de 8
quadros, mais três blocos marcadores de posição de cor sólida a
32×32 / 32×16 / 8×16) e 2 fundos; sem sons. A arte de sprites e fundos
é adaptada do projeto Pingus (GPL-3.0-or-later) — veja `CREDITS.txt`
para a atribuição completa e os termos de licença; este README não
reafirma nem estende essas declarações.

## Coisas para ajustar

- A velocidade horizontal do jogador é um `hspeed = 4` fixo nos eventos de teclado.
- O impulso de pulo é `vspeed = -10`; a gravidade de queda é `0,45`
  (aplicada apenas no ar), com um teto de velocidade terminal em `vspeed = 24`.
- O tamanho da sala é 800×640 a `room_speed = 30`.

## Status da exportação

Esta amostra está listada na lista `SAMPLES` de
`tools/smoke_run_samples.py`, então recebe uma passagem smoke sem
interface gráfica (o loop de jogo real executado por ~180 quadros com
entrada de teclado injetada) a cada execução daquele arnês. Nenhuma
verificação por destino de exportação específico (Kivy/HTML5) foi
feita especificamente para esta amostra. Está exposta na aba Welcome
do IDE como "Platform — Level 2" (`widgets/welcome_tab.py`).
