# Laberinto — Nivel 3

Una exploración de mazmorra en cinco laberintos precedida por una
pantalla de título — el más grande de las tres muestras de laberinto
(17 objetos / 6 salas, contra los 9 objetos / 3 salas de maze_2).
Mantiene el ciclo de recoger-diamantes-luego-alcanzar-el-objetivo de
maze_2 y la puerta cerrada con llave bloqueada por diamantes, y añade
tres mecánicas nuevas que aparecen progresivamente a través de las
salas: un rompecabezas de empujar bloques a agujeros (room5), tres
arquetipos de monstruos en patrulla que matan al contacto (salas
3–5), y una trampa de bomba oculta que detona un radio de explosión
(room4). A diferencia de `maze_1`/`maze_2`, esta muestra **es** una
importación en bruto de GameMaker 8.x — su hermana `samples/maze_3.gmk`
está incluida en el repositorio (no existe un archivo `.gmk` para
`maze_1`/`maze_2`), y el proyecto pygm2 junto a él es el resultado convertido.

**Dónde encaja:** parte de la familia `maze_*` — GameObjects + sprites
más una **imagen de fondo** estática por sala (como `maze_2`), sin
teselas a nivel de sala. Ver
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para cómo esto se compara con `plateforme_*` (añade fondos en teselas)
y `match3_*` (script puro, sin acciones integradas).

**Sonido y música:** 8 archivos de sonido, y — a diferencia del
conjunto incluido pero silencioso de `maze_2` — realmente conectados:
11 puntos de llamada `play_sound`/`play_music` en
`sound_background` (música), `sound_diamond`, `sound_door`,
`sound_goal`, `sound_dead`, `sound_explode`, `sound_hole`, y `sound_push`.

## Cómo se juega

- **Pantalla de título (`room_start`):** presiona **ESPACIO** para empezar.
- Las **teclas de flecha** mueven al jugador una celda de cuadrícula
  de 32px a la vez (`test_alignment`/`snap_to_grid`, mismo patrón que `maze_1`/`maze_2`).
- **Objetivo:** recolectar diamantes (`obj_diamond`, +5 de puntuación
  cada uno) y alcanzar el `obj_goal` de cada sala. Las salas 2–4
  además bloquean la salida detrás de una `obj_door` cerrada con
  llave que se autodestruye solo cuando cada diamante de esa sala ha
  desaparecido (room3 tiene 4 puertas que se abren todas juntas).
  Room5 sustituye los diamantes por un rompecabezas de empujar
  bloques: camina contra un `obj_block` para deslizarlo una celda, o
  empújalo a un `obj_hole` para llenar el pozo (ambos se destruyen).
- **Peligros:** tres arquetipos de monstruos patrullan las salas 3–5
  y matan al contacto — `monster_all` rebota en los muros en
  cualquiera de las 4 direcciones, `monster_lr`/`monster_ud`
  patrullan un solo eje e invierten al chocar con un muro. Room4
  también oculta una placa `obj trigger` que, al tocarla, arma una
  `obj_bomb` cercana convirtiéndola en `obj_explosion` — su explosión
  de 16 fotogramas destruye cualquier instancia no sólida (incluyendo
  al jugador) dentro de un radio de 64px.
- **Condición de derrota:** tocar un monstruo cuesta una vida
  (`sound_dead` + `set_lives -1` + `restart_room`); llegar a 0 vidas
  muestra la pantalla de ingreso de puntuación máxima y reinicia el
  juego. Tocar el objetivo de la última sala muestra en cambio un
  mensaje de felicitación, otorga +100, y termina la partida de la misma forma.
