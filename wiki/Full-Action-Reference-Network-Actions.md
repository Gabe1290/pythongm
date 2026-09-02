# Network

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

### Bind Network Input

| Property | Value |
|----------|-------|
| **Name** | `bind_network_input` |
| **Icon** | ⌨️ |
| **Category** | Network |

Map a local key to a "named input" reported to the host. The host then tests it with "If Player Presses". The arrow keys and Space are already bound ("left", "right", "up", "down", "space")

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `name` | Text | — | A free-form label (e.g. "jump", "fire") |
| `key` | Text | — | Key name: "space", "left", "a", "5", "lshift"... |

### Create Networked Instance

| Property | Value |
|----------|-------|
| **Name** | `network_spawn` |
| **Icon** | ✨ |
| **Category** | Network |

Host only: create an instance that automatically appears on every client (as interpolated "ghosts"). No effect on a client. The created instance is driven by the host -- guard its game logic with global.is_host == 1

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `object` | Object | — | Object type to create |
| `x` | Text | `0` |  |
| `y` | Text | `0` |  |
| `owner` | Text | `0` | Player who drives the instance (0 = host). Often global.network_sender inside "Player Joined".; optional |
| `relative` | Yes/No | No | Position relative to the object running the action; optional |

### Set Instance Owner

| Property | Value |
|----------|-------|
| **Name** | `set_instance_owner` |
| **Icon** | 🎮 |
| **Category** | Network |

Assign which player drives this synced instance (0 = host, 1, 2, ... = clients). On that player's machine, the instance runs locally (responsive) and its state is reported back to the host; everywhere else it's an interpolated ghost. Call it on the host (guarded by global.is_host == 1)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `player` | Text | `0` | Player number (0 = host). Often global.network_sender inside "Player Joined". |

### Set Shared Variable

| Property | Value |
|----------|-------|
| **Name** | `set_shared_var` |
| **Icon** | 📤 |
| **Category** | Network |

Write a variable shared by every machine. On the host: applied immediately. On a client: sent as a request to the host. Readable everywhere via global.<name>

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `name` | Text | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Text | `0` | A number, text, or boolean (complex objects are rejected) |

### Start Networked Game

| Property | Value |
|----------|-------|
| **Name** | `start_networked_game` |
| **Icon** | 🚦 |
| **Category** | Network |

Host only: move everyone out of the waiting lobby and start the game. Fires the "Network Game Started" event on every machine

*Parameters:* none

### Send Network Message

| Property | Value |
|----------|-------|
| **Name** | `send_network_message` |
| **Icon** | ✉️ |
| **Category** | Network |

Broadcast a custom message. Fires the "Network Message" event on the machines it reaches, with global.network_event / global.network_data / global.network_sender

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `event` | Text | — | A free-form label the handler tests for (e.g. "buzz", "answer") |
| `data` | Text | — | A number, text, boolean, or small list; optional |
| `target` | Choice | `all` | all = everyone; host = the host only; Choices: `all`, `host` |

### Host Game

| Property | Value |
|----------|-------|
| **Name** | `host_game` |
| **Icon** | 🌐 |
| **Category** | Network |

Become the host of a LAN multiplayer game: other players connect to this machine. Call once (e.g. in the room controller's Create event). Sets global.player_id = 0 and global.network_role = "host"

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `game_name` | Text | `PyGameMaker` | Name shown in the server list (network discovery, Phase 6); optional |
| `max_players` | Number | `8` | Maximum number of players, including the host (2 to 16); optional |
| `port` | Number | `45782` | TCP port -- must match on the host and every client; optional |
| `player_name` | Text | — | This player's name (empty = global.player_name, or "Player"); optional |
| `show_lobby` | Yes/No | No | Show a "Waiting for players..." screen with a Start button before the game begins; optional |

### Get Shared Variable

| Property | Value |
|----------|-------|
| **Name** | `get_shared_var` |
| **Icon** | 📥 |
| **Category** | Network |

Copy a shared variable into a global variable (to use it in a calculation). Equivalent to reading global.<name> directly

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `name` | Text | — | Name of the shared variable to read |
| `into` | Text | — | Name of the global variable to write the value into |

### Leave Game

| Property | Value |
|----------|-------|
| **Name** | `leave_game` |
| **Icon** | 🚪 |
| **Category** | Network |

Disconnect (or stop hosting) and clear the network global variables

*Parameters:* none

### Join Game

| Property | Value |
|----------|-------|
| **Name** | `join_game` |
| **Icon** | 🔌 |
| **Category** | Network |

Connect to a LAN multiplayer game hosted by another machine. global.player_id will be set by the host (1, 2, ...). If the host can't be reached, the game continues single-player

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `host` | Text | `127.0.0.1` | The host's LAN IP address ("auto" = the built-in connect screen, Phase 6); optional |
| `port` | Number | `45782` | TCP port -- must match the host's; optional |
| `player_name` | Text | — | This player's name (empty = global.player_name, or "Player"); optional |

### Set Sync Rate

| Property | Value |
|----------|-------|
| **Name** | `set_sync_rate` |
| **Icon** | ⏱️ |
| **Category** | Network |

Tune the host's snapshot rate and the clients' interpolation delay. Call it once on the host (and on clients for the delay)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `hz` | Number | `20` | 10-30 works well on a LAN (default 20); optional |
| `interp_ms` | Number | `100` | Ghost display delay, in milliseconds (default 100); optional |

### Set Network Mode (v1)

| Property | Value |
|----------|-------|
| **Name** | `set_network_mode` |
| **Icon** | 🌐 |
| **Category** | Network |

Older low-level action: starts the room as host or client (spectator only -- the client's input has no effect). Prefer "Host Game" / "Join Game". Kept for existing projects and the --net-host / --net-client flags

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `mode` | Choice | `host` | Host = others connect to you; Client = you connect to a host; Choices: `host`, `client` |
| `host` | Text | `127.0.0.1` | The host's LAN IP address (Client mode only); optional |
| `port` | Number | `45782` | TCP port -- must match on the host and the client; optional |

### If I Own This Instance

| Property | Value |
|----------|-------|
| **Name** | `is_instance_owner` |
| **Icon** | ❓ |
| **Category** | Network |

Condition: true if THIS machine owns the synced instance. Place it before a block so control logic only runs on the right player's machine

*Parameters:* none

### If Player Presses

| Property | Value |
|----------|-------|
| **Name** | `remote_input` |
| **Icon** | ❓ |
| **Category** | Network |

Condition (on the host): true if the given player is holding the named input. Lets the host react to a client's keys without owning its avatar

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `player` | Text | `0` | Player number (0 = host) |
| `name` | Text | — | The named input to test (e.g. "jump") |

### Sync This Instance

| Property | Value |
|----------|-------|
| **Name** | `sync_instance` |
| **Icon** | 🔗 |
| **Category** | Network |

Mark the instance running this action as "synced": its position, rotation, image, and visibility replicate to every machine. Call it in the Create event. The host owns it by default -- use "Set Instance Owner" to let a client drive it

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `vars` | Text | — | Names of instance variables to also replicate, comma-separated (e.g. "hp, color"); optional |

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (20)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (11)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (8)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (25)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (4)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (16)
- [Particles](Full-Action-Reference-Particles) (8)

[← Back to Full Action Reference](Full-Action-Reference)
