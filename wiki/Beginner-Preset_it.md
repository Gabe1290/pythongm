# Preset Principiante

*[Home](Home_it) | [Guida ai Preset](Preset-Guide_it) | [Preset Intermedio](Intermediate-Preset_it)*

Il preset **Principiante** e progettato per gli utenti che sono nuovi allo sviluppo di giochi. Fornisce un insieme selezionato di eventi e azioni essenziali che coprono i fondamenti della creazione di semplici giochi 2D senza sopraffare i principianti con troppe opzioni.

## Panoramica

Il preset Principiante include:
- **4 Tipi di Eventi** - Per rispondere alle situazioni di gioco
- **17 Tipi di Azioni** - Per controllare il comportamento del gioco
- **6 Categorie** - Eventi, Movimento, Punteggio/Vite/Salute, Istanza, Stanza, Output

---

## Eventi

Gli eventi sono trigger che rispondono a situazioni specifiche nel tuo gioco. Quando si verifica un evento, le azioni che hai definito per quell'evento verranno eseguite.

### Evento Create

| Proprieta | Valore |
|-----------|--------|
| **Nome Blocco** | `event_create` |
| **Categoria** | Eventi |
| **Descrizione** | Attivato una volta quando un'istanza viene creata per la prima volta |

**Quando si attiva:** Immediatamente quando un'istanza di oggetto viene posizionata in una stanza o creata con l'azione "Crea Istanza".

**Usi comuni:**
- Inizializzare variabili
- Impostare la posizione iniziale
- Impostare velocita o direzione iniziale
- Resettare il punteggio all'inizio del gioco

---

### Evento Step

| Proprieta | Valore |
|-----------|--------|
| **Nome Blocco** | `event_step` |
| **Categoria** | Eventi |
| **Descrizione** | Attivato ogni fotogramma (tipicamente 60 volte al secondo) |

**Quando si attiva:** Continuamente, ogni fotogramma di gioco.

**Usi comuni:**
- Movimento continuo
- Controllo delle condizioni
- Aggiornamento dello stato del gioco
- Controllo dell'animazione

---

### Evento Tasto Premuto

| Proprieta | Valore |
|-----------|--------|
| **Nome Blocco** | `event_keyboard_press` |
| **Categoria** | Eventi |
| **Descrizione** | Attivato una volta quando viene premuto un tasto specifico |

**Quando si attiva:** Una volta nel momento in cui un tasto viene premuto (non mentre e tenuto premuto).

**Tasti supportati:** Tasti freccia (su, giu, sinistra, destra), Spazio, Invio, lettere (A-Z), numeri (0-9)

**Usi comuni:**
- Controlli di movimento del giocatore
- Saltare
- Sparare
- Navigazione nei menu

---

### Evento Collisione

| Proprieta | Valore |
|-----------|--------|
| **Nome Blocco** | `event_collision` |
| **Categoria** | Eventi |
| **Descrizione** | Attivato quando questa istanza collide con un altro oggetto |

**Quando si attiva:** Ogni fotogramma in cui due istanze si sovrappongono.

**Variabile speciale:** In un evento di collisione, `other` si riferisce all'istanza con cui si sta collidendo.

**Usi comuni:**
- Raccogliere oggetti (monete, potenziamenti)
- Subire danni dai nemici
- Colpire muri o ostacoli
- Raggiungere obiettivi o checkpoint

---

## Azioni

Le azioni sono comandi che vengono eseguiti quando si attiva un evento. Piu azioni possono essere aggiunte a un singolo evento e verranno eseguite in ordine.

---

## Azioni di Movimento

### Imposta Velocita Orizzontale

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `set_hspeed` |
| **Nome Blocco** | `move_set_hspeed` |
| **Categoria** | Movimento |
| **Icona** | ↔️ |

**Descrizione:** Imposta la velocita di movimento orizzontale dell'istanza.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `value` | Numero | Velocita in pixel per fotogramma. Positivo = destra, Negativo = sinistra |

**Esempio:** Imposta `value` a `4` per muoversi a destra a 4 pixel per fotogramma, o `-4` per muoversi a sinistra.

---

### Imposta Velocita Verticale

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `set_vspeed` |
| **Nome Blocco** | `move_set_vspeed` |
| **Categoria** | Movimento |
| **Icona** | ↕️ |

**Descrizione:** Imposta la velocita di movimento verticale dell'istanza.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `value` | Numero | Velocita in pixel per fotogramma. Positivo = giu, Negativo = su |

**Esempio:** Imposta `value` a `-4` per muoversi verso l'alto a 4 pixel per fotogramma, o `4` per muoversi verso il basso.

---

### Ferma Movimento

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `stop_movement` |
| **Nome Blocco** | `move_stop` |
| **Categoria** | Movimento |
| **Icona** | 🛑 |

**Descrizione:** Ferma tutto il movimento impostando sia la velocita orizzontale che verticale a zero.

**Parametri:** Nessuno

**Usi comuni:**
- Fermare il giocatore quando colpisce un muro
- Fermare i nemici quando raggiungono una destinazione
- Mettere in pausa il movimento temporaneamente

