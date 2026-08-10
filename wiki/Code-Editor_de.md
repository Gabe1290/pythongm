# Code-Editor

> [English](Code-Editor) | [Français](Code-Editor_fr) | [Deutsch](Code-Editor_de) | [Italiano](Code-Editor_it) | [Español](Code-Editor_es) | [Português](Code-Editor_pt) | [Русский](Code-Editor_ru) | [Slovenščina](Code-Editor_sl) | [Українська](Code-Editor_uk)

---

> [Zurück zur Startseite](Home_de)

Jedes Objekt in PyGameMaker hat einen **Code-Editor**-Tab neben Event
List und Blockly — eine dritte Möglichkeit, mit denselben Ereignissen
und Aktionen zu arbeiten, diesmal als echtes Python. Es ist kein
Einbahnstraßen-Export: Code, den Sie hier schreiben, wird zurück in
strukturierte Ereignisse und Aktionen geparst, sodass er mit den beiden
anderen Ansichten synchron bleibt.

---

## Den Code-Editor öffnen

1. Öffnen Sie ein Objekt im Objekt-Editor
2. Klicken Sie auf den Tab **💻 Code-Editor**

![Der Code-Editor im Modus "Generierten Code anzeigen": eine Klasse mit
einer Methode pro Ereignis (on_create, on_step,
on_collision_obj_power, ...), die zeigt, zu welchem echten Python Ihre
visuellen Ereignisse und Aktionen kompilieren](images/code-editor.png)

---

## Zwei Modi

Ein Dropdown oben schaltet zwischen ihnen um:

### 📖 Generierten Code anzeigen

Nur lesbar. Zeigt das Python, zu dem die aktuellen Ereignisse und
Aktionen Ihres Objekts kompilieren — eine Methode pro Ereignis
(`on_create`, `on_step`, `on_collision_obj_enemy`, ...), die `self.*` und
`game.*` genau wie die Laufzeitumgebung aufruft. Eine Aktion, für die der
Generator keine saubere Python-Entsprechung hat, erscheint trotzdem,
markiert mit einem Kommentar (`# Unknown action: ...`) über der Zeile,
die sie erzeugt hat — nichts wird versteckt, auch bei Randfällen nicht.
Klicken Sie auf **🔄 Aktualisieren**, um nach Änderungen an Ereignissen
an anderer Stelle neu zu generieren.

### ✏️ Benutzerdefinierten Code bearbeiten

Bearbeitbar, mit Python-Syntaxhervorhebung. Beginnen Sie zu tippen (oder
bearbeiten Sie den aus dem Anzeige-Modus übernommenen Startcode), und
PyGameMaker parst Ihre Klasse etwa 1,5 Sekunden nachdem Sie mit dem
Tippen aufhören — eine Statusanzeige neben der Symbolleiste zeigt dabei
**idle / busy / error / empty**. Nach erfolgreichem Parsen **ersetzen**
Ihre Methoden die Ereignisse und Aktionen des Objekts (kein Zusammenführen)
— welche Ereignismethoden Ihr Code auch definiert, sie werden zur
Ereignisliste dieses Objekts, sofort sichtbar auch in den Tabs Event List
und Blockly.

Schlägt das Parsen fehl (ein Syntaxfehler, oder Code, den der Parser
nicht auf Ereignisse zurückführen kann), zeigt die Statusanzeige den
Fehler an, und nichts wird übernommen — die Ereignisse Ihres Objekts
bleiben unverändert, bis der Code sauber geparst wird.

---

## Warum verwenden

- **Geschwindigkeit** — manche Logik (eine mehrverzweigte Berechnung,
  eine Schleife, eine einmalige Formel) tippt sich schneller, als sie
  sich aus Blöcken oder einer Aktionsliste zusammensetzen lässt.
- **Lernbrücke** — schalten Sie die Ereignisse eines von einem Anfänger
  gebauten Objekts in den Anzeige-Modus, um die echte Code-Entsprechung
  zu sehen — ein natürlicher nächster Schritt für Lernende, die von
  visueller Programmierung zu Python übergehen.
- **Präzision** — alles, was sich als einfache Python-Methode auf dem
  Objekt ausdrücken lässt, funktioniert, ohne auf eine passende visuelle
  Aktion warten zu müssen.

Dies ist derselbe zugrunde liegende Mechanismus wie die Aktion **Code
ausführen** aus der Aktionsliste / Blockly (Kategorie *Control*) — der
Code-Editor-Tab arbeitet einfach auf der Ebene eines ganzen Objekts statt
einer einzelnen Aktion.

---

## Nächste Schritte

- [[Objekt_Editor_de|Objekt-Editor]] - Wo sich der Code-Editor-Tab befindet
- [[Visuelle_Programmierung_de|Visuelle Programmierung]] - Die Blockly-Ansicht derselben Ereignisse
- [[Events_und_Aktionen_de|Ereignisse und Aktionen]] - Was jede Aktion tatsächlich bewirkt
