# Eventos y Acciones

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

[Volver al Inicio](Home_es)

Los Eventos y Acciones forman el corazón de la lógica del juego en pyGM.

## Concepto

### Eventos
Los eventos son disparadores que reaccionan a situaciones específicas:
- Inicio del juego
- Presión de teclas
- Colisión
- Temporizador

### Acciones
Las acciones son las respuestas a los eventos:
- Mover
- Crear/Destruir
- Cambiar valores
- Reproducir sonidos

## Categorías de eventos

### Eventos de creación
- **Create**: Una vez al crear la instancia
- **Destroy**: Al eliminar la instancia
- **Room Start**: Al entrar en una sala

### Eventos Step
- **Step**: Cada frame
- **Begin Step**: Antes de la verificación de colisiones
- **End Step**: Después de la verificación de colisiones

### Eventos de entrada
- **Teclado**: Presión/liberación de teclas
- **Ratón**: Clics y movimiento

### Eventos de colisión
- Contacto con otros objetos
- Contacto con paredes
- Verificaciones de área

### Eventos de dibujo
- **Draw**: Dibujo normal
- **Draw GUI**: Elementos de interfaz

### Otros eventos
- **Alarm**: Eventos basados en temporizador
- **Animation End**: Animación de sprite terminada

## Biblioteca de acciones

### Movimiento
- `move_towards_point`: Mover hacia un punto
- `set_speed`: Establecer velocidad
- `set_direction`: Establecer dirección
- `bounce`: Rebotar

### Instancias
- `create_instance`: Crear nueva instancia
- `destroy_instance`: Eliminar instancia
- `set_sprite`: Cambiar sprite

### Variables
- `set_variable`: Establecer valor
- `test_variable`: Verificación condicional

### Audio
- `play_sound`: Reproducir sonido
- `stop_sound`: Detener sonido
- `set_volume`: Cambiar volumen

### Sala
- `goto_room`: Cambiar de sala
- `restart_room`: Reiniciar sala
- `next_room`: Siguiente sala

### Dibujo
- `draw_sprite`: Dibujar sprite
- `draw_text`: Mostrar texto
- `draw_rectangle`: Dibujar rectángulo

## Condiciones y control de flujo

### Acciones condicionales
```
Si Variable == Valor
  Ejecutar acción
Si no
  Acción alternativa
```

### Bucles
- Repetir acciones
- Para todas las instancias

## Mejores prácticas

1. **Usa Step con moderación**: Solo cuando sea necesario
2. **Optimiza las colisiones**: Considera la propiedad Solid
3. **Agrupa los eventos**: Lógica relacionada junta
4. **Usa alarmas**: Para acciones temporizadas

## Ver también

- [Editor de Objetos](Editor_Objetos_es)
- [Programación Visual](Programacion_Visual_es)
- [FAQ](FAQ_es)
