# Editor Sprite

> [English](Sprite-Editor) | [Français](Sprite-Editor_fr) | [Deutsch](Sprite-Editor_de) | [Italiano](Sprite-Editor_it) | [Español](Sprite-Editor_es) | [Português](Sprite-Editor_pt) | [Русский](Sprite-Editor_ru)

---

> [Torna alla Home](Home_it)

Gli sprite sono le immagini e le animazioni collegate agli oggetti.
L'Editor Sprite è uno strumento di pixel art integrato — disegna gli
sprite direttamente in PyGameMaker, senza bisogno di un editor di
immagini esterno.

---

## Aprire l'Editor Sprite

1. Fai doppio clic su uno sprite esistente nell'albero delle risorse, oppure
2. Clic destro su **Sprite** > **Crea Sprite**

![L'Editor Sprite: strumenti di disegno e dimensione del pennello a
sinistra, sotto il selettore dell'origine e l'opzione Precise Collision,
una tavolozza di colori, l'area di disegno al centro con un personaggio
in pixel art a 10x di zoom, e la striscia dei fotogrammi in basso (8
fotogrammi, pulsante Play, aggiunta/duplicazione/eliminazione fotogramma)](images/sprite-editor.png)

---

## Strumenti di Disegno

| Strumento | Scorciatoia | Cosa fa |
|------|----------|---------------|
| **Matita** | P | Disegna pixel singoli |
| **Gomma** | E | Cancella pixel (trasparenza) |
| **Contagocce** | I | Preleva un colore dall'area di disegno |
| **Riempimento** | G | Riempie un'area connessa (secchiello) |
| **Linea** | L | Disegna una linea retta |
| **Rettangolo** | R | Disegna un rettangolo (attiva **Riempito** per pieno/contorno) |
| **Ellisse** | O | Disegna un'ellisse (rispetta anch'essa **Riempito**) |
| **Selezione** | S | Selezione rettangolare — sposta, copia, taglia, incolla o elimina i pixel selezionati |

**La dimensione del pennello** si applica a Matita, Gomma e ai contorni
di linee/forme. La tavolozza dei colori contiene un set di colori di
lavoro più la tavolozza rapida standard a 12 colori; clicca su uno swatch
per selezionarlo, oppure usa il Contagocce per prelevare un colore
direttamente dallo sprite.

---

## Operazioni sull'Area di Disegno

- **Specchia H / Specchia V** — capovolge il fotogramma corrente orizzontalmente o verticalmente
- **Ridimensiona** — apre una finestra di dialogo con due modalità distinte:
  - **Scala Immagine** — allunga il contenuto esistente a una nuova dimensione
  - **Ridimensiona Canvas** — mantiene il contenuto alla dimensione originale e aggiunge/ritaglia spazio attorno, ancorato a un angolo, un bordo o il centro a scelta
- **Griglia** — attiva/disattiva una sovrapposizione di griglia a livello di pixel (non influisce sull'immagine salvata)
- **Zoom Avanti / Zoom Indietro** — l'area di disegno lavora spesso a 10x o più, poiché gli sprite sono generalmente piccoli (16×16-64×64 è comune)
- **Esporta PNG…** — salva il fotogramma corrente come file `.png` autonomo
- Clic destro sull'area di disegno per **Copia / Taglia / Incolla / Elimina / Deseleziona / Seleziona Tutto** (scorciatoie standard: Ctrl+C / Ctrl+X / Ctrl+V / Canc / Esc)

---

## Fotogrammi e Animazione

Uno sprite può contenere più fotogrammi, riprodotti come animazione
durante l'esecuzione del gioco. La striscia dei fotogrammi in basso
nell'editor:

| Controllo | Effetto |
|---------|--------|
| **+** | Aggiunge un nuovo fotogramma vuoto |
| **D** | Duplica il fotogramma corrente |
| **-** | Elimina il fotogramma corrente |
| **Play** | Anteprima dell'animazione nell'editor alla frequenza fotogrammi dello sprite |

Clicca su una miniatura di fotogramma per saltarci sopra e disegnare specificamente su quel fotogramma.

---

## Origine e Collisione

- **Origine** — il punto che gli oggetti che usano questo sprite
  considerano come la loro posizione `(x, y)`. Preimpostazioni:
  Alto-Sinistra, Alto-Centro, Centro, Centro-Basso, Basso-Sinistra,
  Basso-Destra, oppure **Personalizzata** (X/Y esatti). La maggior parte
  dei personaggi platform/vista dall'alto usa **Centro-Basso** in modo
  che i piedi dello sprite siano alla posizione Y dell'oggetto.
- **Precise Collision** — se attivata, le collisioni contro questo
  sprite testano i pixel non trasparenti reali anziché il bounding box
  dello sprite. Più precisa per sprite di forma irregolare, più costosa
  da calcolare — lasciala disattivata per forme semplici (muri, monete)
  e riservala agli sprite dove una collisione a bounding box risulterebbe
  visibilmente sbagliata.

---

## Prossimi Passi

- [[Editor_Oggetti_it|Editor Oggetti]] - Collegare uno sprite a un oggetto di gioco
- [[Editor_Stanze_it|Editor Stanze]] - Posizionare istanze di oggetto che usano il tuo sprite
- [[Primo_Gioco_it|Crea il Tuo Primo Gioco]] - Un tutorial completo che inizia disegnando sprite
