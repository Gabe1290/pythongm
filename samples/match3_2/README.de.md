# Match-3 — Level 2

Die spritebasierte, animierte Weiterentwicklung von
[`match3_1`](../match3_1/README.md), die in der Roadmap dieses Beispiels
versprochen wurde: dasselbe Spielfeld und dieselbe Punktezählung, jetzt
mit echten Edelstein-Sprites statt Farbrechtecken gezeichnet, mit einer
Tausch-Rutsch-Animation und Soundeffekten für Tausch/Übereinstimmung/
Kaskade. Immer noch ein Raum, ein Objekt, keine Skripte — das gesamte
Spiel sind weiterhin vier `execute_code`-Ereignisse auf einem einzigen
Controller-Objekt.

**Wo dies einzuordnen ist:** Teil der `match3_*`-Familie — reines
`execute_code`-Skript, keine eingebauten Aktionen, keine Kacheln auf
Raumebene. Siehe
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
für den Unterschied zum Ansatz mit eingebauten Aktionen über mehrere
Objekte von `maze_*`/`plateforme_*`.

**Sound & Musik:** 3 Sounddateien (`snd_swap`, `snd_match`,
`snd_cascade`), alle aktiv genutzt — aus `execute_code` über
`self._sound_queue` in die Warteschlange gestellt (siehe unten), nicht
über die Aktion `play_sound`.

## Wie man spielt

Wie in match3_1:

- **Klicke** auf eine Kachel, um sie auszuwählen (weißer Umriss), dann
  **klicke auf eine benachbarte Kachel**, um die beiden zu tauschen. Der
  Tausch **rutscht** jetzt an seinen Platz, statt sofort einzurasten.
- Wenn der Tausch **3 oder mehr gleichfarbige Kacheln** in einer Reihe
  oder Spalte ausrichtet, blinken die passenden Kacheln kurz, werden
  zerstört, und die Kacheln darüber **rutschen nach unten**, um die
  Lücke zu füllen; neue Kacheln fallen von oben ins Spielfeld.
  Kettenreaktionen ("Kaskaden") lösen sich Welle für Welle auf.
- Ein Tausch, der keine Übereinstimmung ergibt, **rutscht zurück** an
  seine ursprüngliche Position, statt einfach zurückzuspringen.
- Jede zerstörte Kachel ist **10 Punkte** wert; erreiche **500 Punkte**, um zu gewinnen.
- Jeder Tauschversuch spielt einen Klick; eine erfolgreiche
  Übereinstimmung spielt einen Glockenton, und jede weitere Kaskade
  derselben Kombo spielt einen helleren, aufsteigenden Glockenton.

## Was sich von match3_1 unterscheidet

| match3_1 | match3_2 |
| -------- | -------- |
| Kacheln als gefüllte Farbrechtecke gezeichnet | Kacheln als Edelstein-**Sprites** gezeichnet (Zeichen-Warteschlangen-Befehl im `draw_sprite`-Stil), eine Form pro Farbe für Barrierefreiheit bei Farbenblindheit |
| Tausch wird sofort angewendet, Übereinstimmungen werden sofort ausgewertet | Tausch **rutscht** zuerst an seinen Platz (~4 Frames); ein nicht passender Tausch rutscht zurück statt einzurasten |
| Kein Audio | **Soundeffekte** für Tausch/Übereinstimmung/Kaskade, aus `execute_code` über die neue Primitive `self._sound_queue` in die Warteschlange gestellt (siehe unten) |

Die Spielfeld-Logik selbst (Gittermodell, Übereinstimmungssuche,
Kaskaden-Fall, Punktezählung, Siegbedingung) ist gegenüber match3_1
unverändert — das ist ein wirklich lesbarer Diff, keine Neufassung.

## Projektstruktur

| Datei | Zweck |
| ---- | ------- |
| `project.json` | Projekt-Manifest — 800×800-Fenster, 60 fps, Start-Raum `rm_match3` |
| `rooms/rm_match3.json` | der einzige Raum; enthält eine Instanz von `obj_GridManager` bei (0, 0) |
| `objects/obj_GridManager.json` | das gesamte Spiel: vier Ereignisse, jedes mit einer einzigen `execute_code`-Aktion |
| `sprites/spr_gem_red|blue|green|yellow.png` | 88×88-Edelstein-Kacheln (siehe `CREDITS.txt`) — so bemessen, dass sie genau dort einpassen, wo früher match3_1s Rechteck-Füllung war, da `draw_sprite` in nativer Größe ohne Skalierung zeichnet |
| `sounds/snd_swap|match|cascade.wav` | kurze synthetisierte Töne (siehe `CREDITS.txt`) |

## Wie der Code funktioniert

