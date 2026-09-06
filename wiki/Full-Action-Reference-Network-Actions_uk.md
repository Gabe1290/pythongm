# Network

*[Головна](Home_uk) | [Посібник із пресетів](Preset-Guide_uk) | [Довідник подій](Event-Reference_uk)*

> **Згенеровано автоматично** з реєстру дій IDE за допомогою `tools/gen_action_reference.py` — не редагуйте вручну; повторно запустіть генератор після зміни дій. Переклади взято з `tools/action_ref_i18n.py`.

### Призначити мережеву клавішу

| Властивість | Значення |
|----------|-------|
| **Назва** | `bind_network_input` |
| **Значок** | ⌨️ |
| **Категорія** | Network |

Attach a local key to a "named input" reported to the host. The host then tests it with "If the player presses". The arrow keys and Space are already bound ("left", "right", "up", "down", "space")

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `name` | Текст | — | A label of your choosing (e.g. "jump", "fire") |
| `key` | Текст | — | A key name: "space", "left", "a", "5", "lshift"... |

### Створити мережевий об'єкт

| Властивість | Значення |
|----------|-------|
| **Назва** | `network_spawn` |
| **Значок** | ✨ |
| **Категорія** | Network |

Host only: create an instance that appears automatically on every client, as a smoothed "ghost". Does nothing on a client. The host drives the instance it creates -- guard its game logic with global.is_host == 1

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `object` | Об'єкт | — | The type of object to create |
| `x` | Текст | `0` |  |
| `y` | Текст | `0` |  |
| `owner` | Текст | `0` | The player who drives this instance (0 = host). Often global.network_sender inside "Player joined".; необов'язково |
| `relative` | Так/Ні | Ні | Position relative to the object running the action; необов'язково |

### Створити гру

| Властивість | Значення |
|----------|-------|
| **Назва** | `host_game` |
| **Значок** | 🌐 |
| **Категорія** | Network |

