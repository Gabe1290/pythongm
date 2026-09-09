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

### Salir de la partida

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `leave_game` |
| **Icono** | 🚪 |
| **Categoría** | Red |

Se desconecta (o deja de alojar) y borra las variables globales de red

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
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (18)
- [Partículas](Full-Action-Reference-Particles_es) (8)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
