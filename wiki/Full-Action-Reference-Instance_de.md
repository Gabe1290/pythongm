# Instanz

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

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

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
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
