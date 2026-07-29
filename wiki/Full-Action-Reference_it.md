# Riferimento completo delle azioni

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

Questa pagina elenca tutte le **109** azioni disponibili in PyGameMaker, esattamente come appaiono nel selettore di azioni dell'IDE (incluso il plugin Audio e l'estensione Vista 3D). Le azioni sono comandi che vengono eseguiti quando si attiva un evento.

## Categorie

- [Movimento](#movement) (20)
- [Istanza](#instance) (12)
- [Punteggio](#score) (11)
- [Stanza](#room) (9)
- [Tempo](#timing) (2)
- [Audio](#audio) (6)
- [Gioco](#game) (20)
- [Controllo](#control) (19)
- [Griglia](#grid) (4)
- [Viste](#views) (2)
- [Vista 3D](#3d-view) (4)

---

<a id="movement"></a>
## Movimento

### Rimbalza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `bounce` |
| **Categoria** | Movimento |

Rimbalza sugli oggetti solidi

*Parametri:* nessuno

### Salta alla posizione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `jump_to_position` |
| **Icona** | 📍 |
| **Categoria** | Movimento |

Sposta istantaneamente in una posizione

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `relative` | Sì/No | No | Aggiungi alla posizione corrente invece di impostarne una assoluta |

### Salta a posizione casuale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `jump_to_random` |
| **Icona** | 🎲↪️ |
| **Categoria** | Movimento |

Teletrasporta in una posizione casuale (facoltativamente allineata alla griglia)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `snap_h` | Numero | `1` | Aggancio orizzontale alla griglia (1 = nessun aggancio) |
| `snap_v` | Numero | `1` | Aggancio verticale alla griglia (1 = nessun aggancio) |

### Salta alla posizione iniziale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `jump_to_start` |
| **Icona** | ↩️ |
| **Categoria** | Movimento |

Riporta l'istanza alla sua posizione di creazione

*Parametri:* nessuno

### Movimento libero

| Proprietà | Valore |
|----------|-------|
| **Nome** | `move_free` |
| **Icona** | 🧭 |
| **Categoria** | Movimento |

Muovi in una direzione precisa (0-360 gradi)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Numero | `0` | Direzione in gradi (0=destra, 90=su, antiorario) |
| `speed` | Numero | `4.0` | Velocità di movimento |

### Muovi sulla griglia

| Proprietà | Valore |
|----------|-------|
| **Nome** | `move_grid` |
| **Icona** | ▦ |
| **Categoria** | Movimento |

Sposta di una cella della griglia nella direzione indicata

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Scelta | `right` | Direzione di movimento; Scelte: `left`, `right`, `up`, `down` |
| `grid_size` | Numero | `32` | Dimensione della cella della griglia in pixel |

### Muovi verso un punto

| Proprietà | Valore |
|----------|-------|
| **Nome** | `move_towards_point` |
| **Icona** | 🎯 |
| **Categoria** | Movimento |

Muovi verso un punto a una data velocità

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | X di destinazione |
| `y` | Numero | `0` | Y di destinazione |
| `speed` | Numero | `4.0` | Velocità di movimento |

### Muovi fino al contatto

| Proprietà | Valore |
|----------|-------|
| **Nome** | `move_to_contact` |
| **Icona** | 🎯 |
| **Categoria** | Movimento |

Muovi in una direzione fino a toccare un oggetto (o la distanza massima)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Testo | `direction` | Direzione in gradi (0=destra, 90=su, 180=sinistra, 270=giù) o un'espressione. Predefinito «direction» = l'orientamento corrente dell'istanza (aggancio alla collisione). |
| `max_distance` | Numero | `1000` | Distanza massima di movimento, in pixel |
| `object` | Oggetto | `all` | Fermati al contatto con: «all» tutte le istanze, «solid» solo oggetti solidi o un nome di oggetto specifico.; Scelte: `all`, `solid`; facoltativo |

### Inverti orizzontale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `reverse_horizontal` |
| **Icona** | ↔️ |
| **Categoria** | Movimento |

Inverti la direzione del movimento orizzontale

*Parametri:* nessuno

### Inverti verticale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `reverse_vertical` |
| **Icona** | ↕️ |
| **Categoria** | Movimento |

Inverti la direzione del movimento verticale

*Parametri:* nessuno

### Imposta direzione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_direction` |
| **Icona** | 🧭 |
| **Categoria** | Movimento |

Imposta la direzione del movimento

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Numero | `0` | Direzione in gradi (0=destra, 90=su) |

### Imposta direzione e velocità

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_direction_speed` |
| **Icona** | 🧭 |
| **Categoria** | Movimento |

Imposta la direzione (in gradi) e l'intensità della velocità dell'istanza

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Numero | `0` | Direzione in gradi (0=destra, 90=su) |
| `speed` | Numero | `4.0` | Velocità in pixel per fotogramma |

### Imposta attrito

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_friction` |
| **Icona** | 🛑 |
| **Categoria** | Movimento |

Imposta l'attrito (decelerazione)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `friction` | Numero | `0.1` | Quantità di attrito (sottratta dalla velocità a ogni passo) |

### Imposta gravità

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_gravity` |
| **Icona** | ⬇️ |
| **Categoria** | Movimento |

Imposta direzione e intensità della gravità

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Numero | `270` | Direzione della gravità in gradi (270=giù) |
| `gravity` | Numero | `0.5` | Intensità della gravità (aggiunta a ogni passo) |

### Imposta velocità orizzontale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_hspeed` |
| **Icona** | ↔️ |
| **Categoria** | Movimento |

Imposta la velocità di movimento orizzontale

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `0` | Velocità in pixel per fotogramma |

### Imposta velocità

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_speed` |
| **Icona** | ⚡ |
| **Categoria** | Movimento |

Imposta la velocità di movimento (intensità)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `0` | Velocità di movimento |

### Imposta velocità verticale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_vspeed` |
| **Icona** | ↕️ |
| **Categoria** | Movimento |

Imposta la velocità di movimento verticale

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `0` | Velocità in pixel per fotogramma |

### Inizia a muoverti (direzione)

| Proprietà | Valore |
|----------|-------|
| **Nome** | `start_moving_direction` |
| **Icona** | ➡️ |
| **Categoria** | Movimento |

Inizia a muoverti in una direzione a una data velocità

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `directions` | Scelta multipla | right | Direzione/i di movimento — selezionane una, o diverse per sceglierne una casuale a ogni passo. La cella centrale è lo stop.; Scelte: `up-left`, `up`, `up-right`, `left`, `stop`, `right`, `down-left`, `down`, `down-right` |
| `direction_expr` | Testo | — | Alternativa: espressione libera valutata come gradi; facoltativo |
| `speed` | Numero | `4.0` | Velocità in pixel per fotogramma |

### Ferma il movimento

| Proprietà | Valore |
|----------|-------|
| **Nome** | `stop_movement` |
| **Icona** | 🛑 |
| **Categoria** | Movimento |

Azzera entrambe le velocità

*Parametri:* nessuno

### Avvolgi attorno alla stanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `wrap_around_room` |
| **Icona** | 🔄 |
| **Categoria** | Movimento |

Riappari dal lato opposto della stanza

*Parametri:* nessuno

---

<a id="instance"></a>
## Istanza

### Cambia istanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `change_instance` |
| **Icona** | 🔄 |
| **Categoria** | Istanza |
| **Si applica a** | self / other / object |

Trasforma in un altro tipo di oggetto

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | — | Nuovo tipo di oggetto |
| `perform_events` | Sì/No | Sì | Esegui gli eventi distruzione/creazione |

### Crea istanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `create_instance` |
| **Icona** | ✨ |
| **Categoria** | Istanza |

Crea una nuova istanza

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | — | Oggetto da creare |
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `relative` | Sì/No | No | Posizione relativa all'istanza corrente |

### Crea istanza in movimento

| Proprietà | Valore |
|----------|-------|
| **Nome** | `create_moving_instance` |
| **Icona** | ✨➡️ |
| **Categoria** | Istanza |

Crea un'istanza e avviala in una direzione

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | — | Oggetto da creare |
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `speed` | Numero | `0` | Intensità della velocità iniziale |
| `direction` | Numero | `0` | Direzione iniziale in gradi |

### Crea istanza casuale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `create_random_instance` |
| **Icona** | 🎲 |
| **Categoria** | Istanza |

Crea uno di diversi tipi di oggetto scelto a caso

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `object1` | Oggetto | — | Primo oggetto candidato; facoltativo |
| `object2` | Oggetto | — | Secondo oggetto candidato; facoltativo |
| `object3` | Oggetto | — | Terzo oggetto candidato; facoltativo |
| `object4` | Oggetto | — | Quarto oggetto candidato; facoltativo |

### Distruggi istanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `destroy_instance` |
| **Icona** | 💥 |
| **Categoria** | Istanza |
| **Si applica a** | self / other / object |

Distruggi un'istanza

*Parametri:* nessuno

### Distruggi in posizione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `destroy_at_position` |
| **Icona** | 💣 |
| **Categoria** | Istanza |

Distruggi le istanze entro un raggio da (x, y)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | `all` | Quale tipo di oggetto distruggere. «all» distrugge ogni istanza nel raggio; «solid» solo quelle solide (es. muri); «non-solid» tutto tranne i solidi.; Scelte: `all`, `solid`, `non-solid` |
| `x` | Testo | `self.x` | Posizione X (espressione consentita, es. self.x) |
| `y` | Testo | `self.y` | Posizione Y (espressione consentita, es. self.y) |
| `relative` | Sì/No | No | Tratta X/Y come scostamenti dalla posizione di questa istanza invece che come coordinate assolute; facoltativo |
| `radius` | Numero | `32` | Raggio in pixel attorno a (x, y). Predefinito 32 = ~una cella della griglia. |

### Imposta indice immagine

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_image_index` |
| **Icona** | 🖼️ |
| **Categoria** | Istanza |

Imposta il fotogramma di animazione corrente dello sprite dell'istanza

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `frame` | Numero | `0` | Indice del fotogramma |

### Imposta velocità immagine

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_image_speed` |
| **Icona** | ⏩ |
| **Categoria** | Istanza |

Imposta la velocità di riproduzione dell'animazione dello sprite dell'istanza

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `1.0` | Fotogrammi avanzati per passo (0 = in pausa) |

### Imposta sprite

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_sprite` |
| **Icona** | 🖼️ |
| **Categoria** | Istanza |

Cambia lo sprite e/o il fotogramma/la velocità di animazione di un'istanza

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `sprite` | Sprite | `<self>` | Sprite da usare (o «<self>» per mantenere quello corrente) |
| `subimage` | Numero | `-1` | Indice del fotogramma da impostare; -1 lascia invariato |
| `speed` | Numero | `-1` | Velocità di animazione; -1 lascia invariato |

### Avvia animazione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `start_animation` |
| **Icona** | ▶️ |
| **Categoria** | Istanza |

Riprendi l'animazione dello sprite dell'istanza (image_speed = 1)

*Parametri:* nessuno

### Ferma animazione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `stop_animation` |
| **Icona** | ⏸️ |
| **Categoria** | Istanza |

Metti in pausa l'animazione dello sprite dell'istanza (image_speed = 0)

*Parametri:* nessuno

### Verifica numero di istanze

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_instance_count` |
| **Icona** | ❓🔢 |
| **Categoria** | Istanza |

Condizione: confronta il numero di istanze di un oggetto

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | — | Oggetto da contare |
| `number` | Numero | `0` | Valore di confronto |
| `operation` | Scelta | `equal` | Operatore di confronto; Scelte: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="score"></a>
## Punteggio

### Cancella tabella dei record

| Proprietà | Valore |
|----------|-------|
| **Nome** | `clear_highscore` |
| **Icona** | 🗑️🏆 |
| **Categoria** | Punteggio |

Cancella tutte le voci della tabella dei record

*Parametri:* nessuno

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

### Mostra tabella dei record

| Proprietà | Valore |
|----------|-------|
| **Nome** | `show_highscore` |
| **Icona** | 🏆 |
| **Categoria** | Punteggio |

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
| **Categoria** | Punteggio |

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
| **Categoria** | Punteggio |

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
| **Categoria** | Punteggio |

Condizione: confronta il punteggio con un valore

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `value` | Numero | `0` | Valore di confronto |
| `operation` | Scelta | `equal` | Operatore di confronto; Scelte: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="room"></a>
## Stanza

### Verifica stanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `check_room` |
| **Icona** | ❓🚪 |
| **Categoria** | Stanza |

Condizione: vero se la stanza corrente corrisponde

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `room` | Stanza | — | Stanza da confrontare |
| `not_flag` | Sì/No | No | Inverti il risultato; facoltativo |

### Termina gioco

| Proprietà | Valore |
|----------|-------|
| **Nome** | `game_end` |
| **Icona** | 🛑🎮 |
| **Categoria** | Stanza |

Termina il gioco

*Parametri:* nessuno

### Vai alla stanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `goto_room` |
| **Icona** | 🚪 |
| **Categoria** | Stanza |

Passa a una stanza specifica

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `room` | Stanza | — | Nome della stanza di destinazione |
| `transition` | Scelta | `none` | Effetto di transizione (attualmente accettato ma non renderizzato); Scelte: `none`; facoltativo |

### Se esiste stanza successiva

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_next_room_exists` |
| **Icona** | ❓➡️ |
| **Categoria** | Stanza |

Verifica se c'è una stanza successiva dopo quella corrente

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `then_actions` | Elenco azioni | — | Azioni se esiste la stanza successiva |
| `else_actions` | Elenco azioni | — | Azioni se la stanza successiva non esiste |

### Se esiste stanza precedente

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_previous_room_exists` |
| **Icona** | ❓⬅️ |
| **Categoria** | Stanza |

Verifica se c'è una stanza precedente prima di quella corrente

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `then_actions` | Elenco azioni | — | Azioni se esiste la stanza precedente |
| `else_actions` | Elenco azioni | — | Azioni se la stanza precedente non esiste |

### Stanza successiva

| Proprietà | Valore |
|----------|-------|
| **Nome** | `next_room` |
| **Icona** | ➡️ |
| **Categoria** | Stanza |

Vai alla stanza successiva

*Parametri:* nessuno

### Stanza precedente

| Proprietà | Valore |
|----------|-------|
| **Nome** | `previous_room` |
| **Icona** | ⬅️ |
| **Categoria** | Stanza |

Vai alla stanza precedente

*Parametri:* nessuno

### Riavvia stanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `restart_room` |
| **Icona** | 🔄 |
| **Categoria** | Stanza |

Riavvia la stanza corrente

*Parametri:* nessuno

### Imposta titolo stanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_room_caption` |
| **Icona** | 🏷️ |
| **Categoria** | Stanza |

Imposta il titolo della finestra di gioco

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `caption` | Testo | — | Testo del titolo della finestra |

---

<a id="timing"></a>
## Tempo

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

<a id="audio"></a>
## Audio

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

<a id="game"></a>
## Gioco

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

---

<a id="control"></a>
## Controllo

### Verifica se vuoto

| Proprietà | Valore |
|----------|-------|
| **Nome** | `check_empty` |
| **Icona** | 🔍 |
| **Categoria** | Controllo |

Vero quando (x, y) è privo di collisioni. Usa con start_block/end_block per condizionare l'azione/le azioni successive, in stile GM

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Testo | `self.x` | Posizione X da verificare (espressione consentita, es. self.x + 32) |
| `y` | Testo | `self.y` | Posizione Y da verificare (espressione consentita, es. self.y + 32) |
| `relative` | Sì/No | No | Tratta X/Y come scostamenti dalla posizione di questa istanza invece che come coordinate assolute; facoltativo |
| `objects` | Scelta | `solid` | Quali istanze contano come occupanti la posizione; Scelte: `solid`, `all` |

### Commento

| Proprietà | Valore |
|----------|-------|
| **Nome** | `comment` |
| **Icona** | ⚠️ |
| **Categoria** | Controllo |

Un commento nell'elenco delle azioni (senza effetto in esecuzione)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `text` | Testo | — | Testo di commento libero; facoltativo |

### Altrimenti

| Proprietà | Valore |
|----------|-------|
| **Nome** | `else_action` |
| **Icona** | ⚡ |
| **Categoria** | Controllo |

Contrassegna il ramo «altrimenti» di una condizione

*Parametri:* nessuno

### Fine blocco

| Proprietà | Valore |
|----------|-------|
| **Nome** | `end_block` |
| **Icona** | 📁 |
| **Categoria** | Controllo |

Termina un blocco di azioni

*Parametri:* nessuno

### Esegui codice

| Proprietà | Valore |
|----------|-------|
| **Nome** | `execute_code` |
| **Icona** | 📜 |
| **Categoria** | Controllo |

Esegui un blocco di codice Python integrato

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `code` | Codice | — | Codice Python da valutare rispetto all'istanza |

### Esegui script

| Proprietà | Valore |
|----------|-------|
| **Nome** | `execute_script` |
| **Icona** | 📜 |
| **Categoria** | Controllo |

Esegui uno degli script del progetto

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `script` | Script | — | Nome dello script del progetto da eseguire |
| `arg0` | Testo | — | Disponibile nello script come argument0; facoltativo |
| `arg1` | Testo | — | Disponibile nello script come argument1; facoltativo |
| `arg2` | Testo | — | Disponibile nello script come argument2; facoltativo |
| `arg3` | Testo | — | Disponibile nello script come argument3; facoltativo |
| `arg4` | Testo | — | Disponibile nello script come argument4; facoltativo |

### Esci dall'evento

| Proprietà | Valore |
|----------|-------|
| **Nome** | `exit_event` |
| **Icona** | 🚪 |
| **Categoria** | Controllo |

Interrompi l'esecuzione delle azioni rimanenti in questo evento

*Parametri:* nessuno

### Se si può spingere

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_can_push` |
| **Icona** | 📦 |
| **Categoria** | Controllo |

Verifica se una cassa/un oggetto può essere spinto nella direzione corrente (stile Sokoban)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `direction` | Scelta | `facing` | Direzione da verificare per la spinta; Scelte: `facing` |
| `object_type` | Testo | `box` | Tipo di oggetto spinto |
| `then_action` | Scelta | `push_and_move` | Azione se la spinta è possibile; Scelte: `push_and_move`, `none` |
| `else_action` | Scelta | `stop_movement` | Azione se la spinta è bloccata; Scelte: `stop_movement`, `none` |

### Se collisione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_collision` |
| **Icona** | ❓💥 |
| **Categoria** | Controllo |

Condizione: vero se l'istanza collidesse allo scostamento (x, y)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Scostamento orizzontale da verificare |
| `y` | Numero | `0` | Scostamento verticale da verificare |
| `object` | Testo | `any` | «any», «solid» o un nome di oggetto; Scelte: `any`, `solid`; facoltativo |
| `not_flag` | Sì/No | No | Nega il risultato; facoltativo |

### Se collisione in

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_collision_at` |
| **Icona** | 🎯 |
| **Categoria** | Controllo |

Verifica una collisione in una posizione

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Testo | `self.x + 32` | Espressione della posizione X |
| `y` | Testo | `self.y` | Espressione della posizione Y |
| `object_type` | Scelta | `any` | Tipo di oggetto da verificare; Scelte: `any`, `solid` |
| `then_actions` | Elenco azioni | — | Azioni se collisione trovata |
| `else_actions` | Elenco azioni | — | Azioni se nessuna collisione |

### Se condizione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_condition` |
| **Icona** | ❓ |
| **Categoria** | Controllo |

Verifica condizionale con azioni allora/altrimenti

*Parametri:* nessuno

### Se l'oggetto esiste

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_object_exists` |
| **Icona** | ❓ |
| **Categoria** | Controllo |

Condizione: vero se esiste almeno un'istanza dell'oggetto

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | — | Tipo di oggetto da verificare |
| `not_flag` | Sì/No | No | Nega il risultato (agisci quando l'oggetto NON esiste); facoltativo |

### Ripeti

| Proprietà | Valore |
|----------|-------|
| **Nome** | `repeat` |
| **Icona** | 🔁 |
| **Categoria** | Controllo |

Ripeti l'azione/il blocco successivo N volte

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `times` | Numero | `10` | Numero di ripetizioni |
| `actions` | Elenco azioni | — | Azioni da ripetere |

### Imposta variabile

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_variable` |
| **Icona** | 📝 |
| **Categoria** | Controllo |

Imposta una variabile di istanza o globale

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `variable` | Testo | — | Nome della variabile |
| `value` | Testo | `0` | Valore (numero, stringa o espressione) |
| `scope` | Scelta | `self` | Ambito della variabile; Scelte: `self`, `other`, `global` |
| `relative` | Sì/No | No | Aggiungi al valore attuale invece di sostituirlo |

### Inizio blocco

| Proprietà | Valore |
|----------|-------|
| **Nome** | `start_block` |
| **Icona** | 📂 |
| **Categoria** | Controllo |

Inizia un blocco di azioni (per il raggruppamento)

*Parametri:* nessuno

### Verifica probabilità

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_chance` |
| **Icona** | 🎲❓ |
| **Categoria** | Controllo |

Condizione: vero con probabilità 1 su «sides»

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `sides` | Numero | `6` | Una probabilità di 1 su N di essere vero |

### Verifica espressione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_expression` |
| **Icona** | ❓ |
| **Categoria** | Controllo |

Verifica se un'espressione è vera

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `expression` | Testo | — | Espressione da valutare (vero se >= 0.5) |
| `then_actions` | Elenco azioni | — | Azioni se vero |
| `else_actions` | Elenco azioni | — | Azioni se falso |

### Poni una domanda

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_question` |
| **Icona** | ❓💬 |
| **Categoria** | Controllo |

Condizione: mostra una finestra sì/no; vero se l'utente risponde sì

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `question` | Testo | `Continue?` | Domanda mostrata al giocatore |

### Verifica variabile

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_variable` |
| **Icona** | ❓ |
| **Categoria** | Controllo |

Verifica il valore di una variabile di istanza o globale

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `variable` | Testo | — | Nome della variabile |
| `value` | Testo | `0` | Valore da confrontare |
| `scope` | Scelta | `self` | Ambito della variabile; Scelte: `self`, `other`, `global` |
| `operation` | Scelta | `equal` | Operatore di confronto; Scelte: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="grid"></a>
## Griglia

### Se sulla griglia

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_on_grid` |
| **Icona** | ▦ |
| **Categoria** | Griglia |

Verifica se l'oggetto è allineato alla griglia

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `grid_size` | Numero | `32` | Dimensione della cella della griglia in pixel |
| `then_actions` | Elenco azioni | — | Azioni se sulla griglia |
| `else_actions` | Elenco azioni | — | Azioni se non sulla griglia |

### Allinea alla griglia

| Proprietà | Valore |
|----------|-------|
| **Nome** | `snap_to_grid` |
| **Icona** | ▦ |
| **Categoria** | Griglia |

Allinea la posizione dell'istanza alla griglia

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `grid_size` | Numero | `32` | Dimensione della cella della griglia in pixel |

### Ferma se nessun tasto premuto

| Proprietà | Valore |
|----------|-------|
| **Nome** | `stop_if_no_keys` |
| **Icona** | ▦ |
| **Categoria** | Griglia |

Ferma il movimento sulla griglia quando non è premuto alcun tasto di movimento (perfetto per un allineamento fluido alla griglia)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `grid_size` | Numero | `32` | Dimensione della cella della griglia in pixel |

### Verifica allineamento alla griglia

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_alignment` |
| **Icona** | ❓▦ |
| **Categoria** | Griglia |

Condizione: vero se l'istanza è allineata a una griglia

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `hsnap` | Numero | `32` | Spaziatura orizzontale della griglia in pixel |
| `vsnap` | Numero | `32` | Spaziatura verticale della griglia in pixel |

---

<a id="views"></a>
## Viste

### Abilita viste

| Proprietà | Valore |
|----------|-------|
| **Nome** | `enable_views` |
| **Icona** | 🎥 |
| **Categoria** | Viste |

Attiva o disattiva il sistema di camera/vista della stanza (consente a un livello di scorrere quando è più grande della finestra)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `enable` | Sì/No | Sì | Attivo = viste camera; disattivo = disegna l'intera stanza in una volta |

### Imposta vista

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_view` |
| **Icona** | 🎥 |
| **Categoria** | Viste |

Configura una vista di camera: quale parte della stanza mostra, dove si disegna sullo schermo e un oggetto da seguire

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `view` | Scelta | `0` | Quale delle 8 viste configurare; Scelte: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` |
| `visible` | Sì/No | Sì | Disegna questa vista |
| `view_x` | Numero | `0` | Bordo sinistro della regione della stanza mostrata |
| `view_y` | Numero | `0` | Bordo superiore della regione della stanza mostrata |
| `view_w` | Numero | `800` | Larghezza della regione della stanza mostrata |
| `view_h` | Numero | `600` | Altezza della regione della stanza mostrata |
| `port_x` | Numero | `0` | Bordo sinistro sullo schermo |
| `port_y` | Numero | `0` | Bordo superiore sullo schermo |
| `port_w` | Numero | `800` | Larghezza disegnata sullo schermo |
| `port_h` | Numero | `600` | Altezza disegnata sullo schermo |
| `follow` | Oggetto | — | Oggetto seguito dalla camera (vuoto = vista fissa); facoltativo |
| `hborder` | Numero | `32` | Bordo orizzontale prima che la camera scorra |
| `vborder` | Numero | `32` | Bordo verticale prima che la camera scorra |
| `hspeed` | Numero | `-1` | Velocità di scorrimento orizzontale massima (-1 = istantanea) |
| `vspeed` | Numero | `-1` | Velocità di scorrimento verticale massima (-1 = istantanea) |

---

<a id="3d-view"></a>
## Vista 3D

### Disegna HUD DOOM

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_doom_hud` |
| **Icona** | 🎯 |
| **Categoria** | Vista 3D |

Disegna una barra di stato inferiore in stile DOOM (barra della salute + numero, punteggio, vite, un contatore di obiettivo e un'icona del volto reattiva alla salute) sopra la vista raycast

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Bordo sinistro della barra, in pixel schermo |
| `y` | Numero | `-1` | Bordo superiore della barra; un valore negativo la allinea automaticamente in fondo alla finestra, sotto la vista ridotta; facoltativo |
| `width` | Numero | `0` | Larghezza della barra (0 = larghezza piena della finestra); facoltativo |
| `height` | Numero | `42` | Altezza della barra; mantienila coerente con la fascia viewport_height riservata in enable_raycast_view; facoltativo |
| `back_color` | Colore | `#101010` | Pannello di sfondo della barra; facoltativo |
| `divider_color` | Colore | `#505050` | Bordo superiore e sfondo della barra della salute; facoltativo |
| `text_color` | Colore | `#ffffff` | Colore di tutto il testo della barra; facoltativo |
| `health_label` | Testo | `Health` | facoltativo |
| `health_bar_width` | Numero | `90` | facoltativo |
| `health_bar_height` | Numero | `14` | facoltativo |
| `bar_color` | Colore | `#20c020` | Colore di riempimento della barra della salute; facoltativo |
| `face_sprite` | Sprite | — | Striscia orizzontale di fotogrammi del volto, il più sano per primo (vuoto = nessuna icona del volto); facoltativo |
| `face_frames` | Numero | `4` | Quanti fotogrammi ha la striscia del volto; la salute è distribuita uniformemente tra essi; facoltativo |
| `score_label` | Testo | `Score: ` | facoltativo |
| `lives_sprite` | Sprite | — | Sprite disegnato una volta per ogni vita rimanente; facoltativo |
| `lives_scale` | Numero | `1.0` | facoltativo |
| `objective_value` | Testo | `0` | Espressione mostrata dopo l'etichetta dell'obiettivo (associa la tua variabile chiave/missione); facoltativo |
| `objective_label` | Testo | `Keys: ` | facoltativo |

### Disegna minimappa

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_minimap` |
| **Icona** | 🗺️ |
| **Categoria** | Vista 3D |

Disegna una minimappa orientata a nord dei muri della stanza raycast, con un indicatore che mostra dove si trova la camera e in quale direzione guarda

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Bordo sinistro della minimappa, in pixel schermo |
| `y` | Numero | `0` | Bordo superiore della minimappa, in pixel schermo |
| `size` | Numero | `120` | Larghezza e altezza del quadrato della minimappa, in pixel; facoltativo |
| `back_color` | Colore | `#101018` | Colore del pannello dietro la mappa; facoltativo |
| `wall_color` | Colore | `#8080a0` | Colore delle linee dei muri; facoltativo |
| `player_color` | Colore | `#ffd040` | Colore dell'indicatore della camera e della sua linea di direzione; facoltativo |

### Abilita vista Raycast

| Proprietà | Valore |
|----------|-------|
| **Nome** | `enable_raycast_view` |
| **Icona** | 🕹️ |
| **Categoria** | Vista 3D |

Renderizza la stanza come vista 3D in prima persona in stile Doom/Wolfenstein (muri, cielo, pavimento) invece della vista dall'alto

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `enable` | Sì/No | Sì | Attivo = vista raycast in prima persona; disattivo = normale vista dall'alto |
| `camera_object` | Oggetto | — | Oggetto la cui posizione + angolo di sguardo è la camera (vuoto = l'oggetto che esegue questa azione); facoltativo |
| `fov` | Numero | `66` | Campo visivo orizzontale in gradi; facoltativo |
| `render_distance` | Numero | `20` | Lunghezza massima del raggio in celle della griglia; facoltativo |
| `cell_size` | Numero | `32` | Dimensione della cella della griglia in pixel (corrisponde alla griglia di posizionamento dei muri); facoltativo |
| `columns` | Numero | `320` | Colonne dello schermo per il raycast (meno = più veloce/più grezzo); facoltativo |
| `wall_color` | Colore | `#993333` | Colore uniforme dei muri quando non è impostata una texture di muro; facoltativo |
| `floor_color` | Colore | `#464632` | Colore uniforme del pavimento quando non è impostata una texture di pavimento; facoltativo |
| `ceiling_color` | Colore | `#87CEEB` | Colore uniforme del soffitto quando non è impostata una texture di cielo/soffitto; facoltativo |
| `wall_texture` | Sprite | — | Sprite per texturizzare ogni muro (vuoto = colore uniforme); facoltativo |
| `sky_texture` | Sprite | — | Sprite per un cielo panoramico sopra il soffitto (vuoto = uniforme); facoltativo |
| `floor_texture` | Sprite | — | Sprite proiettato sul pavimento (vuoto = colore uniforme); facoltativo |
| `ceiling_texture` | Sprite | — | Sprite proiettato sul soffitto quando non è impostato un cielo; facoltativo |
| `wall_textured` | Sì/No | Sì | Disattivo forza colori uniformi dei muri anche quando è impostata una texture; facoltativo |
| `floor_cast_res` | Numero | `4` | Sottocampionamento del pavimento proiettato (più alto = più veloce + più grezzo); facoltativo |
| `viewport_height` | Numero | `0` | Riduci la vista 3D a questa altezza in pixel (letterbox), riservando la fascia sottostante per una barra di stato in stile DOOM (0 = altezza piena della finestra, invariato); facoltativo |

### Imposta angolo di sguardo

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_facing_angle` |
| **Icona** | 🧭 |
| **Categoria** | Vista 3D |

Imposta la direzione dello sguardo dell'istanza per una camera raycast (in prima persona) — indipendente dalla velocità di movimento

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `angle` | Numero | `0` | Gradi (0=destra, 90=su, 180=sinistra, 270=giù) |
| `relative` | Sì/No | No | Aggiungi all'angolo di sguardo attuale invece di sostituirlo; facoltativo |

---

## Vedi anche

- [Riferimento eventi](Event-Reference_it) — gli eventi che attivano le azioni
- [Guida ai preset](Preset-Guide_it) — quali azioni espone ogni preset/edizione
- [Vista 3D](3D-View_it) — le azioni della vista in prima persona (raycast)
- [Estensioni](Extensions_it) — come vengono fornite le azioni della Vista 3D
