# 2.5 D — Livello 3

Il terzo livello in prima persona in stile Doom/Wolfenstein,
costruito sullo stesso **motore raycast 2,5D** di
[`raycast_1`](../raycast_1/README.md) e
[`raycast_2`](../raycast_2/README.md) — completo su tutti e tre i
target di esportazione (desktop, HTML5, nativo/Kivy): muri
texturizzati, un cielo scorrevole, cast del pavimento texturizzato a
bassa risoluzione, e sprite billboard rivolti alla camera.

Dove `raycast_1` insegna *la vista in prima persona stessa* e
`raycast_2` aggiunge *cose che succedono nella vista* (gemme, un
nemico in pattuglia, un'uscita bloccata), `raycast_3` riguarda **stato
che puoi vedere mentre giochi**: i mostri costano **salute** invece di
una vita diretta, i kit medici la restituiscono, e un **display
heads-up** composto sopra la vista 3D mostra sempre punteggio, vite e
una barra della salute.

Quell'HUD è il motivo per cui esiste questo esempio. Fino al
20/07/2026 il motore disegnava la vista in prima persona e poi si
fermava, così punteggio e vite di un gioco raycast apparivano solo
nella didascalia della finestra desktop — invisibili sugli export
HTML5 e Kivy. Vedi
[`docs/RAYCAST_HUD_PLAN.md`](../../docs/RAYCAST_HUD_PLAN.md) per quel
lavoro e [`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md)
per il motore.

Un gioco completo a due livelli: attraversa ogni labirinto in prima
persona, raccogli ogni gemma sopravvivendo ai mostri, e raggiungi
l'uscita bloccata dalle gemme — la prima stanza (mattoni caldi) porta
a una seconda stanza (caverna di cristallo fredda), e completarla
vince. Disponibile dalla scheda Welcome dell'IDE (*"2.5 D — Level 3"*).

**Audio e musica:** nessuno — nessun file audio è fornito con questo esempio.

## Come si gioca

- **Su/Giù** — muovono avanti/indietro nella direzione in cui si sta
  guardando (continuo, non agganciato alla griglia; i muri bloccano).
- **Sinistra/Destra** — girano sul posto (ruotano `facing_angle`,
  indipendente dal movimento — puoi girare da fermo).
- **Raccogli le gemme** — ciascuna aggiunge 10 al punteggio, mostrato
  in alto a sinistra.
- **Evita i mostri** — toccarne uno costa **25 salute**, non una
  vita. Dopo un colpo hai una breve finestra di invulnerabilità (45
  passi) così un mostro che ti attraversa non può svuotare l'intera
  barra in una volta.
- **Prendi i kit medici** — le scatole con croce rossa ripristinano
  **40 salute**, limitate al massimo.
- **Se finisce la salute** perdi una vita, la barra si riempie e la
  stanza riavvia. Se finiscono le **vite**, il gioco riavvia.
- **Obiettivo** — raccogli *tutte* le gemme in una stanza, poi
  raggiungi la sua uscita. Raggiungerla presto ti chiede solo di
  raccogliere il resto.

## L'HUD

`obj_hud` lo disegna, in **spazio schermo**, sopra il frame 3D finito:

| Elemento | Angolo | Azione |
|---|---|---|
| Punteggio | alto sinistra | `draw_score` |
| Vite | alto destra | `draw_text` + `draw_lives` |
| Barra salute | basso sinistra | `draw_health_bar` |
| Minimappa | centro, **a richiesta** | `draw_minimap` |

Punteggio e salute stanno in angoli **opposti** apposta: una barra
salute è larga e una stringa punteggio cresce mentre giochi, quindi
sovrapporli inviterebbe a una collisione.

### La minimappa

**Premi `M` per mostrarla o nasconderla** — su Android, tocca il
pulsante mappa in alto a sinistra. È *spenta* per default e disegnata
solo mentre attivata, per due motivi: una mappa completa sono ~250
comandi di linea ogni frame, e coprire permanentemente parte di una
vista in prima persona è esattamente il disordine che un HUD dovrebbe
evitare. Mentre è spenta non costa nulla.

`draw_minimap` disegna una mappa **orientata a nord** dei muri della
stanza con un marcatore che mostra dove sei e in che direzione stai
guardando. Non ruota — la mappa resta fissa e il marcatore gira, che
è più facile da leggere di una mappa rotante.

Non ha bisogno di dati propri: legge gli stessi bordi muro che la
vista in prima persona ha già derivato dalle istanze solide della
stanza, quindi rimane corretta se riprogetti il labirinto. Mostra
**solo muri** — non gemme o mostri — così il labirinto vale ancora la
pena esplorare.

**Non implementato (deliberato):** nebbia di guerra, una modalità
rotante/orientata alla direzione, e mostrare oggetti o nemici. Vedi
[`docs/RAYCAST_MINIMAP_PLAN.md`](../../docs/RAYCAST_MINIMAP_PLAN.md)
per il perché di ogni omissione.

**`obj_hud` è `visible: true`, e questo conta.** GameMaker non esegue
l'evento draw di un'istanza invisibile — quindi l'HUD non può
semplicemente vivere sul controller camera invisibile
(`obj_cam0`/`obj_cam1`). Se costruisci il tuo HUD e non appare nulla,
controlla prima quel flag.

## Struttura del progetto

| File | Scopo |
|---|---|
| `project.json` | Manifesto — finestra 640×480, entrambe le stanze, copie di risorse incorporate |
| `rooms/room0.json` | Labirinto mattoni caldi: 15×15 celle / 480×480, 8 gemme, 3 mostri, 3 kit medici |
| `rooms/room1.json` | Labirinto caverna di cristallo: la metà più difficile — 10 gemme, 5 mostri, solo 2 kit medici |
| `objects/obj_person.json` | Giocatore/camera — movimento, danno salute + alarme invulnerabilità, gestione morte |
| `objects/obj_hud.json` | Il display heads-up (vedi sopra) |
| `objects/obj_cam0.json`, `obj_cam1.json` | Controller camera per stanza, ciascuno con il tema texture di quella stanza |
| `objects/obj_gem.json` | Collezionabile, +10 punteggio |
| `objects/obj_medkit.json` | Ripristina 40 salute |
| `objects/obj_monster.json` | Nemico billboard in pattuglia |
| `objects/obj_goal.json`, `obj_goal_final.json` | Uscite bloccate dalle gemme: avanzamento e vittoria |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segmenti muro sottili (32×8 e 8×32) |
| `sprites/` | 13 sprite, riusati da `raycast_2` più `spr_medkit` |

## Il labirinto è generato, non posizionato a mano

`tools/gen_raycast_3_maze.py` costruisce entrambe le stanze con un
labirinto backtracker ricorsivo passato attraverso il posizionamento a
muro sottile sui bordi di `raycast_1` — partizioni da 8px centrate sui
confini delle celle, non blocchi da 32px che riempiono una cella.
Rieseguirlo riproduce esattamente le stanze distribuite, e un test
verifica che non siano andate alla deriva, così il design del livello
rimane revisionabile e modificabile invece di essere dato opaco. (Il
labirinto di `raycast_2` proveniva da uno script usa-e-getta mai
committato, quindi le sue stanze non possono essere rigenerate —
questo lo corregge.)

I seed sono **scelti, non arbitrari**: `check_start()` verifica che la
cella iniziale si apra a est (il giocatore appare lì guardando a est,
quindi un inizio murato significherebbe iniziare il gioco naso contro
muro) e che ogni cella sia raggiungibile.

## Cose da modificare

- **Danno e guarigione:** `-25` nell'evento
  `collision_with_obj_monster` di `obj_person`, `+40` nell'evento
  `destroy` di `obj_medkit`.
- **Finestra di invulnerabilità:** i `45` passi su `alarm_0`. Più
  corta rende il gioco più duro; rimuoverla e un mostro che ti
  sovrappone ripetutamente distruggerà la barra.
- **Equilibrio di difficoltà:** i `counts` per stanza nel generatore —
  mostri contro kit medici è la manopola principale.
- **Layout HUD:** le coordinate nell'evento draw di `obj_hud`. Tieni
  punteggio e salute in angoli opposti.
- **Minimappa:** `size` su `draw_minimap` scala l'intera stanza in
  quel quadrato, quindi un valore più grande significa semplicemente
  una mappa più leggibile; `wall_color` e `player_color` ne impostano
  l'aspetto. Il toggle vive nell'evento `keyboard_press` → `m` di
  `obj_hud`; usa `test_variable` + `exit_event` piuttosto che due
  condizionali nudi, perché la versione naive imposta il flag a 1 e
  poi lo legge subito 1 e lo rimette immediatamente a 0.
- **Temi:** i parametri texture su `obj_cam0`/`obj_cam1`.

## Una nota sul timing delle collisioni

Il runtime attiva un evento di collisione quando due istanze
**iniziano** a sovrapporsi, non ogni frame in cui rimangono
sovrapposte. Stare dentro un mostro costa quindi un colpo, non un
colpo per frame. L'alarme di invulnerabilità si guadagna comunque il
suo posto: copre il tocco/distacco ripetuto di un mostro che
pattuglia *attraverso* di te, che è il caso che si incontra davvero
giocando.

## Stato dell'esportazione

Gira su tutti e tre i target. Coperto dalla suite smoke senza
interfaccia grafica (`tools/smoke_run_samples.py`) e da
`tests/test_raycast_3_sample.py`, che pilota il vero ciclo di gioco:
danno, l'apertura e chiusura della finestra di invulnerabilità, la
morte che costa esattamente una vita, la guarigione del kit medico e
il suo limite, l'uscita bloccata dalle gemme, la transizione di stanza
nel tema di ghiaccio, e il rendering dell'HUD sopra la vista in prima
persona in **entrambe** le stanze.

Gli export Kivy e HTML5 sono stati verificati portare l'intero ciclo —
`no_more_health`, `alarm_0`, `draw_health_bar`, `obj_hud` e
`spr_medkit` sopravvivono tutti alla generazione del codice — ma il
playtest **visivo** per target vale la pena farlo con i propri occhi
prima di un rilascio.
