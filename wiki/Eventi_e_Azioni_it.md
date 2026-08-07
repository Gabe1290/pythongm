# Eventi e Azioni

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

> [Torna alla Home](Home_it)

Questo è un riferimento completo di tutti gli eventi e le azioni disponibili in PyGameMaker.

---

## Riferimento Eventi

### Evento Create
**Quando:** Una volta, quando un'istanza viene creata
**Uso:** Inizializzazione, impostazione variabili, avvio timer

### Evento Destroy
**Quando:** Quando l'istanza viene distrutta
**Uso:** Pulizia, generazione effetti, assegnazione punti

### Eventi Step

| Evento | Quando |
|-----------|-------|
| **Step** | Ad ogni frame (60 volte al secondo) |
| **Begin Step** | Prima dei controlli di collisione |
| **End Step** | Dopo tutti gli altri eventi |

### Eventi Alarm

| Evento | Quando |
|-----------|-------|
| **Alarm[0-11]** | Quando il contatore raggiunge 0 |

Usa l'azione `Set Alarm` per avviare un conto alla rovescia. I valori dell'allarme sono in frame (60 = 1 secondo a 60 FPS).

### Eventi Tastiera

| Evento | Quando |
|-----------|-------|
| **Keyboard [Tasto]** | Finché il tasto è tenuto premuto (ripetuto) |
| **Key Press [Tasto]** | Una volta, quando il tasto viene premuto |
| **Key Release [Tasto]** | Una volta, quando il tasto viene rilasciato |
| **No Key** | Quando nessun tasto è premuto |

Tasti disponibili: lettere (A-Z), numeri (0-9), tasti freccia, barra spaziatrice, invio, maiuscole, ctrl, alt, tasti funzione (F1-F12)

### Eventi Mouse

| Evento | Quando |
|-----------|-------|
| **Left Button** | Clic sinistro sull'istanza |
| **Right Button** | Clic destro sull'istanza |
| **Middle Button** | Clic col tasto centrale sull'istanza |
| **Left Press** | Tasto sinistro premuto (una volta) |
| **Left Release** | Tasto sinistro rilasciato (una volta) |
| **Mouse Enter** | Il cursore entra nell'istanza |
| **Mouse Leave** | Il cursore lascia l'istanza |
| **Global Left Button** | Clic sinistro ovunque |
| **Global Right Button** | Clic destro ovunque |

### Eventi di Collisione

| Evento | Quando |
|-----------|-------|
| **Collision with [Oggetto]** | Al contatto con l'oggetto specificato |

I controlli di collisione avvengono tra gli eventi Step e Draw.

### Altri Eventi

| Evento | Quando |
|-----------|-------|
| **Outside Room** | L'istanza è completamente fuori dalla stanza |
| **Intersect Boundary** | L'istanza tocca il bordo della stanza |
| **Game Start** | Il gioco si avvia (prima stanza caricata) |
| **Game End** | Il gioco termina |
| **Room Start** | Entrando in una stanza |
| **Room End** | Uscendo da una stanza |
| **No More Lives** | Le vite raggiungono 0 |
| **No More Health** | La salute raggiunge 0 |
| **Animation End** | L'animazione dello sprite è completata |

### Eventi Draw

| Evento | Quando |
|-----------|-------|
| **Draw** | Durante la fase di rendering |
| **Draw GUI** | Dopo aver disegnato la stanza (spazio schermo) |

---

## Riferimento Azioni

### Azioni di Movimento

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Imposta velocità** | Imposta la velocità di movimento | velocità, relativo |
| **Imposta direzione** | Imposta la direzione | direzione (0-360), relativo |
| **Set Horizontal Speed** | Imposta hspeed | hspeed, relativo |
| **Set Vertical Speed** | Imposta vspeed | vspeed, relativo |
| **Set Gravity** | Imposta la gravità | gravity, direction |
| **Set Friction** | Imposta l'attrito | friction |
| **Muovi verso un punto** | Muovi verso coordinate | x, y, velocità |
| **Inizia a muoverti (direzione)** | Muoviti in una direzione | direction, velocità |
| **Jump To Position** | Teletrasporta a coordinate | x, y, relativo |
| **Salta alla posizione iniziale** | Torna alla posizione di creazione | - |
| **Salta a posizione casuale** | Teletrasporto a una posizione completamente casuale (entrambi gli assi; allineabile alla griglia) | snap_h, snap_v |
| **Rimbalza** | Rimbalza dagli oggetti solidi | precise |

### Azioni di Istanza

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Create Instance** | Crea un nuovo oggetto | object, x, y, relativo |
| **Create Moving Instance** | Crea con velocità | object, x, y, speed, direction |
| **Destroy Instance** | Rimuove l'istanza | - |
| **Change Instance** | Trasforma in un altro oggetto | object, perform_events |

### Azioni di Temporizzazione

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Set Alarm** | Avvia un conto alla rovescia | alarm_number, steps |
| **Sleep** | Pausa l'esecuzione | millisecondi |

