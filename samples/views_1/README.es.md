# Views — Nivel 1

Una demo de cámara con desplazamiento: la sala (2400×800) es **tres
veces más ancha que la ventana de 800×600**, así que una sola
pantalla no puede mostrarla toda. La cámara (view 0) sigue al jugador
mientras camina hacia la derecha, revelando el nivel una pantalla a
la vez — todo el sentido de las **views** al estilo GameMaker.
Explora la sala ancha y recolecta las 18 monedas.

**Dónde encaja:** esta es la cuarta familia de muestras, distinta de
las tres familias por técnica de creación (`maze_*` → `plateforme_*`
→ `match3_*`). Lo que introduce no es un nuevo *estilo* de creación
sino una nueva capacidad del motor: una **sala más grande que la
ventana** con una **cámara con desplazamiento**. Ver
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para la progresión completa. Mecánicamente reutiliza el movimiento en
cuadrícula de `maze_1` (acciones integradas
`test_alignment`/`snap_to_grid`/`start_moving_direction`) y añade
exactamente una cosa nueva: la cámara, activada desde el evento
**create** del jugador con las acciones registradas `enable_views` + `set_view`.

**Sonido y música:** ninguno — no se incluyen archivos de sonido con esta muestra.

## Cómo se juega

- Las **teclas de flecha** mueven al jugador una celda de cuadrícula
  (32px) a la vez (movimiento ajustado a la cuadrícula, como en `maze_1`).
- Los muros (`obj_wall`) bordean la sala y forman algunos pilares
  interiores; son sólidos y detienen al jugador.
- **La cámara sigue al jugador**: camina hacia un borde de la
  pantalla y la vista se desplaza para mantenerte en el encuadre,
  fijándose en los bordes de la sala para que nunca veas más allá del
  borde de muros.
- **Objetivo:** recolecta las 18 monedas (`obj_coin`). Cada una vale
  10 puntos (mostrados en el título de la ventana).

## Cómo está configurada la cámara

El evento **create** del jugador ejecuta dos acciones registradas
(sin `execute_code` en bruto):

1. `enable_views` — activa el sistema de views para la sala.
2. `set_view` — configura la **view 0**: `view_w`/`view_h` `800×600`,
   puerto en `(0,0)` con tamaño `800×600`, `follow` = `obj_player`,
   `hborder` 240 / `vborder` 180 (la zona muerta antes de que la
   cámara se desplace), sin tope de velocidad de desplazamiento. La
   misma configuración también está incrustada en el bloque `views`
   de la sala, así la cámara es correcta desde el primer fotograma en
   cada destino de exportación.

## Estructura del proyecto

| Archivo | Propósito |
|---|---|
| `project.json` | Manifiesto del proyecto — configuración de ventana/sala, copias de recursos incrustadas, y la configuración `views` de la sala |
| `rooms/room0.json` | La sala 2400×800 (245 instancias: borde de muros + pilares, jugador, 18 monedas) y su bloque `views` |
| `objects/obj_player.json` | Jugador: movimiento en cuadrícula + la configuración de cámara en el evento create |
| `objects/obj_coin.json` | Coleccionable: destruido al toque del jugador, añade 10 a la puntuación |
| `objects/obj_wall.json` | Muro sólido estático |
| `sprites/` | `spr_player.png`, `spr_wall.png`, `spr_coin.png` + sus metadatos `.json` |
| `CREDITS.txt` | Aviso de licencia de recursos |

## Objetos

| Objeto | Rol | Eventos clave |
|---|---|---|
| `obj_player` | Personaje jugador; movimiento en cuadrícula + activa/configura la cámara | create (`enable_views`, `set_view`), keyboard (down/right/up/left/nokey), collision_with_obj_wall |
| `obj_coin` | Coleccionable con valor de 10 puntos | collision_with_obj_player (`destroy_instance` self), destroy (`set_score` +10) |
| `obj_wall` | Muro sólido estático / límite de fijación de cámara | (ninguno — colisionador pasivo) |

## Recursos

3 sprites (`spr_player`, `spr_wall`, `spr_coin`, cada uno 32×32, un
solo fotograma, colisión precisa a nivel de píxel), 0 sonidos. Los
tres son arte simple de color plano en CC0 generado para esta muestra
— ver `CREDITS.txt`.

## Cosas para modificar

- **Tamaño de sala** (`2400×800` en `rooms/room0.json`) — hazla más
  ancha/alta para desplazar más lejos; la cámara se fija a lo que sea
  el tamaño de la sala.
- **Bordes** (`hborder` 240 / `vborder` 180 en la acción `set_view`
  *y* el bloque `views` de la sala) — bordes más pequeños dejan al
  jugador acercarse más al borde antes de que la cámara se mueva;
  más grandes lo mantienen más centrado.
- **Velocidad de desplazamiento** — `hspeed`/`vspeed` son `-1`
  (seguimiento instantáneo). Fíjalos a un valor positivo de píxeles
  por paso para una cámara que sigue con retraso, suavizada.
- **Monedas** — añade/quita instancias `obj_coin` en `rooms/room0.json`.

## Estado de la exportación

- **Escritorio (pygame):** el destino de referencia — verificado por
  `tests/test_views_1_sample.py`, que carga esta muestra, ejecuta el
  evento create del jugador, y verifica que la cámara se desplace y
  se fije mientras el jugador recorre todo el ancho.
- **Web (HTML5):** el `engine.js` exportado lleva la misma cámara de
  8 views (`tests/test_html5_views.py`, verificado con Chromium
  durante el desarrollo); tanto la configuración `views` de esta
  muestra como el `set_view` del evento create se transfieren
  correctamente en la exportación.
- **Móvil (Kivy/Android):** la escena exportada renderiza toda la
  sala en un Fbo y copia la región visible de cada view en su puerto
  de pantalla, con la ventana del sistema dimensionada según la view
  (no la sala) así la cámara muestra una verdadera porción con
  desplazamiento y soporta múltiples viewports
  (`tests/test_kivy_views.py`). Las acciones
  `enable_views`/`set_view` se emiten, así que la reconfiguración de
  cámara en tiempo de ejecución también funciona. *Una limitación
  residual:* el destino de renderizado multi-view se construye
  cuando la sala se crea, así que una sala debe tener
  `views_enabled` en su configuración (como hace esta muestra) para
  que la cámara renderice — activar las views solo mediante un
  `enable_views` en tiempo de ejecución en una sala que empezó sin
  ellas no lo adaptará retroactivamente en Kivy.
- El acuerdo entre destinos sobre la matemática de desplazamiento está
  fijado por `tests/test_views_export_parity.py`.

Expuesto en la pestaña Welcome del IDE como "Views — Level 1"
(`widgets/welcome_tab.py`).
