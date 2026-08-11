# Punkte

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

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

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (2)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (20)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (4)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
