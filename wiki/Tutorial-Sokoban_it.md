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
**Preset:** Preset Intermedio (la meccanica di spinta e il movimento su
griglia usati qui non sono inclusi nel preset Principiante)

---

## Step 1: Comprendi il gioco

### Regole del gioco
1. Il giocatore può muoversi verso l'alto, il basso, sinistra o destra
2. Il giocatore può spingere le casse (ma non tirarle)
3. Solo una cassa può essere spinta alla volta
4. Le casse non possono essere spinte attraverso muri o altre casse
5. Il livello è completato quando tutte le casse si trovano nei punti bersaglio

### Quello che ci serve

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

1. Nell'**Albero delle risorse**, fai clic destro su **Sprites** e seleziona **Create Sprite**
2. Nominalo `spr_player`
3. Fai clic su **Edit Sprite** per aprire l'editor degli sprite
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

1. Fai clic destro su **Objects** e seleziona **Create Object**
2. Nominalo `obj_wall`
3. Imposta lo sprite su `spr_wall`
4. **Seleziona la casella "Solid"**
5. Non sono necessari eventi

---

## Step 4: Crea l'oggetto bersaglio

I bersagli indicano dove devono essere posizionate le casse.

1. Crea un nuovo oggetto denominato `obj_target`
2. Imposta lo sprite su `spr_target`
3. Non sono necessari eventi - è solo un marcatore
4. Lascia "Solid" deselezionato (il giocatore e le casse possono stare sopra)

---

## Step 5: Crea l'oggetto cassa

La cassa viene spinta dal giocatore e cambia aspetto quando si trova su un bersaglio.

1. Crea un nuovo oggetto denominato `obj_crate`
2. Imposta lo sprite su `spr_crate`
3. **Seleziona la casella "Solid"**

**Evento: Step**
1. Add Event → Step → Step
2. Add Action: **Control** → **If Collision**
   - X Offset: `0`
   - Y Offset: `0`
   - Against: `obj_target`
3. Add Action: **Instance** → **Set Sprite**
   - Sprite: `spr_crate_ok`
4. Add Action: **Control** → **Else**
5. Add Action: **Instance** → **Set Sprite**
   - Sprite: `spr_crate`

Questo fa diventare la cassa verde quando si trova su un punto bersaglio —
**If Collision** con entrambi gli offset a `0` verifica se la posizione
*attuale* della cassa sovrappone un `obj_target`.

---

## Step 6: Crea l'oggetto giocatore

Il giocatore si muove esattamente di una cella della griglia alla volta e spinge le casse in cui si imbatte.

1. Crea un nuovo oggetto denominato `obj_player`
2. Imposta lo sprite su `spr_player`

### 6.1 Movimento su griglia

Aggiungi un evento **Key Press** per ogni direzione, ciascuno con un'azione **Move** → **Move Grid**:

| Evento | Azione Move Grid |
|---|---|
| Key Press → Right Arrow | Direction: `right`, Grid Size: `32` |
| Key Press → Left Arrow | Direction: `left`, Grid Size: `32` |
| Key Press → Up Arrow | Direction: `up`, Grid Size: `32` |
| Key Press → Down Arrow | Direction: `down`, Grid Size: `32` |

**Move Grid** sposta l'istanza esattamente di una cella della griglia ed è
già consapevole delle collisioni per conto proprio — non farà muovere il
giocatore dentro un `obj_wall` solido, quindi non serve un controllo
aggiuntivo sui muri qui.

### 6.2 Fermarsi ai muri

**Evento: Collision with obj_wall**
1. Add Event → Collision → `obj_wall`
2. Add Action: **Move** → **Stop Movement**

### 6.3 Spingere le casse

**Evento: Collision with obj_crate**
1. Add Event → Collision → `obj_crate`
2. Add Action: **Control** → **If Can Push**
   - Direction: `facing`
   - Object Type: `obj_crate`
   - Then Action: `push_and_move`

**If Can Push** verifica se lo spazio dietro la cassa (nella direzione in
cui si muove il giocatore) è libero e, in tal caso, spinge la cassa di una
cella e sposta il giocatore al suo posto, tutto in un'unica azione. Se lo
spazio dietro la cassa è bloccato da un muro o da un'altra cassa, nulla si
muove.

---

## Step 7: Crea il controllo della condizione di vittoria

Ci serve un controllore invisibile che osservi se ogni cassa si trova su un bersaglio.

1. Crea un nuovo oggetto denominato `obj_game_controller`
2. Non è necessario uno sprite

