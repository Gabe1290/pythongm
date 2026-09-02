# Zeitsteuerung

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Pause Timeline

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `pause_timeline` |
| **Symbol** | ⏸️ |
| **Kategorie** | Zeitsteuerung |

Pause timeline playback at the current position

*Parameter:* keine

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

### Set Timeline

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_timeline` |
| **Symbol** | ⏱️ |
| **Kategorie** | Zeitsteuerung |

Set this instance's timeline label and reset its position to 0 (bookkeeping only — see category note)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `timeline` | Text | — | A label for your own reference; not a resource lookup |

### Set Timeline Position

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_timeline_position` |
| **Symbol** | ⏱️ |
| **Kategorie** | Zeitsteuerung |

Set (or offset) this instance's timeline position

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `position` | Zahl | `0` | Position in steps |
| `relative` | Ja/Nein | Nein | Add to the current position instead of setting it absolutely |

### Set Timeline Speed

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_timeline_speed` |
| **Symbol** | ⏱️ |
| **Kategorie** | Zeitsteuerung |

Set the timeline playback speed multiplier

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `speed` | Zahl | `1.0` | 1.0=normal, 0.5=half speed, 2.0=double speed |

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

### Start Timeline

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `start_timeline` |
| **Symbol** | ▶️ |
| **Kategorie** | Zeitsteuerung |

Begin or resume timeline playback from the current position

*Parameter:* keine

### Stop Timeline

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `stop_timeline` |
| **Symbol** | ⏹️ |
| **Kategorie** | Zeitsteuerung |

Stop timeline playback and reset the position to 0

*Parameter:* keine

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (25)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (16)
- [Particles](Full-Action-Reference-Particles_de) (8)
- [Réseau](Full-Action-Reference-Network-Actions_de) (15)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
