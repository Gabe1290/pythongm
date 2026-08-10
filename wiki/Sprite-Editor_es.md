# Editor de Sprites

> [English](Sprite-Editor) | [Français](Sprite-Editor_fr) | [Deutsch](Sprite-Editor_de) | [Italiano](Sprite-Editor_it) | [Español](Sprite-Editor_es) | [Português](Sprite-Editor_pt)

---

> [Volver al Inicio](Home_es)

Los sprites son las imágenes y animaciones adjuntas a los objetos. El
Editor de Sprites es una herramienta de pixel art integrada — dibuja
sprites directamente en PyGameMaker, sin necesidad de un editor de
imágenes externo.

---

## Abrir el Editor de Sprites

1. Haz doble clic en un sprite existente en el árbol de recursos, o
2. Clic derecho en **Sprites** > **Crear Sprite**

![El Editor de Sprites: herramientas de dibujo y tamaño de pincel a la
izquierda, debajo el selector de origen y la opción Precise Collision,
una paleta de colores, el lienzo en el centro mostrando un personaje en
pixel art con un zoom de 10x, y la tira de fotogramas abajo (8
fotogramas, botón Play, agregar/duplicar/eliminar fotograma)](images/sprite-editor.png)

---

## Herramientas de Dibujo

| Herramienta | Atajo | Qué hace |
|------|----------|---------------|
| **Lápiz** | P | Dibujar píxeles individuales |
| **Borrador** | E | Borrar píxeles (transparencia) |
| **Cuentagotas** | I | Tomar un color del lienzo |
| **Relleno** | G | Rellenar un área conectada (bote de pintura) |
| **Línea** | L | Dibujar una línea recta |
| **Rectángulo** | R | Dibujar un rectángulo (activa **Relleno** para sólido/contorno) |
| **Elipse** | O | Dibujar una elipse (también respeta **Relleno**) |
| **Selección** | S | Selección rectangular — mover, copiar, cortar, pegar o eliminar los píxeles seleccionados |

**El tamaño del pincel** se aplica al Lápiz, al Borrador y a los
contornos de líneas/formas. La paleta de colores contiene un conjunto de
colores de trabajo más la paleta rápida estándar de 12 colores; haz clic
en una muestra para elegirla, o usa el Cuentagotas para tomar un color
directamente del sprite.

---

## Operaciones del Lienzo

- **Espejo H / Espejo V** — invierte el fotograma actual horizontal o verticalmente
- **Redimensionar** — abre un diálogo con dos modos distintos:
  - **Escalar Imagen** — estira el contenido existente a un nuevo tamaño
  - **Redimensionar Lienzo** — mantiene el contenido en su tamaño original y añade/recorta espacio alrededor, anclado a una esquina, borde o el centro a elección
- **Cuadrícula** — activa/desactiva una superposición de cuadrícula de píxeles (no afecta la imagen guardada)
- **Acercar / Alejar** — el lienzo suele trabajar a 10x o más, ya que los sprites suelen ser pequeños (16×16 a 64×64 es común)
- **Exportar PNG…** — guarda el fotograma actual como archivo `.png` independiente
- Clic derecho en el lienzo para **Copiar / Cortar / Pegar / Eliminar / Deseleccionar / Seleccionar Todo** (atajos estándar: Ctrl+C / Ctrl+X / Ctrl+V / Supr / Esc)

---

## Fotogramas y Animación

Un sprite puede contener varios fotogramas, reproducidos como animación
durante la ejecución del juego. La tira de fotogramas en la parte
inferior del editor:

| Control | Efecto |
|---------|--------|
| **+** | Agregar un fotograma nuevo en blanco |
| **D** | Duplicar el fotograma actual |
| **-** | Eliminar el fotograma actual |
| **Play** | Previsualizar la animación en el editor a la frecuencia de fotogramas del sprite |

Haz clic en una miniatura de fotograma para saltar a él y dibujar específicamente en ese fotograma.

---

## Origen y Colisión

- **Origen** — el punto que los objetos que usan este sprite consideran
  como su posición `(x, y)`. Preajustes: Arriba-Izquierda,
  Arriba-Centro, Centro, Centro-Abajo, Abajo-Izquierda, Abajo-Derecha, o
  **Personalizado** (X/Y exactos). La mayoría de los personajes de
  plataformas/vista superior usan **Centro-Abajo** para que los pies del
  sprite queden en la posición Y del objeto.
- **Precise Collision** — al activarse, las colisiones contra este
  sprite prueban los píxeles no transparentes reales en lugar de la
  caja delimitadora del sprite. Más precisa para sprites de forma
  irregular, más costosa de calcular — déjala desactivada para formas
  simples (paredes, monedas) y resérvala para sprites donde una colisión
  por caja delimitadora se vería visiblemente incorrecta.

---

## Próximos Pasos

- [[Editor_Objetos_es|Editor de Objetos]] - Adjuntar un sprite a un objeto de juego
- [[Editor_Salas_es|Editor de Salas]] - Colocar instancias de objeto que usen tu sprite
- [[Primer_Juego_es|Crea Tu Primer Juego]] - Un tutorial completo que comienza dibujando sprites
