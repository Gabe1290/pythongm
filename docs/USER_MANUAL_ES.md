# Manual de Usuario del IDE PyGameMaker

**Version 1.0.0-rc.6**
**Un IDE de desarrollo de juegos visual inspirado en GameMaker para crear juegos 2D con Python**

---

## Tabla de Contenidos

1. [Introduccion](#1-introduccion)
2. [Instalacion y Configuracion](#2-instalacion-y-configuracion)
3. [Vista General del IDE](#3-vista-general-del-ide)
4. [Trabajar con Proyectos](#4-trabajar-con-proyectos)
5. [Sprites](#5-sprites)
6. [Sonidos](#6-sonidos)
7. [Fondos](#7-fondos)
8. [Objetos](#8-objetos)
9. [Habitaciones](#9-habitaciones)
10. [Referencia de Eventos](#10-referencia-de-eventos)
11. [Referencia de Acciones](#11-referencia-de-acciones)
12. [Pruebas y Ejecucion de Juegos](#12-pruebas-y-ejecucion-de-juegos)
13. [Exportar Juegos](#13-exportar-juegos)
14. [Programacion Visual con Blockly](#14-programacion-visual-con-blockly)
15. [Soporte para Robot Thymio](#15-soporte-para-robot-thymio)
16. [Configuracion y Preferencias](#16-configuracion-y-preferencias)
17. [Atajos de Teclado](#17-atajos-de-teclado)
18. [Tutoriales](#18-tutoriales)
19. [Solucion de Problemas](#19-solucion-de-problemas)

---

## 1. Introduccion

PyGameMaker es un IDE educativo de desarrollo de juegos inspirado en GameMaker. Te permite crear juegos 2D de forma visual usando un sistema de arrastrar y soltar de eventos/acciones, sin necesidad de escribir codigo. Esta disenado con dos objetivos en mente:

- **Ensenar desarrollo de juegos** de forma visual a traves de una interfaz intuitiva
- **Ensenar programacion en Python** a traves del codigo fuente abierto del IDE

PyGameMaker usa PySide6 (Qt) para la interfaz del IDE y Pygame para el motor de ejecucion del juego. Los juegos se pueden exportar como ejecutables independientes, aplicaciones moviles o juegos web HTML5.

### Caracteristicas Principales

- Programacion visual de eventos/acciones (mas de 80 acciones integradas)
- Editor de sprites con soporte de animacion
- Editor de habitaciones con colocacion de instancias, capas de tiles y desplazamiento de fondo
- Vista previa del juego en tiempo real con F5
- Exportacion a EXE de Windows, movil (Android/iOS via Kivy), HTML5 y robots Thymio
- Integracion con Google Blockly para bloques de codigo visual
- Simulador de robot educativo Thymio
- Interfaz multilingue (mas de 8 idiomas)
- Temas oscuro y claro

---

## 2. Instalacion y Configuracion

### Requisitos

- Python 3.10 o superior
- PySide6
- Pygame
- Pillow (PIL)

### Instalar Dependencias

```bash
pip install PySide6 pygame Pillow
```

### Dependencias Opcionales

Para funciones de exportacion:

```bash
pip install pyinstaller    # For EXE export
pip install kivy           # For mobile export
pip install buildozer      # For Android builds
pip install jinja2         # For code generation templates
```

### Ejecutar el IDE

```bash
python main.py
```

La ventana del IDE se abre con dimensiones predeterminadas de 1400x900 pixeles. La posicion y tamano de la ventana se guardan entre sesiones.

---

## 3. Vista General del IDE

### Diseno de la Ventana

El IDE usa un diseno de tres paneles:

```
+-------------------+---------------------------+------------------+
|   Árbol de        |      Área del editor      |   Propiedades    |
|   recursos        |      (Panel central)      |   (Panel der.)   |
|   (Panel izq.)    |                           |                  |
|                   |   Editores con pestañas   |   Propiedades    |
|   - Sprites       |   para sprites, objetos   |   contextuales   |
|   - Sonidos       |   y salas                 |                  |
|   - Fondos        |                           |                  |
|   - Objetos       |                           |                  |
|   - Salas         |                           |                  |
|   - Scripts       |                           |                  |
|   - Fuentes       |                           |                  |
+-------------------+---------------------------+------------------+
|                       Barra de estado                            |
+------------------------------------------------------------------+
```

- **Panel Izquierdo (Arbol de Recursos):** Muestra todos los recursos del proyecto organizados por tipo. Haz doble clic en un recurso para abrirlo en el editor.
- **Panel Central (Area del Editor):** Espacio de trabajo con pestanas donde editas sprites, objetos y habitaciones. Se muestra una pestana de bienvenida por defecto.
- **Panel Derecho (Propiedades):** Muestra propiedades sensibles al contexto del editor activo. Se puede colapsar.
- **Barra de Estado:** Muestra el estado de la operacion actual y el nombre del proyecto.

### Barra de Menu

#### Menu Archivo

| Comando | Atajo | Descripcion |
|---------|-------|-------------|
| New Project... | Ctrl+N | Crear un nuevo proyecto |
| Open Project... | Ctrl+O | Abrir un proyecto existente |
| Save Project | Ctrl+S | Guardar el proyecto actual |
| Save Project As... | Ctrl+Shift+S | Guardar en una nueva ubicacion |
| Recent Projects | | Submenu de hasta 10 proyectos recientes |
| Export as HTML5... | | Exportar juego como un solo archivo HTML |
| Export as Zip... | | Empaquetar proyecto como archivo ZIP |
| Export to Kivy... | | Exportar para despliegue movil |
| Export Project... | Ctrl+E | Abrir el dialogo de exportacion |
| Open Zip Project... | | Abrir un proyecto empaquetado en ZIP |
| Auto-Save to Zip | | Alternar auto-guardado a ZIP |
| Enable Auto-Save | | Alternar guardado automatico del proyecto |
| Auto-Save Settings... | | Configurar intervalo de auto-guardado |
| Project Settings... | | Abrir configuracion del proyecto |
| Exit | Ctrl+Q | Cerrar el IDE |

#### Menu Editar

| Comando | Atajo | Descripcion |
|---------|-------|-------------|
| Undo | Ctrl+Z | Deshacer la ultima accion |
| Redo | Ctrl+Y | Rehacer la ultima accion deshecha |
| Cut | Ctrl+X | Cortar seleccion |
| Copy | Ctrl+C | Copiar seleccion |
| Paste | Ctrl+V | Pegar desde el portapapeles |
| Duplicate | Ctrl+D | Duplicar elementos seleccionados |
| Find... | Ctrl+F | Abrir dialogo de busqueda |
| Find and Replace... | Ctrl+H | Abrir dialogo de buscar y reemplazar |

#### Menu Recursos

| Comando | Descripcion |
|---------|-------------|
| Import Sprite... | Importar imagenes de sprite (PNG, JPG, BMP, GIF) |
| Import Sound... | Importar archivos de audio |
| Import Background... | Importar imagenes de fondo |
| Create Object... | Crear un nuevo objeto de juego |
| Create Room... (Ctrl+R) | Crear una nueva habitacion de juego |
| Create Script... | Crear un nuevo archivo de script |
| Create Font... | Crear un nuevo recurso de fuente |
| Import Object Package... | Importar un paquete .gmobj |
| Import Room Package... | Importar un paquete .gmroom |

#### Menu Compilar

| Comando | Atajo | Descripcion |
|---------|-------|-------------|
| Test Game | F5 | Ejecutar juego en modo de prueba |
| Debug Game | F6 | Ejecutar juego con salida de depuracion |
| Build Game... | F7 | Abrir configuracion de compilacion |
| Build and Run | F8 | Compilar y ejecutar inmediatamente |
| Export Game... | | Exportar juego compilado |

#### Menu Herramientas

| Comando | Descripcion |
|---------|-------------|
| Preferences... | Abrir preferencias del IDE |
| Asset Manager... | Abrir ventana de gestion de recursos |
| Configure Action Blocks... | Configurar bloques de Blockly |
| Configure Thymio Blocks... | Configurar bloques del robot Thymio |
| Validate Project | Verificar errores en el proyecto |
| Clean Project | Eliminar archivos temporales |
| Migrate to Modular Structure | Actualizar formato del proyecto |
| Language | Cambiar idioma de la interfaz |
| Thymio Programming | Submenu de programacion del robot |

#### Menu Ayuda

| Comando | Atajo | Descripcion |
|---------|-------|-------------|
| Documentación | F1 | Abrir documentación de ayuda |
| Documentación en línea | | Abrir el manual de usuario en línea en GitHub |
| Tutoriales | | Abrir recursos de tutoriales |
| Acerca de PyGameMaker | | Información de versión y licencia |

### Barra de Herramientas

La barra de herramientas proporciona acceso rapido a acciones comunes (de izquierda a derecha):

| Boton | Accion |
|-------|--------|
| New | Crear nuevo proyecto |
| Open | Abrir proyecto existente |
| Save | Guardar proyecto actual |
| Test | Ejecutar juego (F5) |
| Debug | Depurar juego (F6) |
| Export | Exportar juego |
| Import Sprite | Importar una imagen de sprite |
| Import Sound | Importar un archivo de audio |
| Thymio | Agregar evento de robot Thymio |

### Arbol de Recursos

El arbol de recursos en el panel izquierdo organiza los recursos del proyecto en categorias:

**Recursos Multimedia:**
- **Sprites** - Imagenes y tiras de animacion para objetos del juego
- **Sounds** - Efectos de sonido y archivos de musica
- **Backgrounds** - Imagenes de fondo y conjuntos de tiles

**Logica del Juego:**
- **Objects** - Definiciones de objetos del juego con eventos y acciones
- **Rooms** - Niveles/escenas del juego con instancias colocadas

**Recursos de Codigo:**
- **Scripts** - Archivos de codigo
- **Fonts** - Recursos de fuentes personalizadas

**Operaciones del menu contextual:**
- Clic derecho en un encabezado de categoria para crear o importar recursos
- Clic derecho en un recurso para renombrar, duplicar, eliminar, exportar o ver propiedades
- Clic derecho en un sprite para exportarlo como archivo PNG
- Doble clic en un recurso para abrirlo en el editor
- Los recursos de habitaciones se pueden reordenar (Mover Arriba/Abajo/Inicio/Final)

---

## 4. Trabajar con Proyectos

### Crear un Nuevo Proyecto

1. Elige **File > New Project** (Ctrl+N)
2. Ingresa un **Nombre de Proyecto**
3. Elige una **Ubicacion** para la carpeta del proyecto
4. Selecciona una **Plantilla** (opcional):
   - **Empty Project** - Un proyecto en blanco
   - **Platform Game Template** - Preconfigurado para juegos de plataformas
   - **Top-Down Game Template** - Preconfigurado para juegos de vista superior
5. Haz clic en **Create Project**

### Estructura del Proyecto

```
MyProject/
├── project.json          # Main project file
├── sprites/              # Sprite images and metadata
│   ├── player.png
│   └── player.json
├── objects/              # Object definitions
│   └── obj_player.json
├── rooms/                # Room layout data
│   └── room_start.json
├── sounds/               # Audio files and metadata
├── backgrounds/          # Background images
└── thumbnails/           # Auto-generated previews
```

### Guardar Proyectos

- **Ctrl+S** guarda el proyecto en su ubicacion actual
- **Ctrl+Shift+S** guarda en una nueva ubicacion
- El **auto-guardado** se puede activar en File > Enable Auto-Save
- Configura el intervalo de auto-guardado en File > Auto-Save Settings

### Abrir Proyectos

- **Ctrl+O** abre una carpeta de proyecto
- Los proyectos recientes se listan en **File > Recent Projects**
- Los proyectos ZIP se pueden abrir con **File > Open Zip Project**

---

## 5. Sprites

Los sprites son las imagenes visuales usadas por los objetos del juego. Pueden ser imagenes estaticas o tiras de animacion con multiples cuadros.

### Crear un Sprite

1. Clic derecho en **Sprites** en el arbol de recursos y elige **Import Sprite...**
2. Selecciona un archivo de imagen (PNG, JPG, BMP o GIF)
3. El sprite aparece en el arbol de recursos y se abre en el editor de sprites

### Editor de Sprites

El editor de sprites tiene cuatro areas principales:

- **Panel de Herramientas (Izquierda):** Herramientas de dibujo
- **Lienzo (Centro):** El area de edicion con zoom y cuadricula
- **Paleta de Colores (Derecha):** Colores de primer plano/fondo y muestras
- **Linea de Tiempo de Cuadros (Abajo):** Gestion de cuadros de animacion

#### Herramientas de Dibujo

| Herramienta | Atajo | Descripcion |
|-------------|-------|-------------|
| Pencil | P | Dibujo estandar de pixeles |
| Eraser | E | Eliminar pixeles (hacer transparente) |
| Color Picker | I | Muestrear un color del lienzo |
| Fill | G | Relleno por inundacion de regiones conectadas |
| Line | L | Dibujar lineas rectas |
| Rectangle | R | Dibujar rectangulos (contorno o relleno) |
| Ellipse | O | Dibujar elipses (contorno o relleno) |
| Selection | S | Seleccionar, cortar, copiar, pegar regiones |

#### Tamano del Pincel

El tamano del pincel va de 1 a 16 pixeles y afecta a las herramientas Pencil, Eraser y Line.

#### Modo Relleno

Alterna entre modo contorno y relleno para las herramientas Rectangle y Ellipse usando el boton **Filled**.

#### Paleta de Colores

- **Clic izquierdo** en la muestra de primer plano para elegir un color de dibujo
- **Clic derecho** en la muestra de fondo para elegir un color secundario
- El **boton X** intercambia los colores de primer plano y fondo
- Haz clic en cualquier color de la paleta rapida para seleccionarlo
- Doble clic en una muestra de la paleta para personalizarla
- Selector de color RGBA completo con soporte de alfa (transparencia)

### Cuadros de Animacion

Los sprites pueden tener multiples cuadros de animacion organizados como una tira horizontal.

**Controles de la Linea de Tiempo de Cuadros:**
- **+ (Agregar):** Agregar un nuevo cuadro en blanco
- **D (Duplicar):** Copiar el cuadro actual
- **- (Eliminar):** Eliminar el cuadro actual (minimo 1 cuadro)
- **Play/Stop:** Vista previa de la animacion
- El contador de cuadros muestra cuadro actual/total

**Propiedades de Animacion:**
- **Frame Count:** Numero de cuadros de animacion
- **Animation Speed:** Cuadros por segundo (predeterminado: 10 FPS)
- **Animation Type:** single, strip_h (horizontal), strip_v (vertical) o grid

**Soporte de GIF Animados:** Importa archivos GIF animados directamente. Todos los cuadros se extraen automaticamente con manejo de transparencia.

### Origen del Sprite

El punto de origen es la posicion de anclaje usada para la colocacion y rotacion en el juego.

**Posiciones Predefinidas:**
- Superior-Izquierda (0, 0)
- Superior-Centro
- Centro (predeterminado para la mayoria de sprites)
- Centro-Inferior
- Inferior-Izquierda
- Inferior-Derecha
- Personalizado (entrada manual de X/Y)

El origen se muestra como un punto de mira en el lienzo.

### Controles del Lienzo

- **Ctrl+Rueda del Raton:** Acercar/alejar (1x a 64x)
- **Alternar Cuadricula:** Mostrar/ocultar cuadricula de pixeles (visible a 4x de zoom y superior)
- **Espejo H/V:** Voltear el cuadro actual horizontal o verticalmente
- **Redimensionar/Escalar:** Cambiar dimensiones del sprite con opciones de escala o redimensionamiento del lienzo
- **Exportar PNG…:** Exportar la imagen actual como archivo PNG (también disponible mediante clic derecho en el lienzo)

### Propiedades del Sprite (Guardadas)

| Propiedad | Descripcion |
|-----------|-------------|
| name | Nombre del recurso |
| file_path | Ruta al archivo de tira PNG |
| width | Ancho total de la tira |
| height | Altura del cuadro |
| frame_width | Ancho de un solo cuadro |
| frame_height | Altura de un solo cuadro |
| frames | Numero de cuadros |
| animation_type | single, strip_h, strip_v, grid |
| speed | FPS de animacion |
| origin_x | Coordenada X del origen |
| origin_y | Coordenada Y del origen |

---

## 6. Sonidos

Los sonidos son archivos de audio usados para efectos de sonido y musica de fondo.

### Importar Sonidos

1. Clic derecho en **Sounds** en el arbol de recursos y elige **Import Sound...**
2. Selecciona un archivo de audio (WAV, OGG, MP3)
3. El sonido se agrega al proyecto

### Propiedades del Sonido

| Propiedad | Descripcion |
|-----------|-------------|
| name | Nombre del recurso de sonido |
| file_path | Ruta al archivo de audio |
| kind | "sound" (efecto) o "music" (transmision) |
| volume | Volumen predeterminado (0.0 a 1.0) |

Los **efectos de sonido** se cargan en memoria para reproduccion instantanea. Los archivos de **musica** se transmiten desde el disco y solo uno puede reproducirse a la vez.

---

## 7. Fondos

Los fondos son imagenes usadas detras de los objetos del juego. Tambien pueden servir como conjuntos de tiles para niveles basados en tiles.

### Importar Fondos

1. Clic derecho en **Backgrounds** en el arbol de recursos y elige **Import Background...**
2. Selecciona un archivo de imagen

### Configuracion del Conjunto de Tiles

Los fondos se pueden configurar como conjuntos de tiles con estas propiedades:

| Propiedad | Descripcion |
|-----------|-------------|
| tile_width | Ancho de cada tile (predeterminado: 16) |
| tile_height | Altura de cada tile (predeterminado: 16) |
| h_offset | Desplazamiento horizontal al primer tile |
| v_offset | Desplazamiento vertical al primer tile |
| h_sep | Espaciado horizontal entre tiles |
| v_sep | Espaciado vertical entre tiles |
| use_as_tileset | Activar modo de conjunto de tiles |

---

## 8. Objetos

Los objetos definen entidades del juego con propiedades, eventos y acciones. Cada objeto puede tener un sprite para representacion visual y contiene manejadores de eventos que definen su comportamiento.

### Crear un Objeto

1. Clic derecho en **Objects** en el arbol de recursos y elige **Create Object...**
2. Ingresa un nombre para el objeto
3. El objeto se abre en el editor de objetos

### Propiedades del Objeto

| Propiedad | Predeterminado | Descripcion |
|-----------|----------------|-------------|
| Sprite | Ninguno | El sprite visual a mostrar |
| Visible | Si | Si las instancias se dibujan |
| Solid | No | Si el objeto bloquea el movimiento |
| Persistent | No | Si las instancias sobreviven cambios de habitacion |
| Depth | 0 | Orden de dibujo (mayor = detras, menor = delante) |
| Parent | Ninguno | Objeto padre para herencia |

### Objetos Padre

Los objetos pueden heredar de un objeto padre. Los objetos hijos reciben todos los eventos de colision del padre. Esto es util para crear jerarquias como:

```
obj_enemy (parent - has collision with obj_player)
  ├── obj_enemy_melee (inherits collision handling)
  └── obj_enemy_ranged (inherits collision handling)
```

### Agregar Eventos

1. Abre el editor de objetos
2. Haz clic en **Add Event** en el panel de eventos
3. Selecciona un tipo de evento de la lista (ver [Referencia de Eventos](#10-referencia-de-eventos))
4. El evento aparece en el arbol de eventos

### Agregar Acciones a Eventos

1. Selecciona un evento en el arbol de eventos
2. Haz clic en **Add Action** o clic derecho y elige **Add Action**
3. Elige un tipo de accion de la lista categorizada
4. Configura los parametros de la accion en el dialogo
5. Haz clic en OK para agregar la accion

Las acciones se ejecutan en orden de arriba a abajo cuando el evento se activa.

### Logica Condicional

Las acciones soportan flujo condicional si/sino:

1. Agrega una accion condicional (p. ej., **If Collision At**, **Test Variable**)
2. Agrega una accion **Start Block** (llave de apertura)
3. Agrega acciones que se ejecutan cuando la condicion es verdadera
4. Agrega una accion **Else** (opcional)
5. Agrega un **Start Block** para la rama sino
6. Agrega acciones para el caso falso
7. Agrega acciones **End Block** para cerrar cada bloque

Ejemplo de secuencia de acciones:
```
If Collision At (self.x, self.y + 1, "solid")
  Start Block
    Set Vertical Speed (0)
  End Block
Else
  Start Block
    Set Vertical Speed (vspeed + 0.5)
  End Block
```

### Ver Codigo

Marca la opcion **View Code** en el editor de objetos para ver el codigo Python generado para todos los eventos y acciones. Esto es util para entender como las acciones visuales se traducen a codigo.

---

## 9. Habitaciones

Las habitaciones son las escenas o niveles de tu juego. Cada habitacion tiene un fondo, instancias de objetos colocadas y capas de tiles opcionales.

### Crear una Habitacion

1. Clic derecho en **Rooms** en el arbol de recursos y elige **Create Room...**
2. Ingresa un nombre para la habitacion
3. La habitacion se abre en el editor de habitaciones

### Propiedades de la Habitacion

| Propiedad | Predeterminado | Descripcion |
|-----------|----------------|-------------|
| Width | 1024 | Ancho de la habitacion en pixeles |
| Height | 768 | Altura de la habitacion en pixeles |
| Background Color | #87CEEB (azul cielo) | Color de relleno detras de todo |
| Background Image | Ninguno | Imagen de fondo opcional |
| Persistent | No | Preservar estado al salir |

### Colocar Instancias

1. Haz clic en un objeto en la **Paleta de Objetos** (lado izquierdo del editor de habitaciones)
2. Haz clic en el lienzo de la habitacion para colocar una instancia
3. Continua haciendo clic para colocar mas copias
4. Selecciona instancias colocadas para moverlas o configurarlas

### Propiedades de la Instancia

Cuando seleccionas una instancia colocada:

| Propiedad | Rango | Descripcion |
|-----------|-------|-------------|
| X Position | 0-9999 | Posicion horizontal |
| Y Position | 0-9999 | Posicion vertical |
| Visible | Si/No | Visibilidad de la instancia |
| Rotation | 0-360 | Rotacion en grados |
| Scale X | 10%-1000% | Escala horizontal |
| Scale Y | 10%-1000% | Escala vertical |

### Cuadricula y Ajuste

- **Alternar Cuadricula:** Haz clic en el boton de cuadricula para mostrar/ocultar la cuadricula de colocacion
- **Alternar Ajuste:** Haz clic en el boton de ajuste para activar/desactivar el ajuste a cuadricula
- **Tamano de Cuadricula:** 32x32 pixeles por defecto (configurable en Preferencias)

### Operaciones con Instancias

| Accion | Atajo | Descripcion |
|--------|-------|-------------|
| Mover | Arrastrar | Mover instancia a nueva posicion |
| Seleccion Multiple | Shift+Clic | Agregar/quitar de la seleccion |
| Seleccion por Area | Arrastrar area vacia | Seleccionar todas las instancias en el rectangulo |
| Eliminar | Tecla Delete | Eliminar instancias seleccionadas |
| Cortar | Ctrl+X | Cortar al portapapeles |
| Copiar | Ctrl+C | Copiar al portapapeles |
| Pegar | Ctrl+V | Pegar desde el portapapeles |
| Duplicar | Ctrl+D | Duplicar instancias seleccionadas |
| Limpiar Todo | Boton de barra | Eliminar todas las instancias (con confirmacion) |

### Capas de Fondo

Las habitaciones soportan hasta 8 capas de fondo (indexadas 0-7), cada una con configuraciones independientes:

| Propiedad | Descripcion |
|-----------|-------------|
| Background Image | Que recurso de fondo usar |
| Visible | Mostrar/ocultar la capa |
| Foreground | Si es verdadero, se dibuja delante de las instancias |
| Tile Horizontal | Repetir a lo ancho de la habitacion |
| Tile Vertical | Repetir a lo alto de la habitacion |
| H Scroll Speed | Pixeles de desplazamiento horizontal por cuadro |
| V Scroll Speed | Pixeles de desplazamiento vertical por cuadro |
| Stretch | Escalar para llenar toda la habitacion |
| X / Y Offset | Desplazamiento de posicion de la capa |

### Capas de Tiles

Para niveles basados en tiles:

1. Haz clic en **Tile Palette...** para abrir el selector de tiles
2. Elige un conjunto de tiles (fondo marcado como conjunto de tiles)
3. Establece el ancho y alto del tile
4. Haz clic en un tile en la paleta para seleccionarlo
5. Haz clic en la habitacion para colocar tiles
6. Selecciona una **Capa** (0-7) para los tiles

### Orden de las Habitaciones

Las habitaciones se ejecutan en el orden en que aparecen en el arbol de recursos. La primera habitacion es la habitacion inicial.

- Clic derecho en una habitacion y usa **Move Up/Down/Top/Bottom** para reordenar
- Usa las acciones **Next Room** y **Previous Room** para navegar entre habitaciones en tiempo de ejecucion

### Sistema de Vistas

Las habitaciones soportan hasta 8 vistas de camara (como GameMaker):

| Propiedad | Descripcion |
|-----------|-------------|
| Visible | Activar/desactivar esta vista |
| View X/Y | Posicion de la camara en la habitacion |
| View W/H | Tamano del viewport de la camara |
| Port X/Y | Posicion en pantalla para esta vista |
| Port W/H | Tamano en pantalla para esta vista |
| Follow Object | Objeto a seguir con la camara |
| H/V Border | Margen de desplazamiento alrededor del objeto seguido |
| H/V Speed | Velocidad maxima de desplazamiento de la camara (-1 = instantaneo) |

---

## 10. Referencia de Eventos

Los eventos definen cuando se ejecutan las acciones. Cada evento se activa bajo condiciones especificas.

### Eventos de Objeto

| Evento | Categoria | Se Activa Cuando |
|--------|-----------|------------------|
| Create | Object | La instancia se crea por primera vez |
| Destroy | Object | La instancia es destruida |
| Step | Step | Cada cuadro del juego (~60 FPS) |
| Begin Step | Step | Inicio de cada cuadro, antes de la fisica |
| End Step | Step | Final de cada cuadro, despues de las colisiones |

### Eventos de Colision

| Evento | Categoria | Se Activa Cuando |
|--------|-----------|------------------|
| Collision With... | Collision | Dos instancias se superponen (selecciona objeto objetivo) |

### Eventos de Teclado

| Evento | Categoria | Se Activa Cuando |
|--------|-----------|------------------|
| Keyboard | Input | La tecla se mantiene presionada continuamente (para movimiento suave) |
| Keyboard Press | Input | La tecla se presiona por primera vez (una vez por pulsacion) |
| Keyboard Release | Input | La tecla se suelta |

**Teclas Disponibles:** A-Z, 0-9, teclas de flecha, Space, Enter, Escape, Tab, Backspace, Delete, F1-F12, teclas del teclado numerico, Shift, Ctrl, Alt, y mas (mas de 76 teclas en total).

**Eventos Especiales de Teclado:**
- **No Key** - Se activa cuando no se presiona ninguna tecla
- **Any Key** - Se activa cuando se presiona cualquier tecla

### Eventos de Raton

| Evento | Categoria | Se Activa Cuando |
|--------|-----------|------------------|
| Mouse Left/Right/Middle Press | Input | Boton presionado sobre la instancia |
| Mouse Left/Right/Middle Release | Input | Boton soltado sobre la instancia |
| Mouse Left/Right/Middle Down | Input | Boton mantenido sobre la instancia |
| Mouse Enter | Input | El cursor entra en el cuadro delimitador de la instancia |
| Mouse Leave | Input | El cursor sale del cuadro delimitador de la instancia |
| Mouse Wheel Up/Down | Input | Rueda de desplazamiento sobre la instancia |
| Global Mouse Press | Input | Boton presionado en cualquier lugar de la habitacion |
| Global Mouse Release | Input | Boton soltado en cualquier lugar de la habitacion |

### Eventos de Temporizacion

| Evento | Categoria | Se Activa Cuando |
|--------|-----------|------------------|
| Alarm 0-11 | Timing | La cuenta regresiva de la alarma llega a cero (12 alarmas independientes) |

### Eventos de Dibujo

| Evento | Categoria | Se Activa Cuando |
|--------|-----------|------------------|
| Draw | Drawing | La instancia se dibuja (reemplaza el dibujo predeterminado del sprite) |
| Draw GUI | Drawing | Se dibuja encima de todo (para HUD, marcador) |

### Eventos de Habitacion

| Evento | Categoria | Se Activa Cuando |
|--------|-----------|------------------|
| Room Start | Room | La habitacion comienza (despues de los eventos de creacion) |
| Room End | Room | La habitacion esta a punto de terminar |

### Eventos del Juego

| Evento | Categoria | Se Activa Cuando |
|--------|-----------|------------------|
| Game Start | Game | El juego se inicializa (solo en la primera habitacion) |
| Game End | Game | El juego se esta cerrando |

### Otros Eventos

| Evento | Categoria | Se Activa Cuando |
|--------|-----------|------------------|
| Outside Room | Other | La instancia esta completamente fuera de los limites de la habitacion |
| Intersect Boundary | Other | La instancia toca el borde de la habitacion |
| No More Lives | Other | El valor de vidas llega a 0 o menos |
| No More Health | Other | El valor de salud llega a 0 o menos |
| Animation End | Other | La animacion del sprite llega al ultimo cuadro |
| User Event 0-15 | Other | 16 eventos personalizados activados por codigo |

---

## 11. Referencia de Acciones

Las acciones son los bloques de construccion del comportamiento del juego. Se colocan dentro de eventos y se ejecutan en orden.

### Acciones de Movimiento

| Accion | Parametros | Descripcion |
|--------|------------|-------------|
| Move Grid | direction (left/right/up/down), grid_size (predeterminado: 32) | Mover una unidad de cuadricula en una direccion |
| Set Horizontal Speed | speed (pixeles/cuadro) | Establecer hspeed para movimiento horizontal suave |
| Set Vertical Speed | speed (pixeles/cuadro) | Establecer vspeed para movimiento vertical suave |
| Stop Movement | (ninguno) | Establecer ambas velocidades a cero |
| Move Fixed | directions (8 direcciones), speed | Comenzar a moverse en una direccion fija |
| Move Free | direction (0-360 grados), speed | Moverse en un angulo preciso |
| Move Towards | x, y, speed | Moverse hacia una posicion objetivo |
| Set Gravity | direction (270=abajo), gravity | Aplicar aceleracion constante |
| Set Friction | friction | Aplicar desaceleracion cada cuadro |
| Reverse Horizontal | (ninguno) | Invertir direccion de hspeed |
| Reverse Vertical | (ninguno) | Invertir direccion de vspeed |
| Set Speed | speed | Establecer magnitud del movimiento |
| Set Direction | direction (grados) | Establecer angulo del movimiento |
| Jump to Position | x, y | Teletransportarse a una posicion |
| Jump to Start | (ninguno) | Teletransportarse a la posicion inicial |
| Bounce | (ninguno) | Invertir velocidad en colision |

### Acciones de Cuadricula

| Accion | Parametros | Descripcion |
|--------|------------|-------------|
| Snap to Grid | grid_size | Alinear posicion al punto de cuadricula mas cercano |
| If On Grid | grid_size | Verificar si esta alineado a la cuadricula (condicional) |
| Stop If No Keys | grid_size | Detenerse en la cuadricula cuando se sueltan las teclas de movimiento |

### Acciones de Instancia

| Accion | Parametros | Descripcion |
|--------|------------|-------------|
| Create Instance | object, x, y, relative | Crear una nueva instancia de objeto |
| Destroy Instance | target (self/other) | Eliminar una instancia del juego |
| Change Sprite | sprite | Cambiar el sprite mostrado |
| Set Visible | visible (true/false) | Mostrar u ocultar la instancia |
| Set Scale | scale_x, scale_y | Cambiar tamano de la instancia |

### Acciones de Puntuacion, Vidas y Salud

| Accion | Parametros | Descripcion |
|--------|------------|-------------|
| Set Score | value | Establecer puntuacion a un valor especifico |
| Add to Score | value | Agregar puntos (puede ser negativo) |
| Set Lives | value | Establecer numero de vidas |
| Add Lives | value | Agregar/quitar vidas |
| Set Health | value | Establecer salud (0-100) |
| Add Health | value | Agregar/quitar salud |
| Show Highscore Table | (ninguno) | Mostrar la tabla de puntuaciones maximas |

### Acciones de Habitacion y Juego

| Accion | Parametros | Descripcion |
|--------|------------|-------------|
| Restart Room | (ninguno) | Recargar la habitacion actual |
| Next Room | (ninguno) | Ir a la siguiente habitacion en orden |
| Previous Room | (ninguno) | Ir a la habitacion anterior |
| Go to Room | room | Saltar a una habitacion especifica |
| If Next Room Exists | (ninguno) | Condicional: hay una siguiente habitacion? |
| If Previous Room Exists | (ninguno) | Condicional: hay una habitacion anterior? |
| Restart Game | (ninguno) | Reiniciar desde la primera habitacion |
| End Game | (ninguno) | Cerrar el juego |

### Acciones de Temporizacion

| Accion | Parametros | Descripcion |
|--------|------------|-------------|
| Set Alarm | alarm_number (0-11), steps | Iniciar temporizador de cuenta regresiva (30 pasos = 0.5 seg a 60 FPS) |
| Delay Action | action, delay_frames | Ejecutar una accion despues de un retraso |

### Acciones de Mensajes y Visualizacion

| Accion | Parametros | Descripcion |
|--------|------------|-------------|
| Show Message | message | Mostrar un mensaje emergente |
| Draw Text | text, x, y, color, size | Dibujar texto en pantalla (usar en evento Draw) |
| Draw Rectangle | x1, y1, x2, y2, color, filled | Dibujar un rectangulo |
| Draw Circle | x, y, radius, color, filled | Dibujar un circulo |
| Draw Ellipse | x1, y1, x2, y2, color, filled | Dibujar una elipse |
| Draw Line | x1, y1, x2, y2, color | Dibujar una linea |
| Draw Sprite | sprite_name, x, y, subimage | Dibujar un sprite en una posicion |
| Draw Background | background_name, x, y, tiled | Dibujar una imagen de fondo |
| Draw Score | x, y, caption | Dibujar valor de puntuacion en pantalla |
| Draw Lives | x, y, sprite | Dibujar vidas como iconos de sprite |
| Draw Health Bar | x, y, width, height | Dibujar barra de salud en pantalla |

### Acciones de Sonido

| Accion | Parametros | Descripcion |
|--------|------------|-------------|
| Play Sound | sound, loop | Reproducir un efecto de sonido |
| Stop Sound | sound | Detener un sonido en reproduccion |
| Play Music | music | Reproducir musica de fondo (transmision) |
| Stop Music | (ninguno) | Detener musica de fondo |
| Set Volume | sound, volume (0.0-1.0) | Ajustar volumen del sonido |

### Acciones de Flujo de Control

| Accion | Parametros | Descripcion |
|--------|------------|-------------|
| If Collision At | x, y, object_type | Verificar colision en una posicion |
| If Can Push | direction, object_type | Verificacion de empuje estilo Sokoban |
| Set Variable | name, value, scope, relative | Establecer un valor de variable |
| Test Variable | name, value, scope, operation | Comparar una variable |
| Test Expression | expression | Evaluar una expresion booleana |
| Check Empty | x, y, only_solid | Verificar si la posicion esta libre |
| Check Collision | x, y, only_solid | Verificar colision en una posicion |
| Start Block | (ninguno) | Iniciar un bloque de acciones (llave de apertura) |
| End Block | (ninguno) | Finalizar un bloque de acciones (llave de cierre) |
| Else | (ninguno) | Marca la rama sino de un condicional |
| Repeat | times | Repetir la siguiente accion/bloque N veces |
| Exit Event | (ninguno) | Dejar de ejecutar las acciones restantes |

### Ambito de Variables

Las variables se pueden acceder usando referencias con ambito:

| Ambito | Sintaxis | Descripcion |
|--------|----------|-------------|
| Self | `self.variable` o solo `variable` | Variable de la instancia actual |
| Other | `other.variable` | La otra instancia en una colision |
| Global | `global.variable` | Variable global del juego |

Variables integradas de instancia: `x`, `y`, `hspeed`, `vspeed`, `direction`, `speed`, `gravity`, `friction`, `visible`, `depth`, `image_index`, `image_speed`, `scale_x`, `scale_y`

---

## 12. Pruebas y Ejecucion de Juegos

### Prueba Rapida (F5)

Presiona **F5** o haz clic en el boton **Test** para ejecutar tu juego instantaneamente. Se abre una ventana separada de Pygame mostrando tu juego.

- Presiona **Escape** para detener el juego y volver al IDE
- La barra de estado del IDE muestra "Game running..." mientras el juego esta activo

### Modo de Depuracion (F6)

Presiona **F6** para el modo de depuracion, que muestra salida adicional en la consola incluyendo:
- Registro de ejecucion de eventos
- Detalles de deteccion de colisiones
- Valores de parametros de acciones
- Creacion y destruccion de instancias

### Orden de Ejecucion del Juego

Cada cuadro sigue el orden de eventos de GameMaker 7.0:

1. Eventos **Begin Step**
2. Cuenta regresiva y activacion de **Alarm**
3. Eventos **Step**
4. Eventos de entrada **Keyboard/Mouse**
5. **Movimiento** (fisica: gravedad, friccion, hspeed/vspeed)
6. Deteccion de **colisiones** y eventos
7. Eventos **End Step**
8. Eventos **Destroy** para instancias marcadas
9. Eventos **Draw** y renderizado

### Titulo de la Ventana

El titulo de la ventana del juego puede mostrar valores de puntuacion, vidas y salud. Activa esto con la configuracion de visualizacion del titulo en la configuracion del proyecto o usando las acciones de puntuacion/vidas/salud.

---

## 13. Exportar Juegos

### Exportacion HTML5

**File > Export as HTML5**

Crea un unico archivo HTML autocontenido que se ejecuta en cualquier navegador web.

- Todos los sprites se incrustan como datos base64
- Los datos del juego se comprimen con gzip
- El motor JavaScript maneja el renderizado via HTML5 Canvas
- No se requiere servidor - solo abre el archivo en un navegador

### Exportacion EXE (Windows)

**File > Export Project** o **Build > Export Game**

Crea un ejecutable independiente de Windows usando PyInstaller.

**Requisitos:** PyInstaller y Kivy deben estar instalados.

**Proceso:**
1. Genera un juego basado en Kivy a partir de tu proyecto
2. Empaqueta el runtime de Python y todas las dependencias
3. Crea un unico archivo EXE (puede tomar 5-10 minutos)

**Opciones:**
- Consola de depuracion (muestra ventana de terminal para depuracion)
- Icono personalizado
- Compresion UPX (reduce tamano del archivo)

### Exportacion Movil (Kivy)

**File > Export to Kivy**

Genera un proyecto Kivy para despliegue movil.

**La salida incluye:**
- Codigo del juego en Python adaptado para Kivy
- Paquete de recursos optimizado para movil
- Configuracion `buildozer.spec` para compilaciones Android/iOS

**Para compilar para Android:**
```bash
cd exported_project
buildozer android debug
```

### Exportacion ZIP

**File > Export as Zip**

Empaqueta el proyecto completo como un archivo ZIP para compartir o respaldo. El ZIP se puede reabrir con **File > Open Zip Project**.

### Exportacion Aseba (Robot Thymio)

Para proyectos con Thymio, exporta archivos de codigo AESL compatibles con Aseba Studio.

---

## 14. Programacion Visual con Blockly

PyGameMaker integra Google Blockly para programacion visual con bloques de codigo.

### Configurar Bloques

Abre **Tools > Configure Action Blocks** para personalizar que bloques estan disponibles.

### Preajustes de Bloques

| Preajuste | Descripcion |
|-----------|-------------|
| Full (All Blocks) | Todos los 173 bloques activados |
| Beginner | Solo bloques esenciales (eventos, movimiento basico, puntuacion, habitaciones) |
| Intermediate | Agrega dibujo, mas movimiento, vidas, salud, sonido |
| Platformer Game | Enfocado en fisica: gravedad, friccion, colision |
| Grid-based RPG | Movimiento en cuadricula, salud, transiciones de habitacion |
| Sokoban (Box Puzzle) | Movimiento en cuadricula, mecanicas de empuje |
| Testing | Solo bloques validados |
| Implemented Only | Excluye bloques no implementados |
| Code Editor | Para programacion basada en texto |
| Blockly Editor | Para desarrollo visual primero |
| Custom | Tu propia seleccion |

### Categorias de Bloques

Los bloques estan organizados en categorias con codigo de colores:

| Categoria | Color | Bloques |
|-----------|-------|---------|
| Events | Amarillo | 13 bloques de eventos |
| Movement | Azul | 14 bloques de movimiento |
| Timing | Rojo | Bloques de temporizador y alarma |
| Drawing | Morado | Dibujo de formas y texto |
| Score/Lives/Health | Verde | Bloques de seguimiento de puntuacion |
| Instance | Rosa | Crear/destruir instancias |
| Room | Marron | Navegacion de habitaciones |
| Values | Azul oscuro | Variables y expresiones |
| Sound | | Reproduccion de audio |
| Output | | Mensajes y visualizacion |

### Dependencias de Bloques

Algunos bloques requieren otros bloques para funcionar. El dialogo de configuracion muestra advertencias cuando faltan dependencias. Por ejemplo, el bloque **Draw Score** requiere que **Set Score** y **Add Score** esten activados.

---

## 15. Soporte para Robot Thymio

PyGameMaker incluye soporte para el robot educativo Thymio, permitiendote simular y programar robots Thymio dentro del IDE.

### Que es Thymio?

Thymio es un pequeno robot educativo con sensores, LEDs, motores y botones. PyGameMaker puede simular el comportamiento de Thymio y exportar codigo para ejecutar en robots reales.

### Activar Thymio

Ve a **Tools > Thymio Programming > Show Thymio Tab in Object Editor** para activar las funciones de Thymio en el editor de objetos.

### Simulador de Thymio

El simulador modela el robot Thymio fisico:

**Especificaciones:**
- Tamano del robot: 110x110 pixeles (11cm x 11cm)
- Base de ruedas: 95 pixeles
- Rango de velocidad del motor: -500 a +500

### Sensores de Thymio

| Sensor | Cantidad | Rango | Descripcion |
|--------|----------|-------|-------------|
| Proximity | 7 | 0-4000 | Sensores de distancia horizontales (rango de 10cm) |
| Ground | 2 | 0-1023 | Detecta superficies claras/oscuras |
| Buttons | 5 | 0/1 | Adelante, atras, izquierda, derecha, centro |

### Eventos de Thymio

| Evento | Se Activa Cuando |
|--------|------------------|
| Button Forward/Backward/Left/Right/Center | Boton capacitivo presionado |
| Any Button | Cualquier estado de boton cambia |
| Proximity Update | Los sensores de proximidad se actualizan (10 Hz) |
| Ground Update | Los sensores de suelo se actualizan (10 Hz) |
| Tap | El acelerometro detecta golpe/choque |
| Sound Detected | El microfono detecta sonido |
| Timer 0/1 | El periodo del temporizador expira |
| Sound Finished | La reproduccion de sonido se completa |
| Message Received | Comunicacion IR recibida |

### Acciones de Thymio

**Control de Motor:**
- Set Motor Speed (izquierdo, derecho independientemente)
- Move Forward / Backward
- Turn Left / Right
- Stop Motors

**Control de LED:**
- Set Top LED (color RGB)
- Set Bottom Left/Right LED
- Set Circle LEDs (8 LEDs alrededor del perimetro)
- Turn Off All LEDs

**Sonido:**
- Play Tone (frecuencia, duracion)
- Play System Sound
- Stop Sound

**Condiciones de Sensores:**
- If Proximity (sensor, umbral, comparacion)
- If Ground Dark / Light
- If Button Pressed / Released

**Temporizador:**
- Set Timer Period (temporizador 0 o 1, periodo en ms)

### Exportar a un Thymio Real

1. Exporta tu proyecto Thymio via el exportador Aseba
2. Abre el archivo `.aesl` generado en Aseba Studio
3. Conecta tu Thymio via USB
4. Haz clic en **Load** y luego en **Run**

---

## 16. Configuracion y Preferencias

Abre **Tools > Preferences** para configurar el IDE.

### Pestana Apariencia

| Configuracion | Opciones | Predeterminado |
|---------------|----------|----------------|
| Font Size | 8-24 pt | 10 |
| Font Family | System Default, Segoe UI, Arial, Ubuntu, Helvetica, SF Pro Text, Roboto | System Default |
| Theme | Default, Dark, Light | Default |
| UI Scale | 0.5x - 2.0x | 1.0x |
| Show Tooltips | Si/No | Si |

### Pestana Editor

| Configuracion | Opciones | Predeterminado |
|---------------|----------|----------------|
| Enable Auto-Save | Si/No | Si |
| Auto-Save Interval | 1-30 minutos | 5 min |
| Show Grid | Si/No | Si |
| Grid Size | 8-128 px | 32 |
| Snap to Grid | Si/No | Si |
| Show Collision Boxes | Si/No | No |

### Pestana Proyecto

| Configuracion | Opciones | Predeterminado |
|---------------|----------|----------------|
| Default Projects Folder | Ruta | ~/PyGameMaker Projects |
| Recent Projects Limit | 5-50 | 10 |
| Create Backup on Save | Si/No | Si |

### Pestana Avanzado

| Configuracion | Opciones | Predeterminado |
|---------------|----------|----------------|
| Debug Mode | Si/No | No |
| Show Console Output | Si/No | Si |
| Maximum Undo Steps | 10-200 | 50 |

### Archivo de Configuracion

Las configuraciones se almacenan en `~/.pygamemaker/config.json` y persisten entre sesiones.

### Cambiar Idioma

Ve a **Tools > Language** y selecciona tu idioma preferido.

**Idiomas Soportados:**
- English
- Francais
- Espanol
- Deutsch
- Italiano
- Русский (Russian)
- Slovenscina (Slovenian)
- Українська (Ukrainian)

La interfaz se actualiza inmediatamente. Algunos cambios pueden requerir reiniciar el IDE.

---

## 17. Atajos de Teclado

### Atajos Globales

| Atajo | Accion |
|-------|--------|
| Ctrl+N | Nuevo Proyecto |
| Ctrl+O | Abrir Proyecto |
| Ctrl+S | Guardar Proyecto |
| Ctrl+Shift+S | Guardar Proyecto Como |
| Ctrl+E | Exportar Proyecto |
| Ctrl+Q | Salir del IDE |
| Ctrl+R | Crear Habitacion |
| F1 | Documentacion |
| F5 | Probar Juego |
| F6 | Depurar Juego |
| F7 | Compilar Juego |
| F8 | Compilar y Ejecutar |

### Atajos del Editor

| Atajo | Accion |
|-------|--------|
| Ctrl+Z | Deshacer |
| Ctrl+Y | Rehacer |
| Ctrl+X | Cortar |
| Ctrl+C | Copiar |
| Ctrl+V | Pegar |
| Ctrl+D | Duplicar |
| Ctrl+F | Buscar |
| Ctrl+H | Buscar y Reemplazar |
| Delete | Eliminar seleccionado |

### Atajos del Editor de Sprites

| Atajo | Accion |
|-------|--------|
| P | Herramienta lapiz |
| E | Herramienta borrador |
| I | Selector de color (cuentagotas) |
| G | Herramienta de relleno (balde) |
| L | Herramienta de linea |
| R | Herramienta de rectangulo |
| O | Herramienta de elipse |
| S | Herramienta de seleccion |
| Ctrl+Mouse Wheel | Acercar/alejar |

---

## 18. Tutoriales

PyGameMaker incluye tutoriales integrados para ayudarte a comenzar. Accede a ellos desde **Help > Tutorials** o desde la carpeta Tutorials en el directorio de instalacion.

### Tutoriales Disponibles

| # | Tutorial | Descripcion |
|---|----------|-------------|
| 01 | Getting Started | Introduccion al IDE y primer proyecto |
| 02 | First Game | Creando tu primer juego jugable |
| 03 | Pong | Juego clasico de Pong con paleta y pelota |
| 04 | Breakout | Juego de romper ladrillos estilo Breakout |
| 05 | Sokoban | Juego de rompecabezas de empujar cajas |
| 06 | Maze | Juego de navegacion de laberintos |
| 07 | Platformer | Juego de plataformas con desplazamiento lateral |
| 08 | Lunar Lander | Juego de aterrizaje basado en gravedad |

Los tutoriales estan disponibles en multiples idiomas (ingles, aleman, espanol, frances, italiano, ruso, esloveno, ucraniano).

---

## 19. Solucion de Problemas

### El juego no inicia (F5)

- Verifica que tu proyecto tenga al menos una habitacion con instancias
- Comprueba que los objetos tengan sprites asignados
- Revisa la salida de la consola (modo de depuracion F6) para mensajes de error

### Los sprites no se muestran

- Confirma que el archivo de sprite existe en la carpeta `sprites/`
- Comprueba que el objeto tenga un sprite asignado en sus propiedades
- Verifica que la instancia este configurada como `visible = true`

### La colision no funciona

- Asegurate de que el objeto objetivo este marcado como **Solid** si usas colision basada en solidos
- Verifica que tengas un evento **Collision With** configurado para el objeto correcto
- Comprueba que las instancias realmente se superponen (usa el modo de depuracion)

### El sonido no se reproduce

- Verifica que el archivo de sonido exista y sea un formato soportado (WAV, OGG, MP3)
- Comprueba que pygame.mixer se haya inicializado correctamente (ver salida de consola)
- Los archivos de musica se transmiten desde el disco - asegurate de que la ruta del archivo sea correcta

### La exportacion falla

- **Exportacion EXE:** Asegurate de que PyInstaller este instalado (`pip install pyinstaller`)
- **Exportacion Kivy:** Asegurate de que Kivy este instalado (`pip install kivy`)
- **Exportacion HTML5:** Revisa la consola para cualquier error de codificacion
- Todas las exportaciones requieren un proyecto valido con al menos una habitacion

### Problemas de rendimiento

- Reduce el numero de instancias en las habitaciones
- Usa el sistema de colision de cuadricula espacial (activado por defecto)
- Evita operaciones costosas en eventos Step (se ejecuta 60 veces por segundo)
- Usa alarmas para tareas periodicas en lugar de contar cuadros en Step

---

**PyGameMaker IDE** - Version 1.0.0-rc.6
Copyright 2025-2026 Gabriel Thullen
Licensed under GNU General Public License v3 (GPLv3)
GitHub: https://github.com/Gabe1290/pythongm
