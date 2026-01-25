# Tutorial: Creare un Gioco del Labirinto

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Maze) | [Français](Tutorial-Maze_fr) | [Deutsch](Tutorial-Maze_de) | [Italiano](Tutorial-Maze_it) | [Español](Tutorial-Maze_es) | [Português](Tutorial-Maze_pt) | [Slovenščina](Tutorial-Maze_sl) | [Українська](Tutorial-Maze_uk) | [Русский](Tutorial-Maze_ru)

---

## Introduzione

In questo tutorial, creerai un **Gioco del Labirinto** dove il giocatore naviga attraverso i corridoi per raggiungere l'uscita evitando ostacoli e raccogliendo monete. Questo tipo di gioco classico è perfetto per imparare il movimento fluido, il rilevamento delle collisioni e il design dei livelli.

**Cosa imparerai:**
- Movimento fluido del giocatore con input da tastiera
- Gestione delle collisioni con i muri
- Rilevamento dell'obiettivo (raggiungere l'uscita)
- Oggetti collezionabili
- Sistema di timer semplice

**Difficoltà:** Principiante
**Preset:** Preset Principiante

---

## Passo 1: Capire il Gioco

### Regole del Gioco
1. Il giocatore si muove attraverso un labirinto usando i tasti freccia
2. I muri bloccano il movimento del giocatore
3. Raccogli monete per punti
4. Raggiungi l'uscita per completare il livello
5. Completa il labirinto il più velocemente possibile!

### Cosa Ci Serve

| Elemento | Scopo |
|----------|-------|
| **Giocatore** | Il personaggio che controlli |
| **Muro** | Ostacoli solidi che bloccano il movimento |
| **Uscita** | Obiettivo che termina il livello |
| **Moneta** | Oggetti collezionabili per il punteggio |
| **Pavimento** | Sfondo visivo (opzionale) |

---

## Passo 2: Creare gli Sprite

Tutti gli sprite di muri e pavimenti devono essere 32x32 pixel per creare una griglia corretta.

### 2.1 Sprite del Giocatore

1. Nell'**Albero delle Risorse**, clicca con il tasto destro su **Sprite** e seleziona **Crea Sprite**
2. Nominalo `spr_player`
3. Clicca su **Modifica Sprite** per aprire l'editor
4. Disegna un piccolo personaggio (cerchio, persona o forma a freccia)
5. Usa un colore vivace come blu o verde
6. Dimensione: 24x24 pixel (più piccolo dei muri per una navigazione più facile)
7. Clicca su **OK** per salvare

### 2.2 Sprite del Muro

1. Crea un nuovo sprite chiamato `spr_wall`
2. Disegna un pattern solido di mattoni o pietra
3. Usa colori grigi o scuri
4. Dimensione: 32x32 pixel

### 2.3 Sprite dell'Uscita

1. Crea un nuovo sprite chiamato `spr_exit`
2. Disegna una porta, bandiera o marcatore di obiettivo luminoso
3. Usa colori verdi o dorati
4. Dimensione: 32x32 pixel

### 2.4 Sprite della Moneta

1. Crea un nuovo sprite chiamato `spr_coin`
2. Disegna un piccolo cerchio giallo/dorato
3. Dimensione: 16x16 pixel

### 2.5 Sprite del Pavimento (Opzionale)

1. Crea un nuovo sprite chiamato `spr_floor`
2. Disegna un semplice pattern di piastrelle
3. Usa un colore neutro chiaro
4. Dimensione: 32x32 pixel

---

## Passo 3: Creare l'Oggetto Muro

Il muro blocca il movimento del giocatore.

1. Clicca con il tasto destro su **Oggetti** e seleziona **Crea Oggetto**
2. Nominalo `obj_wall`
3. Imposta lo sprite su `spr_wall`
4. **Spunta la casella "Solido"**
5. Non servono eventi

---

## Passo 4: Creare l'Oggetto Uscita

L'uscita termina il livello quando il giocatore la raggiunge.

1. Crea un nuovo oggetto chiamato `obj_exit`
2. Imposta lo sprite su `spr_exit`

**Evento: Collisione con obj_player**
1. Aggiungi Evento → Collisione → obj_player
2. Aggiungi Azione: **Main2** → **Mostra Messaggio**
   - Messaggio: `Hai vinto! Tempo: ` + string(floor(global.timer)) + ` secondi`
3. Aggiungi Azione: **Main1** → **Prossima Room** (o **Riavvia Room** per un singolo livello)

---

## Passo 5: Creare l'Oggetto Moneta

Le monete aggiungono al punteggio quando vengono raccolte.

1. Crea un nuovo oggetto chiamato `obj_coin`
2. Imposta lo sprite su `spr_coin`

