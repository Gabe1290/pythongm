# Controllo

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Verifica se vuoto

| Proprietà | Valore |
|----------|-------|
| **Nome** | `check_empty` |
| **Icona** | 🔍 |
| **Categoria** | Controllo |

Vero quando (x, y) è privo di collisioni. Usa con start_block/end_block per condizionare l'azione/le azioni successive, in stile GM

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Testo | `self.x` | Posizione X da verificare (espressione consentita, es. self.x + 32) |
| `y` | Testo | `self.y` | Posizione Y da verificare (espressione consentita, es. self.y + 32) |
| `relative` | Sì/No | No | Tratta X/Y come scostamenti dalla posizione di questa istanza invece che come coordinate assolute; facoltativo |
| `objects` | Scelta | `solid` | Quali istanze contano come occupanti la posizione; Scelte: `solid`, `all` |

### Commento

| Proprietà | Valore |
|----------|-------|
| **Nome** | `comment` |
| **Icona** | ⚠️ |
| **Categoria** | Controllo |

Un commento nell'elenco delle azioni (senza effetto in esecuzione)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `text` | Testo | — | Testo di commento libero; facoltativo |

### Altrimenti

| Proprietà | Valore |
|----------|-------|
| **Nome** | `else_action` |
| **Icona** | ⚡ |
| **Categoria** | Controllo |

Contrassegna il ramo «altrimenti» di una condizione

*Parametri:* nessuno

### Fine blocco

| Proprietà | Valore |
|----------|-------|
| **Nome** | `end_block` |
| **Icona** | 📁 |
| **Categoria** | Controllo |

Termina un blocco di azioni

*Parametri:* nessuno

### Esegui codice

| Proprietà | Valore |
|----------|-------|
| **Nome** | `execute_code` |
| **Icona** | 📜 |
| **Categoria** | Controllo |

Esegui un blocco di codice Python integrato

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `code` | Codice | — | Codice Python da valutare rispetto all'istanza |

### Esegui script

| Proprietà | Valore |
|----------|-------|
| **Nome** | `execute_script` |
| **Icona** | 📜 |
| **Categoria** | Controllo |

Esegui uno degli script del progetto

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `script` | Script | — | Nome dello script del progetto da eseguire |
| `arg0` | Testo | — | Disponibile nello script come argument0; facoltativo |
| `arg1` | Testo | — | Disponibile nello script come argument1; facoltativo |
| `arg2` | Testo | — | Disponibile nello script come argument2; facoltativo |
| `arg3` | Testo | — | Disponibile nello script come argument3; facoltativo |
| `arg4` | Testo | — | Disponibile nello script come argument4; facoltativo |

### Esci dall'evento

| Proprietà | Valore |
|----------|-------|
| **Nome** | `exit_event` |
| **Icona** | 🚪 |
| **Categoria** | Controllo |

Interrompi l'esecuzione delle azioni rimanenti in questo evento

*Parametri:* nessuno

### Se si può spingere

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_can_push` |
| **Icona** | 📦 |
| **Categoria** | Controllo |

Verifica se una cassa/un oggetto può essere spinto nella direzione corrente (stile Sokoban)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Scelta | `facing` | Direzione da verificare per la spinta; Scelte: `facing` |
| `object_type` | Testo | `box` | Tipo di oggetto spinto |
| `then_action` | Scelta | `push_and_move` | Azione se la spinta è possibile; Scelte: `push_and_move`, `none` |
| `else_action` | Scelta | `stop_movement` | Azione se la spinta è bloccata; Scelte: `stop_movement`, `none` |

### Se collisione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_collision` |
| **Icona** | ❓💥 |
| **Categoria** | Controllo |

Condizione: vero se l'istanza collidesse allo scostamento (x, y)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Scostamento orizzontale da verificare |
| `y` | Numero | `0` | Scostamento verticale da verificare |
| `object` | Testo | `any` | «any», «solid» o un nome di oggetto; Scelte: `any`, `solid`; facoltativo |
| `not_flag` | Sì/No | No | Nega il risultato; facoltativo |

