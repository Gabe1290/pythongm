# 2.5 D — Livello 1

Una vista in prima persona in stile Doom/Wolfenstein dello **stesso
layout labirinto di `maze_1`** — stesse stanze, stesso obiettivo,
stessi percorsi risolvibili. Dove `maze_1` mostra il labirinto
dall'alto con blocchi muro a cella intera, questo esempio lo rende
come proiezione raycast con **muri sottili sui bordi** (partizioni da
8px poste sui confini delle celle, non blocchi da 32px che riempiono
una cella) — corridoi genuinamente proporzionati in stile Wolfenstein,
non solo una camera in prima persona incollata sul vecchio layout a
blocchi. `rooms/room0.json` e `room1.json` sono stati rigenerati dal
layout originale di `maze_1` tramite una conversione che preserva la
topologia (stessa connettività/risolvibilità, geometria muri diversa),
non riprogettati a mano. Vedi
[`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) nella
radice del repository per il piano ingegneristico completo, inclusa
la sezione "Complete rethink" sul perché i muri a cella intera non
funzionavano per uno spazio di svolta reale.

**Questo è 2,5D, non 3D** — la logica di gioco è completamente
invariata rispetto a `maze_1` (stessa posizione 2D `x`/`y`, stessa
collisione muro solido); solo l'*immagine* è falsificata per sembrare
tridimensionale. Non c'è sguardo verticale (nessun pitch), i corridoi
devono essere allineati alla griglia, e non c'è vera sovrapposizione
stanza-su-stanza. Questa è una limitazione deliberata e onesta, non
una funzionalità mancante — vedi la nota pedagogica "why raycasting"
del documento di piano.

**Stato — completamente texturizzato (muri, cielo, pavimento,
billboard) su tutti e tre i target: desktop (pygame), HTML5, e nativo
(Kivy).** I muri campionano una **texture di mattoni**
(`spr_wall_texture`, tramite `wall_texture`): ogni colonna dello
schermo campiona una striscia verticale nella posizione di impatto del
raggio, scalata per distanza, con la faccia del muro rivolta lontano a
metà luminosità come indizio di profondità gratuito. Il soffitto è un
**cielo in stile DOOM** (`spr_sky`, tramite `sky_texture`) — un
panorama che scorre orizzontalmente mentre giri (un giro completo di
360° lo fa scorrere una volta) e che *non* si allontana con la
distanza, quindi si legge come un orizzonte infinitamente lontano. Il
pavimento è una **texture di pietra proiettata** (`spr_floor`, tramite
`floor_texture`) — un cast del pavimento a bassa risoluzione (il
calcolo per pixel a piena risoluzione era ~13× troppo lento in Python
puro; `floor_cast_res` imposta il sotto-campionamento, 4 ≈ 5ms) che si
ripete per cella griglia e incontra le basi dei muri senza soluzione
di continuità. `obj_goal` si rende come sprite billboard rivolto alla
camera (scalato per distanza, occluso dai muri) — vedi "Cosa c'è di
nuovo qui". Per tornare all'aspetto piatto, svuota
`wall_texture`/`sky_texture`/`floor_texture` sull'azione `enable_raycast_view`.

## Come si gioca

- **Su/Giù** muovono avanti/indietro nella direzione in cui si sta
  guardando (movimento continuo, non agganciato alla griglia — i muri
  bloccano comunque tramite la normale collisione dell'istanza solida
  del motore, invariata rispetto a `maze_1`).
- **Sinistra/Destra** girano sul posto (ruotano `facing_angle`,
  indipendente dal movimento — puoi girare da fermo).
- **Obiettivo:** trovare la meta. Toccarla avanza alla stanza
  successiva se ne esiste una (stessa logica `obj_goal` di `maze_1`,
  file identico byte per byte).

## Cosa c'è di nuovo qui, lato motore

- `GameInstance.facing_angle` — direzione dello sguardo persistente
  (convenzione angolo GM: 0=destra, 90=su, 180=sinistra, 270=giù),
  impostata tramite la nuova azione `set_facing_angle`. A differenza
  della proprietà `direction` esistente (derivata da
  `hspeed`/`vspeed`, sempre 0 da fermi), questa sopravvive da fermi —
  richiesta per controlli FPS "gira sul posto".
- `enable_raycast_view` — commuta la stanza corrente sulla camera
  raycast (legata all'istanza chiamante, qui l'evento `create` di
  `obj_person`) o torna al rendering normale dall'alto.
- La mappa dei muri è **derivata dalle istanze solide esistenti di
  questa stanza**, non da un formato di creazione separato — ma a
  partire dal rifacimento a muro sottile, è derivata come bordi reali
  (`GameRoom._build_raycast_walls`), non come occupazione grossolana
  per cella: il rapporto d'aspetto dello sprite di un'istanza solida
  decide se è un segmento di muro orizzontale o verticale
  (approssimativamente quadrato ricade sul bloccare un'intera cella,
  per retrocompatibilità con contenuti non a muro sottile). Questo è
  ciò che fa sì che lo spessore di 8px di `obj_wall_h`/`obj_wall_v`
  conti realmente sia per il rendering sia per lo spazio di svolta,
  non solo visivamente — vedi la sezione "Complete rethink" del
  documento di piano.
- **Sprite billboard.** Ogni istanza visibile, non solida, con uno
  sprite (qui `obj_goal`) si disegna come sprite 2D rivolto alla
  camera nella vista raycast, scalato per distanza e centrato
  verticalmente sull'orizzonte come una striscia di muro.
  L'occlusione è reale ritaglio per colonna contro le distanze dei
  muri già calcolate per il passaggio muri di quel frame, così una
  meta dietro un muro è correttamente nascosta invece di trasparire.
  Questa è una prima versione della Fase 6 del documento di piano (i
  muri disegnano solo istanze solide; i billboard solo quelle non
  solide, quindi niente viene disegnato due volte) — nessuna
  fusione di trasparenza parziale, nessuna rotazione per corrispondere
  all'orientamento proprio dello sprite, solo la scala e il ritaglio
  piatto che un motore in stile Wolfenstein usava per raccolte e nemici.

## Struttura del progetto

| File | Scopo |
|---|---|
| `project.json` | Manifesto del progetto |
| `rooms/room0.json`, `rooms/room1.json` | Stessa *topologia* di labirinto di `maze_1`, rigenerata con muri sottili sui bordi (vedi l'algoritmo di conversione del documento di piano) |
| `objects/obj_person.json` | Giocatore/camera — `create` attiva la vista raycast, gli eventi `keyboard` guidano girare + avanti/indietro, registra `collision_with_obj_wall_h`/`_v` |
| `objects/obj_goal.json` | Oggetto obiettivo — identico byte per byte a quello di `maze_1` |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segmenti muro sottili (32×8 e 8×32) — sostituiscono l'unico `obj_wall` a blocco intero di `maze_1` |
| `sprites/` | `spr_person`, `spr_goal` (da `maze_1`) più gli sprite propri di questo esempio `spr_wall_h`/`spr_wall_v` (placeholder sottili a colore pieno — mai renderizzati in modalità prima persona, contano solo le loro dimensioni per collisione/raycasting) |

## Cose da modificare

- Il tasso di svolta è `3`°/frame (`room_speed: 30` → 90°/sec) e la
  velocità di movimento è `3` px/frame, entrambi hardcoded negli
  eventi `keyboard` di `obj_person`.
- FOV `66`°, `render_distance` `20` celle, `cell_size` `32` — tutti
  parametri `enable_raycast_view` sull'evento `create` di `obj_person`.
- I colori di muro/pavimento/soffitto sono anch'essi parametri
  `enable_raycast_view` — il fallback piatto quando la texture
  corrispondente è svuotata.
- Lo spessore del muro è `8`px, hardcoded nella conversione che ha
  generato `rooms/*.json` (non un parametro a runtime) — rigenera le
  stanze per cambiarlo.
- `spr_person` è **16×16** con una bbox di collisione
  `(4,4)-(12,12)` — il giocatore è stato dimezzato dal vecchio 32×32
  (e ricentrato nella sua cella iniziale, così la camera resta ancora
  al centro della cella) perché il giocatore a piena dimensione
  faceva sembrare i corridoi da 1 cella angusti; un ingombro più
  piccolo dà molto più spazio per muoversi. La **texture di mattoni**
  del muro è stata similmente resa più fine (mattoni a mezza scala)
  così i muri si leggono come più distanti — entrambe le modifiche
  scambiano "attaccato al naso" per un senso di spazio più ampio.

## Stato dell'esportazione

La vista in prima persona **completa** ora si rende su **tutti e tre
i target** — desktop (pygame), **HTML5**
(`export/HTML5/templates/engine.js`), e **nativo/Kivy**
(`export/Kivy/kivy_exporter.py`) — con controlli di sguardo tramite
angolo di orientamento, muri texturizzati e piatti, il cielo
scorrevole, il cast del pavimento texturizzato a bassa risoluzione, e
gli sprite billboard con ritaglio di occlusione. I tre renderer non
condividono codice (tre copie scritte a mano), quindi il loro nucleo
DDA è bloccato insieme da `tests/test_raycast_export_parity.py`
(uguaglianza numerica esatta desktop↔Kivy su una matrice di 260
raggi; parità strutturale HTML5, poiché non c'è motore JS in CI).

Il cast del pavimento usa lo stesso approccio calcola-a-bassa-
risoluzione-poi-scala su ogni target (`floor_cast_res`, default 4); le
misurazioni di timing su hardware reale hanno confermato che rientra
nel budget (browser ~0,4 ms a res=2; Kivy/AMD 840M ~5 ms a res=4). Un
progetto può ancora svuotare `floor_texture` per un pavimento
`floor_color` piatto.

Disponibile dalla scheda Welcome dell'IDE — scegli **"2.5 D — Level
1"** dal menu a tendina *Choose a sample* (aprire un esempio lo copia
nei tuoi Documenti, così l'originale in bundle rimane intatto).
