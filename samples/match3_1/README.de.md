# Match-3 — Level 1

Ein minimales, vollständiges Match-3-Puzzlespiel (drei in einer Reihe).
Dies ist das erste pygm2-Beispiel, das **nativ im eigenen Projektformat
der IDE geschrieben wurde** — die Labyrinth- und Plattform-Beispiele
wurden aus GameMaker-8.x-`.gmk`-Dateien importiert; dieses wurde direkt
für die pygm2-Laufzeitumgebung geschrieben.

Es ist absichtlich klein: ein Raum, ein Objekt, keine Skripte, keine
Sounds. Das gesamte Spiel steckt in vier Ereignissen eines einzigen
Controller-Objekts, was es zum Referenzbeispiel für die Aktion
`execute_code` und für das Rendering über die Zeichen-Warteschlange
macht. Fortgeschrittenere Versionen (spritebasierte Kacheln, Sound,
Level) sind als `match3_2` usw. geplant — siehe *Roadmap* unten.

**Wo dies einzuordnen ist:** `match3_*` ist die letzte (und
unterschiedlichste) der drei Beispielfamilien — ein anderes Paradigma,
kein inkrementeller Schritt: keine eingebauten Aktionen, keine
Pro-Kachel-Objekte, keine Kacheln auf Raumebene. Alles (Gitterzustand,
Kollision, Rendering) wird direkt aus `execute_code`-Python gesteuert,
statt aus eingebauten Aktionen über viele Objekte hinweg zusammengesetzt
zu werden, wie es bei `maze_*` und `plateforme_*` der Fall ist. Siehe
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
für die vollständige Progression.

**Sound & Musik:** keine — absichtlich, aus dem oben genannten Grund.
(Sound wird ab `match3_2` möglich, über die Sound-Warteschlangen-Primitive,
die dieses Beispiel eingeführt hat.)

## Wie man spielt

- **Klicke** auf eine Kachel, um sie auszuwählen (weißer Umriss), dann
  **klicke auf eine benachbarte Kachel**, um die beiden zu tauschen.
- Wenn der Tausch **3 oder mehr gleichfarbige Kacheln** in einer Reihe
  oder Spalte ausrichtet, blinken die passenden Kacheln kurz, werden
  zerstört, und die Kacheln darüber **rutschen nach unten**, um die
  Lücke zu füllen; neue Kacheln fallen von oben ins Spielfeld.
- Kettenreaktionen ("Kaskaden") lösen sich Welle für Welle auf, jede mit
  ihrer eigenen Blink-und-Rutsch-Animation.
- Ein Tausch, der keine Übereinstimmung ergibt, wird sofort rückgängig gemacht.
- Jede zerstörte Kachel ist **10 Punkte** wert; erreiche **500 Punkte**, um zu gewinnen.

## Projektstruktur

| Datei | Zweck |
| ---- | ------- |
| `project.json` | Projekt-Manifest — 800×800-Fenster, 60 fps (`room_speed`), Start-Raum `rm_match3` |
| `rooms/rm_match3.json` | der einzige Raum; enthält eine Instanz von `obj_GridManager` bei (0, 0) |
| `objects/obj_GridManager.json` | das gesamte Spiel: vier Ereignisse, jedes mit einer einzigen `execute_code`-Aktion |
| `sprites/spr_red|blue|green|yellow.*` | 32×32-Kachel-Quadrate — **noch nicht verwendet**; reserviert für die spritebasierte Folgeversion (siehe `CREDITS.txt`) |

Es gibt kein Spielerobjekt und kein Pro-Kachel-Objekt: Das Spielfeld
ist reine Daten (eine 6×6-Liste von Farbindizes), die einer einzigen
unsichtbaren Controller-Instanz gehören, und alles auf dem Bildschirm
wird durch das `draw`-Ereignis dieses Controllers über die
Laufzeit-Zeichen-Warteschlange (`self._draw_queue`) gezeichnet.

## Wie der Code funktioniert

