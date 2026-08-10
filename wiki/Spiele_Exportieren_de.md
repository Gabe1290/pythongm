# Spiele exportieren

> [English](Exporting-Games) | [Français](Exportation_fr) | [Deutsch](Spiele_Exportieren_de) | [Italiano](Esportare_Giochi_it) | [Español](Exportar_Juegos_es) | [Português](Exportar_Jogos_pt) | [Slovenščina](Izvoz_Iger_sl) | [Українська](Eksport_Ihor_uk) | [Русский](Eksport_Igr_ru)

---

> [Zurück zur Startseite](Home_de)

PyGameMaker kann Ihr Spiel auf mehrere Plattformen exportieren. Dieser Leitfaden behandelt jede Exportoption und ihre Verwendung.

---

## Überblick über den Export

| Plattform | Format | Voraussetzungen |
|-----------|--------|-----------------|
| **Windows** | .exe | PyInstaller |
| **macOS** | .app | PyInstaller (auf einem Mac) |
| **HTML5** | .html | Moderner Browser |
| **Linux** | Binärdatei | PyInstaller, Python 3.10+ |
| **Kivy / Android** | Quellcode / .apk | Buildozer |
| **Projekt (.zip)** | .zip | — (das bearbeitbare Projekt teilen) |

> **Nichts wird stillschweigend verworfen.** Wenn Ihr Spiel eine Aktion verwendet,
> die ein Ziel nicht reproduzieren kann (zum Beispiel werden einige Aktionen vom
> Kivy/Android-Export nicht unterstützt), gelingt der Export dennoch, teilt Ihnen
> aber genau mit, welche Aktionen **übersprungen** wurden, damit Sie nachbessern
> können. Wenn Ihr Projekt eine deaktivierte [Erweiterung](Extensions_de) nutzt
> (z. B. die 3D-Ansicht), warnt Sie die IDE beim Laden.

---

## Windows-EXE-Export

Erstellen Sie eine eigenständige Windows-Executable, die ohne installiertes Python läuft.

### So exportieren Sie

1. Öffnen Sie **Datei → Projekt exportieren…** (Strg+E) und wählen Sie **Windows**
2. Wählen Sie einen Ausgabeordner
3. Warten Sie, bis der Build-Vorgang abgeschlossen ist
4. Finden Sie die .exe-Datei im Ausgabeordner

### Was erstellt wird

```
ausgabeordner/
├── MeinSpiel.exe     # Haupt-Executable
├── _internal/        # Erforderliche Bibliotheken
└── assets/           # Spielressourcen
```

### Voraussetzungen

- PyInstaller (installiert über `pip install pyinstaller`)
- Windows-System für den Build (Cross-Kompilierung wird nicht unterstützt)

### Verteilung

Um Ihr Spiel zu teilen:
1. Komprimieren Sie den gesamten Ausgabeordner als ZIP
2. Verteilen Sie die ZIP-Datei
3. Benutzer entpacken und starten die .exe

### Fehlerbehebung

**Fehlende DLLs:** Stellen Sie sicher, dass alle Abhängigkeiten enthalten sind. Prüfen Sie die PyInstaller-Ausgabe auf Warnungen.

**Antivirus-Warnungen:** Manche Antivirenprogramme melden PyInstaller-Executables. Das ist ein Fehlalarm. Möglicherweise müssen Sie Ihre Executable signieren.

---

## macOS-App-Export

Erstellen Sie ein natives macOS-`.app`-Bundle mit PyInstaller.

### So exportieren Sie

1. Öffnen Sie **Datei → Projekt exportieren…** (Strg+E) und wählen Sie **macOS**
2. Wählen Sie einen Ausgabeordner
3. Warten Sie, bis der Build abgeschlossen ist
4. Finden Sie `MeinSpiel.app` im Ausgabeordner

### Voraussetzungen

