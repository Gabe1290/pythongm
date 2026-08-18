# 2.5 D — Nivel 2

Un segundo nivel en primera persona al estilo Doom/Wolfenstein,
construido sobre el mismo **motor raycast 2,5D** que
[`raycast_1`](../raycast_1/README.md) — que está completo en los tres
destinos de exportación (escritorio, HTML5, nativo/Kivy): muros
texturizados, un cielo que se desplaza, lanzamiento de suelo
texturizado de baja resolución, y sprites billboard orientados a la cámara.

Donde `raycast_1` es un pasillo pequeño derivado de maze_1 que enseña
*la vista en primera persona en sí*, `raycast_2` es un **laberinto
más grande con cosas pasando en la vista 3D** — gemas coleccionables,
un enemigo en patrulla, y una salida bloqueada por gemas. Ver
[`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) para el
motor y [`docs/RAYCAST_2_SAMPLE_PLAN.md`](../../docs/RAYCAST_2_SAMPLE_PLAN.md)
para el diseño y el plan de unidades de esta muestra.

Un juego completo de dos niveles: navega cada laberinto en primera
persona, recolecta cada gema esquivando monstruos en patrulla, y
alcanza la salida bloqueada por gemas — la primera sala (ladrillo
cálido) lleva a una segunda sala (caverna de cristal fría), y
completarla gana. Disponible desde la pestaña Welcome del IDE
(*"2.5 D — Level 2"*) y se exporta a los tres destinos (escritorio,
HTML5, nativo/Kivy).

## Cómo se juega

- **Arriba/Abajo** — mueven adelante/atrás en la dirección hacia la
  que se esté mirando (continuo, no ajustado a la cuadrícula; los
  muros bloquean vía la colisión normal de instancia sólida del motor).
- **Izquierda/Derecha** — giran en el sitio (rotan `facing_angle`,
  independiente del movimiento — puedes girar mientras estás parado).
- **Recolecta las gemas** dispersas por el laberinto — cada una añade
  10 a la puntuación, mostrada en el **HUD en pantalla** (arriba a la
  izquierda), dibujado sobre la vista en primera persona por `obj_hud`.
- **Evita los monstruos** — patrullan los pasillos (rebotando en los
  muros) y se dibujan como billboards orientados a la cámara. Tocar
  uno cuesta una vida y reinicia la sala; empiezas con 3 vidas,
  mostradas arriba a la derecha del HUD. Si se agotan, el juego reinicia.
- **Objetivo:** recolecta **todas** las gemas en una sala, luego
  alcanza su objetivo. Alcanzarlo demasiado pronto solo te pide
  *"Collect all the gems before you leave!"* — se abre solo cuando
  cada gema ha desaparecido. El objetivo de la primera sala (ladrillo
  cálido) lleva a una segunda sala fría de **caverna de cristal**;
  completarla gana el juego.

## Geometría del nivel

Tanto `rooms/room0.json` como `rooms/room1.json` son laberintos de
15×15 celdas (480×480) generados por un backtracker recursivo (un
laberinto *perfecto* — cada celda alcanzable, garantizadamente
resoluble — con algunos muros extra derribados para bucles y líneas
de visión más largas), luego convertidos al modelo de **muro fino en
los bordes** de `raycast_1`: cada frontera entre una celda abierta y
un muro se convierte en un segmento `obj_wall_h` (32×8) u `obj_wall_v`
(8×32) de 8px en la línea de la cuadrícula, así los pasillos se leen
como genuinamente proporcionados al estilo Wolfenstein en lugar de en
bloques. Cada sala usa una semilla de laberinto diferente, así que los
dos niveles son trazados distintos.

## Tematización por sala

Las texturas de la vista raycast son **por sala**: `enable_raycast_view`
vive en un pequeño objeto controlador de cámara invisible colocado en
cada sala — `obj_cam0` (ladrillo cálido:
`spr_wall_texture`/`spr_sky`/`spr_floor`) en room0, `obj_cam1`
(caverna de cristal fría:
`spr_wall_ice`/`spr_sky_ice`/`spr_floor_ice`, variantes teñidas de
azul) en room1. Cada controlador nombra a `obj_person` como cámara vía
el parámetro `camera_object` de la acción, así el *jugador* sigue
siendo la cámara aunque sea el *controlador* el que dispara la
acción. Esto es por lo que la segunda sala se ve diferente — la
configuración está limitada al controlador de la sala, no incrustada
en el jugador.

## Estructura del proyecto

| Archivo | Propósito |
|---|---|
| `project.json` | Manifiesto del proyecto |
| `rooms/room0.json`, `rooms/room1.json` | Los dos laberintos generados de muro fino en los bordes (datos de instancia autorizados) |
| `objects/obj_person.json` | Jugador/cámara — los eventos `keyboard` manejan girar + adelante/atrás; `game_start` inicializa puntuación/vidas; registra los manejadores `collision_with_obj_wall_h`/`_v` que controlan el bloqueo de muro, y `collision_with_obj_monster` (perder una vida + reinicio) |
| `objects/obj_cam0.json`, `obj_cam1.json` | Controladores de cámara por sala que activan `enable_raycast_view` con el tema de textura de esa sala |
| `objects/obj_gem.json` | Coleccionable — la colisión lo destruye; su evento `destroy` añade 10 a la puntuación |
| `objects/obj_monster.json` | Enemigo billboard en patrulla — se mueve, rebota en los muros |
| `objects/obj_goal.json`, `obj_goal_final.json` | El objetivo de room0 (→ siguiente sala) y de room1 (→ victoria); ambos bloqueados por gemas |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segmentos de muro finos (32×8 y 8×32) |
| `objects/obj_hud.json` | HUD en espacio de pantalla dibujado sobre la vista en primera persona — `draw_score` + `draw_lives`. Nota que es **visible: true**: GameMaker no ejecuta el evento draw de una instancia invisible, por eso el HUD no puede simplemente vivir en `obj_cam0`/`obj_cam1` (que son invisibles) |
| `sprites/` | Reutilizados de `raycast_1` (persona/objetivo/muro/cielo/suelo + marcadores de muro), más `spr_gem` (gema de match3), `spr_monster` (monstruo de maze_3), y el conjunto de texturas `*_ice` teñido de azul de room1 |

## Motor reutilizado, arte reutilizado

`raycast_2` comparte los objetos y sprites de `raycast_1` — el
propósito de esta muestra es *creación de nivel y jugabilidad sobre
el motor terminado*, no nuevo código de renderizado. El arte de gema
y monstruo (Unidades 2–3) son los únicos recursos nuevos, y ninguna
de la lógica de juego depende del arte específico, así que son reskineables.
