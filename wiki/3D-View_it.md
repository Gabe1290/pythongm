# Vista 3D (rendering in prima persona con raycast)

*[Home](Home_it) | [Riferimento completo delle azioni](Full-Action-Reference_it) | [Estensioni](Extensions_it)*

---

PyGameMaker può renderizzare una stanza come **vista 3D in prima persona in stile
Doom/Wolfenstein** invece della consueta vista dall'alto — muri come strisce
verticali, un pavimento e un soffitto colorati o texturizzati, un cielo panoramico
opzionale e sprite "billboard" per oggetti da raccogliere e mostri. La *logica* del
gioco (movimento, collisioni, eventi) non cambia; cambia solo **come** viene
disegnata la stanza.

Questa funzione è fornita dall'**estensione 2.5D Raycast** integrata (la funzione
[Vista 3D](Extensions_it)), attivata per impostazione predefinita. Si esporta verso
tutti e tre i target — computer, HTML5 e Kivy/Android — così un gioco in prima
persona funziona allo stesso modo ovunque.

Gli esempi inclusi **`raycast_1`–`raycast_4`** sono giochi completi e giocabili (un
labirinto semplice, un gioco a due livelli con oggetti da raccogliere e un mostro,
una variante con salute e kit medici e una dimostrazione di barra di stato in stile
DOOM).

---

## Come funziona

- Una stanza diventa in prima persona quando un oggetto esegue l'azione **Abilita
  vista Raycast** (di solito nel suo evento Crea). Quell'oggetto è la **camera** per
  impostazione predefinita — la sua posizione è il punto di vista e il suo
  `facing_angle` (angolo di sguardo) è la direzione dello sguardo.
- **I muri sono le tue istanze solide.** Il renderer ricava sottili *bordi* di muro
  da ogni oggetto solido nella stanza, su una griglia la cui dimensione è il
  parametro `cell_size` dell'azione (32 per impostazione predefinita — la dimensione
  usata da tutti gli esempi `maze_*`/`raycast_*`). Un oggetto solido con sprite di
  muro texturizza il muro; altrimenti si usa un colore `wall_color` uniforme.
- **La camera ruota** cambiando `facing_angle` (vedi **Imposta angolo di sguardo**)
  e si muove con le consuete azioni di movimento (ad es. `set_direction_speed` con
  `direction = "facing_angle"` per camminare in avanti).
- **Le istanze non solide con sprite** (obiettivi, oggetti, mostri) si disegnano come
  **billboard** rivolti verso la camera, correttamente occlusi dai muri.

---

## Le azioni (categoria **Vista 3D**)

| Azione | Cosa fa |
|--------|---------|
| **Abilita vista Raycast** (`enable_raycast_view`) | Passa la stanza corrente alla vista in prima persona (o ne esce) e configura la camera: `camera_object`, `fov`, `render_distance`, `cell_size`, colori e texture di muro/pavimento/soffitto, una `sky_texture` opzionale e `viewport_height` (una barra in stile DOOM). |
| **Imposta angolo di sguardo** (`set_facing_angle`) | Ruota la camera. Angolo in gradi GameMaker (0 = destra, 90 = su); `relative` somma all'angolo corrente. |
| **Disegna minimappa** (`draw_minimap`) | Disegna una minimappa orientata a nord dei muri della stanza con un indicatore "sei qui". Un'azione HUD — mettila in un evento Disegna. |
| **Disegna HUD DOOM** (`draw_doom_hud`) | Disegna una barra di stato inferiore in stile DOOM: barra della salute + numero, un volto reattivo alla salute, punteggio, vite e un contatore di obiettivo. Si abbina a `viewport_height` di `enable_raycast_view`. |

Vedi il [Riferimento completo delle azioni](Full-Action-Reference_it#3d-view) per
tutti i parametri.

---

## Un controller minimo in prima persona

Nell'oggetto giocatore:

- **Crea:** `Abilita vista Raycast` (lascia `camera_object` vuoto così che il
  giocatore *sia* la camera).
- **Tastiera Sinistra / Destra:** `Imposta angolo di sguardo` con `relative` attivo
  (ad es. ±3°).
- **Tastiera Su:** `Imposta direzione e velocità` con `direction = facing_angle` e
  una piccola velocità per camminare in avanti.

Costruisci la stanza con oggetti-muro solidi su una griglia di 32 pixel, proprio
come gli esempi `maze_*` — il raycaster trasforma quei muri in corridoi 3D.

---

## Note e limiti

- Le azioni HUD (`draw_minimap`, `draw_doom_hud` e le consuete `draw_score` /
  `draw_lives` / `draw_text`) si sovrappongono **sopra** l'immagine in prima persona,
  in coordinate schermo.
- I muri sono statici per la passata in prima persona — i muri creati/distrutti dopo
  il caricamento della stanza non rimodellano la geometria 3D.
- Se l'estensione 2.5D Raycast è **disattivata**, una stanza che abilita la vista si
  renderizza semplicemente dall'alto e l'IDE ti avvisa al caricamento — vedi
  [Estensioni](Extensions_it).

---

## Vedi anche

- [Estensioni](Extensions_it) — come viene fornita la Vista 3D e come disattivarla
- [Riferimento completo delle azioni](Full-Action-Reference_it#3d-view) — le quattro azioni in dettaglio
- [Editor delle stanze](Editor_Stanze_it) — posizionare gli oggetti-muro da cui è costruita la vista