- Ein **Mac** für den Build (Cross-Kompilierung von Windows/Linux wird nicht unterstützt)
- PyInstaller und Kivy im Build-Python installiert

### Verteilung

Komprimieren Sie das `.app`-Bundle als ZIP, um es zu teilen. Unsignierte Apps lösen
auf anderen Macs Gatekeeper aus — Benutzer öffnen sie beim ersten Mal per
Rechtsklick → **Öffnen**, oder Sie signieren/notarisieren die App mit einem
Apple-Developer-Konto.

---

## HTML5-Export

Erstellen Sie eine einzelne HTML-Datei, die in Webbrowsern läuft.

### So exportieren Sie

1. Gehen Sie zu **Datei → Als HTML5 exportieren…**
2. Wählen Sie einen Speicherort
3. Wählen Sie Optionen (Komprimierung usw.)
4. Klicken Sie auf Exportieren

### Was erstellt wird

```
ausgabeordner/
└── MeinSpiel.html    # Einzeldatei-Spiel
```

### Merkmale

- Läuft in jedem modernen Browser (Chrome, Firefox, Edge, Safari)
- Keine Installation erforderlich
- Mit gzip komprimiert für schnelles Laden
- Mobilfreundlich mit Touch-Steuerung

### Ihr Spiel hosten

Laden Sie die HTML-Datei hoch auf:
- Ihren eigenen Webserver
- GitHub Pages (kostenlos)
- itch.io (spielorientiertes Hosting)
- Jedes Hosting für statische Dateien

### Browser-Kompatibilität

| Browser | Unterstützung |
|---------|---------------|
| Chrome 80+ | Vollständig |
| Firefox 75+ | Vollständig |
| Edge 80+ | Vollständig |
| Safari 13+ | Vollständig |
| Mobiles Chrome | Vollständig |
| Mobiles Safari | Vollständig |

### Einschränkungen

- Einige Funktionen funktionieren möglicherweise nicht (Dateisystemzugriff usw.)
- Audio erfordert möglicherweise eine Benutzerinteraktion zum Start
- Die Leistung hängt vom Gerät/Browser ab

---

## Linux-Export

Erstellen Sie eine native Linux-Executable.

### So exportieren Sie

1. Öffnen Sie **Datei → Projekt exportieren…** (Strg+E) und wählen Sie **Linux**
2. Wählen Sie einen Ausgabeordner
3. Warten Sie den Build-Vorgang ab

### Voraussetzungen

- Linux-System für den Build
- Python 3.10+
- PyInstaller

### Verteilung

```bash
# Die Datei ausführbar machen
chmod +x MeinSpiel

# Das Spiel starten
./MeinSpiel
```

Als .tar.gz-Archiv verteilen:
```bash
tar -czvf MeinSpiel-linux.tar.gz MeinSpiel/
```

---

## Kivy-Export (Mobil)

Erstellen Sie mobile Apps für iOS und Android mit dem Kivy-Framework.

### So exportieren Sie

1. Gehen Sie zu **Datei → Nach Kivy exportieren…**
2. Wählen Sie einen Ausgabeordner
3. Konfigurieren Sie die mobilen Einstellungen
4. Exportieren Sie das Kivy-Projekt

### Für Android bauen

Das exportierte Kivy-Projekt nutzt Buildozer, um APKs zu erstellen:

```bash
cd exportiertes_projekt
pip install buildozer
buildozer init
buildozer android debug
```

### Für iOS bauen

Erfordert einen Mac mit Xcode:

```bash
cd exportiertes_projekt
pip install kivy-ios
toolchain build python3 kivy
toolchain create MeinSpiel ~/ios_projekt
```

### Mobile Überlegungen

- Touch-Steuerung wird automatisch zugeordnet
- Die Bildschirmskalierung wird automatisch gehandhabt
- Testen Sie auf mehreren Bildschirmgrößen
- Optimieren Sie die Ressourcengrößen für Mobilgeräte

