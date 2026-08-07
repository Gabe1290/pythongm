# Platform — Level 3

Ein seitwärts scrollender Plattformer, importiert aus GameMaker 8.x
(`samples/plateforme_3.gmk`). Es ist mit Abstand das größte der drei
Plattform-Beispiele: 2 Objekte (plateforme_1) → 4 Objekte
(plateforme_2) → **15 Objekte** hier, mit patrouillierenden Boden- und
Flugmonstern (mit Zertreten-zum-Töten und zur Laufzeit erzeugten
Leichen-/Splat-Varianten), einer unsichtbaren Sofort-Tod-Gefahr, zwei
Sammelobjekt-Typen und einem Ausgangsobjekt, das zum nächsten Raum
führt oder die Highscore-Tabelle zeigt und neu startet.

**Wo dies einzuordnen ist:** Teil der `plateforme_*`-Familie — wie
`plateforme_2` verwendet es einen **gekachelten Hintergrund** (125
Kachel-Stücke unter den festen Ziegel-Objekten, plus das
`fond_degrade`-Verlaufsbild), der Schritt, den diese Familie über
`maze_*` hinaus hinzufügt. Siehe
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
für die vollständige Progression.

**Sound & Musik:** 4 Sounddateien, tatsächlich verdrahtet: 7
`play_sound`-Aufrufstellen für `son_bonus` (Aufnahme),
`son_monstre_mort` (Zertreten-Kill), `son_personnage_mort`
(Spielertod) und `son_niveaufini` (Level abgeschlossen).

## Wie man spielt

- **Pfeil links/rechts** — bewegt Pingus (`obj_pingus`) links/rechts.
- **Pfeil hoch** — Sprung, aber nur während der Spieler auf etwas
  Festem steht (geprüft ein Pixel unterhalb des Spielers).
- **Ziel** — sammle `obj_bonus` (+5 Punkte) und `obj_power` (+20
  Punkte) Gegenstände beim Durchqueren von `niveau_01`, um `obj_sortie`
  zu erreichen; das Berühren spielt einen Jingle und führt entweder zum
  nächsten Raum (keiner existiert in diesem Beispiel, daher fällt es
  auf den Highscore-/Neustart-Zweig zurück) oder zeigt die
  Highscore-Tabelle und startet das Spiel neu.
- **Monster** — auf einem `obj_monstre` oder `obj_monstre_volant`
  landen (`vspeed > 0` und über dem Monster) tötet es und bringt 50
  Punkte; eines von der Seite oder von unten zu treffen kostet ein
  Leben und startet den Raum neu. Hinweis: die Kollision mit
  `obj_monstre_volant` ist wirkungslos (das Flugmonster kann weder
  verletzen noch verletzt werden), bis `obj_power` eingesammelt wurde —
  siehe Zum Experimentieren.
- **Verlust-Bedingung** — `obj_mortel` (eine unsichtbare
  Sofort-Tod-Zone) oder ein Monster auf die falsche Weise zu berühren
  kostet ein Leben und startet den Raum neu; wenn die Leben ausgehen
  (`no_more_lives`), erscheint die Highscore-Tabelle und das gesamte
  Spiel startet neu. Start-Leben: 3 (`project.json`-Einstellungen).

## Projektstruktur

| Datei | Zweck |
| --- | --- |
| `project.json` | Projekt-Manifest — Fenster-/Raumeinstellungen, eingebettete Asset-Kopien. |
| `rooms/niveau_01.json` | Der eine Raum: 800×640, 194 Instanzen + 125 Hintergrundkacheln. Maßgebliche Quelle für den Rauminhalt (`project.json`s eingebettete `instances`-Liste ist leer, dasselbe Muster wie plateforme_2). |
| `objects/*.json` | Pro-Objekt-Nebendateien für alle 15 Objekte; identisch mit den eingebetteten Kopien in `project.json` zum Zeitpunkt dieser Erstellung (byte-für-byte verifiziert, anders als plateforme_2s Raumdatei). |
| `sprites/` | 18 Sprite-Assets (Lauf-/Flug-Streifen, Tod-Sprites, Plattformblöcke, Sammelobjekte, Ausgang, Marker). |
| `sounds/` | 4 Soundeffekte (Monstertod, Spielertod, Bonus-Aufnahme, Level abgeschlossen). |
| `backgrounds/` | Schnee-Kachelsatz (`tuiles_neige.png`, Autotile-Quelle für die 125 Raumkacheln) und ein vertikaler Verlauf (`fond_degrade.png`) als Raumhintergrund. |
| `CREDITS.txt` | Lizenzhinweis für die Sprite-/Hintergrundgrafik (siehe Assets unten). |

## Objekte

15 Objekte, nach Rolle gruppiert. Raumplatzierungs-Anzahlen (von 194
Instanzen) sind gezeigt, wo das Objekt in `niveau_01` erscheint;
"zur Laufzeit erzeugte" Objekte erscheinen nur über `change_instance`
während des Spiels.

