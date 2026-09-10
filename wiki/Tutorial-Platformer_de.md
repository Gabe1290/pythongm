# Tutorial: Ein Plattformer-Spiel erstellen

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Platformer) | [Français](Tutorial-Platformer_fr) | [Deutsch](Tutorial-Platformer_de) | [Italiano](Tutorial-Platformer_it) | [Español](Tutorial-Platformer_es) | [Português](Tutorial-Platformer_pt) | [Slovenščina](Tutorial-Platformer_sl) | [Українська](Tutorial-Platformer_uk) | [Русский](Tutorial-Platformer_ru)

---

## Einführung

In diesem Tutorial erstellen Sie ein **Plattformer-Spiel** - ein seitlich scrollendes Actionspiel, in dem der Spieler läuft, springt und über Plattformen navigiert, während er Gefahren ausweicht und Münzen sammelt. Dieses klassische Genre ist perfekt, um Schwerkraft, Sprungmechanik und Plattform-Kollision zu lernen.

**Was Sie lernen werden:**
- Schwerkraft und Fallphysik
- Sprungmechanik mit Bodenerkennung
- Plattform-Kollision (oben landen)
- Links/Rechts-Bewegung
- Sammelgegenstände und Gefahren

**Schwierigkeit:** Anfänger
**Preset:** Fortgeschrittenen-Preset (die Execute-Code-Aktionen im Abschnitt Erweiterungen sind nicht im Anfänger-Preset; das Basis-Tutorial bis Schritt 10 braucht nur Aktionen des Anfänger-Presets)

---

## Schritt 1: Das Spiel verstehen

### Spielmechanik
1. Der Spieler wird von der Schwerkraft beeinflusst und fällt nach unten
2. Der Spieler kann sich nach links und rechts bewegen
3. Der Spieler kann springen, wenn er auf dem Boden steht
4. Plattformen hindern den Spieler am Durchfallen
5. Sammle Münzen für Punkte
6. Erreiche die Flagge, um das Level abzuschließen

### Was wir brauchen

| Element | Zweck |
|---------|-------|
| **Spieler** | Die Figur, die Sie steuern |
| **Boden/Plattform** | Feste Oberflächen zum Stehen |
| **Münze** | Sammelbare Gegenstände für Punkte |
| **Stachel** | Gefahr, die den Spieler verletzt |
| **Flagge** | Ziel, das das Level beendet |

---

## Schritt 2: Die Sprites erstellen

### 2.1 Spieler-Sprite

1. Klicken Sie im **Ressourcen-Baum** mit der rechten Maustaste auf **Sprites** und wählen Sie **Sprite erstellen**
2. Nennen Sie es `spr_player`
3. Klicken Sie auf **Sprite bearbeiten**, um den Editor zu öffnen
4. Zeichnen Sie eine einfache Figur (Rechteck mit Gesicht oder Strichmännchen)
5. Verwenden Sie eine helle Farbe wie Blau oder Rot
6. Größe: 32x48 Pixel (höher als breit für eine Figur)
7. Klicken Sie auf **OK** zum Speichern

### 2.2 Boden-Sprite

1. Erstellen Sie ein neues Sprite namens `spr_ground`
2. Zeichnen Sie eine Gras/Erde-Plattformkachel
3. Verwenden Sie braune und grüne Farben
4. Größe: 32x32 Pixel

### 2.3 Plattform-Sprite

1. Erstellen Sie ein neues Sprite namens `spr_platform`
2. Zeichnen Sie eine schwebende Plattform (Holz oder Stein)
3. Größe: 64x16 Pixel (breit und dünn)

### 2.4 Münz-Sprite

1. Erstellen Sie ein neues Sprite namens `spr_coin`
2. Zeichnen Sie einen kleinen gelben/goldenen Kreis
3. Größe: 16x16 Pixel

### 2.5 Stachel-Sprite

1. Erstellen Sie ein neues Sprite namens `spr_spike`
2. Zeichnen Sie dreieckige Stacheln, die nach oben zeigen
3. Verwenden Sie graue oder rote Farben
4. Größe: 32x32 Pixel

### 2.6 Flaggen-Sprite

1. Erstellen Sie ein neues Sprite namens `spr_flag`
2. Zeichnen Sie eine Flagge an einem Mast
3. Verwenden Sie helle Farben (grüne Flagge, brauner Mast)
4. Größe: 32x64 Pixel

