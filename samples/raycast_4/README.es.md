# Raycast — Nivel 4

El cuarto nivel en primera persona al estilo Doom/Wolfenstein, y el
primero construido **alrededor de una barra de estado permanente
abajo** — la estética DOOM en lugar de las superposiciones de esquina
de `raycast_3`. La vista 3D es deliberadamente **más corta**
(letterbox) para dejar espacio a la barra; eso es parte del aspecto, no un error.

Donde `raycast_3` demostró un HUD de esquina y la salud como recurso,
`raycast_4` muestra las dos funcionalidades del motor construidas
para una barra DOOM:

- **`viewport_height`** en `enable_raycast_view` reduce la vista en
  primera persona a la parte superior de la ventana y reserva la
  franja debajo.
- **`draw_doom_hud`** llena esa franja: una barra de salud + número,
  un **retrato de rostro reactivo a la salud**, puntuación, vidas, y
  un contador de llaves — todo desde comandos de dibujo ordinarios,
  así se renderiza igual en escritorio, HTML5 y nativo (Kivy).

Ver [`docs/RAYCAST_DOOM_HUD_PLAN.md`](../../docs/RAYCAST_DOOM_HUD_PLAN.md)
para la ingeniería, y [`raycast_3`](../raycast_3/README.md) para la
alternativa de HUD de esquina que este nivel deliberadamente no readapta.

**Sensación de interior.** Dos cosas hacen que esto se lea como un
pasillo dentro de un edificio en lugar de un laberinto al aire libre:
proyecta un **techo de piedra** (`spr_ceiling`) en lugar del cielo
que se desplaza que usan las otras muestras raycast — fijado vía
`ceiling_texture` con `sky_texture` dejado vacío — y los muros se
renderizan **más altos**. Esa altura de muro
(`RAYCAST_WALL_HEIGHT`, 1,5× un cubo) es un valor predeterminado
global del motor, así que todo juego raycast obtiene los muros más
altos; el techo es la elección propia de esta muestra.

**Sonido y música:** ninguno — no se incluyen archivos de sonido con esta muestra.

## Cómo se juega

- **Arriba/Abajo** — mueven adelante/atrás en la dirección hacia la que se esté mirando.
- **Izquierda/Derecha** — giran en el sitio.
- **Recolecta las llaves** — cada una anota 25 puntos y avanza en uno
  el contador **KEYS** en la barra. Hay tres.
- **Evita los monstruos** — tocar uno cuesta **25 de salud** (con una
  breve ventana de invulnerabilidad después). Observa el **rostro**:
  hace una mueca mientras tu salud baja, incluso antes de que hayas
  leído el número.
- **Si se agota la salud** → pierdes una vida, la salud se rellena,
  la sala reinicia. **Si se agotan las vidas** → el juego reinicia.
- **Alcanza la salida** una vez que hayas encontrado **las tres
  llaves**. Tocarla pronto solo te dice que la puerta está cerrada con llave.
- **Presiona `M`** para mostrar un **minimapa** de los muros (apagado
  por defecto). Se dibuja dentro de la vista 3D, sobre la barra de
  estado, y se activa/desactiva — el mismo mapa a petición que usa
  `raycast_3`, aquí mantenido lejos de la barra.

## La barra de estado (`draw_doom_hud`)

`obj_person` la dibuja cada fotograma, en espacio de pantalla, sobre
la vista 3D terminada. De izquierda a derecha:

| Zona | Muestra |
|---|---|
| Izquierda | etiqueta `HEALTH` + una barra de salud proporcional + el número |
| Centro | el **retrato de rostro**, una tira de 4 fotogramas que reacciona a la salud |
| Derecha | `SCORE` sobre `LIVES` |
| Extremo derecho | el contador `KEYS` |

El rostro es el propósito de toda la muestra. Su fotograma se elige
mediante un mapa de segmentos uniformes sobre la salud — fotograma 0
(calmado) cerca de lleno, el último fotograma (muriendo) cerca de
vacío — así el retrato te dice cómo te va antes de que lo haga el
número, exactamente como la barra propia de DOOM.