---

### Salta alla Posizione

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `jump_to_position` |
| **Nome Blocco** | `move_jump_to` |
| **Categoria** | Movimento |
| **Icona** | 📍 |

**Descrizione:** Sposta istantaneamente l'istanza a una posizione specifica (nessun movimento graduale).

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `x` | Numero | Coordinata X di destinazione |
| `y` | Numero | Coordinata Y di destinazione |

**Esempio:** Salta alla posizione (100, 200) per teletrasportare il giocatore in quella posizione.

---

## Azioni Istanza

### Distruggi Istanza

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `destroy_instance` |
| **Nome Blocco** | `instance_destroy` |
| **Categoria** | Istanza |
| **Icona** | 💥 |

**Descrizione:** Rimuove un'istanza dal gioco.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `target` | Scelta | `self` = distrugge questa istanza, `other` = distrugge l'istanza in collisione |

**Usi comuni:**
- Rimuovere monete raccolte (`target: other` nell'evento di collisione)
- Distruggere proiettili quando colpiscono qualcosa
- Rimuovere nemici quando vengono sconfitti

---

### Crea Istanza

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `create_instance` |
| **Nome Blocco** | `instance_create` |
| **Categoria** | Istanza |
| **Icona** | ✨ |

**Descrizione:** Crea una nuova istanza di un oggetto in una posizione specificata.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `object` | Oggetto | Il tipo di oggetto da creare |
| `x` | Numero | Coordinata X per la nuova istanza |
| `y` | Numero | Coordinata Y per la nuova istanza |

**Esempio:** Crea un proiettile alla posizione del giocatore quando viene premuto Spazio.

---

## Azioni Punteggio

### Imposta Punteggio

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `set_score` |
| **Nome Blocco** | `score_set` |
| **Categoria** | Punteggio/Vite/Salute |
| **Icona** | 🏆 |

**Descrizione:** Imposta il punteggio a un valore specifico, o aggiunge/sottrae dal punteggio attuale.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `value` | Numero | Il valore del punteggio |
| `relative` | Booleano | Se vero, aggiunge il valore al punteggio attuale. Se falso, imposta il punteggio al valore |

**Esempi:**
- Resettare punteggio: `value: 0`, `relative: false`
- Aggiungere 10 punti: `value: 10`, `relative: true`
- Sottrarre 5 punti: `value: -5`, `relative: true`

---

### Aggiungi al Punteggio

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `add_score` |
| **Nome Blocco** | `score_add` |
| **Categoria** | Punteggio/Vite/Salute |
| **Icona** | ➕🏆 |

**Descrizione:** Aggiunge un valore al punteggio attuale (scorciatoia per set_score con relative=true).

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `value` | Numero | Punti da aggiungere (puo essere negativo per sottrarre) |

---

### Disegna Punteggio

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `draw_score` |
| **Nome Blocco** | `draw_score` |
| **Categoria** | Punteggio/Vite/Salute |
| **Icona** | 🖼️🏆 |

**Descrizione:** Visualizza il punteggio attuale sullo schermo.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `x` | Numero | Posizione X per disegnare il punteggio |
| `y` | Numero | Posizione Y per disegnare il punteggio |
| `caption` | Stringa | Testo da visualizzare prima del punteggio (es: "Punteggio: ") |

**Nota:** Questo dovrebbe essere usato in un evento Draw (disponibile nel preset Intermedio).

---

## Azioni Stanza

### Vai alla Stanza Successiva

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `next_room` |
| **Nome Blocco** | `room_goto_next` |
| **Categoria** | Stanza |
| **Icona** | ➡️ |

**Descrizione:** Passa alla stanza successiva nell'ordine delle stanze.

**Parametri:** Nessuno

**Nota:** Se sei gia nell'ultima stanza, questa azione non ha effetto (usa "Se Esiste Stanza Successiva" per verificare prima).

---

### Vai alla Stanza Precedente

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `previous_room` |
| **Nome Blocco** | `room_goto_previous` |
| **Categoria** | Stanza |
| **Icona** | ⬅️ |

**Descrizione:** Passa alla stanza precedente nell'ordine delle stanze.

**Parametri:** Nessuno

**Nota:** Se sei gia nella prima stanza, questa azione non ha effetto.

---

### Riavvia Stanza

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `restart_room` |
| **Nome Blocco** | `room_restart` |
| **Categoria** | Stanza |
| **Icona** | 🔄 |

**Descrizione:** Riavvia la stanza corrente, resettando tutte le istanze al loro stato iniziale.

**Parametri:** Nessuno

**Usi comuni:**
- Riavviare il livello dopo la morte del giocatore
- Resettare il puzzle dopo un fallimento
- Rigiocare un mini-gioco

---

### Vai alla Stanza

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `goto_room` |
| **Nome Blocco** | `room_goto` |
| **Categoria** | Stanza |
| **Icona** | 🚪 |

**Descrizione:** Passa a una stanza specifica per nome.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `room` | Stanza | La stanza in cui andare |

---

### Se Esiste Stanza Successiva

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `if_next_room_exists` |
| **Nome Blocco** | `room_if_next_exists` |
| **Categoria** | Stanza |
| **Icona** | ❓➡️ |

**Descrizione:** Blocco condizionale che esegue le azioni contenute solo se esiste una stanza successiva.

**Parametri:** Nessuno (le azioni sono posizionate all'interno del blocco)

**Usi comuni:**
- Verificare prima di andare alla stanza successiva
- Mostrare messaggio "Hai Vinto!" se non ci sono altre stanze

---

### Se Esiste Stanza Precedente

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `if_previous_room_exists` |
| **Nome Blocco** | `room_if_previous_exists` |
| **Categoria** | Stanza |
| **Icona** | ❓⬅️ |

**Descrizione:** Blocco condizionale che esegue le azioni contenute solo se esiste una stanza precedente.

**Parametri:** Nessuno (le azioni sono posizionate all'interno del blocco)

---

## Azioni Output

### Mostra Messaggio

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `show_message` |
| **Nome Blocco** | `output_message` |
| **Categoria** | Output |
| **Icona** | 💬 |

**Descrizione:** Visualizza una finestra di dialogo popup per il giocatore.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `message` | Stringa | Il testo da visualizzare |

**Nota:** Il gioco si mette in pausa mentre il messaggio e visualizzato. Il giocatore deve cliccare OK per continuare.

**Usi comuni:**
- Istruzioni del gioco
- Dialoghi della storia
- Messaggi di vittoria/sconfitta
- Informazioni di debug

---

### Esegui Codice

| Proprieta | Valore |
|-----------|--------|
| **Nome Azione** | `execute_code` |
| **Nome Blocco** | `execute_code` |
| **Categoria** | Output |
| **Icona** | 💻 |

**Descrizione:** Esegue codice Python personalizzato.

**Parametri:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `code` | Stringa | Codice Python da eseguire |

**Nota:** Questa e una funzionalita avanzata. Usare con cautela poiche codice errato puo causare errori.

---

## Riepilogo Categorie

| Categoria | Eventi | Azioni |
|-----------|--------|--------|
| **Eventi** | Create, Step, Tasto Premuto, Collisione | - |
| **Movimento** | - | Imposta Velocita Orizzontale, Imposta Velocita Verticale, Ferma Movimento, Salta alla Posizione |
| **Istanza** | - | Distruggi Istanza, Crea Istanza |
| **Punteggio/Vite/Salute** | - | Imposta Punteggio, Aggiungi Punteggio, Disegna Punteggio |
| **Stanza** | - | Stanza Successiva, Stanza Precedente, Riavvia Stanza, Vai alla Stanza, Se Esiste Stanza Successiva, Se Esiste Stanza Precedente |
| **Output** | - | Mostra Messaggio, Esegui Codice |

---

## Esempio: Semplice Gioco di Raccolta Monete

Ecco come configurare un gioco base di raccolta monete usando solo le funzionalita del preset Principiante:

### Oggetto Giocatore (obj_player)

**Tasto Premuto (Freccia Sinistra):**
- Imposta Velocita Orizzontale: -4

**Tasto Premuto (Freccia Destra):**
- Imposta Velocita Orizzontale: 4

**Tasto Premuto (Freccia Su):**
- Imposta Velocita Verticale: -4

**Tasto Premuto (Freccia Giu):**
- Imposta Velocita Verticale: 4

**Collisione con obj_coin:**
- Imposta Punteggio: 10 (relative: true)
- Distruggi Istanza: other

**Collisione con obj_wall:**
- Ferma Movimento

**Collisione con obj_goal:**
- Imposta Punteggio: 100 (relative: true)
- Stanza Successiva

### Oggetto Moneta (obj_coin)
Nessun evento necessario - solo un oggetto da raccogliere.

### Oggetto Muro (obj_wall)
Nessun evento necessario - solo un ostacolo solido.

### Oggetto Obiettivo (obj_goal)
Nessun evento necessario - attiva il completamento del livello quando il giocatore collide.

---

## Passare all'Intermedio

Quando ti senti a tuo agio con il preset Principiante, considera di passare all'**Intermedio** per accedere a:
- Evento Draw (per rendering personalizzato)
- Evento Destroy (pulizia quando un'istanza viene distrutta)
- Eventi Mouse (rilevamento click)
- Eventi Allarme (azioni temporizzate)
- Sistemi di Vite e Salute
- Azioni Audio e Musica
- Piu opzioni di movimento (direzione, muovi verso)

---

## Vedi Anche

- [Preset Intermedio](Intermediate-Preset_it) - Funzionalita del livello successivo
- [Riferimento Completo Azioni](Full-Action-Reference_it) - Lista completa delle azioni
- [Riferimento Eventi](Event-Reference_it) - Lista completa degli eventi
- [Eventi e Azioni](Events-and-Actions_it) - Concetti fondamentali
- [Creare il Tuo Primo Gioco](Creating-Your-First-Game_it) - Tutorial passo-passo
