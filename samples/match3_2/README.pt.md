# Match-3 — Nível 2

A continuação animada baseada em sprites de
[`match3_1`](../match3_1/README.md), prometida no Roteiro daquela
amostra: o mesmo tabuleiro e pontuação, agora desenhado com sprites
de gemas reais em vez de retângulos coloridos, com uma animação de
deslize da troca, e efeitos sonoros para troca/combinação/cascata.
Ainda uma sala, um objeto, sem scripts — o jogo inteiro ainda são
quatro eventos `execute_code` em um único objeto controlador.

**Onde isso se encaixa:** parte da família `match3_*` — script puro
`execute_code`, sem ações integradas, sem tiles no nível da sala. Veja
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para como isso difere da abordagem de ações integradas e
multi-objeto de `maze_*`/`plateforme_*`.

**Som e música:** 3 arquivos de som (`snd_swap`, `snd_match`,
`snd_cascade`), todos usados ativamente — enfileirados de
`execute_code` via `self._sound_queue` (veja abaixo), não a ação `play_sound`.

## Como jogar

Igual a match3_1:

- **Clique** em um tile para selecioná-lo (contorno branco), depois
  **clique em um tile adjacente** para trocar os dois. A troca agora
  **desliza** para o lugar em vez de encaixar instantaneamente.
- Se a troca alinhar **3 ou mais tiles da mesma cor** em linha ou
  coluna, os tiles combinados piscam por um instante, são destruídos,
  e os tiles acima **deslizam para baixo** para preencher o espaço;
  novos tiles caem do topo do tabuleiro. Reações em cadeia
  ("cascatas") se resolvem onda por onda.
- Uma troca que não produz nenhuma combinação **desliza de volta**
  para sua posição original em vez de encaixar de volta.
- Cada tile destruído vale **10 pontos**; alcance **500 pontos** para vencer.
- Cada tentativa de troca reproduz um clique; uma combinação bem-
  sucedida reproduz um sino, e cada cascata adicional na mesma
  combinação reproduz um sino mais brilhante e ascendente.

## O que muda em relação a match3_1

| match3_1 | match3_2 |
| -------- | -------- |
| Tiles desenhados como retângulos de cor sólida | Tiles desenhados como **sprites** de gema (comando de fila de desenho ao estilo `draw_sprite`), uma forma por cor para acessibilidade a daltônicos |
| A troca se aplica instantaneamente, combinações são avaliadas imediatamente | A troca **desliza** para o lugar primeiro (~4 quadros); uma troca inválida desliza de volta em vez de encaixar |
| Sem áudio | **Efeitos sonoros** para troca/combinação/cascata, enfileirados de `execute_code` via a nova primitiva `self._sound_queue` (veja abaixo) |

A lógica do tabuleiro em si (modelo de grade, busca de combinações,
queda em cascata, pontuação, condição de vitória) permanece inalterada
em relação a match3_1 — é um diff genuinamente legível, não uma reescrita.

## Estrutura do projeto

| Arquivo | Propósito |
| ---- | ------- |
| `project.json` | manifesto do projeto — janela 800×800, 60 fps, sala inicial `rm_match3` |
| `rooms/rm_match3.json` | a única sala; contém uma instância de `obj_GridManager` em (0, 0) |
| `objects/obj_GridManager.json` | o jogo inteiro: quatro eventos, cada um com uma única ação `execute_code` |
| `sprites/spr_gem_red|blue|green|yellow.png` | tiles de gema 88×88 (veja `CREDITS.txt`) — dimensionados para encaixar exatamente onde antes estava o preenchimento retangular de match3_1, já que `draw_sprite` desenha em tamanho nativo sem escala |
| `sounds/snd_swap|match|cascade.wav` | tons sintetizados curtos (veja `CREDITS.txt`) |

## Como o código funciona

O estado e a máquina de estados `step` são os mesmos de match3_1
(`grid`, `sel`, `marked`, `flash`/`flash_total`, `falling`/`fall_speed`,
`score`, `target`, `won`, `find_matches`) — veja aquele README para a
descrição completa. Novo estado adicionado para esta versão:

| Atributo | Significado |
| --------- | ------- |
| `sprite_names` | `['spr_gem_red', 'spr_gem_blue', 'spr_gem_green', 'spr_gem_yellow']`, indexado da mesma forma que `palette` era em match3_1 |
| `swap_off` | dicionário `(gx, gy) → (dx, dy)` deslocamento em pixels para o deslize de troca em andamento; decai para `(0, 0)` a `swap_speed` px/quadro, a mesma técnica de encolher-até-repouso que `falling` já usa para cascatas, generalizada para dois eixos |
| `swap_phase` | `None` / `'forward'` (deslizando para a posição trocada) / `'back'` (uma troca rejeitada deslizando de volta para suas células originais) |
| `last_swap` | `(gx, gy, sx, sy)` — as duas células envolvidas na troca em andamento, para que `step` possa revertê-las sem precisar de estado de fechamento |
| `pending_marks` | o conjunto de combinações calculado logo após uma troca, mantido até que a animação de deslize termine para que o piscar não comece no meio do deslize |
| `arm_swap(a, b)` | função auxiliar (definida em `create`, armazenada na instância como `find_matches`) que define `swap_off` para ambas as células apenas a partir de suas posições — chamá-la novamente com as mesmas duas células produz a animação inversa, o que dá de graça o deslize de reversão |

Fluxo atualizado:

```
clique em tile adjacente
  → grade trocada imediatamente (dados), pending_marks calculado
  → swap_off armado (forward) — os tiles deslizam para suas novas células
       │
       ▼ (o deslize se assenta)
  pending_marks?
    sim → arma o piscar (pisca → destrói → cai → reanalisa, como em match3_1)
    não  → troca a grade de volta, rearma swap_off com as MESMAS duas células (phase='back')
             │
             ▼ (o deslize se assenta)
          idle
```

