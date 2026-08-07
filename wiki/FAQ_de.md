# Häufig gestellte Fragen (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

> [Zurück zur Startseite](Home_de)

---

## Allgemeine Fragen

### Was ist PyGameMaker?

PyGameMaker ist eine quelloffene Spieleentwicklungs-IDE, inspiriert von GameMaker 7.0. Damit können Sie 2D-Spiele mit visueller Programmierung (Google Blockly) oder einem Ereignis-Aktions-System erstellen, ohne Code schreiben zu müssen.

### Ist PyGameMaker kostenlos?

Ja! PyGameMaker ist vollständig kostenlos und quelloffen — der Quellcode steht unter der MIT-Lizenz, die Dokumentation unter CC BY 4.0.

### Für welche Plattformen kann ich exportieren?

- Windows (eigenständige .exe)
- HTML5 (Webbrowser)
- Linux (native Executable)
- Mobil (iOS/Android über Kivy)

### Brauche ich Programmiererfahrung?

Nein! PyGameMaker ist für Einsteiger konzipiert. Sie können Spiele erstellen mit:
- Drag-and-Drop-Blockly-Blöcken
- Point-and-Click-Ereignis/Aktions-System
- Ohne jeglichen Code

### Ist es mit GameMaker-Dateien kompatibel?

PyGameMaker ist von GameMaker 7.0 inspiriert, verwendet aber sein eigenes Projektformat. Sie können GameMaker-Dateien nicht direkt importieren, aber die Konzepte und der Arbeitsablauf sind ähnlich.

---

## Installation

### Welche Systemanforderungen gibt es?

- Python 3.10 oder höher
- Windows, Linux oder macOS
- Mindestens 4 GB RAM (8 GB empfohlen)
- ~500 MB Festplattenspeicher

### Wie installiere ich PyGameMaker?

