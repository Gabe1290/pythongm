# Tutorial: Creare un Gioco Platform

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Platformer) | [Français](Tutorial-Platformer_fr) | [Deutsch](Tutorial-Platformer_de) | [Italiano](Tutorial-Platformer_it) | [Español](Tutorial-Platformer_es) | [Português](Tutorial-Platformer_pt) | [Slovenščina](Tutorial-Platformer_sl) | [Українська](Tutorial-Platformer_uk) | [Русский](Tutorial-Platformer_ru)

---

## Introduzione

In questo tutorial creerai un **Gioco Platform** - un gioco d'azione a scorrimento laterale in cui il giocatore corre, salta e naviga tra le piattaforme evitando i pericoli e raccogliendo monete. Questo genere classico è perfetto per imparare la gravità, le meccaniche di salto e la collisione con le piattaforme.

**Cosa imparerai:**
- Gravità e fisica di caduta
- Meccaniche di salto con rilevamento del terreno
- Collisione con le piattaforme (atterrare sopra)
- Movimento sinistra/destra
- Oggetti da raccogliere e pericoli

**Difficoltà:** Principiante
**Preset:** Preset Intermedio (le azioni Execute Code della sezione Miglioramenti non sono nel preset Principiante; il tutorial di base fino al Passo 10 usa solo azioni del preset Principiante)

---

## Passo 1: Capire il Gioco

### Meccaniche di Gioco
1. Il giocatore è soggetto alla gravità e cade
2. Il giocatore può muoversi a sinistra e a destra
3. Il giocatore può saltare quando è sul terreno
4. Le piattaforme impediscono al giocatore di cadere attraverso
5. Raccogli monete per i punti
6. Raggiungi la bandiera per completare il livello

### Cosa Ci Serve

| Elemento | Scopo |
|----------|-------|
| **Giocatore** | Il personaggio che controlli |
| **Terreno/Piattaforma** | Superfici solide su cui stare |
| **Moneta** | Oggetti da raccogliere per il punteggio |
| **Punta** | Pericolo che ferisce il giocatore |
| **Bandiera** | Obiettivo che termina il livello |

---

## Passo 2: Creare gli Sprite

### 2.1 Sprite del Giocatore

1. Nell'**Albero delle Risorse**, fai clic destro su **Sprites** e seleziona **Create Sprite**
2. Chiamalo `spr_player`
3. Fai clic su **Edit Sprite** per aprire l'editor degli sprite
4. Disegna un personaggio semplice (rettangolo con faccia, o omino stilizzato)
5. Usa un colore vivace come blu o rosso
6. Dimensione: 32x48 pixel (più alto che largo per un personaggio)
7. Fai clic su **OK** per salvare

### 2.2 Sprite del Terreno

1. Crea un nuovo sprite chiamato `spr_ground`
2. Disegna una piastrella di piattaforma erba/terra
3. Usa colori marrone e verde
4. Dimensione: 32x32 pixel

### 2.3 Sprite della Piattaforma

1. Crea un nuovo sprite chiamato `spr_platform`
2. Disegna una piattaforma fluttuante (legno o pietra)
3. Dimensione: 64x16 pixel (larga e sottile)

### 2.4 Sprite della Moneta

1. Crea un nuovo sprite chiamato `spr_coin`
2. Disegna un piccolo cerchio giallo/dorato
3. Dimensione: 16x16 pixel

### 2.5 Sprite della Punta

1. Crea un nuovo sprite chiamato `spr_spike`
2. Disegna punte triangolari rivolte verso l'alto
3. Usa colori grigi o rossi
4. Dimensione: 32x32 pixel

### 2.6 Sprite della Bandiera

1. Crea un nuovo sprite chiamato `spr_flag`
2. Disegna una bandiera su un'asta
3. Usa colori vivaci (bandiera verde, asta marrone)
4. Dimensione: 32x64 pixel

![The Sprite Editor with spr_player open (32x48), origin centered; spr_player, spr_ground, spr_platform, spr_coin, spr_spike and spr_flag in the resource tree](images/tutorial-platformer-02-sprites.png)

