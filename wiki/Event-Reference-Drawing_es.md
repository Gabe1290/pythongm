# Eventos de Dibujo

*[Inicio](Home_es) | [Referencia de Eventos](Event-Reference_es) | [Referencia completa de acciones](Full-Action-Reference_es)*

### Draw
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `draw` |
| **Icono** | 🎨 |
| **Categoría** | Dibujo |
| **Preset** | Principiante |

**Descripción:** Se dispara durante la fase de renderizado.

**Importante:** Agregar un evento Draw desactiva el dibujo automático del sprite. Debes dibujar el sprite manualmente si quieres que sea visible.

**Usos comunes:**
- Renderizado personalizado
- Dibujar formas
- Mostrar texto
- Barras de salud
- Elementos de HUD

**Acciones de dibujo disponibles:**
- Dibujar Sprite
- Dibujar Texto
- Dibujar Rectángulo
- Dibujar Círculo
- Dibujar Línea
- Dibujar Barra de Salud

---

### Draw GUI
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `draw_gui` |
| **Icono** | 🖥️ |
| **Categoría** | Dibujo |
| **Preset** | Principiante |

**Descripción:** Dibuja en el **espacio de pantalla (GUI)**, encima de la sala y sin verse afectado por el desplazamiento de vistas/cámara.

**Diferencia con Draw:** el evento Draw normal está en coordenadas de sala (se desplaza con la vista); Draw GUI permanece fijo a la pantalla — úsalo para HUD, puntuaciones y menús.

---

## Otras Categorías de Eventos

- [Eventos de Objeto](Event-Reference-Object_es) - Create, Step, Destroy
- [Eventos de Entrada](Event-Reference-Input_es) - Teclado, Ratón
- [Eventos de Colisión](Event-Reference-Collision_es) - Colisiones de objetos
- [Eventos de Tiempo](Event-Reference-Timing_es) - Alarmas, Variantes de Step
- [Eventos de Sala](Event-Reference-Room_es) - Transiciones de sala
- [Eventos de Juego](Event-Reference-Game_es) - Inicio/Fin del juego
- [Otros Eventos](Event-Reference-Other_es) - Límites, Vidas, Salud

[← Volver a Referencia de Eventos](Event-Reference_es)
