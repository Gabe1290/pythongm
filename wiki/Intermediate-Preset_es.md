# Preset Intermedio

*[Inicio](Home_es) | [Guia de Presets](Preset-Guide_es) | [Preset Principiante](Beginner-Preset_es)*

El preset **Intermedio** se basa en el [Preset Principiante](Beginner-Preset_es) anadiendo eventos y acciones mas avanzados. Esta disenado para usuarios que han dominado lo basico y quieren crear juegos mas complejos con caracteristicas como eventos temporizados, sonido, vidas y sistemas de salud.

## Vision General

El preset Intermedio incluye todo lo del Principiante, mas:
- **4 Tipos de Eventos Adicionales** - Dibujo, Destruccion, Raton, Alarma
- **12 Tipos de Acciones Adicionales** - Vidas, Salud, Sonido, Temporizacion y mas opciones de movimiento
- **3 Categorias Adicionales** - Temporizacion, Sonido, Dibujo

---

## Eventos Adicionales (Mas alla del Principiante)

### Evento de Dibujo
| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_draw` |
| **Categoria** | Dibujo |
| **Icono** | 🎨 |
| **Descripcion** | Se activa cuando el objeto necesita ser renderizado |

**Cuando se activa:** Cada fotograma durante la fase de dibujo, despues de todos los eventos step.

**Importante:** Cuando agregas un evento de Dibujo, el dibujo predeterminado del sprite se desactiva. Debes dibujar manualmente el sprite si quieres que sea visible.

**Usos comunes:**
- Renderizado personalizado
- Dibujar barras de salud
- Mostrar texto
- Dibujar formas y efectos
- Elementos de interfaz

---

### Evento de Destruccion
| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_destroy` |
| **Categoria** | Objeto |
| **Icono** | 💥 |
| **Descripcion** | Se activa cuando la instancia es destruida |

**Cuando se activa:** Justo antes de que la instancia sea removida del juego.

**Usos comunes:**
- Crear efectos de explosion
- Soltar objetos
- Reproducir sonido de muerte
- Actualizar puntuacion
- Generar particulas

---

