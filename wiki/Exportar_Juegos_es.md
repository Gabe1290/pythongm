# Exportar Juegos

> [English](Exporting-Games) | [Français](Exportation_fr) | [Deutsch](Spiele_Exportieren_de) | [Italiano](Esportare_Giochi_it) | [Español](Exportar_Juegos_es) | [Português](Exportar_Jogos_pt) | [Slovenščina](Izvoz_Iger_sl) | [Українська](Eksport_Ihor_uk) | [Русский](Eksport_Igr_ru)

---

> [Volver al Inicio](Home_es)

PyGameMaker puede exportar tu juego a varias plataformas. Esta guía cubre cada opción de exportación y cómo usarla.

---

## Resumen de la exportación

| Plataforma | Formato | Requisitos |
|------------|---------|------------|
| **Windows** | .exe | PyInstaller |
| **macOS** | .app | PyInstaller (en un Mac) |
| **HTML5** | .html | Navegador moderno |
| **Linux** | Binario | PyInstaller, Python 3.10+ |
| **Kivy / Android** | Código fuente / .apk | Buildozer |
| **Proyecto (.zip)** | .zip | — (compartir el proyecto editable) |

> **Nada se descarta en silencio.** Si tu juego usa una acción que un destino no
> puede reproducir (por ejemplo, algunas acciones no son compatibles con la
> exportación Kivy/Android), la exportación tiene éxito de todos modos pero te indica
> exactamente qué acciones se **omitieron**, para que puedas ajustar. Si tu proyecto
> usa una [extensión](Extensions_es) desactivada (p. ej. la Vista 3D), el IDE te
> avisa al cargar.

---

## Exportación Windows EXE

Crea un ejecutable Windows independiente que funciona sin Python instalado.

### Cómo exportar

1. Abre **Archivo → Exportar proyecto…** (Ctrl+E) y elige **Windows**
2. Elige una carpeta de salida
3. Espera a que termine el proceso de compilación
4. Encuentra el archivo .exe en la carpeta de salida

### Qué se crea

```
carpeta_salida/
├── MiJuego.exe       # Ejecutable principal
├── _internal/        # Bibliotecas necesarias
└── assets/           # Recursos del juego
```

### Requisitos

- PyInstaller (instalado con `pip install pyinstaller`)
- Sistema Windows para la compilación (la compilación cruzada no es compatible)

### Distribución

Para compartir el juego:
1. Comprime en zip toda la carpeta de salida
2. Distribuye el archivo zip
3. Los usuarios extraen y ejecutan el .exe

### Solución de problemas

**DLL faltantes:** Asegúrate de que todas las dependencias estén incluidas. Revisa la salida de PyInstaller en busca de advertencias.

**Alertas de antivirus:** Algunos antivirus marcan los ejecutables de PyInstaller. Es un falso positivo. Puede que tengas que firmar tu ejecutable.

---

## Exportación de app macOS

Crea un paquete `.app` nativo para macOS con PyInstaller.

### Cómo exportar

1. Abre **Archivo → Exportar proyecto…** (Ctrl+E) y elige **macOS**
2. Elige una carpeta de salida
3. Espera a que termine la compilación
4. Encuentra `MiJuego.app` en la carpeta de salida

### Requisitos

- Un **Mac** para la compilación (la compilación cruzada desde Windows/Linux no es compatible)
- PyInstaller y Kivy instalados en el Python de compilación

### Distribución

Comprime en zip el paquete `.app` para compartirlo. Las apps sin firmar activan
Gatekeeper en otros Mac — los usuarios hacen clic derecho → **Abrir** la primera
vez, o firmas/notarizas la app con una cuenta de Apple Developer.

---

## Exportación HTML5

Crea un único archivo HTML que funciona en los navegadores web.

### Cómo exportar

1. Ve a **Archivo → Exportar como HTML5…**
2. Elige una ubicación de salida
3. Selecciona las opciones (compresión, etc.)
4. Haz clic en Exportar

### Qué se crea

```
carpeta_salida/
└── MiJuego.html      # Juego de un solo archivo
```

### Características

- Funciona en cualquier navegador moderno (Chrome, Firefox, Edge, Safari)
- No requiere instalación
- Comprimido con gzip para una carga rápida
- Compatible con móviles con controles táctiles

### Alojar tu juego

Sube el archivo HTML a:
- Tu propio servidor web
- GitHub Pages (gratuito)
- itch.io (alojamiento orientado a juegos)
- Cualquier alojamiento de archivos estáticos

### Compatibilidad de navegadores

| Navegador | Soporte |
|-----------|---------|
| Chrome 80+ | Completo |
| Firefox 75+ | Completo |
| Edge 80+ | Completo |
| Safari 13+ | Completo |
| Chrome móvil | Completo |
| Safari móvil | Completo |

### Limitaciones

- Algunas funciones podrían no funcionar (acceso al sistema de archivos, etc.)
- El audio podría requerir una interacción del usuario para iniciarse
- El rendimiento depende del dispositivo/navegador

---

