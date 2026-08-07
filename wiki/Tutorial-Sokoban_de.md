# Tutorial: Erstellen Sie ein Sokoban-Puzzlespiel

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Sokoban) | [Français](Tutorial-Sokoban_fr) | [Deutsch](Tutorial-Sokoban_de) | [Italiano](Tutorial-Sokoban_it) | [Español](Tutorial-Sokoban_es) | [Português](Tutorial-Sokoban_pt) | [Slovenščina](Tutorial-Sokoban_sl) | [Українська](Tutorial-Sokoban_uk) | [Русский](Tutorial-Sokoban_ru)

---

## Einführung

In diesem Tutorial erstellen Sie ein **Sokoban**-Puzzlespiel - ein klassisches Kisten-Schiebe-Puzzle, bei dem der Spieler alle Kisten auf Zielfelder schieben muss. Sokoban (was "Lagerverwalter" auf Japanisch bedeutet) ist perfekt zum Lernen von gitterbasierter Bewegung und Puzzle-Spiellogik.

**Was Sie lernen werden:**
- Gitterbasierte Bewegung (Bewegung in festen Schritten)
- Schiebemechaniken zum Bewegen von Objekten
- Kollisionserkennung mit mehreren Objekttypen
- Erkennung der Gewinnbedingung
- Leveldesign für Puzzlespiele

**Schwierigkeitsgrad:** Anfänger
**Preset:** Fortgeschrittenen-Preset (die hier verwendete Schiebemechanik und
gitterbasierte Bewegung sind nicht im Anfänger-Preset enthalten)

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
| **Spieler** | Der Lagerverwalter, den Sie steuern |
| **Kiste** | Kartons, die der Spieler schiebt |
| **Wand** | Feste Hindernisse, die die Bewegung blockieren |
| **Ziel** | Zielfelder, auf die Kisten platziert werden müssen |
| **Boden** | Begehbarer Untergrund (optional, nur visuell) |

---

## Schritt 2: Erstellen Sie die Sprites

Alle Sprites sollten die gleiche Größe haben (32x32 Pixel funktioniert gut), um ein ordentliches Gitter zu erzeugen.

### 2.1 Spieler-Sprite

1. Klicken Sie im **Ressourcenbaum** mit der rechten Maustaste auf **Sprites** und wählen Sie **Sprite erstellen**
2. Nennen Sie es `spr_player`
3. Klicken Sie auf **Sprite bearbeiten**, um den Sprite-Editor zu öffnen
4. Zeichnen Sie eine einfache Figur (eine Person oder Roboterform)
5. Verwenden Sie eine deutliche Farbe wie Blau oder Grün
6. Größe: 32x32 Pixel
7. Klicken Sie auf **OK**, um zu speichern

### 2.2 Kisten-Sprite

1. Erstellen Sie ein neues Sprite mit dem Namen `spr_crate`
2. Zeichnen Sie eine Holzkiste
3. Verwenden Sie braune oder orangefarbene Töne
4. Größe: 32x32 Pixel

### 2.3 Sprite für Kiste auf Ziel

1. Erstellen Sie ein neues Sprite mit dem Namen `spr_crate_ok`
2. Zeichnen Sie dieselbe Kiste, aber in einer anderen Farbe (grün), um zu zeigen, dass sie richtig platziert ist
3. Größe: 32x32 Pixel

### 2.4 Wand-Sprite

1. Erstellen Sie ein neues Sprite mit dem Namen `spr_wall`
2. Zeichnen Sie ein durchgehendes Ziegel- oder Steinmuster
3. Verwenden Sie graue oder dunkle Farben
4. Größe: 32x32 Pixel

### 2.5 Ziel-Sprite

1. Erstellen Sie ein neues Sprite mit dem Namen `spr_target`
2. Zeichnen Sie ein X-Zeichen oder eine Zielmarkierung
3. Verwenden Sie eine kräftige Farbe wie Rot oder Gelb
4. Größe: 32x32 Pixel

### 2.6 Boden-Sprite (Optional)

1. Erstellen Sie ein neues Sprite mit dem Namen `spr_floor`
2. Zeichnen Sie ein einfaches Bodenfliesenmuster
3. Verwenden Sie eine neutrale Farbe
4. Größe: 32x32 Pixel

---

## Schritt 3: Erstellen Sie das Wand-Objekt

Die Wand ist das einfachste Objekt - sie blockiert einfach die Bewegung.

1. Klicken Sie mit der rechten Maustaste auf **Objects** und wählen Sie **Create Object**
2. Nennen Sie es `obj_wall`
3. Setzen Sie das Sprite auf `spr_wall`
4. **Aktivieren Sie das Kontrollkästchen "Solid"**
5. Keine Ereignisse nötig

---

## Schritt 4: Erstellen Sie das Ziel-Objekt

Ziele markieren, wo Kisten platziert werden sollen.

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_target`
2. Setzen Sie das Sprite auf `spr_target`
3. Keine Ereignisse nötig - es ist nur eine Markierung
4. Lassen Sie "Solid" deaktiviert (Spieler und Kisten können darüber stehen)

---

## Schritt 5: Erstellen Sie das Kisten-Objekt

Die Kiste wird vom Spieler geschoben und ändert ihr Aussehen, wenn sie auf einem Ziel steht.

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_crate`
2. Setzen Sie das Sprite auf `spr_crate`
3. **Aktivieren Sie das Kontrollkästchen "Solid"**

