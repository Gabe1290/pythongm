# Platform — Nivel 3

Un plataformas de desplazamiento lateral importado desde GameMaker
8.x (`samples/plateforme_3.gmk`). Es por mucho el más grande de las
tres muestras de plataformas: 2 objetos (plateforme_1) → 4 objetos
(plateforme_2) → **15 objetos** aquí, añadiendo monstruos terrestres y
voladores en patrulla (con muerte al pisotear y variantes de
cadáver/salpicadura generadas en tiempo de ejecución), un peligro de
muerte instantánea invisible, dos tipos de coleccionables, y un
objeto de salida que avanza a la siguiente sala o muestra la tabla de
puntuaciones máximas y reinicia.

**Dónde encaja:** parte de la familia `plateforme_*` — como
`plateforme_2`, usa un **fondo en teselas** (125 fragmentos de
teselas bajo los objetos de ladrillo sólido, más la imagen en
degradado `fond_degrade`), el paso que esta familia añade más allá de
`maze_*`. Ver
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
para la progresión completa.

**Sonido y música:** 4 archivos de sonido, realmente conectados: 7
puntos de llamada `play_sound` para `son_bonus` (recolección),
`son_monstre_mort` (muerte por pisotón), `son_personnage_mort`
(muerte del jugador), y `son_niveaufini` (nivel completado).

## Cómo se juega

- **Flecha izquierda/derecha** — mueve a Pingus (`obj_pingus`) izquierda/derecha.
- **Flecha arriba** — salto, pero solo mientras está parado sobre algo
  sólido (comprobado un píxel debajo del jugador).
- **Objetivo** — recolecta los `obj_bonus` (+5 de puntuación) y los
  `obj_power` (+20 de puntuación) mientras atraviesas `niveau_01` para
  alcanzar `obj_sortie`; tocarlo reproduce una melodía y o bien avanza
  a una siguiente sala (ninguna existe en esta muestra, así que recae
  en la rama de tabla-de-puntuaciones/reinicio) o muestra la tabla de
  puntuaciones máximas y reinicia el juego.
- **Monstruos** — aterrizar encima de un `obj_monstre` o
  `obj_monstre_volant` (`vspeed > 0` y por encima del monstruo) lo
  mata y otorga 50 puntos; golpear uno de lado o por debajo cuesta una
  vida y reinicia la sala. Nota: la colisión con `obj_monstre_volant`
  no tiene efecto (el monstruo volador no puede herir ni ser herido)
  hasta que se haya recogido `obj_power` — ver Cosas para modificar.
- **Condición de derrota** — tocar `obj_mortel` (una zona de muerte
  instantánea invisible) o un monstruo de la manera incorrecta cuesta
  una vida y reinicia la sala; quedarse sin vidas (`no_more_lives`)
  muestra la tabla de puntuaciones máximas y reinicia todo el juego.
  Vidas iniciales: 3 (configuración de `project.json`).

## Estructura del proyecto

| Archivo | Propósito |
| --- | --- |
| `project.json` | Manifiesto del proyecto — configuración de ventana/sala, copias de recursos incrustadas. |
| `rooms/niveau_01.json` | La única sala: 800×640, 194 instancias + 125 teselas de fondo. Fuente de verdad para el contenido de la sala (la lista `instances` incrustada de `project.json` está vacía, mismo patrón que plateforme_2). |
| `objects/*.json` | Archivos colaterales por objeto para los 15 objetos; idénticos a las copias incrustadas en `project.json` a esta fecha (verificado byte a byte, a diferencia del archivo de sala de plateforme_2). |
| `sprites/` | 18 recursos sprite (tiras de caminata/vuelo, sprites de muerte, bloques de plataforma, coleccionables, salida, marcador). |
| `sounds/` | 4 efectos de sonido (muerte de monstruo, muerte del jugador, recolección de bonus, nivel completado). |
| `backgrounds/` | Conjunto de teselas de nieve (`tuiles_neige.png`, fuente automática para las 125 teselas de la sala) y un degradado vertical (`fond_degrade.png`) como fondo de sala. |
| `CREDITS.txt` | Aviso de licencia para el arte de sprites/fondo (ver Recursos abajo). |

## Objetos

15 objetos, agrupados por rol. Se muestran los recuentos de
colocación en la sala (de 194 instancias) donde el objeto aparece en
`niveau_01`; los objetos "generados en tiempo de ejecución" solo
aparecen mediante `change_instance` durante el juego.

