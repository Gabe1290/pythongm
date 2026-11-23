# Network

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

### Bind a Network Key

| Property | Value |
|----------|-------|
| **Name** | `bind_network_input` |
| **Icon** | ⌨️ |
| **Category** | Network |

Attach a local key to a "named input" reported to the host. The host then tests it with "If the player presses". The arrow keys and Space are already bound ("left", "right", "up", "down", "space")

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `name` | Text | — | A label of your choosing (e.g. "jump", "fire") |
| `key` | Text | — | A key name: "space", "left", "a", "5", "lshift"... |

### Create a Networked Object

| Property | Value |
|----------|-------|
| **Name** | `network_spawn` |
| **Icon** | ✨ |
| **Category** | Network |

Host only: create an instance that appears automatically on every client, as a smoothed "ghost". Does nothing on a client. The host drives the instance it creates -- guard its game logic with global.is_host == 1

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `object` | Object | — | The type of object to create |
| `x` | Text | `0` |  |
| `y` | Text | `0` |  |
| `owner` | Text | `0` | The player who drives this instance (0 = host). Often global.network_sender inside "Player joined".; optional |
| `relative` | Yes/No | No | Position relative to the object running the action; optional |

### End Turn (File Exchange)

| Property | Value |
|----------|-------|
| **Name** | `end_turn` |
| **Icon** | ✅ |
| **Category** | Network |

Submit your move for this round: whatever you staged with "Set a Shared Variable (File Exchange)" since your last turn, written as one file for the host to pick up. Call it once per round -- even with nothing staged -- if this game expects every player to respond every round; a player who never calls it is skipped once the round deadline passes

*Parameters:* none

### Host a Game

| Property | Value |
|----------|-------|
| **Name** | `host_game` |
| **Icon** | 🌐 |
| **Category** | Network |

