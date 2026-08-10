# Solución de Problemas

> [English](Troubleshooting) | [Français](Troubleshooting_fr) | [Deutsch](Troubleshooting_de) | [Italiano](Troubleshooting_it) | [Español](Troubleshooting_es) | [Português](Troubleshooting_pt)

---

> [Volver al Inicio](Home_es)

Problemas comunes y dónde buscar. Para problemas específicos de
instalación (Python no encontrado, dependencias faltantes, bibliotecas
de visualización de Linux), consulta primero la sección Solución de
Problemas de [[Empezar_es|Primeros Pasos]] — esta página cubre problemas
que surgen una vez que PyGameMaker ya está en ejecución.

---

## Mi juego se bloquea o se cierra inmediatamente al presionar Probar Juego (F5)

**Ejecuta el IDE desde una terminal, no desde un acceso directo del
escritorio, para ver el error.** El traceback de un subproceso de
prueba de juego que falla se registra en la salida de consola del
propio IDE (`python main.py` en una terminal) — si iniciaste el IDE sin
una consola visible (por ejemplo, un acceso directo de Windows), ese
mensaje no tiene dónde aparecer. Vuelve a iniciar desde una terminal y
reproduce el fallo para ver el traceback real de Python.

Causas comunes:
- Una acción **Ejecutar Código** o código personalizado en el Editor de
  Código con un error de sintaxis o un error tipográfico en una llamada
  `game.*`/`self.*`
- Una acción de colisión o comparación que hace referencia a un objeto
  que desde entonces fue renombrado o eliminado

---

## El propio IDE se bloqueó al intentar abrir un editor

Revisa **`~/pygamemaker_crash.log`** (en tu carpeta personal) — los
fallos del editor de objetos/salas/sprites se escriben ahí
específicamente para que sean visibles incluso cuando el IDE se inició
sin una ventana de consola. Incluye la sección relevante de ese archivo
si reportas el error.

---

## La exportación dice "X no encontrado" / falta una dependencia

Las exportaciones de escritorio y móviles (.exe de Windows, .app de
macOS, binario de Linux, Kivy/Android/iOS) empaquetan un entorno de
ejecución mediante PyInstaller o Buildozer, y estas herramientas deben
estar instaladas en el **mismo Python que ejecuta el IDE** — una
instalación a nivel de sistema en otra parte de la máquina no cuenta. El
mensaje de error del diálogo de exportación da la solución exacta, pero
en resumen:

- **No se necesitan derechos de administrador.** Activa tu entorno
  virtual y ejecuta `pip install <paquete>`, o instala en tu propia
  cuenta con `pip install --user <paquete>` — ambos funcionan sin
  derechos de administrador.
- Instalar todo de una vez: `pip install -r requirements.txt`
- **¿No quieres ninguna instalación en absoluto?** Usa en su lugar la
  exportación **HTML5 (Navegador Web)** — no necesita nada instalado
  localmente y el resultado funciona en cualquier navegador. (Nota que
  esto solo aplica a *construir* la exportación — un `.exe`/`.app`
  terminado no necesita nada instalado en la máquina que solo lo
  *ejecuta*.)

---

## Recibí una advertencia antes de Exportar ("X usa Y pero no hay Z")

La exportación ejecuta primero una validación del proyecto y muestra
todo lo que encuentra antes de que aparezca el diálogo de Exportar — por
ejemplo, un objeto que usa **Siguiente Sala** en un proyecto con una
sola sala, lo cual no tendría efecto. Estas son **advertencias, no
errores**: haz clic en OK y la exportación continúa; señalan lógica que
probablemente no hará lo que esperas, sin impedirte publicar.

---

## Un sprite muestra una insignia roja "(no importado)" en el árbol de recursos

Esto significa que el archivo de imagen del sprite falta en el disco
(generalmente porque un proyecto se copió o compartió sin su carpeta
`sprites/`). Es puramente informativo — la ejecución y la exportación lo
ignoran — y **se corrige automáticamente en el próximo guardado**, una
vez que el archivo esté realmente presente de nuevo. No se necesita
corrección manual más allá de asegurarte de que el archivo de imagen
esté donde el sprite lo espera.

---

## Algo más anda mal

- Consulta la [[FAQ_es|FAQ]] para preguntas comunes
- Reporta errores en el [Rastreador de Problemas de GitHub](https://github.com/Gabe1290/pythongm/issues) — incluye tu sistema operativo, versión de Python, y (si es relevante) la salida de consola o `~/pygamemaker_crash.log`

---

## Próximos Pasos

- [[Empezar_es|Primeros Pasos]] - Solución de problemas de instalación
- [[Exportar_Juegos_es|Exportar Juegos]] - Referencia completa de exportación
- [[FAQ_es|FAQ]] - Preguntas frecuentes
