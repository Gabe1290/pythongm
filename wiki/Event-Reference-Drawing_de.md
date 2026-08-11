# Zeichen-Ereignisse

*[Startseite](Home_de) | [Ereignis-Referenz](Event-Reference_de) | [Vollständige Aktionsreferenz](Full-Action-Reference_de)*

### Draw
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `draw` |
| **Symbol** | 🎨 |
| **Kategorie** | Zeichnen |
| **Preset** | Anfänger |

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
| **Preset** | Anfänger |

**Beschreibung:** Zeichnet im **Bildschirm- (GUI-)Raum**, über dem Raum und unbeeinflusst vom Scrollen der Ansichten/Kamera.

**Unterschied zu Draw:** Das reguläre Draw-Ereignis ist in Raumkoordinaten (es scrollt mit der Ansicht); Draw GUI bleibt fest am Bildschirm — für HUDs, Punktestände und Menüs.

---

## Weitere Ereigniskategorien

- [Objekt-Ereignisse](Event-Reference-Object_de) - Create, Step, Destroy
- [Eingabe-Ereignisse](Event-Reference-Input_de) - Tastatur, Maus
- [Kollisions-Ereignisse](Event-Reference-Collision_de) - Objektkollisionen
- [Zeit-Ereignisse](Event-Reference-Timing_de) - Alarme, Step-Varianten
- [Raum-Ereignisse](Event-Reference-Room_de) - Raumübergänge
- [Spiel-Ereignisse](Event-Reference-Game_de) - Spielstart/-ende
- [Andere Ereignisse](Event-Reference-Other_de) - Grenzen, Leben, Gesundheit

[← Zurück zur Ereignis-Referenz](Event-Reference_de)
