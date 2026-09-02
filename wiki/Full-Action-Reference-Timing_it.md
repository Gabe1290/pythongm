# Tempo

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Pause Timeline

| Proprietà | Valore |
|----------|-------|
| **Nome** | `pause_timeline` |
| **Icona** | ⏸️ |
| **Categoria** | Tempo |

Pause timeline playback at the current position

*Parametri:* nessuno

### Imposta allarme

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_alarm` |
| **Icona** | ⏰ |
| **Categoria** | Tempo |

Imposta un allarme

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `alarm_number` | Numero | `0` | Quale allarme (0-11) |
| `steps` | Numero | `30` | Numero di passi prima che l'allarme scatti (30 = 0,5 s a 60 FPS) |

### Set Timeline

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_timeline` |
| **Icona** | ⏱️ |
| **Categoria** | Tempo |

Set this instance's timeline label and reset its position to 0 (bookkeeping only — see category note)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `timeline` | Testo | — | A label for your own reference; not a resource lookup |

### Set Timeline Position

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_timeline_position` |
| **Icona** | ⏱️ |
| **Categoria** | Tempo |

Set (or offset) this instance's timeline position

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `position` | Numero | `0` | Position in steps |
| `relative` | Sì/No | No | Add to the current position instead of setting it absolutely |

### Set Timeline Speed

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_timeline_speed` |
| **Icona** | ⏱️ |
| **Categoria** | Tempo |

Set the timeline playback speed multiplier

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `1.0` | 1.0=normal, 0.5=half speed, 2.0=double speed |

### Pausa

| Proprietà | Valore |
|----------|-------|
| **Nome** | `sleep` |
| **Icona** | 💤 |
| **Categoria** | Tempo |

Metti in pausa il gioco per un certo numero di millisecondi, poi continua. I suoni continuano a suonare durante la pausa (ad esempio per far finire un suono prima di cambiare stanza). Nota: il rendering e l'input sono congelati durante la pausa, quindi mantieni durate brevi

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `milliseconds` | Numero | `1000` | Durata della pausa, in millisecondi (1000 = 1 secondo) |

### Start Timeline

| Proprietà | Valore |
|----------|-------|
| **Nome** | `start_timeline` |
| **Icona** | ▶️ |
| **Categoria** | Tempo |

Begin or resume timeline playback from the current position

*Parametri:* nessuno

### Stop Timeline

| Proprietà | Valore |
|----------|-------|
| **Nome** | `stop_timeline` |
| **Icona** | ⏹️ |
| **Categoria** | Tempo |

Stop timeline playback and reset the position to 0

*Parametri:* nessuno

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (20)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (25)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (16)
- [Particles](Full-Action-Reference-Particles_it) (8)
- [Réseau](Full-Action-Reference-Network-Actions_it) (15)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
