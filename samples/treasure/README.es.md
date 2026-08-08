# Treasure

Una persecución de laberinto al estilo Pac-Man: el **explorador**
recorre un laberinto amurallado recolectando **puntos de tesoro**,
perseguido por **monstruos** que eligen una nueva dirección en cada
cruce. Toma una **píldora de poder** (`pil`) y las tornas se
invierten — cada monstruo se vuelve **asustado** y puede ser comido
por puntos de bonificación hasta que el efecto se desvanece. Este es
un proyecto pygm2 nativo importado desde `treasure.gmk` (GameMaker
8.x); el proyecto en sí está escrito/guardado en el formato JSON
propio de pygm2.

**Dónde encaja:** `treasure` se sitúa junto a la familia `maze_*` —
construido con GameObjects + acciones integradas y el editor visual
de eventos — pero añade un **script a nivel de proyecto**
(`adapt_direction`, la IA del monstruo en los cruces) y un ciclo de
estados al estilo GM de **"persecución / power-up / huida"** a través
de sus objetos. Era una de las dos muestras retiradas en rc.12 por
errores de importación GMK y **se volvió a añadir tras el
endurecimiento del importador** (16/07/2026); ver
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
y [`../../docs/treasure_testing_pass.md`](../../docs/treasure_testing_pass.md).

**Sonido y música:** se incluyen 6 efectos de sonido (recolección,
píldora de poder, comer-monstruo, muerte, …). Una pista heredada de
la era GM8 (`music`) está en un formato que pygame no puede cargar y
se omite en tiempo de ejecución — igual que la música de fondo de las
otras muestras de laberinto; el juego no se ve afectado.

## Cómo se juega

- Las **teclas de flecha** mueven al explorador a través del
  laberinto; los muros bloquean el movimiento.
- Recolecta cada **punto de tesoro** para completar el nivel (4 salas en total).
- Los **monstruos** te persiguen; tocar uno normalmente cuesta una vida.
- Toma una **píldora de poder** y los monstruos se vuelven
  **asustados** (su sprite cambia) durante algunos segundos — toca
  entonces a un monstruo asustado para **comerlo** (+puntos; se
  teletransporta de vuelta a su inicio como un monstruo normal). El
  efecto se desvanece tras un temporizador.

## La IA del monstruo (script `adapt_direction`)

Cada monstruo llama al script de proyecto `adapt_direction` desde sus
eventos step/colisión. Es Python real de pygm2 — en un posible cruce
considera aleatoriamente girar, comprobando
`game.check_collision_at_position(...)` en busca de un muro antes de
comprometerse, así los monstruos vagan por el laberinto en lugar de
correr en línea recta. Abre el recurso **Scripts** para leerlo; la
acción `execute_script` en los eventos del monstruo muestra dónde se llama.

## Estructura del proyecto

| Archivo | Propósito |
|---|---|
| `project.json` | Manifiesto — configuración de ventana/sala, recursos incrustados, el script `adapt_direction`, y el orden de salas |
| `rooms/room0..3.json` | Los cuatro niveles de laberinto (instancias por sala) |
| `objects/*.json` | Las 7 definiciones de objetos (fuente de verdad; fusionadas sobre las copias incrustadas al cargar) |
| `sprites/` | 10 sprites PNG + metadatos `.json` |
| `sounds/` | 6 efectos de sonido |
| `backgrounds/` | 1 fondo |
| `CREDITS.txt` | Aviso de licencia de recursos |

## Objetos

| Objeto | Rol |
|---|---|
| `explorer` | Personaje del jugador; recolecta tesoros, come monstruos asustados, muere al contacto con los normales |
| `monster` | Perseguidor; vaga vía `adapt_direction`; se transforma en `scared` con una píldora de poder |
| `scared` | Un monstruo en su estado de huida; comestible; vuelve a `monster` tras un temporizador |
| `pil` | Píldora de poder — asusta a cada monstruo al recogerla |
| `point` | Tesoro para recolectar |
| `bonus` | Recolectable extra |
| `wall` | Muro sólido estático del laberinto |

## Recursos

10 sprites, 6 sonidos, 1 fondo — todos importados desde
`treasure.gmk`. Ver `CREDITS.txt` y
[`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md) para la procedencia.

## Cosas para modificar

- **Duración del susto** — la alarma de la píldora de poder es `160`
  pasos en el evento `collision_with_pil` de `explorer`; auméntala
  para una fase de huida más larga.
- **Probabilidad de giro del monstruo** — las pruebas
  `random.random() * 3 < 1` en el script `adapt_direction` fijan con
  qué frecuencia giran los monstruos en un cruce.
- **Valores de puntuación** — los puntos de tesoro y de comer-monstruo
  son acciones `set_score` (relativas) en los respectivos eventos de colisión.

## Estado de la exportación

Cubierto por la suite de smoke-tests sin interfaz gráfica
(`tools/smoke_run_samples.py`, que lista `treasure`) y la suite de
regresión de importación (`tests/test_gmk_treasure_maze4_import.py` +
`tests/test_gmk_applies_to.py`). Verificado en una prueba manual
durante el endurecimiento del importador de julio 2026 (ver el
documento de prueba). Expuesto en la pestaña Welcome como **"Treasure"**.

## Regeneración desde el `.gmk` original

El archivo hermano `../treasure.gmk` es la fuente GameMaker 8.x. Para regenerar:

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/treasure.gmk', '/tmp/treasure_reimport')"
```

Una importación nueva es fiel al juego original a partir del
endurecimiento del importador de julio 2026 (sin correcciones
manuales aplicadas a esta muestra).
