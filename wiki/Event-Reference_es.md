# Referencia de Eventos

*[Inicio](Home_es) | [Guía de Preajustes](Preset-Guide_es) | [Referencia completa de acciones](Full-Action-Reference_es)*

Esta página documenta todos los eventos disponibles en PyGameMaker. Los eventos son disparadores que ejecutan acciones cuando ocurren condiciones específicas en tu juego.

## Categorías de Eventos

- [Eventos de Objeto](Event-Reference-Object_es) - Create, Step, Destroy
- [Eventos de Entrada](Event-Reference-Input_es) - Teclado, Ratón
- [Eventos de Colisión](Event-Reference-Collision_es) - Colisiones de objetos
- [Eventos de Tiempo](Event-Reference-Timing_es) - Alarmas, Variantes de Step
- [Eventos de Dibujo](Event-Reference-Drawing_es) - Renderizado personalizado
- [Eventos de Sala](Event-Reference-Room_es) - Transiciones de sala
- [Eventos de Juego](Event-Reference-Game_es) - Inicio/Fin del juego
- [Otros Eventos](Event-Reference-Other_es) - Límites, Vidas, Salud

---

## Orden de Ejecución de Eventos

Entender cuándo se disparan los eventos ayuda a crear un comportamiento
de juego predecible (verificado contra el bucle principal en
`runtime/game_runner.py`):

1. **Begin Step** — Inicio del fotograma
2. **Alarm** — Todas las alarmas activadas cuentan regresivamente y se disparan
3. **Step** (y **Keyboard (mantenida)**) — Lógica principal del juego,
   luego comprobaciones continuas de teclas mantenidas para la misma
   instancia
4. **Keyboard Press/Release, Mouse** — Los eventos de entrada
   acumulados para este fotograma se procesan (esto ocurre *después*
   de Step, no antes — el código en Step reacciona a las teclas que ya
   estaban presionadas al *inicio* del fotograma, no a las presionadas
   durante el fotograma)
5. **Movimiento, luego Colisión** — Se aplica la física (gravedad/
   fricción/hspeed/vspeed), luego se detectan las colisiones y se
   disparan sus eventos
6. **End Step** (y **Destroy**) — Después de las colisiones
7. **Draw** — Fase de renderizado

---

## Eventos por Preset

Verificado contra `events.event_types.get_available_events()`
alimentado con cada preset real de `config/blockly_config.py` — consulta
la [Guía de Preajustes](Preset-Guide_es) para lo que un "preset"
realmente restringe (tanto el selector de Blockly como el panel
estructurado Events/Actions) y cómo se establece el preset de un
proyecto.

| Preset | Eventos Incluidos |
|--------|-------------------|
| **Principiante** (19 eventos) | Create, Step, Keyboard (mantenida), Keyboard \<Sin Tecla\>, Collision, Begin Step, End Step, Alarm, Draw, Draw GUI, Room Start, Room End, Game Start, Game End, Outside Room, Intersect Boundary, No More Lives, No More Health, Animation End |
| **Intermedio** (21 eventos) | + Destroy, Keyboard Press |
| **Completo** (solo Edición Desarrollo, 23 eventos) | + Keyboard Release, Mouse |

---

## Ver También

- [Referencia Completa de Acciones](Full-Action-Reference_es) - Lista completa de acciones
- [Preset Principiante](Beginner-Preset_es) - Eventos esenciales para principiantes
- [Preset Intermedio](Intermediate-Preset_es) - Eventos adicionales
- [Eventos y Acciones](Eventos_y_Acciones_es) - Visión general de conceptos básicos
