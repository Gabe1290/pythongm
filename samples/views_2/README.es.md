# Views — Nivel 2

Una demo de **cooperativo a pantalla dividida**: la sala 2400×800 se
muestra como dos cámaras lado a lado en una sola ventana 800×600. La
**mitad izquierda** (view 0) sigue al **jugador 1** (naranja, teclas
de flecha); la **mitad derecha** (view 1) sigue al **jugador 2**
(verde azulado, WASD). Cada jugador explora la sala compartida en su
propio carril y recolecta monedas — ves a ambos a la vez.

**Dónde encaja:** el segundo nivel de la cuarta familia de muestras.
`views_1` introducía una única cámara con desplazamiento; `views_2`
introduce **múltiples viewports a la vez** — la otra capacidad
principal de las views de GameMaker. Ver
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para la progresión completa. El movimiento reutiliza el idioma de
cuadrícula de `maze_1`/`views_1`.

**Sonido y música:** ninguno — no se incluyen archivos de sonido con esta muestra.

## Cómo se juega

- **Jugador 1 (naranja):** teclas de flecha — se mueve en la view **izquierda**.
- **Jugador 2 (verde azulado):** `W` `A` `S` `D` — se mueve en la view **derecha**.
- Ambos se mueven una celda de cuadrícula (32px) a la vez; los muros
  (`obj_wall`) son sólidos. Un divisor central con aberturas separa
  los dos carriles.
- **Objetivo:** recolecta las 18 monedas (`obj_coin`) — cualquiera de
  los dos jugadores puede tomar cualquier moneda; cada una vale 10
  puntos (mostrados en el título de la ventana).

## Por qué los dos jugadores se detienen independientemente (una trampa real)

El movimiento en cuadrícula normalmente se detiene en el evento
`nokey` (se dispara cuando *ninguna* tecla está presionada). Pero el
estado de las teclas se rastrea globalmente en todas las instancias,
así que con dos jugadores `nokey` solo se dispara cuando **ambos**
sueltan todo — el jugador 2 seguiría deslizándose mientras el jugador
1 mantiene presionada una tecla. Así que cada jugador en cambio se
detiene vía **`keyboard_release`** para **sus propias** teclas
(flechas para J1, WASD para J2), que se dispara por tecla y por
objeto. Esa es la diferencia respecto al jugador único de `views_1`,
que puede usar `nokey` con seguridad.

## Cómo está configurada la pantalla dividida

Un controlador invisible, `obj_camera`, configura ambas views en su
evento **create** (acciones registradas `enable_views` + dos
`set_view`), y la misma configuración está incrustada en el bloque
`views` de la sala para corrección en el fotograma 0 en la exportación:

- **view 0** — `view`/`port` `400×600`, `port_x` 0 (mitad izquierda),
  `follow` `obj_player1`.
- **view 1** — `view`/`port` `400×600`, `port_x` 400 (mitad derecha),
  `follow` `obj_player2`.

Ambas views son **1:1** (tamaño de view == tamaño de puerto) y se
dividen **izquierda/derecha** (`port_y` 0, altura completa). Eso
importa para la consistencia entre destinos: escritorio y HTML5
renderizan cada view 1:1 (recortan + desplazan, **no** escalan una
view a su puerto), y una división izquierda/derecha evita el volteo
de `port_y` entre Kivy (y-arriba) y escritorio/HTML5 (y-abajo). Un
minimapa alejado (view más grande que su puerto) deliberadamente
**no** se usa aquí — solo escalaría correctamente en Kivy.

## Estructura del proyecto

