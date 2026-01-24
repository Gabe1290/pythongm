# Introduccion a la Creacion de Videojuegos con PyGameMaker

*[Home_es](Home_es) | [Beginner-Preset_es](Beginner-Preset_es) | [English](Getting-Started-Breakout) | [Francais](Getting-Started-Breakout_fr)*

**Por el Equipo de PyGameMaker**

---

En este tutorial, aprenderemos los conceptos basicos de la creacion de videojuegos con PyGameMaker. Como es un software relativamente completo con muchas funcionalidades, nos centraremos unicamente en aquellas que nos ayudaran durante este tutorial.

Crearemos un juego sencillo estilo Breakout que se vera asi:

![Concepto del Juego Breakout](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

Este tutorial es para ti, incluso si no tienes conocimientos de programacion, ya que PyGameMaker permite a los principiantes crear juegos facilmente sin importar su nivel de habilidad.

Muy bien, comencemos a disenar nuestro juego!

---

## Paso 1: Primeros Pasos

Comienza abriendo PyGameMaker. Deberias ver la interfaz principal con el panel de **Assets** en el lado izquierdo, listando diferentes categorias de recursos: Sprites, Sounds, Backgrounds, Fonts, Objects y Rooms.

Antes que nada, en un videojuego, lo primero que el jugador nota es lo que ve en pantalla. Esta es en realidad la base de un juego: un juego sin graficos no existe (o es un caso muy especial). Por lo tanto, comenzaremos insertando imagenes en nuestro juego, que seran la representacion grafica de los objetos que el jugador vera en pantalla. En la terminologia del desarrollo de juegos, estas imagenes se llaman **Sprites**.

---

## Paso 2: Creando los Sprites

### 2.1 Creando el Sprite de la Paleta

1. Haz clic derecho en la carpeta **Sprites** en la parte superior de la columna izquierda
2. Haz clic en **Create Sprite**
3. Se abrira una ventana llamada **Sprite Properties** - aqui es donde definiras todas las caracteristicas de tu sprite
4. Usa el editor integrado para dibujar un rectangulo horizontal (aproximadamente 64x16 pixeles) en un color que te guste
5. **Importante:** Haz clic en **Center** para establecer el origen en el centro de tu sprite
   > El origen de un sprite es su punto central, sus coordenadas X:0 e Y:0. Estas son sus coordenadas base.
6. Cambia el nombre de tu sprite usando el campo de texto en la parte superior, e ingresa `spr_paddle`
   > Esto no tiene impacto tecnico - es solo para ayudarte a navegar mejor tus archivos una vez que tengas mas. Puedes elegir cualquier nombre que quieras; esto es solo un ejemplo.
7. Haz clic en **OK**

Acabas de crear tu primer sprite! Esta es tu paleta, el objeto que el jugador controlara para atrapar la pelota.

### 2.2 Creando el Sprite de la Pelota

Continuemos y agreguemos mas sprites. Repite el mismo proceso:

1. Haz clic derecho en **Sprites** → **Create Sprite**
2. Dibuja un circulo pequeno (aproximadamente 16x16 pixeles)
3. Haz clic en **Center** para establecer el origen
4. Nombralo `spr_ball`
5. Haz clic en **OK**

### 2.3 Creando los Sprites de los Ladrillos

Necesitamos tres tipos de ladrillos. Crealos uno por uno:

**Primer Ladrillo (Destructible):**
1. Crea un nuevo sprite
2. Dibuja un rectangulo (aproximadamente 48x24 pixeles) - usa un color brillante como rojo
3. Haz clic en **Center**, nombralo `spr_brick_1`
4. Haz clic en **OK**

**Segundo Ladrillo (Destructible):**
1. Crea un nuevo sprite
2. Dibuja un rectangulo (mismo tamano) - usa un color diferente como azul
3. Haz clic en **Center**, nombralo `spr_brick_2`
4. Haz clic en **OK**

**Tercer Ladrillo (Muro Indestructible):**
1. Crea un nuevo sprite
2. Dibuja un rectangulo (mismo tamano) - usa un color mas oscuro como gris
3. Haz clic en **Center**, nombralo `spr_brick_3`
4. Haz clic en **OK**

Ahora deberias tener todos los sprites para nuestro juego:
- `spr_paddle` - La paleta del jugador
- `spr_ball` - La pelota que rebota
- `spr_brick_1` - Primer ladrillo destructible
- `spr_brick_2` - Segundo ladrillo destructible
- `spr_brick_3` - Ladrillo de muro indestructible

> **Nota:** En los juegos, generalmente hay dos fuentes principales de renderizado grafico: **Sprites** y **Backgrounds**. Eso es todo lo que compone lo que ves en pantalla. Un Background es, como su nombre sugiere, una imagen de fondo.

---

## Paso 3: Entendiendo Objetos y Eventos

Que dijimos al principio? Lo primero que el jugador nota es lo que ve en pantalla. Nos hemos encargado de eso con nuestros sprites. Pero un juego hecho solo de imagenes no es un juego - es una pintura! Ahora pasaremos a la siguiente etapa: los **Objects**.

Un Object es una entidad en tu juego que puede tener comportamientos, responder a eventos e interactuar con otros objetos. El sprite es solo la representacion visual; el objeto es lo que le da vida.

### Como Funciona la Logica del Juego

Todo en la programacion de juegos sigue este patron: **Si esto sucede, entonces ejecuto aquello.**

- Si el jugador presiona una tecla, entonces hago esto
- Si esta variable es igual a este valor, entonces hago aquello
- Si dos objetos colisionan, entonces algo sucede

Esto es lo que llamamos **Events** y **Actions** en PyGameMaker:
- **Events** = Cosas que pueden suceder (presion de tecla, colision, temporizador, etc.)
- **Actions** = Cosas que quieres hacer cuando ocurren los eventos (mover, destruir, cambiar puntaje, etc.)

---

## Paso 4: Creando el Objeto de la Paleta

Creemos el objeto que el jugador controlara: la paleta.

### 4.1 Crear el Objeto

1. Haz clic derecho en la carpeta **Objects** → **Create Object**
2. Nombralo `obj_paddle`
3. En el menu desplegable **Sprite**, selecciona `spr_paddle` - ahora nuestro objeto tiene una apariencia visual!
4. Marca la casilla **Solid** (lo necesitaremos para las colisiones)

### 4.2 Programando el Movimiento

En un juego Breakout, necesitamos mover la paleta para evitar que la pelota escape por la parte inferior. La controlaremos con el teclado.

**Moverse a la Derecha:**
1. Haz clic en **Add Event** → **Keyboard** → **Right Arrow**
2. Desde el panel de acciones a la derecha, agrega la accion **Set Horizontal Speed**
3. Establece el **value** en `5`
4. Haz clic en **OK**

Esto significa: "Cuando se presione la tecla Flecha Derecha, establecer la velocidad horizontal en 5 (moviéndose a la derecha)."

**Moverse a la Izquierda:**
1. Haz clic en **Add Event** → **Keyboard** → **Left Arrow**
2. Agrega la accion **Set Horizontal Speed**
3. Establece el **value** en `-5`
4. Haz clic en **OK**

**Detenerse Cuando se Sueltan las Teclas:**

Si probamos ahora, la paleta seguiria moviendose incluso despues de soltar la tecla! Arreglemos eso:

1. Haz clic en **Add Event** → **Keyboard Release** → **Right Arrow**
2. Agrega la accion **Set Horizontal Speed** con valor `0`
3. Haz clic en **OK**

4. Haz clic en **Add Event** → **Keyboard Release** → **Left Arrow**
5. Agrega la accion **Set Horizontal Speed** con valor `0`
6. Haz clic en **OK**

Ahora nuestra paleta se mueve cuando se presionan las teclas y se detiene cuando se sueltan. Hemos terminado con este objeto por ahora!

---

## Paso 5: Creando el Objeto del Ladrillo Muro

Creemos un ladrillo muro indestructible - esto formara los limites de nuestra area de juego.

1. Crea un nuevo objeto llamado `obj_brick_3`
2. Asigna el sprite `spr_brick_3`
3. Marca la casilla **Solid**

La pelota rebotara en este ladrillo. Como es solo un muro, no necesitamos ningun evento - solo necesita ser solido. Haz clic en **OK** para guardar.

---

## Paso 6: Creando el Objeto de la Pelota

Ahora creemos la pelota, el elemento esencial de nuestro juego.

### 6.1 Crear el Objeto

1. Crea un nuevo objeto llamado `obj_ball`
2. Asigna el sprite `spr_ball`
3. Marca la casilla **Solid**

### 6.2 Movimiento Inicial

Queremos que la pelota se mueva por si sola desde el inicio. Demosle una velocidad y direccion inicial.

1. Haz clic en **Add Event** → **Create**
   > El evento Create ejecuta acciones cuando el objeto aparece en el juego, es decir, cuando entra en la escena.
2. Agrega la accion **Set Horizontal Speed** con valor `4`
3. Agrega la accion **Set Vertical Speed** con valor `-4`
4. Haz clic en **OK**

Esto le da a la pelota un movimiento diagonal (derecha y arriba) al inicio del juego.

### 6.3 Rebotando en la Paleta

Necesitamos que la pelota rebote cuando golpee la paleta.

1. Haz clic en **Add Event** → **Collision** → selecciona `obj_paddle`
   > Este evento se activa cuando la pelota colisiona con la paleta.
2. Agrega la accion **Reverse Vertical**
   > Esto invierte la direccion vertical, haciendo que la pelota rebote.
3. Haz clic en **OK**

### 6.4 Rebotando en los Muros

La misma operacion para los ladrillos muro:

1. Haz clic en **Add Event** → **Collision** → selecciona `obj_brick_3`
2. Agrega la accion **Reverse Vertical**
3. Agrega la accion **Reverse Horizontal**
   > Agregamos ambas porque la pelota podria golpear el muro desde diferentes angulos.
4. Haz clic en **OK**

---

## Paso 7: Probando Nuestro Progreso - Creando una Room

Despues de los Sprites y Objects, llegan las **Rooms**. Una room es donde el juego tiene lugar: es un mapa, un nivel. Aqui es donde colocas todos los elementos de tu juego, donde organizas lo que aparecera en pantalla.

### 7.1 Crear la Room

1. Haz clic derecho en **Rooms** → **Create Room**
2. Nombrala `room_game`

### 7.2 Coloca tus Objetos

Ahora coloca tus objetos usando el raton:
- **Clic izquierdo** para colocar un objeto
- **Clic derecho** para eliminar un objeto

Selecciona el objeto a colocar desde el menu desplegable en el editor de room.

**Construye tu nivel:**
1. Coloca instancias de `obj_brick_3` alrededor de los bordes (arriba, izquierda, derecha) - deja la parte inferior abierta!
2. Coloca `obj_paddle` en el centro inferior
3. Coloca `obj_ball` en algun lugar del medio

### 7.3 Prueba el Juego!

Haz clic en el boton **Play** (flecha verde) en la barra de herramientas. Esto te permite probar tu juego en cualquier momento.

Ya puedes divertirte haciendo rebotar la pelota en los muros y la paleta!

Es minimo, pero ya es un buen comienzo - tienes la base de tu juego!

---

## Paso 8: Agregando Ladrillos Destructibles

Agreguemos algunos ladrillos para romper, para hacer nuestro juego mas divertido.

### 8.1 Primer Ladrillo Destructible

1. Crea un nuevo objeto llamado `obj_brick_1`
2. Asigna el sprite `spr_brick_1`
3. Marca **Solid**

Agregaremos el comportamiento para destruirse a si mismo cuando sea golpeado por la pelota:

1. Haz clic en **Add Event** → **Collision** → selecciona `obj_ball`
2. Agrega la accion **Destroy Instance** con objetivo **self**
   > Esta accion elimina un objeto durante el juego - aqui, el ladrillo mismo.
3. Haz clic en **OK**

Y asi de simple, tienes tu nuevo ladrillo destructible!

### 8.2 Segundo Ladrillo Destructible (Usando Parent)

Ahora crearemos un segundo ladrillo destructible, pero sin tener que reprogramarlo. Lo haremos un "clon" usando la funcion **Parent**.

1. Crea un nuevo objeto llamado `obj_brick_2`
2. Asigna el sprite `spr_brick_2`
3. Marca **Solid**
4. En el menu desplegable **Parent**, selecciona `obj_brick_1`

Que significa esto? Simplemente que lo que programamos en `obj_brick_1` sera heredado por `obj_brick_2`, sin tener que reproducirlo nosotros mismos. La relacion padre-hijo permite que los objetos compartan comportamientos!

Haz clic en **OK** para guardar.

### 8.3 Hacer que la Pelota Rebote en los Nuevos Ladrillos

Vuelve a abrir `obj_ball` haciendo doble clic en el, y agrega eventos de colision para nuestros nuevos ladrillos:

1. Haz clic en **Add Event** → **Collision** → selecciona `obj_brick_1`
2. Agrega la accion **Reverse Vertical**
3. Haz clic en **OK**

4. Haz clic en **Add Event** → **Collision** → selecciona `obj_brick_2`
5. Agrega la accion **Reverse Vertical**
6. Haz clic en **OK**

---

## Paso 9: Game Over - Reiniciando la Room

Necesitamos reiniciar el nivel si la pelota escapa de la pantalla (si el jugador no logra atraparla).

En `obj_ball`:

1. Haz clic en **Add Event** → **Other** → **Outside Room**
2. Agrega la accion **Restart Room**
   > Esta accion reinicia la room actual durante el juego.
3. Haz clic en **OK**

---

## Paso 10: Diseno Final del Nivel

Ahora coloca todo en tu room para crear tu nivel final de Breakout:

1. Abre `room_game`
2. Organiza los muros `obj_brick_3` alrededor de la parte superior y los lados
3. Coloca filas de `obj_brick_1` y `obj_brick_2` en patrones en la parte superior
4. Mantén `obj_paddle` en el centro inferior
5. Coloca `obj_ball` encima de la paleta

**Ejemplo de disposicion:**
```
[3][3][3][3][3][3][3][3][3][3]
[3][1][1][2][2][1][1][2][2][3]
[3][2][2][1][1][2][2][1][1][3]
[3][1][1][2][2][1][1][2][2][3]
[3]                        [3]
[3]                        [3]
[3]       (pelota)         [3]
[3]                        [3]
[3]       [paleta]         [3]
```

---

## Felicitaciones!

Tu juego Breakout esta completo! Ahora puedes disfrutar de tu trabajo jugando el juego que acabas de crear!

Tambien puedes refinarlo aun mas, como agregar:
- **Efectos de sonido** para rebotes y destruccion de ladrillos
- **Seguimiento de puntaje** usando la accion Add Score
- **Tipos adicionales de ladrillos** con diferentes comportamientos
- **Multiples niveles** con diferentes disposiciones

---

## Resumen de lo que Aprendiste

| Concepto | Descripcion |
|----------|-------------|
| **Sprites** | Imagenes visuales que representan objetos en tu juego |
| **Objects** | Entidades del juego con comportamientos, combinando sprites con eventos y acciones |
| **Events** | Disparadores que ejecutan acciones (Create, Keyboard, Collision, etc.) |
| **Actions** | Operaciones a realizar (Move, Destroy, Bounce, etc.) |
| **Solid** | Propiedad que habilita la deteccion de colisiones |
| **Parent** | Permite que los objetos hereden comportamientos de otros objetos |
| **Rooms** | Niveles del juego donde colocas instancias de objetos |

---

## Resumen de Objetos

| Objeto | Sprite | Solid | Eventos |
|--------|--------|-------|---------|
| `obj_paddle` | `spr_paddle` | Si | Keyboard (Left/Right), Keyboard Release |
| `obj_ball` | `spr_ball` | Si | Create, Collision (paddle, bricks), Outside Room |
| `obj_brick_1` | `spr_brick_1` | Si | Collision (ball) - Se destruye a si mismo |
| `obj_brick_2` | `spr_brick_2` | Si | Hereda de `obj_brick_1` |
| `obj_brick_3` | `spr_brick_3` | Si | Ninguno (solo un muro) |

---

## Ver Tambien

- [Beginner-Preset_es](Beginner-Preset_es) - Eventos y acciones disponibles para principiantes
- [Event-Reference_es](Event-Reference_es) - Lista completa de todos los eventos
- [Full-Action-Reference_es](Full-Action-Reference_es) - Lista completa de todas las acciones
- [Tutorial-Breakout_es](Tutorial-Breakout_es) - Version mas corta de este tutorial

---

Ahora estas iniciado en los conceptos basicos de la creacion de videojuegos con PyGameMaker. Es tu turno de crear tus propios juegos!