**Evento: Collisione con obj_player**
1. Aggiungi Evento → Collisione → obj_player
2. Aggiungi Azione: **Score** → **Imposta Score**
   - Nuovo Score: `10`
   - Spunta "Relativo" per aggiungere 10 punti
3. Aggiungi Azione: **Main1** → **Distruggi Istanza**
   - Si applica a: Self

---

## Passo 6: Creare l'Oggetto Giocatore

Il giocatore si muove fluidamente usando i tasti freccia.

1. Crea un nuovo oggetto chiamato `obj_player`
2. Imposta lo sprite su `spr_player`

### 6.1 Evento Create - Inizializzare Variabili

**Evento: Create**
1. Aggiungi Evento → Create
2. Aggiungi Azione: **Controllo** → **Imposta Variabile**
   - Variabile: `move_speed`
   - Valore: `4`

### 6.2 Movimento con Collisione

**Evento: Step**
1. Aggiungi Evento → Step → Step
2. Aggiungi Azione: **Controllo** → **Esegui Codice**

```gml
// Movimento orizzontale
var hspd = 0;
if (keyboard_check(vk_right)) hspd = move_speed;
if (keyboard_check(vk_left)) hspd = -move_speed;

// Movimento verticale
var vspd = 0;
if (keyboard_check(vk_down)) vspd = move_speed;
if (keyboard_check(vk_up)) vspd = -move_speed;

// Controllo collisione orizzontale
if (!place_meeting(x + hspd, y, obj_wall)) {
    x += hspd;
} else {
    // Muoviti il più vicino possibile al muro
    while (!place_meeting(x + sign(hspd), y, obj_wall)) {
        x += sign(hspd);
    }
}

// Controllo collisione verticale
if (!place_meeting(x, y + vspd, obj_wall)) {
    y += vspd;
} else {
    // Muoviti il più vicino possibile al muro
    while (!place_meeting(x, y + sign(vspd), obj_wall)) {
        y += sign(vspd);
    }
}
```

### 6.3 Alternativa: Movimento Semplice a Blocchi

Se preferisci usare blocchi di azione invece del codice:

**Evento: Tasto Premuto - Freccia Destra**
1. Aggiungi Evento → Tastiera → \<Destra\>
2. Aggiungi Azione: **Controllo** → **Testa Collisione**
   - Oggetto: `obj_wall`
   - X: `4`
   - Y: `0`
   - Controlla: NOT
3. Aggiungi Azione: **Movimento** → **Salta a Posizione**
   - X: `4`
   - Y: `0`
   - Spunta "Relativo"

Ripeti per Sinistra (-4, 0), Su (0, -4) e Giù (0, 4).

---

## Passo 7: Creare il Controller del Gioco

Il controller del gioco gestisce il timer e visualizza le informazioni.

1. Crea un nuovo oggetto chiamato `obj_game_controller`
2. Non serve sprite

**Evento: Create**
1. Aggiungi Evento → Create
2. Aggiungi Azione: **Controllo** → **Imposta Variabile**
   - Variabile: `global.timer`
   - Valore: `0`

**Evento: Step**
1. Aggiungi Evento → Step → Step
2. Aggiungi Azione: **Controllo** → **Imposta Variabile**
   - Variabile: `global.timer`
   - Valore: `1/room_speed`
   - Spunta "Relativo"

**Evento: Draw**
1. Aggiungi Evento → Draw → Draw
2. Aggiungi Azione: **Controllo** → **Esegui Codice**

```gml
// Disegna punteggio
draw_set_color(c_white);
draw_text(10, 10, "Punti: " + string(score));

// Disegna timer
draw_text(10, 30, "Tempo: " + string(floor(global.timer)) + "s");

// Disegna monete rimanenti
var coins_left = instance_number(obj_coin);
draw_text(10, 50, "Monete: " + string(coins_left));
```

---

## Passo 8: Progetta il Tuo Labirinto

1. Clicca con il tasto destro su **Room** e seleziona **Crea Room**
2. Nominala `room_maze`
3. Imposta la dimensione della room (es: 640x480)
4. Abilita "Aggancia alla Griglia" e imposta la griglia su 32x32

### Posizionamento degli Oggetti

Costruisci il tuo labirinto seguendo queste linee guida:

1. **Crea il bordo** - Circonda la room con muri
2. **Costruisci corridoi** - Crea percorsi attraverso il labirinto
3. **Posiziona l'uscita** - Mettila alla fine del labirinto
4. **Spargi le monete** - Posizionale lungo i percorsi
5. **Posiziona il giocatore** - Vicino all'ingresso
6. **Aggiungi il controller del gioco** - Ovunque (è invisibile)

### Esempio di Layout del Labirinto

