# Preguntas Frecuentes (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

[Volver al Inicio](Home_es)

Respuestas a preguntas comunes sobre pyGM.

## Preguntas generales

### ¿Qué es pyGM?
pyGM es un editor visual de desarrollo de juegos para Python. Permite crear juegos 2D sin conocimientos extensos de programación.

### ¿Es pyGM gratuito?
Sí, pyGM es de código abierto y completamente gratuito.

### ¿Qué lenguaje de programación se usa?
pyGM está basado en Python. Puedes usar programación visual o escribir código Python directamente.

### ¿Para qué plataformas puedo desarrollar?
- Windows
- macOS
- Linux
- Web (HTML5)
- Móvil (Kivy/Android)

## Instalación

### ¿Cómo instalo pyGM?
```bash
pip install pygm
```

### ¿Qué versión de Python necesito?
Python 3.10 o superior.

### pyGM no inicia. ¿Qué hago?
1. Verifica la versión de Python
2. Reinstala las dependencias
3. Inicia desde la línea de comandos para ver errores

## Desarrollo

### ¿Cómo creo un nuevo proyecto?
Inicia pyGM y selecciona "Nuevo Proyecto" o usa Archivo > Nuevo.

### ¿Cómo agrego sprites?
1. Clic derecho en "Sprites" en el árbol de recursos
2. Selecciona "Nuevo Sprite"
3. Importa una imagen o crea una

### ¿Cómo creo animaciones?
1. Abre un sprite
2. Agrega varios frames
3. Configura la velocidad de animación

### ¿Cómo programo el comportamiento de los objetos?
1. Abre un objeto
2. Agrega eventos (ej. Create, Step)
3. Agrega acciones a los eventos
4. O usa el editor visual Blockly

## Recursos

### ¿Qué formatos de imagen son compatibles?
- PNG (recomendado)
- JPG
- GIF
- BMP

### ¿Qué formatos de audio son compatibles?
- WAV
- MP3
- OGG

### ¿Cómo optimizo mis recursos?
- Usa tamaños de imagen apropiados
- Comprime archivos de audio
- Elimina recursos no utilizados

## Gameplay

### ¿Cómo implemento la detección de colisiones?
1. Crea un evento de colisión en el objeto
2. Selecciona el otro objeto
3. Agrega acciones para la reacción

### ¿Cómo creo múltiples niveles?
1. Crea varias salas
2. Usa la acción "Ir a sala"
3. O "Ir a la siguiente sala"

### ¿Cómo guardo el progreso del juego?
Usa las funciones de guardado integradas:
- `save_game()`: Guardar juego
- `load_game()`: Cargar juego

## Exportación

### ¿Cómo exporto mi juego?
1. Ve a Archivo > Exportar proyecto…
2. Selecciona la plataforma de destino
3. Configura las opciones
4. Haz clic en "Exportar"

### ¿Por qué el archivo exportado es tan grande?
- Incluye el runtime de Python
- Todos los recursos están incrustados
- Consejo: Optimiza los recursos

### ¿Puedo exportar para dispositivos móviles?
Sí, mediante la exportación Kivy/Android. La exportación web también funciona en navegadores móviles.

## Solución de problemas

### Mi juego es lento
- Reduce el código en eventos Step
- Optimiza los tamaños de sprites
- Evita demasiadas instancias

### Los sprites no se muestran
- Verifica la ruta del sprite
- Asegúrate de que Visible=true
- Revisa el orden de dibujo (profundidad)

### Las colisiones no funcionan
- Verifica las máscaras de colisión
- Asegúrate de que los objetos sean sólidos (si es necesario)
- Revisa la configuración de eventos

## Comunidad

### ¿Dónde encuentro ayuda?
- Documentación oficial
- GitHub Issues
- Foros de la comunidad

### ¿Cómo puedo contribuir?
- Reporta errores en GitHub
- Envía Pull Requests
- Mejora la documentación

## Ver también

- [Empezar](Empezar_es)
- [Crear tu primer juego](Primer_Juego_es)
- [Eventos y Acciones](Eventos_y_Acciones_es)
