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
**Preset:** Anfänger-Preset

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

---

## Schritt 3: Das Boden-Objekt erstellen

Der Boden ist eine feste Plattform, die den Spieler am Fallen hindert.

1. Klicken Sie mit der rechten Maustaste auf **Objekte** und wählen Sie **Objekt erstellen**
2. Nennen Sie es `obj_ground`
3. Setzen Sie das Sprite auf `spr_ground`
4. **Aktivieren Sie das Kontrollkästchen "Solid"**
5. Keine Events benötigt

---

## Schritt 4: Das Plattform-Objekt erstellen

Plattformen funktionieren wie der Boden, können aber in der Luft platziert werden.

1. Erstellen Sie ein neues Objekt namens `obj_platform`
2. Setzen Sie das Sprite auf `spr_platform`
3. **Aktivieren Sie das Kontrollkästchen "Solid"**

---

## Schritt 5: Das Spieler-Objekt erstellen

Der Spieler ist das komplexeste Objekt mit Schwerkraft, Springen und Bewegung.

1. Erstellen Sie ein neues Objekt namens `obj_player`
2. Setzen Sie das Sprite auf `spr_player`

### 5.1 Create Event - Variablen initialisieren

**Event: Create**
```gml
hspeed_max = 4;
vspeed_max = 10;
jump_force = -10;
gravity_force = 0.5;
hsp = 0;
vsp = 0;
on_ground = false;
```

### 5.2 Step Event - Bewegung und Physik

**Event: Step**
```gml
var move_input = keyboard_check(vk_right) - keyboard_check(vk_left);
hsp = move_input * hspeed_max;

vsp += gravity_force;
if (vsp > vspeed_max) vsp = vspeed_max;

on_ground = place_meeting(x, y + 1, obj_ground);

if (on_ground && (keyboard_check_pressed(vk_up) || keyboard_check_pressed(vk_space))) {
    vsp = jump_force;
}

if (place_meeting(x + hsp, y, obj_ground)) {
    while (!place_meeting(x + sign(hsp), y, obj_ground)) x += sign(hsp);
    hsp = 0;
}
x += hsp;

if (place_meeting(x, y + vsp, obj_ground)) {
    while (!place_meeting(x, y + sign(vsp), obj_ground)) y += sign(vsp);
    vsp = 0;
}
y += vsp;
```

---

## Schritt 6-8: Sammelobjekte und Gefahren

**obj_coin** - Kollision mit obj_player: Score +10, zerstöre Self

**obj_spike** - Kollision mit obj_player: Zeige Nachricht, Raum neu starten

**obj_flag** - Kollision mit obj_player: Zeige Nachricht, nächster Raum

---

## Schritt 9: Ihr Level entwerfen

1. Erstellen Sie `room_level1` (800x480)
2. Aktivieren Sie Raster-Snap (32x32)
3. Platzieren Sie Boden unten, Plattformen in der Luft
4. Fügen Sie Münzen, Stacheln hinzu
5. Setzen Sie Flagge ans Ende, Spieler an den Start

---

## Was Sie gelernt haben

- **Schwerkraftphysik** - Konstante Abwärtskraft
- **Sprungmechanik** - Negative Vertikalgeschwindigkeit
- **Bodenerkennung** - `place_meeting` verwenden
- **Kollisionsbehandlung** - Pixel für Pixel bewegen

---

## Siehe auch

- [Tutorials](Tutorials_de) - Mehr Spiel-Tutorials
- [Tutorial: Labyrinth](Tutorial-Maze_de) - Ein Labyrinth-Spiel erstellen
