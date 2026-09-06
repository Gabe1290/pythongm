# Network

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Associa un tasto di rete

| Proprietà | Valore |
|----------|-------|
| **Nome** | `bind_network_input` |
| **Icona** | ⌨️ |
| **Categoria** | Network |

Attach a local key to a "named input" reported to the host. The host then tests it with "If the player presses". The arrow keys and Space are already bound ("left", "right", "up", "down", "space")

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `name` | Testo | — | A label of your choosing (e.g. "jump", "fire") |
| `key` | Testo | — | A key name: "space", "left", "a", "5", "lshift"... |

### Crea oggetto in rete

| Proprietà | Valore |
|----------|-------|
| **Nome** | `network_spawn` |
| **Icona** | ✨ |
| **Categoria** | Network |

Host only: create an instance that appears automatically on every client, as a smoothed "ghost". Does nothing on a client. The host drives the instance it creates -- guard its game logic with global.is_host == 1

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | — | The type of object to create |
| `x` | Testo | `0` |  |
| `y` | Testo | `0` |  |
| `owner` | Testo | `0` | The player who drives this instance (0 = host). Often global.network_sender inside "Player joined".; facoltativo |
| `relative` | Sì/No | No | Position relative to the object running the action; facoltativo |

### Ospita una partita

| Proprietà | Valore |
|----------|-------|
| **Nome** | `host_game` |
| **Icona** | 🌐 |
| **Categoria** | Network |

Become the host of a LAN multiplayer game: the other players connect to this machine. Call it once (for example in the room controller's Create event). Sets global.player_id = 0 and global.network_role = "host"

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `game_name` | Testo | `PyGameMaker` | Name shown in the server list (network discovery); facoltativo |
| `max_players` | Numero | `8` | Largest number of players, host included (2 to 16); facoltativo |
| `port` | Numero | `45782` | TCP port -- must be the same on the host and every client; facoltativo |
| `player_name` | Testo | — | This player's name (empty = global.player_name, or "Player"); facoltativo |
| `show_lobby` | Sì/No | No | Show a "Waiting for players..." screen with a Start button before the game begins; facoltativo |

### Se controllo questa istanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `is_instance_owner` |
| **Icona** | ❓ |
| **Categoria** | Network |

A condition: true when THIS machine owns the synchronised instance. Put it before a block so the control logic only runs on the right player's machine

*Parametri:* nessuno

### Se il giocatore preme

| Proprietà | Valore |
|----------|-------|
| **Nome** | `remote_input` |
| **Icona** | ❓ |
| **Categoria** | Network |

A condition, on the host: true while the named player is holding the named input. It lets the host react to a client's keys without owning that client's character

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `player` | Testo | `0` | Player number (0 = host) |
| `name` | Testo | — | The named input to test (e.g. "jump") |

### Unisciti a una partita

| Proprietà | Valore |
|----------|-------|
| **Nome** | `join_game` |
| **Icona** | 🔌 |
| **Categoria** | Network |

Connect to a LAN multiplayer game hosted by another machine. The host sets global.player_id (1, 2, ...). If the host cannot be reached, the game carries on single-player

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `host` | Testo | `127.0.0.1` | The host's LAN IP address ("auto" opens the built-in connection screen); facoltativo |
| `port` | Numero | `45782` | TCP port -- must match the host's; facoltativo |
| `player_name` | Testo | — | This player's name (empty = global.player_name, or "Player"); facoltativo |

### Esci dalla partita

| Proprietà | Valore |
|----------|-------|
| **Nome** | `leave_game` |
| **Icona** | 🚪 |
| **Categoria** | Network |

Disconnect (or stop hosting) and clear the global network variables

*Parametri:* nessuno

### Leggi variabile condivisa

| Proprietà | Valore |
|----------|-------|
| **Nome** | `get_shared_var` |
| **Icona** | 📥 |
| **Categoria** | Network |

Copy a shared variable into a global variable, to use it in a calculation. The same as reading global.<name> directly

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `name` | Testo | — | Name of the shared variable to read |
| `into` | Testo | — | Name of the global variable to write the value into |

### Invia messaggio di rete

| Proprietà | Valore |
|----------|-------|
| **Nome** | `send_network_message` |
| **Icona** | ✉️ |
| **Categoria** | Network |

Broadcast a message of your own. Fires the "Network message" event on the machines concerned, with global.network_event / global.network_data / global.network_sender

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `event` | Testo | — | A label of your choosing that the handler tests (e.g. "buzz", "answer") |
| `data` | Testo | — | A number, text, true/false, or a short list; facoltativo |
| `target` | Scelta | `all` | all = everyone; host = the host only; Scelte: `all`, `host` |

### Imposta la modalità di rete (v1)

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_network_mode` |
| **Icona** | 🌐 |
| **Categoria** | Network |

An older low-level action: starts the room in host or client mode (spectator only -- a client's input has no effect). Prefer "Host a Game" / "Join a Game". Kept for existing projects and the --net-host / --net-client flags

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `mode` | Scelta | `host` | Host = others connect to you; Client = you connect to a host; Scelte: `host`, `client` |
| `host` | Testo | `127.0.0.1` | The host's LAN IP address (Client mode only); facoltativo |
| `port` | Numero | `45782` | TCP port -- must be the same on the host and the client; facoltativo |

### Imposta variabile condivisa

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_shared_var` |
| **Icona** | 📤 |
| **Categoria** | Network |

Write a variable shared by every machine. On the host it applies immediately; on a client it is a request sent to the host. Readable anywhere as global.<name>

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `name` | Testo | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Testo | `0` | A number, text or true/false (complex objects are refused) |

### Imposta il proprietario dell'istanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_instance_owner` |
| **Icona** | 🎮 |
| **Categoria** | Network |

Choose which player drives this synchronised instance (0 = host, 1, 2, ... = clients). On that player's machine the instance runs locally and feels responsive, and its state is reported back to the host; everywhere else it is a smoothed ghost. Call it on the host, guarded by global.is_host == 1

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `player` | Testo | `0` | Player number (0 = host). Often global.network_sender inside "Player joined". |

### Imposta la frequenza di sincronia

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_sync_rate` |
| **Icona** | ⏱️ |
| **Categoria** | Network |

Adjust how often the host sends snapshots, and how far behind clients draw them. Call it once on the host, and on the clients for the delay

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `hz` | Numero | `20` | 10-30 works well on a local network (default 20); facoltativo |
| `interp_ms` | Numero | `100` | How far behind ghosts are drawn, in milliseconds (default 100); facoltativo |

### Avvia la partita in rete

| Proprietà | Valore |
|----------|-------|
| **Nome** | `start_networked_game` |
| **Icona** | 🚦 |
| **Categoria** | Network |

Host only: take everyone out of the waiting room and begin. Fires the "Networked game started" event on every machine

*Parametri:* nessuno

### Sincronizza questa istanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `sync_instance` |
| **Icona** | 🔗 |
| **Categoria** | Network |

Mark the instance running this action as synchronised: its position, rotation, image and visibility are copied to every machine. Call it in the Create event. The host owns it by default; use "Set the instance's owner" to let a client drive it

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `vars` | Testo | — | Instance variable names to copy as well, separated by commas (e.g. "hp, colour"); facoltativo |

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
- [Particles](Full-Action-Reference-Particles_it) (8)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
