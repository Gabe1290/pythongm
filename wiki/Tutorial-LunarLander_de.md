# Tutorial: Ein Mondlandungs-Spiel erstellen

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Einführung

In diesem Tutorial erstellen Sie ein **Mondlandungs-Spiel** - ein klassisches Arcade-Spiel, in dem Sie ein Raumschiff steuern, das auf eine Landeplattform herabsinkt. Sie müssen Ihren Schub so steuern, dass er der Schwerkraft entgegenwirkt, und sanft landen, ohne zu zerschellen. Dieses Spiel ist perfekt, um physikalische Konzepte wie Schwerkraft, Schub, Geschwindigkeit und Treibstoffverwaltung zu lernen.

**Was Sie lernen werden:**
- Schwerkraft- und Schubphysik
- Geschwindigkeitsbasierte Landeerkennung
- Treibstoffverwaltungssystem
- Rotations- oder Richtungssteuerung
- Sichere Landezonen

**Schwierigkeit:** Anfänger
**Preset:** Fortgeschrittenen-Preset (die Schub-/Treibstoffphysik verlässt sich durchgehend auf Execute Code, das nicht im Anfänger-Preset ist)

---

## Schritt 1: Das Spiel verstehen

### Spielmechanik
1. Die Landefähre wird von der Schwerkraft nach unten gezogen
2. Drücken von HOCH wendet Schub nach oben an (verbraucht Treibstoff)
3. LINKS/RECHTS steuern die Rotation oder Bewegung der Landefähre
4. Landen Sie sanft auf der Landeplattform, um zu gewinnen
5. Absturz, wenn Sie zu schnell landen oder die Plattform verfehlen
6. Geht der Treibstoff aus, können Sie nicht mehr abbremsen!

### Was wir brauchen

| Element | Zweck |
|---------|-------|
| **Landefähre** | Das Raumschiff, das Sie steuern |
| **Landeplattform** | Sichere Zone zum Landen |
| **Boden** | Gelände, das einen Absturz verursacht |
| **Treibstoffanzeige** | Zeigt den verbleibenden Treibstoff |
| **Geschwindigkeitsanzeige** | Zeigt die aktuelle Geschwindigkeit |

---

## Schritt 2: Die Sprites erstellen

### 2.1 Landefähren-Sprite

1. Klicken Sie im **Ressourcen-Baum** mit der rechten Maustaste auf **Sprites** und wählen Sie **Sprite erstellen**
2. Nennen Sie es `spr_lander`
3. Klicken Sie auf **Sprite bearbeiten**, um den Editor zu öffnen
4. Zeichnen Sie ein einfaches Raumschiff (Dreieck oder klassische Landefähren-Form)
5. Größe: 32x32 Pixel
6. **Wichtig:** Setzen Sie den Ursprung auf Mitte-unten für eine korrekte Landung

### 2.2 Landeplattform-Sprite

