# Views — Level 2

Eine **Split-Screen-Koop**-Demo: der 2400×800-Raum wird als zwei
nebeneinanderliegende Kameras in einem 800×600-Fenster gezeigt. Die
**linke Hälfte** (View 0) folgt **Spieler 1** (orange, Pfeiltasten);
die **rechte Hälfte** (View 1) folgt **Spieler 2** (petrol, WASD).
Jeder Spieler erkundet den gemeinsamen Raum in seiner eigenen Spur und
sammelt Münzen — man sieht beide gleichzeitig.

**Wo dies einzuordnen ist:** das zweite Level der vierten
Beispielfamilie. `views_1` führte eine einzelne scrollende Kamera ein;
`views_2` führt **mehrere gleichzeitige Viewports** ein — die andere
Kernfähigkeit von GameMaker-Views. Siehe
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
für die vollständige Progression. Die Bewegung verwendet das
Gitter-Idiom aus `maze_1`/`views_1` wieder.

**Sound & Musik:** keine — diesem Beispiel liegen keine Sounddateien bei.

## Wie man spielt

- **Spieler 1 (orange):** Pfeiltasten — bewegt sich in der **linken** Ansicht.
- **Spieler 2 (petrol):** `W` `A` `S` `D` — bewegt sich in der **rechten** Ansicht.
- Beide bewegen sich jeweils um eine Gitterzelle (32px); Wände
  (`obj_wall`) sind fest. Eine mittlere Trennwand mit Lücken trennt die
  beiden Spuren.
- **Ziel:** sammle die 18 Münzen (`obj_coin`) — jeder Spieler kann
  jede Münze aufnehmen; jede ist 10 Punkte wert (angezeigt in der
  Fenstertitelleiste).

## Warum die beiden Spieler unabhängig stoppen (eine echte Falle)

Gitterbewegung stoppt normalerweise beim `nokey`-Ereignis (löst aus,
wenn *keine* Taste gedrückt ist). Aber der Tastenzustand wird global
über alle Instanzen hinweg verfolgt, sodass bei zwei Spielern `nokey`
nur auslöst, wenn **beide** alles loslassen — Spieler 2 würde
weitergleiten, während Spieler 1 eine Taste hält. Also stoppt jeder
Spieler stattdessen über **`keyboard_release`** für **seine eigenen**
Tasten (Pfeile für S1, WASD für S2), was pro Taste und pro Objekt
auslöst. Das ist der Unterschied zu `views_1`s einzelnem Spieler, der
`nokey` sicher verwenden kann.

## Wie der Split-Screen eingerichtet ist

Ein unsichtbarer Controller, `obj_camera`, konfiguriert beide Views in
seinem **create**-Ereignis (registrierte `enable_views` + zwei
`set_view`-Aktionen), und dieselbe Konfiguration ist in den
`views`-Block des Raumes eingebacken, für Frame-0-Korrektheit beim Export:

- **View 0** — `view`/`port` `400×600`, `port_x` 0 (linke Hälfte),
  `follow` `obj_player1`.
- **View 1** — `view`/`port` `400×600`, `port_x` 400 (rechte Hälfte),
  `follow` `obj_player2`.

Beide Views sind **1:1** (View-Größe == Port-Größe) und teilen sich
**links/rechts** (`port_y` 0, volle Höhe). Das ist wichtig für
zielübergreifende Konsistenz: Desktop und HTML5 rendern jede View 1:1
(sie clippen + versetzen, sie skalieren eine View **nicht** auf ihren
Port), und eine Links/Rechts-Teilung vermeidet den Kivy- (y-up) gegen
Desktop/HTML5- (y-down) `port_y`-Flip. Eine herausgezoomte Minikarte
(View größer als ihr Port) wird hier bewusst **nicht** verwendet — sie
würde nur auf Kivy korrekt skalieren.

## Projektstruktur

