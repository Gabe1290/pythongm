# Particelle

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Emetti particelle

| Proprietà | Valore |
|----------|-------|
| **Nome** | `burst_particles` |
| **Icona** | 💥 |
| **Categoria** | Particelle |

Emette una raffica singola di particelle dall'emettitore creato più di recente

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `particle_type` | Numero | `0` | Identificatore del tipo di particella (da «Crea tipo di particella») |
| `number` | Numero | `10` | Numero di particelle da emettere |

### Cancella particelle

| Proprietà | Valore |
|----------|-------|
| **Nome** | `clear_particles` |
| **Icona** | 🧹 |
| **Categoria** | Particelle |

Rimuove tutte le particelle attive, ma conserva i tipi di particella e gli emettitori

*Parametri:* nessuno

### Crea emettitore

| Proprietà | Valore |
|----------|-------|
| **Nome** | `create_emitter` |
| **Icona** | 🌀 |
| **Categoria** | Particelle |

Crea un'area emettitrice di particelle (l'identificatore restituito viene ricordato per la prossima azione che usa un emettitore)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | X del centro dell'emettitore (coordinate della stanza) |
| `y` | Numero | `0` | Y del centro dell'emettitore (coordinate della stanza) |
| `width` | Numero | `0` | Larghezza dell'area emettitrice |
| `height` | Numero | `0` | Altezza dell'area emettitrice |
| `shape` | Scelta | `rectangle` | Forma dell'area emettitrice in cui nascono le particelle; Scelte: `rectangle`, `ellipse`, `diamond`, `line` |

### Crea sistema di particelle

| Proprietà | Valore |
|----------|-------|
| **Nome** | `create_particle_system` |
| **Icona** | ✨ |
| **Categoria** | Particelle |

Crea un sistema di particelle collegato a questa istanza (sostituisce quello esistente)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `depth` | Numero | `0` | Profondità di disegno del sistema di particelle (non ancora usata per l'ordine fra istanze) |

### Crea tipo di particella

| Proprietà | Valore |
|----------|-------|
| **Nome** | `create_particle_type` |
| **Icona** | ⚙️ |
| **Categoria** | Particelle |

Definisce un nuovo aspetto o comportamento di particella (l'identificatore di tipo restituito viene ricordato per la prossima azione che usa un tipo di particella)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite con cui disegnare ogni particella; lascia vuoto per un semplice cerchio colorato; facoltativo |
| `size_min` | Numero | `1.0` | Dimensione minima della particella (fattore di scala) |
| `size_max` | Numero | `1.0` | Dimensione massima della particella (fattore di scala) |
| `size_increase` | Numero | `0.0` | Variazione di dimensione per passo (negativo rimpicciolisce, con minimo 0) |
| `color` | Colore | `#FFFFFF` | Colore della particella (usato quando non è impostato uno sprite) |
| `alpha` | Numero | `1.0` | Trasparenza (0 = invisibile, 1 = opaca) |
| `speed_min` | Numero | `0.0` | Velocità di movimento minima |
| `speed_max` | Numero | `0.0` | Velocità di movimento massima |
| `direction_min` | Numero | `0` | Angolo di direzione minimo (0 = a destra, 90 = in alto) |
| `direction_max` | Numero | `360` | Angolo di direzione massimo |
| `life_min` | Numero | `100` | Durata minima, in passi |
| `life_max` | Numero | `100` | Durata massima, in passi |

### Elimina emettitore

| Proprietà | Valore |
|----------|-------|
| **Nome** | `destroy_emitter` |
| **Icona** | 💥 |
| **Categoria** | Particelle |

Elimina l'emettitore creato più di recente

*Parametri:* nessuno

### Elimina sistema di particelle

| Proprietà | Valore |
|----------|-------|
| **Nome** | `destroy_particle_system` |
| **Icona** | 💥 |
| **Categoria** | Particelle |

Rimuove il sistema di particelle di questa istanza, cancellando tutte le sue particelle e i suoi emettitori

*Parametri:* nessuno

### Emetti particelle in continuo

| Proprietà | Valore |
|----------|-------|
| **Nome** | `stream_particles` |
| **Icona** | 🌊 |
| **Categoria** | Particelle |

Emette particelle in continuo, a ogni passo, dall'emettitore creato più di recente (0 per fermare)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `particle_type` | Numero | `0` | Identificatore del tipo di particella (da «Crea tipo di particella») |
| `number` | Numero | `1` | Particelle emesse per passo (0 ferma l'emissione) |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (20)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (8)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (25)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (18)
- [Rete](Full-Action-Reference-Network-Actions_it) (15)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
