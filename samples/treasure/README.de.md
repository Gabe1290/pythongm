# Treasure

Eine Labyrinth-Verfolgungsjagd im Pac-Man-Stil: der **Entdecker**
durchstreift ein von Mauern umgebenes Labyrinth und sammelt
**Schatzpunkte**, verfolgt von **Monstern**, die an jeder Kreuzung eine
neue Richtung wählen. Schnapp dir eine **Kraftpille** (`pil`), und das
Blatt wendet sich — jedes Monster wird **verängstigt** und kann für
Bonuspunkte gefressen werden, bis der Effekt nachlässt. Dies ist ein
natives pygm2-Projekt, importiert aus `treasure.gmk` (GameMaker 8.x);
das Projekt selbst ist im eigenen JSON-Format von pygm2
geschrieben/gespeichert.

**Wo dies einzuordnen ist:** `treasure` steht neben der
`maze_*`-Familie — gebaut aus GameObjects + eingebauten Aktionen und
dem visuellen Ereignis-Editor — fügt aber ein **Projekt-Skript**
hinzu (`adapt_direction`, die Kreuzungs-KI der Monster) und eine
GM-artige **"Verfolgen/Power-up/Fliehen"**-Zustandsschleife über seine
Objekte hinweg. Es war eines der beiden Beispiele, die in rc.12 wegen
GMK-Import-Bugs entfernt und **nach der Härtung des Importers wieder
hinzugefügt** wurden (16.07.2026); siehe
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
und [`../../docs/treasure_testing_pass.md`](../../docs/treasure_testing_pass.md).

**Sound & Musik:** 6 Soundeffekte liegen bei (Aufnahme, Kraftpille,
Monster-fressen, Tod, …). Ein Legacy-Track aus der GM8-Ära (`music`)
liegt in einem Format vor, das pygame nicht laden kann, und wird zur
Laufzeit übersprungen — genau wie die Hintergrundmusik der anderen
Labyrinth-Beispiele; das Gameplay ist davon nicht betroffen.

## Wie man spielt

- **Pfeiltasten** bewegen den Entdecker durch das Labyrinth; Wände
  blockieren die Bewegung.
- Sammle jeden **Schatzpunkt**, um das Level abzuschließen (4 Räume
  insgesamt).
- **Monster** jagen dich; eines zu berühren kostet normalerweise ein Leben.
- Schnapp dir eine **Kraftpille**, und Monster werden für einige
  Sekunden **verängstigt** (sie ändern ihr Sprite) — berühre ein
  verängstigtes Monster, um es **zu fressen** (+Punkte; es
  teleportiert sich zurück zu seinem Startpunkt als normales Monster).
  Der Effekt kehrt sich nach einem Timer um.

## Die Monster-KI (`adapt_direction`-Skript)

Jedes Monster ruft das Projekt-Skript `adapt_direction` aus seinen
Step-/Kollisions-Ereignissen auf. Es ist echtes pygm2-Python — an einer
möglichen Kreuzung erwägt es zufällig ein Abbiegen und prüft
`game.check_collision_at_position(...)` auf eine Wand, bevor es sich
festlegt, sodass Monster durch das Labyrinth wandern statt in
geraden Linien zu laufen. Öffne die **Scripts**-Ressource, um es zu
lesen; die `execute_script`-Aktion in den Ereignissen des Monsters
zeigt, wo es aufgerufen wird.

## Projektstruktur

| Datei | Zweck |
|---|---|
| `project.json` | Manifest — Fenster-/Raumeinstellungen, eingebettete Assets, das `adapt_direction`-Skript und die Raumreihenfolge |
| `rooms/room0..3.json` | Die vier Labyrinth-Level (Instanzen pro Raum) |
| `objects/*.json` | Die 7 Objektdefinitionen (maßgebliche Quelle; beim Laden über die eingebetteten Kopien gemergt) |
| `sprites/` | 10 Sprite-PNGs + `.json`-Metadaten |
| `sounds/` | 6 Soundeffekte |
| `backgrounds/` | 1 Hintergrund |
| `CREDITS.txt` | Lizenzhinweis für die Assets |

## Objekte

| Objekt | Rolle |
|---|---|
| `explorer` | Spielercharakter; sammelt Schätze, frisst verängstigte Monster, stirbt an normalen |
| `monster` | Verfolger; wandert über `adapt_direction`; verwandelt sich bei einer Kraftpille in `scared` |
| `scared` | Ein Monster in seinem Flucht-Zustand; essbar; kehrt nach einem Timer zu `monster` zurück |
| `pil` | Kraftpille — verängstigt jedes Monster, wenn eingesammelt |
| `point` | Zu sammelnder Schatz |
| `bonus` | Zusätzliches Sammelobjekt |
| `wall` | Statische feste Labyrinthwand |

## Assets

10 Sprites, 6 Sounds, 1 Hintergrund — alle aus `treasure.gmk`
importiert. Siehe `CREDITS.txt` und
[`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md) für die Herkunft.

## Zum Experimentieren

- **Verängstigungsdauer** — der Kraftpillen-Alarm ist `160` Schritte
  im `collision_with_pil`-Ereignis von `explorer`; erhöhe ihn für eine
  längere Flucht-Phase.
- **Monster-Abbiege-Wahrscheinlichkeit** — die
  `random.random() * 3 < 1`-Tests im `adapt_direction`-Skript legen
  fest, wie oft Monster an einer Kreuzung abbiegen.
- **Punktewerte** — Schatz- und Monster-fressen-Punkte sind
  `set_score`-Aktionen (relativ) auf den jeweiligen
  Kollisionsereignissen.

## Export-Status

Abgedeckt durch die Headless-Smoke-Test-Suite
(`tools/smoke_run_samples.py`, die `treasure` auflistet) und die
Import-Regressions-Suite (`tests/test_gmk_treasure_maze4_import.py` +
`tests/test_gmk_applies_to.py`). Verifiziert in einem manuellen
Playtest während der Importer-Härtung im Juli 2026 (siehe das
Testing-Pass-Dokument). Im Willkommens-Tab als **"Treasure"** angezeigt.

## Neugenerierung aus dem `.gmk`-Original

Die begleitende `../treasure.gmk` ist die GameMaker-8.x-Quelle. Zum
Neugenerieren:

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/treasure.gmk', '/tmp/treasure_reimport')"
```

Ein frischer Import ist originalgetreu zum Originalspiel seit der
Importer-Härtung im Juli 2026 (keine Hand-Patches auf dieses Beispiel
angewendet).
