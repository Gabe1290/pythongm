# Tiempo

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Pause Timeline

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `pause_timeline` |
| **Icono** | ⏸️ |
| **Categoría** | Tiempo |

Pause timeline playback at the current position

*Parámetros:* ninguno

### Establecer alarma

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_alarm` |
| **Icono** | ⏰ |
| **Categoría** | Tiempo |

Establecer una alarma

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `alarm_number` | Número | `0` | Qué alarma (0-11) |
| `steps` | Número | `30` | Número de pasos hasta que salte la alarma (30 = 0,5 s a 60 FPS) |

### Set Timeline

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_timeline` |
| **Icono** | ⏱️ |
| **Categoría** | Tiempo |

Set this instance's timeline label and reset its position to 0 (bookkeeping only — see category note)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `timeline` | Texto | — | A label for your own reference; not a resource lookup |

### Set Timeline Position

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_timeline_position` |
| **Icono** | ⏱️ |
| **Categoría** | Tiempo |

Set (or offset) this instance's timeline position

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `position` | Número | `0` | Position in steps |
| `relative` | Sí/No | No | Add to the current position instead of setting it absolutely |

### Set Timeline Speed

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_timeline_speed` |
| **Icono** | ⏱️ |
| **Categoría** | Tiempo |

Set the timeline playback speed multiplier

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `1.0` | 1.0=normal, 0.5=half speed, 2.0=double speed |

### Pausa

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `sleep` |
| **Icono** | 💤 |
| **Categoría** | Tiempo |

Pausar el juego durante un número de milisegundos y luego continuar. Los sonidos siguen sonando durante la pausa (por ejemplo, para dejar que un sonido termine antes de cambiar de sala). Nota: el renderizado y la entrada se congelan durante la pausa, así que mantén duraciones cortas

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `milliseconds` | Número | `1000` | Duración de la pausa, en milisegundos (1000 = 1 segundo) |

### Start Timeline

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `start_timeline` |
| **Icono** | ▶️ |
| **Categoría** | Tiempo |

Begin or resume timeline playback from the current position

*Parámetros:* ninguno

### Stop Timeline

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `stop_timeline` |
| **Icono** | ⏹️ |
| **Categoría** | Tiempo |

Stop timeline playback and reset the position to 0

*Parámetros:* ninguno

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (25)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (16)
- [Particles](Full-Action-Reference-Particles_es) (8)
- [Réseau](Full-Action-Reference-Network-Actions_es) (15)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
