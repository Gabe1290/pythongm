# PyGameMaker IDE

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Home) | [Français](Home_fr) | [Deutsch](Home_de) | [Italiano](Home_it) | [Español](Home_es) | [Português](Home_pt) | [Slovenščina](Home_sl) | [Українська](Home_uk) | [Русский](Home_ru)

---

**Eine visuelle Spielentwicklungsumgebung inspiriert von GameMaker 7.0**

PyGameMaker ist eine Open-Source-IDE, die die 2D-Spieleerstellung durch visuelle blockbasierte Programmierung (Google Blockly) und ein Ereignis-Aktions-System zugänglich macht. Erstellen Sie Spiele ohne tiefe Programmierkenntnisse und exportieren Sie sie dann nach Windows, Linux, HTML5 oder mobile Plattformen.

---

## Wählen Sie Ihr Können

PyGameMaker verwendet **Voreinstellungen**, um zu steuern, welche Ereignisse und Aktionen verfügbar sind. Dies hilft Anfängern, sich auf wesentliche Funktionen zu konzentrieren, während erfahrene Benutzer auf das vollständige Toolset zugreifen können.

| Voreinstellung | Geeignet Für | Funktionen |
|----------------|--------------|------------|
| [**Anfänger**](Beginner-Preset_de) | Neu in der Spieleentwicklung | 4 Ereignisse, 17 Aktionen - Bewegung, Kollisionen, Punktzahl, Räume |
| [**Fortgeschritten**](Intermediate-Preset_de) | Einige Erfahrung | +4 Ereignisse, +12 Aktionen - Leben, Gesundheit, Sound, Alarme, Zeichnen |
| **Experte** | Erfahrene Benutzer | Alle 40+ Ereignisse und Aktionen verfügbar |

**Neue Benutzer:** Beginnen Sie mit der [Anfänger-Voreinstellung](Beginner-Preset_de), um die Grundlagen zu lernen, ohne überfordert zu werden.

Siehe den [Voreinstellungs-Leitfaden](Preset-Guide_de) für einen vollständigen Überblick über das Voreinstellungssystem.

---

## Funktionen auf einen Blick

| Funktion | Beschreibung |
|----------|--------------|
| **Visuelle Programmierung** | Drag-and-Drop-Codierung mit Google Blockly 12.x |
| **Ereignis-Aktions-System** | GameMaker 7.0 kompatible ereignisgesteuerte Logik |
| **Fähigkeitsbasierte Voreinstellungen** | Anfänger-, Fortgeschrittenen- und Experten-Funktionssets |
| **Multi-Plattform-Export** | Windows EXE, HTML5, Linux, Kivy (mobil/Desktop) |
| **Asset-Verwaltung** | Sprites, Sounds, Hintergründe, Schriften und Räume |
| **Mehrsprachige UI** | Englisch, Französisch, Deutsch, Italienisch, Spanisch, Portugiesisch, Slowenisch, Ukrainisch, Russisch |
| **Erweiterbar** | Plugin-System für benutzerdefinierte Ereignisse und Aktionen |

---

## Erste Schritte

### Systemanforderungen

- **Python** 3.10 oder höher
- **Betriebssystem:** Windows, Linux oder macOS

### Installation

1. Klonen Sie das Repository:
   ```bash
   git clone https://github.com/Gabe1290/pythongm.git
   cd pythongm
   ```

2. Erstellen Sie eine virtuelle Umgebung (empfohlen):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # oder
   venv\Scripts\activate     # Windows
   ```

3. Installieren Sie die Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
   ```

4. Starten Sie PyGameMaker:
   ```bash
   python main.py
   ```

---

## Grundkonzepte

### Objekte
Spielentitäten mit Sprites, Eigenschaften und Verhaltensweisen. Jedes Objekt kann mehrere Ereignisse mit zugehörigen Aktionen haben.

### Ereignisse
Auslöser, die Aktionen ausführen, wenn bestimmte Bedingungen eintreten:
- **Create** - Wenn eine Instanz erstellt wird
- **Step** - Jeden Frame (typischerweise 60 FPS)
- **Draw** - Benutzerdefinierte Renderphase
- **Destroy** - Wenn eine Instanz zerstört wird
- **Keyboard** - Taste gedrückt, losgelassen oder gehalten
- **Mouse** - Klicks, Bewegung, Betreten/Verlassen
- **Collision** - Wenn Instanzen sich berühren
- **Alarm** - Countdown-Timer (12 verfügbar)

Siehe die [Ereignis-Referenz](Event-Reference_de) für vollständige Dokumentation.

### Aktionen
Operationen, die ausgeführt werden, wenn Ereignisse ausgelöst werden. 40+ eingebaute Aktionen für:
- Bewegung und Physik
- Zeichnen und Sprites
- Punktzahl, Leben und Gesundheit
- Sound und Musik
- Instanz- und Raumverwaltung

