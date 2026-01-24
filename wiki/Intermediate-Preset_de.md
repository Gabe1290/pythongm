# Mittelstufen-Preset

*[Startseite](Home_de) | [Preset-Leitfaden](Preset-Guide_de) | [Anfaenger-Preset](Beginner-Preset_de)*

Das **Mittelstufen**-Preset baut auf dem [Anfaenger-Preset](Beginner-Preset_de) auf, indem es fortgeschrittenere Ereignisse und Aktionen hinzufuegt. Es ist fuer Benutzer konzipiert, die die Grundlagen beherrschen und komplexere Spiele mit Funktionen wie zeitgesteuerten Ereignissen, Sound, Leben und Gesundheitssystemen erstellen moechten.

## Uebersicht

Das Mittelstufen-Preset enthaelt alles vom Anfaenger-Preset, plus:
- **4 Zusaetzliche Ereignistypen** - Zeichnen, Zerstoeren, Maus, Alarm
- **12 Zusaetzliche Aktionstypen** - Leben, Gesundheit, Sound, Zeitsteuerung und mehr Bewegungsoptionen
- **3 Zusaetzliche Kategorien** - Zeitsteuerung, Sound, Zeichnen

---

## Zusaetzliche Ereignisse (Ueber Anfaenger hinaus)

### Zeichen-Ereignis
| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_draw` |
| **Kategorie** | Zeichnen |
| **Symbol** | 🎨 |
| **Beschreibung** | Wird ausgeloest, wenn das Objekt gerendert werden muss |

**Wann es ausgeloest wird:** Jeden Frame waehrend der Zeichenphase, nach allen Step-Ereignissen.

**Wichtig:** Wenn Sie ein Zeichen-Ereignis hinzufuegen, wird das standardmaessige Sprite-Zeichnen deaktiviert. Sie muessen das Sprite manuell zeichnen, wenn es sichtbar sein soll.

**Haeufige Verwendungen:**
- Benutzerdefiniertes Rendering
- Gesundheitsbalken zeichnen
- Text anzeigen
- Formen und Effekte zeichnen
- HUD-Elemente

---

### Zerstoeren-Ereignis
| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_destroy` |
| **Kategorie** | Objekt |
| **Symbol** | 💥 |
| **Beschreibung** | Wird ausgeloest, wenn die Instanz zerstoert wird |

**Wann es ausgeloest wird:** Kurz bevor die Instanz aus dem Spiel entfernt wird.

**Haeufige Verwendungen:**
- Explosionseffekte erstellen
- Gegenstaende fallen lassen
- Todes-Sound abspielen
- Punktestand aktualisieren
- Partikel erzeugen

---

### Maus-Ereignis
| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_mouse` |
| **Kategorie** | Eingabe |
| **Symbol** | 🖱️ |
| **Beschreibung** | Wird bei Mausinteraktionen ausgeloest |

**Arten von Maus-Ereignissen:**
- Linke Taste (Druecken, Loslassen, Gehalten)
- Rechte Taste (Druecken, Loslassen, Gehalten)
- Mittlere Taste (Druecken, Loslassen, Gehalten)
- Maus betreten (Cursor betritt Instanz)
- Maus verlassen (Cursor verlaesst Instanz)
- Globale Maus-Ereignisse (ueberall auf dem Bildschirm)

**Haeufige Verwendungen:**
- Klickbare Schaltflaechen
- Drag and Drop
- Hover-Effekte
- Menuinteraktionen

---

### Alarm-Ereignis
| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_alarm` |
| **Kategorie** | Zeitsteuerung |
| **Symbol** | ⏰ |
| **Beschreibung** | Wird ausgeloest, wenn ein Alarm-Timer null erreicht |

**Wann es ausgeloest wird:** Wenn der entsprechende Alarm-Countdown 0 erreicht.

**Verfuegbare Alarme:** 12 unabhaengige Alarme (0-11)

**Haeufige Verwendungen:**
- Zeitgesteuertes Spawnen
- Verzoegerte Aktionen
- Abklingzeiten
- Animations-Timing
- Periodische Ereignisse

---

## Zusaetzliche Aktionen (Ueber Anfaenger hinaus)

### Bewegungsaktionen

