# Raycast — Level 2

Ein zweites Ich-Perspektive-Level im Doom-/Wolfenstein-Stil, gebaut auf
derselben **Raycast-2,5D-Engine** wie [`raycast_1`](../raycast_1/README.md)
— die auf allen drei Exportzielen (Desktop, HTML5, nativ/Kivy)
vollständig ist: texturierte Wände, ein verschiebbarer Himmel,
texturiertes Boden-Raycasting in niedriger Auflösung, und
kamerazugewandte Billboard-Sprites.

Wo `raycast_1` ein kleiner, von maze_1 abgeleiteter Korridor ist, der
*die Ich-Perspektive-Ansicht selbst* lehrt, ist `raycast_2` ein
**größeres Labyrinth mit Geschehen in der 3D-Ansicht** — sammelbare
Edelsteine, ein patrouillierender Gegner und ein edelsteingesperrter
Ausgang. Siehe [`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md)
für die Engine und
[`docs/RAYCAST_2_SAMPLE_PLAN.md`](../../docs/RAYCAST_2_SAMPLE_PLAN.md)
für das Design und den Einheitenplan dieses Beispiels.

Ein vollständiges Zwei-Level-Spiel: navigiere jedes Labyrinth in der
Ich-Perspektive, sammle jeden Edelstein, während du patrouillierenden
Monstern ausweichst, und erreiche den edelsteingesperrten Ausgang —
der erste (warme Ziegel-)Raum führt zu einem zweiten (kühlen
Kristallhöhlen-)Raum, und diesen abzuschließen gewinnt das Spiel.
Verfügbar über den Willkommens-Tab der IDE (*"Raycast — Level 2"*) und
exportiert auf alle drei Ziele (Desktop, HTML5, nativ/Kivy).

## Wie man spielt

- **Hoch/Runter** — bewegen vorwärts/rückwärts in die Richtung, in die
  man gerade blickt (kontinuierlich, nicht gitterausgerichtet; Wände
  blockieren über die normale Solid-Instanz-Kollision der Engine).
- **Links/Rechts** — drehen auf der Stelle (dreht `facing_angle`,
  unabhängig von der Bewegung — man kann sich im Stehen drehen).
- **Sammle die Edelsteine**, die im Labyrinth verstreut sind — jeder
  fügt 10 zum Punktestand hinzu, angezeigt im **Bildschirm-HUD** (oben
  links), gezeichnet über die Ich-Perspektive-Ansicht von `obj_hud`.
- **Weiche den Monstern aus** — sie patrouillieren die Korridore
  (prallen von Wänden ab) und werden als kamerazugewandte Billboards
  gezeichnet. Eines zu berühren kostet ein Leben und startet den Raum
  neu; du startest mit 3 Leben, angezeigt oben rechts im HUD. Gehen sie
  aus, startet das Spiel neu.
- **Ziel:** sammle **alle** Edelsteine in einem Raum, dann erreiche
  sein Ziel. Das Ziel vorzeitig zu erreichen zeigt nur die Aufforderung
  *"Collect all the gems before you leave!"* — es öffnet sich erst,
  sobald jeder Edelstein weg ist. Das Ziel des ersten (warmen Ziegel-)
  Raumes führt zu einem zweiten, kühlen **Kristallhöhlen**-Raum; diesen
  abzuschließen gewinnt das Spiel.

## Level-Geometrie

Sowohl `rooms/room0.json` als auch `rooms/room1.json` sind
15×15-Zellen-Labyrinthe (480×480), erzeugt durch einen rekursiven
Backtracker (ein *perfektes* Labyrinth — jede Zelle erreichbar,
garantiert lösbar — mit ein paar zusätzlichen durchgebrochenen Wänden
für Schleifen und längere Sichtlinien), dann in `raycast_1`s **dünnes
Kantenwand**-Modell umgewandelt: jede Grenze zwischen einer offenen
Zelle und einer Wand wird zu einem 8px-`obj_wall_h`- (32×8) oder
`obj_wall_v`- (8×32) Segment auf der Gitterlinie, sodass Korridore
echt Wolfenstein-proportioniert wirken statt klobig. Jeder Raum
verwendet einen anderen Labyrinth-Seed, sodass die beiden Level
unterschiedliche Layouts haben.

## Themen pro Raum

Die Texturen der Raycast-Ansicht sind **pro Raum**: `enable_raycast_view`
sitzt auf einem winzigen unsichtbaren Kamera-Controller-Objekt, das in
jedem Raum platziert ist — `obj_cam0` (warme Ziegel: `spr_wall_texture`/
`spr_sky`/`spr_floor`) in room0, `obj_cam1` (kühle Kristallhöhle:
`spr_wall_ice`/`spr_sky_ice`/`spr_floor_ice`, blau getönte Varianten)
in room1. Jeder Controller benennt `obj_person` als Kamera über den
`camera_object`-Parameter der Aktion, sodass der *Spieler* weiterhin
die Kamera ist, obwohl der *Controller* die Aktion auslöst. Deshalb
sieht der zweite Raum anders aus — die Konfiguration ist auf den
Controller des Raumes begrenzt, nicht in den Spieler eingebacken.

## Projektstruktur

| Datei | Zweck |
|---|---|
| `project.json` | Projekt-Manifest |
| `rooms/room0.json`, `rooms/room1.json` | Die zwei erzeugten Dünnkantenwand-Labyrinthe (maßgebliche Instanzdaten) |
| `objects/obj_person.json` | Spieler/Kamera — `keyboard`-Ereignisse steuern Drehen + Vorwärts/Rückwärts; `game_start` initialisiert Punkte/Leben; registriert die `collision_with_obj_wall_h`/`_v`-Handler, die die Wandblockierung steuern, und `collision_with_obj_monster` (Leben verlieren + Neustart) |
| `objects/obj_cam0.json`, `obj_cam1.json` | Pro-Raum-Kamera-Controller, die `enable_raycast_view` mit dem Texturthema dieses Raumes aufrufen |
| `objects/obj_gem.json` | Sammelobjekt — Kollision zerstört es; sein `destroy`-Ereignis fügt 10 zum Punktestand hinzu |
| `objects/obj_monster.json` | Patrouillierender Billboard-Gegner — bewegt sich, prallt von Wänden ab |
| `objects/obj_goal.json`, `obj_goal_final.json` | Das Ziel von room0 (→ nächster Raum) und von room1 (→ Sieg); beide edelsteingesperrt |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Dünne Wandsegmente (32×8 und 8×32) |
| `objects/obj_hud.json` | Bildschirmraum-HUD, über die Ich-Perspektive-Ansicht gezeichnet — `draw_score` + `draw_lives`. Beachte, dass es **visible: true** ist: GameMaker führt das `draw`-Ereignis einer unsichtbaren Instanz nicht aus, weshalb das HUD nicht einfach auf `obj_cam0`/`obj_cam1` liegen kann (diese sind unsichtbar) |
| `sprites/` | Wiederverwendet aus `raycast_1` (Spieler/Ziel/Wand/Himmel/Boden + Wand-Platzhalter), plus `spr_gem` (match3-Edelstein), `spr_monster` (maze_3-Monster), und der `*_ice`-blau getönte room1-Textursatz |

## Wiederverwendete Engine, wiederverwendete Grafik

`raycast_2` teilt sich `raycast_1`s Objekte und Sprites — der Zweck
dieses Beispiels ist *Level- und Gameplay-Erstellung auf der fertigen
Engine*, kein neuer Rendering-Code. Die Edelstein- und Monstergrafik
(Einheiten 2–3) sind die einzigen neuen Assets, und keine der
Spiellogik hängt von der spezifischen Grafik ab, sodass sie
umskinnbar sind.
