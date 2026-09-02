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

### Hintergrund setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_background` |
| **Symbol** | 🖼️ |
| **Kategorie** | Raum |

Das Hintergrundbild des aktuellen Raums festlegen, mit Kachelungs- und Scroll-Optionen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `background` | Text | — | Name der Hintergrund- oder Sprite-Ressource |
| `visible` | Ja/Nein | Ja | Hintergrund anzeigen; optional |
| `foreground` | Ja/Nein | Nein | Vor den Instanzen zeichnen statt dahinter; optional |
| `tiled_h` | Ja/Nein | Nein | Hintergrund über die Breite des Raums wiederholen; optional |
| `tiled_v` | Ja/Nein | Nein | Hintergrund über die Höhe des Raums wiederholen; optional |
| `hspeed` | Zahl | `0` | Horizontale Auto-Scroll-Geschwindigkeit in Pixel/Bild; optional |
| `vspeed` | Zahl | `0` | Vertikale Auto-Scroll-Geschwindigkeit in Pixel/Bild; optional |

### Hintergrundfarbe setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_background_color` |
| **Symbol** | 🎨 |
| **Kategorie** | Raum |

Die Hintergrundfarbe des aktuellen Raums ändern

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `color` | Farbe | `#87CEEB` | Hintergrundfarbe |
| `show_color` | Ja/Nein | Ja | Ob die Hintergrundfarbe sichtbar ist (aus füllt stattdessen mit Schwarz); optional |

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

### Raum-Persistenz setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_room_persistent` |
| **Symbol** | 💾 |
| **Kategorie** | Raum |

Ob der aktuelle Raum seinen aktiven Zustand (Instanzpositionen, zerstörte Instanzen usw.) behält, wenn der Spieler ihn verlässt und später zurückkehrt, anstatt ihn bei jedem erneuten Betreten aus seinem ursprünglichen Layout neu aufzubauen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `persistent` | Ja/Nein | Ja | Zustand dieses Raums bei erneutem Betreten beibehalten |

### Raumgeschwindigkeit setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_room_speed` |
| **Symbol** | ⏱️ |
| **Kategorie** | Raum |

Die Bildrate des Spiels ändern (Bilder pro Sekunde)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `speed` | Zahl | `30` | Ziel-Bilder pro Sekunde (1-240) |

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (8)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (25)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (16)
- [Particles](Full-Action-Reference-Particles_de) (8)
- [Réseau](Full-Action-Reference-Network-Actions_de) (15)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
