# Platform — Livello 1

Un platform a scorrimento laterale minimale importato da GameMaker 8.x
(`samples/plateforme_1.gmk`). La palla controllata dal giocatore
(`obj_balle`) scala uno schermo singolo di piattaforme di mattoni
(`obj_brique`) usando sonde `if_collision` in stile GameMaker per
muoversi in passi di 4px/frame e cadere sotto gravità solo quando non
c'è nulla di solido direttamente sotto di essa — uno schema di
movimento AABB scritto a mano piuttosto che la fisica integrata del
motore.

**Dove si colloca:** parte della famiglia `plateforme_*`, ma al suo
minimo — a differenza di `plateforme_2`/`plateforme_3`, questo livello
non ha immagine di sfondo e **nessuno sfondo a tessere** (l'array
`tiles` della stanza è vuoto); è costruito solo da GameObject +
sprite, come `maze_1`. Vedi
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
per come l'intera famiglia si confronta con `maze_*` e `match3_*`.

**Audio e musica:** nessuno — nessun file audio è fornito con questo esempio.

## Come si gioca

- **Freccia sinistra/destra** — muove la palla di 4px per pressione
  tasto, bloccata dai mattoni solidi.
- **Freccia su** — salto (imposta `vspeed` a -10), solo mentre si sta
  su un mattone solido.
- Non c'è un oggetto obiettivo esplicito, moneta, o uscita in questo
  livello — è un labirinto verticale di mattoni da scalare. Non c'è
  nemmeno un oggetto mostro/pericolo, quindi non c'è condizione di
  sconfitta; è libera esplorazione della meccanica di collisione/gravità.

## Struttura del progetto

| File | Scopo |
|---|---|
| `project.json` | Manifesto del progetto — impostazioni finestra/stanza, copie di risorse incorporate (vedi nota sotto). |
| `rooms/niveau_01.json` | L'unica stanza: 800×640, 120 istanze (per lo più muri/piattaforme `obj_brique` più una `obj_balle`). |
| `objects/obj_balle.json` | Logica della palla giocatore (movimento, gravità, salto). |
| `objects/obj_brique.json` | Mattone solido statico, nessun evento. |
| `sprites/` | `spr_balle.png` (palla) e `spr_32x32_noir.png` (mattone), ciascuno con un `.json` collaterale. |

`objects/*.json` e `rooms/niveau_01.json` sono gli attuali file
collaterali per risorsa; il loro contenuto corrisponde a quello
incorporato in `project.json` per questo esempio (nessuna divergenza
trovata), ma per convenzione del repository i file collaterali sono
la fonte di verità se i due dovessero mai discordare.

## Oggetti

| Oggetto | Ruolo | Eventi chiave |
|---|---|---|
| `obj_balle` | Palla controllata dal giocatore; gravità, movimento consapevole delle collisioni, salto | create (nessuno definito), step, collision_with_obj_brique, keyboard (left, right, up) |
| `obj_brique` | Tessera piattaforma/muro solida statica | *(nessuno — nessun evento definito)* |

## Risorse

2 sprite (`spr_balle`, `spr_32x32_noir`), 0 suoni. Entrambi gli sprite
sono opere derivate dalla grafica del gioco Pingus, licenziate sotto
GPL-3.0-or-later — vedi `CREDITS.txt` in questa cartella per l'avviso
completo e i crediti degli artisti originali; non trattarli come
coperti dalla licenza MIT dell'IDE.

## Cose da modificare

- Evento step di `obj_balle`: la gravità è `0,45` px/frame², e vspeed
  è limitato a `24` — aumenta o diminuisci l'uno o l'altro per
  cambiare il peso della caduta e la velocità terminale.
- L'impulso del salto è un fisso `vspeed = -10` (tastiera "su") —
  magnitudine maggiore salta più in alto.
- Il passo di movimento orizzontale è `4` px per pressione tasto
  (tastiera "sinistra"/"destra") — passi più grandi sembrano più
  scattanti ma possono attraversare fessure sottili.
- La stanza è 800×640 con `room_speed: 30`; il layout dei mattoni in
  `rooms/niveau_01.json` può essere riorganizzato liberamente poiché
  `obj_brique` non ha logica propria.

## Stato dell'esportazione

Questo esempio è elencato nella lista `SAMPLES` di
`tools/smoke_run_samples.py`, quindi è coperto dall'harness di
smoke-test senza interfaccia grafica (esegue il vero ciclo di gioco
per ~180 frame con input da tastiera iniettato). Non è stato
verificato separatamente contro i target di esportazione Kivy o Web.
È esposto nella scheda Welcome dell'IDE come **"Platform — Level 1"**
(`widgets/welcome_tab.py`).
