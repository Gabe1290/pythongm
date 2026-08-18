# Labyrinth — Level 2

Ein Labyrinth-Spiel aus der Vogelperspektive auf einem Gitter mit zwei
spielbaren Labyrinthen und einem Titelbildschirm: sammle Bonbons für
Punkte, dann erreiche den Ausgang, um weiterzukommen. Es baut auf
`maze_1`s Ein-Raum-Labyrinth-/Ziel-Schleife auf, mit einem
Startbildschirm, einem Sammelobjekt (Bonbon mit Punkten) und einer
verschlossenen Tür, die sich erst öffnet, sobald alle Bonbons des
Raumes eingesammelt sind. Dies ist ein natives pygm2-Projekt (keine
begleitende `.gmk`-Datei — seine Assets stammten ursprünglich aus einem
GameMaker-8.x-Import, siehe `CREDITS.txt`, aber das Projekt selbst ist
im eigenen JSON-Format von pygm2 geschrieben/gespeichert).

**Wo dies einzuordnen ist:** Teil der `maze_*`-Familie — GameObjects +
Sprites, plus (anders als `maze_1`) ein statisches **Hintergrundbild**
pro Raum (`background_main`), keine Kacheln auf Raumebene. Siehe
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
für den Vergleich mit `plateforme_*` (fügt gekachelte Hintergründe
hinzu) und `match3_*` (reines Skript, keine eingebauten Aktionen).

**Sound & Musik:** 4 Sounddateien liegen bei (`sound_background.ogg`,
`sound_diamond`/`door`/`goal.wav`), aber **keine davon ist tatsächlich
verdrahtet** — kein Objekt ruft irgendwo `play_sound`/`play_music`
auf, sodass das Spiel in der Praxis stumm ist, obwohl es Audio-Assets
mitführt. (Im Gegensatz zu `maze_3`, wo derselbe Soundsatz tatsächlich
abgespielt wird.)

## Wie man spielt

- **Titelbildschirm (`room_start`):** drücke **LEERTASTE**, um zu
  starten (die `keyboard_press`-Aktion von `controller_start` ruft
  `next_room` auf).
- **Pfeiltasten** (hoch/runter/links/rechts) bewegen den Spieler
  jeweils um eine Gitterzelle (32px); die Bewegung ist über
  `test_alignment`/`snap_to_grid` gitterausgerichtet (32×32-Gitter),
  dasselbe Muster wie `maze_1`.
- **Ziel:** sammle die im ganzen Labyrinth verstreuten Bonbons
  (`obj_diamond`, Sprite `sprite_bonbon`) — jedes ist +10 Punkte wert —
  und erreiche dann das Ziel (`obj_goal`). In `room2` ist der Ausgang
  zusätzlich durch eine verschlossene Tür (`obj_door`) blockiert, die
  sich erst selbst zerstört, sobald jeder `obj_diamond` im Raum weg ist.
- Das Berühren des Ziels führt zum nächsten Raum (+100 Punkte), falls
  einer existiert; das Berühren im letzten Raum (`room2`) vergibt +100,
  öffnet den Highscore-Eingabebildschirm und beendet das Spiel.
- **Keine Verlust-Bedingung:** keine leben-/gesundheitsbeeinflussende
  Aktion erscheint irgendwo in den Objekten dieses Beispiels —
  `starting_lives: 3` ist in den Projekteinstellungen gesetzt, wird
  aber nie angezeigt oder verringert.

## Projektstruktur

| Datei | Zweck |
|---|---|
| `project.json` | Projekt-Manifest — Fenster-/Raumeinstellungen und eingebettete Kopien aller Assets |
| `rooms/room_start.json` | Titelbildschirm — 1 Instanz (`controller_start`) |
| `rooms/room1.json` | Erstes Labyrinth — 134 Instanzen (Wände, Spieler, Ziel, 4 Bonbons, `controller_main`) |
| `rooms/room2.json` | Zweites Labyrinth — 112 Instanzen (Wände, Spieler, Ziel, 21 Bonbons, verschlossene Tür, `controller_main`) |
| `objects/*.json` | 9 Objektdefinitionen — gegen die eingebetteten Kopien in `project.json` geprüft und in diesem Beispiel identisch (keine Veralterung gefunden) |
| `sprites/` | 7 Sprites (`sprite_person`, `sprite_bonbon`, `sprite_door`, `sprite_goal`, `sprite_wall_corner`, `sprite_wall_horizontal`, `sprite_wall_vertical`) + Metadaten; `tiles.json` ist eine verwaiste Nebendatei (nicht in `project.json` registriert, Bilddatei fehlt — ungenutzt) |
| `backgrounds/` | `background_start.png` (Titelbildschirm), `background_tiles.png` (gekachelter Labyrinthboden) |
| `sounds/` | 4 Sounddateien (siehe Assets unten) |
| `CREDITS.txt` | Lizenzhinweis für die Assets dieses Beispiels |

