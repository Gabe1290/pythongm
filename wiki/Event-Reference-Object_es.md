# Eventos de Objeto

*[Inicio](Home_es) | [Referencia de Eventos](Event-Reference_es) | [Referencia completa de acciones](Full-Action-Reference_es)*

### Create
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `create` |
| **Icono** | 🎯 |
| **Categoría** | Objeto |
| **Preset** | Principiante |

**Descripción:** Se ejecuta una vez cuando se crea una instancia por primera vez.

**Cuándo se dispara:**
- Cuando una instancia se coloca en una sala al iniciar el juego
- Cuando se crea mediante la acción "Crear Instancia"
- Después de transiciones de sala para nuevas instancias

**Usos comunes:**
- Inicializar variables
- Establecer valores iniciales
- Configurar estado inicial

---

### Step
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `step` |
| **Icono** | ⭐ |
| **Categoría** | Objeto |
| **Preset** | Principiante |

**Descripción:** Se ejecuta cada fotograma (típicamente 60 veces por segundo).

**Cuándo se dispara:** Continuamente, cada fotograma del juego.

**Usos comunes:**
- Movimiento continuo
- Verificar condiciones
- Actualizar posiciones
- Lógica del juego

**Nota:** Ten cuidado con el rendimiento - el código aquí se ejecuta constantemente.

---

### Destroy
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `destroy` |
| **Icono** | 💥 |
| **Categoría** | Objeto |
| **Preset** | Intermedio |

**Descripción:** Se ejecuta cuando una instancia es destruida.

**Cuándo se dispara:** Justo antes de que la instancia sea eliminada del juego.

**Usos comunes:**
- Generar efectos (explosiones, partículas)
- Soltar objetos
- Actualizar puntuaciones
- Reproducir sonidos

---

## Otras Categorías de Eventos

- [Eventos de Entrada](Event-Reference-Input_es) - Teclado, Ratón
- [Eventos de Colisión](Event-Reference-Collision_es) - Colisiones de objetos
- [Eventos de Tiempo](Event-Reference-Timing_es) - Alarmas, Variantes de Step
- [Eventos de Dibujo](Event-Reference-Drawing_es) - Renderizado personalizado
- [Eventos de Sala](Event-Reference-Room_es) - Transiciones de sala
- [Eventos de Juego](Event-Reference-Game_es) - Inicio/Fin del juego
- [Otros Eventos](Event-Reference-Other_es) - Límites, Vidas, Salud

[← Volver a Referencia de Eventos](Event-Reference_es)
