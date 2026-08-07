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
**Preset:** Preset Intermedio (l'azione Execute Code usata per il timer
non è inclusa nel preset Principiante)

---

## Passo 1: Capire il Gioco

### Regole del Gioco
1. Il giocatore si muove attraverso un labirinto usando i tasti freccia
2. I muri bloccano il movimento del giocatore
3. Raccogli monete per punti
4. Raggiungi l'uscita per completare il livello
5. Completa il labirinto il più velocemente possibile!

### Quello che ci serve

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

1. Nell'**Albero delle Risorse**, fai clic destro su **Sprites** e seleziona **Create Sprite**
2. Nominalo `spr_player`
3. Fai clic su **Edit Sprite** per aprire l'editor
4. Disegna un piccolo personaggio (cerchio, persona o forma a freccia)
5. Usa un colore vivace come blu o verde
6. Dimensione: 24x24 pixel (più piccolo dei muri per una navigazione più facile)
7. Fai clic su **OK** per salvare

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

1. Fai clic destro su **Objects** e seleziona **Create Object**
2. Nominalo `obj_wall`
3. Imposta lo sprite su `spr_wall`
4. **Seleziona la casella "Solid"**
5. Non servono eventi

---

## Passo 4: Creare l'Oggetto Uscita

L'uscita termina il livello quando il giocatore la raggiunge.

1. Crea un nuovo oggetto chiamato `obj_exit`
2. Imposta lo sprite su `spr_exit`

**Event: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Output** → **Show Message**
   - Message: `You Win!`
3. Add Action: **Room** → **Next Room** (o **Restart Room** per un singolo livello)

Il testo di Show Message è una stringa statica fissa — non può includere un
valore dinamico come il tempo trascorso. Il timer resta visibile nell'HUD
(Passo 7) fino alla vittoria, quindi il giocatore ha già visto il proprio
tempo.

---

## Passo 5: Creare l'Oggetto Moneta

Le monete aggiungono al punteggio quando vengono raccolte.

1. Crea un nuovo oggetto chiamato `obj_coin`
2. Imposta lo sprite su `spr_coin`

**Event: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Score** → **Set Score**
   - New Score: `10`
   - Seleziona "Relative" per aggiungere 10 punti
3. Add Action: **Instance** → **Destroy Instance**
   - Applies to: Self

---

## Passo 6: Creare l'Oggetto Giocatore

Il giocatore si muove fluidamente usando i tasti freccia.

1. Crea un nuovo oggetto chiamato `obj_player`
2. Imposta lo sprite su `spr_player`

### 6.1 Movimento

Aggiungi quattro eventi **Keyboard (held)** più un evento **No Key**,
ciascuno con un'azione **Move** → **Set Horizontal/Vertical Speed**:

| Evento | Azione |
|---|---|
| Keyboard (held) → Right Arrow | Set Horizontal Speed a `4` |
| Keyboard (held) → Left Arrow | Set Horizontal Speed a `-4` |
| Keyboard (held) → Down Arrow | Set Vertical Speed a `4` |
| Keyboard (held) → Up Arrow | Set Vertical Speed a `-4` |
| Keyboard: No Key | Set Horizontal Speed a `0` **e** Set Vertical Speed a `0` |

### 6.2 Fermarsi ai muri

**Event: Collision with obj_wall**
1. Add Event → Collision → `obj_wall`
2. Add Action: **Move** → **Stop Movement**

Qui non serve alcun codice manuale per controllare la posizione. Il ciclo
di movimento di questo motore già impedisce che un'istanza venga spostata
dentro un oggetto solido prima che il frame venga disegnato (`obj_wall` è
Solid), quindi il giocatore non può mai realmente sovrapporsi a un muro —
l'evento di collisione sopra si limita ad azzerare qualsiasi velocità
residua, così il giocatore non continua a "spingere" contro di esso.

---

## Passo 7: Creare il Game Controller

Il game controller gestisce il timer e visualizza le informazioni.

1. Crea un nuovo oggetto chiamato `obj_game_controller`
2. Non serve uno sprite

**Event: Create** — avvia il timer, usando **Control** → **Execute Code**
(l'azione Execute Code di questo progetto esegue vero Python, non
GameMaker Language):

```python
self.timer = 0.0
```

**Event: Step** — lo incrementa ad ogni frame:

```python
self.timer += 1.0 / game.fps
```

**Event: Draw** — costruisce l'HUD con veri comandi della coda di
disegno. Aggiungi tre azioni **Draw** → **Draw Text**:

| Azione Draw Text | Testo | Posizione |
|---|---|---|
| 1ª | `Score:` | X `10`, Y `10` |
| 2ª | `Time:` | X `10`, Y `30` |
| 3ª | `Coins:` | X `10`, Y `50` |

poi tre azioni **Draw** → **Draw Variable** subito dopo, per mostrare i
valori dinamici accanto a ogni etichetta:

| Azione Draw Variable | Variabile | Posizione |
|---|---|---|
| 1ª | `score` | X `70`, Y `10` |
| 2ª | `self.timer` | X `70`, Y `30` |
| 3ª | *(vedi sotto)* | X `70`, Y `50` |

Non esiste un contatore integrato "monete rimanenti" a cui puntare Draw
Variable — aggiungi un'altra azione **Control** → **Execute Code**, subito
prima delle azioni Draw Variable, per calcolarlo in una variabile
d'istanza che Draw Variable può poi leggere:

