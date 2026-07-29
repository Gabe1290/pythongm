# Anfänger-Preset

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Fortgeschrittenen-Preset](Intermediate-Preset_de)*

Das **Anfänger**-Preset ist für Benutzer konzipiert, die neu in der Spieleentwicklung sind. Es bietet eine sorgfältig ausgewählte Sammlung wesentlicher Ereignisse und Aktionen, die die Grundlagen der Erstellung einfacher 2D-Spiele abdecken, ohne Anfänger mit zu vielen Optionen zu überfordern.

## Übersicht

Das Anfänger-Preset umfasst:
- **4 Ereignistypen** - Zum Reagieren auf Spielsituationen
- **17 Aktionstypen** - Zur Steuerung des Spielverhaltens
- **6 Kategorien** - Ereignisse, Bewegung, Punkte/Leben/Gesundheit, Instanz, Raum, Ausgabe

---

## Ereignisse

Ereignisse sind Auslöser, die auf bestimmte Situationen in Ihrem Spiel reagieren. Wenn ein Ereignis eintritt, werden die Aktionen ausgeführt, die Sie für dieses Ereignis definiert haben.

### Create-Ereignis

| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_create` |
| **Kategorie** | Ereignisse |
| **Beschreibung** | Wird einmal ausgelöst, wenn eine Instanz zum ersten Mal erstellt wird |

**Wann es ausgelöst wird:** Sofort, wenn eine Objektinstanz in einem Raum platziert oder mit der Aktion „Instanz erstellen" erstellt wird.

**Häufige Verwendungen:**
- Variablen initialisieren
- Startposition festlegen
- Anfangsgeschwindigkeit oder -richtung festlegen
- Punktestand bei Spielbeginn zurücksetzen

---

### Step-Ereignis

| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_step` |
| **Kategorie** | Ereignisse |
| **Beschreibung** | Wird jeden Frame ausgelöst (normalerweise 60 Mal pro Sekunde) |

**Wann es ausgelöst wird:** Kontinuierlich, jeden Spiel-Frame.

**Häufige Verwendungen:**
- Kontinuierliche Bewegung
- Bedingungen prüfen
- Spielzustand aktualisieren
- Animationssteuerung

---

### Tastendruck-Ereignis

| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_keyboard_press` |
| **Kategorie** | Ereignisse |
| **Beschreibung** | Wird einmal ausgelöst, wenn eine bestimmte Taste gedrückt wird |

**Wann es ausgelöst wird:** Einmal in dem Moment, wenn eine Taste gedrückt wird (nicht während sie gehalten wird).

**Unterstützte Tasten:** Pfeiltasten (hoch, runter, links, rechts), Leertaste, Enter, Buchstaben (A-Z), Zahlen (0-9)

**Häufige Verwendungen:**
- Spielersteuerung
- Springen
- Schießen
- Menünavigation

---

### Kollisions-Ereignis

| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_collision` |
| **Kategorie** | Ereignisse |
| **Beschreibung** | Wird ausgelöst, wenn diese Instanz mit einem anderen Objekt kollidiert |

**Wann es ausgelöst wird:** Jeden Frame, in dem sich zwei Instanzen überlappen.

**Spezielle Variable:** In einem Kollisionsereignis bezieht sich `other` auf die Instanz, mit der kollidiert wird.

**Häufige Verwendungen:**
- Gegenstände sammeln (Münzen, Power-Ups)
- Schaden von Feinden erhalten
- An Wände oder Hindernisse stoßen
- Ziele oder Kontrollpunkte erreichen

---

## Aktionen

Aktionen sind Befehle, die ausgeführt werden, wenn ein Ereignis ausgelöst wird. Mehrere Aktionen können einem einzelnen Ereignis hinzugefügt werden und werden der Reihe nach ausgeführt.

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

**Beispiel:** Setzen Sie `value` auf `4`, um sich mit 4 Pixeln pro Frame nach rechts zu bewegen, oder `-4` für links.

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

**Beispiel:** Setzen Sie `value` auf `-4`, um sich mit 4 Pixeln pro Frame nach oben zu bewegen, oder `4` für unten.

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

