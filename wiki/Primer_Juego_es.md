# Crear tu primer juego

> [English](Creating-Your-First-Game) | [Français](Premier_Jeu_fr) | [Deutsch](Erstes_Spiel_de) | [Italiano](Primo_Gioco_it) | [Español](Primer_Juego_es) | [Português](Primeiro_Jogo_pt) | [Slovenščina](Prva_Igra_sl) | [Українська](Persha_Gra_uk) | [Русский](Pervaya_Igra_ru)

---

[Volver al Inicio](Home_es)

En este tutorial, crearemos un juego sencillo "Atrapa las Estrellas" en el que el jugador se mueve para recolectar estrellas que caen.

---

## Lo Que Aprenderás

- Crear sprites
- Crear objetos con eventos y acciones
- Usar el editor de salas
- Ejecutar y probar tu juego

---

## Paso 1: Crear un Nuevo Proyecto

1. Inicia PyGameMaker
2. Ve a **File > New Project**
3. Nombra tu proyecto "CatchTheStars"
4. Haz clic en **Create**

---

## Paso 2: Crear el Sprite del Jugador

1. Haz clic derecho en **Sprites** en el árbol de recursos
2. Selecciona **Create Sprite**
3. Nómbralo `spr_player`
4. Haz clic en **Edit Sprite** para abrir el editor de sprites
5. Dibuja un personaje sencillo (o usa un rectángulo de color 32x32)
6. Haz clic en **Save**

---

## Paso 3: Crear el Sprite de la Estrella

1. Haz clic derecho en **Sprites** > **Create Sprite**
2. Nómbralo `spr_star`
3. Dibuja una forma de estrella (o usa un círculo amarillo)
4. Haz clic en **Save**

---

## Paso 4: Crear el Objeto Jugador

1. Haz clic derecho en **Objects** en el árbol de recursos
2. Selecciona **Create Object**
3. Nómbralo `obj_player`
4. Establece el **Sprite** en `spr_player`

### Agregar Eventos de Teclado

**Flecha Izquierda:**
1. Haz clic en **Add Event** > **Keyboard** > **Left**
2. Agrega la acción: **Set Horizontal Speed** con valor `-4`

**Flecha Derecha:**
1. Haz clic en **Add Event** > **Keyboard** > **Right**
2. Agrega la acción: **Set Horizontal Speed** con valor `4`

**Ninguna Tecla Presionada:**
1. Haz clic en **Add Event** > **Keyboard** > **No Key**
2. Agrega la acción: **Set Horizontal Speed** con valor `0`

---

## Paso 5: Crear el Objeto Estrella

1. Haz clic derecho en **Objects** > **Create Object**
2. Nómbralo `obj_star`
3. Establece el **Sprite** en `spr_star`

### Agregar el Evento Create
1. Haz clic en **Add Event** > **Create**
2. Agrega la acción: **Set Vertical Speed** con valor `3`
3. Agrega la acción: **Jump To Position** con X `irandom(600)`, Y `20`
   — `irandom(n)` elige un número entero aleatorio entre 0 y `n`, así
   que esto dispersa la estrella en un punto aleatorio cerca de la
   parte superior de una sala de 640 píxeles de ancho cada vez que
   (re)aparece

### Agregar el Evento Outside Room
1. Haz clic en **Add Event** > **Other** > **Outside Room**
2. Agrega la acción: **Jump to Start Position**
3. Agrega la acción: **Set Score** con valor `1` y **Relative** marcado

### Agregar la Colisión con el Jugador
1. Haz clic en **Add Event** > **Collision** > selecciona `obj_player`
2. Agrega la acción: **Set Score** con valor `10` y **Relative** marcado
3. Agrega la acción: **Play Sound** (opcional, si tienes un sonido)
4. Agrega la acción: **Jump to Random Position**

---

## Paso 6: Crear la Sala

1. Haz clic derecho en **Rooms** en el árbol de recursos
2. Selecciona **Create Room**
3. Nómbrala `room_game`
4. Establece el tamaño de la sala en **640 x 480**

### Colocar los Objetos
1. Selecciona la pestaña **Objects** en el editor de salas
2. Haz clic en `obj_player` y colócalo en el centro inferior de la sala
3. Haz clic en `obj_star` y coloca de 5 a 10 estrellas dispersas en la parte superior

---

## Paso 7: Mostrar la Puntuación

1. Abre `obj_player`
2. Haz clic en **Add Event** > **Draw**
3. Agrega la acción: **Draw Score** en la posición (10, 10)

---

## Paso 8: ¡Ejecuta Tu Juego!

1. Presiona **F5** o ve a **Build > Test Game**
2. Usa las teclas de flecha izquierda y derecha para moverte
3. ¡Atrapa las estrellas que caen para aumentar tu puntuación!

---

## Mejoras para Probar

### Agregar Vidas
1. Crea un objeto de "game over" que aparezca cuando las vidas lleguen a 0
2. Agrega un evento de colisión con un objeto "malo" que reste vidas

### Agregar Niveles
1. Crea varias salas
2. Usa la acción **Next Room** cuando la puntuación alcance un umbral

### Agregar Sonido
1. Importa archivos de audio en el recurso Sounds
2. Agrega acciones **Play Sound** a los eventos

### Usar la Programación Visual
1. Abre un objeto
2. Haz clic en la pestaña **Blockly** para la programación de arrastrar y soltar
3. Construye la misma lógica visualmente con bloques

---

## Estructura Completa del Proyecto

Después de completar este tutorial, tu proyecto debería tener:

- **Sprites:** spr_player, spr_star
- **Objetos:** obj_player, obj_star
- **Salas:** room_game

---

## Próximos Pasos

- [[Editor_Objetos_es]] - Aprende más sobre las propiedades de los objetos
- [[Eventos_y_Acciones_es]] - Explora todos los eventos y acciones disponibles
- [[Programacion_Visual_es]] - Prueba a construir con bloques Blockly
- [[Exportar_Juegos_es]] - Comparte tu juego con otros
