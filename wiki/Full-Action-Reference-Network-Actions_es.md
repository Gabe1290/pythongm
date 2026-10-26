# Red

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Asignar una tecla de red

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `bind_network_input` |
| **Icono** | ⌨️ |
| **Categoría** | Red |

Asocia una tecla local a una «entrada con nombre» que se comunica al anfitrión. El anfitrión la comprueba después con «Si el jugador pulsa». Las flechas y la barra espaciadora ya están asociadas ("left", "right", "up", "down", "space")

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Una etiqueta que elijas (por ej. "jump", "fire") |
| `key` | Texto | — | Un nombre de tecla: "space", "left", "a", "5", "lshift"... |

### Crear objeto en red

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `network_spawn` |
| **Icono** | ✨ |
| **Categoría** | Red |

Solo en el anfitrión: crea una instancia que aparece automáticamente en todos los clientes, como un «fantasma» suavizado. En un cliente no hace nada. El anfitrión gobierna la instancia que crea: protege su lógica de juego con global.is_host == 1

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | El tipo de objeto que se crea |
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `owner` | Texto | `0` | El jugador que gobierna esta instancia (0 = anfitrión). A menudo global.network_sender dentro de «Jugador conectado».; opcional |
| `relative` | Sí/No | No | Posición relativa al objeto que ejecuta la acción; opcional |

### End Turn (File Exchange)

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `end_turn` |
| **Icono** | ✅ |
| **Categoría** | Red |

Submit your move for this round: whatever you staged with "Set a Shared Variable (File Exchange)" since your last turn, written as one file for the host to pick up. Call it once per round -- even with nothing staged -- if this game expects every player to respond every round; a player who never calls it is skipped once the round deadline passes

*Parámetros:* ninguno

### Alojar una partida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `host_game` |
| **Icono** | 🌐 |
| **Categoría** | Red |

Convierte esta máquina en el anfitrión de una partida multijugador LAN: los demás jugadores se conectan a ella. Llámala una sola vez (por ejemplo en el evento Crear del controlador de la sala). Define global.player_id = 0 y global.network_role = "host"

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `game_name` | Texto | `PyGameMaker` | Nombre que se muestra en la lista de servidores (descubrimiento en la red); opcional |
| `max_players` | Número | `8` | Número máximo de jugadores, incluido el anfitrión (de 2 a 16); opcional |
| `port` | Número | `45782` | Puerto TCP: debe ser el mismo en el anfitrión y en todos los clientes; opcional |
| `player_name` | Texto | — | Nombre de este jugador (vacío = global.player_name, o "Player"); opcional |
| `show_lobby` | Sí/No | No | Mostrar una pantalla «Esperando jugadores...» con un botón de inicio antes de empezar la partida; opcional |

### Host a Game (File Exchange)

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `host_game_files` |
| **Icono** | 🗂️ |
| **Categoría** | Red |

