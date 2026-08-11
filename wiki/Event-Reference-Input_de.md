# Eingabe-Ereignisse

*[Startseite](Home_de) | [Ereignis-Referenz](Event-Reference_de) | [Vollständige Aktionsreferenz](Full-Action-Reference_de)*

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
| **Preset** | Fortgeschritten |

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
| **Preset** | Voll (Entwicklungsedition) |

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
| **Preset** | Anfänger |

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
| **Preset** | Voll (Entwicklungsedition) |

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

## Weitere Ereigniskategorien

- [Objekt-Ereignisse](Event-Reference-Object_de) - Create, Step, Destroy
- [Kollisions-Ereignisse](Event-Reference-Collision_de) - Objektkollisionen
- [Zeit-Ereignisse](Event-Reference-Timing_de) - Alarme, Step-Varianten
- [Zeichen-Ereignisse](Event-Reference-Drawing_de) - Benutzerdefiniertes Rendern
- [Raum-Ereignisse](Event-Reference-Room_de) - Raumübergänge
- [Spiel-Ereignisse](Event-Reference-Game_de) - Spielstart/-ende
- [Andere Ereignisse](Event-Reference-Other_de) - Grenzen, Leben, Gesundheit

[← Zurück zur Ereignis-Referenz](Event-Reference_de)
