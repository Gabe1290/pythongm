# Labirinto — Nível 4

A maior amostra de labirinto: **21 salas** de quebra-cabeças de
labirinto em grade com **tiles de esteira transportadora**, três
tipos de **monstro**, **bombas/explosões** que explodem paredes, um
**anel de poder** que assusta os monstros, e colecionáveis (diamantes,
anéis, corações). Um projeto pygm2 nativo importado de `maze_4.gmk`
(GameMaker 8.x), escrito/salvo no formato JSON próprio do pygm2.

**Onde isso se encaixa:** o quarto nível `maze_*` e o mais rico
mecanicamente — sobrepõe movimento por esteira, múltiplos tipos de
inimigos, um ciclo de power-up de assustar/comer, e uma bomba que
destrói paredes sobre o movimento básico em grade de `maze_1..3`. Foi
removido na rc.12 por bugs de importação GMK e **readicionado após o
endurecimento do importador** (16/07/2026); veja
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
e [`../../docs/maze_4_testing_pass.md`](../../docs/maze_4_testing_pass.md).

**Som e música:** 10 efeitos sonoros são incluídos. Uma faixa legada
da era GM8 (`sound_background`) está em um formato que o pygame não
consegue carregar e é omitida em tempo de execução (igual a
maze_2/maze_3); a jogabilidade não é afetada.

## Como jogar

- As **teclas de seta** movem o jogador uma célula de grade por vez; paredes bloqueiam o movimento.
- **Tiles de esteira transportadora** (setas cima/baixo/esquerda/
  direita no chão) carregam automaticamente o jogador em sua direção
  enquanto ele está sobre elas.
- **Monstros** vêm em três tipos (`monster_all` vagueia livremente;
  `monster_ud` patrulha verticalmente; `monster_lr` horizontalmente)
  — tocar um custa uma vida e reinicia a sala.
- Pegue um **anel** e todo monstro fica **assustado** (o sprite muda,
  eles congelam) por ~10 segundos — toque um então para comê-lo por
  pontos; eles voltam ao normal quando o temporizador acaba.
- **Bombas** explodem em uma onda que **destrói as paredes ao redor**
  — usadas para abrir seções de outra forma seladas.
- Colete **diamantes/anéis/corações**; alcance o **objetivo** para
  avançar. O HUD (pontuação + vidas) é desenhado ao longo da parte
  inferior por `controller_main`.

## Uma nota sobre o patch manual (documentação honesta)

O movimento do pygm2 *desliza até o contato* com uma parede, enquanto
o GameMaker 8 *reverte* um movimento bloqueado para a posição prévia
ao movimento — o comportamento do GM mantinha o jogador ajustado à
grade de graça. Sem isso, pressionar contra uma parede alinhada
deixava o jogador a alguns pixels da grade de 32, e as verificações
de movimento em grade/esteira então travavam. Então `obj_person`
carrega um **patch manual de jogabilidade** deliberado:
`snap_to_grid(32)` em seus eventos de colisão
`wall_corner`/`wall_horizontal`/`wall_vertical`. Isso espelha o
mesmo patch distribuído em `maze_1` e é uma correção, não uma
mudança de fidelidade — uma importação nova do `.gmk` não a incluirá (veja abaixo).

## Estrutura do projeto

| Arquivo | Propósito |
|---|---|
| `project.json` | Manifesto — configurações de janela/sala, recursos incorporados, e ordem das salas |
| `rooms/*.json` | 21 salas; ordem de jogo `room_start` depois em ordem decrescente (`room14`, `room13`, …) — a ordem própria do jogo original, importada fielmente |
| `objects/*.json` | 24 definições de objetos (fonte da verdade; mescladas sobre as cópias incorporadas ao carregar) |
| `sprites/` | 24 sprites PNG + metadados `.json` |
| `sounds/` | 10 efeitos sonoros |
| `backgrounds/` | 2 fundos |
| `CREDITS.txt` | Aviso de licenciamento de recursos |

## Objetos (24)

Jogador/HUD: `obj_person`, `controller_main` (desenha
pontuação+vidas), `controller_start`.
Paredes: `wall_horizontal`, `wall_vertical`, `wall_corner`, `block`.
Inimigos: `monster_all`, `monster_ud`, `monster_lr`.
Power-ups / itens: `ring` (assusta), `bomb` + `explosion` (destroem
paredes), `obj_diamond`, `heart`, `bonus`, `obj_door`, `obj_goal`,
`trigger`, `hole`.
Tiles de esteira transportadora: `move_up`, `move_down`, `move_left`, `move_right`.

## Recursos

24 sprites, 10 sons, 2 fundos, 1 fonte — todos importados de
`maze_4.gmk`. Veja `CREDITS.txt` e
[`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md) para a procedência.

## Coisas para ajustar

- **Velocidade de esteira/jogador** — as esteiras se movem na
  velocidade `8`; o movimento em grade pelo teclado a `4` (parâmetros
  por ação em `obj_person`).
- **Duração do susto** — o `set_alarm` do anel é `300` passos em `monster_all`.
- **Ordem das salas** — as salas tocam na ordem das chaves do
  dicionário de salas de `project.json`; reordene-as no IDE (arraste
  na árvore de recursos) e o Test Game seguirá.

## Status da exportação

Coberto pela suíte de smoke-tests sem interface gráfica
(`tools/smoke_run_samples.py`, que lista `maze_4`) e a suíte de
regressão de importação (`tests/test_gmk_treasure_maze4_import.py`).
Verificado em um playtest manual durante o endurecimento do
importador de julho de 2026 (veja o documento de teste). Exposto na
aba Welcome como **"Maze — Level 4"**.

## Regeneração a partir do `.gmk` original

O arquivo irmão `../maze_4.gmk` é a fonte GameMaker 8.x:

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/maze_4.gmk', '/tmp/maze_4_reimport')"
```

Uma importação nova é fiel ao jogo original, **menos** o patch manual
`snap_to_grid` de paredes descrito acima — reaplique-o (adicione
`snap_to_grid` com grid_size 32 aos três eventos de colisão de parede
de `obj_person`) após regenerar.
