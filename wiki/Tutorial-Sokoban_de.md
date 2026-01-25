# Tutorial: Erstellen Sie ein Sokoban-Puzzlespiel

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Sokoban) | [Français](Tutorial-Sokoban_fr) | [Deutsch](Tutorial-Sokoban_de) | [Italiano](Tutorial-Sokoban_it) | [Español](Tutorial-Sokoban_es) | [Português](Tutorial-Sokoban_pt) | [Slovenščina](Tutorial-Sokoban_sl) | [Українська](Tutorial-Sokoban_uk) | [Русский](Tutorial-Sokoban_ru)

---

## Einführung

In diesem Tutorial erstellen Sie ein **Sokoban**-Puzzlespiel - ein klassisches Kisten-Schiebe-Puzzle, bei dem der Spieler alle Kisten auf Zielfelder schieben muss. Sokoban (was "Lagerverwalter" im Japanischen bedeutet) ist perfekt zum Lernen von gitterbasierter Bewegung und Puzzle-Spiellogik.

**Was Sie lernen werden:**
- Gitterbasierte Bewegung (Bewegung in festen Schritten)
- Schiebemechaniken zum Bewegen von Objekten
- Kollisionserkennung mit mehreren Objekttypen
- Erkennungsbedingung zum Gewinnen
- Leveldesign für Puzzlespiele

**Schwierigkeitsgrad:** Anfänger
**Voreinstellung:** Anfänger-Voreinstellung

---

## Schritt 1: Das Spiel verstehen

### Spielregeln
1. Der Spieler kann sich nach oben, unten, links oder rechts bewegen
2. Der Spieler kann Kisten schieben (aber nicht ziehen)
3. Es kann jeweils nur eine Kiste geschoben werden
4. Kisten können nicht durch Wände oder andere Kisten geschoben werden
5. Das Level ist abgeschlossen, wenn sich alle Kisten auf Zielfeldern befinden

### Was wir brauchen

| Element | Zweck |
|---------|-------|
| **Spieler** | Der Lagerverwalter, den Sie kontrollieren |
| **Kiste** | Kartons, die der Spieler schiebt |
| **Wand** | Feste Hindernisse, die die Bewegung blockieren |
| **Ziel** | Zielfelder, auf die Kisten platziert werden müssen |
| **Boden** | Begehbarer Untergrund (optional visuell) |

---

## Schritt 2: Erstellen Sie die Grafiken

Alle Grafiken sollten die gleiche Größe haben (32x32 Pixel funktioniert gut), um ein ordnungsgemäßes Gitter zu erstellen.

### 2.1 Spieler-Grafik

1. Klicken Sie im **Ressourcenbaum** mit der rechten Maustaste auf **Grafiken** und wählen Sie **Grafik erstellen**
2. Geben Sie ihr den Namen `spr_player`
3. Klicken Sie auf **Grafik bearbeiten**, um den Grafik-Editor zu öffnen
4. Zeichnen Sie einen einfachen Charakter (eine Person oder Roboterform)
5. Verwenden Sie eine deutliche Farbe wie Blau oder Grün
6. Größe: 32x32 Pixel
7. Klicken Sie auf **OK**, um zu speichern

### 2.2 Kisten-Grafik

1. Erstellen Sie eine neue Grafik mit dem Namen `spr_crate`
2. Zeichnen Sie eine Holzkiste oder Kastenform
3. Verwenden Sie braune oder orange Farben
4. Größe: 32x32 Pixel

### 2.3 Kiste auf Ziel-Grafik

1. Erstellen Sie eine neue Grafik mit dem Namen `spr_crate_ok`
2. Zeichnen Sie die gleiche Kiste, aber mit einer anderen Farbe (grün), um zu zeigen, dass sie richtig platziert ist
3. Größe: 32x32 Pixel

### 2.4 Wand-Grafik

1. Erstellen Sie eine neue Grafik mit dem Namen `spr_wall`
2. Zeichnen Sie ein solides Ziegel- oder Steinmuster
3. Verwenden Sie graue oder dunkle Farben
4. Größe: 32x32 Pixel

### 2.5 Ziel-Grafik

1. Erstellen Sie eine neue Grafik mit dem Namen `spr_target`
2. Zeichnen Sie ein X-Zeichen oder einen Zielindikator
3. Verwenden Sie eine lebendige Farbe wie Rot oder Gelb
4. Größe: 32x32 Pixel

### 2.6 Boden-Grafik (Optional)

