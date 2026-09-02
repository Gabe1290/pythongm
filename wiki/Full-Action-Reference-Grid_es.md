# Cuadrícula

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Si en la cuadrícula

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_on_grid` |
| **Icono** | ▦ |
| **Categoría** | Cuadrícula |

Comprobar si el objeto está alineado a la cuadrícula

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `grid_size` | Número | `32` | Tamaño de la celda de la cuadrícula en píxeles |
| `then_actions` | Lista de acciones | — | Acciones si en la cuadrícula |
| `else_actions` | Lista de acciones | — | Acciones si no en la cuadrícula |

### Ajustar a la cuadrícula

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `snap_to_grid` |
| **Icono** | ▦ |
| **Categoría** | Cuadrícula |

Alinear la posición de la instancia a la cuadrícula

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `grid_size` | Número | `32` | Tamaño de la celda de la cuadrícula en píxeles |

### Detener si no hay teclas pulsadas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stop_if_no_keys` |
| **Icono** | ▦ |
| **Categoría** | Cuadrícula |

Detener el movimiento en la cuadrícula cuando no se pulsa ninguna tecla de movimiento (perfecto para un ajuste suave a la cuadrícula)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `grid_size` | Número | `32` | Tamaño de la celda de la cuadrícula en píxeles |

### Comprobar alineación a la cuadrícula

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_alignment` |
| **Icono** | ❓▦ |
| **Categoría** | Cuadrícula |

Condición: verdadero si la instancia está alineada a una cuadrícula

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `hsnap` | Número | `32` | Espaciado horizontal de la cuadrícula en píxeles |
| `vsnap` | Número | `32` | Espaciado vertical de la cuadrícula en píxeles |

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
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (16)
- [Particles](Full-Action-Reference-Particles_es) (8)
- [Réseau](Full-Action-Reference-Network-Actions_es) (15)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
