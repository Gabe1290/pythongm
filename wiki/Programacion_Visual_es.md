# Programación Visual

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

[Volver al Inicio](Home_es)

PyGameMaker incluye Google Blockly para la programación visual mediante arrastrar y soltar. Construye la lógica de tu juego conectando bloques, en lugar de escribir código.

---

## Acceder a Blockly

1. Abre un objeto en el Editor de Objetos
2. Haz clic en la pestaña **🧩 Blockly** (junto a Event List y Editor de Código)
3. Aparece el área de trabajo de Blockly con una barra de herramientas a la izquierda

![Las pestañas Event List / Blockly / Editor de Código del Editor de
Objetos — al hacer clic en Blockly cambian las acciones del mismo
evento a la vista de bloques de arrastrar y soltar](images/object-editor.png)

*(El área de trabajo de Blockly en sí es un componente web y no se
capturó aquí — consulta [[Code-Editor_es|Editor de Código]] para ver
cómo luce el Python generado equivalente para el mismo evento.)*

**Los bloques que ves dependen de tu preajuste.**
`Tools > Configure Action Blocks...` (o `Preferences > IDE Edition`, que
establece el preajuste predeterminado para proyectos nuevos) controla
el conjunto de bloques — consulta la [Guía de Preajustes](Preset-Guide_es)
para más detalles. Las tablas de abajo enumeran todos los bloques que
existen en cualquier preajuste; un proyecto concreto puede mostrar menos.

---

## El Área de Trabajo de Blockly

### Barra de Herramientas
El panel izquierdo contiene las categorías de bloques:
- **Events** - Bloques disparadores de eventos
- **Control** - Condiciones, variables y agrupación (los bloques
  condicionales de este proyecto son bloques apilables, no contenedores
  Si/Si no clásicos — consulta "Tipos de Bloque" abajo)
- **Movement** - Bloques de movimiento, velocidad y física
- **Timing** - Alarmas
- **Drawing** - Bloques de texto y formas
- **Score/Lives/Health** - Bloques de estado del juego
- **Instance** - Creación/destrucción de objetos
- **Room** - Navegación entre salas
- **Values** - Bloques de valor (posición, velocidad, puntuación,
  vidas, salud, ratón)
- **Sound** - Reproducción de audio
- **Output** - Mensajes y código Python personalizado
- **Game** - Terminar/reiniciar el juego, tabla de puntuaciones

No existe una categoría separada de Math, Text o Logic — los campos
numéricos/de texto se rellenan directamente en cada bloque, y no existe
un bloque de valor booleano/de comparación genérico. Consulta "Tipos de
Bloque" abajo para ver cómo funcionan las condiciones en su lugar.

### Área de Trabajo
La zona central donde construyes tu programa:
- Arrastrando bloques desde la barra de herramientas
- Conectando bloques entre sí
- Configurando los parámetros de los bloques

### Papelera
Arrastra aquí los bloques no deseados para eliminarlos, o presiona la tecla Suprimir.

---

## Tipos de Bloque

### Bloques de Sombrero (Events)
Los bloques de sombrero tienen una parte superior redondeada e inician una secuencia. Representan eventos:

```
┌─────────────────┐
│ When Create     │
└─────────────────┘
```

### Bloques Apilables (Acciones)
Los bloques apilables tienen muescas que se conectan con otros bloques.
Casi todos los bloques fuera de la categoría Values son bloques
apilables — incluidos los bloques condicionales:

```
├─────────────────┤
│ Set Horizontal Speed [5] │
├─────────────────┤
```

### Bloques de Valor (Values)
Los bloques de valor son redondeados y se insertan en un campo numérico
de otro bloque (p. ej. el campo de velocidad de Move Direction, o el
campo de valor de Set Variable). Este proyecto tiene 9 — X Position, Y
Position, Horizontal Speed, Vertical Speed, Score, Lives, Health, Mouse
X, Mouse Y:

```
( X Position )    ( Score )    ( 100 )
```

No existe un bloque de valor genérico `( speed )` o `( direction )` —
estos conceptos no se rastrean como un valor único en este motor (la
velocidad/dirección de movimiento surgen juntas de Horizontal Speed +
Vertical Speed), y tampoco existe un bloque de valor para variables
personalizadas (léelas en su lugar mediante la comparación de Test
Variable).

### Condiciones — bloques apilables, no contenedores en C
A diferencia de los lenguajes visuales al estilo Scratch, los bloques
If Condition / Test Variable de este proyecto son **bloques apilables
con un único slot "then"**, no contenedores Si/Si no de dos lados, y no
existe un bloque booleano hexagonal para insertar — la comparación se
construye directamente mediante campos en el bloque:

```
┌───────────────────────────────────┐
│ If count of [obj_coin] [==] [0]   │
├───────────────────────────────────┤
│  then [acciones aquí]             │
└───────────────────────────────────┘
```

Para agregar una rama "si no" o ejecutar varias acciones en un lado,
combínalo con otros tres bloques Control:
- **Else** - ejecuta su propio bloque siguiente solo si la
  comprobación anterior fue falsa
