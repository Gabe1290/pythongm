# Kollisions-Ereignisse

*[Startseite](Home_de) | [Ereignis-Referenz](Event-Reference_de) | [Vollständige Aktionsreferenz](Full-Action-Reference_de)*

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

## Weitere Ereigniskategorien

- [Objekt-Ereignisse](Event-Reference-Object_de) - Create, Step, Destroy
- [Eingabe-Ereignisse](Event-Reference-Input_de) - Tastatur, Maus
- [Zeit-Ereignisse](Event-Reference-Timing_de) - Alarme, Step-Varianten
- [Zeichen-Ereignisse](Event-Reference-Drawing_de) - Benutzerdefiniertes Rendern
- [Raum-Ereignisse](Event-Reference-Room_de) - Raumübergänge
- [Spiel-Ereignisse](Event-Reference-Game_de) - Spielstart/-ende
- [Andere Ereignisse](Event-Reference-Other_de) - Grenzen, Leben, Gesundheit

[← Zurück zur Ereignis-Referenz](Event-Reference_de)
