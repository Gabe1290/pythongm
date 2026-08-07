# Erste Schritte

> [English](Getting-Started) | [Français](Demarrage_fr) | [Deutsch](Erste_Schritte_de) | [Italiano](Iniziare_it) | [Español](Empezar_es) | [Português](Comecar_pt) | [Slovenščina](Zacetek_sl) | [Українська](Pochatok_uk) | [Русский](Nachalo_ru)

---

> [Zurück zur Startseite](Home_de)

Dieser Leitfaden hilft Ihnen, PyGameMaker auf Ihrem System zum Laufen zu bringen.

---

## Systemanforderungen

- **Python** 3.10 oder höher
- **Betriebssystem:** Windows, Linux oder macOS
- **Festplattenspeicher:** ~500 MB für die Installation
- **RAM:** mindestens 4 GB, 8 GB empfohlen

---

## Installation

### Schritt 1: Python installieren

Laden Sie Python 3.10+ von [python.org](https://www.python.org/downloads/) herunter und installieren Sie es. Aktivieren Sie unter Windows während der Installation „Add Python to PATH".

### Schritt 2: Das Repository klonen

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
```

Oder laden Sie die ZIP-Datei von der [Releases-Seite](https://github.com/Gabe1290/pythongm/releases) herunter.

### Schritt 3: Eine virtuelle Umgebung erstellen

Eine virtuelle Umgebung hält die Abhängigkeiten von PyGameMaker isoliert:

```bash
python -m venv venv
```

Aktivieren Sie die virtuelle Umgebung:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Schritt 4: Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### Schritt 5: PyGameMaker starten

```bash
python main.py
```

---

## Erster Start

Beim ersten Start von PyGameMaker sehen Sie:

1. **Menüleiste** — die Menüs Datei, Bearbeiten, Assets, Build, Werkzeuge und Hilfe
2. **Ressourcenbaum** — linkes Panel mit den Projekt-Assets (Sprites, Sounds, Hintergründe, Objekte, Räume)
3. **Arbeitsbereich** — zentraler Bereich zum Bearbeiten von Assets
4. **Eigenschaften-Panel** — rechtes Panel für Asset-Eigenschaften

---

## Ihr erstes Projekt erstellen

1. Gehen Sie zu **Datei > Neues Projekt**
2. Wählen Sie einen Speicherort und einen Namen für Ihr Projekt
3. Ein neuer Projektordner wird mit der Standardstruktur erstellt

---

## Projektstruktur

Jedes PyGameMaker-Projekt enthält:

```
mein_projekt/
├── project.json      # Projekteinstellungen
├── sprites/          # Sprite-Bilder
├── sounds/           # Audiodateien
├── backgrounds/      # Hintergrundbilder
├── objects/          # Spielobjekt-Definitionen
├── rooms/            # Level-Layouts
├── fonts/            # Schriftdateien
├── scripts/          # Benutzerdefinierte Skripte
└── data/             # Benutzerdefinierte Datendateien
```

---

## Sprache ändern

PyGameMaker unterstützt mehrere Sprachen:

1. Gehen Sie zu **Werkzeuge > Sprache**
2. Wählen Sie Ihre bevorzugte Sprache aus dem Menü
3. Starten Sie PyGameMaker neu, um die Änderung zu übernehmen

Verfügbare Sprachen: Englisch, Französisch, Deutsch, Italienisch, Spanisch, Portugiesisch, Slowenisch, Ukrainisch, Russisch

---

## Nächste Schritte

- [[Erstes_Spiel_de]] - Bauen Sie Schritt für Schritt ein einfaches Spiel
- [[Objekt_Editor_de]] - Lernen Sie, wie man Spielobjekte erstellt
- [[Raum_Editor_de]] - Gestalten Sie Ihre Spiellevel
- [[Events_und_Aktionen_de]] - Verstehen Sie die Spiellogik

---

## Fehlerbehebung

### Python wird nicht gefunden
Stellen Sie sicher, dass Python installiert und zum PATH hinzugefügt ist. Prüfen Sie dies mit `python --version`.

### Fehlende Abhängigkeiten
Bei Importfehlern versuchen Sie, die Abhängigkeiten neu zu installieren:
```bash
pip install -r requirements.txt --force-reinstall
```

### Anzeigeprobleme
Unter Linux benötigt Qt (das GUI-Framework, auf dem PyGameMaker aufbaut) einige
Systembibliotheken, die von `pip` nicht mitinstalliert werden:
```bash
sudo apt-get install -y libegl1 libxkbcommon0 libxcb-cursor0 \
    libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 libasound2-dev libgl1-mesa-dev
```

---

## Hilfe erhalten

- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Fehler melden oder Funktionen anfragen
- [[FAQ_de]] - Häufige Fragen und Antworten
