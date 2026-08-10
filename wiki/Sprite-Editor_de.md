# Sprite-Editor

> [English](Sprite-Editor) | [Français](Sprite-Editor_fr) | [Deutsch](Sprite-Editor_de) | [Italiano](Sprite-Editor_it) | [Español](Sprite-Editor_es)

---

> [Zurück zur Startseite](Home_de)

Sprites sind die Bilder und Animationen, die an Objekte angehängt werden.
Der Sprite-Editor ist ein eingebautes Pixel-Art-Werkzeug — zeichnen Sie
Sprites direkt in PyGameMaker, kein externer Bildeditor nötig.

---

## Den Sprite-Editor öffnen

1. Doppelklicken Sie auf ein vorhandenes Sprite im Ressourcenbaum, oder
2. Rechtsklick auf **Sprites** > **Sprite erstellen**

![Der Sprite-Editor: Zeichenwerkzeuge und Pinselgröße links, darunter die
Ursprungsauswahl und die Option Precise Collision, eine Farbpalette, die
Zeichenfläche in der Mitte mit einer Pixel-Art-Figur bei 10-facher
Vergrößerung, und der Bilderstreifen unten (8 Bilder, Play-Button,
Bild hinzufügen/duplizieren/löschen)](images/sprite-editor.png)

---

## Zeichenwerkzeuge

| Werkzeug | Tastenkürzel | Was es tut |
|------|----------|---------------|
| **Stift** | P | Einzelne Pixel zeichnen |
| **Radiergummi** | E | Pixel transparent löschen |
| **Pipette** | I | Eine Farbe von der Zeichenfläche aufnehmen |
| **Füllen** | G | Zusammenhängenden Bereich füllen (Eimer) |
| **Linie** | L | Eine gerade Linie zeichnen |
| **Rechteck** | R | Ein Rechteck zeichnen (**Gefüllt** umschalten für voll/Umriss) |
| **Ellipse** | O | Eine Ellipse zeichnen (beachtet ebenfalls **Gefüllt**) |
| **Auswahl** | S | Rechteckige Auswahl — verschieben, kopieren, ausschneiden, einfügen oder die ausgewählten Pixel löschen |

**Die Pinselgröße** gilt für Stift, Radiergummi und die Umrisse von
Linien/Formen. Die Farbpalette enthält einen Arbeitsfarbensatz sowie die
Standard-Schnellpalette mit 12 Farben; klicken Sie auf ein Farbfeld zum
Auswählen, oder verwenden Sie die Pipette, um eine Farbe direkt vom
Sprite abzunehmen.

---

## Aktionen auf der Zeichenfläche

- **Horizontal spiegeln / Vertikal spiegeln** — spiegelt das aktuelle Bild horizontal oder vertikal
- **Größe ändern** — öffnet einen Dialog mit zwei unterschiedlichen Modi:
  - **Bild skalieren** — streckt den vorhandenen Inhalt auf eine neue Größe
  - **Leinwand anpassen** — behält den Inhalt in seiner ursprünglichen Größe und fügt Platz hinzu/schneidet ihn ab, verankert an einer Ecke, Kante oder der Mitte nach Wahl
- **Raster** — schaltet ein Pixelraster-Overlay um (wirkt sich nicht auf das gespeicherte Bild aus)
- **Vergrößern / Verkleinern** — die Zeichenfläche arbeitet oft mit 10-facher Vergrößerung oder mehr, da Sprites meist klein sind (16×16 bis 64×64 ist üblich)
- **PNG exportieren…** — speichert das aktuelle Bild als eigenständige `.png`-Datei
- Rechtsklick auf die Zeichenfläche für **Kopieren / Ausschneiden / Einfügen / Löschen / Auswahl aufheben / Alles auswählen** (Standard-Tastenkürzel: Strg+C / Strg+X / Strg+V / Entf / Esc)

---

## Bilder und Animation

Ein Sprite kann mehrere Bilder enthalten, die zur Laufzeit als Animation
abgespielt werden. Der Bilderstreifen am unteren Rand des Editors:

| Steuerung | Effekt |
|---------|--------|
| **+** | Ein neues leeres Bild hinzufügen |
| **D** | Das aktuelle Bild duplizieren |
| **-** | Das aktuelle Bild löschen |
| **Play** | Die Animation im Editor mit der Bildrate des Sprites abspielen |

Klicken Sie auf eine Bild-Miniaturansicht, um dorthin zu springen und
gezielt auf diesem Bild zu zeichnen.

---

## Ursprung und Kollision

- **Ursprung (Origin)** — der Punkt, den Objekte mit diesem Sprite als
  ihre Position `(x, y)` behandeln. Voreinstellungen: Oben-Links,
  Oben-Mitte, Mitte, Mitte-Unten, Unten-Links, Unten-Rechts, oder
  **Benutzerdefiniert** (genaue X/Y). Die meisten Plattformer-/
  Top-Down-Figuren verwenden **Mitte-Unten**, damit die Füße des Sprites
  auf der Y-Position des Objekts sitzen.
- **Precise Collision** — aktiviert, prüfen Kollisionen mit diesem Sprite
  die tatsächlichen nicht-transparenten Pixel statt der Bounding-Box des
  Sprites. Genauer bei unregelmäßig geformten Sprites, aufwendiger zu
  berechnen — lassen Sie es bei einfachen Formen (Wände, Münzen)
  deaktiviert und setzen Sie es dort ein, wo eine Bounding-Box-Kollision
  sichtbar falsch wirken würde.

---

## Nächste Schritte

- [[Objekt_Editor_de|Objekt-Editor]] - Ein Sprite an ein Spielobjekt anhängen
- [[Raum_Editor_de|Raum-Editor]] - Objektinstanzen platzieren, die Ihr Sprite verwenden
- [[Erstes_Spiel_de|Ihr Erstes Spiel]] - Ein vollständiges Tutorial, das mit dem Zeichnen von Sprites beginnt
