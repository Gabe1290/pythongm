# Labirinto — Livello 4

Il più grande esempio di labirinto: **21 stanze** di puzzle a griglia
con **tessere a nastro trasportatore**, tre tipi di **mostro**,
**bombe/esplosioni** che sfondano i muri, un **anello di potere** che
spaventa i mostri, e collezionabili (diamanti, anelli, cuori). Un
progetto pygm2 nativo importato da `maze_4.gmk` (GameMaker 8.x),
scritto/salvato nel formato JSON proprio di pygm2.

**Dove si colloca:** il quarto livello `maze_*` e il più ricco
meccanicamente — sovrappone il movimento a nastro trasportatore,
molteplici tipi di nemici, un ciclo power-up spaventa/mangia, e una
bomba che distrugge muri sul movimento a griglia base di `maze_1..3`.
È stato rimosso in rc.12 per bug di import GMK e **riaggiunto dopo
l'irrobustimento dell'importatore** (16/07/2026); vedi
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
e [`../../docs/maze_4_testing_pass.md`](../../docs/maze_4_testing_pass.md).

**Audio e musica:** 10 effetti sonori sono inclusi. Una traccia legacy
dell'era GM8 (`sound_background`) è in un formato che pygame non può
caricare e viene saltata a runtime (come per maze_2/maze_3); il
gameplay non ne è influenzato.

## Come si gioca

- Le **frecce direzionali** muovono il giocatore di una cella di
  griglia alla volta; i muri bloccano il movimento.
- Le **tessere a nastro trasportatore** (frecce su/giù/sinistra/destra
  sul pavimento) trasportano automaticamente il giocatore nella loro
  direzione mentre ci sta sopra.
- I **mostri** vengono in tre tipi (`monster_all` vaga liberamente;
  `monster_ud` pattuglia verticalmente; `monster_lr` orizzontalmente)
  — toccarne uno costa una vita e riavvia la stanza.
- Prendi un **anello** e ogni mostro diventa **spaventato** (lo sprite
  cambia, si bloccano) per ~10 secondi — toccane uno allora per
  mangiarlo e ottenere punti; tornano normali alla fine del timer.
- Le **bombe** esplodono in un'onda d'urto che **distrugge i muri
  circostanti** — usata per aprire sezioni altrimenti sigillate.
- Raccogli **diamanti/anelli/cuori**; raggiungi l'**obiettivo** per
  avanzare. L'HUD (punteggio + vite) viene disegnato lungo il basso da
  `controller_main`.

## Una nota sulla correzione manuale (documentazione onesta)

Il movimento di pygm2 *scivola fino al contatto* con un muro, mentre
GameMaker 8 *annulla* una mossa bloccata tornando alla posizione
precedente alla mossa — il comportamento GM manteneva il giocatore
allineato alla griglia gratuitamente. Senza di ciò, premere contro un
muro a filo lasciava il giocatore a pochi pixel dalla griglia 32, e i
controlli di movimento a griglia/nastro trasportatore si bloccavano di
conseguenza. Quindi `obj_person` porta una deliberata **correzione
manuale di gameplay**: `snap_to_grid(32)` sui suoi eventi di
collisione `wall_corner`/`wall_horizontal`/`wall_vertical`. Questo
rispecchia la stessa correzione distribuita in `maze_1` ed è una
correzione, non un cambiamento di fedeltà — un nuovo import dal `.gmk`
non la includerà (vedi sotto).

## Struttura del progetto

| File | Scopo |
|---|---|
| `project.json` | Manifesto — impostazioni finestra/stanza, risorse incorporate, e ordine delle stanze |
| `rooms/*.json` | 21 stanze; ordine di gioco `room_start` poi in ordine decrescente (`room14`, `room13`, …) — l'ordine proprio del gioco originale, importato fedelmente |
| `objects/*.json` | 24 definizioni di oggetti (fonte di verità; fuse sopra le copie incorporate al caricamento) |
| `sprites/` | 24 sprite PNG + metadati `.json` |
| `sounds/` | 10 effetti sonori |
| `backgrounds/` | 2 sfondi |
| `CREDITS.txt` | Avviso di licenza delle risorse |

## Oggetti (24)

Giocatore/HUD: `obj_person`, `controller_main` (disegna
punteggio+vite), `controller_start`.
Muri: `wall_horizontal`, `wall_vertical`, `wall_corner`, `block`.
Nemici: `monster_all`, `monster_ud`, `monster_lr`.
Power-up / oggetti: `ring` (spaventa), `bomb` + `explosion`
(distruggono muri), `obj_diamond`, `heart`, `bonus`, `obj_door`,
`obj_goal`, `trigger`, `hole`.
Tessere a nastro trasportatore: `move_up`, `move_down`, `move_left`, `move_right`.

## Risorse

24 sprite, 10 suoni, 2 sfondi, 1 font — tutti importati da
`maze_4.gmk`. Vedi `CREDITS.txt` e
[`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md) per la provenienza.

## Cose da modificare

- **Velocità nastro/giocatore** — i nastri si muovono a velocità `8`;
  il movimento a griglia da tastiera a `4` (parametri per azione su `obj_person`).
- **Durata dello spavento** — l'anello imposta `set_alarm` a `300`
  passi su `monster_all`.
- **Ordine delle stanze** — le stanze giocano nell'ordine delle chiavi
  del dizionario stanze di `project.json`; riordinale nell'IDE
  (trascina nell'albero delle risorse) e Test Game seguirà.

## Stato dell'esportazione

Coperto dalla suite di smoke-test senza interfaccia grafica
(`tools/smoke_run_samples.py`, che elenca `maze_4`) e dalla suite di
regressione import
(`tests/test_gmk_treasure_maze4_import.py`). Verificato in un playtest
manuale durante l'irrobustimento dell'importatore di luglio 2026 (vedi
il documento del test). Esposto nella scheda Welcome come
**"Maze — Level 4"**.

## Rigenerazione dall'originale `.gmk`

Il gemello `../maze_4.gmk` è la fonte GameMaker 8.x:

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/maze_4.gmk', '/tmp/maze_4_reimport')"
```

Un import fresco è fedele al gioco originale, **meno** la correzione
manuale `snap_to_grid` sui muri descritta sopra — riapplicala (aggiungi
`snap_to_grid` con grid_size 32 ai tre eventi di collisione muro di
`obj_person`) dopo la rigenerazione.
