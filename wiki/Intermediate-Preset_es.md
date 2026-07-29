# Preset Intermedio

*[Inicio](Home_es) | [Guia de Presets](Preset-Guide_es) | [Preset Principiante](Beginner-Preset_es)*

El preset **Intermedio** se basa en el [Preset Principiante](Beginner-Preset_es) añadiendo eventos y acciones más avanzados. Está diseñado para usuarios que han dominado lo básico y quieren crear juegos más complejos con características como eventos temporizados, sonido, vidas y sistemas de salud.

## Visión General

El preset Intermedio incluye todo lo del Principiante, más:
- **4 Tipos de Eventos Adicionales** - Dibujo, Destrucción, Ratón, Alarma
- **12 Tipos de Acciones Adicionales** - Vidas, Salud, Sonido, Temporización y más opciones de movimiento
- **3 Categorías Adicionales** - Temporización, Sonido, Dibujo

---

## Eventos Adicionales (Más allá del Principiante)

### Evento de Dibujo
| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_draw` |
| **Categoría** | Dibujo |
| **Icono** | 🎨 |
| **Descripción** | Se activa cuando el objeto necesita ser renderizado |

**Cuándo se activa:** Cada fotograma durante la fase de dibujo, después de todos los eventos step.

**Importante:** Cuando agregas un evento de Dibujo, el dibujo predeterminado del sprite se desactiva. Debes dibujar manualmente el sprite si quieres que sea visible.

**Usos comunes:**
- Renderizado personalizado
- Dibujar barras de salud
- Mostrar texto
- Dibujar formas y efectos
- Elementos de interfaz

---

### Evento de Destrucción
| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_destroy` |
| **Categoría** | Objeto |
| **Icono** | 💥 |
| **Descripción** | Se activa cuando la instancia es destruida |

**Cuándo se activa:** Justo antes de que la instancia sea removida del juego.

**Usos comunes:**
- Crear efectos de explosión
- Soltar objetos
- Reproducir sonido de muerte
- Actualizar puntuación
- Generar partículas

---

### Evento de Ratón
| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_mouse` |
| **Categoría** | Entrada |
| **Icono** | 🖱️ |
| **Descripción** | Se activa en interacciones con el ratón |

**Tipos de eventos de ratón:**
- Botón izquierdo (presionar, soltar, mantenido)
- Botón derecho (presionar, soltar, mantenido)
- Botón central (presionar, soltar, mantenido)
- Ratón entra (cursor entra en la instancia)
- Ratón sale (cursor sale de la instancia)
- Eventos de ratón globales (en cualquier lugar de la pantalla)

**Usos comunes:**
- Botones clicables
- Arrastrar y soltar
- Efectos de hover
- Interacciones de menú

---

### Evento de Alarma
| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_alarm` |
| **Categoría** | Temporización |
| **Icono** | ⏰ |
| **Descripción** | Se activa cuando un temporizador de alarma llega a cero |

**Cuándo se activa:** Cuando la cuenta regresiva de la alarma correspondiente llega a 0.

**Alarmas disponibles:** 12 alarmas independientes (0-11)

**Usos comunes:**
- Generación temporizada
- Acciones retrasadas
- Tiempos de recarga
- Temporización de animación
- Eventos periódicos

---

## Acciones Adicionales (Más allá del Principiante)

### Acciones de Movimiento

#### Mover en Dirección
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `move_direction` |
| **Nombre del Bloque** | `move_direction` |
| **Categoría** | Movimiento |

**Descripción:** Establecer movimiento usando dirección (0-360 grados) y velocidad.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `direction` | Número | Dirección en grados (0=derecha, 90=arriba, 180=izquierda, 270=abajo) |
| `speed` | Número | Velocidad de movimiento |

---

#### Mover Hacia un Punto
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `move_towards_point` |
| **Nombre del Bloque** | `move_towards_point` |
| **Categoría** | Movimiento |

**Descripción:** Moverse hacia una posición específica.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `x` | Número/Expresión | Coordenada X objetivo |
| `y` | Número/Expresión | Coordenada Y objetivo |
| `speed` | Número | Velocidad de movimiento |

---

### Acciones de Temporización

#### Establecer Alarma
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `set_alarm` |
| **Nombre del Bloque** | `set_alarm` |
| **Categoría** | Temporización |
| **Icono** | ⏰ |

**Descripción:** Establecer una alarma para activarse después de un número de pasos.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `alarm` | Número | Número de alarma (0-11) |
| `steps` | Número | Pasos hasta que se active la alarma (a 60 FPS, 60 pasos = 1 segundo) |

**Ejemplo:** Establecer alarma 0 a 180 pasos para un retraso de 3 segundos.

---

### Acciones de Vidas

#### Establecer Vidas
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `set_lives` |
| **Nombre del Bloque** | `lives_set` |
| **Categoría** | Puntuación/Vidas/Salud |
| **Icono** | ❤️ |

**Descripción:** Establecer el número de vidas.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `value` | Número | Valor de vidas |
| `relative` | Booleano | Si es verdadero, suma a las vidas actuales |

---

#### Agregar Vidas
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `add_lives` |
| **Nombre del Bloque** | `lives_add` |
| **Categoría** | Puntuación/Vidas/Salud |
| **Icono** | ➕❤️ |

**Descripción:** Agregar o restar vidas.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `value` | Número | Cantidad a agregar (negativo para restar) |

**Nota:** Cuando las vidas llegan a 0, se activa el evento `no_more_lives`.

---

