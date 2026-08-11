# Tempo

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

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

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (20)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (20)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (4)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
