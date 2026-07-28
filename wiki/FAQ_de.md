# Häufig gestellte Fragen (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

[Zurück zur Startseite](Home_de)

Antworten auf häufige Fragen zu pyGM.

## Allgemeine Fragen

### Was ist pyGM?
pyGM ist ein visueller Spieleentwicklungs-Editor für Python. Er ermöglicht das Erstellen von 2D-Spielen ohne umfangreiche Programmierkenntnisse.

### Ist pyGM kostenlos?
Ja, pyGM ist Open Source und vollständig kostenlos.

### Welche Programmiersprache wird verwendet?
pyGM basiert auf Python. Sie können visuelle Programmierung nutzen oder direkt Python-Code schreiben.

### Für welche Plattformen kann ich entwickeln?
- Windows
- macOS
- Linux
- Web (HTML5)
- Mobil (Kivy/Android)

## Installation

### Wie installiere ich pyGM?
```bash
pip install pygm
```

### Welche Python-Version benötige ich?
Python 3.10 oder höher.

### pyGM startet nicht. Was tun?
1. Prüfen Sie die Python-Version
2. Installieren Sie die Abhängigkeiten neu
3. Starten Sie von der Kommandozeile für Fehlermeldungen

## Entwicklung

### Wie erstelle ich ein neues Projekt?
Starten Sie pyGM und wählen Sie „Neues Projekt" oder verwenden Sie Datei > Neu.

### Wie füge ich Sprites hinzu?
1. Rechtsklick auf „Sprites" im Ressourcenbaum
2. Wählen Sie „Neues Sprite"
3. Importieren Sie ein Bild oder erstellen Sie eines

### Wie erstelle ich Animationen?
1. Öffnen Sie ein Sprite
2. Fügen Sie mehrere Frames hinzu
3. Stellen Sie die Animationsgeschwindigkeit ein

### Wie programmiere ich Objekt-Verhalten?
1. Öffnen Sie ein Objekt
2. Fügen Sie Events hinzu (z. B. Create, Step)
3. Fügen Sie Aktionen zu Events hinzu
4. Oder nutzen Sie den visuellen Blockly-Editor

## Ressourcen

### Welche Bildformate werden unterstützt?
- PNG (empfohlen)
- JPG
- GIF
- BMP

### Welche Audioformate werden unterstützt?
- WAV
- MP3
- OGG

### Wie optimiere ich meine Ressourcen?
- Verwenden Sie angemessene Bildgrößen
- Komprimieren Sie Audio-Dateien
- Entfernen Sie ungenutzte Ressourcen

## Gameplay

### Wie implementiere ich Kollisionserkennung?
1. Erstellen Sie ein Kollisions-Event im Objekt
2. Wählen Sie das andere Objekt
3. Fügen Sie Aktionen für die Reaktion hinzu

### Wie erstelle ich mehrere Levels?
1. Erstellen Sie mehrere Räume
2. Verwenden Sie die Aktion „Gehe zu Raum"
3. Oder „Nächster Raum"

### Wie speichere ich Spielstände?
Verwenden Sie die eingebauten Speicherfunktionen:
- `save_game()`: Spiel speichern
- `load_game()`: Spiel laden

## Export

### Wie exportiere ich mein Spiel?
1. Gehen Sie zu Datei > Projekt exportieren…
2. Wählen Sie die Zielplattform
3. Konfigurieren Sie Optionen
4. Klicken Sie auf „Exportieren"

### Warum ist die exportierte Datei so groß?
- Die Python-Runtime ist enthalten
- Alle Ressourcen sind eingebettet
- Tipp: Ressourcen optimieren

### Kann ich für Mobilgeräte exportieren?
Ja — über den Kivy/Android-Export. Der HTML5-Export funktioniert außerdem in mobilen Browsern.

## Fehlerbehebung

### Mein Spiel ist langsam
- Reduzieren Sie den Step-Event-Code
- Optimieren Sie die Sprite-Größen
- Vermeiden Sie zu viele Instanzen

### Sprites werden nicht angezeigt
- Prüfen Sie den Sprite-Pfad
- Stellen Sie sicher, dass Sichtbar=true
- Überprüfen Sie die Zeichenreihenfolge (Tiefe)

### Kollisionen funktionieren nicht
- Prüfen Sie die Kollisionsmasken
- Stellen Sie sicher, dass Objekte solid sind (falls nötig)
- Überprüfen Sie die Event-Konfiguration

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
