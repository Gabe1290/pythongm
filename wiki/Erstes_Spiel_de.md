# Ihr erstes Spiel erstellen

> [English](Creating-Your-First-Game) | [Français](Premier_Jeu_fr) | [Deutsch](Erstes_Spiel_de) | [Italiano](Primo_Gioco_it) | [Español](Primer_Juego_es) | [Português](Primeiro_Jogo_pt) | [Slovenščina](Prva_Igra_sl) | [Українська](Persha_Gra_uk) | [Русский](Pervaya_Igra_ru)

---

> [Zurück zur Startseite](Home_de)

In diesem Tutorial erstellen wir ein einfaches Spiel „Sterne fangen", bei dem der Spieler sich bewegt, um fallende Sterne einzusammeln.

---

## Was Sie lernen werden

- Sprites erstellen
- Objekte mit Events und Aktionen erstellen
- Den Raum-Editor verwenden
- Ihr Spiel ausführen und testen

---

## Schritt 1: Ein neues Projekt erstellen

1. Starten Sie PyGameMaker
2. Gehen Sie zu **Datei > Neues Projekt**
3. Nennen Sie Ihr Projekt „CatchTheStars"
4. Klicken Sie auf **Erstellen**

---

## Schritt 2: Das Spieler-Sprite erstellen

1. Rechtsklick auf **Sprites** im Ressourcenbaum
2. Wählen Sie **Sprite erstellen**
3. Nennen Sie es `spr_player`
4. Klicken Sie auf **Sprite bearbeiten**, um den Sprite-Editor zu öffnen
5. Zeichnen Sie eine einfache Figur (oder verwenden Sie ein farbiges 32×32-Rechteck)
6. Klicken Sie auf **Speichern**

---

## Schritt 3: Das Stern-Sprite erstellen

1. Rechtsklick auf **Sprites** > **Sprite erstellen**
2. Nennen Sie es `spr_star`
3. Zeichnen Sie eine Sternform (oder verwenden Sie einen gelben Kreis)
4. Klicken Sie auf **Speichern**

---

## Schritt 4: Das Spieler-Objekt erstellen

1. Rechtsklick auf **Objects** im Ressourcenbaum
2. Wählen Sie **Objekt erstellen**
3. Nennen Sie es `obj_player`
4. Setzen Sie das **Sprite** auf `spr_player`

### Tastaturereignisse hinzufügen

**Pfeiltaste links:**
1. Klicken Sie auf **Add Event** > **Keyboard** > **Left**
2. Aktion hinzufügen: **Set Horizontal Speed** mit Wert `-4`

**Pfeiltaste rechts:**
1. Klicken Sie auf **Add Event** > **Keyboard** > **Right**
2. Aktion hinzufügen: **Set Horizontal Speed** mit Wert `4`

**Keine Taste gedrückt:**
1. Klicken Sie auf **Add Event** > **Keyboard** > **No Key**
2. Aktion hinzufügen: **Set Horizontal Speed** mit Wert `0`

---

## Schritt 5: Das Stern-Objekt erstellen

1. Rechtsklick auf **Objects** > **Objekt erstellen**
2. Nennen Sie es `obj_star`
3. Setzen Sie das **Sprite** auf `spr_star`

### Create-Event hinzufügen
1. Klicken Sie auf **Add Event** > **Create**
2. Aktion hinzufügen: **Set Vertical Speed** mit Wert `3`
3. Aktion hinzufügen: **Jump To Position** mit X `irandom(600)`, Y `20` —
   `irandom(n)` wählt eine zufällige ganze Zahl von 0 bis `n`, sodass der
   Stern bei jedem (Wieder-)Erscheinen an einer zufälligen Stelle nahe dem
   oberen Rand eines 640 Pixel breiten Raums platziert wird

### Outside-Room-Event hinzufügen
1. Klicken Sie auf **Add Event** > **Other** > **Outside Room**
2. Aktion hinzufügen: **Jump to Start Position**
3. Aktion hinzufügen: **Set Score** mit Wert `1` und aktiviertem **Relative**

### Kollision mit dem Spieler hinzufügen
1. Klicken Sie auf **Add Event** > **Collision** > wählen Sie `obj_player`
2. Aktion hinzufügen: **Set Score** mit Wert `10` und aktiviertem **Relative**
3. Aktion hinzufügen: **Play Sound** (optional, falls Sie einen Sound haben)
4. Aktion hinzufügen: **Jump to Random Position**

---

## Schritt 6: Den Raum erstellen

1. Rechtsklick auf **Rooms** im Ressourcenbaum
2. Wählen Sie **Raum erstellen**
3. Nennen Sie ihn `room_game`
4. Setzen Sie die Raumgröße auf **640 × 480**

### Objekte platzieren
1. Wählen Sie den **Objects**-Tab im Raum-Editor
2. Klicken Sie auf `obj_player` und platzieren Sie ihn unten mittig im Raum
3. Klicken Sie auf `obj_star` und platzieren Sie 5-10 Sterne oben verteilt

---

## Schritt 7: Den Punktestand anzeigen

1. Öffnen Sie `obj_player`
2. Klicken Sie auf **Add Event** > **Draw**
3. Aktion hinzufügen: **Draw Score** an Position (10, 10)

---

## Schritt 8: Starten Sie Ihr Spiel!

1. Drücken Sie **F5** oder gehen Sie zu **Build > Test Game**
2. Verwenden Sie die linke und rechte Pfeiltaste zur Bewegung
3. Fangen Sie die fallenden Sterne, um Ihren Punktestand zu erhöhen!

---

## Erweiterungen zum Ausprobieren

### Leben hinzufügen
1. Erstellen Sie ein „Game Over"-Objekt, das erscheint, wenn die Leben 0 erreichen
2. Fügen Sie ein Kollisions-Event mit einem „schlechten" Objekt hinzu, das Leben abzieht

### Levels hinzufügen
1. Erstellen Sie mehrere Räume
2. Verwenden Sie die Aktion **Next Room**, wenn der Punktestand einen Schwellenwert erreicht

### Sound hinzufügen
1. Importieren Sie Audiodateien in die Sounds-Ressource
2. Fügen Sie Events die Aktion **Play Sound** hinzu

### Visuelle Programmierung verwenden
1. Öffnen Sie ein Objekt
2. Klicken Sie auf den **Blockly**-Tab für Drag-and-Drop-Programmierung
3. Bauen Sie dieselbe Logik visuell mit Blöcken

---

## Vollständige Projektstruktur

Nach Abschluss dieses Tutorials sollte Ihr Projekt enthalten:

- **Sprites:** spr_player, spr_star
- **Objekte:** obj_player, obj_star
- **Rooms:** room_game

---

## Nächste Schritte

- [[Objekt_Editor_de]] - Erfahren Sie mehr über Objekt-Eigenschaften
- [[Events_und_Aktionen_de]] - Erkunden Sie alle verfügbaren Events und Aktionen
- [[Visuelle_Programmierung_de]] - Probieren Sie das Bauen mit Blockly-Blöcken
- [[Spiele_Exportieren_de]] - Teilen Sie Ihr Spiel mit anderen