```python
self.coins_left = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_coin'
)
```

(poi imposta il campo Variable della 3ª azione Draw Variable su `self.coins_left`).

---

## Passo 8: Progetta il Tuo Labirinto

1. Fai clic destro su **Rooms** e seleziona **Create Room**
2. Nominalo `room_maze`
3. Imposta la dimensione della stanza (es: 640x480)
4. Abilita "Snap to Grid" e imposta la griglia su 32x32

### Posizionamento degli Oggetti

Costruisci il tuo labirinto seguendo queste linee guida:

1. **Crea il bordo** - Circonda la stanza con muri
2. **Costruisci corridoi** - Crea percorsi attraverso il labirinto
3. **Posiziona l'uscita** - Mettila alla fine del labirinto
4. **Spargi le monete** - Posizionale lungo i percorsi
5. **Posiziona il giocatore** - Vicino all'ingresso
6. **Aggiungi il game controller** - Ovunque (è invisibile)

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

1. Fai clic su **Run** o premi **F5** per testare
2. Usa i tasti freccia per navigare nel labirinto
3. Raccogli monete per punti
4. Trova l'uscita per vincere!

---

## Miglioramenti (Opzionale)

### Aggiungere Nemici

Crea un semplice nemico che pattuglia:

1. Crea `spr_enemy` (colore rosso, 24x24)
2. Crea `obj_enemy` con sprite `spr_enemy`

**Event: Create** — Add Action: **Move** → **Start Moving Direction**
(Directions: `right`, Speed: `2`)

**Event: Collision with obj_wall** — Add Action: **Move** → **Reverse
Horizontal** (fa girare il nemico quando colpisce un muro — nessun codice
necessario; combinato con la collisione solida integrata del Passo 6.2,
il nemico non può mai attraversare un muro)

**Event: Collision with obj_player** — Add Action: **Room** → **Restart
Room**

### Aggiungere Sistema di Vite

Nell'evento **Create** di `obj_game_controller`, aggiungi **Score** →
**Set Lives** (Value: `3`).

Nell'evento **Collision with obj_player** di `obj_enemy`, sostituisci
**Restart Room** con due azioni: **Score** → **Set Lives** (Value: `-1`,
**Relative** selezionato), poi **Move** → **Jump to Start Position**
(applicata al giocatore tramite **Applies to: Other**) per far riapparire
il giocatore invece di riavviare l'intero labirinto.

Aggiungi un altro evento a `obj_game_controller`: **Other Events** →
**No More Lives** — questo si attiva automaticamente non appena le vite
raggiungono 0, quindi non serve controllarlo manualmente. Aggiungi
**Output** → **Show Message** (`Game Over!`) seguito da **Room** →
**Restart Game**.

### Aggiungere Chiavi e Porte Chiuse

1. Crea `obj_key` — alla collisione con `obj_player`, **Set Variable**
   (Variable: `global.has_key`, Value: `true`, Scope: `global`), poi
   **Destroy Instance** (self).
2. Crea `obj_locked_door`, con Solid selezionato. Dagli un evento
   **Step** con **Control** → **Test Variable** (Variable:
   `global.has_key`, Value: `true`, Scope: `global`) → **Instance** →
   **Destroy Instance** (self) — la porta scompare (e smette di
   bloccare) non appena la chiave viene raccolta.

### Aggiungere Livelli Multipli

1. Crea stanze aggiuntive (`room_maze2`, `room_maze3`)
2. In `obj_exit`, usa l'azione **Next Room** invece di **Restart Room**

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
| Il giocatore passa attraverso i muri | Controlla che `obj_wall` abbia "Solid" selezionato |
| Il giocatore rimane bloccato nei muri | Assicurati che lo sprite del giocatore sia più piccolo degli spazi tra i muri |
| Le monete non scompaiono | Verifica che l'evento di collisione distrugga Self, non Other |
| Il timer non funziona | Assicurati che il game controller sia posizionato nella stanza |
| Il movimento sembra scattoso | Regola il valore di velocità nelle azioni Set Horizontal/Vertical Speed (prova 3-5) |

---

## Cosa Hai Imparato

Congratulazioni! Hai creato un gioco del labirinto! Hai imparato:

- **Movimento fluido** - Controllare lo stato dei tasti tenuti premuti per il movimento continuo
- **Collisione solida integrata** - I muri bloccano il movimento automaticamente una volta marcati Solid, senza codice manuale di controllo posizione
- **Collezionabili** - Creare oggetti che aumentano il punteggio e scompaiono
- **Sistema di timer** - Tracciare il tempo trascorso con variabili d'istanza
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

- [Tutorials](Tutorials_it) - Altri tutorial di giochi
- [Intermediate Preset](Intermediate-Preset_it) - Panoramica del preset necessario per questo tutorial
- [Tutorial: Pong](Tutorial-Pong_it) - Creare un gioco a due giocatori
- [Tutorial: Breakout](Tutorial-Breakout_it) - Creare un gioco spacca-mattoni
- [Tutorial: Sokoban](Tutorial-Sokoban_it) - Creare un puzzle spingi-scatole
- [Event Reference](Event-Reference_it) - Documentazione completa degli eventi
