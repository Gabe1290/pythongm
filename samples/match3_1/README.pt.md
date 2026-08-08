# Match-3 — Nível 1

Um jogo de puzzle match-3 (três em linha) mínimo e completo. Esta é a
primeira amostra pygm2 **escrita nativamente no formato de projeto
próprio do IDE** — as amostras de labirinto e plataforma foram
importadas de arquivos `.gmk` do GameMaker 8.x; esta foi escrita
diretamente para o motor do pygm2.

É deliberadamente pequena: uma sala, um objeto, sem scripts, sem
sons. Todo o jogo vive em quatro eventos de um único objeto
controlador, o que a torna a amostra de referência para a ação
`execute_code` e para renderização via fila de desenho. Versões mais
avançadas (tiles baseadas em sprites, som, níveis) estão planejadas
como `match3_2`, etc. — veja o *Roteiro* abaixo.

**Onde isso se encaixa:** `match3_*` é a última (e mais diferente)
das três famílias de amostras — um paradigma diferente, não um passo
incremental: sem ações integradas, sem objeto por tile, sem tiles no
nível da sala. Tudo (estado da grade, colisão, renderização) é
conduzido diretamente por Python em `execute_code`, em vez de ser
composto a partir de ações integradas espalhadas por muitos objetos,
como fazem `maze_*` e `plateforme_*`. Veja
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para a progressão completa.

**Som e música:** nenhum — deliberadamente, pelo motivo explicado
acima. (O som se torna possível a partir de `match3_2`, através da
primitiva de fila de som que aquela amostra introduziu.)

## Como jogar

- **Clique** em um tile para selecioná-lo (contorno branco), depois
  **clique em um tile adjacente** para trocar os dois.
- Se a troca alinhar **3 ou mais tiles da mesma cor** em linha ou
  coluna, os tiles combinados piscam por um instante, são destruídos,
  e os tiles acima **deslizam para baixo** para preencher o espaço;
  novos tiles caem do topo do tabuleiro.
- Reações em cadeia ("cascatas") se resolvem onda por onda, cada uma
  com sua própria animação de piscar e deslizar.
- Uma troca que não produz nenhuma combinação é revertida imediatamente.
- Cada tile destruído vale **10 pontos**; alcance **500 pontos** para vencer.

## Estrutura do projeto

| Arquivo | Propósito |
| ---- | ------- |
| `project.json` | manifesto do projeto — janela 800×800, 60 fps (`room_speed`), sala inicial `rm_match3` |
| `rooms/rm_match3.json` | a única sala; contém uma instância de `obj_GridManager` em (0, 0) |
| `objects/obj_GridManager.json` | o jogo inteiro: quatro eventos, cada um com uma única ação `execute_code` |
| `sprites/spr_red|blue|green|yellow.*` | quadrados de tile 32×32 — **ainda não usados**; reservados para a continuação baseada em sprites (veja `CREDITS.txt`) |

Não há objeto jogador nem objeto por tile: o tabuleiro é dados puros
(uma lista 6×6 de índices de cor) pertencente a uma única instância
controladora invisível, e tudo o que aparece na tela é desenhado pelo
evento `draw` desse controlador através da fila de desenho do motor
(`self._draw_queue`).

## Como o código funciona

Todo o estado vive na instância controladora (`self.…`), criada no
evento `create`:

| Atributo | Significado |
| --------- | ------- |
| `grid` | lista 6×6 de inteiros 0–3 (índices em `palette`); semeada sem combinações pré-existentes |
| `sel` | célula atualmente selecionada `(gx, gy)` ou `None` |
| `marked` | conjunto de células atualmente combinadas e piscando |
| `flash` / `flash_total` | quadros restantes da fase de piscar / sua duração (36 quadros ≈ 0,6 s a 60 fps) |
| `falling` | dicionário `(gx, gy) → pixels` — quão acima de sua célula de repouso cada tile deslizante está atualmente |
| `fall_speed` | velocidade de deslize em pixels por quadro (12 → uma linha de 96 px em ~0,13 s) |
| `score`, `target`, `won` | estado de pontuação (vitória em 500) |
| `find_matches` | função auxiliar (definida em `create`, armazenada na instância) que examina a grade e retorna o conjunto de todas as células combinadas |

O jogo é uma pequena máquina de estados conduzida pelo evento `step`:

```
idle ──(troca por clique, combinação encontrada)──▶ FLASH (piscar, 36 quadros)
                                        │ tiles destruídos, pontuação adicionada
                                        ▼
                                      FALL (deslocamento encolhe 12 px/quadro)
                                        │ pousou → reanálise da grade
                          nova combinação ─┴─ sem combinação
                                 │            │
                                 ▼            ▼
                               FLASH        idle
```

- **`create`** — constrói a grade inicial (sorteando novamente
  qualquer tile que completaria uma combinação imediata), inicializa
  o estado acima, e define `find_matches`.
