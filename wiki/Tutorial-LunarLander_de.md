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
**Preset:** Anfänger-Preset

---

## Schritt 1: Das Spiel Verstehen

### Spielmechaniken
1. Der Lander wird von der Schwerkraft nach unten gezogen
2. HOCH drücken wendet Aufwärtsschub an (verbraucht Treibstoff)
3. LINKS/RECHTS steuert Rotation oder Bewegung
4. Lande sanft auf der Plattform um zu gewinnen
5. Absturz wenn du zu schnell landest oder die Plattform verfehlst
6. Kein Treibstoff mehr = kannst nicht abbremsen!

### Was Wir Brauchen

| Element | Zweck |
|---------|-------|
| **Lander** | Das Raumschiff das du steuerst |
| **Landeplattform** | Sichere Zone zum Landen |
| **Boden** | Gelände das Absturz verursacht |
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

### Create-Ereignis
```gml
gravity_force = 0.05;
thrust_force = 0.1;
max_speed = 5;
hsp = 0;
vsp = 0;
fuel = 100;
fuel_use = 0.5;
landed = false;
crashed = false;
safe_speed = 2;
```

### Step-Ereignis
```gml
if (landed || crashed) exit;

vsp += gravity_force;

if (keyboard_check(vk_up) && fuel > 0) {
    vsp -= thrust_force;
    fuel -= fuel_use;
    if (fuel < 0) fuel = 0;
}

if (keyboard_check(vk_left)) hsp -= 0.05;
if (keyboard_check(vk_right)) hsp += 0.05;

hsp = clamp(hsp, -max_speed, max_speed);
vsp = clamp(vsp, -max_speed, max_speed);

x += hsp;
y += vsp;

if (x < 16) { x = 16; hsp = 0; }
if (x > room_width - 16) { x = room_width - 16; hsp = 0; }
if (y < 16) { y = 16; vsp = 0; }
```

### Kollision mit obj_pad
```gml
var total_speed = sqrt(hsp*hsp + vsp*vsp);

if (total_speed <= safe_speed) {
    landed = true;
    hsp = 0;
    vsp = 0;
    show_message("Perfekte Landung! Du gewinnst!");
} else {
    crashed = true;
    show_message("Abgestürzt! Zu schnell!");
    room_restart();
}
```

### Kollision mit obj_ground
```gml
crashed = true;
show_message("In Gelände abgestürzt!");
room_restart();
```

---

## Schritt 6-7: Spielcontroller

**obj_game_controller** - Draw-Ereignis: Treibstoff, Geschwindigkeit, Anweisungen anzeigen

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

- **Schubphysik** - Der Schwerkraft entgegenwirken
- **Geschwindigkeitsmanagement** - Geschwindigkeit kontrollieren
- **Treibstoffsystem** - Ressourcenmanagement
- **Kollisionserkennung** - Unterschiedliche Ergebnisse

---

## Siehe Auch

- [Tutorials](Tutorials_de) - Mehr Tutorials
- [Tutorial: Platformer](Tutorial-Platformer_de) - Erstelle ein Plattformspiel

