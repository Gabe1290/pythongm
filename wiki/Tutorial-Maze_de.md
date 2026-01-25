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
**Preset:** Anfänger-Preset

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

1. Klicken Sie mit der rechten Maustaste auf **Objekte** und wählen Sie **Objekt erstellen**
2. Nennen Sie es `obj_wall`
3. Setzen Sie das Sprite auf `spr_wall`
4. **Aktivieren Sie das Kontrollkästchen "Solid"**
5. Keine Events benötigt

---

## Schritt 4: Das Ausgang-Objekt erstellen

Der Ausgang beendet das Level, wenn der Spieler ihn erreicht.

1. Erstellen Sie ein neues Objekt namens `obj_exit`
2. Setzen Sie das Sprite auf `spr_exit`

**Event: Kollision mit obj_player**
1. Event hinzufügen → Kollision → obj_player
2. Aktion hinzufügen: **Main2** → **Nachricht anzeigen**
   - Nachricht: `Du gewinnst! Zeit: ` + string(floor(global.timer)) + ` Sekunden`
3. Aktion hinzufügen: **Main1** → **Nächster Raum** (oder **Raum neu starten** für einzelnes Level)

---

## Schritt 5: Das Münz-Objekt erstellen

Münzen erhöhen den Punktestand, wenn sie gesammelt werden.

1. Erstellen Sie ein neues Objekt namens `obj_coin`
2. Setzen Sie das Sprite auf `spr_coin`

**Event: Kollision mit obj_player**
1. Event hinzufügen → Kollision → obj_player
2. Aktion hinzufügen: **Score** → **Score setzen**
   - Neuer Score: `10`
   - Aktivieren Sie "Relativ", um 10 Punkte hinzuzufügen
3. Aktion hinzufügen: **Main1** → **Instanz zerstören**
   - Gilt für: Self

---

## Schritt 6: Das Spieler-Objekt erstellen

Der Spieler bewegt sich flüssig mit den Pfeiltasten.

1. Erstellen Sie ein neues Objekt namens `obj_player`
2. Setzen Sie das Sprite auf `spr_player`

### 6.1 Create Event - Variablen initialisieren

**Event: Create**
1. Event hinzufügen → Create
2. Aktion hinzufügen: **Kontrolle** → **Variable setzen**
   - Variable: `move_speed`
   - Wert: `4`

### 6.2 Bewegung mit Kollision

**Event: Step**
1. Event hinzufügen → Step → Step
2. Aktion hinzufügen: **Kontrolle** → **Code ausführen**

```gml
// Horizontale Bewegung
var hspd = 0;
if (keyboard_check(vk_right)) hspd = move_speed;
if (keyboard_check(vk_left)) hspd = -move_speed;

// Vertikale Bewegung
var vspd = 0;
if (keyboard_check(vk_down)) vspd = move_speed;
if (keyboard_check(vk_up)) vspd = -move_speed;

// Horizontale Kollisionsprüfung
if (!place_meeting(x + hspd, y, obj_wall)) {
    x += hspd;
} else {
    // So nah wie möglich an die Wand bewegen
    while (!place_meeting(x + sign(hspd), y, obj_wall)) {
        x += sign(hspd);
    }
}

// Vertikale Kollisionsprüfung
if (!place_meeting(x, y + vspd, obj_wall)) {
    y += vspd;
} else {
    // So nah wie möglich an die Wand bewegen
    while (!place_meeting(x, y + sign(vspd), obj_wall)) {
        y += sign(vspd);
    }
}
```

### 6.3 Alternative: Einfache Block-Bewegung

Wenn Sie lieber Aktionsblöcke statt Code verwenden:

**Event: Taste gedrückt - Pfeil rechts**
1. Event hinzufügen → Tastatur → \<Rechts\>
2. Aktion hinzufügen: **Kontrolle** → **Kollision testen**
   - Objekt: `obj_wall`
   - X: `4`
   - Y: `0`
   - Prüfen: NOT
3. Aktion hinzufügen: **Bewegung** → **Zur Position springen**
   - X: `4`
   - Y: `0`
   - Aktivieren Sie "Relativ"

Wiederholen Sie für Links (-4, 0), Oben (0, -4) und Unten (0, 4).

---

## Schritt 7: Den Spiel-Controller erstellen

Der Spiel-Controller verwaltet den Timer und zeigt Informationen an.

1. Erstellen Sie ein neues Objekt namens `obj_game_controller`
2. Kein Sprite benötigt

**Event: Create**
1. Event hinzufügen → Create
2. Aktion hinzufügen: **Kontrolle** → **Variable setzen**
   - Variable: `global.timer`
   - Wert: `0`

**Event: Step**
1. Event hinzufügen → Step → Step
2. Aktion hinzufügen: **Kontrolle** → **Variable setzen**
   - Variable: `global.timer`
   - Wert: `1/room_speed`
   - Aktivieren Sie "Relativ"

