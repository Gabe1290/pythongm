# Treasure

Uma perseguição de labirinto ao estilo Pac-Man: o **explorador**
vagueia por um labirinto murado coletando **pontos de tesouro**,
perseguido por **monstros** que escolhem uma nova direção a cada
cruzamento. Pegue uma **pílula de poder** (`pil`) e a mesa vira —
todo monstro fica **assustado** e pode ser comido por pontos de
bônus até o efeito passar. Este é um projeto pygm2 nativo importado
de `treasure.gmk` (GameMaker 8.x); o projeto em si é escrito/salvo no
formato JSON próprio do pygm2.

**Onde isso se encaixa:** `treasure` fica ao lado da família
`maze_*` — construído com GameObjects + ações integradas e o editor
visual de eventos — mas adiciona um **script no nível do projeto**
(`adapt_direction`, a IA do monstro nos cruzamentos) e um ciclo de
estados ao estilo GM de **"perseguição / power-up / fuga"** através
de seus objetos. Foi uma das duas amostras removidas na rc.12 por
bugs de importação GMK e **readicionada após o endurecimento do
importador** (16/07/2026); veja
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
e [`../../docs/treasure_testing_pass.md`](../../docs/treasure_testing_pass.md).

**Som e música:** 6 efeitos sonoros são incluídos (coleta, pílula de
poder, comer-monstro, morte, …). Uma faixa legada da era GM8
(`music`) está em um formato que o pygame não consegue carregar e é
omitida em tempo de execução — igual à música de fundo das outras
amostras de labirinto; o jogo não é afetado.

## Como jogar

- As **teclas de seta** movem o explorador através do labirinto; paredes bloqueiam o movimento.
- Colete cada **ponto de tesouro** para completar o nível (4 salas no total).
- Os **monstros** te perseguem; tocar um normalmente custa uma vida.
- Pegue uma **pílula de poder** e os monstros ficam **assustados**
  (seu sprite muda) por alguns segundos — toque então em um monstro
  assustado para **comê-lo** (+pontos; ele se teletransporta de
  volta ao seu início como um monstro normal). O efeito passa após
  um temporizador.

## A IA do monstro (script `adapt_direction`)

Cada monstro chama o script de projeto `adapt_direction` a partir de
seus eventos step/colisão. É Python real do pygm2 — em um possível
cruzamento considera aleatoriamente virar, verificando
`game.check_collision_at_position(...)` em busca de uma parede antes
de se comprometer, então os monstros vagam pelo labirinto em vez de
correr em linha reta. Abra o recurso **Scripts** para lê-lo; a ação
`execute_script` nos eventos do monstro mostra onde é chamado.

## Estrutura do projeto

| Arquivo | Propósito |
|---|---|
| `project.json` | Manifesto — configurações de janela/sala, recursos incorporados, o script `adapt_direction`, e a ordem das salas |
| `rooms/room0..3.json` | Os quatro níveis de labirinto (instâncias por sala) |
| `objects/*.json` | As 7 definições de objetos (fonte da verdade; mescladas sobre as cópias incorporadas ao carregar) |
| `sprites/` | 10 sprites PNG + metadados `.json` |
| `sounds/` | 6 efeitos sonoros |
| `backgrounds/` | 1 fundo |
| `CREDITS.txt` | Aviso de licenciamento de recursos |

## Objetos

| Objeto | Papel |
|---|---|
| `explorer` | Personagem do jogador; coleta tesouros, come monstros assustados, morre ao contato com os normais |
| `monster` | Perseguidor; vagueia via `adapt_direction`; se transforma em `scared` com uma pílula de poder |
| `scared` | Um monstro em seu estado de fuga; comestível; volta a `monster` após um temporizador |
| `pil` | Pílula de poder — assusta todo monstro ao ser coletada |
| `point` | Tesouro para coletar |
| `bonus` | Coleta extra |
| `wall` | Parede sólida estática do labirinto |

## Recursos

10 sprites, 6 sons, 1 fundo — todos importados de `treasure.gmk`.
Veja `CREDITS.txt` e
[`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md) para a procedência.

## Coisas para ajustar

- **Duração do susto** — o alarme da pílula de poder é `160` passos
  no evento `collision_with_pil` de `explorer`; aumente-o para uma
  fase de fuga mais longa.
- **Probabilidade de virada do monstro** — os testes
  `random.random() * 3 < 1` no script `adapt_direction` definem com
  que frequência os monstros viram em um cruzamento.
- **Valores de pontuação** — os pontos de tesouro e de comer-monstro
  são ações `set_score` (relativas) nos respectivos eventos de colisão.

## Status da exportação

Coberto pela suíte de smoke-tests sem interface gráfica
(`tools/smoke_run_samples.py`, que lista `treasure`) e a suíte de
regressão de importação (`tests/test_gmk_treasure_maze4_import.py` +
`tests/test_gmk_applies_to.py`). Verificado em um playtest manual
durante o endurecimento do importador de julho de 2026 (veja o
documento de teste). Exposto na aba Welcome como **"Treasure"**.

## Regeneração a partir do `.gmk` original

O arquivo irmão `../treasure.gmk` é a fonte GameMaker 8.x. Para regenerar:

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/treasure.gmk', '/tmp/treasure_reimport')"
```

Uma importação nova é fiel ao jogo original a partir do endurecimento
do importador de julho de 2026 (nenhuma correção manual aplicada a esta amostra).