## Exportación Linux

Crea un ejecutable Linux nativo.

### Cómo exportar

1. Abre **Archivo → Exportar proyecto…** (Ctrl+E) y elige **Linux**
2. Elige una carpeta de salida
3. Espera el proceso de compilación

### Requisitos

- Sistema Linux para la compilación
- Python 3.10+
- PyInstaller

### Distribución

```bash
# Hacer el archivo ejecutable
chmod +x MiJuego

# Ejecutar el juego
./MiJuego
```

Distribuye como archivo .tar.gz:
```bash
tar -czvf MiJuego-linux.tar.gz MiJuego/
```

---

## Exportación Kivy (móvil)

Crea apps móviles para iOS y Android usando el framework Kivy.

### Cómo exportar

1. Ve a **Archivo → Exportar a Kivy…**
2. Elige una carpeta de salida
3. Configura los ajustes móviles
4. Exporta el proyecto Kivy

### Compilar para Android

El proyecto Kivy exportado usa Buildozer para crear los APK:

```bash
cd proyecto_exportado
pip install buildozer
buildozer init
buildozer android debug
```

### Compilar para iOS

Requiere un Mac con Xcode:

```bash
cd proyecto_exportado
pip install kivy-ios
toolchain build python3 kivy
toolchain create MiJuego ~/proyecto_ios
```

### Consideraciones móviles

- Los controles táctiles se asignan automáticamente
- El escalado de pantalla se gestiona automáticamente
- Prueba en varios tamaños de pantalla
- Optimiza los tamaños de los recursos para móvil

---

## Exportación del proyecto (.zip)

Comparte el **proyecto editable** en sí (no un juego compilado): usa
**Archivo → Exportar proyecto…** (Ctrl+E) para crear un archivo `.zip` que otra
persona puede volver a abrir en PyGameMaker. Ideal para la colaboración, las copias
de seguridad o la entrega de trabajos escolares.

---

## Opciones de exportación

### Ajustes generales

| Ajuste | Descripción |
|--------|-------------|
| **Nombre del juego** | Nombre mostrado en la barra de título/app |
| **Icono** | Icono de la aplicación (Windows/móvil) |
| **Versión** | Número de versión (1.0.0) |
| **Autor** | Nombre del desarrollador |

### Ajustes de Windows

| Ajuste | Descripción |
|--------|-------------|
| **Consola** | Mostrar la ventana de consola (para depuración) |
| **Un archivo** | Un solo .exe vs. carpeta con _internal |
| **UPX** | Comprimir con UPX (tamaño reducido) |

### Ajustes de HTML5

| Ajuste | Descripción |
|--------|-------------|
| **Compresión** | Habilitar la compresión gzip |
| **Pantalla completa** | Iniciar en modo pantalla completa |
| **Controles táctiles** | Mostrar los controles en pantalla |

---

## Lista de verificación antes de exportar

Antes de exportar, verifica:

- [ ] Todos los recursos están incluidos en el proyecto
- [ ] El juego funciona correctamente en el IDE
- [ ] No hay mensajes de depuración ni código de prueba
- [ ] El orden de las salas es correcto (sala inicial primero)
- [ ] Los archivos de audio están en formatos compatibles
- [ ] Los sprites están optimizados por tamaño de archivo

---

## Optimizar el tamaño de los archivos

### Sprites
- Usa dimensiones apropiadas (no sobredimensionadas)
- Comprime los archivos PNG
- Considera el JPEG para imágenes sin transparencia

### Audio
- Usa OGG/MP3 para la música (no WAV)
- Mantén cortos los efectos de sonido
- Frecuencias de muestreo más bajas para sonidos simples

### General
- Elimina los recursos no utilizados
- Minimiza los tamaños de las salas
- Prueba en las plataformas destino

---

## Probar las exportaciones

Prueba siempre tu juego exportado:

1. **Windows:** Prueba en un PC limpio sin Python
2. **HTML5:** Prueba en varios navegadores
3. **Linux:** Si es posible, prueba en diferentes distribuciones
4. **Móvil:** Prueba en dispositivos reales, no solo en emuladores

---

## Plataformas de distribución

### itch.io
- Alojamiento gratuito para juegos indie
- Compatible con HTML5, Windows, Linux, Mac
- Sistema de pago integrado

### Steam
- Requiere la integración del SDK de Steamworks
- Usa PyInstaller con la API de Steam
- Cuota de publicación de pago

### Google Play (Android)
- Requiere una cuenta de desarrollador (25 $)
- Compila un APK firmado con Buildozer
- Sigue las directrices de contenido

### App Store (iOS)
- Requiere una cuenta de Apple Developer (99 $/año)
- Compila con kivy-ios
- Envía a través de App Store Connect

---

## Próximos pasos

- [[Empezar_es]] - Repasar los conceptos básicos
- [[Troubleshooting_es|Solución de Problemas]] - Errores de dependencias faltantes y otros problemas de exportación
- [[FAQ_es]] - Preguntas comunes sobre la exportación
- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Informar de problemas de exportación
