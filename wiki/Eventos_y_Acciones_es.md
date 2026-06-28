# Eventos y Acciones

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

[Volver al Inicio](Home_es)

Los Eventos y Acciones forman el corazon de la logica del juego en pyGM.

## Concepto

### Eventos
Los eventos son disparadores que reaccionan a situaciones especificas:
- Inicio del juego
- Presion de teclas
- Colision
- Temporizador

### Acciones
Las acciones son las respuestas a los eventos:
- Mover
- Crear/Destruir
- Cambiar valores
- Reproducir sonidos

## Categorias de eventos

### Eventos de creacion
- **Create**: Una vez al crear la instancia
- **Destroy**: Al eliminar la instancia
- **Room Start**: Al entrar en una sala

### Eventos Step
- **Step**: Cada frame
- **Begin Step**: Antes de la verificacion de colisiones
- **End Step**: Despues de la verificacion de colisiones

### Eventos de entrada
- **Teclado**: Presion/liberacion de teclas
- **Raton**: Clics y movimiento
- **Gamepad**: Entrada del controlador

### Eventos de colision
- Contacto con otros objetos
- Contacto con paredes
- Verificaciones de area

### Eventos de dibujo
- **Draw**: Dibujo normal
- **Draw GUI**: Elementos de interfaz
- **Draw Begin/End**: Antes/Despues del dibujo

### Otros eventos
- **Alarm**: Eventos basados en temporizador
- **Animation End**: Animacion de sprite terminada
- **User Events**: Eventos personalizados

## Biblioteca de acciones

### Movimiento
- `move_towards`: Mover hacia un punto
- `set_speed`: Establecer velocidad
- `set_direction`: Establecer direccion
- `bounce`: Rebotar

### Instancias
- `instance_create`: Crear nueva instancia
- `instance_destroy`: Eliminar instancia
- `change_sprite`: Cambiar sprite

### Variables
- `set_variable`: Establecer valor
- `add_to_variable`: Agregar valor
- `if_variable`: Verificacion condicional

### Audio
- `play_sound`: Reproducir sonido
- `stop_sound`: Detener sonido
- `set_volume`: Cambiar volumen

### Sala
- `goto_room`: Cambiar de sala
- `restart_room`: Reiniciar sala
- `goto_next_room`: Siguiente sala

### Dibujo
- `draw_sprite`: Dibujar sprite
- `draw_text`: Mostrar texto
- `draw_rectangle`: Dibujar rectangulo

## Condiciones y control de flujo

### Acciones condicionales
```
Si Variable == Valor
  Ejecutar accion
Si no
  Accion alternativa
```

### Bucles
- Repetir acciones
- Para todas las instancias

## Mejores practicas

1. **Usa Step con moderacion**: Solo cuando sea necesario
2. **Optimiza las colisiones**: Considera la propiedad Solid
3. **Agrupa los eventos**: Logica relacionada junta
4. **Usa alarmas**: Para acciones temporizadas

## Ver tambien

- [Editor de Objetos](Editor_Objetos_es)
- [Programacion Visual](Programacion_Visual_es)
- [FAQ](FAQ_es)
