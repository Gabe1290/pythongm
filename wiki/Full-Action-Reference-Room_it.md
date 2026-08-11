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

### Set Background

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_background` |
| **Icona** | 🖼️ |
| **Categoria** | Stanza |

Set the current room's background image, with tiling and scrolling options

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `background` | Testo | — | Background or sprite asset name |
| `visible` | Sì/No | Sì | Show the background; facoltativo |
| `foreground` | Sì/No | No | Draw in front of instances instead of behind them; facoltativo |
| `tiled_h` | Sì/No | No | Repeat the background across the width of the room; facoltativo |
| `tiled_v` | Sì/No | No | Repeat the background across the height of the room; facoltativo |
| `hspeed` | Numero | `0` | Horizontal auto-scroll speed in pixels/frame; facoltativo |
| `vspeed` | Numero | `0` | Vertical auto-scroll speed in pixels/frame; facoltativo |

### Set Background Color

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_background_color` |
| **Icona** | 🎨 |
| **Categoria** | Stanza |

Change the current room's background color

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `color` | Colore | `#87CEEB` | Background color |
| `show_color` | Sì/No | Sì | Whether the background color is visible (off fills black instead); facoltativo |

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

### Set Room Persistent

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_room_persistent` |
| **Icona** | 💾 |
| **Categoria** | Stanza |

Whether the current room keeps its live state (instance positions, destroyed instances, etc.) when the player leaves and later returns to it, instead of rebuilding fresh from its authored layout every revisit

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `persistent` | Sì/No | Sì | Keep this room's state across a revisit |

### Set Room Speed

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_room_speed` |
| **Icona** | ⏱️ |
| **Categoria** | Stanza |

Change the game's frame rate (frames per second)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `30` | Target frames per second (1-240) |

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
