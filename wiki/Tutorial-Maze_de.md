# Tutorial: Ein Labyrinth-Spiel erstellen

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Maze) | [Français](Tutorial-Maze_fr) | [Deutsch](Tutorial-Maze_de) | [Italiano](Tutorial-Maze_it) | [Español](Tutorial-Maze_es) | [Português](Tutorial-Maze_pt) | [Slovenščina](Tutorial-Maze_sl) | [Українська](Tutorial-Maze_uk) | [Русский](Tutorial-Maze_ru)

---

## Einführung

In diesem Tutorial erstellen Sie ein **Labyrinth-Spiel**, in dem der Spieler durch Korridore navigiert, um den Ausgang zu erreichen, während er Hindernissen ausweicht und Münzen sammelt. Dieser klassische Spieltyp ist perfekt, um flüssige Bewegung, Kollisionserkennung und Level-Design zu lernen.

**Was Sie lernen werden:**
- Flüssige Spielerbewegung mit Tastatureingabe
- Wandkollisions-Behandlung
- Zielerkennung (den Ausgang erreichen)
- Sammelbare Gegenstände
- Einfaches Timer-System

**Schwierigkeit:** Anfänger
**Preset:** Fortgeschrittenen-Preset (die für den Timer verwendete
Execute-Code-Aktion ist nicht im Anfänger-Preset enthalten)

---

## Schritt 1: Das Spiel verstehen

### Spielregeln
1. Der Spieler bewegt sich mit den Pfeiltasten durch ein Labyrinth
2. Wände blockieren die Spielerbewegung
3. Sammle Münzen für Punkte
4. Erreiche den Ausgang, um das Level abzuschließen
5. Beende das Labyrinth so schnell wie möglich!

### Was wir brauchen

| Element | Zweck |
|---------|-------|
| **Spieler** | Die Figur, die Sie steuern |
| **Wand** | Solide Hindernisse, die Bewegung blockieren |
| **Ausgang** | Ziel, das das Level beendet |
| **Münze** | Sammelbare Gegenstände für Punkte |
| **Boden** | Visueller Hintergrund (optional) |

---

## Schritt 2: Die Sprites erstellen

Alle Wand- und Boden-Sprites sollten 32x32 Pixel groß sein, um ein korrektes Raster zu erstellen.

### 2.1 Spieler-Sprite

1. Klicken Sie im **Ressourcen-Baum** mit der rechten Maustaste auf **Sprites** und wählen Sie **Sprite erstellen**
2. Nennen Sie es `spr_player`
3. Klicken Sie auf **Sprite bearbeiten**, um den Editor zu öffnen
4. Zeichnen Sie eine kleine Figur (Kreis, Person oder Pfeilform)
5. Verwenden Sie eine helle Farbe wie Blau oder Grün
6. Größe: 24x24 Pixel (kleiner als Wände für einfachere Navigation)
7. Klicken Sie auf **OK** zum Speichern

### 2.2 Wand-Sprite

1. Erstellen Sie ein neues Sprite namens `spr_wall`
2. Zeichnen Sie ein solides Ziegel- oder Steinmuster
3. Verwenden Sie graue oder dunkle Farben
4. Größe: 32x32 Pixel

### 2.3 Ausgang-Sprite

1. Erstellen Sie ein neues Sprite namens `spr_exit`
2. Zeichnen Sie eine Tür, Flagge oder einen leuchtenden Zielmarker
3. Verwenden Sie grüne oder goldene Farben
4. Größe: 32x32 Pixel

### 2.4 Münz-Sprite

1. Erstellen Sie ein neues Sprite namens `spr_coin`
2. Zeichnen Sie einen kleinen gelben/goldenen Kreis
3. Größe: 16x16 Pixel

### 2.5 Boden-Sprite (Optional)

1. Erstellen Sie ein neues Sprite namens `spr_floor`
2. Zeichnen Sie ein einfaches Bodenfliesen-Muster
3. Verwenden Sie eine helle, neutrale Farbe
4. Größe: 32x32 Pixel

---

## Schritt 3: Das Wand-Objekt erstellen

Die Wand blockiert die Spielerbewegung.

