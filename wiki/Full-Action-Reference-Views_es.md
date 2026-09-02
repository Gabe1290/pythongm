# Vistas

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Habilitar vistas

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `enable_views` |
| **Icono** | 🎥 |
| **Categoría** | Vistas |

Activar o desactivar el sistema de cámara/vista de la sala (permite que un nivel se desplace cuando es más grande que la ventana)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `enable` | Sí/No | Sí | Activado = vistas de cámara; desactivado = dibujar toda la sala de una vez |

### Configurar vista

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_view` |
| **Icono** | 🎥 |
| **Categoría** | Vistas |

Configurar una vista de cámara: qué parte de la sala muestra, dónde se dibuja en pantalla y un objeto a seguir

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `view` | Elección | `0` | Cuál de las 8 vistas configurar; Opciones: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` |
| `visible` | Sí/No | Sí | Dibujar esta vista |
| `view_x` | Número | `0` | Borde izquierdo de la región de la sala mostrada |
| `view_y` | Número | `0` | Borde superior de la región de la sala mostrada |
| `view_w` | Número | `800` | Ancho de la región de la sala mostrada |
| `view_h` | Número | `600` | Alto de la región de la sala mostrada |
| `port_x` | Número | `0` | Borde izquierdo en pantalla |
| `port_y` | Número | `0` | Borde superior en pantalla |
| `port_w` | Número | `800` | Ancho dibujado en pantalla |
| `port_h` | Número | `600` | Alto dibujado en pantalla |
| `follow` | Objeto | — | Objeto que sigue la cámara (vacío = vista fija); opcional |
| `hborder` | Número | `32` | Borde horizontal antes de que la cámara se desplace |
| `vborder` | Número | `32` | Borde vertical antes de que la cámara se desplace |
| `hspeed` | Número | `-1` | Velocidad máxima de desplazamiento horizontal (-1 = instantáneo) |
| `vspeed` | Número | `-1` | Velocidad máxima de desplazamiento vertical (-1 = instantáneo) |

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
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (16)
- [Particles](Full-Action-Reference-Particles_es) (8)
- [Réseau](Full-Action-Reference-Network-Actions_es) (15)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
