# Match-3 — Level 3

Die Zuglimit-/Mehrlevel-/Spezialkachel-Weiterentwicklung von
[`match3_2`](../match3_2/README.md), die in match3_1s ursprünglicher
Roadmap versprochen wurde — die letzte der drei geplanten
match3-Versionen. Durchgehend dieselbe Architektur: keine Skripte, das
gesamte Spiel sind weiterhin vier `execute_code`-Ereignisse auf einem
einzigen Controller-Objekt, nur jetzt in drei Räumen statt einem
platziert.

**Wo dies einzuordnen ist:** Teil der `match3_*`-Familie — reines
`execute_code`-Skript, keine eingebauten Aktionen, keine Kacheln auf
Raumebene, und schließt die in
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
beschriebene Progression ab.

**Sound & Musik:** 5 Sounddateien — die 3 aus `match3_2`
(`snd_swap`/`match`/`cascade`) plus 2 neue (`snd_special`,
`snd_level_up`), alle aktiv über `self._sound_queue` genutzt.

## Wie man spielt

Dieselben Tausch-/Übereinstimmungs-/Kaskadenregeln wie match3_1 und
match3_2, plus:

- Du hast eine **begrenzte Anzahl von Zügen** pro Level. Ein Zug wird
  nur verbraucht, wenn ein Tausch tatsächlich eine Übereinstimmung
  ergibt — ein ungültiger Tausch (der zurückrutscht) kann kostenlos
  erneut versucht werden.
- Erreiche die **Zielpunktzahl** des Levels, bevor dir die Züge
  ausgehen, um zum nächsten Raum zu gelangen. Gehen die Züge zuerst aus,
  endet das Level — **klicke irgendwo, um dasselbe Level von vorn zu
  versuchen**.
- **Passe 4 in einer Reihe zusammen** (genau 4), und eine der vier
  Kacheln wird zu einer **Linien-Löschen-Spezialkachel**: ein weißer
  Balken markiert sie. Passe sie später erneut zusammen (als Teil einer
  beliebigen anderen Übereinstimmung) und sie löscht ihre **gesamte
  Reihe oder Spalte** — je nachdem, in welcher Richtung die
  ursprüngliche 4er-Reihe verlief.
- **Passe 5 oder mehr in einer Reihe zusammen**, und eine Kachel wird
  zu einer **Farbbomben-Spezialkachel**: ein weißer Ring markiert sie.
  Passe sie später erneut zusammen und sie löscht **jede Kachel einer
  Farbe** auf dem gesamten Spielfeld.
- Es gibt **3 Level**, jedes ein eigener Raum mit höherem Ziel und
  engerem Zuglimit. Schließe Level 3 ab, um das Spiel zu gewinnen.

## Was sich von match3_2 unterscheidet

| match3_2 | match3_3 |
| -------- | -------- |
| Ein Raum, unbegrenzte Züge, Sieg bei fester Punktzahl | **3 Räume** (einer pro Level), ein **Zuglimit** pro Level, und ein **steigendes Ziel** pro Level |
| Eine Übereinstimmung wird immer vollständig zerstört | Eine Reihe von **4** oder **5+** hinterlässt eine **Spezialkachel**, statt jede Zelle zu zerstören |
| Keine Level-zu-Level-Progression | Das Erreichen des Ziels ruft `self.advance_level()` auf, das `self.goto_room_target` auf den nächsten Raum setzt (oder `self.won` beim letzten Level) |

Die Kern-Zustandsmaschine für Tausch/Blinken/Fallen/Kaskade, das
Sprite-Kachel-Zeichnen und die Sound-Warteschlangen-Trigger sind sonst
gegenüber match3_2 unverändert — siehe die README dieses Beispiels für
die vollständige Beschreibung von `swap_off`/`falling`/`find_matches`.

## Projektstruktur

| Datei | Zweck |
| ---- | ------- |
| `project.json` | Projekt-Manifest — 800×800-Fenster, 60 fps, Start-Raum `rm_level1`, `room_order` = alle 3 Level |
| `rooms/rm_level1|2|3.json` | ein Raum pro Level, jeder mit seiner eigenen Instanz von `obj_GridManager` bei (0, 0) |
| `objects/obj_GridManager.json` | das gesamte Spiel: vier Ereignisse, jedes mit einer einzigen `execute_code`-Aktion |
| `sprites/`, `sounds/` | Edelstein-Kacheln + Effekte, größtenteils aus match3_2 kopiert (siehe `CREDITS.txt`); `snd_special` und `snd_level_up` sind neu |

Es gibt weiterhin kein Pro-Kachel-Objekt und keine Skripte — eine
Controller-Instanz pro Raum, jedes Mal neu erstellt (über GameMakers
übliche Regel "jeder Raum hat seine eigenen Instanzen"), wenn ein Raum
betreten wird, was jedem Level kostenlos einen sauberen Neustart
verschafft.

