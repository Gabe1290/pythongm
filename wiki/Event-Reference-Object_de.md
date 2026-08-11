# Objekt-Ereignisse

*[Startseite](Home_de) | [Ereignis-Referenz](Event-Reference_de) | [Vollständige Aktionsreferenz](Full-Action-Reference_de)*

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

## Weitere Ereigniskategorien

- [Eingabe-Ereignisse](Event-Reference-Input_de) - Tastatur, Maus
- [Kollisions-Ereignisse](Event-Reference-Collision_de) - Objektkollisionen
- [Zeit-Ereignisse](Event-Reference-Timing_de) - Alarme, Step-Varianten
- [Zeichen-Ereignisse](Event-Reference-Drawing_de) - Benutzerdefiniertes Rendern
- [Raum-Ereignisse](Event-Reference-Room_de) - Raumübergänge
- [Spiel-Ereignisse](Event-Reference-Game_de) - Spielstart/-ende
- [Andere Ereignisse](Event-Reference-Other_de) - Grenzen, Leben, Gesundheit

[← Zurück zur Ereignis-Referenz](Event-Reference_de)
