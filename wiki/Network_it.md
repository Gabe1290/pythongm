# Rete (multigiocatore in LAN)

*[Home](Home_it) | [Riferimento completo delle azioni](Full-Action-Reference-Network-Actions_it) | [Estensioni](Extensions_it)*

---

PyGameMaker può trasformare un progetto in un **gioco multigiocatore in LAN**:
una macchina fa da host, le altre si uniscono tramite la rete locale, e i
giocatori condividono lo stato — un tabellone dei punti, messaggi
personalizzati e persino gli avatar degli altri sullo schermo — senza server,
senza account e senza internet. Lo fornisce l'[estensione](Extensions_it)
**LAN Multiplayer** integrata, che è attiva di default.

Gli esempi inclusi **`reseau_1`–`reseau_3`** sono esempi completi e giocabili:
una stanza condivisa in cui due giocatori si muovono insieme, un quiz di classe
con tabellone dei punti in tempo reale e una caccia al tesoro cooperativa per
due.

Supportato oggi: l'esportazione **desktop** (pygame), sia come host sia come
client, e l'esportazione **HTML5** come client (una pagina del browser si
unisce a un host desktop; non può fare da host). Un'esportazione
**Kivy/Android** esegue il gioco in modalità giocatore singolo — le azioni di
rete lì non fanno nulla, senza rischi.

---

## Due livelli

**Livello A — lavagna condivisa.** Niente avatar, solo stato condiviso:
variabili che ogni giocatore può leggere e scrivere, messaggi personalizzati e
chi è connesso. È il modo più semplice per aggiungere il multigiocatore a un
progetto — un quiz, un tabellone dei punti condiviso, un gioco a buzzer del
tipo «chi risponde per primo».

**Livello B — istanze in rete.** Istanze create dall'host (giocatori, nemici,
oggetti da raccogliere) che compaiono e si muovono automaticamente su ogni
macchina, più avatar di proprietà di un giocatore che ognuno controlla
localmente mentre gli altri vedono una copia interpolata in modo fluido.

---

## Come funziona

- Un giocatore chiama **Ospita una partita**, di solito dall'evento Create di un
  oggetto controllore della stanza. Quella macchina diventa l'**host** — le
  macchine di tutti gli altri giocatori si collegano a essa. `global.player_id`
  diventa `0`.
- Gli altri giocatori chiamano **Unisciti a una partita** con l'indirizzo IP dell'host
  nella LAN (oppure `"auto"` per mostrare una schermata di connessione
  integrata che trova gli host nella rete automaticamente). `global.player_id`
  è assegnato dall'host (`1`, `2`, ...).
- Se l'host non è raggiungibile, **il gioco continua in modalità giocatore
  singolo** — unirsi non blocca né manda in crash mai un gioco.
- L'identità del giocatore e lo stato della connessione sono sempre leggibili
  come globali: `global.is_host`, `global.player_id`, `global.player_count`,
  `global.network_role`, `global.network_connected`.
- **Scrivi la logica del gioco con una normale azione «Se»**, ad esempio
  `global.is_host == 1`, per riservare all'host la preparazione (come creare i
  nemici) — non servono azioni speciali di «condizione di rete».
- Una variabile condivisa impostata con **Imposta variabile condivisa** è leggibile
  *ovunque* come `global.<nome>` — anche sulla macchina che l'ha impostata.
- I **messaggi personalizzati** (**Invia messaggio di rete**) permettono di
  segnalare un evento per nome con un piccolo dato allegato — una pressione di
  buzzer, una risposta scelta, un segnale di «pronto».

---

## Le azioni (categoria **Rete**)

| Azione | Cosa fa |
|--------|---------|
| **Ospita una partita** | Diventare l'host. Facoltativamente mostra una sala d'attesa con un pulsante Avvia. |
| **Unisciti a una partita** | Collegarsi a un host tramite indirizzo (o `"auto"` per la schermata di connessione integrata). |
| **Esci dalla partita** | Disconnettersi (o smettere di fare da host) e cancellare le globali di rete. |
| **Avvia la partita in rete** | Solo host: chiudere la sala d'attesa e dire a tutti di cominciare. |
| **Imposta variabile condivisa** | Scrivere una variabile che ogni macchina può leggere come `global.<nome>`. |
| **Leggi variabile condivisa** | Copiare una variabile condivisa in una globale (per usarla in un calcolo). |
| **Invia messaggio di rete** | Trasmettere a tutti un messaggio personalizzato con nome e dati. |
| **Crea oggetto in rete** | Solo host: creare un'istanza che compare su tutti i client. |
| **Sincronizza questa istanza** | Segnare l'istanza agente come replicata tra le macchine. |
| **Imposta il proprietario dell'istanza** | Dare a un giocatore specifico il controllo locale di un'istanza sincronizzata. |
| **Se controllo questa istanza** | Condizione: riserva la logica di controllo alla macchina proprietaria. |
| **Associa un tasto di rete** | Associare un tasto locale a un input con nome che l'host può leggere. |
| **Se il giocatore preme** | Condizione (host): un dato giocatore sta tenendo premuto un input con nome? |
| **Imposta la frequenza di sincronia** | Regolare la frequenza degli snapshot dell'host e il ritardo di interpolazione dei client. |