## Objekte

| Objekt | Rolle | Wichtige Ereignisse |
|---|---|---|
| `obj_person` | Vom Spieler gesteuerte Figur; gitterbasierte Bewegung | keyboard (down, right, up, left, nokey), collision_with_wall_corner |
| `wall_corner` | Grundlegende feste Labyrinthwand; Elternobjekt für die beiden anderen Wandtypen | (keine — nur passiver Kollisionskörper) |
| `wall_horizontal` | Festes horizontales Wandsegment (erbt von `wall_corner`) | (keine — nur passiver Kollisionskörper) |
| `wall_vertical` | Festes vertikales Wandsegment (erbt von `wall_corner`) | (keine — nur passiver Kollisionskörper) |
| `obj_diamond` | Sammelbonbon; fügt beim Aufheben Punkte hinzu | destroy, collision_with_obj_person |
| `obj_door` | Verschlossenes Ausgangstor (nur room2); öffnet sich, sobald alle Bonbons weg sind | step |
| `obj_goal` | Levelausgang; führt zum nächsten Raum oder beendet das Spiel | collision_with_obj_person |
| `controller_start` | Titelbildschirm-Controller; wartet darauf, dass der Spieler beginnt | create, keyboard_press (LEERTASTE) |
| `controller_main` | HUD-Controller im Labyrinth; zeichnet die Punktzahl | draw |

## Assets

7 Sprites (32×32, ein Frame, pixelgenaue Kollision außer bei
`sprite_goal`, das kein explizites `precise`-Flag hat), 2 Hintergründe,
4 Sounds (`sound_background.ogg`, `sound_diamond.wav`,
`sound_door.wav`, `sound_goal.wav`). Lizenz/Herkunft für alle Assets
dieses Beispiels ist **nicht dokumentiert** — siehe `CREDITS.txt` in
diesem Ordner, das auf das "Remaining maze assets"-TODO in
`docs/ASSET_LICENSES.md` verweist. Nimm für diese Dateien keine CC0-
oder andere Lizenz an.

## Zum Experimentieren

- Die Spieler-Bewegungsgeschwindigkeit ist `4` (Gitterzellen/Schritt),
  während der Wand-Stopp die Geschwindigkeit `8` verwendet — beide sind
  fest codierte Parameter der Tastendruck-Aktionen in `obj_person`,
  genau wie in `maze_1`.
- Alle 4 mitgelieferten Sounddateien sind unreferenziert — kein Objekt
  ruft derzeit `play_sound` auf; eine davon für Bonbon-Aufnahme/
  Türöffnung/Zielerreichen zu verdrahten wäre ein naheliegender
  nächster Schritt.
- Die Räume sind `480×480`–`480×512` bei `room_speed: 30` — kleine
  Ein-Bildschirm-Labyrinthe ohne Scrollen.
- `sprites/tiles.json` ist eine übrig gebliebene Nebendatei, die nicht
  als Projekt-Asset registriert ist (ihre `sprites/tiles.png` existiert
  nicht) — kann gefahrlos entfernt oder ignoriert werden.

## Export-Status

Abgedeckt durch die Headless-Smoke-Test-Suite
(`tools/smoke_run_samples.py`, die `maze_2` auflistet und es für ~180
Frames mit simulierten Tastatureingaben laufen lässt); nicht einzeln
pro Export-Ziel (Kivy/Web) erneut verifiziert. Im Willkommens-Tab der
IDE als "Maze — Level 2" angezeigt (`widgets/welcome_tab.py`).
