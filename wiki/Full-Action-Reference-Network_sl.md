# Network

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Dodeli omrežno tipko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `bind_network_input` |
| **Ikona** | ⌨️ |
| **Kategorija** | Network |

Attach a local key to a "named input" reported to the host. The host then tests it with "If the player presses". The arrow keys and Space are already bound ("left", "right", "up", "down", "space")

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `name` | Besedilo | — | A label of your choosing (e.g. "jump", "fire") |
| `key` | Besedilo | — | A key name: "space", "left", "a", "5", "lshift"... |

### Ustvari omrežni predmet

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `network_spawn` |
| **Ikona** | ✨ |
| **Kategorija** | Network |

Host only: create an instance that appears automatically on every client, as a smoothed "ghost". Does nothing on a client. The host drives the instance it creates -- guard its game logic with global.is_host == 1

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | The type of object to create |
| `x` | Besedilo | `0` |  |
| `y` | Besedilo | `0` |  |
| `owner` | Besedilo | `0` | The player who drives this instance (0 = host). Often global.network_sender inside "Player joined".; neobvezno |
| `relative` | Da/Ne | Ne | Position relative to the object running the action; neobvezno |

### Gosti igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `host_game` |
| **Ikona** | 🌐 |
| **Kategorija** | Network |

Become the host of a LAN multiplayer game: the other players connect to this machine. Call it once (for example in the room controller's Create event). Sets global.player_id = 0 and global.network_role = "host"

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `game_name` | Besedilo | `PyGameMaker` | Name shown in the server list (network discovery); neobvezno |
| `max_players` | Število | `8` | Largest number of players, host included (2 to 16); neobvezno |
| `port` | Število | `45782` | TCP port -- must be the same on the host and every client; neobvezno |
| `player_name` | Besedilo | — | This player's name (empty = global.player_name, or "Player"); neobvezno |
| `show_lobby` | Da/Ne | Ne | Show a "Waiting for players..." screen with a Start button before the game begins; neobvezno |

### Če upravljam ta primerek

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `is_instance_owner` |
| **Ikona** | ❓ |
| **Kategorija** | Network |

A condition: true when THIS machine owns the synchronised instance. Put it before a block so the control logic only runs on the right player's machine

*Parametri:* brez

### Če igralec pritisne

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `remote_input` |
| **Ikona** | ❓ |
| **Kategorija** | Network |

A condition, on the host: true while the named player is holding the named input. It lets the host react to a client's keys without owning that client's character

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `player` | Besedilo | `0` | Player number (0 = host) |
| `name` | Besedilo | — | The named input to test (e.g. "jump") |

### Pridruži se igri

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `join_game` |
| **Ikona** | 🔌 |
| **Kategorija** | Network |

Connect to a LAN multiplayer game hosted by another machine. The host sets global.player_id (1, 2, ...). If the host cannot be reached, the game carries on single-player

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `host` | Besedilo | `127.0.0.1` | The host's LAN IP address ("auto" opens the built-in connection screen); neobvezno |
| `port` | Število | `45782` | TCP port -- must match the host's; neobvezno |
| `player_name` | Besedilo | — | This player's name (empty = global.player_name, or "Player"); neobvezno |

### Zapusti igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `leave_game` |
| **Ikona** | 🚪 |
| **Kategorija** | Network |

Disconnect (or stop hosting) and clear the global network variables

*Parametri:* brez

### Preberi skupno spremenljivko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `get_shared_var` |
| **Ikona** | 📥 |
| **Kategorija** | Network |

Copy a shared variable into a global variable, to use it in a calculation. The same as reading global.<name> directly

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `name` | Besedilo | — | Name of the shared variable to read |
| `into` | Besedilo | — | Name of the global variable to write the value into |

### Pošlji omrežno sporočilo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `send_network_message` |
| **Ikona** | ✉️ |
| **Kategorija** | Network |

Broadcast a message of your own. Fires the "Network message" event on the machines concerned, with global.network_event / global.network_data / global.network_sender

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `event` | Besedilo | — | A label of your choosing that the handler tests (e.g. "buzz", "answer") |
| `data` | Besedilo | — | A number, text, true/false, or a short list; neobvezno |
| `target` | Izbira | `all` | all = everyone; host = the host only; Izbire: `all`, `host` |

### Nastavi omrežni način (v1)

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_network_mode` |
| **Ikona** | 🌐 |
| **Kategorija** | Network |

An older low-level action: starts the room in host or client mode (spectator only -- a client's input has no effect). Prefer "Host a Game" / "Join a Game". Kept for existing projects and the --net-host / --net-client flags

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `mode` | Izbira | `host` | Host = others connect to you; Client = you connect to a host; Izbire: `host`, `client` |
| `host` | Besedilo | `127.0.0.1` | The host's LAN IP address (Client mode only); neobvezno |
| `port` | Število | `45782` | TCP port -- must be the same on the host and the client; neobvezno |

### Nastavi skupno spremenljivko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_shared_var` |
| **Ikona** | 📤 |
| **Kategorija** | Network |

Write a variable shared by every machine. On the host it applies immediately; on a client it is a request sent to the host. Readable anywhere as global.<name>

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `name` | Besedilo | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Besedilo | `0` | A number, text or true/false (complex objects are refused) |

### Nastavi lastnika primerka

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_instance_owner` |
| **Ikona** | 🎮 |
| **Kategorija** | Network |

Choose which player drives this synchronised instance (0 = host, 1, 2, ... = clients). On that player's machine the instance runs locally and feels responsive, and its state is reported back to the host; everywhere else it is a smoothed ghost. Call it on the host, guarded by global.is_host == 1

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `player` | Besedilo | `0` | Player number (0 = host). Often global.network_sender inside "Player joined". |

### Nastavi hitrost sinhronizacije

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_sync_rate` |
| **Ikona** | ⏱️ |
| **Kategorija** | Network |

Adjust how often the host sends snapshots, and how far behind clients draw them. Call it once on the host, and on the clients for the delay

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `hz` | Število | `20` | 10-30 works well on a local network (default 20); neobvezno |
| `interp_ms` | Število | `100` | How far behind ghosts are drawn, in milliseconds (default 100); neobvezno |

### Začni omrežno igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `start_networked_game` |
| **Ikona** | 🚦 |
| **Kategorija** | Network |

Host only: take everyone out of the waiting room and begin. Fires the "Networked game started" event on every machine

*Parametri:* brez

### Sinhroniziraj ta primerek

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `sync_instance` |
| **Ikona** | 🔗 |
| **Kategorija** | Network |

Mark the instance running this action as synchronised: its position, rotation, image and visibility are copied to every machine. Call it in the Create event. The host owns it by default; use "Set the instance's owner" to let a client drive it

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `vars` | Besedilo | — | Instance variable names to copy as well, separated by commas (e.g. "hp, colour"); neobvezno |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (20)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (11)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (8)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (25)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (16)
- [Particles](Full-Action-Reference-Particles_sl) (8)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
