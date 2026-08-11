# Zeit-Ereignisse

*[Startseite](Home_de) | [Ereignis-Referenz](Event-Reference_de) | [Vollständige Aktionsreferenz](Full-Action-Reference_de)*

### Alarm
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `alarm` |
| **Symbol** | ⏰ |
| **Kategorie** | Zeit |
| **Preset** | Anfänger |

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
| **Preset** | Anfänger |

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
| **Preset** | Anfänger |

**Beschreibung:** Löst am Ende jedes Frames aus, nach Kollisionen.

**Häufige Verwendungen:**
- Endgültige Positionsanpassungen
- Aufräumoperationen
- Zustandsaktualisierungen nach Kollisionen

---

## Weitere Ereigniskategorien

- [Objekt-Ereignisse](Event-Reference-Object_de) - Create, Step, Destroy
- [Eingabe-Ereignisse](Event-Reference-Input_de) - Tastatur, Maus
- [Kollisions-Ereignisse](Event-Reference-Collision_de) - Objektkollisionen
- [Zeichen-Ereignisse](Event-Reference-Drawing_de) - Benutzerdefiniertes Rendern
- [Raum-Ereignisse](Event-Reference-Room_de) - Raumübergänge
- [Spiel-Ereignisse](Event-Reference-Game_de) - Spielstart/-ende
- [Andere Ereignisse](Event-Reference-Other_de) - Grenzen, Leben, Gesundheit

[← Zurück zur Ereignis-Referenz](Event-Reference_de)
