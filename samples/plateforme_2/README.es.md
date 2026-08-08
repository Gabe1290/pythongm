# Platform — Nivel 2

Un plataformas de desplazamiento lateral importado desde GameMaker
8.x (`samples/plateforme_2.gmk`). Comparado con un primer nivel
mínimo, este eleva la lista de objetos de un solo jugador + un bloque
a cuatro objetos (una plataforma base más variantes horizontal y
vertical que heredan de ella) dispuestos en una sala de 126 instancias
construida a partir de un conjunto de teselas automáticas con tema de
nieve, en lugar de unos pocos bloques colocados a mano.

**Dónde encaja:** parte de la familia `plateforme_*`, y — a
diferencia del mínimo `plateforme_1` — aquí es donde aparece el
**fondo en teselas**: 127 fragmentos de teselas de fondo colocados
individualmente (el array `tiles` de la sala) más una imagen de fondo
en degradado (`fond_degrade`), en capas bajo los *objetos* de ladrillo
sólido que siguen manejando la colisión. Este es el paso que
`plateforme_*` añade más allá de `maze_*`; ver
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para la progresión completa.

**Sonido y música:** ninguno — no se incluyen archivos de sonido con esta muestra.

## Cómo se juega

- **Flecha izquierda/derecha** — mueve al pingüino (`obj_personnage`) izquierda/derecha.
- **Flecha arriba** — salto, pero solo mientras está parado sobre una
  plataforma sólida (comprobado mediante una prueba de colisión un
  píxel debajo del jugador).
- **Objetivo** — no hay un objeto objetivo/bandera en esta muestra; es
  una disposición de plataformas para explorar/atravesar sobre las
  plataformas `obj_brique*`.
- **Condición de derrota** — ninguna está definida (sin peligros, sin
  objetos letales, sin comprobación de muerte por caída); la fila de
  ladrillos inferior de la sala actúa como suelo.

## Estructura del proyecto

| Archivo | Propósito |
| --- | --- |
| `project.json` | Manifiesto del proyecto — configuración de ventana/sala, copias de recursos incrustadas. |
| `rooms/niveau_01.json` | La única sala: 800×640, 126 instancias + 127 teselas de fondo. Fuente de verdad para el contenido de la sala (la lista `instances` incrustada de `project.json` está vacía). |
| `objects/*.json` | Archivos colaterales por objeto de los 4 objetos; idénticos a las copias incrustadas en `project.json` a esta fecha. |
| `sprites/` | 5 recursos sprite (tiras de caminata del jugador y bloques de plataforma sólidos). |
| `backgrounds/` | Conjunto de teselas de nieve (`tuiles_neige.png`, usado como fuente de teselas automáticas) y un pequeño degradado vertical (`fond_degrade.png`) estirado como fondo de sala. |
| `CREDITS.txt` | Aviso de licencia para el arte de sprites/fondo (ver Recursos abajo). |

## Objetos

| Objeto | Rol | Eventos clave |
| --- | --- | --- |
| `obj_personnage` | Jugador (pingüino) — movimiento, salto, gravedad, detección de suelo | create, step, collision_with_obj_brique, keyboard (left, right, up), keyboard_release (LEFT, RIGHT) |
| `obj_brique` | Bloque de plataforma sólida base (32×32) | ninguno (sin eventos; solo bandera sólida) |
| `obj_brique_h` | Variante ancha de plataforma sólida (32×16), hija de `obj_brique` | ninguno |
| `obj_brique_v` | Variante estrecha de plataforma sólida (8×16), hija de `obj_brique`; definida pero no colocada en `niveau_01` | ninguno |

## Recursos

5 sprites (`spr_pingus_dr`/`spr_pingus_ga` tiras de caminata de 8
fotogramas, más tres bloques marcador de posición de color sólido a
32×32 / 32×16 / 8×16) y 2 fondos; sin sonidos. El arte de sprites y
fondos está adaptado del proyecto Pingus (GPL-3.0-or-later) — ver
`CREDITS.txt` para la atribución completa y los términos de licencia;
este README no reafirma ni extiende esas declaraciones.

## Cosas para modificar

- La velocidad horizontal del jugador es un `hspeed = 4` fijo en los eventos de teclado.
- El impulso de salto es `vspeed = -10`; la gravedad de caída es
  `0,45` (aplicada solo en el aire), con un tope de velocidad
  terminal en `vspeed = 24`.
- El tamaño de la sala es 800×640 a `room_speed = 30`.

## Estado de la exportación

Esta muestra está listada en la lista `SAMPLES` de
`tools/smoke_run_samples.py`, así que recibe un pase smoke sin
interfaz gráfica (el bucle de juego real ejecutado durante ~180
fotogramas con entrada de teclado inyectada) en cada ejecución de ese
arnés. No se ha hecho ninguna verificación por destino de exportación
específico (Kivy/HTML5) para esta muestra en particular. Está
expuesta en la pestaña Welcome del IDE como "Platform — Level 2"
(`widgets/welcome_tab.py`).
