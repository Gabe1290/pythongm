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
| **Inizio dello step** | Prima dei controlli di collisione |
| **Fine dello step** | Dopo tutti gli altri eventi |

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
| **Fuori dalla stanza** | L'istanza è completamente fuori dalla stanza |
| **Tocca il bordo della stanza** | L'istanza tocca il bordo della stanza |
| **Inizio del gioco** | Il gioco si avvia (prima stanza caricata) |
| **Fine del gioco** | Il gioco termina |
| **Inizio della stanza** | Entrando in una stanza |
| **Fine della stanza** | Uscendo da una stanza |
| **Vite esaurite** | Le vite raggiungono 0 |
| **Salute esaurita** | La salute raggiunge 0 |
| **Fine dell'animazione** | L'animazione dello sprite è completata |

### Eventi Draw

| Evento | Quando |
|-----------|-------|
| **Disegno** | Durante la fase di rendering |
| **Disegno dell'interfaccia** | Dopo aver disegnato la stanza (spazio schermo) |

---

## Riferimento Azioni

### Azioni di Movimento

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Imposta velocità** | Imposta la velocità di movimento | velocità, relativo |
| **Imposta direzione** | Imposta la direzione | direzione (0-360), relativo |
| **Imposta velocità orizzontale** | Imposta hspeed | hspeed, relativo |
| **Imposta velocità verticale** | Imposta vspeed | vspeed, relativo |
| **Imposta gravità** | Imposta la gravità | gravity, direction |
| **Imposta attrito** | Imposta l'attrito | friction |
| **Muovi verso un punto** | Muovi verso coordinate | x, y, velocità |
| **Inizia a muoverti (direzione)** | Muoviti in una direzione | direction, velocità |
| **Salta alla posizione** | Teletrasporta a coordinate | x, y, relativo |
| **Salta alla posizione iniziale** | Torna alla posizione di creazione | - |
| **Salta a posizione casuale** | Teletrasporto a una posizione completamente casuale (entrambi gli assi; allineabile alla griglia) | snap_h, snap_v |
| **Rimbalza** | Rimbalza dagli oggetti solidi | precise |

### Azioni di Istanza

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Crea istanza** | Crea un nuovo oggetto | object, x, y, relativo |
| **Crea istanza in movimento** | Crea con velocità | object, x, y, speed, direction |
| **Distruggi istanza** | Rimuove l'istanza | - |
| **Cambia istanza** | Trasforma in un altro oggetto | object, perform_events |

### Azioni di Temporizzazione

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Imposta allarme** | Avvia un conto alla rovescia | alarm_number, steps |
| **Pausa** | Pausa l'esecuzione | millisecondi |

### Azioni Score/Vite/Salute

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Imposta punteggio** | Cambia il punteggio | value, relativo |
| **Imposta vite** | Cambia le vite | value, relativo |
| **Imposta salute** | Cambia la salute | value, relativo |
| **Disegna punteggio** | Mostra il punteggio | x, y, caption |
| **Disegna vite** | Mostra le vite come immagini di sprite ripetute | x, y, sprite, scale, tiled |
| **Disegna barra della salute** | Mostra la salute come barra a due colori | x1, y1, x2, y2, back_color, bar_color |

### Azioni di Disegno

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Disegna sprite** | Disegna uno sprite | sprite, x, y, subimage |
| **Disegna testo** | Mostra testo | x, y, text |
| **Disegna rettangolo** | Disegna un rettangolo | x1, y1, x2, y2, filled |
| **Disegna cerchio** | Disegna un cerchio | x, y, radius, filled |
| **Disegna linea** | Disegna una linea | x1, y1, x2, y2 |
| **Imposta colore di disegno** | Imposta il colore per i successivi Draw Text/Draw Rectangle/ecc. | color |
| **Imposta colore** | Imposta la tinta e la trasparenza di uno sprite (non il colore di disegno sopra) | color, alpha |
| **Imposta font di disegno** | Imposta font e allineamento per il prossimo disegno di testo | font, halign, valign |

### Azioni di Stanza

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Stanza successiva** | Vai alla stanza successiva | transition |
| **Stanza precedente** | Vai alla stanza precedente | transition |
| **Riavvia stanza** | Ripristina la stanza | - |
| **Vai alla stanza** | Salta a una stanza specifica | room, transition |
| **Se esiste stanza successiva** | Verifica se esiste una stanza successiva | - |
| **Se esiste stanza precedente** | Verifica se esiste una stanza precedente | - |

### Azioni Sound

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Riproduci suono** | Riproduci un effetto sonoro | sound, loop |
| **Ferma suono** | Ferma un suono | sound |
| **Verifica riproduzione suono** | Verifica se un suono è in riproduzione | sound |
| **Riproduci musica** | Riproduci musica di sottofondo | music, loop |
| **Ferma musica** | Ferma tutta la musica | - |

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
| **Inizio blocco** | Inizia un gruppo di azioni | - |
| **Fine blocco** | Termina un gruppo di azioni | - |
| **Ripeti** | Ripeti N volte | count |
| **Esci dall'evento** | Ferma l'evento attuale | - |

### Altre Azioni

| Azione | Descrizione | Parametri |
|--------|-------------|------------|
| **Mostra messaggio** | Mostra un messaggio popup | message |
| **Riavvia gioco** | Riavvia il gioco | - |
| **Termina gioco** | Chiude il gioco | - |

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
