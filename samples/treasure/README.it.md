# Treasure

Una caccia nel labirinto in stile Pac-Man: l'**esploratore** vaga per
un labirinto murato raccogliendo **punti tesoro**, inseguito da
**mostri** che scelgono una nuova direzione a ogni incrocio. Prendi
una **pillola di potere** (`pil`) e le sorti si invertono — ogni
mostro diventa **spaventato** e può essere mangiato per punti bonus
finché l'effetto non svanisce. Questo è un progetto pygm2 nativo
importato da `treasure.gmk` (GameMaker 8.x); il progetto stesso è
scritto/salvato nel formato JSON proprio di pygm2.

**Dove si colloca:** `treasure` sta accanto alla famiglia `maze_*` —
costruito da GameObject + azioni integrate e l'editor eventi visuale —
ma aggiunge uno **script a livello di progetto** (`adapt_direction`,
l'IA del mostro agli incroci) e un ciclo di stati in stile GM
**"caccia / power-up / fuga"** attraverso i suoi oggetti. Era uno dei
due esempi rimossi in rc.12 per bug di import GMK e **riaggiunto dopo
l'irrobustimento dell'importatore** (16/07/2026); vedi
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
e [`../../docs/treasure_testing_pass.md`](../../docs/treasure_testing_pass.md).

**Audio e musica:** 6 effetti sonori sono inclusi (raccolta, pillola
di potere, mangia-mostro, morte, …). Una traccia legacy dell'era GM8
(`music`) è in un formato che pygame non può caricare ed è saltata a
runtime — come la musica di sottofondo degli altri esempi labirinto;
il gameplay non ne è influenzato.

## Come si gioca

- Le **frecce direzionali** muovono l'esploratore attraverso il
  labirinto; i muri bloccano il movimento.
- Raccogli ogni **punto tesoro** per completare il livello (4 stanze
  in totale).
- I **mostri** ti inseguono; toccarne uno costa normalmente una vita.
- Prendi una **pillola di potere** e i mostri diventano
  **spaventati** (il loro sprite cambia) per alcuni secondi — tocca
  allora un mostro spaventato per **mangiarlo** (+punti; si
  teletrasporta al suo punto di partenza tornando un mostro normale).
  L'effetto svanisce dopo un timer.

## L'IA del mostro (script `adapt_direction`)

Ogni mostro chiama lo script di progetto `adapt_direction` dai suoi
eventi step/collisione. È vero Python pygm2 — a un possibile incrocio
considera casualmente di girare, controllando
`game.check_collision_at_position(...)` per un muro prima di
impegnarsi, così i mostri vagano nel labirinto invece di correre in
linea retta. Apri la risorsa **Scripts** per leggerlo; l'azione
`execute_script` negli eventi del mostro mostra dove viene chiamato.

## Struttura del progetto

| File | Scopo |
|---|---|
| `project.json` | Manifesto — impostazioni finestra/stanza, risorse incorporate, lo script `adapt_direction`, e l'ordine delle stanze |
| `rooms/room0..3.json` | I quattro livelli labirinto (istanze per stanza) |
| `objects/*.json` | Le 7 definizioni di oggetti (fonte di verità; fuse sopra le copie incorporate al caricamento) |
| `sprites/` | 10 sprite PNG + metadati `.json` |
| `sounds/` | 6 effetti sonori |
| `backgrounds/` | 1 sfondo |
| `CREDITS.txt` | Avviso di licenza delle risorse |

## Oggetti

| Oggetto | Ruolo |
|---|---|
| `explorer` | Personaggio giocatore; raccoglie tesori, mangia mostri spaventati, muore a contatto con quelli normali |
| `monster` | Inseguitore; vaga tramite `adapt_direction`; si trasforma in `scared` su una pillola di potere |
| `scared` | Un mostro nel suo stato di fuga; commestibile; torna a `monster` dopo un timer |
| `pil` | Pillola di potere — spaventa ogni mostro quando raccolta |
| `point` | Tesoro da raccogliere |
| `bonus` | Raccolta extra |
| `wall` | Muro solido statico del labirinto |

## Risorse

10 sprite, 6 suoni, 1 sfondo — tutti importati da `treasure.gmk`. Vedi
`CREDITS.txt` e [`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md)
per la provenienza.

## Cose da modificare

- **Durata dello spavento** — l'alarme della pillola di potere è
  `160` passi nell'evento `collision_with_pil` di `explorer`;
  aumentala per una fase di fuga più lunga.
- **Probabilità di svolta del mostro** — i test
  `random.random() * 3 < 1` nello script `adapt_direction` impostano
  quanto spesso i mostri girano a un incrocio.
- **Valori del punteggio** — i punti tesoro e mangia-mostro sono
  azioni `set_score` (relative) sui rispettivi eventi di collisione.

## Stato dell'esportazione

Coperto dalla suite di smoke-test senza interfaccia grafica
(`tools/smoke_run_samples.py`, che elenca `treasure`) e dalla suite di
regressione import (`tests/test_gmk_treasure_maze4_import.py` +
`tests/test_gmk_applies_to.py`). Verificato in un playtest manuale
durante l'irrobustimento dell'importatore di luglio 2026 (vedi il
documento del test). Esposto nella scheda Welcome come **"Treasure"**.

## Rigenerazione dall'originale `.gmk`

Il gemello `../treasure.gmk` è la fonte GameMaker 8.x. Per rigenerare:

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/treasure.gmk', '/tmp/treasure_reimport')"
```

Un import fresco è fedele al gioco originale a partire
dall'irrobustimento dell'importatore di luglio 2026 (nessuna
correzione manuale applicata a questo esempio).