| Archivo | Propósito |
|---|---|
| `project.json` | Manifiesto — configuración de ventana/sala, recursos incrustados, y la configuración `views` de dos views |
| `rooms/room0.json` | La sala 2400×800 (284 instancias: cámara, muros, 2 jugadores, 18 monedas) + su bloque `views` |
| `objects/obj_camera.json` | Controlador invisible: create-evento `enable_views` + dos `set_view` |
| `objects/obj_player1.json` | Jugador 1 (teclas de flecha); movimiento en cuadrícula + parada `keyboard_release` |
| `objects/obj_player2.json` | Jugador 2 (WASD); movimiento en cuadrícula + parada `keyboard_release` |
| `objects/obj_coin.json` | Coleccionable — destruido por ambos jugadores, añade 10 |
| `objects/obj_wall.json` | Muro sólido estático |
| `sprites/` | `spr_player1.png` (naranja), `spr_player2.png` (verde azulado), `spr_wall.png`, `spr_coin.png` + metadatos `.json` |
| `CREDITS.txt` | Aviso de licencia de recursos |

## Objetos

| Objeto | Rol | Eventos clave |
|---|---|---|
| `obj_camera` | Controlador invisible; activa + configura ambas views | create (`enable_views`, 2× `set_view`) |
| `obj_player1` | Jugador de la view izquierda (flechas) | keyboard (up/down/left/right/nokey), keyboard_release (por tecla), collision_with_obj_wall |
| `obj_player2` | Jugador de la view derecha (WASD) | keyboard (w/a/s/d/nokey), keyboard_release (por tecla), collision_with_obj_wall |
| `obj_coin` | Coleccionable con valor de 10 | collision_with_obj_player1, collision_with_obj_player2, destroy (`set_score` +10) |
| `obj_wall` | Muro sólido estático / límite de cámara | (ninguno — colisionador pasivo) |

## Recursos

4 sprites (`spr_player1`, `spr_player2`, `spr_wall`, `spr_coin`, cada
uno 32×32, un solo fotograma, preciso a nivel de píxel), 0 sonidos.
Todo arte de color plano en CC0 generado para esta muestra — ver `CREDITS.txt`.

## Cosas para modificar

- **Dirección de división** — esto usa una división
  izquierda/derecha (`port_x` 0 y 400, `port_y` 0, altura completa).
  Una división arriba/abajo pondría las mitades en `port_y`
  diferentes; nota que eso se renderiza en una posición vertical
  diferente en Kivy (y-arriba) respecto a escritorio/HTML5 (y-abajo),
  así que izquierda/derecha es la elección portable.
- **Ancho de view** — cada view tiene `400` de ancho (la mitad de la
  ventana). Ensancha la ventana o estrecha las views para cambiar
  cuánto de la sala ve cada jugador.
- **Bordes** — `hborder` 120 / `vborder` 150 fijan la zona muerta de
  cada cámara.

## Estado de la exportación

- **Escritorio (pygame):** la referencia —
  `tests/test_views_2_sample.py` carga la muestra, ejecuta el evento
  create de `obj_camera`, y verifica que las dos cámaras se
  desplacen **independientemente** (mover un jugador no mueve la
  view del otro) y se fijen en el borde de la sala, además de la
  puntuación de monedas y la parada `keyboard_release` por jugador.
- **Web (HTML5):** `engine.js` renderiza cada view visible (recorte
  por view + traslación 1:1); la configuración de dos views se
  transfiere correctamente en la exportación.
- **Móvil (Kivy/Android):** el exportador renderiza la sala en un Fbo
  y copia la región visible de cada view en su puerto de pantalla
  (`tests/test_kivy_views.py` cubre el renderizado multi-view). Las
  acciones `enable_views`/`set_view` se emiten, así que la
  configuración de dos views funciona tanto desde el evento create de
  `obj_camera` como desde la configuración incrustada en la sala.
  Limitación residual (como en `views_1`): el destino de renderizado
  se construye al crear la sala, así que `views_enabled` debe estar
  en la configuración de la sala (lo está aquí) para que la cámara
  renderice en Kivy.
- El acuerdo entre destinos sobre la matemática de desplazamiento está
  fijado por `tests/test_views_export_parity.py`.

Expuesto en la pestaña Welcome del IDE como "Views — Level 2" (`widgets/welcome_tab.py`).
