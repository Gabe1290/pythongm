# Programmazione Visuale

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

[Torna alla Home](Home_it)

PyGameMaker include Google Blockly per la programmazione visuale drag-and-drop. Costruisci la logica di gioco collegando blocchi, invece di scrivere codice.

---

## Accedere a Blockly

1. Apri un oggetto nell'Editor Oggetti
2. Fai clic sulla scheda **🧩 Blockly** (accanto a Event List e Editor Codice)
3. Appare l'area di lavoro Blockly con una barra strumenti a sinistra

![Le schede Event List / Blockly / Editor Codice dell'Editor Oggetti —
cliccare su Blockly passa le azioni dello stesso evento alla vista a
blocchi drag-and-drop](images/object-editor.png)

*(L'area di lavoro Blockly stessa è un componente web e non è catturata
qui — vedi [[Code-Editor_it|Editor Codice]] per come appare il Python
generato equivalente per lo stesso evento.)*

**I blocchi visibili dipendono dal tuo preset.**
`Strumenti > Configura blocchi azione...` (oppure `Preferenze > IDE
Edition`, che imposta il preset predefinito per i nuovi progetti)
controlla l'insieme di blocchi — vedi la [Guida ai Preset](Preset-Guide_it)
per i dettagli. Le tabelle sottostanti elencano tutti i blocchi che
esistono in qualsiasi preset; un progetto concreto potrebbe mostrarne
di meno.

---

## L'Area di Lavoro Blockly

### Barra Strumenti
Il pannello sinistro contiene le categorie di blocchi:
- **Events** - Blocchi trigger per gli eventi
- **Control** - Condizioni, variabili e raggruppamento (i blocchi
  condizionali di questo progetto sono blocchi impilabili, non
  contenitori If/Else classici — vedi "Tipi di Blocco" sotto)
- **Movement** - Blocchi di movimento, velocità e fisica
- **Timing** - Allarmi
- **Drawing** - Blocchi di testo e forme
- **Score/Lives/Health** - Blocchi di stato di gioco
- **Instance** - Creazione/distruzione di oggetti
- **Room** - Navigazione tra le stanze
- **Values** - Blocchi valore (posizione, velocità, punteggio, vite,
  salute, mouse)
- **Sound** - Riproduzione audio
- **Output** - Messaggi e codice Python personalizzato
- **Game** - Termina/riavvia il gioco, classifica

Non esiste una categoria separata Math, Text o Logic — i campi
numerici/testuali si compilano direttamente su ciascun blocco, e non
esiste un blocco valore booleano/di confronto generico. Vedi "Tipi di
Blocco" sotto per come funzionano invece le condizioni.

### Area di Lavoro
La zona centrale dove costruisci il tuo programma:
- Trascinando blocchi dalla barra strumenti
- Collegando i blocchi tra loro
- Configurando i parametri dei blocchi

### Cestino
Trascina qui i blocchi indesiderati per eliminarli, oppure premi il tasto Canc.

---

## Tipi di Blocco

### Blocchi a Cappello (Events)
I blocchi a cappello hanno una parte superiore arrotondata e avviano una sequenza. Rappresentano gli eventi:

```
┌─────────────────┐
│ When Create     │
└─────────────────┘
```

### Blocchi Impilabili (Azioni)
I blocchi impilabili hanno delle tacche che si connettono con altri
blocchi. Quasi tutti i blocchi al di fuori della categoria Values sono
blocchi impilabili — inclusi i blocchi condizionali:

```
├─────────────────┤
│ Set Horizontal Speed [5] │
├─────────────────┤
```

### Blocchi Valore (Values)
I blocchi valore sono arrotondati e si inseriscono in un campo numerico
di un altro blocco (ad es. il campo velocità di Move Direction, o il
campo valore di Set Variable). Questo progetto ne ha 9 — X Position, Y
Position, Horizontal Speed, Vertical Speed, Score, Lives, Health, Mouse
X, Mouse Y:

```
( X Position )    ( Score )    ( 100 )
```

Non esiste un blocco valore generico `( speed )` o `( direction )` —
questi concetti non vengono tracciati come valore singolo in questo
motore (la velocità/direzione di movimento derivano insieme da
Horizontal Speed + Vertical Speed), e non esiste nemmeno un blocco
valore per le variabili personalizzate (leggile invece tramite il
confronto di Test Variable).

### Condizioni — blocchi impilabili, non contenitori a C
A differenza dei linguaggi visuali in stile Scratch, i blocchi If
Condition / Test Variable di questo progetto sono **blocchi impilabili
con un singolo slot "then"**, non contenitori If/Else a due lati, e non
esiste un blocco esagonale booleano da inserire — il confronto si
costruisce direttamente tramite campi sul blocco:

```
┌───────────────────────────────────┐
│ If count of [obj_coin] [==] [0]   │
├───────────────────────────────────┤
│  then [azioni qui]                │
└───────────────────────────────────┘
```

Per aggiungere un ramo "else" o eseguire più azioni da un lato, combinalo
con altri tre blocchi Control:
- **Else** - esegue il proprio blocco successivo solo se il test
  precedente era falso
