# micro:bit

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Display löschen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_clear_display` |
| **Symbol** | ⬛ |
| **Kategorie** | micro:bit |

Alle LEDs ausschalten und alles Wartende verwerfen

*Parameter:* keine

### Wenn Taste gedrückt

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_if_button` |
| **Symbol** | 🔘 |
| **Kategorie** | micro:bit |

Wahr, solange die Taste gedrückt gehalten wird (A+B = beide)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `button` | Auswahl | `a` | Auswahl: `a`, `b`, `ab`, `logo` |

### Wenn Geste

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_if_gesture` |
| **Symbol** | 🤝 |
| **Kategorie** | micro:bit |

Wahr, solange sich das Board in dieser Geste oder Lage befindet

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `gesture` | Auswahl | `shake` | Auswahl: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### Wenn LED-Helligkeit

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_if_pixel` |
| **Symbol** | 🔍 |
| **Kategorie** | micro:bit |

Die Helligkeit einer LED (0 bis 9) mit einem Wert vergleichen; standardmäßig lautet die Frage „leuchtet sie?“

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Text | `0` |  |
| `y` | Text | `0` |  |
| `comparison` | Auswahl | `>` | Auswahl: `<`, `<=`, `==`, `>=`, `>`, `!=`; optional |
| `value` | Text | `0` | optional |

### Wenn Neigung

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_if_tilt` |
| **Symbol** | 📐 |
| **Kategorie** | micro:bit |

Eine Achse des Beschleunigungssensors (Milli-g, von -2048 bis 2048) mit einem Wert vergleichen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `axis` | Auswahl | `x` | Auswahl: `x`, `y`, `z` |
| `comparison` | Auswahl | `>` | Auswahl: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Text | `300` |  |

### Melodie spielen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_play_melody` |
| **Symbol** | 🎵 |
| **Kategorie** | micro:bit |

Eine eingebaute Melodie spielen (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, POWER_UP…) oder eigene Noten wie „C4:4 E G C5:8 R:4“ (Note, Oktave, :Dauer; R ist eine Pause)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `melody` | Text | `DADADADUM` | Built-in name, or notes separated by spaces |
| `tempo` | Text | `120` | optional |

### Ton spielen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_play_tone` |
| **Symbol** | 🔔 |
| **Kategorie** | micro:bit |

Einen Piepton mit einer Frequenz für eine Anzahl Millisekunden ausgeben. Töne werden in eine Warteschlange gestellt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `frequency` | Text | `440` | Pitch in hertz (440 = the note A) |
| `duration` | Text | `500` | optional |

### Sensor lesen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_read_sensor` |
| **Symbol** | 📡 |
| **Kategorie** | micro:bit |

Einen Sensor des micro:bit in eine Variable dieses Objekts lesen (oder in eine globale Variable, wenn der Name mit „global.“ beginnt)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `sensor` | Auswahl | `accelerometer x` | Auswahl: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Text | `sensor_value` | Variable that receives the reading |

### Text scrollen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_scroll_text` |
| **Symbol** | 🔤 |
| **Kategorie** | micro:bit |

Einen Text über das LED-Display scrollen lassen. Setze den Text in Anführungszeichen ("Hallo"); sonst wird ein Minus oder Plus als Rechnung gelesen. Umlaute und Akzente erscheinen als ?, wie auf dem echten Board

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `text` | Text | `"Hello"` | Text or expression to scroll |
| `delay` | Zahl | `150` | Scroll speed (MicroPython default 150); optional |

### Funknachricht senden

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_radio_send` |
| **Symbol** | 📻 |
| **Kategorie** | micro:bit |

Eine Zahl oder einen Text an die anderen micro:bits derselben Gruppe senden (nicht an dieses). Sie erhalten das Ereignis „Funknachricht empfangen“, mit dem Wert in radio_number und radio_string. Setze den Text in Anführungszeichen; er wird auf 32 Zeichen gekürzt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `value` | Text | `1` | A number, an expression or quoted text |

### Display-Helligkeit

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_set_brightness` |
| **Symbol** | 🔆 |
| **Kategorie** | micro:bit |

Gesamthelligkeit der LEDs, von 0 (aus) bis 255 (maximal)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `brightness` | Text | `255` |  |

### LED einschalten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_set_pixel` |
| **Symbol** | 💡 |
| **Kategorie** | micro:bit |

Eine LED sofort einschalten (x und y von 0 bis 4, Helligkeit von 0 bis 9)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Text | `0` |  |
| `y` | Text | `0` |  |
| `brightness` | Text | `9` | optional |

### Funkgruppe festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_radio_set_group` |
| **Symbol** | 📡 |
| **Kategorie** | micro:bit |

Die Funkgruppe wählen (0 bis 255). Nur micro:bits in derselben Gruppe hören sich; jedes Board startet in Gruppe 0

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `group` | Text | `0` |  |

### Bild anzeigen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_show_image` |
| **Symbol** | ❤️ |
| **Kategorie** | micro:bit |

Ein Bild auf den LEDs anzeigen: ein Name (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL…) oder fünf Zeilen mit Helligkeitsziffern wie „09090:99999:99999:09990:00900“. Anzeigen werden in eine Warteschlange gestellt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `image` | Text | `HEART` | Built-in image name, or 5 rows of 5 digits (0-9) separated by colons |
| `hold` | Zahl | `0` | How long it stays before the next queued item (0 = until something else is shown); optional |

### Zahl anzeigen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_show_number` |
| **Symbol** | 🔢 |
| **Kategorie** | micro:bit |

Eine Zahl anzeigen: eine Ziffer bleibt stehen, eine längere Zahl scrollt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `value` | Text | `0` | Number or expression |

### Ton stoppen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `microbit_stop_sound` |
| **Symbol** | 🔇 |
| **Kategorie** | micro:bit |

Den Lautsprecher abschalten und wartende Töne verwerfen

*Parameter:* keine

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
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (20)
- [Zeichnen](Full-Action-Reference-Drawing_de) (11)
- [Netzwerk](Full-Action-Reference-Network-Actions_de) (22)
- [Partikel](Full-Action-Reference-Particles_de) (8)
- [Punkte/Leben/Gesundheit](Full-Action-Reference-Score-Lives-Health_de) (5)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
