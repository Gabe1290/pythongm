# Instancia

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Cambiar instancia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `change_instance` |
| **Icono** | 🔄 |
| **Categoría** | Instancia |
| **Se aplica a** | self / other / object |

Transformar en otro tipo de objeto

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Nuevo tipo de objeto |
| `perform_events` | Sí/No | Sí | Ejecutar los eventos destruir/crear |

### Crear instancia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_instance` |
| **Icono** | ✨ |
| **Categoría** | Instancia |

Crear una nueva instancia

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Objeto a crear |
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `relative` | Sí/No | No | Posición relativa a la instancia actual |

### Crear instancia en movimiento

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_moving_instance` |
| **Icono** | ✨➡️ |
| **Categoría** | Instancia |

Crear una instancia e iniciarla en una dirección

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Objeto a crear |
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `speed` | Número | `0` | Magnitud de velocidad inicial |
| `direction` | Número | `0` | Dirección inicial en grados |

### Crear instancia aleatoria

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_random_instance` |
| **Icono** | 🎲 |
| **Categoría** | Instancia |

Crear uno de varios tipos de objeto elegido al azar

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posición X |
| `y` | Número | `0` | Posición Y |
| `object1` | Objeto | — | Primer objeto candidato; opcional |
| `object2` | Objeto | — | Segundo objeto candidato; opcional |
| `object3` | Objeto | — | Tercer objeto candidato; opcional |
| `object4` | Objeto | — | Cuarto objeto candidato; opcional |

### Destruir instancia

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `destroy_instance` |
| **Icono** | 💥 |
| **Categoría** | Instancia |
| **Se aplica a** | self / other / object |

Destruir una instancia

*Parámetros:* ninguno

### Destruir en posición

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `destroy_at_position` |
| **Icono** | 💣 |
| **Categoría** | Instancia |

Destruir instancias dentro de un radio de (x, y)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | `all` | Qué tipo de objeto destruir. «all» destruye cada instancia en el radio; «solid» solo las sólidas (p. ej. muros); «non-solid» todo excepto los sólidos.; Opciones: `all`, `solid`, `non-solid` |
| `x` | Texto | `self.x` | Posición X (expresión permitida, p. ej. self.x) |
| `y` | Texto | `self.y` | Posición Y (expresión permitida, p. ej. self.y) |
| `relative` | Sí/No | No | Tratar X/Y como desplazamientos desde la posición de esta instancia en lugar de coordenadas absolutas; opcional |
| `radius` | Número | `32` | Radio en píxeles alrededor de (x, y). Predeterminado 32 = ~una celda de la cuadrícula. |

### Establecer índice de imagen

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_image_index` |
| **Icono** | 🖼️ |
| **Categoría** | Instancia |

Establecer el fotograma de animación actual del sprite de la instancia

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `frame` | Número | `0` | Índice de fotograma |

### Establecer velocidad de imagen

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_image_speed` |
| **Icono** | ⏩ |
| **Categoría** | Instancia |

Establecer la velocidad de reproducción de la animación del sprite de la instancia

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `1.0` | Fotogramas avanzados por paso (0 = en pausa) |

### Establecer sprite

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_sprite` |
| **Icono** | 🖼️ |
| **Categoría** | Instancia |

Cambiar el sprite y/o el fotograma/velocidad de animación de una instancia

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sprite` | Sprite | `<self>` | Sprite a usar (o «<self>» para mantener el actual) |
| `subimage` | Número | `-1` | Índice de fotograma a establecer; -1 lo deja sin cambios |
| `speed` | Número | `-1` | Velocidad de animación; -1 la deja sin cambios |

### Iniciar animación

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `start_animation` |
| **Icono** | ▶️ |
| **Categoría** | Instancia |

Reanudar la animación del sprite de la instancia (image_speed = 1)

*Parámetros:* ninguno

### Detener animación

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stop_animation` |
| **Icono** | ⏸️ |
| **Categoría** | Instancia |

Pausar la animación del sprite de la instancia (image_speed = 0)

*Parámetros:* ninguno

### Comprobar número de instancias

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_instance_count` |
| **Icono** | ❓🔢 |
| **Categoría** | Instancia |

Condición: comparar el número de instancias de un objeto

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Objeto a contar |
| `number` | Número | `0` | Valor de comparación |
| `operation` | Elección | `equal` | Operador de comparación; Opciones: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (2)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (20)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (4)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
