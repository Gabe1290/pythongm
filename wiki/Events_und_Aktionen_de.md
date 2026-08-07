# Events und Aktionen

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

> [Zurück zur Startseite](Home_de)

Dies ist eine vollständige Referenz aller Events und Aktionen, die in PyGameMaker verfügbar sind.

---

## Event-Referenz

### Create-Event
**Wann:** Einmal, wenn eine Instanz erstellt wird
**Verwendung:** Initialisierung, Variablen festlegen, Timer starten

### Destroy-Event
**Wann:** Wenn die Instanz zerstört wird
**Verwendung:** Aufräumen, Effekte erzeugen, Punkte vergeben

### Step-Events

| Event | Wann |
|-----------|-------|
| **Step** | Bei jedem Frame (60-mal pro Sekunde) |
| **Begin Step** | Vor den Kollisionsprüfungen |
| **End Step** | Nach allen anderen Events |

### Alarm-Events

| Event | Wann |
|-----------|-------|
| **Alarm[0-11]** | Wenn der Zähler 0 erreicht |

Verwenden Sie die Aktion `Set Alarm`, um einen Countdown zu starten. Alarmwerte sind in Frames (60 = 1 Sekunde bei 60 FPS).

### Tastatur-Events

| Event | Wann |
|-----------|-------|
| **Keyboard [Taste]** | Solange die Taste gehalten wird (wiederholt) |
| **Key Press [Taste]** | Einmal, wenn die Taste gedrückt wird |
| **Key Release [Taste]** | Einmal, wenn die Taste losgelassen wird |
| **No Key** | Wenn keine Taste gedrückt ist |

Verfügbare Tasten: Buchstaben (A-Z), Zahlen (0-9), Pfeiltasten, Leertaste, Enter, Umschalt, Strg, Alt, Funktionstasten (F1-F12)

### Maus-Events

| Event | Wann |
|-----------|-------|
| **Left Button** | Linksklick auf die Instanz |
| **Right Button** | Rechtsklick auf die Instanz |
| **Middle Button** | Klick mit mittlerer Maustaste auf die Instanz |
| **Left Press** | Linke Maustaste gedrückt (einmal) |
| **Left Release** | Linke Maustaste losgelassen (einmal) |
| **Mouse Enter** | Der Cursor betritt die Instanz |
| **Mouse Leave** | Der Cursor verlässt die Instanz |
| **Global Left Button** | Linksklick irgendwo |
| **Global Right Button** | Rechtsklick irgendwo |

### Kollisions-Events

| Event | Wann |
|-----------|-------|
| **Collision with [Objekt]** | Bei Berührung mit dem angegebenen Objekt |

Kollisionsprüfungen finden zwischen den Events Step und Draw statt.

### Sonstige Events

| Event | Wann |
|-----------|-------|
| **Outside Room** | Die Instanz ist vollständig außerhalb des Rooms |
| **Intersect Boundary** | Die Instanz berührt den Rand des Rooms |
| **Game Start** | Das Spiel startet (erster Room geladen) |
| **Game End** | Das Spiel wird beendet |
| **Room Start** | Beim Betreten eines Rooms |
| **Room End** | Beim Verlassen eines Rooms |
| **No More Lives** | Die Leben erreichen 0 |
| **No More Health** | Die Gesundheit erreicht 0 |
| **Animation End** | Die Sprite-Animation ist abgeschlossen |

### Draw-Events

| Event | Wann |
|-----------|-------|
| **Draw** | Während der Renderphase |
| **Draw GUI** | Nach dem Zeichnen des Rooms (Bildschirmraum) |

---

## Aktions-Referenz

### Bewegungs-Aktionen

| Aktion | Beschreibung | Parameter |
|--------|-------------|------------|
| **Geschwindigkeit setzen** | Bewegungsgeschwindigkeit festlegen | Geschwindigkeit, relativ |
| **Richtung setzen** | Richtung festlegen | Richtung (0-360), relativ |
| **Set Horizontal Speed** | hspeed festlegen | hspeed, relativ |
| **Set Vertical Speed** | vspeed festlegen | vspeed, relativ |
| **Set Gravity** | Schwerkraft festlegen | gravity, direction |
| **Set Friction** | Reibung festlegen | friction |
| **Zu Punkt bewegen** | Zu Koordinaten bewegen | x, y, Geschwindigkeit |
| **Losbewegen (Richtung)** | In eine Richtung bewegen | direction, Geschwindigkeit |
| **Jump To Position** | Zu Koordinaten teleportieren | x, y, relativ |
| **Zur Startposition springen** | Zurück zur Erstellungsposition | - |
| **Zu zufälliger Position springen** | Teleportation an eine vollständig zufällige Position (beide Achsen; am Gitter ausrichtbar) | snap_h, snap_v |
| **Abprallen** | Von soliden Objekten abprallen | precise |

### Instanz-Aktionen

| Aktion | Beschreibung | Parameter |
|--------|-------------|------------|
| **Create Instance** | Neues Objekt erzeugen | object, x, y, relativ |
| **Create Moving Instance** | Mit Geschwindigkeit erzeugen | object, x, y, speed, direction |
| **Destroy Instance** | Instanz entfernen | - |
| **Change Instance** | In ein anderes Objekt verwandeln | object, perform_events |

### Zeitsteuerungs-Aktionen

| Aktion | Beschreibung | Parameter |
|--------|-------------|------------|
| **Set Alarm** | Countdown starten | alarm_number, steps |
| **Sleep** | Ausführung pausieren | Millisekunden |

### Score/Leben/Gesundheit-Aktionen

