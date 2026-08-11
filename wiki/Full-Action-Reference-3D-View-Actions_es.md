# Vista 3D

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Dibujar HUD DOOM

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_doom_hud` |
| **Icono** | 🎯 |
| **Categoría** | Vista 3D |

Dibujar una barra de estado inferior al estilo DOOM (barra de salud + número, puntuación, vidas, un contador de objetivo y un icono de rostro que reacciona a la salud) sobre la vista raycast

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Borde izquierdo de la barra, en píxeles de pantalla |
| `y` | Número | `-1` | Borde superior de la barra; un valor negativo la alinea automáticamente al fondo de la ventana, bajo la vista reducida; opcional |
| `width` | Número | `0` | Ancho de la barra (0 = ancho completo de la ventana); opcional |
| `height` | Número | `42` | Altura de la barra; mantenla coherente con la franja viewport_height reservada en enable_raycast_view; opcional |
| `back_color` | Color | `#101010` | Panel de fondo de la barra; opcional |
| `divider_color` | Color | `#505050` | Borde superior y fondo de la barra de salud; opcional |
| `text_color` | Color | `#ffffff` | Color de todo el texto de la barra; opcional |
| `health_label` | Texto | `Health` | opcional |
| `health_bar_width` | Número | `90` | opcional |
| `health_bar_height` | Número | `14` | opcional |
| `bar_color` | Color | `#20c020` | Color de relleno de la barra de salud; opcional |
| `face_sprite` | Sprite | — | Tira horizontal de fotogramas de rostro, el más sano primero (vacío = sin icono de rostro); opcional |
| `face_frames` | Número | `4` | Cuántos fotogramas tiene la tira de rostro; la salud se distribuye uniformemente entre ellos; opcional |
| `score_label` | Texto | `Score: ` | opcional |
| `lives_sprite` | Sprite | — | Sprite dibujado una vez por cada vida restante; opcional |
| `lives_scale` | Número | `1.0` | opcional |
| `objective_value` | Texto | `0` | Expresión mostrada después de la etiqueta de objetivo (asocia tu propia variable de llave/misión); opcional |
| `objective_label` | Texto | `Keys: ` | opcional |

### Dibujar minimapa

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `draw_minimap` |
| **Icono** | 🗺️ |
| **Categoría** | Vista 3D |

Dibujar un minimapa orientado al norte de los muros de la sala raycast, con un marcador que muestra dónde está la cámara y hacia dónde mira

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Borde izquierdo del minimapa, en píxeles de pantalla |
| `y` | Número | `0` | Borde superior del minimapa, en píxeles de pantalla |
| `size` | Número | `120` | Ancho y alto del cuadrado del minimapa, en píxeles; opcional |
| `back_color` | Color | `#101018` | Color del panel detrás del mapa; opcional |
| `wall_color` | Color | `#8080a0` | Color de las líneas de los muros; opcional |
| `player_color` | Color | `#ffd040` | Color del marcador de la cámara y su línea de dirección; opcional |

### Habilitar vista Raycast

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `enable_raycast_view` |
| **Icono** | 🕹️ |
| **Categoría** | Vista 3D |

Renderizar la sala como una vista 3D en primera persona al estilo Doom/Wolfenstein (muros, cielo, suelo) en lugar de la vista cenital

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `enable` | Sí/No | Sí | Activado = vista raycast en primera persona; desactivado = vista cenital normal |
| `camera_object` | Objeto | — | Objeto cuya posición + ángulo de mirada es la cámara (vacío = el objeto que ejecuta esta acción); opcional |
| `fov` | Número | `66` | Campo de visión horizontal en grados; opcional |
| `render_distance` | Número | `20` | Longitud máxima del rayo en celdas de la cuadrícula; opcional |
| `cell_size` | Número | `32` | Tamaño de la celda de la cuadrícula en píxeles (coincide con la cuadrícula de colocación de muros); opcional |
| `columns` | Número | `320` | Columnas de pantalla para raycast (menos = más rápido/más tosco); opcional |
| `wall_color` | Color | `#993333` | Color uniforme de los muros cuando no hay textura de muro; opcional |
| `floor_color` | Color | `#464632` | Color uniforme del suelo cuando no hay textura de suelo; opcional |
| `ceiling_color` | Color | `#87CEEB` | Color uniforme del techo cuando no hay textura de cielo/techo; opcional |
| `wall_texture` | Sprite | — | Sprite para texturizar cada muro (vacío = color uniforme); opcional |
| `sky_texture` | Sprite | — | Sprite para un cielo panorámico sobre el techo (vacío = uniforme); opcional |
| `floor_texture` | Sprite | — | Sprite proyectado sobre el suelo (vacío = color uniforme); opcional |
| `ceiling_texture` | Sprite | — | Sprite proyectado sobre el techo cuando no hay cielo; opcional |
| `wall_textured` | Sí/No | Sí | Desactivado fuerza colores uniformes de muros incluso cuando hay una textura; opcional |
| `floor_cast_res` | Número | `4` | Submuestreo del suelo proyectado (mayor = más rápido + más tosco); opcional |
| `viewport_height` | Número | `0` | Reduce la vista 3D a esta altura en píxeles (letterbox), reservando la franja inferior para una barra de estado al estilo DOOM (0 = altura completa de la ventana, sin cambios); opcional |

### Establecer ángulo de mirada

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_facing_angle` |
| **Icono** | 🧭 |
| **Categoría** | Vista 3D |

Establecer la dirección de mirada de la instancia para una cámara raycast (en primera persona) — independiente de la velocidad de movimiento

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `angle` | Número | `0` | Grados (0=derecha, 90=arriba, 180=izquierda, 270=abajo) |
| `relative` | Sí/No | No | Sumar al ángulo de mirada actual en lugar de reemplazarlo; opcional |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (2)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (20)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
