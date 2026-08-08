# Match-3 — Nivel 1

Un juego de puzle match-3 (tres en línea) mínimo y completo. Esta es
la primera muestra de pygm2 **escrita nativamente en el formato de
proyecto propio del IDE** — las muestras de laberinto y plataformas se
importaron desde archivos `.gmk` de GameMaker 8.x; esta se escribió
directamente para el motor de pygm2.

Es deliberadamente pequeña: una sala, un objeto, sin scripts, sin
sonidos. Todo el juego vive en cuatro eventos de un único objeto
controlador, lo que la convierte en la muestra de referencia para la
acción `execute_code` y para el renderizado mediante cola de dibujo.
Están planeadas versiones más avanzadas (tesela basada en sprites,
sonido, niveles) como `match3_2`, etc. — ver *Hoja de ruta* más abajo.

**Dónde encaja:** `match3_*` es la última (y más diferente) de las
tres familias de muestras — un paradigma distinto, no un paso
incremental: sin acciones integradas, sin objeto por tesela, sin
teselas a nivel de sala. Todo (estado de la cuadrícula, colisiones,
renderizado) se maneja directamente desde Python en `execute_code` en
lugar de componerse a partir de acciones integradas repartidas en
muchos objetos, como hacen `maze_*` y `plateforme_*`. Ver
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para la progresión completa.

**Sonido y música:** ninguno — deliberadamente, por el motivo
explicado arriba. (El sonido se vuelve posible desde `match3_2` en
adelante, mediante la primitiva de cola de sonido que esa muestra introdujo.)

## Cómo se juega

- **Haz clic** en una tesela para seleccionarla (contorno blanco),
  luego **haz clic en una tesela adyacente** para intercambiarlas.
- Si el intercambio alinea **3 o más teselas del mismo color** en fila
  o columna, las teselas alineadas parpadean un instante, se
  destruyen, y las teselas de arriba **se deslizan hacia abajo** para
  llenar el hueco; nuevas teselas caen desde arriba del tablero.
- Las reacciones en cadena ("cascadas") se resuelven ola por ola, cada
  una con su propia animación de parpadeo y deslizamiento.
- Un intercambio que no produce ningún alineamiento se revierte de inmediato.
- Cada tesela destruida vale **10 puntos**; alcanza **500 puntos**
  para ganar.

## Estructura del proyecto

| Archivo | Propósito |
| ---- | ------- |
| `project.json` | manifiesto del proyecto — ventana 800×800, 60 fps (`room_speed`), sala de inicio `rm_match3` |
| `rooms/rm_match3.json` | la única sala; contiene una instancia de `obj_GridManager` en (0, 0) |
| `objects/obj_GridManager.json` | todo el juego: cuatro eventos, cada uno con una única acción `execute_code` |
| `sprites/spr_red|blue|green|yellow.*` | cuadros de tesela 32×32 — **aún no usados**; reservados para la continuación basada en sprites (ver `CREDITS.txt`) |

No hay objeto jugador ni objeto por tesela: el tablero es datos puros
(una lista 6×6 de índices de color) propiedad de una única instancia
controladora invisible, y todo lo que aparece en pantalla lo dibuja el
evento `draw` de ese controlador a través de la cola de dibujo del
motor (`self._draw_queue`).

## Cómo funciona el código

Todo el estado vive en la instancia controladora (`self.…`), creada en
el evento `create`:

| Atributo | Significado |
| --------- | ------- |
| `grid` | lista 6×6 de enteros 0–3 (índices en `palette`); inicializada sin alineamientos preexistentes |
| `sel` | celda actualmente seleccionada `(gx, gy)` o `None` |
| `marked` | conjunto de celdas actualmente alineadas y parpadeando |
| `flash` / `flash_total` | fotogramas restantes de la fase de parpadeo / su duración (36 fotogramas ≈ 0,6 s a 60 fps) |
| `falling` | diccionario `(gx, gy) → píxeles` — cuánto por encima de su celda de reposo está actualmente cada tesela deslizándose |
| `fall_speed` | velocidad de deslizamiento en píxeles por fotograma (12 → una fila de 96 px en ~0,13 s) |
| `score`, `target`, `won` | estado de puntuación (victoria a los 500) |
| `find_matches` | función auxiliar (definida en `create`, almacenada en la instancia) que examina la cuadrícula y devuelve el conjunto de todas las celdas alineadas |

El juego es una pequeña máquina de estados manejada por el evento `step`:

```
idle ──(intercambio por clic, alineamiento encontrado)──▶ FLASH (parpadeo, 36 fotogramas)
                                        │ teselas destruidas, puntuación añadida
                                        ▼
                                      FALL (el desplazamiento se reduce 12 px/fotograma)
                                        │ aterrizado → reanálisis de la cuadrícula
                          nuevo alineamiento ─┴─ sin alineamiento
                                 │            │
                                 ▼            ▼
                               FLASH        idle
```

- **`create`** — construye la cuadrícula inicial (volviendo a sortear
  cualquier tesela que completaría un alineamiento inmediato),
  inicializa el estado de arriba, y define `find_matches`.
