# Raycast — Livello 2

Un secondo livello in prima persona in stile Doom/Wolfenstein,
costruito sullo stesso **motore raycast 2,5D** di
[`raycast_1`](../raycast_1/README.md) — che è completo su tutti e tre
i target di esportazione (desktop, HTML5, nativo/Kivy): muri
texturizzati, un cielo scorrevole, cast del pavimento texturizzato a
bassa risoluzione, e sprite billboard rivolti alla camera.

Dove `raycast_1` è un piccolo corridoio derivato da maze_1 che
insegna *la vista in prima persona stessa*, `raycast_2` è un
**labirinto più grande con cose che succedono nella vista 3D** —
gemme collezionabili, un nemico in pattuglia, e un'uscita bloccata
dalle gemme. Vedi
[`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) per il
motore e [`docs/RAYCAST_2_SAMPLE_PLAN.md`](../../docs/RAYCAST_2_SAMPLE_PLAN.md)
per il design e il piano di unità di questo esempio.

Un gioco completo a due livelli: naviga ogni labirinto in prima
persona, raccogli ogni gemma evitando i mostri in pattuglia, e
raggiungi l'uscita bloccata dalle gemme — la prima stanza (mattoni
caldi) porta a una seconda stanza (caverna di cristallo fredda), e
completarla vince. Disponibile dalla scheda Welcome dell'IDE
(*"Raycast — Level 2"*) ed esporta su tutti e tre i target (desktop,
HTML5, nativo/Kivy).

## Come si gioca

- **Su/Giù** — muovono avanti/indietro nella direzione in cui si sta
  guardando (continuo, non agganciato alla griglia; i muri bloccano
  tramite la normale collisione dell'istanza solida del motore).
- **Sinistra/Destra** — girano sul posto (ruotano `facing_angle`,
  indipendente dal movimento — puoi girare da fermo).
- **Raccogli le gemme** sparse nel labirinto — ciascuna aggiunge 10 al
  punteggio, mostrato nell'**HUD a schermo** (in alto a sinistra),
  disegnato sopra la vista in prima persona da `obj_hud`.
- **Evita i mostri** — pattugliano i corridoi (rimbalzando sui muri) e
  si disegnano come billboard rivolti alla camera. Toccarne uno costa
  una vita e riavvia la stanza; inizi con 3 vite, mostrate in alto a
  destra dell'HUD. Se finiscono, il gioco riavvia.
- **Obiettivo:** raccogli **tutte** le gemme in una stanza, poi
  raggiungi il suo obiettivo. Raggiungerlo troppo presto ti chiede
  solo di *"Collect all the gems before you leave!"* — si apre solo
  quando ogni gemma è sparita. L'obiettivo della prima stanza (mattoni
  caldi) porta a una seconda, fredda stanza a **caverna di
  cristallo**; completarla vince il gioco.

## Geometria del livello

Sia `rooms/room0.json` che `rooms/room1.json` sono labirinti di
15×15 celle (480×480) generati da un backtracker ricorsivo (un
labirinto *perfetto* — ogni cella raggiungibile, garantito risolvibile
— con qualche muro extra abbattuto per anelli e linee di vista più
lunghe), poi convertiti al modello di **muro sottile sui bordi** di
`raycast_1`: ogni confine tra una cella aperta e un muro diventa un
segmento `obj_wall_h` (32×8) o `obj_wall_v` (8×32) da 8px sulla linea
della griglia, così i corridoi si leggono come genuinamente
proporzionati in stile Wolfenstein piuttosto che a blocchi. Ogni
stanza usa un seed labirinto diverso, quindi i due livelli sono layout distinti.

## Tematizzazione per stanza

Le texture della vista raycast sono **per stanza**:
`enable_raycast_view` vive su un piccolo oggetto controller camera
invisibile posizionato in ogni stanza — `obj_cam0` (mattoni caldi:
`spr_wall_texture`/`spr_sky`/`spr_floor`) in room0, `obj_cam1`
(caverna di cristallo fredda:
`spr_wall_ice`/`spr_sky_ice`/`spr_floor_ice`, varianti tinte di blu)
in room1. Ogni controller nomina `obj_person` come camera tramite il
parametro `camera_object` dell'azione, così il *giocatore* rimane
sempre la camera anche se è il *controller* ad attivare l'azione.
Questo è il motivo per cui la seconda stanza appare diversa — la
configurazione è limitata al controller della stanza, non incorporata
nel giocatore.

## Struttura del progetto

| File | Scopo |
|---|---|
| `project.json` | Manifesto del progetto |
| `rooms/room0.json`, `rooms/room1.json` | I due labirinti generati a muro sottile sui bordi (dati di istanza autorevoli) |
| `objects/obj_person.json` | Giocatore/camera — gli eventi `keyboard` guidano girare + avanti/indietro; `game_start` inizializza punteggio/vite; registra i gestori `collision_with_obj_wall_h`/`_v` che bloccano ai muri, e `collision_with_obj_monster` (perdi una vita + riavvio) |
| `objects/obj_cam0.json`, `obj_cam1.json` | Controller camera per stanza che attivano `enable_raycast_view` con il tema texture di quella stanza |
| `objects/obj_gem.json` | Collezionabile — la collisione lo distrugge; il suo evento `destroy` aggiunge 10 al punteggio |
| `objects/obj_monster.json` | Nemico billboard in pattuglia — si muove, rimbalza sui muri |
| `objects/obj_goal.json`, `obj_goal_final.json` | L'obiettivo di room0 (→ stanza successiva) e di room1 (→ vittoria); entrambi bloccati dalle gemme |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segmenti muro sottili (32×8 e 8×32) |
| `objects/obj_hud.json` | HUD in spazio schermo disegnato sopra la vista in prima persona — `draw_score` + `draw_lives`. Nota che è **visible: true**: GameMaker non esegue l'evento draw di un'istanza invisibile, ecco perché l'HUD non può semplicemente vivere su `obj_cam0`/`obj_cam1` (che sono invisibili) |
| `sprites/` | Riusati da `raycast_1` (persona/obiettivo/muro/cielo/pavimento + placeholder muro), più `spr_gem` (gemma match3), `spr_monster` (mostro maze_3), e il set texture `*_ice` tinto di blu di room1 |

## Motore riusato, grafica riusata

`raycast_2` condivide gli oggetti e gli sprite di `raycast_1` — il
punto di questo esempio è *creazione di livello e gameplay sul motore
finito*, non nuovo codice di rendering. La grafica di gemma e mostro
(Unità 2–3) sono gli unici nuovi asset, e nessuna della logica di
gioco dipende dalla grafica specifica, quindi sono riskinnabili.
