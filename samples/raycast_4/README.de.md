# Raycast — Level 4

Das vierte Ich-Perspektive-Level im Doom-/Wolfenstein-Stil, und das
erste, das **um eine dauerhafte untere Statusleiste** herum gebaut ist
— die DOOM-Ästhetik statt `raycast_3`s Ecken-Overlays. Die 3D-Ansicht
ist absichtlich **kürzer** (Letterbox), um Platz für die Leiste zu
schaffen; das ist Teil des Looks, kein Bug.

Wo `raycast_3` ein Ecken-HUD und Gesundheit als Ressource bewiesen
hat, zeigt `raycast_4` die beiden Engine-Features, die für eine
DOOM-Leiste gebaut wurden:

- **`viewport_height`** bei `enable_raycast_view` schrumpft die
  Ich-Perspektive-Ansicht in den oberen Teil des Fensters und
  reserviert das Band darunter.
- **`draw_doom_hud`** füllt dieses Band: eine Gesundheitsleiste + Zahl,
  ein **gesundheitsreaktives Gesichtsporträt**, Punkte, Leben und ein
  Schlüsselzähler — alles aus gewöhnlichen Zeichenbefehlen, sodass es
  gleichermaßen auf Desktop, HTML5 und nativ (Kivy) rendert.

Siehe [`docs/RAYCAST_DOOM_HUD_PLAN.md`](../../docs/RAYCAST_DOOM_HUD_PLAN.md)
für die Technik, und [`raycast_3`](../raycast_3/README.md) für die
Ecken-HUD-Alternative, die dieses Level bewusst nicht nachrüstet.

**Innenraum-Gefühl.** Zwei Dinge lassen dies wie einen Korridor in
einem Gebäude wirken statt wie ein offenes Labyrinth: es wirft eine
**Steindecke** (`spr_ceiling`) statt des verschiebbaren Himmels, den
die anderen Raycast-Beispiele verwenden — gesetzt über
`ceiling_texture` mit leer gelassenem `sky_texture` — und die Wände
werden **höher** gerendert. Diese Wandhöhe (`RAYCAST_WALL_HEIGHT`,
1,5× ein Würfel) ist ein globaler Engine-Standard, sodass jedes
Raycast-Spiel die höheren Wände bekommt; die Decke ist die eigene Wahl
dieses Beispiels.

**Sound & Musik:** keine — diesem Beispiel liegen keine Sounddateien bei.

## Wie man spielt

- **Hoch/Runter** — bewegen vorwärts/rückwärts in die Richtung, in die
  man gerade blickt.
- **Links/Rechts** — drehen auf der Stelle.
- **Sammle die Schlüssel** — jeder bringt 25 Punkte und erhöht den
  **KEYS**-Zähler in der Leiste um eins. Es gibt drei.
- **Weiche den Monstern aus** — eines zu berühren kostet **25
  Gesundheit** (danach ein kurzes Unverwundbarkeitsfenster). Beobachte
  das **Gesicht**: es zuckt zusammen, während deine Gesundheit sinkt,
  noch bevor du die Zahl gelesen hast.
- **Geht die Gesundheit aus** → verliere ein Leben, Gesundheit füllt
  sich auf, der Raum startet neu. **Gehen die Leben aus** → das Spiel
  startet neu.
- **Erreiche den Ausgang**, sobald du **alle drei Schlüssel** gefunden
  hast. Ihn vorzeitig zu berühren sagt dir nur, dass das Tor
  verschlossen ist.
- **Drücke `M`**, um eine **Minikarte** der Wände einzublenden
  (standardmäßig aus). Sie wird innerhalb der 3D-Ansicht gezeichnet,
  über der Statusleiste, und wird ein-/ausgeschaltet — dieselbe
  Karte-auf-Anfrage, die `raycast_3` verwendet, hier von der Leiste
  ferngehalten.

## Die Statusleiste (`draw_doom_hud`)

`obj_person` zeichnet sie jeden Frame, im Bildschirmraum, über die
fertige 3D-Ansicht. Von links nach rechts:

| Zone | Zeigt |
|---|---|
| Links | `HEALTH`-Beschriftung + eine proportionale Gesundheitsleiste + die Zahl |
| Zentrum | das **Gesichtsporträt**, ein 4-Frame-Streifen, der auf Gesundheit reagiert |
| Rechts | `SCORE` über `LIVES` |
| Ganz rechts | der `KEYS`-Zähler |

Das Gesicht ist der ganze Sinn dieses Beispiels. Sein Frame wird durch
eine gleichmäßige Bucket-Zuordnung über die Gesundheit gewählt — Frame
0 (ruhig) nahe voll, der letzte Frame (sterbend) nahe leer — sodass das
Porträt dir sagt, wie es dir geht, bevor die Zahl es tut, genau wie
DOOMs eigene Leiste.

