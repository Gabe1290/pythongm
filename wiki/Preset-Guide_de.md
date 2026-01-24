# Voreinstellungs-Leitfaden

*[Deutsch](Preset-Guide_de) | [Zurück zur Startseite](Home_de)*

PyGameMaker bietet verschiedene Voreinstellungen, die steuern, welche Ereignisse und Aktionen verfügbar sind. Dies hilft Anfängern, sich auf wesentliche Funktionen zu konzentrieren, während erfahrene Benutzer auf das vollständige Toolset zugreifen können.

## Wählen Sie Ihr Können

| Voreinstellung | Geeignet Für | Funktionen |
|----------------|--------------|------------|
| [**Anfänger**](Beginner-Preset_de) | Neu in der Spieleentwicklung | 4 Ereignisse, 17 Aktionen - Bewegung, Kollisionen, Punktzahl, Räume |
| [**Fortgeschritten**](Intermediate-Preset_de) | Einige Erfahrung | +4 Ereignisse, +12 Aktionen - Leben, Gesundheit, Sound, Alarme, Zeichnen |
| **Experte** | Erfahrene Benutzer | Alle 40+ Ereignisse und Aktionen verfügbar |

---

## Voreinstellungs-Dokumentation

### Voreinstellungen
| Seite | Beschreibung |
|-------|--------------|
| [Anfänger-Voreinstellung](Beginner-Preset_de) | 4 Ereignisse, 17 Aktionen - Wesentliche Funktionen |
| [Fortgeschrittenen-Voreinstellung](Intermediate-Preset_de) | +4 Ereignisse, +12 Aktionen - Leben, Gesundheit, Sound |

### Referenz
| Seite | Beschreibung |
|-------|--------------|
| [Ereignis-Referenz](Event-Reference_de) | Vollständige Liste aller Ereignisse |
| [Vollständige Aktions-Referenz](Full-Action-Reference_de) | Vollständige Liste aller Aktionen |

---

## Schnellstart-Beispiel

Hier ist ein einfaches Münzsammelspiel mit nur Anfänger-Funktionen:

### 1. Objekte Erstellen
- `obj_player` - Der steuerbare Charakter
- `obj_coin` - Sammelbare Gegenstände
- `obj_wall` - Feste Hindernisse

### 2. Ereignisse zum Spieler Hinzufügen

**Tastatur (Pfeiltasten):**
```
Pfeil Links   → Horizontale Geschwindigkeit setzen: -4
Pfeil Rechts  → Horizontale Geschwindigkeit setzen: 4
Pfeil Oben    → Vertikale Geschwindigkeit setzen: -4
Pfeil Unten   → Vertikale Geschwindigkeit setzen: 4
```

**Kollision mit obj_coin:**
```
Punktzahl Hinzufügen: 10
Instanz Zerstören: other
```

**Kollision mit obj_wall:**
```
Bewegung Stoppen
```

### 3. Einen Raum Erstellen
- Platzieren Sie den Spieler
- Fügen Sie einige Münzen hinzu
- Fügen Sie Wände an den Rändern hinzu

### 4. Das Spiel Starten!
Drücken Sie den Play-Button, um Ihr Spiel zu testen.

---

## Tipps für Erfolg

1. **Einfach Anfangen** - Verwenden Sie zuerst die Anfänger-Voreinstellung
2. **Oft Testen** - Führen Sie Ihr Spiel häufig aus, um Probleme zu erkennen
3. **Eins nach dem Anderen** - Fügen Sie Funktionen schrittweise hinzu
4. **Kollisionen Nutzen** - Die meisten Spielmechaniken beinhalten Kollisionsereignisse
5. **Dokumentation Lesen** - Schauen Sie in die Referenzseiten, wenn Sie nicht weiterkommen

---

## Siehe Auch

- [Startseite](Home_de) - Wiki-Hauptseite
- [Erste Schritte](Erste_Schritte_de) - Installation und Einrichtung
- [Ereignisse und Aktionen](Events_und_Aktionen_de) - Grundkonzepte
- [Ihr Erstes Spiel](Erstes_Spiel_de) - Tutorial
- [Breakout Tutorial](Tutorial-Breakout_de) - Erstellen Sie ein klassisches Breakout-Spiel
- [Einführung in die Spieleentwicklung](Getting-Started-Breakout_de) - Umfassendes Anfänger-Tutorial