- **Teclas de depuración** viven en `controller_main`: **R** cuesta
  instantáneamente una vida y reinicia la sala; **N**/**P** saltan
  directamente a la siguiente/anterior sala — útiles para pruebas,
  pero también un salto de nivel con el que un jugador podría
  tropezar por accidente.

## Estructura del proyecto

| Archivo | Propósito |
|---|---|
| `project.json` | Manifiesto del proyecto — configuración de ventana/sala y copias de recursos incrustadas. Las copias de objetos coinciden exactamente con sus archivos colaterales, pero **las copias de salas están obsoletas**: cada entrada de sala incrustada tiene 0 instancias y un marcador `_external_file` — los datos reales de instancias viven solo en `rooms/*.json` |
| `rooms/room_start.json` | Pantalla de título — 1 instancia (`controller_start`) |
| `rooms/room1.json` | Laberinto 1 — 134 instancias (muros, 4 diamantes, objetivo, jugador, controlador) |
| `rooms/room2.json` | Laberinto 2 — 96 instancias (+20 diamantes, 1 puerta cerrada con llave) |
| `rooms/room3.json` | Laberinto 3 — 105 instancias (+16 diamantes, 4 puertas cerradas con llave, los 3 arquetipos de monstruos, 6 monstruos en total) |
| `rooms/room4.json` | Laberinto 4 — 95 instancias (+14 diamantes, 1 puerta, 4 `monster_lr`, 2 pares trampa/bomba) |
| `rooms/room5.json` | Laberinto 5 — 99 instancias (4 bloques empujables, 3 agujeros, 2 objetivos, 2 `monster_lr` — sin diamantes ni puerta) |
| `objects/*.json` | 17 definiciones de objetos — verificadas contra las copias incrustadas de `project.json` e idénticas (sin obsolescencia). Nota: `objects/obj trigger.json` tiene un espacio literal en el nombre del archivo |
| `sprites/` | 16 sprites + metadatos (ver Recursos) |
| `sounds/` | 8 archivos de sonido, todos referenciados por al menos un objeto |
| `backgrounds/` | 2 fondos (`background_start.png` para la sala de título, `background_main.png` para los laberintos) |
| `CREDITS.txt` | Aviso de licencia de recursos para esta muestra |

## Objetos

**Jugador y controladores**

| Objeto | Rol | Eventos clave |
|---|---|---|
| `obj_person` | Personaje controlado por el jugador; movimiento en cuadrícula | keyboard (up/down/left/right/nokey), collision_with_obj_block, collision_with_monster_all/_lr/_ud, collision_with_wall_corner |
| `controller_start` | Controlador de pantalla de título; fija puntuación/vidas, inicia la música | create, keyboard (ESPACIO) |
| `controller_main` | HUD en el laberinto + teclas de depuración; dibuja puntuación/vidas, termina la partida a 0 vidas | keyboard (R trampa-reinicio), no_more_lives, draw, keyboard_press (N/P salto de sala) |

**Muros y teselas**

| Objeto | Rol | Eventos clave |
|---|---|---|
| `wall_corner` | Muro sólido base; padre de los otros dos tipos de muro | (ninguno — colisionador pasivo) |
| `wall_horizontal` | Segmento de muro horizontal (hereda `wall_corner`) | (ninguno) |
| `wall_vertical` | Segmento de muro vertical (hereda `wall_corner`) | (ninguno) |

**Coleccionables, puertas, objetivos y rompecabezas de empujar bloques (room5)**

| Objeto | Rol | Eventos clave |
|---|---|---|
| `obj_diamond` | Coleccionable; +5 de puntuación al recogerlo | destroy, collision_with_obj_person |
| `obj_door` | Puerta cerrada con llave; se autodestruye cuando cada diamante de la sala ha desaparecido | step |
| `obj_goal` | Salida del nivel; avanza las salas o termina el juego en la última sala | collision_with_obj_person |
| `obj_block` | Caja empujable; se desliza una celda cuando se camina contra ella, o cae en un agujero | collision_with_obj_person |
| `obj_hole` | Pozo; se autodestruye junto con cualquier bloque empujado dentro | collision_with_obj_block |

**Monstruos y trampa de bomba (room4)**

| Objeto | Rol | Eventos clave |
|---|---|---|
| `monster_all` | Rebota en los muros en cualquiera de las 4 direcciones | create, collision_with_wall_corner |
| `monster_lr` | Patrulla izquierda-derecha, invierte al contacto con un muro | create, collision_with_wall_corner |
| `monster_ud` | Patrulla arriba-abajo, invierte al contacto con un muro | create, collision_with_wall_corner |
| `obj trigger` | Placa oculta; al tocarla reproduce el sonido de explosión, transforma la `obj_bomb` emparejada en `obj_explosion`, se autodestruye | collision_with_obj_person |
| `obj_bomb` | Marcador de posición inerte que representa una bomba armada hasta que un disparador se active | (ninguno) |
| `obj_explosion` | Explosión de 16 fotogramas; al aparecer destruye instancias no sólidas dentro de 64px, se autodestruye al final de la animación | create, animation_end |

## Recursos

16 sprites (mayormente 32×32 de un solo fotograma, precisos a nivel
de píxel; `sprite_explosion` es una tira de 1536×96 de 16 fotogramas
sin bandera precisa), 2 fondos, 8 sonidos — los 8 sonidos están
referenciados por al menos un objeto, a diferencia de `maze_2` donde
ninguno estaba conectado. La licencia/procedencia de los recursos de
esta muestra está **sin documentar** — ver `CREDITS.txt` en esta
carpeta, que remite al TODO "Remaining maze assets" en
`docs/ASSET_LICENSES.md`. No asumas CC0 ni ninguna otra licencia para
estos archivos.

## Cosas para modificar

- `sprite_lives` (16×16) es un recurso registrado que nunca se dibuja
  — la acción `draw_lives` de `controller_main` en realidad usa
  `sprite_person` a escala 0,7, dejando `sprite_lives` huérfano
  (misma categoría que el `tiles.json` de `maze_2`).
- La explosión de la trampa de bomba (el evento `create` de
  `obj_explosion`) destruye al jugador mediante un simple
  `destroy_instance` en su comprobación de radio, evitando la ruta
  `sound_dead`/`set_lives`/`restart_room` que usan los monstruos —
  atrapar al jugador deja la partida en un estado extraño en lugar de
  una muerte/reinicio limpio.
- La velocidad de los monstruos está codificada como `32/6` px/paso
  en los tres arquetipos mientras el jugador se mueve a `4` — los
  monstruos no están ajustados a la cuadrícula como lo está el
  jugador, así que su movimiento no permanece alineado a las celdas con el tiempo.
- Las teclas de depuración `R`/`N`/`P` en `controller_main` están
  activas en el controlador distribuido (ver Cómo se juega) — valdría
  la pena condicionarlas tras una bandera de depuración si esta
  muestra se pule más adelante.

## Estado de la exportación

Cubierto por la suite de smoke-tests sin interfaz gráfica
(`tools/smoke_run_samples.py`, que lista `maze_3` y lo ejecuta durante
un número fijo de fotogramas con entrada de teclado inyectada); no
verificado individualmente por cada destino de exportación (Kivy/Web).
Expuesto en la pestaña Welcome del IDE como "Maze — Level 3"
(`widgets/welcome_tab.py`).
