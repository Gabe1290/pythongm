# Gestione Risorse

> [English](Asset-Manager) | [Français](Asset-Manager_fr) | [Deutsch](Asset-Manager_de) | [Italiano](Asset-Manager_it)

---

> [Torna alla Home](Home_it)

Oltre al creare/rinominare/eliminare quotidiano nell'albero delle
risorse, PyGameMaker tiene traccia di **dove ogni risorsa viene
effettivamente usata**, mantiene le risorse eliminate recuperabili
invece di perderle per sempre, e può trovare sia risorse inutilizzate
sia file orfani che ingombrano la cartella del progetto. Tutto questo si
trova nel menu **Strumenti**.

---

## Filtrare l'Albero delle Risorse

Digita nella casella di filtro sopra l'albero delle risorse per
restringerlo ai nomi corrispondenti man mano che digiti. La
corrispondenza ignora maiuscole/minuscole e riguarda il nome grezzo
della risorsa; una categoria (Sprite, Oggetti, ...) si nasconde una
volta che tutti i suoi elementi figli sono filtrati, e riappare non
appena uno corrisponde di nuovo.

---

## Tracciamento dell'Utilizzo

Ogni eliminazione di risorsa ora verifica dove quella risorsa è
effettivamente referenziata — altri oggetti, stanze, azioni — prima che
tu confermi. Se `spr_giocatore` è usato da 3 oggetti, la conferma di
eliminazione lo dice invece di un avviso generico, così lo scopri
*prima* di eliminare qualcosa che romperebbe altre parti del progetto,
non dopo.

**Limitazione nota:** questa analisi vede solo ciò che le strutture dati
di PyGameMaker possono vedere — parametri di azione, target di
collisione, istanze di stanza, campi sprite/parent. Un nome di risorsa
usato solo dentro una stringa Python grezza nell'[[Code-Editor_it|Editor Codice]]
o nell'azione Esegui Codice (ad esempio `game.sounds['explosion'].play()`)
non è visibile a questa analisi.

---

## Ripristinare Risorse Eliminate (Cestino)

**Strumenti > Ripristina Risorse Eliminate...**

Eliminare una risorsa non la cancella immediatamente — i suoi file
vengono spostati in un Cestino locale al progetto e PyGameMaker tiene
traccia di cosa è stato eliminato, dove sono andati i suoi file, e
qualsiasi riferimento incrociato che è stato cancellato (per esempio, il
campo sprite di un oggetto svuotato perché lo sprite a cui puntava è
stato eliminato). Questa finestra di dialogo elenca tutto ciò che si
trova attualmente nel Cestino con tre azioni:

| Azione | Effetto |
|--------|---------|
| **Ripristina** | Riporta la risorsa esattamente com'era. Rifiuta di sovrascrivere se ora esiste una nuova risorsa con lo stesso nome — anche il ripristino non è distruttivo. |
| **Elimina Definitivamente** | Rimuove una singola voce del cestino per sempre |
| **Svuota Cestino** | Rimuove tutto ciò che si trova attualmente nel Cestino |

I riferimenti incrociati cancellati all'eliminazione **non** vengono
ricollegati automaticamente al ripristino — vedrai cosa è cambiato, così
puoi decidere se riconnetterlo invece di far indovinare a PyGameMaker.

I file nel cestino sono esclusi dagli export del progetto (zip/HTML5/
ecc.) — una risorsa eliminata non riappare mai silenziosamente in un
gioco pubblicato.

---

## Trovare Risorse Inutilizzate

**Strumenti > Trova Risorse Inutilizzate...**

Analizza l'intero progetto tramite la stessa analisi di utilizzo sopra e
elenca ogni risorsa senza alcun riferimento, raggruppata per categoria,
ciascuna con una casella di controllo. Seleziona quelle che vuoi
davvero eliminare (o **Seleziona Tutto**) e **Sposta Selezionati nel
Cestino** — stessa rete di sicurezza di qualsiasi altra eliminazione.

**Le stanze sono gestite con cautela.** Una stanza verso cui nessuno
naviga esplicitamente per nome — un gioco a stanza singola, o la primissima
stanza di un gioco — appare legittimamente come "inutilizzata" sotto un
conteggio puro dei riferimenti, ma eliminarla romperebbe il gioco. Le
stanze sono etichettate *"Stanze — non navigate esplicitamente"*
piuttosto che semplicemente "inutilizzate", e **Seleziona Tutto salta le
stanze** di proposito; puoi comunque selezionarne una individualmente se
sei sicuro.

---

## Trovare File Orfani

**Strumenti > Trova File Orfani...**

Il problema inverso: file presenti nella cartella del progetto
(`sprites/`, `sounds/`, `backgrounds/`, `fonts/`, `thumbnails/`) che non
hanno **nessuna** voce corrispondente nel progetto — lasciati da
un'operazione interrotta, o depositati a mano fuori dall'IDE. Li elenca
per categoria con lo stesso schema casella di controllo / Seleziona
Tutto / **Sposta Selezionati nel Cestino** delle risorse inutilizzate, e
include un proprio mini-pannello Cestino (Ripristina / Elimina
Definitivamente / Svuota) nella stessa finestra di dialogo — i file
orfani usano un archivio cestino separato dalle normali eliminazioni di
risorse, poiché non sono mai stati una vera voce project.json fin
dall'inizio.

---

## Pulisci Progetto

**Strumenti > Pulisci Progetto**

Una scansione con un clic per i file `.tmp` residui — i file temporanei
che il processo di salvataggio atomico di PyGameMaker crea e normalmente
rimuove da solo. Vengono toccati solo i file più vecchi di circa un
minuto, così un salvataggio in corso non è mai a rischio. Riporta quanti
file sono stati rimossi, o che non c'era nulla da pulire. A differenza
delle finestre di dialogo sopra, questi file non passano mai attraverso
il sistema delle risorse o il Cestino — un file `.tmp` non è mai la
copia autorevole di nulla, quindi viene eliminato direttamente.

---

## Prossimi Passi

- [[Editor_Stanze_it|Editor Stanze]] / [[Editor_Oggetti_it|Editor Oggetti]] - Da dove provengono la maggior parte dei riferimenti alle risorse
- [[FAQ_it|FAQ]] - Domande comuni, incluse quelle sulla sicurezza dei dati