### Azioni Score/Vite/Salute

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Set Score** | Cambia il punteggio | value, relativo |
| **Set Lives** | Cambia le vite | value, relativo |
| **Set Health** | Cambia la salute | value, relativo |
| **Disegna punteggio** | Mostra il punteggio | x, y, caption |
| **Disegna vite** | Mostra le vite come immagini di sprite ripetute | x, y, sprite, scale, tiled |
| **Disegna barra della salute** | Mostra la salute come barra a due colori | x1, y1, x2, y2, back_color, bar_color |

### Azioni di Disegno

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Draw Sprite** | Disegna uno sprite | sprite, x, y, subimage |
| **Draw Text** | Mostra testo | x, y, text |
| **Draw Rectangle** | Disegna un rettangolo | x1, y1, x2, y2, filled |
| **Draw Circle** | Disegna un cerchio | x, y, radius, filled |
| **Draw Line** | Disegna una linea | x1, y1, x2, y2 |
| **Imposta colore di disegno** | Imposta il colore per i successivi Draw Text/Draw Rectangle/ecc. | color |
| **Imposta colore** | Imposta la tinta e la trasparenza di uno sprite (non il colore di disegno sopra) | color, alpha |
| **Imposta font di disegno** | Imposta font e allineamento per il prossimo disegno di testo | font, halign, valign |

### Azioni di Stanza

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Next Room** | Vai alla stanza successiva | transition |
| **Previous Room** | Vai alla stanza precedente | transition |
| **Restart Room** | Ripristina la stanza | - |
| **Go to Room** | Salta a una stanza specifica | room, transition |
| **If Next Room Exists** | Verifica se esiste una stanza successiva | - |
| **If Previous Room Exists** | Verifica se esiste una stanza precedente | - |

### Azioni Sound

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Play Sound** | Riproduci un effetto sonoro | sound, loop |
| **Stop Sound** | Ferma un suono | sound |
| **Check Sound Playing** | Verifica se un suono è in riproduzione | sound |
| **Play Music** | Riproduci musica di sottofondo | music, loop |
| **Stop Music** | Ferma tutta la musica | - |

### Azioni Variabili

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Imposta variabile** | Assegna un valore | variable, value, relativo |
| **Verifica variabile** | Controlla un valore | variable, value, operation |
| **Disegna variabile** | Mostra una variabile | x, y, variable |

### Azioni di Controllo del Flusso

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Verifica espressione** | Controllo condizionale (un'espressione booleana Python) | expression |
| **Altrimenti** | Ramo alternativo | - |
| **Start Block** | Inizia un gruppo di azioni | - |
| **End Block** | Termina un gruppo di azioni | - |
| **Repeat** | Ripeti N volte | count |
| **Exit Event** | Ferma l'evento attuale | - |

### Altre Azioni

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Show Message** | Mostra un messaggio popup | message |
| **Restart Game** | Riavvia il gioco | - |
| **End Game** | Chiude il gioco | - |

---

## Variabili Integrate

Queste variabili sono disponibili per tutte le istanze:

| Variabile | Descrizione |
|----------|-------------|
| `x` | Posizione orizzontale |
| `y` | Posizione verticale |
| `xstart` | Posizione x iniziale |
| `ystart` | Posizione y iniziale |
| `hspeed` | Velocità orizzontale |
| `vspeed` | Velocità verticale |
| `speed` | Velocità di animazione dello sprite (fotogrammi al secondo) — **non** la velocità di movimento. Non esiste una variabile integrata per la "velocità totale"; calcolala tu stesso da `hspeed`/`vspeed`, ad es. `(hspeed**2 + vspeed**2)**0.5` |
| `direction` | Direzione di movimento (0-360) |
| `gravity` | Gravità |
| `gravity_direction` | Direzione della gravità |
| `friction` | Attrito di movimento |
| `image_index` | Fotogramma di animazione attuale |
| `image_speed` | Velocità di animazione |
| `image_xscale` | Scala orizzontale |
| `image_yscale` | Scala verticale |
| `image_angle` | Angolo di rotazione |
| `visible` | Se viene disegnato |
| `solid` | Se è solido per le collisioni |
| `depth` | Profondità di disegno |
| `sprite_index` | Sprite attuale |
| `alarm[0-11]` | Timer degli allarmi |

### Variabili Globali

| Variabile | Descrizione |
|----------|-------------|
| `score` | Punteggio di gioco |
| `lives` | Vite del giocatore |
| `health` | Salute del giocatore (0-100) |
| `room` | Stanza attuale |
| `room_width` | Larghezza della stanza attuale |
| `room_height` | Altezza della stanza attuale |
| `mouse_x` | Posizione X del mouse |
| `mouse_y` | Posizione Y del mouse |

---

## Prossimi Passi

- [[Programmazione_Visuale_it]] - Usa i blocchi Blockly per la stessa logica
- [[Editor_Oggetti_it]] - Applica eventi e azioni agli oggetti
- [[Primo_Gioco_it]] - Vedi gli eventi in azione