| Datei | Zweck |
|---|---|
| `project.json` | Manifest — Fenster-/Raumeinstellungen, eingebettete Assets, und die Zwei-View-`views`-Konfiguration |
| `rooms/room0.json` | Der 2400×800-Raum (284 Instanzen: Kamera, Wände, 2 Spieler, 18 Münzen) + sein `views`-Block |
| `objects/obj_camera.json` | Unsichtbarer Controller: create-Ereignis `enable_views` + zwei `set_view` |
| `objects/obj_player1.json` | Spieler 1 (Pfeiltasten); Gitterbewegung + `keyboard_release`-Stopp |
| `objects/obj_player2.json` | Spieler 2 (WASD); Gitterbewegung + `keyboard_release`-Stopp |
| `objects/obj_coin.json` | Sammelobjekt — von jedem Spieler zerstörbar, fügt 10 hinzu |
| `objects/obj_wall.json` | Statische feste Wand |
| `sprites/` | `spr_player1.png` (orange), `spr_player2.png` (petrol), `spr_wall.png`, `spr_coin.png` + `.json`-Metadaten |
| `CREDITS.txt` | Lizenzhinweis für die Assets |

## Objekte

| Objekt | Rolle | Wichtige Ereignisse |
|---|---|---|
| `obj_camera` | Unsichtbarer Controller; aktiviert + konfiguriert beide Views | create (`enable_views`, 2× `set_view`) |
| `obj_player1` | Spieler der linken Ansicht (Pfeile) | keyboard (up/down/left/right/nokey), keyboard_release (pro Taste), collision_with_obj_wall |
| `obj_player2` | Spieler der rechten Ansicht (WASD) | keyboard (w/a/s/d/nokey), keyboard_release (pro Taste), collision_with_obj_wall |
| `obj_coin` | Sammelobjekt im Wert von 10 | collision_with_obj_player1, collision_with_obj_player2, destroy (`set_score` +10) |
| `obj_wall` | Statische feste Wand / Kameragrenze | (keine — passiver Kollisionskörper) |

## Assets

4 Sprites (`spr_player1`, `spr_player2`, `spr_wall`, `spr_coin`, je
32×32, ein Frame, pixelgenau), 0 Sounds. Alles einfarbige
CC0-Grafiken, für dieses Beispiel erstellt — siehe `CREDITS.txt`.

## Zum Experimentieren

- **Teilungsrichtung** — dieses Beispiel verwendet eine
  Links/Rechts-Teilung (`port_x` 0 und 400, `port_y` 0, volle Höhe).
  Eine Oben/Unten-Teilung würde die Hälften auf unterschiedliche
  `port_y`-Werte setzen; beachte, dass das auf Kivy (y-up) gegenüber
  Desktop/HTML5 (y-down) an einer anderen vertikalen Position rendert,
  weshalb Links/Rechts die portable Wahl ist.
- **View-Breite** — jede View ist `400` breit (die Hälfte des
  Fensters). Verbreitere das Fenster oder verschmälere die Views, um
  zu ändern, wie viel Raum jeder Spieler sieht.
- **Ränder** — `hborder` 120 / `vborder` 150 legen die Totzone jeder
  Kamera fest.

## Export-Status

- **Desktop (pygame):** die Referenz — `tests/test_views_2_sample.py`
  lädt das Beispiel, führt das create-Ereignis von `obj_camera` aus
  und stellt sicher, dass die zwei Kameras **unabhängig** scrollen
  (das Bewegen eines Spielers bewegt nicht die View des anderen) und
  sich am Raumrand begrenzen, sowie das Münzen-Scoring und den
  Pro-Spieler-`keyboard_release`-Stopp.
- **Web (HTML5):** `engine.js` rendert jede sichtbare View (Pro-View-
  Clip + 1:1-Verschiebung); die Zwei-View-Konfiguration wird im Export
  korrekt übertragen.
- **Mobil (Kivy/Android):** der Exporter rendert den Raum in ein Fbo
  und kopiert den sichtbaren Bereich jeder View in ihren
  Bildschirm-Port (`tests/test_kivy_views.py` deckt das
  Multi-View-Rendering ab). Die `enable_views`/`set_view`-Aktionen
  werden emittiert, sodass die Zwei-View-Einrichtung sowohl aus dem
  create-Ereignis von `obj_camera` als auch aus der eingebackenen
  Raumkonfiguration läuft. Verbleibende Einschränkung (wie bei
  `views_1`): das Renderziel wird bei der Raumerstellung gebaut, daher
  muss `views_enabled` in der Raumkonfiguration stehen (hier der
  Fall), damit die Kamera auf Kivy rendert.
- Die zielübergreifende Übereinstimmung der Scroll-Mathematik wird
  durch `tests/test_views_export_parity.py` fixiert.

Im Willkommens-Tab der IDE als "Views — Level 2" angezeigt
(`widgets/welcome_tab.py`).
