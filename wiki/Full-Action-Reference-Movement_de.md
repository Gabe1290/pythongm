# Bewegung

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Abprallen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `bounce` |
| **Kategorie** | Bewegung |

Von soliden Objekten abprallen

*Parameter:* keine

### Zu Position springen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `jump_to_position` |
| **Symbol** | 📍 |
| **Kategorie** | Bewegung |

Sofort an eine Position bewegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `relative` | Ja/Nein | Nein | Zur aktuellen Position addieren, statt eine absolute zu setzen |

### Zu zufälliger Position springen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `jump_to_random` |
| **Symbol** | 🎲↪️ |
| **Kategorie** | Bewegung |

An eine zufällige Position teleportieren (optional am Gitter eingerastet)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `snap_h` | Zahl | `1` | Horizontales Gitter-Einrasten (1 = kein Einrasten) |
| `snap_v` | Zahl | `1` | Vertikales Gitter-Einrasten (1 = kein Einrasten) |

### Zur Startposition springen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `jump_to_start` |
| **Symbol** | ↩️ |
| **Kategorie** | Bewegung |

Die Instanz zurück an ihre Erstellungsposition bewegen

*Parameter:* keine

### Frei bewegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `move_free` |
| **Symbol** | 🧭 |
| **Kategorie** | Bewegung |

In eine genaue Richtung bewegen (0-360 Grad)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `direction` | Zahl | `0` | Richtung in Grad (0=rechts, 90=oben, gegen den Uhrzeigersinn) |
| `speed` | Zahl | `4.0` | Bewegungsgeschwindigkeit |

### Auf Gitter bewegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `move_grid` |
| **Symbol** | ▦ |
| **Kategorie** | Bewegung |

Um eine Gittereinheit in die angegebene Richtung bewegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `direction` | Auswahl | `right` | Bewegungsrichtung; Auswahl: `left`, `right`, `up`, `down` |
| `grid_size` | Zahl | `32` | Größe der Gittereinheit in Pixeln |

### Zu Punkt bewegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `move_towards_point` |
| **Symbol** | 🎯 |
| **Kategorie** | Bewegung |

Sich mit einer bestimmten Geschwindigkeit auf einen Punkt zu bewegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | Ziel X |
| `y` | Zahl | `0` | Ziel Y |
| `speed` | Zahl | `4.0` | Bewegungsgeschwindigkeit |

### Bis zum Kontakt bewegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `move_to_contact` |
| **Symbol** | 🎯 |
| **Kategorie** | Bewegung |

In eine Richtung bewegen, bis ein Objekt berührt wird (oder die maximale Distanz)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `direction` | Text | `direction` | Richtung in Grad (0=rechts, 90=oben, 180=links, 270=unten) oder ein Ausdruck. Standard „direction“ = die aktuelle Ausrichtung der Instanz (Kollisions-Einrasten). |
| `max_distance` | Zahl | `1000` | Maximale Bewegungsdistanz in Pixeln |
| `object` | Objekt | `all` | Beim Kontakt stoppen mit: „all“ allen Instanzen, „solid“ nur soliden Objekten oder einem bestimmten Objektnamen.; Auswahl: `all`, `solid`; optional |

### Horizontal umkehren

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `reverse_horizontal` |
| **Symbol** | ↔️ |
| **Kategorie** | Bewegung |

Horizontale Bewegungsrichtung umkehren

*Parameter:* keine

### Vertikal umkehren

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `reverse_vertical` |
| **Symbol** | ↕️ |
| **Kategorie** | Bewegung |

Vertikale Bewegungsrichtung umkehren

*Parameter:* keine

### Richtung setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_direction` |
| **Symbol** | 🧭 |
| **Kategorie** | Bewegung |

Bewegungsrichtung setzen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `direction` | Zahl | `0` | Richtung in Grad (0=rechts, 90=oben) |

### Richtung und Geschwindigkeit setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_direction_speed` |
| **Symbol** | 🧭 |
| **Kategorie** | Bewegung |

Die Richtung (in Grad) und den Geschwindigkeitsbetrag der Instanz setzen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `direction` | Zahl | `0` | Richtung in Grad (0=rechts, 90=oben) |
| `speed` | Zahl | `4.0` | Geschwindigkeit in Pixeln pro Bild |

### Reibung setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_friction` |
| **Symbol** | 🛑 |
| **Kategorie** | Bewegung |

Reibung festlegen (Abbremsung)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `friction` | Zahl | `0.1` | Reibungsbetrag (bei jedem Schritt von der Geschwindigkeit abgezogen) |

### Schwerkraft setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_gravity` |
| **Symbol** | ⬇️ |
| **Kategorie** | Bewegung |

Richtung und Stärke der Schwerkraft festlegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `direction` | Zahl | `270` | Schwerkraftrichtung in Grad (270=unten) |
| `gravity` | Zahl | `0.5` | Schwerkraftstärke (bei jedem Schritt hinzugefügt) |

### Horizontale Geschwindigkeit setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_hspeed` |
| **Symbol** | ↔️ |
| **Kategorie** | Bewegung |

Horizontale Bewegungsgeschwindigkeit setzen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `speed` | Zahl | `0` | Geschwindigkeit in Pixeln pro Bild |

### Geschwindigkeit setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_speed` |
| **Symbol** | ⚡ |
| **Kategorie** | Bewegung |

Bewegungsgeschwindigkeit setzen (Betrag)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `speed` | Zahl | `0` | Bewegungsgeschwindigkeit |

### Vertikale Geschwindigkeit setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_vspeed` |
| **Symbol** | ↕️ |
| **Kategorie** | Bewegung |

Vertikale Bewegungsgeschwindigkeit setzen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `speed` | Zahl | `0` | Geschwindigkeit in Pixeln pro Bild |

### Losbewegen (Richtung)

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `start_moving_direction` |
| **Symbol** | ➡️ |
| **Kategorie** | Bewegung |

In eine Richtung mit einer bestimmten Geschwindigkeit zu bewegen beginnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `directions` | Mehrfachauswahl | right | Bewegungsrichtung(en) — eine ankreuzen oder mehrere, um bei jedem Schritt eine zufällige zu wählen. Die mittlere Zelle ist Stopp.; Auswahl: `up-left`, `up`, `up-right`, `left`, `stop`, `right`, `down-left`, `down`, `down-right` |
| `direction_expr` | Text | — | Alternative: freier Ausdruck, in Grad ausgewertet; optional |
| `speed` | Zahl | `4.0` | Geschwindigkeit in Pixeln pro Bild |

### Bewegung stoppen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `stop_movement` |
| **Symbol** | 🛑 |
| **Kategorie** | Bewegung |

Beide Geschwindigkeiten auf null setzen

*Parameter:* keine

### Am Raumrand umbrechen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `wrap_around_room` |
| **Symbol** | 🔄 |
| **Kategorie** | Bewegung |

Auf der gegenüberliegenden Raumseite wieder erscheinen

*Parameter:* keine

---

## Weitere Kategorien

- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (2)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (20)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (4)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
