# Domande Frequenti (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

> [Torna alla Home](Home_it)

---

## Domande Generali

### Cos'è PyGameMaker?

PyGameMaker è un IDE open-source per lo sviluppo di giochi, ispirato a GameMaker 7.0. Ti permette di creare giochi 2D usando la programmazione visuale (Google Blockly) o un sistema eventi-azioni, senza dover scrivere codice.

### PyGameMaker è gratuito?

Sì! PyGameMaker è completamente gratuito e open-source — il codice sorgente è sotto Licenza MIT, la documentazione sotto CC BY 4.0.

### Per quali piattaforme posso esportare?

- Windows (.exe standalone)
- HTML5 (browser web)
- Linux (eseguibile nativo)
- Mobile (iOS/Android tramite Kivy)

### Ho bisogno di esperienza di programmazione?

No! PyGameMaker è progettato per i principianti. Puoi creare giochi usando:
- Blocchi Blockly drag-and-drop
- Sistema eventi/azioni point-and-click
- Senza alcun codice

### È compatibile con i file GameMaker?

PyGameMaker è ispirato a GameMaker 7.0 ma usa un proprio formato di progetto. Non puoi importare direttamente i file GameMaker, ma i concetti e il flusso di lavoro sono simili.

---

## Installazione

### Quali sono i requisiti di sistema?

- Python 3.10 o superiore
- Windows, Linux o macOS
- Minimo 4 GB di RAM (8 GB consigliati)
- ~500 MB di spazio su disco

### Come installo PyGameMaker?

