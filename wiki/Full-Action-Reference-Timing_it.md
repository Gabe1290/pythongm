# Tempo

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Metti in pausa la linea temporale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `pause_timeline` |
| **Icona** | ⏸️ |
| **Categoria** | Tempo |

Mette in pausa la riproduzione della linea temporale nella posizione corrente

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

### Imposta la linea temporale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_timeline` |
| **Icona** | ⏱️ |
| **Categoria** | Tempo |

Imposta l'etichetta della linea temporale di questa istanza e ne riporta la posizione a 0 (solo annotazione — vedi la nota della categoria)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `timeline` | Testo | — | Un'etichetta per uso personale; non cerca alcuna risorsa |

### Imposta la posizione nella linea temporale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_timeline_position` |
| **Icona** | ⏱️ |
| **Categoria** | Tempo |

Imposta (o sposta) la posizione di questa istanza sulla linea temporale

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `position` | Numero | `0` | Posizione, in passi |
| `relative` | Sì/No | No | Aggiungere alla posizione corrente invece di impostarla in modo assoluto |

### Imposta la velocità della linea temporale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_timeline_speed` |
| **Icona** | ⏱️ |
| **Categoria** | Tempo |

Imposta il moltiplicatore di velocità della linea temporale

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `1.0` | 1.0 = normale, 0.5 = metà velocità, 2.0 = doppia velocità |

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

### Avvia la linea temporale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `start_timeline` |
| **Icona** | ▶️ |
| **Categoria** | Tempo |

Avvia o riprende la linea temporale dalla posizione corrente

*Parametri:* nessuno

### Ferma la linea temporale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `stop_timeline` |
| **Icona** | ⏹️ |
| **Categoria** | Tempo |

Ferma la linea temporale e riporta la posizione a 0

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
- [Rete](Full-Action-Reference-Network-Actions_it) (15)
- [Particelle](Full-Action-Reference-Particles_it) (8)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
