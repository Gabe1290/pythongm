# Visuelle Programmierung

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

[Zuruck zur Startseite](Home_de)

pyGM bietet ein visuelles Programmiersystem fur einfache Spieleentwicklung ohne Code.

## Uberblick

Mit der visuellen Programmierung konnen Sie:
- Spiellogik durch Drag-and-Drop erstellen
- Blocke verbinden fur komplexes Verhalten
- Ohne Programmierkenntnisse entwickeln

## Der Blockly-Editor

### Oberflache
1. **Block-Palette**: Verfugbare Blocke nach Kategorie
2. **Arbeitsflache**: Hier verbinden Sie Blocke
3. **Werkzeugleiste**: Speichern, Laden, Loschen

### Block-Kategorien
- **Logik**: Wenn/Dann, Vergleiche, Boolesche Werte
- **Schleifen**: Wiederholungen
- **Mathematik**: Berechnungen
- **Text**: Textoperationen
- **Variablen**: Werte speichern
- **Funktionen**: Wiederverwendbare Blocke
- **Spiel**: pyGM-spezifische Aktionen

## Blocke verwenden

### Block hinzufugen
1. Klicken Sie auf eine Kategorie
2. Ziehen Sie einen Block auf die Arbeitsflache
3. Verbinden Sie ihn mit anderen Blocken

### Blocke verbinden
- Blocke rasten automatisch ein
- Achten Sie auf passende Formen
- Verschachtelte Blocke sind moglich

### Block konfigurieren
- Eingabefelder ausfullen
- Dropdown-Optionen wahlen
- Unterblocks einfugen

## Beispiele

### Einfache Bewegung
```
Wenn [Pfeil rechts] gedruckt
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

## Spiel-Blocke

### Bewegung
- **Bewege zu**: Zu Position bewegen
- **Setze Geschwindigkeit**: Bewegungsgeschwindigkeit
- **Setze Richtung**: Bewegungsrichtung

### Instanzen
- **Erstelle Instanz**: Neues Objekt erzeugen
- **Zerstore**: Objekt loschen
- **Fur alle**: Alle Instanzen eines Typs

### Variablen
- **Setze Variable**: Wert speichern
- **Andere Variable**: Wert andern
- **Hole Variable**: Wert abrufen

### Events
- **Wenn Taste**: Tastatureingabe
- **Wenn Kollision**: Objektberuhrung
- **Wenn Timer**: Zeitbasiert

## Tipps

1. **Klein anfangen**: Einfache Projekte zuerst
2. **Testen**: Regelmasig ausfuhren
3. **Organisieren**: Blocke logisch gruppieren
4. **Kommentare**: Notizen hinzufugen

## Von Blocken zu Code

Der Blockly-Editor kann auch Code generieren:
1. Lernen Sie Programmierkonzepte visuell
2. Sehen Sie den generierten Code
3. Wechseln Sie spater zu Python

## Siehe auch

- [Ihr erstes Spiel erstellen](Erstes_Spiel_de)
- [Events und Aktionen](Events_und_Aktionen_de)
- [FAQ](FAQ_de)
