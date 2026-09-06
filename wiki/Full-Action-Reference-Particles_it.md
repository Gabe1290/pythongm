# Particles

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Emetti particelle

| Proprietà | Valore |
|----------|-------|
| **Nome** | `burst_particles` |
| **Icona** | 💥 |
| **Categoria** | Particles |

Emette una raffica singola di particelle dall'emettitore creato più di recente

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `particle_type` | Numero | `0` | Particle type id (from Create Particle Type) |
| `number` | Numero | `10` | Number of particles to emit |

### Cancella particelle

| Proprietà | Valore |
|----------|-------|
| **Nome** | `clear_particles` |
| **Icona** | 🧹 |
| **Categoria** | Particles |

Rimuove tutte le particelle attive, ma conserva i tipi di particella e gli emettitori

*Parametri:* nessuno

### Crea emettitore

| Proprietà | Valore |
|----------|-------|
| **Nome** | `create_emitter` |
| **Icona** | 🌀 |
| **Categoria** | Particles |

Crea un'area emettitrice di particelle (l'identificatore restituito viene ricordato per la prossima azione che usa un emettitore)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Emitter center X (room coordinates) |
| `y` | Numero | `0` | Emitter center Y (room coordinates) |
| `width` | Numero | `0` | Emitter area width |
| `height` | Numero | `0` | Emitter area height |
| `shape` | Scelta | `rectangle` | Shape of the emitter area particles spawn within; Scelte: `rectangle`, `ellipse`, `diamond`, `line` |

### Crea sistema di particelle

| Proprietà | Valore |
|----------|-------|
| **Nome** | `create_particle_system` |
| **Icona** | ✨ |
| **Categoria** | Particles |

Crea un sistema di particelle collegato a questa istanza (sostituisce quello esistente)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `depth` | Numero | `0` | Drawing depth for the particle system (not yet used for cross-instance sort order) |

### Crea tipo di particella

| Proprietà | Valore |
|----------|-------|
| **Nome** | `create_particle_type` |
| **Icona** | ⚙️ |
| **Categoria** | Particles |

Definisce un nuovo aspetto o comportamento di particella (l'identificatore di tipo restituito viene ricordato per la prossima azione che usa un tipo di particella)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite to draw each particle as; leave empty for a plain colored circle; facoltativo |
| `size_min` | Numero | `1.0` | Minimum particle size (scale factor) |
| `size_max` | Numero | `1.0` | Maximum particle size (scale factor) |
| `size_increase` | Numero | `0.0` | Size change per step (negative shrinks, floored at 0) |
| `color` | Colore | `#FFFFFF` | Particle color (used when no sprite is set) |
| `alpha` | Numero | `1.0` | Transparency (0=invisible, 1=opaque) |
| `speed_min` | Numero | `0.0` | Minimum movement speed |
| `speed_max` | Numero | `0.0` | Maximum movement speed |
| `direction_min` | Numero | `0` | Minimum direction angle (0=right, 90=up) |
| `direction_max` | Numero | `360` | Maximum direction angle |
| `life_min` | Numero | `100` | Minimum lifetime in steps |
| `life_max` | Numero | `100` | Maximum lifetime in steps |

### Elimina emettitore

| Proprietà | Valore |
|----------|-------|
| **Nome** | `destroy_emitter` |
| **Icona** | 💥 |
| **Categoria** | Particles |

Elimina l'emettitore creato più di recente

*Parametri:* nessuno

### Elimina sistema di particelle

| Proprietà | Valore |
|----------|-------|
| **Nome** | `destroy_particle_system` |
| **Icona** | 💥 |
| **Categoria** | Particles |

Rimuove il sistema di particelle di questa istanza, cancellando tutte le sue particelle e i suoi emettitori

*Parametri:* nessuno

### Emetti particelle in continuo

| Proprietà | Valore |
|----------|-------|
| **Nome** | `stream_particles` |
| **Icona** | 🌊 |
| **Categoria** | Particles |

Emette particelle in continuo, a ogni passo, dall'emettitore creato più di recente (0 per fermare)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `particle_type` | Numero | `0` | Particle type id (from Create Particle Type) |
| `number` | Numero | `1` | Particles to emit per step (0 stops streaming) |

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
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (16)
- [Network](Full-Action-Reference-Network-Actions_it) (15)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
