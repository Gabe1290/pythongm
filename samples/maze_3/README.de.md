# Labyrinth — Level 3

Ein Fünf-Labyrinth-Dungeon-Crawl auf einem Gitter mit vorangestelltem
Titelbildschirm — das größte der drei Labyrinth-Beispiele (17 Objekte /
6 Räume, gegenüber 9 Objekten / 3 Räumen bei maze_2). Es behält
maze_2s Sammle-Diamanten-dann-erreiche-das-Ziel-Schleife und die
diamantengesperrte, verschlossene Tür bei und fügt drei neue Mechaniken
hinzu, die progressiv über die Räume hinweg auftauchen: ein
Kiste-in-Loch-schieben-Rätsel (room5), drei Patrouillenmonster-
Archetypen, die bei Berührung töten (rooms 3–5), und eine versteckte
Bombenfalle, die einen Explosionsradius auslöst (room4). Anders als
`maze_1`/`maze_2` **ist** dieses Beispiel ein roher GameMaker-8.x-
Import — seine begleitende `samples/maze_3.gmk` ist im Repository
eingecheckt (für `maze_1`/`maze_2` existiert keine `.gmk`-Datei), und
das daneben liegende pygm2-Projekt ist das konvertierte Ergebnis.

**Wo dies einzuordnen ist:** Teil der `maze_*`-Familie — GameObjects +
Sprites plus ein statisches **Hintergrundbild** pro Raum (wie `maze_2`),
keine Kacheln auf Raumebene. Siehe
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
für den Vergleich mit `plateforme_*` (fügt gekachelte Hintergründe
hinzu) und `match3_*` (reines Skript, keine eingebauten Aktionen).

**Sound & Musik:** 8 Sounddateien, und — anders als bei `maze_2`s
mitgeliefertem, aber stummem Satz — tatsächlich verdrahtet: 11
`play_sound`/`play_music`-Aufrufstellen über `sound_background`
(Musik), `sound_diamond`, `sound_door`, `sound_goal`, `sound_dead`,
`sound_explode`, `sound_hole` und `sound_push`.

## Wie man spielt

- **Titelbildschirm (`room_start`):** drücke **LEERTASTE**, um zu starten.
- **Pfeiltasten** bewegen den Spieler jeweils um eine 32px-Gitterzelle
  (`test_alignment`/`snap_to_grid`, dasselbe Muster wie `maze_1`/`maze_2`).
- **Ziel:** sammle Diamanten (`obj_diamond`, je +5 Punkte) und erreiche
  das `obj_goal` jedes Raumes. Die Räume 2–4 sperren den Ausgang
  zusätzlich hinter einer verschlossenen `obj_door`, die sich erst
  selbst zerstört, sobald jeder Diamant in diesem Raum weg ist (room3
  hat 4 Türen, die sich alle zusammen öffnen). Room5 tauscht Diamanten
  gegen ein Kiste-schieben-Rätsel: laufe in einen `obj_block`, um ihn
  eine Zelle weiterzuschieben, oder schiebe ihn in ein `obj_hole`, um
  die Grube zu füllen (beide werden zerstört).
- **Gefahren:** drei Monster-Archetypen patrouillieren in den Räumen
  3–5 und töten bei Kontakt — `monster_all` prallt in beliebiger von 4
  Richtungen von Wänden ab, `monster_lr`/`monster_ud` patrouillieren
  auf einer einzelnen Achse und drehen bei einem Wandtreffer um. Room4
  versteckt außerdem eine `obj trigger`-Platte, die, einmal berührt,
  eine nahe `obj_bomb` in eine `obj_explosion` verwandelt — deren
  16-Frame-Explosion zerstört jede nicht-feste Instanz (einschließlich
  des Spielers) in einem Radius von 64px.
- **Verlust-Bedingung:** ein Monster zu berühren kostet ein Leben
  (`sound_dead` + `set_lives -1` + `restart_room`); bei 0 Leben
  erscheint der Highscore-Eingabebildschirm und das Spiel startet neu.
  Das Berühren des Ziels im letzten Raum zeigt stattdessen eine
  Glückwunsch-Nachricht, vergibt +100 und beendet den Durchlauf auf
  dieselbe Weise.
