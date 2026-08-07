# Visuelle Programmierung

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

> [Zurück zur Startseite](Home_de)

PyGameMaker enthält Google Blockly für visuelle Programmierung per Drag-and-Drop. Bauen Sie Spiellogik, indem Sie Blöcke verbinden, statt Code zu schreiben.

---

## Auf Blockly zugreifen

1. Öffnen Sie ein Objekt im Object Editor
2. Klicken Sie auf den **Blockly**-Tab (neben dem Events-Tab)
3. Der Blockly-Arbeitsbereich erscheint mit einer Werkzeugleiste links

**Welche Blöcke Sie sehen, hängt von Ihrem Preset ab.**
`Tools > Configure Action Blocks...` (oder `Preferences > IDE Edition`,
welches das Standard-Preset für neue Projekte festlegt) steuert die
Blockmenge — siehe den [Preset-Leitfaden](Preset-Guide_de) für Details.
Die Tabellen unten listen alle Blöcke, die in irgendeinem Preset
existieren; ein konkretes Projekt zeigt möglicherweise weniger.

---

## Der Blockly-Arbeitsbereich

### Werkzeugleiste
Das linke Panel enthält die Blockkategorien:
- **Events** - Ereignis-Auslöser-Blöcke
- **Control** - Bedingungen, Variablen und Gruppierung (die
  Bedingungsblöcke dieses Projekts sind stapelbare Blöcke, keine
  klassischen Wenn/Sonst-Container — siehe "Blocktypen" unten)
- **Movement** - Bewegungs-, Geschwindigkeits- und Physikblöcke
- **Timing** - Alarme
- **Drawing** - Text- und Formblöcke
- **Score/Lives/Health** - Spielzustand-Blöcke
- **Instance** - Erstellen/Zerstören von Objekten
- **Room** - Navigation zwischen Rooms
- **Values** - Wertblöcke (Position, Geschwindigkeit, Score, Leben,
  Gesundheit, Maus)
- **Sound** - Audiowiedergabe
- **Output** - Nachrichten und benutzerdefinierter Python-Code
- **Game** - Spiel beenden/neu starten, Bestenliste

Es gibt keine separate Kategorie Math, Text oder Logik — numerische/Text-
Felder werden direkt auf jedem Block eingegeben, und es gibt keinen
generischen booleschen/Vergleichs-Wertblock. Siehe "Blocktypen" unten,
wie Bedingungen stattdessen funktionieren.

### Arbeitsfläche
Der zentrale Bereich, in dem Sie Ihr Programm bauen, indem Sie:
- Blöcke aus der Werkzeugleiste ziehen
- Blöcke miteinander verbinden
- Blockparameter konfigurieren

### Papierkorb
Ziehen Sie unerwünschte Blöcke hierher, um sie zu löschen, oder drücken Sie die Entfernen-Taste.

---

## Blocktypen

### Hat-Blöcke (Events)
Hat-Blöcke haben eine abgerundete Oberseite und starten eine Sequenz. Sie repräsentieren Events:

```
┌─────────────────┐
│ When Create     │
└─────────────────┘
```

### Stapelbare Blöcke (Aktionen)
Stapelbare Blöcke haben Kerben, die sich mit anderen Blöcken verbinden.
Fast alle Blöcke außerhalb der Kategorie Values sind stapelbare Blöcke —
einschließlich der Bedingungsblöcke:

```
├─────────────────┤
│ Set Horizontal Speed [5] │
├─────────────────┤
```

### Wertblöcke (Values)
Wertblöcke sind abgerundet und werden in ein numerisches Feld eines
anderen Blocks eingesteckt (z. B. das Geschwindigkeitsfeld von Move
Direction, oder das Wertfeld von Set Variable). Dieses Projekt hat 9
davon — X Position, Y Position, Horizontal Speed, Vertical Speed, Score,
Lives, Health, Mouse X, Mouse Y:

```
( X Position )    ( Score )    ( 100 )
```

