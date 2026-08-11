# Zeitsteuerung

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

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

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (20)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (4)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
