# Tutoriales

> **Selecciona tu idioma / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorials) | [Français](Tutorials_fr) | [Deutsch](Tutorials_de) | [Italiano](Tutorials_it) | [Español](Tutorials_es) | [Português](Tutorials_pt) | [Slovenščina](Tutorials_sl) | [Українська](Tutorials_uk) | [Русский](Tutorials_ru)

---

¡Bienvenido a la página de Tutoriales de PyGameMaker! Aquí encontrarás guías paso a paso para ayudarte a crear tus primeros juegos usando programación visual.

---

## Tutoriales para Principiantes

Estos tutoriales están pensados para usuarios nuevos en el desarrollo
de juegos y usan exclusivamente los eventos y acciones del
[Preajuste Principiante](Beginner-Preset_es) (verificado contra
`config/blockly_config.py`'s `get_beginner()`, que enumera exactamente
estos dos tutoriales por nombre).

### Juegos Clásicos

| Tutorial | Descripción | Habilidades Aprendidas |
|----------|-------------|------------------------|
| [**Pong**](Tutorial-Pong_es) | Crea un clásico juego Pong para dos jugadores | Entrada de teclado, detección de colisiones, seguimiento de puntuación, variables globales |
| [**Breakout**](Tutorial-Breakout_es) | Construye un juego tipo rompeladrillos | Destrucción de objetos, mecánicas de rebote, sistema de vidas |

## Tutoriales Intermedios

Estos cuatro tutoriales requieren el
[Preajuste Intermedio](Intermediate-Preset_es) — la mecánica de empuje
de Sokoban (`if_can_push`) y el movimiento en cuadrícula de Sokoban/
Laberinto (`move_snap_to_grid`/`move_grid`) no están en el preajuste
Principiante. Si tu proyecto todavía usa el preajuste Principiante
predeterminado (los proyectos nuevos empiezan ahí — consulta la
[Guía de Preajustes](Preset-Guide_es)), cámbialo primero mediante
`Tools > Configure Action Blocks...`, de lo contrario las acciones de
estos tutoriales no aparecerán en ninguno de los dos editores.

| Tutorial | Descripción | Habilidades Aprendidas |
|----------|-------------|------------------------|
| [**Sokoban**](Tutorial-Sokoban_es) | Crea un juego de puzzle de empujar cajas | Movimiento en cuadrícula, mecánicas de empuje, condiciones de victoria |
| [**Laberinto**](Tutorial-Maze_es) | Navega por los pasillos hasta la salida | Movimiento fluido, colisión con paredes, coleccionables, temporizador |
| [**Platformer**](Tutorial-Platformer_es) | Corre, salta y colecciona monedas | Gravedad, mecánicas de salto, colisión con plataformas |
| [**Aterrizaje Lunar**](Tutorial-LunarLander_es) | Aterriza una nave en la luna | Física de impulso, gestión de combustible, control de velocidad |

### Guías Completas

| Tutorial | Descripción | Habilidades Aprendidas |
|----------|-------------|------------------------|
| [**Introducción a la Creación de Juegos**](Getting-Started-Breakout_es) | Una guía completa para principiantes que cubre todos los conceptos básicos de PyGameMaker a través de la construcción de un juego Breakout | Sprites, objetos, eventos, acciones, objetos padre, salas |

---

## Lo Que Aprenderás

Cada tutorial enseña conceptos importantes del desarrollo de juegos:

### Movimiento y Física
- Establecer velocidad y dirección de objetos
- Usar gravedad y fricción
- Rebotar objetos contra paredes y otros objetos

### Entrada del Usuario
- Manejar entrada de teclado (presionar, soltar, mantener)
- Responder a clics y movimientos del ratón

### Lógica del Juego
- Usar eventos para desencadenar acciones
- Gestionar el estado del juego con variables
- Rastrear puntuación, vidas y salud

### Retroalimentación Visual
- Dibujar texto y formas
- Mostrar puntuación y estado
- Crear efectos visuales

---

## Niveles de Dificultad de los Tutoriales

| Nivel | Descripción | Requisitos Previos |
|-------|-------------|-------------------|
| **Principiante** | Conceptos básicos, juegos simples | Ninguno - ¡Comienza aquí! |
| **Intermedio** | Mecánicas más complejas | Completa al menos un tutorial para principiantes |
| **Avanzado** | Juegos con todas las características | Cómodo con conceptos intermedios |

---

## Comenzar

1. **Instala PyGameMaker** - Sigue las [instrucciones de instalación](Home_es#installation)
2. **Elige un Tutorial** - Comienza con [Pong](Tutorial-Pong_es) o [Breakout](Tutorial-Breakout_es)
3. **Establece tu Preset** - Principiante para Pong/Breakout, Intermedio
   para Sokoban/Laberinto/Platformer/Aterrizaje Lunar (consulta las
   tablas anteriores)
4. **Sigue Adelante** - Trabaja cuidadosamente en cada paso
5. **Experimenta** - ¡Prueba las sugerencias de mejora al final!

---

## Consejos para el Éxito

- **Lee cada paso cuidadosamente** antes de implementarlo
- **Prueba frecuentemente** - Ejecuta tu juego después de cada adición importante
- **No saltes pasos** - Cada paso se construye sobre el anterior
- **Usa las secciones de solución de problemas** si algo no funciona
- **Experimenta** - ¡Una vez que completes un tutorial, intenta modificarlo!

---

## Ver También

- [Preset para Principiantes](Beginner-Preset_es) - Descripción general de características para principiantes
- [Referencia de Eventos](Event-Reference_es) - Documentación completa de eventos
- [Referencia Completa de Acciones](Full-Action-Reference_es) - Todas las acciones disponibles
- [Preguntas Frecuentes](FAQ_es) - Preguntas frecuentes
