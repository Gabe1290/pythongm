# Raycast — Nível 4

O quarto nível em primeira pessoa ao estilo Doom/Wolfenstein, e o
primeiro construído **ao redor de uma barra de status permanente
embaixo** — a estética DOOM em vez das sobreposições de canto de
`raycast_3`. A visão 3D é deliberadamente **mais curta** (letterbox)
para abrir espaço para a barra; isso é parte do visual, não um erro.

Onde `raycast_3` provou um HUD de canto e a saúde como recurso,
`raycast_4` mostra as duas funcionalidades do motor construídas para
uma barra DOOM:

- **`viewport_height`** em `enable_raycast_view` encolhe a visão em
  primeira pessoa para o topo da janela e reserva a faixa abaixo dela.
- **`draw_doom_hud`** preenche essa faixa: uma barra de saúde +
  número, um **retrato de rosto reativo à saúde**, pontuação, vidas,
  e um contador de chaves — tudo a partir de comandos de desenho
  comuns, então renderiza igualmente em desktop, HTML5 e nativo (Kivy).

Veja [`docs/RAYCAST_DOOM_HUD_PLAN.md`](../../docs/RAYCAST_DOOM_HUD_PLAN.md)
para a engenharia, e [`raycast_3`](../raycast_3/README.md) para a
alternativa de HUD de canto que este nível deliberadamente não readapta.

**Sensação de interior.** Duas coisas fazem isso se ler como um
corredor dentro de um prédio em vez de um labirinto ao ar livre:
projeta um **teto de pedra** (`spr_ceiling`) em vez do céu que se
move que as outras amostras raycast usam — definido via
`ceiling_texture` com `sky_texture` deixado vazio — e as paredes
renderizam **mais altas**. Essa altura de parede
(`RAYCAST_WALL_HEIGHT`, 1,5× um cubo) é um padrão global do motor,
então todo jogo raycast obtém as paredes mais altas; o teto é a
escolha própria desta amostra.

**Som e música:** nenhum — nenhum arquivo de som é incluído com esta amostra.

## Como jogar

- **Cima/Baixo** — movem para frente/trás na direção que você estiver olhando.
- **Esquerda/Direita** — giram no lugar.
- **Colete as chaves** — cada uma marca 25 pontos e avança em um o
  contador **KEYS** na barra. Há três.
- **Evite os monstros** — tocar um custa **25 de saúde** (com uma
  breve janela de invulnerabilidade depois). Observe o **rosto**: ele
  faz uma careta enquanto sua saúde cai, mesmo antes de você ter lido o número.
- **Se a saúde acabar** → você perde uma vida, a saúde se enche, a
  sala reinicia. **Se as vidas acabarem** → o jogo reinicia.
- **Alcance a saída** uma vez que tiver encontrado **as três chaves**.
  Tocá-la cedo só te diz que o portão está trancado.
- **Pressione `M`** para exibir um **minimapa** das paredes (desligado
  por padrão). É desenhado dentro da visão 3D, acima da barra de
  status, e alterna ligado/desligado — o mesmo mapa sob demanda que
  `raycast_3` usa, aqui mantido longe da barra.

## A barra de status (`draw_doom_hud`)

`obj_person` a desenha a cada quadro, em espaço de tela, sobre a
visão 3D finalizada. Da esquerda para a direita:

| Zona | Mostra |
|---|---|
| Esquerda | rótulo `HEALTH` + uma barra de saúde proporcional + o número |
| Centro | o **retrato de rosto**, uma tira de 4 quadros que reage à saúde |
| Direita | `SCORE` sobre `LIVES` |
| Extremo direito | o contador `KEYS` |

O rosto é o ponto de toda a amostra. Seu quadro é escolhido por um
mapa de segmentos uniformes sobre a saúde — quadro 0 (calmo) perto de
cheio, o último quadro (morrendo) perto de vazio — então o retrato
te diz como você está indo antes que o número o faça, exatamente
como a barra própria do DOOM.

