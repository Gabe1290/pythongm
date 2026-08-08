# Views — Nível 1

Uma demonstração de câmera com rolagem: a sala (2400×800) é **três
vezes mais larga que a janela de 800×600**, então uma única tela não
consegue mostrar tudo. A câmera (view 0) segue o jogador enquanto ele
anda para a direita, revelando o nível uma tela de cada vez — o
propósito inteiro das **views** ao estilo GameMaker. Explore a sala
larga e colete todas as 18 moedas.

**Onde isso se encaixa:** esta é a quarta família de amostras,
distinta das três famílias de técnica de autoria (`maze_*` →
`plateforme_*` → `match3_*`). O que ela introduz não é um novo
*estilo* de autoria, mas uma nova capacidade do motor: uma **sala
maior que a janela** com uma **câmera que rola**. Veja
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para a progressão completa. Mecanicamente reutiliza o movimento em
grade de `maze_1` (ações integradas `test_alignment`/`snap_to_grid`/
`start_moving_direction`) e adiciona exatamente uma coisa nova: a
câmera, habilitada a partir do evento **create** do jogador com as
ações registradas `enable_views` + `set_view`.

**Som e música:** nenhum — nenhum arquivo de som é incluído com esta amostra.

## Como jogar

- As **teclas de seta** movem o jogador uma célula de grade (32px)
  por vez (movimento ajustado à grade, igual a `maze_1`).
- Paredes (`obj_wall`) margeiam a borda da sala e formam alguns
  pilares internos; são sólidas e param o jogador.
- **A câmera segue o jogador**: ande em direção a uma borda da tela e
  a view rola para te manter no quadro, travando nas bordas da sala
  para que você nunca veja além do limite de paredes.
- **Objetivo:** colete todas as 18 moedas (`obj_coin`). Cada uma vale
  10 pontos (mostrados no título da janela).

## Como a câmera é configurada

O evento **create** do jogador executa duas ações registradas
(nenhum `execute_code` bruto):

1. `enable_views` — liga o sistema de views para a sala.
2. `set_view` — configura a **view 0**: `view_w`/`view_h` `800×600`,
   porta em `(0,0)` com tamanho `800×600`, `follow` = `obj_player`,
   `hborder` 240 / `vborder` 180 (a zona morta antes que a câmera
   role), sem limite de velocidade de rolagem. A mesma configuração
   também é incorporada no bloco `views` da sala, então a câmera está
   correta desde o primeiro quadro em todo destino de exportação.

## Estrutura do projeto

| Arquivo | Propósito |
|---|---|
| `project.json` | Manifesto do projeto — configurações de janela/sala, cópias de recursos incorporadas, e a configuração `views` da sala |
| `rooms/room0.json` | A sala de 2400×800 (245 instâncias: borda de paredes + pilares, jogador, 18 moedas) e seu bloco `views` |
| `objects/obj_player.json` | Jogador: movimento em grade + a configuração da câmera no evento create |
| `objects/obj_coin.json` | Colecionável: destruída ao toque do jogador, adiciona 10 à pontuação |
| `objects/obj_wall.json` | Parede sólida estática |
| `sprites/` | `spr_player.png`, `spr_wall.png`, `spr_coin.png` + seus metadados `.json` |
| `CREDITS.txt` | Aviso de licenciamento de recursos |

## Objetos

| Objeto | Papel | Eventos-chave |
|---|---|---|
| `obj_player` | Personagem do jogador; movimento em grade + habilita/configura a câmera | create (`enable_views`, `set_view`), keyboard (down/right/up/left/nokey), collision_with_obj_wall |
| `obj_coin` | Colecionável que vale 10 pontos | collision_with_obj_player (`destroy_instance` self), destroy (`set_score` +10) |
| `obj_wall` | Parede sólida estática / limite de travamento da câmera | (nenhum — colisor passivo) |

## Recursos

3 sprites (`spr_player`, `spr_wall`, `spr_coin`, cada um 32×32, quadro
único, colisão pixel-precisa), 0 sons. Todos os três são arte simples
de cor sólida CC0 gerada para esta amostra — veja `CREDITS.txt`.

## Coisas para ajustar

- **Tamanho da sala** (`2400×800` em `rooms/room0.json`) — deixe-a
  mais larga/alta para rolar mais; a câmera trava no que quer que a
  sala seja.
- **Bordas** (`hborder` 240 / `vborder` 180 na ação `set_view` *e* no
  bloco `views` da sala) — bordas menores deixam o jogador chegar
  mais perto da borda antes que a câmera se mova; maiores o mantêm
  mais centralizado.
- **Velocidade de rolagem** — `hspeed`/`vspeed` são `-1` (seguimento
  instantâneo). Defina-os como um valor positivo de pixels por passo
  para uma câmera com atraso, suavizada.
- **Moedas** — adicione/remova instâncias de `obj_coin` em `rooms/room0.json`.

## Status da exportação

- **Desktop (pygame):** o destino de referência — verificado por
  `tests/test_views_1_sample.py`, que carrega esta amostra, executa o
  evento create do jogador, e verifica que a câmera rola e trava
  enquanto o jogador caminha por toda a largura.
- **Web (HTML5):** o `engine.js` exportado carrega a mesma câmera de
  8 views (`tests/test_html5_views.py`, verificado no Chromium
  durante o desenvolvimento); a configuração `views` desta amostra e
  o `set_view` do evento create ambos se propagam para a exportação.
- **Móvel (Kivy/Android):** a cena exportada renderiza a sala inteira
  em um Fbo e copia a região de cada view visível para sua porta de
  tela, com a janela do sistema operacional dimensionada para a view
  (não para a sala) para que a câmera mostre uma verdadeira fatia
  rolante e suporte múltiplas viewports (`tests/test_kivy_views.py`).
  As ações `enable_views`/`set_view` são emitidas, então a
  reconfiguração da câmera em tempo de execução também funciona.
  *Uma limitação residual:* o alvo de renderização multi-view é
  construído quando a sala é criada, então uma sala precisa ter
  `views_enabled` em sua configuração (como esta amostra tem) para
  que a câmera renderize — habilitar views apenas por meio de um
  `enable_views` em tempo de execução em uma sala que começou sem
  elas não vai retroadaptá-la no Kivy.
- A concordância entre destinos na matemática de rolagem é fixada por
  `tests/test_views_export_parity.py`.

Exposto na aba Welcome do IDE como "Views — Level 1"
(`widgets/welcome_tab.py`).