![The Sprite Editor with spr_player open (32x48), origin centered; spr_player, spr_ground, spr_platform, spr_coin, spr_spike and spr_flag in the resource tree](images/tutorial-platformer-02-sprites.png)

---

## Schritt 3: Das Boden-Objekt erstellen

Der Boden ist eine feste Plattform, die den Spieler am Fallen hindert.

1. Klicken Sie mit der rechten Maustaste auf **Objekte** und wählen Sie **Objekt erstellen**
2. Nennen Sie es `obj_ground`
3. Setzen Sie das Sprite auf `spr_ground`
4. **Aktivieren Sie das Kontrollkästchen "Solid"**
5. Keine Events benötigt

![obj_ground's Object Events panel: empty -- Solid checked is all it needs](images/tutorial-platformer-03-ground-object.png)

---

## Schritt 4: Das Plattform-Objekt erstellen

Plattformen funktionieren wie der Boden, können aber in der Luft platziert werden.

1. Erstellen Sie ein neues Objekt namens `obj_platform`
2. Setzen Sie das Sprite auf `spr_platform`
3. **Aktivieren Sie das Kontrollkästchen "Solid"**
4. Keine Events benötigt

**Tipp:** Sie können die Plattform zu einem Kind von `obj_ground` machen, um dasselbe Kollisionsverhalten zu teilen.

![obj_platform's Object Events panel: empty, with Solid checked -- a wide, thin sprite is the only difference from obj_ground](images/tutorial-platformer-04-platform-object.png)

---

## Schritt 5: Das Spieler-Objekt erstellen

Der Spieler ist das komplexeste Objekt mit Schwerkraft, Springen und Bewegung.

1. Erstellen Sie ein neues Objekt namens `obj_player`
2. Setzen Sie das Sprite auf `spr_player`

### 5.1 Schwerkraft

**Event: Create** — Fügen Sie die Aktion **Move** → **Set Gravity** hinzu
(Direction: `270`, Gravity: `0.5`) — 270° bedeutet senkrecht nach unten;
der Wert wird bei jedem Schritt zur Vertikalgeschwindigkeit des Spielers
addiert, der Spieler beschleunigt also ab jetzt von selbst nach unten.

### 5.2 Bewegung, Sprung und Bodenkollision

Fügen Sie diese Events hinzu, nach demselben Muster wie in den vorherigen
Tutorials dieses Wikis:

| Event | Aktion |
|---|---|
| Keyboard (held) → Left Arrow | Set Horizontal Speed auf `-4` |
| Keyboard (held) → Right Arrow | Set Horizontal Speed auf `4` |
| Keyboard: No Key | Set Horizontal Speed auf `0` |
| Key Press → Up Arrow | Set Vertical Speed auf `-10` |
| Collision with obj_ground | Stop Movement |

Zwei Details, die dafür sorgen, dass es sich richtig anfühlt:

- **No Key setzt NUR die Horizontalgeschwindigkeit auf 0** — verwenden Sie
  hier niemals Stop Movement, denn Stop Movement setzt auch die
  Vertikalgeschwindigkeit auf null, was die Schwerkraft jedes Mal
  aufheben würde, wenn der Spieler eine Richtungstaste loslässt.
- **Key Press (nicht held)** ist es, was Up zu einem einzelnen
  Sprungimpuls macht, statt den Spieler bei jedem gehaltenen Frame nach
  oben zu treiben. **Stop Movement** bei der Landung hebt diesen Impuls
  dann auf, damit der Spieler nach dem Landen nicht weiter nach oben
  steigt — die eingebaute solide Kollision der Engine (Schritt 3 hat
  `obj_ground` bereits Solid gemacht) verhindert bereits, dass der
  Spieler in den Boden einsinkt; das Event hier löscht lediglich die
  verbleibende Fallgeschwindigkeit.

![obj_player's Object Events panel: Create (Set Gravity), Keyboard (held) with two Set Horizontal Speed actions, Keyboard <No Key>, Keyboard Press with the Up-Arrow jump, and Collision with obj_ground (Stop Movement)](images/tutorial-platformer-05-player-object.png)

---

## Schritt 6: Das Münz-Objekt erstellen

Münzen erhöhen den Punktestand, wenn sie eingesammelt werden.

1. Erstellen Sie ein neues Objekt namens `obj_coin`
2. Setzen Sie das Sprite auf `spr_coin`

**Event: Collision with obj_player**
1. Event hinzufügen → Collision → obj_player
2. Aktion hinzufügen: **Score** → **Set Score**
   - New Score: `10`
   - "Relative" aktivieren
3. Aktion hinzufügen: **Main1** → **Destroy Instance**
   - Applies to: Self

![obj_coin's Object Events panel: a Collision with obj_player event holding Set Score (Relative) and Destroy Instance](images/tutorial-platformer-06-coin-object.png)

---

## Schritt 7: Das Stachel-Objekt erstellen

Stacheln verletzen den Spieler und starten das Level neu.

1. Erstellen Sie ein neues Objekt namens `obj_spike`
2. Setzen Sie das Sprite auf `spr_spike`

**Event: Collision with obj_player**
1. Event hinzufügen → Collision → obj_player
2. Aktion hinzufügen: **Main2** → **Show Message**
   - Message: `Ouch! You hit a spike!`
3. Aktion hinzufügen: **Main1** → **Restart Room**

![obj_spike's Object Events panel: a Collision with obj_player event holding Show Message and Restart Room](images/tutorial-platformer-07-spike-object.png)

---

## Schritt 8: Das Flaggen-Objekt erstellen

Die Flagge beendet das Level, wenn der Spieler sie erreicht.

1. Erstellen Sie ein neues Objekt namens `obj_flag`
2. Setzen Sie das Sprite auf `spr_flag`

**Event: Collision with obj_player**
1. Event hinzufügen → Collision → obj_player
2. Aktion hinzufügen: **Output** → **Show Message**
   - Message: `Level Complete!`
3. Aktion hinzufügen: **Room** → **Next Room** (oder **Restart Room** für ein einzelnes Level)

Der Text von Show Message ist eine feste Zeichenkette — er kann keinen
Live-Wert wie den Punktestand einbetten. Das HUD des Spiel-Controllers
(Schritt 9) zeigt den Punktestand während des gesamten Levels auf dem
Bildschirm, der Spieler hat ihn also bereits gesehen.

![obj_flag's Object Events panel: a Collision with obj_player event holding Show Message and Next Room](images/tutorial-platformer-08-flag-object.png)

---

## Schritt 9: Den Spiel-Controller erstellen

Der Spiel-Controller zeigt den Punktestand an.

1. Erstellen Sie ein neues Objekt namens `obj_game_controller`
2. Kein Sprite nötig

**Event: Draw**
1. Event hinzufügen → Draw → Draw
2. Aktion hinzufügen: **Draw** → **Draw Text** (Text: `Score:`, X: `10`, Y: `10`)
3. Aktion hinzufügen: **Draw** → **Draw Variable** (Variable: `score`, X: `70`, Y: `10`)

Optional: Fügen Sie ein Paar **Draw Text** (`Lives:`, X `10`, Y `30`) +
**Draw Variable** (`lives`, X `70`, Y `30`) auf dieselbe Weise hinzu,
sobald die Erweiterung Leben-System weiter unten eingebaut ist.

![obj_game_controller's Object Events panel: a Draw event with one Draw Text and one Draw Variable action, with no sprite set](images/tutorial-platformer-09-controller-object.png)

---

## Schritt 10: Ihr Level entwerfen

1. Klicken Sie mit der rechten Maustaste auf **Rooms** und wählen Sie **Room erstellen**
2. Nennen Sie ihn `room_level1`
3. Legen Sie die Raumgröße fest (z. B. 800x480)
4. Aktivieren Sie "Am Raster ausrichten" und setzen Sie das Raster auf 32x32

### Objekte platzieren

Bauen Sie Ihr Level nach diesen Richtlinien:

1. **Boden erstellen** - Platzieren Sie `obj_ground` entlang des unteren Rands
2. **Plattformen hinzufügen** - Platzieren Sie `obj_platform` in der Luft für Sprungherausforderungen
3. **Lücken hinzufügen** - Lassen Sie Zwischenräume im Boden (Gruben)
4. **Münzen platzieren** - Verteilen Sie sie auf Plattformen und an schwer erreichbaren Stellen
5. **Stacheln hinzufügen** - In der Nähe von Gruben oder auf Plattformen als Herausforderung
6. **Flagge platzieren** - Am Ende des Levels
7. **Spieler platzieren** - Am Anfang (linke Seite)
8. **Spiel-Controller hinzufügen** - Irgendwo (er ist unsichtbar)

### Beispiel-Level-Layout

```
                                        F
                                      ===
                          C       C
                        =====   =====
            C                           C
          ===== X     X         X     =====
    P                   C
  ====== === ===   ===   === === ===== ======
  GGGGGG     GGG   GGG   GGG         GGGGGGGG

G = Boden    P = Spieler    F = Flagge    C = Münze
X = Stachel    === = Plattform
```

![The Room Editor for room_level1: a brown ground row with two pit gaps, four tan floating platforms at rising heights, gold coins on and above them, two grey spikes on the ground, the red player at the far left and the green flag at the far right](images/tutorial-platformer-10-room.png)

---

## Schritt 11: Testen Sie Ihr Spiel!

1. Klicken Sie auf **Ausführen** oder drücken Sie **F5** zum Testen
2. Benutzen Sie die Pfeiltasten **Links/Rechts** zum Bewegen
3. Drücken Sie **Hoch** oder **Leertaste** zum Springen
4. Sammeln Sie Münzen für Punkte
5. Weichen Sie den Stacheln aus!
6. Erreichen Sie die Flagge, um zu gewinnen!

---

## Erweiterungen (Optional)

### Variable Sprunghöhe hinzufügen

Fügen Sie ein **Step**-Event zu `obj_player` mit **Control** → **Execute
Code** hinzu (echtes Python — `self` ist die aktuelle Instanz, `keyboard`
lässt Sie eine gehaltene Taste per Name prüfen):

```python
# Sprung abbrechen, wenn Up losgelassen wird, während der Spieler noch steigt
if self.vspeed < 0 and not keyboard.check('up'):
    self.vspeed = max(self.vspeed, -5)  # Hälfte des Sprungimpulses -10
```

### Doppelsprung hinzufügen

Das lässt sich vollständig mit strukturierten Aktionen umsetzen — kein
Code nötig.

**Event: Create** — Aktion hinzufügen: **Control** → **Set Variable**
(Variable: `jumps_left`, Value: `2`)

**Event: Collision with obj_ground** — nach **Stop Movement** die Aktion
**Control** → **Set Variable** (Variable: `jumps_left`, Value: `2`)
hinzufügen, um beide Sprünge bei der Landung aufzufüllen.

Ersetzen Sie die einzelne Aktion des bestehenden **Key Press → Up
Arrow**-Events durch drei, in dieser Reihenfolge:
1. **Control** → **Test Variable** (Variable: `jumps_left`, Value: `0`,
   Operation: `greater`)
2. **Control** → **Start Block**
3. **Move** → **Set Vertical Speed** (`-10`)
4. **Control** → **Set Variable** (Variable: `jumps_left`, Value: `-1`,
   **Relative** aktiviert)
5. **Control** → **End Block**

Das Paar Start/End Block bedeutet, dass beide darin enthaltenen Aktionen
nur ausgeführt werden, wenn das Test Variable darüber wahr ist — dasselbe
geschützte Block-Muster, das die Tutorials Sokoban und Labyrinth für ihre
eigenen Bedingungen verwenden.

### Bewegliche Plattformen hinzufügen

1. Erstellen Sie `obj_moving_platform` als Kind von `obj_platform`

**Event: Create** — Aktion hinzufügen: **Control** → **Execute Code**:

```python
self.start_x = self.x
self.hspeed = 2
```

**Event: Step** — Aktion hinzufügen: **Control** → **Execute Code**:

```python
if self.x > self.start_x + 100:
    self.hspeed = -2
elif self.x < self.start_x:
    self.hspeed = 2
```

### Gegner hinzufügen

1. Erstellen Sie `obj_enemy` mit einer einfachen KI

**Event: Create** — Aktion hinzufügen: **Move** → **Start Moving
Direction** (Directions: `right`, Speed: `2`)

**Event: Collision with obj_ground** — Aktion hinzufügen: **Move** →
**Reverse Horizontal** (dreht an Wänden um; kombiniert damit, dass
`obj_ground` Solid ist, kann der Gegner nie über den Rand einer Plattform
in den Boden darunter laufen oder durch eine Wand)

**Event: Collision with obj_player** — dieses Event wird auf `obj_enemy`
ausgelöst, also ist `self` der Gegner und `other` der Spieler. Aktion
hinzufügen: **Control** → **Test Expression**, mit verschachtelten
Then/Else-Aktionen (dasselbe Muster, das das mitgelieferte Beispiel
`plateforme_3` für genau diese "Draufspring"-Prüfung verwendet, nur
gespiegelt, da die Prüfung hier auf dem Gegner statt auf dem Spieler
liegt):
   - Expression: `other.vspeed > 0 and other.y - other.vspeed < y - 16`
   - Then Actions: **Control** → **Execute Code** mit `other.vspeed = -5`
     (ein kleiner Rückprall für den Spieler — `set_vspeed` hat keine
     "applies to other"-Option, also ist dies die eine Stelle, die eine
     Zeile echtes Python statt einer strukturierten Aktion braucht), dann
     **Instance** → **Destroy Instance** (self)
   - Else Actions: **Room** → **Restart Room** (der Spieler stirbt)

`other.vspeed > 0 and other.y - other.vspeed < y - 16` prüft die Position
*des Spielers* von vor der Fallbewegung dieses Frames (mit dem `vspeed`
des Spielers selbst, da er derjenige ist, der fällt), damit ein schneller
Fall nicht in einem Schritt durch das 16-px-Draufspring-Fenster tunneln
kann — siehe das README von `plateforme_3` für die ganze Geschichte,
warum die naive Version `other.y < y - 16` fragil ist.

### Leben-System hinzufügen

Fügen Sie im **Create**-Event von `obj_game_controller` **Score** → **Set
Lives** (Value: `3`) hinzu.

Wenn der Spieler stirbt (die Stachel-Kollision und der Else-Zweig des
Gegners oben), ersetzen Sie **Restart Room** durch **Score** → **Set
Lives** (Value: `-1`, **Relative** aktiviert) — der Raum startet
automatisch neu, weil das Event **No More Lives** erst auslöst, sobald die
Leben tatsächlich 0 erreichen. Fügen Sie dieses Event zu
`obj_game_controller` hinzu: **Other Events** → **No More Lives** →
**Output** → **Show Message** (`Game Over!`) → **Room** → **Restart
Game**.

---

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| Der Spieler fällt durch den Boden | Prüfen Sie, ob `obj_ground` "Solid" aktiviert hat |
| Der Spieler kann nicht springen | Prüfen Sie, ob das Event Key Press → Up Arrow existiert und Set Vertical Speed negativ ist |
| Der Spieler steigt nach der Landung weiter | Stellen Sie sicher, dass Collision with obj_ground eine Stop-Movement-Aktion hat |
| Der Sprung fühlt sich schwebend an | Erhöhen Sie den Gravity-Wert von Set Gravity, oder machen Sie den Sprungwert von Set Vertical Speed negativer |
| Der Sprung fühlt sich zu schwach an | Verringern Sie den Gravity-Wert von Set Gravity, oder machen Sie den Sprungwert von Set Vertical Speed negativer |

---

## Was Sie gelernt haben

Herzlichen Glückwunsch! Sie haben ein Plattformer-Spiel erstellt! Sie haben gelernt:

- **Schwerkraftphysik** - Set Gravity wendet bei jedem Schritt eine konstante Abwärtskraft an
- **Sprungmechanik** - Ein Key-Press-Event (nicht held) gibt einen einzelnen Geschwindigkeitsimpuls nach oben
- **Eingebaute solide Kollision** - Der Boden blockiert den Spieler automatisch, sobald er als Solid markiert ist, ohne manuellen Positionsprüfungs-Code
- **Gefahren** - Objekte erstellen, die das Level neu starten
- **Level-Design** - Plattformer-Herausforderungen bauen

---

## Herausforderungs-Ideen

1. **Wandsprung** - Von Wänden abspringen erlauben
2. **Dash-Bewegung** - Kurzer horizontaler Geschwindigkeitsschub
3. **Bröckelnde Plattformen** - Plattformen, die fallen, nachdem man sie betreten hat
4. **Kontrollpunkte** - Fortschritt mitten im Level speichern
5. **Bosskampf** - Einen Endgegner mit mehreren Treffern hinzufügen

---

## Siehe auch

- [Tutorials](Tutorials_de) - Mehr Spiel-Tutorials
- [Fortgeschrittenen-Preset](Intermediate-Preset_de) - Überblick über das Preset, das der Abschnitt Erweiterungen braucht
- [Tutorial: Labyrinth](Tutorial-Maze_de) - Ein Labyrinth-Navigationsspiel erstellen
- [Tutorial: Breakout](Tutorial-Breakout_de) - Ein Breakout-Spiel erstellen
- [Event-Referenz](Event-Reference_de) - Vollständige Event-Dokumentation