**`obj_person` é tanto a câmera *quanto* o desenhista do HUD.** Isso
é deliberado: o contador de chaves então é apenas uma variável de
instância em `obj_person` (`keys`), então a expressão de objetivo de
`draw_doom_hud` lê o mesmo valor identicamente nos três destinos de
exportação. Um objeto de câmera invisível separado (como em
`raycast_3`) não poderia carregar uma variável que o HUD visível precisa.

## O letterbox (`viewport_height`)

`enable_raycast_view` roda no `create` de `obj_person` com
`viewport_height: 400` em uma janela 640×480 — então a visão 3D é
400px de altura e os **80px** inferiores estão reservados,
preenchidos de preto pelo motor, e pintados por cima pela barra.
Defina `viewport_height` como `0` (o padrão) e a visão preenche toda
a janela sem faixa reservada, exatamente como fazem `raycast_1`–`3`.

O horizonte se move para cima com a visão mais curta, e
paredes/céu/chão escalam todos de acordo com ele — é um verdadeiro
letterbox, não uma barra colocada sobre uma visão de altura completa.
(No Kivy, que é y-para-cima, a faixa reservada fica embaixo na
janela de qualquer forma; o motor trata a inversão.)

## Estrutura do projeto

| Arquivo | Propósito |
|---|---|
| `project.json` | Manifesto — janela 640×480, uma sala |
| `rooms/room0.json` | O labirinto: 15×15 células, 3 chaves, 4 monstros, uma saída bloqueada por chaves |
| `objects/obj_person.json` | Jogador + câmera + barra de status — movimento, saúde, chaves, `draw_doom_hud` |
| `objects/obj_key.json` | Uma chave (passiva; a colisão de `obj_person` a manuseia) |
| `objects/obj_monster.json` | Inimigo billboard em patrulha |
| `objects/obj_goal.json` | Saída bloqueada por chaves (abre quando nenhuma `obj_key` restar) |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segmentos de parede finos |
| `sprites/` | Arte de parede/chão/pessoa/monstro reutilizada, um novo **`spr_ceiling`** (teto de pedra de interior, substituindo o céu), mais novos `spr_face` (retrato de 4 quadros), `spr_key` e `spr_gate` (a saída trancada) |

## O labirinto é gerado

`tools/gen_raycast_4_maze.py` constrói a sala **delegando ao gerador
confirmado de `raycast_3`** — mesmo labirinto backtracker recursivo,
mesmas paredes finas nas bordas, mesma disciplina de semente escolhida
(o spawn abre para o leste, cada célula alcançável). Difere apenas no
que é espalhado (chaves, não gemas/kits médicos) e em que
`obj_person` é a câmera. Executá-lo novamente reproduz a sala
distribuída; um teste a fixa.

## Coisas para ajustar

- **Altura da barra vs. viewport:** a `height` em `draw_doom_hud`
  (80) deveria corresponder à faixa reservada
  (`640×480 − viewport_height 400 = 80`). Mude uma, mude a outra.
- **Reatividade do rosto:** `face_frames` (4) segmenta a saúde sobre
  a tira. Uma tira de 5 quadros com `face_frames: 5` dá expressões mais finas.
- **Dano/chaves:** o `-25` no evento `collision_with_obj_monster` de
  `obj_person`; as 3 chaves e 4 monstros nos `counts` do gerador.
- **Cores e rótulos da barra:** os parâmetros de `draw_doom_hud` no
  evento draw de `obj_person`.

## Status da exportação

Roda em todos os três destinos. Coberto pela suíte smoke sem
interface gráfica (`tools/smoke_run_samples.py`) e
`tests/test_raycast_4_sample.py`, que conduz o loop real: a barra
renderiza todas as suas partes sobre a visão encolhida, alinhada
embaixo à faixa reservada; o **quadro do rosto segue a saúde**
(100/75/50/25 → 0/1/2/3); uma coleta de chave conta, pontua e é destruída.

As exportações Kivy e HTML5 foram verificadas para carregar tudo — o
`viewport_height` do letterbox na configuração de câmera,
`draw_doom_hud`, o rosto multi-quadro — mas o playtest **visual** por
destino é o último passo e vale a pena fazer com os próprios olhos:
esta é a primeira amostra raycast cuja *forma de visão* muda, então a
que mais merece ser observada renderizando em um navegador e no Android.