```
W W W W W W W W W W W W W W W W W W W W
W P . . . . W . . . . . . . W . . . . W
W . W W W . W . W W W W W . W . W W . W
W . W . . . . . . . . . . . . . . W . W
W . W . W W W W W . W W W W W W . W . W
W . . . W . . . . . . . . C . W . . . W
W W W . W . W W W W W W W . . W W W . W
W C . . . . W . . . . . W . . . . . . W
W . W W W W W . W W W . W W W W W W . W
W . . . . . . . . C . . . . . . . . . W
W . W W W W W W W W W . W W W W W W . W
W . . . . . . . . . . . W . . . . . . W
W W W W W W W W W W W . W . W W W W . W
W . . . . . . . . . . . . . W . C . E W
W W W W W W W W W W W W W W W W W W W W

W = Muro    P = Giocatore    E = Uscita    C = Moneta    . = Vuoto
```

---

## Passo 9: Testa il Tuo Gioco!

1. Clicca su **Esegui** o premi **F5** per testare
2. Usa i tasti freccia per navigare nel labirinto
3. Raccogli monete per punti
4. Trova l'uscita per vincere!

---

## Miglioramenti (Opzionale)

### Aggiungere Nemici

Crea un semplice nemico che pattuglia:

1. Crea `spr_enemy` (colore rosso, 24x24)
2. Crea `obj_enemy` con sprite `spr_enemy`

**Evento: Create**
```gml
hspeed = 2;  // Si muove orizzontalmente
```

**Evento: Collisione con obj_wall**
```gml
hspeed = -hspeed;  // Inverti direzione
```

**Evento: Collisione con obj_player**
```gml
room_restart();  // Il giocatore perde
```

### Aggiungere Sistema di Vite

Nell'evento Create di `obj_game_controller`:
```gml
global.lives = 3;
```

Quando il giocatore tocca un nemico (invece di riavviare):
```gml
global.lives -= 1;
if (global.lives <= 0) {
    show_message("Game Over!");
    game_restart();
} else {
    // Fai riapparire il giocatore all'inizio
    obj_player.x = start_x;
    obj_player.y = start_y;
}
```

### Aggiungere Chiavi e Porte Chiuse

1. Crea `obj_key` - scompare quando raccolta, imposta `global.has_key = true`
2. Crea `obj_locked_door` - si apre solo quando `global.has_key == true`

### Aggiungere Livelli Multipli

1. Crea room aggiuntive (`room_maze2`, `room_maze3`)
2. In `obj_exit`, usa `room_goto_next()` invece di `room_restart()`

### Aggiungere Effetti Sonori

Aggiungi suoni per:
- Raccogliere monete
- Raggiungere l'uscita
- Toccare nemici (se aggiunti)
- Musica di sottofondo

---

## Risoluzione dei Problemi

| Problema | Soluzione |
|----------|-----------|
| Il giocatore passa attraverso i muri | Controlla che `obj_wall` abbia "Solido" spuntato |
| Il giocatore rimane bloccato nei muri | Assicurati che lo sprite del giocatore sia più piccolo degli spazi tra i muri |
| Le monete non scompaiono | Verifica che l'evento di collisione distrugga Self, non Other |
| Il timer non funziona | Assicurati che il controller del gioco sia posizionato nella room |
| Il movimento sembra scattoso | Regola il valore di `move_speed` (prova 3-5) |

---

## Cosa Hai Imparato

Congratulazioni! Hai creato un gioco del labirinto! Hai imparato:

- **Movimento fluido** - Controllare lo stato dei tasti premuti per movimento continuo
- **Rilevamento collisioni** - Usare `place_meeting` per controllare prima di muoversi
- **Collisione pixel-perfect** - Muoversi il più vicino possibile ai muri
- **Collezionabili** - Creare oggetti che aumentano il punteggio e scompaiono
- **Sistema di timer** - Tracciare il tempo trascorso con variabili
- **Design dei livelli** - Creare layout di labirinti navigabili

---

## Idee per Sfide

1. **Corsa contro il Tempo** - Aggiungi un timer a conto alla rovescia. Raggiungi l'uscita prima che scada il tempo!
2. **Punteggio Perfetto** - Richiedi di raccogliere tutte le monete prima che l'uscita si apra
3. **Labirinto Casuale** - Ricerca la generazione procedurale di labirinti
4. **Nebbia di Guerra** - Mostra solo l'area intorno al giocatore
5. **Minimappa** - Mostra una piccola panoramica del labirinto

---

## Vedi Anche

- [Tutorial](Tutorials_it) - Altri tutorial di giochi
- [Preset Principiante](Beginner-Preset_it) - Panoramica delle funzionalità per principianti
- [Tutorial: Pong](Tutorial-Pong_it) - Creare un gioco a due giocatori
- [Tutorial: Breakout](Tutorial-Breakout_it) - Creare un gioco spacca-mattoni
- [Tutorial: Sokoban](Tutorial-Sokoban_it) - Creare un puzzle spingi-scatole
- [Riferimento Eventi](Event-Reference_it) - Documentazione completa degli eventi
