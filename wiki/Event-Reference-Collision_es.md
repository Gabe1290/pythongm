# Eventos de Colisión

*[Inicio](Home_es) | [Referencia de Eventos](Event-Reference_es) | [Referencia completa de acciones](Full-Action-Reference_es)*

### Colisión
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `collision` |
| **Icono** | 💥 |
| **Categoría** | Colisión |
| **Preset** | Principiante |

**Descripción:** Se dispara cuando esta instancia se superpone con otro tipo de objeto.

**Configuración:** Selecciona qué tipo de objeto activa esta colisión.

**Variable especial:** `other` - Referencia a la instancia que colisiona.

**Cuándo se dispara:** Cada fotograma en que las instancias se superponen.

**Usos comunes:**
- Recoger objetos
- Recibir daño
- Chocar con paredes
- Activar eventos

**Ejemplos de eventos de colisión:**
- `collision_with_obj_coin` - El jugador toca una moneda
- `collision_with_obj_enemy` - El jugador toca un enemigo
- `collision_with_obj_wall` - La instancia choca con una pared

---

## Otras Categorías de Eventos

- [Eventos de Objeto](Event-Reference-Object_es) - Create, Step, Destroy
- [Eventos de Entrada](Event-Reference-Input_es) - Teclado, Ratón
- [Eventos de Tiempo](Event-Reference-Timing_es) - Alarmas, Variantes de Step
- [Eventos de Dibujo](Event-Reference-Drawing_es) - Renderizado personalizado
- [Eventos de Sala](Event-Reference-Room_es) - Transiciones de sala
- [Eventos de Juego](Event-Reference-Game_es) - Inicio/Fin del juego
- [Otros Eventos](Event-Reference-Other_es) - Límites, Vidas, Salud

[← Volver a Referencia de Eventos](Event-Reference_es)
