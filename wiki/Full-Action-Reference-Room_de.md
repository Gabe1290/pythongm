# Raum

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Raum prüfen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `check_room` |
| **Symbol** | ❓🚪 |
| **Kategorie** | Raum |

Bedingung: wahr, wenn der aktuelle Raum übereinstimmt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `room` | Raum | — | Zu vergleichender Raum |
| `not_flag` | Ja/Nein | Nein | Das Ergebnis umkehren; optional |

### Spiel beenden

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `game_end` |
| **Symbol** | 🛑🎮 |
| **Kategorie** | Raum |

Das Spiel beenden

*Parameter:* keine

### Zu Raum gehen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `goto_room` |
| **Symbol** | 🚪 |
| **Kategorie** | Raum |

Zu einem bestimmten Raum wechseln

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `room` | Raum | — | Name des Zielraums |
| `transition` | Auswahl | `none` | Übergangseffekt (derzeit akzeptiert, aber nicht dargestellt); Auswahl: `none`; optional |

### Wenn nächster Raum existiert

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `if_next_room_exists` |
| **Symbol** | ❓➡️ |
| **Kategorie** | Raum |

Prüfen, ob es nach dem aktuellen einen nächsten Raum gibt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `then_actions` | Aktionsliste | — | Aktionen, wenn der nächste Raum existiert |
| `else_actions` | Aktionsliste | — | Aktionen, wenn der nächste Raum nicht existiert |

### Wenn vorheriger Raum existiert

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `if_previous_room_exists` |
| **Symbol** | ❓⬅️ |
| **Kategorie** | Raum |

Prüfen, ob es vor dem aktuellen einen vorherigen Raum gibt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `then_actions` | Aktionsliste | — | Aktionen, wenn der vorherige Raum existiert |
| `else_actions` | Aktionsliste | — | Aktionen, wenn der vorherige Raum nicht existiert |

### Nächster Raum

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `next_room` |
| **Symbol** | ➡️ |
| **Kategorie** | Raum |

Zum nächsten Raum gehen

*Parameter:* keine

### Vorheriger Raum

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `previous_room` |
| **Symbol** | ⬅️ |
| **Kategorie** | Raum |

Zum vorherigen Raum gehen

*Parameter:* keine

### Raum neu starten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `restart_room` |
| **Symbol** | 🔄 |
| **Kategorie** | Raum |

Aktuellen Raum neu starten

*Parameter:* keine

### Set Background

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_background` |
| **Symbol** | 🖼️ |
| **Kategorie** | Raum |

Set the current room's background image, with tiling and scrolling options

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `background` | Text | — | Background or sprite asset name |
| `visible` | Ja/Nein | Ja | Show the background; optional |
| `foreground` | Ja/Nein | Nein | Draw in front of instances instead of behind them; optional |
| `tiled_h` | Ja/Nein | Nein | Repeat the background across the width of the room; optional |
| `tiled_v` | Ja/Nein | Nein | Repeat the background across the height of the room; optional |
| `hspeed` | Zahl | `0` | Horizontal auto-scroll speed in pixels/frame; optional |
| `vspeed` | Zahl | `0` | Vertical auto-scroll speed in pixels/frame; optional |

### Set Background Color

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_background_color` |
| **Symbol** | 🎨 |
| **Kategorie** | Raum |

Change the current room's background color

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `color` | Farbe | `#87CEEB` | Background color |
| `show_color` | Ja/Nein | Ja | Whether the background color is visible (off fills black instead); optional |

### Raumtitel festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_room_caption` |
| **Symbol** | 🏷️ |
| **Kategorie** | Raum |

Die Titelleiste des Spielfensters festlegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `caption` | Text | — | Text des Fenstertitels |

### Set Room Persistent

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_room_persistent` |
| **Symbol** | 💾 |
| **Kategorie** | Raum |

Whether the current room keeps its live state (instance positions, destroyed instances, etc.) when the player leaves and later returns to it, instead of rebuilding fresh from its authored layout every revisit

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `persistent` | Ja/Nein | Ja | Keep this room's state across a revisit |

### Set Room Speed

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_room_speed` |
| **Symbol** | ⏱️ |
| **Kategorie** | Raum |

Change the game's frame rate (frames per second)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `speed` | Zahl | `30` | Target frames per second (1-240) |

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (2)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (20)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (4)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
