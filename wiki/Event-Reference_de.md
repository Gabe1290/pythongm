# Ereignis-Referenz

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Vollständige Aktionsreferenz](Full-Action-Reference_de)*

Diese Seite dokumentiert alle verfügbaren Ereignisse in PyGameMaker. Ereignisse sind Auslöser, die Aktionen ausführen, wenn bestimmte Bedingungen in Ihrem Spiel auftreten.

## Ereigniskategorien

- [Objekt-Ereignisse](#objekt-ereignisse) - Create, Step, Destroy
- [Eingabe-Ereignisse](#eingabe-ereignisse) - Tastatur, Maus
- [Kollisions-Ereignisse](#kollisions-ereignisse) - Objektkollisionen
- [Zeit-Ereignisse](#zeit-ereignisse) - Alarme, Step-Varianten
- [Zeichen-Ereignisse](#zeichen-ereignisse) - Benutzerdefiniertes Rendern
- [Raum-Ereignisse](#raum-ereignisse) - Raumübergänge
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
| **Preset** | Anfänger |

**Beschreibung:** Wird einmal ausgeführt, wenn eine Instanz erstmals erstellt wird.

**Wann es auslöst:**
- Wenn eine Instanz beim Spielstart in einem Raum platziert wird
- Wenn sie über die Aktion „Instanz erstellen" erstellt wird
- Nach Raumübergängen für neue Instanzen

**Häufige Verwendungen:**
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
| **Preset** | Anfänger |

**Beschreibung:** Wird jeden Frame ausgeführt (typischerweise 60 Mal pro Sekunde).

**Wann es auslöst:** Kontinuierlich, jeden Spielframe.

**Häufige Verwendungen:**
- Kontinuierliche Bewegung
- Bedingungen prüfen
- Positionen aktualisieren
- Spiellogik

**Hinweis:** Achten Sie auf die Leistung — Code hier läuft ständig.

---

### Destroy
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `destroy` |
| **Symbol** | 💥 |
| **Kategorie** | Objekt |
| **Preset** | Fortgeschritten |

**Beschreibung:** Wird ausgeführt, wenn eine Instanz zerstört wird.

**Wann es auslöst:** Kurz bevor die Instanz aus dem Spiel entfernt wird.

**Häufige Verwendungen:**
- Effekte erzeugen (Explosionen, Partikel)
- Gegenstände fallen lassen
- Punktestände aktualisieren
- Sounds abspielen

---

## Eingabe-Ereignisse

### Tastatur (Kontinuierlich)
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `keyboard` |
| **Symbol** | ⌨️ |
| **Kategorie** | Eingabe |
| **Preset** | Anfänger |

**Beschreibung:** Löst kontinuierlich aus, während eine Taste gedrückt gehalten wird.

**Am besten für:** Flüssige, kontinuierliche Bewegung

**Unterstützte Tasten:**
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
| **Preset** | Anfänger |

**Beschreibung:** Löst einmal aus, wenn eine Taste zum ersten Mal gedrückt wird.

**Am besten für:** Einzelaktionen (Springen, Schießen, Menüauswahl)

**Unterschied zu Tastatur:** Löst nur einmal pro Druck aus, nicht während des Haltens.

---

### Taste Loslassen
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `keyboard_release` |
| **Symbol** | ⬆️ |
| **Kategorie** | Eingabe |
| **Preset** | Experte |

**Beschreibung:** Löst einmal aus, wenn eine Taste losgelassen wird.

**Häufige Verwendungen:**
- Bewegung stoppen, wenn Taste losgelassen
- Ladeattacken beenden
- Zustände umschalten

---

### Tastatur (Keine Taste)
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `keyboard_no_key` |
| **Symbol** | ⌨️ |
| **Kategorie** | Eingabe |
| **Preset** | Experte |

**Beschreibung:** Löst jeden Frame aus, solange **keine** Taste gehalten wird.

**Wann es auslöst:** Jeden Frame, in dem die Tastatur inaktiv ist, *vor* dem Step-Ereignis.

**Häufige Verwendungen:**
- Bewegung stoppen, wenn der Spieler alle Tasten loslässt (Gitter-/Labyrinthspiele)
- Leerlaufanimationen

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
| Maus Austritt | Cursor verlässt Instanzgrenzen |
| Globale Linke Taste | Linksklick überall |
| Globale Rechte Taste | Rechtsklick überall |

---

## Kollisions-Ereignisse

### Kollision
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `collision` |
| **Symbol** | 💥 |
| **Kategorie** | Kollision |
| **Preset** | Anfänger |

**Beschreibung:** Löst aus, wenn diese Instanz mit einem anderen Objekttyp überlappt.

**Konfiguration:** Wählen Sie, welcher Objekttyp diese Kollision auslöst.

**Spezielle Variable:** `other` — Verweis auf die kollidierende Instanz.

**Wann es auslöst:** Jeden Frame, in dem Instanzen überlappen.

**Häufige Verwendungen:**
- Gegenstände sammeln
- Schaden nehmen
- Wände treffen
- Ereignisse auslösen

**Beispiel-Kollisionsereignisse:**
- `collision_with_obj_coin` — Spieler berührt eine Münze
- `collision_with_obj_enemy` — Spieler berührt einen Gegner
- `collision_with_obj_wall` — Instanz trifft eine Wand

---

## Zeit-Ereignisse

### Alarm
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `alarm` |
| **Symbol** | ⏰ |
| **Kategorie** | Zeit |
| **Preset** | Fortgeschritten |

**Beschreibung:** Löst aus, wenn ein Alarm-Countdown null erreicht.

**Verfügbare Alarme:** 12 unabhängige Alarme (alarm[0] bis alarm[11])

**Alarme einstellen:** Verwenden Sie die Aktion „Alarm setzen" mit Steps (60 Steps ≈ 1 Sekunde bei 60 FPS)

**Häufige Verwendungen:**
- Zeitgesteuertes Spawnen
- Abklingzeiten
- Verzögerte Effekte
- Wiederholende Aktionen (Alarm im Alarmereignis erneut setzen)

---

### Begin Step
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `begin_step` |
| **Symbol** | ▶️ |
| **Kategorie** | Step |
| **Preset** | Experte |

**Beschreibung:** Löst am Anfang jedes Frames aus, vor regulären Step-Ereignissen.

**Ausführungsreihenfolge:** Begin Step → Step → End Step

**Häufige Verwendungen:**
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

**Beschreibung:** Löst am Ende jedes Frames aus, nach Kollisionen.

**Häufige Verwendungen:**
- Endgültige Positionsanpassungen
- Aufräumoperationen
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

**Beschreibung:** Löst während der Renderphase aus.

**Wichtig:** Das Hinzufügen eines Draw-Ereignisses deaktiviert das automatische Sprite-Zeichnen. Sie müssen das Sprite manuell zeichnen, wenn es sichtbar sein soll.

**Häufige Verwendungen:**
- Benutzerdefiniertes Rendern
- Formen zeichnen
- Text anzeigen
- Gesundheitsbalken
- HUD-Elemente

**Verfügbare Zeichenaktionen:**
- Sprite zeichnen
- Text zeichnen
- Rechteck zeichnen
- Kreis zeichnen
- Linie zeichnen
- Gesundheitsbalken zeichnen

---

### Draw GUI
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `draw_gui` |
| **Symbol** | 🖥️ |
| **Kategorie** | Zeichnen |
| **Preset** | Experte |

**Beschreibung:** Zeichnet im **Bildschirm- (GUI-)Raum**, über dem Raum und unbeeinflusst vom Scrollen der Ansichten/Kamera.

**Unterschied zu Draw:** Das reguläre Draw-Ereignis ist in Raumkoordinaten (es scrollt mit der Ansicht); Draw GUI bleibt fest am Bildschirm — für HUDs, Punktestände und Menüs.

---

## Raum-Ereignisse

### Room Start
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `room_start` |
| **Symbol** | 🚪 |
| **Kategorie** | Raum |
| **Preset** | Experte |

**Beschreibung:** Löst beim Betreten eines Raums aus, nach allen Create-Ereignissen.

**Häufige Verwendungen:**
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

**Beschreibung:** Löst beim Verlassen eines Raums aus.

**Häufige Verwendungen:**
- Fortschritt speichern
- Musik stoppen
- Aufräumen

---

## Spiel-Ereignisse

### Game Start
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `game_start` |
| **Symbol** | 🎮 |
| **Kategorie** | Spiel |
| **Preset** | Experte |

**Beschreibung:** Löst einmal aus, wenn das Spiel zum ersten Mal startet (nur im ersten Raum).

**Häufige Verwendungen:**
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

**Beschreibung:** Löst aus, wenn das Spiel endet.

**Häufige Verwendungen:**
- Spieldaten speichern
- Ressourcen aufräumen

---

## Andere Ereignisse

### Outside Room
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `outside_room` |
| **Symbol** | 🚫 |
| **Kategorie** | Andere |
| **Preset** | Experte |

**Beschreibung:** Löst aus, wenn die Instanz vollständig außerhalb der Raumgrenzen ist.

**Häufige Verwendungen:**
- Kugeln außerhalb des Bildschirms zerstören
- Auf die andere Seite wechseln
- Game Over auslösen

---

### Intersect Boundary
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `intersect_boundary` |
| **Symbol** | ⚠️ |
| **Kategorie** | Andere |
| **Preset** | Experte |

**Beschreibung:** Löst aus, wenn die Instanz die Raumgrenze berührt.

**Häufige Verwendungen:**
- Spieler in Grenzen halten
- Von Rändern abprallen

---

### No More Lives
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `no_more_lives` |
| **Symbol** | 💀 |
| **Kategorie** | Andere |
| **Preset** | Fortgeschritten |

**Beschreibung:** Löst aus, wenn Leben 0 oder weniger werden.

**Häufige Verwendungen:**
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

**Beschreibung:** Löst aus, wenn Gesundheit 0 oder weniger wird.

**Häufige Verwendungen:**
- Ein Leben verlieren
- Spieler respawnen
- Todesanimation auslösen

---

### Animation End
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `animation_end` |
| **Symbol** | 🎞️ |
| **Kategorie** | Andere |
| **Preset** | Experte |

**Beschreibung:** Löst aus, wenn die Sprite-Animation der Instanz einen vollständigen Zyklus abschließt (vom letzten Bild zurück zum ersten springt).

**Häufige Verwendungen:**
- Einen einmaligen Effekt (Explosion) nach einmaligem Abspielen zerstören
- Zu einer anderen Animation wechseln, wenn die aktuelle endet
- Eine Zustandsmaschine bei Animationsende weiterschalten

---

## Ereignis-Ausführungsreihenfolge

Das Verständnis, wann Ereignisse auslösen, hilft dabei, vorhersehbares Spielverhalten zu erstellen:

1. **Begin Step** — Anfang des Frames
2. **Alarm** — Alle ausgelösten Alarme
3. **Keyboard/Mouse** — Eingabeereignisse
4. **Step** — Haupt-Spiellogik
5. **Collision** — Nach Bewegung
6. **End Step** — Nach Kollisionen
7. **Draw** — Renderphase

---

## Ereignisse nach Preset

| Preset | Enthaltene Ereignisse |
|--------|----------------------|
| **Anfänger** | Create, Step, Keyboard Press, Collision |
| **Fortgeschritten** | + Draw, Destroy, Mouse, Alarm |
| **Experte** | + Alle Tastaturvarianten, Begin/End Step, Raum-Ereignisse, Spiel-Ereignisse, Grenzereignisse |

---

## Siehe Auch

- [Vollständige Aktionsreferenz](Full-Action-Reference_de) - Vollständige Aktionsliste
- [Anfänger-Preset](Beginner-Preset_de) - Wesentliche Ereignisse für Anfänger
- [Fortgeschrittenen-Preset](Intermediate-Preset_de) - Zusätzliche Ereignisse
- [Ereignisse und Aktionen](Events_und_Aktionen_de) - Überblick über Kernkonzepte
