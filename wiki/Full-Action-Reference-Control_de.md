# Steuerung

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Auf frei prüfen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `check_empty` |
| **Symbol** | 🔍 |
| **Kategorie** | Steuerung |

Wahr, wenn (x, y) kollisionsfrei ist. Mit start_block/end_block verwenden, um die folgende(n) Aktion(en) zu steuern, GM-Stil

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Text | `self.x` | Zu prüfende X-Position (Ausdruck erlaubt, z. B. self.x + 32) |
| `y` | Text | `self.y` | Zu prüfende Y-Position (Ausdruck erlaubt, z. B. self.y + 32) |
| `relative` | Ja/Nein | Nein | X/Y als Versatz zur Position dieser Instanz statt als absolute Koordinaten behandeln; optional |
| `objects` | Auswahl | `solid` | Welche Instanzen als die Position belegend gelten; Auswahl: `solid`, `all` |

### Kommentar

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `comment` |
| **Symbol** | ⚠️ |
| **Kategorie** | Steuerung |

Ein Kommentar in der Aktionsliste (ohne Laufzeitwirkung)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `text` | Text | — | Freier Kommentartext; optional |

### Sonst

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `else_action` |
| **Symbol** | ⚡ |
| **Kategorie** | Steuerung |

Kennzeichnet den Sonst-Zweig einer Bedingung

*Parameter:* keine

### Block beenden

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `end_block` |
| **Symbol** | 📁 |
| **Kategorie** | Steuerung |

Einen Aktionsblock beenden

*Parameter:* keine

### Code ausführen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `execute_code` |
| **Symbol** | 📜 |
| **Kategorie** | Steuerung |

Einen eingebetteten Python-Codeblock ausführen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `code` | Code | — | Python-Quellcode, der auf der Instanz ausgewertet wird |

### Skript ausführen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `execute_script` |
| **Symbol** | 📜 |
| **Kategorie** | Steuerung |

Eines der Skript-Assets des Projekts ausführen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `script` | Skript | — | Name des auszuführenden Projektskripts |
| `arg0` | Text | — | Im Skript als argument0 verfügbar; optional |
| `arg1` | Text | — | Im Skript als argument1 verfügbar; optional |
| `arg2` | Text | — | Im Skript als argument2 verfügbar; optional |
| `arg3` | Text | — | Im Skript als argument3 verfügbar; optional |
| `arg4` | Text | — | Im Skript als argument4 verfügbar; optional |

### Ereignis verlassen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `exit_event` |
| **Symbol** | 🚪 |
| **Kategorie** | Steuerung |

Die Ausführung der restlichen Aktionen dieses Ereignisses stoppen

*Parameter:* keine

### Wenn Schieben möglich

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `if_can_push` |
| **Symbol** | 📦 |
| **Kategorie** | Steuerung |

Prüfen, ob eine Kiste/ein Objekt in die aktuelle Richtung geschoben werden kann (Sokoban-Stil)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `direction` | Auswahl | `facing` | Zu prüfende Schieberichtung; Auswahl: `facing` |
| `object_type` | Text | `box` | Typ des geschobenen Objekts |
| `then_action` | Auswahl | `push_and_move` | Aktion, wenn Schieben möglich ist; Auswahl: `push_and_move`, `none` |
| `else_action` | Auswahl | `stop_movement` | Aktion, wenn Schieben blockiert ist; Auswahl: `stop_movement`, `none` |

### Wenn Kollision

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `if_collision` |
| **Symbol** | ❓💥 |
| **Kategorie** | Steuerung |

Bedingung: wahr, wenn die Instanz am Versatz (x, y) kollidieren würde

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | Zu testender horizontaler Versatz |
| `y` | Zahl | `0` | Zu testender vertikaler Versatz |
| `object` | Text | `any` | „any“, „solid“ oder ein Objektname; Auswahl: `any`, `solid`; optional |
| `not_flag` | Ja/Nein | Nein | Das Ergebnis negieren; optional |

