# Match-3 — Nível 3

A continuação com limite de movimentos / multi-nível / tiles
especiais de [`match3_2`](../match3_2/README.md) prometida no roteiro
original de match3_1 — a última das três versões match3 planejadas.
Mesma arquitetura em toda parte: sem scripts, o jogo inteiro ainda são
quatro eventos `execute_code` em um único objeto controlador, apenas
colocado em três salas em vez de uma.

**Onde isso se encaixa:** parte da família `match3_*` — script puro
`execute_code`, sem ações integradas, sem tiles no nível da sala,
fechando a progressão descrita em
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays).

**Som e música:** 5 arquivos de som — os 3 de `match3_2`
(`snd_swap`/`match`/`cascade`) mais 2 novos (`snd_special`,
`snd_level_up`), todos usados ativamente via `self._sound_queue`.

## Como jogar

Mesmas regras de troca/combinação/cascata de match3_1 e match3_2, mais:

- Você tem um **número limitado de movimentos** por nível. Um
  movimento só é gasto em uma troca que realmente produz uma
  combinação — uma troca inválida (que desliza de volta) pode ser
  tentada novamente de graça.
- Alcance a **pontuação alvo** do nível antes que os movimentos
  acabem para avançar para a próxima sala. Se acabarem primeiro, o
  nível termina — **clique em qualquer lugar para tentar novamente**
  o mesmo nível do zero.
- **Combine 4 em linha** (exatamente 4) e um dos quatro tiles se
  torna um **especial de limpeza de linha**: uma barra branca o
  marca. Combine-o novamente mais tarde (como parte de qualquer outra
  combinação) e ele limpa toda a sua **linha ou coluna** — qualquer
  direção que a sequência original de 4 tinha.
- **Combine 5 ou mais em linha** e um tile se torna um **especial
  bomba de cor**: um anel branco o marca. Combine-o novamente mais
  tarde e ele limpa **cada tile de uma cor** em todo o tabuleiro.
- Há **3 níveis**, cada um sua própria sala com um alvo mais alto e
  um limite de movimentos mais estreito. Complete o nível 3 para
  vencer o jogo.

## O que muda em relação a match3_2

| match3_2 | match3_3 |
| -------- | -------- |
| Uma sala, movimentos ilimitados, vitória em pontuação fixa | **3 salas** (uma por nível), um **limite de movimentos** por nível, e um **alvo crescente** por nível |
| Uma combinação sempre é destruída completamente | Uma sequência de **4** ou **5+** deixa um **tile especial** em vez de destruir cada célula |
| Sem progressão de nível para nível | Alcançar o alvo chama `self.advance_level()`, que define `self.goto_room_target` para a próxima sala (ou `self.won` no último nível) |

A máquina de estados central de troca/piscar/queda/cascata, o desenho
de tiles sprite, e os gatilhos da fila de som permanecem inalterados
em relação a match3_2 — veja o README daquela amostra para a
descrição completa de `swap_off`/`falling`/`find_matches`.

## Estrutura do projeto

| Arquivo | Propósito |
| ---- | ------- |
| `project.json` | manifesto do projeto — janela 800×800, 60 fps, sala inicial `rm_level1`, `room_order` = os 3 níveis |
| `rooms/rm_level1|2|3.json` | uma sala por nível, cada uma com sua própria instância de `obj_GridManager` em (0, 0) |
| `objects/obj_GridManager.json` | o jogo inteiro: quatro eventos, cada um com uma única ação `execute_code` |
| `sprites/`, `sounds/` | tiles de gema + efeitos, em sua maioria copiados de match3_2 (veja `CREDITS.txt`); `snd_special` e `snd_level_up` são novos |

Ainda não há objeto por tile nem scripts — uma instância controladora
por sala, criada novamente (através da regra usual do GameMaker de
"cada sala tem suas próprias instâncias") toda vez que uma sala é
inserida, o que dá a cada nível uma folha em branco de graça.