Siehe die [Vollständige Aktions-Referenz](Full-Action-Reference_de) für vollständige Dokumentation.

### Räume
Spiellevel, in denen Sie Objektinstanzen platzieren, Hintergründe festlegen und den Spielbereich definieren.

---

## Visuelle Programmierung mit Blockly

PyGameMaker integriert Google Blockly für visuelle Programmierung. Blöcke sind in Kategorien organisiert:

- **Ereignisse** - Create, Step, Draw, Keyboard, Mouse
- **Bewegung** - Geschwindigkeit, Richtung, Position, Gravitation
- **Timing** - Alarme und Verzögerungen
- **Zeichnen** - Formen, Text, Sprites
- **Punktzahl/Leben/Gesundheit** - Spielzustandsverfolgung
- **Instanz** - Objekte erstellen und zerstören
- **Raum** - Navigation und Verwaltung
- **Werte** - Variablen und Ausdrücke
- **Sound** - Audiowiedergabe
- **Ausgabe** - Debug und Anzeige

---

## Export-Optionen

### Windows EXE
Eigenständige Windows-Executables mit PyInstaller. Kein Python auf dem Zielrechner erforderlich.

### HTML5
Einzeldatei-Webspiele, die in jedem modernen Browser laufen. Mit gzip komprimiert für schnelles Laden.

### Linux
Native Linux-Executables für Python 3.10+ Umgebungen.

### Kivy
Plattformübergreifende Apps für Mobil (iOS/Android) und Desktop über Buildozer.

---

## Projektstruktur

```
projektname/
├── project.json      # Projektkonfiguration
├── backgrounds/      # Hintergrundbilder und Metadaten
├── data/             # Benutzerdefinierte Datendateien
├── fonts/            # Schriftdefinitionen
├── objects/          # Objektdefinitionen (JSON)
├── rooms/            # Raumlayouts (JSON)
├── scripts/          # Benutzerdefinierte Skripte
├── sounds/           # Audiodateien und Metadaten
├── sprites/          # Sprite-Bilder und Metadaten
└── thumbnails/       # Generierte Asset-Miniaturansichten
```

---

## Wiki-Inhalt

### Voreinstellungen & Referenz
- [Voreinstellungs-Leitfaden](Preset-Guide_de) - Überblick über das Voreinstellungssystem
- [Anfänger-Voreinstellung](Beginner-Preset_de) - Wesentliche Funktionen für neue Benutzer
- [Fortgeschrittenen-Voreinstellung](Intermediate-Preset_de) - Zusätzliche Funktionen
- [Ereignis-Referenz](Event-Reference_de) - Vollständige Ereignisdokumentation
- [Vollständige Aktions-Referenz](Full-Action-Reference_de) - Vollständige Aktionsdokumentation

### Tutorials & Anleitungen
- [**Tutorials**](Tutorials_de) - Alle Tutorials an einem Ort
- [Erste Schritte](Erste_Schritte_de) - Erste Schritte mit PyGameMaker
- [Ihr Erstes Spiel](Erstes_Spiel_de) - Tutorial-Durchgang
- [Pong Tutorial](Tutorial-Pong_de) - Erstellen Sie ein klassisches Zwei-Spieler Pong-Spiel
- [Breakout Tutorial](Tutorial-Breakout_de) - Erstellen Sie ein klassisches Casse-Briques Spiel
- [Sokoban Tutorial](Tutorial-Sokoban_de) - Erstellen Sie ein Kisten-Schiebe-Puzzlespiel
- [Einführung in die Spieleentwicklung](Getting-Started-Breakout_de) - Umfassendes Anfänger-Tutorial
- [Objekt-Editor](Objekt_Editor_de) - Arbeiten mit Spielobjekten
- [Raum-Editor](Raum_Editor_de) - Level gestalten
- [Ereignisse und Aktionen](Events_und_Aktionen_de) - Spiellogik-Referenz
- [Visuelle Programmierung](Visuelle_Programmierung_de) - Blockly-Blöcke verwenden
- [Spiele Exportieren](Spiele_Exportieren_de) - Für verschiedene Plattformen bauen
- [FAQ](FAQ_de) - Häufig gestellte Fragen

---

## Beitragen

Beiträge sind willkommen! Siehe unsere Beitragsrichtlinien für:
- Fehlerberichte und Funktionsanfragen
- Code-Beiträge
- Übersetzungen
- Dokumentationsverbesserungen

---

## Lizenz

PyGameMaker ist unter der **GNU General Public License v3 (GPLv3)** lizenziert.

Copyright (c) 2024-2025 Gabriel Thullen

---

## Links

- [GitHub Repository](https://github.com/Gabe1290/pythongm)
- [Issue-Tracker](https://github.com/Gabe1290/pythongm/issues)
- [Releases](https://github.com/Gabe1290/pythongm/releases)
