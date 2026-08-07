# Labirinto — Livello 3

Un'esplorazione di dungeon in cinque labirinti a griglia preceduta da
una schermata del titolo — il più grande dei tre esempi di labirinto
(17 oggetti / 6 stanze, contro i 9 oggetti / 3 stanze di maze_2.
Mantiene il ciclo raccogli-diamanti-poi-raggiungi-l'obiettivo di
maze_2 e la porta chiusa a chiave bloccata dai diamanti, e aggiunge
tre nuove meccaniche che appaiono progressivamente attraverso le
stanze: un puzzle di spingere blocchi nei buchi (room5), tre
archetipi di mostri in pattuglia che uccidono al contatto (stanze
3–5), e una trappola bomba nascosta che detona un raggio di
esplosione (room4). A differenza di `maze_1`/`maze_2`, questo esempio
**è** un import grezzo di GameMaker 8.x — il suo gemello
`samples/maze_3.gmk` è incluso nel repository (non esiste un file
`.gmk` per `maze_1`/`maze_2`), e il progetto pygm2 accanto ad esso è
il risultato convertito.

**Dove si colloca:** parte della famiglia `maze_*` — GameObject +
sprite più un'**immagine di sfondo** statica per stanza (come
`maze_2`), nessuna tessera a livello di stanza. Vedi
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
per come questo si confronta con `plateforme_*` (aggiunge sfondi a
tessere) e `match3_*` (puro script, nessuna azione integrata).

**Audio e musica:** 8 file audio, e — a differenza dell'insieme
fornito ma silenzioso di `maze_2` — genuinamente collegati: 11 punti
di chiamata `play_sound`/`play_music` su `sound_background` (musica),
`sound_diamond`, `sound_door`, `sound_goal`, `sound_dead`,
`sound_explode`, `sound_hole`, e `sound_push`.

## Come si gioca

- **Schermata del titolo (`room_start`):** premi **SPAZIO** per iniziare.
- Le **frecce direzionali** muovono il giocatore di una cella di
  griglia da 32px alla volta (`test_alignment`/`snap_to_grid`, stesso
  schema di `maze_1`/`maze_2`).
- **Obiettivo:** raccogliere diamanti (`obj_diamond`, +5 punteggio
  ciascuno) e raggiungere l'`obj_goal` di ogni stanza. Le stanze 2–4
  bloccano inoltre l'uscita dietro una `obj_door` chiusa a chiave che
  si autodistrugge solo quando ogni diamante in quella stanza è
  sparito (room3 ha 4 porte che si aprono tutte insieme). Room5
  sostituisce i diamanti con un puzzle di blocchi da spingere:
  cammina contro un `obj_block` per farlo scivolare di una cella, o
  spingilo in un `obj_hole` per riempire la fossa (entrambi vengono
  distrutti).
- **Pericoli:** tre archetipi di mostri pattugliano le stanze 3–5 e
  uccidono al contatto — `monster_all` rimbalza sui muri in una
  qualsiasi delle 4 direzioni, `monster_lr`/`monster_ud` pattugliano
  un singolo asse e invertono al colpo con un muro. Room4 nasconde
  anche una piastra `obj trigger` che, una volta toccata, arma una
  vicina `obj_bomb` trasformandola in `obj_explosion` — la sua
  esplosione di 16 frame distrugge ogni istanza non solida (incluso il
  giocatore) entro un raggio di 64px.
- **Condizione di sconfitta:** toccare un mostro costa una vita
  (`sound_dead` + `set_lives -1` + `restart_room`); raggiungere 0 vite
  mostra la schermata di inserimento del punteggio più alto e riavvia
  il gioco. Toccare l'obiettivo dell'ultima stanza mostra invece un
  messaggio di congratulazioni, assegna +100, e termina la partita
  allo stesso modo.
