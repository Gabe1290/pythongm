# Match-3 — Livello 3

Il seguito con limite di mosse / multi-livello / tessere speciali di
[`match3_2`](../match3_2/README.md) promesso nella Roadmap originale
di match3_1 — l'ultima delle tre versioni match3 pianificate. Stessa
architettura ovunque: nessuno script, l'intero gioco è ancora quattro
eventi `execute_code` su un singolo oggetto controller, solo
posizionato in tre stanze invece di una.

**Dove si colloca:** parte della famiglia `match3_*` — puro script
`execute_code`, nessuna azione integrata, nessuna tessera a livello di
stanza, chiudendo la progressione descritta in
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays).

**Audio e musica:** 5 file audio — i 3 di `match3_2`
(`snd_swap`/`match`/`cascade`) più 2 nuovi (`snd_special`,
`snd_level_up`), tutti attivamente usati tramite `self._sound_queue`.

## Come si gioca

Stesse regole di scambio/allineamento/cascata di match3_1 e match3_2, più:

- Hai un **numero limitato di mosse** per livello. Una mossa viene
  spesa solo su uno scambio che produce effettivamente un
  allineamento — uno scambio non valido (che scivola indietro) può
  essere ritentato gratuitamente.
- Raggiungi il **punteggio obiettivo** del livello prima che finiscano
  le mosse per avanzare alla stanza successiva. Se finiscono prima, il
  livello termina — **clicca ovunque per riprovare** lo stesso livello
  da capo.
- **Allinea 4 in fila** (esattamente 4) e una delle quattro tessere
  diventa una **speciale per eliminazione di riga**: una barra bianca
  la contrassegna. Allineala di nuovo più tardi (come parte di
  qualsiasi altro allineamento) e cancella la sua **intera riga o
  colonna** — qualunque direzione avesse la sequenza originale di 4.
- **Allinea 5 o più in fila** e una tessera diventa una **speciale
  bomba di colore**: un anello bianco la contrassegna. Allineala di
  nuovo più tardi e cancella **ogni tessera di un colore** su tutto il
  tabellone.
- Ci sono **3 livelli**, ciascuno la sua stanza con un obiettivo più
  alto e un limite di mosse più stretto. Completa il livello 3 per
  vincere il gioco.

## Cosa cambia rispetto a match3_2

| match3_2 | match3_3 |
| -------- | -------- |
| Una stanza, mosse illimitate, vittoria a un punteggio fisso | **3 stanze** (una per livello), un **limite di mosse** per livello, e un **obiettivo crescente** per livello |
| Un allineamento viene sempre distrutto completamente | Una sequenza di **4** o **5+** lascia una **tessera speciale** invece di distruggere ogni cella |
| Nessuna progressione da livello a livello | Raggiungere l'obiettivo chiama `self.advance_level()`, che imposta `self.goto_room_target` sulla stanza successiva (o `self.won` all'ultimo livello) |

La macchina a stati principale di scambio/lampeggio/caduta/cascata, il
disegno delle tessere sprite, e i trigger della coda audio sono
altrimenti invariati rispetto a match3_2 — vedi la README di quell'esempio
per la descrizione completa di `swap_off`/`falling`/`find_matches`.

## Struttura del progetto

| File | Scopo |
| ---- | ------- |
| `project.json` | manifesto del progetto — finestra 800×800, 60 fps, stanza iniziale `rm_level1`, `room_order` = tutti e 3 i livelli |
| `rooms/rm_level1|2|3.json` | una stanza per livello, ciascuna con la propria istanza di `obj_GridManager` in (0, 0) |
| `objects/obj_GridManager.json` | l'intero gioco: quattro eventi, ciascuno con una singola azione `execute_code` |
| `sprites/`, `sounds/` | tessere gemma + effetti, per lo più copiati da match3_2 (vedi `CREDITS.txt`); `snd_special` e `snd_level_up` sono nuovi |

