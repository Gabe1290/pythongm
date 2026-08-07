# Preguntas Frecuentes (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

> [Volver al Inicio](Home_es)

---

## Preguntas Generales

### ¿Qué es PyGameMaker?

PyGameMaker es un IDE de desarrollo de juegos de código abierto, inspirado en GameMaker 7.0. Te permite crear juegos 2D usando programación visual (Google Blockly) o un sistema de eventos-acciones, sin necesidad de escribir código.

### ¿Es PyGameMaker gratuito?

¡Sí! PyGameMaker es completamente gratuito y de código abierto — el código fuente está bajo la Licencia MIT, y la documentación bajo CC BY 4.0.

### ¿Para qué plataformas puedo exportar?

- Windows (.exe independiente)
- HTML5 (navegadores web)
- Linux (binario nativo)
- Móvil (iOS/Android mediante Kivy)

### ¿Necesito experiencia en programación?

¡No! PyGameMaker está diseñado para principiantes. Puedes crear juegos usando:
- Bloques Blockly de arrastrar y soltar
- Sistema de eventos/acciones point-and-click
- Sin necesidad de código

### ¿Es compatible con archivos de GameMaker?

PyGameMaker está inspirado en GameMaker 7.0 pero usa su propio formato de proyecto. No puedes importar archivos de GameMaker directamente, pero los conceptos y el flujo de trabajo son similares.

---

## Instalación

### ¿Cuáles son los requisitos del sistema?

- Python 3.10 o superior
- Windows, Linux o macOS
- Mínimo 4 GB de RAM (8 GB recomendados)
- ~500 MB de espacio en disco

### ¿Cómo instalo PyGameMaker?

