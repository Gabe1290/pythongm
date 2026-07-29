# Referencia de Eventos

*[Inicio](Home_es) | [Guia de Presets](Preset-Guide_es) | [Referencia Completa de Acciones](Full-Action-Reference_es)*

Esta página documenta todos los eventos disponibles en PyGameMaker. Los eventos son disparadores que ejecutan acciones cuando ocurren condiciones específicas en tu juego.

## Categorías de Eventos

- [Eventos de Objeto](#eventos-de-objeto) - Create, Step, Destroy
- [Eventos de Entrada](#eventos-de-entrada) - Teclado, Ratón
- [Eventos de Colisión](#eventos-de-colisión) - Colisiones de objetos
- [Eventos de Tiempo](#eventos-de-tiempo) - Alarmas, Variantes de Step
- [Eventos de Dibujo](#eventos-de-dibujo) - Renderizado personalizado
- [Eventos de Sala](#eventos-de-sala) - Transiciones de sala
- [Eventos de Juego](#eventos-de-juego) - Inicio/Fin del juego
- [Otros Eventos](#otros-eventos) - Límites, Vidas, Salud

---

## Eventos de Objeto

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
- Despues de transiciones de sala para nuevas instancias

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

## Eventos de Entrada

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
| **Preset** | Principiante |

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
| **Preset** | Avanzado |

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
| **Preset** | Avanzado |

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
| **Preset** | Intermedio |

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

## Eventos de Colisión

### Colisión
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `collision` |
| **Icono** | 💥 |
| **Categoría** | Colisión |
| **Preset** | Principiante |

**Descripción:** Se dispara cuando esta instancia se superpone con otro tipo de objeto.

**Configuración:** Selecciona que tipo de objeto activa esta colisión.

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

## Eventos de Tiempo

### Alarma
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `alarm` |
| **Icono** | ⏰ |
| **Categoría** | Tiempo |
| **Preset** | Intermedio |

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
| **Preset** | Avanzado |

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
| **Preset** | Avanzado |

**Descripción:** Se dispara al final de cada fotograma, después de las colisiones.

**Usos comunes:**
- Ajustes finales de posición
- Operaciones de limpieza
- Actualizaciones de estado después de colisiones

---

## Eventos de Dibujo

### Draw
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `draw` |
| **Icono** | 🎨 |
| **Categoría** | Dibujo |
| **Preset** | Intermedio |

**Descripción:** Se dispara durante la fase de renderizado.

**Importante:** Agregar un evento Draw desactiva el dibujo automatico del sprite. Debes dibujar el sprite manualmente si quieres que sea visible.

**Usos comunes:**
- Renderizado personalizado
- Dibujar formas
- Mostrar texto
- Barras de salud
- Elementos de HUD

**Acciones de dibujo disponibles:**
- Dibujar Sprite
- Dibujar Texto
- Dibujar Rectangulo
- Dibujar Circulo
- Dibujar Linea
- Dibujar Barra de Salud

---

### Draw GUI
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `draw_gui` |
| **Icono** | 🖥️ |
| **Categoría** | Dibujo |
| **Preset** | Avanzado |

**Descripción:** Dibuja en el **espacio de pantalla (GUI)**, encima de la sala y sin verse afectado por el desplazamiento de vistas/cámara.

**Diferencia con Draw:** el evento Draw normal está en coordenadas de sala (se desplaza con la vista); Draw GUI permanece fijo a la pantalla — úsalo para HUD, puntuaciones y menús.

---

## Eventos de Sala

### Room Start
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `room_start` |
| **Icono** | 🚪 |
| **Categoría** | Sala |
| **Preset** | Avanzado |

**Descripción:** Se dispara al entrar en una sala, después de todos los eventos Create.

**Usos comunes:**
- Inicialización de sala
- Reproducir música de sala
- Establecer variables específicas de sala

---

### Room End
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `room_end` |
| **Icono** | 🚪 |
| **Categoría** | Sala |
| **Preset** | Avanzado |

**Descripción:** Se dispara al salir de una sala.

**Usos comunes:**
- Guardar progreso
- Detener música
- Limpieza

---

## Eventos de Juego

### Game Start
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `game_start` |
| **Icono** | 🎮 |
| **Categoría** | Juego |
| **Preset** | Avanzado |

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
| **Preset** | Avanzado |

**Descripción:** Se dispara cuando el juego esta terminando.

**Usos comunes:**
- Guardar datos del juego
- Liberar recursos

---

## Otros Eventos

### Outside Room
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `outside_room` |
| **Icono** | 🚫 |
| **Categoría** | Otro |
| **Preset** | Avanzado |

**Descripción:** Se dispara cuando la instancia esta completamente fuera de los límites de la sala.

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
| **Preset** | Avanzado |

**Descripción:** Se dispara cuando la instancia toca el limite de la sala.

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
| **Preset** | Intermedio |

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
| **Preset** | Intermedio |

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
| **Preset** | Avanzado |

**Descripción:** Se dispara cuando la animación del sprite de la instancia completa un ciclo entero (vuelve del último fotograma al primero).

**Usos comunes:**
- Destruir un efecto único (explosión) tras una sola reproducción
- Cambiar a otra animación cuando la actual termina
- Avanzar una máquina de estados al terminar la animación

---

## Orden de Ejecución de Eventos

Entender cuando se disparan los eventos ayuda a crear un comportamiento de juego predecible:

1. **Begin Step** - Inicio del fotograma
2. **Alarm** - Cualquier alarma activada
3. **Keyboard/Mouse** - Eventos de entrada
4. **Step** - Lógica principal del juego
5. **Collision** - Despues del movimiento
6. **End Step** - Despues de colisiones
7. **Draw** - Fase de renderizado

---

## Eventos por Preset

| Preset | Eventos Incluidos |
|--------|-------------------|
| **Principiante** | Create, Step, Keyboard Press, Collision |
| **Intermedio** | + Draw, Destroy, Mouse, Alarm |
| **Avanzado** | + Todas las variantes de teclado, Begin/End Step, Eventos de sala, Eventos de juego, Eventos de limite |

---

## Ver Tambien

- [Referencia Completa de Acciones](Full-Action-Reference_es) - Lista completa de acciones
- [Preset Principiante](Beginner-Preset_es) - Eventos esenciales para principiantes
- [Preset Intermedio](Intermediate-Preset_es) - Eventos adicionales
- [Eventos y Acciones](Events-and-Actions_es) - Visión general de conceptos básicos