Non c'è ancora un oggetto per tessera né script — una istanza
controller per stanza, creata di nuovo (tramite la solita regola di
GameMaker "ogni stanza ha le proprie istanze") ogni volta che si entra
in una stanza, il che dà gratuitamente a ogni livello una lavagna pulita.

## Come funziona il codice

### Impostazione livello (nuovo in `create`)

```python
self.room_order = ['rm_level1', 'rm_level2', 'rm_level3']
level_config = {
    'rm_level1': (300, 20),   # (target score, move limit)
    'rm_level2': (500, 18),
    'rm_level3': (800, 16),
}
```

`create` legge `game.current_room.name`, lo memorizza in
`self.room_name` (necessario perché una semplice variabile locale
definita in un evento `execute_code` **non** sopravvive in un evento
successivo — vedi la nota sulla trappola sotto), e imposta
`self.target`/`self.moves`/`self.level_num` dalla tabella sopra.

### Mosse e sconfitta (nuovo in `mouse_left_press`)

Uno scambio consuma una mossa solo se `find_matches` dice che
produrrà effettivamente un allineamento
(`if marks: self.moves = self.moves - 1`), quindi uno scambio
rifiutato che scivola indietro è gratuito. Quando `self.moves`
raggiunge 0 senza raggiungere l'obiettivo, `step` imposta
`self.lost = True`; `mouse_left_press` controlla quel flag **per
primo**, prima della normale guardia di input, e trasforma qualsiasi
clic in `self.restart_room_flag = True` (lo stesso flag che usa
`restart_room`), che ricostruisce la stanza — e con essa, una nuova
istanza di `obj_GridManager` il cui evento `create` reimposta tutto.

### Tessere speciali (nuovo in `step`)

`find_matches` ora restituisce `(marks, runs)` invece di solo `marks`
— ogni sequenza è `(cells_in_order, 'h' o 'v')`. Alla scadenza del
lampeggio, **prima** di assegnare il punteggio:

