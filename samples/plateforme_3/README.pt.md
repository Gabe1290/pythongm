# Platform — Nível 3

Um plataforma de rolagem lateral importado do GameMaker 8.x
(`samples/plateforme_3.gmk`). É de longe a maior das três amostras de
plataforma: 2 objetos (plateforme_1) → 4 objetos (plateforme_2) →
**15 objetos** aqui, adicionando monstros terrestres e voadores em
patrulha (com morte ao pisar e variantes de cadáver/respingo geradas
em tempo de execução), um perigo de morte instantânea invisível, dois
tipos de colecionáveis, e um objeto de saída que avança para a
próxima sala ou mostra a tabela de recordes e reinicia.

**Onde isso se encaixa:** parte da família `plateforme_*` — como
`plateforme_2`, usa um **fundo em tiles** (125 pedaços de tiles sob
os objetos de tijolo sólido, mais a imagem em degradê
`fond_degrade`), o passo que esta família adiciona além de `maze_*`.
Veja
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para a progressão completa.

**Som e música:** 4 arquivos de som, genuinamente conectados: 7
pontos de chamada `play_sound` para `son_bonus` (coleta),
`son_monstre_mort` (morte ao pisar), `son_personnage_mort` (morte do
jogador), e `son_niveaufini` (nível completo).

## Como jogar

- **Seta esquerda/direita** — move Pingus (`obj_pingus`) esquerda/direita.
- **Seta cima** — pulo, mas apenas enquanto parado sobre algo sólido
  (verificado um pixel abaixo do jogador).
- **Objetivo** — colete os `obj_bonus` (+5 de pontuação) e os
  `obj_power` (+20 de pontuação) enquanto atravessa `niveau_01` para
  alcançar `obj_sortie`; tocá-lo reproduz uma melodia e ou avança
  para uma próxima sala (nenhuma existe nesta amostra, então recai
  no ramo de tabela-de-recordes/reinício) ou mostra a tabela de
  recordes e reinicia o jogo.
- **Monstros** — pousar em cima de um `obj_monstre` ou
  `obj_monstre_volant` (`vspeed > 0` e acima do monstro) o mata e
  concede 50 pontos; atingir um pelo lado ou por baixo custa uma vida
  e reinicia a sala. Nota: a colisão com `obj_monstre_volant` não tem
  efeito (o monstro voador não pode machucar nem ser machucado) até
  que `obj_power` tenha sido coletado — veja Coisas para ajustar.
- **Condição de derrota** — tocar em `obj_mortel` (uma zona de morte
  instantânea invisível) ou em um monstro do jeito errado custa uma
  vida e reinicia a sala; ficar sem vidas (`no_more_lives`) mostra a
  tabela de recordes e reinicia o jogo inteiro. Vidas iniciais: 3
  (configurações de `project.json`).

## Estrutura do projeto

| Arquivo | Propósito |
| --- | --- |
| `project.json` | Manifesto do projeto — configurações de janela/sala, cópias de recursos incorporadas. |
| `rooms/niveau_01.json` | A única sala: 800×640, 194 instâncias + 125 tiles de fundo. Fonte da verdade para o conteúdo da sala (a lista `instances` incorporada de `project.json` está vazia, mesmo padrão de plateforme_2). |
| `objects/*.json` | Arquivos colaterais por objeto para todos os 15 objetos; idênticos às cópias incorporadas em `project.json` até esta data (verificado byte a byte, diferente do arquivo de sala de plateforme_2). |
| `sprites/` | 18 recursos sprite (tiras de caminhada/voo, sprites de morte, blocos de plataforma, colecionáveis, saída, marcador). |
| `sounds/` | 4 efeitos sonoros (morte de monstro, morte do jogador, coleta de bônus, nível completo). |
| `backgrounds/` | Conjunto de tiles de neve (`tuiles_neige.png`, fonte automática para os 125 tiles da sala) e um degradê vertical (`fond_degrade.png`) como fundo de sala. |
| `CREDITS.txt` | Aviso de licenciamento para a arte de sprites/fundo (veja Recursos abaixo). |

## Objetos

15 objetos, agrupados por papel. Contagens de posicionamento na sala
(de 194 instâncias) mostradas onde o objeto aparece em `niveau_01`;
objetos "gerados em tempo de execução" só aparecem via
`change_instance` durante o jogo.

