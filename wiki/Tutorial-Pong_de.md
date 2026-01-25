# Anleitung: Ein klassisches Pong-Spiel erstellen

> **Wählen Sie Ihre Sprache / Select your language / Choisissez votre langue:**
>
> [English](Tutorial-Pong) | [Français](Tutorial-Pong_fr) | [Deutsch](Tutorial-Pong_de) | [Italiano](Tutorial-Pong_it) | [Español](Tutorial-Pong_es) | [Português](Tutorial-Pong_pt) | [Slovenščina](Tutorial-Pong_sl) | [Українська](Tutorial-Pong_uk) | [Русский](Tutorial-Pong_ru)

---

## Einführung

In dieser Anleitung werden Sie ein klassisches **Pong**-Spiel erstellen - eines der ersten Videospiele, die je gemacht wurden! Pong ist ein Zwei-Spieler-Spiel, bei dem jeder Spieler einen Schläger kontrolliert und versucht, den Ball über den Schläger des Gegners zu treffen, um Punkte zu erzielen.

**Das werden Sie lernen:**
- Sprites für Schläger, Ball und Wände erstellen
- Tastatureingaben für zwei Spieler verarbeiten
- Objekte zum Abprallen bringen
- Punkte für beide Spieler verfolgen und anzeigen
- Globale Variablen verwenden

**Schwierigkeitsgrad:** Anfänger
**Vorgabe:** Anfänger-Vorgabe

---

## Schritt 1: Planen Sie Ihr Spiel

Bevor wir beginnen, schauen wir uns an, was wir brauchen:

| Element | Zweck |
|---------|-------|
| **Ball** | Springt zwischen den Spielern hin und her |
| **Linker Schläger** | Spieler 1 steuert ihn mit W/S-Tasten |
| **Rechter Schläger** | Spieler 2 steuert ihn mit Pfeil oben/unten |
| **Wände** | Obere und untere Grenzen |
| **Tore** | Unsichtbare Bereiche hinter jedem Schläger zur Punkteerkennung |
| **Punkteanzeige** | Zeigt die Punkte beider Spieler an |

---

## Schritt 2: Erstellen Sie die Sprites

### 2.1 Ball-Sprite

1. Klicken Sie im **Ressourcenbaum** mit der rechten Maustaste auf **Sprites** und wählen Sie **Sprite erstellen**
2. Geben Sie ihm den Namen `spr_ball`
3. Klicken Sie auf **Sprite bearbeiten**, um den Sprite-Editor zu öffnen
4. Zeichnen Sie einen kleinen weißen Kreis (ungefähr 16x16 Pixel)
5. Klicken Sie auf **OK**, um zu speichern

### 2.2 Schläger-Sprites

Wir erstellen zwei Schläger - einen für jeden Spieler:

**Linker Schläger (Spieler 1):**
1. Erstellen Sie ein neues Sprite mit dem Namen `spr_paddle_left`
2. Zeichnen Sie ein hohes, dünnes Rechteck, das wie eine Klammer ")" gekrümmt ist - blaue Farbe empfohlen
3. Größe: ungefähr 16x64 Pixel

**Rechter Schläger (Spieler 2):**
1. Erstellen Sie ein neues Sprite mit dem Namen `spr_paddle_right`
2. Zeichnen Sie ein hohes, dünnes Rechteck, das wie eine Klammer "(" gekrümmt ist - rote Farbe empfohlen
3. Größe: ungefähr 16x64 Pixel

### 2.3 Wand-Sprite

1. Erstellen Sie ein neues Sprite mit dem Namen `spr_wall`
2. Zeichnen Sie ein durchgehendes Rechteck (grau oder weiß)
3. Größe: 32x32 Pixel (wir dehnen es im Raum)

### 2.4 Tor-Sprite (Unsichtbar)

1. Erstellen Sie ein neues Sprite mit dem Namen `spr_goal`
2. Machen Sie es 32x32 Pixel groß
3. Lassen Sie es transparent oder machen Sie es einfarbig (es wird im Spiel unsichtbar sein)

---

## Schritt 3: Erstellen Sie das Wand-Objekt

Das Wand-Objekt erzeugt Grenzen am oberen und unteren Rand des Spielbereichs.

