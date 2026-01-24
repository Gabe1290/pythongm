# Guía de Preajustes

*[Español](Preset-Guide_es) | [Volver al Inicio](Home_es)*

PyGameMaker ofrece diferentes preajustes que controlan qué eventos y acciones están disponibles. Esto ayuda a los principiantes a enfocarse en las características esenciales mientras permite a los usuarios experimentados acceder al conjunto completo de herramientas.

## Elige Tu Nivel

| Preajuste | Ideal Para | Características |
|-----------|------------|-----------------|
| [**Principiante**](Beginner-Preset_es) | Nuevos en desarrollo de juegos | 4 eventos, 17 acciones - Movimiento, colisiones, puntuación, salas |
| [**Intermedio**](Intermediate-Preset_es) | Algo de experiencia | +4 eventos, +12 acciones - Vidas, salud, sonido, alarmas, dibujo |
| **Avanzado** | Usuarios experimentados | Todos los 40+ eventos y acciones disponibles |

---

## Documentación de Preajustes

### Preajustes
| Página | Descripción |
|--------|-------------|
| [Preajuste Principiante](Beginner-Preset_es) | 4 eventos, 17 acciones - Características esenciales |
| [Preajuste Intermedio](Intermediate-Preset_es) | +4 eventos, +12 acciones - Vidas, salud, sonido |

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

**Teclado (Teclas de Flecha):**
```
Flecha Izquierda  → Establecer Velocidad Horizontal: -4
Flecha Derecha    → Establecer Velocidad Horizontal: 4
Flecha Arriba     → Establecer Velocidad Vertical: -4
Flecha Abajo      → Establecer Velocidad Vertical: 4
```

**Colisión con obj_coin:**
```
Añadir Puntuación: 10
Destruir Instancia: other
```

**Colisión con obj_wall:**
```
Detener Movimiento
```

### 3. Crear una Sala
- Coloca al jugador
- Añade algunas monedas
- Añade paredes alrededor de los bordes

### 4. ¡Ejecuta el Juego!
Presiona el botón Jugar para probar tu juego.

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
- [Primeros Pasos](Primeros_Pasos_es) - Instalación y configuración
- [Eventos y Acciones](Eventos_y_Acciones_es) - Conceptos básicos
- [Crea Tu Primer Juego](Primer_Juego_es) - Tutorial