- **Start Block** / **End Block** - raggruppano più azioni, così il test
  precedente (o Else) agisce sull'intero gruppo, non solo sul blocco
  successivo

Questo è lo stesso flusso condizionale piatto, in stile GM80, usato
anche dal pannello strutturato Events/Actions (vedi [Eventi e
Azioni](Eventi_e_Azioni_it)) — Blockly è un'interfaccia drag-and-drop
sopra la stessa lista di azioni sottostante, non un modello di
esecuzione separato.

---

## Blocchi Evento

### Evento Create
```
┌─────────────────────┐
│ When Create         │
├─────────────────────┤
│ [azioni qui]         │
└─────────────────────┘
```

### Evento Step
```
┌─────────────────────┐
│ When Step            │
├─────────────────────┤
│ [ogni frame]          │
└─────────────────────┘
```

### Eventi Tastiera
Esistono quattro blocchi a cappello separati per la tastiera — Held,
Press, Release e No Key — ciascuno con un menu a tendina per il nome
del tasto (No Key non ne ha, perché si attiva quando nulla è tenuto
premuto):
```
┌─────────────────────────┐
│ When key [held: left] ▼ │
├─────────────────────────┤
│ [azioni qui]              │
└─────────────────────────┘
```

### Eventi di Collisione
```
┌────────────────────────────┐
│ When colliding with [obj] ▼│
├────────────────────────────┤
│ [azioni qui]                 │
└────────────────────────────┘
```

---

## Blocchi di Movimento

| Blocco | Descrizione |
|------|-------------|
| `Set Horizontal Speed [4]` | Imposta la velocità X |
| `Set Vertical Speed [-5]` | Imposta la velocità Y |
| `Stop Movement` | Azzera entrambe le velocità |
| `Move [direction ▼] speed [3]` | Muove in una di 4 direzioni (o diagonali, o "stop") |
| `Move Free [direction] [speed]` | Muove con angolo e velocità arbitrari |
| `Set Speed [5]` | Imposta l'entità della velocità, mantenendo la direzione attuale |
| `Set Direction [90]` | Imposta l'angolo di direzione, mantenendo la velocità attuale |
| `Move Towards x:[100] y:[200] speed:[3]` | Muove verso un punto |
| `Snap to Grid` | Allinea la posizione alla griglia |
| `Jump to Position x:[100] y:[200]` | Teletrasporto istantaneo |
| `Move Grid [direction]` | Muove esattamente di una cella della griglia |
| `Stop if No Keys` / `Check Keys and Move` / `If On Grid` | Blocchi ausiliari per il movimento a griglia |
| `Set Gravity` | Applica una forza costante ad ogni frame (verso il basso o in qualsiasi direzione) |
| `Set Friction` | Applica un decadimento della velocità ad ogni frame |
| `Reverse Horizontal` / `Reverse Vertical` | Inverte la direzione X o Y |
| `Bounce` | Rimbalza dagli oggetti solidi |
| `Wrap Around Room` | Riappare dal lato opposto |
| `Move to Contact` | Si muove finché non tocca qualcosa |

Non esiste un blocco "Jump to Start Position" o "Jump to Random
Position" — queste due azioni esistono solo nel pannello strutturato,
non in Blockly.

---

## Blocchi di Disegno

| Blocco | Descrizione |
|------|-------------|
| `Draw Text [Ciao] at x:[10] y:[10]` | Mostra testo |
| `Draw Rectangle from x1,y1 to x2,y2` | Disegna un rettangolo pieno |
| `Draw Circle at x,y radius [r]` | Disegna un cerchio pieno |
| `Set Sprite [spr]` | Cambia lo sprite dell'istanza |
| `Set Transparency [0-1]` | Imposta l'alpha |

Non esiste un blocco "Draw Sprite a Posizione" o "Set Drawing Color" in
Blockly (entrambi esistono solo nel pannello strutturato). Draw
Score/Draw Lives/Draw Health Bar sono elencati sotto in Score/Lives/
Health, non qui.

---

## Blocchi Score/Lives/Health

| Blocco | Descrizione |
|------|-------------|
| `Set Score [100]` | Imposta esattamente il punteggio |
| `Add to Score [10]` | Aumenta/diminuisce il punteggio |
| `Set Lives [3]` | Imposta esattamente le vite |
| `Add to Lives [-1]` | Aumenta/diminuisce le vite |
| `Set Health [100]` | Imposta esattamente la salute |
| `Add to Health [-25]` | Aumenta/diminuisce la salute |
| `Draw Score` | Mostra il testo del punteggio |
| `Draw Lives` | Mostra le vite come icone ripetute |
| `Draw Health Bar` | Mostra la salute come barra a due colori |

---

## Blocchi Istanza

| Blocco | Descrizione |
|------|-------------|
| `Create Instance [obj] at x:[100] y:[200]` | Crea una nuova istanza |
| `Destroy Instance` | Rimuove se stessa |
| `Destroy Other` | Rimuove l'istanza in collisione (in un evento Collision) |
| `Change Instance [obj]` | Si trasforma in un altro tipo di oggetto |
| `If Can Push [obj] [direction]` | Controllo di spinta in stile Sokoban |