Zustand und die `step`-Zustandsmaschine sind dieselben wie in match3_1
(`grid`, `sel`, `marked`, `flash`/`flash_total`, `falling`/`fall_speed`,
`score`, `target`, `won`, `find_matches`) — siehe diese README für die
vollständige Beschreibung. Neuer Zustand für diese Version:

| Attribut | Bedeutung |
| --------- | ------- |
| `sprite_names` | `['spr_gem_red', 'spr_gem_blue', 'spr_gem_green', 'spr_gem_yellow']`, genauso indiziert wie `palette` in match3_1 |
| `swap_off` | Dict `(gx, gy) → (dx, dy)` Pixel-Versatz für den laufenden Tausch-Rutsch-Vorgang; schrumpft mit `swap_speed` px/Frame auf `(0, 0)` — dieselbe Zur-Ruhe-schrumpfen-Technik, die `falling` bereits für Kaskaden verwendet, verallgemeinert auf zwei Achsen |
| `swap_phase` | `None` / `'forward'` (rutscht in die getauschte Position) / `'back'` (ein abgelehnter Tausch, der zu seinen ursprünglichen Zellen zurückrutscht) |
| `last_swap` | `(gx, gy, sx, sy)` — die beiden am laufenden Tausch beteiligten Zellen, sodass `step` sie zurücksetzen kann, ohne Closure-Zustand zu benötigen |
| `pending_marks` | die direkt nach einem Tausch berechnete Übereinstimmungsmenge, gehalten bis die Rutsch-Animation fertig ist, damit das Blinken nicht mitten im Rutschen beginnt |
| `arm_swap(a, b)` | Hilfsfunktion (definiert in `create`, wie `find_matches` auf der Instanz gespeichert), die `swap_off` für beide Zellen allein aus ihren Positionen setzt — erneutes Aufrufen mit denselben zwei Zellen erzeugt die umgekehrte Animation, was die Rückrutsch-Animation quasi kostenlos liefert |

Aktualisierter Ablauf:

```
Klick auf benachbarte Kachel
  → Gitter sofort getauscht (Daten), pending_marks berechnet
  → swap_off bewaffnet (forward) — Kacheln rutschen in ihre neuen Zellen
       │
       ▼ (Rutschen kommt zur Ruhe)
  pending_marks?
    ja  → Blinken bewaffnen (Blinken → Zerstören → Fallen → Neuscan, wie in match3_1)
    nein → Gitter zurücktauschen, swap_off mit DENSELBEN zwei Zellen erneut bewaffnen (phase='back')
             │
             ▼ (Rutschen kommt zur Ruhe)
          idle
```

- **`create`** — dieselbe Gitter-Aussaat wie match3_1, plus
  `sprite_names`, `swap_off`/`swap_speed`/`swap_phase`/`last_swap`/
  `pending_marks` und die `arm_swap`-Hilfsfunktion.
- **`mouse_left_press`** — die Auswahllogik ist unverändert; ein
  gültiger benachbarter Tausch wendet jetzt den Gittertausch an,
  berechnet `pending_marks`, bewaffnet das Vorwärts-Rutschen und stellt
  `snd_swap` in die Warteschlange.
- **`step`** — die Blink-/Fall-Blöcke sind gegenüber match3_1
  unverändert (stellen weiterhin `snd_cascade` bei einer verketteten
  erneuten Übereinstimmung in die Warteschlange); ein neuer
  `elif self.swap_off:`-Block lässt das Rutschen abklingen und
  bewaffnet, sobald es zur Ruhe gekommen ist, entweder das Blinken (mit
  `snd_match` in der Warteschlange) oder startet das Rückrutsch-Rutschen.
- **`draw`** — dieselbe Panel-/Spielfeld-/Auswahl-/Punkte-/Anweisungs-/
  Sieges-Banner-Zeichnung wie match3_1, aber jede Kachel ist jetzt ein
  `{'type': 'sprite', 'sprite_name': ..., 'x': ..., 'y': ...}`-
  Zeichen-Warteschlangen-Befehl statt eines gefüllten Rechtecks
  (weiterhin während des Blinkens markierter Kacheln durch ein einfaches
  weißes gefülltes Rechteck ersetzt, genau wie match3_1 es tat), versetzt
  um `swap_off` kombiniert mit `falling`.

### Die Primitive `self._sound_queue`

`execute_code` hat nur auf der Desktop-pygame-Laufzeitumgebung ein
lebendiges `game`-Objekt — sowohl die exportierte Kivy-Laufzeitumgebung
als auch die Web-/Pyodide-Laufzeitumgebung binden `game = None` in
diesem Geltungsbereich, sodass `game.sounds[...].play()` (die
naheliegende Lösung) nur auf dem Desktop funktioniert. Dieses Beispiel
war der Anlass, eine echte plattformübergreifende Primitive
hinzuzufügen: Das `execute_code` jedes Ereignisses kann