- **Debug-Tasten** befinden sich auf `controller_main`: **R** kostet
  sofort ein Leben und startet den Raum neu; **N**/**P** springen
  direkt zum nächsten/vorherigen Raum — nützlich zum Testen, aber auch
  ein Level-Skip, in den ein Spieler versehentlich hineinstolpern könnte.

## Projektstruktur

| Datei | Zweck |
|---|---|
| `project.json` | Projekt-Manifest — Fenster-/Raumeinstellungen und eingebettete Asset-Kopien. Objektkopien stimmen exakt mit ihren Nebendateien überein, aber **Raumkopien sind veraltet**: jeder eingebettete Raumeintrag hat 0 Instanzen und einen `_external_file`-Marker — die echten Instanzdaten leben nur in `rooms/*.json` |
| `rooms/room_start.json` | Titelbildschirm — 1 Instanz (`controller_start`) |
| `rooms/room1.json` | Labyrinth 1 — 134 Instanzen (Wände, 4 Diamanten, Ziel, Spieler, Controller) |
| `rooms/room2.json` | Labyrinth 2 — 96 Instanzen (+20 Diamanten, 1 verschlossene Tür) |
| `rooms/room3.json` | Labyrinth 3 — 105 Instanzen (+16 Diamanten, 4 verschlossene Türen, alle 3 Monster-Archetypen, 6 Monster insgesamt) |
| `rooms/room4.json` | Labyrinth 4 — 95 Instanzen (+14 Diamanten, 1 Tür, 4 `monster_lr`, 2 Trigger-/Bomben-Paare) |
| `rooms/room5.json` | Labyrinth 5 — 99 Instanzen (4 schiebbare Kisten, 3 Löcher, 2 Ziele, 2 `monster_lr` — keine Diamanten oder Tür) |
| `objects/*.json` | 17 Objektdefinitionen — gegen die eingebetteten Kopien in `project.json` geprüft und identisch (keine Veralterung). Hinweis: `objects/obj trigger.json` hat ein Leerzeichen im Dateinamen |
| `sprites/` | 16 Sprites + Metadaten (siehe Assets) |
| `sounds/` | 8 Sounddateien, alle von mindestens einem Objekt referenziert |
| `backgrounds/` | 2 Hintergründe (`background_start.png` für den Titelraum, `background_main.png` für die Labyrinthe) |
| `CREDITS.txt` | Lizenzhinweis für die Assets dieses Beispiels |

## Objekte

**Spieler & Controller**

| Objekt | Rolle | Wichtige Ereignisse |
|---|---|---|
| `obj_person` | Vom Spieler gesteuerte Figur; Gitterbewegung | keyboard (up/down/left/right/nokey), collision_with_obj_block, collision_with_monster_all/_lr/_ud, collision_with_wall_corner |
| `controller_start` | Titelbildschirm-Controller; setzt Punkte/Leben, startet die Musik | create, keyboard (LEERTASTE) |
| `controller_main` | In-Labyrinth-HUD + Debug-Tasten; zeichnet Punkte/Leben, beendet den Durchlauf bei 0 Leben | keyboard (R Neustart-Cheat), no_more_lives, draw, keyboard_press (N/P Raum-Skip) |

**Wände & Kacheln**

| Objekt | Rolle | Wichtige Ereignisse |
|---|---|---|
| `wall_corner` | Grundlegende feste Wand; Eltern der beiden anderen Wandtypen | (keine — passiver Kollisionskörper) |
| `wall_horizontal` | Horizontales Wandsegment (erbt `wall_corner`) | (keine) |
| `wall_vertical` | Vertikales Wandsegment (erbt `wall_corner`) | (keine) |

**Sammelobjekte, Türen, Ziele & Schiebekisten-Rätsel (room5)**

| Objekt | Rolle | Wichtige Ereignisse |
|---|---|---|
| `obj_diamond` | Sammelobjekt; +5 Punkte beim Aufheben | destroy, collision_with_obj_person |
| `obj_door` | Verschlossenes Tor; zerstört sich selbst, sobald jeder Diamant im Raum weg ist | step |
| `obj_goal` | Levelausgang; führt zu weiteren Räumen oder beendet das Spiel im letzten Raum | collision_with_obj_person |
| `obj_block` | Schiebbare Kiste; rutscht eine Zelle weiter, wenn man hineinläuft, oder fällt in ein Loch | collision_with_obj_person |
| `obj_hole` | Grube; zerstört sich selbst und jede hineingeschobene Kiste | collision_with_obj_block |

**Monster & Bombenfalle (room4)**

| Objekt | Rolle | Wichtige Ereignisse |
|---|---|---|
| `monster_all` | Prallt in beliebiger von 4 Richtungen von Wänden ab | create, collision_with_wall_corner |
| `monster_lr` | Patrouilliert links-rechts, dreht bei Wandkontakt um | create, collision_with_wall_corner |
| `monster_ud` | Patrouilliert hoch-runter, dreht bei Wandkontakt um | create, collision_with_wall_corner |
| `obj trigger` | Versteckte Platte; spielt bei Berührung den Explosionssound, verwandelt die gepaarte `obj_bomb` in `obj_explosion`, zerstört sich selbst | collision_with_obj_person |
| `obj_bomb` | Inerter Platzhalter, der eine scharfe Bombe darstellt, bis ein Trigger auslöst | (keine) |
| `obj_explosion` | 16-Frame-Explosion; zerstört beim Erscheinen nicht-feste Instanzen innerhalb von 64px, zerstört sich selbst am Ende der Animation | create, animation_end |

## Assets

16 Sprites (meist 32×32, ein Frame, pixelgenau; `sprite_explosion` ist
ein 1536×96-16-Frame-Streifen ohne `precise`-Flag), 2 Hintergründe, 8
Sounds — alle 8 Sounds werden von mindestens einem Objekt referenziert,
anders als bei `maze_2`, wo keiner verdrahtet war. Lizenz/Herkunft für
die Assets dieses Beispiels ist **nicht dokumentiert** — siehe
`CREDITS.txt` in diesem Ordner, das auf das "Remaining maze assets"-
TODO in `docs/ASSET_LICENSES.md` verweist. Nimm für diese Dateien keine
CC0- oder andere Lizenz an.

## Zum Experimentieren

- `sprite_lives` (16×16) ist ein registriertes Asset, das nie
  gezeichnet wird — die `draw_lives`-Aktion von `controller_main`
  verwendet tatsächlich `sprite_person` bei 0,7-facher Skalierung,
  wodurch `sprite_lives` verwaist zurückbleibt (dieselbe Kategorie wie
  `maze_2`s `tiles.json`).
- Die Explosion der Bombenfalle (das `create`-Ereignis von
  `obj_explosion`) zerstört den Spieler über ein einfaches
  `destroy_instance` in ihrer Radiusprüfung und umgeht dabei den
  `sound_dead`/`set_lives`/`restart_room`-Pfad, den Monster verwenden —
  vom Spieler erfasst zu werden, hinterlässt den Durchlauf in einem
  seltsamen Zustand statt eines sauberen Todes/Neustarts.
- Die Monstergeschwindigkeit ist bei allen drei Archetypen fest auf
  `32/6` px/Schritt codiert, während der Spieler sich mit `4` bewegt —
  Monster sind nicht wie der Spieler gitterausgerichtet, sodass ihre
  Bewegung über die Zeit nicht zellenausgerichtet bleibt.
- Die `R`/`N`/`P`-Debug-Tasten auf `controller_main` sind im
  ausgelieferten Controller aktiv (siehe Wie man spielt) — es würde
  sich lohnen, sie hinter ein Debug-Flag zu setzen, falls dieses
  Beispiel weiter poliert wird.

## Export-Status

Abgedeckt durch die Headless-Smoke-Test-Suite
(`tools/smoke_run_samples.py`, die `maze_3` auflistet und es für eine
feste Anzahl von Frames mit simulierten Tastatureingaben laufen
lässt); nicht einzeln pro Export-Ziel (Kivy/Web) erneut verifiziert.
Im Willkommens-Tab der IDE als "Maze — Level 3" angezeigt
(`widgets/welcome_tab.py`).
