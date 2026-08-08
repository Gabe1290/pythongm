# Match-3 — Nivel 3

La continuación con límite de movimientos / multinivel / teselas
especiales de [`match3_2`](../match3_2/README.md) prometida en la Hoja
de ruta original de match3_1 — la última de las tres versiones match3
planeadas. Misma arquitectura en todo: sin scripts, todo el juego
sigue siendo cuatro eventos `execute_code` en un único objeto
controlador, solo que colocado en tres salas en lugar de una.

**Dónde encaja:** parte de la familia `match3_*` — script puro
`execute_code`, sin acciones integradas, sin teselas a nivel de sala,
cerrando la progresión descrita en
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays).

**Sonido y música:** 5 archivos de sonido — los 3 de `match3_2`
(`snd_swap`/`match`/`cascade`) más 2 nuevos (`snd_special`,
`snd_level_up`), todos usados activamente vía `self._sound_queue`.

## Cómo se juega

Mismas reglas de intercambio/alineamiento/cascada que match3_1 y
match3_2, más:

- Tienes un **número limitado de movimientos** por nivel. Un
  movimiento solo se consume en un intercambio que realmente produce
  un alineamiento — un intercambio inválido (que se desliza de
  vuelta) puede reintentarse gratis.
- Alcanza la **puntuación objetivo** del nivel antes de quedarte sin
  movimientos para avanzar a la siguiente sala. Si se agotan primero,
  el nivel termina — **haz clic en cualquier lugar para reintentar**
  el mismo nivel desde cero.
- **Alinea 4 en línea** (exactamente 4) y una de las cuatro teselas se
  convierte en una **especial de limpieza de línea**: una barra blanca
  la marca. Alinéala de nuevo más tarde (como parte de cualquier otro
  alineamiento) y limpia su **fila o columna entera** — la dirección
  que sea que tuviera la racha original de 4.
- **Alinea 5 o más en línea** y una tesela se convierte en una
  **especial bomba de color**: un anillo blanco la marca. Alinéala de
  nuevo más tarde y limpia **cada tesela de un color** en todo el tablero.
- Hay **3 niveles**, cada uno su propia sala con un objetivo más alto
  y un límite de movimientos más estrecho. Completa el nivel 3 para
  ganar el juego.

## Qué cambia respecto a match3_2

| match3_2 | match3_3 |
| -------- | -------- |
| Una sala, movimientos ilimitados, victoria a puntuación fija | **3 salas** (una por nivel), un **límite de movimientos** por nivel, y un **objetivo creciente** por nivel |
| Un alineamiento siempre se destruye por completo | Una racha de **4** o **5+** deja una **tesela especial** en lugar de destruir cada celda |
| Sin progresión de nivel a nivel | Alcanzar el objetivo llama a `self.advance_level()`, que fija `self.goto_room_target` a la siguiente sala (o `self.won` en el último nivel) |

La máquina de estados principal de intercambio/parpadeo/caída/cascada,
el dibujo de teselas sprite, y los disparadores de la cola de sonido
son por lo demás inalterados respecto a match3_2 — ver el README de
esa muestra para la descripción completa de `swap_off`/`falling`/`find_matches`.

## Estructura del proyecto

| Archivo | Propósito |
| ---- | ------- |
| `project.json` | manifiesto del proyecto — ventana 800×800, 60 fps, sala de inicio `rm_level1`, `room_order` = los 3 niveles |
| `rooms/rm_level1|2|3.json` | una sala por nivel, cada una con su propia instancia de `obj_GridManager` en (0, 0) |
| `objects/obj_GridManager.json` | todo el juego: cuatro eventos, cada uno con una única acción `execute_code` |
| `sprites/`, `sounds/` | teselas de gema + efectos, en su mayoría copiados de match3_2 (ver `CREDITS.txt`); `snd_special` y `snd_level_up` son nuevos |

Aún no hay objeto por tesela ni scripts — una instancia controladora
por sala, creada de nuevo (mediante la regla habitual de GameMaker de
"cada sala tiene sus propias instancias") cada vez que se entra en una
sala, lo que le da a cada nivel una pizarra limpia gratis.

