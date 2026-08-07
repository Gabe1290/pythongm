# Labyrinth — Level 1

Ein Labyrinth-Spiel aus der Vogelperspektive auf einem Gitter: führe
das Spieler-Sprite durch ein von Wänden gesäumtes Labyrinth zur
Zielkachel, die zum nächsten Raum weiterführt. Dies ist ein natives
pygm2-Projekt (keine begleitende `.gmk`-Datei — seine Assets stammten
ursprünglich aus einem GameMaker-8.x-Import, siehe CREDITS.txt, aber
das Projekt selbst ist im eigenen JSON-Format von pygm2
geschrieben/gespeichert).

**Wo dies einzuordnen ist:** `maze_*` ist die erste von drei
Beispielfamilien in einer groben Progression der Erstellungstechniken
(eingebaute Objekte/Sprites → `plateforme_*`s hinzugefügte gekachelte
Hintergründe → `match3_*`s reine `execute_code`-Skriptspiele) — siehe
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
für das Gesamtbild. Dieses Beispiel verwendet nur GameObjects +
Sprites, kein Hintergrundbild und keine Kacheln auf Raumebene.

**Sound & Musik:** keine — diesem Beispiel liegen keine Sounddateien bei.

## Wie man spielt

- **Pfeiltasten** (hoch/runter/links/rechts) bewegen den Spieler jeweils
  um eine Gitterzelle (32px); die Bewegung ist über `test_alignment`/
  `snap_to_grid` gitterausgerichtet (32×32-Gitter).
- Wände (`obj_wall`) sind fest — hineinlaufen stoppt den Spieler und
  richtet ihn wieder am Gitter aus.
- **Ziel:** die Zielkachel (`obj_goal`) erreichen. Sie zu berühren
  führt zum nächsten Raum, falls einer existiert, oder startet das
  Spiel neu, falls keiner existiert.
- **Debug-Kürzel:** `N` auf dem Ziel drücken springt zum nächsten Raum
  (falls vorhanden); `P` drücken springt zum vorherigen Raum (falls
  vorhanden) — dieselbe Weiterschalt-/Neustart-Logik wie das Berühren
  des Ziels.
- In diesem Beispiel wird keine Verfolgung von Leben/Punkten/Gesundheit
  verwendet (Gesundheit wird bei Raumwechsel über `set_health`
  zurückgesetzt, aber nie angezeigt).

## Projektstruktur

| Datei | Zweck |
|---|---|
| `project.json` | Projekt-Manifest — Fenster-/Raumeinstellungen und eingebettete Kopien aller Assets |
| `rooms/room0.json` | Labyrinth-Layout für Raum 0 (131 Instanzen: Wände, Spielerstart, Ziel) |
| `rooms/room1.json` | Labyrinth-Layout für Raum 1 (130 Instanzen) |
| `objects/obj_person.json` | Spielerobjekt-Definition (maßgebliche Quelle; identisch mit der eingebetteten Kopie in `project.json`) |
| `objects/obj_goal.json` | Zielobjekt-Definition |
| `objects/obj_wall.json` | Wandobjekt-Definition |
| `sprites/` | `spr_person.png`, `spr_wall.png`, `spr_goal.png` + ihre `.json`-Metadaten |
| `CREDITS.txt` | Lizenzhinweis für die Assets dieses Beispiels |

Die `objects/*.json`-Nebendateien wurden gegen die eingebetteten Kopien
in `project.json` geprüft und sind in diesem Beispiel identisch — keine
Veralterung gefunden.

## Objekte

| Objekt | Rolle | Wichtige Ereignisse |
|---|---|---|
| `obj_person` | Vom Spieler gesteuerte Figur; gitterbasierte Bewegung | implizite Erstellung über die Tastatur, keyboard (down, right, up, left, nokey), collision_with_obj_wall |
| `obj_goal` | Levelausgang; schaltet weiter/startet neu bei Berührung oder Debug-Taste | collision_with_obj_person, keyboard_press (p, n) |
| `obj_wall` | Statische feste Labyrinthwand, blockiert Bewegung | (keine — nur passiver Kollisionskörper) |

## Assets

3 Sprites (`spr_person`, `spr_wall`, `spr_goal`, je 32×32, ein Frame,
pixelgenaue Kollision), 0 Sounds. Lizenzierung: `spr_person.png` und
`spr_wall.png` sind CC0 (gemeinfrei), Werke des pygm2-Autors; die
Herkunft von `spr_goal.png` ist noch nicht dokumentiert — siehe
`CREDITS.txt` in diesem Ordner und `docs/ASSET_LICENSES.md` im
Repository-Wurzelverzeichnis für das vollständige Bild.

## Zum Experimentieren

- Die Spieler-Bewegungsgeschwindigkeit ist `4` (Gitterzellen/Schritt),
  während der Wand-Stopp die Geschwindigkeit `8` verwendet — beide sind
  fest codierte Parameter der Tastendruck-Aktionen in `obj_person`.
- Die Gittergröße ist `32` (passend zu den 32×32-Sprites); eine
  Änderung erfordert passende Anpassungen an den
  `snap_to_grid`/`test_alignment`-Aufrufen und den Raum-Layouts.
- Die Räume sind `480×480` bei `room_speed: 30` — kleine
  Ein-Bildschirm-Labyrinthe ohne Scrollen.
- Die `N`/`P`-Debug-Tasten auf `obj_goal` erlauben es, zwischen
  room0/room1 zu springen, ohne das Ziel zu berühren — praktisch zum
  Testen, aber leicht versehentlich beim Spielen auszulösen.

## Export-Status

Abgedeckt durch die Headless-Smoke-Test-Suite
(`tools/smoke_run_samples.py`, die `maze_1` auflistet und es für ~180
Frames mit simulierten Tastatureingaben laufen lässt); nicht einzeln
pro Export-Ziel (Kivy/Web) erneut verifiziert. Im Willkommens-Tab der
IDE als "Maze — Level 1" angezeigt (`widgets/welcome_tab.py`).
