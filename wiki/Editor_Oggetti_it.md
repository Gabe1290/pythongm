# Editor Oggetti

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

[Torna alla Home](Home_it)

Gli oggetti sono i mattoni fondamentali del tuo gioco. Rappresentano
tutto, dai giocatori ai nemici, dagli oggetti collezionabili agli
elementi dell'interfaccia.

---

## Aprire l'Editor Oggetti

![L'Editor Oggetti: una lista eventi a sinistra (Create, Step, diversi
eventi Collision, Keyboard, No More Lives, Game Start), le proprietà
dell'oggetto (sprite, parent, Visible/Persistent/Solid) a destra, e le
schede Event List / Blockly / Editor Codice che cambiano il modo di
scrivere le azioni di ogni evento](images/object-editor.png)

1. Fai doppio clic su un oggetto esistente nell'albero delle risorse, oppure
2. Clic destro su **Objects** > **Create Object**

---

## Proprietà dell'Oggetto

| Proprietà | Descrizione |
|-----------|-------------|
| **Name** | Identificatore univoco per l'oggetto (es. `obj_giocatore`) |
| **Sprite** | La rappresentazione visiva dell'oggetto |
| **Visible** | Se l'oggetto viene disegnato (predefinito: sì) |
| **Solid** | Usato per il rilevamento delle collisioni con oggetti solidi |
| **Depth** | Ordine di disegno (più basso = disegnato sopra) |
| **Persistent** | L'oggetto sopravvive ai cambi di stanza |
| **Parent Object** | Eredita proprietà/eventi comuni da un altro oggetto |

### Convenzione di Denominazione

Usa il prefisso `obj_` per gli oggetti:
- `obj_giocatore`
- `obj_nemico`
- `obj_moneta`
- `obj_muro`

---

## Eventi

Gli eventi sono trigger che causano l'esecuzione di azioni. Clicca su
"Add Event" per aggiungerne uno.

### Eventi Comuni

| Evento | Quando si Attiva |
|-------|------------------|
| **Creazione** | Una volta, quando un'istanza viene creata |
| **Distruzione** | Quando l'istanza viene distrutta |
| **Step** | Ad ogni frame di gioco (60 volte al secondo) |
| **Disegno** | Durante la fase di disegno |
| **Alarm [0-11]** | Quando un timer di allarme raggiunge lo zero |

### Eventi Tastiera

| Evento | Quando si Attiva |
|-------|------------------|
| **Key Press** | Una volta, quando un tasto viene premuto |
| **Key Release** | Una volta, quando un tasto viene rilasciato |
| **Keyboard** | Ad ogni frame finché un tasto è tenuto premuto |
| **No Key** | Quando nessun tasto è premuto |

### Eventi Mouse

| Evento | Quando si Attiva |
|-------|------------------|
| **Mouse Button** | Al clic sull'istanza |
| **Global Mouse** | Al clic ovunque |
| **Mouse Enter** | Quando il cursore entra nell'istanza |
| **Mouse Leave** | Quando il cursore esce dall'istanza |

### Eventi di Collisione

| Evento | Quando si Attiva |
|-------|------------------|
| **Collision with [oggetto]** | Al contatto con un altro tipo di oggetto |

### Altri Eventi

| Evento | Quando si Attiva |
|-------|------------------|
| **Fuori dalla stanza** | Quando l'istanza lascia i confini della stanza |
| **Tocca il bordo della stanza** | Quando l'istanza tocca il bordo della stanza |
| **Inizio del gioco** | Una volta, all'avvio del gioco |
| **Fine del gioco** | Una volta, alla chiusura del gioco |
| **Inizio della stanza** | Entrando in una stanza |
| **Fine della stanza** | Uscendo da una stanza |

---

## Azioni

Le azioni sono operazioni eseguite quando un evento si attiva. Ogni
evento può avere più azioni, eseguite in ordine.

