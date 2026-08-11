# Ereignis-Referenz

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Vollständige Aktionsreferenz](Full-Action-Reference_de)*

Diese Seite dokumentiert alle verfügbaren Ereignisse in PyGameMaker. Ereignisse sind Auslöser, die Aktionen ausführen, wenn bestimmte Bedingungen in Ihrem Spiel auftreten.

## Ereigniskategorien

- [Objekt-Ereignisse](Event-Reference-Object_de) - Create, Step, Destroy
- [Eingabe-Ereignisse](Event-Reference-Input_de) - Tastatur, Maus
- [Kollisions-Ereignisse](Event-Reference-Collision_de) - Objektkollisionen
- [Zeit-Ereignisse](Event-Reference-Timing_de) - Alarme, Step-Varianten
- [Zeichen-Ereignisse](Event-Reference-Drawing_de) - Benutzerdefiniertes Rendern
- [Raum-Ereignisse](Event-Reference-Room_de) - Raumübergänge
- [Spiel-Ereignisse](Event-Reference-Game_de) - Spielstart/-ende
- [Andere Ereignisse](Event-Reference-Other_de) - Grenzen, Leben, Gesundheit

---

## Ereignis-Ausführungsreihenfolge

Das Verständnis, wann Ereignisse auslösen, hilft dabei, vorhersehbares Spielverhalten zu erstellen
(bestätigt gegen die Hauptschleife in `runtime/game_runner.py`):

1. **Begin Step** — Anfang des Frames
2. **Alarm** — Alle ausgelösten Alarme zählen herunter und lösen aus
3. **Step** (und **Keyboard (gehalten)**) — Haupt-Spiellogik, danach kontinuierliche
   Tastenprüfungen für dieselbe Instanz
4. **Keyboard Press/Release, Mouse** — Für diesen Frame angesammelte Eingabeereignisse
   werden verarbeitet (das geschieht *nach* Step, nicht davor — Code im Step-Ereignis
   reagiert auf Tasten, die zu *Beginn* des Frames bereits gedrückt waren, nicht auf
   solche, die während des Frames gedrückt wurden)
5. **Bewegung, dann Kollision** — Physik (Schwerkraft/Reibung/hspeed/vspeed) wird
   angewendet, dann werden Kollisionen erkannt und ihre Ereignisse ausgelöst
6. **End Step** (und **Destroy**) — Nach den Kollisionen
7. **Draw** — Renderphase

---

## Ereignisse nach Preset

Bestätigt gegen `events.event_types.get_available_events()`, gespeist mit jedem
echten Preset aus `config/blockly_config.py` — siehe den
[Preset-Leitfaden](Preset-Guide_de) für das, was ein „Preset" tatsächlich
einschränkt (sowohl den Blockly-Picker als auch das strukturierte
Ereignisse/Aktionen-Panel) und wie das Preset eines Projekts festgelegt wird.

| Preset | Enthaltene Ereignisse |
|--------|----------------------|
| **Anfänger** (19 Ereignisse) | Create, Step, Keyboard (gehalten), Keyboard \<Keine Taste\>, Collision, Begin Step, End Step, Alarm, Draw, Draw GUI, Room Start, Room End, Game Start, Game End, Outside Room, Intersect Boundary, No More Lives, No More Health, Animation End |
| **Fortgeschritten** (21 Ereignisse) | + Destroy, Keyboard Press |
| **Voll** (nur Entwicklungsedition, 23 Ereignisse) | + Keyboard Release, Mouse |

---

## Siehe Auch

- [Vollständige Aktionsreferenz](Full-Action-Reference_de) - Vollständige Aktionsliste
- [Anfänger-Preset](Beginner-Preset_de) - Wesentliche Ereignisse für Anfänger
- [Fortgeschrittenen-Preset](Intermediate-Preset_de) - Zusätzliche Ereignisse
- [Ereignisse und Aktionen](Events_und_Aktionen_de) - Überblick über Kernkonzepte
