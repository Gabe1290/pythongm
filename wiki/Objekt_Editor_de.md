# Objekt-Editor

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

[Zurück zur Startseite](Home_de)

Der Objekt-Editor ist das zentrale Werkzeug zur Definition des Verhaltens von Spielelementen.

## Überblick

Objekte sind die Bausteine Ihres Spiels. Sie definieren:
- Aussehen (Sprite)
- Verhalten (Events und Aktionen)
- Physik-Eigenschaften
- Interaktionen

## Editor-Oberfläche

### Hauptbereiche
1. **Objektliste**: Alle Objekte im Projekt
2. **Eigenschaften-Panel**: Grundeinstellungen
3. **Event-Liste**: Definierte Events
4. **Aktions-Editor**: Aktionen für Events

## Objekt-Eigenschaften

### Allgemein
- **Name**: Eindeutiger Bezeichner (z. B. obj_spieler)
- **Sprite**: Zugewiesene Grafik
- **Sichtbar**: Ob das Objekt gerendert wird
- **Persistent**: Überlebt Raumwechsel

### Physik
- **Solid**: Kollidiert mit anderen Objekten
- **Tiefe**: Zeichenreihenfolge
- **Eltern-Objekt**: Vererbung von Eigenschaften

## Mit Events arbeiten

### Event hinzufügen
1. Klicken Sie auf „Event hinzufügen"
2. Wählen Sie den Event-Typ
3. Fügen Sie Aktionen hinzu

### Event-Typen
- **Create**: Beim Erstellen der Instanz
- **Step**: Jeden Frame
- **Draw**: Zum Zeichnen
- **Tastatur**: Tasteneingaben
- **Maus**: Mausinteraktionen
- **Kollision**: Bei Berührung mit anderen Objekten

## Aktionen verwenden

### Aktionen hinzufügen
1. Wählen Sie ein Event
2. Ziehen Sie Aktionen aus der Bibliothek
3. Konfigurieren Sie Parameter

### Häufige Aktionen
- Bewegen in Richtung
- Variable setzen
- Instanz erstellen/zerstören
- Sound abspielen
- Raum wechseln

## Best Practices

1. **Klare Benennung**: Verwenden Sie ein Präfix wie „obj_"
2. **Modularität**: Kleine, wiederverwendbare Objekte
3. **Vererbung nutzen**: Eltern-Objekte für gemeinsames Verhalten
4. **Dokumentation**: Kommentare in komplexen Events

## Siehe auch

- [Events und Aktionen](Events_und_Aktionen_de)
- [Visuelle Programmierung](Visuelle_Programmierung_de)
- [Raum-Editor](Raum_Editor_de)