Es gibt keinen generischen `( speed )`- oder `( direction )`-Wertblock —
diese Konzepte werden in dieser Engine nicht als einzelner Wert verfolgt
(Bewegungsgeschwindigkeit/-richtung ergeben sich aus Horizontal Speed +
Vertical Speed zusammen), und es gibt auch keinen Wertblock für
benutzerdefinierte Variablen (lesen Sie sie stattdessen über den
Vergleich von Test Variable).

### Bedingungen — stapelbare Blöcke, keine C-Container
Anders als bei Scratch-artigen visuellen Sprachen sind die Blöcke If
Condition / Test Variable dieses Projekts **stapelbare Blöcke mit einem
einzigen "then"-Slot**, keine zweiseitigen Wenn/Sonst-Container, und es
gibt keinen hexagonalen booleschen Block zum Einstecken — der Vergleich
wird direkt über Felder auf dem Block aufgebaut:

```
┌───────────────────────────────────┐
│ If count of [obj_coin] [==] [0]   │
├───────────────────────────────────┤
│  then [Aktionen hier]             │
└───────────────────────────────────┘
```

Um einen "sonst"-Zweig hinzuzufügen oder mehrere Aktionen auf einer Seite
auszuführen, kombinieren Sie ihn mit drei weiteren Control-Blöcken:
- **Else** - führt seinen eigenen nächsten Block nur aus, wenn der
  vorangehende Test falsch war
- **Start Block** / **End Block** - gruppieren mehrere Aktionen, damit
  der vorangehende Test (oder Else) auf die ganze Gruppe wirkt, nicht nur
  auf den nächsten Block

Dies ist derselbe flache, GM80-artige Bedingungsfluss, den auch das
strukturierte Events/Actions-Panel verwendet (siehe [Events und
Aktionen](Events_und_Aktionen_de)) — Blockly ist eine
Drag-and-Drop-Oberfläche über derselben zugrunde liegenden Aktionsliste,
kein separates Ausführungsmodell.

---

## Event-Blöcke

### Create-Event
```
┌─────────────────────┐
│ When Create         │
├─────────────────────┤
│ [Aktionen hier]      │
└─────────────────────┘
```

### Step-Event
```
┌─────────────────────┐
│ When Step            │
├─────────────────────┤
│ [jeder Frame]         │
└─────────────────────┘
```

### Tastatur-Events
Es gibt vier separate Tastatur-Hat-Blöcke — Held, Press, Release und No
Key — jeder mit einem Dropdown für den Tastennamen (No Key hat keins, da
es feuert, wenn nichts gehalten wird):
```
┌─────────────────────────┐
│ When key [held: left] ▼ │
├─────────────────────────┤
│ [Aktionen hier]          │
└─────────────────────────┘
```

### Kollisions-Events
```
┌────────────────────────────┐
│ When colliding with [obj] ▼│
├────────────────────────────┤
│ [Aktionen hier]             │
└────────────────────────────┘
```

---

## Bewegungsblöcke

| Block | Beschreibung |
|------|-------------|
| `Set Horizontal Speed [4]` | X-Geschwindigkeit festlegen |
| `Set Vertical Speed [-5]` | Y-Geschwindigkeit festlegen |
| `Stop Movement` | Beide Geschwindigkeiten auf null setzen |
| `Move [direction ▼] speed [3]` | In eine von 4 Richtungen bewegen (oder Diagonalen, oder "stop") |
| `Move Free [direction] [speed]` | Mit beliebigem Winkel und beliebiger Geschwindigkeit bewegen |
| `Set Speed [5]` | Geschwindigkeitsbetrag festlegen, aktuelle Richtung beibehalten |
| `Set Direction [90]` | Richtungswinkel festlegen, aktuelle Geschwindigkeit beibehalten |
| `Move Towards x:[100] y:[200] speed:[3]` | Zu einem Punkt bewegen |
| `Snap to Grid` | Position am Gitter ausrichten |
| `Jump to Position x:[100] y:[200]` | Sofortige Teleportation |
| `Move Grid [direction]` | Genau eine Gitterzelle bewegen |
| `Stop if No Keys` / `Check Keys and Move` / `If On Grid` | Hilfsblöcke für Gitterbewegung |
| `Set Gravity` | Bei jedem Frame eine konstante Kraft (nach unten oder in jede Richtung) anwenden |
| `Set Friction` | Bei jedem Frame einen Geschwindigkeitsabfall anwenden |
| `Reverse Horizontal` / `Reverse Vertical` | X- oder Y-Richtung umkehren |
| `Bounce` | Von soliden Objekten abprallen |
| `Wrap Around Room` | Auf der gegenüberliegenden Seite wieder erscheinen |
| `Move to Contact` | Bewegen, bis etwas berührt wird |

