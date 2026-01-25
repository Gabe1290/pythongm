# Tutorial: Creare un gioco di puzzle Sokoban

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Sokoban) | [Français](Tutorial-Sokoban_fr) | [Deutsch](Tutorial-Sokoban_de) | [Italiano](Tutorial-Sokoban_it) | [Español](Tutorial-Sokoban_es) | [Português](Tutorial-Sokoban_pt) | [Slovenščina](Tutorial-Sokoban_sl) | [Українська](Tutorial-Sokoban_uk) | [Русский](Tutorial-Sokoban_ru)

---

## Introduzione

In questo tutorial, creerai un gioco di puzzle **Sokoban** - un classico rompicapo di spinta di scatole dove il giocatore deve spingere tutte le casse nelle posizioni bersaglio. Sokoban (che significa "responsabile del magazzino" in giapponese) è perfetto per imparare il movimento su griglia e la logica dei giochi di puzzle.

**Quello che imparerai:**
- Movimento basato su griglia (movimento in passi fissi)
- Meccanica di spinta per spostare oggetti
- Rilevamento delle collisioni con più tipi di oggetti
- Rilevamento della condizione di vittoria
- Progettazione di livelli per giochi di puzzle

**Difficoltà:** Principiante
**Preset:** Beginner Preset

---

## Step 1: Comprendi il gioco

### Regole del gioco
1. Il giocatore può muoversi verso l'alto, il basso, sinistra o destra
2. Il giocatore può spingere le casse (ma non tirarle)
3. Solo una cassa può essere spinta alla volta
4. Le casse non possono essere spinte attraverso muri o altre casse
5. Il livello è completato quando tutte le casse si trovano nei punti bersaglio

### Quello che abbiamo bisogno

| Elemento | Scopo |
|---------|---------|
| **Giocatore** | Il responsabile del magazzino che controlli |
| **Cassa** | Scatole che il giocatore spinge |
| **Muro** | Ostacoli solidi che bloccano il movimento |
| **Bersaglio** | Punti obiettivo dove le casse devono essere posizionate |
| **Pavimento** | Terreno calpestabile (visuale opzionale) |

---

## Step 2: Crea gli sprite

Tutti gli sprite devono avere la stessa dimensione (32x32 pixel funziona bene) per creare una griglia corretta.

### 2.1 Sprite del giocatore

1. Nell'**Albero delle risorse**, fai clic destro su **Sprite** e seleziona **Crea sprite**
2. Nominalo `spr_player`
3. Fai clic su **Modifica sprite** per aprire l'editor degli sprite
4. Disegna un personaggio semplice (forma di una persona o di un robot)
5. Usa un colore distinto come blu o verde
6. Dimensione: 32x32 pixel
7. Fai clic su **OK** per salvare

### 2.2 Sprite della cassa

1. Crea un nuovo sprite denominato `spr_crate`
2. Disegna una forma di cassa in legno o di scatola
3. Usa colori marrone o arancione
4. Dimensione: 32x32 pixel

### 2.3 Sprite della cassa sul bersaglio

1. Crea un nuovo sprite denominato `spr_crate_ok`
2. Disegna la stessa cassa ma con un colore diverso (verde) per mostrare che è posizionata correttamente
3. Dimensione: 32x32 pixel

### 2.4 Sprite del muro

1. Crea un nuovo sprite denominato `spr_wall`
2. Disegna un motivo di mattone solido o pietra
3. Usa colori grigi o scuri
4. Dimensione: 32x32 pixel

### 2.5 Sprite bersaglio

1. Crea un nuovo sprite denominato `spr_target`
2. Disegna un'X o un indicatore di obiettivo
3. Usa un colore luminoso come rosso o giallo
4. Dimensione: 32x32 pixel

### 2.6 Sprite del pavimento (opzionale)

1. Crea un nuovo sprite denominato `spr_floor`
2. Disegna un semplice motivo di piastrelle del pavimento
3. Usa un colore neutro
4. Dimensione: 32x32 pixel

---

## Step 3: Crea l'oggetto muro

Il muro è l'oggetto più semplice - blocca semplicemente il movimento.

1. Fai clic destro su **Oggetti** e seleziona **Crea oggetto**
2. Nominalo `obj_wall`
3. Imposta lo sprite su `spr_wall`
4. **Seleziona la casella "Solido"**
5. Non sono necessari eventi

---

## Step 4: Crea l'oggetto bersaglio

I bersagli indicano dove devono essere posizionate le casse.

1. Crea un nuovo oggetto denominato `obj_target`
2. Imposta lo sprite su `spr_target`
3. Non sono necessari eventi - è solo un marcatore
4. Lascia "Solido" deselezionato (il giocatore e le casse possono stare sopra)

---

## Step 5: Crea l'oggetto cassa

La cassa viene spinta dal giocatore e cambia aspetto quando si trova su un bersaglio.

1. Crea un nuovo oggetto denominato `obj_crate`
2. Imposta lo sprite su `spr_crate`
3. **Seleziona la casella "Solido"**