```python
self._sound_queue.append('snd_swap')
# oder, für eine abweichende Lautstärke:
self._sound_queue.append({'sound': 'snd_swap', 'volume': 0.5})
```

und es spielt identisch auf allen drei Zielen:

- **Desktop** — `ActionExecutor.execute_event` leert sie und spielt sie
  ab (über `game.sounds[...]`) direkt nach jedem Ereignis, nicht nur
  nach `draw`.
- **Kivy-Export** — `GameObject._drain_sound_queue` (generiert in
  `base_object.py`) löst den Namen über eine generierte `asset_paths.py`
  (`SOUND_PATHS`) auf und ruft die vorhandene `play_sound()`-Hilfsfunktion
  auf; einmal pro Frame und pro lebendiger Instanz aus der `update()`-
  Schleife der Szene geleert, sodass es sogar für Objekte ohne
  `draw`-Ereignis funktioniert.
- **Web (Pyodide)** — das Python-Bootstrap gibt alle in die Warteschlange
  gestellten Sounds im JSON-Patch zusammen mit der Zeichen-Warteschlange
  zurück; `engine.js` spielt sie als echte `<audio>`-Elemente über
  denselben gepoolten Audio-Pfad ab, den die strukturierte
  `play_sound`-Aktion bereits verwendete.

Dieselbe Namensauflösungslücke bestand für `draw_sprite`-artige Befehle,
die aus rohem `execute_code` gesendet wurden (das Kachel-Rendering
dieses Beispiels) — Kivys Zeichen-Warteschlangen-Renderer konnte zuvor
einen Sprite nur über einen `sprite_path` auflösen, der zur
Codegenerierungszeit für *strukturierte* Aktionen eingebettet wurde, so
dass ein handgeschriebenes `{'type': 'sprite', 'sprite_name': ...}`-Dict
dort stillschweigend nicht gerendert wurde. Auf dieselbe Weise behoben:
`asset_paths.py` trägt jetzt auch `SPRITE_PATHS`, und der `'sprite'`-Fall
der Kivy-Zeichen-Warteschlange greift bei fehlendem, bereits aufgelöstem
Pfad namensbasiert darauf zurück.

### Zum Experimentieren

Dieselben Stellschrauben wie in match3_1 (`self.cols`/`self.rows`,
`self.palette`, `self.target`, `flash_total`, `fall_speed`), plus:

- Tausch-Animationsgeschwindigkeit: `self.swap_speed` (px/Frame; 24 →
  ~4 Frames pro Rutschen bei `tile=96`).
- Lautstärke: übergib ein `{'sound': ..., 'volume': ...}`-Dict statt
  eines bloßen Namens an `self._sound_queue.append(...)`.

## Roadmap

**[match3_3](../match3_3/README.md)** — fertig: ein Zuglimit, drei Räume
als Level mit steigendem Ziel, und Spezialkacheln
(4/5-in-einer-Reihe-Boni). Schließt match3_1s ursprüngliche Roadmap ab.

## Export-Status

- **Test Game (F5) / Desktop:** funktioniert — end-to-end mit einem
  echten `GameRunner`-Lauf verifiziert, der einen tatsächlichen
  Mausklick über den Standard-pygame-Ereignispfad einspeist (Tausch →
  Übereinstimmung → Kaskade → Punkte, mit beobachteten echten
  `pygame.mixer.Sound.play()`-Aufrufen).
- **Android (.apk) / Mobil (Kivy):** **unterstützt.** Verifiziert, dass
  der Export sauber kompiliert, `asset_paths.py` die richtigen
  `SPRITE_PATHS`/`SOUND_PATHS` trägt, und dass die Sprite-Bilder/
  Sounddateien nach `assets/images`/`assets/sounds` kopiert werden. Der
  eigentliche `.apk`-Build erfordert zusätzlich buildozer (via WSL unter
  Windows) — siehe [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Web (HTML5):** **unterstützt.** Das Pyodide-Bootstrap der
  exportierten Seite leert `self._sound_queue` in denselben
  JSON-Roundtrip wie die Zeichen-Warteschlange; verifiziert, dass das
  generierte Bootstrap kompiliert und sowohl Zeichenbefehle als auch in
  die Warteschlange gestellte Sounds korrekt unter reinem CPython
  überträgt (kein Browser für diese Prüfung nötig — der In-Browser-
  Pyodide-Start selbst wird von der automatisierten Suite nicht geprüft,
  derselbe Vorbehalt wie bei match3_1). Benötigt beim ersten Laden
  Internetzugang (Pyodide lädt von einem CDN).
- **Eigenständiges Zip:** mit diesem Beispiel ungetestet.