## Como o código funciona

### Configuração de nível (novo em `create`)

```python
self.room_order = ['rm_level1', 'rm_level2', 'rm_level3']
level_config = {
    'rm_level1': (300, 20),   # (target score, move limit)
    'rm_level2': (500, 18),
    'rm_level3': (800, 16),
}
```

`create` lê `game.current_room.name`, armazena em `self.room_name`
(necessário porque uma variável local simples definida em um evento
`execute_code` **não** sobrevive a um evento posterior — veja a nota
sobre a armadilha abaixo), e define
`self.target`/`self.moves`/`self.level_num` a partir da tabela acima.

### Movimentos e derrota (novo em `mouse_left_press`)

Uma troca só consome um movimento se `find_matches` disser que ela
realmente vai combinar (`if marks: self.moves = self.moves - 1`),
então uma troca rejeitada que desliza de volta é grátis. Quando
`self.moves` chega a 0 sem atingir o alvo, `step` define
`self.lost = True`; `mouse_left_press` verifica essa bandeira
**primeiro**, antes da guarda de entrada normal, e transforma
qualquer clique em `self.restart_room_flag = True` (a mesma bandeira
que `restart_room` usa), o que reconstrói a sala — e com ela, uma
nova instância de `obj_GridManager` cujo evento `create` reinicia tudo.

### Tiles especiais (novo em `step`)

`find_matches` agora retorna `(marks, runs)` em vez de apenas `marks`
— cada sequência é `(cells_in_order, 'h' ou 'v')`. Ao expirar o
piscar, **antes** de pontuar:

1. Para cada sequência de comprimento ≥ 4, a **célula do meio**
   se torna um tile especial em vez de ser destruída: sequências de
   comprimento 4 recebem `('row',)` ou `('col',)` (correspondendo à
   orientação da sequência); sequências de comprimento 5+ recebem
   `('color', <índice de cor>)`.
2. Para cada célula já marcada que tem uma entrada em `self.special`
   (ou seja, um tile especial acabou de ser capturado nesta
   combinação), seu efeito dispara uma vez: um especial `row`/`col`
   adiciona toda a sua linha/coluna às células que serão limpas; um
   especial `color` adiciona cada célula do tabuleiro de sua cor
   armazenada. Esta é uma **única passagem, não recursiva** — se a
   explosão de um especial capturar outro especial, aquele é
   destruído mas **não** dispara em cadeia seu próprio efeito. (Uma
   simplificação, não um bug — mantém o efeito limitado e fácil de
   raciocinar.)
3. Células especiais recém-criadas estão protegidas de serem
   destruídas na mesma onda, mesmo que uma explosão do passo 2 as
   tivesse capturado.
4. `self.special` é reconstruído do zero a cada onda, seguindo os
   tiles sobreviventes enquanto caem (o loop de queda por coluna
   agora carrega um terceiro elemento de tupla — o tipo especial do
   tile, ou `None` — junto com sua linha e cor), então um tile
   especial ainda não combinado desliza para baixo com a gravidade
   como qualquer outro.

### Avanço de nível (novo em `create`, usado em `step`)

```python
def advance_level():
    idx = self.room_order.index(self.room_name)
    if idx + 1 < len(self.room_order):
        self.goto_room_target = self.room_order[idx + 1]
        self._sound_queue.append('snd_level_up')
    else:
        self.won = True
self.advance_level = advance_level
```

`self.goto_room_target` é a mesma bandeira de instância que a ação
integrada `goto_room` define — o loop principal do jogo já a consulta
a cada quadro, então defini-la diretamente de `execute_code` é
suficiente para disparar uma transição de sala real, nenhuma ação
estruturada necessária. `step` chama `self.advance_level()` assim que
`self.score >= self.target`, e pula qualquer reanálise de cascata
pelo resto daquele quadro se uma troca de sala (ou uma vitória final)
estiver agora pendente, para que uma sala de saída não continue animando.

