# Network

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Associar uma tecla de rede

| Propriedade | Valor |
|----------|-------|
| **Nome** | `bind_network_input` |
| **Ícone** | ⌨️ |
| **Categoria** | Network |

Attach a local key to a "named input" reported to the host. The host then tests it with "If the player presses". The arrow keys and Space are already bound ("left", "right", "up", "down", "space")

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | A label of your choosing (e.g. "jump", "fire") |
| `key` | Texto | — | A key name: "space", "left", "a", "5", "lshift"... |

### Criar objeto em rede

| Propriedade | Valor |
|----------|-------|
| **Nome** | `network_spawn` |
| **Ícone** | ✨ |
| **Categoria** | Network |

Host only: create an instance that appears automatically on every client, as a smoothed "ghost". Does nothing on a client. The host drives the instance it creates -- guard its game logic with global.is_host == 1

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | The type of object to create |
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `owner` | Texto | `0` | The player who drives this instance (0 = host). Often global.network_sender inside "Player joined".; opcional |
| `relative` | Sim/Não | Não | Position relative to the object running the action; opcional |

### Alojar um jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `host_game` |
| **Ícone** | 🌐 |
| **Categoria** | Network |

Become the host of a LAN multiplayer game: the other players connect to this machine. Call it once (for example in the room controller's Create event). Sets global.player_id = 0 and global.network_role = "host"

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `game_name` | Texto | `PyGameMaker` | Name shown in the server list (network discovery); opcional |
| `max_players` | Número | `8` | Largest number of players, host included (2 to 16); opcional |
| `port` | Número | `45782` | TCP port -- must be the same on the host and every client; opcional |
| `player_name` | Texto | — | This player's name (empty = global.player_name, or "Player"); opcional |
| `show_lobby` | Sim/Não | Não | Show a "Waiting for players..." screen with a Start button before the game begins; opcional |

### Se eu controlo esta instância

| Propriedade | Valor |
|----------|-------|
| **Nome** | `is_instance_owner` |
| **Ícone** | ❓ |
| **Categoria** | Network |

A condition: true when THIS machine owns the synchronised instance. Put it before a block so the control logic only runs on the right player's machine

*Parâmetros:* nenhum

### Se o jogador carregar

| Propriedade | Valor |
|----------|-------|
| **Nome** | `remote_input` |
| **Ícone** | ❓ |
| **Categoria** | Network |

A condition, on the host: true while the named player is holding the named input. It lets the host react to a client's keys without owning that client's character

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Player number (0 = host) |
| `name` | Texto | — | The named input to test (e.g. "jump") |

### Entrar num jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `join_game` |
| **Ícone** | 🔌 |
| **Categoria** | Network |

Connect to a LAN multiplayer game hosted by another machine. The host sets global.player_id (1, 2, ...). If the host cannot be reached, the game carries on single-player

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `host` | Texto | `127.0.0.1` | The host's LAN IP address ("auto" opens the built-in connection screen); opcional |
| `port` | Número | `45782` | TCP port -- must match the host's; opcional |
| `player_name` | Texto | — | This player's name (empty = global.player_name, or "Player"); opcional |

### Sair do jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `leave_game` |
| **Ícone** | 🚪 |
| **Categoria** | Network |

Disconnect (or stop hosting) and clear the global network variables

*Parâmetros:* nenhum

### Ler variável partilhada

| Propriedade | Valor |
|----------|-------|
| **Nome** | `get_shared_var` |
| **Ícone** | 📥 |
| **Categoria** | Network |

Copy a shared variable into a global variable, to use it in a calculation. The same as reading global.<name> directly

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Name of the shared variable to read |
| `into` | Texto | — | Name of the global variable to write the value into |

### Enviar mensagem de rede

| Propriedade | Valor |
|----------|-------|
| **Nome** | `send_network_message` |
| **Ícone** | ✉️ |
| **Categoria** | Network |

Broadcast a message of your own. Fires the "Network message" event on the machines concerned, with global.network_event / global.network_data / global.network_sender

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `event` | Texto | — | A label of your choosing that the handler tests (e.g. "buzz", "answer") |
| `data` | Texto | — | A number, text, true/false, or a short list; opcional |
| `target` | Escolha | `all` | all = everyone; host = the host only; Opções: `all`, `host` |

### Definir o modo de rede (v1)

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_network_mode` |
| **Ícone** | 🌐 |
| **Categoria** | Network |

An older low-level action: starts the room in host or client mode (spectator only -- a client's input has no effect). Prefer "Host a Game" / "Join a Game". Kept for existing projects and the --net-host / --net-client flags

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `mode` | Escolha | `host` | Host = others connect to you; Client = you connect to a host; Opções: `host`, `client` |
| `host` | Texto | `127.0.0.1` | The host's LAN IP address (Client mode only); opcional |
| `port` | Número | `45782` | TCP port -- must be the same on the host and the client; opcional |

### Definir variável partilhada

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_shared_var` |
| **Ícone** | 📤 |
| **Categoria** | Network |

Write a variable shared by every machine. On the host it applies immediately; on a client it is a request sent to the host. Readable anywhere as global.<name>

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Texto | `0` | A number, text or true/false (complex objects are refused) |

### Definir o dono da instância

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_instance_owner` |
| **Ícone** | 🎮 |
| **Categoria** | Network |

Choose which player drives this synchronised instance (0 = host, 1, 2, ... = clients). On that player's machine the instance runs locally and feels responsive, and its state is reported back to the host; everywhere else it is a smoothed ghost. Call it on the host, guarded by global.is_host == 1

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Player number (0 = host). Often global.network_sender inside "Player joined". |

### Ajustar a frequência de sincronização

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_sync_rate` |
| **Ícone** | ⏱️ |
| **Categoria** | Network |

Adjust how often the host sends snapshots, and how far behind clients draw them. Call it once on the host, and on the clients for the delay

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `hz` | Número | `20` | 10-30 works well on a local network (default 20); opcional |
| `interp_ms` | Número | `100` | How far behind ghosts are drawn, in milliseconds (default 100); opcional |

### Começar o jogo em rede

| Propriedade | Valor |
|----------|-------|
| **Nome** | `start_networked_game` |
| **Ícone** | 🚦 |
| **Categoria** | Network |

Host only: take everyone out of the waiting room and begin. Fires the "Networked game started" event on every machine

*Parâmetros:* nenhum

### Sincronizar esta instância

| Propriedade | Valor |
|----------|-------|
| **Nome** | `sync_instance` |
| **Ícone** | 🔗 |
| **Categoria** | Network |

Mark the instance running this action as synchronised: its position, rotation, image and visibility are copied to every machine. Call it in the Create event. The host owns it by default; use "Set the instance's owner" to let a client drive it

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `vars` | Texto | — | Instance variable names to copy as well, separated by commas (e.g. "hp, colour"); opcional |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (8)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (25)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (16)
- [Particles](Full-Action-Reference-Particles_pt) (8)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
