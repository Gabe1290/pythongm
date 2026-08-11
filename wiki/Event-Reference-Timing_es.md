# Eventos de Tiempo

*[Inicio](Home_es) | [Referencia de Eventos](Event-Reference_es) | [Referencia completa de acciones](Full-Action-Reference_es)*

### Alarma
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `alarm` |
| **Icono** | ⏰ |
| **Categoría** | Tiempo |
| **Preset** | Principiante |

**Descripción:** Se dispara cuando una cuenta regresiva de alarma llega a cero.

**Alarmas disponibles:** 12 alarmas independientes (alarm[0] hasta alarm[11])

**Configurar alarmas:** Usa la acción "Establecer Alarma" con pasos (60 pasos ≈ 1 segundo a 60 FPS)

**Usos comunes:**
- Generación temporizada
- Tiempos de recarga
- Efectos retrasados
- Acciones repetitivas (establecer alarma de nuevo en el evento de alarma)

---

### Begin Step
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `begin_step` |
| **Icono** | ▶️ |
| **Categoría** | Step |
| **Preset** | Principiante |

**Descripción:** Se dispara al comienzo de cada fotograma, antes de los eventos Step regulares.

**Orden de ejecución:** Begin Step → Step → End Step

**Usos comunes:**
- Procesamiento de entrada
- Cálculos pre-movimiento

---

### End Step
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `end_step` |
| **Icono** | ⏹️ |
| **Categoría** | Step |
| **Preset** | Principiante |

**Descripción:** Se dispara al final de cada fotograma, después de las colisiones.

**Usos comunes:**
- Ajustes finales de posición
- Operaciones de limpieza
- Actualizaciones de estado después de colisiones

---

## Otras Categorías de Eventos

- [Eventos de Objeto](Event-Reference-Object_es) - Create, Step, Destroy
- [Eventos de Entrada](Event-Reference-Input_es) - Teclado, Ratón
- [Eventos de Colisión](Event-Reference-Collision_es) - Colisiones de objetos
- [Eventos de Dibujo](Event-Reference-Drawing_es) - Renderizado personalizado
- [Eventos de Sala](Event-Reference-Room_es) - Transiciones de sala
- [Eventos de Juego](Event-Reference-Game_es) - Inicio/Fin del juego
- [Otros Eventos](Event-Reference-Other_es) - Límites, Vidas, Salud

[← Volver a Referencia de Eventos](Event-Reference_es)
