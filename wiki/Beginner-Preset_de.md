# Anfaenger-Preset

*[Startseite](Home_de) | [Preset-Leitfaden](Preset-Guide_de) | [Fortgeschrittenen-Preset](Intermediate-Preset_de)*

Das **Anfaenger**-Preset ist fuer Benutzer konzipiert, die neu in der Spieleentwicklung sind. Es bietet eine sorgfaeltig ausgewaehlte Sammlung wesentlicher Ereignisse und Aktionen, die die Grundlagen der Erstellung einfacher 2D-Spiele abdecken, ohne Anfaenger mit zu vielen Optionen zu ueberfordern.

## Uebersicht

Das Anfaenger-Preset umfasst:
- **4 Ereignistypen** - Zum Reagieren auf Spielsituationen
- **17 Aktionstypen** - Zur Steuerung des Spielverhaltens
- **6 Kategorien** - Ereignisse, Bewegung, Punkte/Leben/Gesundheit, Instanz, Raum, Ausgabe

---

## Ereignisse

Ereignisse sind Ausloeser, die auf bestimmte Situationen in Ihrem Spiel reagieren. Wenn ein Ereignis eintritt, werden die Aktionen ausgefuehrt, die Sie fuer dieses Ereignis definiert haben.

### Create-Ereignis

| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_create` |
| **Kategorie** | Ereignisse |
| **Beschreibung** | Wird einmal ausgeloest, wenn eine Instanz zum ersten Mal erstellt wird |

**Wann es ausgeloest wird:** Sofort, wenn eine Objektinstanz in einem Raum platziert oder mit der Aktion "Instanz erstellen" erstellt wird.

**Haeufige Verwendungen:**
- Variablen initialisieren
- Startposition festlegen
- Anfangsgeschwindigkeit oder -richtung festlegen
- Punktestand bei Spielbeginn zuruecksetzen

---

### Step-Ereignis

| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_step` |
| **Kategorie** | Ereignisse |
| **Beschreibung** | Wird jeden Frame ausgeloest (normalerweise 60 Mal pro Sekunde) |

**Wann es ausgeloest wird:** Kontinuierlich, jeden Spiel-Frame.

**Haeufige Verwendungen:**
- Kontinuierliche Bewegung
- Bedingungen pruefen
- Spielzustand aktualisieren
- Animationssteuerung

---

### Tastendruck-Ereignis

| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_keyboard_press` |
| **Kategorie** | Ereignisse |
| **Beschreibung** | Wird einmal ausgeloest, wenn eine bestimmte Taste gedrueckt wird |

**Wann es ausgeloest wird:** Einmal in dem Moment, wenn eine Taste gedrueckt wird (nicht waehrend sie gehalten wird).

**Unterstuetzte Tasten:** Pfeiltasten (hoch, runter, links, rechts), Leertaste, Enter, Buchstaben (A-Z), Zahlen (0-9)

**Haeufige Verwendungen:**
- Spielersteuerung
- Springen
- Schiessen
- Menunavigation

---

### Kollisions-Ereignis

| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_collision` |
| **Kategorie** | Ereignisse |
| **Beschreibung** | Wird ausgeloest, wenn diese Instanz mit einem anderen Objekt kollidiert |

**Wann es ausgeloest wird:** Jeden Frame, in dem sich zwei Instanzen ueberlappen.

**Spezielle Variable:** In einem Kollisionsereignis bezieht sich `other` auf die Instanz, mit der kollidiert wird.

**Haeufige Verwendungen:**
- Gegenstaende sammeln (Muenzen, Power-Ups)
- Schaden von Feinden erhalten
- An Waende oder Hindernisse stossen
- Ziele oder Kontrollpunkte erreichen

---

## Aktionen

Aktionen sind Befehle, die ausgefuehrt werden, wenn ein Ereignis ausgeloest wird. Mehrere Aktionen koennen einem einzelnen Ereignis hinzugefuegt werden und werden der Reihe nach ausgefuehrt.

---

## Bewegungsaktionen

### Horizontale Geschwindigkeit setzen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `set_hspeed` |
| **Blockname** | `move_set_hspeed` |
| **Kategorie** | Bewegung |
| **Symbol** | ↔️ |

