# Events und Aktionen

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

[Zuruck zur Startseite](Home_de)

Events und Aktionen bilden das Herzstuck der Spiellogik in pyGM.

## Konzept

### Events
Events sind Ausloser, die auf bestimmte Situationen reagieren:
- Spielstart
- Tastendruck
- Kollision
- Timer

### Aktionen
Aktionen sind die Reaktionen auf Events:
- Bewegen
- Erstellen/Zerstoren
- Werte andern
- Sounds abspielen

## Event-Kategorien

### Erstellungs-Events
- **Create**: Einmalig bei Instanz-Erstellung
- **Destroy**: Beim Loschen der Instanz
- **Room Start**: Beim Betreten eines Raums

### Schritt-Events
- **Step**: Jeden Frame
- **Begin Step**: Vor Kollisionsprufung
- **End Step**: Nach Kollisionsprufung

### Eingabe-Events
- **Tastatur**: Tastendruck/Loslass
- **Maus**: Klicks und Bewegung
- **Gamepad**: Controller-Eingaben

### Kollisions-Events
- Beruhrung mit anderen Objekten
- Beruhrung mit Wanden
- Bereichsprufungen

### Zeichen-Events
- **Draw**: Normale Zeichnung
- **Draw GUI**: Oberflachenelemente
- **Draw Begin/End**: Vor/Nach dem Zeichnen

### Sonstige Events
- **Alarm**: Timer-basierte Events
- **Animation End**: Sprite-Animation beendet
- **User Events**: Benutzerdefinierte Events

## Aktions-Bibliothek

### Bewegung
- `move_towards`: Zu Punkt bewegen
- `set_speed`: Geschwindigkeit setzen
- `set_direction`: Richtung setzen
- `bounce`: Abprallen

### Instanzen
- `instance_create`: Neue Instanz erstellen
- `instance_destroy`: Instanz loschen
- `change_sprite`: Sprite wechseln

### Variablen
- `set_variable`: Wert setzen
- `add_to_variable`: Wert addieren
- `if_variable`: Bedingte Prufung

### Audio
- `play_sound`: Sound abspielen
- `stop_sound`: Sound stoppen
- `set_volume`: Lautstarke andern

### Raum
- `goto_room`: Raum wechseln
- `restart_room`: Raum neustarten
- `goto_next_room`: Nachster Raum

### Zeichnen
- `draw_sprite`: Sprite zeichnen
- `draw_text`: Text anzeigen
- `draw_rectangle`: Rechteck zeichnen

## Bedingungen und Ablaufsteuerung

### Bedingte Aktionen
```
Wenn Variable == Wert
  Aktion ausfuhren
Sonst
  Alternative Aktion
```

### Schleifen
- Aktionen wiederholen
- Fur alle Instanzen

## Best Practices

1. **Step-Events sparsam nutzen**: Nur wenn notig
2. **Kollisionen optimieren**: Solid-Eigenschaft beachten
3. **Events gruppieren**: Zusammengehorige Logik bundeln
4. **Alarme nutzen**: Fur zeitgesteuerte Aktionen

## Siehe auch

- [Objekt-Editor](Objekt_Editor_de)
- [Visuelle Programmierung](Visuelle_Programmierung_de)
- [FAQ](FAQ_de)