## Cómo funciona el código

### Configuración de nivel (nuevo en `create`)

```python
self.room_order = ['rm_level1', 'rm_level2', 'rm_level3']
level_config = {
    'rm_level1': (300, 20),   # (target score, move limit)
    'rm_level2': (500, 18),
    'rm_level3': (800, 16),
}
```

`create` lee `game.current_room.name`, lo almacena en
`self.room_name` (necesario porque una variable local simple definida
en un evento `execute_code` **no** sobrevive a un evento posterior —
ver la nota sobre la trampa abajo), y fija
`self.target`/`self.moves`/`self.level_num` a partir de la tabla de arriba.

### Movimientos y derrota (nuevo en `mouse_left_press`)

Un intercambio solo consume un movimiento si `find_matches` dice que
realmente producirá un alineamiento
(`if marks: self.moves = self.moves - 1`), así que un intercambio
rechazado que se desliza de vuelta es gratis. Cuando `self.moves`
llega a 0 sin alcanzar el objetivo, `step` fija `self.lost = True`;
`mouse_left_press` comprueba esa bandera **primero**, antes de la
guardia de entrada normal, y convierte cualquier clic en
`self.restart_room_flag = True` (la misma bandera que usa
`restart_room`), lo que reconstruye la sala — y con ella, una nueva
instancia de `obj_GridManager` cuyo evento `create` reinicia todo.

### Teselas especiales (nuevo en `step`)

`find_matches` ahora devuelve `(marks, runs)` en lugar de solo
`marks` — cada racha es `(cells_in_order, 'h' o 'v')`. Al expirar el
parpadeo, **antes** de puntuar:

1. Por cada racha de longitud ≥ 4, la **celda central** se convierte
   en una tesela especial en lugar de ser destruida: las rachas de
   longitud 4 obtienen `('row',)` o `('col',)` (correspondiente a la
   orientación de la racha); las rachas de longitud 5+ obtienen
   `('color', <índice de color>)`.
2. Por cada celda ya marcada que tiene una entrada en `self.special`
   (es decir, una tesela especial fue justo capturada en *este*
   alineamiento), su efecto se dispara una vez: una especial
   `row`/`col` añade toda su fila/columna a las celdas que se
   limpiarán; una especial `color` añade cada celda del tablero de su
   color almacenado. Esto es un **único paso, no recursivo** — si la
   explosión de una especial captura otra especial, esa se destruye
   pero **no** dispara en cadena su propio efecto. (Una
   simplificación, no un error — mantiene el efecto acotado y fácil
   de razonar.)
3. Las celdas especiales recién creadas están protegidas de ser
   destruidas en la misma ola, incluso si una explosión del paso 2 las hubiera capturado.
4. `self.special` se reconstruye desde cero cada ola, siguiendo a las
   teselas supervivientes mientras caen (el bucle de caída por
   columna ahora lleva un tercer elemento de tupla — el tipo especial
   de la tesela, o `None` — junto a su fila y color) así una tesela
   especial que aún no ha sido alineada se desliza hacia abajo con la
   gravedad como cualquier otra.

### Avance de nivel (nuevo en `create`, usado desde `step`)

```python
def advance_level():
    idx = self.room_order.index(self.room_name)
    if idx + 1 < len(self.room_order):
        self.goto_room_target = self.room_order[idx + 1]
        self._sound_queue.append('snd_level_up')
    else:
        self.won = True
self.advance_level = advance_level
```

`self.goto_room_target` es la misma bandera de instancia que fija la
acción integrada `goto_room` — el bucle principal del juego ya la
consulta cada fotograma, así que fijarla directamente desde
`execute_code` es suficiente para disparar una transición de sala
real, no se necesita ninguna acción estructurada. `step` llama a
`self.advance_level()` en cuanto `self.score >= self.target`, y omite
cualquier reanálisis de cascada por el resto de ese fotograma si un
cambio de sala (o una victoria final) está ahora pendiente, así una
sala saliente no sigue animándose.

