# Tutorial: Creare un Gioco di Allunaggio

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Introduzione

In questo tutorial creerai un **Gioco di Allunaggio** - un classico gioco arcade in cui controlli una navicella spaziale che scende su una piattaforma di atterraggio. Devi gestire la tua spinta per contrastare la gravità e atterrare dolcemente senza schiantarti. Questo gioco è perfetto per imparare concetti di fisica come gravità, spinta, velocità e gestione del carburante.

**Cosa imparerai:**
- Fisica di gravità e spinta
- Rilevamento dell'atterraggio basato sulla velocità
- Sistema di gestione del carburante
- Controllo di rotazione o direzionale
- Zone di atterraggio sicure

**Difficoltà:** Principiante
**Preset:** Preset Intermedio (la fisica di spinta/carburante si affida a Execute Code ovunque, che non è nel preset Principiante)

---

## Passo 1: Capire il Gioco

### Meccaniche di Gioco
1. Il modulo è tirato verso il basso dalla gravità
2. Premere SU applica spinta verso l'alto (consuma carburante)
3. SINISTRA/DESTRA controllano la rotazione o il movimento del modulo
4. Atterra dolcemente sulla piattaforma per vincere
5. Ti schianti se atterri troppo veloce o manchi la piattaforma
6. Se finisci il carburante non puoi più rallentare!

### Cosa Ci Serve

| Elemento | Scopo |
|----------|-------|
| **Modulo** | La navicella che controlli |
| **Piattaforma di Atterraggio** | Zona sicura su cui atterrare |
| **Terreno** | Terreno che causa uno schianto |
| **Indicatore Carburante** | Mostra il carburante rimanente |
| **Indicatore Velocità** | Mostra la velocità attuale |

---

## Passo 2: Creare gli Sprite

### 2.1 Sprite del Modulo

1. Nell'**Albero delle Risorse**, fai clic destro su **Sprites** e seleziona **Create Sprite**
2. Chiamalo `spr_lander`
3. Fai clic su **Edit Sprite** per aprire l'editor degli sprite
4. Disegna una navicella semplice (triangolo o forma di modulo classica)
5. Dimensione: 32x32 pixel
6. **Importante:** imposta l'origine su centro-basso per un atterraggio corretto

### 2.2 Sprite della Piattaforma di Atterraggio

1. Crea un nuovo sprite chiamato `spr_pad`
2. Disegna una piattaforma piatta con segni (come una "H")
3. Usa colori vivaci (giallo/verde)
4. Dimensione: 64x16 pixel

### 2.3 Sprite del Terreno

1. Crea un nuovo sprite chiamato `spr_ground`
2. Disegna un terreno roccioso/accidentato
3. Usa colori grigio/marrone
4. Dimensione: 32x32 pixel

### 2.4 Sprite della Fiamma (Opzionale)

1. Crea un nuovo sprite chiamato `spr_flame`
2. Disegna una piccola fiamma/getto di scarico
3. Usa colori arancione/giallo
4. Dimensione: 16x16 pixel

![The Sprite Editor with spr_lander open, Origin set to Center-Bottom (X 16, Y 32); spr_lander, spr_pad, spr_ground and spr_flame in the resource tree](images/tutorial-lunarlander-02-sprites.png)

---

## Passo 3: Creare l'Oggetto Terreno

Il terreno è terreno pericoloso che causa uno schianto.

1. Fai clic destro su **Objects** e seleziona **Create Object**
2. Chiamalo `obj_ground`
3. Imposta lo sprite su `spr_ground`
4. **Seleziona la casella "Solid"**
5. Nessun evento necessario

