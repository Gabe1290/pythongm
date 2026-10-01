# Preset Principiante

*[Home](Home_it) | [Guida ai Preset](Preset-Guide_it) | [Preset Intermedio](Intermediate-Preset_it)*

> **Generato automaticamente** da `get_beginner()` in `config/blockly_config.py` da `tools/gen_preset_docs.py` — non modificare a mano; rilancia il generatore dopo aver cambiato il preset.

> **Cosa restringe davvero questo preset:** questo preset filtra SIA la tavolozza di blocchi visivi Blockly SIA i menu "Aggiungi Evento"/"Aggiungi Azione" del pannello strutturato Eventi/Azioni — qualunque editor tu usi, appaiono solo gli eventi/le azioni elencati qui sotto. Il preset di un *progetto* si imposta in due modi: **`Preferenze > IDE Edition`** sceglie il predefinito per i *nuovi* progetti (edizione Principiante -> questo preset; i progetti esistenti non vengono mai modificati cambiando edizione), e **`Strumenti > Configura blocchi azione...`** cambia il preset del progetto *attualmente aperto* in qualsiasi momento. L'edizione predefinita dell'IDE è Principiante, quindi i nuovi progetti di un'installazione pulita partono esattamente su questa lista.

## Panoramica

Questo preset abilita **19** tipi di eventi e **54** tipi di azioni.

---

## Eventi

| Evento | Nome Blocco | Categoria | Descrizione |
|-------|------------|----------|-------------|
| Create | `create` | Oggetto | Eseguito una volta quando l'istanza viene creata per la prima volta |
| Step | `step` | Oggetto | Eseguito a ogni fotogramma (usalo per controlli continui) |
| Keyboard (held) | `keyboard` | Input | Eseguito continuamente finché un tasto è tenuto premuto (per un movimento fluido) |
| Keyboard <No Key> | `keyboard_no_key` | Input | Eseguito quando al momento non è premuto alcun tasto |
| Collision With... | `collision` | Collisione | Eseguito quando si verifica una collisione con un altro oggetto |
| Begin Step | `begin_step` | Step | Eseguito all'inizio di ogni step, prima degli altri eventi |
| End Step | `end_step` | Step | Eseguito alla fine di ogni step, dopo le collisioni ma prima del disegno |
| Alarm | `alarm` | Tempo | Eseguito quando un timer di allarme raggiunge zero |
| Draw | `draw` | Disegno | Eseguito quando l'oggetto viene disegnato (sostituisce il disegno automatico dello sprite) |
| Draw GUI | `draw_gui` | Disegno | Disegnato sopra a tutto il resto (non influenzato da telecamera/vista). Da usare per HUD, punteggio, vite. |
| Room End | `room_end` | Stanza | Eseguito quando la stanza termina |
| Room Start | `room_start` | Stanza | Eseguito quando la stanza inizia (dopo gli eventi Create) |
| Game End | `game_end` | Gioco | Eseguito quando il gioco termina |
| Game Start | `game_start` | Gioco | Eseguito quando il gioco inizia (solo nella prima stanza) |
| Animation End | `animation_end` | Altro | Si attiva quando l'animazione dello sprite raggiunge l'ultimo fotogramma e ricomincia |
| Intersect Boundary | `intersect_boundary` | Altro | Eseguito quando l'istanza tocca il bordo della stanza |
| No More Health | `no_more_health` | Altro | Eseguito quando la salute arriva a 0 o meno |
| No More Lives | `no_more_lives` | Altro | Eseguito quando le vite arrivano a 0 o meno |
| Outside Room | `outside_room` | Altro | Eseguito quando l'istanza è completamente fuori dalla stanza |

---

## Azioni

### Movimento

| Azione | Nome Blocco | Parametri |
|--------|------------|------------|
| Rimbalza | `bounce` | — |
| Salta alla posizione | `jump_to_position` | `x`, `y`, `relative` |
| Salta alla posizione iniziale | `jump_to_start` | — |
| Muovi fino al contatto | `move_to_contact` | `direction`, `max_distance`, `object` |
| Inverti orizzontale | `reverse_horizontal` | — |
| Inverti verticale | `reverse_vertical` | — |
| Imposta direzione e velocità | `set_direction_speed` | `direction`, `speed` |
| Imposta gravità | `set_gravity` | `direction`, `gravity` |
| Imposta velocità orizzontale | `set_hspeed` | `speed` |
| Imposta velocità verticale | `set_vspeed` | `speed` |
| Inizia a muoverti (direzione) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Ferma il movimento | `stop_movement` | — |

