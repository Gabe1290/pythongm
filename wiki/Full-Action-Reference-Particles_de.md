# Partikel

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Partikel ausstoßen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `burst_particles` |
| **Symbol** | 💥 |
| **Kategorie** | Partikel |

Stößt eine einmalige Salve von Partikeln aus dem zuletzt erstellten Emitter aus

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `particle_type` | Zahl | `0` | Kennung des Partikeltyps (aus „Partikeltyp erstellen“) |
| `number` | Zahl | `10` | Anzahl der auszustoßenden Partikel |

### Partikel löschen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `clear_particles` |
| **Symbol** | 🧹 |
| **Kategorie** | Partikel |

Entfernt alle aktiven Partikel, behält aber Partikeltypen und Emitter

*Parameter:* keine

### Emitter erstellen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `create_emitter` |
| **Symbol** | 🌀 |
| **Kategorie** | Partikel |

Erstellt einen Emitterbereich für Partikel (die zurückgegebene Kennung wird für die nächste Aktion gemerkt, die einen Emitter verwendet)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | X-Mitte des Emitters (Raumkoordinaten) |
| `y` | Zahl | `0` | Y-Mitte des Emitters (Raumkoordinaten) |
| `width` | Zahl | `0` | Breite des Emitterbereichs |
| `height` | Zahl | `0` | Höhe des Emitterbereichs |
| `shape` | Auswahl | `rectangle` | Form des Emitterbereichs, in dem Partikel entstehen; Auswahl: `rectangle`, `ellipse`, `diamond`, `line` |

### Partikelsystem erstellen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `create_particle_system` |
| **Symbol** | ✨ |
| **Kategorie** | Partikel |

Erstellt ein an diese Instanz gebundenes Partikelsystem (ersetzt ein vorhandenes)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `depth` | Zahl | `0` | Zeichentiefe des Partikelsystems (noch nicht für die Sortierung zwischen Instanzen verwendet) |

### Partikeltyp erstellen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `create_particle_type` |
| **Symbol** | ⚙️ |
| **Kategorie** | Partikel |

Legt ein neues Aussehen bzw. Verhalten für Partikel fest (die zurückgegebene Typkennung wird für die nächste Aktion gemerkt, die einen Partikeltyp verwendet)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite, mit dem jedes Partikel gezeichnet wird; leer lassen für einen einfachen farbigen Kreis; optional |
| `size_min` | Zahl | `1.0` | Kleinste Partikelgröße (Skalierungsfaktor) |
| `size_max` | Zahl | `1.0` | Größte Partikelgröße (Skalierungsfaktor) |
| `size_increase` | Zahl | `0.0` | Größenänderung pro Schritt (negativ schrumpft, mindestens 0) |
| `color` | Farbe | `#FFFFFF` | Partikelfarbe (wird verwendet, wenn kein Sprite gesetzt ist) |
| `alpha` | Zahl | `1.0` | Transparenz (0 = unsichtbar, 1 = deckend) |
| `speed_min` | Zahl | `0.0` | Kleinste Bewegungsgeschwindigkeit |
| `speed_max` | Zahl | `0.0` | Größte Bewegungsgeschwindigkeit |
| `direction_min` | Zahl | `0` | Kleinster Richtungswinkel (0 = rechts, 90 = oben) |
| `direction_max` | Zahl | `360` | Größter Richtungswinkel |
| `life_min` | Zahl | `100` | Kleinste Lebensdauer in Schritten |
| `life_max` | Zahl | `100` | Größte Lebensdauer in Schritten |

### Emitter entfernen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `destroy_emitter` |
| **Symbol** | 💥 |
| **Kategorie** | Partikel |

Entfernt den zuletzt erstellten Emitter

*Parameter:* keine

### Partikelsystem entfernen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `destroy_particle_system` |
| **Symbol** | 💥 |
| **Kategorie** | Partikel |

Entfernt das Partikelsystem dieser Instanz und löscht dabei alle Partikel und Emitter

*Parameter:* keine

### Partikel strömen lassen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `stream_particles` |
| **Symbol** | 🌊 |
| **Kategorie** | Partikel |

Stößt bei jedem Schritt fortlaufend Partikel aus dem zuletzt erstellten Emitter aus (0 zum Anhalten)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `particle_type` | Zahl | `0` | Kennung des Partikeltyps (aus „Partikeltyp erstellen“) |
| `number` | Zahl | `1` | Partikel pro Schritt (0 hält den Strom an) |

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (8)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (25)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (18)
- [Netzwerk](Full-Action-Reference-Network-Actions_de) (15)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
