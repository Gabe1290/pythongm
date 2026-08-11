# Tiempo

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

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

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (20)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (4)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
