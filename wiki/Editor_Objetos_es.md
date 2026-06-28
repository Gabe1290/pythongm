# Editor de Objetos

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

[Volver al Inicio](Home_es)

El Editor de Objetos es la herramienta central para definir el comportamiento de los elementos del juego.

## Resumen

Los objetos son los bloques de construccion de tu juego. Definen:
- Apariencia (Sprite)
- Comportamiento (Eventos y Acciones)
- Propiedades fisicas
- Interacciones

## Interfaz del Editor

### Areas principales
1. **Lista de objetos**: Todos los objetos en el proyecto
2. **Panel de propiedades**: Configuraciones basicas
3. **Lista de eventos**: Eventos definidos
4. **Editor de acciones**: Acciones para eventos

## Propiedades del objeto

### Generales
- **Nombre**: Identificador unico (ej. obj_jugador)
- **Sprite**: Grafico asignado
- **Visible**: Si el objeto se renderiza
- **Persistente**: Sobrevive cambios de sala

### Fisica
- **Solido**: Colisiona con otros objetos
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
- **Raton**: Interacciones con el raton
- **Colision**: Al tocar otros objetos

## Usar acciones

### Agregar acciones
1. Selecciona un evento
2. Arrastra acciones desde la biblioteca
3. Configura los parametros

### Acciones comunes
- Mover en una direccion
- Establecer variable
- Crear/destruir instancia
- Reproducir sonido
- Cambiar de sala

## Mejores practicas

1. **Nombres claros**: Usa prefijos como "obj_"
2. **Modularidad**: Objetos pequenos y reutilizables
3. **Usa la herencia**: Objetos padre para comportamiento comun
4. **Documentacion**: Comentarios en eventos complejos

## Ver tambien

- [Eventos y Acciones](Eventos_y_Acciones_es)
- [Programacion Visual](Programacion_Visual_es)
- [Editor de Salas](Editor_Salas_es)
