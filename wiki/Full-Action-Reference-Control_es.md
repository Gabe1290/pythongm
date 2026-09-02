# Control

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Comprobar si vacío

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `check_empty` |
| **Icono** | 🔍 |
| **Categoría** | Control |

Verdadero cuando (x, y) está libre de colisiones. Usa con start_block/end_block para condicionar la(s) acción(es) siguiente(s), al estilo GM

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `self.x` | Posición X a comprobar (expresión permitida, p. ej. self.x + 32) |
| `y` | Texto | `self.y` | Posición Y a comprobar (expresión permitida, p. ej. self.y + 32) |
| `relative` | Sí/No | No | Tratar X/Y como desplazamientos desde la posición de esta instancia en lugar de coordenadas absolutas; opcional |
| `objects` | Elección | `solid` | Qué instancias cuentan como ocupantes de la posición; Opciones: `solid`, `all` |

### Comentario

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `comment` |
| **Icono** | ⚠️ |
| **Categoría** | Control |

Un comentario en la lista de acciones (sin efecto en ejecución)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `text` | Texto | — | Texto de comentario libre; opcional |

### Si no

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `else_action` |
| **Icono** | ⚡ |
| **Categoría** | Control |

Marca la rama «si no» de una condición

*Parámetros:* ninguno

### Fin de bloque

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `end_block` |
| **Icono** | 📁 |
| **Categoría** | Control |

Terminar un bloque de acciones

*Parámetros:* ninguno

### Ejecutar código

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `execute_code` |
| **Icono** | 📜 |
| **Categoría** | Control |

Ejecutar un bloque de código Python integrado

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `code` | Código | — | Código Python a evaluar respecto a la instancia |

### Ejecutar script

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `execute_script` |
| **Icono** | 📜 |
| **Categoría** | Control |

Ejecutar uno de los scripts del proyecto

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `script` | Script | — | Nombre del script del proyecto a ejecutar |
| `arg0` | Texto | — | Disponible en el script como argument0; opcional |
| `arg1` | Texto | — | Disponible en el script como argument1; opcional |
| `arg2` | Texto | — | Disponible en el script como argument2; opcional |
| `arg3` | Texto | — | Disponible en el script como argument3; opcional |
| `arg4` | Texto | — | Disponible en el script como argument4; opcional |

### Salir del evento

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `exit_event` |
| **Icono** | 🚪 |
| **Categoría** | Control |

Detener la ejecución de las acciones restantes en este evento

*Parámetros:* ninguno

### Si se puede empujar

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_can_push` |
| **Icono** | 📦 |
| **Categoría** | Control |

Comprobar si se puede empujar una caja/objeto en la dirección actual (estilo Sokoban)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `direction` | Elección | `facing` | Dirección a comprobar para el empuje; Opciones: `facing` |
| `object_type` | Texto | `box` | Tipo de objeto empujado |
| `then_action` | Elección | `push_and_move` | Acción si el empuje es posible; Opciones: `push_and_move`, `none` |
| `else_action` | Elección | `stop_movement` | Acción si el empuje está bloqueado; Opciones: `stop_movement`, `none` |

### Si colisión

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_collision` |
| **Icono** | ❓💥 |
| **Categoría** | Control |

Condición: verdadero si la instancia colisionaría en el desplazamiento (x, y)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Desplazamiento horizontal a comprobar |
| `y` | Número | `0` | Desplazamiento vertical a comprobar |
| `object` | Texto | `any` | «any», «solid» o un nombre de objeto; Opciones: `any`, `solid`; opcional |
| `not_flag` | Sí/No | No | Negar el resultado; opcional |

### Si colisión en

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_collision_at` |
| **Icono** | 🎯 |
| **Categoría** | Control |

Comprobar una colisión en una posición

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `self.x + 32` | Expresión de la posición X |
| `y` | Texto | `self.y` | Expresión de la posición Y |
| `object_type` | Elección | `any` | Tipo de objeto a comprobar; Opciones: `any`, `solid` |
| `then_actions` | Lista de acciones | — | Acciones si se encuentra colisión |
| `else_actions` | Lista de acciones | — | Acciones si no hay colisión |

### Si condición

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_condition` |
| **Icono** | ❓ |
| **Categoría** | Control |

Comprobación condicional con acciones entonces/si no

*Parámetros:* ninguno

### Si el objeto existe

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `if_object_exists` |
| **Icono** | ❓ |
| **Categoría** | Control |

Condición: verdadero si existe al menos una instancia del objeto

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Tipo de objeto a comprobar |
| `not_flag` | Sí/No | No | Negar el resultado (actuar cuando el objeto NO existe); opcional |

### Repetir

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `repeat` |
| **Icono** | 🔁 |
| **Categoría** | Control |

Repetir la acción/el bloque siguiente N veces

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `times` | Número | `10` | Número de repeticiones |
| `actions` | Lista de acciones | — | Acciones a repetir |

### Establecer variable

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_variable` |
| **Icono** | 📝 |
| **Categoría** | Control |

Establecer una variable de instancia o global

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `variable` | Texto | — | Nombre de la variable |
| `value` | Texto | `0` | Valor (número, cadena o expresión) |
| `scope` | Elección | `self` | Ámbito de la variable; Opciones: `self`, `other`, `global` |
| `relative` | Sí/No | No | Sumar al valor actual en lugar de reemplazarlo |

### Inicio de bloque

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `start_block` |
| **Icono** | 📂 |
| **Categoría** | Control |

Iniciar un bloque de acciones (para agrupar)

*Parámetros:* ninguno

### Comprobar probabilidad

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_chance` |
| **Icono** | 🎲❓ |
| **Categoría** | Control |

Condición: verdadero con probabilidad 1 entre «sides»

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `sides` | Número | `6` | Una probabilidad de 1 entre N de ser verdadero |

### Comprobar expresión

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_expression` |
| **Icono** | ❓ |
| **Categoría** | Control |

Comprobar si una expresión es verdadera

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `expression` | Texto | — | Expresión a evaluar (verdadero si >= 0.5) |
| `then_actions` | Lista de acciones | — | Acciones si verdadero |
| `else_actions` | Lista de acciones | — | Acciones si falso |

### Hacer una pregunta

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_question` |
| **Icono** | ❓💬 |
| **Categoría** | Control |

Condición: mostrar un diálogo sí/no; verdadero si el usuario responde sí

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `question` | Texto | `Continue?` | Pregunta mostrada al jugador |

### Comprobar variable

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `test_variable` |
| **Icono** | ❓ |
| **Categoría** | Control |

Comprobar el valor de una variable de instancia o global

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `variable` | Texto | — | Nombre de la variable |
| `value` | Texto | `0` | Valor a comparar |
| `scope` | Elección | `self` | Ámbito de la variable; Opciones: `self`, `other`, `global` |
| `operation` | Elección | `equal` | Operador de comparación; Opciones: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (8)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (25)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (16)
- [Particles](Full-Action-Reference-Particles_es) (8)
- [Réseau](Full-Action-Reference-Network-Actions_es) (15)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