- **`mouse_left_press`** — lógica de selección/deselección; en un
  intercambio adyacente aplica el intercambio, y o bien arma el
  parpadeo (`marked`, `flash`) o revierte. La entrada se ignora
  mientras un parpadeo o caída están en curso, y después de que el
  juego se haya ganado.
- **`step`** — cuenta regresivamente el parpadeo; al expirar acredita
  la puntuación, reescribe cada columna afectada en su disposición
  final, y registra un desplazamiento en píxeles en `falling` para
  cada tesela que se movió (las teselas supervivientes obtienen
  `filas_caídas × 96`; las teselas de relleno entran desde arriba del
  tablero). Mientras `falling` no esté vacío, reduce cada
  desplazamiento en `fall_speed`; cuando todo ha aterrizado, reanaliza
  en busca de alineamientos en cascada y o bien rearma el parpadeo o
  vuelve a idle.
- **`draw`** — dibuja el panel del tablero, luego cada tesela en
  `posición_de_reposo − desplazamiento_de_caída`. Las teselas por
  encima del borde superior del tablero se recortan (parcialmente
  emergidas) o se omiten (completamente ocultas), de modo que los
  rellenos parecen deslizarse desde debajo de la cabecera. Las teselas
  marcadas parpadean en blanco cada 6 fotogramas y llevan un contorno
  blanco; la selección, la línea de puntuación, las instrucciones y el
  banner de victoria se dibujan al final.

### Cosas para modificar

- Tamaño del tablero: `self.cols` / `self.rows` (las constantes de
  disposición `ox`, `oy`, `tile` controlan la colocación — un tablero
  6×6 de teselas de 96 px cabe en la ventana 800×800).
- Colores / tipos de tesela: `self.palette` (añade una tupla para
  obtener un 5º color; la lógica de resorteo y el renderizador lo
  recogen automáticamente, pero actualiza `random.randrange(4)` en
  `create` y `step`).
- Dificultad: `self.target` (puntos para ganar), `flash_total`,
  `fall_speed`.

## Hoja de ruta (versiones avanzadas planeadas)

- **[match3_2](../match3_2/README.md)** — hecho: dibuja las teselas
  con sprites en lugar de rectángulos de color, añade efectos de
  sonido para intercambio/alineamiento/cascada, y una animación de
  deslizamiento del intercambio.
- **[match3_3](../match3_3/README.md)** — hecho: un límite de
  movimientos, tres salas como niveles de objetivo creciente, y
  teselas especiales a partir de alineamientos de 4/5 en línea. Cierra
  esta hoja de ruta.

Las versiones están pensadas para reflejar la progresión maze_1→3:
cada una es un diff legible respecto a la anterior.

## Estado de la exportación

- **Test Game (F5) / escritorio:** funciona — el juego corre en el
  motor pygame estándar. Se ejerce sin interfaz gráfica en ejecuciones
  smoke tipo CI mediante `tools/smoke_run_samples.py`.
- **Android (.apk) / Móvil (Kivy):** **compatible** (desde el
  03/07/2026). El motor Kivy exportado renderiza la cola de dibujo del
  juego (rectángulos y texto, con el eje y convertido al sistema de
  abajo hacia arriba de Kivy), envía los toques como evento
  `mouse_left_press` con `mouse_x`/`mouse_y` en coordenadas de sala
  tanto en Android (invirtiendo la transformación de escala a pantalla
  completa) como en Kivy de escritorio, y — dado que este juego no
  tiene eventos de teclado — omite la superposición del D-pad virtual
  que de otro modo cubriría la esquina inferior derecha del tablero.
  El juego exportado se ejerce sin interfaz gráfica en
  `tests/test_kivy_draw_queue_mouse_export.py`, que juega una ronda
  completa de intercambio → parpadeo → deslizamiento a través del
  código generado. Construir el `.apk` real requiere además buildozer
  (vía WSL en Windows) — ver
  [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md) para la
  guía completa (configuración, tiempos de compilación, caché para uso
  en clase/sesión); las brechas de paridad de exportación Kivy
  restantes que *no* afectan a este juego están listadas bajo
  "Kivy/Android export" en el `TODO.md` del repositorio.
- **Web (HTML5):** **compatible** (desde el 10/07/2026) — y la mejor
  vía hacia los iPhone (sin instalación, sin firma). La página
  exportada detecta que el juego contiene eventos Python
  `execute_code` y carga el motor Pyodide para ejecutarlos con la
  semántica del IDE; los toques/clics se envían como el evento de
  pulsación del botón izquierdo del ratón y la cola de dibujo se
  renderiza en el canvas. Verificado de extremo a extremo en Chromium
  sin interfaz gráfica (el tablero se renderiza, intercambio por clic,
  parpadeo, deslizamiento, puntuación). Una advertencia: el motor
  Python se carga desde una CDN, por lo que la página necesita acceso
  a internet al abrirse — los juegos basados solo en acciones (las
  muestras de laberinto/plataformas) permanecen completamente sin conexión.
- **Zip independiente:** no probado con esta muestra.
