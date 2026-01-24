# Ereignis-Referenz

*[Startseite](Home_de) | [Preset-Leitfaden](Preset-Guide_de) | [Vollstaendige Aktionsreferenz](Full-Action-Reference_de)*

Diese Seite dokumentiert alle verfuegbaren Ereignisse in PyGameMaker. Ereignisse sind Ausloeser, die Aktionen ausfuehren, wenn bestimmte Bedingungen in Ihrem Spiel auftreten.

## Ereigniskategorien

- [Objekt-Ereignisse](#objekt-ereignisse) - Create, Step, Destroy
- [Eingabe-Ereignisse](#eingabe-ereignisse) - Tastatur, Maus
- [Kollisions-Ereignisse](#kollisions-ereignisse) - Objektkollisionen
- [Zeit-Ereignisse](#zeit-ereignisse) - Alarme, Step-Varianten
- [Zeichen-Ereignisse](#zeichen-ereignisse) - Benutzerdefiniertes Rendern
- [Raum-Ereignisse](#raum-ereignisse) - Raumuebergaenge
- [Spiel-Ereignisse](#spiel-ereignisse) - Spielstart/-ende
- [Andere Ereignisse](#andere-ereignisse) - Grenzen, Leben, Gesundheit

---

## Objekt-Ereignisse

### Create
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `create` |
| **Symbol** | 🎯 |
| **Kategorie** | Objekt |
| **Preset** | Anfaenger |

**Beschreibung:** Wird einmal ausgefuehrt, wenn eine Instanz erstmals erstellt wird.

**Wann es ausloest:**
- Wenn eine Instanz beim Spielstart in einem Raum platziert wird
- Wenn sie ueber die Aktion "Instanz erstellen" erstellt wird
- Nach Raumuebergaengen fuer neue Instanzen

**Haeufige Verwendungen:**
- Variablen initialisieren
- Startwerte setzen
- Anfangszustand konfigurieren

---

### Step
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `step` |
| **Symbol** | ⭐ |
| **Kategorie** | Objekt |
| **Preset** | Anfaenger |

**Beschreibung:** Wird jeden Frame ausgefuehrt (typischerweise 60 Mal pro Sekunde).

**Wann es ausloest:** Kontinuierlich, jeden Spielframe.

**Haeufige Verwendungen:**
- Kontinuierliche Bewegung
- Bedingungen pruefen
- Positionen aktualisieren
- Spiellogik

**Hinweis:** Achten Sie auf die Leistung - Code hier laeuft staendig.

---

### Destroy
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `destroy` |
| **Symbol** | 💥 |
| **Kategorie** | Objekt |
| **Preset** | Fortgeschritten |

**Beschreibung:** Wird ausgefuehrt, wenn eine Instanz zerstoert wird.

**Wann es ausloest:** Kurz bevor die Instanz aus dem Spiel entfernt wird.

**Haeufige Verwendungen:**
- Effekte erzeugen (Explosionen, Partikel)
- Gegenstaende fallen lassen
- Punktestaende aktualisieren
- Sounds abspielen

---

## Eingabe-Ereignisse

### Tastatur (Kontinuierlich)
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `keyboard` |
| **Symbol** | ⌨️ |
| **Kategorie** | Eingabe |
| **Preset** | Anfaenger |

**Beschreibung:** Loest kontinuierlich aus, waehrend eine Taste gedrueckt gehalten wird.

**Am besten fuer:** Fluessige, kontinuierliche Bewegung

**Unterstuetzte Tasten:**
- Pfeiltasten (hoch, runter, links, rechts)
- Buchstaben (A-Z)
- Zahlen (0-9)
- Leertaste, Enter, Escape
- Funktionstasten (F1-F12)
- Modifikatortasten (Shift, Strg, Alt)

---

### Tastendruck
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `keyboard_press` |
| **Symbol** | 🔘 |
| **Kategorie** | Eingabe |
| **Preset** | Anfaenger |

**Beschreibung:** Loest einmal aus, wenn eine Taste zum ersten Mal gedrueckt wird.

**Am besten fuer:** Einzelaktionen (Springen, Schiessen, Menuauswahl)

**Unterschied zu Tastatur:** Loest nur einmal pro Druck aus, nicht waehrend des Haltens.

---

### Taste Loslassen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `keyboard_release` |
| **Symbol** | ⬆️ |
| **Kategorie** | Eingabe |
| **Preset** | Experte |

**Beschreibung:** Loest einmal aus, wenn eine Taste losgelassen wird.

**Haeufige Verwendungen:**
- Bewegung stoppen, wenn Taste losgelassen
- Ladeattacken beenden
- Zustaende umschalten

---

### Maus
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `mouse` |
| **Symbol** | 🖱️ |
| **Kategorie** | Eingabe |
| **Preset** | Fortgeschritten |

**Beschreibung:** Maustasten- und Bewegungsereignisse.

**Ereignistypen:**

| Typ | Beschreibung |
|-----|--------------|
| Linke Taste | Klick mit linker Maustaste |
| Rechte Taste | Klick mit rechter Maustaste |
| Mittlere Taste | Klick mit mittlerer/Scroll-Taste |
| Maus Eintritt | Cursor betritt Instanzgrenzen |
| Maus Austritt | Cursor verlaesst Instanzgrenzen |
| Globale Linke Taste | Linksklick ueberall |
| Globale Rechte Taste | Rechtsklick ueberall |

---

## Kollisions-Ereignisse

### Kollision
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `collision` |
| **Symbol** | 💥 |
| **Kategorie** | Kollision |
| **Preset** | Anfaenger |

**Beschreibung:** Loest aus, wenn diese Instanz mit einem anderen Objekttyp ueberlappt.

**Konfiguration:** Waehlen Sie, welcher Objekttyp diese Kollision ausloest.

**Spezielle Variable:** `other` - Verweis auf die kollidierende Instanz.

**Wann es ausloest:** Jeden Frame, in dem Instanzen ueberlappen.

**Haeufige Verwendungen:**
- Gegenstaende sammeln
- Schaden nehmen
- Waende treffen
- Ereignisse ausloesen

**Beispiel-Kollisionsereignisse:**
- `collision_with_obj_coin` - Spieler beruehrt eine Muenze
- `collision_with_obj_enemy` - Spieler beruehrt einen Gegner
- `collision_with_obj_wall` - Instanz trifft eine Wand

---

## Zeit-Ereignisse

### Alarm
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `alarm` |
| **Symbol** | ⏰ |
| **Kategorie** | Zeit |
| **Preset** | Fortgeschritten |

**Beschreibung:** Loest aus, wenn ein Alarm-Countdown null erreicht.

**Verfuegbare Alarme:** 12 unabhaengige Alarme (alarm[0] bis alarm[11])

**Alarme einstellen:** Verwenden Sie die Aktion "Alarm setzen" mit Steps (60 Steps ≈ 1 Sekunde bei 60 FPS)

**Haeufige Verwendungen:**
- Zeitgesteuertes Spawnen
- Abklingzeiten
- Verzoegerte Effekte
- Wiederholende Aktionen (Alarm im Alarmereignis erneut setzen)

---

### Begin Step
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `begin_step` |
| **Symbol** | ▶️ |
| **Kategorie** | Step |
| **Preset** | Experte |

**Beschreibung:** Loest am Anfang jedes Frames aus, vor regulaeren Step-Ereignissen.

**Ausfuehrungsreihenfolge:** Begin Step → Step → End Step

**Haeufige Verwendungen:**
- Eingabeverarbeitung
- Vor-Bewegungs-Berechnungen

---

### End Step
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `end_step` |
| **Symbol** | ⏹️ |
| **Kategorie** | Step |
| **Preset** | Experte |

**Beschreibung:** Loest am Ende jedes Frames aus, nach Kollisionen.

**Haeufige Verwendungen:**
- Endgueltige Positionsanpassungen
- Aufraeumoperationen
- Zustandsaktualisierungen nach Kollisionen

---

## Zeichen-Ereignisse

### Draw
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `draw` |
| **Symbol** | 🎨 |
| **Kategorie** | Zeichnen |
| **Preset** | Fortgeschritten |

**Beschreibung:** Loest waehrend der Renderphase aus.

**Wichtig:** Das Hinzufuegen eines Draw-Ereignisses deaktiviert das automatische Sprite-Zeichnen. Sie muessen das Sprite manuell zeichnen, wenn es sichtbar sein soll.

**Haeufige Verwendungen:**
- Benutzerdefiniertes Rendern
- Formen zeichnen
- Text anzeigen
- Gesundheitsbalken
- HUD-Elemente

**Verfuegbare Zeichenaktionen:**
- Sprite zeichnen
- Text zeichnen
- Rechteck zeichnen
- Kreis zeichnen
- Linie zeichnen
- Gesundheitsbalken zeichnen

---

## Raum-Ereignisse

### Room Start
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `room_start` |
| **Symbol** | 🚪 |
| **Kategorie** | Raum |
| **Preset** | Experte |

**Beschreibung:** Loest beim Betreten eines Raums aus, nach allen Create-Ereignissen.

**Haeufige Verwendungen:**
- Raum-Initialisierung
- Raum-Musik abspielen
- Raumspezifische Variablen setzen

---

### Room End
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `room_end` |
| **Symbol** | 🚪 |
| **Kategorie** | Raum |
| **Preset** | Experte |

**Beschreibung:** Loest beim Verlassen eines Raums aus.

**Haeufige Verwendungen:**
- Fortschritt speichern
- Musik stoppen
- Aufraeumen

---

## Spiel-Ereignisse

### Game Start
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `game_start` |
| **Symbol** | 🎮 |
| **Kategorie** | Spiel |
| **Preset** | Experte |

**Beschreibung:** Loest einmal aus, wenn das Spiel zum ersten Mal startet (nur im ersten Raum).

**Haeufige Verwendungen:**
- Globale Variablen initialisieren
- Gespeicherte Daten laden
- Intro abspielen

---

### Game End
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `game_end` |
| **Symbol** | 🎮 |
| **Kategorie** | Spiel |
| **Preset** | Experte |

**Beschreibung:** Loest aus, wenn das Spiel endet.

**Haeufige Verwendungen:**
- Spieldaten speichern
- Ressourcen aufraeumen

---

## Andere Ereignisse

### Outside Room
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `outside_room` |
| **Symbol** | 🚫 |
| **Kategorie** | Andere |
| **Preset** | Experte |

**Beschreibung:** Loest aus, wenn die Instanz vollstaendig ausserhalb der Raumgrenzen ist.

**Haeufige Verwendungen:**
- Kugeln ausserhalb des Bildschirms zerstoeren
- Auf die andere Seite wechseln
- Game Over ausloesen

---

### Intersect Boundary
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `intersect_boundary` |
| **Symbol** | ⚠️ |
| **Kategorie** | Andere |
| **Preset** | Experte |

**Beschreibung:** Loest aus, wenn die Instanz die Raumgrenze beruehrt.

**Haeufige Verwendungen:**
- Spieler in Grenzen halten
- Von Raendern abprallen

---

### No More Lives
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `no_more_lives` |
| **Symbol** | 💀 |
| **Kategorie** | Andere |
| **Preset** | Fortgeschritten |

**Beschreibung:** Loest aus, wenn Leben 0 oder weniger werden.

**Haeufige Verwendungen:**
- Game-Over-Bildschirm
- Spiel neu starten
- Endpunktestand anzeigen

---

### No More Health
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `no_more_health` |
| **Symbol** | 💔 |
| **Kategorie** | Andere |
| **Preset** | Fortgeschritten |

**Beschreibung:** Loest aus, wenn Gesundheit 0 oder weniger wird.

**Haeufige Verwendungen:**
- Ein Leben verlieren
- Spieler respawnen
- Todesanimation ausloesen

---

## Ereignis-Ausfuehrungsreihenfolge

Das Verstaendnis, wann Ereignisse ausloesen, hilft dabei, vorhersehbares Spielverhalten zu erstellen:

1. **Begin Step** - Anfang des Frames
2. **Alarm** - Alle ausgeloesten Alarme
3. **Keyboard/Mouse** - Eingabeereignisse
4. **Step** - Haupt-Spiellogik
5. **Collision** - Nach Bewegung
6. **End Step** - Nach Kollisionen
7. **Draw** - Renderphase

---

## Ereignisse nach Preset

| Preset | Enthaltene Ereignisse |
|--------|----------------------|
| **Anfaenger** | Create, Step, Keyboard Press, Collision |
| **Fortgeschritten** | + Draw, Destroy, Mouse, Alarm |
| **Experte** | + Alle Tastaturvarianten, Begin/End Step, Raum-Ereignisse, Spiel-Ereignisse, Grenzereignisse |

---

## Siehe Auch

- [Vollstaendige Aktionsreferenz](Full-Action-Reference_de) - Vollstaendige Aktionsliste
- [Anfaenger-Preset](Beginner-Preset_de) - Wesentliche Ereignisse fuer Anfaenger
- [Fortgeschrittenen-Preset](Intermediate-Preset_de) - Zusaetzliche Ereignisse
- [Ereignisse und Aktionen](Events-and-Actions_de) - Ueberblick ueber Kernkonzepte
