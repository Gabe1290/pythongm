# PyGameMaker IDE

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Home) | [Français](Home_fr) | [Deutsch](Home_de) | [Italiano](Home_it) | [Español](Home_es) | [Português](Home_pt) | [Slovenščina](Home_sl) | [Українська](Home_uk) | [Русский](Home_ru)

---

**Un entorno de desarrollo de juegos visual inspirado en GameMaker 7.0**

PyGameMaker es un IDE de código abierto que hace accesible la creación de juegos 2D a través de programación visual basada en bloques (Google Blockly) y un sistema de eventos-acciones. Crea juegos sin conocimientos profundos de programación y luego expórtalos a Windows, Linux, HTML5 o plataformas móviles.

---

## Elige Tu Nivel

PyGameMaker usa **preajustes** para controlar qué eventos y acciones están disponibles. Esto ayuda a los principiantes a enfocarse en las características esenciales mientras permite a los usuarios experimentados acceder al conjunto completo de herramientas.

| Preajuste | Ideal Para | Características |
|-----------|------------|-----------------|
| [**Principiante**](Beginner-Preset_es) | Nuevos en desarrollo de juegos | 4 eventos, 17 acciones - Movimiento, colisiones, puntuación, salas |
| [**Intermedio**](Intermediate-Preset_es) | Algo de experiencia | +4 eventos, +12 acciones - Vidas, salud, sonido, alarmas, dibujo |
| **Avanzado** | Usuarios experimentados | Todos los 40+ eventos y acciones disponibles |

**Nuevos usuarios:** Comienza con el [Preajuste Principiante](Beginner-Preset_es) para aprender los fundamentos sin sentirte abrumado.

Consulta la [Guía de Preajustes](Preset-Guide_es) para una visión completa del sistema de preajustes.

---

## Características de un Vistazo

| Característica | Descripción |
|----------------|-------------|
| **Programación Visual** | Codificación arrastrar y soltar con Google Blockly 12.x |
| **Sistema Eventos-Acciones** | Lógica basada en eventos compatible con GameMaker 7.0 |
| **Preajustes por Nivel** | Conjuntos de características Principiante, Intermedio y Avanzado |
| **Exportación Multi-Plataforma** | Windows EXE, HTML5, Linux, Kivy (móvil/escritorio) |
| **Gestión de Recursos** | Sprites, sonidos, fondos, fuentes y salas |
| **Interfaz Multilingüe** | Inglés, Francés, Alemán, Italiano, Español, Portugués, Esloveno, Ucraniano, Ruso |
| **Extensible** | Sistema de plugins para eventos y acciones personalizados |

---

## Primeros Pasos

### Requisitos del Sistema

- **Python** 3.10 o superior
- **Sistema Operativo:** Windows, Linux o macOS

### Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Gabe1290/pythongm.git
   cd pythongm
   ```

2. Crea un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # o
   venv\Scripts\activate     # Windows
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecuta PyGameMaker:
   ```bash
   python main.py
   ```

---

## Conceptos Fundamentales

### Objetos
Entidades del juego con sprites, propiedades y comportamientos. Cada objeto puede tener múltiples eventos con acciones asociadas.

### Eventos
Disparadores que ejecutan acciones cuando ocurren condiciones específicas:
- **Create** - Cuando se crea una instancia
- **Step** - Cada fotograma (típicamente 60 FPS)
- **Draw** - Fase de renderizado personalizado
- **Destroy** - Cuando se destruye una instancia
- **Keyboard** - Tecla presionada, liberada o mantenida
- **Mouse** - Clics, movimiento, entrada/salida
- **Collision** - Cuando las instancias se tocan
- **Alarm** - Temporizadores de cuenta regresiva (12 disponibles)

Consulta la [Referencia de Eventos](Event-Reference_es) para documentación completa.

### Acciones
Operaciones realizadas cuando se disparan eventos. 40+ acciones integradas para:
- Movimiento y física
- Dibujo y sprites
- Puntuación, vidas y salud
- Sonido y música
- Gestión de instancias y salas

Consulta la [Referencia Completa de Acciones](Full-Action-Reference_es) para documentación completa.

### Salas
Niveles del juego donde colocas instancias de objetos, estableces fondos y defines el área de juego.

---

## Programación Visual con Blockly

PyGameMaker integra Google Blockly para programación visual. Los bloques están organizados en categorías:

- **Eventos** - Create, Step, Draw, Keyboard, Mouse
- **Movimiento** - Velocidad, dirección, posición, gravedad
- **Temporización** - Alarmas y retrasos
- **Dibujo** - Formas, texto, sprites
- **Puntuación/Vidas/Salud** - Seguimiento del estado del juego
- **Instancia** - Crear y destruir objetos
- **Sala** - Navegación y gestión
- **Valores** - Variables y expresiones
- **Sonido** - Reproducción de audio
- **Salida** - Debug y visualización

---

## Opciones de Exportación

### Windows EXE
Ejecutables Windows independientes usando PyInstaller. No se requiere Python en la máquina destino.

### HTML5
Juegos web de un solo archivo que funcionan en cualquier navegador moderno. Comprimidos con gzip para carga rápida.

### Linux
Ejecutables Linux nativos para entornos Python 3.10+.

### Kivy
Aplicaciones multiplataforma para móvil (iOS/Android) y escritorio vía Buildozer.

---

## Estructura del Proyecto

```
nombre_proyecto/
├── project.json      # Configuración del proyecto
├── backgrounds/      # Imágenes de fondo y metadatos
├── data/             # Archivos de datos personalizados
├── fonts/            # Definiciones de fuentes
├── objects/          # Definiciones de objetos (JSON)
├── rooms/            # Diseños de salas (JSON)
├── scripts/          # Scripts personalizados
├── sounds/           # Archivos de audio y metadatos
├── sprites/          # Imágenes de sprites y metadatos
└── thumbnails/       # Miniaturas generadas de recursos
```

---

## Contenido del Wiki

### Preajustes y Referencia
- [Guía de Preajustes](Preset-Guide_es) - Visión general del sistema de preajustes
- [Preajuste Principiante](Beginner-Preset_es) - Características esenciales para nuevos usuarios
- [Preajuste Intermedio](Intermediate-Preset_es) - Características adicionales
- [Referencia de Eventos](Event-Reference_es) - Documentación completa de eventos
- [Referencia de Acciones](Full-Action-Reference_es) - Documentación completa de acciones

### Tutoriales y Guías
- [Primeros Pasos](Primeros_Pasos_es) - Primeros pasos con PyGameMaker
- [Crea Tu Primer Juego](Primer_Juego_es) - Tutorial paso a paso
- [Editor de Objetos](Editor_Objetos_es) - Trabajar con objetos del juego
- [Editor de Salas](Editor_Salas_es) - Diseñar niveles
- [Eventos y Acciones](Eventos_y_Acciones_es) - Referencia de lógica del juego
- [Programación Visual](Programacion_Visual_es) - Usar bloques Blockly
- [Exportar Juegos](Exportar_Juegos_es) - Compilar para diferentes plataformas
- [FAQ](FAQ_es) - Preguntas frecuentes

---

## Contribuir

¡Las contribuciones son bienvenidas! Consulta nuestras directrices de contribución para:
- Informes de errores y solicitudes de características
- Contribuciones de código
- Traducciones
- Mejoras de documentación

---

## Licencia

PyGameMaker está licenciado bajo la **GNU General Public License v3 (GPLv3)**.

Copyright (c) 2024-2025 Gabriel Thullen

---

## Enlaces

- [Repositorio GitHub](https://github.com/Gabe1290/pythongm)
- [Seguimiento de Issues](https://github.com/Gabe1290/pythongm/issues)
- [Lanzamientos](https://github.com/Gabe1290/pythongm/releases)
