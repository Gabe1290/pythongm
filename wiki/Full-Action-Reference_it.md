# Riferimento Completo delle Azioni

*[Home](Home_it) | [Guida ai Preset](Preset-Guide_it) | [Riferimento Eventi](Event-Reference_it)*

Questa pagina documenta tutte le azioni disponibili in PyGameMaker. Le azioni sono comandi che vengono eseguiti quando gli eventi vengono attivati.

## Categorie di Azioni

- [Azioni di Movimento](#azioni-di-movimento)
- [Azioni di Istanza](#azioni-di-istanza)
- [Azioni Punteggio, Vite e Salute](#azioni-punteggio-vite-e-salute)
- [Azioni Stanza](#azioni-stanza)
- [Azioni di Temporizzazione](#azioni-di-temporizzazione)
- [Azioni Audio](#azioni-audio)
- [Azioni di Disegno](#azioni-di-disegno)
- [Azioni di Controllo del Flusso](#azioni-di-controllo-del-flusso)
- [Azioni di Output](#azioni-di-output)

---

## Azioni di Movimento

### Imposta Velocità Orizzontale
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `set_hspeed` |
| **Icona** | ↔️ |
| **Preset** | Principiante |

**Descrizione:** Imposta la velocità di movimento orizzontale.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `value` | Numero | 0 | Velocità in pixel/frame. Positivo=destra, Negativo=sinistra |

---

### Imposta Velocità Verticale
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `set_vspeed` |
| **Icona** | ↕️ |
| **Preset** | Principiante |

**Descrizione:** Imposta la velocità di movimento verticale.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `value` | Numero | 0 | Velocità in pixel/frame. Positivo=giù, Negativo=su |

---

### Ferma Movimento
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `stop_movement` |
| **Icona** | 🛑 |
| **Preset** | Principiante |

**Descrizione:** Ferma tutto il movimento (imposta hspeed e vspeed a 0).

**Parametri:** Nessuno

---

### Salta alla Posizione
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `jump_to_position` |
| **Icona** | 📍 |
| **Preset** | Principiante |

**Descrizione:** Si sposta istantaneamente a una posizione specifica.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `x` | Numero | 0 | Coordinata X di destinazione |
| `y` | Numero | 0 | Coordinata Y di destinazione |

---

### Movimento Fisso
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `move_fixed` |
| **Icona** | ➡️ |
| **Preset** | Avanzato |

**Descrizione:** Si muove in una delle 8 direzioni fisse.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `directions` | Scelta | right | Direzione(i) di movimento |
| `speed` | Numero | 4 | Velocità di movimento |

**Scelte di direzione:** left, right, up, down, up-left, up-right, down-left, down-right, stop

---

### Movimento Libero
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `move_free` |
| **Icona** | 🧭 |
| **Preset** | Avanzato |

**Descrizione:** Si muove in qualsiasi direzione (0-360 gradi).

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `direction` | Numero | 0 | Direzione in gradi (0=destra, 90=su) |
| `speed` | Numero | 4 | Velocità di movimento |

---

### Muovi Verso
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `move_towards` |
| **Icona** | 🎯 |
| **Preset** | Intermedio |

**Descrizione:** Si muove verso una posizione obiettivo.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `x` | Espressione | 0 | X obiettivo (può usare espressioni come `other.x`) |
| `y` | Espressione | 0 | Y obiettivo |
| `speed` | Numero | 4 | Velocità di movimento |

---

### Imposta Velocità
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `set_speed` |
| **Icona** | ⚡ |
| **Preset** | Avanzato |

**Descrizione:** Imposta la magnitudine della velocità (mantiene la direzione).

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `speed` | Numero | 0 | Magnitudine della velocità |

---

### Imposta Direzione
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `set_direction` |
| **Icona** | 🧭 |
| **Preset** | Avanzato |

**Descrizione:** Imposta la direzione del movimento (mantiene la velocità).

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `direction` | Numero | 0 | Direzione in gradi |

---

### Inverti Orizzontale
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `reverse_horizontal` |
| **Icona** | ↔️ |
| **Preset** | Avanzato |

**Descrizione:** Inverte la direzione orizzontale (moltiplica hspeed per -1).

**Parametri:** Nessuno

---

### Inverti Verticale
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `reverse_vertical` |
| **Icona** | ↕️ |
| **Preset** | Avanzato |

**Descrizione:** Inverte la direzione verticale (moltiplica vspeed per -1).

**Parametri:** Nessuno

---

### Imposta Gravità
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `set_gravity` |
| **Icona** | ⬇️ |
| **Preset** | Platformer |

**Descrizione:** Applica la gravità all'istanza.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `direction` | Numero | 270 | Direzione della gravità (270=giù) |
| `gravity` | Numero | 0.5 | Forza della gravità |

---

### Imposta Attrito
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `set_friction` |
| **Icona** | 🛑 |
| **Preset** | Avanzato |

**Descrizione:** Applica l'attrito (rallentamento graduale).

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `friction` | Numero | 0.1 | Quantità di attrito |

---

## Azioni di Istanza

### Distruggi Istanza
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `destroy_instance` |
| **Icona** | 💥 |
| **Preset** | Principiante |

**Descrizione:** Rimuove un'istanza dal gioco.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `target` | Scelta | self | `self` o `other` (negli eventi di collisione) |

---

### Crea Istanza
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `create_instance` |
| **Icona** | ✨ |
| **Preset** | Principiante |

**Descrizione:** Crea una nuova istanza di un oggetto.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `object` | Oggetto | - | Tipo di oggetto da creare |
| `x` | Numero | 0 | Posizione X |
| `y` | Numero | 0 | Posizione Y |

---

### Imposta Sprite
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `set_sprite` |
| **Icona** | 🖼️ |
| **Preset** | Avanzato |

**Descrizione:** Cambia lo sprite dell'istanza.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `sprite` | Sprite | - | Nuovo sprite |

---

## Azioni Punteggio, Vite e Salute

### Imposta Punteggio
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `set_score` |
| **Icona** | 🏆 |
| **Preset** | Principiante |

**Descrizione:** Imposta o modifica il punteggio.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `value` | Numero | 0 | Valore del punteggio |
| `relative` | Booleano | false | Se vero, aggiunge al punteggio attuale |

---

### Aggiungi Punteggio (Scorciatoia)
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `add_score` |
| **Icona** | ➕🏆 |
| **Preset** | Principiante |

**Descrizione:** Aggiunge punti al punteggio.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `value` | Numero | 10 | Punti da aggiungere (negativo per sottrarre) |

---

### Imposta Vite
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `set_lives` |
| **Icona** | ❤️ |
| **Preset** | Intermedio |

**Descrizione:** Imposta o modifica il conteggio delle vite.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `value` | Numero | 3 | Valore delle vite |
| `relative` | Booleano | false | Se vero, aggiunge alle vite attuali |

**Nota:** Attiva l'evento `no_more_lives` quando raggiunge 0.

---

### Aggiungi Vite (Scorciatoia)
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `add_lives` |
| **Icona** | ➕❤️ |
| **Preset** | Intermedio |

**Descrizione:** Aggiunge o rimuove vite.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `value` | Numero | 1 | Vite da aggiungere (negativo per sottrarre) |

---

### Imposta Salute
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `set_health` |
| **Icona** | 💚 |
| **Preset** | Intermedio |

**Descrizione:** Imposta o modifica la salute (0-100).

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `value` | Numero | 100 | Valore della salute |
| `relative` | Booleano | false | Se vero, aggiunge alla salute attuale |

**Nota:** Attiva l'evento `no_more_health` quando raggiunge 0.

---

### Aggiungi Salute (Scorciatoia)
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `add_health` |
| **Icona** | ➕💚 |
| **Preset** | Intermedio |

**Descrizione:** Aggiunge o rimuove salute.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `value` | Numero | 10 | Salute da aggiungere (negativo per danno) |

---

### Disegna Punteggio
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `draw_score` |
| **Icona** | 🖼️🏆 |
| **Preset** | Principiante |

**Descrizione:** Visualizza il punteggio sullo schermo.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `x` | Numero | 10 | Posizione X |
| `y` | Numero | 10 | Posizione Y |
| `caption` | Stringa | "Score: " | Testo prima del punteggio |

---

### Disegna Vite
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `draw_lives` |
| **Icona** | 🖼️❤️ |
| **Preset** | Intermedio |

**Descrizione:** Visualizza le vite sullo schermo.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `x` | Numero | 10 | Posizione X |
| `y` | Numero | 30 | Posizione Y |
| `sprite` | Sprite | - | Sprite icona vita opzionale |

---

### Disegna Barra della Salute
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `draw_health_bar` |
| **Icona** | 📊💚 |
| **Preset** | Intermedio |

**Descrizione:** Disegna una barra della salute.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `x1` | Numero | 10 | X sinistra |
| `y1` | Numero | 50 | Y superiore |
| `x2` | Numero | 110 | X destra |
| `y2` | Numero | 60 | Y inferiore |
| `back_color` | Colore | gray | Colore di sfondo |
| `bar_color` | Colore | green | Colore della barra |

---

## Azioni Stanza

### Stanza Successiva
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `next_room` |
| **Icona** | ➡️ |
| **Preset** | Principiante |

**Descrizione:** Vai alla stanza successiva nell'ordine delle stanze.

**Parametri:** Nessuno

---

### Stanza Precedente
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `previous_room` |
| **Icona** | ⬅️ |
| **Preset** | Principiante |

**Descrizione:** Vai alla stanza precedente nell'ordine delle stanze.

**Parametri:** Nessuno

---

### Riavvia Stanza
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `restart_room` |
| **Icona** | 🔄 |
| **Preset** | Principiante |

**Descrizione:** Riavvia la stanza corrente.

**Parametri:** Nessuno

---

### Vai alla Stanza
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `goto_room` |
| **Icona** | 🚪 |
| **Preset** | Principiante |

**Descrizione:** Vai a una stanza specifica.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `room` | Stanza | - | Stanza di destinazione |

---

### Se Esiste Stanza Successiva
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `if_next_room_exists` |
| **Icona** | ❓➡️ |
| **Preset** | Principiante |

**Descrizione:** Condizionale - esegue le azioni solo se esiste una stanza successiva.

| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `then_actions` | Lista Azioni | Azioni se esiste la stanza successiva |
| `else_actions` | Lista Azioni | Azioni se non c'è stanza successiva |

---

### Se Esiste Stanza Precedente
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `if_previous_room_exists` |
| **Icona** | ❓⬅️ |
| **Preset** | Principiante |

**Descrizione:** Condizionale - esegue le azioni solo se esiste una stanza precedente.

| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `then_actions` | Lista Azioni | Azioni se esiste la stanza precedente |
| `else_actions` | Lista Azioni | Azioni se non c'è stanza precedente |

---

## Azioni di Temporizzazione

### Imposta Allarme
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `set_alarm` |
| **Icona** | ⏰ |
| **Preset** | Intermedio |

**Descrizione:** Imposta un allarme che si attiva dopo un ritardo.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `alarm` | Numero | 0 | Numero dell'allarme (0-11) |
| `steps` | Numero | 60 | Passi fino all'attivazione dell'allarme |

**Nota:** A 60 FPS, 60 passi = 1 secondo.

---

## Azioni Audio

### Riproduci Suono
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `play_sound` |
| **Icona** | 🔊 |
| **Preset** | Intermedio |

**Descrizione:** Riproduce un effetto sonoro.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `sound` | Suono | - | Risorsa sonora |
| `loop` | Booleano | false | Ripeti il suono in loop |

---

### Riproduci Musica
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `play_music` |
| **Icona** | 🎵 |
| **Preset** | Intermedio |

**Descrizione:** Riproduce musica di sottofondo.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `sound` | Suono | - | Risorsa musicale |
| `loop` | Booleano | true | Ripeti la musica in loop |

---

### Ferma Musica
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `stop_music` |
| **Icona** | 🔇 |
| **Preset** | Intermedio |

**Descrizione:** Ferma tutta la musica in riproduzione.

**Parametri:** Nessuno

---

### Imposta Volume
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `set_volume` |
| **Icona** | 🔉 |
| **Preset** | Avanzato |

**Descrizione:** Imposta il volume audio.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `volume` | Numero | 1.0 | Livello del volume (da 0.0 a 1.0) |

---

## Azioni di Disegno

### Disegna Testo
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `draw_text` |
| **Icona** | 📝 |
| **Preset** | Avanzato |

**Descrizione:** Disegna testo sullo schermo.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `x` | Numero | 0 | Posizione X |
| `y` | Numero | 0 | Posizione Y |
| `text` | Stringa | "" | Testo da disegnare |
| `color` | Colore | white | Colore del testo |

---

### Disegna Rettangolo
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `draw_rectangle` |
| **Icona** | ⬛ |
| **Preset** | Avanzato |

**Descrizione:** Disegna un rettangolo.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `x1` | Numero | 0 | X sinistra |
| `y1` | Numero | 0 | Y superiore |
| `x2` | Numero | 32 | X destra |
| `y2` | Numero | 32 | Y inferiore |
| `color` | Colore | white | Colore di riempimento |
| `outline` | Booleano | false | Solo contorno |

---

### Disegna Cerchio
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `draw_circle` |
| **Icona** | ⚪ |
| **Preset** | Avanzato |

**Descrizione:** Disegna un cerchio.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `x` | Numero | 0 | Centro X |
| `y` | Numero | 0 | Centro Y |
| `radius` | Numero | 16 | Raggio |
| `color` | Colore | white | Colore di riempimento |
| `outline` | Booleano | false | Solo contorno |

---

### Imposta Alfa
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `set_alpha` |
| **Icona** | 👻 |
| **Preset** | Avanzato |

**Descrizione:** Imposta la trasparenza del disegno.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `alpha` | Numero | 1.0 | Trasparenza (0.0=invisibile, 1.0=opaco) |

---

## Azioni di Controllo del Flusso

### Se Collisione A
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `if_collision_at` |
| **Icona** | 🎯 |
| **Preset** | Avanzato |

**Descrizione:** Verifica la collisione in una posizione.

| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `x` | Espressione | Posizione X da verificare |
| `y` | Espressione | Posizione Y da verificare |
| `object_type` | Scelta | `any` o `solid` |
| `then_actions` | Lista Azioni | Se viene trovata collisione |
| `else_actions` | Lista Azioni | Se non c'è collisione |

---

## Azioni di Output

### Mostra Messaggio
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `show_message` |
| **Icona** | 💬 |
| **Preset** | Principiante |

**Descrizione:** Visualizza un messaggio popup.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `message` | Stringa | "Hello!" | Testo del messaggio |

**Nota:** Il gioco si mette in pausa mentre il messaggio è visualizzato.

---

### Esegui Codice
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `execute_code` |
| **Icona** | 💻 |
| **Preset** | Principiante |

**Descrizione:** Esegue codice Python personalizzato.

| Parametro | Tipo | Predefinito | Descrizione |
|-----------|------|-------------|-------------|
| `code` | Codice | "" | Codice Python da eseguire |

**Avvertenza:** Funzionalità avanzata. Usare con cautela.

---

### Termina Gioco
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `end_game` |
| **Icona** | 🚪 |
| **Preset** | Avanzato |

**Descrizione:** Termina il gioco e chiude la finestra.

**Parametri:** Nessuno

---

### Riavvia Gioco
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `restart_game` |
| **Icona** | 🔄 |
| **Preset** | Avanzato |

**Descrizione:** Riavvia il gioco dalla prima stanza.

**Parametri:** Nessuno

---

## Azioni per Preset

| Preset | Conteggio Azioni | Categorie |
|--------|-----------------|-----------|
| **Principiante** | 17 | Movimento, Istanza, Punteggio, Stanza, Output |
| **Intermedio** | 29 | + Vite, Salute, Audio, Temporizzazione |
| **Avanzato** | 40+ | + Disegno, Controllo del Flusso, Gioco |

---

## Vedi Anche

- [Riferimento Eventi](Event-Reference_it) - Lista completa degli eventi
- [Preset Principiante](Beginner-Preset_it) - Azioni essenziali per principianti
- [Preset Intermedio](Intermediate-Preset_it) - Azioni aggiuntive
- [Eventi e Azioni](Events-and-Actions_it) - Panoramica dei concetti fondamentali