1. Klicken Sie mit der rechten Maustaste auf **Objekte** und wählen Sie **Objekt erstellen**
2. Geben Sie ihm den Namen `obj_wall`
3. Stellen Sie das Sprite auf `spr_wall` ein
4. **Aktivieren Sie das Kontrollkästchen "Solid"** - das ist wichtig zum Abprallen!
5. Keine Ereignisse erforderlich - die Wand sitzt einfach dort

---

## Schritt 4: Erstellen Sie die Schläger-Objekte

### 4.1 Linker Schläger (Spieler 1)

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_paddle_left`
2. Stellen Sie das Sprite auf `spr_paddle_left` ein
3. **Aktivieren Sie das Kontrollkästchen "Solid"**

**Tastaturereignisse für die Bewegung hinzufügen:**

**Ereignis: Taste W drücken**
1. Ereignis hinzufügen → Tastatur → W drücken
2. Aktion hinzufügen: **Bewegen** → **Vertikale Geschwindigkeit setzen**
3. Setzen Sie die vertikale Geschwindigkeit auf `-8` (bewegt sich nach oben)

**Ereignis: Taste W loslassen**
1. Ereignis hinzufügen → Tastatur → W loslassen
2. Aktion hinzufügen: **Bewegen** → **Vertikale Geschwindigkeit setzen**
3. Setzen Sie die vertikale Geschwindigkeit auf `0` (stoppt die Bewegung)

**Ereignis: Taste S drücken**
1. Ereignis hinzufügen → Tastatur → S drücken
2. Aktion hinzufügen: **Bewegen** → **Vertikale Geschwindigkeit setzen**
3. Setzen Sie die vertikale Geschwindigkeit auf `8` (bewegt sich nach unten)

**Ereignis: Taste S loslassen**
1. Ereignis hinzufügen → Tastatur → S loslassen
2. Aktion hinzufügen: **Bewegen** → **Vertikale Geschwindigkeit setzen**
3. Setzen Sie die vertikale Geschwindigkeit auf `0` (stoppt die Bewegung)

**Ereignis: Kollision mit obj_wall**
1. Ereignis hinzufügen → Kollision → obj_wall
2. Aktion hinzufügen: **Bewegen** → **Von Objekten abprallen**
3. Wählen Sie "Von festen Objekten abprallen"

### 4.2 Rechter Schläger (Spieler 2)

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_paddle_right`
2. Stellen Sie das Sprite auf `spr_paddle_right` ein
3. **Aktivieren Sie das Kontrollkästchen "Solid"**

**Tastaturereignisse für die Bewegung hinzufügen:**

**Ereignis: Taste Pfeil oben drücken**
1. Ereignis hinzufügen → Tastatur → Pfeil oben drücken
2. Aktion hinzufügen: **Bewegen** → **Vertikale Geschwindigkeit setzen**
3. Setzen Sie die vertikale Geschwindigkeit auf `-8`

**Ereignis: Taste Pfeil oben loslassen**
1. Ereignis hinzufügen → Tastatur → Pfeil oben loslassen
2. Aktion hinzufügen: **Bewegen** → **Vertikale Geschwindigkeit setzen**
3. Setzen Sie die vertikale Geschwindigkeit auf `0`

**Ereignis: Taste Pfeil unten drücken**
1. Ereignis hinzufügen → Tastatur → Pfeil unten drücken
2. Aktion hinzufügen: **Bewegen** → **Vertikale Geschwindigkeit setzen**
3. Setzen Sie die vertikale Geschwindigkeit auf `8`

**Ereignis: Taste Pfeil unten loslassen**
1. Ereignis hinzufügen → Tastatur → Pfeil unten loslassen
2. Aktion hinzufügen: **Bewegen** → **Vertikale Geschwindigkeit setzen**
3. Setzen Sie die vertikale Geschwindigkeit auf `0`

**Ereignis: Kollision mit obj_wall**
1. Ereignis hinzufügen → Kollision → obj_wall
2. Aktion hinzufügen: **Bewegen** → **Von Objekten abprallen**
3. Wählen Sie "Von festen Objekten abprallen"

---

