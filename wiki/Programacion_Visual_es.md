# Programación Visual

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

[Volver al Inicio](Home_es)

pyGM ofrece un sistema de programación visual para el desarrollo de juegos fácil sin código.

## Resumen

Con la programación visual puedes:
- Crear lógica de juego con arrastrar y soltar
- Conectar bloques para comportamientos complejos
- Desarrollar sin conocimientos de programación

## El Editor Blockly

### Interfaz
1. **Paleta de bloques**: Bloques disponibles por categoría
2. **Área de trabajo**: Aquí conectas los bloques
3. **Barra de herramientas**: Guardar, Cargar, Eliminar

### Categorías de bloques
- **Lógica**: Si/Entonces, comparaciones, valores booleanos
- **Bucles**: Repeticiones
- **Matemáticas**: Cálculos
- **Texto**: Operaciones de texto
- **Variables**: Almacenar valores
- **Funciones**: Bloques reutilizables
- **Juego**: Acciones específicas de pyGM

## Usar bloques

### Agregar un bloque
1. Haz clic en una categoría
2. Arrastra un bloque al área de trabajo
3. Conéctalo con otros bloques

### Conectar bloques
- Los bloques encajan automáticamente
- Presta atención a las formas coincidentes
- Es posible anidar bloques

### Configurar un bloque
- Completa los campos de entrada
- Elige opciones del menú desplegable
- Inserta subbloques

## Ejemplos

### Movimiento simple
```
Cuando [flecha derecha] presionada
  Establecer x a (x + 5)
```

### Lógica condicional
```
Si <Vidas <= 0> entonces
  Mostrar mensaje "Game Over"
  Ir a la sala [rm_gameover]
```

### Bucle
```
Repetir [10] veces
  Crear instancia [obj_moneda] en posición (Aleatorio 0-800, Aleatorio 0-600)
```

## Bloques de juego

### Movimiento
- **Mover a**: Mover a posición
- **Establecer velocidad**: Velocidad de movimiento
- **Establecer dirección**: Dirección de movimiento

### Instancias
- **Crear instancia**: Generar nuevo objeto
- **Destruir**: Eliminar objeto
- **Para todos**: Todas las instancias de un tipo

### Variables
- **Establecer variable**: Almacenar valor
- **Modificar variable**: Cambiar valor
- **Obtener variable**: Recuperar valor

### Eventos
- **Cuando tecla**: Entrada de teclado
- **Cuando colisión**: Contacto de objetos
- **Cuando temporizador**: Basado en tiempo

## Consejos

1. **Empieza pequeño**: Primero proyectos simples
2. **Prueba**: Ejecuta regularmente
3. **Organiza**: Agrupa los bloques lógicamente
4. **Comentarios**: Agrega notas

## De bloques a código

El editor Blockly también puede generar código:
1. Aprende conceptos de programación visualmente
2. Ve el código generado
3. Cambia a Python después

## Ver también

- [Crear tu primer juego](Primer_Juego_es)
- [Eventos y Acciones](Eventos_y_Acciones_es)
- [FAQ](FAQ_es)