### Evento de Raton
| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_mouse` |
| **Categoria** | Entrada |
| **Icono** | 🖱️ |
| **Descripcion** | Se activa en interacciones con el raton |

**Tipos de eventos de raton:**
- Boton izquierdo (presionar, soltar, mantenido)
- Boton derecho (presionar, soltar, mantenido)
- Boton central (presionar, soltar, mantenido)
- Raton entra (cursor entra en la instancia)
- Raton sale (cursor sale de la instancia)
- Eventos de raton globales (en cualquier lugar de la pantalla)

**Usos comunes:**
- Botones clicables
- Arrastrar y soltar
- Efectos de hover
- Interacciones de menu

---

### Evento de Alarma
| Propiedad | Valor |
|-----------|-------|
| **Nombre del Bloque** | `event_alarm` |
| **Categoria** | Temporizacion |
| **Icono** | ⏰ |
| **Descripcion** | Se activa cuando un temporizador de alarma llega a cero |

**Cuando se activa:** Cuando la cuenta regresiva de la alarma correspondiente llega a 0.

**Alarmas disponibles:** 12 alarmas independientes (0-11)

**Usos comunes:**
- Generacion temporizada
- Acciones retrasadas
- Tiempos de recarga
- Temporizacion de animacion
- Eventos periodicos

---

## Acciones Adicionales (Mas alla del Principiante)

### Acciones de Movimiento

#### Mover en Direccion
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `move_direction` |
| **Nombre del Bloque** | `move_direction` |
| **Categoria** | Movimiento |

**Descripcion:** Establecer movimiento usando direccion (0-360 grados) y velocidad.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `direction` | Numero | Direccion en grados (0=derecha, 90=arriba, 180=izquierda, 270=abajo) |
| `speed` | Numero | Velocidad de movimiento |

---

#### Mover Hacia un Punto
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `move_towards` |
| **Nombre del Bloque** | `move_towards` |
| **Categoria** | Movimiento |

**Descripcion:** Moverse hacia una posicion especifica.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `x` | Numero/Expresion | Coordenada X objetivo |
| `y` | Numero/Expresion | Coordenada Y objetivo |
| `speed` | Numero | Velocidad de movimiento |

---

### Acciones de Temporizacion

#### Establecer Alarma
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `set_alarm` |
| **Nombre del Bloque** | `set_alarm` |
| **Categoria** | Temporizacion |
| **Icono** | ⏰ |

**Descripcion:** Establecer una alarma para activarse despues de un numero de pasos.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `alarm` | Numero | Numero de alarma (0-11) |
| `steps` | Numero | Pasos hasta que se active la alarma (a 60 FPS, 60 pasos = 1 segundo) |

**Ejemplo:** Establecer alarma 0 a 180 pasos para un retraso de 3 segundos.

---

### Acciones de Vidas

#### Establecer Vidas
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `set_lives` |
| **Nombre del Bloque** | `lives_set` |
| **Categoria** | Puntuacion/Vidas/Salud |
| **Icono** | ❤️ |

**Descripcion:** Establecer el numero de vidas.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `value` | Numero | Valor de vidas |
| `relative` | Booleano | Si es verdadero, suma a las vidas actuales |

---

#### Agregar Vidas
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `add_lives` |
| **Nombre del Bloque** | `lives_add` |
| **Categoria** | Puntuacion/Vidas/Salud |
| **Icono** | ➕❤️ |

**Descripcion:** Agregar o restar vidas.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `value` | Numero | Cantidad a agregar (negativo para restar) |

**Nota:** Cuando las vidas llegan a 0, se activa el evento `no_more_lives`.

---

#### Dibujar Vidas
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `draw_lives` |
| **Nombre del Bloque** | `draw_lives` |
| **Categoria** | Puntuacion/Vidas/Salud |
| **Icono** | 🖼️❤️ |

**Descripcion:** Mostrar vidas en pantalla.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `x` | Numero | Posicion X |
| `y` | Numero | Posicion Y |
| `sprite` | Sprite | Sprite opcional para usar como icono de vida |

---

### Acciones de Salud

#### Establecer Salud
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `set_health` |
| **Nombre del Bloque** | `health_set` |
| **Categoria** | Puntuacion/Vidas/Salud |
| **Icono** | 💚 |

**Descripcion:** Establecer el valor de salud (0-100).

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `value` | Numero | Valor de salud (0-100) |
| `relative` | Booleano | Si es verdadero, suma a la salud actual |

---

#### Agregar Salud
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `add_health` |
| **Nombre del Bloque** | `health_add` |
| **Categoria** | Puntuacion/Vidas/Salud |
| **Icono** | ➕💚 |

**Descripcion:** Agregar o restar salud.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `value` | Numero | Cantidad a agregar (negativo para dano) |

**Nota:** Cuando la salud llega a 0, se activa el evento `no_more_health`.

---

#### Dibujar Barra de Salud
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `draw_health_bar` |
| **Nombre del Bloque** | `draw_health_bar` |
| **Categoria** | Puntuacion/Vidas/Salud |
| **Icono** | 📊💚 |

**Descripcion:** Dibujar una barra de salud en pantalla.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `x1` | Numero | Posicion X izquierda |
| `y1` | Numero | Posicion Y superior |
| `x2` | Numero | Posicion X derecha |
| `y2` | Numero | Posicion Y inferior |
| `back_color` | Color | Color de fondo |
| `bar_color` | Color | Color de la barra de salud |

---

### Acciones de Sonido

#### Reproducir Sonido
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `play_sound` |
| **Nombre del Bloque** | `sound_play` |
| **Categoria** | Sonido |
| **Icono** | 🔊 |

**Descripcion:** Reproducir un efecto de sonido.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `sound` | Sonido | Recurso de sonido a reproducir |
| `loop` | Booleano | Si el sonido debe repetirse en bucle |

---

#### Reproducir Musica
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `play_music` |
| **Nombre del Bloque** | `music_play` |
| **Categoria** | Sonido |
| **Icono** | 🎵 |

**Descripcion:** Reproducir musica de fondo.

**Parametros:**
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `sound` | Sonido | Recurso de musica a reproducir |
| `loop` | Booleano | Si debe repetirse (usualmente verdadero para musica) |

---

#### Detener Musica
| Propiedad | Valor |
|-----------|-------|
| **Nombre de Accion** | `stop_music` |
| **Nombre del Bloque** | `music_stop` |
| **Categoria** | Sonido |
| **Icono** | 🔇 |

**Descripcion:** Detener toda la musica en reproduccion.

**Parametros:** Ninguno

---

## Lista Completa de Caracteristicas

### Eventos en el Preset Intermedio

| Evento | Categoria | Descripcion |
|--------|-----------|-------------|
| Create | Objeto | Instancia creada |
| Step | Objeto | Cada fotograma |
| Destroy | Objeto | Instancia destruida |
| Draw | Dibujo | Fase de renderizado |
| Keyboard Press | Entrada | Tecla presionada una vez |
| Mouse | Entrada | Interacciones de raton |
| Collision | Colision | Superposicion de instancias |
| Alarm | Temporizacion | Temporizador llego a cero |

### Acciones en el Preset Intermedio

| Categoria | Acciones |
|-----------|----------|
| **Movimiento** | Set H/V Speed, Stop, Jump To, Move Direction, Move Towards |
| **Instancia** | Create, Destroy |
| **Puntuacion** | Set Score, Add Score, Draw Score |
| **Vidas** | Set Lives, Add Lives, Draw Lives |
| **Salud** | Set Health, Add Health, Draw Health Bar |
| **Sala** | Next, Previous, Restart, Go To, If Next/Previous Exists |
| **Temporizacion** | Set Alarm |
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

**Colision con obj_enemy:**
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

**Colision con obj_bullet:**
- Add Score: 100
- Play Sound: snd_explosion
- Destroy Instance: self

---

## Actualizacion a Presets Avanzados

Cuando necesites mas caracteristicas, considera:
- **Preset Plataformas** - Gravedad, salto, mecanicas de plataforma
- **Preset Completo** - Todos los eventos y acciones disponibles

---

## Ver Tambien

- [Preset Principiante](Beginner-Preset_es) - Comienza aqui si eres nuevo
- [Referencia Completa de Acciones](Full-Action-Reference_es) - Lista completa de acciones
- [Referencia de Eventos](Event-Reference_es) - Lista completa de eventos
- [Eventos y Acciones](Events-and-Actions_es) - Conceptos basicos
