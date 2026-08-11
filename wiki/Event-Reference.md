# Event Reference

*[Home](Home) | [Preset Guide](Preset-Guide) | [Full Action Reference](Full-Action-Reference)*

This page documents all available events in PyGameMaker. Events are triggers that execute actions when specific conditions occur in your game.

## Event Categories

- [Object Events](Event-Reference-Object) - Create, Step, Destroy
- [Input Events](Event-Reference-Input) - Keyboard, Mouse
- [Collision Events](Event-Reference-Collision) - Object collisions
- [Timing Events](Event-Reference-Timing) - Alarms, Step variants
- [Drawing Events](Event-Reference-Drawing) - Custom rendering
- [Room Events](Event-Reference-Room) - Room transitions
- [Game Events](Event-Reference-Game) - Game start/end
- [Other Events](Event-Reference-Other) - Boundaries, Lives, Health

---

## Event Execution Order

Understanding when events fire helps create predictable game behavior
(confirmed against the main loop in `runtime/game_runner.py`):

1. **Begin Step** - Start of frame
2. **Alarm** - Any triggered alarms count down and fire
3. **Step** (and **Keyboard (held)**) - Main game logic, then continuous
   key-held checks for the same instance
4. **Keyboard Press/Release, Mouse** - Queued input events for the frame are
   dispatched (this happens *after* Step, not before it — code in Step
   reacts to keys that were already held at the *start* of the frame, not
   ones pressed during it)
5. **Movement, then Collision** - Physics (gravity/friction/hspeed/vspeed)
   is applied, then collisions are detected and their events fire
6. **End Step** (and **Destroy**) - After collisions
7. **Draw** - Rendering phase

---

## Events by Preset

Confirmed against `events.event_types.get_available_events()` fed each real
preset from `config/blockly_config.py` — see [Preset Guide](Preset-Guide)
for what a "preset" actually restricts (both the Blockly picker and the
structured Events/Actions panel) and how a project's preset is set.

| Preset | Events included |
|--------|-----------------|
| **Beginner** (19 events) | Create, Step, Keyboard (held), Keyboard \<No Key\>, Collision, Begin Step, End Step, Alarm, Draw, Draw GUI, Room Start, Room End, Game Start, Game End, Outside Room, Intersect Boundary, No More Lives, No More Health, Animation End |
| **Intermediate** (21 events) | + Destroy, Keyboard Press |
| **Full** (Development edition only, 23 events) | + Keyboard Release, Mouse |

---

## See Also

- [Full Action Reference](Full-Action-Reference) - Complete action list
- [Beginner Preset](Beginner-Preset) - Essential events for beginners
- [Intermediate Preset](Intermediate-Preset) - Additional events
- [Events and Actions](Events-and-Actions) - Core concepts overview