- **`create`** — mesma semeadura de grade que match3_1, mais
  `sprite_names`, `swap_off`/`swap_speed`/`swap_phase`/`last_swap`/
  `pending_marks`, e a função auxiliar `arm_swap`.
- **`mouse_left_press`** — a lógica de seleção não muda; uma troca
  adjacente válida agora aplica a troca na grade, calcula
  `pending_marks`, arma o deslize para frente, e enfileira `snd_swap`.
- **`step`** — os blocos de piscar/queda não mudam em relação a
  match3_1 (ainda enfileiram `snd_cascade` em uma nova combinação
  encadeada); um novo bloco `elif self.swap_off:` decai o deslize e,
  uma vez assentado, ou arma o piscar (enfileirando `snd_match`) ou
  inicia o deslize de reversão.
- **`draw`** — mesmo desenho de painel/tabuleiro/seleção/pontuação/
  instruções/banner de vitória que match3_1, mas cada tile é agora um
  comando de fila de desenho
  `{'type': 'sprite', 'sprite_name': ..., 'x': ..., 'y': ...}` em vez
  de um retângulo sólido (ainda substituído por um simples retângulo
  branco sólido durante o piscar do tile marcado, exatamente como
  match3_1 fazia), deslocado por `swap_off` combinado com `falling`.

### A primitiva `self._sound_queue`

`execute_code` só tem um objeto `game` vivo no motor pygame de
desktop — tanto o motor exportado para Kivy quanto o motor Web/
Pyodide vinculam `game = None` naquele escopo, então
`game.sounds[...].play()` (o óbvio a tentar) só funciona no desktop.
Esta amostra é o que motivou adicionar uma primitiva multiplataforma
real: o `execute_code` de qualquer evento pode fazer

```python
self._sound_queue.append('snd_swap')
# ou, para um volume não padrão:
self._sound_queue.append({'sound': 'snd_swap', 'volume': 0.5})
```

e isso reproduz identicamente nos três destinos:

- **Desktop** — `ActionExecutor.execute_event` a esvazia e a
  reproduz (via `game.sounds[...]`) logo após cada evento, não
  apenas `draw`.
- **Exportação Kivy** — `GameObject._drain_sound_queue` (gerado em
  `base_object.py`) resolve o nome via um `asset_paths.py` gerado
  (`SOUND_PATHS`) e chama o auxiliar `play_sound()` existente;
  esvaziado uma vez por quadro para cada instância viva a partir do
  loop `update()` da cena, então funciona mesmo para objetos sem
  evento `draw`.
- **Web (Pyodide)** — o bootstrap Python retorna quaisquer sons
  enfileirados no patch JSON junto com a fila de desenho; `engine.js`
  os reproduz como elementos `<audio>` reais através do mesmo caminho
  de áudio agrupado que a ação estruturada `play_sound` já usava.

A mesma lacuna de resolução por nome existia para comandos ao estilo
`draw_sprite` enviados de `execute_code` bruto (a renderização de
tiles desta amostra) — o renderizador da fila de desenho do Kivy
antes só podia resolver um sprite a partir de um `sprite_path`
incorporado no momento da geração de código para ações
*estruturadas*, então um dicionário
`{'type': 'sprite', 'sprite_name': ...}` escrito à mão silenciosamente
não renderizava lá. Corrigido da mesma forma: `asset_paths.py` agora
também carrega `SPRITE_PATHS`, e o caso `'sprite'` da fila de desenho
do Kivy recorre a ele por nome quando nenhum caminho pré-resolvido está presente.

### Coisas para ajustar

Mesmos controles de match3_1 (`self.cols`/`self.rows`,
`self.palette`, `self.target`, `flash_total`, `fall_speed`), mais:

- Velocidade da animação de troca: `self.swap_speed` (px/quadro; 24 →
  ~4 quadros por deslize com `tile=96`).
- Volume do som: passe um dicionário `{'sound': ..., 'volume': ...}`
  em vez de um nome simples para `self._sound_queue.append(...)`.

## Roteiro

**[match3_3](../match3_3/README.md)** — feito: um limite de
movimentos, três salas como níveis de objetivo crescente, e tiles
especiais (bônus de 4/5 em linha). Fecha o roteiro original de match3_1.

## Status da exportação

- **Test Game (F5) / desktop:** funciona — verificado de ponta a
  ponta com uma execução real do `GameRunner` injetando um clique
  real do mouse através do caminho de eventos pygame padrão (troca →
  combinação → cascata → pontuação, com chamadas reais a
  `pygame.mixer.Sound.play()` observadas).
- **Android (.apk) / Mobile (Kivy):** **suportado.** Verificado que a
  exportação compila corretamente, que `asset_paths.py` carrega os
  `SPRITE_PATHS`/`SOUND_PATHS` corretos, e que as imagens de sprites/
  arquivos de som são copiados para `assets/images`/`assets/sounds`.
  Construir o `.apk` real requer adicionalmente buildozer (via WSL no
  Windows) — veja [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Web (HTML5):** **suportado.** O bootstrap Pyodide da página
  exportada esvazia `self._sound_queue` no mesmo round-trip JSON que
  a fila de desenho; verificado que o bootstrap gerado compila e
  transfere corretamente tanto os comandos de desenho quanto os sons
  enfileirados sob CPython puro (nenhum navegador necessário para
  essa verificação — o boot do Pyodide no navegador em si não é
  coberto pela suíte automática, mesma ressalva de match3_1). Precisa
  de acesso à internet no primeiro carregamento (Pyodide carrega de um CDN).
- **Zip independente:** não testado com esta amostra.