**Beschreibung:** Setzt die horizontale Bewegungsgeschwindigkeit der Instanz.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `value` | Zahl | Geschwindigkeit in Pixeln pro Frame. Positiv = rechts, Negativ = links |

**Beispiel:** Setzen Sie `value` auf `4`, um sich mit 4 Pixeln pro Frame nach rechts zu bewegen, oder `-4` fuer links.

---

### Vertikale Geschwindigkeit setzen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `set_vspeed` |
| **Blockname** | `move_set_vspeed` |
| **Kategorie** | Bewegung |
| **Symbol** | ↕️ |

**Beschreibung:** Setzt die vertikale Bewegungsgeschwindigkeit der Instanz.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `value` | Zahl | Geschwindigkeit in Pixeln pro Frame. Positiv = runter, Negativ = hoch |

**Beispiel:** Setzen Sie `value` auf `-4`, um sich mit 4 Pixeln pro Frame nach oben zu bewegen, oder `4` fuer unten.

---

### Bewegung stoppen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `stop_movement` |
| **Blockname** | `move_stop` |
| **Kategorie** | Bewegung |
| **Symbol** | 🛑 |

**Beschreibung:** Stoppt alle Bewegung, indem sowohl horizontale als auch vertikale Geschwindigkeit auf Null gesetzt werden.

**Parameter:** Keine

**Haeufige Verwendungen:**
- Spieler stoppen, wenn er eine Wand trifft
- Feinde stoppen, wenn sie ein Ziel erreichen
- Bewegung voruebergehend pausieren

---

### Zu Position springen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `jump_to_position` |
| **Blockname** | `move_jump_to` |
| **Kategorie** | Bewegung |
| **Symbol** | 📍 |

**Beschreibung:** Bewegt die Instanz sofort zu einer bestimmten Position (keine fliessende Bewegung).

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `x` | Zahl | Ziel-X-Koordinate |
| `y` | Zahl | Ziel-Y-Koordinate |

**Beispiel:** Springen Sie zu Position (100, 200), um den Spieler an diesen Ort zu teleportieren.

---

## Instanzaktionen

### Instanz zerstoeren

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `destroy_instance` |
| **Blockname** | `instance_destroy` |
| **Kategorie** | Instanz |
| **Symbol** | 💥 |

**Beschreibung:** Entfernt eine Instanz aus dem Spiel.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `target` | Auswahl | `self` = diese Instanz zerstoeren, `other` = die kollidierende Instanz zerstoeren |

**Haeufige Verwendungen:**
- Gesammelte Muenzen entfernen (`target: other` im Kollisionsereignis)
- Kugeln zerstoeren, wenn sie etwas treffen
- Feinde entfernen, wenn sie besiegt sind

---

### Instanz erstellen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `create_instance` |
| **Blockname** | `instance_create` |
| **Kategorie** | Instanz |
| **Symbol** | ✨ |

**Beschreibung:** Erstellt eine neue Instanz eines Objekts an einer bestimmten Position.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `object` | Objekt | Der zu erstellende Objekttyp |
| `x` | Zahl | X-Koordinate fuer die neue Instanz |
| `y` | Zahl | Y-Koordinate fuer die neue Instanz |

**Beispiel:** Erstellen Sie eine Kugel an der Position des Spielers, wenn die Leertaste gedrueckt wird.

---

## Punkteaktionen

### Punkte setzen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `set_score` |
| **Blockname** | `score_set` |
| **Kategorie** | Punkte/Leben/Gesundheit |
| **Symbol** | 🏆 |

**Beschreibung:** Setzt den Punktestand auf einen bestimmten Wert oder addiert/subtrahiert vom aktuellen Punktestand.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `value` | Zahl | Der Punktewert |
| `relative` | Boolean | Wenn wahr, wird der Wert zum aktuellen Punktestand addiert. Wenn falsch, wird der Punktestand auf den Wert gesetzt |

**Beispiele:**
- Punktestand zuruecksetzen: `value: 0`, `relative: false`
- 10 Punkte hinzufuegen: `value: 10`, `relative: true`
- 5 Punkte abziehen: `value: -5`, `relative: true`

---

### Zum Punktestand addieren

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `add_score` |
| **Blockname** | `score_add` |
| **Kategorie** | Punkte/Leben/Gesundheit |
| **Symbol** | ➕🏆 |

