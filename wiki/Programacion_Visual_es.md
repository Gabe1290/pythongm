# Programacion Visual

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

[Volver al Inicio](Home_es)

pyGM ofrece un sistema de programacion visual para el desarrollo de juegos facil sin codigo.

## Resumen

Con la programacion visual puedes:
- Crear logica de juego con arrastrar y soltar
- Conectar bloques para comportamientos complejos
- Desarrollar sin conocimientos de programacion

## El Editor Blockly

### Interfaz
1. **Paleta de bloques**: Bloques disponibles por categoria
2. **Area de trabajo**: Aqui conectas los bloques
3. **Barra de herramientas**: Guardar, Cargar, Eliminar

### Categorias de bloques
- **Logica**: Si/Entonces, comparaciones, valores booleanos
- **Bucles**: Repeticiones
- **Matematicas**: Calculos
- **Texto**: Operaciones de texto
- **Variables**: Almacenar valores
- **Funciones**: Bloques reutilizables
- **Juego**: Acciones especificas de pyGM

## Usar bloques

### Agregar un bloque
1. Haz clic en una categoria
2. Arrastra un bloque al area de trabajo
3. Conectalo con otros bloques

### Conectar bloques
- Los bloques encajan automaticamente
- Presta atencion a las formas coincidentes
- Es posible anidar bloques

### Configurar un bloque
- Completa los campos de entrada
- Elige opciones del menu desplegable
- Inserta subbloques

## Ejemplos

### Movimiento simple
```
Cuando [flecha derecha] presionada
  Establecer x a (x + 5)
```

### Logica condicional
```
Si <Vidas <= 0> entonces
  Mostrar mensaje "Game Over"
  Ir a la sala [rm_gameover]
```

### Bucle
```
Repetir [10] veces
  Crear instancia [obj_moneda] en posicion (Aleatorio 0-800, Aleatorio 0-600)
```

## Bloques de juego

### Movimiento
- **Mover a**: Mover a posicion
- **Establecer velocidad**: Velocidad de movimiento
- **Establecer direccion**: Direccion de movimiento

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
- **Cuando colision**: Contacto de objetos
- **Cuando temporizador**: Basado en tiempo

## Consejos

1. **Empieza pequeno**: Primero proyectos simples
2. **Prueba**: Ejecuta regularmente
3. **Organiza**: Agrupa los bloques logicamente
4. **Comentarios**: Agrega notas

## De bloques a codigo

El editor Blockly tambien puede generar codigo:
1. Aprende conceptos de programacion visualmente
2. Ve el codigo generado
3. Cambia a Python despues

## Ver tambien

- [Crear tu primer juego](Primer_Juego_es)
- [Eventos y Acciones](Eventos_y_Acciones_es)
- [FAQ](FAQ_es)
