# Network

*[Главная](Home_ru) | [Руководство по пресетам](Preset-Guide_ru) | [Справочник событий](Event-Reference_ru)*

> **Сгенерировано автоматически** из реестра действий IDE с помощью `tools/gen_action_reference.py` — не редактируйте вручную; повторно запустите генератор после изменения действий. Переводы взяты из `tools/action_ref_i18n.py`.

### Назначить сетевую клавишу

| Свойство | Значение |
|----------|-------|
| **Имя** | `bind_network_input` |
| **Значок** | ⌨️ |
| **Категория** | Network |

Attach a local key to a "named input" reported to the host. The host then tests it with "If the player presses". The arrow keys and Space are already bound ("left", "right", "up", "down", "space")

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `name` | Текст | — | A label of your choosing (e.g. "jump", "fire") |
| `key` | Текст | — | A key name: "space", "left", "a", "5", "lshift"... |

### Создать сетевой объект

| Свойство | Значение |
|----------|-------|
| **Имя** | `network_spawn` |
| **Значок** | ✨ |
| **Категория** | Network |

Host only: create an instance that appears automatically on every client, as a smoothed "ghost". Does nothing on a client. The host drives the instance it creates -- guard its game logic with global.is_host == 1

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `object` | Объект | — | The type of object to create |
| `x` | Текст | `0` |  |
| `y` | Текст | `0` |  |
| `owner` | Текст | `0` | The player who drives this instance (0 = host). Often global.network_sender inside "Player joined".; необязательно |
| `relative` | Да/Нет | Нет | Position relative to the object running the action; необязательно |

### Создать игру

| Свойство | Значение |
|----------|-------|
| **Имя** | `host_game` |
| **Значок** | 🌐 |
| **Категория** | Network |

