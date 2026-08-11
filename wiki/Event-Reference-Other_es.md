# Otros Eventos

*[Inicio](Home_es) | [Referencia de Eventos](Event-Reference_es) | [Referencia completa de acciones](Full-Action-Reference_es)*

### Outside Room
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `outside_room` |
| **Icono** | 🚫 |
| **Categoría** | Otro |
| **Preset** | Principiante |

**Descripción:** Se dispara cuando la instancia está completamente fuera de los límites de la sala.

**Usos comunes:**
- Destruir balas fuera de pantalla
- Aparecer en el otro lado
- Activar game over

---

### Intersect Boundary
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `intersect_boundary` |
| **Icono** | ⚠️ |
| **Categoría** | Otro |
| **Preset** | Principiante |

**Descripción:** Se dispara cuando la instancia toca el límite de la sala.

**Usos comunes:**
- Mantener al jugador dentro de los límites
- Rebotar en los bordes

---

### No More Lives
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `no_more_lives` |
| **Icono** | 💀 |
| **Categoría** | Otro |
| **Preset** | Principiante |

**Descripción:** Se dispara cuando las vidas llegan a 0 o menos.

**Usos comunes:**
- Pantalla de game over
- Reiniciar juego
- Mostrar puntuación final

---

### No More Health
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `no_more_health` |
| **Icono** | 💔 |
| **Categoría** | Otro |
| **Preset** | Principiante |

**Descripción:** Se dispara cuando la salud llega a 0 o menos.

**Usos comunes:**
- Perder una vida
- Reaparecer jugador
- Activar animación de muerte

---

### Animation End
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `animation_end` |
| **Icono** | 🎞️ |
| **Categoría** | Otro |
| **Preset** | Principiante |

**Descripción:** Se dispara cuando la animación del sprite de la instancia completa un ciclo entero (vuelve del último fotograma al primero).

**Usos comunes:**
- Destruir un efecto único (explosión) tras una sola reproducción
- Cambiar a otra animación cuando la actual termina
- Avanzar una máquina de estados al terminar la animación

---

## Otras Categorías de Eventos

- [Eventos de Objeto](Event-Reference-Object_es) - Create, Step, Destroy
- [Eventos de Entrada](Event-Reference-Input_es) - Teclado, Ratón
- [Eventos de Colisión](Event-Reference-Collision_es) - Colisiones de objetos
- [Eventos de Tiempo](Event-Reference-Timing_es) - Alarmas, Variantes de Step
- [Eventos de Dibujo](Event-Reference-Drawing_es) - Renderizado personalizado
- [Eventos de Sala](Event-Reference-Room_es) - Transiciones de sala
- [Eventos de Juego](Event-Reference-Game_es) - Inicio/Fin del juego

[← Volver a Referencia de Eventos](Event-Reference_es)
