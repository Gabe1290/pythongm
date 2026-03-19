# Manuale Utente di PyGameMaker IDE

**Versione 1.0.0-rc.6**
**Un IDE di sviluppo giochi visuale ispirato a GameMaker per creare giochi 2D con Python**

---

## Indice

1. [Introduzione](#1-introduzione)
2. [Installazione e Configurazione](#2-installazione-e-configurazione)
3. [Panoramica dell'IDE](#3-panoramica-dellide)
4. [Lavorare con i Progetti](#4-lavorare-con-i-progetti)
5. [Sprite](#5-sprite)
6. [Suoni](#6-suoni)
7. [Sfondi](#7-sfondi)
8. [Oggetti](#8-oggetti)
9. [Stanze](#9-stanze)
10. [Riferimento Eventi](#10-riferimento-eventi)
11. [Riferimento Azioni](#11-riferimento-azioni)
12. [Test ed Esecuzione dei Giochi](#12-test-ed-esecuzione-dei-giochi)
13. [Esportazione dei Giochi](#13-esportazione-dei-giochi)
14. [Programmazione Visuale con Blockly](#14-programmazione-visuale-con-blockly)
15. [Supporto Robot Thymio](#15-supporto-robot-thymio)
16. [Impostazioni e Preferenze](#16-impostazioni-e-preferenze)
17. [Scorciatoie da Tastiera](#17-scorciatoie-da-tastiera)
18. [Tutorial](#18-tutorial)
19. [Risoluzione dei Problemi](#19-risoluzione-dei-problemi)

---

## 1. Introduzione

PyGameMaker e un IDE educativo per lo sviluppo di giochi ispirato a GameMaker. Permette di creare giochi 2D in modo visuale utilizzando un sistema di eventi/azioni con trascinamento, senza bisogno di scrivere codice. E stato progettato con due obiettivi:

- **Insegnare lo sviluppo di giochi** in modo visuale attraverso un'interfaccia intuitiva
- **Insegnare la programmazione Python** attraverso il codice sorgente aperto dell'IDE

PyGameMaker utilizza PySide6 (Qt) per l'interfaccia dell'IDE e Pygame per il motore di gioco. I giochi possono essere esportati come eseguibili autonomi, app per dispositivi mobili o giochi web HTML5.

### Caratteristiche Principali

- Programmazione visuale con eventi/azioni (oltre 80 azioni integrate)
- Editor di sprite con supporto animazioni
- Editor di stanze con posizionamento delle istanze, livelli di tile e scorrimento degli sfondi
- Anteprima del gioco in tempo reale con F5
- Esportazione per Windows EXE, dispositivi mobili (Android/iOS tramite Kivy), HTML5 e robot Thymio
- Integrazione con Google Blockly per blocchi di codice visuali
- Simulatore del robot educativo Thymio
- Interfaccia multilingua (oltre 8 lingue)
- Temi scuro e chiaro

---

## 2. Installazione e Configurazione

### Requisiti

- Python 3.10 o superiore
- PySide6
- Pygame
- Pillow (PIL)

### Installazione delle Dipendenze

```bash
pip install PySide6 pygame Pillow
```

### Dipendenze Opzionali

Per le funzionalita di esportazione:

```bash
pip install pyinstaller    # Per esportazione EXE
pip install kivy           # Per esportazione mobile
pip install buildozer      # Per build Android
pip install jinja2         # Per template di generazione codice
```

### Avvio dell'IDE

```bash
python main.py
```

La finestra dell'IDE si apre con dimensioni predefinite di 1400x900 pixel. La posizione e la dimensione della finestra vengono salvate tra le sessioni.

---

## 3. Panoramica dell'IDE

### Disposizione della Finestra

L'IDE utilizza una disposizione a tre pannelli:

```
+-------------------+---------------------------+------------------+
|   Albero Risorse  |      Area Editor          |   Proprietà      |
|   (Pannello Sin.) |      (Pannello Centr.)    |   (Pannello Dx)  |
|                   |                           |                  |
|   - Sprite        |   Editor a schede per     |   Proprietà      |
|   - Suoni         |   sprite, oggetti         |   contestuali    |
|   - Sfondi        |   e stanze                |                  |
|   - Oggetti       |                           |                  |
|   - Stanze        |                           |                  |
|   - Script        |                           |                  |
|   - Font          |                           |                  |
+-------------------+---------------------------+------------------+
|                       Barra di Stato                             |
+------------------------------------------------------------------+
```

- **Pannello Sinistro (Albero Risorse):** Mostra tutte le risorse del progetto organizzate per tipo. Doppio clic su una risorsa per aprirla nell'editor.
- **Pannello Centrale (Area Editor):** Spazio di lavoro a schede dove si modificano sprite, oggetti e stanze. Una scheda di benvenuto e mostrata per impostazione predefinita.
- **Pannello Destro (Proprieta):** Mostra le proprieta contestuali per l'editor attivo corrente. Puo essere compresso.
- **Barra di Stato:** Mostra lo stato dell'operazione corrente e il nome del progetto.

### Barra dei Menu

#### Menu File

| Comando | Scorciatoia | Descrizione |
|---------|-------------|-------------|
| New Project... | Ctrl+N | Crea un nuovo progetto |
| Open Project... | Ctrl+O | Apri un progetto esistente |
| Save Project | Ctrl+S | Salva il progetto corrente |
| Save Project As... | Ctrl+Shift+S | Salva in una nuova posizione |
| Recent Projects | | Sottomenu con fino a 10 progetti recenti |
| Export as HTML5... | | Esporta il gioco come singolo file HTML |
| Export as Zip... | | Impacchetta il progetto come archivio ZIP |
| Export to Kivy... | | Esporta per distribuzione mobile |
| Export Project... | Ctrl+E | Apri la finestra di esportazione |
| Open Zip Project... | | Apri un progetto impacchettato in ZIP |
| Auto-Save to Zip | | Attiva/disattiva il salvataggio automatico in ZIP |
| Enable Auto-Save | | Attiva/disattiva il salvataggio automatico del progetto |
| Auto-Save Settings... | | Configura l'intervallo di salvataggio automatico |
| Project Settings... | | Apri la configurazione del progetto |
| Exit | Ctrl+Q | Chiudi l'IDE |

#### Menu Edit

| Comando | Scorciatoia | Descrizione |
|---------|-------------|-------------|
| Undo | Ctrl+Z | Annulla l'ultima azione |
| Redo | Ctrl+Y | Ripristina l'ultima azione annullata |
| Cut | Ctrl+X | Taglia la selezione |
| Copy | Ctrl+C | Copia la selezione |
| Paste | Ctrl+V | Incolla dagli appunti |
| Duplicate | Ctrl+D | Duplica gli elementi selezionati |
| Find... | Ctrl+F | Apri la finestra di ricerca |
| Find and Replace... | Ctrl+H | Apri la finestra di ricerca e sostituzione |

#### Menu Assets

| Comando | Descrizione |
|---------|-------------|
| Import Sprite... | Importa immagini sprite (PNG, JPG, BMP, GIF) |
| Import Sound... | Importa file audio |
| Import Background... | Importa immagini di sfondo |
| Create Object... | Crea un nuovo oggetto di gioco |
| Create Room... (Ctrl+R) | Crea una nuova stanza di gioco |
| Create Script... | Crea un nuovo file script |
| Create Font... | Crea una nuova risorsa font |
| Import Object Package... | Importa un pacchetto .gmobj |
| Import Room Package... | Importa un pacchetto .gmroom |

#### Menu Build

| Comando | Scorciatoia | Descrizione |
|---------|-------------|-------------|
| Test Game | F5 | Esegui il gioco in modalita test |
| Debug Game | F6 | Esegui il gioco con output di debug |
| Build Game... | F7 | Apri la configurazione di compilazione |
| Build and Run | F8 | Compila ed esegui immediatamente |
| Export Game... | | Esporta il gioco compilato |

#### Menu Tools

| Comando | Descrizione |
|---------|-------------|
| Preferences... | Apri le preferenze dell'IDE |
| Asset Manager... | Apri il gestore delle risorse |
| Configure Action Blocks... | Configura i blocchi Blockly |
| Configure Thymio Blocks... | Configura i blocchi del robot Thymio |
| Validate Project | Controlla il progetto per errori |
| Clean Project | Rimuovi i file temporanei |
| Migrate to Modular Structure | Aggiorna il formato del progetto |
| Language | Cambia la lingua dell'interfaccia |
| Thymio Programming | Sottomenu programmazione robot |

#### Menu Help

| Comando | Scorciatoia | Descrizione |
|---------|-------------|-------------|
| Documentation | F1 | Apri la documentazione |
| Tutorials | | Apri le risorse dei tutorial |
| About PyGameMaker | | Informazioni su versione e licenza |

### Barra degli Strumenti

La barra degli strumenti fornisce accesso rapido alle azioni comuni (da sinistra a destra):

| Pulsante | Azione |
|----------|--------|
| New | Crea nuovo progetto |
| Open | Apri progetto esistente |
| Save | Salva progetto corrente |
| Test | Esegui gioco (F5) |
| Debug | Debug gioco (F6) |
| Export | Esporta gioco |
| Import Sprite | Importa un'immagine sprite |
| Import Sound | Importa un file audio |
| Thymio | Aggiungi evento robot Thymio |

### Albero Risorse

L'albero delle risorse nel pannello sinistro organizza le risorse del progetto in categorie:

**Risorse Multimediali:**
- **Sprite** - Immagini e strisce di animazione per gli oggetti di gioco
- **Suoni** - Effetti sonori e file musicali
- **Sfondi** - Immagini di sfondo e set di tile

**Logica di Gioco:**
- **Oggetti** - Definizioni degli oggetti di gioco con eventi e azioni
- **Stanze** - Livelli/scene del gioco con istanze posizionate

**Risorse di Codice:**
- **Script** - File di codice
- **Font** - Risorse di font personalizzati

**Operazioni del menu contestuale:**
- Clic destro su un'intestazione di categoria per creare o importare risorse
- Clic destro su una risorsa per rinominare, eliminare, esportare o visualizzare le proprieta
- Doppio clic su una risorsa per aprirla nell'editor
- Le risorse stanza possono essere riordinate (Sposta Su/Giu/In Cima/In Fondo)

---

## 4. Lavorare con i Progetti

### Creazione di un Nuovo Progetto

1. Scegli **File > New Project** (Ctrl+N)
2. Inserisci un **Nome Progetto**
3. Scegli una **Posizione** per la cartella del progetto
4. Seleziona un **Modello** (opzionale):
   - **Progetto Vuoto** - Un progetto vuoto
   - **Modello Gioco Platform** - Preconfigurato per giochi a piattaforme
   - **Modello Gioco Dall'Alto** - Preconfigurato per giochi con vista dall'alto
5. Clicca **Crea Progetto**

### Struttura del Progetto

```
MyProject/
├── project.json          # File principale del progetto
├── sprites/              # Immagini e metadati degli sprite
│   ├── player.png
│   └── player.json
├── objects/              # Definizioni degli oggetti
│   └── obj_player.json
├── rooms/                # Dati di disposizione delle stanze
│   └── room_start.json
├── sounds/               # File audio e metadati
├── backgrounds/          # Immagini di sfondo
└── thumbnails/           # Anteprime generate automaticamente
```

### Salvataggio dei Progetti

- **Ctrl+S** salva il progetto nella posizione corrente
- **Ctrl+Shift+S** salva in una nuova posizione
- Il **salvataggio automatico** puo essere attivato in File > Enable Auto-Save
- Configura l'intervallo di salvataggio automatico in File > Auto-Save Settings

### Apertura dei Progetti

- **Ctrl+O** apre una cartella di progetto
- I progetti recenti sono elencati in **File > Recent Projects**
- I progetti ZIP possono essere aperti con **File > Open Zip Project**

---

## 5. Sprite

Gli sprite sono le immagini visuali utilizzate dagli oggetti di gioco. Possono essere immagini statiche o strisce di animazione con piu fotogrammi.

### Creazione di uno Sprite

1. Clic destro su **Sprites** nell'albero delle risorse e scegli **Import Sprite...**
2. Seleziona un file immagine (PNG, JPG, BMP o GIF)
3. Lo sprite appare nell'albero delle risorse e si apre nell'editor di sprite

### Editor di Sprite

L'editor di sprite ha quattro aree principali:

- **Pannello Strumenti (Sinistra):** Strumenti di disegno
- **Tela (Centro):** L'area di modifica con zoom e griglia
- **Tavolozza Colori (Destra):** Colori primo piano/sfondo e campioni
- **Linea Temporale dei Fotogrammi (Basso):** Gestione dei fotogrammi di animazione

#### Strumenti di Disegno

| Strumento | Scorciatoia | Descrizione |
|-----------|-------------|-------------|
| Pencil | P | Disegno standard pixel per pixel |
| Eraser | E | Rimuovi pixel (rendi trasparente) |
| Color Picker | I | Campiona un colore dalla tela |
| Fill | G | Riempimento a inondazione di regioni connesse |
| Line | L | Disegna linee rette |
| Rectangle | R | Disegna rettangoli (contorno o riempito) |
| Ellipse | O | Disegna ellissi (contorno o riempito) |
| Selection | S | Seleziona, taglia, copia, incolla regioni |

#### Dimensione del Pennello

La dimensione del pennello varia da 1 a 16 pixel e influisce sugli strumenti Pencil, Eraser e Line.

#### Modalita Riempimento

Alterna tra modalita contorno e riempimento per gli strumenti Rectangle ed Ellipse usando il pulsante **Filled**.

#### Tavolozza Colori

- **Clic sinistro** sul campione del primo piano per scegliere un colore di disegno
- **Clic destro** sul campione dello sfondo per scegliere un colore secondario
- **Pulsante X** scambia i colori primo piano e sfondo
- Clicca su qualsiasi colore nella tavolozza rapida per selezionarlo
- Doppio clic su un campione della tavolozza per personalizzarlo
- Selettore colori RGBA completo con supporto alfa (trasparenza)

### Fotogrammi di Animazione

Gli sprite possono avere piu fotogrammi di animazione disposti come una striscia orizzontale.

**Controlli della Linea Temporale:**
- **+ (Aggiungi):** Aggiungi un nuovo fotogramma vuoto
- **D (Duplica):** Copia il fotogramma corrente
- **- (Elimina):** Rimuovi il fotogramma corrente (minimo 1 fotogramma)
- **Play/Stop:** Anteprima dell'animazione
- Il contatore dei fotogrammi mostra fotogramma corrente/totale

**Proprieta dell'Animazione:**
- **Conteggio Fotogrammi:** Numero di fotogrammi dell'animazione
- **Velocita dell'Animazione:** Fotogrammi al secondo (predefinito: 10 FPS)
- **Tipo di Animazione:** single, strip_h (orizzontale), strip_v (verticale), o grid

**Supporto GIF Animate:** Importa direttamente file GIF animati. Tutti i fotogrammi vengono estratti automaticamente con gestione della trasparenza.

### Origine dello Sprite

Il punto di origine e la posizione di ancoraggio utilizzata per il posizionamento e la rotazione nel gioco.

**Posizioni Preimpostate:**
- In Alto a Sinistra (0, 0)
- In Alto al Centro
- Centro (predefinito per la maggior parte degli sprite)
- Centro in Basso
- In Basso a Sinistra
- In Basso a Destra
- Personalizzato (inserimento manuale X/Y)

L'origine e mostrata come un mirino sulla tela.

### Controlli della Tela

- **Ctrl+Rotella del Mouse:** Zoom avanti/indietro (da 1x a 64x)
- **Attiva/Disattiva Griglia:** Mostra/nascondi la griglia dei pixel (visibile a zoom 4x e superiore)
- **Specchia O/V:** Capovolgi il fotogramma corrente orizzontalmente o verticalmente
- **Ridimensiona/Scala:** Modifica le dimensioni dello sprite con opzioni di scala o ridimensionamento della tela

### Proprieta dello Sprite (Salvate)

| Proprieta | Descrizione |
|-----------|-------------|
| name | Nome della risorsa |
| file_path | Percorso del file PNG della striscia |
| width | Larghezza totale della striscia |
| height | Altezza del fotogramma |
| frame_width | Larghezza di un singolo fotogramma |
| frame_height | Altezza di un singolo fotogramma |
| frames | Numero di fotogrammi |
| animation_type | single, strip_h, strip_v, grid |
| speed | FPS dell'animazione |
| origin_x | Coordinata X dell'origine |
| origin_y | Coordinata Y dell'origine |

---

## 6. Suoni

I suoni sono file audio utilizzati per effetti sonori e musica di sottofondo.

### Importazione dei Suoni

1. Clic destro su **Sounds** nell'albero delle risorse e scegli **Import Sound...**
2. Seleziona un file audio (WAV, OGG, MP3)
3. Il suono viene aggiunto al progetto

### Proprieta del Suono

| Proprieta | Descrizione |
|-----------|-------------|
| name | Nome della risorsa suono |
| file_path | Percorso del file audio |
| kind | "sound" (effetto) o "music" (streaming) |
| volume | Volume predefinito (da 0.0 a 1.0) |

Gli **effetti sonori** vengono caricati in memoria per la riproduzione istantanea. I file **musicali** vengono trasmessi in streaming dal disco e solo uno puo essere riprodotto alla volta.

---

## 7. Sfondi

Gli sfondi sono immagini utilizzate dietro gli oggetti di gioco. Possono anche servire come set di tile per livelli basati su tile.

### Importazione degli Sfondi

1. Clic destro su **Backgrounds** nell'albero delle risorse e scegli **Import Background...**
2. Seleziona un file immagine

### Configurazione del Set di Tile

Gli sfondi possono essere configurati come set di tile con queste proprieta:

| Proprieta | Descrizione |
|-----------|-------------|
| tile_width | Larghezza di ogni tile (predefinito: 16) |
| tile_height | Altezza di ogni tile (predefinito: 16) |
| h_offset | Offset orizzontale al primo tile |
| v_offset | Offset verticale al primo tile |
| h_sep | Spaziatura orizzontale tra i tile |
| v_sep | Spaziatura verticale tra i tile |
| use_as_tileset | Attiva la modalita set di tile |

---

## 8. Oggetti

Gli oggetti definiscono le entita di gioco con proprieta, eventi e azioni. Ogni oggetto puo avere uno sprite per la rappresentazione visiva e contiene gestori di eventi che definiscono il suo comportamento.

### Creazione di un Oggetto

1. Clic destro su **Objects** nell'albero delle risorse e scegli **Create Object...**
2. Inserisci un nome per l'oggetto
3. L'oggetto si apre nell'editor di oggetti

### Proprieta dell'Oggetto

| Proprieta | Predefinito | Descrizione |
|-----------|-------------|-------------|
| Sprite | Nessuno | Lo sprite visuale da visualizzare |
| Visible | Si | Se le istanze vengono disegnate |
| Solid | No | Se l'oggetto blocca il movimento |
| Persistent | No | Se le istanze sopravvivono ai cambi di stanza |
| Depth | 0 | Ordine di disegno (piu alto = dietro, piu basso = davanti) |
| Parent | Nessuno | Oggetto genitore per l'ereditarieta |

### Oggetti Genitore

Gli oggetti possono ereditare da un oggetto genitore. Gli oggetti figli ricevono tutti gli eventi di collisione del genitore. Questo e utile per creare gerarchie come:

```
obj_enemy (genitore - ha collisione con obj_player)
  ├── obj_enemy_melee (eredita la gestione delle collisioni)
  └── obj_enemy_ranged (eredita la gestione delle collisioni)
```

### Aggiunta di Eventi

1. Apri l'editor di oggetti
2. Clicca **Add Event** nel pannello eventi
3. Seleziona un tipo di evento dalla lista (vedi [Riferimento Eventi](#10-riferimento-eventi))
4. L'evento appare nell'albero degli eventi

### Aggiunta di Azioni agli Eventi

1. Seleziona un evento nell'albero degli eventi
2. Clicca **Add Action** o clic destro e scegli **Add Action**
3. Scegli un tipo di azione dalla lista categorizzata
4. Configura i parametri dell'azione nella finestra di dialogo
5. Clicca OK per aggiungere l'azione

Le azioni vengono eseguite in ordine dall'alto verso il basso quando l'evento si attiva.

### Logica Condizionale

Le azioni supportano il flusso condizionale if/else:

1. Aggiungi un'azione condizionale (es. **If Collision At**, **Test Variable**)
2. Aggiungi un'azione **Start Block** (parentesi graffa aperta)
3. Aggiungi le azioni che si eseguono quando la condizione e vera
4. Aggiungi un'azione **Else** (opzionale)
5. Aggiungi un **Start Block** per il ramo else
6. Aggiungi le azioni per il caso falso
7. Aggiungi le azioni **End Block** per chiudere ogni blocco

Esempio di sequenza di azioni:
```
If Collision At (self.x, self.y + 1, "solid")
  Start Block
    Set Vertical Speed (0)
  End Block
Else
  Start Block
    Set Vertical Speed (vspeed + 0.5)
  End Block
```

### Visualizza Codice

Seleziona l'opzione **View Code** nell'editor di oggetti per vedere il codice Python generato per tutti gli eventi e le azioni. Questo e utile per capire come le azioni visuali vengono tradotte in codice.

---

## 9. Stanze

Le stanze sono le scene o i livelli del tuo gioco. Ogni stanza ha uno sfondo, istanze di oggetti posizionate e livelli di tile opzionali.

### Creazione di una Stanza

1. Clic destro su **Rooms** nell'albero delle risorse e scegli **Create Room...**
2. Inserisci un nome per la stanza
3. La stanza si apre nell'editor di stanze

### Proprieta della Stanza

| Proprieta | Predefinito | Descrizione |
|-----------|-------------|-------------|
| Width | 1024 | Larghezza della stanza in pixel |
| Height | 768 | Altezza della stanza in pixel |
| Background Color | #87CEEB (azzurro cielo) | Colore di riempimento dietro tutto |
| Background Image | Nessuno | Immagine di sfondo opzionale |
| Persistent | No | Preserva lo stato quando si esce |

### Posizionamento delle Istanze

1. Clicca un oggetto nella **Tavolozza Oggetti** (lato sinistro dell'editor di stanze)
2. Clicca nella tela della stanza per posizionare un'istanza
3. Continua a cliccare per posizionare piu copie
4. Seleziona le istanze posizionate per spostarle o configurarle

### Proprieta dell'Istanza

Quando selezioni un'istanza posizionata:

| Proprieta | Intervallo | Descrizione |
|-----------|-----------|-------------|
| X Position | 0-9999 | Posizione orizzontale |
| Y Position | 0-9999 | Posizione verticale |
| Visible | Si/No | Visibilita dell'istanza |
| Rotation | 0-360 | Rotazione in gradi |
| Scale X | 10%-1000% | Scala orizzontale |
| Scale Y | 10%-1000% | Scala verticale |

### Griglia e Agganciamento

- **Attiva/Disattiva Griglia:** Clicca il pulsante griglia per mostrare/nascondere la griglia di posizionamento
- **Attiva/Disattiva Agganciamento:** Clicca il pulsante agganciamento per attivare/disattivare l'agganciamento alla griglia
- **Dimensione Griglia:** 32x32 pixel per impostazione predefinita (configurabile nelle Preferenze)

### Operazioni sulle Istanze

| Azione | Scorciatoia | Descrizione |
|--------|-------------|-------------|
| Sposta | Trascinamento | Sposta l'istanza in una nuova posizione |
| Selezione Multipla | Shift+Clic | Aggiungi/rimuovi dalla selezione |
| Selezione a Rettangolo | Trascinamento area vuota | Seleziona tutte le istanze nel rettangolo |
| Elimina | Delete | Rimuovi le istanze selezionate |
| Taglia | Ctrl+X | Taglia negli appunti |
| Copia | Ctrl+C | Copia negli appunti |
| Incolla | Ctrl+V | Incolla dagli appunti |
| Duplica | Ctrl+D | Duplica le istanze selezionate |
| Pulisci Tutto | Pulsante barra strumenti | Rimuovi tutte le istanze (con conferma) |

### Livelli di Sfondo

Le stanze supportano fino a 8 livelli di sfondo (indicizzati 0-7), ciascuno con impostazioni indipendenti:

| Proprieta | Descrizione |
|-----------|-------------|
| Background Image | Quale risorsa sfondo utilizzare |
| Visible | Mostra/nascondi il livello |
| Foreground | Se vero, disegnato davanti alle istanze |
| Tile Horizontal | Ripeti su tutta la larghezza della stanza |
| Tile Vertical | Ripeti su tutta l'altezza della stanza |
| H Scroll Speed | Pixel di scorrimento orizzontale per fotogramma |
| V Scroll Speed | Pixel di scorrimento verticale per fotogramma |
| Stretch | Scala per riempire l'intera stanza |
| X / Y Offset | Offset di posizione del livello |

### Livelli di Tile

Per livelli basati su tile:

1. Clicca **Tile Palette...** per aprire il selettore di tile
2. Scegli un set di tile (sfondo marcato come set di tile)
3. Imposta larghezza e altezza del tile
4. Clicca un tile nella tavolozza per selezionarlo
5. Clicca nella stanza per posizionare i tile
6. Seleziona un **Livello** (0-7) per i tile

### Ordinamento delle Stanze

Le stanze vengono eseguite nell'ordine in cui appaiono nell'albero delle risorse. La prima stanza e la stanza iniziale.

- Clic destro su una stanza e usa **Move Up/Down/Top/Bottom** per riordinare
- Usa le azioni **Next Room** e **Previous Room** per navigare tra le stanze durante l'esecuzione

### Sistema di Viste

Le stanze supportano fino a 8 viste telecamera (come in GameMaker):

| Proprieta | Descrizione |
|-----------|-------------|
| Visible | Attiva/disattiva questa vista |
| View X/Y | Posizione della telecamera nella stanza |
| View W/H | Dimensione del viewport della telecamera |
| Port X/Y | Posizione sullo schermo per questa vista |
| Port W/H | Dimensione sullo schermo per questa vista |
| Follow Object | Oggetto da seguire con la telecamera |
| H/V Border | Margine di scorrimento attorno all'oggetto seguito |
| H/V Speed | Velocita massima di scorrimento della telecamera (-1 = istantaneo) |

---

## 10. Riferimento Eventi

Gli eventi definiscono quando le azioni vengono eseguite. Ogni evento si attiva in condizioni specifiche.

### Eventi dell'Oggetto

| Evento | Categoria | Si Attiva Quando |
|--------|-----------|------------------|
| Create | Object | L'istanza viene creata per la prima volta |
| Destroy | Object | L'istanza viene distrutta |
| Step | Step | Ogni fotogramma del gioco (~60 FPS) |
| Begin Step | Step | Inizio di ogni fotogramma, prima della fisica |
| End Step | Step | Fine di ogni fotogramma, dopo le collisioni |

### Eventi di Collisione

| Evento | Categoria | Si Attiva Quando |
|--------|-----------|------------------|
| Collision With... | Collision | Due istanze si sovrappongono (seleziona l'oggetto bersaglio) |

### Eventi di Tastiera

| Evento | Categoria | Si Attiva Quando |
|--------|-----------|------------------|
| Keyboard | Input | Il tasto e tenuto premuto continuamente (per movimento fluido) |
| Keyboard Press | Input | Il tasto viene premuto per la prima volta (una volta per pressione) |
| Keyboard Release | Input | Il tasto viene rilasciato |

**Tasti Disponibili:** A-Z, 0-9, tasti freccia, Spazio, Invio, Escape, Tab, Backspace, Delete, F1-F12, tasti del tastierino numerico, Shift, Ctrl, Alt e altri (oltre 76 tasti in totale).

**Eventi Tastiera Speciali:**
- **No Key** - Si attiva quando nessun tasto e premuto
- **Any Key** - Si attiva quando qualsiasi tasto e premuto

### Eventi del Mouse

| Evento | Categoria | Si Attiva Quando |
|--------|-----------|------------------|
| Mouse Left/Right/Middle Press | Input | Pulsante cliccato sull'istanza |
| Mouse Left/Right/Middle Release | Input | Pulsante rilasciato sull'istanza |
| Mouse Left/Right/Middle Down | Input | Pulsante tenuto premuto sull'istanza |
| Mouse Enter | Input | Il cursore entra nel riquadro di delimitazione dell'istanza |
| Mouse Leave | Input | Il cursore esce dal riquadro di delimitazione dell'istanza |
| Mouse Wheel Up/Down | Input | Rotella di scorrimento sull'istanza |
| Global Mouse Press | Input | Pulsante cliccato ovunque nella stanza |
| Global Mouse Release | Input | Pulsante rilasciato ovunque nella stanza |

### Eventi di Temporizzazione

| Evento | Categoria | Si Attiva Quando |
|--------|-----------|------------------|
| Alarm 0-11 | Timing | Il conto alla rovescia dell'allarme raggiunge lo zero (12 allarmi indipendenti) |

### Eventi di Disegno

| Evento | Categoria | Si Attiva Quando |
|--------|-----------|------------------|
| Draw | Drawing | L'istanza viene disegnata (sostituisce il disegno predefinito dello sprite) |
| Draw GUI | Drawing | Disegnato sopra tutto (per HUD, visualizzazione punteggio) |

### Eventi di Stanza

| Evento | Categoria | Si Attiva Quando |
|--------|-----------|------------------|
| Room Start | Room | La stanza inizia (dopo gli eventi di creazione) |
| Room End | Room | La stanza sta per terminare |

### Eventi di Gioco

| Evento | Categoria | Si Attiva Quando |
|--------|-----------|------------------|
| Game Start | Game | Il gioco si inizializza (solo nella prima stanza) |
| Game End | Game | Il gioco si sta chiudendo |

### Altri Eventi

| Evento | Categoria | Si Attiva Quando |
|--------|-----------|------------------|
| Outside Room | Other | L'istanza e completamente fuori dai limiti della stanza |
| Intersect Boundary | Other | L'istanza tocca il bordo della stanza |
| No More Lives | Other | Il valore delle vite raggiunge 0 o meno |
| No More Health | Other | Il valore della salute raggiunge 0 o meno |
| Animation End | Other | L'animazione dello sprite raggiunge l'ultimo fotogramma |
| User Event 0-15 | Other | 16 eventi personalizzati attivabili dal codice |

---

## 11. Riferimento Azioni

Le azioni sono i mattoncini del comportamento di gioco. Vengono posizionate all'interno degli eventi e si eseguono in ordine.

### Azioni di Movimento

| Azione | Parametri | Descrizione |
|--------|-----------|-------------|
| Move Grid | direction (left/right/up/down), grid_size (predefinito: 32) | Muovi di un'unita di griglia in una direzione |
| Set Horizontal Speed | speed (pixel/fotogramma) | Imposta hspeed per il movimento orizzontale fluido |
| Set Vertical Speed | speed (pixel/fotogramma) | Imposta vspeed per il movimento verticale fluido |
| Stop Movement | (nessuno) | Imposta entrambe le velocita a zero |
| Move Fixed | directions (8 direzioni), speed | Inizia a muoversi in una direzione fissa |
| Move Free | direction (0-360 gradi), speed | Muovi a un angolo preciso |
| Move Towards | x, y, speed | Muovi verso una posizione obiettivo |
| Set Gravity | direction (270=giu), gravity | Applica accelerazione costante |
| Set Friction | friction | Applica decelerazione ad ogni fotogramma |
| Reverse Horizontal | (nessuno) | Inverti la direzione di hspeed |
| Reverse Vertical | (nessuno) | Inverti la direzione di vspeed |
| Set Speed | speed | Imposta la magnitudine del movimento |
| Set Direction | direction (gradi) | Imposta l'angolo di movimento |
| Jump to Position | x, y | Teletrasporta alla posizione |
| Jump to Start | (nessuno) | Teletrasporta alla posizione iniziale |
| Bounce | (nessuno) | Inverti la velocita alla collisione |

### Azioni di Griglia

| Azione | Parametri | Descrizione |
|--------|-----------|-------------|
| Snap to Grid | grid_size | Allinea la posizione al punto griglia piu vicino |
| If On Grid | grid_size | Controlla se allineato alla griglia (condizionale) |
| Stop If No Keys | grid_size | Fermati sulla griglia quando i tasti di movimento vengono rilasciati |

### Azioni di Istanza

| Azione | Parametri | Descrizione |
|--------|-----------|-------------|
| Create Instance | object, x, y, relative | Crea una nuova istanza di oggetto |
| Destroy Instance | target (self/other) | Rimuovi un'istanza dal gioco |
| Change Sprite | sprite | Cambia lo sprite visualizzato |
| Set Visible | visible (true/false) | Mostra o nascondi l'istanza |
| Set Scale | scale_x, scale_y | Cambia la dimensione dell'istanza |

### Azioni di Punteggio, Vite e Salute

| Azione | Parametri | Descrizione |
|--------|-----------|-------------|
| Set Score | value | Imposta il punteggio a un valore specifico |
| Add to Score | value | Aggiungi punti (puo essere negativo) |
| Set Lives | value | Imposta il numero di vite |
| Add Lives | value | Aggiungi/rimuovi vite |
| Set Health | value | Imposta la salute (0-100) |
| Add Health | value | Aggiungi/rimuovi salute |
| Show Highscore Table | (nessuno) | Visualizza la tabella dei punteggi migliori |

### Azioni di Stanza e Gioco

| Azione | Parametri | Descrizione |
|--------|-----------|-------------|
| Restart Room | (nessuno) | Ricarica la stanza corrente |
| Next Room | (nessuno) | Vai alla stanza successiva in ordine |
| Previous Room | (nessuno) | Vai alla stanza precedente |
| Go to Room | room | Salta a una stanza specifica |
| If Next Room Exists | (nessuno) | Condizionale: esiste una stanza successiva? |
| If Previous Room Exists | (nessuno) | Condizionale: esiste una stanza precedente? |
| Restart Game | (nessuno) | Riavvia dalla prima stanza |
| End Game | (nessuno) | Chiudi il gioco |

### Azioni di Temporizzazione

| Azione | Parametri | Descrizione |
|--------|-----------|-------------|
| Set Alarm | alarm_number (0-11), steps | Avvia il timer con conto alla rovescia (30 step = 0.5 sec a 60 FPS) |
| Delay Action | action, delay_frames | Esegui un'azione dopo un ritardo |

### Azioni di Messaggio e Visualizzazione

| Azione | Parametri | Descrizione |
|--------|-----------|-------------|
| Show Message | message | Mostra un messaggio popup |
| Draw Text | text, x, y, color, size | Disegna testo sullo schermo (usa nell'evento Draw) |
| Draw Rectangle | x1, y1, x2, y2, color, filled | Disegna un rettangolo |
| Draw Circle | x, y, radius, color, filled | Disegna un cerchio |
| Draw Ellipse | x1, y1, x2, y2, color, filled | Disegna un'ellisse |
| Draw Line | x1, y1, x2, y2, color | Disegna una linea |
| Draw Sprite | sprite_name, x, y, subimage | Disegna uno sprite alla posizione |
| Draw Background | background_name, x, y, tiled | Disegna un'immagine di sfondo |
| Draw Score | x, y, caption | Disegna il valore del punteggio sullo schermo |
| Draw Lives | x, y, sprite | Disegna le vite come icone sprite |
| Draw Health Bar | x, y, width, height | Disegna la barra della salute sullo schermo |

### Azioni Audio

| Azione | Parametri | Descrizione |
|--------|-----------|-------------|
| Play Sound | sound, loop | Riproduci un effetto sonoro |
| Stop Sound | sound | Ferma un suono in riproduzione |
| Play Music | music | Riproduci musica di sottofondo (streaming) |
| Stop Music | (nessuno) | Ferma la musica di sottofondo |
| Set Volume | sound, volume (0.0-1.0) | Regola il volume del suono |

### Azioni di Flusso di Controllo

| Azione | Parametri | Descrizione |
|--------|-----------|-------------|
| If Collision At | x, y, object_type | Controlla la collisione alla posizione |
| If Can Push | direction, object_type | Controllo spinta stile Sokoban |
| Set Variable | name, value, scope, relative | Imposta il valore di una variabile |
| Test Variable | name, value, scope, operation | Confronta una variabile |
| Test Expression | expression | Valuta un'espressione booleana |
| Check Empty | x, y, only_solid | Controlla se la posizione e libera |
| Check Collision | x, y, only_solid | Controlla la collisione alla posizione |
| Start Block | (nessuno) | Inizia un blocco di azioni (parentesi graffa aperta) |
| End Block | (nessuno) | Termina un blocco di azioni (parentesi graffa chiusa) |
| Else | (nessuno) | Segna il ramo else di un condizionale |
| Repeat | times | Ripeti l'azione/blocco successivo N volte |
| Exit Event | (nessuno) | Ferma l'esecuzione delle azioni rimanenti |

### Ambito delle Variabili

Le variabili possono essere accedute usando riferimenti con ambito:

| Ambito | Sintassi | Descrizione |
|--------|----------|-------------|
| Self | `self.variable` o semplicemente `variable` | Variabile dell'istanza corrente |
| Other | `other.variable` | L'altra istanza in una collisione |
| Global | `global.variable` | Variabile globale del gioco |

Variabili predefinite dell'istanza: `x`, `y`, `hspeed`, `vspeed`, `direction`, `speed`, `gravity`, `friction`, `visible`, `depth`, `image_index`, `image_speed`, `scale_x`, `scale_y`

---

## 12. Test ed Esecuzione dei Giochi

### Test Rapido (F5)

Premi **F5** o clicca il pulsante **Test** per eseguire il tuo gioco istantaneamente. Si apre una finestra Pygame separata che mostra il tuo gioco.

- Premi **Escape** per fermare il gioco e tornare all'IDE
- La barra di stato dell'IDE mostra "Game running..." mentre il gioco e attivo

### Modalita Debug (F6)

Premi **F6** per la modalita debug, che mostra output aggiuntivo nella console tra cui:
- Registro dell'esecuzione degli eventi
- Dettagli del rilevamento delle collisioni
- Valori dei parametri delle azioni
- Creazione e distruzione delle istanze

### Ordine di Esecuzione del Gioco

Ogni fotogramma segue l'ordine eventi di GameMaker 7.0:

1. Eventi **Begin Step**
2. Conto alla rovescia e attivazione degli **Alarm**
3. Eventi **Step**
4. Eventi di input **Keyboard/Mouse**
5. **Movimento** (fisica: gravita, attrito, hspeed/vspeed)
6. Rilevamento e eventi di **Collision**
7. Eventi **End Step**
8. Eventi **Destroy** per le istanze segnate
9. Eventi **Draw** e rendering

### Titolo della Finestra

Il titolo della finestra di gioco puo mostrare i valori di punteggio, vite e salute. Attiva questa funzione con le impostazioni di visualizzazione del titolo nelle impostazioni del progetto o usando le azioni punteggio/vite/salute.

---

## 13. Esportazione dei Giochi

### Esportazione HTML5

**File > Export as HTML5**

Crea un singolo file HTML autonomo che funziona in qualsiasi browser web.

- Tutti gli sprite sono incorporati come dati base64
- I dati del gioco sono compressi con gzip
- Il motore JavaScript gestisce il rendering tramite HTML5 Canvas
- Nessun server richiesto - basta aprire il file in un browser

### Esportazione EXE (Windows)

**File > Export Project** o **Build > Export Game**

Crea un eseguibile Windows autonomo usando PyInstaller.

**Requisiti:** PyInstaller e Kivy devono essere installati.

**Procedura:**
1. Genera un gioco basato su Kivy dal tuo progetto
2. Raggruppa il runtime Python e tutte le dipendenze
3. Crea un singolo file EXE (potrebbe richiedere 5-10 minuti)

**Opzioni:**
- Console di debug (mostra la finestra del terminale per il debug)
- Icona personalizzata
- Compressione UPX (riduce la dimensione del file)

### Esportazione Mobile (Kivy)

**File > Export to Kivy**

Genera un progetto Kivy per la distribuzione su dispositivi mobili.

**L'output include:**
- Codice di gioco Python adattato per Kivy
- Pacchetto di risorse ottimizzato per dispositivi mobili
- Configurazione `buildozer.spec` per build Android/iOS

**Per compilare per Android:**
```bash
cd exported_project
buildozer android debug
```

### Esportazione ZIP

**File > Export as Zip**

Impacchetta l'intero progetto come archivio ZIP per la condivisione o il backup. Il file ZIP puo essere riaperto con **File > Open Zip Project**.

### Esportazione Aseba (Robot Thymio)

Per i progetti Thymio robot, esporta file di codice AESL compatibili con Aseba Studio.

---

## 14. Programmazione Visuale con Blockly

PyGameMaker integra Google Blockly per la programmazione visuale a blocchi di codice.

### Configurazione dei Blocchi

Apri **Tools > Configure Action Blocks** per personalizzare quali blocchi sono disponibili.

### Preset dei Blocchi

| Preset | Descrizione |
|--------|-------------|
| Full (All Blocks) | Tutti i 173 blocchi attivati |
| Beginner | Solo blocchi essenziali (eventi, movimento base, punteggio, stanze) |
| Intermediate | Aggiunge disegno, piu movimento, vite, salute, suono |
| Platformer Game | Focalizzato sulla fisica: gravita, attrito, collisione |
| Grid-based RPG | Movimento a griglia, salute, transizioni di stanza |
| Sokoban (Box Puzzle) | Movimento a griglia, meccaniche di spinta |
| Testing | Solo blocchi validati |
| Implemented Only | Esclude i blocchi non implementati |
| Code Editor | Per programmazione basata su testo |
| Blockly Editor | Per sviluppo visuale-first |
| Custom | La tua selezione personalizzata |

### Categorie di Blocchi

I blocchi sono organizzati in categorie codificate per colore:

| Categoria | Colore | Blocchi |
|-----------|--------|---------|
| Events | Giallo | 13 blocchi evento |
| Movement | Blu | 14 blocchi movimento |
| Timing | Rosso | Blocchi timer e allarme |
| Drawing | Viola | Disegno di forme e testo |
| Score/Lives/Health | Verde | Blocchi tracciamento punteggio |
| Instance | Rosa | Creazione/distruzione istanze |
| Room | Marrone | Navigazione stanze |
| Values | Blu Scuro | Variabili ed espressioni |
| Sound | | Riproduzione audio |
| Output | | Messaggi e visualizzazione |

### Dipendenze dei Blocchi

Alcuni blocchi richiedono altri blocchi per funzionare. La finestra di configurazione mostra avvisi quando mancano le dipendenze. Per esempio, il blocco **Draw Score** richiede che **Set Score** e **Add Score** siano attivati.

---

## 15. Supporto Robot Thymio

PyGameMaker include il supporto per il robot educativo Thymio, permettendo di simulare e programmare robot Thymio all'interno dell'IDE.

### Cos'e Thymio?

Thymio e un piccolo robot educativo con sensori, LED, motori e pulsanti. PyGameMaker puo simulare il comportamento di Thymio ed esportare codice da eseguire su robot reali.

### Attivazione di Thymio

Vai su **Tools > Thymio Programming > Show Thymio Tab in Object Editor** per attivare le funzionalita Thymio nell'editor di oggetti.

### Simulatore Thymio

Il simulatore modella il robot Thymio fisico:

**Specifiche:**
- Dimensione robot: 110x110 pixel (11cm x 11cm)
- Interasse ruote: 95 pixel
- Intervallo velocita motore: da -500 a +500

### Sensori di Thymio

| Sensore | Numero | Intervallo | Descrizione |
|---------|--------|-----------|-------------|
| Proximity | 7 | 0-4000 | Sensori di distanza orizzontali (raggio 10cm) |
| Ground | 2 | 0-1023 | Rileva superfici chiare/scure |
| Buttons | 5 | 0/1 | Avanti, indietro, sinistra, destra, centro |

### Eventi di Thymio

| Evento | Si Attiva Quando |
|--------|------------------|
| Button Forward/Backward/Left/Right/Center | Pulsante capacitivo premuto |
| Any Button | Lo stato di qualsiasi pulsante cambia |
| Proximity Update | I sensori di prossimita si aggiornano (10 Hz) |
| Ground Update | I sensori di terra si aggiornano (10 Hz) |
| Tap | L'accelerometro rileva un tocco/urto |
| Sound Detected | Il microfono rileva un suono |
| Timer 0/1 | Il periodo del timer scade |
| Sound Finished | La riproduzione del suono si completa |
| Message Received | Comunicazione IR ricevuta |

### Azioni di Thymio

**Controllo Motori:**
- Imposta Velocita Motore (sinistro, destro indipendentemente)
- Muovi Avanti / Indietro
- Gira a Sinistra / Destra
- Ferma Motori

**Controllo LED:**
- Imposta LED Superiore (colore RGB)
- Imposta LED Inferiore Sinistro/Destro
- Imposta LED Circolari (8 LED attorno al perimetro)
- Spegni Tutti i LED

**Suono:**
- Riproduci Tono (frequenza, durata)
- Riproduci Suono di Sistema
- Ferma Suono

**Condizioni dei Sensori:**
- If Proximity (sensore, soglia, confronto)
- If Ground Dark / Light
- If Button Pressed / Released

**Timer:**
- Imposta Periodo Timer (timer 0 o 1, periodo in ms)

### Esportazione verso il Thymio Reale

1. Esporta il tuo progetto Thymio tramite l'esportatore Aseba
2. Apri il file `.aesl` generato in Aseba Studio
3. Collega il tuo Thymio tramite USB
4. Clicca **Load** poi **Run**

---

## 16. Impostazioni e Preferenze

Apri **Tools > Preferences** per configurare l'IDE.

### Scheda Aspetto

| Impostazione | Opzioni | Predefinito |
|-------------|---------|-------------|
| Font Size | 8-24 pt | 10 |
| Font Family | System Default, Segoe UI, Arial, Ubuntu, Helvetica, SF Pro Text, Roboto | System Default |
| Theme | Default, Dark, Light | Default |
| UI Scale | 0.5x - 2.0x | 1.0x |
| Show Tooltips | Si/No | Si |

### Scheda Editor

| Impostazione | Opzioni | Predefinito |
|-------------|---------|-------------|
| Enable Auto-Save | Si/No | Si |
| Auto-Save Interval | 1-30 minuti | 5 min |
| Show Grid | Si/No | Si |
| Grid Size | 8-128 px | 32 |
| Snap to Grid | Si/No | Si |
| Show Collision Boxes | Si/No | No |

### Scheda Progetto

| Impostazione | Opzioni | Predefinito |
|-------------|---------|-------------|
| Default Projects Folder | Percorso | ~/PyGameMaker Projects |
| Recent Projects Limit | 5-50 | 10 |
| Create Backup on Save | Si/No | Si |

### Scheda Avanzate

| Impostazione | Opzioni | Predefinito |
|-------------|---------|-------------|
| Debug Mode | Si/No | No |
| Show Console Output | Si/No | Si |
| Maximum Undo Steps | 10-200 | 50 |

### File di Configurazione

Le impostazioni sono memorizzate in `~/.pygamemaker/config.json` e persistono tra le sessioni.

### Cambio della Lingua

Vai su **Tools > Language** e seleziona la lingua preferita.

**Lingue Supportate:**
- English
- Francais
- Espanol
- Deutsch
- Italiano
- Russky (Russo)
- Slovenscina (Sloveno)
- Ukrainska (Ucraino)

L'interfaccia si aggiorna immediatamente. Alcune modifiche potrebbero richiedere il riavvio dell'IDE.

---

## 17. Scorciatoie da Tastiera

### Scorciatoie Globali

| Scorciatoia | Azione |
|-------------|--------|
| Ctrl+N | Nuovo Progetto |
| Ctrl+O | Apri Progetto |
| Ctrl+S | Salva Progetto |
| Ctrl+Shift+S | Salva Progetto Come |
| Ctrl+E | Esporta Progetto |
| Ctrl+Q | Esci dall'IDE |
| Ctrl+R | Crea Stanza |
| F1 | Documentazione |
| F5 | Testa Gioco |
| F6 | Debug Gioco |
| F7 | Compila Gioco |
| F8 | Compila ed Esegui |

### Scorciatoie Editor

| Scorciatoia | Azione |
|-------------|--------|
| Ctrl+Z | Annulla |
| Ctrl+Y | Ripristina |
| Ctrl+X | Taglia |
| Ctrl+C | Copia |
| Ctrl+V | Incolla |
| Ctrl+D | Duplica |
| Ctrl+F | Cerca |
| Ctrl+H | Cerca e Sostituisci |
| Delete | Elimina selezionato |

### Scorciatoie Editor di Sprite

| Scorciatoia | Azione |
|-------------|--------|
| P | Strumento matita |
| E | Strumento gomma |
| I | Selettore colore (contagocce) |
| G | Strumento riempimento (secchiello) |
| L | Strumento linea |
| R | Strumento rettangolo |
| O | Strumento ellisse |
| S | Strumento selezione |
| Ctrl+Mouse Wheel | Zoom avanti/indietro |

---

## 18. Tutorial

PyGameMaker include tutorial integrati per aiutarti a iniziare. Accedi ad essi da **Help > Tutorials** o dalla cartella Tutorials nella directory di installazione.

### Tutorial Disponibili

| # | Tutorial | Descrizione |
|---|----------|-------------|
| 01 | Getting Started | Introduzione all'IDE e primo progetto |
| 02 | First Game | Creazione del tuo primo gioco giocabile |
| 03 | Pong | Classico gioco Pong con racchetta e pallina |
| 04 | Breakout | Gioco di rottura dei mattoncini stile Breakout |
| 05 | Sokoban | Gioco rompicapo con spinta di scatole |
| 06 | Maze | Gioco di navigazione nel labirinto |
| 07 | Platformer | Gioco a piattaforme con scorrimento laterale |
| 08 | Lunar Lander | Gioco di atterraggio basato sulla gravita |

I tutorial sono disponibili in piu lingue (Inglese, Tedesco, Spagnolo, Francese, Italiano, Russo, Sloveno, Ucraino).

---

## 19. Risoluzione dei Problemi

### Il gioco non si avvia (F5)

- Verifica che il tuo progetto abbia almeno una stanza con istanze
- Controlla che gli oggetti abbiano sprite assegnati
- Guarda l'output della console (modalita debug F6) per i messaggi di errore

### Gli sprite non vengono mostrati

- Conferma che il file sprite esiste nella cartella `sprites/`
- Controlla che l'oggetto abbia uno sprite assegnato nelle sue proprieta
- Verifica che l'istanza sia impostata su `visible = true`

### Le collisioni non funzionano

- Assicurati che l'oggetto bersaglio sia marcato come **Solid** se usi collisioni basate sui solidi
- Verifica di avere un evento **Collision With** configurato per l'oggetto corretto
- Controlla che le istanze si sovrappongano effettivamente (usa la modalita debug)

### Il suono non viene riprodotto

- Verifica che il file audio esista e sia in un formato supportato (WAV, OGG, MP3)
- Controlla che pygame.mixer sia stato inizializzato con successo (vedi output della console)
- I file musicali vengono trasmessi in streaming dal disco - assicurati che il percorso del file sia corretto

### L'esportazione fallisce

- **Esportazione EXE:** Assicurati che PyInstaller sia installato (`pip install pyinstaller`)
- **Esportazione Kivy:** Assicurati che Kivy sia installato (`pip install kivy`)
- **Esportazione HTML5:** Controlla la console per eventuali errori di codifica
- Tutte le esportazioni richiedono un progetto valido con almeno una stanza

### Problemi di prestazioni

- Riduci il numero di istanze nelle stanze
- Usa il sistema di collisione con griglia spaziale (attivato per impostazione predefinita)
- Evita operazioni costose negli eventi Step (eseguiti 60 volte al secondo)
- Usa gli allarmi per attivita periodiche invece di contare i fotogrammi nello Step

---

**PyGameMaker IDE** - Versione 1.0.0-rc.6
Copyright 2025-2026 Gabriel Thullen
Rilasciato sotto Licenza Pubblica Generale GNU v3 (GPLv3)
GitHub: https://github.com/Gabe1290/pythongm
