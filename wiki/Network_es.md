# Red (multijugador en LAN)

*[Inicio](Home_es) | [Referencia completa de acciones](Full-Action-Reference-Network-Actions_es) | [Extensiones](Extensions_es)*

---

PyGameMaker puede convertir un proyecto en un **juego multijugador en red
local (LAN)**: una máquina hace de anfitrión, las demás se unen por la red
local, y los jugadores comparten estado — un marcador, mensajes
personalizados e incluso los avatares de los demás en pantalla — sin
servidor, sin cuenta y sin internet. Lo proporciona la **extensión**
[LAN Multiplayer](Extensions_es) integrada, que viene activada.

Los ejemplos incluidos **`reseau_1`–`reseau_3`** son ejemplos completos y
jugables: una sala compartida donde dos jugadores se mueven juntos, un
cuestionario de clase con marcador en directo y una búsqueda del tesoro
cooperativa para dos.

Compatible hoy: la exportación de **escritorio** (pygame), tanto como
anfitrión como cliente, y la exportación **HTML5** como cliente (una página
del navegador se une a un anfitrión de escritorio; no puede ser anfitrión).
Una exportación **Kivy/Android** ejecuta el juego en modo un jugador — las
acciones de red no hacen nada, sin riesgo.

---

## Dos niveles

**Nivel A — pizarra compartida.** Sin avatares, solo estado compartido:
variables que todos los jugadores pueden leer y escribir, mensajes
personalizados y quién está conectado. Es la forma más sencilla de añadir
multijugador a un proyecto — un cuestionario, un marcador compartido, un
timbre de «el primero que responde».

**Nivel B — instancias en red.** Instancias creadas por el anfitrión
(jugadores, enemigos, objetos recogibles) que aparecen y se mueven
automáticamente en todas las máquinas, además de avatares propiedad de un
jugador que cada uno controla localmente mientras los demás ven una copia
interpolada con suavidad.

---

## Cómo funciona

- Un jugador llama a **Alojar una partida**, normalmente desde el evento Create de
  un objeto controlador de sala. Esa máquina pasa a ser el **anfitrión** — las
  máquinas de todos los demás jugadores se conectan a ella.
  `global.player_id` pasa a ser `0`.
- Los demás jugadores llaman a **Unirse a una partida** con la dirección IP del
  anfitrión en la LAN (o `"auto"` para mostrar una pantalla de conexión
  integrada que encuentra anfitriones en la red automáticamente). El
  anfitrión asigna `global.player_id` (`1`, `2`, ...).
- Si no se puede alcanzar al anfitrión, **el juego sigue en modo un
  jugador** — unirse nunca bloquea ni rompe un juego.
- La identidad del jugador y el estado de la conexión siempre se pueden leer
  como globales: `global.is_host`, `global.player_id`, `global.player_count`,
  `global.network_role`, `global.network_connected`.
- **Escribe la lógica de tu juego con una acción «Si» normal**, p. ej.
  `global.is_host == 1`, para reservar al anfitrión la preparación (como
  crear enemigos) — no hacen falta acciones especiales de «condición de red».
- Una variable compartida definida con **Definir variable compartida** se puede leer
  *en todas partes* como `global.<nombre>` — incluida la máquina que la
  definió.
- Los **mensajes personalizados** (**Enviar mensaje de red**) permiten
  señalar un evento por su nombre con un pequeño dato adjunto — una pulsación
  de timbre, una respuesta elegida, un indicador de «listo».

---

## Las acciones (categoría **Red**)

| Acción | Qué hace |
|--------|----------|
| **Alojar una partida** | Convertirse en anfitrión. Opcionalmente muestra una sala de espera con un botón Empezar. |
| **Unirse a una partida** | Conectarse a un anfitrión por dirección (o `"auto"` para la pantalla de conexión integrada). |
| **Salir de la partida** | Desconectarse (o dejar de ser anfitrión) y borrar las globales de red. |
| **Empezar la partida en red** | Solo anfitrión: terminar la sala de espera y decir a todos que empiecen. |
| **Definir variable compartida** | Escribir una variable que todas las máquinas pueden leer como `global.<nombre>`. |
| **Leer variable compartida** | Copiar una variable compartida en una global (para usarla en un cálculo). |
| **Enviar mensaje de red** | Difundir un mensaje personalizado con nombre y datos. |
| **Crear objeto en red** | Solo anfitrión: crear una instancia que aparece en todos los clientes. |
| **Sincronizar esta instancia** | Marcar la instancia actuante como replicada entre máquinas. |
| **Definir el dueño de la instancia** | Dar a un jugador concreto el control local de una instancia sincronizada. |
| **Si yo controlo esta instancia** | Condición: reserva la lógica de control para que solo se ejecute en la máquina propietaria. |
| **Asignar una tecla de red** | Asociar una tecla local a una entrada con nombre que el anfitrión puede leer. |
| **Si el jugador pulsa** | Condición (anfitrión): ¿mantiene un jugador dado una entrada con nombre? |
| **Ajustar la frecuencia de sincronización** | Ajustar la frecuencia de instantáneas del anfitrión y el retardo de interpolación de los clientes. |

