# Match-3 — Nivel 2

La continuación animada basada en sprites de
[`match3_1`](../match3_1/README.md), prometida en la Hoja de ruta de
esa muestra: el mismo tablero y puntuación, ahora dibujado con
sprites de gemas reales en lugar de rectángulos de color, con una
animación de deslizamiento del intercambio, y efectos de sonido para
intercambio/alineamiento/cascada. Sigue siendo una sala, un objeto,
sin scripts — todo el juego son aún cuatro eventos `execute_code` en
un único objeto controlador.

**Dónde encaja:** parte de la familia `match3_*` — script puro
`execute_code`, sin acciones integradas, sin teselas a nivel de sala.
Ver
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para cómo esto difiere del enfoque de acciones integradas y
multi-objeto de `maze_*`/`plateforme_*`.

**Sonido y música:** 3 archivos de sonido (`snd_swap`, `snd_match`,
`snd_cascade`), todos usados activamente — encolados desde
`execute_code` vía `self._sound_queue` (ver abajo), no la acción `play_sound`.

## Cómo se juega

Igual que match3_1:

- **Haz clic** en una tesela para seleccionarla (contorno blanco),
  luego **haz clic en una tesela adyacente** para intercambiarlas. El
  intercambio ahora **se desliza** a su lugar en vez de encajar instantáneamente.
- Si el intercambio alinea **3 o más teselas del mismo color** en fila
  o columna, las teselas alineadas parpadean un instante, se
  destruyen, y las teselas de arriba **se deslizan hacia abajo** para
  llenar el hueco; nuevas teselas caen desde arriba del tablero. Las
  reacciones en cadena ("cascadas") se resuelven ola por ola.
- Un intercambio que no produce ningún alineamiento **se desliza de
  vuelta** a su posición original en lugar de encajar hacia atrás.
- Cada tesela destruida vale **10 puntos**; alcanza **500 puntos**
  para ganar.
- Cada intento de intercambio reproduce un clic; un alineamiento
  exitoso reproduce un timbre, y cada cascada adicional en la misma
  combinación reproduce un timbre más brillante y ascendente.

## Qué cambia respecto a match3_1

| match3_1 | match3_2 |
| -------- | -------- |
| Teselas dibujadas como rectángulos de color sólido | Teselas dibujadas como **sprites** de gema (comando de cola de dibujo al estilo `draw_sprite`), una forma por color para accesibilidad a daltónicos |
| El intercambio se aplica instantáneamente, los alineamientos se evalúan de inmediato | El intercambio **se desliza** a su lugar primero (~4 fotogramas); un intercambio inválido se desliza de vuelta en lugar de encajar |
| Sin audio | **Efectos de sonido** para intercambio/alineamiento/cascada, encolados desde `execute_code` vía la nueva primitiva `self._sound_queue` (ver abajo) |

La lógica del tablero en sí (modelo de cuadrícula, búsqueda de
alineamientos, caída en cascada, puntuación, condición de victoria) no
cambia respecto a match3_1 — es un diff genuinamente legible, no una reescritura.

## Estructura del proyecto

| Archivo | Propósito |
| ---- | ------- |
| `project.json` | manifiesto del proyecto — ventana 800×800, 60 fps, sala de inicio `rm_match3` |
| `rooms/rm_match3.json` | la única sala; contiene una instancia de `obj_GridManager` en (0, 0) |
| `objects/obj_GridManager.json` | todo el juego: cuatro eventos, cada uno con una única acción `execute_code` |
| `sprites/spr_gem_red|blue|green|yellow.png` | teselas de gema 88×88 (ver `CREDITS.txt`) — dimensionadas para encajar exactamente donde antes estaba el relleno de rectángulo de match3_1, ya que `draw_sprite` dibuja a tamaño nativo sin escalado |
| `sounds/snd_swap|match|cascade.wav` | tonos sintetizados cortos (ver `CREDITS.txt`) |

## Cómo funciona el código