### Armadilha: closures sobre variáveis locais simples não sobrevivem entre eventos

O ambiente de execução de `execute_code` passa dicionários
**separados** de globals e locals (`exec(code, exec_globals,
exec_locals)`), o que se comporta como o interior de uma função: uma
atribuição simples de nível superior (`room_name = ...`) acaba no
dicionário *locals*, mas um `def` definido nesse mesmo nível superior
resolve suas variáveis livres através do dicionário *globals* quando
é **chamado** mais tarde — o que, para um auxiliar aninhado
armazenado em `self` (como `find_matches`, `arm_swap`, e agora
`advance_level`), sempre acontece a partir de uma chamada
`execute_code` **diferente** com seu próprio dicionário locals novo.
Uma variável local simples referenciada por tal auxiliar levanta um
`NameError` na primeira vez que o auxiliar é realmente invocado de
outro evento — parece correto no evento que o define e falha
silenciosamente até ser disparado mais tarde. A correção é a mesma
que `find_matches` de match3_1/`arm_swap` de match3_2 já modelavam
sem dizer explicitamente: feche apenas sobre `self` (sempre presente
nos globals de cada evento) ou sobre **atributos de instância**
(`self.room_name`, não um `room_name` simples) — nunca sobre uma
variável local simples. Detectado pelo passo de validação com arnês
independente durante o desenvolvimento (veja as notas de metodologia
de auditoria no `CLAUDE.md` do repositório); agora há um teste de
regressão para isso (`tests/test_match3_3_sample.py`).

### `draw`

Mesmo desenho de painel/tabuleiro/seleção/linha de pontuação/banner
de vitória que match3_2, mais: uma linha de HUD para número do nível
e movimentos restantes, uma sobreposição de barra ou anel branco
sobre o sprite de um tile especial (pulada enquanto o tile está no
meio do piscar), e um banner "OUT OF MOVES — click to retry" quando `self.lost`.

### Coisas para ajustar

- Dificuldade por nível: a tabela `level_config` em `create`
  (pontuação alvo, limite de movimentos) — adicione uma quarta
  entrada e uma quarta sala para estender a sequência.
- Raio de explosão dos tiles especiais: os ramos `row`/`col`/`color`
  no loop de ativação de `step`.
- Tudo que match3_2 já expunha (tamanho do tabuleiro, velocidade de
  troca/queda, volumes de som).

## Roteiro

Isso fecha o roteiro original de três partes de match3_1
(match3_1 → match3_2 → match3_3). Nenhuma outra versão planejada.

## Status da exportação

- **Test Game (F5) / desktop:** funciona — verificado de ponta a
  ponta com uma execução real do `GameRunner` injetando um clique
  real do mouse através do caminho de eventos pygame padrão:
  combinação forçada de 4 em linha → tile especial criado → alvo
  alcançado → **a sala realmente mudou para `rm_level2`** com uma
  nova instância (`level_num == 2`, pontuação/movimentos reiniciados).
- **Android (.apk) / Mobile (Kivy):** depende da mesma maquinaria
  `asset_paths.py` / `_drain_sound_queue` / fallback sprite-por-nome
  que match3_2 adicionou e verificou — esta amostra não exercita
  nada novo nessa frente (nenhum novo tipo de comando de desenho,
  nenhum novo tipo de ação; `goto_room` via bandeira funciona
  identicamente no loop da cena exportada para Kivy, que já consulta
  as mesmas bandeiras de instância a cada quadro). Construir o `.apk`
  real requer adicionalmente buildozer (via WSL no Windows) — veja
  [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Web (HTML5):** mesmo raciocínio — nenhuma nova primitiva de fila
  de desenho ou fila de som além do que match3_2 já havia comprovado
  neste destino.
- **Zip independente:** não testado com esta amostra.
