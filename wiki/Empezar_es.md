# Empezar

> [English](Getting-Started) | [Français](Demarrage_fr) | [Deutsch](Erste_Schritte_de) | [Italiano](Iniziare_it) | [Español](Empezar_es) | [Português](Comecar_pt) | [Slovenščina](Zacetek_sl) | [Українська](Pochatok_uk) | [Русский](Nachalo_ru)

---

[Volver al Inicio](Home_es)

Esta guía te ayudará a poner PyGameMaker en funcionamiento en tu sistema.

---

## Requisitos del Sistema

- **Python** 3.10 o superior
- **Sistema Operativo:** Windows, Linux o macOS
- **Espacio en Disco:** ~500 MB para la instalación
- **RAM:** mínimo 4 GB, 8 GB recomendados

---

## Instalación

### Paso 1: Instalar Python

Descarga Python 3.10+ desde [python.org](https://www.python.org/downloads/) e instálalo. Asegúrate de marcar "Add Python to PATH" durante la instalación en Windows.

### Paso 2: Clonar el Repositorio

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
```

O descarga el archivo ZIP desde la [página de Releases](https://github.com/Gabe1290/pythongm/releases).

### Paso 3: Crear un Entorno Virtual

Crear un entorno virtual mantiene aisladas las dependencias de PyGameMaker:

```bash
python -m venv venv
```

Activa el entorno virtual:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Paso 4: Instalar las Dependencias

```bash
pip install -r requirements.txt
```

### Paso 5: Ejecutar PyGameMaker

```bash
python main.py
```

---

## Primer Inicio

Al iniciar PyGameMaker por primera vez, verás:

1. **Barra de Menú** — los menús File, Edit, Assets, Build, Tools y Help
2. **Árbol de Recursos** — panel izquierdo que muestra los recursos del proyecto (Sprites, Sonidos, Fondos, Objetos, Salas)
3. **Espacio de Trabajo** — área central para editar recursos
4. **Panel de Propiedades** — panel derecho para las propiedades de recursos

![La pestaña de Bienvenida al iniciar por primera vez, sin ningún proyecto abierto todavía](images/ide-welcome.png)

---

## Crear Tu Primer Proyecto

1. Ve a **File > New Project**
2. Elige una ubicación y un nombre para tu proyecto
3. Se creará una nueva carpeta de proyecto con la estructura estándar

---

## Estructura del Proyecto

Cada proyecto de PyGameMaker contiene:

```
mi_proyecto/
├── project.json      # Configuración del proyecto
├── sprites/          # Imágenes de sprites
├── sounds/           # Archivos de audio
├── backgrounds/      # Imágenes de fondo
├── objects/          # Definiciones de objetos del juego
├── rooms/            # Diseños de niveles
├── fonts/            # Archivos de fuentes
├── scripts/          # Scripts personalizados
└── data/             # Archivos de datos personalizados
```

---

## Cambiar de Idioma

PyGameMaker admite varios idiomas:

1. Ve a **Tools > Language**
2. Selecciona tu idioma preferido en el menú
3. Reinicia PyGameMaker para aplicar el cambio

Idiomas disponibles: Inglés, Francés, Alemán, Italiano, Español, Portugués, Esloveno, Ucraniano, Ruso

---

## Próximos Pasos

- [[Primer_Juego_es]] - Construye un juego sencillo paso a paso
- [[Editor_Objetos_es]] - Aprende a crear objetos del juego
- [[Editor_Salas_es]] - Diseña tus niveles de juego
- [[Eventos_y_Acciones_es]] - Comprende la lógica del juego

---

## Solución de Problemas

### Python no se encuentra
Asegúrate de que Python esté instalado y agregado al PATH. Prueba ejecutando `python --version` para verificar.

### Dependencias faltantes
Si obtienes errores de importación, intenta reinstalar las dependencias:
```bash
pip install -r requirements.txt --force-reinstall
```

### Problemas de visualización
En Linux, Qt (el framework de GUI en el que está construido
PyGameMaker) necesita algunas bibliotecas del sistema que `pip` no
instala:
```bash
sudo apt-get install -y libegl1 libxkbcommon0 libxcb-cursor0 \
    libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 libasound2-dev libgl1-mesa-dev
```

---

## Obtener Ayuda

- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Reporta errores o solicita funciones
- [[FAQ_es]] - Preguntas y respuestas comunes
