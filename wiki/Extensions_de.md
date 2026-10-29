# Erweiterungen

*[Startseite](Home_de) | [3D-Ansicht](3D-View_de) | [Netzwerk](Network_de) | [micro:bit](Microbit_de) | [File Exchange Multiplayer](FileExchange) (englisch) | [Vollständige Aktionsreferenz](Full-Action-Reference_de)*

---

Eine **Erweiterung** ist ein eigenständiges Zusatzmodul, das PyGameMaker um
Fähigkeiten erweitert, ohne den Kern-Engine zu verändern. Eine Erweiterung kann
beisteuern:

- neue **Aktionen** (sie erscheinen im Aktionsauswahldialog wie jede eingebaute
  Aktion),
- eine neue Art, einen **Raum zu zeichnen** (ein benutzerdefinierter Renderer), und
- den passenden **Export-Code**, sodass Spiele, die sie nutzen, weiterhin nach
  HTML5 und Kivy/Android exportieren.

Die eingebaute **2.5D-Raycast**-Erweiterung (die Funktion [3D-Ansicht](3D-View_de))
ist das ausgearbeitete Beispiel: Sie fügt vier „3D-Ansicht"-Aktionen und einen
First-Person-Renderer hinzu und exportiert in alle drei Ziele.

Die eingebaute **LAN-Multiplayer**-Erweiterung (die Funktion [Netzwerk](Network_de)) ist eine zweite, größere: Sie fügt 15 „Netzwerk“-Aktionen und sechs Ereignisse hinzu und vernetzt ein Spiel über das lokale Netzwerk — aus dem Desktop-Export (als Host oder Client) und dem HTML5-Export (als Client).

Die Erweiterung **File Exchange Multiplayer** (die Funktion [File Exchange Multiplayer](FileExchange), auf Englisch) ist ein rundenbasierter Verwandter von LAN-Multiplayer: Sie fügt 7 „Netzwerk“-Aktionen und sechs Ereignisse hinzu und tauscht den Spielzustand über Dateien auf einem gemeinsamen Laufwerk statt über eine Live-Verbindung aus — für ein Klassenzimmer, in dem eine Firewall die direkten Verbindungen von LAN-Multiplayer blockiert. Nur im Desktop-Export — siehe den Hinweis „Why not every export“ auf der Seite selbst.

Die eingebaute **micro:bit**-Erweiterung (die Funktion [micro:bit](Microbit_de)) setzt einen simulierten BBC micro:bit ins Spielfenster: 16 Aktionen, 24 Ereignisse, eine gezeichnete Platine mit klickbaren Tasten und einer Sensorleiste, Ton und Funk. Sie ist standardmäßig vorhanden, wird aber pro Projekt eingeschaltet (**Projekteinstellungen → Erweiterungen**) und funktioniert in „Spiel testen“ sowie in den Exporten für Desktop, HTML5 und Android (Kivy).

---

## Aktivieren und deaktivieren

Erweiterungen werden **aktiviert** ausgeliefert. Sie können eine abschalten (oder
eine deaktiviert ausgelieferte aktivieren), ohne Code zu bearbeiten, über den
Schlüssel `extensions` in Ihrer Konfiguration — eine Zuordnung
`Ordnername → an/aus`:

```json
"extensions": { "raycast_2_5d": false }
```

Ein **fehlender** Eintrag bedeutet „Standardwert der Erweiterung verwenden", sodass
nie etwas verschwindet, weil ein Schlüssel fehlte. Änderungen werden beim nächsten
Start wirksam (Aktionen registrieren sich beim Start).

Bei deaktivierter 2.5D-Raycast-Erweiterung stellt ein Raum, der die
First-Person-Ansicht aktiviert, einfach die Draufsicht dar.

---

## Wenn ein Projekt eine Erweiterung benötigt

Da eine Erweiterung abgeschaltet werden kann, hilft Ihnen PyGameMaker, böse
Überraschungen zu vermeiden:

- **Beim Laden**: Nutzt ein Projekt Aktionen aus einer derzeit deaktivierten
  Erweiterung, zeigt die IDE eine Warnung, die die Erweiterung und die betroffenen
  Funktionen benennt (damit ein 3D-Spiel nicht stillschweigend als Draufsicht
  erscheint).
- **Beim Speichern** vermerkt das Projekt die Erweiterungen, von denen seine
  Aktionen abhängen, in `project.json` (eine Liste `requires_extensions`) — ein
  dauerhafter Hinweis, den jeder sehen kann, mit dem Sie das Projekt teilen. Ein
  Projekt, das keine Erweiterungsaktionen nutzt, lässt das Feld einfach weg.

---

## Erweiterungen und Plugins

Beide fügen Aktionen hinzu; sie unterscheiden sich nur in der Verpackung:

| | Plugin | Erweiterung |
|---|--------|-----------|
| Form | eine einzelne `.py`-Datei in `plugins/` | ein Ordner in `extensions/` mit einem Manifest |
| Ideal für | eine kleine Menge von Aktionen | eine Funktion über mehrere Dateien und/oder mit Zeichnen/Export |
| Beispiel | die **Audio**-Aktionen (`plugins/audio_actions.py`) | **2.5D-Raycast** (`extensions/raycast_2_5d/`) |

---

## Wie ein Erweiterungsordner aussieht

Für Neugierige (und für jeden, der eine schreibt) ist eine Erweiterung ein
lesbarer Ordner:

```
extensions/raycast_2_5d/
├── extension.json     # Manifest: Name, Version, aktiviert, provides_actions
├── actions.py         # die Aktionsschemas (im Auswahldialog angezeigt)
├── handlers.py        # was die Aktionen zur Laufzeit tun
├── renderer.py        # der benutzerdefinierte Raum-Renderer (der Raycaster)
├── state.py           # der Zustand pro Raum (unter dem Raum abgelegt)
├── hud.py             # die Geometrie-Generatoren für Minikarte / DOOM-Leiste
├── export_html5.js    # der HTML5-Port, in den Web-Export injiziert
├── export_kivy.py     # der Kivy-Port, in den Mobil-/Desktop-Export injiziert
└── README.md          # wie alles zusammenpasst
```

Die Liste `provides_actions` im Manifest ist das, was der IDE erlaubt, die genaue
Erweiterung zu benennen, wenn ein Projekt eine deaktivierte benötigt.

---

## Siehe auch

- [3D-Ansicht](3D-View_de) — die Funktion, die die eingebaute Erweiterung bereitstellt
- [Netzwerk](Network_de) — die Funktion, die die LAN-Multiplayer-Erweiterung bereitstellt
- [micro:bit](Microbit_de) — die Funktion, die die micro:bit-Erweiterung bereitstellt
- [File Exchange Multiplayer](FileExchange) (englisch) — die Funktion, die die File-Exchange-Multiplayer-Erweiterung bereitstellt
- [Vollständige Aktionsreferenz](Full-Action-Reference_de) — Erweiterungsaktionen erscheinen auch hier
- [Spiele exportieren](Spiele_Exportieren_de) — Erweiterungsfunktionen werden in Exporte übernommen