### Griglia

| Azione | Nome Blocco | Parametri |
|--------|------------|------------|
| Verifica allineamento alla griglia | `test_alignment` | `hsnap`, `vsnap` |

### Istanza

| Azione | Nome Blocco | Parametri |
|--------|------------|------------|
| Cambia istanza | `change_instance` | `object`, `perform_events` |
| Crea istanza | `create_instance` | `object`, `x`, `y`, `relative` |
| Distruggi istanza | `destroy_instance` | — |
| Distruggi in posizione | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Verifica numero di istanze | `test_instance_count` | `object`, `number`, `operation` |

### Punteggio

| Azione | Nome Blocco | Parametri |
|--------|------------|------------|
| Disegna vite | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Disegna punteggio | `draw_score` | `x`, `y`, `caption`, `relative` |
| Imposta vite | `set_lives` | `value`, `relative` |
| Imposta punteggio | `set_score` | `value`, `relative` |
| Mostra tabella dei record | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |

### Tempo

| Azione | Nome Blocco | Parametri |
|--------|------------|------------|
| Imposta allarme | `set_alarm` | `alarm_number`, `steps` |
| Pausa | `sleep` | `milliseconds` |

### Stanza

| Azione | Nome Blocco | Parametri |
|--------|------------|------------|
| Termina gioco | `game_end` | — |
| Se esiste stanza successiva | `if_next_room_exists` | `then_actions`, `else_actions` |
| Se esiste stanza precedente | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Riavvia stanza | `restart_room` | — |
| Imposta sfondo | `set_background` | `background`, `visible`, `foreground`, `tiled_h`, `tiled_v`, `hspeed`, `vspeed` |

### Audio

| Azione | Nome Blocco | Parametri |
|--------|------------|------------|
| Verifica riproduzione suono | `check_sound` | `sound`, `not_flag` |
| Riproduci musica | `play_music` | `music`, `loop`, `volume` |
| Riproduci suono | `play_sound` | `sound`, `volume` |
| Imposta volume | `set_volume` | `volume` |
| Ferma musica | `stop_music` | — |
| Ferma suono | `stop_sound` | `sound` |

### Gioco

| Azione | Nome Blocco | Parametri |
|--------|------------|------------|
| Disegna testo | `draw_text` | `text`, `x`, `y`, `relative`, `color` |
| Riavvia gioco | `restart_game` | — |
| Imposta colore di disegno | `set_draw_color` | `color` |
| Imposta titolo finestra | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Mostra messaggio | `show_message` | `message` |

### Controllo

| Azione | Nome Blocco | Parametri |
|--------|------------|------------|
| Verifica se vuoto | `check_empty` | `x`, `y`, `relative`, `objects` |
| Commento | `comment` | `text` |
| Altrimenti | `else_action` | — |
| Fine blocco | `end_block` | — |
| Esegui codice | `execute_code` | `code` |
| Esegui script | `execute_script` | `script`, `arg0`, `arg1`, `arg2`, `arg3`, `arg4` |
| Esci dall'evento | `exit_event` | — |
| Se collisione | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Se l'oggetto esiste | `if_object_exists` | `object`, `not_flag` |
| Inizio blocco | `start_block` | — |
| Verifica probabilità | `test_chance` | `sides` |
| Verifica espressione | `test_expression` | `expression`, `then_actions`, `else_actions` |
| Verifica variabile | `test_variable` | `variable`, `value`, `scope`, `operation` |

---

## Vedi Anche

- [Guida ai Preset](Preset-Guide_it) — cosa sono i preset e come cambiarli
- [Riferimento Eventi](Event-Reference_it) — descrizione completa di ogni evento
- [Riferimento Completo delle Azioni](Full-Action-Reference_it) — dettagli completi dei parametri per ogni azione
- [Preset Intermedio](Intermediate-Preset_it) — il livello superiore