## Wie der Code funktioniert

### Level-Einrichtung (neu in `create`)

```python
self.room_order = ['rm_level1', 'rm_level2', 'rm_level3']
level_config = {
    'rm_level1': (300, 20),   # (target score, move limit)
    'rm_level2': (500, 18),
    'rm_level3': (800, 16),
}
```

`create` liest `game.current_room.name`, speichert es in
`self.room_name` (nötig, weil eine einfache lokale Variable, die in
einem `execute_code`-Ereignis definiert wird, **nicht** in ein späteres
Ereignis überlebt — siehe die Landmine-Anmerkung unten), und setzt
`self.target`/`self.moves`/`self.level_num` aus der obigen Tabelle.

### Züge und Verlieren (neu in `mouse_left_press`)

Ein Tausch verbraucht nur dann einen Zug, wenn `find_matches` meldet,
dass er tatsächlich eine Übereinstimmung ergibt
(`if marks: self.moves = self.moves - 1`), sodass ein abgelehnter
Tausch, der zurückrutscht, kostenlos ist. Wenn `self.moves` 0 erreicht,
ohne das Ziel zu treffen, setzt `step` `self.lost = True`;
`mouse_left_press` prüft dieses Flag **zuerst**, vor der normalen
Eingabesperre, und verwandelt jeden Klick in
`self.restart_room_flag = True` (dasselbe Flag, das `restart_room`
verwendet), was den Raum neu aufbaut — und damit auch eine frische
`obj_GridManager`-Instanz, deren `create`-Ereignis alles zurücksetzt.

### Spezialkacheln (neu in `step`)

`find_matches` gibt jetzt `(marks, runs)` statt nur `marks` zurück —
jede Reihe ist `(cells_in_order, 'h' oder 'v')`. Beim Ablauf des
Blinkens, **vor** der Punktezählung:

1. Für jede Reihe der Länge ≥ 4 wird die **mittlere Zelle** zu einer
   Spezialkachel, statt zerstört zu werden: Reihen der Länge 4
   erhalten `('row',)` oder `('col',)` (passend zur Ausrichtung der
   Reihe); Reihen der Länge 5+ erhalten `('color', <Farbindex>)`.
2. Für jede bereits markierte Zelle, die einen Eintrag in
   `self.special` hat (d. h. eine Spezialkachel wurde gerade in *diese*
   Übereinstimmung mit einbezogen), feuert ihr Effekt einmal: eine
   `row`/`col`-Spezialkachel fügt ihre ganze Reihe/Spalte zu den zu
   löschenden Zellen hinzu; eine `color`-Spezialkachel fügt jede Zelle
   der gespeicherten Farbe auf dem Spielfeld hinzu. Dies ist ein
   **einziger, nicht-rekursiver Durchlauf** — wenn die Explosion einer
   Spezialkachel eine andere Spezialkachel erfasst, wird diese zwar
   zerstört, löst aber **nicht** ihren eigenen Effekt in Kette aus
   (eine Vereinfachung, kein Bug — hält den Effekt begrenzt und leicht
   nachvollziehbar).
3. Neu erzeugte Spezialzellen sind in derselben Welle vor Zerstörung
   geschützt, selbst wenn eine Explosion aus Schritt 2 sie erfasst hätte.
4. `self.special` wird jede Welle von Grund auf neu aufgebaut und
   folgt überlebenden Kacheln beim Fallen (die spaltenweise Fall-
   Schleife trägt jetzt ein drittes Tupel-Element — die Spezialart der
   Kachel, oder `None` — neben ihrer Reihe und Farbe), sodass eine
   noch nicht zusammengepasste Spezialkachel wie alles andere mit der
   Schwerkraft nach unten rutscht.

### Level-Fortschritt (neu in `create`, verwendet in `step`)

```python
def advance_level():
    idx = self.room_order.index(self.room_name)
    if idx + 1 < len(self.room_order):
        self.goto_room_target = self.room_order[idx + 1]
        self._sound_queue.append('snd_level_up')
    else:
        self.won = True
self.advance_level = advance_level
```

`self.goto_room_target` ist dasselbe Instanz-Flag, das die eingebaute
Aktion `goto_room` setzt — die Haupt-Spielschleife fragt es bereits
jeden Frame ab, sodass es genügt, es direkt aus `execute_code` zu
setzen, um einen echten Raumwechsel auszulösen — keine strukturierte
Aktion nötig. `step` ruft `self.advance_level()` auf, sobald
`self.score >= self.target`, und überspringt für den Rest dieses
Frames jede Kaskaden-Neuscan, wenn ein Raumwechsel (oder ein
abschließender Sieg) jetzt ansteht, damit ein verlassener Raum nicht
weiter animiert.