#### Dibujar Vidas
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `draw_lives` |
| **Nombre del Bloque** | `draw_lives` |
| **Categoría** | Puntuación/Vidas/Salud |
| **Icono** | 🖼️❤️ |

**Descripción:** Mostrar vidas en pantalla.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `x` | Número | Posición X |
| `y` | Número | Posición Y |
| `sprite` | Sprite | Sprite opcional para usar como icono de vida |

---

### Acciones de Salud

#### Establecer Salud
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `set_health` |
| **Nombre del Bloque** | `health_set` |
| **Categoría** | Puntuación/Vidas/Salud |
| **Icono** | 💚 |

**Descripción:** Establecer el valor de salud (0-100).

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `value` | Número | Valor de salud (0-100) |
| `relative` | Booleano | Si es verdadero, suma a la salud actual |

---

#### Agregar Salud
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `add_health` |
| **Nombre del Bloque** | `health_add` |
| **Categoría** | Puntuación/Vidas/Salud |
| **Icono** | ➕💚 |

**Descripción:** Agregar o restar salud.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `value` | Número | Cantidad a agregar (negativo para daño) |

**Nota:** Cuando la salud llega a 0, se activa el evento `no_more_health`.

---

#### Dibujar Barra de Salud
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `draw_health_bar` |
| **Nombre del Bloque** | `draw_health_bar` |
| **Categoría** | Puntuación/Vidas/Salud |
| **Icono** | 📊💚 |

**Descripción:** Dibujar una barra de salud en pantalla.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `x1` | Número | Posición X izquierda |
| `y1` | Número | Posición Y superior |
| `x2` | Número | Posición X derecha |
| `y2` | Número | Posición Y inferior |
| `back_color` | Color | Color de fondo |
| `bar_color` | Color | Color de la barra de salud |

---

### Acciones de Sonido

#### Reproducir Sonido
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `play_sound` |
| **Nombre del Bloque** | `sound_play` |
| **Categoría** | Sonido |
| **Icono** | 🔊 |

**Descripción:** Reproducir un efecto de sonido.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `sound` | Sonido | Recurso de sonido a reproducir |
| `loop` | Booleano | Si el sonido debe repetirse en bucle |

---

#### Reproducir Música
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `play_music` |
| **Nombre del Bloque** | `music_play` |
| **Categoría** | Sonido |
| **Icono** | 🎵 |

**Descripción:** Reproducir música de fondo.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `sound` | Sonido | Recurso de música a reproducir |
| `loop` | Booleano | Si debe repetirse (usualmente verdadero para música) |

---

#### Detener Música
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Acción** | `stop_music` |
| **Nombre del Bloque** | `music_stop` |
| **Categoría** | Sonido |
| **Icono** | 🔇 |

**Descripción:** Detener toda la música en reproducción.

**Parámetros:** Ninguno

---

## Lista Completa de Caracteristicas

### Eventos en el Preset Intermedio

| Evento | Categoría | Descripción |
|--------|-----------|-------------|
| Create | Objeto | Instancia creada |
| Step | Objeto | Cada fotograma |
| Destroy | Objeto | Instancia destruida |
| Draw | Dibujo | Fase de renderizado |
| Keyboard Press | Entrada | Tecla presionada una vez |
| Mouse | Entrada | Interacciones de ratón |
| Collision | Colisión | Superposición de instancias |
| Alarm | Temporización | Temporizador llego a cero |

### Acciones en el Preset Intermedio

| Categoría | Acciones |
|-----------|----------|
| **Movimiento** | Set H/V Speed, Stop, Jump To, Move Direction, Move Towards Point |
| **Instancia** | Create, Destroy |
| **Puntuación** | Set Score, Add Score, Draw Score |
| **Vidas** | Set Lives, Add Lives, Draw Lives |
| **Salud** | Set Health, Add Health, Draw Health Bar |
| **Sala** | Next, Previous, Restart, Go To, If Next/Previous Exists |
| **Temporización** | Set Alarm |
| **Sonido** | Play Sound, Play Music, Stop Music |
| **Salida** | Show Message, Execute Code |

---

## Ejemplo: Juego de Disparos con Vidas

### Objeto Jugador

**Create:**
- Set Lives: 3

**Keyboard Press (Espacio):**
- Create Instance: obj_bullet en (x, y-20)
- Set Alarm: 0 a 15 (tiempo de recarga)

**Colisión con obj_enemy:**
- Add Lives: -1
- Play Sound: snd_hurt
- Jump to Position: (320, 400)

**No More Lives:**
- Show Message: "Game Over!"
- Restart Room

### Objeto Enemigo

**Create:**
- Set Alarm: 0 a 60

**Alarm 0:**
- Create Instance: obj_enemy_bullet en (x, y+20)
- Set Alarm: 0 a 60 (repetir)

**Colisión con obj_bullet:**
- Add Score: 100
- Play Sound: snd_explosion
- Destroy Instance: self

---

## Actualización a Presets Avanzados

Cuando necesites más características, considera:
- **Preset Plataformas** - Gravedad, salto, mecanicas de plataforma
- **Preset Completo** - Todos los eventos y acciones disponibles

---

## Ver Tambien

- [Preset Principiante](Beginner-Preset_es) - Comienza aquí si eres nuevo
- [Referencia Completa de Acciones](Full-Action-Reference_es) - Lista completa de acciones
- [Referencia de Eventos](Event-Reference_es) - Lista completa de eventos
- [Eventos y Acciones](Events-and-Actions_es) - Conceptos básicos