Consulta [[Empezar_es]] para instrucciones de instalación detalladas. Versión corta:

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
python main.py
```

### Python no se reconoce / no se encuentra

Asegúrate de que Python esté instalado y agregado al PATH del sistema. Verifícalo ejecutando:

```bash
python --version
```

Si esto falla, reinstala Python y activa "Add Python to PATH" durante la instalación.

### Obtengo errores de importación al iniciar

Intenta reinstalar las dependencias:

```bash
pip install -r requirements.txt --force-reinstall
```

---

## Proyectos

### ¿Dónde se guardan mis proyectos?

Los proyectos se guardan en carpetas que tú eliges. Cada proyecto contiene:
- `project.json` - El archivo principal del proyecto
- Carpetas para sprites, sonidos, objetos, salas, etc.

### ¿Puedo tener varios proyectos abiertos a la vez?

Actualmente, PyGameMaker abre un proyecto a la vez. Usa **File > Open Project** para cambiar entre proyectos.

### ¿Cómo hago una copia de seguridad de mi proyecto?

Simplemente copia toda la carpeta del proyecto. Todos los recursos y configuraciones están contenidos en ella. Considera también usar git para el control de versiones:

```bash
cd mi_proyecto
git init
git add .
git commit -m "Copia de seguridad inicial"
```

### Mi proyecto no se abre / está corrupto

Prueba estos pasos:
1. Verifica que `project.json` exista y no esté vacío
2. Abre `project.json` en un editor de texto para buscar errores JSON
3. Restaura desde una copia de seguridad si está disponible
4. Revisa la salida de la consola para mensajes de error específicos

---

## Objetos y Eventos

### ¿Cuál es la diferencia entre un objeto y una instancia?

- **Objeto**: Una plantilla/modelo que define el comportamiento
- **Instancia**: Una copia específica de un objeto colocada en una sala

Por ejemplo, `obj_enemigo` es un objeto. Colocar 5 enemigos en una sala crea 5 instancias de `obj_enemigo`.

### ¿Por qué no se activa mi evento?

Causas comunes:
1. **Tipo de evento incorrecto**: Asegúrate de usar el evento correcto (ej. "Key Press" en lugar de "Keyboard")
2. **Sin instancias**: El objeto debe tener instancias en la sala
3. **Objeto no visible**: Verifica la propiedad visible
4. **Orden de ejecución**: Algunos eventos se ejecutan antes que otros

### ¿Cómo hago que los objetos interactúen?

Usa eventos de colisión:
1. Abre el objeto que debe detectar la colisión
2. Agrega el evento **Collision with [otro_objeto]**
3. Agrega acciones para lo que sucede en la colisión

### ¿Cuál es la diferencia entre los eventos "Keyboard" y "Key Press"?

- **Keyboard [tecla]**: Se activa en cada fotograma mientras la tecla está presionada
- **Key Press [tecla]**: Se activa una vez cuando la tecla se presiona por primera vez
- **Key Release [tecla]**: Se activa una vez cuando la tecla se suelta

---

## Salas

### ¿Qué sala se carga primero?

La primera sala en el árbol de recursos (en la parte superior de la lista) se carga al iniciar el juego. Arrastra las salas para reordenarlas.

### ¿Cómo cambio de sala?

Usa las acciones de sala:
- **Next Room**: Va a la siguiente sala en orden
- **Previous Room**: Va a la sala anterior
- **Go to Room**: Salta a una sala específica

### Los objetos desaparecen cuando cambio de sala

Los objetos se destruyen al salir de una sala, a menos que estén marcados como **Persistent** en sus propiedades.

### Mi sala es demasiado grande/pequeña en pantalla

El tamaño de la ventana del juego coincide con las dimensiones de la primera sala. Puedes:
- Cambiar el tamaño de la sala para que coincida con el tamaño de ventana deseado
- Usar Views para mostrar solo una parte de la sala

---

## Gráficos y Sprites

### ¿Qué formatos de imagen son compatibles?

- PNG (recomendado, admite transparencia)
- JPEG/JPG
- BMP
- GIF (solo el primer fotograma)

### Mi sprite aparece en la posición incorrecta

Revisa la configuración de **Origin** en el editor de sprites. El origen es el punto de anclaje para el posicionamiento. Configuraciones comunes:
- Arriba a la izquierda (0, 0): Predeterminado
- Centro: Bueno para objetos rotatorios
- Centro inferior: Bueno para personajes

### ¿Cómo animo un sprite?

1. Crea un sprite con varios fotogramas (tira horizontal)
2. Establece **Number of Frames** en las propiedades del sprite
3. Ajusta la **Animation Speed** (fotogramas por segundo)

### Los sprites se ven borrosos

Esto ocurre al escalar sprites. Para pixel art, desactiva la interpolación/suavizado en la configuración del juego, si está disponible.

---

## Sonido y Música

### ¿Qué formatos de audio son compatibles?

- WAV (sin comprimir)
- OGG (recomendado para música)
- MP3

### El sonido no se reproduce

Verifica:
1. Que el archivo de audio exista en la carpeta sounds
2. Que el formato del archivo sea compatible
3. Que estés usando el nombre de sonido correcto en las acciones
4. El navegador puede requerir interacción del usuario (para HTML5)

### ¿Cómo reproduzco música de fondo en bucle?

Usa la acción **Play Music** con la opción de bucle activada, o **Play Sound** con el parámetro loop establecido en verdadero.

---

## Exportación

### Mi juego exportado no funciona

Problemas comunes:
- **Windows**: DLL faltantes — asegúrate de incluir toda la carpeta de salida
- **HTML5**: El navegador bloquea archivos locales — alójalo en un servidor
- **Recursos faltantes**: Verifica que todos los archivos estén incluidos

### El archivo exportado es enorme

El tamaño del juego incluye Python y todas las bibliotecas. Para reducirlo:
- Elimina recursos no usados
- Comprime imágenes y audio
- Usa formatos apropiados (OGG en lugar de WAV)
- Activa la compresión UPX para builds de Windows

### ¿Puedo vender juegos hechos con PyGameMaker?

¡Sí! Los juegos que crees son completamente tuyos y puedes venderlos. El código fuente de PyGameMaker está bajo la permisiva Licencia MIT, así que puedes usarlo libremente en proyectos comerciales — y, a diferencia de las licencias copyleft, no estás obligado a hacer de código abierto tus propias modificaciones.

---

## Blockly / Programación Visual

### ¿Dónde encuentro el editor Blockly?

1. Abre un objeto
2. Haz clic en la pestaña **Blockly** en el editor de objetos
3. Aparece el área de trabajo de programación visual

### ¿Cómo cambio entre Blockly y eventos?

Ambos sistemas trabajan sobre el mismo objeto. La pestaña Blockly y la pestaña Events muestran vistas diferentes de la misma lógica. Los cambios en uno se reflejan en el otro.

### Mis bloques de Blockly desaparecieron

Verifica:
1. Que estés viendo el objeto correcto
2. Desplázate por el área de trabajo (los bloques podrían estar fuera de pantalla)
3. Revisa el nivel de zoom

---

## Rendimiento

### Mi juego va lento

Consejos para un mejor rendimiento:
1. Reduce el número de instancias
2. Evita cálculos pesados en los eventos Step
3. Usa alarmas en lugar de contar fotogramas
4. Optimiza los tamaños de sprite
5. Destruye las instancias que salen de la sala

### El evento Step se ejecuta con demasiada frecuencia

El evento Step se ejecuta en cada fotograma (60 veces por segundo por defecto). Usa:
- Alarmas para acciones retrasadas
- Condiciones que se verifiquen antes de operaciones pesadas
- Una velocidad de sala más baja si es apropiado

---

## Obtener Ayuda

### ¿Dónde puedo reportar errores?

Reporta errores en la página [GitHub Issues](https://github.com/Gabe1290/pythongm/issues). Incluye:
- Qué esperabas que sucediera
- Qué sucedió realmente
- Pasos para reproducir el problema
- Tu sistema operativo y versión de Python

### ¿Dónde puedo aprender más?

- [[Empezar_es]] - Instalación y fundamentos
- [[Primer_Juego_es]] - Tutorial paso a paso
- [[Eventos_y_Acciones_es]] - Referencia completa
- [[Programacion_Visual_es]] - Guía de Blockly
