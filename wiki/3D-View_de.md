# 3D-Ansicht (First-Person-Raycast-Rendering)

*[Startseite](Home_de) | [Vollständige Aktionsreferenz](Full-Action-Reference_de) | [Erweiterungen](Extensions_de)*

---

PyGameMaker kann einen Raum als **First-Person-3D-Ansicht im Doom/Wolfenstein-Stil**
darstellen statt als gewohnte Draufsicht — Wände als vertikale Streifen, ein
texturierter oder farbiger Boden und eine Decke, ein optionaler schwenkender
Himmel und Billboard-Sprites für Sammelobjekte und Monster. Die *Logik* des Spiels
(Bewegung, Kollisionen, Ereignisse) bleibt unverändert; es ändert sich nur, **wie**
der Raum **gezeichnet** wird.

Dies stellt die integrierte **2.5D-Raycast**-[Erweiterung](Extensions_de) bereit,
die standardmäßig aktiviert ist. Sie wird in alle drei Ziele exportiert —
Desktop, HTML5 und Kivy/Android — sodass ein First-Person-Spiel überall gleich
läuft.

Die mitgelieferten Beispiele **`raycast_1`–`raycast_4`** sind vollständige,
spielbare Beispiele (ein einfaches Labyrinth, ein zweistufiges Spiel mit
Sammelobjekten und einem Monster, eine Variante mit Gesundheit und Verbandskästen
sowie eine Vorführung einer Statusleiste im DOOM-Stil).

---

## Wie es funktioniert

- Ein Raum wird zur First-Person-Ansicht, wenn ein Objekt die Aktion
  **Raycast-Ansicht aktivieren** ausführt (meist in seinem Erstellen-Ereignis).
  Dieses Objekt ist standardmäßig die **Kamera** — seine Position ist der
  Blickpunkt und sein `facing_angle` (Blickwinkel) die Blickrichtung.
- **Wände sind Ihre soliden Instanzen.** Der Renderer leitet dünne Wand-*Kanten*
  aus jedem soliden Objekt im Raum ab, auf einem Gitter, dessen Größe der
  Aktionsparameter `cell_size` ist (Standard 32 — die Größe, die alle
  `maze_*`/`raycast_*`-Beispiele verwenden). Ein solides Objekt mit Wand-Sprite
  texturiert die Wand; andernfalls wird eine einfarbige `wall_color` verwendet.
- **Die Kamera dreht sich**, indem `facing_angle` geändert wird (siehe
  **Blickwinkel setzen**), und bewegt sich mit den üblichen Bewegungsaktionen
  (z. B. `set_direction_speed` mit `direction = "facing_angle"`, um geradeaus zu
  gehen).
- **Nicht-solide Instanzen mit Sprite** (Ziele, Sammelobjekte, Monster) werden
  als der Kamera zugewandte **Billboards** gezeichnet, korrekt durch Wände
  verdeckt.

---

## Die Aktionen (Kategorie **3D-Ansicht**)

| Aktion | Was sie tut |
|--------|-------------|
| **Raycast-Ansicht aktivieren** (`enable_raycast_view`) | Schaltet den aktuellen Raum in die First-Person-Ansicht (oder zurück) und konfiguriert die Kamera: `camera_object`, `fov`, `render_distance`, `cell_size`, Farben und Texturen von Wand/Boden/Decke, eine optionale `sky_texture` und `viewport_height` (ein DOOM-Leistenrahmen). |
| **Blickwinkel setzen** (`set_facing_angle`) | Dreht die Kamera. Winkel in GameMaker-Grad (0 = rechts, 90 = oben); `relative` addiert zum aktuellen Blickwinkel. |
| **Minikarte zeichnen** (`draw_minimap`) | Zeichnet eine nach Norden ausgerichtete Minikarte der Wände des Raums mit einer „Sie sind hier"-Markierung. Eine HUD-Aktion — in ein Zeichnen-Ereignis setzen. |
| **DOOM-HUD zeichnen** (`draw_doom_hud`) | Zeichnet eine untere Statusleiste im DOOM-Stil: Gesundheitsbalken + Zahl, ein auf die Gesundheit reagierendes Gesicht, Punktzahl, Leben und einen Zielzähler. Passt zu `viewport_height` von `enable_raycast_view`. |

Siehe die [Vollständige Aktionsreferenz](Full-Action-Reference_de#3d-view) für
alle Parameter.

---

## Eine minimale First-Person-Steuerung

Im Spielerobjekt:

- **Erstellen:** `Raycast-Ansicht aktivieren` (lassen Sie `camera_object` leer,
  damit der Spieler die Kamera *ist*).
- **Tastatur Links / Rechts:** `Blickwinkel setzen` mit aktiviertem `relative`
  (z. B. ±3°).
- **Tastatur Oben:** `Richtung und Geschwindigkeit setzen` mit
  `direction = facing_angle` und einer kleinen Geschwindigkeit, um vorwärtszugehen.

Bauen Sie den Raum aus soliden Wandobjekten auf einem 32-Pixel-Gitter, genau wie
die `maze_*`-Beispiele — der Raycaster verwandelt diese Wände in die 3D-Korridore.

---

## Hinweise und Grenzen

- Die HUD-Aktionen (`draw_minimap`, `draw_doom_hud` sowie die üblichen
  `draw_score` / `draw_lives` / `draw_text`) werden **über** das
  First-Person-Bild gelegt, in Bildschirmkoordinaten.
- Die Wände sind für den First-Person-Durchgang statisch — nach dem Laden des
  Raums erstellte/zerstörte Wände verändern die 3D-Geometrie nicht.
- Ist die 2.5D-Raycast-Erweiterung **deaktiviert**, wird ein Raum, der die
  Ansicht aktiviert, einfach als Draufsicht dargestellt, und die IDE warnt Sie
  beim Laden — siehe [Erweiterungen](Extensions_de).

---

## Siehe auch

- [Erweiterungen](Extensions_de) — wie die 3D-Ansicht ausgeliefert wird und wie man sie abschaltet
- [Vollständige Aktionsreferenz](Full-Action-Reference_de#3d-view) — die vier Aktionen im Detail
- [Raum-Editor](Raum_Editor_de) — das Platzieren der Wandobjekte, aus denen die Ansicht aufgebaut wird