## Schritt 5: Erstellen Sie das Ball-Objekt

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_ball`
2. Stellen Sie das Sprite auf `spr_ball` ein

**Ereignis: Erstellen**
1. Ereignis hinzufügen → Erstellen
2. Aktion hinzufügen: **Bewegen** → **In Richtung zu bewegen beginnen**
3. Wählen Sie eine diagonale Richtung (nicht gerade oben oder unten)
4. Setzen Sie die Geschwindigkeit auf `6`

**Ereignis: Kollision mit obj_paddle_left**
1. Ereignis hinzufügen → Kollision → obj_paddle_left
2. Aktion hinzufügen: **Bewegen** → **Von Objekten abprallen**
3. Wählen Sie "Von festen Objekten abprallen"

**Ereignis: Kollision mit obj_paddle_right**
1. Ereignis hinzufügen → Kollision → obj_paddle_right
2. Aktion hinzufügen: **Bewegen** → **Von Objekten abprallen**
3. Wählen Sie "Von festen Objekten abprallen"

**Ereignis: Kollision mit obj_wall**
1. Ereignis hinzufügen → Kollision → obj_wall
2. Aktion hinzufügen: **Bewegen** → **Von Objekten abprallen**
3. Wählen Sie "Von festen Objekten abprallen"

---

## Schritt 6: Erstellen Sie die Tor-Objekte

Tore sind unsichtbare Bereiche hinter jedem Schläger. Wenn der Ball ein Tor erreicht, erzielt der gegnerische Spieler einen Punkt.

### 6.1 Linkes Tor

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_goal_left`
2. Stellen Sie das Sprite auf `spr_goal` ein
3. **Deaktivieren Sie "Sichtbar"** - das Tor sollte unsichtbar sein
4. **Aktivieren Sie "Solid"**

