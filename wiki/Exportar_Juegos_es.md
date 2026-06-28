# Exportar Juegos

> [English](Exporting-Games) | [Français](Exportation_fr) | [Deutsch](Spiele_Exportieren_de) | [Italiano](Esportare_Giochi_it) | [Español](Exportar_Juegos_es) | [Português](Exportar_Jogos_pt) | [Slovenščina](Izvoz_Iger_sl) | [Українська](Eksport_Ihor_uk) | [Русский](Eksport_Igr_ru)

---

[Volver al Inicio](Home_es)

Aprende como exportar tus juegos pyGM para diferentes plataformas.

## Resumen

pyGM permite la exportacion para:
- Windows (EXE)
- macOS (APP)
- Linux
- Web (HTML5)

## Preparacion para la exportacion

### Antes de exportar, verifica
1. **Todos los recursos presentes**: Sprites, sonidos, etc.
2. **Juego probado**: Sin errores criticos
3. **Configuraciones optimizadas**: Resolucion, pantalla completa

### Configuracion del proyecto
- **Nombre del juego**: Nombre mostrado
- **Version**: Numero de version
- **Icono**: Icono de la aplicacion
- **Pantalla de inicio**: Splash Screen

## Exportacion Windows

### Requisitos
- pyinstaller instalado
- Sistema Windows o compilacion cruzada

### Pasos
1. Ve a Archivo > Exportar
2. Selecciona "Windows Executable"
3. Configura las opciones:
   - Archivo de icono
   - Ocultar ventana de consola
   - Archivo EXE unico
4. Haz clic en "Exportar"

### Salida
- Archivo EXE unico
- O carpeta con dependencias

## Exportacion macOS

### Requisitos
- Sistema macOS recomendado
- py2app o pyinstaller

### Pasos
1. Archivo > Exportar > macOS
2. Ingresa nombre del App Bundle
3. Elige icono (formato ICNS)
4. Exportar

## Exportacion Linux

### Opciones
- AppImage (recomendado)
- Paquete Debian
- Archivo ejecutable

### Pasos
1. Archivo > Exportar > Linux
2. Elige formato
3. Exportar

## Exportacion Web (HTML5)

### Ventajas
- Funciona en el navegador
- Facil de compartir
- Sin instalacion necesaria

### Pasos
1. Archivo > Exportar > Web
2. Configura:
   - Tamano del canvas
   - Pantalla de carga
   - Compresion
3. Exportar

### Salida
- Archivo HTML
- Archivos JavaScript
- Carpeta de recursos

### Alojamiento
- Sube a un servidor web
- Usa itch.io
- Usa GitHub Pages

## Opciones de exportacion

### Generales
- **Compresion**: Reducir tamano del archivo
- **Modo depuracion**: Mantener para pruebas
- **Incrustar recursos**: Todo en un archivo

### Especificas de plataforma
- **Windows**: Manifiesto UAC
- **macOS**: Firma de codigo
- **Web**: Version WebGL

## Solucion de problemas

### Problemas comunes

**La exportacion falla**
- Revisa los mensajes de error
- Actualiza pyinstaller

**Faltan recursos**
- Verifica las rutas
- Vuelve a incluir los recursos

**El juego no inicia**
- Prueba en modo depuracion
- Verifica las dependencias

## Optimizacion

1. **Optimiza tamanos de imagen**: Comprime sprites
2. **Comprime audio**: MP3 en lugar de WAV
3. **Elimina recursos no utilizados**
4. **Optimiza el codigo**: Mejora la eficiencia

## Ver tambien

- [FAQ](FAQ_es)
- [Crear tu primer juego](Primer_Juego_es)
- [Empezar](Empezar_es)