1. Erstellen Sie eine neue Grafik mit dem Namen `spr_floor`
2. Zeichnen Sie ein einfaches Bodenfliesen-Muster
3. Verwenden Sie eine neutrale Farbe
4. Größe: 32x32 Pixel

---

## Schritt 3: Erstellen Sie das Wand-Objekt

Die Wand ist das einfachste Objekt - sie blockiert einfach die Bewegung.

1. Klicken Sie mit der rechten Maustaste auf **Objekte** und wählen Sie **Objekt erstellen**
2. Geben Sie ihm den Namen `obj_wall`
3. Setzen Sie die Grafik auf `spr_wall`
4. **Aktivieren Sie das Kontrollkästchen "Solid"**
5. Keine Ereignisse erforderlich

---

## Schritt 4: Erstellen Sie das Ziel-Objekt

Ziele markieren, wo Kisten platziert werden sollen.

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_target`
2. Setzen Sie die Grafik auf `spr_target`
3. Keine Ereignisse erforderlich - es ist nur ein Markierungsfeld
4. Lassen Sie "Solid" deaktiviert (Spieler und Kisten können darauf sein)

---

## Schritt 5: Erstellen Sie das Kisten-Objekt

Die Kiste wird vom Spieler geschoben und ändert ihr Aussehen, wenn sie sich auf einem Zielfeld befindet.

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_crate`
2. Setzen Sie die Grafik auf `spr_crate`
3. **Aktivieren Sie das Kontrollkästchen "Solid"**

**Ereignis: Schritt**
1. Ereignis hinzufügen → Schritt → Schritt
2. Aktion hinzufügen: **Steuerung** → **Variable testen**
   - Variable: `place_meeting(x, y, obj_target)`
   - Wert: `1`
   - Operation: Gleich
3. Aktion hinzufügen: **Main1** → **Grafik wechseln**
   - Grafik: `spr_crate_ok`
   - Unterbild: `0`
   - Geschwindigkeit: `1`
4. Aktion hinzufügen: **Steuerung** → **Sonst**
5. Aktion hinzufügen: **Main1** → **Grafik wechseln**
   - Grafik: `spr_crate`
   - Unterbild: `0`
   - Geschwindigkeit: `1`

Dies lässt die Kiste grün werden, wenn sie sich auf einem Zielfeld befindet.

---

## Schritt 6: Erstellen Sie das Spieler-Objekt

Der Spieler ist das komplexeste Objekt mit gitterbasierter Bewegung und Schiebemechaniken.

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_player`
2. Setzen Sie die Grafik auf `spr_player`

### 6.1 Nach rechts bewegen

**Ereignis: Tastatur Nach-rechts-Pfeiltaste drücken**
1. Ereignis hinzufügen → Tastatur → Nach rechts drücken

Überprüfen Sie zunächst, ob eine Wand im Weg ist:
2. Aktion hinzufügen: **Steuerung** → **Kollision testen**
   - Objekt: `obj_wall`
   - X: `32`
   - Y: `0`
   - Prüfen: NICHT (was bedeutet "wenn es KEINE Wand gibt")

Falls keine Wand vorhanden ist, überprüfen Sie, ob es eine Kiste gibt:
3. Aktion hinzufügen: **Steuerung** → **Kollision testen**
   - Objekt: `obj_crate`
   - X: `32`
   - Y: `0`

Falls es eine Kiste gibt, müssen wir überprüfen, ob wir sie schieben können:
4. Aktion hinzufügen: **Steuerung** → **Kollision testen** (für das Zielfeld der Kiste)
   - Objekt: `obj_wall`
   - X: `64`
   - Y: `0`
   - Prüfen: NICHT

5. Aktion hinzufügen: **Steuerung** → **Kollision testen**
   - Objekt: `obj_crate`
   - X: `64`
   - Y: `0`
   - Prüfen: NICHT

Falls beide Überprüfungen bestanden sind, schieben Sie die Kiste:
6. Aktion hinzufügen: **Steuerung** → **Codeblock**
```
var crate = instance_place(x + 32, y, obj_crate);
if (crate != noone) {
    crate.x += 32;
}
```

Jetzt bewegen Sie den Spieler:
7. Aktion hinzufügen: **Bewegung** → **Zu Position springen**
   - X: `32`
   - Y: `0`
   - Markieren Sie "Relativ"

### 6.2 Nach links bewegen

**Ereignis: Tastatur Nach-links-Pfeiltaste drücken**
Folgen Sie dem gleichen Muster wie das Bewegen nach rechts, verwenden Sie aber:
- X-Versatz: `-32` zum Überprüfen von Wand/Kiste
- X-Versatz: `-64` zum Überprüfen, ob die Kiste geschoben werden kann
- Kiste um `-32` verschieben
- Zu Position X springen: `-32`

### 6.3 Nach oben bewegen

**Ereignis: Tastatur Nach-oben-Pfeiltaste drücken**
Folgen Sie dem gleichen Muster, verwenden Sie aber Y-Werte:
- Y-Versatz: `-32` zum Überprüfen
- Y-Versatz: `-64` für das Zielfeld der Kiste
- Kiste um Y verschieben: `-32`
- Zu Position Y springen: `-32`

### 6.4 Nach unten bewegen

**Ereignis: Tastatur Nach-unten-Pfeiltaste drücken**
Verwenden Sie:
- Y-Versatz: `32` zum Überprüfen
- Y-Versatz: `64` für das Zielfeld der Kiste
- Kiste um Y verschieben: `32`
- Zu Position Y springen: `32`

---

## Schritt 7: Vereinfachte Spielerbewegung (Alternative)

Falls der blockbasierte Ansatz oben komplex zu sein scheint, hier ist ein einfacherer codebasierter Ansatz für jede Richtung:

**Ereignis: Tastatur Nach-rechts-Pfeiltaste drücken**
Aktion hinzufügen: **Steuerung** → **Code ausführen**
```
// Überprüfen Sie, ob wir nach rechts gehen können
if (!place_meeting(x + 32, y, obj_wall)) {
    // Überprüfen Sie, ob es eine Kiste gibt
    var crate = instance_place(x + 32, y, obj_crate);
    if (crate != noone) {
        // Es gibt eine Kiste - können wir sie schieben?
        if (!place_meeting(x + 64, y, obj_wall) && !place_meeting(x + 64, y, obj_crate)) {
            crate.x += 32;
            x += 32;
        }
    } else {
        // Keine Kiste, einfach bewegen
        x += 32;
    }
}
```

Wiederholen Sie dies für andere Richtungen mit entsprechenden Koordinatenänderungen.

---

## Schritt 8: Erstellen Sie die Gewinnbedingungsprüfer

Wir benötigen ein Objekt, um zu überprüfen, ob sich alle Kisten auf Zielfeldern befinden.

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_game_controller`
2. Keine Grafik erforderlich

