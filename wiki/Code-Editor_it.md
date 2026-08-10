# Editor Codice

> [English](Code-Editor) | [Français](Code-Editor_fr) | [Deutsch](Code-Editor_de) | [Italiano](Code-Editor_it) | [Español](Code-Editor_es) | [Português](Code-Editor_pt) | [Русский](Code-Editor_ru) | [Slovenščina](Code-Editor_sl)

---

> [Torna alla Home](Home_it)

Ogni oggetto in PyGameMaker ha una scheda **Editor Codice** accanto a
Event List e Blockly — un terzo modo di lavorare con gli stessi eventi e
azioni, questa volta come vero Python. Non è un export a senso unico: il
codice che scrivi qui viene rianalizzato in eventi e azioni strutturati,
quindi resta sincronizzato con le altre due viste.

---

## Aprire l'Editor Codice

1. Apri un oggetto nell'Editor Oggetti
2. Clicca sulla scheda **💻 Editor Codice**

![L'Editor Codice in modalità "Visualizza Codice Generato": una classe
con un metodo per evento (on_create, on_step,
on_collision_obj_power, ...), che mostra il vero Python in cui
compilano i tuoi eventi e azioni visivi](images/code-editor.png)

---

## Due Modalità

Un menu a tendina in alto permette di passare dall'una all'altra:

### 📖 Visualizza Codice Generato

Sola lettura. Mostra il Python in cui compilano gli eventi e le azioni
attuali del tuo oggetto — un metodo per evento (`on_create`, `on_step`,
`on_collision_obj_nemico`, ...), che chiama `self.*` e `game.*` esattamente
come fa il motore di gioco. Un'azione per cui il generatore non ha una
corrispondenza Python pulita appare comunque, contrassegnata da un
commento (`# Unknown action: ...`) sopra la riga che ha prodotto — niente
è nascosto, nemmeno per i casi limite. Clicca su **🔄 Aggiorna** per
rigenerare dopo aver modificato gli eventi altrove.

### ✏️ Modifica Codice Personalizzato

Modificabile, con evidenziazione della sintassi Python. Inizia a
digitare (o modifica il codice iniziale ripreso dalla modalità
Visualizza) e PyGameMaker analizza la tua classe circa 1,5 secondi dopo
che smetti di digitare — una pillola di stato accanto alla barra degli
strumenti mostra **idle / busy / error / empty** durante il processo. Se
l'analisi ha successo, i tuoi metodi **sostituiscono** gli eventi e le
azioni dell'oggetto (non li uniscono) — qualunque metodo evento il tuo
codice definisca, diventa la lista eventi di quell'oggetto, visibile
immediatamente anche nelle schede Event List e Blockly.

Se l'analisi fallisce (un errore di sintassi, o codice che l'analizzatore
non riesce a ricondurre a eventi), la pillola di stato mostra l'errore e
nulla viene applicato — gli eventi del tuo oggetto restano come erano
finché il codice non viene analizzato correttamente.

---

## Perché Usarlo

- **Velocità** — alcune logiche (un calcolo con più rami, un ciclo, una
  formula puntuale) si scrivono più velocemente di quanto si assemblino
  con blocchi o una lista di azioni.
- **Ponte di apprendimento** — passa gli eventi di un oggetto costruito
  da un principiante in modalità Visualizza per vedere l'equivalente in
  codice reale, un passo naturale per uno studente che passa dalla
  programmazione visuale a Python.
- **Precisione** — tutto ciò che si esprime come un semplice metodo
  Python sull'oggetto funziona, senza aspettare che esista un'azione
  visiva corrispondente.

È lo stesso meccanismo sottostante dell'azione **Esegui Codice**
disponibile dalla lista azioni / Blockly (categoria *Control*) — la
scheda Editor Codice funziona semplicemente alla scala di un intero
oggetto invece che di una singola azione.

---

## Prossimi Passi

- [[Editor_Oggetti_it|Editor Oggetti]] - Dove si trova la scheda Editor Codice
- [[Programmazione_Visuale_it|Programmazione Visuale]] - La vista Blockly degli stessi eventi
- [[Eventi_e_Azioni_it|Eventi e Azioni]] - Cosa fa realmente ogni azione