### Trampa: los cierres sobre variables locales simples no sobreviven entre eventos

El entorno de ejecución de `execute_code` pasa diccionarios
**separados** de globals y locals (`exec(code, exec_globals,
exec_locals)`), lo que se comporta como el interior de una función:
una asignación simple de nivel superior (`room_name = ...`) termina en
el diccionario *locals*, pero un `def` definido en ese mismo nivel
superior resuelve sus variables libres a través del diccionario
*globals* cuando es **llamado** más tarde — lo cual, para un
auxiliar anidado almacenado en `self` (como `find_matches`,
`arm_swap`, y ahora `advance_level`), siempre ocurre desde una llamada
`execute_code` **diferente** con su propio diccionario locals nuevo.
Una variable local desnuda referenciada por tal auxiliar lanza un
`NameError` la primera vez que el auxiliar es realmente invocado
desde otro evento — parece correcto en el evento que lo define y
falla silenciosamente hasta que se dispara más tarde. La corrección
es la misma que `find_matches` de match3_1/`arm_swap` de match3_2 ya
modelaban sin decirlo explícitamente: cierra solo sobre `self`
(siempre presente en los globals de cada evento) o sobre
**atributos de instancia** (`self.room_name`, no un `room_name`
desnudo) — nunca sobre una variable local desnuda. Detectado por el
paso de validación con arnés independiente durante el desarrollo (ver
las notas de metodología de auditoría en el `CLAUDE.md` del
repositorio); ahora hay una prueba de regresión para esto
(`tests/test_match3_3_sample.py`).

### `draw`

Mismo dibujo de panel/tablero/selección/línea de puntuación/banner de
victoria que match3_2, más: una línea HUD para número de nivel y
movimientos restantes, una superposición de barra o anillo blanco
sobre el sprite de una tesela especial (omitida mientras la tesela
está a mitad de parpadeo), y un banner "OUT OF MOVES — click to retry"
cuando `self.lost`.

### Cosas para modificar

- Dificultad por nivel: la tabla `level_config` en `create`
  (puntuación objetivo, límite de movimientos) — añade una cuarta
  entrada y una cuarta sala para extender la secuencia.
- Radio de explosión de teselas especiales: las ramas
  `row`/`col`/`color` en el bucle de activación de `step`.
- Todo lo que match3_2 ya exponía (tamaño del tablero, velocidad de
  intercambio/caída, volúmenes de sonido).

## Hoja de ruta

Esto cierra la hoja de ruta original de tres partes de match3_1
(match3_1 → match3_2 → match3_3). No hay más versiones planeadas.

## Estado de la exportación

- **Test Game (F5) / escritorio:** funciona — verificado de extremo a
  extremo con una ejecución real de `GameRunner` que inyecta un clic
  de ratón real a través de la ruta de eventos pygame estándar:
  alineamiento forzado de 4 en línea → tesela especial creada →
  objetivo alcanzado → **la sala realmente cambió a `rm_level2`** con
  una nueva instancia (`level_num == 2`, puntuación/movimientos reiniciados).
- **Android (.apk) / Móvil (Kivy):** se apoya en la misma maquinaria
  `asset_paths.py` / `_drain_sound_queue` / respaldo sprite-por-nombre
  que match3_2 añadió y verificó — esta muestra no ejerce nada nuevo
  en ese frente (ningún nuevo tipo de comando de dibujo, ningún nuevo
  tipo de acción; `goto_room` vía bandera funciona idénticamente en
  el bucle de escena exportado a Kivy, que ya consulta las mismas
  banderas de instancia cada fotograma). Construir el `.apk` real
  requiere además buildozer (vía WSL en Windows) — ver
  [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Web (HTML5):** mismo razonamiento — ninguna nueva primitiva de
  cola de dibujo o cola de sonido más allá de lo que match3_2 ya
  había demostrado en este destino.
- **Zip independiente:** no probado con esta muestra.