| Objeto | Papel | Eventos-chave |
| --- | --- | --- |
| `obj_pingus` | Jogador — movimento, pulo, gravidade, todo o manuseio de colisão/derrota/vitória | create, step, keyboard (left/right/up), keyboard_release, collision_with_obj_brique/obj_monstre/obj_monstre_volant/obj_mortel/obj_bonus/obj_power/obj_sortie/obj_marqueur, game_start, no_more_lives |
| `obj_brique` | Bloco de plataforma sólida base, 32×32 (109 colocados) | nenhum (apenas bandeira sólida) |
| `obj_brique_h` | Variante larga de plataforma, 32×16, filha de `obj_brique` (15 colocados) | nenhum |
| `obj_brique_v` | Variante estreita de plataforma, 16×32, filha de `obj_brique`; definida mas não colocada em `niveau_01` | nenhum |
| `obj_brique_c` | Pequena variante de plataforma, 16×16, filha de `obj_brique` (1 colocado) | nenhum |
| `obj_monstre` | Monstro terrestre — patrulha esquerda/direita, inverte ao contato com parede (3 colocados) | create, collision_with_obj_brique |
| `obj_monstre_mort` | Cadáver de monstro gerado em tempo de execução após uma morte ao pisar; herda `obj_brique` (torna-se um degrau sólido) | create |
| `obj_monstre_volant` | Monstro voador — patrulha para a direita, ricocheteia em paredes (2 colocados) | create, collision_with_obj_brique |
| `obj_monstre_volant_mort` | Cadáver de monstro voador gerado em tempo de execução; cai com gravidade limitada, pousa em plataformas/marcadores | step, collision_with_obj_brique, collision_with_obj_marqueur |
| `obj_mortel` | Zona de perigo de morte instantânea invisível (4 colocadas) | nenhum (manuseado a partir do evento de colisão de `obj_pingus`) |
| `obj_splat` | Animação de morte do jogador gerada em tempo de execução, reinicia a sala ao final da animação | create, animation_end |
| `obj_bonus` | Colecionável menor, +5 de pontuação, quadro de repouso aleatório (52 colocados) | create |
| `obj_power` | Colecionável maior, +20 de pontuação; também determina se monstros voadores podem machucar/ser mortos (1 colocado) | create |
| `obj_sortie` | Saída do nível — reproduz uma melodia, depois próxima sala ou tabela de recordes + reinício (1 colocada) | nenhum (manuseado a partir do evento de colisão de `obj_pingus`) |
| `obj_marqueur` | Marcador de design de sala invisível e não sólido; colisões não têm efeito explicitamente (5 colocados) | nenhum |

## Recursos

18 sprites, 4 sons, 2 fundos. A arte de sprites/fundos é adaptada do
projeto Pingus (GPL-3.0-or-later) — veja `CREDITS.txt` para a
atribuição completa e os termos de licença; este README não reafirma
nem estende essas declarações.

## Coisas para ajustar

- O teste de pisão entre `obj_pingus` e
  `obj_monstre`/`obj_monstre_volant` costumava ser
  `vspeed > 0 and y < other.y+8`, que uma queda rápida podia superar
  (a janela de 8px era verificada contra a posição *após o
  movimento*) e custava uma vida no que parecia uma pisão limpa.
  Agora é `vspeed > 0 and y - vspeed < other.y+8`, que verifica a
  janela contra a posição prévia ao movimento em vez disso.
- O colecionável `obj_power` condiciona silenciosamente toda
  interação com `obj_monstre_volant` (via um
  `if_object_exists(obj_power, not_flag=true)` ao redor da lógica de
  pisão/morte em `obj_pingus`) — valeria a pena torná-lo visível para
  os jogadores (ex.: uma mudança de sprite/paleta) em vez de uma
  regra invisível.
- A velocidade horizontal do jogador é um `hspeed = 4` fixo; o
  impulso de pulo é `vspeed = -10`; a gravidade de queda é `0,5` com
  um teto de velocidade terminal em `vspeed = 24`.
- O tamanho da sala é 800×640 a `room_speed = 30`.

## Status da exportação

Esta amostra está listada na lista `SAMPLES` de
`tools/smoke_run_samples.py`, então recebe uma passagem smoke sem
interface gráfica (o loop de jogo real executado por ~180 quadros com
entrada de teclado injetada) a cada execução daquele arnês. Nenhuma
verificação por destino de exportação específico (Kivy/HTML5) foi
feita especificamente para esta amostra. Está exposta na aba Welcome
do IDE como "Platform — Level 3" (`widgets/welcome_tab.py`).
