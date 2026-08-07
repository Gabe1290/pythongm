# Views — Level 1

Eine Kamera-Scrolling-Demo: der Raum (2400×800) ist **dreimal so
breit wie das 800×600-Fenster**, sodass ein einzelner Bildschirm nicht
alles zeigen kann. Die Kamera (View 0) folgt dem Spieler, während er
nach rechts läuft, und enthüllt das Level bildschirmweise — der ganze
Sinn von GameMaker-artigen **Views**. Erkunde den breiten Raum und
sammle alle 18 Münzen.

**Wo dies einzuordnen ist:** dies ist die vierte Beispielfamilie,
verschieden von den drei nach Erstellungstechnik geordneten Familien
(`maze_*` → `plateforme_*` → `match3_*`). Was sie einführt, ist kein
neuer Erstellungs-*Stil*, sondern eine neue Engine-Fähigkeit: ein
**Raum, größer als das Fenster**, mit einer **scrollenden Kamera**.
Siehe
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
für die vollständige Progression. Mechanisch verwendet dieses Beispiel
`maze_1`s Gitterbewegung wieder (eingebaute
`test_alignment`/`snap_to_grid`/`start_moving_direction`-Aktionen) und
fügt genau eine neue Sache hinzu: die Kamera, aktiviert aus dem
**create**-Ereignis des Spielers mit den registrierten
`enable_views` + `set_view`-Aktionen.

**Sound & Musik:** keine — diesem Beispiel liegen keine Sounddateien bei.

## Wie man spielt

- **Pfeiltasten** bewegen den Spieler jeweils um eine Gitterzelle
  (32px) (gitterausgerichtete Bewegung, dasselbe wie `maze_1`).
- Wände (`obj_wall`) säumen den Raumrand und bilden einige innere
  Säulen; sie sind fest und stoppen den Spieler.
- **Die Kamera folgt dem Spieler**: laufe auf einen Bildschirmrand zu,
  und die Ansicht scrollt, um dich im Bild zu behalten, begrenzt an
  den Raumrändern, sodass du nie über die Wandgrenze hinaussiehst.
- **Ziel:** sammle alle 18 Münzen (`obj_coin`). Jede ist 10 Punkte
  wert (angezeigt in der Fenstertitelleiste).

## Wie die Kamera eingerichtet ist

Das **create**-Ereignis des Spielers führt zwei registrierte Aktionen
aus (kein rohes `execute_code`):

1. `enable_views` — schaltet das View-System für den Raum ein.
2. `set_view` — konfiguriert **View 0**: `view_w`/`view_h` `800×600`,
   Port bei `(0,0)` mit Größe `800×600`, `follow` = `obj_player`,
   `hborder` 240 / `vborder` 180 (die Totzone, bevor die Kamera
   scrollt), keine Scrollgeschwindigkeitsbegrenzung. Dieselbe
   Konfiguration ist auch in den `views`-Block des Raumes eingebacken,
   sodass die Kamera ab dem ersten Frame auf jedem Exportziel korrekt ist.

## Projektstruktur

| Datei | Zweck |
|---|---|
| `project.json` | Projekt-Manifest — Fenster-/Raumeinstellungen, eingebettete Asset-Kopien, und die `views`-Konfiguration des Raumes |
| `rooms/room0.json` | Der 2400×800-Raum (245 Instanzen: Wandrand + Säulen, Spieler, 18 Münzen) und sein `views`-Block |
| `objects/obj_player.json` | Spieler: Gitterbewegung + die Kamera-Einrichtung im create-Ereignis |
| `objects/obj_coin.json` | Sammelobjekt: zerstört bei Spielerberührung, fügt 10 zum Punktestand hinzu |
| `objects/obj_wall.json` | Statische feste Wand |
| `sprites/` | `spr_player.png`, `spr_wall.png`, `spr_coin.png` + ihre `.json`-Metadaten |
| `CREDITS.txt` | Lizenzhinweis für die Assets |

