# Spiel

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

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
| `color` | Farbe | — | Textfarbe (z. B. #ffffff). Leer = die aktive Zeichenfarbe, sonst Schwarz.; optional |

### Spiel laden

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `load_game` |
| **Symbol** | 📂 |
| **Kategorie** | Spiel |

Stellt Raum, Punkte/Leben/Gesundheit, globale Variablen und Instanzzustände aus einer Speicherdatei wieder her

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `filename` | Text | `savegame.sav` | Name der zu ladenden Speicherdatei (aus dem Ordner saves/ des Projekts) |

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

### Spiel speichern

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `save_game` |
| **Symbol** | 💾 |
| **Kategorie** | Spiel |

Speichert den aktuellen Raum, Punkte/Leben/Gesundheit, globale Variablen und Instanzzustände in einer Datei

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `filename` | Text | `savegame.sav` | Name der Speicherdatei (wird in den Ordner saves/ des Projekts geschrieben) |

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

### Video abspielen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `show_video` |
| **Symbol** | 🎬 |
| **Kategorie** | Spiel |

Spielt eine Videodatei im Standard-Videoplayer des Systems ab – sie öffnet sich in einem eigenen Fenster und wird nicht im Spiel selbst dargestellt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `filename` | Text | — | Pfad zur Videodatei |
| `fullscreen` | Ja/Nein | Nein | Vollbildwiedergabe anfordern (ob das geht, hängt vom Player Ihres Systems ab); optional |

### Startbild: Bild zeigen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `splash_show_image` |
| **Symbol** | 🖼️ |
| **Kategorie** | Spiel |

Zeigt ein Sprite bildschirmfüllend und hält das Spiel an, bis der Spieler es wegklickt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `image` | Sprite | — | Sprite, das bildschirmfüllend angezeigt wird |

### Startbild: Text zeigen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `splash_show_text` |
| **Symbol** | 💬 |
| **Kategorie** | Spiel |

Zeigt eine Nachricht und hält das Spiel an, bis der Spieler sie wegklickt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `text` | Text | — | Anzuzeigende Nachricht |

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (21)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (6)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (8)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (3)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (18)
- [Zeichnen](Full-Action-Reference-Drawing_de) (11)
- [Netzwerk](Full-Action-Reference-Network-Actions_de) (22)
- [Partikel](Full-Action-Reference-Particles_de) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_de) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_de) (16)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
