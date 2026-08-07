# Views — Livello 2

Una demo di **cooperativa a schermo diviso**: la stanza 2400×800 è
mostrata come due camere affiancate in una finestra 800×600 singola.
La **metà sinistra** (view 0) segue il **giocatore 1** (arancione,
frecce direzionali); la **metà destra** (view 1) segue il
**giocatore 2** (petrolio, WASD). Ogni giocatore esplora la stanza
condivisa nella propria corsia e raccoglie monete — vedi entrambi
contemporaneamente.

**Dove si colloca:** il secondo livello della quarta famiglia di
esempi. `views_1` introduceva una singola camera scrollante;
`views_2` introduce **più viewport simultanei** — l'altra capacità di
punta delle views di GameMaker. Vedi
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
per la progressione completa. Il movimento riusa l'idioma a griglia
da `maze_1`/`views_1`.

**Audio e musica:** nessuno — nessun file audio è fornito con questo esempio.

## Come si gioca

- **Giocatore 1 (arancione):** frecce direzionali — si muove nella
  view **sinistra**.
- **Giocatore 2 (petrolio):** `W` `A` `S` `D` — si muove nella view **destra**.
- Entrambi si muovono di una cella griglia (32px) alla volta; i muri
  (`obj_wall`) sono solidi. Un divisore centrale con aperture separa
  le due corsie.
- **Obiettivo:** raccogli le 18 monete (`obj_coin`) — entrambi i
  giocatori possono prendere qualsiasi moneta; ciascuna vale 10 punti
  (mostrati nella didascalia della finestra).

## Perché i due giocatori si fermano indipendentemente (una vera trappola)

Il movimento a griglia normalmente si ferma sull'evento `nokey`
(attivato quando *nessun* tasto è premuto). Ma lo stato dei tasti è
tracciato globalmente su tutte le istanze, così con due giocatori
`nokey` si attiva solo quando **entrambi** rilasciano tutto — il
giocatore 2 continuerebbe a scivolare mentre il giocatore 1 tiene
premuto un tasto. Quindi ogni giocatore invece si ferma tramite
**`keyboard_release`** per i **propri** tasti (frecce per G1, WASD per
G2), che si attiva per tasto e per oggetto. Questa è la differenza
rispetto al singolo giocatore di `views_1`, che può usare `nokey` in
sicurezza.

## Come è impostato lo schermo diviso

Un controller invisibile, `obj_camera`, configura entrambe le views
nel suo evento **create** (azioni registrate `enable_views` + due
`set_view`), e la stessa configurazione è incorporata nel blocco
`views` della stanza per correttezza al frame-0 all'export:

- **view 0** — `view`/`port` `400×600`, `port_x` 0 (metà sinistra),
  `follow` `obj_player1`.
- **view 1** — `view`/`port` `400×600`, `port_x` 400 (metà destra),
  `follow` `obj_player2`.

Entrambe le views sono **1:1** (dimensione view == dimensione porta)
e si dividono **sinistra/destra** (`port_y` 0, altezza intera). Questo
conta per la coerenza cross-target: desktop e HTML5 rendono ogni view
1:1 (ritagliano + spostano, **non** scalano una view alla sua porta),
e una divisione sinistra/destra evita il flip `port_y` tra Kivy
(y-up) e desktop/HTML5 (y-down). Una minimappa zoomata fuori (view più
grande della sua porta) è deliberatamente **non** usata qui — si
scalerebbe correttamente solo su Kivy.

## Struttura del progetto