Non esiste un blocco "distruggi tutti di un tipo" o "crea a questa posizione".

---

## Blocchi Room

| Blocco | Descrizione |
|------|-------------|
| `Next Room` | Passa alla stanza successiva |
| `Previous Room` | Torna alla stanza precedente |
| `Restart Room` | Riavvia la stanza attuale |
| `Go to Room [room_name]` | Salta a una stanza specifica |
| `If Next Room Exists` / `If Previous Room Exists` | Protegge la navigazione tra più stanze |

---

## Blocchi Sound

| Blocco | Descrizione |
|------|-------------|
| `Play Sound [snd]` | Riproduce un effetto sonoro |
| `Play Music [music]` | Riproduce musica di sottofondo (in loop) |
| `Stop Music` | Ferma la musica |

Non esiste un blocco "Stop Sound" (per singolo suono) o "Ferma tutti i
suoni" in Blockly (solo Stop Music, che ferma specificamente la musica).

---

## Blocchi Control

| Blocco | Descrizione |
|------|-------------|
| `If count of [obj] [==] [0] then...` | Confronta il numero di istanze di un oggetto; esegue il blocco/i blocchi successivi se vero |
| `If variable [var] [==] [value] then...` | Confronta una variabile personalizzata; esegue il blocco/i blocchi successivi se vero |
| `Set Variable [name] to [value]` | Assegna una variabile d'istanza o globale |
| `Check Empty at x,y` | Vero se una posizione non ha collisioni (movimento a griglia) |
| `Exit Event` | Ferma le azioni rimanenti di questo evento |
| `Else` | Esegue il proprio blocco successivo se il test precedente era falso |
| `Start Block` / `End Block` | Raggruppa più azioni sotto un Test/Else |

---

## Blocchi Output e Game

| Blocco | Descrizione |
|------|-------------|
| `Show Message [text]` | Mostra un messaggio popup |
| `Execute Code` | Esegue vero Python (vedi [Eventi e Azioni](Eventi_e_Azioni_it)) |
| `End Game` | Chiude il gioco |
| `Restart Game` | Riavvia dalla prima stanza |
| `Show Highscore` / `Clear Highscore` | Mostra o azzera la classifica |

---

## Blocchi Valore

Blocchi valore — inseriscili in un campo numerico di un altro blocco:

| Blocco | Descrizione |
|------|-------------|
| `X Position` | La coordinata X di questa istanza |
| `Y Position` | La coordinata Y di questa istanza |
| `Horizontal Speed` | La velocità X di questa istanza |
| `Vertical Speed` | La velocità Y di questa istanza |
| `Score` | Il punteggio attuale |
| `Lives` | Le vite attuali |
| `Health` | La salute attuale |
| `Mouse X` / `Mouse Y` | La posizione attuale del mouse |

---

## Esempio: Movimento del Giocatore

```
┌──────────────────────────┐
│ When key [held: left]    │
├──────────────────────────┤
│ Set Horizontal Speed [-4]│
└──────────────────────────┘

┌──────────────────────────┐
│ When key [held: right]   │
├──────────────────────────┤
│ Set Horizontal Speed [4] │
└──────────────────────────┘

┌──────────────────────────┐
│ When key [no key]        │
├──────────────────────────┤
│ Set Horizontal Speed [0] │
└──────────────────────────┘
```

---

## Esempio: Raccogliere Monete

```
┌─────────────────────────────┐
│ When colliding with obj_coin│
├─────────────────────────────┤
│ Add to Score [10]           │
├─────────────────────────────┤
│ Play Sound [snd_coin]       │
├─────────────────────────────┤
│ Destroy Other                │
└─────────────────────────────┘
```

---

## Suggerimenti

1. **Inizia con gli Events** - Parti sempre con un blocco Event (blocco a cappello)
2. **Connetti verticalmente** - I blocchi impilabili si collegano dall'alto verso il basso
3. **Usa i colori** - I colori dei blocchi indicano la loro categoria
4. **Clic destro** - Accedi a Duplica, Elimina e Aiuto
5. **Zoom** - Usa la rotella del mouse o i controlli di zoom per programmi grandi
6. **Passa al pannello strutturato** - Tutto ciò che Blockly può fare
   corrisponde a un'azione nella scheda Events del pannello strutturato,
   ma non il contrario (ad es. Jump to Start/Random Position e Stop
   Sound per singolo suono non hanno un blocco Blockly) — in questi casi
   usa il pannello strutturato invece di Blockly.

---

## Prossimi Passi

- [[Eventi_e_Azioni_it]] - Vedi l'equivalente come lista di azioni
- [[Primo_Gioco_it]] - Costruisci un gioco completo
- [[Editor_Oggetti_it]] - Dove è integrato Blockly
- [[Preset-Guide_it]] - Quali blocchi sono disponibili nel tuo progetto