Vedi [[Iniziare_it]] per istruzioni di installazione dettagliate. Versione breve:

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
python -m venv venv
source venv/bin/activate  # oppure venv\Scripts\activate su Windows
pip install -r requirements.txt
python main.py
```

### Python non viene riconosciuto / non trovato

Assicurati che Python sia installato e aggiunto al PATH di sistema. Verifica eseguendo:

```bash
python --version
```

Se questo fallisce, reinstalla Python e attiva "Add Python to PATH" durante l'installazione.

### Ricevo errori di importazione all'avvio

Prova a reinstallare le dipendenze:

```bash
pip install -r requirements.txt --force-reinstall
```

---

## Progetti

### Dove vengono salvati i miei progetti?

I progetti vengono salvati in cartelle che scegli tu. Ogni progetto contiene:
- `project.json` - Il file principale del progetto
- Cartelle per sprite, suoni, oggetti, stanze, ecc.

### Posso avere più progetti aperti contemporaneamente?

Attualmente, PyGameMaker apre un progetto alla volta. Usa **File > Apri Progetto** per passare tra progetti.

### Come faccio il backup del mio progetto?

Copia semplicemente l'intera cartella del progetto. Tutti gli asset e le impostazioni sono contenuti al suo interno. Valuta anche l'uso di git per il controllo versione:

```bash
cd mio_progetto
git init
git add .
git commit -m "Backup iniziale"
```

### Il mio progetto non si apre / è corrotto

Prova questi passaggi:
1. Verifica che `project.json` esista e non sia vuoto
2. Apri `project.json` in un editor di testo per controllare errori JSON
3. Ripristina da un backup se disponibile
4. Controlla l'output della console per messaggi di errore specifici

---

## Oggetti ed Eventi

### Qual è la differenza tra un oggetto e un'istanza?

- **Oggetto**: Un modello/schema che definisce il comportamento
- **Istanza**: Una copia specifica di un oggetto posizionata in una stanza

Ad esempio, `obj_nemico` è un oggetto. Posizionare 5 nemici in una stanza crea 5 istanze di `obj_nemico`.

### Perché il mio evento non si attiva?

Cause comuni:
1. **Tipo di evento sbagliato**: Assicurati di usare l'evento giusto (es. "Key Press" invece di "Keyboard")
2. **Nessuna istanza**: L'oggetto deve avere istanze nella stanza
3. **Oggetto non visibile**: Controlla la proprietà visible
4. **Ordine di esecuzione**: Alcuni eventi vengono eseguiti prima di altri

### Come faccio interagire gli oggetti?

Usa gli eventi di collisione:
1. Apri l'oggetto che deve rilevare la collisione
2. Aggiungi l'evento **Collision with [altro_oggetto]**
3. Aggiungi le azioni per cosa succede alla collisione

### Qual è la differenza tra gli eventi "Keyboard" e "Key Press"?

- **Keyboard [tasto]**: Si attiva ad ogni frame finché il tasto è tenuto premuto
- **Key Press [tasto]**: Si attiva una volta quando il tasto viene premuto per la prima volta
- **Key Release [tasto]**: Si attiva una volta quando il tasto viene rilasciato

---

## Stanze

### Quale stanza si carica per prima?

La prima stanza nell'albero delle risorse (in alto nell'elenco) si carica all'avvio del gioco. Trascina le stanze per riordinarle.

### Come cambio stanza?

Usa le azioni per le stanze:
- **Next Room**: Vai alla stanza successiva nell'ordine
- **Previous Room**: Vai alla stanza precedente
- **Go to Room**: Salta a una stanza specifica

### Gli oggetti scompaiono quando cambio stanza

Gli oggetti vengono distrutti quando si lascia una stanza, a meno che non siano contrassegnati come **Persistent** nelle loro proprietà.

### La mia stanza è troppo grande/piccola sullo schermo

La dimensione della finestra di gioco corrisponde alle dimensioni della prima stanza. Puoi:
- Cambiare la dimensione della stanza per adattarla alla dimensione desiderata della finestra
- Usare le View per mostrare solo una parte della stanza

---

## Grafica e Sprite

### Quali formati immagine sono supportati?

- PNG (consigliato, supporta la trasparenza)
- JPEG/JPG
- BMP
- GIF (solo il primo frame)

### Il mio sprite appare nella posizione sbagliata

Controlla l'impostazione **Origine** nell'editor sprite. L'origine è il punto di ancoraggio per il posizionamento. Impostazioni comuni:
- In alto a sinistra (0, 0): Predefinita
- Centro: Buona per oggetti rotanti
- Centro in basso: Buona per i personaggi

### Come animo uno sprite?

1. Crea uno sprite con più frame (striscia orizzontale)
2. Imposta **Numero di Frame** nelle proprietà dello sprite
3. Regola la **Velocità di Animazione** (frame al secondo)

### Gli sprite sono sfocati

Questo accade quando si ridimensionano gli sprite. Per la pixel art, disabilita l'interpolazione/smoothing nelle impostazioni di gioco, se disponibile.

---

## Suoni e Musica

### Quali formati audio sono supportati?

- WAV (non compresso)
- OGG (consigliato per la musica)
- MP3

### Il suono non viene riprodotto

Controlla:
1. Che il file audio esista nella cartella sounds
2. Che il formato del file sia supportato
3. Che tu stia usando il nome del suono corretto nelle azioni
4. Il browser potrebbe richiedere un'interazione dell'utente (per HTML5)

### Come faccio la musica in loop?

Usa l'azione **Play Music** con l'opzione loop attivata, oppure **Play Sound** con il parametro loop impostato a vero.

---

## Esportazione

### Il mio gioco esportato non funziona

Problemi comuni:
- **Windows**: DLL mancanti — assicurati che l'intera cartella di output sia inclusa
- **HTML5**: Il browser blocca i file locali — ospitalo su un server
- **Asset mancanti**: Verifica che tutti i file siano inclusi

### Il file esportato è enorme

La dimensione del gioco include Python e tutte le librerie. Per ridurla:
- Rimuovi gli asset non usati
- Comprimi immagini e audio
- Usa formati appropriati (OGG invece di WAV)
- Attiva la compressione UPX per le build Windows

### Posso vendere i giochi creati con PyGameMaker?

Sì! I giochi che crei sono interamente tuoi e possono essere venduti. Il codice sorgente di PyGameMaker è sotto la permissiva Licenza MIT, quindi puoi usarlo liberamente in progetti commerciali — e, a differenza delle licenze copyleft, non sei obbligato a rendere open-source le tue modifiche.

---

## Blockly / Programmazione Visuale

### Dove trovo l'editor Blockly?

1. Apri un oggetto
2. Fai clic sulla scheda **Blockly** nell'editor oggetti
3. Appare l'area di lavoro di programmazione visuale

### Come passo da Blockly agli eventi?

Entrambi i sistemi lavorano sullo stesso oggetto. La scheda Blockly e la scheda Events mostrano viste diverse della stessa logica. Le modifiche in uno si riflettono nell'altro.

### I miei blocchi Blockly sono scomparsi

Controlla:
1. Di stare visualizzando l'oggetto corretto
2. Scorri l'area di lavoro (i blocchi potrebbero essere fuori schermo)
3. Controlla il livello di zoom

---

## Prestazioni

### Il mio gioco è lento

Suggerimenti per migliori prestazioni:
1. Riduci il numero di istanze
2. Evita calcoli pesanti negli eventi Step
3. Usa gli allarmi invece di contare i frame
4. Ottimizza le dimensioni degli sprite
5. Distruggi le istanze che lasciano la stanza

### L'evento Step viene eseguito troppo spesso

L'evento Step viene eseguito ad ogni frame (60 volte al secondo per impostazione predefinita). Usa:
- Allarmi per azioni ritardate
- Condizioni da verificare prima di operazioni pesanti
- Una velocità della stanza più bassa, se appropriato

---

## Ottenere Aiuto

### Dove posso segnalare bug?

Segnala i bug nella pagina [GitHub Issues](https://github.com/Gabe1290/pythongm/issues). Includi:
- Cosa ti aspettavi che succedesse
- Cosa è successo realmente
- Passi per riprodurre il problema
- Il tuo sistema operativo e la versione di Python

### Dove posso saperne di più?

- [[Iniziare_it]] - Installazione e nozioni di base
- [[Primo_Gioco_it]] - Tutorial passo-passo
- [[Eventi_e_Azioni_it]] - Riferimento completo
- [[Programmazione_Visuale_it]] - Guida a Blockly