**Häufige Verwendungen:**
- Spieler stoppen, wenn er eine Wand trifft
- Feinde stoppen, wenn sie ein Ziel erreichen
- Bewegung vorübergehend pausieren

---

### Zu Position springen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `jump_to_position` |
| **Blockname** | `move_jump_to` |
| **Kategorie** | Bewegung |
| **Symbol** | 📍 |

**Beschreibung:** Bewegt die Instanz sofort zu einer bestimmten Position (keine fließende Bewegung).

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `x` | Zahl | Ziel-X-Koordinate |
| `y` | Zahl | Ziel-Y-Koordinate |

**Beispiel:** Springen Sie zu Position (100, 200), um den Spieler an diesen Ort zu teleportieren.

---

## Instanzaktionen

### Instanz zerstören

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
| `target` | Auswahl | `self` = diese Instanz zerstören, `other` = die kollidierende Instanz zerstören |

**Häufige Verwendungen:**
- Gesammelte Münzen entfernen (`target: other` im Kollisionsereignis)
- Kugeln zerstören, wenn sie etwas treffen
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
| `x` | Zahl | X-Koordinate für die neue Instanz |
| `y` | Zahl | Y-Koordinate für die neue Instanz |

**Beispiel:** Erstellen Sie eine Kugel an der Position des Spielers, wenn die Leertaste gedrückt wird.

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
- Punktestand zurücksetzen: `value: 0`, `relative: false`
- 10 Punkte hinzufügen: `value: 10`, `relative: true`
- 5 Punkte abziehen: `value: -5`, `relative: true`

---

### Zum Punktestand addieren

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `add_score` |
| **Blockname** | `score_add` |
| **Kategorie** | Punkte/Leben/Gesundheit |
| **Symbol** | ➕🏆 |