![obj_ground's Object Events panel: empty -- Solid checked is all it needs](images/tutorial-lunarlander-03-ground-object.png)

---

## Passo 4: Creare l'Oggetto Piattaforma di Atterraggio

La piattaforma di atterraggio è il punto in cui il giocatore deve atterrare in sicurezza.

1. Crea un nuovo oggetto chiamato `obj_pad`
2. Imposta lo sprite su `spr_pad`
3. **Seleziona la casella "Solid"**
4. Nessun evento necessario (la collisione è gestita dal modulo)

![obj_pad's Object Events panel: empty, with Solid checked](images/tutorial-lunarlander-04-pad-object.png)

---

## Passo 5: Creare l'Oggetto Modulo

Il modulo è il principale oggetto controllato dal giocatore, con fisica. A
differenza degli altri tutorial di movimento di questo wiki, i suoi
comandi devono accumulare velocità gradualmente e tracciare una risorsa
di carburante, quindi questo oggetto si affida più a **Control** →
**Execute Code** (Python reale — `self` è l'istanza corrente, `game` è il
game runner, `keyboard.check(nome)` segnala un tasto tenuto premuto) che
alle sole azioni strutturate. Ovunque un'azione strutturata svolga il
lavoro, questo tutorial ne usa comunque una.

1. Crea un nuovo oggetto chiamato `obj_lander`
2. Imposta lo sprite su `spr_lander`

### 5.1 Gravità e Variabili Iniziali

**Evento: Create**
1. Aggiungi l'azione **Move** → **Set Gravity** (Direction: `270`, Gravity: `0.05`)
   — una lieve attrazione verso il basso; il motore la aggiunge
   automaticamente alla velocità verticale del modulo a ogni passo, come
   la gravità del tutorial Platform, solo più debole.
2. Aggiungi l'azione **Control** → **Execute Code**:

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

Il sistema di movimento di questo progetto traccia già la velocità
tramite `self.hspeed`/`self.vspeed` e sposta l'istanza di quella quantità
a ogni frame (con la collisione solida integrata) — non serve creare
variabili `hsp`/`vsp` separate come farebbe una simulazione fisica grezza.

### 5.2 Evento Step — Spinta e Comandi

**Evento: Step** — Aggiungi l'azione **Control** → **Execute Code**:

```python
if not self.landed and not self.crashed:
    if keyboard.check('up') and self.fuel > 0:
        self.vspeed -= self.thrust_force
        self.fuel -= self.fuel_use
        if self.fuel < 0:
            self.fuel = 0

    if keyboard.check('left'):
        self.hspeed -= 0.05
    if keyboard.check('right'):
        self.hspeed += 0.05

    # Limita la velocità massima
    self.hspeed = max(-self.max_speed, min(self.max_speed, self.hspeed))
    self.vspeed = max(-self.max_speed, min(self.max_speed, self.vspeed))

    # Impedisce al modulo di uscire dai lati o sopra la room
    room = game.current_room
    if self.x < 16:
        self.x = 16
        self.hspeed = 0
    if self.x > room.width - 16:
        self.x = room.width - 16
        self.hspeed = 0
    if self.y < 16:
        self.y = 16
        self.vspeed = 0
```

L'intero blocco è racchiuso in `if not self.landed and not self.crashed:`
così che spinta e sterzata si fermino nell'istante in cui la partita
finisce — l'oggetto `self` non ha un modo per abbandonare un evento a
metà (nessun `exit` in stile GML), quindi un `if` attorno al resto del
codice è l'equivalente.

### 5.3 Collisione con la Piattaforma di Atterraggio

**Evento: Collision with obj_pad**
1. Aggiungi l'azione **Control** → **Test Expression**
   - Expression: `(self.hspeed**2 + self.vspeed**2)**0.5 <= self.safe_speed`
     — la velocità di atterraggio è la lunghezza del vettore velocità;
     Pitagora, non una variabile `speed` (in questo motore, `speed` è la
     *velocità di animazione dello sprite*, non la magnitudine del
     movimento — una vera trappola per chi viene da GameMaker).
   - Then Actions:
     1. **Control** → **Set Variable** (Variable: `landed`, Value: `true`, Scope: `self`)
     2. **Move** → **Stop Movement**
     3. **Move** → **Set Gravity** (Direction: `270`, Gravity: `0`) —
        impedisce alla gravità di riaccumulare silenziosamente velocità
        verticale su un modulo già atterrato
     4. **Output** → **Show Message** (Message: `Perfect Landing! You Win!`)
   - Else Actions:
     1. **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
     2. **Output** → **Show Message** (Message: `Crashed! Too fast!`)
     3. **Room** → **Restart Room**

Il testo di Show Message è una stringa fissa — non può incorporare la
velocità reale di atterraggio. L'HUD (Passo 7) mostra già la velocità in
tempo reale fino al momento del contatto, quindi il giocatore ha già
visto il numero.

### 5.4 Collisione con il Terreno

**Evento: Collision with obj_ground**
1. Aggiungi l'azione **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
2. Aggiungi l'azione **Output** → **Show Message** (Message: `Crashed into terrain!`)
3. Aggiungi l'azione **Room** → **Restart Room**

![obj_lander's Object Events panel: Create (Set Gravity + Execute Code), Step (Execute Code), Collision with obj_pad (the Test Expression landing check), Collision with obj_ground (Set Variable + Show Message + Restart Room)](images/tutorial-lunarlander-05-lander-object.png)

---

## Passo 6: Creare l'Oggetto Fiamma (Opzionale)

Riscontro visivo durante la spinta.

1. Crea un nuovo oggetto chiamato `obj_flame`
2. Imposta lo sprite su `spr_flame`

Verrà creato dal modulo durante la spinta (funzione avanzata). Per un
approccio più semplice, puoi disegnare la fiamma nell'evento Draw del
modulo.

![obj_flame's Object Events panel: empty -- it just needs the spr_flame sprite](images/tutorial-lunarlander-06-flame-object.png)

---

## Passo 7: Creare il Controller di Gioco

Il controller di gioco mostra carburante, velocità e istruzioni leggendoli
dall'istanza del modulo a ogni frame.

1. Crea un nuovo oggetto chiamato `obj_game_controller`
2. Nessuno sprite necessario

**Evento: Draw**
1. Aggiungi l'azione **Control** → **Execute Code** — trova il modulo e
   calcola i valori che le azioni Draw qui sotto mostreranno:

```python
lander = None
for inst in game.current_room.instances:
    if inst.object_name == 'obj_lander':
        lander = inst
        break

if lander is not None:
    self.fuel_display = round(lander.fuel)
    self.speed_display = round((lander.hspeed ** 2 + lander.vspeed ** 2) ** 0.5, 2)
    self.too_fast = self.speed_display > lander.safe_speed
    self.no_fuel = lander.fuel <= 0
else:
    self.fuel_display = 0
    self.speed_display = 0.0
    self.too_fast = False
    self.no_fuel = False
```

2. Aggiungi l'azione **Game** → **Set Draw Color** (Color: `#FFFFFF`)
3. Aggiungi l'azione **Game** → **Draw Text** (Text: `LUNAR LANDER`, X: `10`, Y: `10`)
4. Aggiungi l'azione **Game** → **Draw Text** (Text: `Fuel:`, X: `10`, Y: `30`)
5. Aggiungi l'azione **Game** → **Draw Variable** (Variable: `self.fuel_display`, X: `70`, Y: `30`)
6. Aggiungi l'azione **Game** → **Draw Text** (Text: `Speed:`, X: `10`, Y: `50`)
7. Aggiungi l'azione **Game** → **Draw Variable** (Variable: `self.speed_display`, X: `70`, Y: `50`)
8. Aggiungi l'azione **Game** → **Draw Text** (Text: `Safe Speed: < 2`, X: `10`, Y: `70`)

Poi le due righe di avviso, ciascuna condizionata da **Control** → **Test
Expression** (nessun Else necessario — non si disegna nulla quando la
condizione è falsa):

9. **Control** → **Test Expression** (Expression: `self.too_fast`)
   - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
     **Draw Text** (`TOO FAST!`, X `10`, Y `90`)
   - Else Actions: **Game** → **Set Draw Color** (`#00FF00`), **Game** →
     **Draw Text** (`Speed OK`, X `10`, Y `90`)
10. **Control** → **Test Expression** (Expression: `self.no_fuel`)
    - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
      **Draw Text** (`NO FUEL!`, X `10`, Y `110`)

11. Aggiungi l'azione **Game** → **Set Draw Color** (Color: `#808080`)
12. Aggiungi l'azione **Game** → **Draw Text** (Text: `UP: Thrust | LEFT/RIGHT: Move`,
    X: `10`, Y: `440`) — scegli una Y vicino al fondo della dimensione di
    room che usi nel Passo 8.

![obj_game_controller's Object Events panel: a Draw event with 12 actions -- the Execute Code HUD-value calculation, then the Set Draw Color / Draw Text / Draw Variable chain and the two Test Expression warning blocks -- with no sprite set](images/tutorial-lunarlander-07-controller-object.png)

---

## Passo 8: Progettare il Tuo Livello

1. Fai clic destro su **Rooms** e seleziona **Create Room**
2. Chiamala `room_game`
3. Imposta la dimensione della room (es. 640x480)
4. Imposta il colore di sfondo su nero (lo spazio)

### Posizionare gli Oggetti

Costruisci il tuo livello seguendo queste linee guida:

1. **Terreno** - Posiziona `obj_ground` lungo il fondo per creare il terreno
2. **Piattaforma di atterraggio** - Posiziona `obj_pad` in un vuoto del terreno
3. **Modulo** - Posiziona `obj_lander` in cima alla room
4. **Controller di gioco** - Posiziona `obj_game_controller` ovunque

### Esempio di Layout del Livello

```
    L                          <- Il modulo parte qui




GGG    GGG    PPPP    GGG    GGG
GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG

G = Terreno    L = Modulo    P = Piattaforma di atterraggio
```

![The Room Editor for room_game: a solid terrain row along the bottom with rocky chunks above it, a yellow landing pad in a clear gap, the white lander near the top-left, and the obj_game_controller marker near the top-right, all on a black space background](images/tutorial-lunarlander-08-room.png)

---

## Passo 9: Prova il Tuo Gioco!

1. Fai clic su **Esegui** o premi **F5** per testare
2. Usa la freccia **SU** per la spinta (occhio al carburante!)
3. Usa le frecce **SINISTRA/DESTRA** per sterzare
4. Atterra dolcemente sulla piattaforma (la velocità deve essere sotto 2)
5. Evita il terreno roccioso!

---

## Miglioramenti (Opzionale)

### Aggiungere il Controllo di Rotazione

Invece del movimento sinistra/destra, ruota il modulo e spingi nella
direzione verso cui è rivolto. Le istanze di questo motore hanno un vero
attributo `rotation` (gradi, 0 = destra, crescente in senso antiorario)
usato per ruotare lo sprite — non serve
`image_angle`/`lengthdir_x`/`lengthdir_y`, dato che `math` è già
disponibile in Execute Code:

Sostituisci il codice dell'evento Create del 5.1 con:
```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
self.rotation = 90  # rivolto verso l'alto
self.rotation_speed = 3
```

Sostituisci le righe di sterzata del 5.2 (il blocco `left`/`right` →
`hspeed`) con:
```python
if keyboard.check('left'):
    self.rotation -= self.rotation_speed
if keyboard.check('right'):
    self.rotation += self.rotation_speed
```

E sostituisci le righe di spinta con:
```python
if keyboard.check('up') and self.fuel > 0:
    rad = math.radians(self.rotation)
    self.hspeed += self.thrust_force * math.cos(rad)
    self.vspeed -= self.thrust_force * math.sin(rad)
    self.fuel -= self.fuel_use
    if self.fuel < 0:
        self.fuel = 0
```

(il `-=` su `vspeed` corrisponde al codice di gravità del motore stesso —
l'asse Y dello schermo cresce verso il basso, quindi "su" è velocità
verticale negativa).

### Aggiungere Più Piattaforme di Atterraggio

Crea piattaforme di dimensioni diverse con valori di punti diversi:
- Piattaforma piccola = 100 punti (più difficile)
- Piattaforma grande = 50 punti (più facile)

### Aggiungere Rifornimenti di Carburante

1. Crea `obj_fuel` che fluttua in aria
2. Alla collisione con il modulo, aggiungi carburante e distruggilo

### Aggiungere Livelli

Crea più room con terreno sempre più difficile e piattaforme di
atterraggio più piccole.

### Aggiungere il Vento

Aggiungi una piccola spinta orizzontale costante. Nel codice dell'evento
Create di `obj_lander`, aggiungi `self.wind_force = 0.02`; poi, all'inizio
del blocco `if not self.landed and not self.crashed:` dell'evento Step,
aggiungi:
```python
self.hspeed += self.wind_force
```

---

## Risoluzione dei Problemi

| Problema | Soluzione |
|----------|-----------|
| Il modulo cade troppo veloce | Diminuisci il valore `Gravity` di Set Gravity, o aumenta `thrust_force` nel codice dell'evento Create |
| Non riesco a rallentare abbastanza | Aumenta `thrust_force`, o aumenta `safe_speed` |
| Il carburante finisce troppo in fretta | Diminuisci `fuel_use`, o aumenta il `fuel` iniziale |
| Il modulo esce dallo schermo | Controlla il blocco dei limiti alla fine del codice dell'evento Step |
| L'atterraggio non viene registrato | Assicurati che `obj_pad` abbia "Solid" selezionato |

---

## Cosa Hai Imparato

Congratulazioni! Hai creato un gioco di allunaggio! Hai imparato:

- **Fisica della spinta** - Spingere `self.vspeed` contro un'attrazione continua di Set Gravity
- **Gestione della velocità** - Calcolare la velocità da `hspeed`/`vspeed` con il teorema di Pitagora
- **Sistema di carburante** - Gameplay di gestione delle risorse con una semplice variabile di istanza
- **Rilevamento delle collisioni** - Esiti diversi per piattaforma vs terreno, scelti con Test Expression
- **Visualizzazione HUD** - Calcolare i valori da mostrare in Execute Code e poi mostrarli con Draw Text/Draw Variable

---

## Idee di Sfida

1. **Rotazione Realistica** - Ruotare e spingere nella direzione verso cui si è rivolti
2. **Più Livelli** - Terreno sempre più difficile
3. **Sistema di Punteggio** - Punti in base al carburante rimanente e alla precisione dell'atterraggio
4. **Asteroidi** - Aggiungere pericoli mobili da evitare
5. **Modalità a Due Giocatori** - Gara ad atterrare per primi

---

## Vedi Anche

- [Tutorial](Tutorials_it) - Altri tutorial di giochi
- [Preset Intermedio](Intermediate-Preset_it) - Panoramica del preset di cui ha bisogno questo tutorial
- [Tutorial: Platform](Tutorial-Platformer_it) - Creare un gioco di salti su piattaforme
- [Tutorial: Labirinto](Tutorial-Maze_it) - Creare un gioco di navigazione in un labirinto
- [Riferimento Eventi](Event-Reference_it) - Documentazione completa degli eventi
