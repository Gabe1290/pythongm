# Rete

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Associa un tasto di rete

| Proprietà | Valore |
|----------|-------|
| **Nome** | `bind_network_input` |
| **Icona** | ⌨️ |
| **Categoria** | Rete |

Associa un tasto locale a un «comando con nome» segnalato all'host. L'host lo controlla poi con «Se il giocatore preme». Le frecce e la barra spaziatrice sono già associate ("left", "right", "up", "down", "space")

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `name` | Testo | — | Un nome a tua scelta (per es. "jump", "fire") |
| `key` | Testo | — | Un nome di tasto: "space", "left", "a", "5", "lshift"... |

### Crea oggetto in rete

| Proprietà | Valore |
|----------|-------|
| **Nome** | `network_spawn` |
| **Icona** | ✨ |
| **Categoria** | Rete |

Solo sull'host: crea un'istanza che compare automaticamente su ogni client come «fantasma» interpolato. Su un client non fa nulla. L'host guida l'istanza che crea: proteggi la sua logica di gioco con global.is_host == 1

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | — | Il tipo di oggetto da creare |
| `x` | Testo | `0` |  |
| `y` | Testo | `0` |  |
| `owner` | Testo | `0` | Il giocatore che guida questa istanza (0 = host). Spesso global.network_sender dentro «Giocatore entrato».; facoltativo |
| `relative` | Sì/No | No | Posizione relativa all'oggetto che esegue l'azione; facoltativo |

### Ospita una partita

| Proprietà | Valore |
|----------|-------|
| **Nome** | `host_game` |
| **Icona** | 🌐 |
| **Categoria** | Rete |

Rende questa macchina l'host di una partita multigiocatore LAN: gli altri giocatori si collegano a essa. Va chiamata una sola volta (per esempio nell'evento Creazione del controller della stanza). Imposta global.player_id = 0 e global.network_role = "host"

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `game_name` | Testo | `PyGameMaker` | Nome mostrato nell'elenco dei server (rilevamento in rete); facoltativo |
| `max_players` | Numero | `8` | Numero massimo di giocatori, host compreso (da 2 a 16); facoltativo |
| `port` | Numero | `45782` | Porta TCP: deve essere la stessa sull'host e su ogni client; facoltativo |
| `player_name` | Testo | — | Nome di questo giocatore (vuoto = global.player_name, oppure "Player"); facoltativo |
| `show_lobby` | Sì/No | No | Mostrare una schermata «In attesa di giocatori...» con un pulsante Avvia prima che la partita inizi; facoltativo |

### Se controllo questa istanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `is_instance_owner` |
| **Icona** | ❓ |
| **Categoria** | Rete |

Una condizione: vera quando QUESTA macchina è proprietaria dell'istanza sincronizzata. Mettila prima di un blocco perché la logica di controllo giri solo sulla macchina del giocatore giusto

*Parametri:* nessuno

### Se il giocatore preme

| Proprietà | Valore |
|----------|-------|
| **Nome** | `remote_input` |
| **Icona** | ❓ |
| **Categoria** | Rete |

Una condizione, sull'host: vera finché il giocatore indicato tiene premuto il comando indicato. Permette all'host di reagire ai tasti di un client senza possedere il suo personaggio

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `player` | Testo | `0` | Numero del giocatore (0 = host) |
| `name` | Testo | — | Il comando con nome da controllare (per es. "jump") |

### Unisciti a una partita

| Proprietà | Valore |
|----------|-------|
| **Nome** | `join_game` |
| **Icona** | 🔌 |
| **Categoria** | Rete |

Si collega a una partita multigiocatore LAN ospitata da un'altra macchina. L'host assegna global.player_id (1, 2, ...). Se l'host non è raggiungibile, la partita prosegue da soli

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `host` | Testo | `127.0.0.1` | Indirizzo IP dell'host sulla rete locale ("auto" apre la schermata di connessione integrata); facoltativo |
| `port` | Numero | `45782` | Porta TCP: deve corrispondere a quella dell'host; facoltativo |
| `player_name` | Testo | — | Nome di questo giocatore (vuoto = global.player_name, oppure "Player"); facoltativo |

### Esci dalla partita

| Proprietà | Valore |
|----------|-------|
| **Nome** | `leave_game` |
| **Icona** | 🚪 |
| **Categoria** | Rete |

Si disconnette (o smette di ospitare) e azzera le variabili globali di rete

*Parametri:* nessuno

### Leggi variabile condivisa

