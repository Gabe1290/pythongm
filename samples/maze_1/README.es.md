# Laberinto — Nivel 1

Un juego de laberinto en cuadrícula visto desde arriba: guía al sprite
del jugador a través de un laberinto bordeado de muros para alcanzar
la tesela objetivo, que avanza a la siguiente sala. Este es un
proyecto pygm2 nativo (sin archivo `.gmk` hermano — sus recursos se
importaron originalmente mediante una importación de GameMaker 8.x,
según CREDITS.txt, pero el proyecto en sí está escrito/guardado en el
formato JSON propio de pygm2).

**Dónde encaja:** `maze_*` es la primera de tres familias de muestras
en una progresión aproximada de técnicas de creación (objetos/sprites
integrados → fondos en teselas añadidos de `plateforme_*` → juegos de
script puro `execute_code` de `match3_*`) — ver
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para el panorama completo. Esta muestra solo usa GameObjects + sprites,
sin imagen de fondo y sin teselas a nivel de sala.

**Sonido y música:** ninguno — no se incluyen archivos de sonido con esta muestra.

## Cómo se juega

- Las **teclas de flecha** (arriba/abajo/izquierda/derecha) mueven al
  jugador una celda de cuadrícula (32px) a la vez; el movimiento está
  ajustado a la cuadrícula vía
  `test_alignment`/`snap_to_grid` (cuadrícula 32×32).
- Los muros (`obj_wall`) son sólidos — caminar contra uno detiene al
  jugador y lo reajusta a la cuadrícula.
- **Objetivo:** alcanzar la tesela objetivo (`obj_goal`). Tocarla
  avanza a la siguiente sala si existe una, o reinicia el juego si no hay ninguna.
- **Atajos de depuración:** presionar `N` sobre el objetivo salta a la
  siguiente sala (si hay alguna); presionar `P` salta a la sala
  anterior (si hay alguna) — misma lógica de avance/reinicio que tocar el objetivo.
- No se usa seguimiento de vidas/puntuación/salud en esta muestra (la
  salud se reinicia vía `set_health` al avanzar de sala, pero nunca se muestra).

## Estructura del proyecto

| Archivo | Propósito |
|---|---|
| `project.json` | Manifiesto del proyecto — configuración de ventana/sala y copias incrustadas de todos los recursos |
| `rooms/room0.json` | Trazado del laberinto para la sala 0 (131 instancias: muros, inicio del jugador, objetivo) |
| `rooms/room1.json` | Trazado del laberinto para la sala 1 (130 instancias) |
| `objects/obj_person.json` | Definición del objeto jugador (fuente de verdad; coincide con la copia incrustada en `project.json`) |
| `objects/obj_goal.json` | Definición del objeto objetivo |
| `objects/obj_wall.json` | Definición del objeto muro |
| `sprites/` | `spr_person.png`, `spr_wall.png`, `spr_goal.png` + sus metadatos `.json` |
| `CREDITS.txt` | Aviso de licencia de recursos para esta muestra |

Los archivos colaterales `objects/*.json` se verificaron contra las
copias incrustadas de `project.json` y son idénticos en esta muestra —
no se encontró obsolescencia.

## Objetos

| Objeto | Rol | Eventos clave |
|---|---|---|
| `obj_person` | Personaje controlado por el jugador; movimiento en cuadrícula | create-implícito vía teclado, keyboard (down, right, up, left, nokey), collision_with_obj_wall |
| `obj_goal` | Salida del nivel; avanza/reinicia al toque o tecla de depuración | collision_with_obj_person, keyboard_press (p, n) |
| `obj_wall` | Muro sólido estático del laberinto, bloquea el movimiento | (ninguno — solo colisionador pasivo) |

## Recursos

3 sprites (`spr_person`, `spr_wall`, `spr_goal`, cada uno 32×32, un
solo fotograma, colisión precisa a nivel de píxel), 0 sonidos.
Licencias: `spr_person.png` y `spr_wall.png` son CC0 (dominio
público), obras del autor de pygm2; la procedencia de `spr_goal.png`
aún no está documentada — ver `CREDITS.txt` en esta carpeta y
`docs/ASSET_LICENSES.md` en la raíz del repositorio para el panorama completo.

## Cosas para modificar

- La velocidad de movimiento del jugador es `4` (celdas de
  cuadrícula/paso) mientras que la parada por choque con muro usa
  velocidad `8` — ambos son parámetros de acción codificados por
  tecla en `obj_person`.
- El tamaño de la cuadrícula es `32` (coincide con los sprites de
  32×32); cambiarlo necesita ediciones correspondientes a las
  llamadas `snap_to_grid`/`test_alignment` y a los trazados de las salas.
- Las salas son `480×480` a `room_speed: 30` — laberintos pequeños de
  pantalla única sin desplazamiento.
- Las teclas de depuración `N`/`P` en `obj_goal` permiten saltar entre
  room0/room1 sin tocar el objetivo — útil para pruebas, pero fácil
  de activar accidentalmente durante el juego.

## Estado de la exportación

Cubierto por la suite de smoke-tests sin interfaz gráfica
(`tools/smoke_run_samples.py`, que lista `maze_1` y lo ejecuta durante
~180 fotogramas con entrada de teclado inyectada); no verificado
individualmente por cada destino de exportación (Kivy/Web). Expuesto
en la pestaña Welcome del IDE como "Maze — Level 1"
(`widgets/welcome_tab.py`).
