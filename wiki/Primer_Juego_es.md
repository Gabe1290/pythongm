# Crear tu primer juego

> [English](Creating-Your-First-Game) | [Français](Premier_Jeu_fr) | [Deutsch](Erstes_Spiel_de) | [Italiano](Primo_Gioco_it) | [Español](Primer_Juego_es) | [Português](Primeiro_Jogo_pt) | [Slovenščina](Prva_Igra_sl) | [Українська](Persha_Gra_uk) | [Русский](Pervaya_Igra_ru)

---

[Volver al Inicio](Home_es)

En esta guia crearas un juego simple para aprender los conceptos basicos de pyGM.

## Resumen

Crearemos un juego simple con:
- Un personaje jugador que puede moverse
- Un objeto coleccionable
- Un sistema de puntuacion

## Paso 1: Crear un nuevo proyecto

1. Inicia pyGM
2. Selecciona "Nuevo Proyecto"
3. Ingresa un nombre para el proyecto
4. Elige una ubicacion para guardar

## Paso 2: Crear sprites

### Sprite del jugador
1. Clic derecho en "Sprites" en el arbol de recursos
2. Selecciona "Nuevo Sprite"
3. Usa el editor integrado o importa una imagen
4. Nombralo "spr_jugador"

### Sprite del objeto coleccionable
1. Crea otro sprite
2. Nombralo "spr_moneda"

## Paso 3: Crear objetos

### Objeto jugador
1. Clic derecho en "Objetos"
2. Selecciona "Nuevo Objeto"
3. Nombralo "obj_jugador"
4. Asigna "spr_jugador" como sprite

### Agregar movimiento
1. Agrega el evento "Presion de tecla"
2. Usa acciones para el movimiento:
   - Flecha arriba: Mover hacia arriba
   - Flecha abajo: Mover hacia abajo
   - Flecha izquierda: Mover hacia la izquierda
   - Flecha derecha: Mover hacia la derecha

### Objeto moneda
1. Crea "obj_moneda"
2. Asigna "spr_moneda"
3. Agrega evento de colision con el jugador
4. Accion: Destruir instancia y agregar puntos

## Paso 4: Crear una sala

1. Clic derecho en "Salas"
2. Selecciona "Nueva Sala"
3. Nombrala "rm_nivel1"
4. Coloca los objetos:
   - Un jugador
   - Varias monedas

## Paso 5: Probar el juego

1. Haz clic en "Ejecutar juego" o presiona F5
2. Prueba el movimiento
3. Recoge las monedas

## Ideas de expansion

- Agregar obstaculos
- Implementar un sistema de tiempo
- Crear diferentes niveles
- Agregar efectos de sonido

## Proximos pasos

- [Profundizar en Eventos y Acciones](Eventos_y_Acciones_es)
- [Aprender Programacion Visual](Programacion_Visual_es)
- [Exportar Juegos](Exportar_Juegos_es)
