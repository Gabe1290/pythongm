# 2.5 D — Nível 2

Um segundo nível em primeira pessoa ao estilo Doom/Wolfenstein,
construído sobre o mesmo **motor raycast 2,5D** de
[`raycast_1`](../raycast_1/README.md) — que está completo em todos os
três destinos de exportação (desktop, HTML5, nativo/Kivy): paredes
texturizadas, um céu que se move, lançamento de chão texturizado de
baixa resolução, e sprites billboard voltados para a câmera.

Onde `raycast_1` é um pequeno corredor derivado de maze_1 que ensina
*a visão em primeira pessoa em si*, `raycast_2` é um **labirinto
maior com coisas acontecendo na visão 3D** — gemas colecionáveis, um
inimigo em patrulha, e uma saída bloqueada por gemas. Veja
[`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) para o
motor e [`docs/RAYCAST_2_SAMPLE_PLAN.md`](../../docs/RAYCAST_2_SAMPLE_PLAN.md)
para o design e o plano de unidades desta amostra.

Um jogo completo de dois níveis: navegue cada labirinto em primeira
pessoa, colete cada gema desviando de monstros em patrulha, e
alcance a saída bloqueada por gemas — a primeira sala (tijolo quente)
leva a uma segunda sala (caverna de cristal fria), e completá-la
vence. Disponível na aba Welcome do IDE (*"2.5 D — Level 2"*) e
exporta para os três destinos (desktop, HTML5, nativo/Kivy).

## Como jogar

- **Cima/Baixo** — movem para frente/trás na direção que você estiver
  olhando (contínuo, não ajustado à grade; paredes bloqueiam via a
  colisão normal de instância sólida do motor).
- **Esquerda/Direita** — giram no lugar (rotacionam `facing_angle`,
  independente do movimento — você pode girar enquanto parado).
- **Colete as gemas** espalhadas pelo labirinto — cada uma adiciona
  10 à pontuação, mostrada no **HUD na tela** (canto superior
  esquerdo), desenhado sobre a visão em primeira pessoa por `obj_hud`.
- **Evite os monstros** — eles patrulham os corredores (ricocheteando
  em paredes) e desenham como billboards voltados para a câmera.
  Tocar um custa uma vida e reinicia a sala; você começa com 3 vidas,
  mostradas no canto superior direito do HUD. Se acabarem, o jogo reinicia.
- **Objetivo:** colete **todas** as gemas em uma sala, depois alcance
  seu objetivo. Alcançá-lo cedo demais só pede que você
  *"Collect all the gems before you leave!"* — ele só abre quando
  cada gema tiver desaparecido. O objetivo da primeira sala (tijolo
  quente) leva a uma segunda sala fria de **caverna de cristal**;
  completá-la vence o jogo.

## Geometria do nível

Tanto `rooms/room0.json` quanto `rooms/room1.json` são labirintos de
15×15 células (480×480) gerados por um backtracker recursivo (um
labirinto *perfeito* — cada célula alcançável, garantidamente
solucionável — com algumas paredes extras derrubadas para loops e
linhas de visão mais longas), depois convertidos ao modelo de
**parede fina na borda** de `raycast_1`: cada fronteira entre uma
célula aberta e uma parede se torna um segmento `obj_wall_h` (32×8)
ou `obj_wall_v` (8×32) de 8px na linha da grade, então os corredores
se leem como genuinamente proporcionados ao estilo Wolfenstein em vez
de em blocos. Cada sala usa uma semente de labirinto diferente,
então os dois níveis são layouts distintos.

## Tematização por sala

As texturas da visão raycast são **por sala**: `enable_raycast_view`
vive em um pequeno objeto controlador de câmera invisível colocado em
cada sala — `obj_cam0` (tijolo quente:
`spr_wall_texture`/`spr_sky`/`spr_floor`) em room0, `obj_cam1`
(caverna de cristal fria:
`spr_wall_ice`/`spr_sky_ice`/`spr_floor_ice`, variantes tingidas de
azul) em room1. Cada controlador nomeia `obj_person` como câmera via
o parâmetro `camera_object` da ação, então o *jogador* continua
sendo a câmera mesmo que seja o *controlador* que dispara a ação.
Por isso a segunda sala parece diferente — a configuração é limitada
ao controlador da sala, não incorporada no jogador.

## Estrutura do projeto

| Arquivo | Propósito |
|---|---|
| `project.json` | Manifesto do projeto |
| `rooms/room0.json`, `rooms/room1.json` | Os dois labirintos gerados de parede fina na borda (dados de instância autoritativos) |
| `objects/obj_person.json` | Jogador/câmera — eventos `keyboard` conduzem girar + frente/trás; `game_start` inicializa pontuação/vidas; registra os manipuladores `collision_with_obj_wall_h`/`_v` que controlam o bloqueio de parede, e `collision_with_obj_monster` (perder uma vida + reiniciar) |
| `objects/obj_cam0.json`, `obj_cam1.json` | Controladores de câmera por sala que ativam `enable_raycast_view` com o tema de textura daquela sala |
| `objects/obj_gem.json` | Colecionável — a colisão o destrói; seu evento `destroy` adiciona 10 à pontuação |
| `objects/obj_monster.json` | Inimigo billboard em patrulha — se move, ricocheteia em paredes |
| `objects/obj_goal.json`, `obj_goal_final.json` | O objetivo de room0 (→ próxima sala) e de room1 (→ vitória); ambos bloqueados por gemas |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segmentos de parede finos (32×8 e 8×32) |
| `objects/obj_hud.json` | HUD em espaço de tela desenhado sobre a visão em primeira pessoa — `draw_score` + `draw_lives`. Note que é **visible: true**: o GameMaker não executa o evento draw de uma instância invisível, por isso o HUD não pode simplesmente viver em `obj_cam0`/`obj_cam1` (que são invisíveis) |
| `sprites/` | Reutilizados de `raycast_1` (pessoa/objetivo/parede/céu/chão + marcadores de parede), mais `spr_gem` (gema de match3), `spr_monster` (monstro de maze_3), e o conjunto de texturas `*_ice` tingido de azul de room1 |

## Motor reutilizado, arte reutilizada

`raycast_2` compartilha os objetos e sprites de `raycast_1` — o
propósito desta amostra é *criação de nível e jogabilidade sobre o
motor finalizado*, não novo código de renderização. A arte de gema e
monstro (Unidades 2–3) são os únicos recursos novos, e nenhuma da
lógica de jogo depende da arte específica, então são reskineáveis.