Der gesamte Zustand lebt auf der Controller-Instanz (`self.…`), erstellt
im `create`-Ereignis:

| Attribut | Bedeutung |
| --------- | ------- |
| `grid` | 6×6-Liste von Ganzzahlen 0–3 (Indizes in `palette`); ohne bereits vorhandene Übereinstimmungen initialisiert |
| `sel` | aktuell ausgewählte Zelle `(gx, gy)` oder `None` |
| `marked` | Menge der aktuell übereinstimmenden und blinkenden Zellen |
| `flash` / `flash_total` | verbleibende Frames der Blinkphase / ihre Länge (36 Frames ≈ 0,6 s bei 60 fps) |
| `falling` | Dict `(gx, gy) → Pixel` — wie weit über ihrer Ruhezelle sich jede rutschende Kachel gerade befindet |
| `fall_speed` | Rutschgeschwindigkeit in Pixel pro Frame (12 → eine 96-px-Reihe in ~0,13 s) |
| `score`, `target`, `won` | Punktestand-Zustand (Sieg bei 500) |
| `find_matches` | Hilfsfunktion (definiert in `create`, auf der Instanz gespeichert), die das Gitter durchsucht und die Menge aller übereinstimmenden Zellen zurückgibt |

Das Spiel ist eine kleine Zustandsmaschine, gesteuert durch das
`step`-Ereignis:

```
idle ──(Klick-Tausch, Übereinstimmung gefunden)──▶ FLASH (Blinken, 36 Frames)
                                        │ Kacheln zerstört, Punkte hinzugefügt
                                        ▼
                                      FALL (Versatz schrumpft 12 px/Frame)
                                        │ gelandet → Gitter neu scannen
                     neue Übereinstimmung ─┴─ keine Übereinstimmung
                                 │            │
                                 ▼            ▼
                               FLASH        idle
```

- **`create`** — baut das Startgitter (würfelt jede Kachel neu, die
  eine sofortige Übereinstimmung vervollständigen würde), initialisiert
  den obigen Zustand und definiert `find_matches`.
- **`mouse_left_press`** — Auswahl-/Abwahllogik; bei einem
  benachbarten Tausch wendet sie den Tausch an und bewaffnet entweder
  das Blinken (`marked`, `flash`) oder macht ihn rückgängig. Eingaben
  werden ignoriert, während ein Blinken oder Fallen läuft, sowie nachdem
  das Spiel gewonnen wurde.
- **`step`** — zählt das Blinken herunter; bei Ablauf schreibt es die
  Punkte gut, schreibt jede betroffene Spalte in ihr endgültiges Layout
  um und zeichnet einen Pixel-Versatz in `falling` für jede Kachel auf,
  die sich bewegt hat (überlebende Kacheln erhalten
  `heruntergefallene_reihen × 96`; Nachfüll-Kacheln treten von oberhalb
  des Spielfelds ein). Während `falling` nicht leer ist, schrumpft es
  jeden Versatz um `fall_speed`; wenn alles gelandet ist, wird erneut
  nach Kaskaden-Übereinstimmungen gescannt und entweder das Blinken
  erneut bewaffnet oder zu idle zurückgekehrt.
- **`draw`** — zeichnet das Spielfeld-Panel, dann jede Kachel bei
  `ruheposition − fall_versatz`. Kacheln oberhalb der oberen Kante des
  Spielfelds werden abgeschnitten (teilweise aufgetaucht) oder
  übersprungen (vollständig verborgen), sodass Nachfüllungen scheinbar
  von unter der Kopfzeile hereingleiten. Markierte Kacheln blinken alle
  6 Frames weiß und tragen einen weißen Umriss; Auswahl, Punktezeile,
  Anweisungen und das Sieges-Banner werden zuletzt gezeichnet.

### Zum Experimentieren

- Spielfeldgröße: `self.cols` / `self.rows` (die Layout-Konstanten
  `ox`, `oy`, `tile` steuern die Platzierung — ein 6×6-Spielfeld mit
  96-px-Kacheln passt in das 800×800-Fenster).
