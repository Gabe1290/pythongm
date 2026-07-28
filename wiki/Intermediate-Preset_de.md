# Mittelstufen-Preset

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Anfänger-Preset](Beginner-Preset_de)*

Das **Mittelstufen**-Preset baut auf dem [Anfänger-Preset](Beginner-Preset_de) auf, indem es fortgeschrittenere Ereignisse und Aktionen hinzufügt. Es ist für Benutzer konzipiert, die die Grundlagen beherrschen und komplexere Spiele mit Funktionen wie zeitgesteuerten Ereignissen, Sound, Leben und Gesundheitssystemen erstellen möchten.

## Übersicht

Das Mittelstufen-Preset enthält alles vom Anfänger-Preset, plus:
- **4 Zusätzliche Ereignistypen** - Zeichnen, Zerstören, Maus, Alarm
- **12 Zusätzliche Aktionstypen** - Leben, Gesundheit, Sound, Zeitsteuerung und mehr Bewegungsoptionen
- **3 Zusätzliche Kategorien** - Zeitsteuerung, Sound, Zeichnen

---

## Zusätzliche Ereignisse (Über Anfänger hinaus)

### Zeichen-Ereignis
| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_draw` |
| **Kategorie** | Zeichnen |
| **Symbol** | 🎨 |
| **Beschreibung** | Wird ausgelöst, wenn das Objekt gerendert werden muss |

**Wann es ausgelöst wird:** Jeden Frame während der Zeichenphase, nach allen Step-Ereignissen.

**Wichtig:** Wenn Sie ein Zeichen-Ereignis hinzufügen, wird das standardmäßige Sprite-Zeichnen deaktiviert. Sie müssen das Sprite manuell zeichnen, wenn es sichtbar sein soll.

**Häufige Verwendungen:**
- Benutzerdefiniertes Rendering
- Gesundheitsbalken zeichnen
- Text anzeigen
- Formen und Effekte zeichnen
- HUD-Elemente

---

### Zerstören-Ereignis
| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_destroy` |
| **Kategorie** | Objekt |
| **Symbol** | 💥 |
| **Beschreibung** | Wird ausgelöst, wenn die Instanz zerstört wird |

**Wann es ausgelöst wird:** Kurz bevor die Instanz aus dem Spiel entfernt wird.

**Häufige Verwendungen:**
- Explosionseffekte erstellen
- Gegenstände fallen lassen
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
| **Beschreibung** | Wird bei Mausinteraktionen ausgelöst |

**Arten von Maus-Ereignissen:**
- Linke Taste (Drücken, Loslassen, Gehalten)
- Rechte Taste (Drücken, Loslassen, Gehalten)
- Mittlere Taste (Drücken, Loslassen, Gehalten)
- Maus betreten (Cursor betritt Instanz)
- Maus verlassen (Cursor verlässt Instanz)
- Globale Maus-Ereignisse (überall auf dem Bildschirm)

**Häufige Verwendungen:**
- Klickbare Schaltflächen
- Drag and Drop
- Hover-Effekte
- Menüinteraktionen

---

### Alarm-Ereignis
| Eigenschaft | Wert |
|-------------|------|
| **Blockname** | `event_alarm` |
| **Kategorie** | Zeitsteuerung |
| **Symbol** | ⏰ |
| **Beschreibung** | Wird ausgelöst, wenn ein Alarm-Timer null erreicht |

**Wann es ausgelöst wird:** Wenn der entsprechende Alarm-Countdown 0 erreicht.

**Verfügbare Alarme:** 12 unabhängige Alarme (0-11)

**Häufige Verwendungen:**
- Zeitgesteuertes Spawnen
- Verzögerte Aktionen
- Abklingzeiten
- Animations-Timing
- Periodische Ereignisse

---

## Zusätzliche Aktionen (Über Anfänger hinaus)

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
| **Aktionsname** | `move_towards_point` |
| **Blockname** | `move_towards_point` |
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

**Beschreibung:** Einen Alarm setzen, der nach einer Anzahl von Schritten ausgelöst wird.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `alarm` | Zahl | Alarmnummer (0-11) |
| `steps` | Zahl | Schritte bis zum Auslösen des Alarms (bei 60 FPS, 60 Schritte = 1 Sekunde) |

**Beispiel:** Alarm 0 auf 180 Schritte setzen für eine 3-Sekunden-Verzögerung.

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

#### Leben hinzufügen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `add_lives` |
| **Blockname** | `lives_add` |
| **Kategorie** | Score/Leben/Gesundheit |
| **Symbol** | ➕❤️ |

**Beschreibung:** Leben hinzufügen oder abziehen.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `value` | Zahl | Menge zum Hinzufügen (negativ zum Abziehen) |

**Hinweis:** Wenn die Leben 0 erreichen, wird das `no_more_lives`-Ereignis ausgelöst.

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

#### Gesundheit hinzufügen
| Eigenschaft | Wert |
|-------------|------|
| **Aktionsname** | `add_health` |
| **Blockname** | `health_add` |
| **Kategorie** | Score/Leben/Gesundheit |
| **Symbol** | ➕💚 |

**Beschreibung:** Gesundheit hinzufügen oder abziehen.

**Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `value` | Zahl | Menge zum Hinzufügen (negativ für Schaden) |

**Hinweis:** Wenn die Gesundheit 0 erreicht, wird das `no_more_health`-Ereignis ausgelöst.

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
| `loop` | Boolean | Ob wiederholt werden soll (normalerweise wahr für Musik) |

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

## Vollständige Funktionsliste

### Ereignisse im Mittelstufen-Preset

| Ereignis | Kategorie | Beschreibung |
|----------|-----------|--------------|
| Create | Objekt | Instanz erstellt |
| Step | Objekt | Jeden Frame |
| Destroy | Objekt | Instanz zerstört |
| Draw | Zeichnen | Renderphase |
| Keyboard Press | Eingabe | Taste einmal gedrückt |
| Mouse | Eingabe | Mausinteraktionen |
| Collision | Kollision | Instanz-Überlappung |
| Alarm | Zeitsteuerung | Timer erreichte null |

### Aktionen im Mittelstufen-Preset

| Kategorie | Aktionen |
|-----------|----------|
| **Bewegung** | Set H/V Speed, Stop, Jump To, Move Direction, Move Towards Point |
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

Wenn Sie mehr Funktionen benötigen, erwägen Sie:
- **Platformer-Preset** - Schwerkraft, Springen, Plattform-Mechaniken
- **Vollständiges Preset** - Alle verfügbaren Ereignisse und Aktionen

---

## Siehe Auch

- [Anfänger-Preset](Beginner-Preset_de) - Beginnen Sie hier, wenn Sie neu sind
- [Vollständige Aktionsreferenz](Full-Action-Reference_de) - Vollständige Aktionsliste
- [Ereignisreferenz](Event-Reference_de) - Vollständige Ereignisliste
- [Ereignisse und Aktionen](Events_und_Aktionen_de) - Kernkonzepte