**`obj_person` ist sowohl die Kamera *als auch* der HUD-Zeichner.**
Das ist Absicht: der Schlüsselzähler ist dann einfach eine
Instanzvariable auf `obj_person` (`keys`), sodass der Ziel-Ausdruck
von `draw_doom_hud` denselben Wert identisch auf allen drei
Exportzielen liest. Ein separates unsichtbares Kameraobjekt (wie in
`raycast_3`) könnte keine Variable tragen, die das sichtbare HUD braucht.

## Der Letterbox-Effekt (`viewport_height`)

`enable_raycast_view` läuft in `obj_person`s `create` mit
`viewport_height: 400` in einem 640×480-Fenster — die 3D-Ansicht ist
also 400px hoch, und die unteren **80px** sind reserviert, von der
Engine schwarz gefüllt, und von der Leiste übermalt. Setze
`viewport_height` auf `0` (den Standard), und die Ansicht füllt das
gesamte Fenster ohne reserviertes Band, genau wie `raycast_1`–`3` es tun.

Der Horizont bewegt sich mit der kürzeren Ansicht nach oben, und
Wände/Himmel/Boden skalieren alle dazu — es ist ein echter
Letterbox-Effekt, keine Leiste, die über eine volle Ansicht gelegt
wird. (Bei Kivy, das y-up ist, liegt das reservierte Band trotzdem
unten im Fenster; die Engine übernimmt die Umkehrung.)

## Projektstruktur

| Datei | Zweck |
|---|---|
| `project.json` | Manifest — 640×480-Fenster, ein Raum |
| `rooms/room0.json` | Das Labyrinth: 15×15 Zellen, 3 Schlüssel, 4 Monster, ein schlüsselgesperrter Ausgang |
| `objects/obj_person.json` | Spieler + Kamera + Statusleiste — Bewegung, Gesundheit, Schlüssel, `draw_doom_hud` |
| `objects/obj_key.json` | Ein Schlüssel (passiv; die Kollision von `obj_person` behandelt ihn) |
| `objects/obj_monster.json` | Patrouillierender Billboard-Gegner |
| `objects/obj_goal.json` | Schlüsselgesperrter Ausgang (öffnet sich, wenn kein `obj_key` mehr übrig ist) |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Dünne Wandsegmente |
| `sprites/` | Wiederverwendete Wand-/Boden-/Spieler-/Monster-Grafik, eine neue **`spr_ceiling`** (Innenraum-Steindecke, ersetzt den Himmel), plus neue `spr_face` (4-Frame-Porträt) und `spr_key` |

## Das Labyrinth ist erzeugt

`tools/gen_raycast_4_maze.py` baut den Raum, indem es **an
`raycast_3`s eingecheckten Generator delegiert** — dasselbe rekursive
Backtracker-Labyrinth, dieselben dünnen Kantenwände, dieselbe
gewählte-Seed-Disziplin (der Spawn öffnet sich nach Osten, jede Zelle
erreichbar). Es unterscheidet sich nur darin, was verstreut wird
(Schlüssel, nicht Edelsteine/Verbandskästen) und dass `obj_person` die
Kamera ist. Erneutes Ausführen reproduziert den ausgelieferten Raum;
ein Test fixiert ihn.

## Zum Experimentieren

- **Leistenhöhe vs. Viewport:** die `height` bei `draw_doom_hud` (80)
  sollte zum reservierten Band passen (`640×480 − viewport_height 400
  = 80`). Ändere eines, ändere das andere.
- **Gesichtsreaktivität:** `face_frames` (4) verteilt die Gesundheit
  über den Streifen. Ein 5-Frame-Streifen mit `face_frames: 5` gibt
  feinere Ausdrücke.
- **Schaden/Schlüssel:** `-25` im `collision_with_obj_monster`-Ereignis
  von `obj_person`; die 3 Schlüssel und 4 Monster in den `counts` des
  Generators.
- **Leistenfarben und Beschriftungen:** die `draw_doom_hud`-Parameter
  im `draw`-Ereignis von `obj_person`.

## Export-Status

Läuft auf allen drei Zielen. Abgedeckt durch die Headless-Smoke-Suite
(`tools/smoke_run_samples.py`) und `tests/test_raycast_4_sample.py`,
die die echte Schleife durchspielt: die Leiste rendert alle ihre Teile
über die geschrumpfte Ansicht, unten am reservierten Band
ausgerichtet; das **Gesichts-Frame folgt der Gesundheit** (100/75/50/25
→ 0/1/2/3); eine Schlüsselaufnahme zählt, punktet und wird zerstört.

Es wurde verifiziert, dass die Kivy- und HTML5-Exporte alles tragen —
den Letterbox-`viewport_height` in der Kamerakonfiguration,
`draw_doom_hud`, das Mehr-Frame-Gesicht — aber der **visuelle**
Playtest pro Ziel ist der letzte Schritt und lohnt sich, mit eigenen
Augen betrachtet zu werden: dies ist das erste Raycast-Beispiel, dessen
*Ansichtsform* sich ändert, also dasjenige, das es am meisten wert
ist, in einem Browser und auf Android beim Rendern beobachtet zu werden.
