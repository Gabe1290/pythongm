# Laberinto — Nivel 4

La muestra de laberinto más grande: **21 salas** de rompecabezas de
laberinto en cuadrícula con **teselas de cinta transportadora**, tres
tipos de **monstruo**, **bombas/explosiones** que vuelan muros, un
**anillo de poder** que asusta a los monstruos, y coleccionables
(diamantes, anillos, corazones). Un proyecto pygm2 nativo importado
desde `maze_4.gmk` (GameMaker 8.x), escrito/guardado en el formato
JSON propio de pygm2.

**Dónde encaja:** el cuarto nivel `maze_*` y el mecánicamente más
rico — superpone el movimiento por cinta transportadora, múltiples
tipos de enemigos, un ciclo de power-up de asustar/comer, y una bomba
que destruye muros sobre el movimiento básico en cuadrícula de
`maze_1..3`. Se retiró en rc.12 por errores de importación GMK y **se
volvió a añadir tras el endurecimiento del importador** (16/07/2026);
ver
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
y [`../../docs/maze_4_testing_pass.md`](../../docs/maze_4_testing_pass.md).

**Sonido y música:** se incluyen 10 efectos de sonido. Una pista
heredada de la era GM8 (`sound_background`) está en un formato que
pygame no puede cargar y se omite en tiempo de ejecución (igual que
maze_2/maze_3); el juego no se ve afectado.

## Cómo se juega

- Las **teclas de flecha** mueven al jugador una celda de cuadrícula a la vez; los muros bloquean el movimiento.
- Las **teselas de cinta transportadora** (flechas arriba/abajo/
  izquierda/derecha en el suelo) llevan automáticamente al jugador en
  su dirección mientras está sobre ellas.
- Los **monstruos** vienen en tres tipos (`monster_all` vaga
  libremente; `monster_ud` patrulla verticalmente; `monster_lr`
  horizontalmente) — tocar uno cuesta una vida y reinicia la sala.
- Toma un **anillo** y cada monstruo se vuelve **asustado** (el sprite
  cambia, se congelan) durante ~10 segundos — tócalo entonces para
  comerlo por puntos; vuelven a la normalidad cuando el temporizador se agota.
- Las **bombas** explotan en una onda que **destruye los muros
  circundantes** — usadas para abrir secciones de otro modo selladas.
- Recolecta **diamantes/anillos/corazones**; alcanza el **objetivo**
  para avanzar. El HUD (puntuación + vidas) se dibuja a lo largo de
  abajo por `controller_main`.

## Una nota sobre el parche manual (documentación honesta)

El movimiento de pygm2 *se desliza hasta el contacto* con un muro,
mientras que GameMaker 8 *revierte* un movimiento bloqueado a la
posición previa al movimiento — el comportamiento de GM mantenía al
jugador ajustado a la cuadrícula gratis. Sin esto, presionar contra un
muro al ras dejaba al jugador a unos pocos píxeles de la cuadrícula
de 32, y las comprobaciones de movimiento en cuadrícula/cinta
transportadora entonces se atascaban. Así que `obj_person` lleva un
**parche manual de jugabilidad** deliberado: `snap_to_grid(32)` en
sus eventos de colisión `wall_corner`/`wall_horizontal`/`wall_vertical`.
Esto refleja el mismo parche distribuido en `maze_1` y es una
corrección, no un cambio de fidelidad — una importación nueva desde
el `.gmk` no lo incluirá (ver abajo).

## Estructura del proyecto

| Archivo | Propósito |
|---|---|
| `project.json` | Manifiesto — configuración de ventana/sala, recursos incrustados, y orden de salas |
| `rooms/*.json` | 21 salas; orden de juego `room_start` luego en orden descendente (`room14`, `room13`, …) — el orden propio del juego original, importado fielmente |
| `objects/*.json` | 24 definiciones de objetos (fuente de verdad; fusionadas sobre las copias incrustadas al cargar) |
| `sprites/` | 24 sprites PNG + metadatos `.json` |
| `sounds/` | 10 efectos de sonido |
| `backgrounds/` | 2 fondos |
| `CREDITS.txt` | Aviso de licencia de recursos |

## Objetos (24)

Jugador/HUD: `obj_person`, `controller_main` (dibuja
puntuación+vidas), `controller_start`.
Muros: `wall_horizontal`, `wall_vertical`, `wall_corner`, `block`.
Enemigos: `monster_all`, `monster_ud`, `monster_lr`.
Power-ups / objetos: `ring` (asusta), `bomb` + `explosion` (destruyen
muros), `obj_diamond`, `heart`, `bonus`, `obj_door`, `obj_goal`,
`trigger`, `hole`.
Teselas de cinta transportadora: `move_up`, `move_down`, `move_left`, `move_right`.

## Recursos

24 sprites, 10 sonidos, 2 fondos, 1 fuente — todos importados desde
`maze_4.gmk`. Ver `CREDITS.txt` y
[`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md) para la procedencia.

## Cosas para modificar

- **Velocidad de cinta/jugador** — las cintas se mueven a velocidad
  `8`; el movimiento en cuadrícula por teclado a `4` (parámetros por
  acción en `obj_person`).
- **Duración del susto** — el `set_alarm` del anillo es `300` pasos en `monster_all`.
- **Orden de salas** — las salas se reproducen en el orden de claves
  del diccionario de salas de `project.json`; reordénalas en el IDE
  (arrastrar en el árbol de recursos) y Test Game lo seguirá.

## Estado de la exportación

Cubierto por la suite de smoke-tests sin interfaz gráfica
(`tools/smoke_run_samples.py`, que lista `maze_4`) y la suite de
regresión de importación (`tests/test_gmk_treasure_maze4_import.py`).
Verificado en una prueba manual durante el endurecimiento del
importador de julio 2026 (ver el documento de prueba). Expuesto en la
pestaña Welcome como **"Maze — Level 4"**.

## Regeneración desde el `.gmk` original

El archivo hermano `../maze_4.gmk` es la fuente GameMaker 8.x:

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/maze_4.gmk', '/tmp/maze_4_reimport')"
```

Una importación nueva es fiel al juego original, **menos** el parche
manual `snap_to_grid` de muros descrito arriba — vuelve a aplicarlo
(añade `snap_to_grid` con grid_size 32 a los tres eventos de colisión
de muro de `obj_person`) después de regenerar.
