# Raycast — Livello 4

Il quarto livello in prima persona in stile Doom/Wolfenstein, e il
primo costruito **attorno a una barra di stato permanente in basso**
— l'estetica DOOM piuttosto che gli overlay d'angolo di `raycast_3`.
La vista 3D è deliberatamente **più corta** (letterbox) per fare
spazio alla barra; questo fa parte dell'aspetto, non è un bug.

Dove `raycast_3` ha dimostrato un HUD d'angolo e la salute come
risorsa, `raycast_4` mostra le due funzionalità del motore costruite
per una barra DOOM:

- **`viewport_height`** su `enable_raycast_view` riduce la vista in
  prima persona nella parte superiore della finestra e riserva la
  fascia sottostante.
- **`draw_doom_hud`** riempie quella fascia: una barra salute + numero,
  un **ritratto viso reattivo alla salute**, punteggio, vite, e un
  contatore chiavi — tutto da normali comandi di disegno, così si
  rende su desktop, HTML5 e nativo (Kivy) allo stesso modo.

Vedi [`docs/RAYCAST_DOOM_HUD_PLAN.md`](../../docs/RAYCAST_DOOM_HUD_PLAN.md)
per l'ingegneria, e [`raycast_3`](../raycast_3/README.md) per
l'alternativa HUD d'angolo che questo livello deliberatamente non
retrofit.

**Sensazione di interno.** Due cose fanno leggere questo come un
corridoio dentro un edificio piuttosto che un labirinto a cielo
aperto: proietta un **soffitto di pietra** (`spr_ceiling`) invece del
cielo scorrevole che usano gli altri esempi raycast — impostato
tramite `ceiling_texture` con `sky_texture` lasciato vuoto — e i muri
si rendono **più alti**. Quell'altezza muro (`RAYCAST_WALL_HEIGHT`,
1,5× un cubo) è un default globale del motore, quindi ogni gioco
raycast ottiene i muri più alti; il soffitto è la scelta propria di
questo esempio.

**Audio e musica:** nessuno — nessun file audio è fornito con questo esempio.

## Come si gioca

- **Su/Giù** — muovono avanti/indietro nella direzione in cui si sta guardando.
- **Sinistra/Destra** — girano sul posto.
- **Raccogli le chiavi** — ciascuna assegna 25 punti e fa avanzare di
  uno il contatore **KEYS** nella barra. Ce ne sono tre.
- **Evita i mostri** — toccarne uno costa **25 salute** (con una
  breve finestra di invulnerabilità dopo). Osserva il **viso**: si
  contrae mentre la tua salute scende, prima ancora che tu abbia letto
  il numero.
- **Se finisce la salute** → perdi una vita, la salute si riempie, la
  stanza riavvia. **Se finiscono le vite** → il gioco riavvia.
- **Raggiungi l'uscita** una volta trovate **tutte e tre le chiavi**.
  Toccarla presto ti dice solo che il cancello è chiuso a chiave.
- **Premi `M`** per far apparire una **minimappa** che mostra i muri, le chiavi dorate ancora da trovare e i mostri in rosso (spenta
  per default). È disegnata dentro la vista 3D, sopra la barra di
  stato, e si attiva/disattiva — la stessa mappa a richiesta che usa
  `raycast_3`, qui tenuta lontana dalla barra.

## La barra di stato (`draw_doom_hud`)

`obj_person` la disegna ogni frame, in spazio schermo, sopra la vista
3D finita. Da sinistra a destra:

| Zona | Mostra |
|---|---|
| Sinistra | etichetta `HEALTH` + una barra salute proporzionale + il numero |
| Centro | il **ritratto viso**, una striscia a 4 frame che reagisce alla salute |
| Destra | `SCORE` sopra `LIVES` |
| Estrema destra | il contatore `KEYS` |

Il viso è il punto centrale dell'intero esempio. Il suo frame è scelto
da una mappa a bucket uniforme sulla salute — frame 0 (calmo) vicino
al pieno, l'ultimo frame (morente) vicino al vuoto — così il ritratto
ti dice come stai andando prima che lo faccia il numero, esattamente
come la barra propria di DOOM.

