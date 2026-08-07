# Editor Stanze

> [English](Room-Editor) | [Français](Editeur_Salles_fr) | [Deutsch](Raum_Editor_de) | [Italiano](Editor_Stanze_it) | [Español](Editor_Salas_es) | [Português](Editor_Salas_pt) | [Slovenščina](Urejevalnik_Sob_sl) | [Українська](Redaktor_Kimnat_uk) | [Русский](Redaktor_Komnat_ru)

---

[Torna alla Home](Home_it)

Le stanze sono i livelli, le schermate o le scene del tuo gioco.
L'Editor Stanze ti permette di progettare questi spazi posizionando
oggetti e configurando gli sfondi.

---

## Aprire l'Editor Stanze

1. Fai doppio clic su una stanza esistente nell'albero delle risorse, oppure
2. Clic destro su **Rooms** > **Create Room**

---

## Proprietà della Stanza

| Proprietà | Descrizione |
|-----------|-------------|
| **Name** | Identificatore univoco (es. `room_livello1`) |
| **Width** | Larghezza della stanza in pixel |
| **Height** | Altezza della stanza in pixel |
| **Speed** | Velocità di gioco in fotogrammi al secondo (predefinito: 60) |
| **Persistent** | Mantiene lo stato della stanza uscendo/rientrando |

### Convenzione di Denominazione

Usa il prefisso `room_` per le stanze:
- `room_menu`
- `room_livello1`
- `room_game_over`

---

## Posizionare Oggetti

### Aggiungere Istanze

1. Seleziona un oggetto dal pannello **Objects**
2. Clicca nella vista della stanza per posizionare un'istanza
3. Clicca e trascina per posizionare più istanze

### Selezionare Istanze

- Clicca su un'istanza per selezionarla
- Tieni premuto **Ctrl** e clicca per selezionarne più di una
- Disegna un rettangolo per selezionare tutte le istanze al suo interno

### Spostare Istanze

- Trascina le istanze selezionate con il mouse
- Usa i tasti freccia per un movimento preciso

### Eliminare Istanze

- Seleziona le istanze e premi **Canc**, oppure
- Clic destro e scegli "Elimina"

---

## Impostazioni della Griglia

Attiva la griglia per un posizionamento preciso:

1. Vai su **View > Show Grid**
2. Imposta la dimensione della griglia (es. 32x32)
3. Attiva "Snap to Grid"

Dimensioni di griglia comuni:
- **16x16** - Mattonelle piccole
- **32x32** - Mattonelle standard
- **64x64** - Mattonelle grandi

---

## Sfondi

### Impostare uno Sfondo

1. Clicca sulla scheda **Backgrounds**
2. Seleziona una risorsa di sfondo
3. Configura le opzioni di visualizzazione

### Opzioni di Sfondo

| Opzione | Descrizione |
|--------|-------------|
| **Visible** | Mostra/nascondi lo sfondo |
| **Foreground** | Disegna davanti agli oggetti |
| **Tile Horizontal** | Ripeti orizzontalmente |
| **Tile Vertical** | Ripeti verticalmente |
| **Stretch** | Estendi per riempire la stanza |
| **Horizontal Speed** | Velocità di scorrimento (parallasse) |
| **Vertical Speed** | Velocità di scorrimento (parallasse) |

### Layer di Sfondo

Una stanza supporta fino a **8 layer di sfondo**, ciascuno con la
propria velocità di scorrimento per effetti parallasse. Esempio di
disposizione:
- Layer 0: Cielo (più lontano)
- Layer 1: Montagne (scorrimento più lento)
- Layer 2: Alberi (scorrimento medio)
- Layer 3: Terreno (nessuno scorrimento)

---

## Views (Camera)

Le view controllano quale porzione della stanza è visibile sullo
schermo. Fino a **8 view** (View 0 - View 7) possono essere configurate
per stanza — View 0 è visibile per impostazione predefinita; attiva
altre view per split-screen o picture-in-picture.

### Attivare le Views

1. Seleziona "Enable Views" nelle proprietà della stanza
2. Configura View 0 (la view primaria)

### Proprietà delle Views

| Proprietà | Descrizione |
|-----------|-------------|
| **View X/Y** | Angolo in alto a sinistra della view nella stanza |
| **View Width/Height** | Dimensione dell'area visibile |
| **Port X/Y** | Posizione sullo schermo |
| **Port Width/Height** | Dimensione sullo schermo (può essere estesa) |
| **Object Following** | Oggetto seguito dalla view |
| **Border H/V** | Zona morta prima che la camera si muova |

### Seguire un Oggetto

Per far seguire il giocatore dalla camera:
1. Imposta "Object Following" su `obj_player`
2. Regola "Border H" e "Border V" per uno scorrimento fluido

---

## Ordine delle Stanze

L'ordine delle stanze nell'albero delle risorse determina:
1. Quale stanza carica per prima (stanza in alto = stanza iniziale)
2. L'ordine per le azioni "Next Room" e "Previous Room"

### Cambiare l'Ordine delle Stanze

- Trascina le stanze nell'albero delle risorse per riordinarle
- Oppure clic destro e usa "Sposta su" / "Sposta giù"

---

## Suggerimenti e Buone Pratiche

### Organizzazione
- Nomina le stanze chiaramente in base al loro scopo
- Mantieni il menu principale come prima stanza
- Usa dimensioni di stanza coerenti all'interno di un gioco

### Prestazioni
- Non posizionare troppe istanze in una stanza
- Usa le mattonelle per la geometria statica dei livelli
- Distruggi le istanze fuori schermo quando possibile

---

## Prossimi Passi

- [[Editor_Oggetti_it]] - Crea oggetti da posizionare nelle stanze
- [[Eventi_e_Azioni_it]] - Aggiungi interattività ai tuoi livelli
- [[Esportare_Giochi_it]] - Condividi il tuo gioco completato
