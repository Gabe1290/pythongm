# micro:bit (simulatore di BBC micro:bit)

*[Home](Home_it) | [Riferimento completo delle azioni](Full-Action-Reference-Microbit-Actions_it) | [Estensioni](Extensions_it)*

---

PyGameMaker può mettere una **BBC micro:bit simulata** nella finestra del tuo
gioco: un display di 5×5 LED, i pulsanti **A** e **B**, un logo tattile, i pin
0/1/2, un accelerometro, sensori di luce, temperatura, bussola e suono, un
altoparlante e una radio — tutto disegnato sullo schermo e programmato con gli
stessi eventi e le stesse azioni del resto dell'IDE. Non serve alcun hardware.
È fornita dall'[estensione](Extensions_it) **micro:bit** integrata, che è
attiva di default.

L'esempio incluso **`microbit_1`** («Dado e umori») è un gioco completo: A e B
mostrano un viso felice e uno triste, scuotere lancia un dado, e toccare il logo
fa scorrere quanti lanci hai fatto.

---

## Per iniziare

1. Crea un oggetto il cui **nome inizia con `microbit`** (per esempio
   `microbit_1`) e posiziona una sua istanza in una stanza. Quell'oggetto *è* la
   micro:bit: il motore disegna la scheda sopra di esso e ne esegue il
   simulatore.
2. In **Impostazioni progetto → Estensioni**, spunta **micro:bit**. (Un progetto
   che usa già un'azione micro:bit ce l'ha attiva automaticamente; uno che non
   ne usa non vede mai i blocchi né le azioni micro:bit.)
3. Metti gli eventi **su quello stesso oggetto**: ogni azione micro:bit agisce
   sulla micro:bit che la esegue. Per esempio *Button A Pressed* → *Show Image*
   `HAPPY`.
4. **Testa gioco.** Fai clic sui pulsanti della scheda.

Un oggetto può diventare una micro:bit anche spuntando `is_microbit` sulla sua
istanza nella stanza. Più micro:bit nella stessa stanza vanno benissimo — è
questo che rende utile la radio.

---

## La scheda e come comandarla

| Sullo schermo | Mouse | Tastiera (opzionale) |
|---|---|---|
| Pulsante **A** / **B** | Clic (tenuto finché il mouse è premuto) | `A` / `B` |
| **A+B** insieme | Clic destro su uno dei pulsanti | tenere premuti `A` e `B` |
| **Logo** tattile (dorato, sopra il display) | Clic | — |
| Pin **0, 1, 2** (contatti lungo il bordo inferiore) | Clic | — |
| **Pad di inclinazione** | Trascina; il bordo vale un g e al rilascio torna in piano | tasti freccia |
| Pulsante **SHAKE** | Clic | `S` |
| Cursori **Light / Temp / Compass / Sound** | Trascina; il valore resta | — |

Le scorciatoie da tastiera sono **disattivate di default**, così non rubano mai
i tasti del tuo gioco. Attivale per una scheda con la proprietà dell'oggetto
`microbit_keyboard` (funziona anche la variabile d'istanza con lo stesso nome).

Altre proprietà dell'oggetto: `microbit_scale` (moltiplicatore di dimensione,
`1.0` di default, circa 220 px di larghezza) e `microbit_show_sensors`
(impostala su `false` per nascondere la barra dei sensori). Se l'oggetto ha uno
**sprite**, questo diventa il corpo della scheda e sopra vengono disegnati solo
i LED e i controlli.

Un clic sulla scheda non fa scattare anche i tuoi eventi del mouse.

---

## Le azioni (categoria **micro:bit**)

