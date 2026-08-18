# 2.5 D — Nivel 3

El tercer nivel en primera persona al estilo Doom/Wolfenstein,
construido sobre el mismo **motor raycast 2,5D** que
[`raycast_1`](../raycast_1/README.md) y
[`raycast_2`](../raycast_2/README.md) — completo en los tres destinos
de exportación (escritorio, HTML5, nativo/Kivy): muros texturizados,
un cielo que se desplaza, lanzamiento de suelo texturizado de baja
resolución, y sprites billboard orientados a la cámara.

Donde `raycast_1` enseña *la vista en primera persona en sí* y
`raycast_2` añade *cosas pasando en la vista* (gemas, un enemigo en
patrulla, una salida bloqueada), `raycast_3` trata sobre **estado que
puedes ver mientras juegas**: los monstruos cuestan **salud** en
lugar de una vida directamente, los botiquines la devuelven, y una
**pantalla de información** compuesta sobre la vista 3D muestra
siempre puntuación, vidas y una barra de salud.

Ese HUD es la razón por la que existe esta muestra. Hasta el
20/07/2026 el motor dibujaba la vista en primera persona y luego se
detenía, así que la puntuación y vidas de un juego raycast solo
aparecían en el título de la ventana de escritorio — invisibles en
las exportaciones HTML5 y Kivy. Ver
[`docs/RAYCAST_HUD_PLAN.md`](../../docs/RAYCAST_HUD_PLAN.md) para ese
trabajo y [`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md)
para el motor.

Un juego completo de dos niveles: cruza cada laberinto en primera
persona, recolecta cada gema mientras sobrevives a los monstruos, y
alcanza la salida bloqueada por gemas — la primera sala (ladrillo
cálido) lleva a una segunda sala (caverna de cristal fría), y
completarla gana. Disponible desde la pestaña Welcome del IDE
(*"2.5 D — Level 3"*).

**Sonido y música:** ninguno — no se incluyen archivos de sonido con esta muestra.

## Cómo se juega

- **Arriba/Abajo** — mueven adelante/atrás en la dirección hacia la
  que se esté mirando (continuo, no ajustado a la cuadrícula; los muros bloquean).
- **Izquierda/Derecha** — giran en el sitio (rotan `facing_angle`,
  independiente del movimiento — puedes girar mientras estás parado).
- **Recolecta las gemas** — cada una añade 10 a la puntuación,
  mostrada arriba a la izquierda.
- **Evita los monstruos** — tocar uno cuesta **25 de salud**, no una
  vida. Tras un golpe tienes una breve ventana de invulnerabilidad
  (45 pasos) así un monstruo que te atraviesa no puede vaciar toda la
  barra de una vez.
- **Toma los botiquines** — las cajas con cruz roja restauran **40 de
  salud**, con tope al máximo.
- **Si se agota la salud** pierdes una vida, la barra se rellena y la
  sala reinicia. Si se agotan las **vidas**, el juego reinicia.
- **Objetivo** — recolecta *todas* las gemas de una sala, luego
  alcanza su salida. Alcanzarla pronto solo te pide recolectar el resto.

## El HUD

`obj_hud` lo dibuja, en **espacio de pantalla**, sobre el fotograma 3D terminado:

| Elemento | Esquina | Acción |
|---|---|---|
| Puntuación | arriba izquierda | `draw_score` |
| Vidas | arriba derecha | `draw_text` + `draw_lives` |
| Barra de salud | abajo izquierda | `draw_health_bar` |
| Minimapa | centro, **a petición** | `draw_minimap` |

Puntuación y salud están en esquinas **opuestas** a propósito: una
barra de salud es ancha y una cadena de puntuación crece mientras
juegas, así que apilarlas invitaría a una colisión.

### El minimapa

**Presiona `M` para mostrarlo u ocultarlo** — en Android, toca el
botón de mapa arriba a la izquierda. Está *apagado* por defecto y se
dibuja solo mientras está activado, por dos razones: un mapa completo
son ~250 comandos de línea cada fotograma, y cubrir permanentemente
parte de una vista en primera persona es exactamente el desorden que
un HUD debería evitar. Mientras está apagado no cuesta nada en absoluto.

`draw_minimap` dibuja un mapa **orientado al norte** de los muros de
la sala con un marcador que muestra dónde estás y hacia dónde miras.
No rota — el mapa permanece fijo y el marcador gira, lo que es más
fácil de leer que un mapa que gira.

No necesita datos propios: lee los mismos bordes de muro que la vista
en primera persona ya derivó de las instancias sólidas de la sala,
así que permanece correcto si rediseñas el laberinto. Muestra
**solo muros** — no gemas ni monstruos — así el laberinto sigue
valiendo la pena explorar.

**No implementado (deliberado):** niebla de guerra, un modo
rotativo/orientado a la dirección, y mostrar objetos o enemigos. Ver
[`docs/RAYCAST_MINIMAP_PLAN.md`](../../docs/RAYCAST_MINIMAP_PLAN.md)
para el porqué de cada omisión.

**`obj_hud` es `visible: true`, y eso importa.** GameMaker no ejecuta
el evento draw de una instancia invisible — así que el HUD no puede
simplemente vivir en el controlador de cámara invisible
(`obj_cam0`/`obj_cam1`). Si construyes tu propio HUD y nada aparece,
comprueba primero esa bandera.

## Estructura del proyecto

| Archivo | Propósito |
|---|---|
| `project.json` | Manifiesto — ventana 640×480, ambas salas, copias de recursos incrustadas |
| `rooms/room0.json` | Laberinto de ladrillo cálido: 15×15 celdas / 480×480, 8 gemas, 3 monstruos, 3 botiquines |
| `rooms/room1.json` | Laberinto de caverna de cristal: la mitad más difícil — 10 gemas, 5 monstruos, solo 2 botiquines |
| `objects/obj_person.json` | Jugador/cámara — movimiento, daño de salud + alarma de invulnerabilidad, manejo de muerte |
| `objects/obj_hud.json` | La pantalla de información (ver arriba) |
| `objects/obj_cam0.json`, `obj_cam1.json` | Controladores de cámara por sala, cada uno llevando el tema de textura de esa sala |
| `objects/obj_gem.json` | Coleccionable, +10 de puntuación |
| `objects/obj_medkit.json` | Restaura 40 de salud |
| `objects/obj_monster.json` | Enemigo billboard en patrulla |
| `objects/obj_goal.json`, `obj_goal_final.json` | Salidas bloqueadas por gemas: avance, y victoria |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segmentos de muro finos (32×8 y 8×32) |
| `sprites/` | 13 sprites, reutilizados de `raycast_2` más `spr_medkit` |

## El laberinto se genera, no se coloca a mano

`tools/gen_raycast_3_maze.py` construye ambas salas con un laberinto
backtracker recursivo pasado por la colocación de muro fino en los
bordes de `raycast_1` — particiones de 8px centradas en los límites
de celda, no bloques de 32px que llenan una celda. Volver a
ejecutarlo reproduce exactamente las salas distribuidas, y una prueba
verifica que no se hayan desviado, así el diseño de nivel permanece
revisable y ajustable en lugar de ser datos opacos. (El laberinto de
`raycast_2` provino de un script desechable nunca confirmado, así que
sus salas no pueden regenerarse — este lo corrige.)

Las semillas son **elegidas, no arbitrarias**: `check_start()`
verifica que la celda inicial se abra hacia el este (el jugador
aparece allí mirando al este, así que un inicio amurallado
significaría empezar el juego con la nariz contra un muro) y que cada
celda sea alcanzable.

## Cosas para modificar

- **Daño y curación:** `-25` en el evento
  `collision_with_obj_monster` de `obj_person`, `+40` en el evento
  `destroy` de `obj_medkit`.
- **Ventana de invulnerabilidad:** los `45` pasos en `alarm_0`. Más
  corta hace el juego más duro; quitarla y un monstruo que se
  superponga contigo repetidamente destrozará la barra.
- **Balance de dificultad:** los `counts` por sala en el generador —
  monstruos contra botiquines es el control principal.
- **Disposición del HUD:** las coordenadas en el evento draw de
  `obj_hud`. Mantén puntuación y salud en esquinas opuestas.
- **Minimapa:** `size` en `draw_minimap` escala toda la sala en ese
  cuadrado, así que un valor mayor solo significa un mapa más
  legible; `wall_color` y `player_color` fijan su aspecto. El
  interruptor vive en el evento `keyboard_press` → `m` de `obj_hud`;
  usa `test_variable` + `exit_event` en lugar de dos condicionales
  desnudos, porque la versión ingenua fija la bandera a 1 y luego la
  lee inmediatamente como 1 y la devuelve inmediatamente a 0.
- **Temas:** los parámetros de textura en `obj_cam0`/`obj_cam1`.

## Una nota sobre el momento de las colisiones

El tiempo de ejecución dispara un evento de colisión cuando dos
instancias **empiezan** a superponerse, no cada fotograma en que
permanecen superpuestas. Estar dentro de un monstruo por lo tanto
cuesta un golpe, no un golpe por fotograma. La alarma de
invulnerabilidad se gana su lugar de todos modos: cubre el toque/
destoque repetido de un monstruo que patrulla *a través* de ti, que
es el caso que realmente encuentras jugando.

## Estado de la exportación

Corre en los tres destinos. Cubierto por la suite smoke sin interfaz
gráfica (`tools/smoke_run_samples.py`) y por
`tests/test_raycast_3_sample.py`, que conduce el bucle de juego real:
daño, la apertura y cierre de la ventana de invulnerabilidad, la
muerte costando exactamente una vida, la curación del botiquín y su
tope, la salida bloqueada por gemas, la transición de sala al tema de
hielo, y el renderizado del HUD sobre la vista en primera persona en
**ambas** salas.

Las exportaciones Kivy y HTML5 se verificaron para llevar todo el
bucle — `no_more_health`, `alarm_0`, `draw_health_bar`, `obj_hud` y
`spr_medkit` sobreviven todos a la generación de código — pero la
prueba de juego **visual** por destino vale la pena hacerla con los
propios ojos antes de un lanzamiento.
