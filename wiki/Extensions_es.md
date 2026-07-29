# Extensiones

*[Inicio](Home_es) | [Vista 3D](3D-View_es) | [Referencia completa de acciones](Full-Action-Reference_es)*

---

Una **extensión** es un complemento autónomo que añade capacidades a PyGameMaker sin
modificar el motor base. Una extensión puede aportar:

- nuevas **acciones** (aparecen en el selector de acciones como cualquier acción
  integrada),
- una nueva forma de **dibujar una sala** (un renderizador personalizado), y
- el **código de exportación** correspondiente, para que los juegos que la usan sigan
  exportándose a HTML5 y Kivy/Android.

La extensión integrada **2.5D Raycast** (la función [Vista 3D](3D-View_es)) es el
ejemplo de referencia: añade cuatro acciones "Vista 3D" y un renderizador en primera
persona, y se exporta a los tres destinos.

---

## Activar y desactivar

Las extensiones se entregan **activadas**. Puedes desactivar una (o activar una que
se entrega desactivada) sin editar código, mediante la clave `extensions` de tu
configuración — un mapa `nombre de carpeta → activado/desactivado`:

```json
"extensions": { "raycast_2_5d": false }
```

Una entrada **ausente** significa "usar el valor predeterminado de la extensión", así
que nada desaparece nunca por una clave faltante. Los cambios surten efecto en el
siguiente inicio (las acciones se registran al arrancar).

Con la extensión 2.5D Raycast desactivada, una sala que habilita la vista en primera
persona simplemente se renderiza cenital.

---

## Cuando un proyecto necesita una extensión

Como una extensión puede desactivarse, PyGameMaker te ayuda a evitar sorpresas:

- **Al cargar**, si un proyecto usa acciones de una extensión actualmente
  desactivada, el IDE muestra un aviso que nombra la extensión y las funciones
  afectadas (para que un juego 3D no se renderice cenital en silencio).
- **Al guardar**, el proyecto registra las extensiones de las que dependen sus
  acciones en `project.json` (una lista `requires_extensions`) — una nota duradera
  que puede ver cualquiera con quien compartas el proyecto. Un proyecto que no usa
  acciones de extensiones simplemente omite el campo.

---

## Extensiones y complementos (plugins)

Ambos añaden acciones; solo difieren en el empaquetado:

| | Complemento | Extensión |
|---|--------|-----------|
| Forma | un único archivo `.py` en `plugins/` | una carpeta en `extensions/` con un manifiesto |
| Ideal para | un pequeño conjunto de acciones | una función que abarca varios archivos y/o que dibuja/exporta |
| Ejemplo | las acciones **Audio** (`plugins/audio_actions.py`) | **2.5D Raycast** (`extensions/raycast_2_5d/`) |

---

## Cómo es una carpeta de extensión

Para los curiosos (y para quien escriba una), una extensión es una carpeta legible:

```
extensions/raycast_2_5d/
├── extension.json     # manifiesto: nombre, versión, activado, provides_actions
├── actions.py         # los esquemas de acciones (mostrados en el selector)
├── handlers.py        # qué hacen las acciones en ejecución
├── renderer.py        # el renderizador de sala personalizado (el raycaster)
├── state.py           # el estado por sala (en el espacio de nombres de la sala)
├── hud.py             # los generadores de geometría de minimapa / barra DOOM
├── export_html5.js    # el port HTML5, inyectado en la exportación web
├── export_kivy.py     # el port Kivy, inyectado en la exportación móvil/ordenador
└── README.md          # cómo encaja todo
```

La lista `provides_actions` del manifiesto es lo que permite al IDE nombrar la
extensión exacta cuando un proyecto necesita una desactivada.

---

## Véase también

- [Vista 3D](3D-View_es) — la función que proporciona la extensión integrada
- [Referencia completa de acciones](Full-Action-Reference_es) — las acciones de extensión también aparecen aquí
- [Exportar juegos](Exportar_Juegos_es) — las funciones de extensión se trasladan a las exportaciones
