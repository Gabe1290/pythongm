# 2.5 D — Nivel 1

Una vista en primera persona al estilo Doom/Wolfenstein del **mismo
trazado de laberinto que `maze_1`** — mismas salas, mismo objetivo,
mismos caminos resolubles. Donde `maze_1` muestra el laberinto desde
arriba con bloques de muro de celda completa, esta muestra lo
renderiza como una proyección raycast con **muros finos en los
bordes** (particiones de 8px asentadas en los límites de celda, no
bloques de 32px que llenan una celda) — pasillos genuinamente
proporcionados al estilo Wolfenstein, no solo una cámara en primera
persona atornillada al antiguo trazado en bloques. `rooms/room0.json`
y `room1.json` se regeneraron desde el trazado original de `maze_1`
mediante una conversión que preserva la topología (misma
conectividad/resolubilidad, geometría de muros diferente), no
rediseñados a mano. Ver
[`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) en la
raíz del repositorio para el plan de ingeniería completo, incluyendo
la sección "Complete rethink" sobre por qué los muros de celda
completa no funcionaban para un espacio de giro real.

**Esto es 2,5D, no 3D** — la lógica de juego es completamente
inalterada respecto a `maze_1` (misma posición 2D `x`/`y`, misma
colisión de muro sólido); solo la *imagen* está falseada para parecer
tridimensional. No hay mirada vertical (sin inclinación), los
pasillos deben estar alineados a la cuadrícula, y no hay verdadera
superposición sala-sobre-sala. Esta es una limitación deliberada y
honesta, no una funcionalidad faltante — ver la nota pedagógica "why
raycasting" del documento del plan.

**Estado — completamente texturizado (muros, cielo, suelo, billboards)
en los tres destinos: escritorio (pygame), HTML5, y nativo (Kivy).**
Los muros muestrean una **textura de ladrillo** (`spr_wall_texture`,
vía `wall_texture`): cada columna de pantalla muestrea una tira
vertical en la posición de impacto del rayo, escalada por distancia,
con la cara del muro orientada lejos a la mitad del brillo como
indicio de profundidad gratuito. El techo es un **cielo al estilo
DOOM** (`spr_sky`, vía `sky_texture`) — un panorama que se desplaza
horizontalmente al girar (un giro completo de 360° lo desplaza una
vez) y que *no* retrocede con la distancia, así que se lee como un
horizonte infinitamente lejano. El suelo es una **textura de piedra
proyectada** (`spr_floor`, vía `floor_texture`) — un lanzamiento de
suelo de baja resolución (el cálculo por píxel a resolución completa
era ~13× demasiado lento en Python puro; `floor_cast_res` fija el
submuestreo, 4 ≈ 5ms) que se repite por celda de cuadrícula y se
encuentra con las bases de los muros sin costuras. `obj_goal` se
renderiza como un sprite billboard orientado a la cámara (escalado
por distancia, oculto por muros) — ver "Qué hay de nuevo aquí". Para
volver al aspecto plano, vacía
`wall_texture`/`sky_texture`/`floor_texture` en la acción `enable_raycast_view`.

## Cómo se juega

- **Arriba/Abajo** mueven adelante/atrás en la dirección hacia la que
  se esté mirando (movimiento continuo, no ajustado a la cuadrícula —
  los muros aún bloquean vía la colisión normal de instancia sólida
  del motor, inalterada respecto a `maze_1`).
- **Izquierda/Derecha** giran en el sitio (rotan `facing_angle`,
  independiente del movimiento — puedes girar mientras estás parado).
- **Objetivo:** encontrar la meta. Tocarla avanza a la siguiente sala
  si existe una (misma lógica `obj_goal` que `maze_1`, archivo idéntico byte a byte).

## Qué hay de nuevo aquí, en el motor

- `GameInstance.facing_angle` — dirección de mirada persistente
  (convención de ángulo GM: 0=derecha, 90=arriba, 180=izquierda,
  270=abajo), fijada vía la nueva acción `set_facing_angle`. A
  diferencia de la propiedad `direction` existente (derivada de
  `hspeed`/`vspeed`, siempre 0 al estar parado), esta sobrevive al
  estar parado — requerida para controles FPS de "girar en el sitio".
- `enable_raycast_view` — cambia la sala actual a la cámara raycast
  (vinculada a la instancia que llama, aquí el evento `create` de
  `obj_person`) o vuelve al renderizado normal desde arriba.
- El mapa de muros está **derivado de las instancias sólidas
  existentes de esta sala**, no de un formato de creación separado —
  pero desde la reelaboración de muros finos, se deriva como bordes
  reales (`GameRoom._build_raycast_walls`), no como ocupación
  gruesa por celda: la relación de aspecto del sprite de una
  instancia sólida decide si es un segmento de muro horizontal o
  vertical (aproximadamente cuadrado recae en bloquear una celda
  entera, para retrocompatibilidad con contenido sin muros finos).
  Esto es lo que hace que el grosor de 8px de
  `obj_wall_h`/`obj_wall_v` realmente importe tanto para el
  renderizado como para el espacio de giro, no solo visualmente —
  ver la sección "Complete rethink" del documento del plan.
- **Sprites billboard.** Cualquier instancia visible, no sólida, con
  un sprite (aquí, `obj_goal`) se dibuja como un sprite 2D orientado
  a la cámara en la vista raycast, escalado por distancia y
  centrado verticalmente en el horizonte como una tira de muro. La
  oclusión es recorte real por columna contra las distancias de
  muro ya calculadas para el paso de muros de ese fotograma, así que
  una meta detrás de un muro está correctamente oculta en lugar de
  transparentarse. Este es un primer corte de la Fase 6 del
  documento del plan (los muros solo dibujan instancias sólidas; los
  billboards solo dibujan las no sólidas, así que nada se dibuja dos
  veces) — sin mezcla de transparencia parcial, sin rotación para
  coincidir con la orientación propia del sprite, solo el escalado y
  recorte plano que un motor al estilo Wolfenstein usaba para
  objetos y enemigos.

## Estructura del proyecto

| Archivo | Propósito |
|---|---|
| `project.json` | Manifiesto del proyecto |
| `rooms/room0.json`, `rooms/room1.json` | Misma *topología* de laberinto que `maze_1`, regenerada con muros finos en los bordes (ver el algoritmo de conversión del documento del plan) |
| `objects/obj_person.json` | Jugador/cámara — `create` activa la vista raycast, los eventos `keyboard` manejan girar + adelante/atrás, registra `collision_with_obj_wall_h`/`_v` |
| `objects/obj_goal.json` | Objeto objetivo — idéntico byte a byte al de `maze_1` |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segmentos de muro finos (32×8 y 8×32) — reemplazan el único `obj_wall` de bloque completo de `maze_1` |
| `sprites/` | `spr_person`, `spr_goal` (de `maze_1`) más los propios `spr_wall_h`/`spr_wall_v` de esta muestra (marcadores de posición finos de color sólido — nunca renderizados en modo primera persona, solo importan sus dimensiones para colisión/raycasting) |

## Cosas para modificar

- La tasa de giro es `3`°/fotograma (`room_speed: 30` → 90°/seg) y la
  velocidad de movimiento es `3` px/fotograma, ambos codificados en
  los eventos `keyboard` de `obj_person`.
- FOV `66`°, `render_distance` `20` celdas, `cell_size` `32` — todos
  parámetros de `enable_raycast_view` en el evento `create` de `obj_person`.
- Los colores de muro/suelo/techo también son parámetros de
  `enable_raycast_view` — el respaldo plano cuando la textura
  correspondiente está vacía.
- El grosor del muro es `8`px, codificado en la conversión que generó
  `rooms/*.json` (no un parámetro en tiempo de ejecución) — regenera
  las salas para cambiarlo.
- `spr_person` es **16×16** con una caja de colisión
  `(4,4)-(12,12)` — el jugador se redujo a la mitad respecto al
  antiguo 32×32 (y se recentró en su celda inicial, así que la
  cámara aún se sienta en el centro de la celda) porque el jugador a
  tamaño completo hacía que los pasillos de 1 celda se sintieran
  agobiantes; una huella más pequeña da mucho más espacio para
  moverse. La **textura de ladrillo** del muro también se hizo más
  fina de manera similar (ladrillos a media escala) así los muros se
  leen como más distantes — ambos ajustes intercambian "pegado a la
  cara" por una sensación de espacio más amplia.

## Estado de la exportación

La vista en primera persona **completa** ahora se renderiza en **los
tres destinos** — escritorio (pygame), **HTML5**
(`export/HTML5/templates/engine.js`), y **nativo/Kivy**
(`export/Kivy/kivy_exporter.py`) — con controles de mirada por
ángulo de orientación, muros texturizados y planos, el cielo que se
desplaza, el lanzamiento de suelo texturizado de baja resolución, y
sprites billboard con recorte de oclusión. Los tres renderizadores no
comparten código (tres copias escritas a mano), así que su núcleo DDA
está enlazado mediante `tests/test_raycast_export_parity.py`
(igualdad numérica exacta escritorio↔Kivy sobre una matriz de 260
rayos; paridad estructural HTML5, ya que no hay motor JS en CI).

El lanzamiento de suelo usa el mismo enfoque calcular-en-baja-
resolución-luego-escalar en cada destino (`floor_cast_res`,
predeterminado 4); las mediciones de tiempo en hardware real
confirmaron que cabe en el presupuesto (navegador ~0,4 ms a res=2;
Kivy/AMD 840M ~5 ms a res=4). Un proyecto aún puede vaciar
`floor_texture` para un suelo plano de `floor_color`.

Disponible desde la pestaña Welcome del IDE — elige **"2.5 D —
Level 1"** del menú desplegable *Choose a sample* (abrir una muestra
la copia a tus Documentos, así el original incluido permanece intacto).
