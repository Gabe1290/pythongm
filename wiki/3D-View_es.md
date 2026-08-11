# Vista 3D (renderizado en primera persona con raycast)

*[Inicio](Home_es) | [Referencia completa de acciones](Full-Action-Reference_es) | [Extensiones](Extensions_es)*

---

PyGameMaker puede renderizar una sala como una **vista 3D en primera persona al
estilo Doom/Wolfenstein** en lugar de la habitual vista cenital — muros como franjas
verticales, un suelo y un techo con color o textura, un cielo panorámico opcional y
sprites "cartel" (billboard) para objetos y monstruos. La *lógica* del juego
(movimiento, colisiones, eventos) no cambia; solo cambia **cómo** se dibuja la sala.

Esto lo proporciona la **extensión 2.5D Raycast** integrada (la función
[Vista 3D](Extensions_es)), activada de forma predeterminada. Se exporta a los tres
destinos — ordenador, HTML5 y Kivy/Android — así que un juego en primera persona
funciona igual en todas partes.

Los ejemplos incluidos **`raycast_1`–`raycast_4`** son juegos completos y jugables
(un laberinto sencillo, un juego de dos niveles con objetos y un monstruo, una
variante con salud y botiquines y una demostración de barra de estado al estilo
DOOM).

---

## Cómo funciona

- Una sala pasa a primera persona cuando un objeto ejecuta la acción **Habilitar
  vista Raycast** (normalmente en su evento Crear). Ese objeto es la **cámara** de
  forma predeterminada — su posición es el punto de vista y su `facing_angle`
  (ángulo de mirada) es la dirección de la mirada.
- **Los muros son tus instancias sólidas.** El renderizador deriva finos *bordes* de
  muro de cada objeto sólido de la sala, en una cuadrícula cuyo tamaño es el
  parámetro `cell_size` de la acción (32 de forma predeterminada — el tamaño que usan
  todos los ejemplos `maze_*`/`raycast_*`). Un objeto sólido con sprite de muro
  texturiza el muro; de lo contrario se usa un color `wall_color` uniforme.
- **La cámara gira** cambiando `facing_angle` (ver **Establecer ángulo de mirada**) y
  se mueve con las acciones de movimiento habituales (p. ej. `set_direction_speed`
  con `direction = "facing_angle"` para caminar hacia adelante).
- **Las instancias no sólidas con sprite** (objetivos, objetos, monstruos) se dibujan
  como **carteles** orientados a la cámara, correctamente ocultados por los muros.

---

## Las acciones (categoría **Vista 3D**)

| Acción | Qué hace |
|--------|----------|
| **Habilitar vista Raycast** (`enable_raycast_view`) | Cambia la sala actual a la vista en primera persona (o vuelve) y configura la cámara: `camera_object`, `fov`, `render_distance`, `cell_size`, colores y texturas de muro/suelo/techo, una `sky_texture` opcional y `viewport_height` (una barra al estilo DOOM). |
| **Establecer ángulo de mirada** (`set_facing_angle`) | Gira la cámara. Ángulo en grados GameMaker (0 = derecha, 90 = arriba); `relative` suma al ángulo actual. |
| **Dibujar minimapa** (`draw_minimap`) | Dibuja un minimapa orientado al norte de los muros de la sala con un marcador "estás aquí". Una acción de HUD — ponla en un evento Dibujar. |
| **Dibujar HUD DOOM** (`draw_doom_hud`) | Dibuja una barra de estado inferior al estilo DOOM: barra de salud + número, un rostro que reacciona a la salud, puntuación, vidas y un contador de objetivo. Se combina con `viewport_height` de `enable_raycast_view`. |

Ver la [Referencia completa de acciones](Full-Action-Reference-3D-View-Actions_es) para
todos los parámetros.

---

## Un controlador mínimo en primera persona

En el objeto jugador:

- **Crear:** `Habilitar vista Raycast` (deja `camera_object` vacío para que el
  jugador *sea* la cámara).
- **Teclado Izquierda / Derecha:** `Establecer ángulo de mirada` con `relative`
  activo (p. ej. ±3°).
- **Teclado Arriba:** `Establecer dirección y velocidad` con
  `direction = facing_angle` y una pequeña velocidad para caminar hacia adelante.

Construye la sala con objetos-muro sólidos en una cuadrícula de 32 píxeles, igual que
los ejemplos `maze_*` — el raycaster convierte esos muros en corredores 3D.

---

## Notas y límites

- Las acciones de HUD (`draw_minimap`, `draw_doom_hud` y las habituales `draw_score`
  / `draw_lives` / `draw_text`) se superponen **encima** de la imagen en primera
  persona, en coordenadas de pantalla.
- Los muros son estáticos para la pasada en primera persona — los muros
  creados/destruidos después de cargar la sala no remodelan la geometría 3D.
- Si la extensión 2.5D Raycast está **desactivada**, una sala que habilita la vista
  simplemente se renderiza cenital y el IDE te avisa al cargar — ver
  [Extensiones](Extensions_es).

---

## Véase también

- [Extensiones](Extensions_es) — cómo se entrega la Vista 3D y cómo desactivarla
- [Referencia completa de acciones](Full-Action-Reference-3D-View-Actions_es) — las cuatro acciones en detalle
- [Editor de salas](Editor_Salas_es) — colocar los objetos-muro con los que se construye la vista