**Ereignis: Erstellen**
1. Ereignis hinzufügen → Erstellen
2. Aktion hinzufügen: **Punktestand** → **Variable einstellen**
   - Variable: `global.total_targets`
   - Wert: `0`
3. Aktion hinzufügen: **Steuerung** → **Code ausführen**
```
// Zählen Sie, wie viele Ziele existieren
global.total_targets = instance_number(obj_target);
```

**Ereignis: Schritt**
1. Ereignis hinzufügen → Schritt → Schritt
2. Aktion hinzufügen: **Steuerung** → **Code ausführen**
```
// Zählen Sie Kisten, die sich auf Zielen befinden
var crates_on_targets = 0;
with (obj_crate) {
    if (place_meeting(x, y, obj_target)) {
        crates_on_targets += 1;
    }
}

// Überprüfen Sie, ob alle Ziele Kisten haben
if (crates_on_targets >= global.total_targets && global.total_targets > 0) {
    // Level abgeschlossen!
    show_message("Level abgeschlossen!");
    room_restart();
}
```

**Ereignis: Zeichnen**
1. Ereignis hinzufügen → Zeichnen
2. Aktion hinzufügen: **Zeichnen** → **Text zeichnen**
   - Text: `Sokoban - Schieben Sie alle Kisten zu den Zielen!`
   - X: `10`
   - Y: `10`

---

## Schritt 9: Entwerfen Sie Ihren Level

1. Klicken Sie mit der rechten Maustaste auf **Zimmer** und wählen Sie **Zimmer erstellen**
2. Geben Sie ihm den Namen `room_level1`
3. Setzen Sie die Zimmergröße auf ein Vielfaches von 32 (z. B. 640x480)
4. Aktivieren Sie "An Gitter ausrichten" und setzen Sie das Gitter auf 32x32

### Platzierung von Objekten

Bauen Sie Ihren Level nach diesen Richtlinien:

1. **Umgeben Sie den Level mit Wänden** - Erstellen Sie einen Rahmen
2. **Fügen Sie interne Wände hinzu** - Erstellen Sie die Rätselstruktur
3. **Platzieren Sie Ziele** - Wo Kisten hin müssen
4. **Platzieren Sie Kisten** - Gleiche Anzahl wie Ziele!
5. **Platzieren Sie den Spieler** - Startposition
6. **Platzieren Sie den Spielkontroller** - Überall (er ist unsichtbar)

