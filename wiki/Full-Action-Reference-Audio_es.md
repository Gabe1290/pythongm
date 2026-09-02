# Audio

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Comprobar reproducción de sonido

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `check_sound` |
| **Icono** | ❓🔊 |
| **Categoría** | Audio |

Condición: verdadero si el sonido indicado se está reproduciendo actualmente

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sound` | Sonido | — | Sonido a comprobar |
| `not_flag` | Sí/No | No | Invertir el resultado; opcional |

### Reproducir música

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `play_music` |
| **Icono** | 🎵 |
| **Categoría** | Audio |

Reproducir música de fondo (en bucle)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `music` | Sonido | — | Archivo de música a reproducir |
| `loop` | Sí/No | Sí | Reproducir la música en bucle |
| `volume` | Número | `0.7` | Volumen (de 0.0 a 1.0) |

### Reproducir sonido

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `play_sound` |
| **Icono** | 🔊 |
| **Categoría** | Audio |

Reproducir un efecto de sonido una vez

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sound` | Sonido | — | Sonido a reproducir |
| `volume` | Número | `1.0` | Volumen (de 0.0 a 1.0) |

### Establecer volumen

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_volume` |
| **Icono** | 🔉 |
| **Categoría** | Audio |

Establecer el volumen general de sonido/música

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `volume` | Número | `1.0` | Volumen (de 0.0 a 1.0) |

### Detener música

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stop_music` |
| **Icono** | 🔇 |
| **Categoría** | Audio |

Detener la música de fondo

*Parámetros:* ninguno

### Detener sonido

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stop_sound` |
| **Icono** | 🔇 |
| **Categoría** | Audio |

Detener un sonido en reproducción

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sound` | Sonido | — | Sonido a detener |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (8)
- [Juego](Full-Action-Reference-Game_es) (25)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (16)
- [Particles](Full-Action-Reference-Particles_es) (8)
- [Réseau](Full-Action-Reference-Network-Actions_es) (15)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
