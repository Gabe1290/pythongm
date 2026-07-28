# Visuelle Programmierung

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

[Zurück zur Startseite](Home_de)

pyGM bietet ein visuelles Programmiersystem für einfache Spieleentwicklung ohne Code.

## Überblick

Mit der visuellen Programmierung können Sie:
- Spiellogik durch Drag-and-Drop erstellen
- Blöcke verbinden für komplexes Verhalten
- Ohne Programmierkenntnisse entwickeln

## Der Blockly-Editor

### Oberfläche
1. **Block-Palette**: Verfügbare Blöcke nach Kategorie
2. **Arbeitsfläche**: Hier verbinden Sie Blöcke
3. **Werkzeugleiste**: Speichern, Laden, Löschen

### Block-Kategorien
- **Logik**: Wenn/Dann, Vergleiche, Boolesche Werte
- **Schleifen**: Wiederholungen
- **Mathematik**: Berechnungen
- **Text**: Textoperationen
- **Variablen**: Werte speichern
- **Funktionen**: Wiederverwendbare Blöcke
- **Spiel**: pyGM-spezifische Aktionen

## Blöcke verwenden

### Block hinzufügen
1. Klicken Sie auf eine Kategorie
2. Ziehen Sie einen Block auf die Arbeitsfläche
3. Verbinden Sie ihn mit anderen Blöcken

### Blöcke verbinden
- Blöcke rasten automatisch ein
- Achten Sie auf passende Formen
- Verschachtelte Blöcke sind möglich

### Block konfigurieren
- Eingabefelder ausfüllen
- Dropdown-Optionen wählen
- Unterblöcke einfügen

## Beispiele

### Einfache Bewegung
```
Wenn [Pfeil rechts] gedrückt
  Setze x auf (x + 5)
```

### Bedingte Logik
```
Wenn <Leben <= 0> dann
  Zeige Nachricht "Game Over"
  Gehe zu Raum [rm_gameover]
```

### Schleife
```
Wiederhole [10] mal
  Erstelle Instanz [obj_muenze] an Position (Zufall 0-800, Zufall 0-600)
```

## Spiel-Blöcke

### Bewegung
- **Bewege zu**: Zu Position bewegen
- **Setze Geschwindigkeit**: Bewegungsgeschwindigkeit
- **Setze Richtung**: Bewegungsrichtung

### Instanzen
- **Erstelle Instanz**: Neues Objekt erzeugen
- **Zerstöre**: Objekt löschen
- **Für alle**: Alle Instanzen eines Typs

### Variablen
- **Setze Variable**: Wert speichern
- **Ändere Variable**: Wert ändern
- **Hole Variable**: Wert abrufen

### Events
- **Wenn Taste**: Tastatureingabe
- **Wenn Kollision**: Objektberührung
- **Wenn Timer**: Zeitbasiert

## Tipps

1. **Klein anfangen**: Einfache Projekte zuerst
2. **Testen**: Regelmäßig ausführen
3. **Organisieren**: Blöcke logisch gruppieren
4. **Kommentare**: Notizen hinzufügen

## Von Blöcken zu Code

Der Blockly-Editor kann auch Code generieren:
1. Lernen Sie Programmierkonzepte visuell
2. Sehen Sie den generierten Code
3. Wechseln Sie später zu Python

## Siehe auch

- [Ihr erstes Spiel erstellen](Erstes_Spiel_de)
- [Events und Aktionen](Events_und_Aktionen_de)
- [FAQ](FAQ_de)
