# Vollständige Aktionsreferenz

*[Startseite](Home_de) | [Preset-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

Diese Seite dokumentiert alle verfügbaren Aktionen in PyGameMaker. Aktionen sind Befehle, die ausgeführt werden, wenn Ereignisse ausgelöst werden.

## Aktionskategorien

- [Bewegungsaktionen](#bewegungsaktionen)
- [Instanzaktionen](#instanzaktionen)
- [Punkte-, Leben- und Gesundheitsaktionen](#punkte--leben--und-gesundheitsaktionen)
- [Raumaktionen](#raumaktionen)
- [Zeitsteuerungsaktionen](#zeitsteuerungsaktionen)
- [Soundaktionen](#soundaktionen)
- [Zeichenaktionen](#zeichenaktionen)
- [Kontrollflussaktionen](#kontrollflussaktionen)
- [Ausgabeaktionen](#ausgabeaktionen)

---

## Bewegungsaktionen

### Horizontale Geschwindigkeit Setzen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `set_hspeed` |
| **Symbol** | ↔️ |
| **Preset** | Anfänger |

**Beschreibung:** Setzt die horizontale Bewegungsgeschwindigkeit.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `value` | Zahl | 0 | Geschwindigkeit in Pixel/Frame. Positiv=rechts, Negativ=links |

---

### Vertikale Geschwindigkeit Setzen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `set_vspeed` |
| **Symbol** | ↕️ |
| **Preset** | Anfänger |

**Beschreibung:** Setzt die vertikale Bewegungsgeschwindigkeit.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `value` | Zahl | 0 | Geschwindigkeit in Pixel/Frame. Positiv=unten, Negativ=oben |

---

### Bewegung Stoppen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `stop_movement` |
| **Symbol** | 🛑 |
| **Preset** | Anfänger |

**Beschreibung:** Stoppt alle Bewegung (setzt hspeed und vspeed auf 0).

**Parameter:** Keine

---

### Zu Position Springen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `jump_to_position` |
| **Symbol** | 📍 |
| **Preset** | Anfänger |

**Beschreibung:** Bewegt sich sofort zu einer bestimmten Position.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `x` | Zahl | 0 | Ziel-X-Koordinate |
| `y` | Zahl | 0 | Ziel-Y-Koordinate |

---

### Feste Bewegung
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `move_fixed` |
| **Symbol** | ➡️ |
| **Preset** | Fortgeschritten |

**Beschreibung:** Bewegt sich in eine von 8 festen Richtungen.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `directions` | Auswahl | right | Bewegungsrichtung(en) |
| `speed` | Zahl | 4 | Bewegungsgeschwindigkeit |

**Richtungsoptionen:** left, right, up, down, up-left, up-right, down-left, down-right, stop

---

### Freie Bewegung
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `move_free` |
| **Symbol** | 🧭 |
| **Preset** | Fortgeschritten |

**Beschreibung:** Bewegt sich in beliebige Richtung (0-360 Grad).

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `direction` | Zahl | 0 | Richtung in Grad (0=rechts, 90=oben) |
| `speed` | Zahl | 4 | Bewegungsgeschwindigkeit |

---

### Auf Ziel Bewegen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `move_towards` |
| **Symbol** | 🎯 |
| **Preset** | Mittelstufe |

**Beschreibung:** Bewegt sich zu einer Zielposition.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `x` | Ausdruck | 0 | Ziel-X (kann Ausdrücke wie `other.x` verwenden) |
| `y` | Ausdruck | 0 | Ziel-Y |
| `speed` | Zahl | 4 | Bewegungsgeschwindigkeit |

---

### Geschwindigkeit Setzen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `set_speed` |
| **Symbol** | ⚡ |
| **Preset** | Fortgeschritten |

**Beschreibung:** Setzt die Geschwindigkeitsgröße (behält Richtung bei).

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `speed` | Zahl | 0 | Geschwindigkeitsgröße |

---

### Richtung Setzen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `set_direction` |
| **Symbol** | 🧭 |
| **Preset** | Fortgeschritten |

**Beschreibung:** Setzt die Bewegungsrichtung (behält Geschwindigkeit bei).

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `direction` | Zahl | 0 | Richtung in Grad |

---

### Horizontal Umkehren
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `reverse_horizontal` |
| **Symbol** | ↔️ |
| **Preset** | Fortgeschritten |

**Beschreibung:** Kehrt die horizontale Richtung um (multipliziert hspeed mit -1).

**Parameter:** Keine

---

### Vertikal Umkehren
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `reverse_vertical` |
| **Symbol** | ↕️ |
| **Preset** | Fortgeschritten |

**Beschreibung:** Kehrt die vertikale Richtung um (multipliziert vspeed mit -1).

**Parameter:** Keine

---

### Schwerkraft Setzen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `set_gravity` |
| **Symbol** | ⬇️ |
| **Preset** | Platformer |

**Beschreibung:** Wendet Schwerkraft auf die Instanz an.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `direction` | Zahl | 270 | Schwerkraftrichtung (270=unten) |
| `gravity` | Zahl | 0.5 | Schwerkraftstärke |

---

### Reibung Setzen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `set_friction` |
| **Symbol** | 🛑 |
| **Preset** | Fortgeschritten |

**Beschreibung:** Wendet Reibung an (allmähliche Verlangsamung).

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `friction` | Zahl | 0.1 | Reibungsmenge |

---

## Instanzaktionen

### Instanz Zerstören
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `destroy_instance` |
| **Symbol** | 💥 |
| **Preset** | Anfänger |

**Beschreibung:** Entfernt eine Instanz aus dem Spiel.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `target` | Auswahl | self | `self` oder `other` (bei Kollisionsereignissen) |

---

### Instanz Erstellen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `create_instance` |
| **Symbol** | ✨ |
| **Preset** | Anfänger |

**Beschreibung:** Erstellt eine neue Instanz eines Objekts.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `object` | Objekt | - | Zu erstellender Objekttyp |
| `x` | Zahl | 0 | X-Position |
| `y` | Zahl | 0 | Y-Position |

---

### Sprite Setzen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `set_sprite` |
| **Symbol** | 🖼️ |
| **Preset** | Fortgeschritten |

**Beschreibung:** Ändert das Sprite der Instanz.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `sprite` | Sprite | - | Neues Sprite |

---

## Punkte-, Leben- und Gesundheitsaktionen

### Punkte Setzen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `set_score` |
| **Symbol** | 🏆 |
| **Preset** | Anfänger |

**Beschreibung:** Setzt oder ändert die Punkte.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `value` | Zahl | 0 | Punktewert |
| `relative` | Boolean | false | Wenn wahr, zum aktuellen Punktestand addieren |

---

### Punkte Hinzufügen (Kurzbefehl)
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `add_score` |
| **Symbol** | ➕🏆 |
| **Preset** | Anfänger |

**Beschreibung:** Fügt Punkte zum Punktestand hinzu.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `value` | Zahl | 10 | Hinzuzufügende Punkte (negativ zum Abziehen) |

---

### Leben Setzen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `set_lives` |
| **Symbol** | ❤️ |
| **Preset** | Mittelstufe |

**Beschreibung:** Setzt oder ändert die Lebenanzahl.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `value` | Zahl | 3 | Lebenwert |
| `relative` | Boolean | false | Wenn wahr, zu aktuellen Leben addieren |

**Hinweis:** Löst das Ereignis `no_more_lives` aus, wenn 0 erreicht wird.

---

### Leben Hinzufügen (Kurzbefehl)
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `add_lives` |
| **Symbol** | ➕❤️ |
| **Preset** | Mittelstufe |

**Beschreibung:** Fügt Leben hinzu oder entfernt sie.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `value` | Zahl | 1 | Hinzuzufügende Leben (negativ zum Abziehen) |

---

### Gesundheit Setzen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `set_health` |
| **Symbol** | 💚 |
| **Preset** | Mittelstufe |

**Beschreibung:** Setzt oder ändert die Gesundheit (0-100).

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `value` | Zahl | 100 | Gesundheitswert |
| `relative` | Boolean | false | Wenn wahr, zur aktuellen Gesundheit addieren |

**Hinweis:** Löst das Ereignis `no_more_health` aus, wenn 0 erreicht wird.

---

### Gesundheit Hinzufügen (Kurzbefehl)
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `add_health` |
| **Symbol** | ➕💚 |
| **Preset** | Mittelstufe |

**Beschreibung:** Fügt Gesundheit hinzu oder entfernt sie.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `value` | Zahl | 10 | Hinzuzufügende Gesundheit (negativ für Schaden) |

---

### Punkte Zeichnen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `draw_score` |
| **Symbol** | 🖼️🏆 |
| **Preset** | Anfänger |

**Beschreibung:** Zeigt den Punktestand auf dem Bildschirm an.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `x` | Zahl | 10 | X-Position |
| `y` | Zahl | 10 | Y-Position |
| `caption` | Zeichenkette | "Score: " | Text vor dem Punktestand |

---

### Leben Zeichnen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `draw_lives` |
| **Symbol** | 🖼️❤️ |
| **Preset** | Mittelstufe |

**Beschreibung:** Zeigt Leben auf dem Bildschirm an.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `x` | Zahl | 10 | X-Position |
| `y` | Zahl | 30 | Y-Position |
| `sprite` | Sprite | - | Optionales Leben-Symbol-Sprite |

---

### Gesundheitsbalken Zeichnen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `draw_health_bar` |
| **Symbol** | 📊💚 |
| **Preset** | Mittelstufe |

**Beschreibung:** Zeichnet einen Gesundheitsbalken.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `x1` | Zahl | 10 | Linkes X |
| `y1` | Zahl | 50 | Oberes Y |
| `x2` | Zahl | 110 | Rechtes X |
| `y2` | Zahl | 60 | Unteres Y |
| `back_color` | Farbe | gray | Hintergrundfarbe |
| `bar_color` | Farbe | green | Balkenfarbe |

---

## Raumaktionen

### Nächster Raum
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `next_room` |
| **Symbol** | ➡️ |
| **Preset** | Anfänger |

**Beschreibung:** Gehe zum nächsten Raum in der Raumreihenfolge.

**Parameter:** Keine

---

### Vorheriger Raum
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `previous_room` |
| **Symbol** | ⬅️ |
| **Preset** | Anfänger |

**Beschreibung:** Gehe zum vorherigen Raum in der Raumreihenfolge.

**Parameter:** Keine

---

### Raum Neustarten
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `restart_room` |
| **Symbol** | 🔄 |
| **Preset** | Anfänger |

**Beschreibung:** Startet den aktuellen Raum neu.

**Parameter:** Keine

---

### Zu Raum Gehen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `goto_room` |
| **Symbol** | 🚪 |
| **Preset** | Anfänger |

**Beschreibung:** Gehe zu einem bestimmten Raum.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `room` | Raum | - | Zielraum |

---

### Wenn Nächster Raum Existiert
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `if_next_room_exists` |
| **Symbol** | ❓➡️ |
| **Preset** | Anfänger |

**Beschreibung:** Bedingt - führt Aktionen nur aus, wenn es einen nächsten Raum gibt.

| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `then_actions` | Aktionsliste | Aktionen wenn nächster Raum existiert |
| `else_actions` | Aktionsliste | Aktionen wenn kein nächster Raum |

---

### Wenn Vorheriger Raum Existiert
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `if_previous_room_exists` |
| **Symbol** | ❓⬅️ |
| **Preset** | Anfänger |

**Beschreibung:** Bedingt - führt Aktionen nur aus, wenn es einen vorherigen Raum gibt.

| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `then_actions` | Aktionsliste | Aktionen wenn vorheriger Raum existiert |
| `else_actions` | Aktionsliste | Aktionen wenn kein vorheriger Raum |

---

## Zeitsteuerungsaktionen

### Alarm Setzen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `set_alarm` |
| **Symbol** | ⏰ |
| **Preset** | Mittelstufe |

**Beschreibung:** Setzt einen Alarm, der nach einer Verzögerung ausgelöst wird.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `alarm` | Zahl | 0 | Alarmnummer (0-11) |
| `steps` | Zahl | 60 | Schritte bis zur Alarmauslösung |

**Hinweis:** Bei 60 FPS entsprechen 60 Schritte = 1 Sekunde.

---

## Soundaktionen

### Sound Abspielen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `play_sound` |
| **Symbol** | 🔊 |
| **Preset** | Mittelstufe |

**Beschreibung:** Spielt einen Soundeffekt ab.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `sound` | Sound | - | Soundressource |
| `loop` | Boolean | false | Sound wiederholen |

---

### Musik Abspielen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `play_music` |
| **Symbol** | 🎵 |
| **Preset** | Mittelstufe |

**Beschreibung:** Spielt Hintergrundmusik ab.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `sound` | Sound | - | Musikressource |
| `loop` | Boolean | true | Musik wiederholen |

---

### Musik Stoppen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `stop_music` |
| **Symbol** | 🔇 |
| **Preset** | Mittelstufe |

**Beschreibung:** Stoppt alle laufende Musik.

**Parameter:** Keine

---

### Lautstärke Setzen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `set_volume` |
| **Symbol** | 🔉 |
| **Preset** | Fortgeschritten |

**Beschreibung:** Setzt die Audiolautstärke.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `volume` | Zahl | 1.0 | Lautstärkepegel (0.0 bis 1.0) |

---

## Zeichenaktionen

### Text Zeichnen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `draw_text` |
| **Symbol** | 📝 |
| **Preset** | Fortgeschritten |

**Beschreibung:** Zeichnet Text auf dem Bildschirm.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `x` | Zahl | 0 | X-Position |
| `y` | Zahl | 0 | Y-Position |
| `text` | Zeichenkette | "" | Zu zeichnender Text |
| `color` | Farbe | white | Textfarbe |

---

### Rechteck Zeichnen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `draw_rectangle` |
| **Symbol** | ⬛ |
| **Preset** | Fortgeschritten |

**Beschreibung:** Zeichnet ein Rechteck.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `x1` | Zahl | 0 | Linkes X |
| `y1` | Zahl | 0 | Oberes Y |
| `x2` | Zahl | 32 | Rechtes X |
| `y2` | Zahl | 32 | Unteres Y |
| `color` | Farbe | white | Füllfarbe |
| `outline` | Boolean | false | Nur Umriss |

---

### Kreis Zeichnen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `draw_circle` |
| **Symbol** | ⚪ |
| **Preset** | Fortgeschritten |

**Beschreibung:** Zeichnet einen Kreis.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `x` | Zahl | 0 | Mittelpunkt X |
| `y` | Zahl | 0 | Mittelpunkt Y |
| `radius` | Zahl | 16 | Radius |
| `color` | Farbe | white | Füllfarbe |
| `outline` | Boolean | false | Nur Umriss |

---

### Alpha Setzen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `set_alpha` |
| **Symbol** | 👻 |
| **Preset** | Fortgeschritten |

**Beschreibung:** Setzt die Zeichentransparenz.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `alpha` | Zahl | 1.0 | Transparenz (0.0=unsichtbar, 1.0=undurchsichtig) |

---

## Kontrollflussaktionen

### Wenn Kollision Bei
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `if_collision_at` |
| **Symbol** | 🎯 |
| **Preset** | Fortgeschritten |

**Beschreibung:** Prüft auf Kollision an einer Position.

| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `x` | Ausdruck | Zu prüfende X-Position |
| `y` | Ausdruck | Zu prüfende Y-Position |
| `object_type` | Auswahl | `any` oder `solid` |
| `then_actions` | Aktionsliste | Wenn Kollision gefunden |
| `else_actions` | Aktionsliste | Wenn keine Kollision |

---

## Ausgabeaktionen

### Nachricht Anzeigen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `show_message` |
| **Symbol** | 💬 |
| **Preset** | Anfänger |

**Beschreibung:** Zeigt eine Popup-Nachricht an.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `message` | Zeichenkette | "Hello!" | Nachrichtentext |

**Hinweis:** Das Spiel pausiert, während die Nachricht angezeigt wird.

---

### Code Ausführen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `execute_code` |
| **Symbol** | 💻 |
| **Preset** | Anfänger |

**Beschreibung:** Führt benutzerdefinierten Python-Code aus.

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `code` | Code | "" | Auszuführender Python-Code |

**Warnung:** Fortgeschrittene Funktion. Mit Vorsicht verwenden.

---

### Spiel Beenden
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `end_game` |
| **Symbol** | 🚪 |
| **Preset** | Fortgeschritten |

**Beschreibung:** Beendet das Spiel und schließt das Fenster.

**Parameter:** Keine

---

### Spiel Neustarten
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `restart_game` |
| **Symbol** | 🔄 |
| **Preset** | Fortgeschritten |

**Beschreibung:** Startet das Spiel vom ersten Raum neu.

**Parameter:** Keine

---

## Aktionen nach Preset

| Preset | Aktionsanzahl | Kategorien |
|--------|--------------|------------|
| **Anfänger** | 17 | Bewegung, Instanz, Punkte, Raum, Ausgabe |
| **Mittelstufe** | 29 | + Leben, Gesundheit, Sound, Zeitsteuerung |
| **Fortgeschritten** | 40+ | + Zeichnen, Kontrollfluss, Spiel |

---

## Siehe Auch

- [Ereignisreferenz](Event-Reference_de) - Vollständige Ereignisliste
- [Anfänger-Preset](Beginner-Preset_de) - Grundlegende Aktionen für Anfänger
- [Mittelstufe-Preset](Intermediate-Preset_de) - Zusätzliche Aktionen
- [Ereignisse und Aktionen](Events-and-Actions_de) - Übersicht der Kernkonzepte
