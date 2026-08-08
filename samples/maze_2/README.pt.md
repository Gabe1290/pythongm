# Labirinto — Nível 2

Um jogo de labirinto em grade visto de cima com dois labirintos
jogáveis mais uma tela de título: colete doces por pontuação, depois
alcance a saída para avançar. Ele se constrói sobre o ciclo
labirinto/objetivo de sala única de `maze_1` com uma tela inicial, um
colecionável (doce com pontuação), e uma porta trancada que só abre
quando os doces da sala forem todos coletados. Este é um projeto
pygm2 nativo (sem arquivo `.gmk` irmão — seus recursos foram
originalmente trazidos via uma importação do GameMaker 8.x, conforme
`CREDITS.txt`, mas o projeto em si é escrito/salvo no formato JSON
próprio do pygm2).

**Onde isso se encaixa:** parte da família `maze_*` — GameObjects +
sprites, mais (diferente de `maze_1`) uma **imagem de fundo** estática
por sala (`background_main`), sem tiles no nível da sala. Veja
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para como isso se compara a `plateforme_*` (adiciona fundos em tiles)
e `match3_*` (script puro, sem ações integradas).

**Som e música:** 4 arquivos de som são incluídos
(`sound_background.mid`, `sound_diamond`/`door`/`goal.wav`) mas
**nenhum deles está realmente conectado** — nenhum objeto referencia
`play_sound`/`play_music` em lugar nenhum, então o jogo é silencioso
na prática apesar de carregar recursos de áudio. (Em contraste com
`maze_3`, onde o mesmo conjunto de sons é genuinamente reproduzido.)

## Como jogar

- **Tela de título (`room_start`):** pressione **ESPAÇO** para
  começar (a ação `keyboard_press` de `controller_start` chama `next_room`).
- As **teclas de seta** (cima/baixo/esquerda/direita) movem o jogador
  uma célula de grade (32px) por vez; o movimento é ajustado à grade
  via `test_alignment`/`snap_to_grid` (grade 32×32), mesmo padrão de `maze_1`.
- **Objetivo:** coletar os doces (`obj_diamond`, sprite
  `sprite_bonbon`) espalhados por cada labirinto — cada um vale +10
  de pontuação — depois alcançar o objetivo (`obj_goal`). Em `room2`,
  a saída é adicionalmente bloqueada por uma porta trancada
  (`obj_door`) que se autodestrói somente quando cada `obj_diamond`
  na sala tiver desaparecido.
- Tocar no objetivo avança para a próxima sala (+100 de pontuação) se
  existir uma; tocá-lo na última sala (`room2`) concede +100, abre a
  tela de entrada de pontuação máxima, e termina o jogo.
- **Sem condição de derrota:** nenhuma ação que afete vidas/saúde
  aparece em lugar nenhum nos objetos desta amostra —
  `starting_lives: 3` está definido nas configurações do projeto mas
  nunca é exibido ou decrementado.

## Estrutura do projeto

| Arquivo | Propósito |
|---|---|
| `project.json` | Manifesto do projeto — configurações de janela/sala e cópias incorporadas de todos os recursos |
| `rooms/room_start.json` | Tela de título — 1 instância (`controller_start`) |
| `rooms/room1.json` | Primeiro labirinto — 134 instâncias (paredes, jogador, objetivo, 4 doces, `controller_main`) |
| `rooms/room2.json` | Segundo labirinto — 112 instâncias (paredes, jogador, objetivo, 21 doces, porta trancada, `controller_main`) |
| `objects/*.json` | 9 definições de objetos — verificadas contra as cópias incorporadas de `project.json` e idênticas nesta amostra (nenhuma obsolescência encontrada) |
| `sprites/` | 7 sprites (`sprite_person`, `sprite_bonbon`, `sprite_door`, `sprite_goal`, `sprite_wall_corner`, `sprite_wall_horizontal`, `sprite_wall_vertical`) + metadados; `tiles.json` é um arquivo colateral órfão (não registrado em `project.json`, arquivo de imagem ausente — não usado) |
| `backgrounds/` | `background_start.png` (tela de título), `background_tiles.png` (piso do labirinto em tiles) |
| `sounds/` | 4 arquivos de som (veja Recursos abaixo) |
| `CREDITS.txt` | Aviso de licenciamento de recursos para esta amostra |

## Objetos

| Objeto | Papel | Eventos-chave |
|---|---|---|
| `obj_person` | Personagem controlado pelo jogador; movimento em grade | keyboard (down, right, up, left, nokey), collision_with_wall_corner |
| `wall_corner` | Parede sólida base do labirinto; objeto pai para os outros dois tipos de parede | (nenhum — apenas colisor passivo) |
| `wall_horizontal` | Segmento de parede horizontal sólida (herda de `wall_corner`) | (nenhum — apenas colisor passivo) |
| `wall_vertical` | Segmento de parede vertical sólida (herda de `wall_corner`) | (nenhum — apenas colisor passivo) |
| `obj_diamond` | Doce colecionável; adiciona pontuação ao coletar | destroy, collision_with_obj_person |
| `obj_door` | Portão de saída trancado (apenas room2); abre quando todos os doces desaparecem | step |
| `obj_goal` | Saída do nível; avança para a próxima sala ou termina o jogo | collision_with_obj_person |
| `controller_start` | Controlador de tela de título; espera o jogador começar | create, keyboard_press (ESPAÇO) |
| `controller_main` | Controlador de HUD dentro do labirinto; desenha a pontuação | draw |

## Recursos

7 sprites (32×32, um único quadro, colisão precisa em nível de pixel
exceto `sprite_goal` que não tem uma bandeira `precise` explícita), 2
fundos, 4 sons (`sound_background.mid`, `sound_diamond.wav`,
`sound_door.wav`, `sound_goal.wav`). Licença/procedência para todos
os recursos desta amostra está **não documentada** — veja
`CREDITS.txt` nesta pasta, que aponta para o TODO
"Remaining maze assets" em `docs/ASSET_LICENSES.md`. Não assuma CC0
nem qualquer outra licença para esses arquivos.

## Coisas para ajustar

- A velocidade de movimento do jogador é `4` (células de grade/passo)
  enquanto a parada por colisão com parede usa velocidade `8` —
  ambos são parâmetros de ação fixos por tecla em `obj_person`, igual a `maze_1`.
- Todos os 4 arquivos de som incluídos não estão referenciados —
  nenhum objeto atualmente chama `play_sound`; conectar um para
  coleta de doce / abertura de porta / objetivo alcançado seria um
  próximo passo natural.
- As salas são `480×480`–`480×512` a `room_speed: 30` — labirintos
  pequenos de tela única sem rolagem.
- `sprites/tiles.json` é um arquivo colateral residual não registrado
  como recurso do projeto (seu `sprites/tiles.png` não existe) —
  seguro remover ou ignorar.

## Status da exportação

Coberto pela suíte de smoke-tests sem interface gráfica
(`tools/smoke_run_samples.py`, que lista `maze_2` e o executa por
~180 quadros com entrada de teclado injetada); não verificado
individualmente para cada destino de exportação (Kivy/Web). Exposto
na aba Welcome do IDE como "Maze — Level 2" (`widgets/welcome_tab.py`).
