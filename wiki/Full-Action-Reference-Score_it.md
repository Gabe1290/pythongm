# Punteggio

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Disegna barra della salute

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_health_bar` |
| **Icona** | 🩺 |
| **Categoria** | Punteggio |

Disegna la salute attuale come una barra a due colori

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x1` | Numero | `0` | X sinistra |
| `y1` | Numero | `0` | Y superiore |
| `x2` | Numero | `100` | X destra |
| `y2` | Numero | `20` | Y inferiore |
| `back_color` | Colore | `#FF0000` | Colore di sfondo (vuoto) |
| `bar_color` | Colore | `#00FF00` | Colore di riempimento (salute) |

### Disegna vite

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_lives` |
| **Icona** | 🖍️❤️ |
| **Categoria** | Punteggio |

Disegna il numero di vite attuale come immagini di sprite ripetute

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `sprite` | Sprite | — | Sprite disegnato una volta per ogni vita rimanente; facoltativo |
| `scale` | Numero | `1.0` | Fattore di scala uniforme per l'icona della vita (1.0 = dimensione nativa); facoltativo |
| `relative` | Sì/No | No | Disegna rispetto alla posizione di questa istanza invece che a coordinate schermo assolute; facoltativo |

### Disegna punteggio

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_score` |
| **Icona** | 🖍️🏆 |
| **Categoria** | Punteggio |

Disegna il punteggio attuale sullo schermo

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `caption` | Testo | `Score: ` | Testo mostrato prima del valore del punteggio; facoltativo |
| `relative` | Sì/No | No | Disegna rispetto alla posizione di questa istanza invece che a coordinate schermo assolute; facoltativo |

### Imposta salute

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_health` |
| **Icona** | 💚 |
| **Categoria** | Punteggio |

Imposta la salute, o aggiungi ad essa con «Relativo»

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `value` | Numero | `100` | Valore della salute (0-100) |
| `relative` | Sì/No | No | Aggiungi alla salute attuale invece di sostituirla |

### Imposta vite

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_lives` |
| **Icona** | ❤️ |
| **Categoria** | Punteggio |

Imposta le vite, o aggiungi ad esse con «Relativo»

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `value` | Numero | `3` | Numero di vite |
| `relative` | Sì/No | No | Aggiungi alle vite attuali invece di sostituirle |

### Imposta punteggio

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_score` |
| **Icona** | 🏆 |
| **Categoria** | Punteggio |

Imposta il punteggio, o aggiungi ad esso con «Relativo»

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `value` | Numero | `0` | Valore del punteggio da impostare |
| `relative` | Sì/No | No | Aggiungi al punteggio attuale invece di sostituirlo |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (21)
- [Istanza](Full-Action-Reference-Instance_it) (12)
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
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_it) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_it) (16)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