**Event: Step**
1. Aggiungi evento → Step → Step
2. Aggiungi azione: **Control** → **Test Variable**
   - Variabile: `place_meeting(x, y, obj_target)`
   - Valore: `1`
   - Operazione: Uguale a
3. Aggiungi azione: **Main1** → **Change Sprite**
   - Sprite: `spr_crate_ok`
   - Subimage: `0`
   - Speed: `1`
4. Aggiungi azione: **Control** → **Else**
5. Aggiungi azione: **Main1** → **Change Sprite**
   - Sprite: `spr_crate`
   - Subimage: `0`
   - Speed: `1`

Ciò fa sì che la cassa diventi verde quando si trova su un punto bersaglio.

---

## Step 6: Crea l'oggetto giocatore

L'oggetto giocatore è il più complesso con movimento basato su griglia e meccanica di spinta.

1. Crea un nuovo oggetto denominato `obj_player`
2. Imposta lo sprite su `spr_player`

### 6.1 Spostamento a destra

**Event: Keyboard Press Right Arrow**
1. Aggiungi evento → Keyboard → Press Right

Per prima cosa, controlla se c'è un muro nel modo:
2. Aggiungi azione: **Control** → **Test Collision**
   - Oggetto: `obj_wall`
   - X: `32`
   - Y: `0`
   - Controllo: NOT (il che significa "se NON c'è un muro")

Se non c'è un muro, controlla se c'è una cassa:
3. Aggiungi azione: **Control** → **Test Collision**
   - Oggetto: `obj_crate`
   - X: `32`
   - Y: `0`

Se c'è una cassa, abbiamo bisogno di controllare se possiamo spingere:
4. Aggiungi azione: **Control** → **Test Collision** (per la destinazione della cassa)
   - Oggetto: `obj_wall`
   - X: `64`
   - Y: `0`
   - Controllo: NOT

5. Aggiungi azione: **Control** → **Test Collision**
   - Oggetto: `obj_crate`
   - X: `64`
   - Y: `0`
   - Controllo: NOT

Se entrambi i controlli passano, spingi la cassa:
6. Aggiungi azione: **Control** → **Code Block**
```
var crate = instance_place(x + 32, y, obj_crate);
if (crate != noone) {
    crate.x += 32;
}
```

Ora sposta il giocatore:
7. Aggiungi azione: **Move** → **Jump to Position**
   - X: `32`
   - Y: `0`
   - Seleziona "Relative"

### 6.2 Spostamento a sinistra

**Event: Keyboard Press Left Arrow**
Segui lo stesso modello dello spostamento a destra, ma usa:
- Offset X: `-32` per il controllo muro/cassa
- Offset X: `-64` per il controllo se la cassa può essere spinta
- Muovi la cassa di `-32`
- Salta alla posizione X: `-32`

### 6.3 Spostamento verso l'alto

**Event: Keyboard Press Up Arrow**
Segui lo stesso modello, ma usa i valori Y:
- Offset Y: `-32` per il controllo
- Offset Y: `-64` per la destinazione della cassa
- Muovi la cassa di Y: `-32`
- Salta alla posizione Y: `-32`

### 6.4 Spostamento verso il basso

**Event: Keyboard Press Down Arrow**
Usa:
- Offset Y: `32` per il controllo
- Offset Y: `64` per la destinazione della cassa
- Muovi la cassa di Y: `32`
- Salta alla posizione Y: `32`

---

## Step 7: Movimento del giocatore semplificato (alternativa)

Se l'approccio basato su blocchi qui sopra sembra complesso, ecco un approccio più semplice basato su codice per ogni direzione:

**Event: Keyboard Press Right Arrow**
Aggiungi azione: **Control** → **Execute Code**
```
// Check if we can move right
if (!place_meeting(x + 32, y, obj_wall)) {
    // Check if there's a crate
    var crate = instance_place(x + 32, y, obj_crate);
    if (crate != noone) {
        // There's a crate - can we push it?
        if (!place_meeting(x + 64, y, obj_wall) && !place_meeting(x + 64, y, obj_crate)) {
            crate.x += 32;
            x += 32;
        }
    } else {
        // No crate, just move
        x += 32;
    }
}
```

Ripeti per le altre direzioni con i relativi cambiamenti di coordinate.

---

## Step 8: Crea il controllore della condizione di vittoria

Abbiamo bisogno di un oggetto per controllare se tutte le casse si trovano sui bersagli.

1. Crea un nuovo oggetto denominato `obj_game_controller`
2. Non è necessario uno sprite

**Event: Create**
1. Aggiungi evento → Create
2. Aggiungi azione: **Score** → **Set Variable**
   - Variabile: `global.total_targets`
   - Valore: `0`
3. Aggiungi azione: **Control** → **Execute Code**
```
// Count how many targets exist
global.total_targets = instance_number(obj_target);
```

**Event: Step**
1. Aggiungi evento → Step → Step
2. Aggiungi azione: **Control** → **Execute Code**
```
// Count crates that are on targets
var crates_on_targets = 0;
with (obj_crate) {
    if (place_meeting(x, y, obj_target)) {
        crates_on_targets += 1;
    }
}

// Check if all targets have crates
if (crates_on_targets >= global.total_targets && global.total_targets > 0) {
    // Level complete!
    show_message("Level Complete!");
    room_restart();
}
```

