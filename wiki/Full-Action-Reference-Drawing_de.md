# Zeichnen

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Pfeil zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_arrow` |
| **Symbol** | ➡️ |
| **Kategorie** | Zeichnen |

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
| **Kategorie** | Zeichnen |

Ein Hintergrundbild zeichnen, optional über den Bildschirm gekachelt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `background` | Text | — | Name des Hintergrund-Assets |
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `tiled` | Ja/Nein | Nein | Über den Bildschirm kacheln; optional |

### Ellipse zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_ellipse` |
| **Symbol** | 🥚 |
| **Kategorie** | Zeichnen |

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
| **Kategorie** | Zeichnen |

Eine Linie zwischen zwei Punkten zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x1` | Zahl | `0` | Start X |
| `y1` | Zahl | `0` | Start Y |
| `x2` | Zahl | `100` | Ende X |
| `y2` | Zahl | `100` | Ende Y |

### Skalierten Text zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_scaled_text` |
| **Symbol** | 🖍️ |
| **Kategorie** | Zeichnen |

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
| **Kategorie** | Zeichnen |

Ein Sprite-Bild an einer Position zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Zu zeichnendes Sprite |
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `subimage` | Zahl | `0` | Zu zeichnender Bildindex |

### Variable zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_variable` |
| **Symbol** | 🔢 |
| **Kategorie** | Zeichnen |

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
| **Kategorie** | Zeichnen |

Den gesamten Anzeigebereich mit einer einfarbigen Farbe füllen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `color` | Farbe | `#000000` | RGB-Hexfarbe |

### Farbe setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_color` |
| **Symbol** | 🎨 |
| **Kategorie** | Zeichnen |

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
| **Kategorie** | Zeichnen |

Die von nachfolgenden draw_*-Aktionen verwendete Farbe festlegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `color` | Farbe | `#000000` | RGB-Hexfarbe |

### Zeichenschrift festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_draw_font` |
| **Symbol** | 🔤 |
| **Kategorie** | Zeichnen |

Schriftart und Ausrichtung für das nachfolgende Textzeichnen festlegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `font` | Text | — | Name des Schrift-Assets (leer = Standardschrift); optional |
| `halign` | Auswahl | `left` | Horizontale Textausrichtung; Auswahl: `left`, `center`, `right` |
| `valign` | Auswahl | `top` | Vertikale Textausrichtung; Auswahl: `top`, `middle`, `bottom` |

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
- [Netzwerk](Full-Action-Reference-Network-Actions_de) (22)
- [Partikel](Full-Action-Reference-Particles_de) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_de) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_de) (16)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