Siehe [[Erste_Schritte_de]] für eine ausführliche Installationsanleitung. Kurzfassung:

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
python -m venv venv
source venv/bin/activate  # oder venv\Scripts\activate unter Windows
pip install -r requirements.txt
python main.py
```

### Python wird nicht erkannt / nicht gefunden

Stellen Sie sicher, dass Python installiert und zum System-PATH hinzugefügt ist. Prüfen Sie dies mit:

```bash
python --version
```

Falls das fehlschlägt, installieren Sie Python neu und aktivieren Sie „Add Python to PATH" während der Installation.

### Ich erhalte Importfehler beim Start

Versuchen Sie, die Abhängigkeiten neu zu installieren:

```bash
pip install -r requirements.txt --force-reinstall
```

---

## Projekte

### Wo werden meine Projekte gespeichert?

Projekte werden in Ordnern gespeichert, die Sie selbst wählen. Jedes Projekt enthält:
- `project.json` - Die Hauptprojektdatei
- Ordner für Sprites, Sounds, Objekte, Räume usw.

### Kann ich mehrere Projekte gleichzeitig geöffnet haben?

Aktuell öffnet PyGameMaker jeweils ein Projekt. Verwenden Sie **Datei > Projekt öffnen**, um zwischen Projekten zu wechseln.

### Wie sichere ich mein Projekt?

Kopieren Sie einfach den gesamten Projektordner. Alle Assets und Einstellungen sind darin enthalten. Ziehen Sie auch git zur Versionskontrolle in Betracht:

```bash
cd mein_projekt
git init
git add .
git commit -m "Erste Sicherung"
```

### Mein Projekt lässt sich nicht öffnen / ist beschädigt

Versuchen Sie Folgendes:
1. Prüfen Sie, ob `project.json` existiert und nicht leer ist
2. Öffnen Sie `project.json` in einem Texteditor, um JSON-Fehler zu finden
3. Stellen Sie es aus einer Sicherung wieder her, falls vorhanden
4. Prüfen Sie die Konsolenausgabe auf konkrete Fehlermeldungen

---

## Objekte und Ereignisse

### Was ist der Unterschied zwischen einem Objekt und einer Instanz?

- **Objekt**: Eine Vorlage/Schablone, die Verhalten definiert
- **Instanz**: Eine konkrete Kopie eines Objekts, die in einem Room platziert ist

Zum Beispiel ist `obj_gegner` ein Objekt. Werden 5 Gegner in einem Room platziert, entstehen 5 Instanzen von `obj_gegner`.

### Warum löst mein Ereignis nicht aus?

Häufige Ursachen:
1. **Falscher Ereignistyp**: Stellen Sie sicher, dass Sie das richtige Ereignis verwenden (z. B. „Key Press" statt „Keyboard")
2. **Keine Instanzen**: Das Objekt muss Instanzen im Room haben
3. **Objekt nicht sichtbar**: Prüfen Sie die Eigenschaft „Sichtbar"
4. **Ausführungsreihenfolge**: Manche Ereignisse laufen vor anderen

### Wie lasse ich Objekte interagieren?

Verwenden Sie Kollisions-Ereignisse:
1. Öffnen Sie das Objekt, das die Kollision erkennen soll
2. Fügen Sie das Ereignis **Collision with [anderes_objekt]** hinzu
3. Fügen Sie Aktionen für die Reaktion hinzu

### Was ist der Unterschied zwischen „Keyboard" und „Key Press"?

- **Keyboard [Taste]**: Löst bei jedem Frame aus, solange die Taste gehalten wird
- **Key Press [Taste]**: Löst einmal aus, wenn die Taste zuerst gedrückt wird
- **Key Release [Taste]**: Löst einmal aus, wenn die Taste losgelassen wird

---

## Rooms

### Welcher Room lädt zuerst?

Der erste Room im Ressourcenbaum (oben in der Liste) lädt beim Spielstart. Ziehen Sie Rooms, um sie neu anzuordnen.

### Wie wechsle ich zwischen Rooms?

Verwenden Sie Room-Aktionen:
- **Next Room**: Zum nächsten Room in der Reihenfolge gehen
- **Previous Room**: Zum vorherigen Room gehen
- **Go to Room**: Zu einem bestimmten Room springen

### Objekte verschwinden beim Room-Wechsel

Objekte werden beim Verlassen eines Rooms zerstört, außer sie sind in ihren Eigenschaften als **Persistent** markiert.

### Mein Room ist auf dem Bildschirm zu groß/klein

Die Fenstergröße des Spiels entspricht den Abmessungen des ersten Rooms. Sie können:
- Die Room-Größe an die gewünschte Fenstergröße anpassen
- Views verwenden, um nur einen Teil des Rooms anzuzeigen

---

## Grafik und Sprites

### Welche Bildformate werden unterstützt?

- PNG (empfohlen, unterstützt Transparenz)
- JPEG/JPG
- BMP
- GIF (nur das erste Bild)

### Mein Sprite erscheint an der falschen Position

Prüfen Sie die Einstellung **Ursprung** im Sprite-Editor. Der Ursprung ist der Ankerpunkt für die Positionierung. Übliche Einstellungen:
- Oben links (0, 0): Standard
- Mitte: Gut für rotierende Objekte
- Unten-Mitte: Gut für Charaktere

### Wie animiere ich ein Sprite?

1. Erstellen Sie ein Sprite mit mehreren Bildern (horizontaler Streifen)
2. Legen Sie **Anzahl der Bilder** in den Sprite-Eigenschaften fest
3. Passen Sie die **Animationsgeschwindigkeit** an (Bilder pro Sekunde)

### Sprites sind unscharf

Das passiert beim Skalieren von Sprites. Bei Pixel-Art deaktivieren Sie die Interpolation/Glättung in den Spieleinstellungen, falls verfügbar.

---

## Sound und Musik

### Welche Audioformate werden unterstützt?

- WAV (unkomprimiert)
- OGG (empfohlen für Musik)
- MP3

### Sound spielt nicht ab

Prüfen Sie:
1. Ob die Audiodatei im Sounds-Ordner existiert
2. Ob das Dateiformat unterstützt wird
3. Ob Sie den korrekten Sound-Namen in den Aktionen verwenden
4. Der Browser könnte eine Benutzerinteraktion erfordern (bei HTML5)

### Wie spiele ich Hintergrundmusik in einer Schleife?

Verwenden Sie die Aktion **Play Music** mit aktivierter Loop-Option, oder **Play Sound** mit dem Loop-Parameter auf „wahr" gesetzt.

---

## Exportieren

### Mein exportiertes Spiel funktioniert nicht

Häufige Probleme:
- **Windows**: Fehlende DLLs — stellen Sie sicher, dass der gesamte Ausgabeordner enthalten ist
- **HTML5**: Der Browser blockiert lokale Dateien — auf einem Server hosten
- **Fehlende Assets**: Prüfen Sie, dass alle Dateien enthalten sind

### Die exportierte Datei ist riesig

Die Spielgröße umfasst Python und alle Bibliotheken. So verkleinern Sie sie:
- Ungenutzte Assets entfernen
- Bilder und Audio komprimieren
- Passende Formate verwenden (OGG statt WAV)
- UPX-Komprimierung für Windows-Builds aktivieren

### Kann ich mit PyGameMaker erstellte Spiele verkaufen?

Ja! Die von Ihnen erstellten Spiele gehören vollständig Ihnen und dürfen verkauft werden. Der Quellcode von PyGameMaker steht unter der freizügigen MIT-Lizenz, Sie können ihn also frei in kommerziellen Projekten verwenden — und anders als bei Copyleft-Lizenzen sind Sie nicht verpflichtet, Ihre eigenen Änderungen quelloffen zu machen.

---

## Blockly / Visuelle Programmierung

### Wo finde ich den Blockly-Editor?

1. Öffnen Sie ein Objekt
2. Klicken Sie auf den **Blockly**-Tab im Objekt-Editor
3. Der visuelle Programmier-Arbeitsbereich erscheint

### Wie wechsle ich zwischen Blockly und Ereignissen?

Beide Systeme arbeiten am selben Objekt. Der Blockly-Tab und der Ereignisse-Tab zeigen unterschiedliche Ansichten derselben Logik. Änderungen in einem wirken sich auf das andere aus.

### Meine Blockly-Blöcke sind verschwunden

Prüfen Sie:
1. Ob Sie das richtige Objekt ansehen
2. Scrollen Sie im Arbeitsbereich (Blöcke könnten außerhalb des sichtbaren Bereichs sein)
3. Prüfen Sie die Zoomstufe

---

## Leistung

### Mein Spiel läuft langsam

Tipps für bessere Leistung:
1. Reduzieren Sie die Anzahl der Instanzen
2. Vermeiden Sie aufwendige Berechnungen in Step-Ereignissen
3. Verwenden Sie Alarme statt Frames zu zählen
4. Optimieren Sie die Sprite-Größen
5. Zerstören Sie Instanzen, die den Room verlassen

### Das Step-Ereignis läuft zu häufig

Das Step-Ereignis läuft bei jedem Frame (standardmäßig 60-mal pro Sekunde). Verwenden Sie:
- Alarme für verzögerte Aktionen
- Bedingungen, die vor aufwendigen Operationen geprüft werden
- Eine niedrigere Room-Geschwindigkeit, falls angemessen

---

## Hilfe erhalten

### Wo kann ich Fehler melden?

Melden Sie Fehler auf der Seite [GitHub Issues](https://github.com/Gabe1290/pythongm/issues). Geben Sie an:
- Was Sie erwartet haben
- Was tatsächlich passiert ist
- Schritte zur Reproduktion
- Ihr Betriebssystem und Ihre Python-Version

### Wo kann ich mehr erfahren?

- [[Erste_Schritte_de]] - Installation und Grundlagen
- [[Erstes_Spiel_de]] - Schritt-für-Schritt-Tutorial
- [[Events_und_Aktionen_de]] - Vollständige Referenz
- [[Visuelle_Programmierung_de]] - Blockly-Leitfaden
