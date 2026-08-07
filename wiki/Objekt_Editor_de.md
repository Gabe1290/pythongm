# Objekt-Editor

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

[Zurück zur Startseite](Home_de)

Objekte sind die Grundbausteine Ihres Spiels. Sie stehen für alles vom Spieler
über Gegner bis hin zu Sammelobjekten und UI-Elementen.

---

## Den Objekt-Editor öffnen

1. Doppelklicken Sie auf ein vorhandenes Objekt im Ressourcenbaum, oder
2. Rechtsklick auf **Objekte** > **Objekt erstellen**

---

## Objekt-Eigenschaften

| Eigenschaft | Beschreibung |
|-------------|--------------|
| **Name** | Eindeutiger Bezeichner für das Objekt (z. B. `obj_spieler`) |
| **Sprite** | Die visuelle Darstellung des Objekts |
| **Sichtbar** | Ob das Objekt gezeichnet wird (Standard: ja) |
| **Solid** | Wird für die Kollisionserkennung mit soliden Objekten verwendet |
| **Tiefe** | Zeichenreihenfolge (niedriger = wird oben gezeichnet) |
| **Persistent** | Das Objekt überlebt Raumwechsel |
| **Eltern-Objekt** | Vererbung gemeinsamer Eigenschaften/Events von einem anderen Objekt |

### Namenskonvention

Verwenden Sie das Präfix `obj_` für Objekte:
- `obj_spieler`
- `obj_gegner`
- `obj_muenze`
- `obj_wand`

---

## Events

Events sind Auslöser, die die Ausführung von Aktionen bewirken. Klicken Sie
auf „Event hinzufügen", um eines hinzuzufügen.

### Häufige Events

| Event | Wann es auslöst |
|-------|------------------|
| **Create** | Einmal, wenn eine Instanz erstellt wird |
| **Destroy** | Wenn die Instanz zerstört wird |
| **Step** | Bei jedem Spielframe (60-mal pro Sekunde) |
| **Draw** | Während der Zeichenphase |
| **Alarm [0-11]** | Wenn ein Alarm-Timer null erreicht |

### Tastatur-Events

| Event | Wann es auslöst |
|-------|------------------|
| **Key Press** | Einmal, wenn eine Taste gedrückt wird |
| **Key Release** | Einmal, wenn eine Taste losgelassen wird |
| **Keyboard** | Bei jedem Frame, solange eine Taste gehalten wird |
| **No Key** | Wenn keine Taste gedrückt ist |

### Maus-Events

| Event | Wann es auslöst |
|-------|------------------|
| **Mouse Button** | Bei einem Klick auf die Instanz |
| **Global Mouse** | Bei einem Klick irgendwo |
| **Mouse Enter** | Wenn der Cursor die Instanz betritt |
| **Mouse Leave** | Wenn der Cursor die Instanz verlässt |

### Kollisions-Events

| Event | Wann es auslöst |
|-------|------------------|
| **Collision with [Objekt]** | Bei Berührung mit einem anderen Objekttyp |

### Sonstige Events

| Event | Wann es auslöst |
|-------|------------------|
| **Outside Room** | Wenn die Instanz den Room verlässt |
| **Intersect Boundary** | Wenn die Instanz den Rand des Rooms berührt |
| **Game Start** | Einmal, wenn das Spiel beginnt |
| **Game End** | Einmal, wenn das Spiel beendet wird |
| **Room Start** | Beim Betreten eines Rooms |
| **Room End** | Beim Verlassen eines Rooms |

---

## Aktionen

Aktionen sind Operationen, die ausgeführt werden, wenn ein Event auslöst.
Jedes Event kann mehrere Aktionen haben, die der Reihe nach ausgeführt werden.

