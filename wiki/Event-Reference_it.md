# Riferimento Eventi

*[Home](Home_it) | [Guida ai Preset](Preset-Guide_it) | [Riferimento Completo delle Azioni](Full-Action-Reference_it)*

Questa pagina documenta tutti gli eventi disponibili in PyGameMaker. Gli eventi sono trigger che eseguono azioni quando si verificano condizioni specifiche nel tuo gioco.

## Categorie di Eventi

- [Eventi Oggetto](#eventi-oggetto) - Create, Step, Destroy
- [Eventi di Input](#eventi-di-input) - Tastiera, Mouse
- [Eventi di Collisione](#eventi-di-collisione) - Collisioni tra oggetti
- [Eventi di Temporizzazione](#eventi-di-temporizzazione) - Allarmi, Varianti di Step
- [Eventi di Disegno](#eventi-di-disegno) - Rendering personalizzato
- [Eventi di Stanza](#eventi-di-stanza) - Transizioni di stanza
- [Eventi di Gioco](#eventi-di-gioco) - Inizio/Fine gioco
- [Altri Eventi](#altri-eventi) - Confini, Vite, Salute

---

## Eventi Oggetto

### Create
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `create` |
| **Icona** | 🎯 |
| **Categoria** | Oggetto |
| **Preset** | Principiante |

**Descrizione:** Eseguito una volta quando un'istanza viene creata per la prima volta.

**Quando si attiva:**
- Quando un'istanza viene posizionata in una stanza all'avvio del gioco
- Quando creata tramite l'azione "Crea Istanza"
- Dopo le transizioni di stanza per le nuove istanze

**Usi comuni:**
- Inizializzare variabili
- Impostare valori iniziali
- Configurare lo stato iniziale

---

### Step
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `step` |
| **Icona** | ⭐ |
| **Categoria** | Oggetto |
| **Preset** | Principiante |

**Descrizione:** Eseguito ogni frame (tipicamente 60 volte al secondo).

**Quando si attiva:** Continuamente, ogni frame di gioco.

**Usi comuni:**
- Movimento continuo
- Verifica delle condizioni
- Aggiornamento delle posizioni
- Logica di gioco

**Nota:** Attenzione alle prestazioni - il codice qui viene eseguito costantemente.

---

### Destroy
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `destroy` |
| **Icona** | 💥 |
| **Categoria** | Oggetto |
| **Preset** | Intermedio |

**Descrizione:** Eseguito quando un'istanza viene distrutta.

**Quando si attiva:** Appena prima che l'istanza venga rimossa dal gioco.

**Usi comuni:**
- Generare effetti (esplosioni, particelle)
- Rilasciare oggetti
- Aggiornare i punteggi
- Riprodurre suoni

---

## Eventi di Input

### Tastiera (Continuo)
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `keyboard` |
| **Icona** | ⌨️ |
| **Categoria** | Input |
| **Preset** | Principiante |

**Descrizione:** Si attiva continuamente mentre un tasto e tenuto premuto.

**Ideale per:** Movimento fluido e continuo

**Tasti Supportati:**
- Tasti freccia (su, giu, sinistra, destra)
- Lettere (A-Z)
- Numeri (0-9)
- Spazio, Invio, Escape
- Tasti funzione (F1-F12)
- Tasti modificatori (Shift, Ctrl, Alt)

---

### Pressione Tastiera
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `keyboard_press` |
| **Icona** | 🔘 |
| **Categoria** | Input |
| **Preset** | Principiante |

**Descrizione:** Si attiva una volta quando un tasto viene premuto per la prima volta.

**Ideale per:** Azioni singole (saltare, sparare, selezionare nel menu)

**Differenza da Tastiera:** Si attiva solo una volta per pressione, non mentre e tenuto premuto.

---

### Rilascio Tastiera
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `keyboard_release` |
| **Icona** | ⬆️ |
| **Categoria** | Input |
| **Preset** | Avanzato |

**Descrizione:** Si attiva una volta quando un tasto viene rilasciato.

**Usi comuni:**
- Fermare il movimento quando il tasto viene rilasciato
- Terminare attacchi caricati
- Alternare stati

---

### Mouse
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `mouse` |
| **Icona** | 🖱️ |
| **Categoria** | Input |
| **Preset** | Intermedio |

**Descrizione:** Eventi di pulsanti del mouse e movimento.

**Tipi di Eventi:**

| Tipo | Descrizione |
|------|-------------|
| Pulsante Sinistro | Clic con il pulsante sinistro del mouse |
| Pulsante Destro | Clic con il pulsante destro del mouse |
| Pulsante Centrale | Clic con il pulsante centrale/rotella |
| Entrata Mouse | Il cursore entra nei confini dell'istanza |
| Uscita Mouse | Il cursore esce dai confini dell'istanza |
| Pulsante Sinistro Globale | Clic sinistro ovunque |
| Pulsante Destro Globale | Clic destro ovunque |

---

## Eventi di Collisione

### Collisione
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `collision` |
| **Icona** | 💥 |
| **Categoria** | Collisione |
| **Preset** | Principiante |

**Descrizione:** Si attiva quando questa istanza si sovrappone con un altro tipo di oggetto.

**Configurazione:** Seleziona quale tipo di oggetto attiva questa collisione.

**Variabile speciale:** `other` - Riferimento all'istanza in collisione.

**Quando si attiva:** Ogni frame in cui le istanze si sovrappongono.

**Usi comuni:**
- Raccogliere oggetti
- Subire danni
- Colpire muri
- Attivare eventi

**Esempi di eventi di collisione:**
- `collision_with_obj_coin` - Il giocatore tocca una moneta
- `collision_with_obj_enemy` - Il giocatore tocca un nemico
- `collision_with_obj_wall` - L'istanza colpisce un muro

---

## Eventi di Temporizzazione

### Allarme
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `alarm` |
| **Icona** | ⏰ |
| **Categoria** | Temporizzazione |
| **Preset** | Intermedio |

**Descrizione:** Si attiva quando un conto alla rovescia dell'allarme raggiunge lo zero.

**Allarmi disponibili:** 12 allarmi indipendenti (alarm[0] fino a alarm[11])

**Impostare gli allarmi:** Usa l'azione "Imposta Allarme" con step (60 step ≈ 1 secondo a 60 FPS)

**Usi comuni:**
- Generazione temporizzata
- Tempi di ricarica
- Effetti ritardati
- Azioni ripetitive (reimpostare l'allarme nell'evento allarme)

---

### Begin Step
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `begin_step` |
| **Icona** | ▶️ |
| **Categoria** | Step |
| **Preset** | Avanzato |

**Descrizione:** Si attiva all'inizio di ogni frame, prima degli eventi Step regolari.

**Ordine di esecuzione:** Begin Step → Step → End Step

**Usi comuni:**
- Elaborazione dell'input
- Calcoli pre-movimento

---

### End Step
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `end_step` |
| **Icona** | ⏹️ |
| **Categoria** | Step |
| **Preset** | Avanzato |

**Descrizione:** Si attiva alla fine di ogni frame, dopo le collisioni.

**Usi comuni:**
- Aggiustamenti finali della posizione
- Operazioni di pulizia
- Aggiornamenti di stato dopo le collisioni

---

## Eventi di Disegno

### Draw
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `draw` |
| **Icona** | 🎨 |
| **Categoria** | Disegno |
| **Preset** | Intermedio |

**Descrizione:** Si attiva durante la fase di rendering.

**Importante:** Aggiungere un evento Draw disabilita il disegno automatico dello sprite. Devi disegnare lo sprite manualmente se vuoi che sia visibile.

**Usi comuni:**
- Rendering personalizzato
- Disegnare forme
- Visualizzare testo
- Barre della salute
- Elementi HUD

**Azioni di disegno disponibili:**
- Disegna Sprite
- Disegna Testo
- Disegna Rettangolo
- Disegna Cerchio
- Disegna Linea
- Disegna Barra della Salute

---

## Eventi di Stanza

### Room Start
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `room_start` |
| **Icona** | 🚪 |
| **Categoria** | Stanza |
| **Preset** | Avanzato |

**Descrizione:** Si attiva quando si entra in una stanza, dopo tutti gli eventi Create.

**Usi comuni:**
- Inizializzazione della stanza
- Riprodurre musica della stanza
- Impostare variabili specifiche della stanza

---

### Room End
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `room_end` |
| **Icona** | 🚪 |
| **Categoria** | Stanza |
| **Preset** | Avanzato |

**Descrizione:** Si attiva quando si esce da una stanza.

**Usi comuni:**
- Salvare i progressi
- Fermare la musica
- Pulizia

---

## Eventi di Gioco

### Game Start
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `game_start` |
| **Icona** | 🎮 |
| **Categoria** | Gioco |
| **Preset** | Avanzato |

**Descrizione:** Si attiva una volta quando il gioco inizia per la prima volta (solo nella prima stanza).

**Usi comuni:**
- Inizializzare variabili globali
- Caricare dati salvati
- Riprodurre intro

---

### Game End
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `game_end` |
| **Icona** | 🎮 |
| **Categoria** | Gioco |
| **Preset** | Avanzato |

**Descrizione:** Si attiva quando il gioco sta terminando.

**Usi comuni:**
- Salvare i dati di gioco
- Liberare risorse

---

## Altri Eventi

### Outside Room
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `outside_room` |
| **Icona** | 🚫 |
| **Categoria** | Altro |
| **Preset** | Avanzato |

**Descrizione:** Si attiva quando l'istanza e completamente fuori dai confini della stanza.

**Usi comuni:**
- Distruggere proiettili fuori schermo
- Avvolgere dall'altro lato
- Attivare game over

---

### Intersect Boundary
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `intersect_boundary` |
| **Icona** | ⚠️ |
| **Categoria** | Altro |
| **Preset** | Avanzato |

**Descrizione:** Si attiva quando l'istanza tocca il confine della stanza.

**Usi comuni:**
- Mantenere il giocatore nei confini
- Rimbalzare sui bordi

---

### No More Lives
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `no_more_lives` |
| **Icona** | 💀 |
| **Categoria** | Altro |
| **Preset** | Intermedio |

**Descrizione:** Si attiva quando le vite diventano 0 o meno.

**Usi comuni:**
- Schermata di game over
- Riavviare il gioco
- Mostrare il punteggio finale

---

### No More Health
| Proprieta | Valore |
|-----------|--------|
| **Nome** | `no_more_health` |
| **Icona** | 💔 |
| **Categoria** | Altro |
| **Preset** | Intermedio |

**Descrizione:** Si attiva quando la salute diventa 0 o meno.

**Usi comuni:**
- Perdere una vita
- Far riapparire il giocatore
- Attivare l'animazione di morte

---

## Ordine di Esecuzione degli Eventi

Capire quando gli eventi si attivano aiuta a creare un comportamento di gioco prevedibile:

1. **Begin Step** - Inizio del frame
2. **Alarm** - Qualsiasi allarme attivato
3. **Keyboard/Mouse** - Eventi di input
4. **Step** - Logica principale del gioco
5. **Collision** - Dopo il movimento
6. **End Step** - Dopo le collisioni
7. **Draw** - Fase di rendering

---

## Eventi per Preset

| Preset | Eventi Inclusi |
|--------|----------------|
| **Principiante** | Create, Step, Keyboard Press, Collision |
| **Intermedio** | + Draw, Destroy, Mouse, Alarm |
| **Avanzato** | + Tutte le varianti di tastiera, Begin/End Step, Eventi di stanza, Eventi di gioco, Eventi di confine |

---

## Vedi Anche

- [Riferimento Completo delle Azioni](Full-Action-Reference_it) - Lista completa delle azioni
- [Preset Principiante](Beginner-Preset_it) - Eventi essenziali per principianti
- [Preset Intermedio](Intermediate-Preset_it) - Eventi aggiuntivi
- [Eventi e Azioni](Events-and-Actions_it) - Panoramica dei concetti base