- **Start Block** / **End Block** - agrupan varias acciones, para que
  la comprobación anterior (o Else) actúe sobre todo el grupo, no solo
  sobre el bloque siguiente

Este es el mismo flujo condicional plano, al estilo GM80, que también
usa el panel estructurado Events/Actions (consulta [Eventos y
Acciones](Eventos_y_Acciones_es)) — Blockly es una interfaz de
arrastrar y soltar sobre la misma lista de acciones subyacente, no un
modelo de ejecución aparte.

---

## Bloques de Evento

### Evento Create
```
┌─────────────────────┐
│ When Create         │
├─────────────────────┤
│ [acciones aquí]      │
└─────────────────────┘
```

### Evento Step
```
┌─────────────────────┐
│ When Step            │
├─────────────────────┤
│ [cada fotograma]      │
└─────────────────────┘
```

### Eventos de Teclado
Existen cuatro bloques de sombrero de teclado separados — Held, Press,
Release y No Key — cada uno con un menú desplegable para el nombre de
la tecla (No Key no tiene uno, ya que se activa cuando nada está
presionado):
```
┌─────────────────────────┐
│ When key [held: left] ▼ │
├─────────────────────────┤
│ [acciones aquí]           │
└─────────────────────────┘
```

### Eventos de Colisión
```
┌────────────────────────────┐
│ When colliding with [obj] ▼│
├────────────────────────────┤
│ [acciones aquí]              │
└────────────────────────────┘
```

---

## Bloques de Movimiento

| Bloque | Descripción |
|------|-------------|
| `Set Horizontal Speed [4]` | Establece la velocidad X |
| `Set Vertical Speed [-5]` | Establece la velocidad Y |
| `Stop Movement` | Pone a cero ambas velocidades |
| `Move [direction ▼] speed [3]` | Se mueve en una de 4 direcciones (o diagonales, o "stop") |
| `Move Free [direction] [speed]` | Se mueve con ángulo y velocidad arbitrarios |
| `Set Speed [5]` | Establece la magnitud de la velocidad, manteniendo la dirección actual |
| `Set Direction [90]` | Establece el ángulo de dirección, manteniendo la velocidad actual |
| `Move Towards x:[100] y:[200] speed:[3]` | Se mueve hacia un punto |
| `Snap to Grid` | Alinea la posición a la cuadrícula |
| `Jump to Position x:[100] y:[200]` | Teletransporte instantáneo |
| `Move Grid [direction]` | Se mueve exactamente una celda de la cuadrícula |
| `Stop if No Keys` / `Check Keys and Move` / `If On Grid` | Bloques auxiliares para movimiento en cuadrícula |
| `Set Gravity` | Aplica una fuerza constante en cada fotograma (hacia abajo o en cualquier dirección) |
| `Set Friction` | Aplica una reducción de velocidad en cada fotograma |
| `Reverse Horizontal` / `Reverse Vertical` | Invierte la dirección X o Y |
| `Bounce` | Rebota en objetos sólidos |
| `Wrap Around Room` | Reaparece por el lado opuesto |
| `Move to Contact` | Se mueve hasta tocar algo |

No existe un bloque "Jump to Start Position" o "Jump to Random
Position" — estas dos acciones solo existen en el panel estructurado,
no en Blockly.

---

## Bloques de Dibujo

| Bloque | Descripción |
|------|-------------|
| `Draw Text [Hola] at x:[10] y:[10]` | Muestra texto |
| `Draw Rectangle from x1,y1 to x2,y2` | Dibuja un rectángulo relleno |
| `Draw Circle at x,y radius [r]` | Dibuja un círculo relleno |
| `Set Sprite [spr]` | Cambia el sprite de la instancia |
| `Set Transparency [0-1]` | Establece el alfa |

No existe un bloque "Draw Sprite en Posición" o "Set Drawing Color" en
Blockly (ambos existen solo en el panel estructurado). Draw Score/Draw
Lives/Draw Health Bar aparecen abajo en Score/Lives/Health, no aquí.

---

## Bloques Score/Lives/Health

| Bloque | Descripción |
|------|-------------|
| `Set Score [100]` | Establece exactamente la puntuación |
| `Add to Score [10]` | Aumenta/disminuye la puntuación |
| `Set Lives [3]` | Establece exactamente las vidas |
| `Add to Lives [-1]` | Aumenta/disminuye las vidas |
| `Set Health [100]` | Establece exactamente la salud |
| `Add to Health [-25]` | Aumenta/disminuye la salud |
| `Draw Score` | Muestra el texto de la puntuación |
| `Draw Lives` | Muestra las vidas como iconos repetidos |
| `Draw Health Bar` | Muestra la salud como una barra de dos colores |

---

## Bloques de Instancia