**Ereignis: Step**
1. Add Event → Step → Step
2. Add Action: **Control** → **If Collision**
   - X Offset: `0`
   - Y Offset: `0`
   - Against: `obj_target`
3. Add Action: **Instance** → **Set Sprite**
   - Sprite: `spr_crate_ok`
4. Add Action: **Control** → **Else**
5. Add Action: **Instance** → **Set Sprite**
   - Sprite: `spr_crate`

Dadurch wird die Kiste grün, sobald sie auf einem Zielfeld steht — **If
Collision** mit beiden Versätzen auf `0` prüft, ob die *aktuelle* Position
der Kiste ein `obj_target` überlappt.

---

## Schritt 6: Erstellen Sie das Spieler-Objekt

Der Spieler bewegt sich immer genau eine Gitterzelle weit und schiebt Kisten, in die er hineinläuft.

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_player`
2. Setzen Sie das Sprite auf `spr_player`

### 6.1 Gitterbewegung

Fügen Sie ein **Key Press**-Ereignis pro Richtung hinzu, jeweils mit einer **Move** → **Move Grid**-Aktion:

| Ereignis | Move-Grid-Aktion |
|---|---|
| Key Press → Right Arrow | Direction: `right`, Grid Size: `32` |
| Key Press → Left Arrow | Direction: `left`, Grid Size: `32` |
| Key Press → Up Arrow | Direction: `up`, Grid Size: `32` |
| Key Press → Down Arrow | Direction: `down`, Grid Size: `32` |

**Move Grid** bewegt die Instanz exakt eine Gitterzelle weit und erkennt
dabei selbstständig Kollisionen — es bewegt den Spieler nicht in eine
solide `obj_wall` hinein, daher ist hier keine zusätzliche Wandprüfung nötig.

### 6.2 An Wänden stoppen

**Ereignis: Collision with obj_wall**
1. Add Event → Collision → `obj_wall`
2. Add Action: **Move** → **Stop Movement**

### 6.3 Kisten schieben

**Ereignis: Collision with obj_crate**
1. Add Event → Collision → `obj_crate`
2. Add Action: **Control** → **If Can Push**
   - Direction: `facing`
   - Object Type: `obj_crate`
   - Then Action: `push_and_move`

**If Can Push** prüft, ob der Platz hinter der Kiste (in der Richtung, in
die sich der Spieler bewegt) frei ist, und schiebt — falls ja — die Kiste
um eine Zelle weiter und bewegt den Spieler an ihre bisherige Stelle,
alles in einer einzigen Aktion. Ist der Platz hinter der Kiste durch eine
Wand oder eine andere Kiste blockiert, bewegt sich nichts.

---

## Schritt 7: Erstellen Sie die Gewinnbedingungsprüfung

Wir brauchen einen unsichtbaren Controller, der überwacht, ob sich jede Kiste auf einem Ziel befindet.

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_game_controller`
2. Kein Sprite nötig

**Ereignis: Create** — die Zielanzahl einmalig ermitteln, mit **Control** →
**Execute Code** (die Execute-Code-Aktion dieses Projekts führt echtes
Python aus, keine GameMaker Language — `self` ist die aktuelle Instanz,
`game` ist der Game Runner):

```python
# Zählt, wie viele Zielfelder sich im Room befinden
self.total_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_target'
)
```

**Ereignis: Step** — bei jedem Frame prüfen, ob alle Kisten auf einem Ziel stehen:

```python
# Zählt Kisten, die aktuell ein Zielfeld überlappen
crates_on_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_crate'
    and game.check_collision_at_position(inst, inst.x, inst.y, 'obj_target')
)

if self.total_targets > 0 and crates_on_targets >= self.total_targets:
    self.restart_room_flag = True
```

`self.restart_room_flag = True` löst denselben Room-Neustart aus, den auch
die **Restart Room**-Aktion durchführt — die Hauptschleife prüft dieses
Flag bei jedem Frame. Fügen Sie direkt nach dem Execute-Code-Block eine
**Show Message**-Aktion (aus **Output**, Nachricht `Level Complete!`)
hinzu, wenn Sie vor dem Neustart ein Popup anzeigen möchten.

**Ereignis: Draw**
1. Add Event → Draw
2. Add Action: **Draw** → **Draw Text**
   - Text: `Sokoban - Push all crates to targets!`
   - X: `10`
   - Y: `10`

---

## Schritt 9: Entwerfen Sie Ihr Level

1. Klicken Sie mit der rechten Maustaste auf **Rooms** und wählen Sie **Create Room**
2. Nennen Sie es `room_level1`
3. Setzen Sie die Room-Größe auf ein Vielfaches von 32 (z. B. 640x480)
4. Aktivieren Sie "Snap to Grid" und setzen Sie das Gitter auf 32x32

### Objekte platzieren

