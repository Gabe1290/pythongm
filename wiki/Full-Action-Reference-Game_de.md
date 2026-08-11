# Spiel

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Pfeil zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_arrow` |
| **Symbol** | ➡️ |
| **Kategorie** | Spiel |

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
| **Kategorie** | Spiel |

Ein Hintergrundbild zeichnen, optional über den Bildschirm gekachelt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `background` | Text | — | Name des Hintergrund-Assets |
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `tiled` | Ja/Nein | Nein | Über den Bildschirm kacheln; optional |

### Kreis zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_circle` |
| **Symbol** | ⭕ |
| **Kategorie** | Spiel |

Einen gefüllten oder umrissenen Kreis zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | Mitte X |
| `y` | Zahl | `0` | Mitte Y |
| `radius` | Zahl | `50` | Kreisradius |
| `filled` | Ja/Nein | Ja | Gefüllt oder nur Umriss; optional |

### Ellipse zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_ellipse` |
| **Symbol** | 🥚 |
| **Kategorie** | Spiel |

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
| **Kategorie** | Spiel |

Eine Linie zwischen zwei Punkten zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x1` | Zahl | `0` | Start X |
| `y1` | Zahl | `0` | Start Y |
| `x2` | Zahl | `100` | Ende X |
| `y2` | Zahl | `100` | Ende Y |

### Rechteck zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_rectangle` |
| **Symbol** | 🟥 |
| **Kategorie** | Spiel |

Ein gefülltes oder umrissenes Rechteck zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x1` | Zahl | `0` | Links X |
| `y1` | Zahl | `0` | Oben Y |
| `x2` | Zahl | `100` | Rechts X |
| `y2` | Zahl | `100` | Unten Y |
| `filled` | Ja/Nein | Ja | Gefüllt oder nur Umriss; optional |

### Skalierten Text zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_scaled_text` |
| **Symbol** | 🖍️ |
| **Kategorie** | Spiel |

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
| **Kategorie** | Spiel |

Ein Sprite-Bild an einer Position zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Zu zeichnendes Sprite |
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `subimage` | Zahl | `0` | Zu zeichnender Bildindex |

### Text zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_text` |
| **Symbol** | 🖍️ |
| **Kategorie** | Spiel |

Eine Textzeichenkette an einer Position zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `text` | Text | — | Zu zeichnender Text (unterstützt Ausdrücke) |
| `x` | Zahl | `0` | X-Position |
| `y` | Zahl | `0` | Y-Position |
| `relative` | Ja/Nein | Nein | Relativ zur Position dieser Instanz statt zu absoluten Bildschirmkoordinaten zeichnen; optional |

### Variable zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_variable` |
| **Symbol** | 🔢 |
| **Kategorie** | Spiel |

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
| **Kategorie** | Spiel |

Den gesamten Anzeigebereich mit einer einfarbigen Farbe füllen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `color` | Farbe | `#000000` | RGB-Hexfarbe |

### Webseite öffnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `open_webpage` |
| **Symbol** | 🌐 |
| **Kategorie** | Spiel |

Eine URL im Standardbrowser öffnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `url` | Text | — | Zu öffnende Webadresse |

### Spiel neu starten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `restart_game` |
| **Symbol** | 🔁🎮 |
| **Kategorie** | Spiel |

Das Spiel vom Startraum aus neu starten

*Parameter:* keine

### Alpha setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_alpha` |
| **Symbol** | 🌫️ |
| **Kategorie** | Spiel |

Die Zeichentransparenz für nachfolgende Zeichnungen festlegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `alpha` | Zahl | `1.0` | Deckkraft von 0.0 (durchsichtig) bis 1.0 (undurchsichtig) |

### Farbe setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_color` |
| **Symbol** | 🎨 |
| **Kategorie** | Spiel |

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
| **Kategorie** | Spiel |

Die von nachfolgenden draw_*-Aktionen verwendete Farbe festlegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `color` | Farbe | `#000000` | RGB-Hexfarbe |

### Zeichenschrift festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_draw_font` |
| **Symbol** | 🔤 |
| **Kategorie** | Spiel |

Schriftart und Ausrichtung für das nachfolgende Textzeichnen festlegen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `font` | Text | — | Name des Schrift-Assets (leer = Standardschrift); optional |
| `halign` | Auswahl | `left` | Horizontale Textausrichtung; Auswahl: `left`, `center`, `right` |
| `valign` | Auswahl | `top` | Vertikale Textausrichtung; Auswahl: `top`, `middle`, `bottom` |

### Fenstertitel festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_window_caption` |
| **Symbol** | 🪟 |
| **Kategorie** | Spiel |

Anzeige von Punkten/Leben/Gesundheit im Fenstertitel konfigurieren

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `show_score` | Ja/Nein | Ja | Die aktuelle Punktzahl an den Fenstertitel anhängen |
| `show_lives` | Ja/Nein | Ja | Die aktuelle Lebenszahl an den Fenstertitel anhängen |
| `show_health` | Ja/Nein | Nein | Den aktuellen Gesundheitswert an den Fenstertitel anhängen |
| `caption` | Text | — | Optionaler Titelpräfix, der vor den Zählern angezeigt wird; optional |

### Spielinfo anzeigen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `show_info` |
| **Symbol** | ℹ️ |
| **Kategorie** | Spiel |

Den Informationsbildschirm des Spiels anzeigen

*Parameter:* keine

### Nachricht anzeigen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `show_message` |
| **Symbol** | 💬 |
| **Kategorie** | Spiel |

Eine Nachricht anzeigen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `message` | Text | `Hello!` | Nachrichtentext |

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (2)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (4)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
