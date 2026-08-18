# 2.5 D — Nível 1

Uma visão em primeira pessoa ao estilo Doom/Wolfenstein do **mesmo
layout de labirinto que `maze_1`** — mesmas salas, mesmo objetivo,
mesmos caminhos solucionáveis. Onde `maze_1` mostra o labirinto de
cima com blocos de parede de célula inteira, esta amostra o
renderiza como uma projeção raycast com **paredes finas nas bordas**
(partições de 8px assentadas nos limites de célula, não blocos de
32px que preenchem uma célula) — corredores genuinamente
proporcionados ao estilo Wolfenstein, não apenas uma câmera em
primeira pessoa parafusada no antigo layout em blocos.
`rooms/room0.json` e `room1.json` foram regenerados a partir do
layout original de `maze_1` via uma conversão que preserva a topologia
(mesma conectividade/solucionabilidade, geometria de paredes
diferente), não redesenhados à mão. Veja
[`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) na
raiz do repositório para o plano de engenharia completo, incluindo a
seção "Complete rethink" sobre por que paredes de célula inteira não
funcionavam para espaço de giro real.

**Isto é 2,5D, não 3D** — a lógica de jogo é completamente inalterada
em relação a `maze_1` (mesma posição 2D `x`/`y`, mesma colisão de
parede sólida); apenas a *imagem* é falsificada para parecer
tridimensional. Não há visão vertical (sem inclinação), corredores
devem ser alinhados à grade, e não há verdadeira sobreposição
sala-sobre-sala. Essa é uma limitação deliberada e honesta, não uma
funcionalidade faltante — veja a nota pedagógica "why raycasting" do documento do plano.

**Status — totalmente texturizado (paredes, céu, chão, billboards) em
todos os três destinos: desktop (pygame), HTML5, e nativo (Kivy).**
As paredes amostram uma **textura de tijolo** (`spr_wall_texture`,
via `wall_texture`): cada coluna de tela amostra uma tira vertical na
posição de impacto do raio, escalada pela distância, com a face de
parede voltada para longe em metade do brilho como uma dica de
profundidade gratuita. O teto é um **céu ao estilo DOOM** (`spr_sky`,
via `sky_texture`) — um panorama que se move horizontalmente ao
girar (um giro completo de 360° o move uma vez) e que *não* recua
com a distância, então se lê como um horizonte infinitamente
distante. O chão é uma **textura de pedra projetada** (`spr_floor`,
via `floor_texture`) — um lançamento de chão de baixa resolução (o
cálculo por pixel em resolução completa era ~13× muito lento em
Python puro; `floor_cast_res` define a subamostragem, 4 ≈ 5ms) que se
repete por célula de grade e encontra as bases das paredes sem
costuras. `obj_goal` renderiza como um sprite billboard voltado para
a câmera (escalado pela distância, ocluído por paredes) — veja "O que
há de novo aqui". Para voltar ao visual plano, esvazie
`wall_texture`/`sky_texture`/`floor_texture` na ação `enable_raycast_view`.

## Como jogar

- **Cima/Baixo** movem para frente/trás na direção que você estiver
  olhando (movimento contínuo, não ajustado à grade — paredes ainda
  bloqueiam via a colisão normal de instância sólida do motor,
  inalterada em relação a `maze_1`).
- **Esquerda/Direita** giram no lugar (rotacionam `facing_angle`,
  independente do movimento — você pode girar enquanto parado).
- **Objetivo:** encontrar a meta. Tocá-la avança para a próxima sala
  se existir uma (mesma lógica `obj_goal` de `maze_1`, arquivo idêntico byte a byte).

## O que há de novo aqui, no motor

- `GameInstance.facing_angle` — direção de olhar persistente
  (convenção de ângulo GM: 0=direita, 90=cima, 180=esquerda,
  270=baixo), definida via a nova ação `set_facing_angle`. Diferente
  da propriedade `direction` existente (derivada de
  `hspeed`/`vspeed`, sempre 0 ao ficar parado), esta sobrevive ao
  ficar parado — necessária para controles FPS de "girar no lugar".
- `enable_raycast_view` — muda a sala atual para a câmera raycast
  (vinculada à instância chamadora, aqui o evento `create` de
  `obj_person`) ou volta à renderização normal de cima.
- O mapa de paredes é **derivado das instâncias sólidas existentes
  desta sala**, não de um formato de criação separado — mas desde a
  reformulação de paredes finas, é derivado como bordas reais
  (`GameRoom._build_raycast_walls`), não como ocupação grosseira por
  célula: a proporção de aspecto do sprite de uma instância sólida
  decide se é um segmento de parede horizontal ou vertical
  (aproximadamente quadrado recai em bloquear uma célula inteira,
  para retrocompatibilidade com conteúdo sem paredes finas). Isso é o
  que faz a espessura de 8px de `obj_wall_h`/`obj_wall_v`
  realmente importar tanto para renderização quanto para espaço de
  giro, não apenas visualmente — veja a seção "Complete rethink" do documento do plano.
- **Sprites billboard.** Qualquer instância visível, não sólida, com
  um sprite (aqui, `obj_goal`) desenha como um sprite 2D voltado para
  a câmera na visão raycast, escalado pela distância e centralizado
  verticalmente no horizonte como uma tira de parede. A oclusão é
  recorte real por coluna contra as distâncias de parede já
  calculadas para a passagem de paredes daquele quadro, então uma
  meta atrás de uma parede fica corretamente oculta em vez de
  transparecer. Este é um primeiro corte da Fase 6 do documento do
  plano (paredes só desenham instâncias sólidas; billboards só
  desenham as não sólidas, então nada é desenhado duas vezes) — sem
  mistura de transparência parcial, sem rotação para corresponder à
  orientação própria do sprite, apenas o escalonamento e recorte
  plano que um motor ao estilo Wolfenstein usava para itens e inimigos.

## Estrutura do projeto

| Arquivo | Propósito |
|---|---|
| `project.json` | Manifesto do projeto |
| `rooms/room0.json`, `rooms/room1.json` | Mesma *topologia* de labirinto que `maze_1`, regenerada com paredes finas nas bordas (veja o algoritmo de conversão do documento do plano) |
| `objects/obj_person.json` | Jogador/câmera — `create` ativa a visão raycast, eventos `keyboard` conduzem girar + frente/trás, registra `collision_with_obj_wall_h`/`_v` |
| `objects/obj_goal.json` | Objeto objetivo — idêntico byte a byte ao de `maze_1` |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segmentos de parede finos (32×8 e 8×32) — substituem o único `obj_wall` de bloco inteiro de `maze_1` |
| `sprites/` | `spr_person`, `spr_goal` (de `maze_1`) mais os próprios `spr_wall_h`/`spr_wall_v` desta amostra (marcadores de posição finos de cor sólida — nunca renderizados no modo primeira pessoa, apenas suas dimensões importam para colisão/raycasting) |

## Coisas para ajustar

- A taxa de giro é `3`°/quadro (`room_speed: 30` → 90°/seg) e a
  velocidade de movimento é `3` px/quadro, ambas fixas nos eventos
  `keyboard` de `obj_person`.
- FOV `66`°, `render_distance` `20` células, `cell_size` `32` — todos
  parâmetros de `enable_raycast_view` no evento `create` de `obj_person`.
- As cores de parede/chão/teto também são parâmetros de
  `enable_raycast_view` — o fallback plano quando a textura
  correspondente está vazia.
- A espessura de parede é `8`px, fixa na conversão que gerou
  `rooms/*.json` (não um parâmetro em tempo de execução) — regenere
  as salas para alterá-la.
- `spr_person` é **16×16** com uma caixa de colisão
  `(4,4)-(12,12)` — o jogador foi reduzido pela metade do antigo
  32×32 (e recentrado em sua célula inicial, então a câmera ainda se
  senta no centro da célula) porque o jogador em tamanho completo
  fazia os corredores de 1 célula parecerem apertados; uma pegada
  menor dá muito mais espaço para se mover. A **textura de tijolo**
  da parede foi similarmente refinada (tijolos em meia escala) para
  que as paredes pareçam mais distantes — ambos os ajustes trocam
  "colado no rosto" por uma sensação de espaço mais amplo.

## Status da exportação

A visão em primeira pessoa **completa** agora renderiza nos **três
destinos** — desktop (pygame), **HTML5**
(`export/HTML5/templates/engine.js`), e **nativo/Kivy**
(`export/Kivy/kivy_exporter.py`) — com controles de olhar por ângulo
de orientação, paredes texturizadas e planas, o céu que se move, o
lançamento de chão texturizado de baixa resolução, e sprites
billboard com recorte de oclusão. Os três renderizadores não
compartilham código (três cópias escritas à mão), então seu núcleo
DDA é travado por `tests/test_raycast_export_parity.py` (igualdade
numérica exata desktop↔Kivy sobre uma matriz de 260 raios; paridade
estrutural HTML5, já que não há motor JS em CI).

O lançamento de chão usa a mesma abordagem calcular-em-baixa-
resolução-depois-escalar em cada destino (`floor_cast_res`, padrão
4); medições de tempo em hardware real confirmaram que cabe no
orçamento (navegador ~0,4 ms a res=2; Kivy/AMD 840M ~5 ms a res=4).
Um projeto ainda pode esvaziar `floor_texture` para um chão plano de `floor_color`.

Disponível a partir da aba Welcome do IDE — escolha **"2.5 D —
Level 1"** no menu suspenso *Choose a sample* (abrir uma amostra a
copia para seus Documentos, então o original incluído permanece intacto).
