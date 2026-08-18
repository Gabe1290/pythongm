# Laberinto — Nivel 2

Un juego de laberinto en cuadrícula visto desde arriba con dos
laberintos jugables más una pantalla de título: recolecta caramelos
por puntuación, luego alcanza la salida para avanzar. Se construye
sobre el ciclo laberinto/objetivo de sala única de `maze_1` con una
pantalla de inicio, un coleccionable (caramelo con puntuación), y una
puerta cerrada con llave que solo se abre cuando los caramelos de la
sala han sido recogidos todos. Este es un proyecto pygm2 nativo (sin
archivo `.gmk` hermano — sus recursos se importaron originalmente
mediante una importación de GameMaker 8.x, según `CREDITS.txt`, pero
el proyecto en sí está escrito/guardado en el formato JSON propio de pygm2).

**Dónde encaja:** parte de la familia `maze_*` — GameObjects +
sprites, más (a diferencia de `maze_1`) una **imagen de fondo**
estática por sala (`background_main`), sin teselas a nivel de sala.
Ver
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para cómo esto se compara con `plateforme_*` (añade fondos en teselas)
y `match3_*` (script puro, sin acciones integradas).

**Sonido y música:** se incluyen 4 archivos de sonido
(`sound_background.ogg`, `sound_diamond`/`door`/`goal.wav`) pero
**ninguno está realmente conectado** — ningún objeto referencia
`play_sound`/`play_music` en ninguna parte, así que el juego es
silencioso en la práctica a pesar de llevar recursos de audio. (En
contraste con `maze_3`, donde el mismo conjunto de sonidos sí se reproduce.)

## Cómo se juega

- **Pantalla de título (`room_start`):** presiona **ESPACIO** para
  empezar (la acción `keyboard_press` de `controller_start` llama a `next_room`).
- Las **teclas de flecha** (arriba/abajo/izquierda/derecha) mueven al
  jugador una celda de cuadrícula (32px) a la vez; el movimiento está
  ajustado a la cuadrícula vía `test_alignment`/`snap_to_grid`
  (cuadrícula 32×32), mismo patrón que `maze_1`.
- **Objetivo:** recolectar los caramelos (`obj_diamond`, sprite
  `sprite_bonbon`) dispersos por cada laberinto — cada uno vale +10 de
  puntuación — luego alcanzar el objetivo (`obj_goal`). En `room2`, la
  salida está además bloqueada por una puerta cerrada con llave
  (`obj_door`) que se autodestruye solo cuando cada `obj_diamond` de
  la sala ha desaparecido.
- Tocar el objetivo avanza a la siguiente sala (+100 de puntuación) si
  existe una; tocarlo en la última sala (`room2`) otorga +100, abre la
  pantalla de ingreso de puntuación máxima, y termina el juego.
- **Sin condición de derrota:** ninguna acción que afecte
  vidas/salud aparece en ninguna parte de los objetos de esta muestra
  — `starting_lives: 3` está fijado en la configuración del proyecto
  pero nunca se muestra ni decrementa.

## Estructura del proyecto

| Archivo | Propósito |
|---|---|
| `project.json` | Manifiesto del proyecto — configuración de ventana/sala y copias incrustadas de todos los recursos |
| `rooms/room_start.json` | Pantalla de título — 1 instancia (`controller_start`) |
| `rooms/room1.json` | Primer laberinto — 134 instancias (muros, jugador, objetivo, 4 caramelos, `controller_main`) |
| `rooms/room2.json` | Segundo laberinto — 112 instancias (muros, jugador, objetivo, 21 caramelos, puerta cerrada con llave, `controller_main`) |
| `objects/*.json` | 9 definiciones de objetos — verificadas contra las copias incrustadas de `project.json` e idénticas en esta muestra (no se encontró obsolescencia) |
| `sprites/` | 7 sprites (`sprite_person`, `sprite_bonbon`, `sprite_door`, `sprite_goal`, `sprite_wall_corner`, `sprite_wall_horizontal`, `sprite_wall_vertical`) + metadatos; `tiles.json` es un archivo colateral huérfano (no registrado en `project.json`, falta el archivo de imagen — sin usar) |
| `backgrounds/` | `background_start.png` (pantalla de título), `background_tiles.png` (suelo del laberinto en teselas) |
| `sounds/` | 4 archivos de sonido (ver Recursos abajo) |
| `CREDITS.txt` | Aviso de licencia de recursos para esta muestra |

## Objetos

| Objeto | Rol | Eventos clave |
|---|---|---|
| `obj_person` | Personaje controlado por el jugador; movimiento en cuadrícula | keyboard (down, right, up, left, nokey), collision_with_wall_corner |
| `wall_corner` | Muro sólido base del laberinto; objeto padre para los otros dos tipos de muro | (ninguno — solo colisionador pasivo) |
| `wall_horizontal` | Segmento de muro horizontal sólido (hereda de `wall_corner`) | (ninguno — solo colisionador pasivo) |
| `wall_vertical` | Segmento de muro vertical sólido (hereda de `wall_corner`) | (ninguno — solo colisionador pasivo) |
| `obj_diamond` | Caramelo coleccionable; añade puntuación al recogerlo | destroy, collision_with_obj_person |
| `obj_door` | Puerta de salida cerrada con llave (solo room2); se abre cuando todos los caramelos han desaparecido | step |
| `obj_goal` | Salida del nivel; avanza a la siguiente sala o termina el juego | collision_with_obj_person |
| `controller_start` | Controlador de pantalla de título; espera a que el jugador empiece | create, keyboard_press (ESPACIO) |
| `controller_main` | Controlador HUD dentro del laberinto; dibuja la puntuación | draw |

## Recursos

7 sprites (32×32, un solo fotograma, colisión precisa a nivel de
píxel excepto `sprite_goal` que no tiene una bandera `precise`
explícita), 2 fondos, 4 sonidos (`sound_background.ogg`,
`sound_diamond.wav`, `sound_door.wav`, `sound_goal.wav`). La
licencia/procedencia de todos los recursos de esta muestra está **sin
documentar** — ver `CREDITS.txt` en esta carpeta, que remite al TODO
"Remaining maze assets" en `docs/ASSET_LICENSES.md`. No asumas CC0 ni
ninguna otra licencia para estos archivos.

## Cosas para modificar

- La velocidad de movimiento del jugador es `4` (celdas de
  cuadrícula/paso) mientras que la parada por choque con muro usa
  velocidad `8` — ambos son parámetros de acción codificados por
  tecla en `obj_person`, igual que en `maze_1`.
- Los 4 archivos de sonido incluidos no están referenciados — ningún
  objeto llama actualmente a `play_sound`; conectar uno para la
  recogida de caramelo / apertura de puerta / objetivo alcanzado
  sería un siguiente paso natural.
- Las salas son `480×480`–`480×512` a `room_speed: 30` — laberintos
  pequeños de pantalla única sin desplazamiento.
- `sprites/tiles.json` es un archivo colateral residual no registrado
  como recurso del proyecto (su `sprites/tiles.png` no existe) —
  seguro de eliminar o ignorar.

## Estado de la exportación

Cubierto por la suite de smoke-tests sin interfaz gráfica
(`tools/smoke_run_samples.py`, que lista `maze_2` y lo ejecuta durante
~180 fotogramas con entrada de teclado inyectada); no verificado
individualmente por cada destino de exportación (Kivy/Web). Expuesto
en la pestaña Welcome del IDE como "Maze — Level 2"
(`widgets/welcome_tab.py`).
