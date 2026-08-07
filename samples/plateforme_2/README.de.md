# Platform — Level 2

Ein seitwärts scrollender Plattformer, importiert aus GameMaker 8.x
(`samples/plateforme_2.gmk`). Im Vergleich zu einem minimalen ersten
Level erweitert dieses die Objektliste von einem einzelnen Spieler +
einem Block auf vier Objekte (eine Basisplattform plus horizontale und
vertikale Größenvarianten, die davon erben), angeordnet in einem
126-Instanzen-Raum, der aus einem schneethematischen Autotile-Kachelsatz
gebaut ist, statt aus ein paar von Hand platzierten Blöcken.

**Wo dies einzuordnen ist:** Teil der `plateforme_*`-Familie, und —
anders als das minimale `plateforme_1` — hier taucht der **gekachelte
Hintergrund** auf: 127 einzeln platzierte Hintergrundkachel-Stücke (das
`tiles`-Array des Raumes) plus ein Verlaufs-Hintergrundbild
(`fond_degrade`), geschichtet unter den festen Ziegel-*Objekten*, die
weiterhin die Kollision übernehmen. Dies ist der Schritt, den
`plateforme_*` über `maze_*` hinaus hinzufügt; siehe
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
für die vollständige Progression.

**Sound & Musik:** keine — diesem Beispiel liegen keine Sounddateien bei.

## Wie man spielt

- **Pfeil links/rechts** — bewegt den Pinguin (`obj_personnage`) links/rechts.
- **Pfeil hoch** — Sprung, aber nur während der Spieler auf einer
  festen Plattform steht (geprüft durch einen Kollisionstest ein Pixel
  unterhalb des Spielers).
- **Ziel** — es gibt in diesem Beispiel kein Ziel-/Flaggenobjekt; es
  ist ein Plattform-Layout zum Erkunden/Durchqueren über die
  `obj_brique*`-Plattformen.
- **Verlust-Bedingung** — keine ist definiert (keine Gefahren, keine
  tödlichen Objekte, keine Fall-Tod-Prüfung); die unterste Ziegelreihe
  des Raumes fungiert als Boden.

## Projektstruktur

| Datei | Zweck |
| --- | --- |
| `project.json` | Projekt-Manifest — Fenster-/Raumeinstellungen, eingebettete Asset-Kopien. |
| `rooms/niveau_01.json` | Der eine Raum: 800×640, 126 Instanzen + 127 Hintergrundkacheln. Maßgebliche Quelle für den Rauminhalt (`project.json`s eingebettete `instances`-Liste ist leer). |
| `objects/*.json` | Pro-Objekt-Nebendateien für die 4 Objekte; identisch mit den eingebetteten Kopien in `project.json` zum Zeitpunkt dieser Erstellung. |
| `sprites/` | 5 Sprite-Assets (Spieler-Lauf-Streifen + feste Plattformblöcke). |
| `backgrounds/` | Schnee-Kachelsatz (`tuiles_neige.png`, als Autotile-Quelle verwendet) und ein kleiner vertikaler Verlauf (`fond_degrade.png`), gestreckt als Raumhintergrund. |
| `CREDITS.txt` | Lizenzhinweis für die Sprite-/Hintergrundgrafik (siehe Assets unten). |

## Objekte

| Objekt | Rolle | Wichtige Ereignisse |
| --- | --- | --- |
| `obj_personnage` | Spieler (Pinguin) — Bewegung, Sprung, Schwerkraft, Bodenerkennung | create, step, collision_with_obj_brique, keyboard (left, right, up), keyboard_release (LEFT, RIGHT) |
| `obj_brique` | Basis-feste Plattform-Block (32×32) | keine (keine Ereignisse; nur Solid-Flag) |
| `obj_brique_h` | Breite feste Plattform-Variante (32×16), Kind von `obj_brique` | keine |
| `obj_brique_v` | Schmale feste Plattform-Variante (8×16), Kind von `obj_brique`; definiert, aber nicht in `niveau_01` platziert | keine |

## Assets

5 Sprites (`spr_pingus_dr`/`spr_pingus_ga` 8-Frame-Lauf-Streifen, plus
drei einfarbige Platzhalter-Blöcke bei 32×32 / 32×16 / 8×16) und 2
Hintergründe; keine Sounds. Die Sprite- und Hintergrundgrafik ist vom
Pingus-Projekt (GPL-3.0-or-later) adaptiert — siehe `CREDITS.txt` für
die vollständige Zuschreibung und Lizenzbedingungen; diese README
wiederholt oder erweitert diese Angaben nicht.

## Zum Experimentieren

- Die horizontale Spielergeschwindigkeit ist ein fester `hspeed = 4` in
  den Tastatur-Ereignissen.
- Der Sprungimpuls ist `vspeed = -10`; die Fallschwerkraft ist `0,45`
  (nur in der Luft angewendet), mit einer Endgeschwindigkeitsbegrenzung
  bei `vspeed = 24`.
- Die Raumgröße ist 800×640 bei `room_speed = 30`.

## Export-Status

Dieses Beispiel ist in der `SAMPLES`-Liste von
`tools/smoke_run_samples.py` aufgeführt, sodass es bei jedem Lauf
dieses Harness einen Headless-Smoke-Durchlauf erhält (die echte
Spielschleife läuft für ~180 Frames mit simulierten
Tastatureingaben). Es wurde keine spezifische Verifikation pro
Export-Ziel (Kivy/HTML5) für dieses Beispiel durchgeführt. Im
Willkommens-Tab der IDE als "Platform — Level 2" angezeigt
(`widgets/welcome_tab.py`).
