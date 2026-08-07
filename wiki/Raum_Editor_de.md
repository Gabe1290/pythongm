# Raum-Editor

> [English](Room-Editor) | [Français](Editeur_Salles_fr) | [Deutsch](Raum_Editor_de) | [Italiano](Editor_Stanze_it) | [Español](Editor_Salas_es) | [Português](Editor_Salas_pt) | [Slovenščina](Urejevalnik_Sob_sl) | [Українська](Redaktor_Kimnat_uk) | [Русский](Redaktor_Komnat_ru)

---

[Zurück zur Startseite](Home_de)

Räume sind die Level, Bildschirme oder Szenen Ihres Spiels. Der Raum-Editor
ermöglicht das Gestalten dieser Räume durch Platzieren von Objekten und
Konfigurieren von Hintergründen.

---

## Den Raum-Editor öffnen

1. Doppelklicken Sie auf einen vorhandenen Room im Ressourcenbaum, oder
2. Rechtsklick auf **Rooms** > **Room erstellen**

---

## Room-Eigenschaften

| Eigenschaft | Beschreibung |
|-------------|--------------|
| **Name** | Eindeutiger Bezeichner (z. B. `room_level1`) |
| **Breite** | Room-Breite in Pixeln |
| **Höhe** | Room-Höhe in Pixeln |
| **Geschwindigkeit** | Spielgeschwindigkeit in Bildern pro Sekunde (Standard: 60) |
| **Persistent** | Room-Zustand beim Verlassen/Wiederbetreten beibehalten |

### Namenskonvention

Verwenden Sie das Präfix `room_` für Rooms:
- `room_menu`
- `room_level1`
- `room_game_over`

---

## Objekte platzieren

### Instanzen hinzufügen

1. Wählen Sie ein Objekt im **Objekte**-Panel aus
2. Klicken Sie in die Raumansicht, um eine Instanz zu platzieren
3. Klicken und ziehen Sie, um mehrere Instanzen zu platzieren

### Instanzen auswählen

- Klicken Sie auf eine Instanz, um sie auszuwählen
- Halten Sie **Strg** und klicken Sie, um mehrere auszuwählen
- Ziehen Sie ein Rechteck, um alle Instanzen darin auszuwählen

### Instanzen verschieben

- Ziehen Sie ausgewählte Instanzen mit der Maus
- Verwenden Sie die Pfeiltasten für präzise Bewegung

### Instanzen löschen

- Wählen Sie Instanzen aus und drücken Sie **Entf**, oder
- Rechtsklick und „Löschen" wählen

---

## Raster-Einstellungen

Aktivieren Sie das Raster für präzise Platzierung:

1. Gehen Sie zu **Ansicht > Raster anzeigen**
2. Legen Sie die Rastergröße fest (z. B. 32×32)
3. Aktivieren Sie „Am Raster ausrichten"

Übliche Rastergrößen:
- **16×16** — Kleine Kacheln
- **32×32** — Standard-Kacheln
- **64×64** — Große Kacheln

---

## Hintergründe

### Einen Hintergrund festlegen

1. Klicken Sie auf den **Hintergründe**-Tab
2. Wählen Sie eine Hintergrund-Ressource
3. Konfigurieren Sie die Anzeigeoptionen

### Hintergrund-Optionen

| Option | Beschreibung |
|--------|--------------|
| **Sichtbar** | Hintergrund anzeigen/verbergen |
| **Vordergrund** | Vor den Objekten zeichnen |
| **Horizontal kacheln** | Horizontal wiederholen |
| **Vertikal kacheln** | Vertikal wiederholen |
| **Strecken** | Auf Raumgröße strecken |
| **Horizontale Geschwindigkeit** | Scroll-Geschwindigkeit (Parallaxe) |
| **Vertikale Geschwindigkeit** | Scroll-Geschwindigkeit (Parallaxe) |

### Hintergrund-Layer

Ein Room unterstützt bis zu **8 Hintergrund-Layer**, jeder mit eigener
Scroll-Geschwindigkeit für Parallax-Effekte. Beispielaufbau:
- Layer 0: Himmel (am weitesten hinten)
- Layer 1: Berge (langsameres Scrollen)
- Layer 2: Bäume (mittleres Scrollen)
- Layer 3: Boden (kein Scrollen)

---

## Views (Kamera)

Views bestimmen, welcher Ausschnitt des Rooms auf dem Bildschirm sichtbar
ist. Bis zu **8 Views** (View 0 bis View 7) können pro Room konfiguriert
werden — View 0 ist standardmäßig sichtbar; aktivieren Sie weitere Views
für Splitscreen oder Bild-im-Bild.

### Views aktivieren

1. Aktivieren Sie „Views aktivieren" in den Room-Eigenschaften
2. Konfigurieren Sie View 0 (die primäre View)

### View-Eigenschaften

| Eigenschaft | Beschreibung |
|-------------|--------------|
| **View X/Y** | Obere linke Ecke der View im Room |
| **View-Breite/Höhe** | Größe des sichtbaren Bereichs |
| **Port X/Y** | Position auf dem Bildschirm |
| **Port-Breite/Höhe** | Größe auf dem Bildschirm (kann gestreckt werden) |
| **Verfolgtes Objekt** | Objekt, dem die View folgt |
| **Rand H/V** | Toter Bereich, bevor die Kamera sich bewegt |

### Einem Objekt folgen

Damit die Kamera dem Spieler folgt:
1. Setzen Sie „Verfolgtes Objekt" auf `obj_player`
2. Passen Sie „Rand H" und „Rand V" für sanftes Scrollen an

---

## Room-Reihenfolge

Die Reihenfolge der Rooms im Ressourcenbaum bestimmt:
1. Welcher Room zuerst lädt (oberster Room = Start-Room)
2. Die Reihenfolge für die Aktionen „Next Room" und „Previous Room"

### Room-Reihenfolge ändern

- Ziehen Sie Rooms im Ressourcenbaum, um sie neu anzuordnen
- Oder Rechtsklick und „Nach oben" / „Nach unten" verwenden

---

## Tipps und bewährte Praktiken

### Organisation
- Benennen Sie Rooms klar nach ihrem Zweck
- Behalten Sie das Hauptmenü als ersten Room
- Verwenden Sie konsistente Room-Größen innerhalb eines Spiels

### Leistung
- Platzieren Sie nicht zu viele Instanzen in einem Room
- Verwenden Sie Kacheln für statische Level-Geometrie
- Zerstören Sie Instanzen außerhalb des Bildschirms, wenn möglich

---

## Nächste Schritte

- [[Objekt_Editor_de]] - Objekte erstellen, die in Rooms platziert werden
- [[Events_und_Aktionen_de]] - Interaktivität zu Ihren Levels hinzufügen
- [[Spiele_Exportieren_de]] - Ihr fertiges Spiel weitergeben
