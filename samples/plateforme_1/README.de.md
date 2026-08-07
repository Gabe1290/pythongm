# Platform — Level 1

Ein minimaler seitwärts scrollender Plattformer, importiert aus
GameMaker 8.x (`samples/plateforme_1.gmk`). Der vom Spieler gesteuerte
Ball (`obj_balle`) erklimmt einen einzigen Bildschirm mit
Ziegelplattformen (`obj_brique`) mithilfe von `if_collision`-Sonden im
GameMaker-Stil, um sich in 4px/Frame-Schritten zu bewegen und nur unter
Schwerkraft zu fallen, wenn sich nichts Festes direkt darunter befindet
— ein handgeschriebenes AABB-Bewegungsschema statt der eingebauten
Physik der Engine.

**Wo dies einzuordnen ist:** Teil der `plateforme_*`-Familie, aber in
ihrer minimalsten Form — anders als `plateforme_2`/`plateforme_3` hat
dieses Level kein Hintergrundbild und **keinen gekachelten
Hintergrund** (das `tiles`-Array des Raumes ist leer); es ist nur aus
GameObjects + Sprites gebaut, genau wie `maze_1`. Siehe
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
für den Vergleich der gesamten Familie mit `maze_*` und `match3_*`.

**Sound & Musik:** keine — diesem Beispiel liegen keine Sounddateien bei.

## Wie man spielt

- **Pfeil links/rechts** — bewegt den Ball 4px pro Tastendruck,
  blockiert durch feste Ziegel.
- **Pfeil hoch** — Sprung (setzt `vspeed` auf -10), nur während der Ball
  auf einem festen Ziegel steht.
- Es gibt in diesem Level kein explizites Zielobjekt, keine Münze und
  keinen Ausgang — es ist ein vertikales Ziegellabyrinth zum Erklimmen.
  Es gibt auch kein Monster-/Gefahrenobjekt, daher gibt es keine
  Verlust-Bedingung; es ist freies Erkunden der Kollisions-/
  Schwerkraftmechanik.

## Projektstruktur

| Datei | Zweck |
|---|---|
| `project.json` | Projekt-Manifest — Fenster-/Raumeinstellungen, eingebettete Asset-Kopien (siehe Hinweis unten). |
| `rooms/niveau_01.json` | Der einzige Raum: 800×640, 120 Instanzen (meist `obj_brique`-Wände/Plattformen plus ein `obj_balle`). |
| `objects/obj_balle.json` | Logik des Spielerballs (Bewegung, Schwerkraft, Sprung). |
| `objects/obj_brique.json` | Statischer fester Ziegel, keine Ereignisse. |
| `sprites/` | `spr_balle.png` (Ball) und `spr_32x32_noir.png` (Ziegel), jeweils mit `.json`-Begleitdatei. |

`objects/*.json` und `rooms/niveau_01.json` sind die aktuellen
Pro-Asset-Nebendateien; ihr Inhalt stimmt mit dem in `project.json`
eingebetteten Inhalt für dieses Beispiel überein (keine Abweichung
gefunden), aber gemäß Repository-Konvention sind die Nebendateien die
maßgebliche Quelle, falls die beiden jemals voneinander abweichen.

## Objekte

| Objekt | Rolle | Wichtige Ereignisse |
|---|---|---|
| `obj_balle` | Vom Spieler gesteuerter Ball; Schwerkraft, kollisionsbewusste Bewegung, Sprung | create (nicht definiert), step, collision_with_obj_brique, keyboard (left, right, up) |
| `obj_brique` | Statische feste Plattform-/Wandkachel | *(keine — keine Ereignisse definiert)* |

## Assets

2 Sprites (`spr_balle`, `spr_32x32_noir`), 0 Sounds. Beide Sprites sind
abgeleitete Werke der Grafik des Spiels Pingus, lizenziert unter
GPL-3.0-or-later — siehe `CREDITS.txt` in diesem Ordner für den
vollständigen Hinweis und die Credits der ursprünglichen Künstler;
behandle sie nicht als von der MIT-Lizenz der IDE abgedeckt.

## Zum Experimentieren

- `obj_balle`-Step-Ereignis: Schwerkraft ist `0,45` px/Frame², und
  vspeed ist auf `24` begrenzt — erhöhe oder verringere eines von
  beiden, um das Fallgewicht und die Endgeschwindigkeit zu ändern.
- Der Sprungimpuls ist ein fester `vspeed = -10` (Tastatur "hoch") —
  höherer Betrag springt höher.
- Der horizontale Bewegungsschritt ist `4` px pro Tastendruck (Tastatur
  "links"/"rechts") — größere Schritte fühlen sich zackiger an, können
  aber durch dünne Lücken tunneln.
- Der Raum ist 800×640 bei `room_speed: 30`; das Ziegel-Layout in
  `rooms/niveau_01.json` kann frei umgestaltet werden, da `obj_brique`
  keine eigene Logik hat.

## Export-Status

Dieses Beispiel ist in der `SAMPLES`-Liste von
`tools/smoke_run_samples.py` aufgeführt, daher ist es durch den
Headless-Smoke-Test-Harness abgedeckt (führt die echte Spielschleife
für ~180 Frames mit simulierten Tastatureingaben aus). Es wurde nicht
separat gegen die Kivy- oder Web-Exportziele verifiziert. Im
Willkommens-Tab der IDE als **"Platform — Level 1"** angezeigt
(`widgets/welcome_tab.py`).
