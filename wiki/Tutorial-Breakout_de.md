# Tutorial: Ein Breakout-Spiel erstellen

*[Home](Home_de) | [Beginner Preset](Beginner-Preset_de) | [English](Tutorial-Breakout) | [Deutsch](Tutorial-Breakout_de)*

Dieses Tutorial führt dich durch die Erstellung eines klassischen Breakout-Spiels. Es ist ein perfektes erstes Projekt, um PyGameMaker zu lernen!

![Breakout Game Concept](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

---

## Was du lernen wirst

- Sprites erstellen und verwenden
- Spielobjekte mit Events und Aktionen einrichten
- Tastatursteuerung für die Spielerbewegung
- Kollisionserkennung und Abprallen
- Objekte bei Kollision zerstören
- Einen Spielraum bauen

---

## Schritt 1: Die Sprites erstellen

Zuerst müssen wir die visuellen Elemente für unser Spiel erstellen.

### 1.1 Das Paddle-Sprite erstellen
1. Im **Assets**-Panel, Rechtsklick auf **Sprites** -> **Create Sprite**
2. Nenne es `spr_paddle`
3. Zeichne ein horizontales Rechteck (etwa 64x16 Pixel)
4. **Wichtig:** Klicke auf **Center**, um den Ursprung in die Mitte zu setzen

### 1.2 Das Ball-Sprite erstellen
1. Erstelle ein weiteres Sprite namens `spr_ball`
2. Zeichne einen kleinen Kreis (etwa 16x16 Pixel)
3. Klicke auf **Center**, um den Ursprung zu setzen

### 1.3 Das Brick-Sprite erstellen
1. Erstelle ein Sprite namens `spr_brick`
2. Zeichne ein Rechteck (etwa 48x24 Pixel)
3. Klicke auf **Center**, um den Ursprung zu setzen

### 1.4 Das Wall-Sprite erstellen
1. Erstelle ein Sprite namens `spr_wall`
2. Zeichne ein Quadrat (etwa 32x32 Pixel) - dies wird die Begrenzung
3. Klicke auf **Center**, um den Ursprung zu setzen

### 1.5 Einen Hintergrund erstellen (Optional)
1. Rechtsklick auf **Backgrounds** -> **Create Background**
2. Nenne es `bg_game`
3. Zeichne oder lade ein Hintergrundbild

---

## Schritt 2: Das Paddle-Objekt erstellen

Jetzt programmieren wir das Paddle, das der Spieler steuert.

### 2.1 Das Objekt erstellen
1. Rechtsklick auf **Objects** -> **Create Object**
2. Nenne es `obj_paddle`
3. Setze das **Sprite** auf `spr_paddle`
4. Aktiviere das **Solid**-Kontrollkästchen

### 2.2 Rechtspfeil-Bewegung hinzufügen
1. Klicke auf **Add Event** -> **Keyboard** -> wähle **Right Arrow**
2. Füge die Aktion **Set Horizontal Speed** hinzu
3. Setze **value** auf `5` (oder eine beliebige Geschwindigkeit)

### 2.3 Linkspfeil-Bewegung hinzufügen
1. Klicke auf **Add Event** -> **Keyboard** -> wähle **Left Arrow**
2. Füge die Aktion **Set Horizontal Speed** hinzu
3. Setze **value** auf `-5`

### 2.4 Stoppen, wenn Tasten losgelassen werden
Das Paddle bewegt sich weiter, auch nachdem die Taste losgelassen wurde! Lass uns das beheben.

1. Klicke auf **Add Event** -> **Keyboard Release** -> wähle **Right Arrow**
2. Füge die Aktion **Set Horizontal Speed** hinzu
3. Setze **value** auf `0`

4. Klicke auf **Add Event** -> **Keyboard Release** -> wähle **Left Arrow**
5. Füge die Aktion **Set Horizontal Speed** hinzu
6. Setze **value** auf `0`

Jetzt stoppt das Paddle, wenn du die Pfeiltasten loslässt.

---

## Schritt 3: Das Ball-Objekt erstellen

### 3.1 Das Objekt erstellen
1. Erstelle ein neues Objekt namens `obj_ball`
2. Setze das **Sprite** auf `spr_ball`
3. Aktiviere das **Solid**-Kontrollkästchen

### 3.2 Anfangsbewegung setzen
1. Klicke auf **Add Event** -> **Create**
2. Füge die Aktion **Move in Direction** hinzu (oder **Set Horizontal/Vertical Speed**)
3. Setze eine diagonale Richtung mit Geschwindigkeit `5`
   - Zum Beispiel: **hspeed** = `4`, **vspeed** = `-4`

Dies lässt den Ball starten, wenn das Spiel beginnt.

### 3.3 Vom Paddle abprallen
1. Klicke auf **Add Event** -> **Collision** -> wähle `obj_paddle`
2. Füge die Aktion **Reverse Vertical** hinzu (zum Abprallen)

### 3.4 Von Wänden abprallen
1. Klicke auf **Add Event** -> **Collision** -> wähle `obj_wall`
2. Füge die Aktion **Reverse Horizontal** oder **Reverse Vertical** nach Bedarf hinzu
   - Oder verwende beide, um Eckabpraller zu handhaben

---

## Schritt 4: Das Brick-Objekt erstellen

### 4.1 Das Objekt erstellen
1. Erstelle ein neues Objekt namens `obj_brick`
2. Setze das **Sprite** auf `spr_brick`
3. Aktiviere das **Solid**-Kontrollkästchen

### 4.2 Bei Ball-Kollision zerstören
1. Klicke auf **Add Event** -> **Collision** -> wähle `obj_ball`
2. Füge die Aktion **Destroy Instance** mit Ziel **self** hinzu

Dies zerstört den Brick, wenn der Ball ihn trifft!

### 4.3 Den Ball abprallen lassen
Im selben Kollisions-Event, füge auch hinzu:
1. Füge die Aktion **Reverse Vertical** hinzu (angewendet auf **other** - den Ball)

Oder gehe zurück zu `obj_ball` und füge hinzu:
1. **Add Event** -> **Collision** -> wähle `obj_brick`
2. Füge die Aktion **Reverse Vertical** hinzu

---

## Schritt 5: Das Wall-Objekt erstellen

### 5.1 Das Objekt erstellen
1. Erstelle ein neues Objekt namens `obj_wall`
2. Setze das **Sprite** auf `spr_wall`
3. Aktiviere das **Solid**-Kontrollkästchen

Das ist alles - die Wand muss nur solid sein, damit der Ball davon abprallt.

---

## Schritt 6: Den Spielraum erstellen

### 6.1 Den Raum erstellen
1. Rechtsklick auf **Rooms** -> **Create Room**
2. Nenne es `room_game`

### 6.2 Den Hintergrund setzen (Optional)
1. In den Raum-Einstellungen, finde **Background**
2. Wähle deinen `bg_game` Hintergrund
3. Aktiviere **Stretch**, wenn er den Raum füllen soll

### 6.3 Die Objekte platzieren

Jetzt platziere deine Objekte im Raum:

1. **Platziere das Paddle:** Setze `obj_paddle` unten in die Mitte des Raums

2. **Platziere die Wände:** Setze `obj_wall`-Instanzen an die Ränder:
   - Entlang der Oberseite
   - Entlang der linken Seite
   - Entlang der rechten Seite
   - Lass die Unterseite offen (hier kann der Ball entkommen!)

3. **Platziere den Ball:** Setze `obj_ball` irgendwo in die Mitte

4. **Platziere die Bricks:** Ordne `obj_brick`-Instanzen in Reihen oben im Raum an

---

## Schritt 7: Teste dein Spiel!

1. Klicke auf den **Play**-Button (grüner Pfeil)
2. Benutze die **Links**- und **Rechts**-Pfeiltasten, um das Paddle zu bewegen
3. Versuche, den Ball abprallen zu lassen, um alle Bricks zu zerstören!
4. Drücke **Escape** zum Beenden

---

## Was kommt als Nächstes?

Dein grundlegendes Breakout-Spiel ist fertig! Hier sind einige Verbesserungen zum Ausprobieren:

### Ein Leben-System hinzufügen
- Füge ein **No More Lives**-Event hinzu, um „Game Over" anzuzeigen
- Verliere ein Leben, wenn der Ball unten herausfällt

### Punktestand hinzufügen
- Benutze die **Add Score**-Aktion beim Zerstören von Bricks
- Zeige den Punktestand mit **Draw Score** an

### Mehrere Levels hinzufügen
- Erstelle mehr Räume mit verschiedenen Brick-Anordnungen
- Benutze **Next Room**, wenn alle Bricks zerstört sind

### Soundeffekte hinzufügen
- Füge Sounds für Abprallen und Brick-Zerstörung hinzu
- Benutze die **Play Sound**-Aktion

---

## Zusammenfassung der Objekte

| Objekt | Sprite | Solid | Events |
|--------|--------|-------|--------|
| `obj_paddle` | `spr_paddle` | Ja | Keyboard (Left/Right), Keyboard Release |
| `obj_ball` | `spr_ball` | Ja | Create, Collision (paddle, wall, brick) |
| `obj_brick` | `spr_brick` | Ja | Collision (ball) - Destroy self |
| `obj_wall` | `spr_wall` | Ja | Keine benötigt |

---

## Siehe auch

- [Beginner Preset](Beginner-Preset_de) - Events und Aktionen, die in diesem Tutorial verwendet werden
- [Event Reference](Event-Reference_de) - Alle verfügbaren Events
- [Full Action Reference](Full-Action-Reference_de) - Alle verfügbaren Aktionen
