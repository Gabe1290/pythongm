# Labyrinth — Level 4

Das größte Labyrinth-Beispiel: **21 Räume** mit Gitter-Labyrinth-
Rätseln mit **Förderband-Kacheln**, drei Arten von **Monstern**,
**Bomben/Explosionen**, die durch Wände sprengen, einem **Machtring**,
der die Monster verängstigt, und Sammelobjekten (Diamanten, Ringen,
Herzen). Ein natives pygm2-Projekt, importiert aus `maze_4.gmk`
(GameMaker 8.x), im eigenen JSON-Format von pygm2 geschrieben/gespeichert.

**Wo dies einzuordnen ist:** das vierte `maze_*`-Level und das
mechanisch reichhaltigste — es schichtet Förderband-Bewegung, mehrere
Gegnertypen, eine Verängstigen-und-Fressen-Power-up-Schleife und eine
zerstörbare-Wand-Bombe auf die grundlegende Gitterbewegung von
`maze_1..3`. Es wurde in rc.12 wegen GMK-Import-Bugs entfernt und
**nach der Härtung des Importers wieder hinzugefügt** (16.07.2026);
siehe
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
und [`../../docs/maze_4_testing_pass.md`](../../docs/maze_4_testing_pass.md).

**Sound & Musik:** 10 Soundeffekte liegen bei. Ein Legacy-Track aus der
GM8-Ära (`sound_background`) liegt in einem Format vor, das pygame
nicht laden kann, und wird zur Laufzeit übersprungen (wie bei maze_2/
maze_3); das Gameplay ist davon nicht betroffen.

## Wie man spielt

- **Pfeiltasten** bewegen den Spieler jeweils um eine Gitterzelle;
  Wände blockieren die Bewegung.
- **Förderband-Kacheln** (Pfeile hoch/runter/links/rechts auf dem
  Boden) tragen den Spieler automatisch in ihre Richtung, solange er
  darauf steht.
- **Monster** gibt es in drei Arten (`monster_all` streift frei umher;
  `monster_ud` patrouilliert vertikal; `monster_lr` horizontal) —
  eines zu berühren kostet ein Leben und startet den Raum neu.
- Schnapp dir einen **Ring**, und jedes Monster wird für ~10 Sekunden
  **verängstigt** (Sprite ändert sich, sie erstarren) — berühre eines
  dann, um es für Punkte zu fressen; sie kehren zurück, wenn der Timer
  abläuft.
- **Bomben** explodieren in einer Druckwelle, die **die umgebenden
  Wände zerstört** — genutzt, um sonst versiegelte Abschnitte zu öffnen.
- Sammle **Diamanten/Ringe/Herzen**; erreiche das **Ziel**, um
  weiterzukommen. Das HUD (Punkte + Leben) wird unten von
  `controller_main` gezeichnet.

## Eine Anmerkung zum Hand-Patch (ehrliche Dokumentation)

pygm2s Bewegung *rutscht bis zum Kontakt* mit einer Wand, während
GameMaker 8 einen blockierten Zug *rückgängig macht* und zur
Position vor dem Zug zurückkehrt — das GM-Verhalten hielt den Spieler
kostenlos gitterausgerichtet. Ohne dies ließ das Hineindrücken in eine
bündige Wand den Spieler ein paar Pixel neben dem 32er-Gitter zurück,
und die gitterabhängigen Bewegungs-/Förderband-Prüfungen verklemmten
sich dann. Daher trägt `obj_person` einen bewussten
**Gameplay-Hand-Patch**: `snap_to_grid(32)` bei seinen
`wall_corner`/`wall_horizontal`/`wall_vertical`-Kollisionsereignissen.
Dies spiegelt denselben Patch, der auch in `maze_1` ausgeliefert wird,
und ist eine Korrektur, keine Treue-Änderung — ein frischer Import aus
der `.gmk` wird ihn nicht enthalten (siehe unten).

## Projektstruktur

| Datei | Zweck |
|---|---|
| `project.json` | Manifest — Fenster-/Raumeinstellungen, eingebettete Assets und Raumreihenfolge |
| `rooms/*.json` | 21 Räume; Spielreihenfolge `room_start` dann absteigende Läufe (`room14`, `room13`, …) — die eigene Reihenfolge des Originalspiels, originalgetreu importiert |
| `objects/*.json` | 24 Objektdefinitionen (maßgebliche Quelle; beim Laden über die eingebetteten Kopien gemergt) |
| `sprites/` | 24 Sprite-PNGs + `.json`-Metadaten |
| `sounds/` | 10 Soundeffekte |
| `backgrounds/` | 2 Hintergründe |
| `CREDITS.txt` | Lizenzhinweis für die Assets |

## Objekte (24)

Spieler/HUD: `obj_person`, `controller_main` (zeichnet Punkte+Leben),
`controller_start`.
Wände: `wall_horizontal`, `wall_vertical`, `wall_corner`, `block`.
Gegner: `monster_all`, `monster_ud`, `monster_lr`.
Power-ups / Gegenstände: `ring` (verängstigt), `bomb` + `explosion`
(zerstören Wände), `obj_diamond`, `heart`, `bonus`, `obj_door`,
`obj_goal`, `trigger`, `hole`.
Förderband-Kacheln: `move_up`, `move_down`, `move_left`, `move_right`.

## Assets

24 Sprites, 10 Sounds, 2 Hintergründe, 1 Schriftart — alle aus
`maze_4.gmk` importiert. Siehe `CREDITS.txt` und
[`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md) für die Herkunft.

## Zum Experimentieren

- **Förderband-/Spielergeschwindigkeit** — Förderbänder bewegen sich
  mit Geschwindigkeit `8`; die Tastatur-Gitterbewegung mit `4`
  (Pro-Aktion-Parameter auf `obj_person`).
- **Verängstigungsdauer** — der `set_alarm` des Rings ist `300`
  Schritte auf `monster_all`.
- **Raumreihenfolge** — Räume spielen in der Schlüsselreihenfolge des
  Raum-Dicts von `project.json`; ordne sie in der IDE neu an (Ziehen im
  Ressourcenbaum), und Test Game folgt.

## Export-Status

Abgedeckt durch die Headless-Smoke-Test-Suite
(`tools/smoke_run_samples.py`, die `maze_4` auflistet) und die
Import-Regressions-Suite (`tests/test_gmk_treasure_maze4_import.py`).
Verifiziert in einem manuellen Playtest während der
Importer-Härtung im Juli 2026 (siehe das Testing-Pass-Dokument). Im
Willkommens-Tab als **"Maze — Level 4"** angezeigt.

## Neugenerierung aus dem `.gmk`-Original

Die begleitende `../maze_4.gmk` ist die GameMaker-8.x-Quelle:

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/maze_4.gmk', '/tmp/maze_4_reimport')"
```

Ein frischer Import ist originalgetreu zum Originalspiel, **abzüglich**
des oben beschriebenen `snap_to_grid`-Wand-Hand-Patches — wende ihn nach
der Neugenerierung erneut an (füge `snap_to_grid` mit `grid_size` 32 zu
den drei Wand-Kollisionsereignissen von `obj_person` hinzu).