### Landmine: Closures über einfache Lokale überleben Ereignisse nicht

Die Ausführungsumgebung von `execute_code` übergibt **getrennte**
globals- und locals-Dicts (`exec(code, exec_globals, exec_locals)`),
was sich wie das Innere einer Funktion verhält: eine einfache
Top-Level-Zuweisung (`room_name = ...`) landet im *locals*-Dict, aber
ein auf derselben Top-Ebene definiertes `def` löst seine freien
Variablen beim späteren **Aufruf** über das *globals*-Dict auf — was
bei einer verschachtelten Hilfsfunktion, die auf `self` gespeichert ist
(wie `find_matches`, `arm_swap`, und jetzt `advance_level`), immer aus
einem **anderen** `execute_code`-Aufruf mit eigenem frischen
locals-Dict geschieht. Ein bloßes Lokal, auf das eine solche
Hilfsfunktion verweist, löst beim ersten tatsächlichen Aufruf der
Hilfsfunktion aus einem anderen Ereignis einen `NameError` aus — es
sieht im definierenden Ereignis unauffällig aus und schlägt erst später
stillschweigend fehl, sobald es ausgelöst wird. Die Lösung ist
dieselbe, die match3_1s `find_matches`/match3_2s `arm_swap` bereits
vorgelebt haben, ohne es explizit zu sagen: schließe nur über `self`
(immer in den globals jedes Ereignisses vorhanden) oder über
**Instanzattribute** (`self.room_name`, nicht ein bloßes `room_name`) —
niemals über ein bloßes Lokal. Während der Entwicklung durch den
eigenständigen Validierungs-Harness-Schritt gefunden (siehe die
Audit-Methodik-Anmerkungen im `CLAUDE.md` des Repositorys); es gibt
jetzt einen Regressionstest dafür (`tests/test_match3_3_sample.py`).

### `draw`

Dasselbe Panel-/Spielfeld-/Auswahl-/Punkte-/Sieges-Banner-Zeichnen wie
match3_2, plus: eine HUD-Zeile für Levelnummer und verbleibende Züge,
ein weißer Balken- oder Ring-Overlay über dem Sprite einer
Spezialkachel (übersprungen während die Kachel mitten im Blinken ist),
und ein "OUT OF MOVES — click to retry"-Banner, wenn `self.lost`.

### Zum Experimentieren

- Schwierigkeit pro Level: die `level_config`-Tabelle in `create`
  (Zielpunktzahl, Zuglimit) — füge einen vierten Eintrag und einen
  vierten Raum hinzu, um die Sequenz zu erweitern.
- Explosionsradius der Spezialkacheln: die `row`/`col`/`color`-Zweige
  in der Aktivierungsschleife von `step`.
- Alles, was match3_2 bereits offengelegt hat (Spielfeldgröße,
  Tausch-/Fallgeschwindigkeit, Lautstärken).

## Roadmap

Dies schließt match3_1s ursprüngliche dreiteilige Roadmap ab
(match3_1 → match3_2 → match3_3). Keine weiteren geplanten Versionen.

## Export-Status

- **Test Game (F5) / Desktop:** funktioniert — end-to-end mit einem
  echten `GameRunner`-Lauf verifiziert, der einen tatsächlichen
  Mausklick über den Standard-pygame-Ereignispfad einspeist: erzwungene
  4er-Reihen-Übereinstimmung → Spezialkachel erzeugt → Ziel erreicht →
  **der Raum wechselte tatsächlich zu `rm_level2`** mit einer frischen
  Instanz (`level_num == 2`, zurückgesetzte Punkte/Züge).
- **Android (.apk) / Mobil (Kivy):** verlässt sich auf dieselbe
  `asset_paths.py`/`_drain_sound_queue`/Sprite-nach-Name-Fallback-
  Maschinerie, die match3_2 hinzugefügt und verifiziert hat — dieses
  Beispiel prüft in dieser Hinsicht nichts Neues (keine neuen
  Zeichenbefehlstypen, keine neuen Aktionstypen; `goto_room` über Flag
  funktioniert in der exportierten Kivy-Szenenschleife identisch, die
  bereits dieselben Instanz-Flags jeden Frame abfragt). Der eigentliche
  `.apk`-Build erfordert zusätzlich buildozer (via WSL unter Windows) —
  siehe [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Web (HTML5):** dieselbe Begründung — keine neuen Zeichen-
  Warteschlangen- oder Sound-Warteschlangen-Primitiven über das hinaus,
  was match3_2 auf diesem Ziel bereits bewiesen hat.
- **Eigenständiges Zip:** mit diesem Beispiel ungetestet.
