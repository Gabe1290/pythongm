# Preset Intermedio

*[Home](Home_it) | [Guida ai Preset](Preset-Guide_it) | [Preset Principiante](Beginner-Preset_it)*

Il preset **Intermedio** si basa sul [Preset Principiante](Beginner-Preset_it) aggiungendo eventi e azioni piu avanzati. E progettato per utenti che hanno padroneggiato le basi e vogliono creare giochi piu complessi con funzionalita come eventi temporizzati, suono, vite e sistemi di salute.

## Panoramica

Il preset Intermedio include tutto dal Principiante, piu:
- **4 Tipi di Eventi Aggiuntivi** - Disegno, Distruzione, Mouse, Allarme
- **12 Tipi di Azioni Aggiuntive** - Vite, Salute, Suono, Temporizzazione e piu opzioni di movimento
- **3 Categorie Aggiuntive** - Temporizzazione, Suono, Disegno

---

## Eventi Aggiuntivi (Oltre il Principiante)

### Evento Disegno
| Proprieta | Valore |
|-----------|--------|
| **Nome Blocco** | `event_draw` |
| **Categoria** | Disegno |
| **Icona** | 🎨 |
| **Descrizione** | Attivato quando l'oggetto deve essere renderizzato |

**Quando si attiva:** Ogni frame durante la fase di disegno, dopo tutti gli eventi step.

**Importante:** Quando aggiungi un evento Disegno, il disegno predefinito dello sprite viene disabilitato. Devi disegnare manualmente lo sprite se vuoi che sia visibile.

**Usi comuni:**
- Rendering personalizzato
- Disegnare barre della salute
- Visualizzare testo
- Disegnare forme ed effetti
- Elementi dell'interfaccia

---

### Evento Distruzione
| Proprieta | Valore |
|-----------|--------|
| **Nome Blocco** | `event_destroy` |
| **Categoria** | Oggetto |
| **Icona** | 💥 |
| **Descrizione** | Attivato quando l'istanza viene distrutta |

**Quando si attiva:** Appena prima che l'istanza venga rimossa dal gioco.

**Usi comuni:**
- Creare effetti di esplosione
- Rilasciare oggetti
- Riprodurre suono di morte
- Aggiornare il punteggio
- Generare particelle

---

### Evento Mouse
| Proprieta | Valore |
|-----------|--------|
| **Nome Blocco** | `event_mouse` |
| **Categoria** | Input |
| **Icona** | 🖱️ |
| **Descrizione** | Attivato su interazioni con il mouse |

