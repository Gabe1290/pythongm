# Gitter

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

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

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (8)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (25)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (16)
- [Particles](Full-Action-Reference-Particles_de) (8)
- [Réseau](Full-Action-Reference-Network-Actions_de) (15)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