Become the host of a LAN multiplayer game: the other players connect to this machine. Call it once (for example in the room controller's Create event). Sets global.player_id = 0 and global.network_role = "host"

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `game_name` | Текст | `PyGameMaker` | Name shown in the server list (network discovery); необов'язково |
| `max_players` | Число | `8` | Largest number of players, host included (2 to 16); необов'язково |
| `port` | Число | `45782` | TCP port -- must be the same on the host and every client; необов'язково |
| `player_name` | Текст | — | This player's name (empty = global.player_name, or "Player"); необов'язково |
| `show_lobby` | Так/Ні | Ні | Show a "Waiting for players..." screen with a Start button before the game begins; необов'язково |

### Якщо я керую цим екземпляром

| Властивість | Значення |
|----------|-------|
| **Назва** | `is_instance_owner` |
| **Значок** | ❓ |
| **Категорія** | Network |

A condition: true when THIS machine owns the synchronised instance. Put it before a block so the control logic only runs on the right player's machine

*Параметри:* немає

### Якщо гравець натискає

| Властивість | Значення |
|----------|-------|
| **Назва** | `remote_input` |
| **Значок** | ❓ |
| **Категорія** | Network |

A condition, on the host: true while the named player is holding the named input. It lets the host react to a client's keys without owning that client's character

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `player` | Текст | `0` | Player number (0 = host) |
| `name` | Текст | — | The named input to test (e.g. "jump") |

### Приєднатися до гри

| Властивість | Значення |
|----------|-------|
| **Назва** | `join_game` |
| **Значок** | 🔌 |
| **Категорія** | Network |

Connect to a LAN multiplayer game hosted by another machine. The host sets global.player_id (1, 2, ...). If the host cannot be reached, the game carries on single-player

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `host` | Текст | `127.0.0.1` | The host's LAN IP address ("auto" opens the built-in connection screen); необов'язково |
| `port` | Число | `45782` | TCP port -- must match the host's; необов'язково |
| `player_name` | Текст | — | This player's name (empty = global.player_name, or "Player"); необов'язково |

### Покинути гру

| Властивість | Значення |
|----------|-------|
| **Назва** | `leave_game` |
| **Значок** | 🚪 |
| **Категорія** | Network |

Disconnect (or stop hosting) and clear the global network variables

*Параметри:* немає

### Прочитати спільну змінну

| Властивість | Значення |
|----------|-------|
| **Назва** | `get_shared_var` |
| **Значок** | 📥 |
| **Категорія** | Network |

Copy a shared variable into a global variable, to use it in a calculation. The same as reading global.<name> directly

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `name` | Текст | — | Name of the shared variable to read |
| `into` | Текст | — | Name of the global variable to write the value into |

### Надіслати мережеве повідомлення

| Властивість | Значення |
|----------|-------|
| **Назва** | `send_network_message` |
| **Значок** | ✉️ |
| **Категорія** | Network |

Broadcast a message of your own. Fires the "Network message" event on the machines concerned, with global.network_event / global.network_data / global.network_sender

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `event` | Текст | — | A label of your choosing that the handler tests (e.g. "buzz", "answer") |
| `data` | Текст | — | A number, text, true/false, or a short list; необов'язково |
| `target` | Вибір | `all` | all = everyone; host = the host only; Варіанти: `all`, `host` |

### Задати мережевий режим (v1)

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_network_mode` |
| **Значок** | 🌐 |
| **Категорія** | Network |

An older low-level action: starts the room in host or client mode (spectator only -- a client's input has no effect). Prefer "Host a Game" / "Join a Game". Kept for existing projects and the --net-host / --net-client flags

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `mode` | Вибір | `host` | Host = others connect to you; Client = you connect to a host; Варіанти: `host`, `client` |
| `host` | Текст | `127.0.0.1` | The host's LAN IP address (Client mode only); необов'язково |
| `port` | Число | `45782` | TCP port -- must be the same on the host and the client; необов'язково |

### Задати спільну змінну

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_shared_var` |
| **Значок** | 📤 |
| **Категорія** | Network |

Write a variable shared by every machine. On the host it applies immediately; on a client it is a request sent to the host. Readable anywhere as global.<name>

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `name` | Текст | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Текст | `0` | A number, text or true/false (complex objects are refused) |

### Задати власника екземпляра

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_instance_owner` |
| **Значок** | 🎮 |
| **Категорія** | Network |

Choose which player drives this synchronised instance (0 = host, 1, 2, ... = clients). On that player's machine the instance runs locally and feels responsive, and its state is reported back to the host; everywhere else it is a smoothed ghost. Call it on the host, guarded by global.is_host == 1

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `player` | Текст | `0` | Player number (0 = host). Often global.network_sender inside "Player joined". |

### Задати частоту синхронізації

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_sync_rate` |
| **Значок** | ⏱️ |
| **Категорія** | Network |

Adjust how often the host sends snapshots, and how far behind clients draw them. Call it once on the host, and on the clients for the delay

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `hz` | Число | `20` | 10-30 works well on a local network (default 20); необов'язково |
| `interp_ms` | Число | `100` | How far behind ghosts are drawn, in milliseconds (default 100); необов'язково |

### Почати мережеву гру

| Властивість | Значення |
|----------|-------|
| **Назва** | `start_networked_game` |
| **Значок** | 🚦 |
| **Категорія** | Network |

Host only: take everyone out of the waiting room and begin. Fires the "Networked game started" event on every machine

*Параметри:* немає

### Синхронізувати цей екземпляр

| Властивість | Значення |
|----------|-------|
| **Назва** | `sync_instance` |
| **Значок** | 🔗 |
| **Категорія** | Network |

Mark the instance running this action as synchronised: its position, rotation, image and visibility are copied to every machine. Call it in the Create event. The host owns it by default; use "Set the instance's owner" to let a client drive it

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `vars` | Текст | — | Instance variable names to copy as well, separated by commas (e.g. "hp, colour"); необов'язково |

---

## Інші Категорії

- [Рух](Full-Action-Reference-Movement_uk) (20)
- [Екземпляр](Full-Action-Reference-Instance_uk) (12)
- [Рахунок](Full-Action-Reference-Score_uk) (11)
- [Кімната](Full-Action-Reference-Room_uk) (13)
- [Час](Full-Action-Reference-Timing_uk) (8)
- [Аудіо](Full-Action-Reference-Audio_uk) (6)
- [Гра](Full-Action-Reference-Game_uk) (25)
- [Керування](Full-Action-Reference-Control_uk) (19)
- [Сітка](Full-Action-Reference-Grid_uk) (4)
- [Вигляди](Full-Action-Reference-Views_uk) (2)
- [3D-вигляд](Full-Action-Reference-3D-View-Actions_uk) (16)
- [Particles](Full-Action-Reference-Particles_uk) (8)

[← Назад до Повного Довідника Дій](Full-Action-Reference_uk)
