# Einführung in die Videospiel-Erstellung mit PyGameMaker

*[Home](Home_de) | [Beginner Preset](Beginner-Preset_de) | [English](Getting-Started-Breakout) | [Français](Getting-Started-Breakout_fr)*

**Vom PyGameMaker-Team**

---

In diesem Tutorial lernen wir die Grundlagen der Spielerstellung mit PyGameMaker. Da es sich um eine relativ umfangreiche Software mit vielen Funktionen handelt, konzentrieren wir uns nur auf diejenigen, die uns während dieses Tutorials helfen werden.

Wir werden ein einfaches Breakout-Spiel erstellen, das so aussehen wird:

![Breakout-Spielkonzept](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

Dieses Tutorial ist auch für dich geeignet, wenn du keine Programmierkenntnisse hast, da PyGameMaker es Anfängern ermöglicht, unabhängig von ihrem Kenntnisstand einfach Spiele zu erstellen.

Also gut, fangen wir mit dem Design unseres Spiels an!

---

## Schritt 1: Erste Schritte

Beginne damit, PyGameMaker zu öffnen. Du solltest die Hauptoberfläche mit dem **Assets**-Panel auf der linken Seite sehen, das verschiedene Ressourcenkategorien auflistet: Sprites, Sounds, Hintergründe, Schriftarten, Objekte und Räume.

Bevor wir irgendetwas anderes tun: In einem Videospiel ist das Erste, was der Spieler bemerkt, das, was er auf dem Bildschirm sieht. Dies ist tatsächlich die Grundlage eines Spiels: Ein Spiel ohne Grafik existiert nicht (oder es ist ein sehr spezieller Fall). Wir werden daher damit beginnen, Bilder in unser Spiel einzufügen, die die grafische Darstellung der Objekte sein werden, die der Spieler auf dem Bildschirm sehen wird. In der Spielentwicklungsterminologie werden diese Bilder **Sprites** genannt.

---

## Schritt 2: Erstellen der Sprites

### 2.1 Erstellen des Schläger-Sprites

1. Klicke mit der rechten Maustaste auf den **Sprites**-Ordner oben in der linken Spalte
2. Klicke auf **Create Sprite**
3. Ein Fenster namens **Sprite Properties** öffnet sich - hier definierst du alle Eigenschaften deines Sprites
4. Verwende den eingebauten Editor, um ein horizontales Rechteck (etwa 64x16 Pixel) in einer Farbe deiner Wahl zu zeichnen
5. **Wichtig:** Klicke auf **Center**, um den Ursprung in der Mitte deines Sprites zu setzen
   > Der Ursprung eines Sprites ist sein Mittelpunkt, seine X:0 und Y:0 Koordinaten. Dies sind seine Basiskoordinaten.
6. Ändere den Namen deines Sprites im Textfeld oben und gib `spr_paddle` ein
   > Dies hat keine technische Auswirkung - es dient nur dazu, dir zu helfen, deine Dateien besser zu navigieren, sobald du mehr davon hast. Du kannst jeden beliebigen Namen wählen; dies ist nur ein Beispiel.
7. Klicke auf **OK**

Du hast gerade dein erstes Sprite erstellt! Dies ist dein Schläger, das Objekt, das der Spieler steuern wird, um den Ball zu fangen.

### 2.2 Erstellen des Ball-Sprites

Lass uns fortfahren und weitere Sprites hinzufügen. Wiederhole den gleichen Vorgang:

1. Rechtsklick auf **Sprites** → **Create Sprite**
2. Zeichne einen kleinen Kreis (etwa 16x16 Pixel)
3. Klicke auf **Center**, um den Ursprung zu setzen
4. Nenne es `spr_ball`
5. Klicke auf **OK**

### 2.3 Erstellen der Stein-Sprites

Wir brauchen drei Arten von Steinen. Erstelle sie nacheinander:

**Erster Stein (Zerstörbar):**
1. Erstelle ein neues Sprite
2. Zeichne ein Rechteck (etwa 48x24 Pixel) - verwende eine leuchtende Farbe wie Rot
3. Klicke auf **Center**, nenne es `spr_brick_1`
4. Klicke auf **OK**

**Zweiter Stein (Zerstörbar):**
1. Erstelle ein neues Sprite
2. Zeichne ein Rechteck (gleiche Größe) - verwende eine andere Farbe wie Blau
3. Klicke auf **Center**, nenne es `spr_brick_2`
4. Klicke auf **OK**

**Dritter Stein (Unzerstörbare Wand):**
1. Erstelle ein neues Sprite
2. Zeichne ein Rechteck (gleiche Größe) - verwende eine dunklere Farbe wie Grau
3. Klicke auf **Center**, nenne es `spr_brick_3`
4. Klicke auf **OK**

Du solltest jetzt alle Sprites für unser Spiel haben:
- `spr_paddle` - Der Schläger des Spielers
- `spr_ball` - Der springende Ball
- `spr_brick_1` - Erster zerstörbarer Stein
- `spr_brick_2` - Zweiter zerstörbarer Stein
- `spr_brick_3` - Unzerstörbarer Wandstein

> **Hinweis:** In Spielen gibt es im Allgemeinen zwei Hauptquellen für die grafische Darstellung: **Sprites** und **Hintergründe**. Das ist alles, was das ausmacht, was du auf dem Bildschirm siehst. Ein Hintergrund ist, wie der Name schon sagt, ein Hintergrundbild.

---

## Schritt 3: Verstehen von Objekten und Events

Was haben wir am Anfang gesagt? Das Erste, was der Spieler bemerkt, ist das, was er auf dem Bildschirm sieht. Darum haben wir uns mit unseren Sprites gekümmert. Aber ein Spiel, das nur aus Bildern besteht, ist kein Spiel - es ist ein Gemälde! Wir gehen jetzt zur nächsten Stufe über: **Objekte**.

Ein Objekt ist eine Entität in deinem Spiel, die Verhaltensweisen haben, auf Events reagieren und mit anderen Objekten interagieren kann. Das Sprite ist nur die visuelle Darstellung; das Objekt ist das, was ihm Leben verleiht.

### Wie Spiellogik funktioniert

Alles in der Spielprogrammierung folgt diesem Muster: **Wenn das passiert, dann führe ich das aus.**

- Wenn der Spieler eine Taste drückt, dann mache ich dies
- Wenn diese Variable diesem Wert entspricht, dann mache ich das
- Wenn zwei Objekte kollidieren, dann passiert etwas

Dies nennen wir **Events** und **Actions** in PyGameMaker:
- **Events** = Dinge, die passieren können (Tastendruck, Kollision, Timer, usw.)
- **Actions** = Dinge, die du tun möchtest, wenn Events eintreten (bewegen, zerstören, Punktestand ändern, usw.)

---

## Schritt 4: Erstellen des Schläger-Objekts

Lass uns das Objekt erstellen, das der Spieler steuern wird: den Schläger.

### 4.1 Erstellen des Objekts

1. Rechtsklick auf den **Objects**-Ordner → **Create Object**
2. Nenne es `obj_paddle`
3. Wähle im **Sprite**-Dropdown `spr_paddle` aus - jetzt hat unser Objekt ein visuelles Erscheinungsbild!
4. Aktiviere das **Solid**-Kontrollkästchen (wir brauchen das für Kollisionen)

### 4.2 Programmieren der Bewegung

In einem Breakout-Spiel müssen wir den Schläger bewegen, um zu verhindern, dass der Ball unten entkommt. Wir steuern ihn mit der Tastatur.

**Nach rechts bewegen:**
1. Klicke auf **Add Event** → **Keyboard** → **Right Arrow**
2. Füge aus dem Aktions-Panel auf der rechten Seite die Aktion **Set Horizontal Speed** hinzu
3. Setze den **value** auf `5`
4. Klicke auf **OK**

Das bedeutet: "Wenn die Pfeiltaste nach rechts gedrückt wird, setze die horizontale Geschwindigkeit auf 5 (Bewegung nach rechts)."

**Nach links bewegen:**
1. Klicke auf **Add Event** → **Keyboard** → **Left Arrow**
2. Füge die Aktion **Set Horizontal Speed** hinzu
3. Setze den **value** auf `-5`
4. Klicke auf **OK**

**Stoppen, wenn Tasten losgelassen werden:**

Wenn wir jetzt testen würden, würde der Schläger sich weiter bewegen, auch nachdem die Taste losgelassen wurde! Lass uns das beheben:

1. Klicke auf **Add Event** → **Keyboard Release** → **Right Arrow**
2. Füge die Aktion **Set Horizontal Speed** mit dem Wert `0` hinzu
3. Klicke auf **OK**

4. Klicke auf **Add Event** → **Keyboard Release** → **Left Arrow**
5. Füge die Aktion **Set Horizontal Speed** mit dem Wert `0` hinzu
6. Klicke auf **OK**

Jetzt bewegt sich unser Schläger, wenn die Tasten gedrückt werden, und stoppt, wenn sie losgelassen werden. Wir sind mit diesem Objekt vorerst fertig!

---

## Schritt 5: Erstellen des Wandstein-Objekts

Lass uns einen unzerstörbaren Wandstein erstellen - dieser wird die Grenzen unseres Spielbereichs bilden.

1. Erstelle ein neues Objekt namens `obj_brick_3`
2. Weise das Sprite `spr_brick_3` zu
3. Aktiviere das **Solid**-Kontrollkästchen

Der Ball wird von diesem Stein abprallen. Da es nur eine Wand ist, brauchen wir keine Events - es muss nur solide sein. Klicke auf **OK** zum Speichern.

---

## Schritt 6: Erstellen des Ball-Objekts

Jetzt erstellen wir den Ball, das wesentliche Element unseres Spiels.

### 6.1 Erstellen des Objekts

1. Erstelle ein neues Objekt namens `obj_ball`
2. Weise das Sprite `spr_ball` zu
3. Aktiviere das **Solid**-Kontrollkästchen

### 6.2 Anfangsbewegung

Wir möchten, dass sich der Ball von Anfang an selbstständig bewegt. Geben wir ihm eine Anfangsgeschwindigkeit und Richtung.

1. Klicke auf **Add Event** → **Create**
   > Das Create-Event führt Aktionen aus, wenn das Objekt im Spiel erscheint, d.h. wenn es die Szene betritt.
2. Füge die Aktion **Set Horizontal Speed** mit dem Wert `4` hinzu
3. Füge die Aktion **Set Vertical Speed** mit dem Wert `-4` hinzu
4. Klicke auf **OK**

Dies gibt dem Ball eine diagonale Bewegung (nach rechts und oben) zu Beginn des Spiels.

### 6.3 Abprallen vom Schläger

Wir müssen den Ball abprallen lassen, wenn er den Schläger trifft.

1. Klicke auf **Add Event** → **Collision** → wähle `obj_paddle`
   > Dieses Event wird ausgelöst, wenn der Ball mit dem Schläger kollidiert.
2. Füge die Aktion **Reverse Vertical** hinzu
   > Dies kehrt die vertikale Richtung um und lässt den Ball abprallen.
3. Klicke auf **OK**

### 6.4 Abprallen von Wänden

Die gleiche Operation für die Wandsteine:

1. Klicke auf **Add Event** → **Collision** → wähle `obj_brick_3`
2. Füge die Aktion **Reverse Vertical** hinzu
3. Füge die Aktion **Reverse Horizontal** hinzu
   > Wir fügen beide hinzu, weil der Ball die Wand aus verschiedenen Winkeln treffen könnte.
4. Klicke auf **OK**

---

## Schritt 7: Testen unseres Fortschritts - Erstellen eines Raums

Nach Sprites und Objekten kommen die **Räume**. Ein Raum ist der Ort, an dem das Spiel stattfindet: Es ist eine Karte, ein Level. Hier platzierst du alle deine Spielelemente, hier organisierst du, was auf dem Bildschirm erscheinen wird.

### 7.1 Erstellen des Raums

1. Rechtsklick auf **Rooms** → **Create Room**
2. Nenne es `room_game`

### 7.2 Platziere deine Objekte

Platziere nun deine Objekte mit der Maus:
- **Linksklick** zum Platzieren eines Objekts
- **Rechtsklick** zum Löschen eines Objekts

Wähle das zu platzierende Objekt aus dem Dropdown-Menü im Raum-Editor.

**Baue dein Level:**
1. Platziere `obj_brick_3`-Instanzen an den Rändern (oben, links, rechts) - lass den Boden offen!
2. Platziere `obj_paddle` unten in der Mitte
3. Platziere `obj_ball` irgendwo in der Mitte

### 7.3 Teste das Spiel!

Klicke auf den **Play**-Button (grüner Pfeil) in der Werkzeugleiste. Damit kannst du dein Spiel jederzeit testen.

Du kannst bereits Spaß daran haben, den Ball von den Wänden und dem Schläger abprallen zu lassen!

Es ist minimal, aber bereits ein guter Anfang - du hast dein Spielfundament!

---

## Schritt 8: Hinzufügen von zerstörbaren Steinen

Lass uns einige Steine zum Zerstören hinzufügen, um unser Spiel unterhaltsamer zu machen.

### 8.1 Erster zerstörbarer Stein

1. Erstelle ein neues Objekt namens `obj_brick_1`
2. Weise das Sprite `spr_brick_1` zu
3. Aktiviere **Solid**

Wir fügen das Verhalten hinzu, sich selbst zu zerstören, wenn er vom Ball getroffen wird:

1. Klicke auf **Add Event** → **Collision** → wähle `obj_ball`
2. Füge die Aktion **Destroy Instance** mit Ziel **self** hinzu
   > Diese Aktion entfernt ein Objekt während des Spiels - hier den Stein selbst.
3. Klicke auf **OK**

Und schon hast du deinen neuen zerstörbaren Stein!

### 8.2 Zweiter zerstörbarer Stein (mit Parent)

Jetzt erstellen wir einen zweiten zerstörbaren Stein, aber ohne ihn neu programmieren zu müssen. Wir machen ihn mit der **Parent**-Funktion zu einem "Klon".

1. Erstelle ein neues Objekt namens `obj_brick_2`
2. Weise das Sprite `spr_brick_2` zu
3. Aktiviere **Solid**
4. Wähle im **Parent**-Dropdown `obj_brick_1` aus

Was bedeutet das? Einfach, dass das, was wir in `obj_brick_1` programmiert haben, von `obj_brick_2` geerbt wird, ohne es selbst reproduzieren zu müssen. Die Eltern-Kind-Beziehung ermöglicht es Objekten, Verhaltensweisen zu teilen!

Klicke auf **OK** zum Speichern.

### 8.3 Den Ball von neuen Steinen abprallen lassen

Öffne `obj_ball` erneut durch Doppelklick und füge Kollisions-Events für unsere neuen Steine hinzu:

1. Klicke auf **Add Event** → **Collision** → wähle `obj_brick_1`
2. Füge die Aktion **Reverse Vertical** hinzu
3. Klicke auf **OK**

4. Klicke auf **Add Event** → **Collision** → wähle `obj_brick_2`
5. Füge die Aktion **Reverse Vertical** hinzu
6. Klicke auf **OK**

---

## Schritt 9: Game Over - Den Raum neu starten

Wir müssen das Level neu starten, wenn der Ball den Bildschirm verlässt (wenn der Spieler ihn nicht fängt).

In `obj_ball`:

1. Klicke auf **Add Event** → **Other** → **Outside Room**
2. Füge die Aktion **Restart Room** hinzu
   > Diese Aktion startet den aktuellen Raum während des Spiels neu.
3. Klicke auf **OK**

---

## Schritt 10: Finales Level-Design

Platziere jetzt alles in deinem Raum, um dein finales Breakout-Level zu erstellen:

1. Öffne `room_game`
2. Ordne `obj_brick_3`-Wände oben und an den Seiten an
3. Platziere Reihen von `obj_brick_1` und `obj_brick_2` in Mustern oben
4. Behalte `obj_paddle` unten in der Mitte
5. Platziere `obj_ball` über dem Schläger

**Beispiel-Layout:**
```
[3][3][3][3][3][3][3][3][3][3]
[3][1][1][2][2][1][1][2][2][3]
[3][2][2][1][1][2][2][1][1][3]
[3][1][1][2][2][1][1][2][2][3]
[3]                        [3]
[3]                        [3]
[3]         (ball)         [3]
[3]                        [3]
[3]        [paddle]        [3]
```

---

## Herzlichen Glückwunsch!

Dein Breakout-Spiel ist fertig! Du kannst jetzt deine Arbeit genießen, indem du das Spiel spielst, das du gerade erstellt hast!

Du kannst es auch weiter verfeinern, zum Beispiel durch Hinzufügen von:
- **Soundeffekte** für Abprallen und Steinzerstörung
- **Punkteverfolgung** mit der Add Score-Aktion
- **Zusätzliche Steintypen** mit verschiedenen Verhaltensweisen
- **Mehrere Level** mit verschiedenen Layouts

---

## Zusammenfassung des Gelernten

| Konzept | Beschreibung |
|---------|--------------|
| **Sprites** | Visuelle Bilder, die Objekte in deinem Spiel darstellen |
| **Objekte** | Spielentitäten mit Verhaltensweisen, die Sprites mit Events und Aktionen kombinieren |
| **Events** | Auslöser, die Aktionen ausführen (Create, Keyboard, Collision, usw.) |
| **Actions** | Operationen zum Ausführen (Bewegen, Zerstören, Abprallen, usw.) |
| **Solid** | Eigenschaft, die Kollisionserkennung ermöglicht |
| **Parent** | Ermöglicht Objekten, Verhaltensweisen von anderen Objekten zu erben |
| **Räume** | Spiellevel, in denen du Objektinstanzen platzierst |

---

## Objekt-Zusammenfassung

| Objekt | Sprite | Solid | Events |
|--------|--------|-------|--------|
| `obj_paddle` | `spr_paddle` | Ja | Keyboard (Links/Rechts), Keyboard Release |
| `obj_ball` | `spr_ball` | Ja | Create, Collision (Schläger, Steine), Outside Room |
| `obj_brick_1` | `spr_brick_1` | Ja | Collision (Ball) - Selbst zerstören |
| `obj_brick_2` | `spr_brick_2` | Ja | Erbt von `obj_brick_1` |
| `obj_brick_3` | `spr_brick_3` | Ja | Keine (nur eine Wand) |

---

## Siehe auch

- [Beginner Preset](Beginner-Preset_de) - Events und Aktionen für Anfänger verfügbar
- [Event Reference](Event-Reference_de) - Vollständige Liste aller Events
- [Full Action Reference](Full-Action-Reference_de) - Vollständige Liste aller Aktionen
- [Tutorial: Breakout](Tutorial-Breakout_de) - Kürzere Version dieses Tutorials

---

Du bist jetzt in die Grundlagen der Videospiel-Erstellung mit PyGameMaker eingeweiht. Jetzt bist du dran, deine eigenen Spiele zu erstellen!
