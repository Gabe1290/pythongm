# Gioco

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Disegna cerchio

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_circle` |
| **Icona** | ⭕ |
| **Categoria** | Gioco |

Disegna un cerchio pieno o solo contorno

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | X centro |
| `y` | Numero | `0` | Y centro |
| `radius` | Numero | `50` | Raggio del cerchio |
| `filled` | Sì/No | Sì | Pieno o solo contorno; facoltativo |

### Disegna rettangolo

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_rectangle` |
| **Icona** | 🟥 |
| **Categoria** | Gioco |

Disegna un rettangolo pieno o solo contorno

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x1` | Numero | `0` | X sinistra |
| `y1` | Numero | `0` | Y superiore |
| `x2` | Numero | `100` | X destra |
| `y2` | Numero | `100` | Y inferiore |
| `filled` | Sì/No | Sì | Pieno o solo contorno; facoltativo |

### Disegna testo

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_text` |
| **Icona** | 🖍️ |
| **Categoria** | Gioco |

Disegna una stringa di testo in una posizione

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `text` | Testo | — | Testo da disegnare (supporta espressioni) |
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `relative` | Sì/No | No | Disegna rispetto alla posizione di questa istanza invece che a coordinate schermo assolute; facoltativo |
| `color` | Colore | — | Colore del testo (per es. #ffffff). Vuoto = il colore di disegno attivo, altrimenti nero.; facoltativo |

### Carica la partita

| Proprietà | Valore |
|----------|-------|
| **Nome** | `load_game` |
| **Icona** | 📂 |
| **Categoria** | Gioco |

Ripristina la stanza, il punteggio, le vite, la salute, le variabili globali e lo stato delle istanze da un file di salvataggio

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `filename` | Testo | `savegame.sav` | Nome del file di salvataggio da caricare (dalla cartella saves/ del progetto) |

### Apri pagina web

| Proprietà | Valore |
|----------|-------|
| **Nome** | `open_webpage` |
| **Icona** | 🌐 |
| **Categoria** | Gioco |

Apri un URL nel browser predefinito

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `url` | Testo | — | Indirizzo web da aprire |

### Riavvia gioco

| Proprietà | Valore |
|----------|-------|
| **Nome** | `restart_game` |
| **Icona** | 🔁🎮 |
| **Categoria** | Gioco |

Riavvia il gioco dalla stanza iniziale

*Parametri:* nessuno

### Salva la partita

| Proprietà | Valore |
|----------|-------|
| **Nome** | `save_game` |
| **Icona** | 💾 |
| **Categoria** | Gioco |

Salva in un file la stanza corrente, il punteggio, le vite, la salute, le variabili globali e lo stato delle istanze

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `filename` | Testo | `savegame.sav` | Nome del file di salvataggio (scritto nella cartella saves/ del progetto) |

### Imposta trasparenza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_alpha` |
| **Icona** | 🌫️ |
| **Categoria** | Gioco |

Imposta la trasparenza di disegno per i disegni successivi

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `alpha` | Numero | `1.0` | Opacità da 0.0 (trasparente) a 1.0 (opaco) |

### Imposta titolo finestra

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_window_caption` |
| **Icona** | 🪟 |
| **Categoria** | Gioco |

Configura la visualizzazione di punteggio/vite/salute nel titolo della finestra

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `show_score` | Sì/No | Sì | Aggiungi il punteggio attuale al titolo della finestra |
| `show_lives` | Sì/No | Sì | Aggiungi il numero di vite attuale al titolo della finestra |
| `show_health` | Sì/No | No | Aggiungi il valore della salute attuale al titolo della finestra |
| `caption` | Testo | — | Prefisso del titolo facoltativo mostrato prima dei contatori; facoltativo |

### Mostra info gioco

| Proprietà | Valore |
|----------|-------|
| **Nome** | `show_info` |
| **Icona** | ℹ️ |
| **Categoria** | Gioco |

Mostra la schermata delle informazioni del gioco

*Parametri:* nessuno

### Mostra messaggio

| Proprietà | Valore |
|----------|-------|
| **Nome** | `show_message` |
| **Icona** | 💬 |
| **Categoria** | Gioco |

Mostra un messaggio

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `message` | Testo | `Hello!` | Testo del messaggio |

### Mostra un video

| Proprietà | Valore |
|----------|-------|
| **Nome** | `show_video` |
| **Icona** | 🎬 |
| **Categoria** | Gioco |

Riproduce un file video nel lettore video predefinito del sistema: si apre in una finestra separata, non viene disegnato dentro il gioco

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `filename` | Testo | — | Percorso del file video |
| `fullscreen` | Sì/No | No | Chiedere la riproduzione a schermo intero (dipende dal lettore del tuo sistema); facoltativo |

### Schermata: mostra immagine

| Proprietà | Valore |
|----------|-------|
| **Nome** | `splash_show_image` |
| **Icona** | 🖼️ |
| **Categoria** | Gioco |

Mostra uno sprite a schermo intero e mette il gioco in pausa finché il giocatore non lo chiude

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `image` | Sprite | — | Sprite da mostrare a schermo intero |

### Schermata: mostra testo

| Proprietà | Valore |
|----------|-------|
| **Nome** | `splash_show_text` |
| **Icona** | 💬 |
| **Categoria** | Gioco |

Mostra un messaggio e mette il gioco in pausa finché il giocatore non lo chiude

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `text` | Testo | — | Messaggio da mostrare |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (21)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (6)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (8)
- [Audio](Full-Action-Reference-Audio_it) (6)
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
