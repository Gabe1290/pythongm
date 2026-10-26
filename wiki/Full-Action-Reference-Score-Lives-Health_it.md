# Score/Lives/Health

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Cancella tabella dei record

| Proprietà | Valore |
|----------|-------|
| **Nome** | `clear_highscore` |
| **Icona** | 🗑️🏆 |
| **Categoria** | Score/Lives/Health |

Cancella tutte le voci della tabella dei record

*Parametri:* nessuno

### Mostra tabella dei record

| Proprietà | Valore |
|----------|-------|
| **Nome** | `show_highscore` |
| **Icona** | 🏆 |
| **Categoria** | Score/Lives/Health |

Mostra la finestra della tabella dei record

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `background` | Colore | `#FFFFDD` | Colore di sfondo della finestra; facoltativo |
| `new_color` | Colore | `#FF0000` | Colore usato per la nuova voce (idonea); facoltativo |
| `other_color` | Colore | `#000000` | Colore usato per le altre voci; facoltativo |
| `allow_new_entry` | Sì/No | Sì | Chiedi il nome se il punteggio attuale è idoneo |

### Verifica salute

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_health` |
| **Icona** | ❓💚 |
| **Categoria** | Score/Lives/Health |

Condizione: confronta la salute attuale con un valore

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `operation` | Scelta | `equal` | Operatore di confronto; Scelte: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |
| `value` | Numero | `0` | Valore di confronto |

### Verifica vite

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_lives` |
| **Icona** | ❓❤️ |
| **Categoria** | Score/Lives/Health |

Condizione: confronta il numero di vite con un valore

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `value` | Numero | `0` | Valore di confronto |
| `operation` | Scelta | `equal` | Operatore di confronto; Scelte: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

### Verifica punteggio

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_score` |
| **Icona** | ❓🏆 |
| **Categoria** | Score/Lives/Health |

Condizione: confronta il punteggio con un valore

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `value` | Numero | `0` | Valore di confronto |
| `operation` | Scelta | `equal` | Operatore di confronto; Scelte: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (21)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (6)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (8)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (14)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (3)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (18)
- [Disegno](Full-Action-Reference-Drawing_it) (11)
- [Rete](Full-Action-Reference-Network-Actions_it) (22)
- [Particelle](Full-Action-Reference-Particles_it) (8)
- [micro:bit](Full-Action-Reference-Microbit-Actions_it) (16)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