### Azioni di Movimento
- **Imposta velocità** — Imposta la velocità di movimento
- **Imposta direzione** — Imposta la direzione di movimento (0-360 gradi)
- **Imposta velocità orizzontale** — Imposta hspeed
- **Imposta velocità verticale** — Imposta vspeed
- **Muovi verso un punto** — Muovi verso coordinate
- **Jump to Position** — Teletrasporta istantaneamente a coordinate
- **Salta alla posizione iniziale** — Torna alla posizione di creazione
- **Salta a posizione casuale** — Teletrasporta a una posizione casuale

### Azioni di Istanza
- **Crea istanza** — Crea un nuovo oggetto
- **Distruggi istanza** — Rimuove l'istanza attuale
- **Cambia istanza** — Si trasforma in un altro tipo di oggetto

### Azioni di Temporizzazione
- **Imposta allarme** — Avvia un timer a conto alla rovescia
- **Pausa** — Mette in pausa l'esecuzione per un breve momento

### Azioni di Disegno
- **Disegna sprite** — Disegna uno sprite
- **Disegna testo** — Mostra testo sullo schermo
- **Disegna rettangolo** — Disegna un rettangolo pieno o contornato
- **Disegna punteggio** — Mostra il punteggio attuale
- **Disegna vite** — Mostra le vite rimanenti
- **Disegna barra della salute** — Mostra la barra della salute

### Score/Lives/Health
- **Imposta punteggio** — Cambia il valore del punteggio
- **Imposta vite** — Cambia il numero di vite
- **Imposta salute** — Cambia il valore della salute
- **Verifica punteggio** — Controlla una condizione sul punteggio
- **Verifica vite** — Controlla una condizione sulle vite
- **Verifica salute** — Controlla una condizione sulla salute

### Azioni di Stanza
- **Stanza successiva** — Vai alla stanza successiva
- **Stanza precedente** — Vai alla stanza precedente
- **Riavvia stanza** — Ripristina la stanza attuale
- **Vai alla stanza** — Salta a una stanza specifica

### Azioni Sound
- **Riproduci suono** — Riproduci un effetto sonoro
- **Ferma suono** — Ferma un suono in riproduzione
- **Riproduci musica** — Riproduci musica di sottofondo
- **Ferma musica** — Ferma la musica di sottofondo

### Azioni Variabili
- **Imposta variabile** — Assegna un valore a una variabile
- **Verifica variabile** — Controlla una condizione su una variabile

---

## Programmazione Visuale con Blockly

Invece di usare la lista di azioni, puoi passare alla scheda **Blockly**
per la programmazione visuale:

1. Apri un oggetto
2. Fai clic sulla scheda **Blockly**
3. Trascina i blocchi dalla barra strumenti per creare la logica
4. I blocchi si agganciano per formare programmi completi

Vedi [[Programmazione_Visuale_it]] per maggiori dettagli.

---

## Suggerimenti e Buone Pratiche

### Organizzazione
- Dai agli oggetti nomi descrittivi
- Raggruppa gli oggetti correlati con prefissi simili
- Usa l'evento Create solo per l'inizializzazione

### Prestazioni
- Evita calcoli pesanti nell'evento Step
- Usa gli allarmi invece di contare i frame manualmente
- Distruggi le istanze che lasciano la stanza

### Debug
- Usa l'azione **Mostra messaggio** per visualizzare i valori
- Controlla l'output della console per gli errori
- Testa frequentemente durante lo sviluppo

---

## Esempio: IA Semplice per Nemico

```
Create Event:
  - Set Alarm[0] = 60 (1 secondo a 60 FPS)
  - Set direction = random(360)
  - Set speed = 2

Alarm[0] Event:
  - Set direction = random(360)
  - Set Alarm[0] = 60

Collision with obj_player:
  - Set Lives relative = -1
  - Destroy Instance
```

---

## Prossimi Passi

- [[Editor_Stanze_it]] - Posiziona gli oggetti nei tuoi livelli di gioco
- [[Eventi_e_Azioni_it]] - Riferimento completo di tutti gli eventi e azioni
- [[Programmazione_Visuale_it]] - Impara la programmazione a blocchi con Blockly