Es gibt keinen Block "Jump to Start Position" oder "Jump to Random
Position" — diese beiden Aktionen existieren nur im strukturierten
Panel, nicht in Blockly.

---

## Zeichenblöcke

| Block | Beschreibung |
|------|-------------|
| `Draw Text [Hallo] at x:[10] y:[10]` | Text anzeigen |
| `Draw Rectangle from x1,y1 to x2,y2` | Gefülltes Rechteck zeichnen |
| `Draw Circle at x,y radius [r]` | Gefüllten Kreis zeichnen |
| `Set Sprite [spr]` | Sprite der Instanz ändern |
| `Set Transparency [0-1]` | Alpha festlegen |

Es gibt keinen Block "Draw Sprite an Position" oder "Set Drawing Color"
in Blockly (beide existieren nur im strukturierten Panel). Draw
Score/Draw Lives/Draw Health Bar sind unten unter Score/Lives/Health
gelistet, nicht hier.

---

## Score/Lives/Health-Blöcke

| Block | Beschreibung |
|------|-------------|
| `Set Score [100]` | Score exakt festlegen |
| `Add to Score [10]` | Score erhöhen/verringern |
| `Set Lives [3]` | Leben exakt festlegen |
| `Add to Lives [-1]` | Leben erhöhen/verringern |
| `Set Health [100]` | Gesundheit exakt festlegen |
| `Add to Health [-25]` | Gesundheit erhöhen/verringern |
| `Draw Score` | Score-Text anzeigen |
| `Draw Lives` | Leben als wiederholte Icons anzeigen |
| `Draw Health Bar` | Gesundheit als zweifarbigen Balken anzeigen |

---

## Instanzblöcke

| Block | Beschreibung |
|------|-------------|
| `Create Instance [obj] at x:[100] y:[200]` | Neue Instanz erzeugen |
| `Destroy Instance` | Sich selbst entfernen |
| `Destroy Other` | Die kollidierende Instanz entfernen (in einem Collision-Event) |
| `Change Instance [obj]` | In einen anderen Objekttyp verwandeln |
| `If Can Push [obj] [direction]` | Sokoban-artige Schiebeprüfung |

Es gibt keinen Block "alle eines Typs zerstören" oder "an dieser Position erstellen".

---

## Room-Blöcke

| Block | Beschreibung |
|------|-------------|
| `Next Room` | Zum nächsten Room weitergehen |
| `Previous Room` | Zum vorherigen Room zurückkehren |
| `Restart Room` | Aktuellen Room zurücksetzen |
| `Go to Room [room_name]` | Zu einem bestimmten Room springen |
| `If Next Room Exists` / `If Previous Room Exists` | Absichern der Mehr-Room-Navigation |

---

## Sound-Blöcke

| Block | Beschreibung |
|------|-------------|
| `Play Sound [snd]` | Soundeffekt abspielen |
| `Play Music [music]` | Hintergrundmusik abspielen (in Schleife) |
| `Stop Music` | Musik stoppen |

Es gibt keinen Block "Stop Sound" (pro Sound) oder "Alle Sounds stoppen"
in Blockly (nur Stop Music, das speziell die Musik stoppt).

---

## Kontrollblöcke

