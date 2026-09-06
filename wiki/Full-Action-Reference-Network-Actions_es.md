# Network

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Asignar una tecla de red

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `bind_network_input` |
| **Icono** | ⌨️ |
| **Categoría** | Network |

Asocia una tecla local a una «entrada con nombre» que se comunica al anfitrión. El anfitrión la comprueba después con «Si el jugador pulsa». Las flechas y la barra espaciadora ya están asociadas ("left", "right", "up", "down", "space")

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

Solo en el anfitrión: crea una instancia que aparece automáticamente en todos los clientes, como un «fantasma» suavizado. En un cliente no hace nada. El anfitrión gobierna la instancia que crea: protege su lógica de juego con global.is_host == 1

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

Convierte esta máquina en el anfitrión de una partida multijugador LAN: los demás jugadores se conectan a ella. Llámala una sola vez (por ejemplo en el evento Crear del controlador de la sala). Define global.player_id = 0 y global.network_role = "host"

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

Una condición: verdadera cuando ESTA máquina es la dueña de la instancia sincronizada. Colócala delante de un bloque para que la lógica de control solo se ejecute en la máquina del jugador correcto

*Parámetros:* ninguno

### Si el jugador pulsa

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `remote_input` |
| **Icono** | ❓ |
| **Categoría** | Network |

Una condición, en el anfitrión: verdadera mientras el jugador indicado mantenga pulsada la entrada indicada. Permite al anfitrión reaccionar a las teclas de un cliente sin ser dueño de su personaje

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

Se conecta a una partida multijugador LAN alojada en otra máquina. El anfitrión asigna global.player_id (1, 2, ...). Si no se puede contactar con el anfitrión, la partida continúa en solitario

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

Se desconecta (o deja de alojar) y borra las variables globales de red

*Parámetros:* ninguno

### Leer variable compartida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `get_shared_var` |
| **Icono** | 📥 |
| **Categoría** | Network |

Copia una variable compartida en una variable global, para usarla en un cálculo. Equivale a leer global.<nombre> directamente

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

Difunde un mensaje propio. Dispara el evento «Mensaje de red» en las máquinas afectadas, con global.network_event / global.network_data / global.network_sender

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

Una acción antigua de bajo nivel: arranca la sala en modo anfitrión o cliente (solo espectador: la entrada del cliente no tiene efecto). Es preferible usar «Alojar una partida» / «Unirse a una partida». Se conserva para los proyectos existentes y para las opciones --net-host / --net-client

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

Escribe una variable compartida por todas las máquinas. En el anfitrión se aplica de inmediato; en un cliente es una petición que se envía al anfitrión. Se puede leer en cualquier parte como global.<nombre>

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

Elige qué jugador gobierna esta instancia sincronizada (0 = anfitrión; 1, 2, ... = clientes). En la máquina de ese jugador la instancia se simula localmente y responde con fluidez, y su estado se comunica al anfitrión; en el resto es un fantasma suavizado. Llámala en el anfitrión, protegida con global.is_host == 1

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Player number (0 = host). Often global.network_sender inside "Player joined". |

### Ajustar la frecuencia de sincronización

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_sync_rate` |
| **Icono** | ⏱️ |
| **Categoría** | Network |

Ajusta con qué frecuencia envía instantáneas el anfitrión y con cuánto retraso las dibujan los clientes. Llámala una vez en el anfitrión, y en los clientes para el retraso

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

Solo en el anfitrión: saca a todo el mundo de la sala de espera y empieza la partida. Dispara el evento «Partida en red iniciada» en todas las máquinas

*Parámetros:* ninguno

### Sincronizar esta instancia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `sync_instance` |
| **Icono** | 🔗 |
| **Categoría** | Network |

Marca como sincronizada la instancia que ejecuta esta acción: su posición, rotación, imagen y visibilidad se copian a todas las máquinas. Llámala en el evento Crear. El anfitrión es su dueño por defecto; usa «Definir el dueño de la instancia» para que la gobierne un cliente

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
