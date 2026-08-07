# Labirinto — Livello 2

Un gioco di labirinto a griglia visto dall'alto con due labirinti
giocabili più una schermata del titolo: raccogli caramelle per punti,
poi raggiungi l'uscita per avanzare. Costruisce sul ciclo
labirinto/obiettivo a stanza singola di `maze_1` con una schermata
iniziale, un collezionabile (caramella con punteggio), e una porta
chiusa a chiave che si apre solo quando le caramelle della stanza sono
tutte raccolte. Questo è un progetto pygm2 nativo (nessun file `.gmk`
gemello — le sue risorse sono state originariamente importate tramite
un import GameMaker 8.x, vedi `CREDITS.txt`, ma il progetto stesso è
scritto/salvato nel formato JSON proprio di pygm2).

**Dove si colloca:** parte della famiglia `maze_*` — GameObject +
sprite, più (a differenza di `maze_1`) un'**immagine di sfondo**
statica per stanza (`background_main`), nessuna tessera a livello di
stanza. Vedi
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
per come questo si confronta con `plateforme_*` (aggiunge sfondi a
tessere) e `match3_*` (puro script, nessuna azione integrata).

**Audio e musica:** 4 file audio sono forniti (`sound_background.mid`,
`sound_diamond`/`door`/`goal.wav`) ma **nessuno di essi è
effettivamente collegato** — nessun oggetto fa riferimento a
`play_sound`/`play_music` da nessuna parte, quindi il gioco è
silenzioso in pratica nonostante porti risorse audio. (In contrasto
con `maze_3`, dove lo stesso insieme di suoni viene genuinamente
riprodotto.)

## Come si gioca

- **Schermata del titolo (`room_start`):** premi **SPAZIO** per
  iniziare (l'azione `keyboard_press` di `controller_start` chiama `next_room`).
- Le **frecce direzionali** (su/giù/sinistra/destra) muovono il
  giocatore di una cella della griglia (32px) alla volta; il movimento
  è agganciato alla griglia tramite `test_alignment`/`snap_to_grid`
  (griglia 32×32), stesso schema di `maze_1`.
- **Obiettivo:** raccogliere le caramelle (`obj_diamond`, sprite
  `sprite_bonbon`) sparse in ogni labirinto — ciascuna vale +10
  punteggio — poi raggiungere l'obiettivo (`obj_goal`). In `room2`,
  l'uscita è inoltre bloccata da una porta chiusa a chiave
  (`obj_door`) che si autodistrugge solo quando ogni `obj_diamond`
  nella stanza è sparito.
- Toccare l'obiettivo avanza alla stanza successiva (+100 punteggio)
  se ne esiste una; toccarlo nell'ultima stanza (`room2`) assegna
  +100, apre la schermata di inserimento del punteggio più alto, e
  termina il gioco.
- **Nessuna condizione di sconfitta:** nessuna azione che influisce su
  vite/salute appare da nessuna parte negli oggetti di questo esempio
  — `starting_lives: 3` è impostato nelle impostazioni del progetto ma
  non viene mai mostrato o decrementato.

## Struttura del progetto

| File | Scopo |
|---|---|
| `project.json` | Manifesto del progetto — impostazioni finestra/stanza e copie incorporate di tutte le risorse |
| `rooms/room_start.json` | Schermata del titolo — 1 istanza (`controller_start`) |
| `rooms/room1.json` | Primo labirinto — 134 istanze (muri, giocatore, obiettivo, 4 caramelle, `controller_main`) |
| `rooms/room2.json` | Secondo labirinto — 112 istanze (muri, giocatore, obiettivo, 21 caramelle, porta chiusa a chiave, `controller_main`) |
| `objects/*.json` | 9 definizioni di oggetti — verificate rispetto alle copie incorporate di `project.json` e identiche in questo esempio (nessuna obsolescenza trovata) |
| `sprites/` | 7 sprite (`sprite_person`, `sprite_bonbon`, `sprite_door`, `sprite_goal`, `sprite_wall_corner`, `sprite_wall_horizontal`, `sprite_wall_vertical`) + metadati; `tiles.json` è un file collaterale orfano (non registrato in `project.json`, file immagine mancante — inutilizzato) |
| `backgrounds/` | `background_start.png` (schermata del titolo), `background_tiles.png` (pavimento del labirinto a tessere) |
| `sounds/` | 4 file audio (vedi Risorse sotto) |
| `CREDITS.txt` | Avviso di licenza delle risorse per questo esempio |

## Oggetti

| Oggetto | Ruolo | Eventi chiave |
|---|---|---|
| `obj_person` | Personaggio controllato dal giocatore; movimento a griglia | keyboard (down, right, up, left, nokey), collision_with_wall_corner |
| `wall_corner` | Muro solido base del labirinto; oggetto genitore per gli altri due tipi di muro | (nessuno — solo collisore passivo) |
| `wall_horizontal` | Segmento di muro orizzontale solido (eredita da `wall_corner`) | (nessuno — solo collisore passivo) |
| `wall_vertical` | Segmento di muro verticale solido (eredita da `wall_corner`) | (nessuno — solo collisore passivo) |
| `obj_diamond` | Caramella collezionabile; aggiunge punteggio alla raccolta | destroy, collision_with_obj_person |
| `obj_door` | Cancello di uscita chiuso a chiave (solo room2); si apre quando tutte le caramelle sono sparite | step |
| `obj_goal` | Uscita del livello; avanza alla stanza successiva o termina il gioco | collision_with_obj_person |
| `controller_start` | Controller della schermata del titolo; attende che il giocatore inizi | create, keyboard_press (SPAZIO) |
| `controller_main` | Controller HUD nel labirinto; disegna il punteggio | draw |

## Risorse

7 sprite (32×32, singolo frame, collisione precisa al pixel eccetto
`sprite_goal` che non ha un flag `precise` esplicito), 2 sfondi, 4
suoni (`sound_background.mid`, `sound_diamond.wav`, `sound_door.wav`,
`sound_goal.wav`). Licenza/provenienza per tutte le risorse di questo
esempio è **non documentata** — vedi `CREDITS.txt` in questa cartella,
che rimanda al TODO "Remaining maze assets" in
`docs/ASSET_LICENSES.md`. Non presumere CC0 o qualsiasi altra licenza
per questi file.

## Cose da modificare

- La velocità di movimento del giocatore è `4` (celle griglia/passo)
  mentre l'arresto per urto contro muro usa velocità `8` — entrambi
  sono parametri d'azione hardcoded per pressione tasto in
  `obj_person`, come in `maze_1`.
- Tutti e 4 i file audio forniti non sono referenziati — nessun
  oggetto chiama attualmente `play_sound`; collegarne uno per
  raccolta caramella/apertura porta/obiettivo raggiunto sarebbe un
  passo successivo naturale.
- Le stanze sono `480×480`–`480×512` a `room_speed: 30` — piccoli
  labirinti a schermo singolo senza scorrimento.
- `sprites/tiles.json` è un file collaterale residuo non registrato
  come risorsa del progetto (il suo `sprites/tiles.png` non esiste) —
  sicuro da rimuovere o ignorare.

## Stato dell'esportazione

Coperto dalla suite di smoke-test senza interfaccia grafica
(`tools/smoke_run_samples.py`, che elenca `maze_2` e lo esegue per
~180 frame con input da tastiera iniettato); non verificato
individualmente per ogni target di esportazione (Kivy/Web). Esposto
nella scheda Welcome dell'IDE come "Maze — Level 2"
(`widgets/welcome_tab.py`).
