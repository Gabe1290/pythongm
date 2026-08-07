# Match-3 — Livello 1

Un gioco puzzle match-3 (tre in fila) minimale e completo. Questo è il
primo esempio pygm2 **scritto nativamente nel formato di progetto
dell'IDE** — gli esempi labirinto e piattaforma sono stati importati
da file `.gmk` di GameMaker 8.x; questo è stato scritto direttamente
per il motore pygm2.

È deliberatamente piccolo: una stanza, un oggetto, nessuno script,
nessun suono. L'intero gioco vive in quattro eventi di un singolo
oggetto controller, il che lo rende l'esempio di riferimento per
l'azione `execute_code` e per il rendering tramite coda di disegno.
Versioni più avanzate (tessere basate su sprite, suono, livelli) sono
pianificate come `match3_2` ecc. — vedi *Roadmap* più sotto.

**Dove si colloca:** `match3_*` è l'ultima (e la più diversa) delle
tre famiglie di esempi — un paradigma diverso, non un passo
incrementale: nessuna azione integrata, nessun oggetto per tessera,
nessuna tessera a livello di stanza. Tutto (stato della griglia,
collisioni, rendering) è guidato direttamente da Python in
`execute_code` invece di essere composto da azioni integrate su molti
oggetti, come fanno `maze_*` e `plateforme_*`. Vedi
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
per la progressione completa.