1. Per ogni sequenza di lunghezza ≥ 4, la **cella centrale** diventa
   una tessera speciale invece di essere distrutta: le sequenze di
   lunghezza 4 ottengono `('row',)` o `('col',)` (corrispondente
   all'orientamento della sequenza); le sequenze di lunghezza 5+
   ottengono `('color', <indice colore>)`.
2. Per ogni cella già marcata che ha una voce in `self.special` (cioè
   una tessera speciale è appena stata catturata in *questo*
   allineamento), il suo effetto si attiva una volta: una speciale
   `row`/`col` aggiunge l'intera riga/colonna alle celle da cancellare;
   una speciale `color` aggiunge ogni cella sul tabellone del suo
   colore memorizzato. Questo è un **singolo passaggio, non
   ricorsivo** — se l'esplosione di una speciale cattura un'altra
   speciale, quella viene distrutta ma **non** attiva a catena il
   proprio effetto. (Una semplificazione, non un bug — mantiene
   l'effetto limitato e facile da ragionare.)
3. Le celle speciali appena create sono protette dalla distruzione
   nella stessa ondata, anche se un'esplosione dal passo 2 le avrebbe catturate.
4. `self.special` viene ricostruito da zero ogni ondata, seguendo le
   tessere sopravvissute mentre cadono (il ciclo di caduta per colonna
   ora porta un terzo elemento di tupla — il tipo speciale della
   tessera, o `None` — insieme alla sua riga e colore) così una
   tessera speciale non ancora allineata scivola giù con la gravità
   come tutte le altre.

### Avanzamento di livello (nuovo in `create`, usato da `step`)

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

`self.goto_room_target` è lo stesso flag di istanza che imposta
l'azione integrata `goto_room` — il ciclo principale del gioco lo
interroga già ogni frame, quindi impostarlo direttamente da
`execute_code` è sufficiente per innescare una vera transizione di
stanza, nessuna azione strutturata necessaria. `step` chiama
`self.advance_level()` appena `self.score >= self.target`, e salta
qualsiasi rianalisi a cascata per il resto di quel frame se un cambio
di stanza (o una vittoria finale) è ora in sospeso, così una stanza in
uscita non continua ad animarsi.

### Trappola: le chiusure su semplici variabili locali non sopravvivono tra eventi

L'ambiente di esecuzione di `execute_code` passa dizionari **separati**
di globals e locals (`exec(code, exec_globals, exec_locals)`), il che
si comporta come l'interno di una funzione: un'assegnazione semplice
di livello superiore (`room_name = ...`) finisce nel dizionario
*locals*, ma un `def` definito allo stesso livello superiore risolve
le sue variabili libere tramite il dizionario *globals* quando viene
**chiamato** più tardi — il che, per un helper annidato memorizzato su
`self` (come `find_matches`, `arm_swap`, e ora `advance_level`),
avviene sempre da una chiamata `execute_code` **diversa** con il
proprio dizionario locals nuovo. Una variabile locale nuda a cui fa
riferimento un tale helper solleva un `NameError` la prima volta che
l'helper viene effettivamente invocato da un altro evento — sembra
corretto nell'evento che lo definisce e fallisce silenziosamente fino
a quando non viene attivato più tardi. La correzione è quella che
`find_matches` di match3_1/`arm_swap` di match3_2 avevano già
modellato senza dirlo esplicitamente: chiudi solo su `self` (sempre
presente nei globals di ogni evento) o su **attributi di istanza**
(`self.room_name`, non una `room_name` nuda) — mai su una variabile
locale nuda. Individuato dal passo di validazione con harness
standalone durante lo sviluppo (vedi le note sulla metodologia di
audit nel `CLAUDE.md` del repository); ora c'è un test di regressione
per questo (`tests/test_match3_3_sample.py`).

### `draw`

Stesso disegno di pannello/tabellone/selezione/riga punteggio/banner
di vittoria di match3_2, più: una riga HUD per numero di livello e
mosse rimanenti, una sovrapposizione a barra o anello bianco sopra lo
sprite di una tessera speciale (saltata mentre la tessera è a metà
lampeggio), e un banner "OUT OF MOVES — click to retry" quando `self.lost`.

### Cose da modificare

- Difficoltà per livello: la tabella `level_config` in `create`
  (punteggio obiettivo, limite di mosse) — aggiungi una quarta voce e
  una quarta stanza per estendere la sequenza.
- Raggio dell'esplosione delle tessere speciali: i rami
  `row`/`col`/`color` nel ciclo di attivazione di `step`.
- Tutto ciò che match3_2 già esponeva (dimensione tabellone, velocità
  scambio/caduta, volumi audio).

## Roadmap

Questo chiude la roadmap originale in tre parti di match3_1
(match3_1 → match3_2 → match3_3). Nessuna ulteriore versione pianificata.

## Stato dell'esportazione

- **Test Game (F5) / desktop:** funziona — verificato end-to-end con
  un'esecuzione reale di `GameRunner` che inietta un vero clic del
  mouse attraverso il normale percorso di eventi pygame: allineamento
  forzato di 4 in fila → tessera speciale creata → obiettivo
  raggiunto → **la stanza è effettivamente passata a `rm_level2`** con
  una nuova istanza (`level_num == 2`, punteggio/mosse reimpostati).
- **Android (.apk) / Mobile (Kivy):** si affida agli stessi meccanismi
  `asset_paths.py` / `_drain_sound_queue` / fallback sprite-per-nome
  che match3_2 ha aggiunto e verificato — questo esempio non testa
  nulla di nuovo su quel fronte (nessun nuovo tipo di comando di
  disegno, nessun nuovo tipo di azione; `goto_room` tramite flag
  funziona identicamente nel ciclo della scena esportata Kivy, che già
  interroga gli stessi flag di istanza ogni frame). Costruire
  l'effettivo `.apk` richiede inoltre buildozer (tramite WSL su
  Windows) — vedi [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Web (HTML5):** stesso ragionamento — nessuna nuova primitiva di
  coda di disegno o coda audio oltre a quanto match3_2 aveva già
  dimostrato su questo target.
- **Zip autonomo:** non testato con questo esempio.
