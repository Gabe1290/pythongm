# Match-3 — Livello 2

Il seguito animato basato su sprite di [`match3_1`](../match3_1/README.md),
promesso nella Roadmap di quell'esempio: stesso tabellone e stesso
punteggio, ora disegnato con veri sprite di gemme invece di rettangoli
colorati, con un'animazione di scivolamento dello scambio ed effetti
sonori per scambio/allineamento/cascata. Ancora una stanza, un
oggetto, nessuno script — l'intero gioco è ancora quattro eventi
`execute_code` su un singolo oggetto controller.

**Dove si colloca:** parte della famiglia `match3_*` — puro script
`execute_code`, nessuna azione integrata, nessuna tessera a livello di
stanza. Vedi
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
per come questo differisce dall'approccio ad azioni integrate e
multi-oggetto di `maze_*`/`plateforme_*`.

**Audio e musica:** 3 file audio (`snd_swap`, `snd_match`,
`snd_cascade`), tutti attivamente usati — messi in coda da
`execute_code` tramite `self._sound_queue` (vedi sotto), non l'azione
`play_sound`.

## Come si gioca

Come in match3_1:

- **Clicca** su una tessera per selezionarla (contorno bianco), poi
  **clicca su una tessera adiacente** per scambiarle. Lo scambio ora
  **scivola** al suo posto invece di scattare istantaneamente.
- Se lo scambio allinea **3 o più tessere dello stesso colore** in
  riga o colonna, le tessere allineate lampeggiano per un istante,
  vengono distrutte, e le tessere sopra **scivolano verso il basso**
  per riempire il vuoto; nuove tessere cadono dall'alto del tabellone.
  Le reazioni a catena ("cascate") si risolvono ondata dopo ondata.
- Uno scambio che non produce nessun allineamento **scivola
  indietro** alla sua posizione originale invece di scattare indietro.
- Ogni tessera distrutta vale **10 punti**; raggiungi **500 punti**
  per vincere.
- Ogni tentativo di scambio riproduce un clic; un allineamento
  riuscito riproduce un carillon, e ogni cascata aggiuntiva nella
  stessa combo riproduce un carillon più brillante e ascendente.

## Cosa cambia rispetto a match3_1

| match3_1 | match3_2 |
| -------- | -------- |
| Tessere disegnate come rettangoli colorati pieni | Tessere disegnate come **sprite** di gemme (comando coda di disegno in stile `draw_sprite`), una forma per colore per l'accessibilità ai daltonici |
| Lo scambio si applica istantaneamente, gli allineamenti si valutano subito | Lo scambio **scivola** al suo posto per primo (~4 frame); uno scambio non valido scivola indietro invece di scattare |
| Nessun audio | **Effetti sonori** per scambio/allineamento/cascata, messi in coda da `execute_code` tramite la nuova primitiva `self._sound_queue` (vedi sotto) |

La logica del tabellone stessa (modello griglia, ricerca allineamenti,
caduta a cascata, punteggio, condizione di vittoria) è invariata
rispetto a match3_1 — è un diff genuinamente leggibile, non una riscrittura.

## Struttura del progetto

| File | Scopo |
| ---- | ------- |
| `project.json` | manifesto del progetto — finestra 800×800, 60 fps, stanza iniziale `rm_match3` |
| `rooms/rm_match3.json` | l'unica stanza; contiene una istanza di `obj_GridManager` in (0, 0) |
| `objects/obj_GridManager.json` | l'intero gioco: quattro eventi, ciascuno con una singola azione `execute_code` |
| `sprites/spr_gem_red|blue|green|yellow.png` | tessere gemma 88×88 (vedi `CREDITS.txt`) — dimensionate per adattarsi esattamente dove prima si trovava il riempimento a rettangolo di match3_1, poiché `draw_sprite` disegna a dimensione nativa senza scalatura |
| `sounds/snd_swap|match|cascade.wav` | brevi toni sintetizzati (vedi `CREDITS.txt`) |

## Come funziona il codice