- Farben / Kachelarten: `self.palette` (füge ein Tupel hinzu, um eine
  5. Farbe zu erhalten; die Neuwürfel-Logik und der Renderer übernehmen
  sie automatisch, aber aktualisiere `random.randrange(4)` in `create`
  und `step`).
- Schwierigkeit: `self.target` (Punkte zum Gewinnen), `flash_total`,
  `fall_speed`.

## Roadmap (geplante fortgeschrittene Versionen)

- **[match3_2](../match3_2/README.md)** — fertig: zeichnet die Kacheln
  mit Sprites statt Farbrechtecken, fügt Soundeffekte für
  Tausch/Übereinstimmung/Kaskade hinzu, und eine Tausch-Rutsch-Animation.
- **[match3_3](../match3_3/README.md)** — fertig: ein Zuglimit, drei
  Räume als Level mit steigendem Ziel, und Spezialkacheln aus
  4/5-in-einer-Reihe-Übereinstimmungen. Schließt diese Roadmap ab.

Die Versionen sollen die maze_1→3-Progression widerspiegeln: jede eine
lesbare Weiterentwicklung der vorherigen.

## Export-Status

- **Test Game (F5) / Desktop:** funktioniert — das Spiel läuft auf der
  Standard-pygame-Laufzeitumgebung. Es wird in CI-artigen
  Smoke-Test-Läufen über `tools/smoke_run_samples.py` ohne
  Bildschirmausgabe geprüft.
- **Android (.apk) / Mobil (Kivy):** **unterstützt** (seit 03.07.2026).
  Die exportierte Kivy-Laufzeitumgebung rendert die Zeichen-Warteschlange
  des Spiels (Rechtecke und Text, mit der y-Achse ins Kivy-Koordinatensystem
  von unten nach oben umgewandelt), verteilt Taps als `mouse_left_press`-
  Ereignis mit raumkoordinierten `mouse_x`/`mouse_y` sowohl auf Android
  (unter Umkehrung der Vollbild-Skalierungstransformation) als auch auf
  Desktop-Kivy, und — da dieses Spiel keine Tastaturereignisse hat —
  lässt das virtuelle D-Pad-Overlay weg, das sonst die untere rechte Ecke
  des Spielfelds verdecken würde. Das exportierte Spiel wird ohne
  Bildschirmausgabe in `tests/test_kivy_draw_queue_mouse_export.py`
  geprüft, das eine vollständige Runde Tausch → Blinken → Rutschen durch
  den generierten Code spielt. Der eigentliche `.apk`-Build erfordert
  zusätzlich buildozer (via WSL unter Windows) — siehe
  [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md) für die
  vollständige Anleitung (Einrichtung, Build-Zeiten, Caching für den
  Unterrichts-/Sitzungsgebrauch); verbleibende Kivy-Export-Paritätslücken,
  die dieses Spiel *nicht* betreffen, sind unter "Kivy/Android export" in
  der Repository-`TODO.md` aufgelistet.
- **Web (HTML5):** **unterstützt** (seit 10.07.2026) — und der beste Weg
  zu iPhones (keine Installation, keine Signierung). Die exportierte
  Seite erkennt, dass das Spiel Python-`execute_code`-Ereignisse enthält,
  und lädt die Pyodide-Laufzeitumgebung, um sie mit der Semantik der IDE
  auszuführen; Taps/Klicks werden als Linksklick-Ereignis verteilt, und
  die Zeichen-Warteschlange wird auf das Canvas gerendert. End-to-end in
  Headless-Chromium verifiziert (Spielfeld rendert, Klick-Tausch,
  Blinken, Rutschen, Punktezählung). Ein Vorbehalt: Die Python-Laufzeit
  lädt von einem CDN, daher benötigt die Seite beim Öffnen
  Internetzugang — reine Aktions-Spiele (die Labyrinth-/Plattform-
  Beispiele) bleiben vollständig offline.
- **Eigenständiges Zip:** mit diesem Beispiel ungetestet.
