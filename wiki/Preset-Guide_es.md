# Guía de Preajustes

*[Español](Preset-Guide_es) | [Volver al Inicio](Home_es)*

PyGameMaker ofrece diferentes preajustes que controlan qué eventos y
acciones están disponibles — **tanto** en la paleta visual de bloques
Blockly como en el panel estructurado Events/Actions ("Add Event"/"Add
Action") que usa cada tutorial de este wiki. Esto ayuda a los
principiantes a enfocarse en las características esenciales mientras
permite a los usuarios experimentados acceder al conjunto completo de
herramientas.

El preajuste de un proyecto se establece de dos formas:
**`Preferences > IDE Edition`** elige el predeterminado para los
proyectos *nuevos* (los proyectos existentes nunca cambian al cambiar
de edición), y **`Tools > Configure Action Blocks...`** cambia el
preajuste del proyecto *actualmente abierto* en cualquier momento. La
edición predeterminada del IDE es Principiante, así que los proyectos
nuevos de una instalación limpia ya inician con el preajuste
Principiante.

## Elige Tu Nivel

| IDE Edition | Ideal Para | Preajuste que usa |
|--------|----------|----------|
| **Principiante** (predeterminada) | Usuarios nuevos | [Preajuste Principiante](Beginner-Preset_es) — movimiento básico, colisiones, puntuación, salas |
| **Avanzado** | Algo de experiencia | [Preajuste Intermedio](Intermediate-Preset_es) — + vidas, salud, sonido, alarmas, movimiento en cuadrícula |
| **Desarrollo** | Usuarios experimentados | El preajuste `full` — todos los eventos y acciones disponibles |

Ten en cuenta que los nombres no se corresponden 1:1: la edición
"Avanzado" usa el preajuste `intermediate` (no existe un preajuste
"avanzado" aparte) — consulta el
[Preajuste Principiante](Beginner-Preset_es)/[Preajuste Intermedio](Intermediate-Preset_es)
para los números exactos y siempre actualizados de eventos y acciones
de cada uno.

---

## Documentación de Preajustes

### Preajustes
| Página | Descripción |
|--------|-------------|
| [Preajuste Principiante](Beginner-Preset_es) | Características esenciales — números exactos en esa página |
| [Preajuste Intermedio](Intermediate-Preset_es) | Añade vidas, salud, sonido, alarmas, movimiento en cuadrícula — números exactos en esa página |

### Referencia
| Página | Descripción |
|--------|-------------|
| [Referencia de Eventos](Event-Reference_es) | Lista completa de todos los eventos |
| [Referencia de Acciones](Full-Action-Reference_es) | Lista completa de todas las acciones |

---

## Ejemplo de Inicio Rápido

Aquí hay un simple juego de recolección de monedas usando solo características de Principiante:

### 1. Crear Objetos
- `obj_player` - El personaje controlable
- `obj_coin` - Objetos coleccionables
- `obj_wall` - Obstáculos sólidos

### 2. Añadir Eventos al Jugador

**Keyboard (Arrow Keys):**
```
Left Arrow  → Set Horizontal Speed: -4
Right Arrow → Set Horizontal Speed: 4
Up Arrow    → Set Vertical Speed: -4
Down Arrow  → Set Vertical Speed: 4
```

**Collision with obj_coin:**
```
Add Score: 10
Destroy Instance: other
```

**Collision with obj_wall:**
```
Stop Movement
```

### 3. Crear una Sala
- Coloca al jugador
- Añade algunas monedas
- Añade paredes alrededor de los bordes

### 4. ¡Ejecuta el Juego!
Presiona el botón Play para probar tu juego.

---

## Consejos para el Éxito

1. **Empieza Simple** - Usa primero el preajuste Principiante
2. **Prueba Frecuentemente** - Ejecuta tu juego con frecuencia para detectar problemas
3. **Una Cosa a la Vez** - Añade características gradualmente
4. **Usa Colisiones** - La mayoría de las mecánicas de juego involucran eventos de colisión
5. **Lee la Documentación** - Consulta las páginas de referencia cuando te atasques

---

## Ver También

- [Inicio](Home_es) - Página principal del wiki
- [Primeros Pasos](Empezar_es) - Instalación y configuración
- [Eventos y Acciones](Eventos_y_Acciones_es) - Conceptos básicos
- [Crea Tu Primer Juego](Primer_Juego_es) - Tutorial
- [Tutorial Breakout](Tutorial-Breakout_es) - Crea un juego Breakout clásico
- [Introducción a la Creación de Juegos](Getting-Started-Breakout_es) - Tutorial completo para principiantes