Lo stato e la macchina a stati `step` sono gli stessi di match3_1
(`grid`, `sel`, `marked`, `flash`/`flash_total`, `falling`/`fall_speed`,
`score`, `target`, `won`, `find_matches`) — vedi quella README per la
descrizione completa. Nuovo stato aggiunto per questa versione:

| Attributo | Significato |
| --------- | ------- |
| `sprite_names` | `['spr_gem_red', 'spr_gem_blue', 'spr_gem_green', 'spr_gem_yellow']`, indicizzato allo stesso modo in cui era `palette` in match3_1 |
| `swap_off` | dizionario `(gx, gy) → (dx, dy)` offset in pixel per lo scivolamento di scambio in corso; decade a `(0, 0)` a `swap_speed` px/frame, la stessa tecnica di riduzione-a-riposo che `falling` già usa per le cascate, generalizzata a due assi |
| `swap_phase` | `None` / `'forward'` (scivolando nella posizione scambiata) / `'back'` (uno scambio rifiutato che scivola indietro nelle sue celle originali) |
| `last_swap` | `(gx, gy, sx, sy)` — le due celle coinvolte nello scambio in corso, così `step` può ripristinarle senza bisogno di stato di chiusura |
| `pending_marks` | l'insieme di allineamenti calcolato subito dopo uno scambio, mantenuto finché l'animazione di scivolamento non finisce affinché il lampeggio non inizi a metà dello scivolamento |
| `arm_swap(a, b)` | funzione ausiliaria (definita in `create`, memorizzata sull'istanza come `find_matches`) che imposta `swap_off` per entrambe le celle solo dalle loro posizioni — richiamarla di nuovo con le stesse due celle produce l'animazione inversa, il che fornisce gratuitamente lo scivolamento di ripristino |

Flusso aggiornato:

```
clic su tessera adiacente
  → griglia scambiata immediatamente (dati), pending_marks calcolato
  → swap_off armato (forward) — le tessere scivolano nelle nuove celle
       │
       ▼ (lo scivolamento si assesta)
  pending_marks?
    sì → arma il lampeggio (lampeggia → distrugge → cade → rianalizza, come in match3_1)
    no  → scambia indietro la griglia, riarma swap_off con le STESSE due celle (phase='back')
             │
             ▼ (lo scivolamento si assesta)
          idle
```

- **`create`** — stessa inizializzazione griglia di match3_1, più
  `sprite_names`, `swap_off`/`swap_speed`/`swap_phase`/`last_swap`/
  `pending_marks`, e la funzione ausiliaria `arm_swap`.
- **`mouse_left_press`** — la logica di selezione è invariata; uno
  scambio adiacente valido ora applica lo scambio nella griglia,
  calcola `pending_marks`, arma lo scivolamento in avanti, e mette in
  coda `snd_swap`.
- **`step`** — i blocchi di lampeggio/caduta sono invariati rispetto a
  match3_1 (mettono ancora in coda `snd_cascade` su un nuovo
  allineamento concatenato); un nuovo blocco `elif self.swap_off:`
  fa decadere lo scivolamento e, una volta assestato, o arma il
  lampeggio (mettendo in coda `snd_match`) o avvia lo scivolamento di ripristino.
- **`draw`** — stesso disegno di pannello/tabellone/selezione/
  punteggio/istruzioni/banner di vittoria di match3_1, ma ogni tessera
  è ora un comando coda di disegno
  `{'type': 'sprite', 'sprite_name': ..., 'x': ..., 'y': ...}` invece
  di un rettangolo pieno (ancora sostituito da un semplice rettangolo
  bianco pieno durante il lampeggio della tessera marcata, esattamente
  come faceva match3_1), spostato di `swap_off` combinato con `falling`.

### La primitiva `self._sound_queue`

`execute_code` ha un oggetto `game` vivo solo sul runtime pygame
desktop — sia il runtime esportato Kivy sia il runtime Web/Pyodide
legano `game = None` in quello scope, quindi `game.sounds[...].play()`
(la cosa ovvia da provare) funziona solo su desktop. Questo esempio è
ciò che ha motivato l'aggiunta di una vera primitiva cross-platform:
l'`execute_code` di qualsiasi evento può fare

```python
self._sound_queue.append('snd_swap')
# oppure, per un volume non predefinito:
self._sound_queue.append({'sound': 'snd_swap', 'volume': 0.5})
```

e questo si riproduce identicamente su tutti e tre i target:

- **Desktop** — `ActionExecutor.execute_event` la svuota e la
  riproduce (tramite `game.sounds[...]`) subito dopo ogni evento, non
  solo `draw`.
- **Export Kivy** — `GameObject._drain_sound_queue` (generato in
  `base_object.py`) risolve il nome tramite un `asset_paths.py`
  generato (`SOUND_PATHS`) e chiama l'helper `play_sound()` esistente;
  svuotato una volta per frame per ogni istanza viva dal ciclo
  `update()` della scena, quindi funziona anche per oggetti senza
  evento `draw`.
- **Web (Pyodide)** — il bootstrap Python restituisce eventuali suoni
  in coda nella patch JSON insieme alla coda di disegno; `engine.js`
  li riproduce come veri elementi `<audio>` attraverso lo stesso
  percorso audio a pool già usato dall'azione strutturata `play_sound`.

Lo stesso divario di risoluzione per nome esisteva per i comandi in
stile `draw_sprite` inviati da `execute_code` grezzo (il rendering
delle tessere di questo esempio) — il renderer della coda di disegno
di Kivy prima poteva risolvere uno sprite solo da un `sprite_path`
incorporato al momento della generazione del codice per azioni
*strutturate*, quindi un dizionario
`{'type': 'sprite', 'sprite_name': ...}` scritto a mano non veniva
renderizzato lì silenziosamente. Corretto allo stesso modo:
`asset_paths.py` ora porta anche `SPRITE_PATHS`, e il caso `'sprite'`
della coda di disegno di Kivy ricade su di esso per nome quando non è
presente un percorso pre-risolto.

### Cose da modificare

Stesse manopole di match3_1 (`self.cols`/`self.rows`, `self.palette`,
`self.target`, `flash_total`, `fall_speed`), più:

- Velocità dell'animazione di scambio: `self.swap_speed` (px/frame; 24
  → ~4 frame per scivolamento con `tile=96`).
