# Editor de Código

> [English](Code-Editor) | [Français](Code-Editor_fr) | [Deutsch](Code-Editor_de) | [Italiano](Code-Editor_it) | [Español](Code-Editor_es)

---

> [Volver al Inicio](Home_es)

Cada objeto en PyGameMaker tiene una pestaña **Editor de Código** junto a
Event List y Blockly — una tercera forma de trabajar con los mismos
eventos y acciones, esta vez como Python real. No es una exportación de
un solo sentido: el código que escribes aquí se vuelve a analizar en
eventos y acciones estructurados, por lo que permanece sincronizado con
las otras dos vistas.

---

## Abrir el Editor de Código

1. Abre un objeto en el Editor de Objetos
2. Haz clic en la pestaña **💻 Editor de Código**

![El Editor de Código en modo "Ver Código Generado": una clase con un
método por evento (on_create, on_step, on_collision_obj_power, ...),
mostrando el Python real al que compilan tus eventos y acciones
visuales](images/code-editor.png)

---

## Dos Modos

Un menú desplegable arriba alterna entre ellos:

### 📖 Ver Código Generado

Solo lectura. Muestra el Python al que compilan los eventos y acciones
actuales de tu objeto — un método por evento (`on_create`, `on_step`,
`on_collision_obj_enemigo`, ...), llamando a `self.*` y `game.*` igual
que lo hace el motor en tiempo de ejecución. Una acción para la que el
generador no tiene una equivalencia Python limpia igualmente aparece,
marcada con un comentario (`# Unknown action: ...`) encima de la línea
que produjo — nada se oculta, ni siquiera en los casos límite. Haz clic
en **🔄 Actualizar** para regenerar después de cambiar eventos en otro
lugar.

### ✏️ Editar Código Personalizado

Editable, con resaltado de sintaxis Python. Empieza a escribir (o edita
el código inicial heredado del modo Ver) y PyGameMaker analiza tu clase
unos 1,5 segundos después de que dejas de escribir — una píldora de
estado junto a la barra de herramientas muestra **idle / busy / error /
empty** mientras tanto. Tras un análisis exitoso, tus métodos
**reemplazan** los eventos y acciones del objeto (sin fusionar) —
cualquier método de evento que tu código defina se convierte en la lista
de eventos de ese objeto, visible de inmediato también en las pestañas
Event List y Blockly.

Si el análisis falla (un error de sintaxis, o código que el analizador
no puede traducir a eventos), la píldora de estado muestra el error y no
se aplica nada — los eventos de tu objeto permanecen como estaban hasta
que el código se analice correctamente.

---

## Por Qué Usarlo

- **Velocidad** — cierta lógica (un cálculo con múltiples ramas, un
  bucle, una fórmula puntual) se escribe más rápido de lo que se
  ensambla con bloques o una lista de acciones.
- **Puente de aprendizaje** — cambia los eventos de un objeto construido
  por un principiante al modo Ver para ver el equivalente en código
  real, un siguiente paso natural para un estudiante que pasa de la
  programación visual a Python.
- **Precisión** — todo lo que se pueda expresar como un método Python
  simple en el objeto funciona, sin esperar a que exista una acción
  visual correspondiente.

Este es el mismo mecanismo subyacente que la acción **Ejecutar Código**
disponible desde la lista de acciones / Blockly (categoría *Control*) —
la pestaña Editor de Código simplemente trabaja a la escala de un objeto
completo en lugar de una sola acción.

---

## Próximos Pasos

- [[Editor_Objetos_es|Editor de Objetos]] - Dónde se encuentra la pestaña Editor de Código
- [[Programacion_Visual_es|Programación Visual]] - La vista Blockly de los mismos eventos
- [[Eventos_y_Acciones_es|Eventos y Acciones]] - Qué hace realmente cada acción
