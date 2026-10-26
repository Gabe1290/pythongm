# Score/Lives/Health

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Bestenliste löschen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `clear_highscore` |
| **Symbol** | 🗑️🏆 |
| **Kategorie** | Score/Lives/Health |

Alle Einträge der Bestenliste löschen

*Parameter:* keine

### Bestenliste anzeigen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `show_highscore` |
| **Symbol** | 🏆 |
| **Kategorie** | Score/Lives/Health |

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
| **Kategorie** | Score/Lives/Health |

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
| **Kategorie** | Score/Lives/Health |

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
| **Kategorie** | Score/Lives/Health |

Bedingung: die Punktzahl mit einem Wert vergleichen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `value` | Zahl | `0` | Vergleichswert |
| `operation` | Auswahl | `equal` | Vergleichsoperator; Auswahl: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (21)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (6)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (8)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (14)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (3)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (18)
- [Zeichnen](Full-Action-Reference-Drawing_de) (11)
- [Netzwerk](Full-Action-Reference-Network-Actions_de) (22)
- [Partikel](Full-Action-Reference-Particles_de) (8)
- [micro:bit](Full-Action-Reference-Microbit-Actions_de) (16)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
