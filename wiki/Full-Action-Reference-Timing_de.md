# Zeitsteuerung

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Zeitleiste anhalten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `pause_timeline` |
| **Symbol** | ⏸️ |
| **Kategorie** | Zeitsteuerung |

Hält die Wiedergabe der Zeitleiste an der aktuellen Position an

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

### Zeitleiste festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_timeline` |
| **Symbol** | ⏱️ |
| **Kategorie** | Zeitsteuerung |

Setzt die Zeitleisten-Bezeichnung dieser Instanz und stellt ihre Position auf 0 zurück (nur Buchführung – siehe Hinweis zur Kategorie)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `timeline` | Text | — | Eine Bezeichnung für Sie selbst; keine Ressourcensuche |

### Position der Zeitleiste festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_timeline_position` |
| **Symbol** | ⏱️ |
| **Kategorie** | Zeitsteuerung |

Setzt die Position dieser Instanz auf der Zeitleiste (oder verschiebt sie)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `position` | Zahl | `0` | Position in Schritten |
| `relative` | Ja/Nein | Nein | Zur aktuellen Position addieren, statt sie absolut zu setzen |

### Geschwindigkeit der Zeitleiste festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_timeline_speed` |
| **Symbol** | ⏱️ |
| **Kategorie** | Zeitsteuerung |

Setzt den Geschwindigkeitsfaktor der Zeitleisten-Wiedergabe

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `speed` | Zahl | `1.0` | 1.0 = normal, 0.5 = halbe Geschwindigkeit, 2.0 = doppelte Geschwindigkeit |

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

### Zeitleiste starten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `start_timeline` |
| **Symbol** | ▶️ |
| **Kategorie** | Zeitsteuerung |

Startet die Wiedergabe der Zeitleiste ab der aktuellen Position oder setzt sie fort

*Parameter:* keine

### Zeitleiste stoppen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `stop_timeline` |
| **Symbol** | ⏹️ |
| **Kategorie** | Zeitsteuerung |

Stoppt die Wiedergabe der Zeitleiste und stellt die Position auf 0 zurück

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
- [Netzwerk](Full-Action-Reference-Network-Actions_de) (15)
- [Partikel](Full-Action-Reference-Particles_de) (8)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