**Event: Draw**
1. Aggiungi evento → Draw
2. Aggiungi azione: **Draw** → **Draw Text**
   - Testo: `Sokoban - Push all crates to targets!`
   - X: `10`
   - Y: `10`

---

## Step 9: Progetta il tuo livello

1. Fai clic destro su **Stanze** e seleziona **Crea stanza**
2. Nominalo `room_level1`
3. Imposta la dimensione della stanza su un multiplo di 32 (ad es. 640x480)
4. Abilita "Aggancia alla griglia" e imposta la griglia su 32x32

### Posizionamento di oggetti

Costruisci il tuo livello seguendo queste linee guida:

1. **Circonda il livello con muri** - Crea un bordo
2. **Aggiungi muri interni** - Crea la struttura del puzzle
3. **Posiziona i bersagli** - Dove le casse devono andare
4. **Posiziona le casse** - Lo stesso numero dei bersagli!
5. **Posiziona il giocatore** - Posizione iniziale
6. **Posiziona il controllore di gioco** - Ovunque (è invisibile)

### Esempio di layout del livello

```
W W W W W W W W W W
W . . . . . . . . W
W . P . . . C . . W
W . . W W . . . . W
W . . W T . . C . W
W . . . . . W W . W
W . T . . . . . . W
W . . . . . . . . W
W W W W W W W W W W

W = Wall
P = Player
C = Crate
T = Target
. = Empty floor
```

**Importante:** Avere sempre lo stesso numero di casse e bersagli!

---

## Step 10: Testa il tuo gioco!

1. Fai clic su **Run** o premi **F5** per testare
2. Usa i tasti freccia per muoverti
3. Spingi le casse sui bersagli rossi X
4. Quando tutte le casse si trovano sui bersagli, vinci!

---

## Miglioramenti (opzionali)

### Aggiungi un contatore di mosse

In `obj_game_controller`:

**Event: Create** - Aggiungi:
```
global.moves = 0;
```

In `obj_player`, dopo ogni movimento riuscito, aggiungi:
```
global.moves += 1;
```

In `obj_game_controller` **Event: Draw** - Aggiungi:
```
draw_text(10, 30, "Moves: " + string(global.moves));
```

### Aggiungi funzione di annullamento

Archivia le posizioni precedenti e consenti di premere Z per annullare l'ultima mossa.

### Aggiungi più livelli

Crea più stanze (`room_level2`, `room_level3`, ecc.) e usa:
```
room_goto_next();
```
invece di `room_restart()` quando completi un livello.

### Aggiungi effetti sonori

Aggiungi suoni per:
- Movimento del giocatore
- Spinta di una cassa
- Atterraggio della cassa sul bersaglio
- Completamento del livello

---

## Risoluzione dei problemi

| Problema | Soluzione |
|---------|----------|
| Il giocatore si muove attraverso i muri | Verifica che `obj_wall` abbia "Solido" selezionato |
| La cassa non cambia colore | Verifica che l'evento Step controlli `place_meeting` correttamente |
| Puoi spingere la cassa attraverso il muro | Verifica il rilevamento delle collisioni prima di spostare la cassa |
| Il messaggio di vittoria viene visualizzato immediatamente | Assicurati che i bersagli siano posizionati separatamente dalle casse |
| Il giocatore si muove di più quadrati | Usa l'evento Keyboard Press, non l'evento Keyboard |

---

## Quello che hai imparato

Congratulazioni! Hai creato un gioco di puzzle Sokoban completo! Hai imparato:

- **Movimento basato su griglia** - Movimento in passi fissi di 32 pixel
- **Meccanica di spinta** - Rilevare e spostare gli oggetti che il giocatore spinge
- **Logica di collisione complessa** - Controllare più condizioni prima di consentire il movimento
- **Cambiamenti di stato** - Modifica dello sprite in base alla posizione dell'oggetto
- **Condizioni di vittoria** - Controllare quando tutti gli obiettivi sono completati
- **Progettazione di livelli** - Creazione di layout di puzzle risolvibili

---

## Sfida: progetta i tuoi livelli!

Il vero divertimento di Sokoban è la progettazione di puzzle. Prova a creare livelli che:
- Iniziano facilmente e diventano progressivamente più difficili
- Richiedono pianificazione in anticipo
- Hanno una sola soluzione
- Utilizzano lo spazio in modo efficiente e minimo

Ricorda: un buon puzzle di Sokoban dovrebbe essere impegnativo ma equo!

---

## Vedi anche

- [Tutorials](Tutorials_it) - Altri tutorial di gioco
- [Beginner Preset](Beginner-Preset_it) - Panoramica delle funzioni per principianti
- [Tutorial: Pong](Tutorial-Pong_it) - Crea un gioco per due giocatori
- [Tutorial: Breakout](Tutorial-Breakout_it) - Crea un gioco di rompimuri
- [Event Reference](Event-Reference_it) - Documentazione di riferimento dell'evento completa
