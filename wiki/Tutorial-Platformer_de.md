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

### 5.1 Schwerkraft

**Event: Create** — Add Action: **Move** → **Set Gravity**
(Direction: `270`, Gravity: `0.5`) — 270° bedeutet senkrecht nach unten;
der Wert wird bei jedem Frame zur Vertikalgeschwindigkeit des Spielers
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

- **Schwerkraftphysik** - Set Gravity wendet bei jedem Frame eine konstante Abwärtskraft an
- **Sprungmechanik** - Ein Key-Press-Event (nicht held) gibt einen einzelnen Geschwindigkeitsimpuls nach oben
- **Eingebaute solide Kollision** - Der Boden blockiert den Spieler automatisch, sobald er als Solid markiert ist, ohne manuellen Positionsprüfungs-Code

---

## Siehe auch

- [Tutorials](Tutorials_de) - Mehr Spiel-Tutorials
- [Tutorial: Labyrinth](Tutorial-Maze_de) - Ein Labyrinth-Spiel erstellen
