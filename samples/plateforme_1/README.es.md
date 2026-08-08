# Platform — Nivel 1

Un plataformas de desplazamiento lateral mínimo importado desde
GameMaker 8.x (`samples/plateforme_1.gmk`). La bola controlada por el
jugador (`obj_balle`) escala una única pantalla de plataformas de
ladrillo (`obj_brique`) usando sondas `if_collision` al estilo
GameMaker para moverse en pasos de 4px/fotograma y caer bajo gravedad
solo cuando no hay nada sólido directamente debajo de ella — un
esquema de movimiento AABB escrito a mano en lugar de la física
integrada del motor.

**Dónde encaja:** parte de la familia `plateforme_*`, pero en su
mínima expresión — a diferencia de `plateforme_2`/`plateforme_3`,
este nivel no tiene imagen de fondo y **ningún fondo en teselas** (el
array `tiles` de la sala está vacío); está construido solo con
GameObjects + sprites, igual que `maze_1`. Ver
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para cómo la familia entera se compara con `maze_*` y `match3_*`.

**Sonido y música:** ninguno — no se incluyen archivos de sonido con esta muestra.

## Cómo se juega

- **Flecha izquierda/derecha** — mueve la bola 4px por pulsación de
  tecla, bloqueada por ladrillos sólidos.
- **Flecha arriba** — salto (fija `vspeed` a -10), solo mientras se
  está parado sobre un ladrillo sólido.
- No hay un objeto objetivo explícito, moneda, o salida en este nivel
  — es un laberinto vertical de ladrillos para escalar. Tampoco hay un
  objeto monstruo/peligro, así que no hay condición de derrota; es
  exploración libre de la mecánica de colisión/gravedad.

## Estructura del proyecto

| Archivo | Propósito |
|---|---|
| `project.json` | Manifiesto del proyecto — configuración de ventana/sala, copias de recursos incrustadas (ver nota abajo). |
| `rooms/niveau_01.json` | La única sala: 800×640, 120 instancias (mayormente muros/plataformas `obj_brique` más una `obj_balle`). |
| `objects/obj_balle.json` | Lógica de la bola del jugador (movimiento, gravedad, salto). |
| `objects/obj_brique.json` | Ladrillo sólido estático, sin eventos. |
| `sprites/` | `spr_balle.png` (bola) y `spr_32x32_noir.png` (ladrillo), cada uno con un colateral `.json`. |

`objects/*.json` y `rooms/niveau_01.json` son los archivos colaterales
por recurso actuales; su contenido coincide con lo incrustado en
`project.json` para esta muestra (sin divergencia encontrada), pero
por convención del repositorio los archivos colaterales son la fuente
de verdad si los dos alguna vez discrepan.

## Objetos

| Objeto | Rol | Eventos clave |
|---|---|---|
| `obj_balle` | Bola controlada por el jugador; gravedad, movimiento consciente de colisiones, salto | create (ninguno definido), step, collision_with_obj_brique, keyboard (left, right, up) |
| `obj_brique` | Tesela de plataforma/muro sólida estática | *(ninguno — sin eventos definidos)* |

## Recursos

2 sprites (`spr_balle`, `spr_32x32_noir`), 0 sonidos. Ambos sprites
son obras derivadas del arte del juego Pingus, licenciadas bajo
GPL-3.0-or-later — ver `CREDITS.txt` en esta carpeta para el aviso
completo y los créditos de los artistas originales; no los trates
como cubiertos por la licencia MIT del IDE.

## Cosas para modificar

- Evento step de `obj_balle`: la gravedad es `0,45` px/fotograma², y
  vspeed está limitado a `24` — sube o baja cualquiera de los dos
  para cambiar el peso de la caída y la velocidad terminal.
- El impulso del salto es un `vspeed = -10` fijo (teclado "arriba") —
  mayor magnitud salta más alto.
- El paso de movimiento horizontal es `4` px por pulsación de tecla
  (teclado "izquierda"/"derecha") — pasos más grandes se sienten más
  ágiles pero pueden atravesar huecos delgados.
- La sala es 800×640 con `room_speed: 30`; la disposición de
  ladrillos en `rooms/niveau_01.json` puede reorganizarse libremente
  ya que `obj_brique` no tiene lógica propia.

## Estado de la exportación

Esta muestra está listada en la lista `SAMPLES` de
`tools/smoke_run_samples.py`, así que está cubierta por el arnés de
smoke-tests sin interfaz gráfica (ejecuta el bucle de juego real
durante ~180 fotogramas con entrada de teclado inyectada). No se ha
verificado por separado contra los destinos de exportación Kivy o
Web. Está expuesta en la pestaña Welcome del IDE como
**"Platform — Level 1"** (`widgets/welcome_tab.py`).
