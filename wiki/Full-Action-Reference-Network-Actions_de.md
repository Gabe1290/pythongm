# Network

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Netzwerktaste zuweisen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `bind_network_input` |
| **Symbol** | ⌨️ |
| **Kategorie** | Network |

Attach a local key to a "named input" reported to the host. The host then tests it with "If the player presses". The arrow keys and Space are already bound ("left", "right", "up", "down", "space")

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `name` | Text | — | A label of your choosing (e.g. "jump", "fire") |
| `key` | Text | — | A key name: "space", "left", "a", "5", "lshift"... |

### Netzwerkobjekt erzeugen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `network_spawn` |
| **Symbol** | ✨ |
| **Kategorie** | Network |

Host only: create an instance that appears automatically on every client, as a smoothed "ghost". Does nothing on a client. The host drives the instance it creates -- guard its game logic with global.is_host == 1

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `object` | Objekt | — | The type of object to create |
| `x` | Text | `0` |  |
| `y` | Text | `0` |  |
| `owner` | Text | `0` | The player who drives this instance (0 = host). Often global.network_sender inside "Player joined".; optional |
| `relative` | Ja/Nein | Nein | Position relative to the object running the action; optional |

### Spiel hosten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `host_game` |
| **Symbol** | 🌐 |
| **Kategorie** | Network |

Become the host of a LAN multiplayer game: the other players connect to this machine. Call it once (for example in the room controller's Create event). Sets global.player_id = 0 and global.network_role = "host"

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `game_name` | Text | `PyGameMaker` | Name shown in the server list (network discovery); optional |
| `max_players` | Zahl | `8` | Largest number of players, host included (2 to 16); optional |
| `port` | Zahl | `45782` | TCP port -- must be the same on the host and every client; optional |
| `player_name` | Text | — | This player's name (empty = global.player_name, or "Player"); optional |
| `show_lobby` | Ja/Nein | Nein | Show a "Waiting for players..." screen with a Start button before the game begins; optional |

### Wenn ich diese Instanz steuere

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `is_instance_owner` |
| **Symbol** | ❓ |
| **Kategorie** | Network |

A condition: true when THIS machine owns the synchronised instance. Put it before a block so the control logic only runs on the right player's machine

*Parameter:* keine

### Wenn der Spieler drückt

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `remote_input` |
| **Symbol** | ❓ |
| **Kategorie** | Network |

A condition, on the host: true while the named player is holding the named input. It lets the host react to a client's keys without owning that client's character

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `player` | Text | `0` | Player number (0 = host) |
| `name` | Text | — | The named input to test (e.g. "jump") |

### Spiel beitreten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `join_game` |
| **Symbol** | 🔌 |
| **Kategorie** | Network |

Connect to a LAN multiplayer game hosted by another machine. The host sets global.player_id (1, 2, ...). If the host cannot be reached, the game carries on single-player

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `host` | Text | `127.0.0.1` | The host's LAN IP address ("auto" opens the built-in connection screen); optional |
| `port` | Zahl | `45782` | TCP port -- must match the host's; optional |
| `player_name` | Text | — | This player's name (empty = global.player_name, or "Player"); optional |

### Spiel verlassen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `leave_game` |
| **Symbol** | 🚪 |
| **Kategorie** | Network |

Disconnect (or stop hosting) and clear the global network variables

*Parameter:* keine

### Geteilte Variable lesen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `get_shared_var` |
| **Symbol** | 📥 |
| **Kategorie** | Network |

Copy a shared variable into a global variable, to use it in a calculation. The same as reading global.<name> directly

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `name` | Text | — | Name of the shared variable to read |
| `into` | Text | — | Name of the global variable to write the value into |

### Netzwerknachricht senden

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `send_network_message` |
| **Symbol** | ✉️ |
| **Kategorie** | Network |

Broadcast a message of your own. Fires the "Network message" event on the machines concerned, with global.network_event / global.network_data / global.network_sender

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `event` | Text | — | A label of your choosing that the handler tests (e.g. "buzz", "answer") |
| `data` | Text | — | A number, text, true/false, or a short list; optional |
| `target` | Auswahl | `all` | all = everyone; host = the host only; Auswahl: `all`, `host` |

### Netzwerkmodus festlegen (v1)

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_network_mode` |
| **Symbol** | 🌐 |
| **Kategorie** | Network |

An older low-level action: starts the room in host or client mode (spectator only -- a client's input has no effect). Prefer "Host a Game" / "Join a Game". Kept for existing projects and the --net-host / --net-client flags

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `mode` | Auswahl | `host` | Host = others connect to you; Client = you connect to a host; Auswahl: `host`, `client` |
| `host` | Text | `127.0.0.1` | The host's LAN IP address (Client mode only); optional |
| `port` | Zahl | `45782` | TCP port -- must be the same on the host and the client; optional |

### Geteilte Variable setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_shared_var` |
| **Symbol** | 📤 |
| **Kategorie** | Network |

Write a variable shared by every machine. On the host it applies immediately; on a client it is a request sent to the host. Readable anywhere as global.<name>

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `name` | Text | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Text | `0` | A number, text or true/false (complex objects are refused) |

### Besitzer der Instanz festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_instance_owner` |
| **Symbol** | 🎮 |
| **Kategorie** | Network |

Choose which player drives this synchronised instance (0 = host, 1, 2, ... = clients). On that player's machine the instance runs locally and feels responsive, and its state is reported back to the host; everywhere else it is a smoothed ghost. Call it on the host, guarded by global.is_host == 1

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `player` | Text | `0` | Player number (0 = host). Often global.network_sender inside "Player joined". |

### Synchronisationsrate festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_sync_rate` |
| **Symbol** | ⏱️ |
| **Kategorie** | Network |

Adjust how often the host sends snapshots, and how far behind clients draw them. Call it once on the host, and on the clients for the delay

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `hz` | Zahl | `20` | 10-30 works well on a local network (default 20); optional |
| `interp_ms` | Zahl | `100` | How far behind ghosts are drawn, in milliseconds (default 100); optional |

### Netzwerkspiel starten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `start_networked_game` |
| **Symbol** | 🚦 |
| **Kategorie** | Network |

Host only: take everyone out of the waiting room and begin. Fires the "Networked game started" event on every machine

*Parameter:* keine

### Diese Instanz synchronisieren

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `sync_instance` |
| **Symbol** | 🔗 |
| **Kategorie** | Network |

Mark the instance running this action as synchronised: its position, rotation, image and visibility are copied to every machine. Call it in the Create event. The host owns it by default; use "Set the instance's owner" to let a client drive it

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `vars` | Text | — | Instance variable names to copy as well, separated by commas (e.g. "hp, colour"); optional |

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (8)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (25)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (16)
- [Particles](Full-Action-Reference-Particles_de) (8)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
