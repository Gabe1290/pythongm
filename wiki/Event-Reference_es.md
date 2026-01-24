# Referencia de Eventos

*[Inicio](Home_es) | [Guia de Presets](Preset-Guide_es) | [Referencia Completa de Acciones](Full-Action-Reference_es)*

Esta pagina documenta todos los eventos disponibles en PyGameMaker. Los eventos son disparadores que ejecutan acciones cuando ocurren condiciones especificas en tu juego.

## Categorias de Eventos

- [Eventos de Objeto](#eventos-de-objeto) - Create, Step, Destroy
- [Eventos de Entrada](#eventos-de-entrada) - Teclado, Raton
- [Eventos de Colision](#eventos-de-colision) - Colisiones de objetos
- [Eventos de Tiempo](#eventos-de-tiempo) - Alarmas, Variantes de Step
- [Eventos de Dibujo](#eventos-de-dibujo) - Renderizado personalizado
- [Eventos de Sala](#eventos-de-sala) - Transiciones de sala
- [Eventos de Juego](#eventos-de-juego) - Inicio/Fin del juego
- [Otros Eventos](#otros-eventos) - Limites, Vidas, Salud

---

## Eventos de Objeto

### Create
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `create` |
| **Icono** | 🎯 |
| **Categoria** | Objeto |
| **Preset** | Principiante |

**Descripcion:** Se ejecuta una vez cuando se crea una instancia por primera vez.

**Cuando se dispara:**
- Cuando una instancia se coloca en una sala al iniciar el juego
- Cuando se crea mediante la accion "Crear Instancia"
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
| **Categoria** | Objeto |
| **Preset** | Principiante |

**Descripcion:** Se ejecuta cada fotograma (tipicamente 60 veces por segundo).

**Cuando se dispara:** Continuamente, cada fotograma del juego.

**Usos comunes:**
- Movimiento continuo
- Verificar condiciones
- Actualizar posiciones
- Logica del juego

**Nota:** Ten cuidado con el rendimiento - el codigo aqui se ejecuta constantemente.

---

### Destroy
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `destroy` |
| **Icono** | 💥 |
| **Categoria** | Objeto |
| **Preset** | Intermedio |

**Descripcion:** Se ejecuta cuando una instancia es destruida.

**Cuando se dispara:** Justo antes de que la instancia sea eliminada del juego.

**Usos comunes:**
- Generar efectos (explosiones, particulas)
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
| **Categoria** | Entrada |
| **Preset** | Principiante |

**Descripcion:** Se dispara continuamente mientras una tecla esta presionada.

**Ideal para:** Movimiento suave y continuo

**Teclas Soportadas:**
- Teclas de flecha (arriba, abajo, izquierda, derecha)
- Letras (A-Z)
- Numeros (0-9)
- Espacio, Enter, Escape
- Teclas de funcion (F1-F12)
- Teclas modificadoras (Shift, Ctrl, Alt)

---

### Pulsacion de Teclado
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `keyboard_press` |
| **Icono** | 🔘 |
| **Categoria** | Entrada |
| **Preset** | Principiante |

**Descripcion:** Se dispara una vez cuando una tecla se presiona por primera vez.

**Ideal para:** Acciones unicas (saltar, disparar, seleccionar en menu)

**Diferencia con Teclado:** Solo se dispara una vez por pulsacion, no mientras se mantiene.

---

### Liberacion de Teclado
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `keyboard_release` |
| **Icono** | ⬆️ |
| **Categoria** | Entrada |
| **Preset** | Avanzado |

**Descripcion:** Se dispara una vez cuando una tecla se suelta.

**Usos comunes:**
- Detener movimiento cuando se suelta la tecla
- Terminar ataques cargados
- Alternar estados

---

### Raton
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `mouse` |
| **Icono** | 🖱️ |
| **Categoria** | Entrada |
| **Preset** | Intermedio |

**Descripcion:** Eventos de boton de raton y movimiento.

**Tipos de Eventos:**

| Tipo | Descripcion |
|------|-------------|
| Boton Izquierdo | Clic con boton izquierdo del raton |
| Boton Derecho | Clic con boton derecho del raton |
| Boton Central | Clic con boton central/rueda |
| Entrada de Raton | El cursor entra en los limites de la instancia |
| Salida de Raton | El cursor sale de los limites de la instancia |
| Boton Izquierdo Global | Clic izquierdo en cualquier lugar |
| Boton Derecho Global | Clic derecho en cualquier lugar |

---

## Eventos de Colision

### Colision
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `collision` |
| **Icono** | 💥 |
| **Categoria** | Colision |
| **Preset** | Principiante |

**Descripcion:** Se dispara cuando esta instancia se superpone con otro tipo de objeto.

**Configuracion:** Selecciona que tipo de objeto activa esta colision.

**Variable especial:** `other` - Referencia a la instancia que colisiona.

**Cuando se dispara:** Cada fotograma en que las instancias se superponen.

**Usos comunes:**
- Recoger objetos
- Recibir dano
- Chocar con paredes
- Activar eventos

**Ejemplos de eventos de colision:**
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
| **Categoria** | Tiempo |
| **Preset** | Intermedio |

**Descripcion:** Se dispara cuando una cuenta regresiva de alarma llega a cero.

**Alarmas disponibles:** 12 alarmas independientes (alarm[0] hasta alarm[11])

**Configurar alarmas:** Usa la accion "Establecer Alarma" con pasos (60 pasos ≈ 1 segundo a 60 FPS)

**Usos comunes:**
- Generacion temporizada
- Tiempos de recarga
- Efectos retrasados
- Acciones repetitivas (establecer alarma de nuevo en el evento de alarma)

---

### Begin Step
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `begin_step` |
| **Icono** | ▶️ |
| **Categoria** | Step |
| **Preset** | Avanzado |

**Descripcion:** Se dispara al comienzo de cada fotograma, antes de los eventos Step regulares.

**Orden de ejecucion:** Begin Step → Step → End Step

**Usos comunes:**
- Procesamiento de entrada
- Calculos pre-movimiento

---

### End Step
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `end_step` |
| **Icono** | ⏹️ |
| **Categoria** | Step |
| **Preset** | Avanzado |

**Descripcion:** Se dispara al final de cada fotograma, despues de las colisiones.

**Usos comunes:**
- Ajustes finales de posicion
- Operaciones de limpieza
- Actualizaciones de estado despues de colisiones

---

## Eventos de Dibujo

### Draw
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `draw` |
| **Icono** | 🎨 |
| **Categoria** | Dibujo |
| **Preset** | Intermedio |

**Descripcion:** Se dispara durante la fase de renderizado.

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

## Eventos de Sala

### Room Start
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `room_start` |
| **Icono** | 🚪 |
| **Categoria** | Sala |
| **Preset** | Avanzado |

**Descripcion:** Se dispara al entrar en una sala, despues de todos los eventos Create.

**Usos comunes:**
- Inicializacion de sala
- Reproducir musica de sala
- Establecer variables especificas de sala

---

### Room End
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `room_end` |
| **Icono** | 🚪 |
| **Categoria** | Sala |
| **Preset** | Avanzado |

**Descripcion:** Se dispara al salir de una sala.

**Usos comunes:**
- Guardar progreso
- Detener musica
- Limpieza

---

## Eventos de Juego

### Game Start
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `game_start` |
| **Icono** | 🎮 |
| **Categoria** | Juego |
| **Preset** | Avanzado |

**Descripcion:** Se dispara una vez cuando el juego inicia por primera vez (solo en la primera sala).

**Usos comunes:**
- Inicializar variables globales
- Cargar datos guardados
- Reproducir introduccion

---

### Game End
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `game_end` |
| **Icono** | 🎮 |
| **Categoria** | Juego |
| **Preset** | Avanzado |

**Descripcion:** Se dispara cuando el juego esta terminando.

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
| **Categoria** | Otro |
| **Preset** | Avanzado |

**Descripcion:** Se dispara cuando la instancia esta completamente fuera de los limites de la sala.

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
| **Categoria** | Otro |
| **Preset** | Avanzado |

**Descripcion:** Se dispara cuando la instancia toca el limite de la sala.

**Usos comunes:**
- Mantener al jugador dentro de los limites
- Rebotar en los bordes

---

### No More Lives
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `no_more_lives` |
| **Icono** | 💀 |
| **Categoria** | Otro |
| **Preset** | Intermedio |

**Descripcion:** Se dispara cuando las vidas llegan a 0 o menos.

**Usos comunes:**
- Pantalla de game over
- Reiniciar juego
- Mostrar puntuacion final

---

### No More Health
| Propiedad | Valor |
|-----------|-------|
| **Nombre** | `no_more_health` |
| **Icono** | 💔 |
| **Categoria** | Otro |
| **Preset** | Intermedio |

**Descripcion:** Se dispara cuando la salud llega a 0 o menos.

**Usos comunes:**
- Perder una vida
- Reaparecer jugador
- Activar animacion de muerte

---

## Orden de Ejecucion de Eventos

Entender cuando se disparan los eventos ayuda a crear un comportamiento de juego predecible:

1. **Begin Step** - Inicio del fotograma
2. **Alarm** - Cualquier alarma activada
3. **Keyboard/Mouse** - Eventos de entrada
4. **Step** - Logica principal del juego
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
- [Eventos y Acciones](Events-and-Actions_es) - Vision general de conceptos basicos
