# Eventos de Juego

*[Inicio](Home_es) | [Referencia de Eventos](Event-Reference_es) | [Referencia completa de acciones](Full-Action-Reference_es)*

### Game Start
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `game_start` |
| **Icono** | 🎮 |
| **Categoría** | Juego |
| **Preset** | Principiante |

**Descripción:** Se dispara una vez cuando el juego inicia por primera vez (solo en la primera sala).

**Usos comunes:**
- Inicializar variables globales
- Cargar datos guardados
- Reproducir introducción

---

### Game End
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `game_end` |
| **Icono** | 🎮 |
| **Categoría** | Juego |
| **Preset** | Principiante |

**Descripción:** Se dispara cuando el juego está terminando.

**Usos comunes:**
- Guardar datos del juego
- Liberar recursos

---

## Otras Categorías de Eventos

- [Eventos de Objeto](Event-Reference-Object_es) - Create, Step, Destroy
- [Eventos de Entrada](Event-Reference-Input_es) - Teclado, Ratón
- [Eventos de Colisión](Event-Reference-Collision_es) - Colisiones de objetos
- [Eventos de Tiempo](Event-Reference-Timing_es) - Alarmas, Variantes de Step
- [Eventos de Dibujo](Event-Reference-Drawing_es) - Renderizado personalizado
- [Eventos de Sala](Event-Reference-Room_es) - Transiciones de sala
- [Otros Eventos](Event-Reference-Other_es) - Límites, Vidas, Salud

[← Volver a Referencia de Eventos](Event-Reference_es)