| Proprietà | Valore |
|----------|-------|
| **Nome** | `get_shared_var` |
| **Icona** | 📥 |
| **Categoria** | Rete |

Copia una variabile condivisa in una variabile globale, per usarla in un calcolo. Equivale a leggere direttamente global.<nome>

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `name` | Testo | — | Nome della variabile condivisa da leggere |
| `into` | Testo | — | Nome della variabile globale in cui scrivere il valore |

### Invia messaggio di rete

| Proprietà | Valore |
|----------|-------|
| **Nome** | `send_network_message` |
| **Icona** | ✉️ |
| **Categoria** | Rete |

Trasmette un messaggio personalizzato. Attiva l'evento «Messaggio di rete» sulle macchine interessate, con global.network_event / global.network_data / global.network_sender

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `event` | Testo | — | Un nome a tua scelta che il gestore controlla (per es. "buzz", "answer") |
| `data` | Testo | — | Un numero, del testo, true/false o un breve elenco; facoltativo |
| `target` | Scelta | `all` | all = tutti; host = solo l'host; Scelte: `all`, `host` |

### Imposta la modalità di rete (v1)

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_network_mode` |
| **Icona** | 🌐 |
| **Categoria** | Rete |

Una vecchia azione di basso livello: avvia la stanza in modalità host o client (solo spettatore — i comandi del client non hanno effetto). Meglio usare «Ospita una partita» / «Unisciti a una partita». Conservata per i progetti esistenti e per le opzioni --net-host / --net-client

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `mode` | Scelta | `host` | Host = gli altri si collegano a te; Client = tu ti colleghi a un host; Scelte: `host`, `client` |
| `host` | Testo | `127.0.0.1` | Indirizzo IP dell'host sulla rete locale (solo in modalità Client); facoltativo |
| `port` | Numero | `45782` | Porta TCP: deve essere la stessa sull'host e sul client; facoltativo |

### Imposta variabile condivisa

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_shared_var` |
| **Icona** | 📤 |
| **Categoria** | Rete |

Scrive una variabile condivisa da tutte le macchine. Sull'host viene applicata subito; su un client è una richiesta inviata all'host. Leggibile ovunque come global.<nome>

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `name` | Testo | — | Un identificatore semplice (lettere, cifre, _): niente spazi né operatori |
| `value` | Testo | `0` | Un numero, del testo o true/false (gli oggetti complessi vengono rifiutati) |

### Imposta il proprietario dell'istanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_instance_owner` |
| **Icona** | 🎮 |
| **Categoria** | Rete |

Sceglie quale giocatore guida questa istanza sincronizzata (0 = host; 1, 2, ... = client). Sulla macchina di quel giocatore l'istanza gira in locale e risponde in modo fluido, e il suo stato viene riferito all'host; altrove è un fantasma interpolato. Va chiamata sull'host, protetta da global.is_host == 1

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `player` | Testo | `0` | Numero del giocatore (0 = host). Spesso global.network_sender dentro «Giocatore entrato». |

### Imposta la frequenza di sincronia

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_sync_rate` |
| **Icona** | ⏱️ |
| **Categoria** | Rete |

Regola ogni quanto l'host invia le istantanee e con quanto ritardo i client le disegnano. Va chiamata una volta sull'host, e sui client per il ritardo

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `hz` | Numero | `20` | Da 10 a 30 funziona bene su una rete locale (predefinito 20); facoltativo |
| `interp_ms` | Numero | `100` | Con quanto ritardo vengono disegnati i fantasmi, in millisecondi (predefinito 100); facoltativo |

### Avvia la partita in rete

| Proprietà | Valore |
|----------|-------|
| **Nome** | `start_networked_game` |
| **Icona** | 🚦 |
| **Categoria** | Rete |

Solo sull'host: fa uscire tutti dalla sala d'attesa e comincia la partita. Attiva l'evento «Partita di rete avviata» su ogni macchina

*Parametri:* nessuno

### Sincronizza questa istanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `sync_instance` |
| **Icona** | 🔗 |
| **Categoria** | Rete |

Contrassegna come sincronizzata l'istanza che esegue questa azione: posizione, rotazione, immagine e visibilità vengono copiate su tutte le macchine. Va chiamata nell'evento Creazione. Per impostazione predefinita è dell'host; usa «Imposta il proprietario dell'istanza» per farla guidare da un client

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `vars` | Testo | — | Nomi delle variabili di istanza da copiare anche, separati da virgole (per es. "hp, colour"); facoltativo |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (20)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (8)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (25)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (16)
- [Particelle](Full-Action-Reference-Particles_it) (8)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