## Objekte

| Objekt | Rolle | Wichtige Ereignisse |
|---|---|---|
| `obj_player` | Spielercharakter; Gitterbewegung + aktiviert/konfiguriert die Kamera | create (`enable_views`, `set_view`), keyboard (down/right/up/left/nokey), collision_with_obj_wall |
| `obj_coin` | Sammelobjekt im Wert von 10 Punkten | collision_with_obj_player (`destroy_instance` self), destroy (`set_score` +10) |
| `obj_wall` | Statische feste Wand / Kamera-Begrenzungsgrenze | (keine — passiver Kollisionskörper) |

## Assets

3 Sprites (`spr_player`, `spr_wall`, `spr_coin`, je 32×32, ein Frame,
pixelgenaue Kollision), 0 Sounds. Alle drei sind einfache
einfarbige CC0-Grafiken, für dieses Beispiel erstellt — siehe `CREDITS.txt`.

## Zum Experimentieren

- **Raumgröße** (`2400×800` in `rooms/room0.json`) — mache ihn
  breiter/höher, um weiter zu scrollen; die Kamera begrenzt sich auf
  das, was der Raum ist.
- **Ränder** (`hborder` 240 / `vborder` 180 in der `set_view`-Aktion
  *und* dem `views`-Block des Raumes) — kleinere Ränder lassen den
  Spieler näher an den Rand kommen, bevor die Kamera sich bewegt;
  größere halten ihn zentrierter.
- **Scrollgeschwindigkeit** — `hspeed`/`vspeed` sind `-1` (sofortiges
  Folgen). Setze sie auf einen positiven Pixel-pro-Schritt-Wert für
  eine nachziehende, geglättete Kamera.
- **Münzen** — füge `obj_coin`-Instanzen in `rooms/room0.json` hinzu
  oder entferne sie.

## Export-Status

- **Desktop (pygame):** das Referenzziel — verifiziert durch
  `tests/test_views_1_sample.py`, das dieses Beispiel lädt, das
  create-Ereignis des Spielers ausführt und sicherstellt, dass die
  Kamera scrollt und sich begrenzt, während der Spieler die gesamte
  Breite durchläuft.
- **Web (HTML5):** das exportierte `engine.js` trägt dieselbe
  8-View-Kamera (`tests/test_html5_views.py`, während der Entwicklung
  in Chromium verifiziert); sowohl die `views`-Konfiguration dieses
  Beispiels als auch das `set_view` im create-Ereignis werden im
  Export korrekt übertragen.
- **Mobil (Kivy/Android):** die exportierte Szene rendert den
  gesamten Raum in ein Fbo und kopiert den sichtbaren Bereich jedes
  Views in seinen Bildschirm-Port, wobei das OS-Fenster nach dem View
  bemessen ist (nicht nach dem Raum), sodass die Kamera einen echten
  scrollenden Ausschnitt zeigt und mehrere Viewports unterstützt
  (`tests/test_kivy_views.py`). Die `enable_views`/`set_view`-Aktionen
  werden emittiert, sodass die Laufzeit-Neukonfiguration der Kamera
  ebenfalls funktioniert. *Eine verbleibende Einschränkung:* das
  Multi-View-Renderziel wird bei der Raumerstellung gebaut, daher muss
  ein Raum `views_enabled` in seiner Konfiguration haben (wie dieses
  Beispiel es tut), damit die Kamera rendert — Views ausschließlich
  über ein Laufzeit-`enable_views` auf einem Raum zu aktivieren, der
  ohne sie gestartet ist, rüstet es auf Kivy nicht nach.
- Die zielübergreifende Übereinstimmung der Scroll-Mathematik wird
  durch `tests/test_views_export_parity.py` fixiert.

Im Willkommens-Tab der IDE als "Views — Level 1" angezeigt
(`widgets/welcome_tab.py`).