| Aktion | Beschreibung | Parameter |
|--------|-------------|------------|
| **Set Score** | Score ändern | value, relativ |
| **Set Lives** | Leben ändern | value, relativ |
| **Set Health** | Gesundheit ändern | value, relativ |
| **Punkte zeichnen** | Score anzeigen | x, y, caption |
| **Leben zeichnen** | Leben als wiederholte Sprite-Bilder anzeigen | x, y, sprite, scale, tiled |
| **Gesundheitsbalken zeichnen** | Gesundheit als zweifarbigen Balken anzeigen | x1, y1, x2, y2, back_color, bar_color |

### Zeichen-Aktionen

| Aktion | Beschreibung | Parameter |
|--------|-------------|------------|
| **Draw Sprite** | Sprite zeichnen | sprite, x, y, subimage |
| **Draw Text** | Text anzeigen | x, y, text |
| **Draw Rectangle** | Rechteck zeichnen | x1, y1, x2, y2, filled |
| **Draw Circle** | Kreis zeichnen | x, y, radius, filled |
| **Draw Line** | Linie zeichnen | x1, y1, x2, y2 |
| **Zeichenfarbe festlegen** | Farbe für nachfolgende Draw Text/Draw Rectangle/etc. festlegen | color |
| **Farbe setzen** | Farbton und Transparenz eines Sprites festlegen (nicht die Zeichenfarbe oben) | color, alpha |
| **Zeichenschrift festlegen** | Schrift und Ausrichtung für den nächsten Textzeichenvorgang festlegen | font, halign, valign |

### Room-Aktionen

| Aktion | Beschreibung | Parameter |
|--------|-------------|------------|
| **Next Room** | Zum nächsten Room gehen | transition |
| **Previous Room** | Zum vorherigen Room gehen | transition |
| **Restart Room** | Room zurücksetzen | - |
| **Go to Room** | Zu einem bestimmten Room springen | room, transition |
| **If Next Room Exists** | Prüfen, ob ein nächster Room existiert | - |
| **If Previous Room Exists** | Prüfen, ob ein vorheriger Room existiert | - |

### Sound-Aktionen

| Aktion | Beschreibung | Parameter |
|--------|-------------|------------|
| **Play Sound** | Soundeffekt abspielen | sound, loop |
| **Stop Sound** | Sound stoppen | sound |
| **Check Sound Playing** | Prüfen, ob ein Sound abgespielt wird | sound |
| **Play Music** | Hintergrundmusik abspielen | music, loop |
| **Stop Music** | Alle Musik stoppen | - |

### Variablen-Aktionen

| Aktion | Beschreibung | Parameter |
|--------|-------------|------------|
| **Set Variable** | Wert zuweisen | variable, value, relativ |
| **Variable testen** | Wert prüfen | variable, value, operation |
| **Variable zeichnen** | Variable anzeigen | x, y, variable |

### Kontrollfluss-Aktionen

| Aktion | Beschreibung | Parameter |
|--------|-------------|------------|
| **Ausdruck testen** | Bedingungsprüfung (ein boolescher Python-Ausdruck) | expression |
| **Sonst** | Alternativer Zweig | - |
| **Start Block** | Aktionsgruppe beginnen | - |
| **End Block** | Aktionsgruppe beenden | - |
| **Repeat** | N-mal wiederholen | count |
| **Exit Event** | Aktuelles Event stoppen | - |

### Sonstige Aktionen

| Aktion | Beschreibung | Parameter |
|--------|-------------|------------|
| **Show Message** | Popup-Nachricht anzeigen | message |
| **Restart Game** | Spiel neu starten | - |
| **End Game** | Spiel schließen | - |

---

## Eingebaute Variablen

Diese Variablen sind für alle Instanzen verfügbar:

| Variable | Beschreibung |
|----------|-------------|
| `x` | Horizontale Position |
| `y` | Vertikale Position |
| `xstart` | Start-x-Position |
| `ystart` | Start-y-Position |
| `hspeed` | Horizontale Geschwindigkeit |
| `vspeed` | Vertikale Geschwindigkeit |
| `speed` | Sprite-Animationsrate (Bilder pro Sekunde) — **nicht** die Bewegungsgeschwindigkeit. Es gibt keine eingebaute Variable für die "Gesamtgeschwindigkeit"; berechnen Sie sie selbst aus `hspeed`/`vspeed`, z. B. `(hspeed**2 + vspeed**2)**0.5` |
| `direction` | Bewegungsrichtung (0-360) |
| `gravity` | Schwerkraft |
| `gravity_direction` | Richtung der Schwerkraft |
| `friction` | Bewegungsreibung |
| `image_index` | Aktuelles Animations-Frame |
| `image_speed` | Animationsgeschwindigkeit |
| `image_xscale` | Horizontale Skalierung |
| `image_yscale` | Vertikale Skalierung |
| `image_angle` | Rotationswinkel |
| `visible` | Ob gezeichnet wird |
| `solid` | Ob solide für Kollisionen |
| `depth` | Zeichentiefe |
| `sprite_index` | Aktuelles Sprite |
| `alarm[0-11]` | Alarm-Timer |

### Globale Variablen

| Variable | Beschreibung |
|----------|-------------|
| `score` | Spielstand |
| `lives` | Leben des Spielers |
| `health` | Gesundheit des Spielers (0-100) |
| `room` | Aktueller Room |
| `room_width` | Breite des aktuellen Rooms |
| `room_height` | Höhe des aktuellen Rooms |
| `mouse_x` | X-Position der Maus |
| `mouse_y` | Y-Position der Maus |

---

## Nächste Schritte

- [[Visuelle_Programmierung_de]] - Verwenden Sie Blockly-Blöcke für dieselbe Logik
- [[Objekt_Editor_de]] - Wenden Sie Events und Aktionen auf Objekte an
- [[Erstes_Spiel_de]] - Sehen Sie Events in Aktion