**Beschreibung:** Addiert einen Wert zum aktuellen Punktestand (Abkürzung für set_score mit relative=true).

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `value` | Zahl | Punkte zum Hinzufügen (kann negativ sein zum Abziehen) |

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
| `caption` | Zeichenkette | Text, der vor dem Punktestand angezeigt wird (z. B. „Punkte: ") |

**Hinweis:** Dies sollte in einem Draw-Ereignis verwendet werden (verfügbar im Fortgeschrittenen-Preset).

---

## Raumaktionen

### Zum nächsten Raum gehen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `next_room` |
| **Blockname** | `room_goto_next` |
| **Kategorie** | Raum |
| **Symbol** | ➡️ |

**Beschreibung:** Wechselt zum nächsten Raum in der Raumreihenfolge.

**Parameter:** Keine

**Hinweis:** Wenn Sie sich bereits im letzten Raum befinden, hat diese Aktion keine Auswirkung (verwenden Sie „Wenn nächster Raum existiert", um zuerst zu prüfen).

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

**Beschreibung:** Startet den aktuellen Raum neu und setzt alle Instanzen auf ihren Anfangszustand zurück.

**Parameter:** Keine

**Häufige Verwendungen:**
- Level neu starten, nachdem der Spieler gestorben ist
- Rätsel nach einem Fehlschlag zurücksetzen
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

### Wenn nächster Raum existiert

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `if_next_room_exists` |
| **Blockname** | `room_if_next_exists` |
| **Kategorie** | Raum |
| **Symbol** | ❓➡️ |

**Beschreibung:** Bedingungsblock, der enthaltene Aktionen nur ausführt, wenn ein nächster Raum existiert.

**Parameter:** Keine (Aktionen werden innerhalb des Blocks platziert)

**Häufige Verwendungen:**
- Vor dem Wechsel zum nächsten Raum prüfen
- „Sie haben gewonnen!"-Nachricht anzeigen, wenn keine weiteren Räume vorhanden sind

---

### Wenn vorheriger Raum existiert

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `if_previous_room_exists` |
| **Blockname** | `room_if_previous_exists` |
| **Kategorie** | Raum |
| **Symbol** | ❓⬅️ |

**Beschreibung:** Bedingungsblock, der enthaltene Aktionen nur ausführt, wenn ein vorheriger Raum existiert.

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

**Hinweis:** Das Spiel pausiert, während die Nachricht angezeigt wird. Der Spieler muss auf OK klicken, um fortzufahren.

**Häufige Verwendungen:**
- Spielanweisungen
- Geschichtsdialoge
- Gewinn-/Verlustnachrichten
- Debug-Informationen

---

### Code ausführen

| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `execute_code` |
| **Blockname** | `execute_code` |
| **Kategorie** | Ausgabe |
| **Symbol** | 💻 |

**Beschreibung:** Führt benutzerdefinierten Python-Code aus.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `code` | Zeichenkette | Auszuführender Python-Code |

**Hinweis:** Dies ist eine erweiterte Funktion. Verwenden Sie sie mit Vorsicht, da falscher Code Fehler verursachen kann.

---

## Kategorienübersicht

| Kategorie | Ereignisse | Aktionen |
|-----------|------------|----------|
| **Ereignisse** | Create, Step, Tastendruck, Kollision | - |
| **Bewegung** | - | Horizontale Geschwindigkeit setzen, Vertikale Geschwindigkeit setzen, Bewegung stoppen, Zu Position springen |
| **Instanz** | - | Instanz zerstören, Instanz erstellen |
| **Punkte/Leben/Gesundheit** | - | Punkte setzen, Punkte addieren, Punkte zeichnen |
| **Raum** | - | Nächster Raum, Vorheriger Raum, Raum neu starten, Zu Raum gehen, Wenn nächster Raum existiert, Wenn vorheriger Raum existiert |
| **Ausgabe** | - | Nachricht anzeigen, Code ausführen |

---

## Beispiel: Einfaches Münzensammelspiel

So richten Sie ein einfaches Münzensammelspiel nur mit Funktionen des Anfänger-Presets ein:

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
- Instanz zerstören: other

**Kollision mit obj_wall:**
- Bewegung stoppen

**Kollision mit obj_goal:**
- Punkte setzen: 100 (relative: true)
- Nächster Raum

### Münzenobjekt (obj_coin)
Keine Ereignisse erforderlich - nur ein sammelbarer Gegenstand.

### Wandobjekt (obj_wall)
Keine Ereignisse erforderlich - nur ein festes Hindernis.

### Zielobjekt (obj_goal)
Keine Ereignisse erforderlich - löst den Levelabschluss aus, wenn der Spieler kollidiert.

---

## Upgrade auf Fortgeschritten

Wenn Sie mit dem Anfänger-Preset vertraut sind, sollten Sie ein Upgrade auf **Fortgeschritten** in Betracht ziehen, um Zugang zu erhalten zu:
- Draw-Ereignis (für benutzerdefiniertes Rendering)
- Destroy-Ereignis (Aufräumen, wenn eine Instanz zerstört wird)
- Mausereignisse (Klickerkennung)
- Alarm-Ereignisse (zeitgesteuerte Aktionen)
- Leben- und Gesundheitssysteme
- Sound- und Musikaktionen
- Mehr Bewegungsoptionen (Richtung, auf etwas zubewegen)

---

## Siehe auch

- [Tutorials](Tutorials_de) - Alle Tutorials an einem Ort
- [Fortgeschrittenen-Preset](Intermediate-Preset_de) - Funktionen der nächsten Stufe
- [Vollständige Aktionsreferenz](Full-Action-Reference_de) - Vollständige Aktionsliste
- [Ereignisreferenz](Event-Reference_de) - Vollständige Ereignisliste
- [Ereignisse und Aktionen](Events_und_Aktionen_de) - Kernkonzepte
- [Erstellen Sie Ihr erstes Spiel](Erstes_Spiel_de) - Schritt-für-Schritt-Anleitung
- [Pong Tutorial](Tutorial-Pong_de) - Erstellen Sie ein klassisches Zwei-Spieler Pong-Spiel
- [Breakout Tutorial](Tutorial-Breakout_de) - Erstellen Sie ein klassisches Breakout-Spiel
- [Einführung in die Spieleentwicklung](Getting-Started-Breakout_de) - Umfassendes Anfänger-Tutorial
