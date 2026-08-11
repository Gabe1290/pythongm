# Andere Ereignisse

*[Startseite](Home_de) | [Ereignis-Referenz](Event-Reference_de) | [Vollständige Aktionsreferenz](Full-Action-Reference_de)*

### Outside Room
| Eigenschaft | Wert |
|-------------|------|
| **Name** | `outside_room` |
| **Symbol** | 🚫 |
| **Kategorie** | Andere |
| **Preset** | Anfänger |

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
| **Preset** | Anfänger |

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
| **Preset** | Anfänger |

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
| **Preset** | Anfänger |

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
| **Preset** | Anfänger |

**Beschreibung:** Löst aus, wenn die Sprite-Animation der Instanz einen vollständigen Zyklus abschließt (vom letzten Bild zurück zum ersten springt).

**Häufige Verwendungen:**
- Einen einmaligen Effekt (Explosion) nach einmaligem Abspielen zerstören
- Zu einer anderen Animation wechseln, wenn die aktuelle endet
- Eine Zustandsmaschine bei Animationsende weiterschalten

---

## Weitere Ereigniskategorien

- [Objekt-Ereignisse](Event-Reference-Object_de) - Create, Step, Destroy
- [Eingabe-Ereignisse](Event-Reference-Input_de) - Tastatur, Maus
- [Kollisions-Ereignisse](Event-Reference-Collision_de) - Objektkollisionen
- [Zeit-Ereignisse](Event-Reference-Timing_de) - Alarme, Step-Varianten
- [Zeichen-Ereignisse](Event-Reference-Drawing_de) - Benutzerdefiniertes Rendern
- [Raum-Ereignisse](Event-Reference-Room_de) - Raumübergänge
- [Spiel-Ereignisse](Event-Reference-Game_de) - Spielstart/-ende

[← Zurück zur Ereignis-Referenz](Event-Reference_de)