Consulta la [Referencia completa de acciones](Full-Action-Reference-Network-Actions_es) para ver todos los parámetros.

---

## Los eventos (categoría **Red**)

Se disparan en cada instancia cuyo objeto los gestiona, en cada máquina
afectada:

| Evento | Se dispara cuando |
|--------|-------------------|
| **Network Ready** | Un cliente termina de conectarse al anfitrión (el anfitrión no lo dispara para sí mismo). |
| **Player Joined** | Se conecta un jugador nuevo. `global.network_sender` / `global.network_player_name` lo identifican. |
| **Player Left** | Un jugador se desconecta. |
| **Network Message** | Llega un **Enviar mensaje de red** — `global.network_event` / `global.network_data` / `global.network_sender`. |
| **Network Game Started** | El anfitrión llama a **Empezar la partida en red**. |
| **Connection Lost** | Se corta la conexión de un cliente con el anfitrión. El juego sigue — solo desaparecen los fantasmas de ese jugador. |

---

## Un ejemplo mínimo de sala compartida (Nivel A)

En un objeto controlador de sala invisible:

- **Create:** `Alojar una partida` si es la máquina del profesor, y si no
  `Unirse a una partida` con su IP (o `"auto"`).
- **Create:** `Definir variable compartida` `round = 1` (solo anfitrión, protegido por
  `global.is_host == 1`).
- En cualquier sitio: `draw_text` mostrando `global.round` — todos los
  jugadores ven el mismo valor.

## Un ejemplo mínimo de avatares compartidos (Nivel B)

En el evento Create del objeto jugador:

- `Sincronizar esta instancia` — esta instancia pasa a replicarse.
- En el **anfitrión**: `Crear objeto en red` crea una instancia de jugador por
  cada jugador que se conecta (en un manejador de **Player Joined**) y luego
  `Definir el dueño de la instancia` con el número de ese jugador.
- El código de movimiento protegido por `Si yo controlo esta instancia` se ejecuta solo
  en la máquina del jugador propietario; en todas las demás la instancia es un
  fantasma interpolado con suavidad.

---

## Notas y límites

- **TCP, solo LAN.** Sin atravesar NAT, sin juego por internet — ambas
  máquinas deben ser alcanzables en la misma red local (un wifi de aula o un
  laboratorio cableado). El wifi con aislamiento de clientes (habitual en las
  redes escolares gestionadas) bloquea por igual el descubrimiento y la
  conexión directa; un laboratorio cableado es la opción más fiable.
- **Puertos 45782 (TCP)** y **45783 (UDP, descubrimiento)** — consulta al
  departamento de informática de tu centro antes de usarlo en una red
  gestionada, y espera un aviso del cortafuegos la primera vez que alojes.
- Un cliente de navegador (exportación HTML5) se conecta un puerto por encima
  del del anfitrión, p. ej. `45783` si el anfitrión usa el predeterminado —
  esto ocurre automáticamente.
- La pérdida del anfitrión es suave: el juego propio de un cliente continúa;
  solo desaparecen los fantasmas de los demás jugadores y se dispara
  **Connection Lost** para que puedas mostrar un mensaje.
- Si la extensión LAN Multiplayer está **desactivada**, estas acciones y
  eventos simplemente no hacen nada — véase [Extensiones](Extensions_es).

---

## Véase también

- [File Exchange Multiplayer](FileExchange) (en inglés) — el hermano por
  turnos, para un aula donde un cortafuegos bloquea las conexiones directas de
  esta extensión
- [Extensiones](Extensions_es) — cómo se incluye LAN Multiplayer y cómo desactivarla
- [Referencia completa de acciones](Full-Action-Reference-Network-Actions_es) — cada acción y parámetro
- [Referencia de eventos](Event-Reference_es)