| Block | Beschreibung |
|------|-------------|
| `If count of [obj] [==] [0] then...` | Instanzanzahl eines Objekts vergleichen; folgende(n) Block(e) ausführen, wenn wahr |
| `If variable [var] [==] [value] then...` | Benutzerdefinierte Variable vergleichen; folgende(n) Block(e) ausführen, wenn wahr |
| `Set Variable [name] to [value]` | Instanz- oder globale Variable zuweisen |
| `Check Empty at x,y` | Wahr, wenn eine Position keine Kollision hat (Gitterbewegung) |
| `Exit Event` | Restliche Aktionen dieses Events stoppen |
| `Else` | Führt seinen eigenen nächsten Block aus, wenn der vorangehende Test falsch war |
| `Start Block` / `End Block` | Mehrere Aktionen unter einem Test/Else gruppieren |

---

## Output- und Game-Blöcke

| Block | Beschreibung |
|------|-------------|
| `Show Message [text]` | Popup-Nachricht anzeigen |
| `Execute Code` | Echtes Python ausführen (siehe [Events und Aktionen](Events_und_Aktionen_de)) |
| `End Game` | Spiel schließen |
| `Restart Game` | Ab dem ersten Room neu starten |
| `Show Highscore` / `Clear Highscore` | Bestenliste anzeigen oder zurücksetzen |

---

## Wertblöcke

Wertblöcke — stecken Sie sie in ein numerisches Feld eines anderen Blocks:

| Block | Beschreibung |
|------|-------------|
| `X Position` | Die X-Koordinate dieser Instanz |
| `Y Position` | Die Y-Koordinate dieser Instanz |
| `Horizontal Speed` | Die X-Geschwindigkeit dieser Instanz |
| `Vertical Speed` | Die Y-Geschwindigkeit dieser Instanz |
| `Score` | Der aktuelle Score |
| `Lives` | Die aktuellen Leben |
| `Health` | Die aktuelle Gesundheit |
| `Mouse X` / `Mouse Y` | Die aktuelle Mausposition |

---

## Beispiel: Spielerbewegung

```
┌──────────────────────────┐
│ When key [held: left]    │
├──────────────────────────┤
│ Set Horizontal Speed [-4]│
└──────────────────────────┘

┌──────────────────────────┐
│ When key [held: right]   │
├──────────────────────────┤
│ Set Horizontal Speed [4] │
└──────────────────────────┘

┌──────────────────────────┐
│ When key [no key]        │
├──────────────────────────┤
│ Set Horizontal Speed [0] │
└──────────────────────────┘
```

---

## Beispiel: Münzen sammeln

```
┌─────────────────────────────┐
│ When colliding with obj_coin│
├─────────────────────────────┤
│ Add to Score [10]           │
├─────────────────────────────┤
│ Play Sound [snd_coin]       │
├─────────────────────────────┤
│ Destroy Other                │
└─────────────────────────────┘
```

---

## Tipps

1. **Mit Events beginnen** - Immer mit einem Event-Block (Hat-Block) starten
2. **Vertikal verbinden** - Stapelbare Blöcke verbinden sich von oben nach unten
3. **Farben nutzen** - Blockfarben zeigen ihre Kategorie an
4. **Rechtsklick** - Zugriff auf Duplizieren, Löschen und Hilfe
5. **Zoom** - Mausrad oder Zoom-Steuerung für große Programme verwenden
6. **Wechsel zum strukturierten Panel** - Alles, was Blockly kann,
   entspricht einer Aktion im Events-Tab des strukturierten Panels, aber
   nicht umgekehrt (z. B. haben Jump to Start/Random Position und Stop
   Sound pro Sound keinen Blockly-Block) — verwenden Sie in diesem Fall
   für dieses Event das strukturierte Panel statt Blockly.

---

## Nächste Schritte

- [[Events_und_Aktionen_de]] - Das Äquivalent als Aktionsliste ansehen
- [[Erstes_Spiel_de]] - Ein vollständiges Spiel bauen
- [[Objekt_Editor_de]] - Wo Blockly integriert ist
- [[Preset-Guide_de]] - Welche Blöcke in Ihrem Projekt verfügbar sind
