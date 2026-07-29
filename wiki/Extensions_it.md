# Estensioni

*[Home](Home_it) | [Vista 3D](3D-View_it) | [Riferimento completo delle azioni](Full-Action-Reference_it)*

---

Un'**estensione** è un componente aggiuntivo autonomo che aggiunge funzionalità a
PyGameMaker senza modificare il motore di base. Un'estensione può contribuire:

- nuove **azioni** (appaiono nel selettore di azioni come qualsiasi azione integrata),
- un nuovo modo di **disegnare una stanza** (un renderer personalizzato), e
- il **codice di esportazione** corrispondente, così i giochi che la usano si
  esportano comunque verso HTML5 e Kivy/Android.

L'estensione integrata **2.5D Raycast** (la funzione [Vista 3D](3D-View_it)) è
l'esempio di riferimento: aggiunge quattro azioni "Vista 3D" e un renderer in prima
persona e si esporta verso tutti e tre i target.

---

## Attivazione e disattivazione

Le estensioni sono fornite **attivate**. Puoi disattivarne una (o attivarne una
fornita disattivata) senza modificare alcun codice, tramite la chiave `extensions`
nella tua configurazione — una mappa `nome cartella → attivo/disattivo`:

```json
"extensions": { "raycast_2_5d": false }
```

Una voce **assente** significa "usa il valore predefinito dell'estensione", così
nulla scompare mai perché una chiave mancava. Le modifiche hanno effetto al riavvio
successivo (le azioni si registrano all'avvio).

Con l'estensione 2.5D Raycast disattivata, una stanza che abilita la vista in prima
persona si renderizza semplicemente dall'alto.

---

## Quando un progetto necessita di un'estensione

Poiché un'estensione può essere disattivata, PyGameMaker ti aiuta a evitare sorprese:

- **Al caricamento**, se un progetto usa azioni di un'estensione attualmente
  disattivata, l'IDE mostra un avviso che nomina l'estensione e le funzioni
  interessate (così un gioco 3D non si renderizza silenziosamente dall'alto).
- **Al salvataggio** il progetto registra le estensioni da cui dipendono le sue
  azioni in `project.json` (un elenco `requires_extensions`) — una nota duratura che
  chiunque riceva il progetto può vedere. Un progetto che non usa azioni di
  estensioni omette semplicemente il campo.

---

## Estensioni e plugin

Entrambi aggiungono azioni; differiscono solo nel confezionamento:

| | Plugin | Estensione |
|---|--------|-----------|
| Forma | un singolo file `.py` in `plugins/` | una cartella in `extensions/` con un manifesto |
| Ideale per | un piccolo insieme di azioni | una funzione che copre più file e/o che disegna/esporta |
| Esempio | le azioni **Audio** (`plugins/audio_actions.py`) | **2.5D Raycast** (`extensions/raycast_2_5d/`) |

---

## Com'è fatta una cartella di estensione

Per i curiosi (e per chi ne scrive una), un'estensione è una cartella leggibile:

```
extensions/raycast_2_5d/
├── extension.json     # manifesto: nome, versione, attivo, provides_actions
├── actions.py         # gli schemi delle azioni (mostrati nel selettore)
├── handlers.py        # cosa fanno le azioni in esecuzione
├── renderer.py        # il renderer di stanza personalizzato (il raycaster)
├── state.py           # lo stato per stanza (nello spazio dei nomi della stanza)
├── hud.py             # i generatori di geometria minimappa / barra DOOM
├── export_html5.js    # il port HTML5, iniettato nell'esportazione web
├── export_kivy.py     # il port Kivy, iniettato nell'esportazione mobile/computer
└── README.md          # come tutto si incastra
```

L'elenco `provides_actions` del manifesto è ciò che permette all'IDE di nominare
l'estensione esatta quando un progetto ne necessita una disattivata.

---

## Vedi anche

- [Vista 3D](3D-View_it) — la funzione fornita dall'estensione integrata
- [Riferimento completo delle azioni](Full-Action-Reference_it) — anche le azioni delle estensioni appaiono qui
- [Esportare giochi](Esportare_Giochi_it) — le funzioni delle estensioni si trasferiscono nelle esportazioni
