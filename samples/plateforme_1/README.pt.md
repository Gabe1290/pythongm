# Platform — Nível 1

Um plataforma de rolagem lateral mínimo importado do GameMaker 8.x
(`samples/plateforme_1.gmk`). A bola controlada pelo jogador
(`obj_balle`) escala uma única tela de plataformas de tijolo
(`obj_brique`) usando sondas `if_collision` ao estilo GameMaker para
se mover em passos de 4px/quadro e cair sob gravidade somente quando
não há nada sólido diretamente abaixo dela — um esquema de movimento
AABB escrito à mão em vez da física integrada do motor.

**Onde isso se encaixa:** parte da família `plateforme_*`, mas em sua
forma mínima — diferente de `plateforme_2`/`plateforme_3`, este nível
não tem imagem de fundo e **nenhum fundo em tiles** (o array `tiles`
da sala está vazio); é construído apenas com GameObjects + sprites,
igual a `maze_1`. Veja
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para como a família inteira se compara a `maze_*` e `match3_*`.

**Som e música:** nenhum — nenhum arquivo de som é incluído com esta amostra.

## Como jogar

- **Seta esquerda/direita** — move a bola 4px por pressão de tecla, bloqueada por tijolos sólidos.
- **Seta cima** — pulo (define `vspeed` para -10), apenas enquanto
  parada sobre um tijolo sólido.
- Não há um objeto objetivo explícito, moeda, ou saída neste nível —
  é um labirinto vertical de tijolos para escalar. Também não há um
  objeto monstro/perigo, então não há condição de derrota; é
  exploração livre da mecânica de colisão/gravidade.

## Estrutura do projeto

| Arquivo | Propósito |
|---|---|
| `project.json` | Manifesto do projeto — configurações de janela/sala, cópias de recursos incorporadas (veja nota abaixo). |
| `rooms/niveau_01.json` | A única sala: 800×640, 120 instâncias (majoritariamente paredes/plataformas `obj_brique` mais uma `obj_balle`). |
| `objects/obj_balle.json` | Lógica da bola do jogador (movimento, gravidade, pulo). |
| `objects/obj_brique.json` | Tijolo sólido estático, sem eventos. |
| `sprites/` | `spr_balle.png` (bola) e `spr_32x32_noir.png` (tijolo), cada um com um colateral `.json`. |

`objects/*.json` e `rooms/niveau_01.json` são os arquivos colaterais
por recurso atuais; seu conteúdo corresponde ao que está incorporado
em `project.json` para esta amostra (nenhuma divergência encontrada),
mas por convenção do repositório os arquivos colaterais são a fonte
da verdade se os dois algum dia discordarem.

## Objetos

| Objeto | Papel | Eventos-chave |
|---|---|---|
| `obj_balle` | Bola controlada pelo jogador; gravidade, movimento consciente de colisão, pulo | create (nenhum definido), step, collision_with_obj_brique, keyboard (left, right, up) |
| `obj_brique` | Tile de plataforma/parede sólida estática | *(nenhum — nenhum evento definido)* |

## Recursos

2 sprites (`spr_balle`, `spr_32x32_noir`), 0 sons. Ambos os sprites
são obras derivadas da arte do jogo Pingus, licenciadas sob
GPL-3.0-or-later — veja `CREDITS.txt` nesta pasta para o aviso
completo e os créditos dos artistas originais; não os trate como
cobertos pela licença MIT do IDE.

## Coisas para ajustar

- Evento step de `obj_balle`: a gravidade é `0,45` px/quadro², e
  vspeed é limitada a `24` — aumente ou diminua qualquer um dos dois
  para mudar o peso da queda e a velocidade terminal.
- O impulso do pulo é um `vspeed = -10` fixo (teclado "cima") —
  magnitude maior pula mais alto.
- O passo de movimento horizontal é `4` px por pressão de tecla
  (teclado "esquerda"/"direita") — passos maiores parecem mais ágeis
  mas podem atravessar frestas finas.
- A sala é 800×640 com `room_speed: 30`; o layout de tijolos em
  `rooms/niveau_01.json` pode ser rearranjado livremente já que
  `obj_brique` não tem lógica própria.

## Status da exportação

Esta amostra está listada na lista `SAMPLES` de
`tools/smoke_run_samples.py`, então está coberta pelo arnês de
smoke-tests sem interface gráfica (executa o loop de jogo real por
~180 quadros com entrada de teclado injetada). Não foi verificada
separadamente contra os destinos de exportação Kivy ou Web. Está
exposta na aba Welcome do IDE como **"Platform — Level 1"**
(`widgets/welcome_tab.py`).