El estado y la máquina de estados `step` son los mismos que en
match3_1 (`grid`, `sel`, `marked`, `flash`/`flash_total`,
`falling`/`fall_speed`, `score`, `target`, `won`, `find_matches`) —
ver ese README para la descripción completa. Nuevo estado añadido
para esta versión:

| Atributo | Significado |
| --------- | ------- |
| `sprite_names` | `['spr_gem_red', 'spr_gem_blue', 'spr_gem_green', 'spr_gem_yellow']`, indexado de la misma forma que `palette` lo estaba en match3_1 |
| `swap_off` | diccionario `(gx, gy) → (dx, dy)` desplazamiento en píxeles para el deslizamiento de intercambio en curso; decae a `(0, 0)` a `swap_speed` px/fotograma, la misma técnica de reducción-al-reposo que `falling` ya usa para las cascadas, generalizada a dos ejes |
| `swap_phase` | `None` / `'forward'` (deslizándose hacia la posición intercambiada) / `'back'` (un intercambio rechazado deslizándose de vuelta a sus celdas originales) |
| `last_swap` | `(gx, gy, sx, sy)` — las dos celdas implicadas en el intercambio en vuelo, así `step` puede revertirlas sin necesitar estado de cierre |
| `pending_marks` | el conjunto de alineamiento calculado justo después de un intercambio, retenido hasta que la animación de deslizamiento termina para que el parpadeo no empiece a mitad del deslizamiento |
| `arm_swap(a, b)` | función auxiliar (definida en `create`, almacenada en la instancia como `find_matches`) que fija `swap_off` para ambas celdas solo a partir de sus posiciones — llamarla de nuevo con las mismas dos celdas produce la animación inversa, lo que da gratis el deslizamiento de reversión |

Flujo actualizado:

```
clic en tesela adyacente
  → cuadrícula intercambiada de inmediato (datos), pending_marks calculado
  → swap_off armado (forward) — las teselas se deslizan a sus nuevas celdas
       │
       ▼ (el deslizamiento se asienta)
  pending_marks?
    sí → arma el parpadeo (parpadea → destruye → cae → reanaliza, como en match3_1)
    no  → intercambia la cuadrícula de vuelta, rearma swap_off con las MISMAS dos celdas (phase='back')
             │
             ▼ (el deslizamiento se asienta)
          idle
```

- **`create`** — misma siembra de cuadrícula que match3_1, más
  `sprite_names`, `swap_off`/`swap_speed`/`swap_phase`/`last_swap`/
  `pending_marks`, y la función auxiliar `arm_swap`.
- **`mouse_left_press`** — la lógica de selección no cambia; un
  intercambio adyacente válido ahora aplica el intercambio en la
  cuadrícula, calcula `pending_marks`, arma el deslizamiento hacia
  adelante, y encola `snd_swap`.
- **`step`** — los bloques de parpadeo/caída no cambian respecto a
  match3_1 (siguen encolando `snd_cascade` en un nuevo alineamiento
  encadenado); un nuevo bloque `elif self.swap_off:` decae el
  deslizamiento y, una vez asentado, o bien arma el parpadeo
  (encolando `snd_match`) o inicia el deslizamiento de reversión.
- **`draw`** — mismo dibujo de panel/tablero/selección/puntuación/
  instrucciones/banner de victoria que match3_1, pero cada tesela es
  ahora un comando de cola de dibujo
  `{'type': 'sprite', 'sprite_name': ..., 'x': ..., 'y': ...}` en
  lugar de un rectángulo sólido (aún reemplazado por un simple
  rectángulo blanco sólido durante el parpadeo de la tesela marcada,
  exactamente como hacía match3_1), desplazado por `swap_off`
  combinado con `falling`.

### La primitiva `self._sound_queue`

`execute_code` solo tiene un objeto `game` vivo en el motor pygame de
escritorio — tanto el motor exportado a Kivy como el motor Web/Pyodide
vinculan `game = None` en ese ámbito, así que
`game.sounds[...].play()` (lo obvio a probar) solo funciona en
escritorio. Esta muestra es lo que motivó añadir una primitiva
multiplataforma real: el `execute_code` de cualquier evento puede hacer

