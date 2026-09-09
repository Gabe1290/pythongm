# Partículas

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Lanzar partículas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `burst_particles` |
| **Icono** | 💥 |
| **Categoría** | Partículas |

Lanza una ráfaga única de partículas desde el emisor creado más recientemente

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `particle_type` | Número | `0` | Identificador del tipo de partícula (de «Crear tipo de partícula») |
| `number` | Número | `10` | Número de partículas a lanzar |

### Borrar partículas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `clear_particles` |
| **Icono** | 🧹 |
| **Categoría** | Partículas |

Elimina todas las partículas activas, pero conserva los tipos de partícula y los emisores

*Parámetros:* ninguno

### Crear emisor

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_emitter` |
| **Icono** | 🌀 |
| **Categoría** | Partículas |

Crea una zona emisora de partículas (el identificador devuelto se guarda para la siguiente acción que use un emisor)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | X del centro del emisor (coordenadas de la sala) |
| `y` | Número | `0` | Y del centro del emisor (coordenadas de la sala) |
| `width` | Número | `0` | Anchura de la zona emisora |
| `height` | Número | `0` | Altura de la zona emisora |
| `shape` | Elección | `rectangle` | Forma de la zona emisora dentro de la cual nacen las partículas; Opciones: `rectangle`, `ellipse`, `diamond`, `line` |

### Crear sistema de partículas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_particle_system` |
| **Icono** | ✨ |
| **Categoría** | Partículas |

Crea un sistema de partículas asociado a esta instancia (sustituye cualquier otro existente)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `depth` | Número | `0` | Profundidad de dibujo del sistema de partículas (todavía no se usa para ordenar entre instancias) |

### Crear tipo de partícula

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `create_particle_type` |
| **Icono** | ⚙️ |
| **Categoría** | Partículas |

Define una nueva apariencia o comportamiento de partícula (el identificador de tipo devuelto se guarda para la siguiente acción que use un tipo de partícula)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite con el que se dibuja cada partícula; déjalo vacío para un simple círculo de color; opcional |
| `size_min` | Número | `1.0` | Tamaño mínimo de la partícula (factor de escala) |
| `size_max` | Número | `1.0` | Tamaño máximo de la partícula (factor de escala) |
| `size_increase` | Número | `0.0` | Cambio de tamaño por paso (negativo encoge, con 0 como mínimo) |
| `color` | Color | `#FFFFFF` | Color de la partícula (se usa cuando no hay sprite) |
| `alpha` | Número | `1.0` | Transparencia (0 = invisible, 1 = opaca) |
| `speed_min` | Número | `0.0` | Velocidad de movimiento mínima |
| `speed_max` | Número | `0.0` | Velocidad de movimiento máxima |
| `direction_min` | Número | `0` | Ángulo de dirección mínimo (0 = derecha, 90 = arriba) |
| `direction_max` | Número | `360` | Ángulo de dirección máximo |
| `life_min` | Número | `100` | Duración mínima, en pasos |
| `life_max` | Número | `100` | Duración máxima, en pasos |

### Destruir emisor

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `destroy_emitter` |
| **Icono** | 💥 |
| **Categoría** | Partículas |

Destruye el emisor creado más recientemente

*Parámetros:* ninguno

### Destruir sistema de partículas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `destroy_particle_system` |
| **Icono** | 💥 |
| **Categoría** | Partículas |

Elimina el sistema de partículas de esta instancia, borrando todas sus partículas y emisores

*Parámetros:* ninguno

### Emitir partículas en continuo

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stream_particles` |
| **Icono** | 🌊 |
| **Categoría** | Partículas |

Emite partículas de forma continua en cada paso desde el emisor creado más recientemente (0 para detenerlo)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `particle_type` | Número | `0` | Identificador del tipo de partícula (de «Crear tipo de partícula») |
| `number` | Número | `1` | Partículas emitidas por paso (0 detiene la emisión) |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (8)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (25)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (18)
- [Red](Full-Action-Reference-Network-Actions_es) (15)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
