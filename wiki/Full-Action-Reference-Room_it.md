# Stanza

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Verifica stanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `check_room` |
| **Icona** | ❓🚪 |
| **Categoria** | Stanza |

Condizione: vero se la stanza corrente corrisponde

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `room` | Stanza | — | Stanza da confrontare |
| `not_flag` | Sì/No | No | Inverti il risultato; facoltativo |

### Termina gioco

| Proprietà | Valore |
|----------|-------|
| **Nome** | `game_end` |
| **Icona** | 🛑🎮 |
| **Categoria** | Stanza |

Termina il gioco

*Parametri:* nessuno

### Vai alla stanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `goto_room` |
| **Icona** | 🚪 |
| **Categoria** | Stanza |

Passa a una stanza specifica

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `room` | Stanza | — | Nome della stanza di destinazione |
| `transition` | Scelta | `none` | Effetto di transizione (attualmente accettato ma non renderizzato); Scelte: `none`; facoltativo |

### Se esiste stanza successiva

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_next_room_exists` |
| **Icona** | ❓➡️ |
| **Categoria** | Stanza |

Verifica se c'è una stanza successiva dopo quella corrente

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `then_actions` | Elenco azioni | — | Azioni se esiste la stanza successiva |
| `else_actions` | Elenco azioni | — | Azioni se la stanza successiva non esiste |

### Se esiste stanza precedente

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_previous_room_exists` |
| **Icona** | ❓⬅️ |
| **Categoria** | Stanza |

Verifica se c'è una stanza precedente prima di quella corrente

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `then_actions` | Elenco azioni | — | Azioni se esiste la stanza precedente |
| `else_actions` | Elenco azioni | — | Azioni se la stanza precedente non esiste |

### Stanza successiva

| Proprietà | Valore |
|----------|-------|
| **Nome** | `next_room` |
| **Icona** | ➡️ |
| **Categoria** | Stanza |

Vai alla stanza successiva

*Parametri:* nessuno

### Stanza precedente

| Proprietà | Valore |
|----------|-------|
| **Nome** | `previous_room` |
| **Icona** | ⬅️ |
| **Categoria** | Stanza |

Vai alla stanza precedente

*Parametri:* nessuno

### Riavvia stanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `restart_room` |
| **Icona** | 🔄 |
| **Categoria** | Stanza |

Riavvia la stanza corrente

*Parametri:* nessuno

### Imposta sfondo

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_background` |
| **Icona** | 🖼️ |
| **Categoria** | Stanza |

Imposta l'immagine di sfondo della stanza attuale, con opzioni di ripetizione e scorrimento

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `background` | Testo | — | Nome della risorsa di sfondo o sprite |
| `visible` | Sì/No | Sì | Mostra lo sfondo; facoltativo |
| `foreground` | Sì/No | No | Disegna davanti alle istanze invece che dietro; facoltativo |
| `tiled_h` | Sì/No | No | Ripeti lo sfondo sulla larghezza della stanza; facoltativo |
| `tiled_v` | Sì/No | No | Ripeti lo sfondo sull'altezza della stanza; facoltativo |
| `hspeed` | Numero | `0` | Velocità di scorrimento automatico orizzontale in pixel/fotogramma; facoltativo |
| `vspeed` | Numero | `0` | Velocità di scorrimento automatico verticale in pixel/fotogramma; facoltativo |

### Imposta colore di sfondo

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_background_color` |
| **Icona** | 🎨 |
| **Categoria** | Stanza |

Cambia il colore di sfondo della stanza attuale

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `color` | Colore | `#87CEEB` | Colore di sfondo |
| `show_color` | Sì/No | Sì | Se il colore di sfondo è visibile (disattivato riempie di nero); facoltativo |

### Imposta titolo stanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_room_caption` |
| **Icona** | 🏷️ |
| **Categoria** | Stanza |

Imposta il titolo della finestra di gioco

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `caption` | Testo | — | Testo del titolo della finestra |

### Imposta persistenza stanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_room_persistent` |
| **Icona** | 💾 |
| **Categoria** | Stanza |

Se la stanza attuale mantiene il suo stato attivo (posizioni delle istanze, istanze distrutte, ecc.) quando il giocatore la lascia e vi ritorna, invece di ricostruirla da zero dal suo layout originale ogni volta

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `persistent` | Sì/No | Sì | Mantieni lo stato di questa stanza tra una visita e l'altra |

### Imposta velocità stanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_room_speed` |
| **Icona** | ⏱️ |
| **Categoria** | Stanza |

Cambia il frame rate del gioco (fotogrammi al secondo)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `30` | Fotogrammi al secondo target (1-240) |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (20)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Tempo](Full-Action-Reference-Timing_it) (2)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (20)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (4)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