**`obj_person` è sia la camera *sia* il disegnatore HUD.** Questo è
deliberato: il contatore chiavi è quindi solo una variabile di
istanza su `obj_person` (`keys`), così l'espressione obiettivo di
`draw_doom_hud` legge lo stesso valore identicamente su tutti e tre i
target di esportazione. Un oggetto camera invisibile separato (come in
`raycast_3`) non potrebbe portare una variabile di cui l'HUD visibile
ha bisogno.

## Il letterbox (`viewport_height`)

`enable_raycast_view` gira nel `create` di `obj_person` con
`viewport_height: 400` in una finestra 640×480 — quindi la vista 3D è
alta 400px e i **80px** in basso sono riservati, riempiti di nero dal
motore, e dipinti sopra dalla barra. Imposta `viewport_height` a `0`
(il default) e la vista riempie l'intera finestra senza fascia
riservata, esattamente come fanno `raycast_1`–`3`.

L'orizzonte si sposta in su con la vista più corta, e
muri/cielo/pavimento scalano tutti in base a esso — è un vero
letterbox, non una barra posata su una vista a piena altezza. (Su
Kivy, che è y-up, la fascia riservata è comunque in basso nella
finestra; il motore gestisce l'inversione.)

## Struttura del progetto

| File | Scopo |
|---|---|
| `project.json` | Manifesto — finestra 640×480, una stanza |
| `rooms/room0.json` | Il labirinto: 15×15 celle, 3 chiavi, 4 mostri, un'uscita bloccata dalle chiavi |
| `objects/obj_person.json` | Giocatore + camera + barra di stato — movimento, salute, chiavi, `draw_doom_hud` |
| `objects/obj_key.json` | Una chiave (passiva; la collisione di `obj_person` la gestisce) |
| `objects/obj_monster.json` | Nemico billboard in pattuglia |
| `objects/obj_goal.json` | Uscita bloccata dalle chiavi (si apre quando non resta nessun `obj_key`) |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segmenti muro sottili |
| `sprites/` | Grafica muro/pavimento/persona/mostro riusata, un nuovo **`spr_ceiling`** (soffitto di pietra da interno, in sostituzione del cielo), più nuovi `spr_face` (ritratto a 4 frame), `spr_key` e `spr_gate` (l'uscita chiusa) |

## Il labirinto è generato

`tools/gen_raycast_4_maze.py` costruisce la stanza **delegando al
generatore committato di `raycast_3`** — stesso labirinto backtracker
ricorsivo, stessi muri sottili sui bordi, stessa disciplina di seed
scelto (lo spawn si apre a est, ogni cella raggiungibile). Differisce
solo in cosa è sparso (chiavi, non gemme/kit medici) e nel fatto che
`obj_person` è la camera. Rieseguirlo riproduce la stanza distribuita;
un test la blocca.

## Cose da modificare

- **Altezza barra vs viewport:** l'`height` su `draw_doom_hud` (80)
  dovrebbe corrispondere alla fascia riservata (`640×480 −
  viewport_height 400 = 80`). Cambia una, cambia l'altra.
- **Reattività del viso:** `face_frames` (4) suddivide la salute
  sulla striscia. Una striscia a 5 frame con `face_frames: 5` dà
  espressioni più fini.
- **Danno/chiavi:** il `-25` nell'evento
  `collision_with_obj_monster` di `obj_person`; le 3 chiavi e 4 mostri
  nei `counts` del generatore.
- **Colori ed etichette della barra:** i parametri `draw_doom_hud`
  nell'evento draw di `obj_person`.

## Stato dell'esportazione

Gira su tutti e tre i target. Coperto dalla suite smoke senza
interfaccia grafica (`tools/smoke_run_samples.py`) e
`tests/test_raycast_4_sample.py`, che pilota il vero ciclo: la barra
rende tutte le sue parti sopra la vista ridotta, allineata in basso
alla fascia riservata; il **frame del viso segue la salute**
(100/75/50/25 → 0/1/2/3); una raccolta chiave conta, punteggia ed è
distrutta.

Gli export Kivy e HTML5 sono stati verificati portare tutto — il
`viewport_height` del letterbox nella configurazione camera,
`draw_doom_hud`, il viso multi-frame — ma il playtest **visivo** per
target è l'ultimo passo e vale la pena farlo con i propri occhi:
questo è il primo esempio raycast la cui *forma della vista* cambia,
quindi quello più meritevole di essere osservato mentre si rende in
un browser e su Android.