### Beispiel-Levellayout

```
W W W W W W W W W W
W . . . . . . . . W
W . P . . . C . . W
W . . W W . . . . W
W . . W T . . C . W
W . . . . . W W . W
W . T . . . . . . W
W . . . . . . . . W
W W W W W W W W W W

W = Wand
P = Spieler
C = Kiste
T = Ziel
. = Leerer Boden
```

**Wichtig:** Stellen Sie immer sicher, dass Sie die gleiche Anzahl von Kisten und Zielen haben!

---

## Schritt 10: Testen Sie Ihr Spiel!

1. Klicken Sie auf **Ausführen** oder drücken Sie **F5**, um zu testen
2. Verwenden Sie Pfeiltasten, um sich zu bewegen
3. Schieben Sie Kisten auf die roten X-Ziele
4. Wenn sich alle Kisten auf Zielen befinden, gewinnen Sie!

---

## Verbesserungen (Optional)

### Fügen Sie einen Zählschaltbesucher hinzu

In `obj_game_controller`:

**Ereignis: Erstellen** - Fügen Sie hinzu:
```
global.moves = 0;
```

In `obj_player`, nach jedem erfolgreichen Zug, fügen Sie hinzu:
```
global.moves += 1;
```

In `obj_game_controller` **Ereignis: Zeichnen** - Fügen Sie hinzu:
```
draw_text(10, 30, "Moves: " + string(global.moves));
```

### Fügen Sie eine Rückgängig-Funktion hinzu

Speichern Sie vorherige Positionen und ermöglichen Sie es, Z zu drücken, um den letzten Zug rückgängig zu machen.

### Fügen Sie mehrere Level hinzu

Erstellen Sie mehr Zimmer (`room_level2`, `room_level3`, etc.) und verwenden Sie:
```
room_goto_next();
```
statt `room_restart()` nach dem Abschließen eines Levels.

### Fügen Sie Soundeffekte hinzu

Fügen Sie Sounds für hinzu:
- Spieler bewegt sich
- Kiste schieben
- Kiste landet auf Ziel
- Level abgeschlossen

---

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| Spieler geht durch Wände | Überprüfen Sie, ob `obj_wall` "Solid" aktiviert hat |
| Kiste ändert die Farbe nicht | Überprüfen Sie, ob das Schritt-Ereignis `place_meeting` korrekt kontrolliert |
| Kiste kann durch Wand geschoben werden | Überprüfen Sie die Kollisionserkennung vor dem Verschieben der Kiste |
| Gewinnmeldung erscheint sofort | Stellen Sie sicher, dass Ziele separate von Kisten platziert werden |
| Spieler bewegt mehrere Felder | Verwenden Sie das Ereignis "Tastatur drücken", nicht "Tastatur" |

---

## Was Sie gelernt haben

Glückwunsch! Sie haben ein vollständiges Sokoban-Puzzlespiel erstellt! Sie haben gelernt:

- **Gitterbasierte Bewegung** - Bewegung in festen 32-Pixel-Schritten
- **Schiebemechaniken** - Erkennung und Bewegung von Objekten, die der Spieler schiebt
- **Komplexe Kollisionslogik** - Überprüfung mehrerer Bedingungen vor der Zulassung einer Bewegung
- **Statusänderungen** - Änderung der Grafik basierend auf der Objektposition
- **Gewinnbedingungen** - Überprüfung, wenn alle Ziele erreicht sind
- **Leveldesign** - Erstellung lösbarer Puzzle-Layouts

---

## Herausforderung: Entwerfen Sie Ihre eigenen Level!

Der wahre Spaß bei Sokoban liegt im Entwerfen von Rätseln. Versuchen Sie, Level zu erstellen, die:
- Einfach anfangen und progressiv schwieriger werden
- Vorausplanung erfordern
- Nur eine Lösung haben
- Den Platz effizient nutzen

Denken Sie daran: Ein gutes Sokoban-Puzzle sollte herausfordernd aber fair sein!

---

## Siehe auch

- [Tutorials](Tutorials_de) - Weitere Spiel-Tutorials
- [Anfänger-Voreinstellung](Beginner-Preset_de) - Übersicht der Anfänger-Funktionen
- [Tutorial: Pong](Tutorial-Pong_de) - Erstellen Sie ein Zwei-Spieler-Spiel
- [Tutorial: Breakout](Tutorial-Breakout_de) - Erstellen Sie ein Brick-Breaker-Spiel
- [Ereignis-Referenz](Event-Reference_de) - Vollständige Ereignisdokumentation