| Bloque | Descripción |
|------|-------------|
| `Create Instance [obj] at x:[100] y:[200]` | Crea una nueva instancia |
| `Destroy Instance` | Se elimina a sí misma |
| `Destroy Other` | Elimina la instancia en colisión (en un evento Collision) |
| `Change Instance [obj]` | Se transforma en otro tipo de objeto |
| `If Can Push [obj] [direction]` | Comprobación de empuje al estilo Sokoban |

No existe un bloque "destruir todos de un tipo" o "crear en esta posición".

---

## Bloques de Sala

| Bloque | Descripción |
|------|-------------|
| `Next Room` | Pasa a la sala siguiente |
| `Previous Room` | Vuelve a la sala anterior |
| `Restart Room` | Reinicia la sala actual |
| `Go to Room [room_name]` | Salta a una sala específica |
| `If Next Room Exists` / `If Previous Room Exists` | Protege la navegación entre varias salas |

---

## Bloques de Sonido

| Bloque | Descripción |
|------|-------------|
| `Play Sound [snd]` | Reproduce un efecto de sonido |
| `Play Music [music]` | Reproduce música de fondo (en bucle) |
| `Stop Music` | Detiene la música |

No existe un bloque "Stop Sound" (por sonido) o "Detener todos los
sonidos" en Blockly (solo Stop Music, que detiene específicamente la
música).

---

## Bloques de Control

| Bloque | Descripción |
|------|-------------|
| `If count of [obj] [==] [0] then...` | Compara el número de instancias de un objeto; ejecuta el bloque/los bloques siguientes si es verdadero |
| `If variable [var] [==] [value] then...` | Compara una variable personalizada; ejecuta el bloque/los bloques siguientes si es verdadero |
| `Set Variable [name] to [value]` | Asigna una variable de instancia o global |
| `Check Empty at x,y` | Verdadero si una posición no tiene colisión (movimiento en cuadrícula) |
| `Exit Event` | Detiene las acciones restantes de este evento |
| `Else` | Ejecuta su propio bloque siguiente si la comprobación anterior fue falsa |
| `Start Block` / `End Block` | Agrupa varias acciones bajo un Test/Else |

---

## Bloques de Output y Game

| Bloque | Descripción |
|------|-------------|
| `Show Message [text]` | Muestra un mensaje emergente |
| `Execute Code` | Ejecuta Python real (consulta [Eventos y Acciones](Eventos_y_Acciones_es)) |
| `End Game` | Cierra el juego |
| `Restart Game` | Reinicia desde la primera sala |
| `Show Highscore` / `Clear Highscore` | Muestra o borra la tabla de puntuaciones |

---

## Bloques de Valor

Bloques de valor — insértalos en un campo numérico de otro bloque:

| Bloque | Descripción |
|------|-------------|
| `X Position` | La coordenada X de esta instancia |
| `Y Position` | La coordenada Y de esta instancia |
| `Horizontal Speed` | La velocidad X de esta instancia |
| `Vertical Speed` | La velocidad Y de esta instancia |
| `Score` | La puntuación actual |
| `Lives` | Las vidas actuales |
| `Health` | La salud actual |
| `Mouse X` / `Mouse Y` | La posición actual del ratón |

---

## Ejemplo: Movimiento del Jugador

```
┌──────────────────────────┐
│ When key [held: left]    │
├──────────────────────────┤
│ Set Horizontal Speed [-4]│
└──────────────────────────┘

┌──────────────────────────┐
│ When key [held: right]   │
├──────────────────────────┤
│ Set Horizontal Speed [4] │
└──────────────────────────┘

┌──────────────────────────┐
│ When key [no key]        │
├──────────────────────────┤
│ Set Horizontal Speed [0] │
└──────────────────────────┘
```

---

## Ejemplo: Recolectar Monedas

```
┌─────────────────────────────┐
│ When colliding with obj_coin│
├─────────────────────────────┤
│ Add to Score [10]           │
├─────────────────────────────┤
│ Play Sound [snd_coin]       │
├─────────────────────────────┤
│ Destroy Other                │
└─────────────────────────────┘
```

---

## Consejos

1. **Comienza con Events** - Siempre empieza con un bloque Event (bloque de sombrero)
2. **Conecta verticalmente** - Los bloques apilables se conectan de arriba hacia abajo
3. **Usa los colores** - Los colores de los bloques indican su categoría
4. **Clic derecho** - Accede a Duplicar, Eliminar y Ayuda
5. **Zoom** - Usa la rueda del ratón o los controles de zoom para programas grandes
6. **Cambia al panel estructurado** - Todo lo que Blockly puede hacer
   corresponde a una acción en la pestaña Events del panel estructurado,
   pero no al revés (p. ej. Jump to Start/Random Position y Stop Sound
   por sonido no tienen bloque de Blockly) — en esos casos usa el panel
   estructurado en lugar de Blockly.

---

## Próximos Pasos

- [[Eventos_y_Acciones_es]] - Ve el equivalente como lista de acciones
- [[Primer_Juego_es]] - Construye un juego completo
- [[Editor_Objetos_es]] - Dónde está integrado Blockly
- [[Preset-Guide_es]] - Qué bloques están disponibles en tu proyecto