- **`mouse_left_press`** — lógica de seleção/deseleção; em uma troca
  adjacente aplica a troca, e ou arma o piscar (`marked`, `flash`) ou
  reverte. A entrada é ignorada enquanto um piscar ou queda está em
  andamento, e depois que o jogo é vencido.
- **`step`** — conta regressivamente o piscar; ao expirar credita a
  pontuação, reescreve cada coluna afetada em seu layout final, e
  registra um deslocamento em pixels em `falling` para cada tile que
  se moveu (tiles sobreviventes recebem `linhas_caídas × 96`; tiles de
  preenchimento entram de cima do tabuleiro). Enquanto `falling` não
  estiver vazio, encolhe cada deslocamento por `fall_speed`; quando
  tudo pousou, reanalisa em busca de combinações em cascata e ou
  rearmam o piscar ou retorna a idle.
- **`draw`** — desenha o painel do tabuleiro, depois cada tile em
  `posição_de_repouso − deslocamento_de_queda`. Tiles acima da borda
  superior do tabuleiro são recortados (parcialmente emergidos) ou
  pulados (completamente ocultos), então os preenchimentos parecem
  deslizar de baixo do cabeçalho. Tiles marcados piscam em branco a
  cada 6 quadros e carregam um contorno branco; a seleção, a linha de
  pontuação, as instruções e o banner de vitória são desenhados por último.

### Coisas para ajustar

- Tamanho do tabuleiro: `self.cols` / `self.rows` (as constantes de
  layout `ox`, `oy`, `tile` controlam o posicionamento — um tabuleiro
  6×6 de tiles de 96 px cabe na janela 800×800).
- Cores / tipos de tile: `self.palette` (adicione uma tupla para
  obter uma 5ª cor; a lógica de sorteio e o renderizador a captam
  automaticamente, mas atualize `random.randrange(4)` em `create` e `step`).
- Dificuldade: `self.target` (pontos para vencer), `flash_total`, `fall_speed`.

## Roteiro (versões avançadas planejadas)

- **[match3_2](../match3_2/README.md)** — feito: desenha os tiles com
  sprites em vez de retângulos coloridos, adiciona efeitos sonoros
  para troca/combinação/cascata, e uma animação de deslize da troca.
- **[match3_3](../match3_3/README.md)** — feito: um limite de
  movimentos, três salas como níveis de objetivo crescente, e tiles
  especiais a partir de combinações de 4/5 em linha. Fecha este roteiro.

As versões pretendem espelhar a progressão maze_1→3: cada uma um diff legível sobre a anterior.

## Status da exportação

- **Test Game (F5) / desktop:** funciona — o jogo roda no motor
  pygame padrão. É exercitado sem interface gráfica em execuções
  smoke estilo CI via `tools/smoke_run_samples.py`.
- **Android (.apk) / Mobile (Kivy):** **suportado** (desde
  03/07/2026). O motor Kivy exportado renderiza a fila de desenho do
  jogo (retângulos e texto, com o eixo y convertido para o sistema de
  baixo para cima do Kivy), despacha toques como o evento
  `mouse_left_press` com `mouse_x`/`mouse_y` em coordenadas de sala
  tanto no Android (invertendo a transformação de escala de tela
  cheia) quanto no Kivy desktop, e — como este jogo não tem eventos
  de teclado — omite a sobreposição do D-pad virtual que de outra
  forma cobriria o canto inferior direito do tabuleiro. O jogo
  exportado é exercitado sem interface gráfica em
  `tests/test_kivy_draw_queue_mouse_export.py`, que joga uma rodada
  completa troca → piscar → deslizar através do código gerado.
  Construir o `.apk` real requer adicionalmente buildozer (via WSL no
  Windows) — veja
  [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md) para o
  guia completo (configuração, tempos de build, cache para uso em
  sala de aula/sessão); lacunas de paridade de exportação Kivy
  restantes que *não* afetam este jogo estão listadas sob
  "Kivy/Android export" no `TODO.md` do repositório.
- **Web (HTML5):** **suportado** (desde 10/07/2026) — e a melhor
  rota para iPhones (sem instalação, sem assinatura). A página
  exportada detecta que o jogo contém eventos Python `execute_code` e
  carrega o motor Pyodide para executá-los com a semântica do IDE;
  toques/cliques despacham como o evento de pressionamento do botão
  esquerdo do mouse e a fila de desenho renderiza no canvas.
  Verificado de ponta a ponta em Chromium sem interface gráfica (o
  tabuleiro renderiza, troca por clique, piscar, deslizar,
  pontuação). Uma ressalva: o motor Python carrega de um CDN, então
  a página precisa de acesso à internet ao abrir — jogos baseados
  apenas em ações (as amostras de labirinto/plataforma) permanecem
  totalmente offline.
- **Zip independente:** não testado com esta amostra.
