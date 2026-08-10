# Gestor de Recursos

> [English](Asset-Manager) | [Français](Asset-Manager_fr) | [Deutsch](Asset-Manager_de) | [Italiano](Asset-Manager_it) | [Español](Asset-Manager_es)

---

> [Volver al Inicio](Home_es)

Más allá del crear/renombrar/eliminar cotidiano del árbol de recursos,
PyGameMaker rastrea **dónde se usa realmente cada recurso**, mantiene
los recursos eliminados recuperables en lugar de perderlos para siempre,
y puede encontrar tanto recursos sin usar como archivos huérfanos que
saturan la carpeta del proyecto. Todo esto vive en el menú
**Herramientas**.

---

## Filtrar el Árbol de Recursos

Escribe en el cuadro de filtro sobre el árbol de recursos para
restringirlo a los nombres coincidentes mientras escribes. La
coincidencia ignora mayúsculas/minúsculas y actúa sobre el nombre bruto
del recurso; una categoría (Sprites, Objetos, ...) se oculta una vez que
todos sus elementos hijos quedan filtrados, y reaparece en cuanto uno
vuelve a coincidir.

---

## Seguimiento de Uso

Cada eliminación de recurso ahora comprueba dónde se referencia
realmente ese recurso — otros objetos, salas, acciones — antes de que
confirmes. Si `spr_jugador` es usado por 3 objetos, la confirmación de
eliminación lo indica en lugar de una advertencia genérica, así lo sabes
*antes* de eliminar algo que rompería otras partes del proyecto, no
después.

**Limitación conocida:** este análisis solo ve lo que las estructuras de
datos propias de PyGameMaker pueden ver — parámetros de acción, objetivos
de colisión, instancias de sala, campos sprite/parent. Un nombre de
recurso usado solo dentro de una cadena Python en bruto en el
[[Code-Editor_es|Editor de Código]] o la acción Ejecutar Código (por
ejemplo `game.sounds['explosion'].play()`) no es visible para este
análisis.

---

## Restaurar Recursos Eliminados (Papelera)

**Herramientas > Restaurar Recursos Eliminados...**

Eliminar un recurso no lo borra inmediatamente — sus archivos se mueven
a una Papelera local del proyecto y PyGameMaker guarda un registro de lo
que se eliminó, adónde fueron sus archivos, y cualquier referencia
cruzada que se haya borrado (por ejemplo, el campo sprite de un objeto
que queda vacío porque el sprite al que apuntaba fue eliminado). Este
diálogo lista todo lo que está actualmente en la Papelera con tres
acciones:

| Acción | Efecto |
|--------|--------|
| **Restaurar** | Devuelve el recurso exactamente como estaba. Se niega a sobrescribir si ahora existe un nuevo recurso con el mismo nombre — restaurar tampoco es destructivo. |
| **Eliminar Permanentemente** | Elimina una sola entrada de la papelera para siempre |
| **Vaciar Papelera** | Elimina todo lo que está actualmente en la Papelera |

Las referencias cruzadas que se borraron al eliminar **no** se
reconectan automáticamente al restaurar — verás qué cambió, para que
puedas decidir si reconectarlo en lugar de dejar que PyGameMaker adivine.

Los archivos en la papelera están excluidos de las exportaciones del
proyecto (zip/HTML5/etc.) — un recurso eliminado nunca reaparece
silenciosamente en un juego publicado.

---

## Encontrar Recursos Sin Usar

**Herramientas > Encontrar Recursos Sin Usar...**

Analiza todo el proyecto mediante el mismo análisis de uso anterior y
lista cada recurso sin ninguna referencia, agrupado por categoría, cada
uno con una casilla de verificación. Selecciona los que realmente
quieres eliminar (o **Seleccionar Todo**) y **Mover Selección a la
Papelera** — la misma red de seguridad que cualquier otra eliminación.

**Las salas se manejan con cuidado.** Una sala a la que nadie navega
explícitamente por su nombre — un juego de una sola sala, o la primera
sala de un juego — aparece legítimamente como "sin usar" bajo un simple
conteo de referencias, pero eliminarla rompería el juego. Las salas se
etiquetan *"Salas — no navegadas explícitamente"* en lugar de
simplemente "sin usar", y **Seleccionar Todo omite las salas** a
propósito; aún puedes marcar una individualmente si estás seguro.

---

## Encontrar Archivos Huérfanos

**Herramientas > Encontrar Archivos Huérfanos...**

El problema inverso: archivos que están en la carpeta del proyecto
(`sprites/`, `sounds/`, `backgrounds/`, `fonts/`, `thumbnails/`) que no
tienen **ninguna** entrada correspondiente en el proyecto — dejados por
una operación interrumpida, o colocados a mano fuera del IDE. Los lista
por categoría con el mismo patrón de casilla / Seleccionar Todo /
**Mover Selección a la Papelera** que los recursos sin usar, e incluye
su propio mini panel de Papelera (Restaurar / Eliminar Permanentemente /
Vaciar) en el mismo diálogo — los archivos huérfanos usan un
almacenamiento de papelera separado de las eliminaciones normales de
recursos, ya que nunca fueron una entrada real de project.json para
empezar.

---

## Limpiar Proyecto

**Herramientas > Limpiar Proyecto**

Un barrido de un clic para los archivos `.tmp` restantes — los archivos
temporales que el proceso de guardado atómico de PyGameMaker crea y
normalmente elimina él mismo. Solo se tocan los archivos con más de un
minuto de antigüedad aproximadamente, para que un guardado en curso
nunca esté en riesgo. Informa cuántos archivos se eliminaron, o que no
había nada que limpiar. A diferencia de los diálogos anteriores, estos
archivos nunca pasan por el sistema de recursos ni la Papelera — un
archivo `.tmp` nunca es la copia autorizada de nada, así que se elimina
directamente.

---

## Próximos Pasos

- [[Editor_Salas_es|Editor de Salas]] / [[Editor_Objetos_es|Editor de Objetos]] - De dónde provienen la mayoría de las referencias de recursos
- [[FAQ_es|FAQ]] - Preguntas comunes, incluidas las de seguridad de datos