#### In Richtung bewegen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `move_direction` |
| **Blockname** | `move_direction` |
| **Kategorie** | Bewegung |

**Beschreibung:** Bewegung mit Richtung (0-360 Grad) und Geschwindigkeit festlegen.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `direction` | Zahl | Richtung in Grad (0=rechts, 90=oben, 180=links, 270=unten) |
| `speed` | Zahl | Bewegungsgeschwindigkeit |

---

#### Auf Punkt zubewegen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `move_towards` |
| **Blockname** | `move_towards` |
| **Kategorie** | Bewegung |

**Beschreibung:** Auf eine bestimmte Position zubewegen.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `x` | Zahl/Ausdruck | Ziel-X-Koordinate |
| `y` | Zahl/Ausdruck | Ziel-Y-Koordinate |
| `speed` | Zahl | Bewegungsgeschwindigkeit |

---

### Zeitsteuerungsaktionen

#### Alarm setzen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `set_alarm` |
| **Blockname** | `set_alarm` |
| **Kategorie** | Zeitsteuerung |
| **Symbol** | ⏰ |

**Beschreibung:** Einen Alarm setzen, der nach einer Anzahl von Schritten ausgeloest wird.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `alarm` | Zahl | Alarmnummer (0-11) |
| `steps` | Zahl | Schritte bis zum Ausloesen des Alarms (bei 60 FPS, 60 Schritte = 1 Sekunde) |

**Beispiel:** Alarm 0 auf 180 Schritte setzen fuer eine 3-Sekunden-Verzoegerung.

---

### Leben-Aktionen

#### Leben setzen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `set_lives` |
| **Blockname** | `lives_set` |
| **Kategorie** | Score/Leben/Gesundheit |
| **Symbol** | ❤️ |

**Beschreibung:** Die Anzahl der Leben festlegen.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `value` | Zahl | Leben-Wert |
| `relative` | Boolean | Wenn wahr, wird zu den aktuellen Leben addiert |

---

#### Leben hinzufuegen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `add_lives` |
| **Blockname** | `lives_add` |
| **Kategorie** | Score/Leben/Gesundheit |
| **Symbol** | ➕❤️ |

**Beschreibung:** Leben hinzufuegen oder abziehen.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `value` | Zahl | Menge zum Hinzufuegen (negativ zum Abziehen) |

**Hinweis:** Wenn die Leben 0 erreichen, wird das `no_more_lives`-Ereignis ausgeloest.

---

#### Leben zeichnen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `draw_lives` |
| **Blockname** | `draw_lives` |
| **Kategorie** | Score/Leben/Gesundheit |
| **Symbol** | 🖼️❤️ |

**Beschreibung:** Leben auf dem Bildschirm anzeigen.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `x` | Zahl | X-Position |
| `y` | Zahl | Y-Position |
| `sprite` | Sprite | Optionales Sprite als Lebens-Symbol |

---

### Gesundheitsaktionen

#### Gesundheit setzen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `set_health` |
| **Blockname** | `health_set` |
| **Kategorie** | Score/Leben/Gesundheit |
| **Symbol** | 💚 |

**Beschreibung:** Den Gesundheitswert festlegen (0-100).

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `value` | Zahl | Gesundheitswert (0-100) |
| `relative` | Boolean | Wenn wahr, wird zur aktuellen Gesundheit addiert |

---

#### Gesundheit hinzufuegen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `add_health` |
| **Blockname** | `health_add` |
| **Kategorie** | Score/Leben/Gesundheit |
| **Symbol** | ➕💚 |

**Beschreibung:** Gesundheit hinzufuegen oder abziehen.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `value` | Zahl | Menge zum Hinzufuegen (negativ fuer Schaden) |

**Hinweis:** Wenn die Gesundheit 0 erreicht, wird das `no_more_health`-Ereignis ausgeloest.

---

#### Gesundheitsbalken zeichnen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `draw_health_bar` |
| **Blockname** | `draw_health_bar` |
| **Kategorie** | Score/Leben/Gesundheit |
| **Symbol** | 📊💚 |

**Beschreibung:** Einen Gesundheitsbalken auf dem Bildschirm zeichnen.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `x1` | Zahl | Linke X-Position |
| `y1` | Zahl | Obere Y-Position |
| `x2` | Zahl | Rechte X-Position |
| `y2` | Zahl | Untere Y-Position |
| `back_color` | Farbe | Hintergrundfarbe |
| `bar_color` | Farbe | Gesundheitsbalken-Farbe |

