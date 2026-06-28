# Haufig gestellte Fragen (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

[Zuruck zur Startseite](Home_de)

Antworten auf haufige Fragen zu pyGM.

## Allgemeine Fragen

### Was ist pyGM?
pyGM ist ein visueller Spieleentwicklungs-Editor fur Python. Er ermoglicht das Erstellen von 2D-Spielen ohne umfangreiche Programmierkenntnisse.

### Ist pyGM kostenlos?
Ja, pyGM ist Open Source und vollstandig kostenlos.

### Welche Programmiersprache wird verwendet?
pyGM basiert auf Python. Sie konnen visuelle Programmierung nutzen oder direkt Python-Code schreiben.

### Fur welche Plattformen kann ich entwickeln?
- Windows
- macOS
- Linux
- Web (HTML5)

## Installation

### Wie installiere ich pyGM?
```bash
pip install pygm
```

### Welche Python-Version benotige ich?
Python 3.8 oder hoher.

### pyGM startet nicht. Was tun?
1. Prufen Sie die Python-Version
2. Installieren Sie Abhangigkeiten neu
3. Starten Sie von der Kommandozeile fur Fehlermeldungen

## Entwicklung

### Wie erstelle ich ein neues Projekt?
Starten Sie pyGM und wahlen Sie "Neues Projekt" oder verwenden Sie Datei > Neu.

### Wie fuege ich Sprites hinzu?
1. Rechtsklick auf "Sprites" im Ressourcenbaum
2. Wahlen Sie "Neues Sprite"
3. Importieren Sie ein Bild oder erstellen Sie eines

### Wie erstelle ich Animationen?
1. Offnen Sie ein Sprite
2. Fugen Sie mehrere Frames hinzu
3. Stellen Sie die Animationsgeschwindigkeit ein

### Wie programmiere ich Objekt-Verhalten?
1. Offnen Sie ein Objekt
2. Fugen Sie Events hinzu (z.B. Create, Step)
3. Fugen Sie Aktionen zu Events hinzu
4. Oder nutzen Sie den visuellen Blockly-Editor

## Ressourcen

### Welche Bildformate werden unterstutzt?
- PNG (empfohlen)
- JPG
- GIF
- BMP

### Welche Audioformate werden unterstutzt?
- WAV
- MP3
- OGG

### Wie optimiere ich meine Ressourcen?
- Verwenden Sie angemessene Bildgrossen
- Komprimieren Sie Audio-Dateien
- Entfernen Sie ungenutzte Ressourcen

## Gameplay

### Wie implementiere ich Kollisionserkennung?
1. Erstellen Sie ein Kollisions-Event im Objekt
2. Wahlen Sie das andere Objekt
3. Fugen Sie Aktionen fur die Reaktion hinzu

### Wie erstelle ich mehrere Levels?
1. Erstellen Sie mehrere Raume
2. Verwenden Sie die Aktion "Gehe zu Raum"
3. Oder "Gehe zu nachstem Raum"

### Wie speichere ich Spielstande?
Verwenden Sie die eingebauten Speicherfunktionen:
- `save_game()`: Spiel speichern
- `load_game()`: Spiel laden

## Export

### Wie exportiere ich mein Spiel?
1. Gehen Sie zu Datei > Exportieren
2. Wahlen Sie die Zielplattform
3. Konfigurieren Sie Optionen
4. Klicken Sie auf "Exportieren"

### Warum ist die exportierte Datei so gross?
- Python-Runtime ist enthalten
- Alle Ressourcen eingebettet
- Tipp: Ressourcen optimieren

### Kann ich fur Mobilgerate exportieren?
Derzeit nicht direkt unterstutzt. Web-Export funktioniert auf mobilen Browsern.

## Fehlerbehebung

### Mein Spiel ist langsam
- Reduzieren Sie Step-Event-Code
- Optimieren Sie Sprite-Grossen
- Vermeiden Sie zu viele Instanzen

### Sprites werden nicht angezeigt
- Prufen Sie den Sprite-Pfad
- Stellen Sie sicher, dass Sichtbar=true
- Uberprufen Sie die Zeichenreihenfolge (Tiefe)

### Kollisionen funktionieren nicht
- Prufen Sie Kollisionsmasken
- Stellen Sie sicher, dass Objekte solid sind (falls notig)
- Uberprufen Sie Event-Konfiguration

## Community

### Wo finde ich Hilfe?
- Offizielle Dokumentation
- GitHub Issues
- Community-Foren

### Wie kann ich beitragen?
- Bugs auf GitHub melden
- Pull Requests einreichen
- Dokumentation verbessern

## Siehe auch

- [Erste Schritte](Erste_Schritte_de)
- [Ihr erstes Spiel erstellen](Erstes_Spiel_de)
- [Events und Aktionen](Events_und_Aktionen_de)
