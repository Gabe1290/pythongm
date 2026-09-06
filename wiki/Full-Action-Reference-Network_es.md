# Network

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Asignar una tecla de red

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `bind_network_input` |
| **Icono** | ⌨️ |
| **Categoría** | Network |

Attach a local key to a "named input" reported to the host. The host then tests it with "If the player presses". The arrow keys and Space are already bound ("left", "right", "up", "down", "space")

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | A label of your choosing (e.g. "jump", "fire") |
| `key` | Texto | — | A key name: "space", "left", "a", "5", "lshift"... |

### Crear objeto en red

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `network_spawn` |
| **Icono** | ✨ |
| **Categoría** | Network |

Host only: create an instance that appears automatically on every client, as a smoothed "ghost". Does nothing on a client. The host drives the instance it creates -- guard its game logic with global.is_host == 1

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | The type of object to create |
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `owner` | Texto | `0` | The player who drives this instance (0 = host). Often global.network_sender inside "Player joined".; opcional |
| `relative` | Sí/No | No | Position relative to the object running the action; opcional |

### Alojar una partida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `host_game` |
| **Icono** | 🌐 |
| **Categoría** | Network |

Become the host of a LAN multiplayer game: the other players connect to this machine. Call it once (for example in the room controller's Create event). Sets global.player_id = 0 and global.network_role = "host"

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `game_name` | Texto | `PyGameMaker` | Name shown in the server list (network discovery); opcional |
| `max_players` | Número | `8` | Largest number of players, host included (2 to 16); opcional |
| `port` | Número | `45782` | TCP port -- must be the same on the host and every client; opcional |
| `player_name` | Texto | — | This player's name (empty = global.player_name, or "Player"); opcional |
| `show_lobby` | Sí/No | No | Show a "Waiting for players..." screen with a Start button before the game begins; opcional |

### Si yo controlo esta instancia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `is_instance_owner` |
| **Icono** | ❓ |
| **Categoría** | Network |

A condition: true when THIS machine owns the synchronised instance. Put it before a block so the control logic only runs on the right player's machine

*Parámetros:* ninguno

### Si el jugador pulsa

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `remote_input` |
| **Icono** | ❓ |
| **Categoría** | Network |

A condition, on the host: true while the named player is holding the named input. It lets the host react to a client's keys without owning that client's character

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Player number (0 = host) |
| `name` | Texto | — | The named input to test (e.g. "jump") |

### Unirse a una partida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `join_game` |
| **Icono** | 🔌 |
| **Categoría** | Network |

Connect to a LAN multiplayer game hosted by another machine. The host sets global.player_id (1, 2, ...). If the host cannot be reached, the game carries on single-player

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `host` | Texto | `127.0.0.1` | The host's LAN IP address ("auto" opens the built-in connection screen); opcional |
| `port` | Número | `45782` | TCP port -- must match the host's; opcional |
| `player_name` | Texto | — | This player's name (empty = global.player_name, or "Player"); opcional |

### Salir de la partida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `leave_game` |
| **Icono** | 🚪 |
| **Categoría** | Network |

Disconnect (or stop hosting) and clear the global network variables

*Parámetros:* ninguno

### Leer variable compartida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `get_shared_var` |
| **Icono** | 📥 |
| **Categoría** | Network |

Copy a shared variable into a global variable, to use it in a calculation. The same as reading global.<name> directly

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Name of the shared variable to read |
| `into` | Texto | — | Name of the global variable to write the value into |

### Enviar mensaje de red

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `send_network_message` |
| **Icono** | ✉️ |
| **Categoría** | Network |

Broadcast a message of your own. Fires the "Network message" event on the machines concerned, with global.network_event / global.network_data / global.network_sender

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `event` | Texto | — | A label of your choosing that the handler tests (e.g. "buzz", "answer") |
| `data` | Texto | — | A number, text, true/false, or a short list; opcional |
| `target` | Elección | `all` | all = everyone; host = the host only; Opciones: `all`, `host` |

### Definir el modo de red (v1)

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_network_mode` |
| **Icono** | 🌐 |
| **Categoría** | Network |

An older low-level action: starts the room in host or client mode (spectator only -- a client's input has no effect). Prefer "Host a Game" / "Join a Game". Kept for existing projects and the --net-host / --net-client flags

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `mode` | Elección | `host` | Host = others connect to you; Client = you connect to a host; Opciones: `host`, `client` |
| `host` | Texto | `127.0.0.1` | The host's LAN IP address (Client mode only); opcional |
| `port` | Número | `45782` | TCP port -- must be the same on the host and the client; opcional |

### Definir variable compartida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_shared_var` |
| **Icono** | 📤 |
| **Categoría** | Network |

Write a variable shared by every machine. On the host it applies immediately; on a client it is a request sent to the host. Readable anywhere as global.<name>

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Texto | `0` | A number, text or true/false (complex objects are refused) |

### Definir el dueño de la instancia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_instance_owner` |
| **Icono** | 🎮 |
| **Categoría** | Network |

Choose which player drives this synchronised instance (0 = host, 1, 2, ... = clients). On that player's machine the instance runs locally and feels responsive, and its state is reported back to the host; everywhere else it is a smoothed ghost. Call it on the host, guarded by global.is_host == 1

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Player number (0 = host). Often global.network_sender inside "Player joined". |

### Ajustar la frecuencia de sincronización

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_sync_rate` |
| **Icono** | ⏱️ |
| **Categoría** | Network |

Adjust how often the host sends snapshots, and how far behind clients draw them. Call it once on the host, and on the clients for the delay

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `hz` | Número | `20` | 10-30 works well on a local network (default 20); opcional |
| `interp_ms` | Número | `100` | How far behind ghosts are drawn, in milliseconds (default 100); opcional |

### Empezar la partida en red

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `start_networked_game` |
| **Icono** | 🚦 |
| **Categoría** | Network |

Host only: take everyone out of the waiting room and begin. Fires the "Networked game started" event on every machine

*Parámetros:* ninguno

### Sincronizar esta instancia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `sync_instance` |
| **Icono** | 🔗 |
| **Categoría** | Network |

Mark the instance running this action as synchronised: its position, rotation, image and visibility are copied to every machine. Call it in the Create event. The host owns it by default; use "Set the instance's owner" to let a client drive it

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `vars` | Texto | — | Instance variable names to copy as well, separated by commas (e.g. "hp, colour"); opcional |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (8)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (25)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (16)
- [Particles](Full-Action-Reference-Particles_es) (8)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
