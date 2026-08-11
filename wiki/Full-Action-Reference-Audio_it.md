# Audio

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Verifica riproduzione suono

| Proprietà | Valore |
|----------|-------|
| **Nome** | `check_sound` |
| **Icona** | ❓🔊 |
| **Categoria** | Audio |

Condizione: vero se il suono indicato è attualmente in riproduzione

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `sound` | Suono | — | Suono da verificare |
| `not_flag` | Sì/No | No | Inverti il risultato; facoltativo |

### Riproduci musica

| Proprietà | Valore |
|----------|-------|
| **Nome** | `play_music` |
| **Icona** | 🎵 |
| **Categoria** | Audio |

Riproduci musica di sottofondo (in loop)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `music` | Suono | — | File musicale da riprodurre |
| `loop` | Sì/No | Sì | Riproduci la musica in loop |
| `volume` | Numero | `0.7` | Volume (da 0.0 a 1.0) |

### Riproduci suono

| Proprietà | Valore |
|----------|-------|
| **Nome** | `play_sound` |
| **Icona** | 🔊 |
| **Categoria** | Audio |

Riproduci un effetto sonoro una volta

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `sound` | Suono | — | Suono da riprodurre |
| `volume` | Numero | `1.0` | Volume (da 0.0 a 1.0) |

### Imposta volume

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_volume` |
| **Icona** | 🔉 |
| **Categoria** | Audio |

Imposta il volume generale di suoni/musica

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `volume` | Numero | `1.0` | Volume (da 0.0 a 1.0) |

### Ferma musica

| Proprietà | Valore |
|----------|-------|
| **Nome** | `stop_music` |
| **Icona** | 🔇 |
| **Categoria** | Audio |

Ferma la musica di sottofondo

*Parametri:* nessuno

### Ferma suono

| Proprietà | Valore |
|----------|-------|
| **Nome** | `stop_sound` |
| **Icona** | 🔇 |
| **Categoria** | Audio |

Ferma un suono in riproduzione

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `sound` | Suono | — | Suono da fermare |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (20)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (2)
- [Gioco](Full-Action-Reference-Game_it) (20)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (4)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