| Azione | Cosa fa |
|--------|---------|
| **Show Image** (`microbit_show_image`) | Il nome di un'immagine integrata (`HEART`, `HAPPY`, `SAD`, `YES`, `NO`, `ARROW_N`, `SKULL`… 64 in tutto) oppure cinque righe di cinque cifre di luminosità come `09090:99999:99999:09990:00900`. |
| **Scroll Text** (`microbit_scroll_text`) | Far scorrere un testo sul display (150 ms per colonna di default). |
| **Show Number** (`microbit_show_number`) | Una cifra resta ferma; i numeri più lunghi scorrono. |
| **Set LED** (`microbit_set_pixel`) | Accendere subito un LED: `x`, `y` da 0 a 4, luminosità da 0 a 9. |
| **Clear Display** (`microbit_clear_display`) | Spegnere tutti i LED e scartare ciò che era in coda. |
| **Set Display Brightness** (`microbit_set_brightness`) | Luminosità generale, da 0 a 255. |
| **Play Tone** (`microbit_play_tone`) | Un bip a una frequenza per un numero di millisecondi. |
| **Play Melody** (`microbit_play_melody`) | Una delle 21 melodie integrate (`DADADADUM`, `ENTERTAINER`, `POWER_UP`…) o le tue note: `"C4:4 E G C5:8 R:4"` (nota, ottava, `:durata`; `R` è una pausa). |
| **Stop Sound** (`microbit_stop_sound`) | Zittire l'altoparlante e scartare i suoni in coda. |
| **Set Radio Group** (`microbit_radio_set_group`) | Scegliere il gruppo radio, da 0 a 255. |
| **Send Radio Message** (`microbit_radio_send`) | Inviare un numero o un testo alle altre micro:bit del gruppo. |
| **Read Sensor** (`microbit_read_sensor`) | Mettere una lettura (accelerometro x/y/z, intensità, bussola, luce, temperatura, livello sonoro, pin 0–2 analogico) in una variabile — o in una variabile globale se il nome inizia con `global.`. |
| **If Button Pressed** (`microbit_if_button`) | Condizione: A, B, A+B o il logo sono tenuti premuti. |
| **If Gesture** (`microbit_if_gesture`) | Condizione: la scheda è in un gesto o in una posizione (`shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`…`8g`). |
| **If Tilt** (`microbit_if_tilt`) | Condizione: confrontare un asse dell'accelerometro (milli-g) con un valore. |
| **If LED Brightness** (`microbit_if_pixel`) | Condizione: confrontare la luminosità di un LED con un valore. |

Le condizioni proteggono l'azione o il blocco che le segue, in stile GameMaker.
Vedi il
[Riferimento completo delle azioni](Full-Action-Reference-Microbit-Actions_it)
per tutti i parametri.

> **Il testo va tra virgolette doppie.** `Scroll Text` e `Send Radio Message`
> leggono il loro valore come qualsiasi altra espressione, quindi `Score - 3` è
> un calcolo. Scrivi il testo letterale come `"Ciao"`. Il display ha solo ASCII
> stampabile; le lettere accentate compaiono come `?`, come sulla scheda reale.

---

## Gli eventi

Vengono generati sull'oggetto stesso della micro:bit:

| Evento | Scatta quando |
|--------|---------------|
| **Button A Pressed**, **Button B Pressed**, **Buttons A+B Pressed** | Il pulsante o i pulsanti vengono premuti. |
| **Logo Touched** | Il logo viene toccato. |
| **Pin 0 / 1 / 2 Touched** | Quel pin viene toccato. |
| **Shake**, **Logo Up**, **Logo Down**, **Tilt Left**, **Tilt Right**, **Screen Up**, **Screen Down**, **Free Fall**, **2g / 3g / 6g / 8g Impact** | La scheda rileva quel gesto (lo stesso algoritmo della micro:bit reale). |
| **Loud Sound** / **Quiet Sound** | Il livello del microfono supera la soglia di suono forte / tranquillo. |
| **Display Finished** | La coda del display ha riprodotto tutto. |
| **Sound Finished** | Tutte le note e le melodie in coda sono state riprodotte. |
| **Radio Message Received** | Un'altra micro:bit dello stesso gruppo ha inviato un messaggio. |

«Forever» è il normale evento **Step**.

### Radio

Ogni scheda parte nel gruppo 0. **Send Radio Message** consegna a ogni *altra*
micro:bit dello stesso gruppo (una scheda non sente mai se stessa, e un gruppo
diverso non sente nulla). Il ricevente riceve l'evento e due variabili:
`radio_number` (0 se il testo non è un numero) e `radio_string` (sempre il
testo). Il testo viene tagliato a 32 caratteri, come nella radio reale.

---

## Il tempo: la coda del display e del suono

Su una micro:bit reale, far scorrere un testo *blocca* il programma. Un gioco non
può bloccarsi, quindi le azioni del display vengono **messe in coda** e
riprodotte una dopo l'altra (al massimo 16; chiedere ciò che è già mostrato non
fa nulla). **Clear Display** svuota la coda e **Display Finished** ti dice
quando si è esaurita, così puoi concatenare le animazioni. I suoni si mettono in
coda allo stesso modo, con **Stop Sound** e **Sound Finished**.

