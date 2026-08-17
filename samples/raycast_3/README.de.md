# 2.5 D — Level 3

Das dritte Ich-Perspektive-Level im Doom-/Wolfenstein-Stil, gebaut auf
derselben **Raycast-2,5D-Engine** wie [`raycast_1`](../raycast_1/README.md)
und [`raycast_2`](../raycast_2/README.md) — vollständig auf allen drei
Exportzielen (Desktop, HTML5, nativ/Kivy): texturierte Wände, ein
verschiebbarer Himmel, texturiertes Boden-Raycasting in niedriger
Auflösung, und kamerazugewandte Billboard-Sprites.

Wo `raycast_1` *die Ich-Perspektive-Ansicht selbst* lehrt und
`raycast_2` *Geschehen in der Ansicht* hinzufügt (Edelsteine, ein
patrouillierender Gegner, ein gesperrter Ausgang), geht es bei
`raycast_3` um **Zustand, den man während des Spielens sehen kann**:
Monster kosten **Gesundheit** statt direkt ein Leben, Verbandskästen
geben sie zurück, und ein über die 3D-Ansicht gelegtes **Head-up-
Display** zeigt jederzeit Punkte, Leben und eine Gesundheitsleiste.

Dieses HUD ist der Grund, warum dieses Beispiel existiert. Bis zum
20.07.2026 zeichnete die Engine die Ich-Perspektive-Ansicht und hörte
dann auf, sodass Punkte und Leben eines Raycast-Spiels nur in der
Desktop-Fenstertitelleiste erschienen — unsichtbar bei den HTML5- und
Kivy-Exporten. Siehe [`docs/RAYCAST_HUD_PLAN.md`](../../docs/RAYCAST_HUD_PLAN.md)
für diese Arbeit und [`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md)
für die Engine.

Ein vollständiges Zwei-Level-Spiel: durchquere jedes Labyrinth in der
Ich-Perspektive, sammle jeden Edelstein, während du die Monster
überlebst, und erreiche den edelsteingesperrten Ausgang — der erste
(warme Ziegel-)Raum führt zu einem zweiten (kühlen Kristallhöhlen-)
Raum, und diesen abzuschließen gewinnt das Spiel. Verfügbar über den
Willkommens-Tab der IDE (*"2.5 D — Level 3"*).

**Sound & Musik:** keine — diesem Beispiel liegen keine Sounddateien bei.

## Wie man spielt

- **Hoch/Runter** — bewegen vorwärts/rückwärts in die Richtung, in die
  man gerade blickt (kontinuierlich, nicht gitterausgerichtet; Wände
  blockieren).
- **Links/Rechts** — drehen auf der Stelle (dreht `facing_angle`,
  unabhängig von der Bewegung — man kann sich im Stehen drehen).
- **Sammle die Edelsteine** — jeder fügt 10 zum Punktestand hinzu,
  oben links angezeigt.
- **Weiche den Monstern aus** — eines zu berühren kostet **25
  Gesundheit**, nicht ein Leben. Nach einem Treffer bekommst du ein
  kurzes Fenster der Unverwundbarkeit (45 Schritte), sodass ein
  Monster, das durch dich hindurchläuft, nicht die gesamte Leiste auf
  einmal leert.
- **Schnapp dir die Verbandskästen** — die Boxen mit rotem Kreuz
  stellen **40 Gesundheit** wieder her, bei voller Leiste gedeckelt.
- **Geht die Gesundheit aus**, verlierst du ein Leben, die Leiste
  füllt sich wieder auf und der Raum startet neu. Gehen die **Leben**
  aus, startet das Spiel neu.
- **Ziel** — sammle *alle* Edelsteine in einem Raum, dann erreiche
  seinen Ausgang. Ihn vorzeitig zu erreichen fordert nur dazu auf, den
  Rest zu sammeln.

## Das HUD

`obj_hud` zeichnet es, im **Bildschirmraum**, über das fertige
3D-Bild:

| Element | Ecke | Aktion |
|---|---|---|
| Punkte | oben links | `draw_score` |
| Leben | oben rechts | `draw_text` + `draw_lives` |
| Gesundheitsleiste | unten links | `draw_health_bar` |
| Minikarte | Zentrum, **auf Anfrage** | `draw_minimap` |

Punkte und Gesundheit sitzen absichtlich in **gegenüberliegenden**
Ecken: eine Gesundheitsleiste ist breit und eine Punktestand-Zeichenkette
wächst beim Spielen, sodass ein Stapeln eine Kollision provoziert.

### Die Minikarte

**Drücke `M`, um sie ein-/auszublenden** — auf Android tippe den
Kartenknopf oben links. Sie ist standardmäßig *aus* und wird nur
gezeichnet, während sie umgeschaltet ist, aus zwei Gründen: eine volle
Karte sind ~250 Zeilenbefehle pro Frame, und einen Teil einer
Ich-Perspektive-Ansicht dauerhaft zu bedecken ist genau die Unordnung,
die ein HUD vermeiden sollte. Während sie aus ist, kostet sie
überhaupt nichts.

`draw_minimap` zeichnet eine **nordausgerichtete** Karte der Wände des
Raumes mit einem Marker, der zeigt, wo man sich befindet und wohin man
blickt. Sie dreht sich nicht — die Karte bleibt fest und der Marker
dreht sich, was leichter zu lesen ist als eine sich drehende Karte.

Sie benötigt keine eigenen Daten: sie liest dieselben Wandkanten, die
die Ich-Perspektive-Ansicht bereits aus den soliden Instanzen des
Raumes abgeleitet hat, sodass sie korrekt bleibt, wenn man das
Labyrinth neu gestaltet. Sie zeigt **nur Wände** — keine Edelsteine
oder Monster — sodass das Labyrinth weiterhin erkundenswert bleibt.

**Nicht implementiert (bewusst):** Kriegsnebel, ein rotierender/
blickrichtungsorientierter Modus, und das Anzeigen von Gegenständen
oder Gegnern. Siehe [`docs/RAYCAST_MINIMAP_PLAN.md`](../../docs/RAYCAST_MINIMAP_PLAN.md)
dafür, warum jedes davon weggelassen wurde.

**`obj_hud` ist `visible: true`, und das ist wichtig.** GameMaker
führt das `draw`-Ereignis einer unsichtbaren Instanz nicht aus — daher
kann das HUD nicht einfach auf dem unsichtbaren Kamera-Controller
(`obj_cam0`/`obj_cam1`) liegen. Falls du dein eigenes HUD baust und
nichts erscheint, prüfe zuerst dieses Flag.

## Projektstruktur

| Datei | Zweck |
|---|---|
| `project.json` | Manifest — 640×480-Fenster, beide Räume, eingebettete Asset-Kopien |
| `rooms/room0.json` | Warmes-Ziegel-Labyrinth: 15×15 Zellen / 480×480, 8 Edelsteine, 3 Monster, 3 Verbandskästen |
| `rooms/room1.json` | Kristallhöhlen-Labyrinth: die schwerere Hälfte — 10 Edelsteine, 5 Monster, nur 2 Verbandskästen |
| `objects/obj_person.json` | Spieler/Kamera — Bewegung, Gesundheitsschaden + Unverwundbarkeits-Alarm, Todesbehandlung |
| `objects/obj_hud.json` | Das Head-up-Display (siehe oben) |
| `objects/obj_cam0.json`, `obj_cam1.json` | Pro-Raum-Kamera-Controller, jeder mit dem Texturthema dieses Raumes |
| `objects/obj_gem.json` | Sammelobjekt, +10 Punkte |
| `objects/obj_medkit.json` | Stellt 40 Gesundheit wieder her |
| `objects/obj_monster.json` | Patrouillierender Billboard-Gegner |
| `objects/obj_goal.json`, `obj_goal_final.json` | Edelsteingesperrte Ausgänge: Weiterkommen und Sieg |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Dünne Wandsegmente (32×8 und 8×32) |
| `sprites/` | 13 Sprites, wiederverwendet aus `raycast_2` plus `spr_medkit` |

## Das Labyrinth ist erzeugt, nicht von Hand platziert

`tools/gen_raycast_3_maze.py` baut beide Räume mit einem rekursiven
Backtracker-Labyrinth, das durch `raycast_1`s Dünnkantenwand-Platzierung
läuft — 8px-Trennwände, zentriert auf Zellgrenzen, nicht 32px-Blöcke,
die eine Zelle füllen. Erneutes Ausführen reproduziert die
ausgelieferten Räume exakt, und ein Test stellt sicher, dass sie nicht
abgedriftet sind, sodass das Level-Design überprüfbar und anpassbar
bleibt statt undurchsichtige Daten zu sein. (`raycast_2`s Labyrinth
stammte aus einem Wegwerf-Skript, das nie eingecheckt wurde, daher
können seine Räume nicht regeneriert werden — dieses hier behebt das.)

Die Seeds sind **gewählt, nicht willkürlich**: `check_start()` stellt
sicher, dass die Startzelle sich nach Osten öffnet (der Spieler spawnt
dort mit Blick nach Osten, sodass ein ummauerter Start bedeuten würde,
das Spiel mit der Nase an einer Wand zu beginnen) und dass jede Zelle
erreichbar ist.

## Zum Experimentieren

- **Schaden und Heilung:** `-25` im `collision_with_obj_monster`-
  Ereignis von `obj_person`, `+40` im `destroy`-Ereignis von
  `obj_medkit`.
- **Unverwundbarkeitsfenster:** die `45` Schritte auf `alarm_0`.
  Kürzer macht das Spiel härter; entferne es, und ein Monster, das dich
  wiederholt überlappt, wird die Leiste zerfetzen.
- **Schwierigkeitsbalance:** die Pro-Raum-`counts` im Generator —
  Monster gegen Verbandskästen ist der Hauptregler.
- **HUD-Layout:** die Koordinaten im `draw`-Ereignis von `obj_hud`.
  Halte Punkte und Gesundheit in gegenüberliegenden Ecken.
- **Minikarte:** `size` bei `draw_minimap` skaliert den ganzen Raum in
  dieses Quadrat, sodass ein größerer Wert einfach eine lesbarere
  Karte bedeutet; `wall_color` und `player_color` legen ihr Aussehen
  fest. Der Umschalter liegt im `keyboard_press` → `m`-Ereignis von
  `obj_hud`; er verwendet `test_variable` + `exit_event` statt zweier
  bloßer Bedingungen, weil die naive Version das Flag auf 1 setzt und
  dann sofort 1 liest und es direkt wieder auf 0 zurücksetzt.
- **Themen:** die Texturparameter auf `obj_cam0`/`obj_cam1`.

## Eine Anmerkung zum Kollisions-Timing

Die Laufzeitumgebung löst ein Kollisionsereignis aus, wenn zwei
Instanzen **beginnen** zu überlappen, nicht jeden Frame, in dem sie
weiterhin überlappen. In einem Monster zu stehen kostet daher einen
Treffer, nicht einen Treffer pro Frame. Der Unverwundbarkeits-Alarm
verdient sich trotzdem seinen Platz: er deckt das wiederholte
Berühren/Loslassen eines Monsters ab, das *durch* dich hindurch
patrouilliert, was der Fall ist, dem man beim Spielen tatsächlich begegnet.

## Export-Status

Läuft auf allen drei Zielen. Abgedeckt durch die Headless-Smoke-Suite
(`tools/smoke_run_samples.py`) und durch `tests/test_raycast_3_sample.py`,
die die echte Spielschleife durchspielt: Schaden, das Öffnen und
Schließen des Unverwundbarkeitsfensters, dass der Tod exakt ein Leben
kostet, die Verbandskasten-Heilung und ihre Deckelung, den
edelsteingesperrten Ausgang, den Raumübergang in das Eis-Thema, und
das Rendern des HUD über die Ich-Perspektive-Ansicht in **beiden**
Räumen.

Es wurde verifiziert, dass die Kivy- und HTML5-Exporte die gesamte
Schleife tragen — `no_more_health`, `alarm_0`, `draw_health_bar`,
`obj_hud` und `spr_medkit` überleben alle die Codegenerierung — aber
der *visuelle* Playtest pro Ziel lohnt sich vor einem Release, mit
eigenen Augen betrachtet zu werden.