1. Erstellen Sie ein neues Sprite namens `spr_pad`
2. Zeichnen Sie eine flache Plattform mit Markierungen (wie ein „H")
3. Verwenden Sie helle Farben (Gelb/Grün)
4. Größe: 64x16 Pixel

### 2.3 Boden-Sprite

1. Erstellen Sie ein neues Sprite namens `spr_ground`
2. Zeichnen Sie felsiges/raues Gelände
3. Verwenden Sie graue/braune Farben
4. Größe: 32x32 Pixel

### 2.4 Flammen-Sprite (Optional)

1. Erstellen Sie ein neues Sprite namens `spr_flame`
2. Zeichnen Sie eine kleine Flamme/einen Abgasstrahl
3. Verwenden Sie orange/gelbe Farben
4. Größe: 16x16 Pixel

![The Sprite Editor with spr_lander open, Origin set to Center-Bottom (X 16, Y 32); spr_lander, spr_pad, spr_ground and spr_flame in the resource tree](images/tutorial-lunarlander-02-sprites.png)

---

## Schritt 3: Das Boden-Objekt erstellen

Der Boden ist gefährliches Gelände, das einen Absturz verursacht.

1. Klicken Sie mit der rechten Maustaste auf **Objekte** und wählen Sie **Objekt erstellen**
2. Nennen Sie es `obj_ground`
3. Setzen Sie das Sprite auf `spr_ground`
4. **Aktivieren Sie das Kontrollkästchen "Solid"**
5. Keine Events benötigt

![obj_ground's Object Events panel: empty -- Solid checked is all it needs](images/tutorial-lunarlander-03-ground-object.png)

---

## Schritt 4: Das Landeplattform-Objekt erstellen

Die Landeplattform ist der Ort, an dem der Spieler sicher landen muss.

1. Erstellen Sie ein neues Objekt namens `obj_pad`
2. Setzen Sie das Sprite auf `spr_pad`
3. **Aktivieren Sie das Kontrollkästchen "Solid"**
4. Keine Events benötigt (die Kollision wird von der Landefähre behandelt)

![obj_pad's Object Events panel: empty, with Solid checked](images/tutorial-lunarlander-04-pad-object.png)

---

## Schritt 5: Das Landefähren-Objekt erstellen

Die Landefähre ist das wichtigste vom Spieler gesteuerte Objekt mit
Physik. Anders als bei den anderen Bewegungs-Tutorials dieses Wikis müssen
ihre Steuerungen Geschwindigkeit allmählich aufbauen und eine
Treibstoffressource verfolgen, daher stützt sich dieses Objekt stärker auf
**Control** → **Execute Code** (echtes Python — `self` ist die aktuelle
Instanz, `game` ist der Game Runner, `keyboard.check(name)` meldet eine
gehaltene Taste) als allein auf strukturierte Aktionen. Überall, wo eine
strukturierte Aktion die Arbeit erledigt, verwendet dieses Tutorial
weiterhin eine.

1. Erstellen Sie ein neues Objekt namens `obj_lander`
2. Setzen Sie das Sprite auf `spr_lander`

### 5.1 Schwerkraft und Startvariablen

**Event: Create**
1. Aktion hinzufügen: **Move** → **Set Gravity** (Direction: `270`, Gravity: `0.05`)
   — ein sanfter Zug nach unten; die Engine addiert dies bei jedem Schritt
   automatisch zur Vertikalgeschwindigkeit der Landefähre, genau wie die
   Schwerkraft des Plattformer-Tutorials, nur schwächer.
2. Aktion hinzufügen: **Control** → **Execute Code**:

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

Das Bewegungssystem dieses Projekts verfolgt die Geschwindigkeit bereits
über `self.hspeed`/`self.vspeed` und bewegt die Instanz bei jedem Frame um
diesen Betrag (mit eingebauter solider Kollision) — es sind keine
separaten `hsp`/`vsp`-Variablen nötig, wie sie eine rohe
Physiksimulation verfolgen würde.

### 5.2 Step-Event — Schub und Steuerung

**Event: Step** — Aktion hinzufügen: **Control** → **Execute Code**:

```python
if not self.landed and not self.crashed:
    if keyboard.check('up') and self.fuel > 0:
        self.vspeed -= self.thrust_force
        self.fuel -= self.fuel_use
        if self.fuel < 0:
            self.fuel = 0

    if keyboard.check('left'):
        self.hspeed -= 0.05
    if keyboard.check('right'):
        self.hspeed += 0.05

    # Höchstgeschwindigkeit begrenzen
    self.hspeed = max(-self.max_speed, min(self.max_speed, self.hspeed))
    self.vspeed = max(-self.max_speed, min(self.max_speed, self.vspeed))

    # Verhindert, dass die Landefähre über die Seiten oder über den Raum hinaus driftet
    room = game.current_room
    if self.x < 16:
        self.x = 16
        self.hspeed = 0
    if self.x > room.width - 16:
        self.x = room.width - 16
        self.hspeed = 0
    if self.y < 16:
        self.y = 16
        self.vspeed = 0
```

Der gesamte Block ist in `if not self.landed and not self.crashed:`
gehüllt, damit Schub und Steuerung sofort stoppen, wenn das Spiel endet —
das `self`-Objekt hat keine Möglichkeit, ein Event mittendrin abzubrechen
(kein `exit` im GML-Stil), also ist ein `if` um den restlichen Code das
Äquivalent.

### 5.3 Kollision mit der Landeplattform

**Event: Collision with obj_pad**
1. Aktion hinzufügen: **Control** → **Test Expression**
   - Expression: `(self.hspeed**2 + self.vspeed**2)**0.5 <= self.safe_speed`
     — die Landegeschwindigkeit ist die Länge des Geschwindigkeitsvektors;
     Pythagoras, keine `speed`-Variable (in dieser Engine ist `speed` die
     *Sprite-Animations*-Rate, nicht der Bewegungsbetrag — eine echte
     Falle für alle, die von GameMaker kommen).
   - Then Actions:
     1. **Control** → **Set Variable** (Variable: `landed`, Value: `true`, Scope: `self`)
     2. **Move** → **Stop Movement**
     3. **Move** → **Set Gravity** (Direction: `270`, Gravity: `0`) — hält
        die Schwerkraft davon ab, bei einer bereits gelandeten Landefähre
        wieder unbemerkt Vertikalgeschwindigkeit aufzubauen
     4. **Output** → **Show Message** (Message: `Perfect Landing! You Win!`)
   - Else Actions:
     1. **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
     2. **Output** → **Show Message** (Message: `Crashed! Too fast!`)
     3. **Room** → **Restart Room**

Der Text von Show Message ist eine feste Zeichenkette — er kann die
tatsächliche Landegeschwindigkeit nicht einbetten. Das HUD (Schritt 7)
zeigt die Live-Geschwindigkeit bis zum Moment des Aufsetzens, der Spieler
hat die Zahl also bereits gesehen.

### 5.4 Kollision mit dem Boden

**Event: Collision with obj_ground**
1. Aktion hinzufügen: **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
2. Aktion hinzufügen: **Output** → **Show Message** (Message: `Crashed into terrain!`)
3. Aktion hinzufügen: **Room** → **Restart Room**

![obj_lander's Object Events panel: Create (Set Gravity + Execute Code), Step (Execute Code), Collision with obj_pad (the Test Expression landing check), Collision with obj_ground (Set Variable + Show Message + Restart Room)](images/tutorial-lunarlander-05-lander-object.png)

---

## Schritt 6: Das Flammen-Objekt erstellen (Optional)

Visuelles Feedback beim Schub.

1. Erstellen Sie ein neues Objekt namens `obj_flame`
2. Setzen Sie das Sprite auf `spr_flame`

Es wird von der Landefähre beim Schub erzeugt (fortgeschrittene Funktion).
Für einen einfacheren Ansatz können Sie die Flamme im Draw-Event der
Landefähre zeichnen.

![obj_flame's Object Events panel: empty -- it just needs the spr_flame sprite](images/tutorial-lunarlander-06-flame-object.png)

---

## Schritt 7: Den Spiel-Controller erstellen

Der Spiel-Controller zeigt Treibstoff, Geschwindigkeit und Anweisungen an,
indem er sie bei jedem Frame von der Landefähren-Instanz abliest.

1. Erstellen Sie ein neues Objekt namens `obj_game_controller`
2. Kein Sprite nötig

**Event: Draw**
1. Aktion hinzufügen: **Control** → **Execute Code** — findet die
   Landefähre und berechnet die Werte, die die Draw-Aktionen unten
   anzeigen:

```python
lander = None
for inst in game.current_room.instances:
    if inst.object_name == 'obj_lander':
        lander = inst
        break

if lander is not None:
    self.fuel_display = round(lander.fuel)
    self.speed_display = round((lander.hspeed ** 2 + lander.vspeed ** 2) ** 0.5, 2)
    self.too_fast = self.speed_display > lander.safe_speed
    self.no_fuel = lander.fuel <= 0
else:
    self.fuel_display = 0
    self.speed_display = 0.0
    self.too_fast = False
    self.no_fuel = False
```

2. Aktion hinzufügen: **Game** → **Set Draw Color** (Color: `#FFFFFF`)
3. Aktion hinzufügen: **Game** → **Draw Text** (Text: `LUNAR LANDER`, X: `10`, Y: `10`)
4. Aktion hinzufügen: **Game** → **Draw Text** (Text: `Fuel:`, X: `10`, Y: `30`)
5. Aktion hinzufügen: **Game** → **Draw Variable** (Variable: `self.fuel_display`, X: `70`, Y: `30`)
6. Aktion hinzufügen: **Game** → **Draw Text** (Text: `Speed:`, X: `10`, Y: `50`)
7. Aktion hinzufügen: **Game** → **Draw Variable** (Variable: `self.speed_display`, X: `70`, Y: `50`)
8. Aktion hinzufügen: **Game** → **Draw Text** (Text: `Safe Speed: < 2`, X: `10`, Y: `70`)

Dann die zwei Warnzeilen, jede über **Control** → **Test Expression**
gesteuert (kein Else nötig — es wird nichts gezeichnet, wenn die Bedingung
falsch ist):

9. **Control** → **Test Expression** (Expression: `self.too_fast`)
   - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
     **Draw Text** (`TOO FAST!`, X `10`, Y `90`)
   - Else Actions: **Game** → **Set Draw Color** (`#00FF00`), **Game** →
     **Draw Text** (`Speed OK`, X `10`, Y `90`)
10. **Control** → **Test Expression** (Expression: `self.no_fuel`)
    - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
      **Draw Text** (`NO FUEL!`, X `10`, Y `110`)

11. Aktion hinzufügen: **Game** → **Set Draw Color** (Color: `#808080`)
12. Aktion hinzufügen: **Game** → **Draw Text** (Text: `UP: Thrust | LEFT/RIGHT: Move`,
    X: `10`, Y: `440`) — wählen Sie ein Y nahe dem unteren Rand der
    Raumgröße, die Sie in Schritt 8 verwenden.

![obj_game_controller's Object Events panel: a Draw event with 12 actions -- the Execute Code HUD-value calculation, then the Set Draw Color / Draw Text / Draw Variable chain and the two Test Expression warning blocks -- with no sprite set](images/tutorial-lunarlander-07-controller-object.png)

---

## Schritt 8: Ihr Level entwerfen

1. Klicken Sie mit der rechten Maustaste auf **Rooms** und wählen Sie **Room erstellen**
2. Nennen Sie ihn `room_game`
3. Legen Sie die Raumgröße fest (z. B. 640x480)
4. Setzen Sie die Hintergrundfarbe auf Schwarz (Weltraum)

### Objekte platzieren

Bauen Sie Ihr Level nach diesen Richtlinien:

1. **Boden** - Platzieren Sie `obj_ground` entlang des unteren Rands, um Gelände zu schaffen
2. **Landeplattform** - Platzieren Sie `obj_pad` in einer Lücke im Gelände
3. **Landefähre** - Platzieren Sie `obj_lander` oben im Raum
4. **Spiel-Controller** - Platzieren Sie `obj_game_controller` irgendwo

### Beispiel-Level-Layout

```
    L                          <- Die Landefähre startet hier




GGG    GGG    PPPP    GGG    GGG
GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG

G = Boden    L = Landefähre    P = Landeplattform
```

![The Room Editor for room_game: a solid terrain row along the bottom with rocky chunks above it, a yellow landing pad in a clear gap, the white lander near the top-left, and the obj_game_controller marker near the top-right, all on a black space background](images/tutorial-lunarlander-08-room.png)

---

## Schritt 9: Testen Sie Ihr Spiel!

1. Klicken Sie auf **Ausführen** oder drücken Sie **F5** zum Testen
2. Verwenden Sie die Pfeiltaste **HOCH** für Schub (achten Sie auf Ihren Treibstoff!)
3. Verwenden Sie die Pfeiltasten **LINKS/RECHTS** zum Steuern
4. Landen Sie sanft auf der Plattform (Geschwindigkeit muss unter 2 sein)
5. Weichen Sie dem felsigen Gelände aus!

---

## Erweiterungen (Optional)

### Rotationssteuerung hinzufügen

Statt Links/Rechts-Bewegung: drehen Sie die Landefähre und geben Sie Schub
in die Richtung, in die sie zeigt. Die Instanzen dieser Engine haben ein
echtes `rotation`-Attribut (Grad, 0 = rechts, gegen den Uhrzeigersinn
zunehmend), mit dem das Sprite gedreht wird — kein
`image_angle`/`lengthdir_x`/`lengthdir_y` nötig, da `math` in Execute Code
bereits verfügbar ist:

Ersetzen Sie den Create-Event-Code aus 5.1 durch:
```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
self.rotation = 90  # nach oben zeigend
self.rotation_speed = 3
```

Ersetzen Sie die Steuerungszeilen aus 5.2 (den `left`/`right` →
`hspeed`-Block) durch:
```python
if keyboard.check('left'):
    self.rotation -= self.rotation_speed
if keyboard.check('right'):
    self.rotation += self.rotation_speed
```

Und ersetzen Sie die Schubzeilen durch:
```python
if keyboard.check('up') and self.fuel > 0:
    rad = math.radians(self.rotation)
    self.hspeed += self.thrust_force * math.cos(rad)
    self.vspeed -= self.thrust_force * math.sin(rad)
    self.fuel -= self.fuel_use
    if self.fuel < 0:
        self.fuel = 0
```

(das `-=` bei `vspeed` entspricht dem Schwerkraftcode der Engine — die
Bildschirm-Y-Achse nimmt nach unten zu, „oben" ist also negative
Vertikalgeschwindigkeit).

### Mehrere Landeplattformen hinzufügen

Erstellen Sie Plattformen unterschiedlicher Größe mit unterschiedlichen
Punktwerten:
- Kleine Plattform = 100 Punkte (schwerer)
- Große Plattform = 50 Punkte (einfacher)

### Treibstoff-Aufsammler hinzufügen

1. Erstellen Sie `obj_fuel`, das in der Luft schwebt
2. Bei Kollision mit der Landefähre: Treibstoff hinzufügen und zerstören

### Level hinzufügen

Erstellen Sie mehrere Räume mit zunehmend schwierigerem Gelände und
kleineren Landeplattformen.

### Wind hinzufügen

Fügen Sie einen kleinen konstanten horizontalen Schub hinzu. Im
Create-Event-Code von `obj_lander` fügen Sie `self.wind_force = 0.02`
hinzu; dann am Anfang des `if not self.landed and not self.crashed:`-Blocks
des Step-Events:
```python
self.hspeed += self.wind_force
```

---

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| Die Landefähre fällt zu schnell | Verringern Sie den `Gravity`-Wert von Set Gravity, oder erhöhen Sie `thrust_force` im Create-Event-Code |
| Kann nicht genug abbremsen | Erhöhen Sie `thrust_force`, oder erhöhen Sie `safe_speed` |
| Der Treibstoff geht zu schnell aus | Verringern Sie `fuel_use`, oder erhöhen Sie den Start-`fuel` |
| Die Landefähre verlässt den Bildschirm | Prüfen Sie den Grenzblock am Ende des Step-Event-Codes |
| Die Landung wird nicht erkannt | Stellen Sie sicher, dass `obj_pad` "Solid" aktiviert hat |

---

## Was Sie gelernt haben

Herzlichen Glückwunsch! Sie haben ein Mondlandungs-Spiel erstellt! Sie haben gelernt:

- **Schubphysik** - `self.vspeed` gegen einen kontinuierlichen Set-Gravity-Zug anstupsen
- **Geschwindigkeitsverwaltung** - Geschwindigkeit aus `hspeed`/`vspeed` mit dem Satz des Pythagoras berechnen
- **Treibstoffsystem** - Ressourcenverwaltungs-Gameplay mit einer einfachen Instanzvariablen
- **Kollisionserkennung** - Unterschiedliche Ergebnisse für Plattform vs. Boden, gewählt mit Test Expression
- **HUD-Anzeige** - Anzeigewerte in Execute Code berechnen und dann mit Draw Text/Draw Variable anzeigen

---

## Herausforderungs-Ideen

1. **Realistische Rotation** - In Blickrichtung drehen und Schub geben
2. **Mehrere Level** - Zunehmend schwieriges Gelände
3. **Punktesystem** - Punkte je nach verbleibendem Treibstoff und Landegenauigkeit
4. **Asteroiden** - Bewegliche Gefahren zum Ausweichen hinzufügen
5. **Zwei-Spieler-Modus** - Wettlauf, wer zuerst landet

---

## Siehe auch

- [Tutorials](Tutorials_de) - Mehr Spiel-Tutorials
- [Fortgeschrittenen-Preset](Intermediate-Preset_de) - Überblick über das Preset, das dieses Tutorial braucht
- [Tutorial: Plattformer](Tutorial-Platformer_de) - Ein Plattform-Sprungspiel erstellen
- [Tutorial: Labyrinth](Tutorial-Maze_de) - Ein Labyrinth-Navigationsspiel erstellen
- [Event-Referenz](Event-Reference_de) - Vollständige Event-Dokumentation