---

## Projekt-Export (.zip)

Teilen Sie das **bearbeitbare Projekt** selbst (kein kompiliertes Spiel):
Verwenden Sie **Datei → Projekt exportieren…** (Strg+E), um ein `.zip`-Archiv zu
erstellen, das jemand anderes wieder in PyGameMaker öffnen kann. Ideal für
Zusammenarbeit, Backups oder die Abgabe von Schularbeiten.

---

## Export-Einstellungen

### Allgemeine Einstellungen

| Einstellung | Beschreibung |
|-------------|--------------|
| **Spielname** | In Titelleiste/App angezeigter Name |
| **Symbol** | Anwendungssymbol (Windows/Mobil) |
| **Version** | Versionsnummer (1.0.0) |
| **Autor** | Name des Entwicklers |

### Windows-Einstellungen

| Einstellung | Beschreibung |
|-------------|--------------|
| **Konsole** | Konsolenfenster anzeigen (zum Debuggen) |
| **Eine Datei** | Einzelne .exe vs. Ordner mit _internal |
| **UPX** | Mit UPX komprimieren (kleinere Größe) |

### HTML5-Einstellungen

| Einstellung | Beschreibung |
|-------------|--------------|
| **Komprimierung** | gzip-Komprimierung aktivieren |
| **Vollbild** | Im Vollbildmodus starten |
| **Touch-Steuerung** | Bildschirmsteuerung anzeigen |

---

## Checkliste vor dem Export

Prüfen Sie vor dem Export:

- [ ] Alle Ressourcen sind im Projekt enthalten
- [ ] Das Spiel läuft in der IDE korrekt
- [ ] Keine Debug-Meldungen oder Testcode
- [ ] Die Raumreihenfolge stimmt (Startraum zuerst)
- [ ] Audiodateien liegen in unterstützten Formaten vor
- [ ] Sprites sind für die Dateigröße optimiert

---

## Dateigröße optimieren

### Sprites
- Angemessene Abmessungen verwenden (nicht überdimensioniert)
- PNG-Dateien komprimieren
- JPEG für Bilder ohne Transparenz in Betracht ziehen

### Audio
- OGG/MP3 für Musik verwenden (nicht WAV)
- Soundeffekte kurz halten
- Niedrigere Abtastraten für einfache Klänge

### Allgemein
- Ungenutzte Ressourcen entfernen
- Raumgrößen minimieren
- Auf den Zielplattformen testen

---

## Exporte testen

Testen Sie Ihr exportiertes Spiel immer:

1. **Windows:** Auf einem sauberen PC ohne Python testen
2. **HTML5:** In mehreren Browsern testen
3. **Linux:** Wenn möglich auf verschiedenen Distributionen testen
4. **Mobil:** Auf echten Geräten testen, nicht nur in Emulatoren

---

## Verteilungsplattformen

### itch.io
- Kostenloses Hosting für Indie-Spiele
- Unterstützt HTML5, Windows, Linux, Mac
- Integriertes Zahlungssystem

### Steam
- Erfordert die Integration des Steamworks-SDK
- PyInstaller mit der Steam-API verwenden
- Kostenpflichtige Veröffentlichungsgebühr

### Google Play (Android)
- Erfordert ein Entwicklerkonto (25 $)
- Signiertes APK mit Buildozer bauen
- Inhaltsrichtlinien befolgen

### App Store (iOS)
- Erfordert ein Apple-Developer-Konto (99 $/Jahr)
- Mit kivy-ios bauen
- Über App Store Connect einreichen

---

## Nächste Schritte

- [[Erste_Schritte_de]] - Die Grundlagen wiederholen
- [[Troubleshooting_de|Fehlerbehebung]] - Fehlende Abhängigkeiten und andere Exportprobleme
- [[FAQ_de]] - Häufige Fragen zum Export
- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Exportprobleme melden