---

### Sound-Aktionen

#### Sound abspielen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `play_sound` |
| **Blockname** | `sound_play` |
| **Kategorie** | Sound |
| **Symbol** | 🔊 |

**Beschreibung:** Einen Soundeffekt abspielen.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `sound` | Sound | Abzuspielende Sound-Ressource |
| `loop` | Boolean | Ob der Sound wiederholt werden soll |

---

#### Musik abspielen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `play_music` |
| **Blockname** | `music_play` |
| **Kategorie** | Sound |
| **Symbol** | 🎵 |

**Beschreibung:** Hintergrundmusik abspielen.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `sound` | Sound | Abzuspielende Musik-Ressource |
| `loop` | Boolean | Ob wiederholt werden soll (normalerweise wahr fuer Musik) |

---

#### Musik stoppen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `stop_music` |
| **Blockname** | `music_stop` |
| **Kategorie** | Sound |
| **Symbol** | 🔇 |

**Beschreibung:** Alle aktuell abgespielte Musik stoppen.

**Parameter:** Keine

---

## Vollstaendige Funktionsliste

### Ereignisse im Mittelstufen-Preset

| Ereignis | Kategorie | Beschreibung |
|----------|-----------|--------------|
| Create | Objekt | Instanz erstellt |
| Step | Objekt | Jeden Frame |
| Destroy | Objekt | Instanz zerstoert |
| Draw | Zeichnen | Renderphase |
| Keyboard Press | Eingabe | Taste einmal gedrueckt |
| Mouse | Eingabe | Mausinteraktionen |
| Collision | Kollision | Instanz-Ueberlappung |
| Alarm | Zeitsteuerung | Timer erreichte null |

### Aktionen im Mittelstufen-Preset

| Kategorie | Aktionen |
|-----------|----------|
| **Bewegung** | Set H/V Speed, Stop, Jump To, Move Direction, Move Towards |
| **Instanz** | Create, Destroy |
| **Score** | Set Score, Add Score, Draw Score |
| **Leben** | Set Lives, Add Lives, Draw Lives |
| **Gesundheit** | Set Health, Add Health, Draw Health Bar |
| **Raum** | Next, Previous, Restart, Go To, If Next/Previous Exists |
| **Zeitsteuerung** | Set Alarm |
| **Sound** | Play Sound, Play Music, Stop Music |
| **Ausgabe** | Show Message, Execute Code |

---

## Beispiel: Shooter-Spiel mit Leben

### Spieler-Objekt

**Create:**
- Set Lives: 3

**Keyboard Press (Leertaste):**
- Create Instance: obj_bullet bei (x, y-20)
- Set Alarm: 0 auf 15 (Abklingzeit)

**Kollision mit obj_enemy:**
- Add Lives: -1
- Play Sound: snd_hurt
- Jump to Position: (320, 400)

**No More Lives:**
- Show Message: "Game Over!"
- Restart Room

### Feind-Objekt

**Create:**
- Set Alarm: 0 auf 60

**Alarm 0:**
- Create Instance: obj_enemy_bullet bei (x, y+20)
- Set Alarm: 0 auf 60 (wiederholen)

**Kollision mit obj_bullet:**
- Add Score: 100
- Play Sound: snd_explosion
- Destroy Instance: self

---

## Upgrade auf Fortgeschrittene Presets

Wenn Sie mehr Funktionen benoetigen, erwaegen Sie:
- **Platformer-Preset** - Schwerkraft, Springen, Plattform-Mechaniken
- **Vollstaendiges Preset** - Alle verfuegbaren Ereignisse und Aktionen

---

## Siehe Auch

- [Anfaenger-Preset](Beginner-Preset_de) - Beginnen Sie hier, wenn Sie neu sind
- [Vollstaendige Aktionsreferenz](Full-Action-Reference_de) - Vollstaendige Aktionsliste
- [Ereignisreferenz](Event-Reference_de) - Vollstaendige Ereignisliste
- [Ereignisse und Aktionen](Events-and-Actions_de) - Kernkonzepte