- **Tasti di debug** vivono su `controller_main`: **R** costa
  istantaneamente una vita e riavvia la stanza; **N**/**P** saltano
  direttamente alla stanza successiva/precedente — utili per testare,
  ma anche un salto di livello in cui un giocatore potrebbe inciampare
  per caso.

## Struttura del progetto

| File | Scopo |
|---|---|
| `project.json` | Manifesto del progetto — impostazioni finestra/stanza e copie di risorse incorporate. Le copie degli oggetti corrispondono esattamente ai loro file collaterali, ma **le copie delle stanze sono obsolete**: ogni voce di stanza incorporata ha 0 istanze e un marcatore `_external_file` — i dati reali delle istanze vivono solo in `rooms/*.json` |
| `rooms/room_start.json` | Schermata del titolo — 1 istanza (`controller_start`) |
| `rooms/room1.json` | Labirinto 1 — 134 istanze (muri, 4 diamanti, obiettivo, giocatore, controller) |
| `rooms/room2.json` | Labirinto 2 — 96 istanze (+20 diamanti, 1 porta chiusa a chiave) |
| `rooms/room3.json` | Labirinto 3 — 105 istanze (+16 diamanti, 4 porte chiuse a chiave, tutti e 3 gli archetipi di mostri, 6 mostri in totale) |
| `rooms/room4.json` | Labirinto 4 — 95 istanze (+14 diamanti, 1 porta, 4 `monster_lr`, 2 coppie trigger/bomba) |
| `rooms/room5.json` | Labirinto 5 — 99 istanze (4 blocchi spingibili, 3 buchi, 2 obiettivi, 2 `monster_lr` — nessun diamante o porta) |
| `objects/*.json` | 17 definizioni di oggetti — verificate rispetto alle copie incorporate di `project.json` e identiche (nessuna obsolescenza). Nota: `objects/obj trigger.json` ha uno spazio letterale nel nome del file |
| `sprites/` | 16 sprite + metadati (vedi Risorse) |
| `sounds/` | 8 file audio, tutti referenziati da almeno un oggetto |
| `backgrounds/` | 2 sfondi (`background_start.png` per la stanza del titolo, `background_main.png` per i labirinti) |
| `CREDITS.txt` | Avviso di licenza delle risorse per questo esempio |

## Oggetti

**Giocatore e controller**

| Oggetto | Ruolo | Eventi chiave |
|---|---|---|
| `obj_person` | Personaggio controllato dal giocatore; movimento a griglia | keyboard (up/down/left/right/nokey), collision_with_obj_block, collision_with_monster_all/_lr/_ud, collision_with_wall_corner |
| `controller_start` | Controller della schermata del titolo; imposta punteggio/vite, avvia la musica | create, keyboard (SPAZIO) |
| `controller_main` | HUD nel labirinto + tasti di debug; disegna punteggio/vite, termina la partita a 0 vite | keyboard (R trucco-riavvio), no_more_lives, draw, keyboard_press (N/P salto stanza) |

**Muri e tessere**

| Oggetto | Ruolo | Eventi chiave |
|---|---|---|
| `wall_corner` | Muro solido base; genitore degli altri due tipi di muro | (nessuno — collisore passivo) |
| `wall_horizontal` | Segmento di muro orizzontale (eredita `wall_corner`) | (nessuno) |
| `wall_vertical` | Segmento di muro verticale (eredita `wall_corner`) | (nessuno) |

**Collezionabili, porte, obiettivi e puzzle di spinta blocchi (room5)**

| Oggetto | Ruolo | Eventi chiave |
|---|---|---|
| `obj_diamond` | Collezionabile; +5 punteggio alla raccolta | destroy, collision_with_obj_person |
| `obj_door` | Cancello chiuso a chiave; si autodistrugge quando ogni diamante nella stanza è sparito | step |
| `obj_goal` | Uscita del livello; avanza le stanze o termina il gioco nell'ultima stanza | collision_with_obj_person |
| `obj_block` | Cassa spingibile; scivola di una cella quando ci si cammina contro, o cade in un buco | collision_with_obj_person |
| `obj_hole` | Fossa; si autodistrugge insieme a qualsiasi blocco spinto dentro | collision_with_obj_block |

**Mostri e trappola bomba (room4)**

| Oggetto | Ruolo | Eventi chiave |
|---|---|---|
| `monster_all` | Rimbalza sui muri in una qualsiasi delle 4 direzioni | create, collision_with_wall_corner |
| `monster_lr` | Pattuglia sinistra-destra, inverte al contatto con un muro | create, collision_with_wall_corner |
| `monster_ud` | Pattuglia su-giù, inverte al contatto con un muro | create, collision_with_wall_corner |
| `obj trigger` | Piastra nascosta; al tocco riproduce il suono di esplosione, trasforma la `obj_bomb` accoppiata in `obj_explosion`, si autodistrugge | collision_with_obj_person |
| `obj_bomb` | Segnaposto inerte che rappresenta una bomba armata fino a quando un trigger si attiva | (nessuno) |
| `obj_explosion` | Esplosione di 16 frame; alla comparsa distrugge le istanze non solide entro 64px, si autodistrugge alla fine dell'animazione | create, animation_end |

## Risorse

16 sprite (per lo più 32×32 singolo frame, precisi al pixel;
`sprite_explosion` è una striscia 1536×96 di 16 frame senza flag
preciso), 2 sfondi, 8 suoni — tutti e 8 i suoni sono referenziati da
almeno un oggetto, a differenza di `maze_2` dove nessuno era
collegato. Licenza/provenienza per le risorse di questo esempio è
**non documentata** — vedi `CREDITS.txt` in questa cartella, che
rimanda al TODO "Remaining maze assets" in `docs/ASSET_LICENSES.md`.
Non presumere CC0 o qualsiasi altra licenza per questi file.

## Cose da modificare

- `sprite_lives` (16×16) è una risorsa registrata che non viene mai
  disegnata — l'azione `draw_lives` di `controller_main` usa in realtà
  `sprite_person` a scala 0,7, lasciando `sprite_lives` orfano (stessa
  categoria del `tiles.json` di `maze_2`).
- L'esplosione della trappola bomba (l'evento `create` di
  `obj_explosion`) distrugge il giocatore tramite un semplice
  `destroy_instance` nel suo controllo del raggio, aggirando il
  percorso `sound_dead`/`set_lives`/`restart_room` che usano i mostri
  — catturare il giocatore lascia la partita in uno stato strano
  invece di una morte/riavvio pulita.
- La velocità dei mostri è hardcoded a `32/6` px/passo su tutti e tre
  gli archetipi mentre il giocatore si muove a `4` — i mostri non sono
  agganciati alla griglia come lo è il giocatore, quindi il loro
  movimento non rimane allineato alle celle nel tempo.
- I tasti di debug `R`/`N`/`P` su `controller_main` sono attivi nel
  controller distribuito (vedi Come si gioca) — varrebbe la pena
  vincolarli dietro un flag di debug se questo esempio venisse
  ulteriormente rifinito.

## Stato dell'esportazione

Coperto dalla suite di smoke-test senza interfaccia grafica
(`tools/smoke_run_samples.py`, che elenca `maze_3` e lo esegue per un
numero fisso di frame con input da tastiera iniettato); non
verificato individualmente per ogni target di esportazione (Kivy/Web).
Esposto nella scheda Welcome dell'IDE come "Maze — Level 3"
(`widgets/welcome_tab.py`).