- Volume del suono: passa un dizionario
  `{'sound': ..., 'volume': ...}` invece di un nome nudo a
  `self._sound_queue.append(...)`.

## Roadmap

**[match3_3](../match3_3/README.md)** — fatto: un limite di mosse, tre
stanze come livelli con obiettivo crescente, e tessere speciali (bonus
di 4/5 in fila). Chiude la roadmap originale di match3_1.

## Stato dell'esportazione

- **Test Game (F5) / desktop:** funziona — verificato end-to-end con
  un'esecuzione reale di `GameRunner` che inietta un vero clic del
  mouse attraverso il normale percorso di eventi pygame (scambio →
  allineamento → cascata → punteggio, con veri richiami a
  `pygame.mixer.Sound.play()` osservati).
- **Android (.apk) / Mobile (Kivy):** **supportato.** Verificato che
  l'export compili in modo pulito, che `asset_paths.py` porti i
  corretti `SPRITE_PATHS`/`SOUND_PATHS`, e che le immagini sprite/file
  audio siano copiate in `assets/images`/`assets/sounds`. Costruire
  l'effettivo `.apk` richiede inoltre buildozer (tramite WSL su
  Windows) — vedi [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Web (HTML5):** **supportato.** Il bootstrap Pyodide della pagina
  esportata svuota `self._sound_queue` nello stesso round-trip JSON
  della coda di disegno; verificato che il bootstrap generato compili
  e trasferisca correttamente sia i comandi di disegno sia i suoni in
  coda sotto CPython puro (nessun browser necessario per questo
  controllo — l'avvio in-browser di Pyodide non è di per sé testato
  dalla suite automatica, stesso avvertimento di match3_1). Richiede
  accesso a internet al primo caricamento (Pyodide si carica da una CDN).
- **Zip autonomo:** non testato con questo esempio.