**Beschreibung:** Addiert einen Wert zum aktuellen Punktestand (Abkuerzung fuer set_score mit relative=true).

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `value` | Zahl | Punkte zum Hinzufuegen (kann negativ sein zum Abziehen) |

---

### Punkte zeichnen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `draw_score` |
| **Blockname** | `draw_score` |
| **Kategorie** | Punkte/Leben/Gesundheit |
| **Symbol** | 🖼️🏆 |

**Beschreibung:** Zeigt den aktuellen Punktestand auf dem Bildschirm an.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `x` | Zahl | X-Position zum Zeichnen des Punktestands |
| `y` | Zahl | Y-Position zum Zeichnen des Punktestands |
| `caption` | Zeichenkette | Text, der vor dem Punktestand angezeigt wird (z.B. "Punkte: ") |

**Hinweis:** Dies sollte in einem Draw-Ereignis verwendet werden (verfuegbar im Fortgeschrittenen-Preset).

---

## Raumaktionen

### Zum naechsten Raum gehen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `next_room` |
| **Blockname** | `room_goto_next` |
| **Kategorie** | Raum |
| **Symbol** | ➡️ |

**Beschreibung:** Wechselt zum naechsten Raum in der Raumreihenfolge.

**Parameter:** Keine

**Hinweis:** Wenn Sie sich bereits im letzten Raum befinden, hat diese Aktion keine Auswirkung (verwenden Sie "Wenn naechster Raum existiert", um zuerst zu pruefen).

---

### Zum vorherigen Raum gehen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `previous_room` |
| **Blockname** | `room_goto_previous` |
| **Kategorie** | Raum |
| **Symbol** | ⬅️ |

**Beschreibung:** Wechselt zum vorherigen Raum in der Raumreihenfolge.

**Parameter:** Keine

**Hinweis:** Wenn Sie sich bereits im ersten Raum befinden, hat diese Aktion keine Auswirkung.

---

### Raum neu starten

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `restart_room` |
| **Blockname** | `room_restart` |
| **Kategorie** | Raum |
| **Symbol** | 🔄 |

**Beschreibung:** Startet den aktuellen Raum neu und setzt alle Instanzen auf ihren Anfangszustand zurueck.

**Parameter:** Keine

**Haeufige Verwendungen:**
- Level neu starten, nachdem der Spieler gestorben ist
- Raetsel nach Fehlschlag zuruecksetzen
- Minispiel wiederholen

---

### Zu Raum gehen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `goto_room` |
| **Blockname** | `room_goto` |
| **Kategorie** | Raum |
| **Symbol** | 🚪 |

**Beschreibung:** Wechselt zu einem bestimmten Raum nach Name.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `room` | Raum | Der Raum, zu dem gewechselt werden soll |

---

### Wenn naechster Raum existiert

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `if_next_room_exists` |
| **Blockname** | `room_if_next_exists` |
| **Kategorie** | Raum |
| **Symbol** | ❓➡️ |

**Beschreibung:** Bedingungsblock, der enthaltene Aktionen nur ausfuehrt, wenn ein naechster Raum existiert.

**Parameter:** Keine (Aktionen werden innerhalb des Blocks platziert)

**Haeufige Verwendungen:**
- Vor dem Wechsel zum naechsten Raum pruefen
- "Sie haben gewonnen!"-Nachricht anzeigen, wenn keine weiteren Raeume vorhanden sind

---

### Wenn vorheriger Raum existiert

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `if_previous_room_exists` |
| **Blockname** | `room_if_previous_exists` |
| **Kategorie** | Raum |
| **Symbol** | ❓⬅️ |

**Beschreibung:** Bedingungsblock, der enthaltene Aktionen nur ausfuehrt, wenn ein vorheriger Raum existiert.

**Parameter:** Keine (Aktionen werden innerhalb des Blocks platziert)

---

## Ausgabeaktionen

### Nachricht anzeigen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `show_message` |
| **Blockname** | `output_message` |
| **Kategorie** | Ausgabe |
| **Symbol** | 💬 |

**Beschreibung:** Zeigt dem Spieler einen Popup-Nachrichtendialog an.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `message` | Zeichenkette | Der anzuzeigende Text |

**Hinweis:** Das Spiel pausiert, waehrend die Nachricht angezeigt wird. Der Spieler muss auf OK klicken, um fortzufahren.