Become the host of a LAN multiplayer game: the other players connect to this machine. Call it once (for example in the room controller's Create event). Sets global.player_id = 0 and global.network_role = "host"

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `game_name` | Text | `PyGameMaker` | Name shown in the server list (network discovery); optional |
| `max_players` | Number | `8` | Largest number of players, host included (2 to 16); optional |
| `port` | Number | `45782` | TCP port -- must be the same on the host and every client; optional |
| `player_name` | Text | — | This player's name (empty = global.player_name, or "Player"); optional |
| `show_lobby` | Yes/No | No | Show a "Waiting for players..." screen with a Start button before the game begins; optional |

### Host a Game (File Exchange)

| Property | Value |
|----------|-------|
| **Name** | `host_game_files` |
| **Icon** | 🗂️ |
| **Category** | Network |

Become the host of a turn-based game played over a shared folder instead of a live connection -- works through a school firewall that blocks direct connections between machines. Call it once (for example in the room controller's Create event). Sets global.player_id = 0 and global.is_host = 1

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `folder` | Text | — | Path to a folder both machines can reach (a mapped network drive, a synced Dropbox/OneDrive folder, ...) |
| `max_players` | Number | `8` | Largest number of players, host included (2 to 16); optional |
| `player_name` | Text | — | This player's name (empty = global.player_name, or "Player"); optional |
| `round_deadline` | Number | `30` | How long to wait for every joined player's move before advancing the round anyway (a missing player is skipped that round, not left blocking the game forever); optional |
| `show_lobby` | Yes/No | No | Show a "Waiting for players..." screen with a Start button before handing control back to the game; optional |

### If I Drive This Instance

| Property | Value |
|----------|-------|
| **Name** | `is_instance_owner` |
| **Icon** | ❓ |
| **Category** | Network |

A condition: true when THIS machine owns the synchronised instance. Put it before a block so the control logic only runs on the right player's machine

*Parameters:* none

### If the Player Presses

| Property | Value |
|----------|-------|
| **Name** | `remote_input` |
| **Icon** | ❓ |
| **Category** | Network |

A condition, on the host: true while the named player is holding the named input. It lets the host react to a client's keys without owning that client's character

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `player` | Text | `0` | Player number (0 = host) |
| `name` | Text | — | The named input to test (e.g. "jump") |

### Join a Game

| Property | Value |
|----------|-------|
| **Name** | `join_game` |
| **Icon** | 🔌 |
| **Category** | Network |

Connect to a LAN multiplayer game hosted by another machine. The host sets global.player_id (1, 2, ...). If the host cannot be reached, the game carries on single-player

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `host` | Text | `127.0.0.1` | The host's LAN IP address ("auto" opens the built-in connection screen); optional |
| `port` | Number | `45782` | TCP port -- must match the host's; optional |
| `player_name` | Text | — | This player's name (empty = global.player_name, or "Player"); optional |

### Join a Game (File Exchange)

| Property | Value |
|----------|-------|
| **Name** | `join_game_files` |
| **Icon** | 🔌 |
| **Category** | Network |

Join a turn-based game hosted by another machine through a shared folder. The host assigns global.player_id (1, 2, ...)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `folder` | Text | — | Path to the SAME shared folder the host used ("auto" opens the built-in screen to type it in) |
| `player_name` | Text | — | This player's name (empty = global.player_name, or "Player"); optional |

### Leave the Game

| Property | Value |
|----------|-------|
| **Name** | `leave_game` |
| **Icon** | 🚪 |
| **Category** | Network |

Disconnect (or stop hosting) and clear the global network variables

*Parameters:* none

### Leave the Game (File Exchange)

| Property | Value |
|----------|-------|
| **Name** | `leave_game_files` |
| **Icon** | 🚪 |
| **Category** | Network |

Stop hosting or leave the game, and clear the global status variables

*Parameters:* none

### Read a Shared Variable

| Property | Value |
|----------|-------|
| **Name** | `get_shared_var` |
| **Icon** | 📥 |
| **Category** | Network |

Copy a shared variable into a global variable, to use it in a calculation. The same as reading global.<name> directly

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `name` | Text | — | Name of the shared variable to read |
| `into` | Text | — | Name of the global variable to write the value into |

### Read a Shared Variable (File Exchange)

| Property | Value |
|----------|-------|
| **Name** | `get_shared_var_files` |
| **Icon** | 📥 |
| **Category** | Network |

Copy a shared variable into a global variable, to use it in a calculation. The same as reading global.<name> directly -- the value as of the last round the host published, not live

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `name` | Text | — | Name of the shared variable to read |
| `into` | Text | — | Name of the global variable to write the value into |

### Send a Network Message

| Property | Value |
|----------|-------|
| **Name** | `send_network_message` |
| **Icon** | ✉️ |
| **Category** | Network |

Broadcast a message of your own. Fires the "Network message" event on the machines concerned, with global.network_event / global.network_data / global.network_sender

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `event` | Text | — | A label of your choosing that the handler tests (e.g. "buzz", "answer") |
| `data` | Text | — | A number, text, true/false, or a short list; optional |
| `target` | Choice | `all` | all = everyone; host = the host only; Choices: `all`, `host` |

### Send a Network Message (File Exchange)

| Property | Value |
|----------|-------|
| **Name** | `send_network_message_files` |
| **Icon** | ✉️ |
| **Category** | Network |

Stage a message of your own, delivered the same way "Set a Shared Variable (File Exchange)" is -- at the next round boundary, not instantly. Fires the "Network Message (File Exchange)" event, with global.network_event / global.network_data / global.network_sender

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `event` | Text | — | A label of your choosing that the handler tests (e.g. "buzz", "answer") |
| `data` | Text | — | A number, text, true/false, or a short list; optional |
| `target` | Choice | `all` | all = everyone, once they pick up the next round; host = the host only, processed immediately when the round resolves; Choices: `all`, `host` |

### Set Network Mode (v1)

| Property | Value |
|----------|-------|
| **Name** | `set_network_mode` |
| **Icon** | 🌐 |
| **Category** | Network |

An older low-level action: starts the room in host or client mode (spectator only -- a client's input has no effect). Prefer "Host a Game" / "Join a Game". Kept for existing projects and the --net-host / --net-client flags

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `mode` | Choice | `host` | Host = others connect to you; Client = you connect to a host; Choices: `host`, `client` |
| `host` | Text | `127.0.0.1` | The host's LAN IP address (Client mode only); optional |
| `port` | Number | `45782` | TCP port -- must be the same on the host and the client; optional |

### Set a Shared Variable

| Property | Value |
|----------|-------|
| **Name** | `set_shared_var` |
| **Icon** | 📤 |
| **Category** | Network |

Write a variable shared by every machine. On the host it applies immediately; on a client it is a request sent to the host. Readable anywhere as global.<name>

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `name` | Text | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Text | `0` | A number, text or true/false (complex objects are refused) |

### Set a Shared Variable (File Exchange)

| Property | Value |
|----------|-------|
| **Name** | `set_shared_var_files` |
| **Icon** | 📤 |
| **Category** | Network |

Stage a variable to publish to everyone. It takes effect once you call "End Turn" and the host folds your move into the next round -- not immediately, since there is no live connection to write over. Readable anywhere as global.<name> once published

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `name` | Text | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Text | `0` | A number, text or true/false (complex objects are refused) |

### Set the Instance's Owner

| Property | Value |
|----------|-------|
| **Name** | `set_instance_owner` |
| **Icon** | 🎮 |
| **Category** | Network |

Choose which player drives this synchronised instance (0 = host, 1, 2, ... = clients). On that player's machine the instance runs locally and feels responsive, and its state is reported back to the host; everywhere else it is a smoothed ghost. Call it on the host, guarded by global.is_host == 1

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `player` | Text | `0` | Player number (0 = host). Often global.network_sender inside "Player joined". |

### Set the Sync Rate

| Property | Value |
|----------|-------|
| **Name** | `set_sync_rate` |
| **Icon** | ⏱️ |
| **Category** | Network |

Adjust how often the host sends snapshots, and how far behind clients draw them. Call it once on the host, and on the clients for the delay

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `hz` | Number | `20` | 10-30 works well on a local network (default 20); optional |
| `interp_ms` | Number | `100` | How far behind ghosts are drawn, in milliseconds (default 100); optional |

### Start the Networked Game

| Property | Value |
|----------|-------|
| **Name** | `start_networked_game` |
| **Icon** | 🚦 |
| **Category** | Network |

Host only: take everyone out of the waiting room and begin. Fires the "Networked game started" event on every machine

*Parameters:* none

### Synchronise This Instance

| Property | Value |
|----------|-------|
| **Name** | `sync_instance` |
| **Icon** | 🔗 |
| **Category** | Network |

Mark the instance running this action as synchronised: its position, rotation, image and visibility are copied to every machine. Call it in the Create event. The host owns it by default; use "Set the instance's owner" to let a client drive it

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `vars` | Text | — | Instance variable names to copy as well, separated by commas (e.g. "hp, colour"); optional |

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (21)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (6)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (8)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (14)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (3)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (23)
- [Drawing](Full-Action-Reference-Drawing) (11)
- [Particles](Full-Action-Reference-Particles) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions) (16)

[← Back to Full Action Reference](Full-Action-Reference)
