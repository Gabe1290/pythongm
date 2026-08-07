# Tutorial: Creare un Gioco di Atterraggio Lunare

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Introduzione

In questo tutorial, creerai un **Gioco di Atterraggio Lunare** - un classico gioco arcade dove controlli un'astronave che scende verso una piattaforma di atterraggio. Devi gestire la spinta per contrastare la gravità e atterrare dolcemente senza schiantarti. Questo gioco è perfetto per imparare concetti fisici come gravità, spinta, velocità e gestione del carburante.

**Cosa imparerai:**
- Fisica della gravità e della spinta
- Rilevamento dell'atterraggio basato sulla velocità
- Sistema di gestione del carburante
- Controllo di rotazione o direzionale
- Zone di atterraggio sicuro

**Difficoltà:** Principiante
**Preset:** Preset Intermedio (la fisica di spinta/carburante si basa
interamente su Execute Code, non incluso nel preset Principiante)

---

## Passo 1: Capire il Gioco

### Meccaniche del Gioco
1. Il lander è attirato verso il basso dalla gravità
2. Premere SU applica spinta verso l'alto (usa carburante)
3. SINISTRA/DESTRA controlla rotazione o movimento
4. Atterra dolcemente sulla piattaforma per vincere
5. Ti schianti se atterri troppo velocemente o manchi la piattaforma
6. Senza carburante non puoi rallentare!

### Quello che ci serve

| Elemento | Scopo |
|----------|-------|
| **Lander** | L'astronave che controlli |
| **Piattaforma** | Zona sicura per atterrare |
| **Terreno** | Suolo che causa lo schianto |
| **Display Carburante** | Mostra il carburante rimanente |
| **Display Velocità** | Mostra la velocità attuale |

---

## Passo 2: Creare gli Sprite

### Sprite
- `spr_lander` (32x32 pixel) - astronave semplice
- `spr_pad` (64x16 pixel) - piattaforma di atterraggio
- `spr_ground` (32x32 pixel) - terreno roccioso
- `spr_flame` (16x16 pixel) - fiamma di propulsione (opzionale)

---

## Passo 3-4: Creare Oggetti Terreno e Piattaforma

**obj_ground** e **obj_pad**: Imposta lo sprite, seleziona "Solid"

---

## Passo 5: Creare l'Oggetto Lander

Il lander è l'oggetto principale controllato dal giocatore. A differenza
degli altri tutorial di movimento di questo wiki, i controlli del lander
devono accumulare velocità gradualmente e tenere traccia del carburante,
quindi questo oggetto fa più affidamento su **Control** → **Execute Code**
(vero Python — `self` è l'istanza corrente, `game` è il game runner,
`keyboard.check(name)` segnala se un tasto è tenuto premuto) rispetto ai
tutorial di movimento precedenti, ma usa comunque un'azione strutturata
ovunque sia possibile.

### 5.1 Gravità e Variabili Iniziali

**Event: Create**
1. Azione: **Move** → **Set Gravity** (Direction: `270`, Gravity: `0.05`)
   — una leggera trazione verso il basso; il motore la aggiunge
   automaticamente alla velocità verticale del lander ad ogni frame, come
   nel tutorial del Platform, solo più debole.
2. Azione: **Control** → **Execute Code**:

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

Il sistema di movimento di questo motore tiene già traccia della
velocità tramite `self.hspeed`/`self.vspeed` e sposta l'istanza di
quell'ammontare ad ogni frame (con collisione solida integrata) — non
serve creare variabili separate `hsp`/`vsp` come farebbe una
simulazione fisica manuale.

### 5.2 Evento Step — Spinta e Controlli

**Event: Step** — Azione: **Control** → **Execute Code**:

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

    # Impedisce al lander di uscire dai bordi o sopra la stanza
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
in modo che spinta e sterzo si fermino nell'istante in cui il gioco
termina — l'oggetto non ha un modo per interrompere un evento a metà
(nessun `exit` come in GML); un `if` attorno al resto del codice svolge
lo stesso compito.

### 5.3 Collisione con la Piattaforma

**Event: Collision with obj_pad**
1. Azione: **Control** → **Test Expression**
   - Expression: `(self.hspeed**2 + self.vspeed**2)**0.5 <= self.safe_speed`
     — la velocità di atterraggio è la lunghezza del vettore velocità
     (teorema di Pitagora), non una variabile `speed` (in questo motore
     `speed` indica la *velocità di animazione dello sprite*, non
     l'entità del movimento — una trappola reale per chi viene da
     GameMaker).
   - Then Actions:
     1. **Control** → **Set Variable** (Variable: `landed`, Value: `true`, Scope: `self`)
     2. **Move** → **Stop Movement**
     3. **Move** → **Set Gravity** (Direction: `270`, Gravity: `0`) —
        impedisce che la gravità accumuli di nuovo velocità verticale
        senza che nessuno se ne accorga su un lander già atterrato
     4. **Output** → **Show Message** (Message: `Atterraggio Perfetto! Hai Vinto!`)
   - Else Actions:
     1. **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
     2. **Output** → **Show Message** (Message: `Schianto! Troppo veloce!`)
     3. **Room** → **Restart Room**

Il testo di Show Message è una stringa fissa — non può mostrare la
velocità di atterraggio effettiva. L'HUD (Passo 7) mostra già la
velocità in tempo reale fino al momento del contatto, quindi il
giocatore ha già visto il numero.

### 5.4 Collisione con il Terreno

**Event: Collision with obj_ground**
1. Azione: **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
2. Azione: **Output** → **Show Message** (Message: `Schiantato nel terreno!`)
3. Azione: **Room** → **Restart Room**

---

## Passo 6-7: Controller del Gioco

**obj_game_controller** — Evento Draw: trova il lander tramite un ciclo
su `game.current_room.instances` (lo stesso schema del contatore monete
del tutorial del Labirinto), calcola carburante/velocità arrotondati in
un **Execute Code**, poi li mostra con **Draw Text**/**Draw Variable**;
vedi la [versione inglese](Tutorial-LunarLander) per i dettagli completi
azione per azione.

---

## Passo 8: Progetta il Tuo Livello

1. Crea `room_game` (640x480)
2. Sfondo nero (spazio)
3. Posiziona il terreno in basso con un'apertura
4. Posiziona la piattaforma nell'apertura
5. Posiziona il lander in alto
6. Posiziona il game controller

---

## Cosa Hai Imparato

- **Fisica della spinta** - Modificare `self.vspeed` contro una trazione continua di Set Gravity
- **Gestione della velocità** - Calcolare la velocità da `hspeed`/`vspeed` col teorema di Pitagora
- **Sistema carburante** - Gestione risorse con una semplice variabile d'istanza
- **Rilevamento collisioni** - Esiti diversi per piattaforma e terreno, scelti tramite Test Expression

---

## Vedi Anche

- [Tutorials](Tutorials_it) - Altri tutorial
- [Tutorial: Platformer](Tutorial-Platformer_it) - Creare un gioco platform