**Tipi di eventi mouse:**
- Pulsante sinistro (pressione, rilascio, tenuto)
- Pulsante destro (pressione, rilascio, tenuto)
- Pulsante centrale (pressione, rilascio, tenuto)
- Mouse entra (cursore entra nell'istanza)
- Mouse esce (cursore esce dall'istanza)
- Eventi mouse globali (ovunque sullo schermo)

**Usi comuni:**
- Pulsanti cliccabili
- Trascina e rilascia
- Effetti hover
- Interazioni con menu

---

### Evento Allarme
| Proprieta | Valore |
|-----------|--------|
| **Nome Blocco** | `event_alarm` |
| **Categoria** | Temporizzazione |
| **Icona** | ⏰ |
| **Descrizione** | Attivato quando un timer allarme raggiunge zero |

**Quando si attiva:** Quando il conto alla rovescia dell'allarme corrispondente raggiunge 0.

**Allarmi disponibili:** 12 allarmi indipendenti (0-11)

**Usi comuni:**
- Generazione temporizzata
- Azioni ritardate
- Tempi di ricarica
- Temporizzazione animazione
- Eventi periodici

---

## Azioni Aggiuntive (Oltre il Principiante)

### Azioni di Movimento

#### Muovi in Direzione
| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `move_direction` |
| **Nome Blocco** | `move_direction` |
| **Categoria** | Movimento |

**Descrizione:** Imposta il movimento usando direzione (0-360 gradi) e velocita.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `direction` | Numero | Direzione in gradi (0=destra, 90=su, 180=sinistra, 270=giu) |
| `speed` | Numero | Velocita di movimento |

---

#### Muovi Verso un Punto
| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `move_towards` |
| **Nome Blocco** | `move_towards` |
| **Categoria** | Movimento |

**Descrizione:** Muoviti verso una posizione specifica.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `x` | Numero/Espressione | Coordinata X obiettivo |
| `y` | Numero/Espressione | Coordinata Y obiettivo |
| `speed` | Numero | Velocita di movimento |

---

### Azioni di Temporizzazione

#### Imposta Allarme
| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `set_alarm` |
| **Nome Blocco** | `set_alarm` |
| **Categoria** | Temporizzazione |
| **Icona** | ⏰ |

**Descrizione:** Imposta un allarme per attivarsi dopo un numero di passi.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `alarm` | Numero | Numero allarme (0-11) |
| `steps` | Numero | Passi fino all'attivazione dell'allarme (a 60 FPS, 60 passi = 1 secondo) |

**Esempio:** Imposta allarme 0 a 180 passi per un ritardo di 3 secondi.

---

### Azioni Vite

#### Imposta Vite
| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `set_lives` |
| **Nome Blocco** | `lives_set` |
| **Categoria** | Punteggio/Vite/Salute |
| **Icona** | ❤️ |

**Descrizione:** Imposta il numero di vite.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `value` | Numero | Valore vite |
| `relative` | Booleano | Se vero, aggiunge alle vite attuali |

---

#### Aggiungi Vite
| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `add_lives` |
| **Nome Blocco** | `lives_add` |
| **Categoria** | Punteggio/Vite/Salute |
| **Icona** | ➕❤️ |

**Descrizione:** Aggiungi o sottrai vite.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `value` | Numero | Quantita da aggiungere (negativo per sottrarre) |

**Nota:** Quando le vite raggiungono 0, viene attivato l'evento `no_more_lives`.

---

#### Disegna Vite
| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `draw_lives` |
| **Nome Blocco** | `draw_lives` |
| **Categoria** | Punteggio/Vite/Salute |
| **Icona** | 🖼️❤️ |

**Descrizione:** Visualizza le vite sullo schermo.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `x` | Numero | Posizione X |
| `y` | Numero | Posizione Y |
| `sprite` | Sprite | Sprite opzionale da usare come icona vita |

---

### Azioni Salute

#### Imposta Salute
| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `set_health` |
| **Nome Blocco** | `health_set` |
| **Categoria** | Punteggio/Vite/Salute |
| **Icona** | 💚 |

**Descrizione:** Imposta il valore della salute (0-100).

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `value` | Numero | Valore salute (0-100) |
| `relative` | Booleano | Se vero, aggiunge alla salute attuale |

---

#### Aggiungi Salute
| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `add_health` |
| **Nome Blocco** | `health_add` |
| **Categoria** | Punteggio/Vite/Salute |
| **Icona** | ➕💚 |

**Descrizione:** Aggiungi o sottrai salute.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `value` | Numero | Quantita da aggiungere (negativo per danni) |

**Nota:** Quando la salute raggiunge 0, viene attivato l'evento `no_more_health`.

---

#### Disegna Barra della Salute
| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `draw_health_bar` |
| **Nome Blocco** | `draw_health_bar` |
| **Categoria** | Punteggio/Vite/Salute |
| **Icona** | 📊💚 |

**Descrizione:** Disegna una barra della salute sullo schermo.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `x1` | Numero | Posizione X sinistra |
| `y1` | Numero | Posizione Y superiore |
| `x2` | Numero | Posizione X destra |
| `y2` | Numero | Posizione Y inferiore |
| `back_color` | Colore | Colore di sfondo |
| `bar_color` | Colore | Colore della barra della salute |

---

### Azioni Audio

#### Riproduci Suono
| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `play_sound` |
| **Nome Blocco** | `sound_play` |
| **Categoria** | Suono |
| **Icona** | 🔊 |

**Descrizione:** Riproduci un effetto sonoro.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `sound` | Suono | Risorsa audio da riprodurre |
| `loop` | Booleano | Se il suono deve ripetersi in loop |

---

#### Riproduci Musica
| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `play_music` |
| **Nome Blocco** | `music_play` |
| **Categoria** | Suono |
| **Icona** | 🎵 |

**Descrizione:** Riproduci musica di sottofondo.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `sound` | Suono | Risorsa musicale da riprodurre |
| `loop` | Booleano | Se deve ripetersi (solitamente vero per la musica) |

---

#### Ferma Musica
| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `stop_music` |
| **Nome Blocco** | `music_stop` |
| **Categoria** | Suono |
| **Icona** | 🔇 |

**Descrizione:** Ferma tutta la musica attualmente in riproduzione.

**Parametri:** Nessuno

---

## Lista Completa delle Funzionalita

### Eventi nel Preset Intermedio

| Evento | Categoria | Descrizione |
|--------|-----------|-------------|
| Create | Oggetto | Istanza creata |
| Step | Oggetto | Ogni frame |
| Destroy | Oggetto | Istanza distrutta |
| Draw | Disegno | Fase di rendering |
| Keyboard Press | Input | Tasto premuto una volta |
| Mouse | Input | Interazioni mouse |
| Collision | Collisione | Sovrapposizione istanze |
| Alarm | Temporizzazione | Timer raggiunto zero |

### Azioni nel Preset Intermedio

| Categoria | Azioni |
|-----------|--------|
| **Movimento** | Set H/V Speed, Stop, Jump To, Move Direction, Move Towards |
| **Istanza** | Create, Destroy |
| **Punteggio** | Set Score, Add Score, Draw Score |
| **Vite** | Set Lives, Add Lives, Draw Lives |
| **Salute** | Set Health, Add Health, Draw Health Bar |
| **Stanza** | Next, Previous, Restart, Go To, If Next/Previous Exists |
| **Temporizzazione** | Set Alarm |
| **Suono** | Play Sound, Play Music, Stop Music |
| **Output** | Show Message, Execute Code |

---

## Esempio: Gioco Sparatutto con Vite

### Oggetto Giocatore

**Create:**
- Set Lives: 3

**Keyboard Press (Spazio):**
- Create Instance: obj_bullet a (x, y-20)
- Set Alarm: 0 a 15 (tempo di ricarica)

**Collisione con obj_enemy:**
- Add Lives: -1
- Play Sound: snd_hurt
- Jump to Position: (320, 400)

**No More Lives:**
- Show Message: "Game Over!"
- Restart Room

### Oggetto Nemico

**Create:**
- Set Alarm: 0 a 60

**Alarm 0:**
- Create Instance: obj_enemy_bullet a (x, y+20)
- Set Alarm: 0 a 60 (ripeti)

**Collisione con obj_bullet:**
- Add Score: 100
- Play Sound: snd_explosion
- Destroy Instance: self

---

## Aggiornamento ai Preset Avanzati

Quando hai bisogno di piu funzionalita, considera:
- **Preset Piattaforma** - Gravita, salto, meccaniche platform
- **Preset Completo** - Tutti gli eventi e le azioni disponibili

---

## Vedi Anche

- [Preset Principiante](Beginner-Preset_it) - Inizia qui se sei nuovo
- [Riferimento Completo Azioni](Full-Action-Reference_it) - Lista completa delle azioni
- [Riferimento Eventi](Event-Reference_it) - Lista completa degli eventi
- [Eventi e Azioni](Events-and-Actions_it) - Concetti fondamentali