| File | Scopo |
|---|---|
| `project.json` | Manifesto — impostazioni finestra/stanza, risorse incorporate, e la configurazione `views` a due view |
| `rooms/room0.json` | La stanza 2400×800 (284 istanze: camera, muri, 2 giocatori, 18 monete) + il suo blocco `views` |
| `objects/obj_camera.json` | Controller invisibile: create-evento `enable_views` + due `set_view` |
| `objects/obj_player1.json` | Giocatore 1 (frecce direzionali); movimento a griglia + arresto `keyboard_release` |
| `objects/obj_player2.json` | Giocatore 2 (WASD); movimento a griglia + arresto `keyboard_release` |
| `objects/obj_coin.json` | Collezionabile — distrutto da entrambi i giocatori, aggiunge 10 |
| `objects/obj_wall.json` | Muro solido statico |
| `sprites/` | `spr_player1.png` (arancione), `spr_player2.png` (petrolio), `spr_wall.png`, `spr_coin.png` + metadati `.json` |
| `CREDITS.txt` | Avviso di licenza delle risorse |

## Oggetti

| Oggetto | Ruolo | Eventi chiave |
|---|---|---|
| `obj_camera` | Controller invisibile; attiva + configura entrambe le views | create (`enable_views`, 2× `set_view`) |
| `obj_player1` | Giocatore della view sinistra (frecce) | keyboard (up/down/left/right/nokey), keyboard_release (per tasto), collision_with_obj_wall |
| `obj_player2` | Giocatore della view destra (WASD) | keyboard (w/a/s/d/nokey), keyboard_release (per tasto), collision_with_obj_wall |
| `obj_coin` | Collezionabile del valore di 10 | collision_with_obj_player1, collision_with_obj_player2, destroy (`set_score` +10) |
| `obj_wall` | Muro solido statico / confine camera | (nessuno — collisore passivo) |

## Risorse

4 sprite (`spr_player1`, `spr_player2`, `spr_wall`, `spr_coin`,
ciascuno 32×32, singolo frame, preciso al pixel), 0 suoni. Tutta
grafica CC0 a colore piatto generata per questo esempio — vedi `CREDITS.txt`.

## Cose da modificare

- **Direzione di divisione** — questo usa una divisione
  sinistra/destra (`port_x` 0 e 400, `port_y` 0, altezza intera). Una
  divisione alto/basso metterebbe le metà a `port_y` diversi; nota che
  questo si rende a una posizione verticale diversa su Kivy (y-up)
  rispetto a desktop/HTML5 (y-down), quindi sinistra/destra è la
  scelta portabile.
- **Larghezza view** — ogni view è larga `400` (metà della finestra).
  Allarga la finestra o restringi le views per cambiare quanto della
  stanza vede ogni giocatore.
- **Bordi** — `hborder` 120 / `vborder` 150 impostano la zona morta di
  ogni camera.

## Stato dell'esportazione

- **Desktop (pygame):** il riferimento — `tests/test_views_2_sample.py`
  carica l'esempio, esegue l'evento create di `obj_camera`, e verifica
  che le due camere scorrano **indipendentemente** (muovere un
  giocatore non muove la view dell'altro) e si blocchino al bordo
  della stanza, oltre al punteggio delle monete e all'arresto
  `keyboard_release` per giocatore.
- **Web (HTML5):** `engine.js` rende ogni view visibile (ritaglio per
  view + traslazione 1:1); la configurazione a due view si trasferisce
  correttamente nell'export.
- **Mobile (Kivy/Android):** l'exporter rende la stanza in un Fbo e
  copia la regione visibile di ogni view nella sua porta schermo
  (`tests/test_kivy_views.py` copre il rendering multi-view). Le
  azioni `enable_views`/`set_view` vengono emesse, quindi
  l'impostazione a due view funziona sia dall'evento create di
  `obj_camera` sia dalla configurazione incorporata nella stanza.
  Limitazione residua (come in `views_1`): il target di rendering è
  costruito alla creazione della stanza, quindi `views_enabled` deve
  essere nella configurazione della stanza (lo è qui) perché la camera
  renderizzi su Kivy.
- L'accordo cross-target sulla matematica di scorrimento è fissato da
  `tests/test_views_export_parity.py`.

Esposto nella scheda Welcome dell'IDE come "Views — Level 2" (`widgets/welcome_tab.py`).