| Objekt | Rolle | Wichtige Ereignisse |
| --- | --- | --- |
| `obj_pingus` | Spieler — Bewegung, Sprung, Schwerkraft, gesamte Kollisions-/Verlust-/Sieg-Behandlung | create, step, keyboard (left/right/up), keyboard_release, collision_with_obj_brique/obj_monstre/obj_monstre_volant/obj_mortel/obj_bonus/obj_power/obj_sortie/obj_marqueur, game_start, no_more_lives |
| `obj_brique` | Basis-feste Plattform-Block, 32×32 (109 platziert) | keine (nur Solid-Flag) |
| `obj_brique_h` | Breite Plattform-Variante, 32×16, Kind von `obj_brique` (15 platziert) | keine |
| `obj_brique_v` | Schmale Plattform-Variante, 16×32, Kind von `obj_brique`; definiert, aber nicht in `niveau_01` platziert | keine |
| `obj_brique_c` | Kleine Plattform-Variante, 16×16, Kind von `obj_brique` (1 platziert) | keine |
| `obj_monstre` | Bodenmonster — patrouilliert links/rechts, dreht bei Wandkontakt um (3 platziert) | create, collision_with_obj_brique |
| `obj_monstre_mort` | Zur Laufzeit erzeugte Monsterleiche nach einem Zertreten-Kill; erbt von `obj_brique` (wird zu einer festen Stufe) | create |
| `obj_monstre_volant` | Flugmonster — patrouilliert nach rechts, prallt von Wänden ab (2 platziert) | create, collision_with_obj_brique |
| `obj_monstre_volant_mort` | Zur Laufzeit erzeugte Flugmonster-Leiche; fällt mit begrenzter Schwerkraft, landet auf Plattformen/Markern | step, collision_with_obj_brique, collision_with_obj_marqueur |
| `obj_mortel` | Unsichtbare Sofort-Tod-Gefahrenzone (4 platziert) | keine (behandelt im Kollisionsereignis von `obj_pingus`) |
| `obj_splat` | Zur Laufzeit erzeugte Spielertod-Animation, startet den Raum am Ende der Animation neu | create, animation_end |
| `obj_bonus` | Kleines Sammelobjekt, +5 Punkte, zufälliger Ruhe-Frame (52 platziert) | create |
| `obj_power` | Großes Sammelobjekt, +20 Punkte; bestimmt auch, ob Flugmonster verletzen/getötet werden können (1 platziert) | create |
| `obj_sortie` | Levelausgang — spielt einen Jingle, dann nächster Raum oder Highscore + Neustart (1 platziert) | keine (behandelt im Kollisionsereignis von `obj_pingus`) |
| `obj_marqueur` | Unsichtbarer, nicht fester Raumdesign-Marker; Kollisionen sind explizit wirkungslos (5 platziert) | keine |

## Assets

18 Sprites, 4 Sounds, 2 Hintergründe. Sprite-/Hintergrundgrafik ist vom
Pingus-Projekt (GPL-3.0-or-later) adaptiert — siehe `CREDITS.txt` für
die vollständige Zuschreibung und Lizenzbedingungen; diese README
wiederholt oder erweitert diese Angaben nicht.

## Zum Experimentieren

- Der Zertreten-Test zwischen `obj_pingus` und
  `obj_monstre`/`obj_monstre_volant` war früher
  `vspeed > 0 and y < other.y+8`, was ein schneller Fall überschreiten
  konnte (das 8px-Fenster wurde gegen die Position *nach* der Bewegung
  geprüft) und ein Leben kostete bei etwas, das wie ein sauberes
  Zertreten aussah. Jetzt ist es
  `vspeed > 0 and y - vspeed < other.y+8`, was das Fenster stattdessen
  gegen die Position *vor* der Bewegung prüft.
- Das `obj_power`-Sammelobjekt gattert stillschweigend jede Interaktion
  mit `obj_monstre_volant` (über ein
  `if_object_exists(obj_power, not_flag=true)` um die Zertreten-/Tod-
  Logik in `obj_pingus`) — es würde sich lohnen, dies für Spieler
  sichtbar zu machen (z. B. ein Sprite-/Farbwechsel) statt einer
  unsichtbaren Regel.
- Die horizontale Spielergeschwindigkeit ist ein fester `hspeed = 4`;
  der Sprungimpuls ist `vspeed = -10`; die Fallschwerkraft ist `0,5`
  mit einer Endgeschwindigkeitsbegrenzung bei `vspeed = 24`.
- Die Raumgröße ist 800×640 bei `room_speed = 30`.

## Export-Status

Dieses Beispiel ist in der `SAMPLES`-Liste von
`tools/smoke_run_samples.py` aufgeführt, sodass es bei jedem Lauf
dieses Harness einen Headless-Smoke-Durchlauf erhält (die echte
Spielschleife läuft für ~180 Frames mit simulierten
Tastatureingaben). Es wurde keine spezifische Verifikation pro
Export-Ziel (Kivy/HTML5) für dieses Beispiel durchgeführt. Im
Willkommens-Tab der IDE als "Platform — Level 3" angezeigt
(`widgets/welcome_tab.py`).