Become the host of a LAN multiplayer game: the other players connect to this machine. Call it once (for example in the room controller's Create event). Sets global.player_id = 0 and global.network_role = "host"

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `game_name` | Текст | `PyGameMaker` | Name shown in the server list (network discovery); необязательно |
| `max_players` | Число | `8` | Largest number of players, host included (2 to 16); необязательно |
| `port` | Число | `45782` | TCP port -- must be the same on the host and every client; необязательно |
| `player_name` | Текст | — | This player's name (empty = global.player_name, or "Player"); необязательно |
| `show_lobby` | Да/Нет | Нет | Show a "Waiting for players..." screen with a Start button before the game begins; необязательно |

### Если я управляю этим экземпляром

| Свойство | Значение |
|----------|-------|
| **Имя** | `is_instance_owner` |
| **Значок** | ❓ |
| **Категория** | Network |

A condition: true when THIS machine owns the synchronised instance. Put it before a block so the control logic only runs on the right player's machine

*Параметры:* нет

### Если игрок нажимает

| Свойство | Значение |
|----------|-------|
| **Имя** | `remote_input` |
| **Значок** | ❓ |
| **Категория** | Network |

A condition, on the host: true while the named player is holding the named input. It lets the host react to a client's keys without owning that client's character

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `player` | Текст | `0` | Player number (0 = host) |
| `name` | Текст | — | The named input to test (e.g. "jump") |

### Присоединиться к игре

| Свойство | Значение |
|----------|-------|
| **Имя** | `join_game` |
| **Значок** | 🔌 |
| **Категория** | Network |

Connect to a LAN multiplayer game hosted by another machine. The host sets global.player_id (1, 2, ...). If the host cannot be reached, the game carries on single-player

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `host` | Текст | `127.0.0.1` | The host's LAN IP address ("auto" opens the built-in connection screen); необязательно |
| `port` | Число | `45782` | TCP port -- must match the host's; необязательно |
| `player_name` | Текст | — | This player's name (empty = global.player_name, or "Player"); необязательно |

### Покинуть игру

| Свойство | Значение |
|----------|-------|
| **Имя** | `leave_game` |
| **Значок** | 🚪 |
| **Категория** | Network |

Disconnect (or stop hosting) and clear the global network variables

*Параметры:* нет

### Прочитать общую переменную

| Свойство | Значение |
|----------|-------|
| **Имя** | `get_shared_var` |
| **Значок** | 📥 |
| **Категория** | Network |

Copy a shared variable into a global variable, to use it in a calculation. The same as reading global.<name> directly

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `name` | Текст | — | Name of the shared variable to read |
| `into` | Текст | — | Name of the global variable to write the value into |

### Отправить сетевое сообщение

| Свойство | Значение |
|----------|-------|
| **Имя** | `send_network_message` |
| **Значок** | ✉️ |
| **Категория** | Network |

Broadcast a message of your own. Fires the "Network message" event on the machines concerned, with global.network_event / global.network_data / global.network_sender

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `event` | Текст | — | A label of your choosing that the handler tests (e.g. "buzz", "answer") |
| `data` | Текст | — | A number, text, true/false, or a short list; необязательно |
| `target` | Выбор | `all` | all = everyone; host = the host only; Варианты: `all`, `host` |

### Задать сетевой режим (v1)

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_network_mode` |
| **Значок** | 🌐 |
| **Категория** | Network |

An older low-level action: starts the room in host or client mode (spectator only -- a client's input has no effect). Prefer "Host a Game" / "Join a Game". Kept for existing projects and the --net-host / --net-client flags

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `mode` | Выбор | `host` | Host = others connect to you; Client = you connect to a host; Варианты: `host`, `client` |
| `host` | Текст | `127.0.0.1` | The host's LAN IP address (Client mode only); необязательно |
| `port` | Число | `45782` | TCP port -- must be the same on the host and the client; необязательно |

### Задать общую переменную

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_shared_var` |
| **Значок** | 📤 |
| **Категория** | Network |

Write a variable shared by every machine. On the host it applies immediately; on a client it is a request sent to the host. Readable anywhere as global.<name>

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `name` | Текст | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Текст | `0` | A number, text or true/false (complex objects are refused) |

### Задать владельца экземпляра

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_instance_owner` |
| **Значок** | 🎮 |
| **Категория** | Network |

Choose which player drives this synchronised instance (0 = host, 1, 2, ... = clients). On that player's machine the instance runs locally and feels responsive, and its state is reported back to the host; everywhere else it is a smoothed ghost. Call it on the host, guarded by global.is_host == 1

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `player` | Текст | `0` | Player number (0 = host). Often global.network_sender inside "Player joined". |

### Задать частоту синхронизации

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_sync_rate` |
| **Значок** | ⏱️ |
| **Категория** | Network |

Adjust how often the host sends snapshots, and how far behind clients draw them. Call it once on the host, and on the clients for the delay

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `hz` | Число | `20` | 10-30 works well on a local network (default 20); необязательно |
| `interp_ms` | Число | `100` | How far behind ghosts are drawn, in milliseconds (default 100); необязательно |

### Начать сетевую игру

| Свойство | Значение |
|----------|-------|
| **Имя** | `start_networked_game` |
| **Значок** | 🚦 |
| **Категория** | Network |

Host only: take everyone out of the waiting room and begin. Fires the "Networked game started" event on every machine

*Параметры:* нет

### Синхронизировать этот экземпляр

| Свойство | Значение |
|----------|-------|
| **Имя** | `sync_instance` |
| **Значок** | 🔗 |
| **Категория** | Network |

Mark the instance running this action as synchronised: its position, rotation, image and visibility are copied to every machine. Call it in the Create event. The host owns it by default; use "Set the instance's owner" to let a client drive it

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `vars` | Текст | — | Instance variable names to copy as well, separated by commas (e.g. "hp, colour"); необязательно |

---

## Другие Категории

- [Движение](Full-Action-Reference-Movement_ru) (20)
- [Экземпляр](Full-Action-Reference-Instance_ru) (12)
- [Счёт](Full-Action-Reference-Score_ru) (11)
- [Комната](Full-Action-Reference-Room_ru) (13)
- [Время](Full-Action-Reference-Timing_ru) (8)
- [Аудио](Full-Action-Reference-Audio_ru) (6)
- [Игра](Full-Action-Reference-Game_ru) (25)
- [Управление](Full-Action-Reference-Control_ru) (19)
- [Сетка](Full-Action-Reference-Grid_ru) (4)
- [Виды](Full-Action-Reference-Views_ru) (2)
- [3D-вид](Full-Action-Reference-3D-View-Actions_ru) (16)
- [Particles](Full-Action-Reference-Particles_ru) (8)

[← Назад к Полному Справочнику Действий](Full-Action-Reference_ru)
