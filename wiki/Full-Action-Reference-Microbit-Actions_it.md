# micro:bit

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Cancella il display

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_clear_display` |
| **Icona** | ⬛ |
| **Categoria** | micro:bit |

Spegnere tutti i LED e scartare ciò che era in attesa

*Parametri:* nessuno

### Se il pulsante è premuto

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_if_button` |
| **Icona** | 🔘 |
| **Categoria** | micro:bit |

Vero finché il pulsante resta premuto (A+B = entrambi)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `button` | Scelta | `a` | Scelte: `a`, `b`, `ab`, `logo` |

### Se c'è un gesto

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_if_gesture` |
| **Icona** | 🤝 |
| **Categoria** | micro:bit |

Vero finché la scheda si trova in questo gesto o posizione

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `gesture` | Scelta | `shake` | Scelte: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### Se la luminosità del LED

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_if_pixel` |
| **Icona** | 🔍 |
| **Categoria** | micro:bit |

Confrontare la luminosità di un LED (da 0 a 9) con un valore; per impostazione predefinita la domanda è «è acceso?»

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Testo | `0` |  |
| `y` | Testo | `0` |  |
| `comparison` | Scelta | `>` | Scelte: `<`, `<=`, `==`, `>=`, `>`, `!=`; facoltativo |
| `value` | Testo | `0` | facoltativo |

### Se c'è inclinazione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_if_tilt` |
| **Icona** | 📐 |
| **Categoria** | micro:bit |

Confrontare un asse dell'accelerometro (milli-g, da -2048 a 2048) con un valore

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `axis` | Scelta | `x` | Scelte: `x`, `y`, `z` |
| `comparison` | Scelta | `>` | Scelte: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Testo | `300` |  |

### Suona una melodia

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_play_melody` |
| **Icona** | 🎵 |
| **Categoria** | micro:bit |

Suonare una melodia integrata (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, POWER_UP…) oppure note tue come «C4:4 E G C5:8 R:4» (nota, ottava, :durata; R è una pausa)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `melody` | Testo | `DADADADUM` | Built-in name, or notes separated by spaces |
| `tempo` | Testo | `120` | facoltativo |

### Suona una nota

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_play_tone` |
| **Icona** | 🔔 |
| **Categoria** | micro:bit |

Emettere un segnale acustico a una frequenza per un certo numero di millisecondi. I suoni vengono messi in coda

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `frequency` | Testo | `440` | Pitch in hertz (440 = the note A) |
| `duration` | Testo | `500` | facoltativo |

### Leggi un sensore

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_read_sensor` |
| **Icona** | 📡 |
| **Categoria** | micro:bit |

Leggere un sensore della micro:bit in una variabile di questo oggetto (o in una variabile globale se il nome inizia con «global.»)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `sensor` | Scelta | `accelerometer x` | Scelte: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Testo | `sensor_value` | Variable that receives the reading |

### Scorri un testo

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_scroll_text` |
| **Icona** | 🔤 |
| **Categoria** | micro:bit |

Far scorrere un testo sul display a LED. Metti il testo tra virgolette ("Ciao"); altrimenti un trattino o un più viene letto come un calcolo. Le lettere accentate appaiono come ? come sulla scheda vera

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `text` | Testo | `"Hello"` | Text or expression to scroll |
| `delay` | Numero | `150` | Scroll speed (MicroPython default 150); facoltativo |

### Invia un messaggio radio

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_radio_send` |
| **Icona** | 📻 |
| **Categoria** | micro:bit |

Inviare un numero o un testo alle altre micro:bit dello stesso gruppo (non a questa). Ricevono l'evento «Messaggio radio ricevuto», con il valore in radio_number e radio_string. Metti il testo tra virgolette; viene troncato a 32 caratteri

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `value` | Testo | `1` | A number, an expression or quoted text |

### Luminosità del display

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_set_brightness` |
| **Icona** | 🔆 |
| **Categoria** | micro:bit |

Luminosità generale dei LED, da 0 (spento) a 255 (massimo)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `brightness` | Testo | `255` |  |

### Accendi un LED

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_set_pixel` |
| **Icona** | 💡 |
| **Categoria** | micro:bit |

Accendere subito un LED (x e y da 0 a 4, luminosità da 0 a 9)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Testo | `0` |  |
| `y` | Testo | `0` |  |
| `brightness` | Testo | `9` | facoltativo |

### Imposta il gruppo radio

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_radio_set_group` |
| **Icona** | 📡 |
| **Categoria** | micro:bit |

Scegliere il gruppo radio (da 0 a 255). Solo le micro:bit dello stesso gruppo si sentono; ogni scheda parte dal gruppo 0

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `group` | Testo | `0` |  |

### Mostra un'immagine

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_show_image` |
| **Icona** | ❤️ |
| **Categoria** | micro:bit |

Mostrare un'immagine sui LED: un nome (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL…) oppure cinque righe di cifre di luminosità come «09090:99999:99999:09990:00900». Le immagini vengono messe in coda

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `image` | Testo | `HEART` | Built-in image name, or 5 rows of 5 digits (0-9) separated by colons |
| `hold` | Numero | `0` | How long it stays before the next queued item (0 = until something else is shown); facoltativo |

### Mostra un numero

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_show_number` |
| **Icona** | 🔢 |
| **Categoria** | micro:bit |

Mostrare un numero: una cifra resta ferma, un numero più lungo scorre

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `value` | Testo | `0` | Number or expression |

### Ferma il suono

| Proprietà | Valore |
|----------|-------|
| **Nome** | `microbit_stop_sound` |
| **Icona** | 🔇 |
| **Categoria** | micro:bit |

Spegnere l'altoparlante e scartare i suoni in attesa

*Parametri:* nessuno

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
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (20)
- [Disegno](Full-Action-Reference-Drawing_it) (11)
- [Rete](Full-Action-Reference-Network-Actions_it) (22)
- [Particelle](Full-Action-Reference-Particles_it) (8)
- [Punteggio/Vite/Salute](Full-Action-Reference-Score-Lives-Health_it) (5)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
