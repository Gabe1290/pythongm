# Labirinto — Livello 1

Un gioco di labirinto a griglia visto dall'alto: guida lo sprite del
giocatore attraverso un labirinto delimitato da muri per raggiungere
la tessera obiettivo, che fa avanzare alla stanza successiva. Questo è
un progetto pygm2 nativo (nessun file `.gmk` gemello — le sue risorse
sono state originariamente importate tramite un import GameMaker 8.x,
vedi CREDITS.txt, ma il progetto stesso è scritto/salvato nel formato
JSON proprio di pygm2).

**Dove si colloca:** `maze_*` è la prima delle tre famiglie di esempi
in una progressione approssimativa di tecniche di creazione (oggetti/
sprite integrati → sfondi a tessere aggiunti di `plateforme_*` →
giochi puro-script `execute_code` di `match3_*`) — vedi
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
per il quadro completo. Questo esempio usa solo GameObject + sprite,
nessuna immagine di sfondo e nessuna tessera a livello di stanza.

**Audio e musica:** nessuno — nessun file audio è fornito con questo esempio.

## Come si gioca

- Le **frecce direzionali** (su/giù/sinistra/destra) muovono il
  giocatore di una cella della griglia (32px) alla volta; il movimento
  è agganciato alla griglia tramite
  `test_alignment`/`snap_to_grid` (griglia 32×32).
- I muri (`obj_wall`) sono solidi — camminarci contro ferma il
  giocatore e lo riaggancia alla griglia.
- **Obiettivo:** raggiungere la tessera obiettivo (`obj_goal`).
  Toccarla fa avanzare alla stanza successiva se ne esiste una, o
  riavvia il gioco se non ce n'è una.
- **Scorciatoie di debug:** premere `N` sull'obiettivo salta alla
  stanza successiva (se presente); premere `P` salta alla stanza
  precedente (se presente) — stessa logica di avanzamento/riavvio del
  toccare l'obiettivo.
- Nessun tracciamento di vite/punteggio/salute è usato in questo
  esempio (la salute viene reimpostata tramite `set_health`
  all'avanzamento di stanza, ma mai mostrata).

## Struttura del progetto

| File | Scopo |
|---|---|
| `project.json` | Manifesto del progetto — impostazioni finestra/stanza e copie incorporate di tutte le risorse |
| `rooms/room0.json` | Layout del labirinto per la stanza 0 (131 istanze: muri, partenza giocatore, obiettivo) |
| `rooms/room1.json` | Layout del labirinto per la stanza 1 (130 istanze) |
| `objects/obj_person.json` | Definizione dell'oggetto giocatore (fonte di verità; corrisponde alla copia incorporata in `project.json`) |
| `objects/obj_goal.json` | Definizione dell'oggetto obiettivo |
| `objects/obj_wall.json` | Definizione dell'oggetto muro |
| `sprites/` | `spr_person.png`, `spr_wall.png`, `spr_goal.png` + i rispettivi metadati `.json` |
| `CREDITS.txt` | Avviso di licenza delle risorse per questo esempio |

I file collaterali `objects/*.json` sono stati verificati rispetto
alle copie incorporate di `project.json` e sono identici in questo
esempio — nessuna obsolescenza trovata.

## Oggetti

| Oggetto | Ruolo | Eventi chiave |
|---|---|---|
| `obj_person` | Personaggio controllato dal giocatore; movimento a griglia | create-implicito tramite tastiera, keyboard (down, right, up, left, nokey), collision_with_obj_wall |
| `obj_goal` | Uscita del livello; avanza/riavvia al tocco o al tasto di debug | collision_with_obj_person, keyboard_press (p, n) |
| `obj_wall` | Muro solido statico del labirinto, blocca il movimento | (nessuno — solo collisore passivo) |

## Risorse

3 sprite (`spr_person`, `spr_wall`, `spr_goal`, ciascuno 32×32, singolo
frame, collisione precisa al pixel), 0 suoni. Licenze: `spr_person.png`
e `spr_wall.png` sono CC0 (pubblico dominio), opere dell'autore di
pygm2; la provenienza di `spr_goal.png` non è ancora documentata —
vedi `CREDITS.txt` in questa cartella e `docs/ASSET_LICENSES.md` nella
radice del repository per il quadro completo.

## Cose da modificare

- La velocità di movimento del giocatore è `4` (celle griglia/passo)
  mentre l'arresto per urto contro muro usa velocità `8` — entrambi
  sono parametri d'azione hardcoded per pressione tasto in
  `obj_person`.
- La dimensione della griglia è `32` (corrisponde agli sprite 32×32);
  cambiarla richiede modifiche corrispondenti alle chiamate
  `snap_to_grid`/`test_alignment` e ai layout delle stanze.
- Le stanze sono `480×480` a `room_speed: 30` — piccoli labirinti a
  schermo singolo senza scorrimento.
- I tasti di debug `N`/`P` su `obj_goal` permettono di saltare tra
  room0/room1 senza toccare l'obiettivo — utile per testare, ma facile
  da attivare accidentalmente durante il gioco.

## Stato dell'esportazione

Coperto dalla suite di smoke-test senza interfaccia grafica
(`tools/smoke_run_samples.py`, che elenca `maze_1` e lo esegue per
~180 frame con input da tastiera iniettato); non verificato
individualmente per ogni target di esportazione (Kivy/Web). Esposto
nella scheda Welcome dell'IDE come "Maze — Level 1"
(`widgets/welcome_tab.py`).
