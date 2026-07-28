# Vollständige Aktionsreferenz

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

Diese Seite listet alle **109** in PyGameMaker verfügbaren Aktionen auf, genau so, wie sie im Aktionsauswahldialog der IDE erscheinen (einschließlich des Audio-Plugins und der 3D-Ansicht-Erweiterung). Aktionen sind Befehle, die ausgeführt werden, wenn ein Ereignis ausgelöst wird.

## Kategorien

- [Bewegung](#movement) (20)
- [Instanz](#instance) (12)
- [Punkte](#score) (11)
- [Raum](#room) (9)
- [Zeitsteuerung](#timing) (2)
- [Audio](#audio) (6)
- [Spiel](#game) (20)
- [Steuerung](#control) (19)
- [Gitter](#grid) (4)
- [Ansichten](#views) (2)
- [3D-Ansicht](#3d-view) (4)

---

<a id="movement"></a>
## Bewegung

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

<a id="instance"></a>
## Instanz

### Instanz ändern

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `change_instance` |
| **Symbol** | 🔄 |
| **Kategorie** | Instanz |
| **Gilt für** | self / other / object |

In einen anderen Objekttyp umwandeln

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `object` | Objekt | — | Neuer Objekttyp |
| `perform_events` | Ja/Nein | Ja | Zerstören-/Erstellen-Ereignisse ausführen |

### Instanz erstellen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `create_instance` |
| **Symbol** | ✨ |
| **Kategorie** | Instanz |

Eine neue Instanz erstellen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `object` | Objekt | — | Zu erstellendes Objekt |
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `relative` | Ja/Nein | Nein | Position relativ zur aktuellen Instanz |

### Bewegte Instanz erstellen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `create_moving_instance` |
| **Symbol** | ✨➡️ |
| **Kategorie** | Instanz |

Eine Instanz erstellen und in eine Richtung in Bewegung setzen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `object` | Objekt | — | Zu erstellendes Objekt |
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `speed` | Zahl | `0` | Anfänglicher Geschwindigkeitsbetrag |
| `direction` | Zahl | `0` | Anfängliche Richtung in Grad |

### Zufällige Instanz erstellen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `create_random_instance` |
| **Symbol** | 🎲 |
| **Kategorie** | Instanz |

Einen von mehreren Objekttypen zufällig ausgewählt erstellen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `object1` | Objekt | — | Erstes Kandidatenobjekt; optional |
| `object2` | Objekt | — | Zweites Kandidatenobjekt; optional |
| `object3` | Objekt | — | Drittes Kandidatenobjekt; optional |
| `object4` | Objekt | — | Viertes Kandidatenobjekt; optional |

### Instanz zerstören

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `destroy_instance` |
| **Symbol** | 💥 |
| **Kategorie** | Instanz |
| **Gilt für** | self / other / object |

Eine Instanz zerstören

*Parameter:* keine

### An Position zerstören

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `destroy_at_position` |
| **Symbol** | 💣 |
| **Kategorie** | Instanz |

Instanzen im Umkreis von (x, y) zerstören

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `object` | Objekt | `all` | Welcher Objekttyp zerstört wird. „all“ zerstört jede Instanz in Reichweite; „solid“ nur solide (z. B. Wände); „non-solid“ alles außer soliden.; Auswahl: `all`, `solid`, `non-solid` |
| `x` | Text | `self.x` | X-Position (Ausdruck erlaubt, z. B. self.x) |
| `y` | Text | `self.y` | Y-Position (Ausdruck erlaubt, z. B. self.y) |
| `relative` | Ja/Nein | Nein | X/Y als Versatz zur Position dieser Instanz statt als absolute Koordinaten behandeln; optional |
| `radius` | Zahl | `32` | Pixelradius um (x, y). Standard 32 = ~eine Gitterzelle. |

### Bildindex setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_image_index` |
| **Symbol** | 🖼️ |
| **Kategorie** | Instanz |

Das aktuelle Animationsbild des Sprites der Instanz setzen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `frame` | Zahl | `0` | Bildindex |

### Bildgeschwindigkeit setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_image_speed` |
| **Symbol** | ⏩ |
| **Kategorie** | Instanz |

Die Wiedergabegeschwindigkeit der Animation des Sprites der Instanz setzen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `speed` | Zahl | `1.0` | Pro Schritt weitergeschaltete Bilder (0 = pausiert) |

### Sprite setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_sprite` |
| **Symbol** | 🖼️ |
| **Kategorie** | Instanz |

Das Sprite und/oder das Animationsbild/-tempo einer Instanz ändern

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `sprite` | Sprite | `<self>` | Zu verwendendes Sprite (oder „<self>“, um das aktuelle beizubehalten) |
| `subimage` | Zahl | `-1` | Zu setzender Bildindex; -1 lässt ihn unverändert |
| `speed` | Zahl | `-1` | Animationsgeschwindigkeit; -1 lässt sie unverändert |

### Animation starten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `start_animation` |
| **Symbol** | ▶️ |
| **Kategorie** | Instanz |

Die Sprite-Animation der Instanz fortsetzen (image_speed = 1)

*Parameter:* keine

### Animation stoppen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `stop_animation` |
| **Symbol** | ⏸️ |
| **Kategorie** | Instanz |

Die Sprite-Animation der Instanz anhalten (image_speed = 0)

*Parameter:* keine

### Instanzanzahl testen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `test_instance_count` |
| **Symbol** | ❓🔢 |
| **Kategorie** | Instanz |

Bedingung: die Anzahl der Instanzen eines Objekts vergleichen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `object` | Objekt | — | Zu zählendes Objekt |
| `number` | Zahl | `0` | Vergleichswert |
| `operation` | Auswahl | `equal` | Vergleichsoperator; Auswahl: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="score"></a>
## Punkte

### Bestenliste löschen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `clear_highscore` |
| **Symbol** | 🗑️🏆 |
| **Kategorie** | Punkte |

Alle Einträge der Bestenliste löschen

*Parameter:* keine

### Gesundheitsbalken zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_health_bar` |
| **Symbol** | 🩺 |
| **Kategorie** | Punkte |

Die aktuelle Gesundheit als zweifarbigen Balken zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x1` | Zahl | `0` | Links X |
| `y1` | Zahl | `0` | Oben Y |
| `x2` | Zahl | `100` | Rechts X |
| `y2` | Zahl | `20` | Unten Y |
| `back_color` | Farbe | `#FF0000` | Hintergrundfarbe (leer) |
| `bar_color` | Farbe | `#00FF00` | Füllfarbe (Gesundheit) |

### Leben zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_lives` |
| **Symbol** | 🖍️❤️ |
| **Kategorie** | Punkte |

Die aktuelle Lebenszahl als wiederholte Sprite-Bilder zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `sprite` | Sprite | — | Sprite, das einmal pro verbleibendem Leben gezeichnet wird; optional |
| `scale` | Zahl | `1.0` | Gleichmäßiger Skalierungsfaktor für das Lebenssymbol (1.0 = native Größe); optional |
| `relative` | Ja/Nein | Nein | Relativ zur Position dieser Instanz statt zu absoluten Bildschirmkoordinaten zeichnen; optional |

### Punkte zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_score` |
| **Symbol** | 🖍️🏆 |
| **Kategorie** | Punkte |

Die aktuelle Punktzahl auf dem Bildschirm zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `caption` | Text | `Score: ` | Text, der vor dem Punktwert angezeigt wird; optional |
| `relative` | Ja/Nein | Nein | Relativ zur Position dieser Instanz statt zu absoluten Bildschirmkoordinaten zeichnen; optional |

### Gesundheit setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_health` |
| **Symbol** | 💚 |
| **Kategorie** | Punkte |

Die Gesundheit setzen oder mit Relativ dazu addieren

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `value` | Zahl | `100` | Gesundheitswert (0-100) |
| `relative` | Ja/Nein | Nein | Zur aktuellen Gesundheit addieren, statt sie zu ersetzen |

### Leben setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_lives` |
| **Symbol** | ❤️ |
| **Kategorie** | Punkte |

Die Leben setzen oder mit Relativ dazu addieren

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `value` | Zahl | `3` | Anzahl der Leben |
| `relative` | Ja/Nein | Nein | Zu den aktuellen Leben addieren, statt sie zu ersetzen |

### Punkte setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_score` |
| **Symbol** | 🏆 |
| **Kategorie** | Punkte |

Die Punktzahl setzen oder mit Relativ dazu addieren

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `value` | Zahl | `0` | Zu setzender Punktwert |
| `relative` | Ja/Nein | Nein | Zur aktuellen Punktzahl addieren, statt sie zu ersetzen |

### Bestenliste anzeigen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `show_highscore` |
| **Symbol** | 🏆 |
| **Kategorie** | Punkte |

Den Bestenlisten-Dialog anzeigen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `background` | Farbe | `#FFFFDD` | Hintergrundfarbe des Dialogs; optional |
| `new_color` | Farbe | `#FF0000` | Farbe für den neuen (qualifizierten) Eintrag; optional |
| `other_color` | Farbe | `#000000` | Farbe für die anderen Einträge; optional |
| `allow_new_entry` | Ja/Nein | Ja | Nach dem Namen fragen, wenn die aktuelle Punktzahl sich qualifiziert |

### Gesundheit testen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `test_health` |
| **Symbol** | ❓💚 |
| **Kategorie** | Punkte |

Bedingung: die aktuelle Gesundheit mit einem Wert vergleichen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `operation` | Auswahl | `equal` | Vergleichsoperator; Auswahl: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |
| `value` | Zahl | `0` | Vergleichswert |

### Leben testen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `test_lives` |
| **Symbol** | ❓❤️ |
| **Kategorie** | Punkte |

Bedingung: die Lebenszahl mit einem Wert vergleichen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `value` | Zahl | `0` | Vergleichswert |
| `operation` | Auswahl | `equal` | Vergleichsoperator; Auswahl: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

### Punkte testen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `test_score` |
| **Symbol** | ❓🏆 |
| **Kategorie** | Punkte |

Bedingung: die Punktzahl mit einem Wert vergleichen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `value` | Zahl | `0` | Vergleichswert |
| `operation` | Auswahl | `equal` | Vergleichsoperator; Auswahl: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="room"></a>
## Raum

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

---

<a id="timing"></a>
## Zeitsteuerung

### Wecker stellen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_alarm` |
| **Symbol** | ⏰ |
| **Kategorie** | Zeitsteuerung |

Einen Wecker stellen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `alarm_number` | Zahl | `0` | Welcher Wecker (0-11) |
| `steps` | Zahl | `30` | Anzahl der Schritte bis zur Auslösung des Weckers (30 = 0,5 s bei 60 FPS) |

### Warten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `sleep` |
| **Symbol** | 💤 |
| **Kategorie** | Zeitsteuerung |

Das Spiel für eine Anzahl von Millisekunden anhalten und dann fortfahren. Klänge werden während der Pause weiter abgespielt (z. B. um einen Klang vor dem Raumwechsel zu Ende spielen zu lassen). Hinweis: Rendering und Eingabe sind während des Wartens eingefroren, halten Sie die Dauer daher kurz

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `milliseconds` | Zahl | `1000` | Dauer der Pause in Millisekunden (1000 = 1 Sekunde) |

---

<a id="audio"></a>
## Audio

### Klangwiedergabe prüfen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `check_sound` |
| **Symbol** | ❓🔊 |
| **Kategorie** | Audio |

Bedingung: wahr, wenn der angegebene Klang gerade abgespielt wird

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `sound` | Sound | — | Zu prüfender Klang |
| `not_flag` | Ja/Nein | Nein | Das Ergebnis umkehren; optional |

### Musik abspielen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `play_music` |
| **Symbol** | 🎵 |
| **Kategorie** | Audio |

Hintergrundmusik abspielen (in Schleife)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `music` | Sound | — | Abzuspielende Musikdatei |
| `loop` | Ja/Nein | Ja | Die Musik in Schleife abspielen |
| `volume` | Zahl | `0.7` | Lautstärke (0.0 bis 1.0) |

### Klang abspielen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `play_sound` |
| **Symbol** | 🔊 |
| **Kategorie** | Audio |

Einen Soundeffekt einmal abspielen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `sound` | Sound | — | Abzuspielender Klang |
| `volume` | Zahl | `1.0` | Lautstärke (0.0 bis 1.0) |

### Lautstärke setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_volume` |
| **Symbol** | 🔉 |
| **Kategorie** | Audio |

Globale Klang-/Musiklautstärke festlegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `volume` | Zahl | `1.0` | Lautstärke (0.0 bis 1.0) |

### Musik stoppen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `stop_music` |
| **Symbol** | 🔇 |
| **Kategorie** | Audio |

Hintergrundmusik stoppen

*Parameter:* keine

### Klang stoppen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `stop_sound` |
| **Symbol** | 🔇 |
| **Kategorie** | Audio |

Einen laufenden Klang stoppen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `sound` | Sound | — | Zu stoppender Klang |

---

<a id="game"></a>
## Spiel

### Pfeil zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_arrow` |
| **Symbol** | ➡️ |
| **Kategorie** | Spiel |

Einen Pfeil von einem Punkt zu einem anderen zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x1` | Zahl | `0` | Start X |
| `y1` | Zahl | `0` | Start Y |
| `x2` | Zahl | `100` | Spitze X |
| `y2` | Zahl | `100` | Spitze Y |
| `tip_size` | Zahl | `10` | Größe der Pfeilspitze in Pixeln |

### Hintergrund zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_background` |
| **Symbol** | 🌄 |
| **Kategorie** | Spiel |

Ein Hintergrundbild zeichnen, optional über den Bildschirm gekachelt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `background` | Text | — | Name des Hintergrund-Assets |
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `tiled` | Ja/Nein | Nein | Über den Bildschirm kacheln; optional |

### Kreis zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_circle` |
| **Symbol** | ⭕ |
| **Kategorie** | Spiel |

Einen gefüllten oder umrissenen Kreis zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | Mitte X |
| `y` | Zahl | `0` | Mitte Y |
| `radius` | Zahl | `50` | Kreisradius |
| `filled` | Ja/Nein | Ja | Gefüllt oder nur Umriss; optional |

### Ellipse zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_ellipse` |
| **Symbol** | 🥚 |
| **Kategorie** | Spiel |

Eine gefüllte oder umrissene Ellipse innerhalb eines Begrenzungsrahmens zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x1` | Zahl | `0` | Links X |
| `y1` | Zahl | `0` | Oben Y |
| `x2` | Zahl | `100` | Rechts X |
| `y2` | Zahl | `100` | Unten Y |
| `filled` | Ja/Nein | Ja | Gefüllt oder nur Umriss; optional |

### Linie zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_line` |
| **Symbol** | 📏 |
| **Kategorie** | Spiel |

Eine Linie zwischen zwei Punkten zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x1` | Zahl | `0` | Start X |
| `y1` | Zahl | `0` | Start Y |
| `x2` | Zahl | `100` | Ende X |
| `y2` | Zahl | `100` | Ende Y |

### Rechteck zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_rectangle` |
| **Symbol** | 🟥 |
| **Kategorie** | Spiel |

Ein gefülltes oder umrissenes Rechteck zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x1` | Zahl | `0` | Links X |
| `y1` | Zahl | `0` | Oben Y |
| `x2` | Zahl | `100` | Rechts X |
| `y2` | Zahl | `100` | Unten Y |
| `filled` | Ja/Nein | Ja | Gefüllt oder nur Umriss; optional |

### Skalierten Text zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_scaled_text` |
| **Symbol** | 🖍️ |
| **Kategorie** | Spiel |

Text in beliebiger Skalierung zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `text` | Text | — | Zu zeichnender Text |
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `xscale` | Zahl | `1.0` | Horizontaler Skalierungsfaktor |
| `yscale` | Zahl | `1.0` | Vertikaler Skalierungsfaktor |

### Sprite zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_sprite` |
| **Symbol** | 🖼️ |
| **Kategorie** | Spiel |

Ein Sprite-Bild an einer Position zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Zu zeichnendes Sprite |
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `subimage` | Zahl | `0` | Zu zeichnender Bildindex |

### Text zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_text` |
| **Symbol** | 🖍️ |
| **Kategorie** | Spiel |

Eine Textzeichenkette an einer Position zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `text` | Text | — | Zu zeichnender Text (unterstützt Ausdrücke) |
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `relative` | Ja/Nein | Nein | Relativ zur Position dieser Instanz statt zu absoluten Bildschirmkoordinaten zeichnen; optional |

### Variable zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_variable` |
| **Symbol** | 🔢 |
| **Kategorie** | Spiel |

Den Wert einer Variable auf dem Bildschirm zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `variable` | Text | — | Variablenname (self.var, global.var oder einfacher Name) |

### Bildschirm mit Farbe füllen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `fill_color` |
| **Symbol** | 🪣 |
| **Kategorie** | Spiel |

Den gesamten Anzeigebereich mit einer einfarbigen Farbe füllen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `color` | Farbe | `#000000` | RGB-Hexfarbe |

### Webseite öffnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `open_webpage` |
| **Symbol** | 🌐 |
| **Kategorie** | Spiel |

Eine URL im Standardbrowser öffnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `url` | Text | — | Zu öffnende Webadresse |

### Spiel neu starten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `restart_game` |
| **Symbol** | 🔁🎮 |
| **Kategorie** | Spiel |

Das Spiel vom Startraum aus neu starten

*Parameter:* keine

### Alpha setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_alpha` |
| **Symbol** | 🌫️ |
| **Kategorie** | Spiel |

Die Zeichentransparenz für nachfolgende Zeichnungen festlegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `alpha` | Zahl | `1.0` | Deckkraft von 0.0 (durchsichtig) bis 1.0 (undurchsichtig) |

### Farbe setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_color` |
| **Symbol** | 🎨 |
| **Kategorie** | Spiel |

Zeichenfarbe und Alpha für nachfolgende Zeichnungen festlegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `color` | Farbe | `#FFFFFF` | RGB-Hexfarbe |
| `alpha` | Zahl | `1.0` | Deckkraft 0.0–1.0; optional |

### Zeichenfarbe festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_draw_color` |
| **Symbol** | 🎨 |
| **Kategorie** | Spiel |

Die von nachfolgenden draw_*-Aktionen verwendete Farbe festlegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `color` | Farbe | `#000000` | RGB-Hexfarbe |

### Zeichenschrift festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_draw_font` |
| **Symbol** | 🔤 |
| **Kategorie** | Spiel |

Schriftart und Ausrichtung für das nachfolgende Textzeichnen festlegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `font` | Text | — | Name des Schrift-Assets (leer = Standardschrift); optional |
| `halign` | Auswahl | `left` | Horizontale Textausrichtung; Auswahl: `left`, `center`, `right` |
| `valign` | Auswahl | `top` | Vertikale Textausrichtung; Auswahl: `top`, `middle`, `bottom` |

### Fenstertitel festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_window_caption` |
| **Symbol** | 🪟 |
| **Kategorie** | Spiel |

Anzeige von Punkten/Leben/Gesundheit im Fenstertitel konfigurieren

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `show_score` | Ja/Nein | Ja | Die aktuelle Punktzahl an den Fenstertitel anhängen |
| `show_lives` | Ja/Nein | Ja | Die aktuelle Lebenszahl an den Fenstertitel anhängen |
| `show_health` | Ja/Nein | Nein | Den aktuellen Gesundheitswert an den Fenstertitel anhängen |
| `caption` | Text | — | Optionaler Titelpräfix, der vor den Zählern angezeigt wird; optional |

### Spielinfo anzeigen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `show_info` |
| **Symbol** | ℹ️ |
| **Kategorie** | Spiel |

Den Informationsbildschirm des Spiels anzeigen

*Parameter:* keine

### Nachricht anzeigen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `show_message` |
| **Symbol** | 💬 |
| **Kategorie** | Spiel |

Eine Nachricht anzeigen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `message` | Text | `Hello!` | Nachrichtentext |

---

<a id="control"></a>
## Steuerung

### Auf frei prüfen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `check_empty` |
| **Symbol** | 🔍 |
| **Kategorie** | Steuerung |

Wahr, wenn (x, y) kollisionsfrei ist. Mit start_block/end_block verwenden, um die folgende(n) Aktion(en) zu steuern, GM-Stil

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Text | `self.x` | Zu prüfende X-Position (Ausdruck erlaubt, z. B. self.x + 32) |
| `y` | Text | `self.y` | Zu prüfende Y-Position (Ausdruck erlaubt, z. B. self.y + 32) |
| `relative` | Ja/Nein | Nein | X/Y als Versatz zur Position dieser Instanz statt als absolute Koordinaten behandeln; optional |
| `objects` | Auswahl | `solid` | Welche Instanzen als die Position belegend gelten; Auswahl: `solid`, `all` |

### Kommentar

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `comment` |
| **Symbol** | ⚠️ |
| **Kategorie** | Steuerung |

Ein Kommentar in der Aktionsliste (ohne Laufzeitwirkung)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `text` | Text | — | Freier Kommentartext; optional |

### Sonst

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `else_action` |
| **Symbol** | ⚡ |
| **Kategorie** | Steuerung |

Kennzeichnet den Sonst-Zweig einer Bedingung

*Parameter:* keine

### Block beenden

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `end_block` |
| **Symbol** | 📁 |
| **Kategorie** | Steuerung |

Einen Aktionsblock beenden

*Parameter:* keine

### Code ausführen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `execute_code` |
| **Symbol** | 📜 |
| **Kategorie** | Steuerung |

Einen eingebetteten Python-Codeblock ausführen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `code` | Code | — | Python-Quellcode, der auf der Instanz ausgewertet wird |

### Skript ausführen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `execute_script` |
| **Symbol** | 📜 |
| **Kategorie** | Steuerung |

Eines der Skript-Assets des Projekts ausführen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `script` | Skript | — | Name des auszuführenden Projektskripts |
| `arg0` | Text | — | Im Skript als argument0 verfügbar; optional |
| `arg1` | Text | — | Im Skript als argument1 verfügbar; optional |
| `arg2` | Text | — | Im Skript als argument2 verfügbar; optional |
| `arg3` | Text | — | Im Skript als argument3 verfügbar; optional |
| `arg4` | Text | — | Im Skript als argument4 verfügbar; optional |

### Ereignis verlassen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `exit_event` |
| **Symbol** | 🚪 |
| **Kategorie** | Steuerung |

Die Ausführung der restlichen Aktionen dieses Ereignisses stoppen

*Parameter:* keine

### Wenn Schieben möglich

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `if_can_push` |
| **Symbol** | 📦 |
| **Kategorie** | Steuerung |

Prüfen, ob eine Kiste/ein Objekt in die aktuelle Richtung geschoben werden kann (Sokoban-Stil)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `direction` | Auswahl | `facing` | Zu prüfende Schieberichtung; Auswahl: `facing` |
| `object_type` | Text | `box` | Typ des geschobenen Objekts |
| `then_action` | Auswahl | `push_and_move` | Aktion, wenn Schieben möglich ist; Auswahl: `push_and_move`, `none` |
| `else_action` | Auswahl | `stop_movement` | Aktion, wenn Schieben blockiert ist; Auswahl: `stop_movement`, `none` |

### Wenn Kollision

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `if_collision` |
| **Symbol** | ❓💥 |
| **Kategorie** | Steuerung |

Bedingung: wahr, wenn die Instanz am Versatz (x, y) kollidieren würde

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | Zu testender horizontaler Versatz |
| `y` | Zahl | `0` | Zu testender vertikaler Versatz |
| `object` | Text | `any` | „any“, „solid“ oder ein Objektname; Auswahl: `any`, `solid`; optional |
| `not_flag` | Ja/Nein | Nein | Das Ergebnis negieren; optional |

### Wenn Kollision bei

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `if_collision_at` |
| **Symbol** | 🎯 |
| **Kategorie** | Steuerung |

Auf Kollision an einer Position prüfen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Text | `self.x + 32` | Ausdruck der X-Position |
| `y` | Text | `self.y` | Ausdruck der Y-Position |
| `object_type` | Auswahl | `any` | Zu prüfender Objekttyp; Auswahl: `any`, `solid` |
| `then_actions` | Aktionsliste | — | Aktionen, wenn Kollision gefunden |
| `else_actions` | Aktionsliste | — | Aktionen, wenn keine Kollision |

### Wenn Bedingung

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `if_condition` |
| **Symbol** | ❓ |
| **Kategorie** | Steuerung |

Bedingte Prüfung mit Dann-/Sonst-Aktionen

*Parameter:* keine

### Wenn Objekt existiert

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `if_object_exists` |
| **Symbol** | ❓ |
| **Kategorie** | Steuerung |

Bedingung: wahr, wenn mindestens eine Instanz des Objekts existiert

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `object` | Objekt | — | Zu prüfender Objekttyp |
| `not_flag` | Ja/Nein | Nein | Das Ergebnis negieren (handeln, wenn das Objekt NICHT existiert); optional |

### Wiederholen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `repeat` |
| **Symbol** | 🔁 |
| **Kategorie** | Steuerung |

Nächste Aktion/nächsten Block N-mal wiederholen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `times` | Zahl | `10` | Anzahl der Wiederholungen |
| `actions` | Aktionsliste | — | Zu wiederholende Aktionen |

### Variable setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_variable` |
| **Symbol** | 📝 |
| **Kategorie** | Steuerung |

Eine Instanz- oder globale Variable setzen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `variable` | Text | — | Variablenname |
| `value` | Text | `0` | Wert (Zahl, Zeichenkette oder Ausdruck) |
| `scope` | Auswahl | `self` | Gültigkeitsbereich der Variable; Auswahl: `self`, `other`, `global` |
| `relative` | Ja/Nein | Nein | Zum aktuellen Wert addieren, statt ihn zu ersetzen |

### Block beginnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `start_block` |
| **Symbol** | 📂 |
| **Kategorie** | Steuerung |

Einen Aktionsblock beginnen (zur Gruppierung)

*Parameter:* keine

### Zufall testen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `test_chance` |
| **Symbol** | 🎲❓ |
| **Kategorie** | Steuerung |

Bedingung: wahr mit einer Wahrscheinlichkeit von 1 zu „sides“

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `sides` | Zahl | `6` | Eine 1-zu-N-Chance, wahr zu sein |

### Ausdruck testen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `test_expression` |
| **Symbol** | ❓ |
| **Kategorie** | Steuerung |

Testen, ob ein Ausdruck wahr ist

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `expression` | Text | — | Auszuwertender Ausdruck (wahr, wenn >= 0,5) |
| `then_actions` | Aktionsliste | — | Aktionen, wenn wahr |
| `else_actions` | Aktionsliste | — | Aktionen, wenn falsch |

### Frage stellen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `test_question` |
| **Symbol** | ❓💬 |
| **Kategorie** | Steuerung |

Bedingung: einen Ja/Nein-Dialog anzeigen; wahr, wenn der Benutzer mit Ja antwortet

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `question` | Text | `Continue?` | Dem Spieler angezeigte Frage |

### Variable testen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `test_variable` |
| **Symbol** | ❓ |
| **Kategorie** | Steuerung |

Den Wert einer Instanz- oder globalen Variable testen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `variable` | Text | — | Variablenname |
| `value` | Text | `0` | Zu vergleichender Wert |
| `scope` | Auswahl | `self` | Gültigkeitsbereich der Variable; Auswahl: `self`, `other`, `global` |
| `operation` | Auswahl | `equal` | Vergleichsoperator; Auswahl: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="grid"></a>
## Gitter

### Wenn am Gitter

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `if_on_grid` |
| **Symbol** | ▦ |
| **Kategorie** | Gitter |

Prüfen, ob das Objekt am Gitter ausgerichtet ist

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `grid_size` | Zahl | `32` | Gitterzellengröße in Pixeln |
| `then_actions` | Aktionsliste | — | Aktionen, wenn am Gitter |
| `else_actions` | Aktionsliste | — | Aktionen, wenn nicht am Gitter |

### Am Gitter ausrichten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `snap_to_grid` |
| **Symbol** | ▦ |
| **Kategorie** | Gitter |

Instanzposition am Gitter ausrichten

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `grid_size` | Zahl | `32` | Gitterzellengröße in Pixeln |

### Stoppen, wenn keine Taste

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `stop_if_no_keys` |
| **Symbol** | ▦ |
| **Kategorie** | Gitter |

Bewegung am Gitter stoppen, wenn keine Bewegungstaste gedrückt ist (ideal für sanftes Gitter-Einrasten)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `grid_size` | Zahl | `32` | Gitterzellengröße in Pixeln |

### Gitterausrichtung testen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `test_alignment` |
| **Symbol** | ❓▦ |
| **Kategorie** | Gitter |

Bedingung: wahr, wenn die Instanz an einem Gitter ausgerichtet ist

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `hsnap` | Zahl | `32` | Horizontaler Gitterabstand in Pixeln |
| `vsnap` | Zahl | `32` | Vertikaler Gitterabstand in Pixeln |

---

<a id="views"></a>
## Ansichten

### Ansichten aktivieren

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `enable_views` |
| **Symbol** | 🎥 |
| **Kategorie** | Ansichten |

Das Kamera-/Ansichtssystem des Raums ein- oder ausschalten (ermöglicht das Scrollen eines Levels, das größer als das Fenster ist)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `enable` | Ja/Nein | Ja | An = Kameraansichten; aus = den ganzen Raum auf einmal zeichnen |

### Ansicht festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_view` |
| **Symbol** | 🎥 |
| **Kategorie** | Ansichten |

Eine Kameraansicht konfigurieren: welchen Teil des Raums sie zeigt, wo sie auf dem Bildschirm zeichnet und welches Objekt sie verfolgt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `view` | Auswahl | `0` | Welche der 8 Ansichten konfiguriert wird; Auswahl: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` |
| `visible` | Ja/Nein | Ja | Diese Ansicht zeichnen |
| `view_x` | Zahl | `0` | Linker Rand des angezeigten Raumbereichs |
| `view_y` | Zahl | `0` | Oberer Rand des angezeigten Raumbereichs |
| `view_w` | Zahl | `800` | Breite des angezeigten Raumbereichs |
| `view_h` | Zahl | `600` | Höhe des angezeigten Raumbereichs |
| `port_x` | Zahl | `0` | Linker Rand auf dem Bildschirm |
| `port_y` | Zahl | `0` | Oberer Rand auf dem Bildschirm |
| `port_w` | Zahl | `800` | Auf dem Bildschirm gezeichnete Breite |
| `port_h` | Zahl | `600` | Auf dem Bildschirm gezeichnete Höhe |
| `follow` | Objekt | — | Objekt, das die Kamera verfolgt (leer = feste Ansicht); optional |
| `hborder` | Zahl | `32` | Horizontaler Rand, bevor die Kamera scrollt |
| `vborder` | Zahl | `32` | Vertikaler Rand, bevor die Kamera scrollt |
| `hspeed` | Zahl | `-1` | Maximale horizontale Scrollgeschwindigkeit (-1 = sofort) |
| `vspeed` | Zahl | `-1` | Maximale vertikale Scrollgeschwindigkeit (-1 = sofort) |

---

<a id="3d-view"></a>
## 3D-Ansicht

### DOOM-HUD zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_doom_hud` |
| **Symbol** | 🎯 |
| **Kategorie** | 3D-Ansicht |

Eine untere Statusleiste im DOOM-Stil (Gesundheitsbalken + Zahl, Punkte, Leben, ein Zielzähler und ein auf die Gesundheit reagierendes Gesichtssymbol) über der Raycast-Ansicht zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | Linker Rand der Leiste, in Bildschirmpixeln |
| `y` | Zahl | `-1` | Oberer Rand der Leiste; ein negativer Wert richtet sie automatisch am unteren Fensterrand aus, unter dem verkleinerten Ansichtsfenster; optional |
| `width` | Zahl | `0` | Leistenbreite (0 = volle Fensterbreite); optional |
| `height` | Zahl | `42` | Leistenhöhe; halten Sie sie mit dem in enable_raycast_view reservierten viewport_height-Band abgestimmt; optional |
| `back_color` | Farbe | `#101010` | Hintergrundpanel der Leiste; optional |
| `divider_color` | Farbe | `#505050` | Oberer Rand und Hintergrund des Gesundheitsbalkens; optional |
| `text_color` | Farbe | `#ffffff` | Farbe des gesamten Leistentexts; optional |
| `health_label` | Text | `Health` | optional |
| `health_bar_width` | Zahl | `90` | optional |
| `health_bar_height` | Zahl | `14` | optional |
| `bar_color` | Farbe | `#20c020` | Füllfarbe des Gesundheitsbalkens; optional |
| `face_sprite` | Sprite | — | Horizontaler Streifen von Gesichtsbildern, das gesündeste zuerst (leer = kein Gesichtssymbol); optional |
| `face_frames` | Zahl | `4` | Wie viele Bilder der Gesichtsstreifen hat; die Gesundheit wird gleichmäßig auf sie verteilt; optional |
| `score_label` | Text | `Score: ` | optional |
| `lives_sprite` | Sprite | — | Sprite, das einmal pro verbleibendem Leben gezeichnet wird; optional |
| `lives_scale` | Zahl | `1.0` | optional |
| `objective_value` | Text | `0` | Ausdruck, der nach der Zielbeschriftung angezeigt wird (binden Sie Ihre eigene Schlüssel-/Quest-Variable ein); optional |
| `objective_label` | Text | `Keys: ` | optional |

### Minikarte zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_minimap` |
| **Symbol** | 🗺️ |
| **Kategorie** | 3D-Ansicht |

Eine nach Norden ausgerichtete Minikarte der Wände des Raycast-Raums zeichnen, mit einer Markierung, die zeigt, wo die Kamera ist und in welche Richtung sie blickt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | Linker Rand der Minikarte, in Bildschirmpixeln |
| `y` | Zahl | `0` | Oberer Rand der Minikarte, in Bildschirmpixeln |
| `size` | Zahl | `120` | Breite und Höhe des Minikarten-Quadrats, in Pixeln; optional |
| `back_color` | Farbe | `#101018` | Panelfarbe hinter der Karte; optional |
| `wall_color` | Farbe | `#8080a0` | Farbe der Wandlinien; optional |
| `player_color` | Farbe | `#ffd040` | Farbe der Kameramarkierung und ihrer Blickrichtungslinie; optional |

### Raycast-Ansicht aktivieren

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `enable_raycast_view` |
| **Symbol** | 🕹️ |
| **Kategorie** | 3D-Ansicht |

Den Raum als First-Person-3D-Ansicht im Doom/Wolfenstein-Stil (Wände, Himmel, Boden) statt als Draufsicht darstellen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `enable` | Ja/Nein | Ja | An = First-Person-Raycast-Ansicht; aus = normale Draufsicht |
| `camera_object` | Objekt | — | Objekt, dessen Position + Blickwinkel die Kamera ist (leer = das Objekt, das diese Aktion ausführt); optional |
| `fov` | Zahl | `66` | Horizontales Sichtfeld in Grad; optional |
| `render_distance` | Zahl | `20` | Maximale Strahllänge in Gitterzellen; optional |
| `cell_size` | Zahl | `32` | Gitterzellengröße in Pixeln (an das Wandplatzierungsgitter angepasst); optional |
| `columns` | Zahl | `320` | Bildschirmspalten zum Raycasten (weniger = schneller/grobkörniger); optional |
| `wall_color` | Farbe | `#993333` | Einfarbige Wandfarbe, wenn keine Wandtextur gesetzt ist; optional |
| `floor_color` | Farbe | `#464632` | Einfarbige Bodenfarbe, wenn keine Bodentextur gesetzt ist; optional |
| `ceiling_color` | Farbe | `#87CEEB` | Einfarbige Deckenfarbe, wenn keine Himmel-/Deckentextur gesetzt ist; optional |
| `wall_texture` | Sprite | — | Sprite zum Texturieren jeder Wand (leer = einfarbig); optional |
| `sky_texture` | Sprite | — | Sprite für einen schwenkenden Himmel über der Decke (leer = einfarbig); optional |
| `floor_texture` | Sprite | — | Auf den Boden projiziertes Sprite (leer = einfarbig); optional |
| `ceiling_texture` | Sprite | — | Auf die Decke projiziertes Sprite, wenn kein Himmel gesetzt ist; optional |
| `wall_textured` | Ja/Nein | Ja | Aus erzwingt einfarbige Wandfarben, auch wenn eine Textur gesetzt ist; optional |
| `floor_cast_res` | Zahl | `4` | Boden-Downsampling (höher = schneller + grobkörniger); optional |
| `viewport_height` | Zahl | `0` | Die 3D-Ansicht auf diese Pixelhöhe verkleinern (Letterbox) und das Band darunter für eine DOOM-Statusleiste reservieren (0 = volle Fensterhöhe, unverändert); optional |

### Blickwinkel setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_facing_angle` |
| **Symbol** | 🧭 |
| **Kategorie** | 3D-Ansicht |

Die Blickrichtung der Instanz für eine Raycast-Kamera (First-Person) festlegen — unabhängig von der Bewegungsgeschwindigkeit

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `angle` | Zahl | `0` | Grad (0=rechts, 90=oben, 180=links, 270=unten) |
| `relative` | Ja/Nein | Nein | Zum aktuellen Blickwinkel addieren, statt ihn zu ersetzen; optional |

---

## Siehe auch

- [Ereignisreferenz](Event-Reference_de) — die Ereignisse, die Aktionen auslösen
- [Voreinstellungs-Leitfaden](Preset-Guide_de) — welche Aktionen jede Voreinstellung/Edition bereitstellt
- [3D-Ansicht](3D-View_de) — die First-Person-Raycast-Aktionen
- [Erweiterungen](Extensions_de) — wie die 3D-Ansicht-Aktionen bereitgestellt werden