---

## Passo 3: Creare l'Oggetto Terreno

Il terreno è una piattaforma solida che impedisce al giocatore di cadere.

1. Fai clic destro su **Objects** e seleziona **Create Object**
2. Chiamalo `obj_ground`
3. Imposta lo sprite su `spr_ground`
4. **Seleziona la casella "Solid"**
5. Nessun evento necessario

![obj_ground's Object Events panel: empty -- Solid checked is all it needs](images/tutorial-platformer-03-ground-object.png)

---

## Passo 4: Creare l'Oggetto Piattaforma

Le piattaforme funzionano come il terreno ma possono essere posizionate in aria.

1. Crea un nuovo oggetto chiamato `obj_platform`
2. Imposta lo sprite su `spr_platform`
3. **Seleziona la casella "Solid"**
4. Nessun evento necessario

**Suggerimento:** puoi rendere la piattaforma figlia di `obj_ground` per condividere lo stesso comportamento di collisione.

![obj_platform's Object Events panel: empty, with Solid checked -- a wide, thin sprite is the only difference from obj_ground](images/tutorial-platformer-04-platform-object.png)

---

## Passo 5: Creare l'Oggetto Giocatore

Il giocatore è l'oggetto più complesso, con gravità, salto e movimento.

1. Crea un nuovo oggetto chiamato `obj_player`
2. Imposta lo sprite su `spr_player`

### 5.1 Gravità

**Evento: Create** — Aggiungi l'azione **Move** → **Set Gravity**
(Direction: `270`, Gravity: `0.5`) — 270° è dritto verso il basso; il
valore viene sommato alla velocità verticale del giocatore a ogni passo,
quindi il giocatore accelera verso il basso da solo da qui in avanti.

### 5.2 Movimento, Salto e Collisione con il Terreno

Aggiungi questi eventi, seguendo lo stesso schema già usato dai tutorial
precedenti di questo wiki:

| Evento | Azione |
|---|---|
| Keyboard (held) → Left Arrow | Set Horizontal Speed a `-4` |
| Keyboard (held) → Right Arrow | Set Horizontal Speed a `4` |
| Keyboard: No Key | Set Horizontal Speed a `0` |
| Key Press → Up Arrow | Set Vertical Speed a `-10` |
| Collision with obj_ground | Stop Movement |

Due dettagli che rendono la sensazione giusta:

- **No Key azzera SOLO la velocità orizzontale** — non usare mai
  Stop Movement lì, perché Stop Movement azzera anche la velocità
  verticale, il che annullerebbe la gravità ogni volta che il giocatore
  rilascia un tasto direzionale.
- **Key Press (non held)** è ciò che rende Up un singolo impulso di
  salto, invece di spingere il giocatore verso l'alto a ogni frame in
  cui è tenuto premuto. **Stop Movement** all'atterraggio annulla poi
  quell'impulso, così il giocatore non continua a salire dopo essere
  atterrato — la collisione solida integrata del motore (il Passo 3 ha
  già reso `obj_ground` Solid) impedisce già al giocatore di sprofondare
  nel terreno; l'evento qui si limita a cancellare la velocità di caduta
  rimanente.

![obj_player's Object Events panel: Create (Set Gravity), Keyboard (held) with two Set Horizontal Speed actions, Keyboard <No Key>, Keyboard Press with the Up-Arrow jump, and Collision with obj_ground (Stop Movement)](images/tutorial-platformer-05-player-object.png)

---

## Passo 6: Creare l'Oggetto Moneta

Le monete aggiungono al punteggio quando vengono raccolte.

1. Crea un nuovo oggetto chiamato `obj_coin`
2. Imposta lo sprite su `spr_coin`

**Evento: Collision with obj_player**
1. Aggiungi Evento → Collision → obj_player
2. Aggiungi l'azione **Score** → **Set Score**
   - New Score: `10`
   - Seleziona "Relative"
3. Aggiungi l'azione **Main1** → **Destroy Instance**
   - Applies to: Self

![obj_coin's Object Events panel: a Collision with obj_player event holding Set Score (Relative) and Destroy Instance](images/tutorial-platformer-06-coin-object.png)

---

## Passo 7: Creare l'Oggetto Punta

Le punte feriscono il giocatore e riavviano il livello.

1. Crea un nuovo oggetto chiamato `obj_spike`
2. Imposta lo sprite su `spr_spike`

**Evento: Collision with obj_player**
1. Aggiungi Evento → Collision → obj_player
2. Aggiungi l'azione **Main2** → **Show Message**
   - Message: `Ouch! You hit a spike!`
3. Aggiungi l'azione **Main1** → **Restart Room**

![obj_spike's Object Events panel: a Collision with obj_player event holding Show Message and Restart Room](images/tutorial-platformer-07-spike-object.png)

---

## Passo 8: Creare l'Oggetto Bandiera

La bandiera termina il livello quando il giocatore la raggiunge.

1. Crea un nuovo oggetto chiamato `obj_flag`
2. Imposta lo sprite su `spr_flag`

**Evento: Collision with obj_player**
1. Aggiungi Evento → Collision → obj_player
2. Aggiungi l'azione **Output** → **Show Message**
   - Message: `Level Complete!`
3. Aggiungi l'azione **Room** → **Next Room** (o **Restart Room** per un singolo livello)

Il testo di Show Message è una stringa fissa — non può incorporare un
valore dinamico come il punteggio. L'HUD del controller di gioco (Passo 9)
mostra già il punteggio a schermo per tutto il livello, quindi il
giocatore l'ha già visto.

![obj_flag's Object Events panel: a Collision with obj_player event holding Show Message and Next Room](images/tutorial-platformer-08-flag-object.png)

---

## Passo 9: Creare il Controller di Gioco

Il controller di gioco mostra il punteggio.

1. Crea un nuovo oggetto chiamato `obj_game_controller`
2. Nessuno sprite necessario

**Evento: Draw**
1. Aggiungi Evento → Draw → Draw
2. Aggiungi l'azione **Draw** → **Draw Text** (Text: `Score:`, X: `10`, Y: `10`)
3. Aggiungi l'azione **Draw** → **Draw Variable** (Variable: `score`, X: `70`, Y: `10`)

Opzionale: aggiungi una coppia **Draw Text** (`Lives:`, X `10`, Y `30`) +
**Draw Variable** (`lives`, X `70`, Y `30`) allo stesso modo, una volta
che il miglioramento Sistema di Vite qui sotto è a posto.

![obj_game_controller's Object Events panel: a Draw event with one Draw Text and one Draw Variable action, with no sprite set](images/tutorial-platformer-09-controller-object.png)

---

## Passo 10: Progettare il Tuo Livello

1. Fai clic destro su **Rooms** e seleziona **Create Room**
2. Chiamala `room_level1`
3. Imposta la dimensione della room (es. 800x480)
4. Attiva "Snap to Grid" e imposta la griglia su 32x32

### Posizionare gli Oggetti

Costruisci il tuo livello seguendo queste linee guida:

1. **Crea il terreno** - Posiziona `obj_ground` lungo il fondo
2. **Aggiungi piattaforme** - Posiziona `obj_platform` in aria per sfide di salto
3. **Aggiungi vuoti** - Lascia spazi nel terreno (fosse)
4. **Posiziona monete** - Sparpagliale sulle piattaforme e in punti difficili da raggiungere
5. **Aggiungi punte** - Vicino alle fosse o sulle piattaforme come sfida
6. **Posiziona la bandiera** - Alla fine del livello
7. **Posiziona il giocatore** - All'inizio (lato sinistro)
8. **Aggiungi il controller di gioco** - Ovunque (è invisibile)

### Esempio di Layout del Livello

```
                                        F
                                      ===
                          C       C
                        =====   =====
            C                           C
          ===== X     X         X     =====
    P                   C
  ====== === ===   ===   === === ===== ======
  GGGGGG     GGG   GGG   GGG         GGGGGGGG

G = Terreno    P = Giocatore    F = Bandiera    C = Moneta
X = Punta    === = Piattaforma
```

![The Room Editor for room_level1: a brown ground row with two pit gaps, four tan floating platforms at rising heights, gold coins on and above them, two grey spikes on the ground, the red player at the far left and the green flag at the far right](images/tutorial-platformer-10-room.png)

---

## Passo 11: Prova il Tuo Gioco!

1. Fai clic su **Esegui** o premi **F5** per testare
2. Usa le frecce **Sinistra/Destra** per muoverti
3. Premi **Su** o **Spazio** per saltare
4. Raccogli monete per i punti
5. Evita le punte!
6. Raggiungi la bandiera per vincere!

---

## Miglioramenti (Opzionale)

### Aggiungere un'Altezza di Salto Variabile

Aggiungi un evento **Step** a `obj_player` con **Control** → **Execute
Code** (Python reale — `self` è l'istanza corrente, `keyboard` ti permette
di controllare un tasto tenuto premuto per nome):

```python
# Interrompe il salto se Up viene rilasciato mentre si sale ancora
if self.vspeed < 0 and not keyboard.check('up'):
    self.vspeed = max(self.vspeed, -5)  # metà dell'impulso di salto -10
```

### Aggiungere il Doppio Salto

Si può fare interamente con azioni strutturate — nessun codice necessario.

**Evento: Create** — Aggiungi l'azione **Control** → **Set Variable**
(Variable: `jumps_left`, Value: `2`)

**Evento: Collision with obj_ground** — dopo **Stop Movement**, aggiungi
**Control** → **Set Variable** (Variable: `jumps_left`, Value: `2`) per
ricaricare entrambi i salti all'atterraggio.

Sostituisci l'unica azione dell'evento **Key Press → Up Arrow** esistente
con tre, in ordine:
1. **Control** → **Test Variable** (Variable: `jumps_left`, Value: `0`,
   Operation: `greater`)
2. **Control** → **Start Block**
3. **Move** → **Set Vertical Speed** (`-10`)
4. **Control** → **Set Variable** (Variable: `jumps_left`, Value: `-1`,
   **Relative** selezionato)
5. **Control** → **End Block**

La coppia Start/End Block significa che entrambe le azioni al suo interno
vengono eseguite solo quando il Test Variable sopra è vero — lo stesso
schema di blocco protetto che i tutorial Sokoban e Labirinto usano per le
loro condizioni.

### Aggiungere Piattaforme Mobili

1. Crea `obj_moving_platform` come figlio di `obj_platform`

**Evento: Create** — Aggiungi l'azione **Control** → **Execute Code**:

```python
self.start_x = self.x
self.hspeed = 2
```

**Evento: Step** — Aggiungi l'azione **Control** → **Execute Code**:

```python
if self.x > self.start_x + 100:
    self.hspeed = -2
elif self.x < self.start_x:
    self.hspeed = 2
```

### Aggiungere un Nemico

1. Crea `obj_enemy` con un'IA semplice

**Evento: Create** — Aggiungi l'azione **Move** → **Start Moving
Direction** (Directions: `right`, Speed: `2`)

**Evento: Collision with obj_ground** — Aggiungi l'azione **Move** →
**Reverse Horizontal** (fa inversione ai muri; combinato con il fatto che
`obj_ground` è Solid, il nemico non può mai uscire dal bordo di una
piattaforma nel terreno sottostante né attraversare un muro)

**Evento: Collision with obj_player** — questo evento scatta su
`obj_enemy`, quindi `self` è il nemico e `other` è il giocatore. Aggiungi
l'azione **Control** → **Test Expression**, con azioni Then/Else annidate
(lo stesso schema che l'esempio incluso `plateforme_3` usa esattamente
per questo controllo di "salto sulla testa", solo rispecchiato perché qui
il controllo vive sul nemico invece che sul giocatore):
   - Expression: `other.vspeed > 0 and other.y - other.vspeed < y - 16`
   - Then Actions: **Control** → **Execute Code** con `other.vspeed = -5`
     (un piccolo rimbalzo per il giocatore — `set_vspeed` non ha
     un'opzione "applies to other", quindi questo è l'unico punto che
     richiede una riga di Python reale invece di un'azione strutturata),
     poi **Instance** → **Destroy Instance** (self)
   - Else Actions: **Room** → **Restart Room** (il giocatore muore)

`other.vspeed > 0 and other.y - other.vspeed < y - 16` controlla la
posizione *del giocatore* da prima del movimento di caduta di questo frame
(usando il `vspeed` del giocatore stesso, dato che è lui a cadere), così
una caduta veloce non può attraversare la finestra di salto di 16 px in un
solo passo — vedi il README di `plateforme_3` per la storia completa del
perché la versione ingenua `other.y < y - 16` è fragile.

### Aggiungere un Sistema di Vite

Nell'evento **Create** di `obj_game_controller`, aggiungi **Score** →
**Set Lives** (Value: `3`).

Quando il giocatore muore (la collisione con la punta e il ramo Else del
nemico sopra), sostituisci **Restart Room** con **Score** → **Set Lives**
(Value: `-1`, **Relative** selezionato) — la room si riavvia
automaticamente perché l'evento **No More Lives** scatta solo quando le
vite raggiungono effettivamente 0. Aggiungi quell'evento a
`obj_game_controller`: **Other Events** → **No More Lives** → **Output** →
**Show Message** (`Game Over!`) → **Room** → **Restart Game**.

---

## Risoluzione dei Problemi

| Problema | Soluzione |
|----------|-----------|
| Il giocatore cade attraverso il terreno | Controlla che `obj_ground` abbia "Solid" selezionato |
| Il giocatore non può saltare | Verifica che l'evento Key Press → Up Arrow esista e che Set Vertical Speed sia negativo |
| Il giocatore continua a salire dopo l'atterraggio | Assicurati che Collision with obj_ground abbia un'azione Stop Movement |
| Il salto sembra fluttuante | Aumenta il valore Gravity di Set Gravity, o rendi il valore di salto di Set Vertical Speed più negativo |
| Il salto sembra troppo debole | Diminuisci il valore Gravity di Set Gravity, o rendi il valore di salto di Set Vertical Speed più negativo |

---

## Cosa Hai Imparato

Congratulazioni! Hai creato un gioco platform! Hai imparato:

- **Fisica della gravità** - Set Gravity applica una forza costante verso il basso a ogni passo
- **Meccaniche di salto** - Un evento Key Press (non held) dà un singolo impulso di velocità verso l'alto
- **Collisione solida integrata** - Il terreno blocca il giocatore automaticamente una volta marcato Solid, senza codice manuale di controllo della posizione
- **Pericoli** - Creare oggetti che riavviano il livello
- **Progettazione dei livelli** - Costruire sfide di gioco platform

---

## Idee di Sfida

1. **Salto sul Muro** - Permettere di saltare via dai muri
2. **Mossa di Scatto** - Un breve scatto orizzontale di velocità
3. **Piattaforme che Crollano** - Piattaforme che cadono dopo che ci si è saliti
4. **Punti di Controllo** - Salvare i progressi a metà livello
5. **Combattimento con il Boss** - Aggiungere un nemico finale con più colpi

---

## Vedi Anche

- [Tutorial](Tutorials_it) - Altri tutorial di giochi
- [Preset Intermedio](Intermediate-Preset_it) - Panoramica del preset di cui ha bisogno la sezione Miglioramenti
- [Tutorial: Labirinto](Tutorial-Maze_it) - Creare un gioco di navigazione in un labirinto
- [Tutorial: Breakout](Tutorial-Breakout_it) - Creare un gioco rompi-mattoni
- [Riferimento Eventi](Event-Reference_it) - Documentazione completa degli eventi
