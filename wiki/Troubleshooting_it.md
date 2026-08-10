# Risoluzione dei Problemi

> [English](Troubleshooting) | [Français](Troubleshooting_fr) | [Deutsch](Troubleshooting_de) | [Italiano](Troubleshooting_it) | [Español](Troubleshooting_es) | [Português](Troubleshooting_pt) | [Русский](Troubleshooting_ru) | [Slovenščina](Troubleshooting_sl) | [Українська](Troubleshooting_uk)

---

> [Torna alla Home](Home_it)

Problemi comuni e dove guardare. Per problemi specifici
dell'installazione (Python non trovato, dipendenze mancanti, librerie
di visualizzazione Linux), vedi prima la sezione Risoluzione dei
Problemi di [[Iniziare_it|Per Iniziare]] — questa pagina copre i
problemi che si presentano quando PyGameMaker è già in esecuzione.

---

## Il mio gioco va in crash o si chiude immediatamente quando premo Testa Gioco (F5)

**Avvia l'IDE da un terminale, non da un collegamento del desktop, per
vedere l'errore.** Il traceback di un sottoprocesso di test del gioco
che va in crash viene registrato nell'output della console dell'IDE
stessa (`python main.py` in un terminale) — se hai avviato l'IDE senza
una console visibile (ad esempio un collegamento Windows), questo
messaggio non ha dove apparire. Riavvia da un terminale e riproduci il
crash per vedere il vero traceback Python.

Cause comuni:
- Un'azione **Esegui Codice** o codice personalizzato nell'Editor
  Codice con un errore di sintassi o un refuso in una chiamata
  `game.*`/`self.*`
- Un'azione di collisione o confronto che fa riferimento a un oggetto
  che è stato da allora rinominato o eliminato

---

## L'IDE stessa è andata in crash quando ho provato ad aprire un editor

Controlla **`~/pygamemaker_crash.log`** (nella tua cartella home) — i
crash dell'editor oggetti/stanze/sprite vengono scritti lì
specificamente per restare visibili anche quando l'IDE è stata avviata
senza una finestra di console. Includi la sezione rilevante di quel
file se segnali il bug.

---

## L'export dice "X non trovato" / manca una dipendenza

Gli export desktop e mobile (.exe Windows, .app macOS, binario Linux,
Kivy/Android/iOS) integrano un runtime tramite PyInstaller o Buildozer,
e questi strumenti devono essere installati nello **stesso Python che
esegue l'IDE** — un'installazione a livello di sistema altrove sulla
macchina non conta. Il messaggio di errore della finestra di dialogo di
export dà la soluzione esatta, ma in breve:

- **Nessun diritto amministrativo necessario.** Attiva il tuo ambiente
  virtuale ed esegui `pip install <pacchetto>`, oppure installa nel tuo
  account con `pip install --user <pacchetto>` — entrambi funzionano
  senza diritti admin.
- Installare tutto in una volta: `pip install -r requirements.txt`
- **Nessuna installazione del tutto?** Usa invece l'export **HTML5
  (Browser Web)** — non richiede nulla installato localmente e il
  risultato funziona in qualsiasi browser. (Nota che questo si applica
  solo alla *costruzione* dell'export — un `.exe`/`.app` finito non
  richiede nulla installato sulla macchina che lo *esegue* soltanto.)

---

## Ho ricevuto un avviso prima dell'Export ("X usa Y ma non c'è Z")

L'export esegue prima una convalida del progetto e mostra tutto ciò che
trova prima che appaia la finestra di dialogo Export — ad esempio un
oggetto che usa **Stanza Successiva** in un progetto con una sola
stanza, il che non avrebbe alcun effetto. Questi sono **avvisi, non
errori**: clicca OK e l'export continua; segnalano una logica che
probabilmente non farà quello che ti aspetti, senza impedirti di
pubblicare.

---

## Uno sprite mostra un badge rosso "(non importato)" nell'albero delle risorse

Significa che il file immagine dello sprite manca dal disco
(solitamente perché un progetto è stato copiato o condiviso senza la
sua cartella `sprites/`). È puramente informativo — l'esecuzione e
l'export lo ignorano — e **si corregge automaticamente al prossimo
salvataggio**, una volta che il file è effettivamente di nuovo
presente. Nessuna correzione manuale necessaria oltre ad assicurarsi
che il file immagine si trovi dove lo sprite se lo aspetta.

---

## Qualcos'altro non va

- Consulta la [[FAQ_it|FAQ]] per le domande comuni
- Segnala i bug sul [Tracker Problemi GitHub](https://github.com/Gabe1290/pythongm/issues) — includi il tuo OS, la tua versione di Python, e (se rilevante) l'output della console o `~/pygamemaker_crash.log`

---

## Prossimi Passi

- [[Iniziare_it|Per Iniziare]] - Risoluzione dei problemi di installazione
- [[Esportare_Giochi_it|Esportare Giochi]] - Riferimento completo dell'export
- [[FAQ_it|FAQ]] - Domande frequenti