Bauen Sie Ihr Level nach diesen Richtlinien:

1. **Umgeben Sie das Level mit Wänden** - Erstellen Sie eine Umrandung
2. **Fügen Sie innere Wände hinzu** - Erstellen Sie die Rätselstruktur
3. **Platzieren Sie Ziele** - Wo Kisten hin sollen
4. **Platzieren Sie Kisten** - Gleiche Anzahl wie Ziele!
5. **Platzieren Sie den Spieler** - Startposition
6. **Platzieren Sie den Game Controller** - Beliebige Stelle (er ist unsichtbar)

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

**Wichtig:** Achten Sie immer darauf, dieselbe Anzahl an Kisten und Zielen zu haben!

---

## Schritt 10: Testen Sie Ihr Spiel!

1. Klicken Sie auf **Run** oder drücken Sie **F5**, um zu testen
2. Bewegen Sie sich mit den Pfeiltasten
3. Schieben Sie Kisten auf die roten X-Ziele
4. Wenn alle Kisten auf Zielen stehen, gewinnen Sie!

---

## Verbesserungen (Optional)

### Zugzähler hinzufügen

Fügen Sie im **Create**-Ereignis von `obj_game_controller` **Control** →
**Set Variable** hinzu (Variable: `global.moves`, Value: `0`, Scope: `global`).

Fügen Sie in jedem der vier Key-Press-Ereignisse von `obj_player` direkt
nach Move Grid eine zweite Aktion hinzu: **Control** → **Set Variable**
(Variable: `global.moves`, Value: `1`, Scope: `global`, **Relative**
aktiviert) — dies addiert bei jedem Tastendruck 1 zum Zähler, unabhängig
davon, ob die Bewegung tatsächlich durch eine Wand blockiert wurde.

Fügen Sie im **Draw**-Ereignis von `obj_game_controller` **Draw** →
**Draw Variable** hinzu (Variable: `global.moves`, X: `10`, Y: `30`).

### Undo-Funktion hinzufügen

Speichern Sie vorherige Positionen und ermöglichen Sie es, mit Z den letzten Zug rückgängig zu machen.

### Mehrere Level hinzufügen

Erstellen Sie weitere Rooms (`room_level2`, `room_level3` usw.) und
verwenden Sie im Gewinnprüfungs-Codeblock die **Next Room**-Aktion
(Kategorie Room) statt **Restart Room** (`self.next_room_flag = True`
statt `self.restart_room_flag = True`), wenn ein Level abgeschlossen wird.

### Soundeffekte hinzufügen

Fügen Sie Sounds hinzu für:
- Spielerbewegung
- Kiste schieben
- Kiste landet auf Ziel
- Level abgeschlossen

---

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| Spieler geht durch Wände | Prüfen Sie, ob `obj_wall` "Solid" aktiviert hat |
| Kiste ändert die Farbe nicht | Prüfen Sie, ob die **If Collision**-Aktion im Step-Ereignis auf `obj_target` zielt |
| Kiste kann durch Wand geschoben werden | Kollisionserkennung vor dem Verschieben der Kiste prüfen |
| Gewinnmeldung erscheint sofort | Stellen Sie sicher, dass Ziele getrennt von Kisten platziert sind |
| Spieler bewegt sich mehrere Felder | Verwenden Sie das Keyboard-Press-Ereignis, nicht das Keyboard-Ereignis |

---

## Was Sie gelernt haben

Glückwunsch! Sie haben ein vollständiges Sokoban-Puzzlespiel erstellt! Sie haben gelernt:

- **Gitterbasierte Bewegung** - Bewegung in festen 32-Pixel-Schritten
- **Schiebemechaniken** - Erkennung und Bewegung von Objekten, die der Spieler schiebt
- **Komplexe Kollisionslogik** - Prüfung mehrerer Bedingungen vor einer Bewegung
- **Statuswechsel** - Sprite-Änderung abhängig von der Objektposition
- **Gewinnbedingungen** - Prüfung, wann alle Ziele erreicht sind
- **Leveldesign** - Erstellung lösbarer Puzzle-Layouts

---

## Herausforderung: Entwerfen Sie Ihre eigenen Level!

Der wahre Spaß an Sokoban liegt im Entwerfen von Rätseln. Versuchen Sie, Level zu erstellen, die:
- Leicht beginnen und zunehmend schwieriger werden
- Vorausplanung erfordern
- Nur eine Lösung haben
- Den Platz effizient nutzen

Denken Sie daran: Ein gutes Sokoban-Rätsel sollte herausfordernd, aber fair sein!

---

## Siehe auch

- [Tutorials](Tutorials_de) - Weitere Spiel-Tutorials
- [Fortgeschrittenen-Preset](Intermediate-Preset_de) - Übersicht des für dieses Tutorial nötigen Presets
- [Tutorial: Pong](Tutorial-Pong_de) - Erstellen Sie ein Zwei-Spieler-Spiel
- [Tutorial: Breakout](Tutorial-Breakout_de) - Erstellen Sie ein Ziegelstein-Spiel
- [Event-Referenz](Event-Reference_de) - Vollständige Ereignisdokumentation
