# Events und Aktionen

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

[Zurück zur Startseite](Home_de)

Events und Aktionen bilden das Herzstück der Spiellogik in pyGM.

## Konzept

### Events
Events sind Auslöser, die auf bestimmte Situationen reagieren:
- Spielstart
- Tastendruck
- Kollision
- Timer

### Aktionen
Aktionen sind die Reaktionen auf Events:
- Bewegen
- Erstellen/Zerstören
- Werte ändern
- Sounds abspielen

## Event-Kategorien

### Erstellungs-Events
- **Create**: Einmalig bei Instanz-Erstellung
- **Destroy**: Beim Löschen der Instanz
- **Room Start**: Beim Betreten eines Raums

### Schritt-Events
- **Step**: Jeden Frame
- **Begin Step**: Vor der Kollisionsprüfung
- **End Step**: Nach der Kollisionsprüfung

### Eingabe-Events
- **Tastatur**: Tastendruck/Loslassen
- **Maus**: Klicks und Bewegung

### Kollisions-Events
- Berührung mit anderen Objekten
- Berührung mit Wänden
- Bereichsprüfungen

### Zeichen-Events
- **Draw**: Normale Zeichnung
- **Draw GUI**: Oberflächenelemente

### Sonstige Events
- **Alarm**: Timer-basierte Events
- **Animation End**: Sprite-Animation beendet

## Aktions-Bibliothek

### Bewegung
- `move_towards_point`: Zu Punkt bewegen
- `set_speed`: Geschwindigkeit setzen
- `set_direction`: Richtung setzen
- `bounce`: Abprallen

### Instanzen
- `create_instance`: Neue Instanz erstellen
- `destroy_instance`: Instanz löschen
- `set_sprite`: Sprite wechseln

### Variablen
- `set_variable`: Wert setzen
- `test_variable`: Bedingte Prüfung

### Audio
- `play_sound`: Sound abspielen
- `stop_sound`: Sound stoppen
- `set_volume`: Lautstärke ändern

### Raum
- `goto_room`: Raum wechseln
- `restart_room`: Raum neu starten
- `next_room`: Nächster Raum

### Zeichnen
- `draw_sprite`: Sprite zeichnen
- `draw_text`: Text anzeigen
- `draw_rectangle`: Rechteck zeichnen

## Bedingungen und Ablaufsteuerung

### Bedingte Aktionen
```
Wenn Variable == Wert
  Aktion ausführen
Sonst
  Alternative Aktion
```

### Schleifen
- Aktionen wiederholen
- Für alle Instanzen

## Best Practices

1. **Step-Events sparsam nutzen**: Nur wenn nötig
2. **Kollisionen optimieren**: Solid-Eigenschaft beachten
3. **Events gruppieren**: Zusammengehörige Logik bündeln
4. **Alarme nutzen**: Für zeitgesteuerte Aktionen

## Siehe auch

- [Objekt-Editor](Objekt_Editor_de)
- [Visuelle Programmierung](Visuelle_Programmierung_de)
- [FAQ](FAQ_de)