**Evento: Create** — imposta il conteggio dei bersagli una sola volta,
usando **Control** → **Execute Code** (l'azione Execute Code di questo
progetto esegue vero Python, non GameMaker Language — `self` è l'istanza
corrente, `game` è il game runner):

```python
# Conta quanti bersagli esistono nella stanza
self.total_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_target'
)
```

**Evento: Step** — controlla ad ogni frame se tutte le casse si trovano su un bersaglio:

```python
# Conta le casse che attualmente sovrappongono un bersaglio
crates_on_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_crate'
    and game.check_collision_at_position(inst, inst.x, inst.y, 'obj_target')
)

if self.total_targets > 0 and crates_on_targets >= self.total_targets:
    self.restart_room_flag = True
```

`self.restart_room_flag = True` è il modo in cui un blocco Execute Code
grezzo attiva lo stesso riavvio della stanza eseguito dall'azione
**Restart Room** — il ciclo principale lo controlla ad ogni frame.
Aggiungi un'azione **Show Message** (da **Output**, messaggio `Level
Complete!`) subito dopo il blocco Execute Code se vuoi mostrare un popup
prima del riavvio.

**Evento: Draw**
1. Add Event → Draw
2. Add Action: **Draw** → **Draw Text**
   - Text: `Sokoban - Push all crates to targets!`
   - X: `10`
   - Y: `10`

---

## Step 9: Progetta il tuo livello

1. Fai clic destro su **Rooms** e seleziona **Create Room**
2. Nominalo `room_level1`
3. Imposta la dimensione della stanza su un multiplo di 32 (ad es. 640x480)
4. Abilita "Snap to Grid" e imposta la griglia su 32x32

### Posizionamento di oggetti

Costruisci il tuo livello seguendo queste linee guida:

1. **Circonda il livello con muri** - Crea un bordo
2. **Aggiungi muri interni** - Crea la struttura del puzzle
3. **Posiziona i bersagli** - Dove le casse devono andare
4. **Posiziona le casse** - Lo stesso numero dei bersagli!
5. **Posiziona il giocatore** - Posizione iniziale
6. **Posiziona il game controller** - Ovunque (è invisibile)

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

W = Muro
P = Giocatore
C = Cassa
T = Bersaglio
. = Pavimento vuoto
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

Nell'evento **Create** di `obj_game_controller`, aggiungi **Control** →
**Set Variable** (Variable: `global.moves`, Value: `0`, Scope: `global`).

In ciascuno dei quattro eventi Key Press di `obj_player`, aggiungi una
seconda azione subito dopo Move Grid: **Control** → **Set Variable**
(Variable: `global.moves`, Value: `1`, Scope: `global`, **Relative**
selezionato) — questo aggiunge 1 al contatore ad ogni pressione di tasto,
indipendentemente dal fatto che il movimento sia stato effettivamente
bloccato da un muro.

Nell'evento **Draw** di `obj_game_controller`, aggiungi **Draw** →
**Draw Variable** (Variable: `global.moves`, X: `10`, Y: `30`).

### Aggiungi funzione di annullamento

Archivia le posizioni precedenti e consenti di premere Z per annullare l'ultima mossa.

### Aggiungi più livelli

Crea più stanze (`room_level2`, `room_level3`, ecc.) e usa l'azione
**Next Room** (categoria Room) al posto di **Restart Room** nel blocco
Execute Code di controllo vittoria (`self.next_room_flag = True` invece di
`self.restart_room_flag = True`) quando un livello viene completato.

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
| Il giocatore si muove attraverso i muri | Verifica che `obj_wall` abbia "Solid" selezionato |
| La cassa non cambia colore | Verifica che l'azione **If Collision** nell'evento Step punti a `obj_target` |
| Puoi spingere la cassa attraverso il muro | Verifica il rilevamento delle collisioni prima di spostare la cassa |
| Il messaggio di vittoria viene visualizzato immediatamente | Assicurati che i bersagli siano posizionati separatamente dalle casse |
| Il giocatore si muove di più caselle | Usa l'evento Keyboard Press, non l'evento Keyboard |

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
- [Intermediate Preset](Intermediate-Preset_it) - Panoramica del preset necessario per questo tutorial
- [Tutorial: Pong](Tutorial-Pong_it) - Crea un gioco per due giocatori
- [Tutorial: Breakout](Tutorial-Breakout_it) - Crea un gioco di rompimuri
- [Event Reference](Event-Reference_it) - Documentazione di riferimento dell'evento completa
