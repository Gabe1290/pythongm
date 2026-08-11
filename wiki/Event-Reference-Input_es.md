# Eventos de Entrada

*[Inicio](Home_es) | [Referencia de Eventos](Event-Reference_es) | [Referencia completa de acciones](Full-Action-Reference_es)*

### Teclado (Continuo)
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `keyboard` |
| **Icono** | ⌨️ |
| **Categoría** | Entrada |
| **Preset** | Principiante |

**Descripción:** Se dispara continuamente mientras una tecla está presionada.

**Ideal para:** Movimiento suave y continuo

**Teclas Soportadas:**
- Teclas de flecha (arriba, abajo, izquierda, derecha)
- Letras (A-Z)
- Números (0-9)
- Espacio, Enter, Escape
- Teclas de función (F1-F12)
- Teclas modificadoras (Shift, Ctrl, Alt)

---

### Pulsación de Teclado
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `keyboard_press` |
| **Icono** | 🔘 |
| **Categoría** | Entrada |
| **Preset** | Intermedio |

**Descripción:** Se dispara una vez cuando una tecla se presiona por primera vez.

**Ideal para:** Acciones únicas (saltar, disparar, seleccionar en menú)

**Diferencia con Teclado:** Solo se dispara una vez por pulsación, no mientras se mantiene.

---

### Liberación de Teclado
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `keyboard_release` |
| **Icono** | ⬆️ |
| **Categoría** | Entrada |
| **Preset** | Completo (Edición Desarrollo) |

**Descripción:** Se dispara una vez cuando una tecla se suelta.

**Usos comunes:**
- Detener movimiento cuando se suelta la tecla
- Terminar ataques cargados
- Alternar estados

---

### Teclado (Ninguna tecla)
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `keyboard_no_key` |
| **Icono** | ⌨️ |
| **Categoría** | Entrada |
| **Preset** | Principiante |

**Descripción:** Se dispara en cada fotograma mientras **no** se mantiene ninguna tecla.

**Cuándo se dispara:** En cada fotograma en que el teclado está inactivo, *antes* del evento Step.

**Usos comunes:**
- Detener el movimiento cuando el jugador suelta todas las teclas (juegos de cuadrícula/laberintos)
- Animaciones en reposo

---

### Ratón
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `mouse` |
| **Icono** | 🖱️ |
| **Categoría** | Entrada |
| **Preset** | Completo (Edición Desarrollo) |

**Descripción:** Eventos de botón de ratón y movimiento.

**Tipos de Eventos:**

| Tipo | Descripción |
|------|-------------|
| Botón Izquierdo | Clic con botón izquierdo del ratón |
| Botón Derecho | Clic con botón derecho del ratón |
| Botón Central | Clic con botón central/rueda |
| Entrada de Ratón | El cursor entra en los límites de la instancia |
| Salida de Ratón | El cursor sale de los límites de la instancia |
| Botón Izquierdo Global | Clic izquierdo en cualquier lugar |
| Botón Derecho Global | Clic derecho en cualquier lugar |

---

## Otras Categorías de Eventos

- [Eventos de Objeto](Event-Reference-Object_es) - Create, Step, Destroy
- [Eventos de Colisión](Event-Reference-Collision_es) - Colisiones de objetos
- [Eventos de Tiempo](Event-Reference-Timing_es) - Alarmas, Variantes de Step
- [Eventos de Dibujo](Event-Reference-Drawing_es) - Renderizado personalizado
- [Eventos de Sala](Event-Reference-Room_es) - Transiciones de sala
- [Eventos de Juego](Event-Reference-Game_es) - Inicio/Fin del juego
- [Otros Eventos](Event-Reference-Other_es) - Límites, Vidas, Salud

[← Volver a Referencia de Eventos](Event-Reference_es)
