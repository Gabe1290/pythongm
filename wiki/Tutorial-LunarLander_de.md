# Tutorial: Erstelle ein Mondlandung-Spiel

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Einführung

In diesem Tutorial erstellst du ein **Mondlandung-Spiel** - ein klassisches Arcade-Spiel, bei dem du ein Raumschiff steuerst, das auf einer Landeplattform landet. Du musst deinen Schub verwalten, um der Schwerkraft entgegenzuwirken und sanft zu landen, ohne abzustürzen. Dieses Spiel ist perfekt, um Physikkonzepte wie Schwerkraft, Schub, Geschwindigkeit und Treibstoffmanagement zu lernen.

**Was du lernen wirst:**
- Schwerkraft- und Schubphysik
- Geschwindigkeitsbasierte Landeerkennung
- Treibstoffmanagementsystem
- Rotations- oder Richtungssteuerung
- Sichere Landezonen

**Schwierigkeit:** Anfänger
**Preset:** Fortgeschrittenen-Preset (die Schub-/Treibstoffphysik beruht
durchgehend auf Execute Code, das nicht im Anfänger-Preset enthalten ist)

---

## Schritt 1: Das Spiel Verstehen

### Spielmechaniken
1. Der Lander wird von der Schwerkraft nach unten gezogen
2. HOCH drücken wendet Aufwärtsschub an (verbraucht Treibstoff)
3. LINKS/RECHTS steuert Rotation oder Bewegung
4. Lande sanft auf der Plattform, um zu gewinnen
5. Absturz, wenn du zu schnell landest oder die Plattform verfehlst
6. Kein Treibstoff mehr = kannst nicht abbremsen!

### Was Wir Brauchen

| Element | Zweck |
|---------|-------|
| **Lander** | Das Raumschiff, das du steuerst |
| **Landeplattform** | Sichere Zone zum Landen |
| **Boden** | Gelände, das Absturz verursacht |
| **Treibstoffanzeige** | Zeigt verbleibenden Treibstoff |
| **Geschwindigkeitsanzeige** | Zeigt aktuelle Geschwindigkeit |

---

## Schritt 2: Sprites Erstellen

### Sprites
- `spr_lander` (32x32 Pixel) - einfaches Raumschiff
- `spr_pad` (64x16 Pixel) - Landeplattform
- `spr_ground` (32x32 Pixel) - felsiges Gelände
- `spr_flame` (16x16 Pixel) - Schubflamme (optional)

---

## Schritt 3-4: Boden- und Plattform-Objekte Erstellen

**obj_ground** und **obj_pad**: Sprite einstellen, "Solid" aktivieren

---

## Schritt 5: Lander-Objekt Erstellen

Der Lander ist das komplexeste Objekt: Seine Steuerung muss Geschwindigkeit
schrittweise aufbauen und eine Treibstoffressource verwalten. Dieses
Objekt nutzt daher mehr **Control** → **Execute Code** (echtes Python —
`self` ist die aktuelle Instanz, `game` ist der Game Runner,
`keyboard.check(name)` zeigt an, ob eine Taste gehalten wird) als die
vorherigen Bewegungs-Tutorials dieses Wikis, verwendet aber weiterhin
überall eine strukturierte Aktion, wo es möglich ist.

### 5.1 Schwerkraft und Startvariablen

**Event: Create**
1. Action: **Move** → **Set Gravity** (Direction: `270`, Gravity: `0.05`)
   — ein leichter Zug nach unten; die Engine addiert ihn automatisch bei
   jedem Frame zur Vertikalgeschwindigkeit, wie im Plattformer-Tutorial,
   nur schwächer.
2. Action: **Control** → **Execute Code**:

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

Das Bewegungssystem dieser Engine verfolgt die Geschwindigkeit bereits
über `self.hspeed`/`self.vspeed` und bewegt die Instanz bei jedem Frame um
diesen Betrag (inklusive eingebauter solider Kollision) — es müssen keine
separaten Variablen `hsp`/`vsp` angelegt werden, wie es eine manuelle
Physiksimulation tun würde.

### 5.2 Step-Event — Schub und Steuerung

