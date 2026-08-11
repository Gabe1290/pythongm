# Movimento

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Rimbalza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `bounce` |
| **Categoria** | Movimento |

Rimbalza sugli oggetti solidi

*Parametri:* nessuno

### Salta alla posizione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `jump_to_position` |
| **Icona** | 📍 |
| **Categoria** | Movimento |

Sposta istantaneamente in una posizione

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `relative` | Sì/No | No | Aggiungi alla posizione corrente invece di impostarne una assoluta |

### Salta a posizione casuale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `jump_to_random` |
| **Icona** | 🎲↪️ |
| **Categoria** | Movimento |

Teletrasporta in una posizione casuale (facoltativamente allineata alla griglia)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `snap_h` | Numero | `1` | Aggancio orizzontale alla griglia (1 = nessun aggancio) |
| `snap_v` | Numero | `1` | Aggancio verticale alla griglia (1 = nessun aggancio) |

### Salta alla posizione iniziale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `jump_to_start` |
| **Icona** | ↩️ |
| **Categoria** | Movimento |

Riporta l'istanza alla sua posizione di creazione

*Parametri:* nessuno

### Movimento libero

| Proprietà | Valore |
|----------|-------|
| **Nome** | `move_free` |
| **Icona** | 🧭 |
| **Categoria** | Movimento |

Muovi in una direzione precisa (0-360 gradi)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Numero | `0` | Direzione in gradi (0=destra, 90=su, antiorario) |
| `speed` | Numero | `4.0` | Velocità di movimento |

### Muovi sulla griglia

| Proprietà | Valore |
|----------|-------|
| **Nome** | `move_grid` |
| **Icona** | ▦ |
| **Categoria** | Movimento |

Sposta di una cella della griglia nella direzione indicata

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Scelta | `right` | Direzione di movimento; Scelte: `left`, `right`, `up`, `down` |
| `grid_size` | Numero | `32` | Dimensione della cella della griglia in pixel |

### Muovi verso un punto

| Proprietà | Valore |
|----------|-------|
| **Nome** | `move_towards_point` |
| **Icona** | 🎯 |
| **Categoria** | Movimento |

Muovi verso un punto a una data velocità

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | X di destinazione |
| `y` | Numero | `0` | Y di destinazione |
| `speed` | Numero | `4.0` | Velocità di movimento |

### Muovi fino al contatto

| Proprietà | Valore |
|----------|-------|
| **Nome** | `move_to_contact` |
| **Icona** | 🎯 |
| **Categoria** | Movimento |

Muovi in una direzione fino a toccare un oggetto (o la distanza massima)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Testo | `direction` | Direzione in gradi (0=destra, 90=su, 180=sinistra, 270=giù) o un'espressione. Predefinito «direction» = l'orientamento corrente dell'istanza (aggancio alla collisione). |
| `max_distance` | Numero | `1000` | Distanza massima di movimento, in pixel |
| `object` | Oggetto | `all` | Fermati al contatto con: «all» tutte le istanze, «solid» solo oggetti solidi o un nome di oggetto specifico.; Scelte: `all`, `solid`; facoltativo |

### Inverti orizzontale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `reverse_horizontal` |
| **Icona** | ↔️ |
| **Categoria** | Movimento |

Inverti la direzione del movimento orizzontale

*Parametri:* nessuno

### Inverti verticale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `reverse_vertical` |
| **Icona** | ↕️ |
| **Categoria** | Movimento |

Inverti la direzione del movimento verticale

*Parametri:* nessuno

### Imposta direzione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_direction` |
| **Icona** | 🧭 |
| **Categoria** | Movimento |

Imposta la direzione del movimento

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Numero | `0` | Direzione in gradi (0=destra, 90=su) |

### Imposta direzione e velocità

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_direction_speed` |
| **Icona** | 🧭 |
| **Categoria** | Movimento |

Imposta la direzione (in gradi) e l'intensità della velocità dell'istanza

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Numero | `0` | Direzione in gradi (0=destra, 90=su) |
| `speed` | Numero | `4.0` | Velocità in pixel per fotogramma |

### Imposta attrito

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_friction` |
| **Icona** | 🛑 |
| **Categoria** | Movimento |

Imposta l'attrito (decelerazione)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `friction` | Numero | `0.1` | Quantità di attrito (sottratta dalla velocità a ogni passo) |

### Imposta gravità

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_gravity` |
| **Icona** | ⬇️ |
| **Categoria** | Movimento |

Imposta direzione e intensità della gravità

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Numero | `270` | Direzione della gravità in gradi (270=giù) |
| `gravity` | Numero | `0.5` | Intensità della gravità (aggiunta a ogni passo) |

### Imposta velocità orizzontale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_hspeed` |
| **Icona** | ↔️ |
| **Categoria** | Movimento |

Imposta la velocità di movimento orizzontale

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `0` | Velocità in pixel per fotogramma |

### Imposta velocità

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_speed` |
| **Icona** | ⚡ |
| **Categoria** | Movimento |

Imposta la velocità di movimento (intensità)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `0` | Velocità di movimento |

### Imposta velocità verticale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_vspeed` |
| **Icona** | ↕️ |
| **Categoria** | Movimento |

Imposta la velocità di movimento verticale

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `0` | Velocità in pixel per fotogramma |

### Inizia a muoverti (direzione)

| Proprietà | Valore |
|----------|-------|
| **Nome** | `start_moving_direction` |
| **Icona** | ➡️ |
| **Categoria** | Movimento |

Inizia a muoverti in una direzione a una data velocità

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `directions` | Scelta multipla | right | Direzione/i di movimento — selezionane una, o diverse per sceglierne una casuale a ogni passo. La cella centrale è lo stop.; Scelte: `up-left`, `up`, `up-right`, `left`, `stop`, `right`, `down-left`, `down`, `down-right` |
| `direction_expr` | Testo | — | Alternativa: espressione libera valutata come gradi; facoltativo |
| `speed` | Numero | `4.0` | Velocità in pixel per fotogramma |

### Ferma il movimento

| Proprietà | Valore |
|----------|-------|
| **Nome** | `stop_movement` |
| **Icona** | 🛑 |
| **Categoria** | Movimento |

Azzera entrambe le velocità

*Parametri:* nessuno

### Avvolgi attorno alla stanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `wrap_around_room` |
| **Icona** | 🔄 |
| **Categoria** | Movimento |

Riappari dal lato opposto della stanza

*Parametri:* nessuno

---

## Altre Categorie

- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (2)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (20)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (4)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