### Wenn Kollision bei

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `if_collision_at` |
| **Symbol** | 🎯 |
| **Kategorie** | Steuerung |

Auf Kollision an einer Position prüfen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Text | `self.x + 32` | Ausdruck der X-Position |
| `y` | Text | `self.y` | Ausdruck der Y-Position |
| `object_type` | Auswahl | `any` | Zu prüfender Objekttyp; Auswahl: `any`, `solid` |
| `then_actions` | Aktionsliste | — | Aktionen, wenn Kollision gefunden |
| `else_actions` | Aktionsliste | — | Aktionen, wenn keine Kollision |

### Wenn Bedingung

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `if_condition` |
| **Symbol** | ❓ |
| **Kategorie** | Steuerung |

Bedingte Prüfung mit Dann-/Sonst-Aktionen

*Parameter:* keine

### Wenn Objekt existiert

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `if_object_exists` |
| **Symbol** | ❓ |
| **Kategorie** | Steuerung |

Bedingung: wahr, wenn mindestens eine Instanz des Objekts existiert

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `object` | Objekt | — | Zu prüfender Objekttyp |
| `not_flag` | Ja/Nein | Nein | Das Ergebnis negieren (handeln, wenn das Objekt NICHT existiert); optional |

### Wiederholen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `repeat` |
| **Symbol** | 🔁 |
| **Kategorie** | Steuerung |

Nächste Aktion/nächsten Block N-mal wiederholen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `times` | Zahl | `10` | Anzahl der Wiederholungen |
| `actions` | Aktionsliste | — | Zu wiederholende Aktionen |

### Variable setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_variable` |
| **Symbol** | 📝 |
| **Kategorie** | Steuerung |

Eine Instanz- oder globale Variable setzen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `variable` | Text | — | Variablenname |
| `value` | Text | `0` | Wert (Zahl, Zeichenkette oder Ausdruck) |
| `scope` | Auswahl | `self` | Gültigkeitsbereich der Variable; Auswahl: `self`, `other`, `global` |
| `relative` | Ja/Nein | Nein | Zum aktuellen Wert addieren, statt ihn zu ersetzen |

### Block beginnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `start_block` |
| **Symbol** | 📂 |
| **Kategorie** | Steuerung |

Einen Aktionsblock beginnen (zur Gruppierung)

*Parameter:* keine

### Zufall testen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `test_chance` |
| **Symbol** | 🎲❓ |
| **Kategorie** | Steuerung |

Bedingung: wahr mit einer Wahrscheinlichkeit von 1 zu „sides“

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `sides` | Zahl | `6` | Eine 1-zu-N-Chance, wahr zu sein |

### Ausdruck testen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `test_expression` |
| **Symbol** | ❓ |
| **Kategorie** | Steuerung |

Testen, ob ein Ausdruck wahr ist

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `expression` | Text | — | Auszuwertender Ausdruck (wahr, wenn >= 0,5) |
| `then_actions` | Aktionsliste | — | Aktionen, wenn wahr |
| `else_actions` | Aktionsliste | — | Aktionen, wenn falsch |

### Frage stellen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `test_question` |
| **Symbol** | ❓💬 |
| **Kategorie** | Steuerung |

Bedingung: einen Ja/Nein-Dialog anzeigen; wahr, wenn der Benutzer mit Ja antwortet

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `question` | Text | `Continue?` | Dem Spieler angezeigte Frage |

### Variable testen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `test_variable` |
| **Symbol** | ❓ |
| **Kategorie** | Steuerung |

Den Wert einer Instanz- oder globalen Variable testen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `variable` | Text | — | Variablenname |
| `value` | Text | `0` | Zu vergleichender Wert |
| `scope` | Auswahl | `self` | Gültigkeitsbereich der Variable; Auswahl: `self`, `other`, `global` |
| `operation` | Auswahl | `equal` | Vergleichsoperator; Auswahl: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (8)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (25)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (16)
- [Particles](Full-Action-Reference-Particles_de) (8)
- [Réseau](Full-Action-Reference-Network-Actions_de) (15)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