**Haeufige Verwendungen:**
- Spielanweisungen
- Geschichtsdialoge
- Gewinn-/Verlustnachrichten
- Debug-Informationen

---

### Code ausfuehren

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `execute_code` |
| **Blockname** | `execute_code` |
| **Kategorie** | Ausgabe |
| **Symbol** | 💻 |

**Beschreibung:** Fuehrt benutzerdefinierten Python-Code aus.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `code` | Zeichenkette | Auszufuehrender Python-Code |

**Hinweis:** Dies ist eine erweiterte Funktion. Verwenden Sie sie mit Vorsicht, da falscher Code Fehler verursachen kann.

---

## Kategorienuebersicht

| Kategorie | Ereignisse | Aktionen |
|-----------|------------|----------|
| **Ereignisse** | Create, Step, Tastendruck, Kollision | - |
| **Bewegung** | - | Horizontale Geschwindigkeit setzen, Vertikale Geschwindigkeit setzen, Bewegung stoppen, Zu Position springen |
| **Instanz** | - | Instanz zerstoeren, Instanz erstellen |
| **Punkte/Leben/Gesundheit** | - | Punkte setzen, Punkte addieren, Punkte zeichnen |
| **Raum** | - | Naechster Raum, Vorheriger Raum, Raum neu starten, Zu Raum gehen, Wenn naechster Raum existiert, Wenn vorheriger Raum existiert |
| **Ausgabe** | - | Nachricht anzeigen, Code ausfuehren |

---

## Beispiel: Einfaches Muenzensammelspiel

So richten Sie ein einfaches Muenzensammelspiel nur mit Funktionen des Anfaenger-Presets ein:

### Spielerobjekt (obj_player)

**Tastendruck (Pfeil links):**
- Horizontale Geschwindigkeit setzen: -4

**Tastendruck (Pfeil rechts):**
- Horizontale Geschwindigkeit setzen: 4

**Tastendruck (Pfeil hoch):**
- Vertikale Geschwindigkeit setzen: -4

**Tastendruck (Pfeil runter):**
- Vertikale Geschwindigkeit setzen: 4

**Kollision mit obj_coin:**
- Punkte setzen: 10 (relative: true)
- Instanz zerstoeren: other

**Kollision mit obj_wall:**
- Bewegung stoppen

**Kollision mit obj_goal:**
- Punkte setzen: 100 (relative: true)
- Naechster Raum

### Muenzenobjekt (obj_coin)
Keine Ereignisse erforderlich - nur ein sammelbarer Gegenstand.

### Wandobjekt (obj_wall)
Keine Ereignisse erforderlich - nur ein festes Hindernis.

### Zielobjekt (obj_goal)
Keine Ereignisse erforderlich - loest Levelabschluss aus, wenn der Spieler kollidiert.

---

## Upgrade auf Fortgeschritten

Wenn Sie mit dem Anfaenger-Preset vertraut sind, sollten Sie ein Upgrade auf **Fortgeschritten** in Betracht ziehen, um Zugang zu erhalten zu:
- Draw-Ereignis (fuer benutzerdefiniertes Rendering)
- Destroy-Ereignis (Aufraeumen, wenn eine Instanz zerstoert wird)
- Mausereignisse (Klickerkennung)
- Alarm-Ereignisse (zeitgesteuerte Aktionen)
- Leben- und Gesundheitssysteme
- Sound- und Musikaktionen
- Mehr Bewegungsoptionen (Richtung, auf etwas zubewegen)

---

## Siehe auch

- [Fortgeschrittenen-Preset](Intermediate-Preset_de) - Funktionen der naechsten Stufe
- [Vollstaendige Aktionsreferenz](Full-Action-Reference_de) - Vollstaendige Aktionsliste
- [Ereignisreferenz](Event-Reference_de) - Vollstaendige Ereignisliste
- [Ereignisse und Aktionen](Events-and-Actions_de) - Kernkonzepte
- [Erstellen Sie Ihr erstes Spiel](Creating-Your-First-Game_de) - Schritt-fuer-Schritt-Anleitung
- [Breakout Tutorial](Tutorial-Breakout_de) - Erstellen Sie ein klassisches Breakout-Spiel
- [Einfuehrung in die Spieleentwicklung](Getting-Started-Breakout_de) - Umfassendes Anfaenger-Tutorial
