# Views — Nível 2

Uma demonstração de **cooperativo em tela dividida**: a sala de
2400×800 é mostrada como duas câmeras lado a lado em uma única janela
de 800×600. A **metade esquerda** (view 0) segue o **jogador 1**
(laranja, teclas de seta); a **metade direita** (view 1) segue o
**jogador 2** (azul-petróleo, WASD). Cada jogador explora a sala
compartilhada em sua própria faixa e coleta moedas — você observa os
dois ao mesmo tempo.

**Onde isso se encaixa:** o segundo nível da quarta família de
amostras. `views_1` introduziu uma única câmera com rolagem;
`views_2` introduz **múltiplas viewports ao mesmo tempo** — a outra
capacidade de destaque das views do GameMaker. Veja
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para a progressão completa. O movimento reutiliza o idioma de grade
de `maze_1`/`views_1`.

**Som e música:** nenhum — nenhum arquivo de som é incluído com esta amostra.

## Como jogar

- **Jogador 1 (laranja):** teclas de seta — move na view **esquerda**.
- **Jogador 2 (azul-petróleo):** `W` `A` `S` `D` — move na view **direita**.
- Ambos se movem uma célula de grade (32px) por vez; paredes
  (`obj_wall`) são sólidas. Um divisor central com aberturas separa
  as duas faixas.
- **Objetivo:** colete as 18 moedas (`obj_coin`) — qualquer jogador
  pode pegar qualquer moeda; cada uma vale 10 pontos (mostrados no
  título da janela).

## Por que os dois jogadores param independentemente (uma pegadinha real)

O movimento em grade normalmente para no evento `nokey` (disparado
quando *nenhuma* tecla está pressionada). Mas o estado das teclas é
rastreado globalmente entre todas as instâncias, então com dois
jogadores `nokey` só dispara quando **ambos** soltam tudo — o
jogador 2 continuaria deslizando enquanto o jogador 1 segura uma
tecla. Então cada jogador para, em vez disso, via **`keyboard_release`**
para **suas próprias** teclas (setas para P1, WASD para P2), que
dispara por tecla e por objeto. Essa é a diferença em relação ao
jogador único de `views_1`, que pode usar `nokey` com segurança.

## Como a tela dividida é configurada

Um controlador invisível, `obj_camera`, configura ambas as views em
seu evento **create** (`enable_views` registrado + duas ações
`set_view`), e a mesma configuração é incorporada no bloco `views` da
sala para correção no quadro 0 na exportação:

- **view 0** — `view`/`port` `400×600`, `port_x` 0 (metade esquerda),
  `follow` `obj_player1`.
- **view 1** — `view`/`port` `400×600`, `port_x` 400 (metade direita),
  `follow` `obj_player2`.

Ambas as views são **1:1** (tamanho da view == tamanho da porta) e
divididas **esquerda/direita** (`port_y` 0, altura completa). Isso
importa para a consistência entre destinos: desktop e HTML5
renderizam cada view em 1:1 (recortam + deslocam, **não** escalam uma
view para sua porta), e uma divisão esquerda/direita evita a
inversão de `port_y` entre Kivy (y-para-cima) e desktop/HTML5
(y-para-baixo). Um minimapa reduzido (view maior que sua porta) é
deliberadamente **não** usado aqui — ele só escalaria corretamente no Kivy.

## Estrutura do projeto

| Arquivo | Propósito |
|---|---|
| `project.json` | Manifesto — configurações de janela/sala, recursos incorporados, e a configuração `views` de duas views |
| `rooms/room0.json` | A sala de 2400×800 (284 instâncias: câmera, paredes, 2 jogadores, 18 moedas) + seu bloco `views` |
| `objects/obj_camera.json` | Controlador invisível: `enable_views` no evento create + duas `set_view` |
| `objects/obj_player1.json` | Jogador 1 (teclas de seta); movimento em grade + parada por `keyboard_release` |
| `objects/obj_player2.json` | Jogador 2 (WASD); movimento em grade + parada por `keyboard_release` |
| `objects/obj_coin.json` | Colecionável — destruída por qualquer jogador, adiciona 10 |
| `objects/obj_wall.json` | Parede sólida estática |
| `sprites/` | `spr_player1.png` (laranja), `spr_player2.png` (azul-petróleo), `spr_wall.png`, `spr_coin.png` + metadados `.json` |
| `CREDITS.txt` | Aviso de licenciamento de recursos |

## Objetos

| Objeto | Papel | Eventos-chave |
|---|---|---|
| `obj_camera` | Controlador invisível; habilita + configura ambas as views | create (`enable_views`, 2× `set_view`) |
| `obj_player1` | Jogador da view esquerda (setas) | keyboard (up/down/left/right/nokey), keyboard_release (por tecla), collision_with_obj_wall |
| `obj_player2` | Jogador da view direita (WASD) | keyboard (w/a/s/d/nokey), keyboard_release (por tecla), collision_with_obj_wall |
| `obj_coin` | Colecionável que vale 10 | collision_with_obj_player1, collision_with_obj_player2, destroy (`set_score` +10) |
| `obj_wall` | Parede sólida estática / limite da câmera | (nenhum — colisor passivo) |

## Recursos

4 sprites (`spr_player1`, `spr_player2`, `spr_wall`, `spr_coin`, cada
um 32×32, quadro único, pixel-precisos), 0 sons. Toda a arte é de cor
sólida CC0 gerada para esta amostra — veja `CREDITS.txt`.

## Coisas para ajustar

- **Direção da divisão** — esta amostra usa uma divisão
  esquerda/direita (`port_x` 0 e 400, `port_y` 0, altura completa).
  Uma divisão superior/inferior colocaria as metades em `port_y`
  diferentes; note que isso renderiza em uma posição vertical
  diferente no Kivy (y-para-cima) vs. desktop/HTML5 (y-para-baixo),
  então esquerda/direita é a escolha portável.
- **Largura da view** — cada view tem `400` de largura (metade da
  janela). Alargue a janela ou estreite as views para mudar quanto de
  sala cada jogador vê.
- **Bordas** — `hborder` 120 / `vborder` 150 definem a zona morta de
  cada câmera.

## Status da exportação

- **Desktop (pygame):** a referência — `tests/test_views_2_sample.py`
  carrega a amostra, executa o evento create de `obj_camera`, e
  verifica que as duas câmeras rolam **independentemente** (mover um
  jogador não move a view do outro) e travam na borda da sala, além
  da pontuação de moedas e da parada por `keyboard_release` por
  jogador.
- **Web (HTML5):** `engine.js` renderiza toda view visível (recorte
  por view + tradução 1:1); a configuração de duas views se propaga
  para a exportação.
- **Móvel (Kivy/Android):** o exportador renderiza a sala em um Fbo e
  copia a região de cada view visível para sua porta de tela
  (`tests/test_kivy_views.py` cobre a renderização multi-view). As
  ações `enable_views`/`set_view` são emitidas, então a configuração
  de duas views roda a partir do evento create de `obj_camera`, assim
  como a partir da configuração incorporada na sala. Limitação
  residual (como em `views_1`): o alvo de renderização é construído
  na criação da sala, então `views_enabled` precisa estar na
  configuração da sala (está aqui) para que a câmera renderize no Kivy.
- A concordância entre destinos na matemática de rolagem é fixada por
  `tests/test_views_export_parity.py`.

Exposto na aba Welcome do IDE como "Views — Level 2" (`widgets/welcome_tab.py`).
