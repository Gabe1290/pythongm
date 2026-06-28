# Spiele exportieren

> [English](Exporting-Games) | [Français](Exportation_fr) | [Deutsch](Spiele_Exportieren_de) | [Italiano](Esportare_Giochi_it) | [Español](Exportar_Juegos_es) | [Português](Exportar_Jogos_pt) | [Slovenščina](Izvoz_Iger_sl) | [Українська](Eksport_Ihor_uk) | [Русский](Eksport_Igr_ru)

---

[Zuruck zur Startseite](Home_de)

Erfahren Sie, wie Sie Ihre pyGM-Spiele fur verschiedene Plattformen exportieren.

## Uberblick

pyGM ermoglicht den Export fur:
- Windows (EXE)
- macOS (APP)
- Linux
- Web (HTML5)

## Export-Vorbereitung

### Vor dem Export prufen
1. **Alle Ressourcen vorhanden**: Sprites, Sounds, etc.
2. **Spiel getestet**: Keine kritischen Fehler
3. **Einstellungen optimiert**: Auflosung, Fullscreen

### Projekt-Einstellungen
- **Spielname**: Angezeigter Name
- **Version**: Versionsnummer
- **Icon**: Anwendungssymbol
- **Startbildschirm**: Splash Screen

## Windows-Export

### Voraussetzungen
- pyinstaller installiert
- Windows-System oder Cross-Compilation

### Schritte
1. Gehen Sie zu Datei > Exportieren
2. Wahlen Sie "Windows Executable"
3. Konfigurieren Sie Optionen:
   - Icon-Datei
   - Konsolenfenster ausblenden
   - Einzelne EXE-Datei
4. Klicken Sie auf "Exportieren"

### Ausgabe
- Einzelne EXE-Datei
- Oder Ordner mit Abhangigkeiten

## macOS-Export

### Voraussetzungen
- macOS-System empfohlen
- py2app oder pyinstaller

### Schritte
1. Datei > Exportieren > macOS
2. App-Bundle-Name eingeben
3. Icon wahlen (ICNS-Format)
4. Exportieren

## Linux-Export

### Optionen
- AppImage (empfohlen)
- Debian-Paket
- Ausfuhrbare Datei

### Schritte
1. Datei > Exportieren > Linux
2. Format wahlen
3. Exportieren

## Web-Export (HTML5)

### Vorteile
- Lauft im Browser
- Einfach zu teilen
- Keine Installation notig

### Schritte
1. Datei > Exportieren > Web
2. Konfigurieren:
   - Canvas-Grosse
   - Ladebildschirm
   - Komprimierung
3. Exportieren

### Ausgabe
- HTML-Datei
- JavaScript-Dateien
- Ressourcen-Ordner

### Hosting
- Auf Webserver hochladen
- itch.io nutzen
- GitHub Pages verwenden

## Export-Optionen

### Allgemein
- **Komprimierung**: Dateigrosse reduzieren
- **Debug-Modus**: Fur Tests beibehalten
- **Ressourcen einbetten**: Alles in eine Datei

### Plattform-spezifisch
- **Windows**: UAC-Manifest
- **macOS**: Code-Signierung
- **Web**: WebGL-Version

## Fehlerbehebung

### Haufige Probleme

**Export schlagt fehl**
- Prufen Sie Fehlermeldungen
- Aktualisieren Sie pyinstaller

**Ressourcen fehlen**
- Pfade uberprufen
- Ressourcen neu einbinden

**Spiel startet nicht**
- Im Debug-Modus testen
- Abhangigkeiten prufen

## Optimierung

1. **Bildgrosse optimieren**: Sprites komprimieren
2. **Sounds komprimieren**: MP3 statt WAV
3. **Ungenutzte Ressourcen entfernen**
4. **Code optimieren**: Effizienz verbessern

## Siehe auch

- [FAQ](FAQ_de)
- [Ihr erstes Spiel erstellen](Erstes_Spiel_de)
- [Erste Schritte](Erste_Schritte_de)