**Audio e musica:** nessuno — deliberatamente, per il motivo spiegato
sopra. (L'audio diventa possibile a partire da `match3_2`, tramite la
primitiva di coda audio introdotta da quell'esempio.)

## Come si gioca

- **Clicca** su una tessera per selezionarla (contorno bianco), poi
  **clicca su una tessera adiacente** per scambiarle.
- Se lo scambio allinea **3 o più tessere dello stesso colore** in
  riga o colonna, le tessere allineate lampeggiano per un istante,
  vengono distrutte, e le tessere sopra **scivolano verso il basso**
  per riempire il vuoto; nuove tessere cadono dall'alto del tabellone.
- Le reazioni a catena ("cascate") si risolvono ondata dopo ondata,
  ciascuna con la propria animazione di lampeggio e scivolamento.
- Uno scambio che non produce nessun allineamento viene annullato
  immediatamente.
- Ogni tessera distrutta vale **10 punti**; raggiungi **500 punti**
  per vincere.

## Struttura del progetto

| File | Scopo |
| ---- | ------- |
| `project.json` | manifesto del progetto — finestra 800×800, 60 fps (`room_speed`), stanza iniziale `rm_match3` |
| `rooms/rm_match3.json` | l'unica stanza; contiene una istanza di `obj_GridManager` in (0, 0) |
| `objects/obj_GridManager.json` | l'intero gioco: quattro eventi, ciascuno con una singola azione `execute_code` |
| `sprites/spr_red|blue|green|yellow.*` | tessere quadrate 32×32 — **non ancora usate**; riservate al seguito basato su sprite (vedi `CREDITS.txt`) |

Non c'è un oggetto giocatore né un oggetto per tessera: il tabellone è
puro dato (una lista 6×6 di indici colore) posseduto da un'unica
istanza controller invisibile, e tutto ciò che appare a schermo è
disegnato dall'evento `draw` di quel controller tramite la coda di
disegno del motore (`self._draw_queue`).

## Come funziona il codice

Tutto lo stato vive sull'istanza controller (`self.…`), creato
nell'evento `create`:

| Attributo | Significato |
| --------- | ------- |
| `grid` | lista 6×6 di interi 0–3 (indici in `palette`); inizializzata senza allineamenti già esistenti |
| `sel` | cella attualmente selezionata `(gx, gy)` o `None` |
| `marked` | insieme delle celle attualmente allineate e lampeggianti |
| `flash` / `flash_total` | frame rimanenti della fase di lampeggio / la sua durata (36 frame ≈ 0,6 s a 60 fps) |
| `falling` | dizionario `(gx, gy) → pixel` — quanto sopra la propria cella di riposo si trova attualmente ogni tessera scivolante |
| `fall_speed` | velocità di scivolamento in pixel per frame (12 → una riga di 96 px in ~0,13 s) |
| `score`, `target`, `won` | stato del punteggio (vittoria a 500) |
| `find_matches` | funzione ausiliaria (definita in `create`, memorizzata sull'istanza) che esamina la griglia e restituisce l'insieme di tutte le celle allineate |

Il gioco è una piccola macchina a stati guidata dall'evento `step`:

```
idle ──(scambio da clic, allineamento trovato)──▶ FLASH (lampeggio, 36 frame)
                                        │ tessere distrutte, punteggio aggiunto
                                        ▼
                                      FALL (offset si riduce di 12 px/frame)
                                        │ atterrato → rianalisi griglia
                          nuovo allineamento ─┴─ nessun allineamento
                                 │            │
                                 ▼            ▼
                               FLASH        idle
```

- **`create`** — costruisce la griglia iniziale (ripescando ogni
  tessera che completerebbe un allineamento immediato), inizializza lo
  stato sopra, e definisce `find_matches`.
- **`mouse_left_press`** — logica di selezione/deselezione; su uno
  scambio adiacente applica lo scambio, e o arma il lampeggio
  (`marked`, `flash`) oppure annulla. L'input viene ignorato mentre un
  lampeggio o una caduta sono in corso, e dopo che il gioco è stato vinto.
- **`step`** — conta alla rovescia il lampeggio; alla scadenza
  accredita il punteggio, riscrive ogni colonna interessata nel suo
  layout finale, e registra un offset in pixel in `falling` per ogni
  tessera che si è mossa (le tessere sopravvissute ottengono
  `righe_scese × 96`; le tessere di riempimento entrano da sopra il
  tabellone). Finché `falling` non è vuoto, ogni offset si riduce di
  `fall_speed`; quando tutto è atterrato, si rianalizza per allineamenti
  a cascata e o si riarma il lampeggio o si ritorna a idle.
- **`draw`** — disegna il pannello del tabellone, poi ogni tessera a
  `posizione_di_riposo − offset_di_caduta`. Le tessere sopra il bordo
  superiore del tabellone vengono ritagliate (parzialmente emerse) o
  saltate (completamente nascoste), cosicché i riempimenti sembrano
  scivolare da sotto l'intestazione. Le tessere marcate lampeggiano in
  bianco ogni 6 frame e portano un contorno bianco; la selezione, la
  riga del punteggio, le istruzioni e il banner di vittoria vengono
  disegnati per ultimi.

### Cose da modificare

- Dimensione del tabellone: `self.cols` / `self.rows` (le costanti di
  layout `ox`, `oy`, `tile` controllano il posizionamento — un
  tabellone 6×6 di tessere da 96 px si adatta alla finestra 800×800).
- Colori / tipi di tessera: `self.palette` (aggiungi una tupla per
  ottenere un 5° colore; la logica di ripescaggio e il renderer lo
  recepiscono automaticamente, ma aggiorna `random.randrange(4)` in
  `create` e `step`).
- Difficoltà: `self.target` (punti per vincere), `flash_total`,
  `fall_speed`.

## Roadmap (versioni avanzate pianificate)

- **[match3_2](../match3_2/README.md)** — fatto: disegna le tessere
  con sprite invece di rettangoli colorati, aggiunge effetti sonori
  per scambio/allineamento/cascata, e un'animazione di scivolamento
  dello scambio.
- **[match3_3](../match3_3/README.md)** — fatto: un limite di mosse,
  tre stanze come livelli con obiettivo crescente, e tessere speciali
  da allineamenti di 4/5 in fila. Chiude questa roadmap.

Le versioni sono pensate per rispecchiare la progressione maze_1→3:
ognuna è un diff leggibile rispetto alla precedente.

## Stato dell'esportazione

- **Test Game (F5) / desktop:** funziona — il gioco gira sul motore
  pygame standard. Viene testato senza interfaccia grafica in
  esecuzioni smoke in stile CI tramite `tools/smoke_run_samples.py`.
- **Android (.apk) / Mobile (Kivy):** **supportato** (dal 03/07/2026).
  Il motore Kivy esportato renderizza la coda di disegno del gioco
  (rettangoli e testo, con l'asse y convertito nel sistema Kivy
  dal basso verso l'alto), invia i tocchi come evento
  `mouse_left_press` con `mouse_x`/`mouse_y` in coordinate della
  stanza sia su Android (invertendo la trasformazione di scala a
  schermo intero) sia su Kivy desktop, e — poiché questo gioco non ha
  eventi da tastiera — omette l'overlay del D-pad virtuale che
  altrimenti coprirebbe l'angolo in basso a destra del tabellone. Il
  gioco esportato viene testato senza interfaccia grafica in
  `tests/test_kivy_draw_queue_mouse_export.py`, che gioca un turno
  completo scambio → lampeggio → scivolamento attraverso il codice
  generato. Costruire l'effettivo `.apk` richiede inoltre buildozer
  (tramite WSL su Windows) — vedi
  [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md) per la guida
  completa (configurazione, tempi di build, cache per l'uso in
  classe/sessione); le lacune di parità restanti dell'export Kivy che
  *non* riguardano questo gioco sono elencate sotto "Kivy/Android
  export" nel `TODO.md` del repository.
- **Web (HTML5):** **supportato** (dal 10/07/2026) — e la strada
  migliore verso gli iPhone (nessuna installazione, nessuna firma). La
  pagina esportata rileva che il gioco contiene eventi Python
  `execute_code` e carica il runtime Pyodide per eseguirli con la
  semantica dell'IDE; i tocchi/clic vengono inviati come evento di
  pressione del pulsante sinistro del mouse e la coda di disegno
  renderizza sul canvas. Verificato end-to-end in Chromium headless
  (il tabellone si renderizza, scambio con clic, lampeggio,
  scivolamento, punteggio). Un avvertimento: il runtime Python si
  carica da una CDN, quindi la pagina ha bisogno di accesso a internet
  quando viene aperta — i giochi basati solo su azioni (gli esempi
  labirinto/piattaforma) restano completamente offline.
- **Zip autonomo:** non testato con questo esempio.
