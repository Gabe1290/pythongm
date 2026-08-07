# Preset-Leitfaden

*[Deutsch](Preset-Guide_de) | [Zurück zur Startseite](Home_de)*

PyGameMaker bietet verschiedene Presets, die steuern, welche Ereignisse
und Aktionen verfügbar sind — **sowohl** im visuellen Blockly-Blockbild
als auch im strukturierten Ereignisse/Aktionen-Panel ("Add Event"/"Add
Action"), das jedes Tutorial in diesem Wiki verwendet. Dies hilft
Anfängern, sich auf wesentliche Funktionen zu konzentrieren, während
erfahrene Benutzer auf das vollständige Toolset zugreifen können.

Das Preset eines Projekts wird auf zwei Arten festgelegt:
**`Preferences > IDE Edition`** legt den Standard für *neue* Projekte
fest (bestehende Projekte werden durch einen Editionswechsel nie
verändert), und **`Tools > Configure Action Blocks...`** ändert das
Preset des *aktuell geöffneten* Projekts jederzeit. Die Standard-Edition
der IDE ist Anfänger, daher starten neue Projekte einer Neuinstallation
bereits auf dem Anfänger-Preset.

## Wählen Sie Ihr Können

| IDE-Edition | Geeignet Für | Verwendetes Preset |
|--------|----------|----------|
| **Anfänger** (Standard) | Neue Benutzer | [Anfänger-Preset](Beginner-Preset_de) — grundlegende Bewegung, Kollisionen, Punktestand, Rooms |
| **Fortgeschritten** | Etwas Erfahrung | [Fortgeschrittenen-Preset](Intermediate-Preset_de) — + Leben, Gesundheit, Sound, Alarme, Gitterbewegung |
| **Entwicklung** | Erfahrene Benutzer | Das `full`-Preset — jedes Ereignis und jede Aktion verfügbar |

Beachten Sie, dass die Bezeichnungen nicht 1:1 übereinstimmen: Die
Edition "Fortgeschritten" verwendet das `intermediate`-Preset (es gibt
kein separates "fortgeschrittenes" Preset) — die genauen, stets
aktuellen Ereignis- und Aktionszahlen jedes Presets finden Sie auf den
Seiten [Anfänger-Preset](Beginner-Preset_de)/[Fortgeschrittenen-Preset](Intermediate-Preset_de).

---

## Preset-Dokumentation

### Presets
| Seite | Beschreibung |
|-------|--------------|
| [Anfänger-Preset](Beginner-Preset_de) | Wesentliche Funktionen — genaue Zahlen auf dieser Seite |
| [Fortgeschrittenen-Preset](Intermediate-Preset_de) | Fügt Leben, Gesundheit, Sound, Alarme, Gitterbewegung hinzu — genaue Zahlen auf dieser Seite |

### Referenz
| Seite | Beschreibung |
|-------|--------------|
| [Ereignis-Referenz](Event-Reference_de) | Vollständige Liste aller Ereignisse |
| [Vollständige Aktions-Referenz](Full-Action-Reference_de) | Vollständige Liste aller Aktionen |

---

## Schnellstart-Beispiel

Hier ist ein einfaches Münzsammelspiel mit nur Anfänger-Funktionen:

### 1. Objekte Erstellen
- `obj_player` - Der steuerbare Charakter
- `obj_coin` - Sammelbare Gegenstände
- `obj_wall` - Feste Hindernisse

### 2. Ereignisse zum Spieler Hinzufügen

**Keyboard (Arrow Keys):**
```
Left Arrow  → Set Horizontal Speed: -4
Right Arrow → Set Horizontal Speed: 4
Up Arrow    → Set Vertical Speed: -4
Down Arrow  → Set Vertical Speed: 4
```

**Collision with obj_coin:**
```
Add Score: 10
Destroy Instance: other
```

**Collision with obj_wall:**
```
Stop Movement
```

### 3. Einen Room Erstellen
- Platzieren Sie den Spieler
- Fügen Sie einige Münzen hinzu
- Fügen Sie Wände an den Rändern hinzu

### 4. Das Spiel Starten!
Drücken Sie den Play-Button, um Ihr Spiel zu testen.

---

## Tipps für Erfolg

1. **Einfach Anfangen** - Verwenden Sie zuerst das Anfänger-Preset
2. **Oft Testen** - Führen Sie Ihr Spiel häufig aus, um Probleme zu erkennen
3. **Eins nach dem Anderen** - Fügen Sie Funktionen schrittweise hinzu
4. **Kollisionen Nutzen** - Die meisten Spielmechaniken beinhalten Kollisionsereignisse
5. **Dokumentation Lesen** - Schauen Sie in die Referenzseiten, wenn Sie nicht weiterkommen

---

## Siehe Auch

- [Startseite](Home_de) - Wiki-Hauptseite
- [Erste Schritte](Erste_Schritte_de) - Installation und Einrichtung
- [Ereignisse und Aktionen](Events_und_Aktionen_de) - Grundkonzepte
- [Ihr Erstes Spiel](Erstes_Spiel_de) - Tutorial
- [Breakout Tutorial](Tutorial-Breakout_de) - Erstellen Sie ein klassisches Breakout-Spiel
- [Einführung in die Spieleentwicklung](Getting-Started-Breakout_de) - Umfassendes Anfänger-Tutorial
