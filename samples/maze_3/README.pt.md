# Labirinto — Nível 3

Uma exploração de masmorra em cinco labirintos precedida por uma tela
de título — a maior das três amostras de labirinto (17 objetos / 6
salas, contra os 9 objetos / 3 salas de maze_2). Mantém o ciclo de
coletar-diamantes-depois-alcançar-o-objetivo de maze_2 e a porta
trancada bloqueada por diamantes, e adiciona três novas mecânicas que
aparecem progressivamente pelas salas: um quebra-cabeça de empurrar
blocos em buracos (room5), três arquétipos de monstros em patrulha
que matam ao contato (salas 3–5), e uma armadilha de bomba oculta que
detona um raio de explosão (room4). Diferente de `maze_1`/`maze_2`,
esta amostra **é** uma importação bruta do GameMaker 8.x — sua irmã
`samples/maze_3.gmk` está incluída no repositório (não existe um
arquivo `.gmk` para `maze_1`/`maze_2`), e o projeto pygm2 ao lado dela
é o resultado convertido.

**Onde isso se encaixa:** parte da família `maze_*` — GameObjects +
sprites mais uma **imagem de fundo** estática por sala (como
`maze_2`), sem tiles no nível da sala. Veja
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para como isso se compara a `plateforme_*` (adiciona fundos em tiles)
e `match3_*` (script puro, sem ações integradas).

**Som e música:** 8 arquivos de som, e — diferente do conjunto
incluído mas silencioso de `maze_2` — genuinamente conectados: 11
pontos de chamada `play_sound`/`play_music` em `sound_background`
(música), `sound_diamond`, `sound_door`, `sound_goal`, `sound_dead`,
`sound_explode`, `sound_hole`, e `sound_push`.

## Como jogar

- **Tela de título (`room_start`):** pressione **ESPAÇO** para começar.
- As **teclas de seta** movem o jogador uma célula de grade de 32px
  por vez (`test_alignment`/`snap_to_grid`, mesmo padrão de `maze_1`/`maze_2`).
- **Objetivo:** coletar diamantes (`obj_diamond`, +5 de pontuação
  cada) e alcançar o `obj_goal` de cada sala. As salas 2–4
  adicionalmente bloqueiam a saída atrás de uma `obj_door` trancada
  que se autodestrói somente quando cada diamante naquela sala tiver
  desaparecido (room3 tem 4 portas que abrem todas juntas). Room5
  substitui os diamantes por um quebra-cabeça de empurrar: ande
  contra um `obj_block` para deslizá-lo uma célula, ou empurre-o para
  um `obj_hole` para preencher o poço (ambos são destruídos).
- **Perigos:** três arquétipos de monstros patrulham as salas 3–5 e
  matam ao contato — `monster_all` ricocheteia em paredes em
  qualquer uma das 4 direções, `monster_lr`/`monster_ud` patrulham um
  único eixo e invertem ao bater em uma parede. Room4 também esconde
  uma placa `obj trigger` que, ao ser tocada, arma uma `obj_bomb`
  próxima transformando-a em `obj_explosion` — sua explosão de 16
  quadros destrói qualquer instância não sólida (incluindo o
  jogador) dentro de um raio de 64px.
- **Condição de derrota:** tocar em um monstro custa uma vida
  (`sound_dead` + `set_lives -1` + `restart_room`); chegar a 0 vidas
  mostra a tela de entrada de pontuação máxima e reinicia o jogo.
  Tocar no objetivo da última sala mostra em vez disso uma mensagem
  de parabéns, concede +100, e termina a partida da mesma forma.
