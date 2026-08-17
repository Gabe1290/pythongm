# 2.5 D — Nível 3

O terceiro nível em primeira pessoa ao estilo Doom/Wolfenstein,
construído sobre o mesmo **motor raycast 2,5D** de
[`raycast_1`](../raycast_1/README.md) e
[`raycast_2`](../raycast_2/README.md) — completo em todos os três
destinos de exportação (desktop, HTML5, nativo/Kivy): paredes
texturizadas, um céu que se move, lançamento de chão texturizado de
baixa resolução, e sprites billboard voltados para a câmera.

Onde `raycast_1` ensina *a visão em primeira pessoa em si* e
`raycast_2` adiciona *coisas acontecendo na visão* (gemas, um inimigo
em patrulha, uma saída bloqueada), `raycast_3` é sobre **estado que
você pode ver enquanto joga**: os monstros custam **saúde** em vez de
uma vida diretamente, kits médicos a devolvem, e um **display de
informações** composto sobre a visão 3D mostra sempre pontuação,
vidas e uma barra de saúde.

Esse HUD é a razão pela qual esta amostra existe. Até 20/07/2026 o
motor desenhava a visão em primeira pessoa e depois parava, então a
pontuação e vidas de um jogo raycast só apareciam no título da janela
de desktop — invisíveis nas exportações HTML5 e Kivy. Veja
[`docs/RAYCAST_HUD_PLAN.md`](../../docs/RAYCAST_HUD_PLAN.md) para
esse trabalho e [`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md)
para o motor.

Um jogo completo de dois níveis: atravesse cada labirinto em primeira
pessoa, colete cada gema enquanto sobrevive aos monstros, e alcance a
saída bloqueada por gemas — a primeira sala (tijolo quente) leva a
uma segunda sala (caverna de cristal fria), e completá-la vence.
Disponível na aba Welcome do IDE (*"2.5 D — Level 3"*).

**Som e música:** nenhum — nenhum arquivo de som é incluído com esta amostra.

## Como jogar

- **Cima/Baixo** — movem para frente/trás na direção que você estiver
  olhando (contínuo, não ajustado à grade; paredes bloqueiam).
- **Esquerda/Direita** — giram no lugar (rotacionam `facing_angle`,
  independente do movimento — você pode girar enquanto parado).
- **Colete as gemas** — cada uma adiciona 10 à pontuação, mostrada no
  canto superior esquerdo.
- **Evite os monstros** — tocar um custa **25 de saúde**, não uma
  vida. Após um golpe você tem uma breve janela de invulnerabilidade
  (45 passos) para que um monstro que atravesse você não possa
  esvaziar toda a barra de uma vez.
- **Pegue os kits médicos** — as caixas com cruz vermelha restauram
  **40 de saúde**, limitado ao máximo.
- **Se a saúde acabar** você perde uma vida, a barra se enche e a
  sala reinicia. Se as **vidas** acabarem, o jogo reinicia.
- **Objetivo** — colete *todas* as gemas em uma sala, depois alcance
  sua saída. Alcançá-la cedo só pede que você colete o resto.

## O HUD

`obj_hud` o desenha, em **espaço de tela**, sobre o quadro 3D finalizado:

| Elemento | Canto | Ação |
|---|---|---|
| Pontuação | superior esquerdo | `draw_score` |
| Vidas | superior direito | `draw_text` + `draw_lives` |
| Barra de saúde | inferior esquerdo | `draw_health_bar` |
| Minimapa | centro, **sob demanda** | `draw_minimap` |

Pontuação e saúde ficam em cantos **opostos** propositalmente: uma
barra de saúde é larga e uma string de pontuação cresce enquanto você
joga, então empilhá-las convidaria a uma colisão.

### O minimapa

**Pressione `M` para mostrá-lo ou escondê-lo** — no Android, toque o
botão de mapa no canto superior esquerdo. Ele está *desligado* por
padrão e é desenhado apenas enquanto ativado, por dois motivos: um
mapa completo são ~250 comandos de linha a cada quadro, e cobrir
permanentemente parte de uma visão em primeira pessoa é exatamente a
desordem que um HUD deveria evitar. Enquanto está desligado, não
custa nada.

`draw_minimap` desenha um mapa **orientado ao norte** das paredes da
sala com um marcador mostrando onde você está e para onde está
olhando. Ele não gira — o mapa permanece fixo e o marcador gira, o
que é mais fácil de ler do que um mapa girando.

Ele não precisa de dados próprios: lê as mesmas bordas de parede que
a visão em primeira pessoa já derivou das instâncias sólidas da sala,
então permanece correto se você redesenhar o labirinto. Mostra
**apenas paredes** — não gemas ou monstros — então o labirinto ainda
vale a pena explorar.

**Não implementado (deliberado):** névoa de guerra, um modo
rotativo/orientado à direção, e mostrar itens ou inimigos. Veja
[`docs/RAYCAST_MINIMAP_PLAN.md`](../../docs/RAYCAST_MINIMAP_PLAN.md)
para o porquê de cada omissão.

**`obj_hud` é `visible: true`, e isso importa.** O GameMaker não
executa o evento draw de uma instância invisível — então o HUD não
pode simplesmente viver no controlador de câmera invisível
(`obj_cam0`/`obj_cam1`). Se você construir seu próprio HUD e nada
aparecer, verifique primeiro essa bandeira.

## Estrutura do projeto

| Arquivo | Propósito |
|---|---|
| `project.json` | Manifesto — janela 640×480, ambas as salas, cópias de recursos incorporadas |
| `rooms/room0.json` | Labirinto de tijolo quente: 15×15 células / 480×480, 8 gemas, 3 monstros, 3 kits médicos |
| `rooms/room1.json` | Labirinto de caverna de cristal: a metade mais difícil — 10 gemas, 5 monstros, apenas 2 kits médicos |
| `objects/obj_person.json` | Jogador/câmera — movimento, dano de saúde + alarme de invulnerabilidade, manuseio de morte |
| `objects/obj_hud.json` | O display de informações (veja acima) |
| `objects/obj_cam0.json`, `obj_cam1.json` | Controladores de câmera por sala, cada um carregando o tema de textura daquela sala |
| `objects/obj_gem.json` | Colecionável, +10 de pontuação |
| `objects/obj_medkit.json` | Restaura 40 de saúde |
| `objects/obj_monster.json` | Inimigo billboard em patrulha |
| `objects/obj_goal.json`, `obj_goal_final.json` | Saídas bloqueadas por gemas: avanço, e vitória |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segmentos de parede finos (32×8 e 8×32) |
| `sprites/` | 13 sprites, reutilizados de `raycast_2` mais `spr_medkit` |

## O labirinto é gerado, não colocado à mão

`tools/gen_raycast_3_maze.py` constrói ambas as salas com um
labirinto backtracker recursivo passado pela colocação de parede
fina na borda de `raycast_1` — partições de 8px centradas nos
limites de célula, não blocos de 32px que preenchem uma célula.
Executá-lo novamente reproduz exatamente as salas distribuídas, e um
teste verifica que elas não se desviaram, então o design de nível
permanece revisável e ajustável em vez de ser dados opacos. (O
labirinto de `raycast_2` veio de um script descartável nunca
confirmado, então suas salas não podem ser regeneradas — este corrige isso.)

As sementes são **escolhidas, não arbitrárias**: `check_start()`
verifica que a célula inicial se abre para o leste (o jogador aparece
lá olhando para o leste, então um início murado significaria começar
o jogo com o nariz contra uma parede) e que cada célula é alcançável.

## Coisas para ajustar

- **Dano e cura:** `-25` no evento `collision_with_obj_monster` de
  `obj_person`, `+40` no evento `destroy` de `obj_medkit`.
- **Janela de invulnerabilidade:** os `45` passos em `alarm_0`. Mais
  curta torna o jogo mais duro; removê-la e um monstro que se
  sobrepõe a você repetidamente vai destroçar a barra.
- **Balanceamento de dificuldade:** os `counts` por sala no gerador —
  monstros contra kits médicos é o controle principal.
- **Layout do HUD:** as coordenadas no evento draw de `obj_hud`.
  Mantenha pontuação e saúde em cantos opostos.
- **Minimapa:** `size` em `draw_minimap` escala toda a sala naquele
  quadrado, então um valor maior só significa um mapa mais legível;
  `wall_color` e `player_color` definem sua aparência. O alternador
  vive no evento `keyboard_press` → `m` de `obj_hud`; usa
  `test_variable` + `exit_event` em vez de dois condicionais
  simples, porque a versão ingênua define a bandeira como 1 e depois
  imediatamente lê 1 e a redefine imediatamente para 0.
- **Temas:** os parâmetros de textura em `obj_cam0`/`obj_cam1`.

## Uma nota sobre o momento das colisões

O motor de execução dispara um evento de colisão quando duas
instâncias **começam** a se sobrepor, não a cada quadro em que
permanecem sobrepostas. Ficar dentro de um monstro, portanto, custa
um golpe, não um golpe por quadro. O alarme de invulnerabilidade
ainda merece seu lugar: ele cobre o toque/destoque repetido de um
monstro que patrulha *através* de você, que é o caso que você
realmente encontra jogando.

## Status da exportação

Roda em todos os três destinos. Coberto pela suíte smoke sem
interface gráfica (`tools/smoke_run_samples.py`) e por
`tests/test_raycast_3_sample.py`, que conduz o loop de jogo real:
dano, a abertura e fechamento da janela de invulnerabilidade, a
morte custando exatamente uma vida, a cura do kit médico e seu
limite, a saída bloqueada por gemas, a transição de sala para o tema
de gelo, e a renderização do HUD sobre a visão em primeira pessoa em
**ambas** as salas.

As exportações Kivy e HTML5 foram verificadas para carregar todo o
loop — `no_more_health`, `alarm_0`, `draw_health_bar`, `obj_hud` e
`spr_medkit` todos sobrevivem à geração de código — mas o playtest
**visual** por destino vale a pena fazer com os próprios olhos antes
de um lançamento.