**`obj_person` es tanto la cámara *como* el dibujante del HUD.** Eso
es deliberado: el contador de llaves entonces es solo una variable de
instancia en `obj_person` (`keys`), así la expresión de objetivo de
`draw_doom_hud` lee el mismo valor idénticamente en los tres destinos
de exportación. Un objeto de cámara invisible separado (como en
`raycast_3`) no podría llevar una variable que el HUD visible necesita.

## El letterbox (`viewport_height`)

`enable_raycast_view` corre en el `create` de `obj_person` con
`viewport_height: 400` en una ventana 640×480 — así la vista 3D es de
400px de alto y los **80px** inferiores están reservados, rellenados
de negro por el motor, y pintados encima por la barra. Fija
`viewport_height` a `0` (el predeterminado) y la vista llena toda la
ventana sin franja reservada, exactamente como hacen `raycast_1`–`3`.

El horizonte se mueve hacia arriba con la vista más corta, y
muros/cielo/suelo escalan todos según él — es un verdadero letterbox,
no una barra puesta sobre una vista a altura completa. (En Kivy, que
es y-arriba, la franja reservada está de todos modos abajo en la
ventana; el motor maneja la inversión.)

## Estructura del proyecto

| Archivo | Propósito |
|---|---|
| `project.json` | Manifiesto — ventana 640×480, una sala |
| `rooms/room0.json` | El laberinto: 15×15 celdas, 3 llaves, 4 monstruos, una salida bloqueada por llaves |
| `objects/obj_person.json` | Jugador + cámara + barra de estado — movimiento, salud, llaves, `draw_doom_hud` |
| `objects/obj_key.json` | Una llave (pasiva; la colisión de `obj_person` la maneja) |
| `objects/obj_monster.json` | Enemigo billboard en patrulla |
| `objects/obj_goal.json` | Salida bloqueada por llaves (se abre cuando no queda ninguna `obj_key`) |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segmentos de muro finos |
| `sprites/` | Arte de muro/suelo/persona/monstruo reutilizado, un nuevo **`spr_ceiling`** (techo de piedra de interior, reemplazando el cielo), más nuevos `spr_face` (retrato de 4 fotogramas) y `spr_key` |

## El laberinto es generado

`tools/gen_raycast_4_maze.py` construye la sala **delegando al
generador confirmado de `raycast_3`** — mismo laberinto backtracker
recursivo, mismos muros finos en los bordes, misma disciplina de
semilla elegida (el spawn se abre al este, cada celda alcanzable).
Difiere solo en qué se dispersa (llaves, no gemas/botiquines) y en
que `obj_person` es la cámara. Volver a ejecutarlo reproduce la sala
distribuida; una prueba la fija.

## Cosas para modificar

- **Altura de barra vs. viewport:** la `height` en `draw_doom_hud`
  (80) debería coincidir con la franja reservada
  (`640×480 − viewport_height 400 = 80`). Cambia una, cambia la otra.
- **Reactividad del rostro:** `face_frames` (4) segmenta la salud
  sobre la tira. Una tira de 5 fotogramas con `face_frames: 5` da
  expresiones más finas.
- **Daño/llaves:** el `-25` en el evento
  `collision_with_obj_monster` de `obj_person`; las 3 llaves y 4
  monstruos en los `counts` del generador.
- **Colores y etiquetas de la barra:** los parámetros de
  `draw_doom_hud` en el evento draw de `obj_person`.

## Estado de la exportación

Corre en los tres destinos. Cubierto por la suite smoke sin interfaz
gráfica (`tools/smoke_run_samples.py`) y
`tests/test_raycast_4_sample.py`, que conduce el bucle real: la barra
renderiza todas sus partes sobre la vista reducida, alineada abajo a
la franja reservada; el **fotograma del rostro sigue la salud**
(100/75/50/25 → 0/1/2/3); una recogida de llave cuenta, puntúa y se destruye.

Las exportaciones Kivy y HTML5 se verificaron para llevar todo — el
`viewport_height` del letterbox en la configuración de cámara,
`draw_doom_hud`, el rostro multi-fotograma — pero la prueba de juego
**visual** por destino es el último paso y vale la pena hacerla con
los propios ojos: esta es la primera muestra raycast cuya *forma de
vista* cambia, así que la que más merece observarse renderizando en
un navegador y en Android.
