# Platform — Livello 2

Un platform a scorrimento laterale importato da GameMaker 8.x
(`samples/plateforme_2.gmk`). Rispetto a un primo livello minimale,
questo espande la lista degli oggetti da un singolo giocatore + un
blocco a quattro oggetti (una piattaforma base più varianti
orizzontale e verticale che ne ereditano), disposti in una stanza di
126 istanze costruita da un set di tessere automatiche a tema neve,
invece di qualche blocco posizionato a mano.

**Dove si colloca:** parte della famiglia `plateforme_*`, e — a
differenza del minimale `plateforme_1` — qui appare lo **sfondo a
tessere**: 127 pezzi di tessere sfondo posizionati individualmente
(l'array `tiles` della stanza) più un'immagine di sfondo sfumato
(`fond_degrade`), stratificati sotto gli *oggetti* mattone solidi che
gestiscono ancora la collisione. Questo è il passo che `plateforme_*`
aggiunge oltre `maze_*`; vedi
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
per la progressione completa.

**Audio e musica:** nessuno — nessun file audio è fornito con questo esempio.

## Come si gioca

- **Freccia sinistra/destra** — muove il pinguino (`obj_personnage`) sinistra/destra.
- **Freccia su** — salto, ma solo mentre si sta su una piattaforma
  solida (controllato tramite un test di collisione un pixel sotto il giocatore).
- **Obiettivo** — non c'è un oggetto obiettivo/bandiera in questo
  esempio; è un layout di piattaforme da esplorare/attraversare sulle
  piattaforme `obj_brique*`.
- **Condizione di sconfitta** — nessuna è definita (nessun pericolo,
  nessun oggetto letale, nessun controllo morte-per-caduta); la riga
  di mattoni in basso della stanza funge da pavimento.

## Struttura del progetto

| File | Scopo |
| --- | --- |
| `project.json` | Manifesto del progetto — impostazioni finestra/stanza, copie di risorse incorporate. |
| `rooms/niveau_01.json` | L'unica stanza: 800×640, 126 istanze + 127 tessere di sfondo. Fonte di verità per il contenuto della stanza (la lista `instances` incorporata di `project.json` è vuota). |
| `objects/*.json` | File collaterali per oggetto dei 4 oggetti; identici alle copie incorporate in `project.json` a questa data. |
| `sprites/` | 5 risorse sprite (strisce di camminata del giocatore e blocchi piattaforma solidi). |
| `backgrounds/` | Set di tessere neve (`tuiles_neige.png`, usato come sorgente tessere automatiche) e un piccolo sfumato verticale (`fond_degrade.png`) stirato come sfondo della stanza. |
| `CREDITS.txt` | Avviso di licenza per la grafica sprite/sfondo (vedi Risorse sotto). |

## Oggetti

| Oggetto | Ruolo | Eventi chiave |
| --- | --- | --- |
| `obj_personnage` | Giocatore (pinguino) — movimento, salto, gravità, rilevamento del terreno | create, step, collision_with_obj_brique, keyboard (left, right, up), keyboard_release (LEFT, RIGHT) |
| `obj_brique` | Blocco piattaforma solido base (32×32) | nessuno (nessun evento; solo flag solido) |
| `obj_brique_h` | Variante larga piattaforma solida (32×16), figlio di `obj_brique` | nessuno |
| `obj_brique_v` | Variante stretta piattaforma solida (8×16), figlio di `obj_brique`; definita ma non posizionata in `niveau_01` | nessuno |

## Risorse

5 sprite (`spr_pingus_dr`/`spr_pingus_ga` strisce di camminata da 8
frame, più tre blocchi placeholder a colore pieno a 32×32 / 32×16 /
8×16) e 2 sfondi; nessun suono. La grafica di sprite e sfondi è
adattata dal progetto Pingus (GPL-3.0-or-later) — vedi `CREDITS.txt`
per l'attribuzione completa e i termini di licenza; questa README non
riafferma né estende quelle dichiarazioni.

## Cose da modificare

- La velocità orizzontale del giocatore è un fisso `hspeed = 4` negli
  eventi tastiera.
- L'impulso di salto è `vspeed = -10`; la gravità di caduta è `0,45`
  (applicata solo in aria), con un tetto di velocità terminale a
  `vspeed = 24`.
- La dimensione della stanza è 800×640 a `room_speed = 30`.

## Stato dell'esportazione

Questo esempio è elencato nella lista `SAMPLES` di
`tools/smoke_run_samples.py`, quindi riceve un passaggio smoke senza
interfaccia grafica (il vero ciclo di gioco eseguito per ~180 frame
con input da tastiera iniettato) a ogni esecuzione di quell'harness.
Nessuna verifica per target di esportazione specifico (Kivy/HTML5) è
stata fatta specificamente per questo esempio. È esposto nella scheda
Welcome dell'IDE come "Platform — Level 2" (`widgets/welcome_tab.py`).
