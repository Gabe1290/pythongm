# Ihr erstes Spiel erstellen

> [English](Creating-Your-First-Game) | [Français](Premier_Jeu_fr) | [Deutsch](Erstes_Spiel_de) | [Italiano](Primo_Gioco_it) | [Español](Primer_Juego_es) | [Português](Primeiro_Jogo_pt) | [Slovenščina](Prva_Igra_sl) | [Українська](Persha_Gra_uk) | [Русский](Pervaya_Igra_ru)

---

[Zurück zur Startseite](Home_de)

In dieser Anleitung erstellen Sie ein einfaches Spiel, um die Grundlagen von pyGM zu erlernen.

## Überblick

Wir erstellen ein einfaches Spiel mit:
- Einem Spieler-Charakter, der sich bewegen kann
- Einem Sammelobjekt
- Einem Punktesystem

## Schritt 1: Neues Projekt erstellen

1. Starten Sie pyGM
2. Wählen Sie „Neues Projekt"
3. Geben Sie einen Projektnamen ein
4. Wählen Sie einen Speicherort

## Schritt 2: Sprites erstellen

### Spieler-Sprite
1. Rechtsklick auf „Sprites" im Ressourcenbaum
2. Wählen Sie „Neues Sprite"
3. Verwenden Sie den integrierten Editor oder importieren Sie ein Bild
4. Benennen Sie es „spr_spieler"

### Sammelobjekt-Sprite
1. Erstellen Sie ein weiteres Sprite
2. Benennen Sie es „spr_muenze"

## Schritt 3: Objekte erstellen

### Spieler-Objekt
1. Rechtsklick auf „Objekte"
2. Wählen Sie „Neues Objekt"
3. Benennen Sie es „obj_spieler"
4. Weisen Sie „spr_spieler" als Sprite zu

### Bewegung hinzufügen
1. Fügen Sie das Event „Tastendruck" hinzu
2. Verwenden Sie Aktionen für Bewegung:
   - Pfeiltaste hoch: Nach oben bewegen
   - Pfeiltaste unten: Nach unten bewegen
   - Pfeiltaste links: Nach links bewegen
   - Pfeiltaste rechts: Nach rechts bewegen

### Münz-Objekt
1. Erstellen Sie „obj_muenze"
2. Weisen Sie „spr_muenze" zu
3. Fügen Sie ein Kollisions-Event mit dem Spieler hinzu
4. Aktion: Instanz zerstören und Punkte hinzufügen

## Schritt 4: Raum erstellen

1. Rechtsklick auf „Räume"
2. Wählen Sie „Neuer Raum"
3. Benennen Sie ihn „rm_level1"
4. Platzieren Sie Objekte:
   - Einen Spieler
   - Mehrere Münzen

## Schritt 5: Spiel testen

1. Klicken Sie auf „Spiel ausführen" oder drücken Sie F5
2. Testen Sie die Bewegung
3. Sammeln Sie Münzen

## Erweiterungsideen

- Hindernisse hinzufügen
- Zeitsystem implementieren
- Verschiedene Levels erstellen
- Soundeffekte einbauen

## Nächste Schritte

- [Events und Aktionen vertiefen](Events_und_Aktionen_de)
- [Visuelle Programmierung lernen](Visuelle_Programmierung_de)
- [Spiele exportieren](Spiele_Exportieren_de)
