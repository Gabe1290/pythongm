# Editor de Objetos

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

[Volver al Inicio](Home_es)

El Editor de Objetos es la herramienta central para definir el comportamiento de los elementos del juego.

## Resumen

Los objetos son los bloques de construcción de tu juego. Definen:
- Apariencia (Sprite)
- Comportamiento (Eventos y Acciones)
- Propiedades físicas
- Interacciones

## Interfaz del Editor

### Áreas principales
1. **Lista de objetos**: Todos los objetos en el proyecto
2. **Panel de propiedades**: Configuraciones básicas
3. **Lista de eventos**: Eventos definidos
4. **Editor de acciones**: Acciones para eventos

## Propiedades del objeto

### Generales
- **Nombre**: Identificador único (ej. obj_jugador)
- **Sprite**: Gráfico asignado
- **Visible**: Si el objeto se renderiza
- **Persistente**: Sobrevive cambios de sala

### Física
- **Sólido**: Colisiona con otros objetos
- **Profundidad**: Orden de dibujo
- **Objeto padre**: Herencia de propiedades

## Trabajar con eventos

### Agregar un evento
1. Haz clic en "Agregar Evento"
2. Selecciona el tipo de evento
3. Agrega acciones

### Tipos de eventos
- **Create**: Al crear la instancia
- **Step**: Cada frame
- **Draw**: Para dibujar
- **Teclado**: Entrada de teclado
- **Ratón**: Interacciones con el ratón
- **Colisión**: Al tocar otros objetos

## Usar acciones

### Agregar acciones
1. Selecciona un evento
2. Arrastra acciones desde la biblioteca
3. Configura los parámetros

### Acciones comunes
- Mover en una dirección
- Establecer variable
- Crear/destruir instancia
- Reproducir sonido
- Cambiar de sala

## Mejores prácticas

1. **Nombres claros**: Usa prefijos como "obj_"
2. **Modularidad**: Objetos pequeños y reutilizables
3. **Usa la herencia**: Objetos padre para comportamiento común
4. **Documentación**: Comentarios en eventos complejos

## Ver también

- [Eventos y Acciones](Eventos_y_Acciones_es)
- [Programación Visual](Programacion_Visual_es)
- [Editor de Salas](Editor_Salas_es)
