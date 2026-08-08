# Labirinto — Nível 1

Um jogo de labirinto em grade visto de cima: guie o sprite do jogador
através de um labirinto cercado de paredes para alcançar o tile
objetivo, que avança para a próxima sala. Este é um projeto pygm2
nativo (sem arquivo `.gmk` irmão — seus recursos foram originalmente
trazidos via uma importação do GameMaker 8.x, conforme CREDITS.txt,
mas o projeto em si é escrito/salvo no formato JSON próprio do pygm2).

**Onde isso se encaixa:** `maze_*` é a primeira das três famílias de
amostras em uma progressão aproximada de técnicas de criação (objetos/
sprites integrados → fundos em tiles adicionados de `plateforme_*` →
jogos de script puro `execute_code` de `match3_*`) — veja
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para o panorama completo. Esta amostra usa apenas GameObjects +
sprites, sem imagem de fundo e sem tiles no nível da sala.

**Som e música:** nenhum — nenhum arquivo de som é incluído com esta amostra.

## Como jogar

- As **teclas de seta** (cima/baixo/esquerda/direita) movem o jogador
  uma célula de grade (32px) por vez; o movimento é ajustado à grade
  via `test_alignment`/`snap_to_grid` (grade 32×32).
- Paredes (`obj_wall`) são sólidas — andar contra uma para o jogador
  e o reajusta à grade.
- **Objetivo:** alcançar o tile objetivo (`obj_goal`). Tocá-lo avança
  para a próxima sala se existir uma, ou reinicia o jogo se não houver nenhuma.
- **Atalhos de depuração:** pressionar `N` no objetivo pula para a
  próxima sala (se houver alguma); pressionar `P` pula para a sala
  anterior (se houver alguma) — mesma lógica de avanço/reinício que
  tocar no objetivo.
- Nenhum rastreamento de vidas/pontuação/saúde é usado nesta amostra
  (a saúde é reiniciada via `set_health` ao avançar de sala, mas nunca exibida).

## Estrutura do projeto

| Arquivo | Propósito |
|---|---|
| `project.json` | Manifesto do projeto — configurações de janela/sala e cópias incorporadas de todos os recursos |
| `rooms/room0.json` | Layout do labirinto para a sala 0 (131 instâncias: paredes, início do jogador, objetivo) |
| `rooms/room1.json` | Layout do labirinto para a sala 1 (130 instâncias) |
| `objects/obj_person.json` | Definição do objeto jogador (fonte da verdade; corresponde à cópia incorporada em `project.json`) |
| `objects/obj_goal.json` | Definição do objeto objetivo |
| `objects/obj_wall.json` | Definição do objeto parede |
| `sprites/` | `spr_person.png`, `spr_wall.png`, `spr_goal.png` + seus metadados `.json` |
| `CREDITS.txt` | Aviso de licenciamento de recursos para esta amostra |

Os arquivos colaterais `objects/*.json` foram verificados contra as
cópias incorporadas de `project.json` e são idênticos nesta amostra —
nenhuma obsolescência encontrada.

## Objetos

| Objeto | Papel | Eventos-chave |
|---|---|---|
| `obj_person` | Personagem controlado pelo jogador; movimento em grade | create-implícito via teclado, keyboard (down, right, up, left, nokey), collision_with_obj_wall |
| `obj_goal` | Saída do nível; avança/reinicia ao toque ou tecla de depuração | collision_with_obj_person, keyboard_press (p, n) |
| `obj_wall` | Parede sólida estática do labirinto, bloqueia o movimento | (nenhum — apenas colisor passivo) |

## Recursos

3 sprites (`spr_person`, `spr_wall`, `spr_goal`, cada um 32×32, um
único quadro, colisão precisa em nível de pixel), 0 sons. Licenças:
`spr_person.png` e `spr_wall.png` são CC0 (domínio público), obras do
autor do pygm2; a procedência de `spr_goal.png` ainda não está
documentada — veja `CREDITS.txt` nesta pasta e
`docs/ASSET_LICENSES.md` na raiz do repositório para o panorama completo.

## Coisas para ajustar

- A velocidade de movimento do jogador é `4` (células de grade/passo)
  enquanto a parada por colisão com parede usa velocidade `8` —
  ambos são parâmetros de ação fixos por tecla em `obj_person`.
- O tamanho da grade é `32` (corresponde aos sprites 32×32); alterá-lo
  precisa de edições correspondentes nas chamadas
  `snap_to_grid`/`test_alignment` e nos layouts das salas.
- As salas são `480×480` a `room_speed: 30` — labirintos pequenos de
  tela única sem rolagem.
- As teclas de depuração `N`/`P` em `obj_goal` permitem pular entre
  room0/room1 sem tocar no objetivo — útil para testes, mas fácil de
  acionar acidentalmente durante o jogo.

## Status da exportação

Coberto pela suíte de smoke-tests sem interface gráfica
(`tools/smoke_run_samples.py`, que lista `maze_1` e o executa por
~180 quadros com entrada de teclado injetada); não verificado
individualmente para cada destino de exportação (Kivy/Web). Exposto
na aba Welcome do IDE como "Maze — Level 1" (`widgets/welcome_tab.py`).