1. Klicken Sie mit der rechten Maustaste auf **Objects** und wählen Sie **Create Object**
2. Nennen Sie es `obj_wall`
3. Setzen Sie das Sprite auf `spr_wall`
4. **Aktivieren Sie das Kontrollkästchen "Solid"**
5. Keine Events nötig

---

## Schritt 4: Das Ausgang-Objekt erstellen

Der Ausgang beendet das Level, wenn der Spieler ihn erreicht.

1. Erstellen Sie ein neues Objekt namens `obj_exit`
2. Setzen Sie das Sprite auf `spr_exit`

**Event: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Output** → **Show Message**
   - Message: `You Win!`
3. Add Action: **Room** → **Next Room** (oder **Restart Room** für ein einzelnes Level)

Der Text von Show Message ist eine feste, statische Zeichenkette — er kann
keinen Live-Wert wie die vergangene Zeit einbetten. Der Timer bleibt im HUD
(Schritt 7) bis zum Sieg sichtbar, der Spieler hat seine Zeit also bereits
gesehen.

---

## Schritt 5: Das Münz-Objekt erstellen

Münzen erhöhen den Punktestand, wenn sie gesammelt werden.

1. Erstellen Sie ein neues Objekt namens `obj_coin`
2. Setzen Sie das Sprite auf `spr_coin`

**Event: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Score** → **Set Score**
   - New Score: `10`
   - Aktivieren Sie "Relative", um 10 Punkte hinzuzufügen
3. Add Action: **Main1** → **Destroy Instance**
   - Applies to: Self

---

## Schritt 6: Das Spieler-Objekt erstellen

Der Spieler bewegt sich flüssig mit den Pfeiltasten.

1. Erstellen Sie ein neues Objekt namens `obj_player`
2. Setzen Sie das Sprite auf `spr_player`

### 6.1 Bewegung

Fügen Sie vier **Keyboard (held)**-Events sowie ein **No Key**-Event hinzu,
jeweils mit einer **Move** → **Set Horizontal/Vertical Speed**-Aktion:

| Event | Aktion |
|---|---|
| Keyboard (held) → Right Arrow | Set Horizontal Speed auf `4` |
| Keyboard (held) → Left Arrow | Set Horizontal Speed auf `-4` |
| Keyboard (held) → Down Arrow | Set Vertical Speed auf `4` |
| Keyboard (held) → Up Arrow | Set Vertical Speed auf `-4` |
| Keyboard: No Key | Set Horizontal Speed auf `0` **und** Set Vertical Speed auf `0` |

### 6.2 An Wänden stoppen

**Event: Collision with obj_wall**
1. Add Event → Collision → `obj_wall`
2. Add Action: **Move** → **Stop Movement**

Hier ist kein manueller Positionsprüfungs-Code nötig. Die Bewegungsschleife
dieser Engine verhindert bereits, dass eine Instanz vor dem Zeichnen des
Frames in ein solides Objekt hineinbewegt wird (`obj_wall` ist Solid), der
Spieler kann eine Wand also nie tatsächlich überlappen — das Kollisions-
Event oben setzt lediglich verbleibende Restgeschwindigkeit auf null,
damit der Spieler nicht weiter gegen die Wand "drückt".

---

## Schritt 7: Den Game Controller erstellen

Der Game Controller verwaltet den Timer und zeigt Informationen an.

1. Erstellen Sie ein neues Objekt namens `obj_game_controller`
2. Kein Sprite nötig

**Event: Create** — startet den Timer, mit **Control** → **Execute Code**
(die Execute-Code-Aktion dieses Projekts führt echtes Python aus, keine
GameMaker Language):

```python
self.timer = 0.0
```

**Event: Step** — erhöht ihn bei jedem Frame:

```python
self.timer += 1.0 / game.fps
```

**Event: Draw** — baut das HUD aus echten Draw-Queue-Befehlen auf. Fügen
Sie drei **Draw** → **Draw Text**-Aktionen hinzu:

| Draw-Text-Aktion | Text | Position |
|---|---|---|
| 1. | `Score:` | X `10`, Y `10` |
| 2. | `Time:` | X `10`, Y `30` |
| 3. | `Coins:` | X `10`, Y `50` |

danach drei **Draw** → **Draw Variable**-Aktionen direkt dahinter, um die
Live-Werte neben jeder Beschriftung anzuzeigen:

| Draw-Variable-Aktion | Variable | Position |
|---|---|---|
| 1. | `score` | X `70`, Y `10` |
| 2. | `self.timer` | X `70`, Y `30` |
| 3. | *(siehe unten)* | X `70`, Y `50` |

Es gibt keinen eingebauten "verbleibende Münzen"-Zähler, auf den Draw
Variable zeigen könnte — fügen Sie direkt vor den Draw-Variable-Aktionen
eine weitere **Control** → **Execute Code**-Aktion hinzu, um ihn in eine
Instanzvariable zu berechnen, die Draw Variable dann lesen kann:

```python
self.coins_left = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_coin'
)
```

(setzen Sie danach das Variable-Feld der 3. Draw-Variable-Aktion auf `self.coins_left`).

---

## Schritt 8: Entwerfen Sie Ihr Labyrinth

1. Klicken Sie mit der rechten Maustaste auf **Rooms** und wählen Sie **Create Room**
2. Nennen Sie ihn `room_maze`
3. Setzen Sie die Room-Größe (z. B. 640x480)
4. Aktivieren Sie "Snap to Grid" und setzen Sie das Gitter auf 32x32

### Objekte platzieren

Bauen Sie Ihr Labyrinth nach diesen Richtlinien:

1. **Erstellen Sie den Rand** - Umgeben Sie den Room mit Wänden
2. **Bauen Sie Korridore** - Erstellen Sie Wege durch das Labyrinth
3. **Platzieren Sie den Ausgang** - Setzen Sie ihn ans Ende des Labyrinths
4. **Verteilen Sie Münzen** - Platzieren Sie sie entlang der Wege
5. **Platzieren Sie den Spieler** - Nahe am Eingang
6. **Fügen Sie den Game Controller hinzu** - Irgendwo (er ist unsichtbar)

### Beispiel-Labyrinth-Layout

```
W W W W W W W W W W W W W W W W W W W W
W P . . . . W . . . . . . . W . . . . W
W . W W W . W . W W W W W . W . W W . W
W . W . . . . . . . . . . . . . . W . W
W . W . W W W W W . W W W W W W . W . W
W . . . W . . . . . . . . C . W . . . W
W W W . W . W W W W W W W . . W W W . W
W C . . . . W . . . . . W . . . . . . W
W . W W W W W . W W W . W W W W W W . W
W . . . . . . . . C . . . . . . . . . W
W . W W W W W W W W W . W W W W W W . W
W . . . . . . . . . . . W . . . . . . W
W W W W W W W W W W W . W . W W W W . W
W . . . . . . . . . . . . . W . C . E W
W W W W W W W W W W W W W W W W W W W W

W = Wand    P = Spieler    E = Ausgang    C = Münze    . = Leer
```

---

## Schritt 9: Testen Sie Ihr Spiel!

1. Klicken Sie auf **Run** oder drücken Sie **F5** zum Testen
2. Verwenden Sie die Pfeiltasten, um durch das Labyrinth zu navigieren
3. Sammeln Sie Münzen für Punkte
4. Finden Sie den Ausgang zum Gewinnen!

---

## Erweiterungen (Optional)

### Feinde hinzufügen

Erstellen Sie einen einfachen patrouillierenden Feind:

1. Erstellen Sie `spr_enemy` (rote Farbe, 24x24)
2. Erstellen Sie `obj_enemy` mit Sprite `spr_enemy`

**Event: Create** — Add Action: **Move** → **Start Moving Direction**
(Directions: `right`, Speed: `2`)

**Event: Collision with obj_wall** — Add Action: **Move** → **Reverse
Horizontal** (dreht den Feind um, wenn er auf eine Wand trifft — kein Code
nötig; zusammen mit der eingebauten soliden Kollision aus Schritt 6.2 kann
der Feind gar nicht erst durch eine Wand laufen)

**Event: Collision with obj_player** — Add Action: **Room** → **Restart
Room**

### Ein Leben-System hinzufügen

Fügen Sie im **Create**-Event von `obj_game_controller` **Score** →
**Set Lives** hinzu (Value: `3`).

Ersetzen Sie im **Collision with obj_player**-Event von `obj_enemy`
**Restart Room** durch zwei Aktionen: **Score** → **Set Lives** (Value:
`-1`, **Relative** aktiviert), dann **Move** → **Jump to Start Position**
(auf den Spieler angewendet, über **Applies to: Other**), um den Spieler
zu respawnen statt das ganze Labyrinth neu zu starten.