### 6.2 Rechtes Tor

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_goal_right`
2. Stellen Sie das Sprite auf `spr_goal` ein
3. **Deaktivieren Sie "Sichtbar"**
4. **Aktivieren Sie "Solid"**

### 6.3 Tor-Kollisionsereignisse zum Ball hinzufügen

Gehen Sie zurück zu `obj_ball` und fügen Sie diese Ereignisse hinzu:

**Ereignis: Kollision mit obj_goal_left**
1. Ereignis hinzufügen → Kollision → obj_goal_left
2. Aktion hinzufügen: **Bewegen** → **Zu Startposition springen** (setzt den Ball zurück)
3. Aktion hinzufügen: **Punkte** → **Punkte setzen**
   - Variable: `global.p2score`
   - Wert: `1`
   - Aktivieren Sie "Relativ" (addiert 1 zur aktuellen Punktzahl)

**Ereignis: Kollision mit obj_goal_right**
1. Ereignis hinzufügen → Kollision → obj_goal_right
2. Aktion hinzufügen: **Bewegen** → **Zu Startposition springen**
3. Aktion hinzufügen: **Punkte** → **Punkte setzen**
   - Variable: `global.p1score`
   - Wert: `1`
   - Aktivieren Sie "Relativ"

---

## Schritt 7: Erstellen Sie das Punkteanzeige-Objekt

1. Erstellen Sie ein neues Objekt mit dem Namen `obj_score`
2. Kein Sprite erforderlich

**Ereignis: Erstellen**
1. Ereignis hinzufügen → Erstellen
2. Aktion hinzufügen: **Punkte** → **Punkte setzen**
   - Variable: `global.p1score`
   - Wert: `0`
3. Aktion hinzufügen: **Punkte** → **Punkte setzen**
   - Variable: `global.p2score`
   - Wert: `0`

**Ereignis: Zeichnen**
1. Ereignis hinzufügen → Zeichnen
2. Aktion hinzufügen: **Zeichnen** → **Text zeichnen**
   - Text: `Spieler 1:`
   - X: `10`
   - Y: `10`
3. Aktion hinzufügen: **Zeichnen** → **Variable zeichnen**
   - Variable: `global.p1score`
   - X: `100`
   - Y: `10`
4. Aktion hinzufügen: **Zeichnen** → **Text zeichnen**
   - Text: `Spieler 2:`
   - X: `10`
   - Y: `30`
5. Aktion hinzufügen: **Zeichnen** → **Variable zeichnen**
   - Variable: `global.p2score`
   - X: `100`
   - Y: `30`

---

## Schritt 8: Entwerfen Sie den Raum

1. Klicken Sie mit der rechten Maustaste auf **Räume** und wählen Sie **Raum erstellen**
2. Geben Sie ihm den Namen `room_pong`
3. Stellen Sie die Raumgröße ein (z. B. 640x480)

**Platzieren Sie die Objekte:**

1. **Wände**: Platzieren Sie `obj_wall`-Instanzen entlang der oberen und unteren Kanten des Raumes
2. **Linker Schläger**: Platzieren Sie `obj_paddle_left` in der Nähe der linken Kante, vertikal zentriert
3. **Rechter Schläger**: Platzieren Sie `obj_paddle_right` in der Nähe der rechten Kante, vertikal zentriert
4. **Ball**: Platzieren Sie `obj_ball` in der Mitte des Raumes
5. **Tore**:
   - Platzieren Sie `obj_goal_left`-Instanzen entlang der linken Kante (hinter wo der Schläger ist)
   - Platzieren Sie `obj_goal_right`-Instanzen entlang der rechten Kante
6. **Punkteanzeige**: Platzieren Sie `obj_score` überall (es hat keine Grafik, es zeichnet nur Text)

**Raumlayout-Beispiel:**
```
[WALL WALL WALL WALL WALL WALL WALL WALL WALL WALL]
[GOAL]  [PADDLE_L]            [BALL]            [PADDLE_R]  [GOAL]
[GOAL]  [PADDLE_L]                              [PADDLE_R]  [GOAL]
[GOAL]                                                      [GOAL]
[WALL WALL WALL WALL WALL WALL WALL WALL WALL WALL]
```

---

## Schritt 9: Testen Sie Ihr Spiel!

1. Klicken Sie auf **Ausführen** oder drücken Sie **F5**, um Ihr Spiel zu testen
2. Spieler 1 verwendet **W** (nach oben) und **S** (nach unten)
3. Spieler 2 verwendet **Pfeil oben** und **Pfeil unten**
4. Versuchen Sie, den Ball über den Schläger des Gegners zu treffen!

---

## Verbesserungen (Optional)

### Geschwindigkeitserhöhung
Machen Sie den Ball schneller, jedes Mal wenn er einen Schläger trifft, indem Sie zu den Kollisionsereignissen folgende Aktion hinzufügen:
- Nach der Abprall-Aktion fügen Sie **Bewegen** → **Geschwindigkeit setzen** hinzu
- Setzen Sie die Geschwindigkeit auf `speed + 0.5` mit "Relativ" aktiviert

### Soundeffekte
Fügen Sie Sounds hinzu, wenn:
- Der Ball einen Schläger trifft
- Der Ball eine Wand trifft
- Ein Spieler einen Punkt erzielt

### Gewinnbedingung
Fügen Sie eine Überprüfung im Zeichnen-Ereignis hinzu:
- Wenn `global.p1score >= 10`, zeigen Sie "Spieler 1 gewinnt!" an
- Wenn `global.p2score >= 10`, zeigen Sie "Spieler 2 gewinnt!" an

---

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| Der Ball geht durch den Schläger | Stellen Sie sicher, dass Schläger "Solid" aktiviert haben |
| Der Schläger stoppt nicht an den Wänden | Fügen Sie ein Kollisionsereignis mit obj_wall hinzu |
| Die Punkte werden nicht aktualisiert | Überprüfen Sie, dass die Variablennamen genau übereinstimmen (global.p1score, global.p2score) |
| Der Ball bewegt sich nicht | Überprüfen Sie, dass das Erstellen-Ereignis die Bewegungsaktion hat |

---

## Das haben Sie gelernt

Glückwunsch! Sie haben ein komplettes Zwei-Spieler-Pong-Spiel erstellt! Sie haben gelernt:

- Wie man Tastatureingaben für zwei verschiedene Spieler verarbeitet
- Wie man Tastenlos-Ereignisse verwendet, um die Bewegung zu stoppen
- Wie man Objekte zum Abprallen bringt
- Wie man globale Variablen zur Verfolgung von Punkten verwendet
- Wie man Text und Variablen auf dem Bildschirm anzeigt

---

## Siehe auch

- [Anfänger-Vorgabe](Beginner-Preset_de) - Übersicht über Anfänger-Funktionen
- [Anleitung: Breakout](Tutorial-Breakout_de) - Ein Brick-Breaker-Spiel erstellen
- [Ereignis-Referenz](Event-Reference_de) - Komplette Ereignisdokumentation
- [Vollständige Aktions-Referenz](Full-Action-Reference_de) - Alle verfügbaren Aktionen
