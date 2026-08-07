# Views — Livello 1

Una demo di camera scrollante: la stanza (2400×800) è **tre volte più
larga della finestra 800×600**, quindi un singolo schermo non può
mostrarla tutta. La camera (view 0) segue il giocatore mentre cammina
verso destra, rivelando il livello uno schermo alla volta — l'intero
senso delle **views** in stile GameMaker. Esplora la stanza ampia e
raccogli tutte le 18 monete.

**Dove si colloca:** questa è la quarta famiglia di esempi, distinta
dalle tre famiglie per tecnica di creazione (`maze_*` → `plateforme_*`
→ `match3_*`). Ciò che introduce non è un nuovo *stile* di creazione
ma una nuova capacità del motore: una **stanza più grande della
finestra** con una **camera scrollante**. Vedi
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
per la progressione completa. Meccanicamente riusa il movimento a
griglia di `maze_1` (azioni integrate
`test_alignment`/`snap_to_grid`/`start_moving_direction`) e aggiunge
esattamente una cosa nuova: la camera, attivata dall'evento **create**
del giocatore con le azioni registrate `enable_views` + `set_view`.

**Audio e musica:** nessuno — nessun file audio è fornito con questo esempio.

## Come si gioca

- Le **frecce direzionali** muovono il giocatore di una cella di
  griglia (32px) alla volta (movimento agganciato alla griglia, come
  in `maze_1`).
- I muri (`obj_wall`) delimitano il bordo della stanza e formano
  alcuni pilastri interni; sono solidi e fermano il giocatore.
- **La camera segue il giocatore**: cammina verso un bordo dello
  schermo e la vista scorre per tenerti nell'inquadratura, bloccandosi
  ai bordi della stanza così non vedi mai oltre il bordo di muri.
- **Obiettivo:** raccogli tutte le 18 monete (`obj_coin`). Ciascuna
  vale 10 punti (mostrati nella didascalia della finestra).

## Come è impostata la camera

L'evento **create** del giocatore esegue due azioni registrate
(nessun `execute_code` grezzo):

1. `enable_views` — attiva il sistema views per la stanza.
2. `set_view` — configura la **view 0**: `view_w`/`view_h` `800×600`,
   porta a `(0,0)` dimensionata `800×600`, `follow` = `obj_player`,
   `hborder` 240 / `vborder` 180 (la zona morta prima che la camera
   scorra), nessun tetto di velocità scorrimento. La stessa
   configurazione è anche incorporata nel blocco `views` della stanza,
   così la camera è corretta dal primo frame su ogni target di esportazione.

## Struttura del progetto

| File | Scopo |
|---|---|
| `project.json` | Manifesto del progetto — impostazioni finestra/stanza, copie di risorse incorporate, e la configurazione `views` della stanza |
| `rooms/room0.json` | La stanza 2400×800 (245 istanze: bordo muri + pilastri, giocatore, 18 monete) e il suo blocco `views` |
| `objects/obj_player.json` | Giocatore: movimento a griglia + l'impostazione camera nell'evento create |
| `objects/obj_coin.json` | Collezionabile: distrutto al tocco del giocatore, aggiunge 10 al punteggio |
| `objects/obj_wall.json` | Muro solido statico |
| `sprites/` | `spr_player.png`, `spr_wall.png`, `spr_coin.png` + i rispettivi metadati `.json` |
| `CREDITS.txt` | Avviso di licenza delle risorse |

## Oggetti

| Oggetto | Ruolo | Eventi chiave |
|---|---|---|
| `obj_player` | Personaggio giocatore; movimento a griglia + attiva/configura la camera | create (`enable_views`, `set_view`), keyboard (down/right/up/left/nokey), collision_with_obj_wall |
| `obj_coin` | Collezionabile del valore di 10 punti | collision_with_obj_player (`destroy_instance` self), destroy (`set_score` +10) |
| `obj_wall` | Muro solido statico / confine di blocco camera | (nessuno — collisore passivo) |

## Risorse

3 sprite (`spr_player`, `spr_wall`, `spr_coin`, ciascuno 32×32,
singolo frame, collisione precisa al pixel), 0 suoni. Tutti e tre
sono semplice grafica CC0 a colore piatto generata per questo esempio
— vedi `CREDITS.txt`.

## Cose da modificare

- **Dimensione stanza** (`2400×800` in `rooms/room0.json`) — rendila
  più larga/alta per scorrere più lontano; la camera si blocca a
  qualunque dimensione la stanza abbia.
- **Bordi** (`hborder` 240 / `vborder` 180 nell'azione `set_view` *e*
  nel blocco `views` della stanza) — bordi più piccoli lasciano il
  giocatore avvicinarsi di più al bordo prima che la camera si muova;
  più grandi lo mantengono più centrato.
- **Velocità di scorrimento** — `hspeed`/`vspeed` sono `-1` (seguito
  istantaneo). Impostali a un valore positivo di pixel per passo per
  una camera che segue con ritardo, ammorbidita.
- **Monete** — aggiungi/rimuovi istanze `obj_coin` in `rooms/room0.json`.

## Stato dell'esportazione

- **Desktop (pygame):** il target di riferimento — verificato da
  `tests/test_views_1_sample.py`, che carica questo esempio, esegue
  l'evento create del giocatore, e verifica che la camera scorra e si
  blocchi mentre il giocatore percorre l'intera larghezza.
- **Web (HTML5):** l'`engine.js` esportato porta la stessa camera a 8
  views (`tests/test_html5_views.py`, verificato con Chromium durante
  lo sviluppo); sia la configurazione `views` di questo esempio sia il
  `set_view` dell'evento create si trasferiscono correttamente nell'export.
- **Mobile (Kivy/Android):** la scena esportata rende l'intera stanza
  in un Fbo e copia la regione visibile di ogni view nella sua porta
  schermo, con la finestra del sistema dimensionata secondo la view
  (non la stanza) così la camera mostra una vera fetta scorrevole e
  supporta più viewport (`tests/test_kivy_views.py`). Le azioni
  `enable_views`/`set_view` vengono emesse, quindi funziona anche la
  riconfigurazione camera a runtime. *Una limitazione residua:* il
  target di rendering multi-view è costruito quando la stanza viene
  creata, quindi una stanza deve avere `views_enabled` nella sua
  configurazione (come fa questo esempio) perché la camera renderizzi
  — attivare le views solo tramite un `enable_views` a runtime su una
  stanza iniziata senza di esse non lo adatterà retroattivamente su Kivy.
- L'accordo cross-target sulla matematica di scorrimento è fissato da
  `tests/test_views_export_parity.py`.

Esposto nella scheda Welcome dell'IDE come "Views — Level 1"
(`widgets/welcome_tab.py`).