- **Teclas de depuração** vivem em `controller_main`: **R** custa
  instantaneamente uma vida e reinicia a sala; **N**/**P** pulam
  diretamente para a próxima/anterior sala — úteis para testes, mas
  também um salto de nível no qual um jogador poderia tropeçar por acidente.

## Estrutura do projeto

| Arquivo | Propósito |
|---|---|
| `project.json` | Manifesto do projeto — configurações de janela/sala e cópias de recursos incorporadas. As cópias de objetos correspondem exatamente aos seus arquivos colaterais, mas **as cópias de salas estão obsoletas**: cada entrada de sala incorporada tem 0 instâncias e um marcador `_external_file` — os dados reais de instância vivem apenas em `rooms/*.json` |
| `rooms/room_start.json` | Tela de título — 1 instância (`controller_start`) |
| `rooms/room1.json` | Labirinto 1 — 134 instâncias (paredes, 4 diamantes, objetivo, jogador, controlador) |
| `rooms/room2.json` | Labirinto 2 — 96 instâncias (+20 diamantes, 1 porta trancada) |
| `rooms/room3.json` | Labirinto 3 — 105 instâncias (+16 diamantes, 4 portas trancadas, todos os 3 arquétipos de monstros, 6 monstros no total) |
| `rooms/room4.json` | Labirinto 4 — 95 instâncias (+14 diamantes, 1 porta, 4 `monster_lr`, 2 pares gatilho/bomba) |
| `rooms/room5.json` | Labirinto 5 — 99 instâncias (4 blocos empurráveis, 3 buracos, 2 objetivos, 2 `monster_lr` — sem diamantes ou porta) |
| `objects/*.json` | 17 definições de objetos — verificadas contra as cópias incorporadas de `project.json` e idênticas (nenhuma obsolescência). Nota: `objects/obj trigger.json` tem um espaço literal no nome do arquivo |
| `sprites/` | 16 sprites + metadados (veja Recursos) |
| `sounds/` | 8 arquivos de som, todos referenciados por pelo menos um objeto |
| `backgrounds/` | 2 fundos (`background_start.png` para a sala de título, `background_main.png` para os labirintos) |
| `CREDITS.txt` | Aviso de licenciamento de recursos para esta amostra |

## Objetos

**Jogador e controladores**

| Objeto | Papel | Eventos-chave |
|---|---|---|
| `obj_person` | Personagem controlado pelo jogador; movimento em grade | keyboard (up/down/left/right/nokey), collision_with_obj_block, collision_with_monster_all/_lr/_ud, collision_with_wall_corner |
| `controller_start` | Controlador de tela de título; define pontuação/vidas, inicia a música | create, keyboard (ESPAÇO) |
| `controller_main` | HUD dentro do labirinto + teclas de depuração; desenha pontuação/vidas, termina a partida em 0 vidas | keyboard (R trapaça-reinício), no_more_lives, draw, keyboard_press (N/P pulo de sala) |

**Paredes e tiles**

| Objeto | Papel | Eventos-chave |
|---|---|---|
| `wall_corner` | Parede sólida base; pai dos outros dois tipos de parede | (nenhum — colisor passivo) |
| `wall_horizontal` | Segmento de parede horizontal (herda `wall_corner`) | (nenhum) |
| `wall_vertical` | Segmento de parede vertical (herda `wall_corner`) | (nenhum) |

**Colecionáveis, portas, objetivos e quebra-cabeça de empurrar blocos (room5)**

| Objeto | Papel | Eventos-chave |
|---|---|---|
| `obj_diamond` | Colecionável; +5 de pontuação ao coletar | destroy, collision_with_obj_person |
| `obj_door` | Portão trancado; se autodestrói quando cada diamante da sala tiver desaparecido | step |
| `obj_goal` | Saída do nível; avança as salas ou termina o jogo na última sala | collision_with_obj_person |
| `obj_block` | Caixa empurrável; desliza uma célula quando se anda contra ela, ou cai em um buraco | collision_with_obj_person |
| `obj_hole` | Poço; se autodestrói junto com qualquer bloco empurrado para dentro | collision_with_obj_block |

**Monstros e armadilha de bomba (room4)**

| Objeto | Papel | Eventos-chave |
|---|---|---|
| `monster_all` | Ricocheteia em paredes em qualquer uma das 4 direções | create, collision_with_wall_corner |
| `monster_lr` | Patrulha esquerda-direita, inverte ao contato com parede | create, collision_with_wall_corner |
| `monster_ud` | Patrulha cima-baixo, inverte ao contato com parede | create, collision_with_wall_corner |
| `obj trigger` | Placa oculta; ao toque reproduz o som de explosão, transforma a `obj_bomb` pareada em `obj_explosion`, se autodestrói | collision_with_obj_person |
| `obj_bomb` | Marcador de posição inerte representando uma bomba armada até que um gatilho dispare | (nenhum) |
| `obj_explosion` | Explosão de 16 quadros; ao aparecer destrói instâncias não sólidas dentro de 64px, se autodestrói ao final da animação | create, animation_end |

## Recursos

16 sprites (majoritariamente 32×32 de um único quadro, precisos em
nível de pixel; `sprite_explosion` é uma tira de 1536×96 de 16
quadros sem bandeira precisa), 2 fundos, 8 sons — todos os 8 sons são
referenciados por pelo menos um objeto, diferente de `maze_2` onde
nenhum estava conectado. Licença/procedência para os recursos desta
amostra está **não documentada** — veja `CREDITS.txt` nesta pasta,
que aponta para o TODO "Remaining maze assets" em
`docs/ASSET_LICENSES.md`. Não assuma CC0 nem qualquer outra licença
para esses arquivos.

## Coisas para ajustar

- `sprite_lives` (16×16) é um recurso registrado que nunca é
  desenhado — a ação `draw_lives` de `controller_main` na verdade usa
  `sprite_person` em escala 0,7, deixando `sprite_lives` órfão (mesma
  categoria do `tiles.json` de `maze_2`).
- A explosão da armadilha de bomba (o evento `create` de
  `obj_explosion`) destrói o jogador via um simples
  `destroy_instance` em sua verificação de raio, contornando o
  caminho `sound_dead`/`set_lives`/`restart_room` que os monstros
  usam — pegar o jogador deixa a partida em um estado estranho em
  vez de uma morte/reinício limpo.
- A velocidade dos monstros é fixa em `32/6` px/passo em todos os
  três arquétipos enquanto o jogador se move a `4` — os monstros não
  são ajustados à grade como o jogador é, então seu movimento não
  permanece alinhado às células com o tempo.
- As teclas de depuração `R`/`N`/`P` em `controller_main` estão
  ativas no controlador distribuído (veja Como jogar) — valeria a
  pena condicioná-las a uma bandeira de depuração se esta amostra for
  polida mais adiante.

## Status da exportação

Coberto pela suíte de smoke-tests sem interface gráfica
(`tools/smoke_run_samples.py`, que lista `maze_3` e o executa por um
número fixo de quadros com entrada de teclado injetada); não
verificado individualmente para cada destino de exportação (Kivy/Web).
Exposto na aba Welcome do IDE como "Maze — Level 3"
(`widgets/welcome_tab.py`).
