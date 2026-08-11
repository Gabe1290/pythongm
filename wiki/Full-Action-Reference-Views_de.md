# Ansichten

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

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

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (2)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (20)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (4)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