Il suono è un'onda quadra, come il cicalino della scheda. Se il computer non ha
un dispositivo audio, viene saltato in silenzio (il simulatore lo registra
comunque).

---

## Esportazioni

L'esportazione **desktop** (Windows, Linux, macOS) impacchetta il motore reale,
quindi la micro:bit funziona esattamente come in «Testa gioco». Anche
l'esportazione **HTML5** ha il simulatore: la scheda e la barra dei sensori sono
disegnate nel browser, puoi fare clic o toccare i pulsanti, il logo e i pin,
trascinare il pad di inclinazione e i cursori, e l'altoparlante emette bip (i
browser consentono il suono solo dopo il primo clic o la prima pressione di un
tasto). Anche l'esportazione **Android/Kivy** ce l'ha: la scheda e la barra dei
sensori sono disegnate, puoi
toccare i pulsanti, il logo, i pin, il pad di inclinazione, il pulsante di
scossa e i cursori, gli eventi scattano e l'altoparlante riproduce le sue note.
Le scorciatoie da tastiera funzionano solo per una scheda la cui proprietà (o variabile)
`microbit_keyboard` è attiva. Una scheda viene riconosciuta dal nome del suo
oggetto (deve iniziare con `microbit`) o da `is_microbit` sulla sua istanza nella stanza.

---

## Esportazione MicroPython (su una vera micro:bit)

È un'esportazione di tipo diverso. Invece di un gioco per un altro computer,
trasforma il programma dei tuoi oggetti micro:bit in vero codice **MicroPython**
che gira su una scheda fisica.

1. Apri **File → Esporta codice micro:bit (MicroPython)...** (deve essere
   aperto un progetto).
2. Indica quale scheda hai: **V2 (2020 o successiva)**, **V1 (originale,
   2016-2020)** oppure **Entrambe (un solo file .hex per schede V1 e V2)**.
3. Scegli una cartella. Ogni oggetto micro:bit ha il suo programma,
   `<cartella>/<nome dell'oggetto>/main.py`.
4. Quando è stato esportato esattamente un oggetto, l'IDE offre due modi per
   metterlo sulla scheda. **Copiare sulla micro:bit?** copia `main.py` su una
   scheda collegata via USB che esegue già MicroPython (il programma parte poi
   da solo). **Creare un file .hex pronto da caricare?** produce un file `.hex`
   che trascini sull'unità USB **MICROBIT** della scheda — funziona anche su una
   scheda nuova che non ha mai eseguito MicroPython.

Tutte le azioni e condizioni micro:bit vengono tradotte, come anche *Set
Variable*, *Test Variable*, i blocchi e i commenti. Ogni evento diventa un
controllo all'interno di un unico ciclo. Le azioni di gioco che non hanno
significato su una scheda (stanze, sprite, punteggi…) non vengono esportate.
Nelle espressioni funzionano `irandom`, `random` e `choose`; le altre funzioni
di GameMaker non vengono tradotte.

La finestra di esportazione elenca ciò che non è stato possibile esportare:

- **Display Finished** e **Sound Finished** (le chiamate di display e suono
  della scheda aspettano già la propria fine).
- Su una scheda V1, ciò che richiede una V2: la lettura del livello sonoro, il
  logo tattile (*If Button Pressed* con il logo, **Logo Touched**) e gli eventi
  **Loud Sound** / **Quiet Sound**.
- Tutto il resto che non ha un equivalente in MicroPython.

**Dimensione:** il programma deve stare in 8.187 byte su una scheda V1 e in
20.150 byte su una V2. **Entrambe** crea un unico Universal Hex, quindi è
limitato dalla dimensione della V1 e viene esportato con le regole della V1.

> I file `.hex` sono stati verificati con il vero firmware della micro:bit, ma
> non ancora su una scheda fisica.

---

## E poi?

- Apri l'esempio **`microbit_1`** dalla scheda di benvenuto e leggi la sua guida.
- Prova due schede in una stanza, ciascuna con un *Set Radio Group*, e invia un
  messaggio da un pulsante.
- Previsto: un collegamento in tempo reale con una vera micro:bit via USB. Non è
  ancora disponibile.

Vedi anche: [Estensioni](Extensions_it), [Riferimento completo delle azioni](Full-Action-Reference-Microbit-Actions_it), [Riferimento degli eventi](Event-Reference_it).
