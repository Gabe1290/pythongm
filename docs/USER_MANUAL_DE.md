# PyGameMaker IDE Benutzerhandbuch

**Version 1.0.0-rc.6**
**Eine von GameMaker inspirierte visuelle Spielentwicklungs-IDE zum Erstellen von 2D-Spielen mit Python**

---

## Inhaltsverzeichnis

1. [Einfuehrung](#1-einfuehrung)
2. [Installation und Einrichtung](#2-installation-und-einrichtung)
3. [IDE-Uebersicht](#3-ide-uebersicht)
4. [Arbeiten mit Projekten](#4-arbeiten-mit-projekten)
5. [Sprites](#5-sprites)
6. [Sounds](#6-sounds)
7. [Hintergruende](#7-hintergruende)
8. [Objekte](#8-objekte)
9. [Raeume](#9-raeume)
10. [Ereignis-Referenz](#10-ereignis-referenz)
11. [Aktions-Referenz](#11-aktions-referenz)
12. [Testen und Ausfuehren von Spielen](#12-testen-und-ausfuehren-von-spielen)
13. [Spiele exportieren](#13-spiele-exportieren)
14. [Blockly Visuelle Programmierung](#14-blockly-visuelle-programmierung)
15. [Thymio Roboter-Unterstuetzung](#15-thymio-roboter-unterstuetzung)
16. [Einstellungen und Praeferenzen](#16-einstellungen-und-praeferenzen)
17. [Tastaturkuerzel](#17-tastaturkuerzel)
18. [Anleitungen](#18-anleitungen)
19. [Fehlerbehebung](#19-fehlerbehebung)

---

## 1. Einfuehrung

PyGameMaker ist eine paedagogische Spielentwicklungs-IDE, inspiriert von GameMaker. Sie ermoeglicht es, 2D-Spiele visuell mit einem Drag-and-Drop-Ereignis/Aktions-System zu erstellen, ohne Code schreiben zu muessen. Sie wurde mit zwei Zielen entwickelt:

- **Spielentwicklung lehren** durch eine intuitive visuelle Oberflaeche
- **Python-Programmierung lehren** durch den offenen Quellcode der IDE

PyGameMaker verwendet PySide6 (Qt) fuer die IDE-Oberflaeche und Pygame fuer die Spiel-Laufzeitumgebung. Spiele koennen als eigenstaendige ausfuehrbare Dateien, mobile Apps oder HTML5-Webspiele exportiert werden.

### Hauptmerkmale

- Visuelle Ereignis/Aktions-Programmierung (80+ eingebaute Aktionen)
- Sprite-Editor mit Animationsunterstuetzung
- Raum-Editor mit Instanzplatzierung, Kachelebenen und Hintergrund-Scrolling
- Echtzeit-Spielvorschau mit F5
- Export nach Windows EXE, Mobil (Android/iOS via Kivy), HTML5 und Thymio-Roboter
- Google Blockly-Integration fuer visuelle Code-Bloecke
- Thymio Lernroboter-Simulator
- Mehrsprachige Oberflaeche (8+ Sprachen)
- Dunkles und helles Design

---

## 2. Installation und Einrichtung

### Voraussetzungen

- Python 3.10 oder hoeher
- PySide6
- Pygame
- Pillow (PIL)

### Abhaengigkeiten installieren

```bash
pip install PySide6 pygame Pillow
```

### Optionale Abhaengigkeiten

Fuer Export-Funktionen:

```bash
pip install pyinstaller    # For EXE export
pip install kivy           # For mobile export
pip install buildozer      # For Android builds
pip install jinja2         # For code generation templates
```

### Die IDE starten

```bash
python main.py
```

Das IDE-Fenster oeffnet sich mit Standardabmessungen von 1400x900 Pixeln. Fensterposition und -groesse werden zwischen Sitzungen gespeichert.

---

## 3. IDE-Uebersicht

### Fensterlayout

Die IDE verwendet ein Drei-Panel-Layout:

```
+-------------------+---------------------------+------------------+
|   Asset-Baum      |      Editor-Bereich       | Eigenschaften    |
|   (Linkes Panel)  |      (Mittleres Panel)    | (Rechtes Panel)  |
|                   |                           |                  |
|   - Sprites       |   Registerkarteneditor    |   Kontext-       |
|   - Sounds        |   für Sprites, Objekte    |   sensitive      |
|   - Hintergründe  |   und Räume               |   Eigenschaften  |
|   - Objekte       |                           |                  |
|   - Räume         |                           |                  |
|   - Skripte       |                           |                  |
|   - Schriftarten  |                           |                  |
+-------------------+---------------------------+------------------+
|                       Statusleiste                               |
+------------------------------------------------------------------+
```

- **Linkes Panel (Asset-Baum):** Zeigt alle Projekt-Assets nach Typ geordnet an. Doppelklicken Sie auf ein Asset, um es im Editor zu oeffnen.
- **Mittleres Panel (Editor-Bereich):** Arbeitsbereich mit Registerkarten, in dem Sie Sprites, Objekte und Raeume bearbeiten. Standardmaessig wird eine Willkommens-Registerkarte angezeigt.
- **Rechtes Panel (Eigenschaften):** Zeigt kontextsensitive Eigenschaften fuer den aktuell aktiven Editor. Kann eingeklappt werden.
- **Statusleiste:** Zeigt den aktuellen Betriebsstatus und den Projektnamen an.

### Menueleiste

#### Datei-Menue

| Befehl | Tastaturkuerzel | Beschreibung |
|--------|-----------------|--------------|
| Neues Projekt... | Ctrl+N | Ein neues Projekt erstellen |
| Projekt oeffnen... | Ctrl+O | Ein bestehendes Projekt oeffnen |
| Projekt speichern | Ctrl+S | Das aktuelle Projekt speichern |
| Projekt speichern als... | Ctrl+Shift+S | An einem neuen Ort speichern |
| Letzte Projekte | | Untermenue mit bis zu 10 letzten Projekten |
| Als HTML5 exportieren... | | Spiel als einzelne HTML-Datei exportieren |
| Als Zip exportieren... | | Projekt als ZIP-Archiv verpacken |
| Nach Kivy exportieren... | | Fuer mobile Bereitstellung exportieren |
| Projekt exportieren... | Ctrl+E | Den Export-Dialog oeffnen |
| Zip-Projekt oeffnen... | | Ein ZIP-gepacktes Projekt oeffnen |
| Auto-Speichern als Zip | | Auto-Speichern als ZIP umschalten |
| Auto-Speichern aktivieren | | Automatisches Projektspeichern umschalten |
| Auto-Speicher-Einstellungen... | | Auto-Speicher-Intervall konfigurieren |
| Projekteinstellungen... | | Projektkonfiguration oeffnen |
| Beenden | Ctrl+Q | Die IDE schliessen |

#### Bearbeiten-Menue

| Befehl | Tastaturkuerzel | Beschreibung |
|--------|-----------------|--------------|
| Rueckgaengig | Ctrl+Z | Letzte Aktion rueckgaengig machen |
| Wiederherstellen | Ctrl+Y | Letzte rueckgaengig gemachte Aktion wiederherstellen |
| Ausschneiden | Ctrl+X | Auswahl ausschneiden |
| Kopieren | Ctrl+C | Auswahl kopieren |
| Einfuegen | Ctrl+V | Aus Zwischenablage einfuegen |
| Duplizieren | Ctrl+D | Ausgewaehlte Elemente duplizieren |
| Suchen... | Ctrl+F | Suchdialog oeffnen |
| Suchen und Ersetzen... | Ctrl+H | Suchen-und-Ersetzen-Dialog oeffnen |

#### Assets-Menue

| Befehl | Beschreibung |
|--------|--------------|
| Sprite importieren... | Sprite-Bilder importieren (PNG, JPG, BMP, GIF) |
| Sound importieren... | Audiodateien importieren |
| Hintergrund importieren... | Hintergrundbilder importieren |
| Objekt erstellen... | Ein neues Spielobjekt erstellen |
| Raum erstellen... (Ctrl+R) | Einen neuen Spielraum erstellen |
| Skript erstellen... | Eine neue Skriptdatei erstellen |
| Schriftart erstellen... | Ein neues Schriftart-Asset erstellen |
| Objekt-Paket importieren... | Ein .gmobj-Paket importieren |
| Raum-Paket importieren... | Ein .gmroom-Paket importieren |

#### Erstellen-Menue

| Befehl | Tastaturkuerzel | Beschreibung |
|--------|-----------------|--------------|
| Spiel testen | F5 | Spiel im Testmodus ausfuehren |
| Spiel debuggen | F6 | Spiel mit Debug-Ausgabe ausfuehren |
| Spiel erstellen... | F7 | Build-Konfiguration oeffnen |
| Erstellen und Ausfuehren | F8 | Erstellen und sofort ausfuehren |
| Spiel exportieren... | | Kompiliertes Spiel exportieren |

#### Werkzeuge-Menue

| Befehl | Beschreibung |
|--------|--------------|
| Einstellungen... | IDE-Einstellungen oeffnen |
| Asset-Manager... | Asset-Verwaltungsfenster oeffnen |
| Aktionsbloecke konfigurieren... | Blockly-Bloecke konfigurieren |
| Thymio-Bloecke konfigurieren... | Thymio-Roboter-Bloecke konfigurieren |
| Projekt validieren | Projekt auf Fehler pruefen |
| Projekt bereinigen | Temporaere Dateien entfernen |
| Zu modularer Struktur migrieren | Projektformat aktualisieren |
| Sprache | Oberflaechen-Sprache aendern |
| Thymio Programmierung | Untermenue fuer Roboterprogrammierung |

#### Hilfe-Menue

| Befehl | Tastaturkuerzel | Beschreibung |
|--------|-----------------|--------------|
| Dokumentation | F1 | Hilfedokumentation oeffnen |
| Anleitungen | | Anleitungsressourcen oeffnen |
| Ueber PyGameMaker | | Versions- und Lizenzinformationen |

### Werkzeugleiste

Die Werkzeugleiste bietet schnellen Zugriff auf haeufige Aktionen (von links nach rechts):

| Schaltflaeche | Aktion |
|---------------|--------|
| Neu | Neues Projekt erstellen |
| Oeffnen | Bestehendes Projekt oeffnen |
| Speichern | Aktuelles Projekt speichern |
| Testen | Spiel ausfuehren (F5) |
| Debuggen | Spiel debuggen (F6) |
| Exportieren | Spiel exportieren |
| Sprite importieren | Ein Sprite-Bild importieren |
| Sound importieren | Eine Audiodatei importieren |
| Thymio | Thymio-Roboter-Ereignis hinzufuegen |

### Asset-Baum

Der Asset-Baum im linken Panel organisiert Projekt-Assets in Kategorien:

**Medien-Assets:**
- **Sprites** - Bilder und Animationsstreifen fuer Spielobjekte
- **Sounds** - Soundeffekte und Musikdateien
- **Hintergruende** - Hintergrundbilder und Kachelsaetze

**Spiellogik:**
- **Objekte** - Spielobjekt-Definitionen mit Ereignissen und Aktionen
- **Raeume** - Spiellevel/Szenen mit platzierten Instanzen

**Code-Assets:**
- **Skripte** - Codedateien
- **Schriftarten** - Benutzerdefinierte Schriftart-Assets

**Kontextmenue-Operationen:**
- Rechtsklick auf eine Kategorieueberueberschrift, um Assets zu erstellen oder zu importieren
- Rechtsklick auf ein Asset zum Umbenennen, Loeschen, Exportieren oder Anzeigen von Eigenschaften
- Doppelklick auf ein Asset, um es im Editor zu oeffnen
- Raum-Assets koennen umsortiert werden (Nach oben/unten/ganz oben/ganz unten verschieben)

---

## 4. Arbeiten mit Projekten

### Ein neues Projekt erstellen

1. Waehlen Sie **Datei > Neues Projekt** (Ctrl+N)
2. Geben Sie einen **Projektnamen** ein
3. Waehlen Sie einen **Speicherort** fuer den Projektordner
4. Waehlen Sie eine **Vorlage** (optional):
   - **Leeres Projekt** - Ein leeres Projekt
   - **Plattformspiel-Vorlage** - Vorkonfiguriert fuer Plattformspiele
   - **Top-Down-Spiel-Vorlage** - Vorkonfiguriert fuer Top-Down-Spiele
5. Klicken Sie auf **Projekt erstellen**

### Projektstruktur

```
MyProject/
├── project.json          # Haupt-Projektdatei
├── sprites/              # Sprite-Bilder und Metadaten
│   ├── player.png
│   └── player.json
├── objects/              # Objektdefinitionen
│   └── obj_player.json
├── rooms/                # Raum-Layoutdaten
│   └── room_start.json
├── sounds/               # Audiodateien und Metadaten
├── backgrounds/          # Hintergrundbilder
└── thumbnails/           # Automatisch generierte Vorschauen
```

### Projekte speichern

- **Ctrl+S** speichert das Projekt am aktuellen Speicherort
- **Ctrl+Shift+S** speichert an einem neuen Speicherort
- **Auto-Speichern** kann unter Datei > Auto-Speichern aktivieren eingeschaltet werden
- Auto-Speicher-Intervall unter Datei > Auto-Speicher-Einstellungen konfigurieren

### Projekte oeffnen

- **Ctrl+O** oeffnet einen Projektordner
- Letzte Projekte sind unter **Datei > Letzte Projekte** aufgelistet
- ZIP-Projekte koennen mit **Datei > Zip-Projekt oeffnen** geoeffnet werden

---

## 5. Sprites

Sprites sind die visuellen Bilder, die von Spielobjekten verwendet werden. Sie koennen statische Bilder oder Animationsstreifen mit mehreren Einzelbildern sein.

### Ein Sprite erstellen

1. Rechtsklick auf **Sprites** im Asset-Baum und **Sprite importieren...** waehlen
2. Eine Bilddatei auswaehlen (PNG, JPG, BMP oder GIF)
3. Das Sprite erscheint im Asset-Baum und oeffnet sich im Sprite-Editor

### Sprite-Editor

Der Sprite-Editor hat vier Hauptbereiche:

- **Werkzeugpanel (Links):** Zeichenwerkzeuge
- **Leinwand (Mitte):** Der Bearbeitungsbereich mit Zoom und Raster
- **Farbpalette (Rechts):** Vordergrund-/Hintergrundfarben und Farbfelder
- **Einzelbild-Zeitleiste (Unten):** Verwaltung von Animationseinzelbildern

#### Zeichenwerkzeuge

| Werkzeug | Tastaturkuerzel | Beschreibung |
|----------|-----------------|--------------|
| Bleistift | P | Standard-Pixelzeichnung |
| Radierer | E | Pixel entfernen (transparent machen) |
| Farbpipette | I | Eine Farbe von der Leinwand aufnehmen |
| Fuellen | G | Zusammenhaengende Bereiche fluten |
| Linie | L | Gerade Linien zeichnen |
| Rechteck | R | Rechtecke zeichnen (Umriss oder gefuellt) |
| Ellipse | O | Ellipsen zeichnen (Umriss oder gefuellt) |
| Auswahl | S | Bereiche auswaehlen, ausschneiden, kopieren, einfuegen |

#### Pinselgroesse

Die Pinselgroesse reicht von 1 bis 16 Pixel und beeinflusst die Werkzeuge Bleistift, Radierer und Linie.

#### Fuellmodus

Wechseln Sie zwischen Umriss- und Fuellmodus fuer die Werkzeuge Rechteck und Ellipse mit der Schaltflaeche **Gefuellt**.

#### Farbpalette

- **Linksklick** auf das Vordergrund-Farbfeld, um eine Zeichenfarbe zu waehlen
- **Rechtsklick** auf das Hintergrund-Farbfeld, um eine Sekundaerfarbe zu waehlen
- **X-Schaltflaeche** tauscht Vordergrund- und Hintergrundfarben
- Klicken Sie auf eine Farbe in der Schnellpalette, um sie auszuwaehlen
- Doppelklicken Sie auf ein Palettenfeld, um es anzupassen
- Voller RGBA-Farbwaehler mit Alpha-(Transparenz-)Unterstuetzung

### Animationseinzelbilder

Sprites koennen mehrere Animationseinzelbilder haben, die als horizontaler Streifen angeordnet sind.

**Steuerelemente der Einzelbild-Zeitleiste:**
- **+ (Hinzufuegen):** Ein neues leeres Einzelbild hinzufuegen
- **D (Duplizieren):** Das aktuelle Einzelbild kopieren
- **- (Loeschen):** Das aktuelle Einzelbild entfernen (mindestens 1 Einzelbild)
- **Abspielen/Stoppen:** Vorschau der Animation
- Einzelbild-Zaehler zeigt aktuelles/gesamte Einzelbilder

**Animationseigenschaften:**
- **Frame Count:** Anzahl der Animationseinzelbilder
- **Animation Speed:** Einzelbilder pro Sekunde (Standard: 10 FPS)
- **Animation Type:** single, strip_h (horizontal), strip_v (vertikal) oder grid

**Animiertes GIF-Unterstuetzung:** Importieren Sie animierte GIF-Dateien direkt. Alle Einzelbilder werden automatisch mit Transparenzbehandlung extrahiert.

### Sprite-Ursprung

Der Ursprungspunkt ist die Anklerposition, die fuer Platzierung und Rotation im Spiel verwendet wird.

**Voreingestellte Positionen:**
- Oben-Links (0, 0)
- Oben-Mitte
- Mitte (Standard fuer die meisten Sprites)
- Mitte-Unten
- Unten-Links
- Unten-Rechts
- Benutzerdefiniert (manuelle X/Y-Eingabe)

Der Ursprung wird als Fadenkreuz auf der Leinwand angezeigt.

### Leinwand-Steuerung

- **Ctrl+Mausrad:** Hinein-/Herauszoomen (1x bis 64x)
- **Raster-Umschalter:** Pixelraster ein-/ausblenden (sichtbar ab 4x Zoom)
- **Spiegeln H/V:** Das aktuelle Einzelbild horizontal oder vertikal spiegeln
- **Groesse aendern/Skalieren:** Sprite-Abmessungen mit Skalierungs- oder Leinwandgroessen-Optionen aendern

### Sprite-Eigenschaften (gespeichert)

| Eigenschaft | Beschreibung |
|-------------|--------------|
| name | Asset-Name |
| file_path | Pfad zur PNG-Streifendatei |
| width | Gesamte Streifenbreite |
| height | Einzelbildhoehe |
| frame_width | Einzelbildbreite |
| frame_height | Einzelbildhoehe |
| frames | Anzahl der Einzelbilder |
| animation_type | single, strip_h, strip_v, grid |
| speed | Animations-FPS |
| origin_x | Ursprung X-Koordinate |
| origin_y | Ursprung Y-Koordinate |

---

## 6. Sounds

Sounds sind Audiodateien, die fuer Soundeffekte und Hintergrundmusik verwendet werden.

### Sounds importieren

1. Rechtsklick auf **Sounds** im Asset-Baum und **Sound importieren...** waehlen
2. Eine Audiodatei auswaehlen (WAV, OGG, MP3)
3. Der Sound wird dem Projekt hinzugefuegt

### Sound-Eigenschaften

| Eigenschaft | Beschreibung |
|-------------|--------------|
| name | Sound-Asset-Name |
| file_path | Pfad zur Audiodatei |
| kind | "sound" (Effekt) oder "music" (Streaming) |
| volume | Standardlautstaerke (0.0 bis 1.0) |

**Soundeffekte** werden in den Speicher geladen fuer sofortige Wiedergabe. **Musik**-Dateien werden von der Festplatte gestreamt und es kann nur eine gleichzeitig abgespielt werden.

---

## 7. Hintergruende

Hintergruende sind Bilder, die hinter Spielobjekten verwendet werden. Sie koennen auch als Kachelsaetze fuer kachelbasierte Level dienen.

### Hintergruende importieren

1. Rechtsklick auf **Hintergruende** im Asset-Baum und **Hintergrund importieren...** waehlen
2. Eine Bilddatei auswaehlen

### Kachelsatz-Konfiguration

Hintergruende koennen als Kachelsaetze mit diesen Eigenschaften konfiguriert werden:

| Eigenschaft | Beschreibung |
|-------------|--------------|
| tile_width | Breite jeder Kachel (Standard: 16) |
| tile_height | Hoehe jeder Kachel (Standard: 16) |
| h_offset | Horizontaler Versatz zur ersten Kachel |
| v_offset | Vertikaler Versatz zur ersten Kachel |
| h_sep | Horizontaler Abstand zwischen Kacheln |
| v_sep | Vertikaler Abstand zwischen Kacheln |
| use_as_tileset | Kachelsatz-Modus aktivieren |

---

## 8. Objekte

Objekte definieren Spielentitaeten mit Eigenschaften, Ereignissen und Aktionen. Jedes Objekt kann ein Sprite zur visuellen Darstellung haben und enthaelt Ereignisbehandler, die sein Verhalten definieren.

### Ein Objekt erstellen

1. Rechtsklick auf **Objekte** im Asset-Baum und **Objekt erstellen...** waehlen
2. Einen Namen fuer das Objekt eingeben
3. Das Objekt oeffnet sich im Objekt-Editor

### Objekt-Eigenschaften

| Eigenschaft | Standard | Beschreibung |
|-------------|----------|--------------|
| Sprite | Keins | Das anzuzeigende visuelle Sprite |
| Visible | Ja | Ob Instanzen gezeichnet werden |
| Solid | Nein | Ob das Objekt Bewegung blockiert |
| Persistent | Nein | Ob Instanzen Raumwechsel ueberleben |
| Depth | 0 | Zeichenreihenfolge (hoeher = dahinter, niedriger = davor) |
| Parent | Keins | Elternobjekt fuer Vererbung |

### Elternobjekte

Objekte koennen von einem Elternobjekt erben. Kindobjekte erhalten alle Kollisionsereignisse des Elternobjekts. Dies ist nuetzlich fuer die Erstellung von Hierarchien wie:

```
obj_enemy (parent - has collision with obj_player)
  ├── obj_enemy_melee (inherits collision handling)
  └── obj_enemy_ranged (inherits collision handling)
```

### Ereignisse hinzufuegen

1. Den Objekt-Editor oeffnen
2. **Ereignis hinzufuegen** im Ereignis-Panel klicken
3. Einen Ereignistyp aus der Liste waehlen (siehe [Ereignis-Referenz](#10-ereignis-referenz))
4. Das Ereignis erscheint im Ereignisbaum

### Aktionen zu Ereignissen hinzufuegen

1. Ein Ereignis im Ereignisbaum auswaehlen
2. **Aktion hinzufuegen** klicken oder Rechtsklick und **Aktion hinzufuegen** waehlen
3. Einen Aktionstyp aus der kategorisierten Liste waehlen
4. Die Parameter der Aktion im Dialog konfigurieren
5. OK klicken, um die Aktion hinzuzufuegen

Aktionen werden von oben nach unten ausgefuehrt, wenn das Ereignis ausgeloest wird.

### Bedingte Logik

Aktionen unterstuetzen bedingte Wenn/Sonst-Ablaeufe:

1. Eine bedingte Aktion hinzufuegen (z.B. **Wenn Kollision bei**, **Variable testen**)
2. Eine **Block-Anfang**-Aktion hinzufuegen (oeffnende Klammer)
3. Aktionen hinzufuegen, die ausgefuehrt werden, wenn die Bedingung wahr ist
4. Eine **Sonst**-Aktion hinzufuegen (optional)
5. Einen **Block-Anfang** fuer den Sonst-Zweig hinzufuegen
6. Aktionen fuer den Falsch-Fall hinzufuegen
7. **Block-Ende**-Aktionen hinzufuegen, um jeden Block zu schliessen

Beispiel-Aktionssequenz:
```
If Collision At (self.x, self.y + 1, "solid")
  Start Block
    Set Vertical Speed (0)
  End Block
Else
  Start Block
    Set Vertical Speed (vspeed + 0.5)
  End Block
```

### Code anzeigen

Aktivieren Sie die Option **Code anzeigen** im Objekt-Editor, um den generierten Python-Code fuer alle Ereignisse und Aktionen zu sehen. Dies ist nuetzlich, um zu verstehen, wie die visuellen Aktionen in Code uebersetzt werden.

---

## 9. Raeume

Raeume sind die Szenen oder Level Ihres Spiels. Jeder Raum hat einen Hintergrund, platzierte Objektinstanzen und optionale Kachelebenen.

### Einen Raum erstellen

1. Rechtsklick auf **Raeume** im Asset-Baum und **Raum erstellen...** waehlen
2. Einen Namen fuer den Raum eingeben
3. Der Raum oeffnet sich im Raum-Editor

### Raum-Eigenschaften

| Eigenschaft | Standard | Beschreibung |
|-------------|----------|--------------|
| Width | 1024 | Raumbreite in Pixeln |
| Height | 768 | Raumhoehe in Pixeln |
| Background Color | #87CEEB (Himmelblau) | Fuellfarbe hinter allem |
| Background Image | Keins | Optionales Hintergrundbild |
| Persistent | Nein | Zustand beim Verlassen beibehalten |

### Instanzen platzieren

1. Ein Objekt in der **Objekt-Palette** (linke Seite des Raum-Editors) anklicken
2. In die Raum-Leinwand klicken, um eine Instanz zu platzieren
3. Weiter klicken, um weitere Kopien zu platzieren
4. Platzierte Instanzen auswaehlen, um sie zu verschieben oder zu konfigurieren

### Instanz-Eigenschaften

Wenn Sie eine platzierte Instanz auswaehlen:

| Eigenschaft | Bereich | Beschreibung |
|-------------|---------|--------------|
| X Position | 0-9999 | Horizontale Position |
| Y Position | 0-9999 | Vertikale Position |
| Visible | Ja/Nein | Sichtbarkeit der Instanz |
| Rotation | 0-360 | Rotation in Grad |
| Scale X | 10%-1000% | Horizontale Skalierung |
| Scale Y | 10%-1000% | Vertikale Skalierung |

### Raster und Einrasten

- **Raster-Umschalter:** Klicken Sie die Raster-Schaltflaeche, um das Platzierungsraster ein-/auszublenden
- **Einrast-Umschalter:** Klicken Sie die Einrast-Schaltflaeche, um Rastereinrastung ein-/auszuschalten
- **Rastergroesse:** Standardmaessig 32x32 Pixel (in den Einstellungen konfigurierbar)

### Instanz-Operationen

| Aktion | Tastaturkuerzel | Beschreibung |
|--------|-----------------|--------------|
| Verschieben | Ziehen | Instanz an neue Position verschieben |
| Mehrere auswaehlen | Shift+Klick | Zur Auswahl hinzufuegen/entfernen |
| Gummiband-Auswahl | Leeren Bereich ziehen | Alle Instanzen im Rechteck auswaehlen |
| Loeschen | Delete-Taste | Ausgewaehlte Instanzen entfernen |
| Ausschneiden | Ctrl+X | In Zwischenablage ausschneiden |
| Kopieren | Ctrl+C | In Zwischenablage kopieren |
| Einfuegen | Ctrl+V | Aus Zwischenablage einfuegen |
| Duplizieren | Ctrl+D | Ausgewaehlte Instanzen duplizieren |
| Alle loeschen | Werkzeugleisten-Schaltflaeche | Alle Instanzen entfernen (mit Bestaetigung) |

### Hintergrund-Ebenen

Raeume unterstuetzen bis zu 8 Hintergrund-Ebenen (Index 0-7), jede mit unabhaengigen Einstellungen:

| Eigenschaft | Beschreibung |
|-------------|--------------|
| Background Image | Welches Hintergrund-Asset verwendet wird |
| Visible | Ebene ein-/ausblenden |
| Foreground | Wenn wahr, vor Instanzen gezeichnet |
| Tile Horizontal | Ueber die Raumbreite wiederholen |
| Tile Vertical | Ueber die Raumhoehe wiederholen |
| H Scroll Speed | Horizontale Scroll-Pixel pro Einzelbild |
| V Scroll Speed | Vertikale Scroll-Pixel pro Einzelbild |
| Stretch | Auf den gesamten Raum skalieren |
| X / Y Offset | Ebenenpositionsversatz |

### Kachel-Ebenen

Fuer kachelbasierte Level:

1. **Kachel-Palette...** klicken, um den Kachelwaehler zu oeffnen
2. Einen Kachelsatz waehlen (als Kachelsatz markierter Hintergrund)
3. Kachelbreite und -hoehe einstellen
4. Eine Kachel in der Palette anklicken, um sie auszuwaehlen
5. In den Raum klicken, um Kacheln zu platzieren
6. Eine **Ebene** (0-7) fuer die Kacheln waehlen

### Raum-Reihenfolge

Raeume werden in der Reihenfolge ausgefuehrt, in der sie im Asset-Baum erscheinen. Der erste Raum ist der Startraum.

- Rechtsklick auf einen Raum und **Nach oben/unten/ganz oben/ganz unten verschieben** verwenden, um umzusortieren
- Die Aktionen **Naechster Raum** und **Vorheriger Raum** verwenden, um zur Laufzeit zwischen Raeumen zu navigieren

### Ansichtssystem

Raeume unterstuetzen bis zu 8 Kameraansichten (wie in GameMaker):

| Eigenschaft | Beschreibung |
|-------------|--------------|
| Visible | Diese Ansicht ein-/ausschalten |
| View X/Y | Kameraposition im Raum |
| View W/H | Kamera-Ansichtsgroesse |
| Port X/Y | Bildschirmposition fuer diese Ansicht |
| Port W/H | Bildschirmgroesse fuer diese Ansicht |
| Follow Object | Objekt, dem die Kamera folgt |
| H/V Border | Scrollrand um das verfolgte Objekt |
| H/V Speed | Maximale Kamera-Scrollgeschwindigkeit (-1 = sofort) |

---

## 10. Ereignis-Referenz

Ereignisse definieren, wann Aktionen ausgefuehrt werden. Jedes Ereignis wird unter bestimmten Bedingungen ausgeloest.

### Objekt-Ereignisse

| Ereignis | Kategorie | Wird ausgeloest, wenn |
|----------|-----------|----------------------|
| Create | Objekt | Instanz zum ersten Mal erstellt wird |
| Destroy | Objekt | Instanz zerstoert wird |
| Step | Schritt | Jedes Spieleinzelbild (~60 FPS) |
| Begin Step | Schritt | Beginn jedes Einzelbilds, vor der Physik |
| End Step | Schritt | Ende jedes Einzelbilds, nach Kollisionen |

### Kollisions-Ereignisse

| Ereignis | Kategorie | Wird ausgeloest, wenn |
|----------|-----------|----------------------|
| Collision With... | Kollision | Zwei Instanzen sich ueberlappen (Zielobjekt auswaehlen) |

### Tastatur-Ereignisse

| Ereignis | Kategorie | Wird ausgeloest, wenn |
|----------|-----------|----------------------|
| Keyboard | Eingabe | Taste kontinuierlich gedrueckt gehalten wird (fuer fluessige Bewegung) |
| Keyboard Press | Eingabe | Taste zum ersten Mal gedrueckt wird (einmal pro Druck) |
| Keyboard Release | Eingabe | Taste losgelassen wird |

**Verfuegbare Tasten:** A-Z, 0-9, Pfeiltasten, Leertaste, Eingabe, Escape, Tab, Ruecktaste, Entfernen, F1-F12, Nummernblock-Tasten, Shift, Ctrl, Alt und mehr (insgesamt 76+ Tasten).

**Spezielle Tastatur-Ereignisse:**
- **Keine Taste** - Wird ausgeloest, wenn keine Taste gedrueckt ist
- **Beliebige Taste** - Wird ausgeloest, wenn eine beliebige Taste gedrueckt wird

### Maus-Ereignisse

| Ereignis | Kategorie | Wird ausgeloest, wenn |
|----------|-----------|----------------------|
| Mouse Left/Right/Middle Press | Eingabe | Taste auf Instanz geklickt wird |
| Mouse Left/Right/Middle Release | Eingabe | Taste auf Instanz losgelassen wird |
| Mouse Left/Right/Middle Down | Eingabe | Taste auf Instanz gehalten wird |
| Mouse Enter | Eingabe | Cursor den Begrenzungsrahmen der Instanz betritt |
| Mouse Leave | Eingabe | Cursor den Begrenzungsrahmen der Instanz verlaesst |
| Mouse Wheel Up/Down | Eingabe | Scrollrad auf Instanz verwendet wird |
| Global Mouse Press | Eingabe | Taste irgendwo im Raum geklickt wird |
| Global Mouse Release | Eingabe | Taste irgendwo im Raum losgelassen wird |

### Zeitsteuerungs-Ereignisse

| Ereignis | Kategorie | Wird ausgeloest, wenn |
|----------|-----------|----------------------|
| Alarm 0-11 | Zeitsteuerung | Alarm-Countdown Null erreicht (12 unabhaengige Alarme) |

### Zeichen-Ereignisse

| Ereignis | Kategorie | Wird ausgeloest, wenn |
|----------|-----------|----------------------|
| Draw | Zeichnen | Instanz gezeichnet wird (ersetzt Standard-Sprite-Zeichnung) |
| Draw GUI | Zeichnen | Ueber allem gezeichnet wird (fuer HUD, Punkteanzeige) |

### Raum-Ereignisse

| Ereignis | Kategorie | Wird ausgeloest, wenn |
|----------|-----------|----------------------|
| Room Start | Raum | Raum beginnt (nach Create-Ereignissen) |
| Room End | Raum | Raum gleich endet |

### Spiel-Ereignisse

| Ereignis | Kategorie | Wird ausgeloest, wenn |
|----------|-----------|----------------------|
| Game Start | Spiel | Spiel initialisiert wird (nur erster Raum) |
| Game End | Spiel | Spiel geschlossen wird |

### Andere Ereignisse

| Ereignis | Kategorie | Wird ausgeloest, wenn |
|----------|-----------|----------------------|
| Outside Room | Andere | Instanz vollstaendig ausserhalb der Raumgrenzen ist |
| Intersect Boundary | Andere | Instanz den Raumrand beruehrt |
| No More Lives | Andere | Leben-Wert 0 oder weniger erreicht |
| No More Health | Andere | Gesundheits-Wert 0 oder weniger erreicht |
| Animation End | Andere | Sprite-Animation das letzte Einzelbild erreicht |
| User Event 0-15 | Andere | 16 benutzerdefinierte Ereignisse, die durch Code ausgeloest werden |

---

## 11. Aktions-Referenz

Aktionen sind die Bausteine des Spielverhaltens. Sie werden in Ereignisse platziert und der Reihe nach ausgefuehrt.

### Bewegungs-Aktionen

| Aktion | Parameter | Beschreibung |
|--------|-----------|--------------|
| Move Grid | direction (left/right/up/down), grid_size (Standard: 32) | Eine Rastereinheit in eine Richtung bewegen |
| Set Horizontal Speed | speed (Pixel/Einzelbild) | hspeed fuer fluessige horizontale Bewegung setzen |
| Set Vertical Speed | speed (Pixel/Einzelbild) | vspeed fuer fluessige vertikale Bewegung setzen |
| Stop Movement | (keine) | Beide Geschwindigkeiten auf Null setzen |
| Move Fixed | directions (8-Wege), speed | Bewegung in fester Richtung starten |
| Move Free | direction (0-360 Grad), speed | In einem praezisen Winkel bewegen |
| Move Towards | x, y, speed | Auf eine Zielposition zubewegen |
| Set Gravity | direction (270=unten), gravity | Konstante Beschleunigung anwenden |
| Set Friction | friction | Verzoegerung pro Einzelbild anwenden |
| Reverse Horizontal | (keine) | hspeed-Richtung umkehren |
| Reverse Vertical | (keine) | vspeed-Richtung umkehren |
| Set Speed | speed | Bewegungsstaerke setzen |
| Set Direction | direction (Grad) | Bewegungswinkel setzen |
| Jump to Position | x, y | Zu Position teleportieren |
| Jump to Start | (keine) | Zur Startposition teleportieren |
| Bounce | (keine) | Geschwindigkeit bei Kollision umkehren |

### Raster-Aktionen

| Aktion | Parameter | Beschreibung |
|--------|-----------|--------------|
| Snap to Grid | grid_size | Position am naechsten Rasterpunkt ausrichten |
| If On Grid | grid_size | Pruefen, ob am Raster ausgerichtet (bedingt) |
| Stop If No Keys | grid_size | Auf Raster stoppen, wenn Bewegungstasten losgelassen |

### Instanz-Aktionen

| Aktion | Parameter | Beschreibung |
|--------|-----------|--------------|
| Create Instance | object, x, y, relative | Eine neue Objektinstanz erstellen |
| Destroy Instance | target (self/other) | Eine Instanz aus dem Spiel entfernen |
| Change Sprite | sprite | Das angezeigte Sprite aendern |
| Set Visible | visible (true/false) | Instanz ein- oder ausblenden |
| Set Scale | scale_x, scale_y | Instanzgroesse aendern |

### Punkte-, Leben- und Gesundheits-Aktionen

| Aktion | Parameter | Beschreibung |
|--------|-----------|--------------|
| Set Score | value | Punktzahl auf einen bestimmten Wert setzen |
| Add to Score | value | Punkte hinzufuegen (kann negativ sein) |
| Set Lives | value | Anzahl der Leben setzen |
| Add Lives | value | Leben hinzufuegen/entfernen |
| Set Health | value | Gesundheit setzen (0-100) |
| Add Health | value | Gesundheit hinzufuegen/entfernen |
| Show Highscore Table | (keine) | Die Bestenliste anzeigen |

### Raum- und Spiel-Aktionen

| Aktion | Parameter | Beschreibung |
|--------|-----------|--------------|
| Restart Room | (keine) | Den aktuellen Raum neu laden |
| Next Room | (keine) | Zum naechsten Raum in der Reihenfolge gehen |
| Previous Room | (keine) | Zum vorherigen Raum gehen |
| Go to Room | room | Zu einem bestimmten Raum springen |
| If Next Room Exists | (keine) | Bedingt: Gibt es einen naechsten Raum? |
| If Previous Room Exists | (keine) | Bedingt: Gibt es einen vorherigen Raum? |
| Restart Game | (keine) | Vom ersten Raum neu starten |
| End Game | (keine) | Das Spiel beenden |

### Zeitsteuerungs-Aktionen

| Aktion | Parameter | Beschreibung |
|--------|-----------|--------------|
| Set Alarm | alarm_number (0-11), steps | Countdown-Timer starten (30 Schritte = 0,5 Sek. bei 60 FPS) |
| Delay Action | action, delay_frames | Eine Aktion nach einer Verzoegerung ausfuehren |

### Nachrichten- und Anzeige-Aktionen

| Aktion | Parameter | Beschreibung |
|--------|-----------|--------------|
| Show Message | message | Eine Popup-Nachricht anzeigen |
| Draw Text | text, x, y, color, size | Text auf dem Bildschirm zeichnen (im Draw-Ereignis verwenden) |
| Draw Rectangle | x1, y1, x2, y2, color, filled | Ein Rechteck zeichnen |
| Draw Circle | x, y, radius, color, filled | Einen Kreis zeichnen |
| Draw Ellipse | x1, y1, x2, y2, color, filled | Eine Ellipse zeichnen |
| Draw Line | x1, y1, x2, y2, color | Eine Linie zeichnen |
| Draw Sprite | sprite_name, x, y, subimage | Ein Sprite an einer Position zeichnen |
| Draw Background | background_name, x, y, tiled | Ein Hintergrundbild zeichnen |
| Draw Score | x, y, caption | Punktzahl auf dem Bildschirm zeichnen |
| Draw Lives | x, y, sprite | Leben als Sprite-Symbole zeichnen |
| Draw Health Bar | x, y, width, height | Gesundheitsbalken auf dem Bildschirm zeichnen |

### Sound-Aktionen

| Aktion | Parameter | Beschreibung |
|--------|-----------|--------------|
| Play Sound | sound, loop | Einen Soundeffekt abspielen |
| Stop Sound | sound | Einen laufenden Sound stoppen |
| Play Music | music | Hintergrundmusik abspielen (Streaming) |
| Stop Music | (keine) | Hintergrundmusik stoppen |
| Set Volume | sound, volume (0.0-1.0) | Lautstaerke anpassen |

### Kontrollfluss-Aktionen

| Aktion | Parameter | Beschreibung |
|--------|-----------|--------------|
| If Collision At | x, y, object_type | Auf Kollision an Position pruefen |
| If Can Push | direction, object_type | Sokoban-artige Schiebe-Pruefung |
| Set Variable | name, value, scope, relative | Einen Variablenwert setzen |
| Test Variable | name, value, scope, operation | Eine Variable vergleichen |
| Test Expression | expression | Einen booleschen Ausdruck auswerten |
| Check Empty | x, y, only_solid | Pruefen, ob Position frei ist |
| Check Collision | x, y, only_solid | Auf Kollision an Position pruefen |
| Start Block | (keine) | Einen Aktionsblock beginnen (oeffnende Klammer) |
| End Block | (keine) | Einen Aktionsblock beenden (schliessende Klammer) |
| Else | (keine) | Markiert den Sonst-Zweig einer Bedingung |
| Repeat | times | Die naechste Aktion/den naechsten Block N-mal wiederholen |
| Exit Event | (keine) | Ausfuehrung der verbleibenden Aktionen stoppen |

### Variablen-Gueltigkeitsbereich

Auf Variablen kann mit bereichsbezogenen Referenzen zugegriffen werden:

| Bereich | Syntax | Beschreibung |
|---------|--------|--------------|
| Self | `self.variable` oder nur `variable` | Variable der aktuellen Instanz |
| Other | `other.variable` | Die andere Instanz bei einer Kollision |
| Global | `global.variable` | Spielweite Variable |

Eingebaute Instanzvariablen: `x`, `y`, `hspeed`, `vspeed`, `direction`, `speed`, `gravity`, `friction`, `visible`, `depth`, `image_index`, `image_speed`, `scale_x`, `scale_y`

---

## 12. Testen und Ausfuehren von Spielen

### Schnelltest (F5)

Druecken Sie **F5** oder klicken Sie die **Testen**-Schaltflaeche, um Ihr Spiel sofort auszufuehren. Ein separates Pygame-Fenster oeffnet sich und zeigt Ihr Spiel.

- Druecken Sie **Escape**, um das Spiel zu stoppen und zur IDE zurueckzukehren
- Die IDE-Statusleiste zeigt "Spiel laeuft..." waehrend das Spiel aktiv ist

### Debug-Modus (F6)

Druecken Sie **F6** fuer den Debug-Modus, der zusaetzliche Konsolenausgaben anzeigt, darunter:
- Protokollierung der Ereignisausfuehrung
- Details der Kollisionserkennung
- Aktionsparameterwerte
- Instanzerstellung und -zerstoerung

### Spielausfuehrungsreihenfolge

Jedes Einzelbild folgt der GameMaker 7.0-Ereignisreihenfolge:

1. **Begin Step**-Ereignisse
2. **Alarm**-Countdown und Ausloeser
3. **Step**-Ereignisse
4. **Tastatur/Maus**-Eingabeereignisse
5. **Bewegung** (Physik: Gravitation, Reibung, hspeed/vspeed)
6. **Kollisions**-Erkennung und Ereignisse
7. **End Step**-Ereignisse
8. **Destroy**-Ereignisse fuer markierte Instanzen
9. **Draw**-Ereignisse und Rendering

### Fenstertitel

Der Spielfenstertitel kann Punkte-, Leben- und Gesundheitswerte anzeigen. Aktivieren Sie dies mit den Titelanzeige-Einstellungen in den Projekteinstellungen oder durch Verwendung der Punkte-/Leben-/Gesundheits-Aktionen.

---

## 13. Spiele exportieren

### HTML5-Export

**Datei > Als HTML5 exportieren**

Erstellt eine einzelne, eigenstaendige HTML-Datei, die in jedem Webbrowser laeuft.

- Alle Sprites werden als Base64-Daten eingebettet
- Spieldaten werden mit gzip komprimiert
- JavaScript-Engine uebernimmt das Rendering via HTML5 Canvas
- Kein Server erforderlich - einfach die Datei im Browser oeffnen

### EXE-Export (Windows)

**Datei > Projekt exportieren** oder **Erstellen > Spiel exportieren**

Erstellt eine eigenstaendige Windows-ausfuehrbare Datei mit PyInstaller.

**Voraussetzungen:** PyInstaller und Kivy muessen installiert sein.

**Ablauf:**
1. Generiert ein Kivy-basiertes Spiel aus Ihrem Projekt
2. Buendelt Python-Laufzeitumgebung und alle Abhaengigkeiten
3. Erstellt eine einzelne EXE-Datei (kann 5-10 Minuten dauern)

**Optionen:**
- Debug-Konsole (zeigt Terminalfenster zum Debuggen)
- Benutzerdefiniertes Symbol
- UPX-Komprimierung (reduziert Dateigroesse)

### Mobiler Export (Kivy)

**Datei > Nach Kivy exportieren**

Generiert ein Kivy-Projekt fuer mobile Bereitstellung.

**Ausgabe umfasst:**
- Python-Spielcode angepasst fuer Kivy
- Asset-Buendel optimiert fuer Mobilgeraete
- `buildozer.spec`-Konfiguration fuer Android/iOS-Builds

**Fuer Android erstellen:**
```bash
cd exported_project
buildozer android debug
```

### ZIP-Export

**Datei > Als Zip exportieren**

Verpackt das gesamte Projekt als ZIP-Archiv zum Teilen oder zur Sicherung. Die ZIP-Datei kann mit **Datei > Zip-Projekt oeffnen** wieder geoeffnet werden.

### Aseba-Export (Thymio-Roboter)

Fuer Thymio-Roboter-Projekte werden AESL-Codedateien exportiert, die mit Aseba Studio kompatibel sind.

---

## 14. Blockly Visuelle Programmierung

PyGameMaker integriert Google Blockly fuer visuelle Code-Block-Programmierung.

### Bloecke konfigurieren

Oeffnen Sie **Werkzeuge > Aktionsbloecke konfigurieren**, um anzupassen, welche Bloecke verfuegbar sind.

### Block-Voreinstellungen

| Voreinstellung | Beschreibung |
|----------------|--------------|
| Voll (Alle Bloecke) | Alle 173 Bloecke aktiviert |
| Anfaenger | Nur wesentliche Bloecke (Ereignisse, Grundbewegung, Punkte, Raeume) |
| Fortgeschritten | Fuegt Zeichnen, mehr Bewegung, Leben, Gesundheit, Sound hinzu |
| Plattformspiel | Physik-fokussiert: Gravitation, Reibung, Kollision |
| Rasterbasiertes RPG | Rasterbewegung, Gesundheit, Raumuebergaenge |
| Sokoban (Kisten-Raetsel) | Rasterbewegung, Schiebe-Mechaniken |
| Testen | Nur validierte Bloecke |
| Nur implementiert | Schliesst nicht implementierte Bloecke aus |
| Code-Editor | Fuer textbasierte Programmierung |
| Blockly-Editor | Fuer visuell-orientierte Entwicklung |
| Benutzerdefiniert | Ihre eigene Auswahl |

### Block-Kategorien

Bloecke sind in farbkodierte Kategorien organisiert:

| Kategorie | Farbe | Bloecke |
|-----------|-------|---------|
| Ereignisse | Gelb | 13 Ereignis-Bloecke |
| Bewegung | Blau | 14 Bewegungs-Bloecke |
| Zeitsteuerung | Rot | Timer- und Alarm-Bloecke |
| Zeichnen | Lila | Form- und Textzeichnung |
| Punkte/Leben/Gesundheit | Gruen | Punkte-Verfolgungs-Bloecke |
| Instanz | Rosa | Instanzen erstellen/zerstoeren |
| Raum | Braun | Raum-Navigation |
| Werte | Dunkelblau | Variablen und Ausdruecke |
| Sound | | Audio-Wiedergabe |
| Ausgabe | | Nachrichten und Anzeige |

### Block-Abhaengigkeiten

Einige Bloecke benoetigen andere Bloecke, um zu funktionieren. Der Konfigurationsdialog zeigt Warnungen an, wenn Abhaengigkeiten fehlen. Zum Beispiel benoetigt der **Draw Score**-Block, dass **Set Score** und **Add Score** aktiviert sind.

---

## 15. Thymio Roboter-Unterstuetzung

PyGameMaker bietet Unterstuetzung fuer den Thymio-Lernroboter, mit der Sie Thymio-Roboter innerhalb der IDE simulieren und programmieren koennen.

### Was ist Thymio?

Thymio ist ein kleiner Lernroboter mit Sensoren, LEDs, Motoren und Tasten. PyGameMaker kann Thymio-Verhalten simulieren und Code exportieren, der auf echten Robotern laeuft.

### Thymio aktivieren

Gehen Sie zu **Werkzeuge > Thymio Programmierung > Thymio-Tab im Objekt-Editor anzeigen**, um Thymio-Funktionen im Objekt-Editor zu aktivieren.

### Thymio-Simulator

Der Simulator modelliert den physischen Thymio-Roboter:

**Spezifikationen:**
- Robotergroesse: 110x110 Pixel (11cm x 11cm)
- Radabstand: 95 Pixel
- Motorgeschwindigkeitsbereich: -500 bis +500

### Thymio-Sensoren

| Sensor | Anzahl | Bereich | Beschreibung |
|--------|--------|---------|--------------|
| Naeherung | 7 | 0-4000 | Horizontale Abstandssensoren (10cm Reichweite) |
| Boden | 2 | 0-1023 | Erkennt helle/dunkle Oberflaechen |
| Tasten | 5 | 0/1 | Vorwaerts, rueckwaerts, links, rechts, Mitte |

### Thymio-Ereignisse

| Ereignis | Wird ausgeloest, wenn |
|----------|----------------------|
| Button Forward/Backward/Left/Right/Center | Kapazitive Taste gedrueckt wird |
| Any Button | Beliebiger Tastenzustand sich aendert |
| Proximity Update | Naeherungssensoren aktualisiert werden (10 Hz) |
| Ground Update | Bodensensoren aktualisiert werden (10 Hz) |
| Tap | Beschleunigungsmesser Antippen/Stoss erkennt |
| Sound Detected | Mikrofon Ton erkennt |
| Timer 0/1 | Timer-Periode ablaeuft |
| Sound Finished | Tonwiedergabe abgeschlossen ist |
| Message Received | IR-Kommunikation empfangen wird |

### Thymio-Aktionen

**Motorsteuerung:**
- Motorgeschwindigkeit setzen (links, rechts unabhaengig)
- Vorwaerts / Rueckwaerts fahren
- Links / Rechts drehen
- Motoren stoppen

**LED-Steuerung:**
- Obere LED setzen (RGB-Farbe)
- Untere linke/rechte LED setzen
- Kreis-LEDs setzen (8 LEDs am Umfang)
- Alle LEDs ausschalten

**Sound:**
- Ton abspielen (Frequenz, Dauer)
- Systemton abspielen
- Ton stoppen

**Sensor-Bedingungen:**
- Wenn Naeherung (Sensor, Schwellenwert, Vergleich)
- Wenn Boden dunkel / hell
- Wenn Taste gedrueckt / losgelassen

**Timer:**
- Timer-Periode setzen (Timer 0 oder 1, Periode in ms)

### Export auf echten Thymio

1. Ihr Thymio-Projekt ueber den Aseba-Exporter exportieren
2. Die generierte `.aesl`-Datei in Aseba Studio oeffnen
3. Ihren Thymio per USB verbinden
4. **Laden** und dann **Ausfuehren** klicken

---

## 16. Einstellungen und Praeferenzen

Oeffnen Sie **Werkzeuge > Einstellungen**, um die IDE zu konfigurieren.

### Darstellungs-Tab

| Einstellung | Optionen | Standard |
|-------------|----------|----------|
| Schriftgroesse | 8-24 pt | 10 |
| Schriftfamilie | System Default, Segoe UI, Arial, Ubuntu, Helvetica, SF Pro Text, Roboto | System Default |
| Design | Default, Dark, Light | Default |
| UI-Skalierung | 0.5x - 2.0x | 1.0x |
| Tooltips anzeigen | Ja/Nein | Ja |

### Editor-Tab

| Einstellung | Optionen | Standard |
|-------------|----------|----------|
| Auto-Speichern aktivieren | Ja/Nein | Ja |
| Auto-Speicher-Intervall | 1-30 Minuten | 5 Min. |
| Raster anzeigen | Ja/Nein | Ja |
| Rastergroesse | 8-128 px | 32 |
| Am Raster einrasten | Ja/Nein | Ja |
| Kollisionsrahmen anzeigen | Ja/Nein | Nein |

### Projekt-Tab

| Einstellung | Optionen | Standard |
|-------------|----------|----------|
| Standard-Projektordner | Pfad | ~/PyGameMaker Projects |
| Limit fuer letzte Projekte | 5-50 | 10 |
| Sicherung beim Speichern erstellen | Ja/Nein | Ja |

### Erweitert-Tab

| Einstellung | Optionen | Standard |
|-------------|----------|----------|
| Debug-Modus | Ja/Nein | Nein |
| Konsolenausgabe anzeigen | Ja/Nein | Ja |
| Maximale Rueckgaengig-Schritte | 10-200 | 50 |

### Konfigurationsdatei

Einstellungen werden in `~/.pygamemaker/config.json` gespeichert und bleiben zwischen Sitzungen erhalten.

### Sprache aendern

Gehen Sie zu **Werkzeuge > Sprache** und waehlen Sie Ihre bevorzugte Sprache.

**Unterstuetzte Sprachen:**
- English
- Francais
- Espanol
- Deutsch
- Italiano
- Russisch (Russian)
- Slovenscina (Slovenian)
- Ukrainisch (Ukrainian)

Die Oberflaeche wird sofort aktualisiert. Einige Aenderungen erfordern moeglicherweise einen Neustart der IDE.

---

## 17. Tastaturkuerzel

### Globale Tastaturkuerzel

| Tastaturkuerzel | Aktion |
|-----------------|--------|
| Ctrl+N | Neues Projekt |
| Ctrl+O | Projekt oeffnen |
| Ctrl+S | Projekt speichern |
| Ctrl+Shift+S | Projekt speichern als |
| Ctrl+E | Projekt exportieren |
| Ctrl+Q | IDE beenden |
| Ctrl+R | Raum erstellen |
| F1 | Dokumentation |
| F5 | Spiel testen |
| F6 | Spiel debuggen |
| F7 | Spiel erstellen |
| F8 | Erstellen und ausfuehren |

### Editor-Tastaturkuerzel

| Tastaturkuerzel | Aktion |
|-----------------|--------|
| Ctrl+Z | Rueckgaengig |
| Ctrl+Y | Wiederherstellen |
| Ctrl+X | Ausschneiden |
| Ctrl+C | Kopieren |
| Ctrl+V | Einfuegen |
| Ctrl+D | Duplizieren |
| Ctrl+F | Suchen |
| Ctrl+H | Suchen und Ersetzen |
| Delete | Ausgewaehlte loeschen |

### Sprite-Editor-Tastaturkuerzel

| Tastaturkuerzel | Aktion |
|-----------------|--------|
| P | Bleistift-Werkzeug |
| E | Radierer-Werkzeug |
| I | Farbpipette |
| G | Fuell-(Eimer-)Werkzeug |
| L | Linien-Werkzeug |
| R | Rechteck-Werkzeug |
| O | Ellipsen-Werkzeug |
| S | Auswahl-Werkzeug |
| Ctrl+Mausrad | Hinein-/Herauszoomen |

---

## 18. Anleitungen

PyGameMaker enthaelt eingebaute Anleitungen, um Ihnen den Einstieg zu erleichtern. Greifen Sie ueber **Hilfe > Anleitungen** oder den Anleitungsordner im Installationsverzeichnis darauf zu.

### Verfuegbare Anleitungen

| # | Anleitung | Beschreibung |
|---|-----------|--------------|
| 01 | Erste Schritte | IDE-Einfuehrung und erstes Projekt |
| 02 | Erstes Spiel | Ihr erstes spielbares Spiel erstellen |
| 03 | Pong | Klassisches Pong-Spiel mit Schlaeger und Ball |
| 04 | Breakout | Breakout-artiges Ziegelbrecher-Spiel |
| 05 | Sokoban | Kisten-Schiebe-Raetselspiel |
| 06 | Labyrinth | Labyrinth-Navigationsspiel |
| 07 | Plattformspiel | Seitenscrollendes Plattformspiel |
| 08 | Mondlandung | Gravitationsbasiertes Landungsspiel |

Anleitungen sind in mehreren Sprachen verfuegbar (Englisch, Deutsch, Spanisch, Franzoesisch, Italienisch, Russisch, Slowenisch, Ukrainisch).

---

## 19. Fehlerbehebung

### Spiel startet nicht (F5)

- Stellen Sie sicher, dass Ihr Projekt mindestens einen Raum mit Instanzen hat
- Pruefen Sie, ob Objekten Sprites zugewiesen sind
- Sehen Sie sich die Konsolenausgabe an (F6 Debug-Modus) fuer Fehlermeldungen

### Sprites werden nicht angezeigt

- Bestaetigen Sie, dass die Sprite-Datei im `sprites/`-Ordner existiert
- Pruefen Sie, ob dem Objekt ein Sprite in seinen Eigenschaften zugewiesen ist
- Stellen Sie sicher, dass die Instanz auf `visible = true` gesetzt ist

### Kollision funktioniert nicht

- Stellen Sie sicher, dass das Zielobjekt als **Solid** markiert ist, wenn solidbasierte Kollision verwendet wird
- Ueberpruefen Sie, ob ein **Kollision mit**-Ereignis fuer das richtige Objekt eingerichtet ist
- Pruefen Sie, ob sich Instanzen tatsaechlich ueberlappen (Debug-Modus verwenden)

### Sound wird nicht abgespielt

- Stellen Sie sicher, dass die Sounddatei existiert und ein unterstuetztes Format hat (WAV, OGG, MP3)
- Pruefen Sie, ob pygame.mixer erfolgreich initialisiert wurde (siehe Konsolenausgabe)
- Musikdateien werden von der Festplatte gestreamt - stellen Sie sicher, dass der Dateipfad korrekt ist

### Export schlaegt fehl

- **EXE-Export:** Stellen Sie sicher, dass PyInstaller installiert ist (`pip install pyinstaller`)
- **Kivy-Export:** Stellen Sie sicher, dass Kivy installiert ist (`pip install kivy`)
- **HTML5-Export:** Pruefen Sie die Konsole auf Kodierungsfehler
- Alle Exporte erfordern ein gueltiges Projekt mit mindestens einem Raum

### Leistungsprobleme

- Reduzieren Sie die Anzahl der Instanzen in Raeumen
- Verwenden Sie das raeumliche Raster-Kollisionssystem (standardmaessig aktiviert)
- Vermeiden Sie aufwaendige Operationen in Step-Ereignissen (wird 60-mal pro Sekunde ausgefuehrt)
- Verwenden Sie Alarme fuer periodische Aufgaben statt Einzelbilder im Step-Ereignis zu zaehlen

---

**PyGameMaker IDE** - Version 1.0.0-rc.6
Copyright 2025-2026 Gabriel Thullen
Lizenziert unter der GNU General Public License v3 (GPLv3)
GitHub: https://github.com/Gabe1290/pythongm
