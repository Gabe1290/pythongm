# Fehlerbehebung

> [English](Troubleshooting) | [Français](Troubleshooting_fr) | [Deutsch](Troubleshooting_de) | [Italiano](Troubleshooting_it)

---

> [Zurück zur Startseite](Home_de)

Häufige Probleme und wo man nachsehen sollte. Für installationsbezogene
Probleme (Python nicht gefunden, fehlende Abhängigkeiten, Linux-
Anzeigebibliotheken) siehe zuerst den Abschnitt Fehlerbehebung in
[[Erste_Schritte_de|Erste Schritte]] — diese Seite behandelt Probleme,
die auftreten, wenn PyGameMaker bereits läuft.

---

## Mein Spiel stürzt ab oder schließt sofort, wenn ich Spiel testen (F5) drücke

**Starten Sie die IDE von einem Terminal aus, nicht über eine
Desktop-Verknüpfung, um den Fehler zu sehen.** Der Traceback eines
abstürzenden Test-Spiel-Subprozesses wird in die Konsolenausgabe der IDE
selbst protokolliert (`python main.py` in einem Terminal) — wenn Sie die
IDE ohne sichtbare Konsole gestartet haben (z. B. über eine
Windows-Verknüpfung), hat diese Meldung nirgendwo, wo sie erscheinen
könnte. Starten Sie erneut über ein Terminal und reproduzieren Sie den
Absturz, um den echten Python-Traceback zu sehen.

Häufige Ursachen:
- Eine **Code ausführen**-Aktion oder benutzerdefinierter Code im
  Code-Editor mit einem Syntaxfehler oder einem Tippfehler in einem
  `game.*`/`self.*`-Aufruf
- Eine Kollisions- oder Vergleichsaktion, die auf ein Objekt verweist,
  das inzwischen umbenannt oder gelöscht wurde

---

## Die IDE selbst ist abgestürzt, als ich versucht habe, einen Editor zu öffnen

Prüfen Sie **`~/pygamemaker_crash.log`** (in Ihrem Home-Verzeichnis) —
Abstürze des Objekt-/Raum-/Sprite-Editors werden dort speziell
protokolliert, damit sie auch sichtbar sind, wenn die IDE ohne
Konsolenfenster gestartet wurde. Fügen Sie den relevanten Abschnitt
dieser Datei bei, wenn Sie den Fehler melden.

---

## Beim Export heißt es "X nicht gefunden" / eine Abhängigkeit fehlt

Desktop- und Mobil-Exporte (Windows .exe, macOS .app, Linux-Binärdatei,
Kivy/Android/iOS) bündeln eine Laufzeitumgebung über PyInstaller oder
Buildozer, und diese Werkzeuge müssen in **demselben Python installiert
sein, das die IDE ausführt** — eine systemweite Installation an anderer
Stelle auf dem Rechner zählt nicht. Die Fehlermeldung im Export-Dialog
gibt die genaue Lösung an, aber kurz gesagt:

- **Keine Administratorrechte nötig.** Aktivieren Sie entweder Ihre
  virtuelle Umgebung und führen Sie `pip install <Paket>` aus, oder
  installieren Sie in Ihr eigenes Benutzerkonto mit
  `pip install --user <Paket>` — beides funktioniert ohne Admin-Rechte.
- Alles auf einmal installieren: `pip install -r requirements.txt`
- **Gar keine Einrichtung gewünscht?** Verwenden Sie stattdessen den
  **HTML5 (Webbrowser)**-Export — er benötigt nichts lokal Installiertes,
  und das Ergebnis läuft in jedem Browser. (Beachten Sie, dass dies nur
  für das *Erstellen* des Exports gilt — eine fertige `.exe`/`.app`
  benötigt nichts Installiertes auf dem Rechner, der sie nur *ausführt*.)

---

## Ich habe vor dem Export eine Warnung erhalten ("X verwendet Y, aber es gibt kein Z")

Der Export führt zunächst eine Projektvalidierung durch und zeigt alles
an, was gefunden wird, bevor der Export-Dialog erscheint — zum Beispiel
ein Objekt, das **Nächster Raum** in einem Projekt mit nur einem Raum
verwendet, was keine Wirkung hätte. Dies sind **Warnungen, keine
Fehler**: klicken Sie auf OK, und der Export läuft weiter; sie weisen auf
Logik hin, die wahrscheinlich nicht das tut, was Sie erwarten, ohne Sie
am Veröffentlichen zu hindern.

---

## Ein Sprite zeigt im Ressourcenbaum ein rotes Abzeichen "(nicht importiert)"

Das bedeutet, die Bilddatei des Sprites fehlt auf der Festplatte
(meistens, weil ein Projekt ohne seinen `sprites/`-Ordner kopiert oder
geteilt wurde). Es ist rein informativ — Laufzeitumgebung und Export
ignorieren es — und **behebt sich automatisch beim nächsten Speichern**,
sobald die Datei tatsächlich wieder vorhanden ist. Keine manuelle
Korrektur nötig, außer sicherzustellen, dass sich die Bilddatei dort
befindet, wo das Sprite sie erwartet.

---

## Etwas anderes stimmt nicht

- Sehen Sie in der [[FAQ_de|FAQ]] nach häufigen Fragen
- Melden Sie Fehler im [GitHub Issue Tracker](https://github.com/Gabe1290/pythongm/issues) — geben Sie Ihr Betriebssystem, Ihre Python-Version und (falls relevant) die Konsolenausgabe oder `~/pygamemaker_crash.log` an

---

## Nächste Schritte

- [[Erste_Schritte_de|Erste Schritte]] - Fehlerbehebung zur Installation
- [[Spiele_Exportieren_de|Spiele Exportieren]] - Vollständige Export-Referenz
- [[FAQ_de|FAQ]] - Häufig gestellte Fragen