Fügen Sie `obj_game_controller` ein weiteres Event hinzu: **Other Events**
→ **No More Lives** — dies feuert automatisch, sobald die Leben 0
erreichen, Sie müssen es also nicht selbst abfragen. Fügen Sie **Output**
→ **Show Message** hinzu (`Game Over!`), gefolgt von **Room** →
**Restart Game**.

### Schlüssel und verschlossene Türen hinzufügen

1. Erstellen Sie `obj_key` — bei Collision mit `obj_player`: **Set
   Variable** (Variable: `global.has_key`, Value: `true`, Scope:
   `global`), dann **Destroy Instance** (self).
2. Erstellen Sie `obj_locked_door`, Solid aktiviert. Geben Sie ihm ein
   **Step**-Event mit **Control** → **Test Variable** (Variable:
   `global.has_key`, Value: `true`, Scope: `global`) → **Instance** →
   **Destroy Instance** (self) — die Tür verschwindet (und blockiert
   nicht mehr), sobald der Schlüssel eingesammelt wurde.

### Mehrere Level hinzufügen

1. Erstellen Sie zusätzliche Rooms (`room_maze2`, `room_maze3`)
2. Verwenden Sie in `obj_exit` die **Next Room**-Aktion statt **Restart Room**

### Soundeffekte hinzufügen

Fügen Sie Sounds hinzu für:
- Münzen sammeln
- Ausgang erreichen
- Feinde berühren (falls hinzugefügt)
- Hintergrundmusik

---

## Problembehandlung

| Problem | Lösung |
|---------|--------|
| Spieler bewegt sich durch Wände | Prüfen Sie, ob `obj_wall` "Solid" aktiviert hat |
| Spieler steckt in Wänden fest | Stellen Sie sicher, dass das Spieler-Sprite kleiner als die Wandlücken ist |
| Münzen verschwinden nicht | Überprüfen Sie, dass das Kollisions-Event Self zerstört, nicht Other |
| Timer funktioniert nicht | Stellen Sie sicher, dass der Game Controller im Room platziert ist |
| Bewegung fühlt sich ruckelig an | Passen Sie den `move_speed`-Wert an (versuchen Sie 3-5) |

---

## Was Sie gelernt haben

Gratulation! Sie haben ein Labyrinth-Spiel erstellt! Sie haben gelernt:

- **Flüssige Bewegung** - Gedrückte Tasten für kontinuierliche Bewegung prüfen
- **Eingebaute solide Kollision** - Wände blockieren die Bewegung automatisch, sobald sie als Solid markiert sind, ohne manuellen Positionsprüfungs-Code
- **Sammelobjekte** - Gegenstände erstellen, die den Score erhöhen und verschwinden
- **Timer-System** - Vergangene Zeit mit Instanzvariablen verfolgen
- **Level-Design** - Navigierbare Labyrinth-Layouts erstellen

---

## Herausforderungs-Ideen

1. **Zeitangriff** - Fügen Sie einen Countdown-Timer hinzu. Erreichen Sie den Ausgang, bevor die Zeit abläuft!
2. **Perfekter Score** - Erfordern Sie das Sammeln aller Münzen, bevor sich der Ausgang öffnet
3. **Zufälliges Labyrinth** - Erforschen Sie prozedurale Labyrinth-Generierung
4. **Nebel des Krieges** - Zeigen Sie nur den Bereich um den Spieler
5. **Minimap** - Zeigen Sie eine kleine Übersicht des Labyrinths

---

## Siehe auch

- [Tutorials](Tutorials_de) - Weitere Spiel-Tutorials
- [Fortgeschrittenen-Preset](Intermediate-Preset_de) - Übersicht des für dieses Tutorial nötigen Presets
- [Tutorial: Pong](Tutorial-Pong_de) - Ein Zwei-Spieler-Spiel erstellen
- [Tutorial: Breakout](Tutorial-Breakout_de) - Ein Ziegelstein-Spiel erstellen
- [Tutorial: Sokoban](Tutorial-Sokoban_de) - Ein Kisten-Schiebe-Puzzle erstellen
- [Event-Referenz](Event-Reference_de) - Vollständige Event-Dokumentation