### Se collisione in

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_collision_at` |
| **Icona** | 🎯 |
| **Categoria** | Controllo |

Verifica una collisione in una posizione

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Testo | `self.x + 32` | Espressione della posizione X |
| `y` | Testo | `self.y` | Espressione della posizione Y |
| `object_type` | Scelta | `any` | Tipo di oggetto da verificare; Scelte: `any`, `solid` |
| `then_actions` | Elenco azioni | — | Azioni se collisione trovata |
| `else_actions` | Elenco azioni | — | Azioni se nessuna collisione |

### Se condizione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_condition` |
| **Icona** | ❓ |
| **Categoria** | Controllo |

Verifica condizionale con azioni allora/altrimenti

*Parametri:* nessuno

### Se l'oggetto esiste

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_object_exists` |
| **Icona** | ❓ |
| **Categoria** | Controllo |

Condizione: vero se esiste almeno un'istanza dell'oggetto

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | — | Tipo di oggetto da verificare |
| `not_flag` | Sì/No | No | Nega il risultato (agisci quando l'oggetto NON esiste); facoltativo |

### Ripeti

| Proprietà | Valore |
|----------|-------|
| **Nome** | `repeat` |
| **Icona** | 🔁 |
| **Categoria** | Controllo |

Ripeti l'azione/il blocco successivo N volte

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `times` | Numero | `10` | Numero di ripetizioni |
| `actions` | Elenco azioni | — | Azioni da ripetere |

### Imposta variabile

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_variable` |
| **Icona** | 📝 |
| **Categoria** | Controllo |

Imposta una variabile di istanza o globale

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `variable` | Testo | — | Nome della variabile |
| `value` | Testo | `0` | Valore (numero, stringa o espressione) |
| `scope` | Scelta | `self` | Ambito della variabile; Scelte: `self`, `other`, `global` |
| `relative` | Sì/No | No | Aggiungi al valore attuale invece di sostituirlo |

### Inizio blocco

| Proprietà | Valore |
|----------|-------|
| **Nome** | `start_block` |
| **Icona** | 📂 |
| **Categoria** | Controllo |

Inizia un blocco di azioni (per il raggruppamento)

*Parametri:* nessuno

### Verifica probabilità

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_chance` |
| **Icona** | 🎲❓ |
| **Categoria** | Controllo |

Condizione: vero con probabilità 1 su «sides»

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `sides` | Numero | `6` | Una probabilità di 1 su N di essere vero |

### Verifica espressione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_expression` |
| **Icona** | ❓ |
| **Categoria** | Controllo |

Verifica se un'espressione è vera

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `expression` | Testo | — | Espressione da valutare (vero se >= 0.5) |
| `then_actions` | Elenco azioni | — | Azioni se vero |
| `else_actions` | Elenco azioni | — | Azioni se falso |

### Poni una domanda

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_question` |
| **Icona** | ❓💬 |
| **Categoria** | Controllo |

Condizione: mostra una finestra sì/no; vero se l'utente risponde sì

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `question` | Testo | `Continue?` | Domanda mostrata al giocatore |

### Verifica variabile

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_variable` |
| **Icona** | ❓ |
| **Categoria** | Controllo |

Verifica il valore di una variabile di istanza o globale

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `variable` | Testo | — | Nome della variabile |
| `value` | Testo | `0` | Valore da confrontare |
| `scope` | Scelta | `self` | Ambito della variabile; Scelte: `self`, `other`, `global` |
| `operation` | Scelta | `equal` | Operatore di confronto; Scelte: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (20)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (8)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (25)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (16)
- [Particles](Full-Action-Reference-Particles_it) (8)
- [Réseau](Full-Action-Reference-Network-Actions_it) (15)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
