# Preguntas Frecuentes (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

[Volver al Inicio](Home_es)

Respuestas a preguntas comunes sobre pyGM.

## Preguntas generales

### Que es pyGM?
pyGM es un editor visual de desarrollo de juegos para Python. Permite crear juegos 2D sin conocimientos extensos de programacion.

### Es pyGM gratuito?
Si, pyGM es de codigo abierto y completamente gratuito.

### Que lenguaje de programacion se usa?
pyGM esta basado en Python. Puedes usar programacion visual o escribir codigo Python directamente.

### Para que plataformas puedo desarrollar?
- Windows
- macOS
- Linux
- Web (HTML5)

## Instalacion

### Como instalo pyGM?
```bash
pip install pygm
```

### Que version de Python necesito?
Python 3.8 o superior.

### pyGM no inicia. Que hago?
1. Verifica la version de Python
2. Reinstala las dependencias
3. Inicia desde la linea de comandos para ver errores

## Desarrollo

### Como creo un nuevo proyecto?
Inicia pyGM y selecciona "Nuevo Proyecto" o usa Archivo > Nuevo.

### Como agrego sprites?
1. Clic derecho en "Sprites" en el arbol de recursos
2. Selecciona "Nuevo Sprite"
3. Importa una imagen o crea una

### Como creo animaciones?
1. Abre un sprite
2. Agrega varios frames
3. Configura la velocidad de animacion

### Como programo el comportamiento de los objetos?
1. Abre un objeto
2. Agrega eventos (ej. Create, Step)
3. Agrega acciones a los eventos
4. O usa el editor visual Blockly

## Recursos

### Que formatos de imagen son compatibles?
- PNG (recomendado)
- JPG
- GIF
- BMP

### Que formatos de audio son compatibles?
- WAV
- MP3
- OGG

### Como optimizo mis recursos?
- Usa tamanos de imagen apropiados
- Comprime archivos de audio
- Elimina recursos no utilizados

## Gameplay

### Como implemento la deteccion de colisiones?
1. Crea un evento de colision en el objeto
2. Selecciona el otro objeto
3. Agrega acciones para la reaccion

### Como creo multiples niveles?
1. Crea varias salas
2. Usa la accion "Ir a sala"
3. O "Ir a la siguiente sala"

### Como guardo el progreso del juego?
Usa las funciones de guardado integradas:
- `save_game()`: Guardar juego
- `load_game()`: Cargar juego

## Exportacion

### Como exporto mi juego?
1. Ve a Archivo > Exportar
2. Selecciona la plataforma de destino
3. Configura las opciones
4. Haz clic en "Exportar"

### Por que el archivo exportado es tan grande?
- Incluye el runtime de Python
- Todos los recursos incrustados
- Consejo: Optimiza los recursos

### Puedo exportar para dispositivos moviles?
Actualmente no es compatible directamente. La exportacion web funciona en navegadores moviles.

## Solucion de problemas

### Mi juego es lento
- Reduce el codigo en eventos Step
- Optimiza los tamanos de sprites
- Evita demasiadas instancias

### Los sprites no se muestran
- Verifica la ruta del sprite
- Asegurate de que Visible=true
- Revisa el orden de dibujo (profundidad)

### Las colisiones no funcionan
- Verifica las mascaras de colision
- Asegurate de que los objetos sean solidos (si es necesario)
- Revisa la configuracion de eventos

## Comunidad

### Donde encuentro ayuda?
- Documentacion oficial
- GitHub Issues
- Foros de la comunidad

### Como puedo contribuir?
- Reporta errores en GitHub
- Envia Pull Requests
- Mejora la documentacion

## Ver tambien

- [Empezar](Empezar_es)
- [Crear tu primer juego](Primer_Juego_es)
- [Eventos y Acciones](Eventos_y_Acciones_es)
