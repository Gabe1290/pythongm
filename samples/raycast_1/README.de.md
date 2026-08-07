# Raycast — Level 1

Eine Ansicht aus der Ich-Perspektive im Doom-/Wolfenstein-Stil vom
**gleichen Labyrinth-Layout wie `maze_1`** — gleiche Räume, gleiches
Ziel, gleiche lösbare Wege. Wo `maze_1` das Labyrinth aus der
Vogelperspektive mit vollzelligen Wandblöcken zeigt, rendert dieses
Beispiel es als Raycast-Projektion mit **dünnen Kantenwänden**
(8px-Trennwände, die auf Zellgrenzen sitzen, nicht 32px-Blöcke, die
eine Zelle füllen) — echte, im Wolfenstein-Maßstab proportionierte
Korridore, nicht nur eine Ich-Perspektive-Kamera, die auf das alte,
klobige Layout aufgesetzt wurde. `rooms/room0.json` und `room1.json`
wurden aus `maze_1`s ursprünglichem Layout über eine
topologieerhaltende Umwandlung neu erzeugt (gleiche Konnektivität/
Lösbarkeit, andere Wandgeometrie), nicht von Hand neu gestaltet. Siehe
[`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) im
Repository-Wurzelverzeichnis für den vollständigen technischen Plan,
einschließlich des Abschnitts "Complete rethink" darüber, warum
vollzellige Wände keinen echten Wendespielraum boten.

**Dies ist 2,5D, nicht 3D** — die Spiellogik ist gegenüber `maze_1`
vollständig unverändert (dieselbe 2D-`x`/`y`-Position, dieselbe feste
Wand-Kollision); nur das *Bild* wird so vorgetäuscht, dass es
dreidimensional aussieht. Es gibt keinen vertikalen Blick (kein
Neigen), Korridore müssen gitterausgerichtet sein, und es gibt keine
echte Raum-über-Raum-Überlagerung. Das ist eine bewusste, ehrliche
Einschränkung, kein fehlendes Feature — siehe die "Why raycasting"-
Pädagogik-Anmerkung des Plandokuments.

**Status — vollständig texturiert (Wände, Himmel, Boden, Billboards)
auf allen drei Zielen: Desktop (pygame), HTML5 und nativ (Kivy).**
Wände tasten eine **Ziegeltextur** ab (`spr_wall_texture`, über
`wall_texture`): jede Bildschirmspalte tastet einen vertikalen
Streifen an der Trefferposition des Strahls ab, skaliert nach
Entfernung, wobei die abgewandte Wandseite bei halber Helligkeit einen
kostenlosen Tiefenhinweis liefert. Die Decke ist ein **DOOM-artiger
Himmel** (`spr_sky`, über `sky_texture`) — ein Panorama, das sich beim
Drehen horizontal verschiebt (eine volle 360°-Drehung schiebt es
einmal durch) und sich *nicht* mit der Entfernung zurückzieht, sodass
es sich wie ein unendlich ferner Horizont liest. Der Boden ist eine
**projizierte Steintextur** (`spr_floor`, über `floor_texture`) — ein
Boden-Raycasting in niedriger Auflösung (Pixel-für-Pixel bei voller
Auflösung war ~13× zu langsam in reinem Python; `floor_cast_res` legt
das Downsampling fest, 4 ≈ 5ms), das pro Gitterzelle kachelt und
nahtlos an den Wandsockeln trifft. `obj_goal` wird als
kamerazugewandtes Billboard-Sprite gerendert (nach Entfernung
skaliert, von Wänden verdeckt) — siehe "Was hier neu ist". Um zur
flachen Optik zurückzukehren, leere `wall_texture`/`sky_texture`/
`floor_texture` bei der Aktion `enable_raycast_view`.

## Wie man spielt

- **Hoch/Runter** bewegen vorwärts/rückwärts in die Richtung, in die
  man gerade blickt (kontinuierliche Bewegung, nicht gitterausgerichtet
  — Wände blockieren weiterhin über die normale
  Solid-Instanz-Kollision der Engine, unverändert gegenüber `maze_1`).
- **Links/Rechts** drehen auf der Stelle (dreht `facing_angle`,
  unabhängig von der Bewegung — man kann sich im Stehen drehen).
- **Ziel:** finde das Ziel. Es zu berühren führt zum nächsten Raum,
  falls einer existiert (dieselbe `obj_goal`-Logik wie `maze_1`,
  byte-identische Datei).

## Was hier neu ist, Engine-seitig

- `GameInstance.facing_angle` — persistente Blickrichtung
  (GM-Winkelkonvention: 0=rechts, 90=hoch, 180=links, 270=runter),
  gesetzt über die neue Aktion `set_facing_angle`. Anders als die
  vorhandene `direction`-Eigenschaft (abgeleitet von
  `hspeed`/`vspeed`, immer 0 im Stillstand) übersteht diese das
  Stillstehen — nötig für "auf der Stelle drehen"-FPS-Steuerung.
- `enable_raycast_view` — schaltet den aktuellen Raum auf die
  Raycast-Kamera um (gebunden an die aufrufende Instanz, hier
  `obj_person`s `create`-Ereignis) oder zurück zum normalen
  Rendering aus der Vogelperspektive.
- Die Wandkarte wird **aus den bereits vorhandenen soliden Instanzen
  dieses Raumes abgeleitet**, nicht aus einem separaten
  Erstellungsformat — aber seit der Dünnwand-Überarbeitung wird sie
  als echte Kanten abgeleitet (`GameRoom._build_raycast_walls`), nicht
  als grobe Pro-Zelle-Belegung: das Sprite-Seitenverhältnis einer
  soliden Instanz entscheidet, ob es sich um ein horizontales oder
  vertikales Wandsegment handelt (ungefähr quadratisch fällt zurück
  auf das Blockieren einer ganzen Zelle, für Rückwärtskompatibilität
  mit Nicht-Dünnwand-Inhalten). Das ist, was die 8px-Dicke von
  `obj_wall_h`/`obj_wall_v` sowohl für das Rendering als auch den
  Wendespielraum tatsächlich zählen lässt, nicht nur visuell — siehe
  den Abschnitt "Complete rethink" des Plandokuments.
- **Billboard-Sprites.** Jede sichtbare, nicht solide Instanz mit
  einem Sprite (hier `obj_goal`) wird in der Raycast-Ansicht als
  kamerazugewandtes 2D-Sprite gezeichnet, nach Entfernung skaliert und
  vertikal am Horizont zentriert wie ein Wandstreifen. Die Verdeckung
  ist echtes Pro-Spalte-Clipping gegen die für diesen Frame bereits
  berechneten Wandabstände des Wand-Durchgangs, sodass ein Ziel hinter
  einer Wand korrekt verborgen wird, statt durchzuscheinen. Dies ist
  ein erster Entwurf von Phase 6 des Plandokuments (Wände zeichnen nur
  solide Instanzen; Billboards nur nicht-solide, sodass nichts doppelt
  gezeichnet wird) — keine Halbtransparenz-Überblendung, keine
  Rotation zur eigenen Ausrichtung des Sprites, nur das flache
  Skalieren-und-Clippen, das eine Wolfenstein-artige Engine für
  Gegenstände und Gegner verwendete.

## Projektstruktur

| Datei | Zweck |
|---|---|
| `project.json` | Projekt-Manifest |
| `rooms/room0.json`, `rooms/room1.json` | Dieselbe Labyrinth-*Topologie* wie `maze_1`, mit dünnen Kantenwänden neu erzeugt (siehe den Umwandlungsalgorithmus des Plandokuments) |
| `objects/obj_person.json` | Spieler/Kamera — `create` aktiviert die Raycast-Ansicht, `keyboard`-Ereignisse steuern Drehen + Vorwärts/Rückwärts, registriert `collision_with_obj_wall_h`/`_v` |
| `objects/obj_goal.json` | Zielobjekt — byte-identisch mit dem von `maze_1` |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Dünne Wandsegmente (32×8 und 8×32) — ersetzen `maze_1`s einzelnen vollblockigen `obj_wall` |
| `sprites/` | `spr_person`, `spr_goal` (von `maze_1`) plus die eigenen `spr_wall_h`/`spr_wall_v` dieses Beispiels (dünne, einfarbige Platzhalter — im Ich-Perspektive-Modus nie gerendert, nur ihre Abmessungen zählen für Kollision/Raycasting) |

## Zum Experimentieren

- Die Drehrate ist `3`°/Frame (`room_speed: 30` → 90°/s) und die
  Bewegungsgeschwindigkeit ist `3` px/Frame, beide fest codiert in
  `obj_person`s `keyboard`-Ereignissen.
- FOV `66`°, `render_distance` `20` Zellen, `cell_size` `32` — alles
  `enable_raycast_view`-Parameter auf `obj_person`s `create`-Ereignis.
- Wand-/Boden-/Deckenfarben sind ebenfalls `enable_raycast_view`-
  Parameter — der flache Fallback-Look, wenn die passende Textur
  geleert wird.
- Wanddicke ist `8`px, fest codiert in der Umwandlung, die
  `rooms/*.json` erzeugt hat (kein Laufzeitparameter) — regeneriere
  die Räume, um sie zu ändern.
- `spr_person` ist **16×16** mit einer `(4,4)-(12,12)`-Kollisionsbox —
  der Spieler wurde vom alten 32×32 halbiert (und in seiner
  Startzelle neu zentriert, sodass die Kamera weiterhin im
  Zellzentrum sitzt), weil der volle Spieler die 1-Zellen-Korridore
  beengt wirken ließ; ein kleinerer Umriss gibt viel mehr
  Bewegungsraum. Die Wand-**Ziegeltextur** wurde ebenso feiner gemacht
  (Ziegel bei halbem Maßstab), sodass die Wände weiter entfernt
  wirken — beide Anpassungen tauschen "direkt vor der Nase" gegen ein
  geräumigeres Raumgefühl.

## Export-Status

Die **vollständige** Ich-Perspektive-Ansicht rendert jetzt auf **allen
drei Zielen** — Desktop (pygame), **HTML5**
(`export/HTML5/templates/engine.js`) und **nativ/Kivy**
(`export/Kivy/kivy_exporter.py`) — mit Blickwinkel-Steuerung über
`facing_angle`, texturierten und flachen Wänden, dem verschiebbaren
Himmel, texturiertem Boden-Raycasting in niedriger Auflösung und
verdeckungs-geclippten Billboard-Sprites. Die drei Renderer teilen
keinen Code (drei handgeschriebene Kopien), sodass ihr DDA-Kern durch
`tests/test_raycast_export_parity.py` zusammengehalten wird
(Desktop↔Kivy exakte numerische Gleichheit über eine 260-Strahl-
Matrix; HTML5 strukturelle Parität, da es keine JS-Engine in CI gibt).

Boden-Raycasting verwendet auf jedem Ziel denselben Ansatz
"niedrig-aufgelöst berechnen, dann hochskalieren" (`floor_cast_res`,
Standard 4); Timing-Messungen auf echter Hardware bestätigten, dass es
ins Budget passt (Browser ~0,4 ms bei res=2; Kivy/AMD 840M ~5 ms bei
res=4). Ein Projekt kann weiterhin `floor_texture` leeren für einen
flachen `floor_color`-Boden.

Verfügbar über den Willkommens-Tab der IDE — wähle **"Raycast — Level
1"** aus dem Dropdown *Choose a sample* (das Öffnen eines Beispiels
kopiert es in deine Dokumente, sodass das mitgelieferte Original
unberührt bleibt).