**Event: Draw**
1. Event hinzufügen → Draw → Draw
2. Aktion hinzufügen: **Kontrolle** → **Code ausführen**

```gml
// Score zeichnen
draw_set_color(c_white);
draw_text(10, 10, "Punkte: " + string(score));

// Timer zeichnen
draw_text(10, 30, "Zeit: " + string(floor(global.timer)) + "s");

// Verbleibende Münzen zeichnen
var coins_left = instance_number(obj_coin);
draw_text(10, 50, "Münzen: " + string(coins_left));
```

---

## Schritt 8: Ihr Labyrinth entwerfen

1. Klicken Sie mit der rechten Maustaste auf **Räume** und wählen Sie **Raum erstellen**
2. Nennen Sie ihn `room_maze`
3. Setzen Sie die Raumgröße (z.B. 640x480)
4. Aktivieren Sie "Am Raster ausrichten" und setzen Sie das Raster auf 32x32

### Objekte platzieren

Bauen Sie Ihr Labyrinth nach diesen Richtlinien:

1. **Erstellen Sie den Rand** - Umgeben Sie den Raum mit Wänden
2. **Bauen Sie Korridore** - Erstellen Sie Wege durch das Labyrinth
3. **Platzieren Sie den Ausgang** - Setzen Sie ihn ans Ende des Labyrinths
4. **Verteilen Sie Münzen** - Platzieren Sie sie entlang der Wege
5. **Platzieren Sie den Spieler** - Nahe am Eingang
6. **Fügen Sie den Spiel-Controller hinzu** - Irgendwo (er ist unsichtbar)

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

1. Klicken Sie auf **Ausführen** oder drücken Sie **F5** zum Testen
2. Verwenden Sie die Pfeiltasten, um durch das Labyrinth zu navigieren
3. Sammeln Sie Münzen für Punkte
4. Finden Sie den Ausgang zum Gewinnen!

---

## Erweiterungen (Optional)

### Feinde hinzufügen

Erstellen Sie einen einfachen patrouillierenden Feind:

1. Erstellen Sie `spr_enemy` (rote Farbe, 24x24)
2. Erstellen Sie `obj_enemy` mit Sprite `spr_enemy`

**Event: Create**
```gml
hspeed = 2;  // Bewegt sich horizontal
```

**Event: Kollision mit obj_wall**
```gml
hspeed = -hspeed;  // Richtung umkehren
```

**Event: Kollision mit obj_player**
```gml
room_restart();  // Spieler verliert
```

### Leben-System hinzufügen

Im Create-Event von `obj_game_controller`:
```gml
global.lives = 3;
```

Wenn der Spieler einen Feind berührt (statt neu zu starten):
```gml
global.lives -= 1;
if (global.lives <= 0) {
    show_message("Game Over!");
    game_restart();
} else {
    // Spieler am Start respawnen
    obj_player.x = start_x;
    obj_player.y = start_y;
}
```

### Schlüssel und verschlossene Türen hinzufügen

1. Erstellen Sie `obj_key` - verschwindet beim Einsammeln, setzt `global.has_key = true`
2. Erstellen Sie `obj_locked_door` - öffnet sich nur wenn `global.has_key == true`

### Mehrere Level hinzufügen

1. Erstellen Sie zusätzliche Räume (`room_maze2`, `room_maze3`)
2. In `obj_exit` verwenden Sie `room_goto_next()` statt `room_restart()`

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
| Timer funktioniert nicht | Stellen Sie sicher, dass der Spiel-Controller im Raum platziert ist |
| Bewegung fühlt sich ruckelig an | Passen Sie den `move_speed`-Wert an (versuchen Sie 3-5) |

---

## Was Sie gelernt haben

Gratulation! Sie haben ein Labyrinth-Spiel erstellt! Sie haben gelernt:

- **Flüssige Bewegung** - Gedrückte Tasten für kontinuierliche Bewegung prüfen
- **Kollisionserkennung** - `place_meeting` vor dem Bewegen verwenden
- **Pixel-genaue Kollision** - So nah wie möglich an Wände bewegen
- **Sammelobjekte** - Gegenstände erstellen, die den Score erhöhen und verschwinden
- **Timer-System** - Vergangene Zeit mit Variablen verfolgen
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

- [Tutorials](Tutorials_de) - Mehr Spiel-Tutorials
- [Anfänger-Preset](Beginner-Preset_de) - Übersicht der Anfänger-Funktionen
- [Tutorial: Pong](Tutorial-Pong_de) - Ein Zwei-Spieler-Spiel erstellen
- [Tutorial: Breakout](Tutorial-Breakout_de) - Ein Brick-Breaker-Spiel erstellen
- [Tutorial: Sokoban](Tutorial-Sokoban_de) - Ein Box-Pushing-Puzzle erstellen
- [Event-Referenz](Event-Reference_de) - Vollständige Event-Dokumentation
