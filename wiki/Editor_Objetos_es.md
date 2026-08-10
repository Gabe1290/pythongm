# Editor de Objetos

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

[Volver al Inicio](Home_es)

Los objetos son los bloques fundamentales de construcción de tu juego.
Representan todo, desde jugadores y enemigos hasta coleccionables y
elementos de interfaz.

---

## Abrir el Editor de Objetos

1. Haz doble clic en un objeto existente en el árbol de recursos, o
2. Clic derecho en **Objects** > **Create Object**

![El Editor de Objetos: una lista de eventos a la izquierda (Create,
Step, varios eventos Collision, Keyboard, No More Lives, Game Start),
propiedades del objeto (sprite, parent, Visible/Persistent/Solid) a la
derecha, y las pestañas Event List / Blockly / Editor de Código que
cambian cómo editas las acciones de cada evento](images/object-editor.png)

---

## Propiedades del Objeto

| Propiedad | Descripción |
|-----------|-------------|
| **Name** | Identificador único para el objeto (ej. `obj_jugador`) |
| **Sprite** | La representación visual del objeto |
| **Visible** | Si el objeto se dibuja (predeterminado: sí) |
| **Solid** | Se usa para la detección de colisiones con objetos sólidos |
| **Depth** | Orden de dibujo (menor = se dibuja encima) |
| **Persistent** | El objeto sobrevive a los cambios de sala |
| **Parent Object** | Hereda propiedades/eventos comunes de otro objeto |

### Convención de Nombres

Usa el prefijo `obj_` para los objetos:
- `obj_jugador`
- `obj_enemigo`
- `obj_moneda`
- `obj_pared`

---

## Eventos

Los eventos son disparadores que provocan la ejecución de acciones. Haz
clic en "Add Event" para agregar uno.

### Eventos Comunes

| Evento | Cuándo se Dispara |
|-------|------------------|
| **Create** | Una vez, cuando se crea una instancia |
| **Destroy** | Cuando la instancia es destruida |
| **Step** | En cada fotograma del juego (60 veces por segundo) |
| **Draw** | Durante la fase de dibujo |
| **Alarm [0-11]** | Cuando un temporizador de alarma llega a cero |

### Eventos de Teclado

| Evento | Cuándo se Dispara |
|-------|------------------|
| **Key Press** | Una vez, cuando se presiona una tecla |
| **Key Release** | Una vez, cuando se suelta una tecla |
| **Keyboard** | En cada fotograma mientras una tecla está presionada |
| **No Key** | Cuando no hay ninguna tecla presionada |

### Eventos de Ratón

| Evento | Cuándo se Dispara |
|-------|------------------|
| **Mouse Button** | Al hacer clic en la instancia |
| **Global Mouse** | Al hacer clic en cualquier lugar |
| **Mouse Enter** | Cuando el cursor entra en la instancia |
| **Mouse Leave** | Cuando el cursor sale de la instancia |

### Eventos de Colisión

| Evento | Cuándo se Dispara |
|-------|------------------|
| **Collision with [objeto]** | Al tocar otro tipo de objeto |

### Otros Eventos

| Evento | Cuándo se Dispara |
|-------|------------------|
| **Outside Room** | Cuando la instancia sale de la sala |
| **Intersect Boundary** | Cuando la instancia toca el borde de la sala |
| **Game Start** | Una vez, al iniciar el juego |
| **Game End** | Una vez, al cerrar el juego |
| **Room Start** | Al entrar en una sala |
| **Room End** | Al salir de una sala |

---

## Acciones

Las acciones son operaciones que se ejecutan cuando se dispara un
evento. Cada evento puede tener varias acciones, ejecutadas en orden.

### Acciones de Movimiento
- **Set Speed** — Establece la velocidad de movimiento
- **Set Direction** — Establece la dirección de movimiento (0-360 grados)
- **Set Horizontal Speed** — Establece hspeed
- **Set Vertical Speed** — Establece vspeed
- **Mover hacia un punto** — Mueve hacia coordenadas
- **Jump to Position** — Teletransporta instantáneamente a coordenadas
- **Saltar a la posición inicial** — Vuelve a la posición de creación
- **Saltar a posición aleatoria** — Teletransporta a una posición aleatoria

### Acciones de Instancia
- **Create Instance** — Crea un nuevo objeto
- **Destroy Instance** — Elimina la instancia actual
- **Change Instance** — Se transforma en otro tipo de objeto

### Acciones de Temporización
- **Set Alarm** — Inicia un temporizador de cuenta regresiva
- **Sleep** — Pausa la ejecución por un breve momento

### Acciones de Dibujo
- **Draw Sprite** — Dibuja un sprite
- **Draw Text** — Muestra texto en pantalla
- **Draw Rectangle** — Dibuja un rectángulo relleno o contorneado
- **Dibujar puntuación** — Muestra la puntuación actual
- **Dibujar vidas** — Muestra las vidas restantes
- **Dibujar barra de salud** — Muestra la barra de salud

### Score/Lives/Health
- **Set Score** — Cambia el valor de la puntuación
- **Set Lives** — Cambia el número de vidas
- **Set Health** — Cambia el valor de la salud
- **Comprobar puntuación** — Verifica una condición de puntuación
- **Comprobar vidas** — Verifica una condición de vidas
- **Comprobar salud** — Verifica una condición de salud

### Acciones de Sala
- **Next Room** — Va a la siguiente sala
- **Previous Room** — Va a la sala anterior
- **Restart Room** — Reinicia la sala actual
- **Go to Room** — Salta a una sala específica

### Acciones Sound
- **Play Sound** — Reproduce un efecto de sonido
- **Stop Sound** — Detiene un sonido en reproducción
- **Play Music** — Reproduce música de fondo
- **Stop Music** — Detiene la música de fondo

### Acciones de Variables
- **Set Variable** — Asigna un valor a una variable
- **Comprobar variable** — Verifica una condición de variable

---

## Programación Visual con Blockly

En lugar de usar la lista de acciones, puedes cambiar a la pestaña
**Blockly** para la programación visual:

1. Abre un objeto
2. Haz clic en la pestaña **Blockly**
3. Arrastra bloques desde la barra de herramientas para crear la lógica
4. Los bloques encajan entre sí para formar programas completos

Consulta [[Programacion_Visual_es]] para más detalles.

---

## Consejos y Buenas Prácticas

### Organización
- Da a los objetos nombres descriptivos
- Agrupa objetos relacionados con prefijos similares
- Usa el evento Create solo para inicialización

### Rendimiento
- Evita cálculos pesados en el evento Step
- Usa alarmas en lugar de contar fotogramas manualmente
- Destruye las instancias que salen de la sala

### Depuración
- Usa la acción **Show Message** para mostrar valores
- Revisa la salida de la consola para errores
- Prueba frecuentemente mientras desarrollas

---

## Ejemplo: IA Simple para Enemigo

```
Create Event:
  - Set Alarm[0] = 60 (1 segundo a 60 FPS)
  - Set direction = random(360)
  - Set speed = 2

Alarm[0] Event:
  - Set direction = random(360)
  - Set Alarm[0] = 60

Collision with obj_player:
  - Set Lives relative = -1
  - Destroy Instance
```

---

## Próximos Pasos

- [[Editor_Salas_es]] - Coloca objetos en tus niveles de juego
- [[Eventos_y_Acciones_es]] - Referencia completa de todos los eventos y acciones
- [[Programacion_Visual_es]] - Aprende la programación por bloques con Blockly
