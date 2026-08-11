# Audio

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

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

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (2)
- [Spiel](Full-Action-Reference-Game_de) (20)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (4)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