| Objeto | Rol | Eventos clave |
| --- | --- | --- |
| `obj_pingus` | Jugador — movimiento, salto, gravedad, todo el manejo de colisiones/derrota/victoria | create, step, keyboard (left/right/up), keyboard_release, collision_with_obj_brique/obj_monstre/obj_monstre_volant/obj_mortel/obj_bonus/obj_power/obj_sortie/obj_marqueur, game_start, no_more_lives |
| `obj_brique` | Bloque de plataforma sólida base, 32×32 (109 colocados) | ninguno (solo bandera sólida) |
| `obj_brique_h` | Variante ancha de plataforma, 32×16, hija de `obj_brique` (15 colocados) | ninguno |
| `obj_brique_v` | Variante estrecha de plataforma, 16×32, hija de `obj_brique`; definida pero no colocada en `niveau_01` | ninguno |
| `obj_brique_c` | Pequeña variante de plataforma, 16×16, hija de `obj_brique` (1 colocado) | ninguno |
| `obj_monstre` | Monstruo terrestre — patrulla izquierda/derecha, invierte al contacto con un muro (3 colocados) | create, collision_with_obj_brique |
| `obj_monstre_mort` | Cadáver de monstruo generado en tiempo de ejecución tras una muerte por pisotón; hereda `obj_brique` (se convierte en un escalón sólido) | create |
| `obj_monstre_volant` | Monstruo volador — patrulla hacia la derecha, rebota en los muros (2 colocados) | create, collision_with_obj_brique |
| `obj_monstre_volant_mort` | Cadáver de monstruo volador generado en tiempo de ejecución; cae con gravedad limitada, aterriza sobre plataformas/marcadores | step, collision_with_obj_brique, collision_with_obj_marqueur |
| `obj_mortel` | Zona de peligro de muerte instantánea invisible (4 colocadas) | ninguno (manejado desde el evento de colisión de `obj_pingus`) |
| `obj_splat` | Animación de muerte del jugador generada en tiempo de ejecución, reinicia la sala al final de la animación | create, animation_end |
| `obj_bonus` | Coleccionable menor, +5 de puntuación, fotograma de reposo aleatorio (52 colocados) | create |
| `obj_power` | Coleccionable mayor, +20 de puntuación; también determina si los monstruos voladores pueden herir/ser matados (1 colocado) | create |
| `obj_sortie` | Salida del nivel — reproduce una melodía, luego siguiente sala o tabla de puntuaciones + reinicio (1 colocada) | ninguno (manejado desde el evento de colisión de `obj_pingus`) |
| `obj_marqueur` | Marcador de diseño de sala invisible y no sólido; las colisiones no tienen efecto explícitamente (5 colocados) | ninguno |

## Recursos

18 sprites, 4 sonidos, 2 fondos. El arte de sprites/fondos está
adaptado del proyecto Pingus (GPL-3.0-or-later) — ver `CREDITS.txt`
para la atribución completa y los términos de licencia; este README
no reafirma ni extiende esas declaraciones.

## Cosas para modificar

- La prueba de pisotón entre `obj_pingus` y
  `obj_monstre`/`obj_monstre_volant` solía ser
  `vspeed > 0 and y < other.y+8`, que una caída rápida podía superar
  (la ventana de 8px se comprobaba contra la posición *tras el
  movimiento*) y costaba una vida en lo que parecía un pisotón
  limpio. Ahora es `vspeed > 0 and y - vspeed < other.y+8`, que
  comprueba la ventana contra la posición previa al movimiento en su lugar.
- El coleccionable `obj_power` condiciona silenciosamente toda
  interacción con `obj_monstre_volant` (mediante un
  `if_object_exists(obj_power, not_flag=true)` alrededor de la
  lógica de pisotón/muerte en `obj_pingus`) — valdría la pena
  hacerlo visible para los jugadores (p. ej. un cambio de sprite/paleta)
  en lugar de una regla invisible.
- La velocidad horizontal del jugador es un `hspeed = 4` fijo; el
  impulso de salto es `vspeed = -10`; la gravedad de caída es `0,5`
  con un tope de velocidad terminal en `vspeed = 24`.
- El tamaño de la sala es 800×640 a `room_speed = 30`.

## Estado de la exportación

Esta muestra está listada en la lista `SAMPLES` de
`tools/smoke_run_samples.py`, así que recibe un pase smoke sin
interfaz gráfica (el bucle de juego real ejecutado durante ~180
fotogramas con entrada de teclado inyectada) en cada ejecución de ese
arnés. No se ha hecho ninguna verificación por destino de exportación
específico (Kivy/HTML5) para esta muestra en particular. Está
expuesta en la pestaña Welcome del IDE como "Platform — Level 3"
(`widgets/welcome_tab.py`).