```python
self._sound_queue.append('snd_swap')
# o, para un volumen no predeterminado:
self._sound_queue.append({'sound': 'snd_swap', 'volume': 0.5})
```

y esto se reproduce idénticamente en los tres destinos:

- **Escritorio** — `ActionExecutor.execute_event` la vacía y la
  reproduce (vía `game.sounds[...]`) justo después de cada evento, no
  solo `draw`.
- **Exportación Kivy** — `GameObject._drain_sound_queue` (generado en
  `base_object.py`) resuelve el nombre vía un `asset_paths.py`
  generado (`SOUND_PATHS`) y llama al helper `play_sound()`
  existente; vaciado una vez por fotograma por cada instancia viva
  desde el bucle `update()` de la escena, así que funciona incluso
  para objetos sin evento `draw`.
- **Web (Pyodide)** — el bootstrap de Python devuelve cualquier sonido
  encolado en el parche JSON junto con la cola de dibujo; `engine.js`
  los reproduce como elementos `<audio>` reales a través de la misma
  ruta de audio agrupada que ya usaba la acción estructurada `play_sound`.

La misma brecha de resolución por nombre existía para los comandos al
estilo `draw_sprite` enviados desde `execute_code` en bruto (el
renderizado de teselas de esta muestra) — el renderizador de la cola
de dibujo de Kivy antes solo podía resolver un sprite a partir de un
`sprite_path` incrustado en el momento de la generación de código
para acciones *estructuradas*, así que un diccionario
`{'type': 'sprite', 'sprite_name': ...}` escrito a mano no se
renderizaba allí silenciosamente. Corregido de la misma forma:
`asset_paths.py` ahora también lleva `SPRITE_PATHS`, y el caso
`'sprite'` de la cola de dibujo de Kivy recurre a él por nombre cuando
no hay una ruta pre-resuelta presente.

### Cosas para modificar

Mismos controles que match3_1 (`self.cols`/`self.rows`,
`self.palette`, `self.target`, `flash_total`, `fall_speed`), más:

- Velocidad de la animación de intercambio: `self.swap_speed`
  (px/fotograma; 24 → ~4 fotogramas por deslizamiento con `tile=96`).
- Volumen del sonido: pasa un diccionario
  `{'sound': ..., 'volume': ...}` en lugar de un nombre desnudo a
  `self._sound_queue.append(...)`.

## Hoja de ruta

**[match3_3](../match3_3/README.md)** — hecho: un límite de
movimientos, tres salas como niveles de objetivo creciente, y teselas
especiales (bonificaciones de 4/5 en línea). Cierra la hoja de ruta
original de match3_1.

## Estado de la exportación

- **Test Game (F5) / escritorio:** funciona — verificado de extremo a
  extremo con una ejecución real de `GameRunner` que inyecta un clic
  de ratón real a través de la ruta de eventos pygame estándar
  (intercambio → alineamiento → cascada → puntuación, con llamadas
  reales a `pygame.mixer.Sound.play()` observadas).
- **Android (.apk) / Móvil (Kivy):** **compatible.** Verificado que la
  exportación compile limpiamente, que `asset_paths.py` lleve los
  `SPRITE_PATHS`/`SOUND_PATHS` correctos, y que las imágenes de
  sprites/archivos de sonido se copien a
  `assets/images`/`assets/sounds`. Construir el `.apk` real requiere
  además buildozer (vía WSL en Windows) — ver
  [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Web (HTML5):** **compatible.** El bootstrap Pyodide de la página
  exportada vacía `self._sound_queue` en el mismo intercambio JSON
  que la cola de dibujo; verificado que el bootstrap generado
  compile y transfiera correctamente tanto los comandos de dibujo
  como los sonidos encolados bajo CPython puro (no se necesita
  navegador para esta comprobación — el arranque de Pyodide en el
  navegador en sí no lo cubre la suite automática, misma advertencia
  que match3_1). Necesita acceso a internet en la primera carga
  (Pyodide se carga desde una CDN).
- **Zip independiente:** no probado con esta muestra.