### Bewegungs-Aktionen
- **Geschwindigkeit setzen** — Bewegungsgeschwindigkeit festlegen
- **Richtung setzen** — Bewegungsrichtung festlegen (0-360 Grad)
- **Set Horizontal Speed** — hspeed festlegen
- **Set Vertical Speed** — vspeed festlegen
- **Zu Punkt bewegen** — Zu Koordinaten bewegen
- **Jump to Position** — Sofort zu Koordinaten teleportieren
- **Zur Startposition springen** — Zurück zur Erstellungsposition
- **Zu zufälliger Position springen** — An eine zufällige Position teleportieren

### Instanz-Aktionen
- **Create Instance** — Ein neues Objekt erzeugen
- **Destroy Instance** — Die aktuelle Instanz entfernen
- **Change Instance** — In einen anderen Objekttyp verwandeln

### Zeitsteuerungs-Aktionen
- **Set Alarm** — Einen Countdown-Timer starten
- **Sleep** — Ausführung kurz pausieren

### Zeichen-Aktionen
- **Draw Sprite** — Ein Sprite zeichnen
- **Draw Text** — Text auf dem Bildschirm anzeigen
- **Draw Rectangle** — Ein gefülltes oder umrandetes Rechteck zeichnen
- **Punkte zeichnen** — Den aktuellen Punktestand anzeigen
- **Leben zeichnen** — Verbleibende Leben anzeigen
- **Gesundheitsbalken zeichnen** — Gesundheitsbalken anzeigen

### Score/Leben/Gesundheit
- **Set Score** — Punktestand ändern
- **Set Lives** — Lebenszahl ändern
- **Set Health** — Gesundheitswert ändern
- **Punkte testen** — Punktestand-Bedingung prüfen
- **Leben testen** — Lebenszahl-Bedingung prüfen
- **Gesundheit testen** — Gesundheits-Bedingung prüfen

### Room-Aktionen
- **Next Room** — Zum nächsten Room gehen
- **Previous Room** — Zum vorherigen Room gehen
- **Restart Room** — Den aktuellen Room zurücksetzen
- **Go to Room** — Zu einem bestimmten Room springen

### Sound-Aktionen
- **Play Sound** — Einen Soundeffekt abspielen
- **Stop Sound** — Einen abgespielten Sound stoppen
- **Play Music** — Hintergrundmusik abspielen
- **Stop Music** — Hintergrundmusik stoppen

### Variablen-Aktionen
- **Set Variable** — Einer Variable einen Wert zuweisen
- **Variable testen** — Eine Variablen-Bedingung prüfen

---

## Visuelle Programmierung mit Blockly

Anstatt die Aktionsliste zu verwenden, können Sie zum **Blockly**-Tab
wechseln, um visuell zu programmieren:

1. Öffnen Sie ein Objekt
2. Klicken Sie auf den **Blockly**-Tab
3. Ziehen Sie Blöcke aus der Werkzeugleiste, um Logik zu erstellen
4. Blöcke rasten ineinander ein und bilden vollständige Programme

Siehe [[Visuelle_Programmierung_de]] für weitere Details.

---

## Tipps und bewährte Praktiken

### Organisation
- Geben Sie Objekten beschreibende Namen
- Gruppieren Sie verwandte Objekte mit ähnlichen Präfixen
- Verwenden Sie das Create-Event nur zur Initialisierung

### Leistung
- Vermeiden Sie aufwendige Berechnungen im Step-Event
- Verwenden Sie Alarme statt manuell Frames zu zählen
- Zerstören Sie Instanzen, die den Room verlassen

### Fehlersuche
- Verwenden Sie die Aktion **Show Message**, um Werte anzuzeigen
- Prüfen Sie die Konsolenausgabe auf Fehler
- Testen Sie häufig während der Entwicklung

---

## Nächste Schritte

- [[Raum_Editor_de]] - Platzieren Sie Objekte in Ihren Spiel-Räumen
- [[Events_und_Aktionen_de]] - Vollständige Referenz aller Events und Aktionen
- [[Visuelle_Programmierung_de]] - Lernen Sie die Blockly-Blockprogrammierung