Vedi il [Riferimento completo delle azioni](Full-Action-Reference-Network-Actions_it) per tutti i parametri.

---

## Gli eventi (categoria **Rete**)

Vengono generati su ogni istanza il cui oggetto li gestisce, su ogni macchina
interessata:

| Evento | Scatta quando |
|--------|---------------|
| **Network Ready** | Un client termina la connessione all'host (l'host non lo genera per se stesso). |
| **Player Joined** | Si connette un nuovo giocatore. `global.network_sender` / `global.network_player_name` lo identificano. |
| **Player Left** | Un giocatore si disconnette. |
| **Network Message** | Arriva un **Invia messaggio di rete** — `global.network_event` / `global.network_data` / `global.network_sender`. |
| **Network Game Started** | L'host chiama **Avvia la partita in rete**. |
| **Connection Lost** | La connessione di un client all'host cade. Il gioco continua — scompaiono solo i fantasmi di quel giocatore. |

---

## Un esempio minimo di stanza condivisa (Livello A)

In un oggetto controllore di stanza invisibile:

- **Create:** `Ospita una partita` se è la macchina dell'insegnante, altrimenti
  `Unisciti a una partita` con il suo IP (o `"auto"`).
- **Create:** `Imposta variabile condivisa` `round = 1` (solo host, protetto da
  `global.is_host == 1`).
- Ovunque: `draw_text` che mostra `global.round` — tutti i giocatori vedono lo
  stesso valore.

## Un esempio minimo di avatar condivisi (Livello B)

Nell'evento Create dell'oggetto giocatore:

- `Sincronizza questa istanza` — questa istanza ora viene replicata.
- Sull'**host**: `Crea oggetto in rete` crea un'istanza giocatore per ogni
  giocatore che si connette (in un gestore di **Player Joined**), poi
  `Imposta il proprietario dell'istanza` con il numero di quel giocatore.
- Il codice di movimento protetto da `Se controllo questa istanza` gira solo sulla
  macchina del giocatore proprietario; ovunque altrove l'istanza è un fantasma
  interpolato in modo fluido.

---

## Note e limiti

- **TCP, solo LAN.** Nessun attraversamento NAT, nessun gioco via internet —
  entrambe le macchine devono essere raggiungibili sulla stessa rete locale (il
  wifi di una classe o un laboratorio cablato). Il wifi con isolamento dei
  client (comune nelle reti scolastiche gestite) blocca allo stesso modo
  rilevamento e connessione diretta; un laboratorio cablato è la soluzione più
  affidabile.
- **Porte 45782 (TCP)** e **45783 (UDP, rilevamento)** — chiedi all'assistenza
  informatica della scuola prima di usarlo su una rete gestita e aspettati un
  avviso del firewall la prima volta che fai da host.
- Un client browser (esportazione HTML5) si collega alla porta successiva a
  quella dell'host, ad esempio `45783` se l'host usa quella predefinita — avviene
  automaticamente.
- La perdita dell'host è gestita con grazia: il gioco di un client continua;
  scompaiono solo i fantasmi degli altri giocatori e scatta **Connection Lost**,
  così puoi mostrare un messaggio.
- Se l'estensione LAN Multiplayer è **disattivata**, queste azioni ed eventi
  semplicemente non fanno nulla — vedi [Estensioni](Extensions_it).

---

## Vedi anche

- [File Exchange Multiplayer](FileExchange) (in inglese) — il fratello a turni,
  per un'aula in cui un firewall blocca le connessioni dirette di questa
  estensione
- [Estensioni](Extensions_it) — come viene fornita LAN Multiplayer e come disattivarla
- [Riferimento completo delle azioni](Full-Action-Reference-Network-Actions_it) — ogni azione e parametro
- [Riferimento degli eventi](Event-Reference_it)
