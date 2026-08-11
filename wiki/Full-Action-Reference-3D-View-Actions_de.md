# 3D-Ansicht

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### DOOM-HUD zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_doom_hud` |
| **Symbol** | 🎯 |
| **Kategorie** | 3D-Ansicht |

Eine untere Statusleiste im DOOM-Stil (Gesundheitsbalken + Zahl, Punkte, Leben, ein Zielzähler und ein auf die Gesundheit reagierendes Gesichtssymbol) über der Raycast-Ansicht zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | Linker Rand der Leiste, in Bildschirmpixeln |
| `y` | Zahl | `-1` | Oberer Rand der Leiste; ein negativer Wert richtet sie automatisch am unteren Fensterrand aus, unter dem verkleinerten Ansichtsfenster; optional |
| `width` | Zahl | `0` | Leistenbreite (0 = volle Fensterbreite); optional |
| `height` | Zahl | `42` | Leistenhöhe; halten Sie sie mit dem in enable_raycast_view reservierten viewport_height-Band abgestimmt; optional |
| `back_color` | Farbe | `#101010` | Hintergrundpanel der Leiste; optional |
| `divider_color` | Farbe | `#505050` | Oberer Rand und Hintergrund des Gesundheitsbalkens; optional |
| `text_color` | Farbe | `#ffffff` | Farbe des gesamten Leistentexts; optional |
| `health_label` | Text | `Health` | optional |
| `health_bar_width` | Zahl | `90` | optional |
| `health_bar_height` | Zahl | `14` | optional |
| `bar_color` | Farbe | `#20c020` | Füllfarbe des Gesundheitsbalkens; optional |
| `face_sprite` | Sprite | — | Horizontaler Streifen von Gesichtsbildern, das gesündeste zuerst (leer = kein Gesichtssymbol); optional |
| `face_frames` | Zahl | `4` | Wie viele Bilder der Gesichtsstreifen hat; die Gesundheit wird gleichmäßig auf sie verteilt; optional |
| `score_label` | Text | `Score: ` | optional |
| `lives_sprite` | Sprite | — | Sprite, das einmal pro verbleibendem Leben gezeichnet wird; optional |
| `lives_scale` | Zahl | `1.0` | optional |
| `objective_value` | Text | `0` | Ausdruck, der nach der Zielbeschriftung angezeigt wird (binden Sie Ihre eigene Schlüssel-/Quest-Variable ein); optional |
| `objective_label` | Text | `Keys: ` | optional |

### Minikarte zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_minimap` |
| **Symbol** | 🗺️ |
| **Kategorie** | 3D-Ansicht |

Eine nach Norden ausgerichtete Minikarte der Wände des Raycast-Raums zeichnen, mit einer Markierung, die zeigt, wo die Kamera ist und in welche Richtung sie blickt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | Linker Rand der Minikarte, in Bildschirmpixeln |
| `y` | Zahl | `0` | Oberer Rand der Minikarte, in Bildschirmpixeln |
| `size` | Zahl | `120` | Breite und Höhe des Minikarten-Quadrats, in Pixeln; optional |
| `back_color` | Farbe | `#101018` | Panelfarbe hinter der Karte; optional |
| `wall_color` | Farbe | `#8080a0` | Farbe der Wandlinien; optional |
| `player_color` | Farbe | `#ffd040` | Farbe der Kameramarkierung und ihrer Blickrichtungslinie; optional |

### Raycast-Ansicht aktivieren

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `enable_raycast_view` |
| **Symbol** | 🕹️ |
| **Kategorie** | 3D-Ansicht |

Den Raum als First-Person-3D-Ansicht im Doom/Wolfenstein-Stil (Wände, Himmel, Boden) statt als Draufsicht darstellen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `enable` | Ja/Nein | Ja | An = First-Person-Raycast-Ansicht; aus = normale Draufsicht |
| `camera_object` | Objekt | — | Objekt, dessen Position + Blickwinkel die Kamera ist (leer = das Objekt, das diese Aktion ausführt); optional |
| `fov` | Zahl | `66` | Horizontales Sichtfeld in Grad; optional |
| `render_distance` | Zahl | `20` | Maximale Strahllänge in Gitterzellen; optional |
| `cell_size` | Zahl | `32` | Gitterzellengröße in Pixeln (an das Wandplatzierungsgitter angepasst); optional |
| `columns` | Zahl | `320` | Bildschirmspalten zum Raycasten (weniger = schneller/grobkörniger); optional |
| `wall_color` | Farbe | `#993333` | Einfarbige Wandfarbe, wenn keine Wandtextur gesetzt ist; optional |
| `floor_color` | Farbe | `#464632` | Einfarbige Bodenfarbe, wenn keine Bodentextur gesetzt ist; optional |
| `ceiling_color` | Farbe | `#87CEEB` | Einfarbige Deckenfarbe, wenn keine Himmel-/Deckentextur gesetzt ist; optional |
| `wall_texture` | Sprite | — | Sprite zum Texturieren jeder Wand (leer = einfarbig); optional |
| `sky_texture` | Sprite | — | Sprite für einen schwenkenden Himmel über der Decke (leer = einfarbig); optional |
| `floor_texture` | Sprite | — | Auf den Boden projiziertes Sprite (leer = einfarbig); optional |
| `ceiling_texture` | Sprite | — | Auf die Decke projiziertes Sprite, wenn kein Himmel gesetzt ist; optional |
| `wall_textured` | Ja/Nein | Ja | Aus erzwingt einfarbige Wandfarben, auch wenn eine Textur gesetzt ist; optional |
| `floor_cast_res` | Zahl | `4` | Boden-Downsampling (höher = schneller + grobkörniger); optional |
| `viewport_height` | Zahl | `0` | Die 3D-Ansicht auf diese Pixelhöhe verkleinern (Letterbox) und das Band darunter für eine DOOM-Statusleiste reservieren (0 = volle Fensterhöhe, unverändert); optional |

### Blickwinkel setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_facing_angle` |
| **Symbol** | 🧭 |
| **Kategorie** | 3D-Ansicht |

Die Blickrichtung der Instanz für eine Raycast-Kamera (First-Person) festlegen — unabhängig von der Bewegungsgeschwindigkeit

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `angle` | Zahl | `0` | Grad (0=rechts, 90=oben, 180=links, 270=unten) |
| `relative` | Ja/Nein | Nein | Zum aktuellen Blickwinkel addieren, statt ihn zu ersetzen; optional |

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
- [Ansichten](Full-Action-Reference-Views_de) (2)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
