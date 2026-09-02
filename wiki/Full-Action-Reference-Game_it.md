# Gioco

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Disegna freccia

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_arrow` |
| **Icona** | ➡️ |
| **Categoria** | Gioco |

Disegna una freccia da un punto a un altro

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x1` | Numero | `0` | X iniziale |
| `y1` | Numero | `0` | Y iniziale |
| `x2` | Numero | `100` | X punta |
| `y2` | Numero | `100` | Y punta |
| `tip_size` | Numero | `10` | Dimensione della punta della freccia in pixel |

### Disegna sfondo

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_background` |
| **Icona** | 🌄 |
| **Categoria** | Gioco |

Disegna un'immagine di sfondo, facoltativamente affiancata su tutto lo schermo

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `background` | Testo | — | Nome dell'asset di sfondo |
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `tiled` | Sì/No | No | Affianca su tutto lo schermo; facoltativo |

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

### Disegna ellisse

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_ellipse` |
| **Icona** | 🥚 |
| **Categoria** | Gioco |

Disegna un'ellisse piena o solo contorno entro un riquadro

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x1` | Numero | `0` | X sinistra |
| `y1` | Numero | `0` | Y superiore |
| `x2` | Numero | `100` | X destra |
| `y2` | Numero | `100` | Y inferiore |
| `filled` | Sì/No | Sì | Pieno o solo contorno; facoltativo |

### Disegna linea

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_line` |
| **Icona** | 📏 |
| **Categoria** | Gioco |

Disegna una linea tra due punti

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x1` | Numero | `0` | X iniziale |
| `y1` | Numero | `0` | Y iniziale |
| `x2` | Numero | `100` | X finale |
| `y2` | Numero | `100` | Y finale |

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

### Disegna testo scalato

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_scaled_text` |
| **Icona** | 🖍️ |
| **Categoria** | Gioco |

Disegna testo a una scala arbitraria

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `text` | Testo | — | Testo da disegnare |
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `xscale` | Numero | `1.0` | Fattore di scala orizzontale |
| `yscale` | Numero | `1.0` | Fattore di scala verticale |

### Disegna sprite

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_sprite` |
| **Icona** | 🖼️ |
| **Categoria** | Gioco |

Disegna un fotogramma di sprite in una posizione

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite da disegnare |
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `subimage` | Numero | `0` | Indice del fotogramma da disegnare |

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

### Disegna variabile

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_variable` |
| **Icona** | 🔢 |
| **Categoria** | Gioco |

Disegna il valore di una variabile sullo schermo

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `variable` | Testo | — | Nome della variabile (self.var, global.var o nome semplice) |

### Riempi schermo con colore

| Proprietà | Valore |
|----------|-------|
| **Nome** | `fill_color` |
| **Icona** | 🪣 |
| **Categoria** | Gioco |

Riempi l'intera area di visualizzazione con un colore uniforme

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `color` | Colore | `#000000` | Colore RGB esadecimale |

### Load Game

| Proprietà | Valore |
|----------|-------|
| **Nome** | `load_game` |
| **Icona** | 📂 |
| **Categoria** | Gioco |

Restore room, score/lives/health, global variables, and instance states from a save file

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `filename` | Testo | `savegame.sav` | Save file name to load (from the project's saves/ folder) |

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

### Save Game

| Proprietà | Valore |
|----------|-------|
| **Nome** | `save_game` |
| **Icona** | 💾 |
| **Categoria** | Gioco |

Save the current room, score/lives/health, global variables, and instance states to a file

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `filename` | Testo | `savegame.sav` | Save file name (written to the project's saves/ folder) |

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

### Imposta colore

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_color` |
| **Icona** | 🎨 |
| **Categoria** | Gioco |

Imposta il colore e la trasparenza di disegno per i disegni successivi

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `color` | Colore | `#FFFFFF` | Colore RGB esadecimale |
| `alpha` | Numero | `1.0` | Opacità 0.0–1.0; facoltativo |

### Imposta colore di disegno

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_draw_color` |
| **Icona** | 🎨 |
| **Categoria** | Gioco |

Imposta il colore usato dalle successive azioni draw_*

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `color` | Colore | `#000000` | Colore RGB esadecimale |

### Imposta font di disegno

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_draw_font` |
| **Icona** | 🔤 |
| **Categoria** | Gioco |

Imposta il font e l'allineamento per il successivo disegno del testo

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `font` | Testo | — | Nome dell'asset del font (vuoto = font predefinito); facoltativo |
| `halign` | Scelta | `left` | Allineamento orizzontale del testo; Scelte: `left`, `center`, `right` |
| `valign` | Scelta | `top` | Allineamento verticale del testo; Scelte: `top`, `middle`, `bottom` |

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

### Show Video

| Proprietà | Valore |
|----------|-------|
| **Nome** | `show_video` |
| **Icona** | 🎬 |
| **Categoria** | Gioco |

Play a video file in your system's default video player -- opens as a separate window, not rendered inside the game itself

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `filename` | Testo | — | Path to the video file |
| `fullscreen` | Sì/No | No | Request fullscreen playback (support depends on your system's player); facoltativo |

### Splash: Show Image

| Proprietà | Valore |
|----------|-------|
| **Nome** | `splash_show_image` |
| **Icona** | 🖼️ |
| **Categoria** | Gioco |

Show a sprite full-screen and pause the game until the player dismisses it

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `image` | Sprite | — | Sprite to display full-screen |

### Splash: Show Text

| Proprietà | Valore |
|----------|-------|
| **Nome** | `splash_show_text` |
| **Icona** | 💬 |
| **Categoria** | Gioco |

Show a message and pause the game until the player dismisses it

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `text` | Testo | — | Message to display |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (20)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (8)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (16)
- [Particles](Full-Action-Reference-Particles_it) (8)
- [Réseau](Full-Action-Reference-Network-Actions_it) (15)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