Become the host of a turn-based game played over a shared folder instead of a live connection -- works through a school firewall that blocks direct connections between machines. Call it once (for example in the room controller's Create event). Sets global.player_id = 0 and global.is_host = 1

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `folder` | Texto | — | Path to a folder both machines can reach (a mapped network drive, a synced Dropbox/OneDrive folder, ...) |
| `max_players` | Número | `8` | Número máximo de jugadores, incluido el anfitrión (de 2 a 16); opcional |
| `player_name` | Texto | — | Nombre de este jugador (vacío = global.player_name, o "Player"); opcional |
| `round_deadline` | Número | `30` | How long to wait for every joined player's move before advancing the round anyway (a missing player is skipped that round, not left blocking the game forever); opcional |
| `show_lobby` | Sí/No | No | Show a "Waiting for players..." screen with a Start button before handing control back to the game; opcional |

### Si yo controlo esta instancia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `is_instance_owner` |
| **Icono** | ❓ |
| **Categoría** | Red |

Una condición: verdadera cuando ESTA máquina es la dueña de la instancia sincronizada. Colócala delante de un bloque para que la lógica de control solo se ejecute en la máquina del jugador correcto

*Parámetros:* ninguno

### Si el jugador pulsa

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `remote_input` |
| **Icono** | ❓ |
| **Categoría** | Red |

Una condición, en el anfitrión: verdadera mientras el jugador indicado mantenga pulsada la entrada indicada. Permite al anfitrión reaccionar a las teclas de un cliente sin ser dueño de su personaje

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Número de jugador (0 = anfitrión) |
| `name` | Texto | — | La entrada con nombre que se comprueba (por ej. "jump") |

### Unirse a una partida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `join_game` |
| **Icono** | 🔌 |
| **Categoría** | Red |

Se conecta a una partida multijugador LAN alojada en otra máquina. El anfitrión asigna global.player_id (1, 2, ...). Si no se puede contactar con el anfitrión, la partida continúa en solitario

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `host` | Texto | `127.0.0.1` | Dirección IP del anfitrión en la LAN ("auto" abre la pantalla de conexión integrada); opcional |
| `port` | Número | `45782` | Puerto TCP: debe coincidir con el del anfitrión; opcional |
| `player_name` | Texto | — | Nombre de este jugador (vacío = global.player_name, o "Player"); opcional |

### Join a Game (File Exchange)

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `join_game_files` |
| **Icono** | 🔌 |
| **Categoría** | Red |

Join a turn-based game hosted by another machine through a shared folder. The host assigns global.player_id (1, 2, ...)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `folder` | Texto | — | Path to the SAME shared folder the host used ("auto" opens the built-in screen to type it in) |
| `player_name` | Texto | — | Nombre de este jugador (vacío = global.player_name, o "Player"); opcional |

### Salir de la partida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `leave_game` |
| **Icono** | 🚪 |
| **Categoría** | Red |

Se desconecta (o deja de alojar) y borra las variables globales de red

*Parámetros:* ninguno

### Leave the Game (File Exchange)

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `leave_game_files` |
| **Icono** | 🚪 |
| **Categoría** | Red |

Stop hosting or leave the game, and clear the global status variables

*Parámetros:* ninguno

### Leer variable compartida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `get_shared_var` |
| **Icono** | 📥 |
| **Categoría** | Red |

Copia una variable compartida en una variable global, para usarla en un cálculo. Equivale a leer global.<nombre> directamente

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Nombre de la variable compartida que se va a leer |
| `into` | Texto | — | Nombre de la variable global en la que se escribe el valor |

### Read a Shared Variable (File Exchange)

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `get_shared_var_files` |
| **Icono** | 📥 |
| **Categoría** | Red |

Copy a shared variable into a global variable, to use it in a calculation. The same as reading global.<name> directly -- the value as of the last round the host published, not live

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Nombre de la variable compartida que se va a leer |
| `into` | Texto | — | Nombre de la variable global en la que se escribe el valor |

### Enviar mensaje de red

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `send_network_message` |
| **Icono** | ✉️ |
| **Categoría** | Red |

Difunde un mensaje propio. Dispara el evento «Mensaje de red» en las máquinas afectadas, con global.network_event / global.network_data / global.network_sender

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `event` | Texto | — | Una etiqueta que elijas y que comprueba el manejador (por ej. "buzz", "answer") |
| `data` | Texto | — | Un número, un texto, true/false o una lista corta; opcional |
| `target` | Elección | `all` | all = todos; host = solo el anfitrión; Opciones: `all`, `host` |

### Send a Network Message (File Exchange)

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `send_network_message_files` |
| **Icono** | ✉️ |
| **Categoría** | Red |

Stage a message of your own, delivered the same way "Set a Shared Variable (File Exchange)" is -- at the next round boundary, not instantly. Fires the "Network Message (File Exchange)" event, with global.network_event / global.network_data / global.network_sender

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `event` | Texto | — | Una etiqueta que elijas y que comprueba el manejador (por ej. "buzz", "answer") |
| `data` | Texto | — | Un número, un texto, true/false o una lista corta; opcional |
| `target` | Elección | `all` | all = everyone, once they pick up the next round; host = the host only, processed immediately when the round resolves; Opciones: `all`, `host` |

### Definir el modo de red (v1)

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_network_mode` |
| **Icono** | 🌐 |
| **Categoría** | Red |

Una acción antigua de bajo nivel: arranca la sala en modo anfitrión o cliente (solo espectador: la entrada del cliente no tiene efecto). Es preferible usar «Alojar una partida» / «Unirse a una partida». Se conserva para los proyectos existentes y para las opciones --net-host / --net-client

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `mode` | Elección | `host` | Anfitrión = los demás se conectan a ti; Cliente = tú te conectas a un anfitrión; Opciones: `host`, `client` |
| `host` | Texto | `127.0.0.1` | Dirección IP del anfitrión en la LAN (solo en modo Cliente); opcional |
| `port` | Número | `45782` | Puerto TCP: debe ser el mismo en el anfitrión y en el cliente; opcional |

### Definir variable compartida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_shared_var` |
| **Icono** | 📤 |
| **Categoría** | Red |

Escribe una variable compartida por todas las máquinas. En el anfitrión se aplica de inmediato; en un cliente es una petición que se envía al anfitrión. Se puede leer en cualquier parte como global.<nombre>

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Un identificador simple (letras, dígitos, _): sin espacios ni operadores |
| `value` | Texto | `0` | Un número, un texto o true/false (los objetos complejos se rechazan) |

### Set a Shared Variable (File Exchange)

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_shared_var_files` |
| **Icono** | 📤 |
| **Categoría** | Red |

Stage a variable to publish to everyone. It takes effect once you call "End Turn" and the host folds your move into the next round -- not immediately, since there is no live connection to write over. Readable anywhere as global.<name> once published

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Un identificador simple (letras, dígitos, _): sin espacios ni operadores |
| `value` | Texto | `0` | Un número, un texto o true/false (los objetos complejos se rechazan) |

### Definir el dueño de la instancia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_instance_owner` |
| **Icono** | 🎮 |
| **Categoría** | Red |

Elige qué jugador gobierna esta instancia sincronizada (0 = anfitrión; 1, 2, ... = clientes). En la máquina de ese jugador la instancia se simula localmente y responde con fluidez, y su estado se comunica al anfitrión; en el resto es un fantasma suavizado. Llámala en el anfitrión, protegida con global.is_host == 1

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Número de jugador (0 = anfitrión). A menudo global.network_sender dentro de «Jugador conectado». |

### Ajustar la frecuencia de sincronización

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_sync_rate` |
| **Icono** | ⏱️ |
| **Categoría** | Red |

Ajusta con qué frecuencia envía instantáneas el anfitrión y con cuánto retraso las dibujan los clientes. Llámala una vez en el anfitrión, y en los clientes para el retraso

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `hz` | Número | `20` | De 10 a 30 funciona bien en una red local (por omisión 20); opcional |
| `interp_ms` | Número | `100` | Con cuánto retraso se dibujan los fantasmas, en milisegundos (por omisión 100); opcional |

### Empezar la partida en red

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `start_networked_game` |
| **Icono** | 🚦 |
| **Categoría** | Red |

Solo en el anfitrión: saca a todo el mundo de la sala de espera y empieza la partida. Dispara el evento «Partida en red iniciada» en todas las máquinas

*Parámetros:* ninguno

### Sincronizar esta instancia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `sync_instance` |
| **Icono** | 🔗 |
| **Categoría** | Red |

Marca como sincronizada la instancia que ejecuta esta acción: su posición, rotación, imagen y visibilidad se copian a todas las máquinas. Llámala en el evento Crear. El anfitrión es su dueño por defecto; usa «Definir el dueño de la instancia» para que la gobierne un cliente

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `vars` | Texto | — | Nombres de variables de instancia que también se copian, separados por comas (por ej. "hp, colour"); opcional |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (21)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (6)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (8)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (14)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (3)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (18)
- [Dibujo](Full-Action-Reference-Drawing_es) (11)
- [Partículas](Full-Action-Reference-Particles_es) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_es) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_es) (16)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
