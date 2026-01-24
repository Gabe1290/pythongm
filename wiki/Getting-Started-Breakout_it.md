# Introduzione alla Creazione di Videogiochi con PyGameMaker

*[Home](Home_it) | [Preset per Principianti](Beginner-Preset_it) | [English](Getting-Started-Breakout) | [Français](Getting-Started-Breakout_fr)*

**A cura del Team PyGameMaker**

---

In questo tutorial, impareremo le basi della creazione di videogiochi con PyGameMaker. Trattandosi di un software relativamente completo con molte funzionalita, ci concentreremo solo su quelle che ci saranno utili durante questo tutorial.

Creeremo un semplice gioco in stile Breakout che assomigliera a questo:

![Concetto del Gioco Breakout](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

Questo tutorial e pensato per te, anche se non hai conoscenze di programmazione, poiche PyGameMaker permette ai principianti di creare facilmente giochi indipendentemente dal loro livello di competenza.

Bene, iniziamo a progettare il nostro gioco!

---

## Passo 1: Per Iniziare

Inizia aprendo PyGameMaker. Dovresti vedere l'interfaccia principale con il pannello **Risorse** sul lato sinistro, che elenca le diverse categorie di risorse: Sprite, Suoni, Sfondi, Font, Oggetti e Stanze.

Prima di tutto, in un videogioco, la prima cosa che il giocatore nota e cio che vede sullo schermo. Questa e in realta la base di un gioco: un gioco senza grafica non esiste (o e un caso molto speciale). Inizieremo quindi inserendo immagini nel nostro gioco, che saranno la rappresentazione grafica degli oggetti che il giocatore vedra sullo schermo. Nella terminologia dello sviluppo di videogiochi, queste immagini sono chiamate **Sprite**.

---

## Passo 2: Creazione degli Sprite

### 2.1 Creazione dello Sprite della Racchetta

1. Fai clic destro sulla cartella **Sprites** in cima alla colonna sinistra
2. Clicca su **Crea Sprite**
3. Si aprira una finestra chiamata **Proprieta Sprite** - qui definirai tutte le caratteristiche del tuo sprite
4. Usa l'editor integrato per disegnare un rettangolo orizzontale (circa 64x16 pixel) nel colore che preferisci
5. **Importante:** Clicca **Centra** per impostare l'origine al centro del tuo sprite
   > L'origine di uno sprite e il suo punto centrale, le sue coordinate X:0 e Y:0. Queste sono le sue coordinate di base.
6. Cambia il nome del tuo sprite usando il campo di testo in alto, e inserisci `spr_paddle`
   > Questo non ha impatto tecnico - serve solo per aiutarti a navigare meglio tra i tuoi file una volta che ne avrai di piu. Puoi scegliere qualsiasi nome tu voglia; questo e solo un esempio.
7. Clicca **OK**

Hai appena creato il tuo primo sprite! Questa e la tua racchetta, l'oggetto che il giocatore controllera per colpire la palla.

### 2.2 Creazione dello Sprite della Palla

Continuiamo e aggiungiamo altri sprite. Ripeti lo stesso processo:

1. Fai clic destro su **Sprites** -> **Crea Sprite**
2. Disegna un piccolo cerchio (circa 16x16 pixel)
3. Clicca **Centra** per impostare l'origine
4. Chiamalo `spr_ball`
5. Clicca **OK**

### 2.3 Creazione degli Sprite dei Mattoni

Abbiamo bisogno di tre tipi di mattoni. Creali uno alla volta:

**Primo Mattone (Distruttibile):**
1. Crea un nuovo sprite
2. Disegna un rettangolo (circa 48x24 pixel) - usa un colore vivace come il rosso
3. Clicca **Centra**, chiamalo `spr_brick_1`
4. Clicca **OK**

**Secondo Mattone (Distruttibile):**
1. Crea un nuovo sprite
2. Disegna un rettangolo (stesse dimensioni) - usa un colore diverso come il blu
3. Clicca **Centra**, chiamalo `spr_brick_2`
4. Clicca **OK**

**Terzo Mattone (Muro Indistruttibile):**
1. Crea un nuovo sprite
2. Disegna un rettangolo (stesse dimensioni) - usa un colore piu scuro come il grigio
3. Clicca **Centra**, chiamalo `spr_brick_3`
4. Clicca **OK**

Ora dovresti avere tutti gli sprite per il nostro gioco:
- `spr_paddle` - La racchetta del giocatore
- `spr_ball` - La palla che rimbalza
- `spr_brick_1` - Primo mattone distruttibile
- `spr_brick_2` - Secondo mattone distruttibile
- `spr_brick_3` - Mattone muro indistruttibile

> **Nota:** Nei giochi, ci sono generalmente due fonti principali di rendering grafico: **Sprite** e **Sfondi**. E tutto cio che compone quello che vedi sullo schermo. Uno Sfondo e, come suggerisce il nome, un'immagine di sfondo.

---

## Passo 3: Comprendere Oggetti ed Eventi

Cosa abbiamo detto all'inizio? La prima cosa che il giocatore nota e cio che vede sullo schermo. Ce ne siamo occupati con i nostri sprite. Ma un gioco fatto solo di immagini non e un gioco - e un dipinto! Passeremo ora alla fase successiva: gli **Oggetti**.

Un Oggetto e un'entita nel tuo gioco che puo avere comportamenti, rispondere a eventi e interagire con altri oggetti. Lo sprite e solo la rappresentazione visiva; l'oggetto e cio che gli da vita.

### Come Funziona la Logica di Gioco

Tutto nella programmazione di giochi segue questo schema: **Se accade questo, allora eseguo quello.**

- Se il giocatore preme un tasto, allora faccio questo
- Se questa variabile equivale a questo valore, allora faccio quello
- Se due oggetti collidono, allora succede qualcosa

Questo e cio che chiamiamo **Eventi** e **Azioni** in PyGameMaker:
- **Eventi** = Cose che possono accadere (pressione di tasto, collisione, timer, ecc.)
- **Azioni** = Cose che vuoi fare quando gli eventi si verificano (muovere, distruggere, cambiare punteggio, ecc.)

---

## Passo 4: Creazione dell'Oggetto Racchetta

Creiamo l'oggetto che il giocatore controllera: la racchetta.

### 4.1 Crea l'Oggetto

1. Fai clic destro sulla cartella **Objects** -> **Crea Oggetto**
2. Chiamalo `obj_paddle`
3. Nel menu a tendina **Sprite**, seleziona `spr_paddle` - ora il nostro oggetto ha un aspetto visivo!
4. Spunta la casella **Solido** (ci servira per le collisioni)

### 4.2 Programmazione del Movimento

In un gioco Breakout, dobbiamo muovere la racchetta per impedire alla palla di sfuggire dal basso. La controlleremo con la tastiera.

**Movimento a Destra:**
1. Clicca **Aggiungi Evento** -> **Tastiera** -> **Freccia Destra**
2. Dal pannello azioni sulla destra, aggiungi l'azione **Imposta Velocita Orizzontale**
3. Imposta il **valore** a `5`
4. Clicca **OK**

Questo significa: "Quando il tasto Freccia Destra viene premuto, imposta la velocita orizzontale a 5 (movimento verso destra)."

**Movimento a Sinistra:**
1. Clicca **Aggiungi Evento** -> **Tastiera** -> **Freccia Sinistra**
2. Aggiungi l'azione **Imposta Velocita Orizzontale**
3. Imposta il **valore** a `-5`
4. Clicca **OK**

**Fermarsi Quando i Tasti Vengono Rilasciati:**

Se testassimo ora, la racchetta continuerebbe a muoversi anche dopo aver rilasciato il tasto! Risolviamolo:

1. Clicca **Aggiungi Evento** -> **Rilascio Tasto** -> **Freccia Destra**
2. Aggiungi l'azione **Imposta Velocita Orizzontale** con valore `0`
3. Clicca **OK**

4. Clicca **Aggiungi Evento** -> **Rilascio Tasto** -> **Freccia Sinistra**
5. Aggiungi l'azione **Imposta Velocita Orizzontale** con valore `0`
6. Clicca **OK**

Ora la nostra racchetta si muove quando i tasti vengono premuti e si ferma quando vengono rilasciati. Abbiamo finito con questo oggetto per ora!

---

## Passo 5: Creazione dell'Oggetto Mattone Muro

Creiamo un mattone muro indistruttibile - questo formera i confini della nostra area di gioco.

1. Crea un nuovo oggetto chiamato `obj_brick_3`
2. Assegna lo sprite `spr_brick_3`
3. Spunta la casella **Solido**

La palla rimbalzera su questo mattone. Dato che e solo un muro, non abbiamo bisogno di eventi - deve solo essere solido. Clicca **OK** per salvare.

---

## Passo 6: Creazione dell'Oggetto Palla

Ora creiamo la palla, l'elemento essenziale del nostro gioco.

### 6.1 Crea l'Oggetto

1. Crea un nuovo oggetto chiamato `obj_ball`
2. Assegna lo sprite `spr_ball`
3. Spunta la casella **Solido**

### 6.2 Movimento Iniziale

Vogliamo che la palla si muova da sola dall'inizio. Diamole una velocita e una direzione iniziali.

1. Clicca **Aggiungi Evento** -> **Creazione**
   > L'evento Creazione esegue azioni quando l'oggetto appare nel gioco, cioe quando entra nella scena.
2. Aggiungi l'azione **Imposta Velocita Orizzontale** con valore `4`
3. Aggiungi l'azione **Imposta Velocita Verticale** con valore `-4`
4. Clicca **OK**

Questo da alla palla un movimento diagonale (destra e su) all'inizio del gioco.

### 6.3 Rimbalzo sulla Racchetta

Dobbiamo far rimbalzare la palla quando colpisce la racchetta.

1. Clicca **Aggiungi Evento** -> **Collisione** -> seleziona `obj_paddle`
   > Questo evento si attiva quando la palla collide con la racchetta.
2. Aggiungi l'azione **Inverti Verticale**
   > Questo inverte la direzione verticale, facendo rimbalzare la palla.
3. Clicca **OK**

### 6.4 Rimbalzo sui Muri

Stessa operazione per i mattoni muro:

1. Clicca **Aggiungi Evento** -> **Collisione** -> seleziona `obj_brick_3`
2. Aggiungi l'azione **Inverti Verticale**
3. Aggiungi l'azione **Inverti Orizzontale**
   > Aggiungiamo entrambi perche la palla potrebbe colpire il muro da angoli diversi.
4. Clicca **OK**

---

## Passo 7: Testare i Nostri Progressi - Creazione di una Stanza

Dopo Sprite e Oggetti, ecco le **Stanze**. Una stanza e dove si svolge il gioco: e una mappa, un livello. Qui e dove posizioni tutti gli elementi del tuo gioco, dove organizzi cio che apparira sullo schermo.

### 7.1 Crea la Stanza

1. Fai clic destro su **Rooms** -> **Crea Stanza**
2. Chiamala `room_game`

### 7.2 Posiziona i Tuoi Oggetti

Ora posiziona i tuoi oggetti usando il mouse:
- **Clic sinistro** per posizionare un oggetto
- **Clic destro** per eliminare un oggetto

Seleziona l'oggetto da posizionare dal menu a tendina nell'editor della stanza.

**Costruisci il tuo livello:**
1. Posiziona istanze di `obj_brick_3` lungo i bordi (alto, sinistra, destra) - lascia il basso aperto!
2. Posiziona `obj_paddle` al centro in basso
3. Posiziona `obj_ball` da qualche parte nel mezzo

### 7.3 Testa il Gioco!

Clicca il pulsante **Gioca** (freccia verde) nella barra degli strumenti. Questo ti permette di testare il tuo gioco in qualsiasi momento.

Puoi gia divertirti a far rimbalzare la palla sui muri e sulla racchetta!

E minimo, ma gia un buon inizio - hai le fondamenta del tuo gioco!

---

## Passo 8: Aggiunta dei Mattoni Distruttibili

Aggiungiamo dei mattoni da rompere, per rendere il nostro gioco piu divertente.

### 8.1 Primo Mattone Distruttibile

1. Crea un nuovo oggetto chiamato `obj_brick_1`
2. Assegna lo sprite `spr_brick_1`
3. Spunta **Solido**

Aggiungeremo il comportamento per distruggersi quando colpito dalla palla:

1. Clicca **Aggiungi Evento** -> **Collisione** -> seleziona `obj_ball`
2. Aggiungi l'azione **Distruggi Istanza** con bersaglio **se stesso**
   > Questa azione rimuove un oggetto durante il gioco - qui, il mattone stesso.
3. Clicca **OK**

E cosi, hai il tuo nuovo mattone distruttibile!

### 8.2 Secondo Mattone Distruttibile (Usando il Genitore)

Ora creeremo un secondo mattone distruttibile, ma senza doverlo riprogrammare. Lo renderemo un "clone" usando la funzione **Genitore**.

1. Crea un nuovo oggetto chiamato `obj_brick_2`
2. Assegna lo sprite `spr_brick_2`
3. Spunta **Solido**
4. Nel menu a tendina **Genitore**, seleziona `obj_brick_1`

Cosa significa questo? Semplicemente che cio che abbiamo programmato in `obj_brick_1` sara ereditato da `obj_brick_2`, senza doverlo riprodurre noi stessi. La relazione genitore-figlio permette agli oggetti di condividere comportamenti!

Clicca **OK** per salvare.

### 8.3 Far Rimbalzare la Palla sui Nuovi Mattoni

Riapri `obj_ball` facendo doppio clic su di esso, e aggiungi eventi di collisione per i nostri nuovi mattoni:

1. Clicca **Aggiungi Evento** -> **Collisione** -> seleziona `obj_brick_1`
2. Aggiungi l'azione **Inverti Verticale**
3. Clicca **OK**

4. Clicca **Aggiungi Evento** -> **Collisione** -> seleziona `obj_brick_2`
5. Aggiungi l'azione **Inverti Verticale**
6. Clicca **OK**

---

## Passo 9: Game Over - Riavvio della Stanza

Dobbiamo riavviare il livello se la palla esce dallo schermo (se il giocatore non riesce a prenderla).

In `obj_ball`:

1. Clicca **Aggiungi Evento** -> **Altro** -> **Fuori dalla Stanza**
2. Aggiungi l'azione **Riavvia Stanza**
   > Questa azione riavvia la stanza corrente durante il gioco.
3. Clicca **OK**

---

## Passo 10: Design Finale del Livello

Ora posiziona tutto nella tua stanza per creare il tuo livello Breakout finale:

1. Apri `room_game`
2. Disponi i muri `obj_brick_3` in alto e sui lati
3. Posiziona file di `obj_brick_1` e `obj_brick_2` in schemi nella parte alta
4. Mantieni `obj_paddle` al centro in basso
5. Posiziona `obj_ball` sopra la racchetta

**Esempio di disposizione:**
```
[3][3][3][3][3][3][3][3][3][3]
[3][1][1][2][2][1][1][2][2][3]
[3][2][2][1][1][2][2][1][1][3]
[3][1][1][2][2][1][1][2][2][3]
[3]                        [3]
[3]                        [3]
[3]         (palla)        [3]
[3]                        [3]
[3]       [racchetta]      [3]
```

---

## Congratulazioni!

Il tuo gioco Breakout e completo! Ora puoi goderti il tuo lavoro giocando al gioco che hai appena creato!

Puoi anche perfezionarlo ulteriormente, ad esempio aggiungendo:
- **Effetti sonori** per rimbalzi e distruzione dei mattoni
- **Tracciamento del punteggio** usando l'azione Aggiungi Punteggio
- **Tipi di mattoni aggiuntivi** con comportamenti diversi
- **Livelli multipli** con disposizioni diverse

---

## Riepilogo di Cio Che Hai Imparato

| Concetto | Descrizione |
|----------|-------------|
| **Sprite** | Immagini visive che rappresentano gli oggetti nel tuo gioco |
| **Oggetti** | Entita di gioco con comportamenti, che combinano sprite con eventi e azioni |
| **Eventi** | Trigger che eseguono azioni (Creazione, Tastiera, Collisione, ecc.) |
| **Azioni** | Operazioni da eseguire (Muovi, Distruggi, Rimbalza, ecc.) |
| **Solido** | Proprieta che abilita il rilevamento delle collisioni |
| **Genitore** | Permette agli oggetti di ereditare comportamenti da altri oggetti |
| **Stanze** | Livelli di gioco dove posizioni le istanze degli oggetti |

---

## Riepilogo degli Oggetti

| Oggetto | Sprite | Solido | Eventi |
|---------|--------|--------|--------|
| `obj_paddle` | `spr_paddle` | Si | Tastiera (Sinistra/Destra), Rilascio Tasto |
| `obj_ball` | `spr_ball` | Si | Creazione, Collisione (racchetta, mattoni), Fuori dalla Stanza |
| `obj_brick_1` | `spr_brick_1` | Si | Collisione (palla) - Distruggi se stesso |
| `obj_brick_2` | `spr_brick_2` | Si | Eredita da `obj_brick_1` |
| `obj_brick_3` | `spr_brick_3` | Si | Nessuno (solo un muro) |

---

## Vedi Anche

- [Preset per Principianti](Beginner-Preset_it) - Eventi e azioni disponibili per principianti
- [Riferimento Eventi](Event-Reference_it) - Lista completa di tutti gli eventi
- [Riferimento Completo Azioni](Full-Action-Reference_it) - Lista completa di tutte le azioni
- [Tutorial: Breakout](Tutorial-Breakout_it) - Versione piu breve di questo tutorial

---

Ora sei iniziato alle basi della creazione di videogiochi con PyGameMaker. Tocca a te creare i tuoi giochi!