**Event: Step** — Action: **Control** → **Execute Code**:

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

    # Begrenzt die Höchstgeschwindigkeit
    self.hspeed = max(-self.max_speed, min(self.max_speed, self.hspeed))
    self.vspeed = max(-self.max_speed, min(self.max_speed, self.vspeed))

    # Verhindert, dass der Lander über die Ränder oder aus dem Room hinaus driftet
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

Der gesamte Block ist von `if not self.landed and not self.crashed:`
umgeben, damit Schub und Steuerung sofort stoppen, sobald das Spiel
beendet ist — das Objekt hat keine Möglichkeit, ein Event mittendrin
abzubrechen (kein `exit` wie in GML); ein `if` um den restlichen Code
herum übernimmt dieselbe Aufgabe.

### 5.3 Kollision mit der Landeplattform

**Event: Collision with obj_pad**
1. Action: **Control** → **Test Expression**
   - Expression: `(self.hspeed**2 + self.vspeed**2)**0.5 <= self.safe_speed`
     — die Landegeschwindigkeit ist die Länge des Geschwindigkeitsvektors
     (Satz des Pythagoras), keine Variable `speed` (in dieser Engine
     bezeichnet `speed` die *Sprite-Animationsgeschwindigkeit*, nicht die
     Bewegungsgröße — eine echte Falle für alle, die von GameMaker kommen).
   - Then Actions:
     1. **Control** → **Set Variable** (Variable: `landed`, Value: `true`, Scope: `self`)
     2. **Move** → **Stop Movement**
     3. **Move** → **Set Gravity** (Direction: `270`, Gravity: `0`) —
        verhindert, dass die Schwerkraft bei einem bereits gelandeten
        Lander unbemerkt wieder Vertikalgeschwindigkeit aufbaut
     4. **Output** → **Show Message** (Message: `Perfekte Landung! Du gewinnst!`)
   - Else Actions:
     1. **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
     2. **Output** → **Show Message** (Message: `Abgestürzt! Zu schnell!`)
     3. **Room** → **Restart Room**

Der Text von Show Message ist eine feste Zeichenkette — er kann die
tatsächliche Landegeschwindigkeit nicht anzeigen. Das HUD (Schritt 7)
zeigt die Geschwindigkeit bereits live bis zum Moment der Berührung an,
der Spieler hat die Zahl also schon gesehen.

### 5.4 Kollision mit dem Boden

**Event: Collision with obj_ground**
1. Action: **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
2. Action: **Output** → **Show Message** (Message: `In Gelände abgestürzt!`)
3. Action: **Room** → **Restart Room**

---

## Schritt 6-7: Spielcontroller

**obj_game_controller** — Draw-Event: findet den Lander über eine Schleife
über `game.current_room.instances` (dasselbe Muster wie der Münzzähler im
Labyrinth-Tutorial), berechnet gerundeten Treibstoff/Geschwindigkeit in
einem **Execute Code**, und zeigt sie dann mit **Draw Text**/**Draw
Variable** an; siehe die [englische Version](Tutorial-LunarLander) für die
vollständigen Details Aktion für Aktion.

---

## Schritt 8: Dein Level Gestalten

1. Erstelle `room_game` (640x480)
2. Schwarzer Hintergrund (Weltraum)
3. Platziere Boden unten mit einer Lücke
4. Platziere Plattform in der Lücke
5. Platziere Lander oben
6. Platziere Spielcontroller

---

## Was Du Gelernt Hast

- **Schubphysik** - `self.vspeed` gegen eine kontinuierliche Schwerkraft (Set Gravity) anpassen
- **Geschwindigkeitsmanagement** - Geschwindigkeit aus `hspeed`/`vspeed` mit dem Satz des Pythagoras berechnen
- **Treibstoffsystem** - Ressourcenmanagement mit einer einfachen Instanzvariable
- **Kollisionserkennung** - Unterschiedliche Ergebnisse für Plattform und Boden, per Test Expression gewählt

---

## Siehe Auch

- [Tutorials](Tutorials_de) - Mehr Tutorials
- [Tutorial: Platformer](Tutorial-Platformer_de) - Erstelle ein Plattformspiel
