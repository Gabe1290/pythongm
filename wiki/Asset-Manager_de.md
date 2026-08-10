# Ressourcenverwaltung

> [English](Asset-Manager) | [Français](Asset-Manager_fr) | [Deutsch](Asset-Manager_de) | [Italiano](Asset-Manager_it) | [Español](Asset-Manager_es) | [Português](Asset-Manager_pt) | [Русский](Asset-Manager_ru) | [Slovenščina](Asset-Manager_sl) | [Українська](Asset-Manager_uk)

---

> [Zurück zur Startseite](Home_de)

Über das alltägliche Erstellen/Umbenennen/Löschen im Ressourcenbaum
hinaus verfolgt PyGameMaker, **wo jede Ressource tatsächlich verwendet
wird**, hält gelöschte Ressourcen wiederherstellbar, statt sie endgültig
zu verlieren, und kann sowohl ungenutzte Ressourcen als auch verwaiste
Dateien finden, die den Projektordner verstopfen. All das befindet sich
im Menü **Extras**.

---

## Den Ressourcenbaum filtern

Tippen Sie in das Filterfeld über dem Ressourcenbaum, um ihn während der
Eingabe auf passende Namen einzugrenzen. Der Abgleich ignoriert Groß-/
Kleinschreibung und bezieht sich auf den rohen Ressourcennamen; eine
Kategorie (Sprites, Objekte, ...) verbirgt sich, sobald alle enthaltenen
Elemente herausgefiltert sind, und erscheint wieder, sobald eines wieder
passt.

---

## Nutzungsverfolgung

Jedes Löschen einer Ressource prüft jetzt, wo diese Ressource
tatsächlich referenziert wird — andere Objekte, Räume, Aktionen — bevor
Sie bestätigen. Wird `spr_player` von 3 Objekten verwendet, sagt die
Löschbestätigung das direkt, statt einer allgemeinen Warnung, sodass Sie
es *vor* dem Löschen erfahren, nicht danach, wenn dadurch bereits etwas
kaputtgegangen ist.

**Bekannte Einschränkung:** diese Analyse sieht nur, was PyGameMakers
eigene Datenstrukturen sehen können — Aktionsparameter, Kollisionsziele,
Rauminstanzen, Sprite-/Parent-Felder. Ein Ressourcenname, der nur
innerhalb einer rohen Python-Zeichenkette im [[Code-Editor_de|Code-Editor]]
oder der Aktion Code ausführen verwendet wird (z. B.
`game.sounds['explosion'].play()`), ist für diese Analyse nicht sichtbar.

---

## Gelöschte Ressourcen wiederherstellen (Papierkorb)

**Extras > Gelöschte Ressourcen wiederherstellen...**

Das Löschen einer Ressource entfernt sie nicht sofort — ihre Dateien
wandern in einen projektlokalen Papierkorb, und PyGameMaker führt Buch
darüber, was gelöscht wurde, wohin die Dateien verschoben wurden, und
welche Querverweise dabei gelöscht wurden (zum Beispiel das Sprite-Feld
eines Objekts, das geleert wird, weil das referenzierte Sprite gelöscht
wurde). Dieser Dialog listet alles, was sich aktuell im Papierkorb
befindet, mit drei Aktionen auf:

| Aktion | Wirkung |
|--------|--------|
| **Wiederherstellen** | Bringt die Ressource genau so zurück, wie sie war. Verweigert das Überschreiben, wenn inzwischen eine neue Ressource mit demselben Namen existiert — auch die Wiederherstellung ist nicht destruktiv. |
| **Endgültig löschen** | Entfernt einen einzelnen Papierkorb-Eintrag dauerhaft |
| **Papierkorb leeren** | Entfernt alles, was sich aktuell im Papierkorb befindet |

Querverweise, die beim Löschen entfernt wurden, werden bei der
Wiederherstellung **nicht** automatisch wiederhergestellt — Sie sehen,
was sich geändert hat, und können selbst entscheiden, ob Sie es wieder
verknüpfen, statt PyGameMaker raten zu lassen.

Dateien im Papierkorb sind von Projekt-Exporten (Zip/HTML5/etc.)
ausgeschlossen — eine gelöschte Ressource taucht nie still und heimlich
in einem veröffentlichten Spiel wieder auf.

---

## Ungenutzte Ressourcen finden

**Extras > Ungenutzte Ressourcen finden...**

Durchsucht das gesamte Projekt mit derselben Nutzungsanalyse wie oben und
listet jede Ressource ohne jegliche Referenz auf, gruppiert nach
Kategorie, jede mit einem Kontrollkästchen. Wählen Sie diejenigen aus,
die Sie wirklich loswerden möchten (oder **Alle auswählen**) und
**Auswahl in den Papierkorb verschieben** — dasselbe Sicherheitsnetz wie
bei jedem anderen Löschvorgang.

**Räume werden mit Vorsicht behandelt.** Ein Raum, den niemand explizit
namentlich ansteuert — ein Spiel mit nur einem Raum, oder der allererste
Raum eines Spiels — erscheint unter einer reinen Referenzzählung
berechtigterweise als "ungenutzt", aber ihn zu löschen würde das Spiel
zerstören. Räume werden mit *"Räume — nicht explizit angesteuert"*
beschriftet statt schlicht "ungenutzt", und **Alle auswählen überspringt
Räume** absichtlich; Sie können trotzdem einzelne markieren, wenn Sie
sich sicher sind.

---

## Verwaiste Dateien finden

**Extras > Verwaiste Dateien finden...**

Das umgekehrte Problem: Dateien im Projektordner (`sprites/`, `sounds/`,
`backgrounds/`, `fonts/`, `thumbnails/`), die **keinen** passenden
Eintrag im Projekt haben — zurückgelassen durch eine unterbrochene
Operation, oder von Hand außerhalb der IDE abgelegt. Listet sie nach
Kategorie mit demselben Muster aus Kontrollkästchen / Alle auswählen /
**Auswahl in den Papierkorb verschieben** wie bei ungenutzten Ressourcen
auf und enthält im selben Dialog ein eigenes Mini-Papierkorb-Panel
(Wiederherstellen / Endgültig löschen / Leeren) — verwaiste Dateien
verwenden einen eigenen, separaten Papierkorb-Speicher, getrennt von
normalen Ressourcenlöschungen, da sie von vornherein nie ein echter
project.json-Eintrag waren.

---

## Projekt bereinigen

**Extras > Projekt bereinigen**

Ein Ein-Klick-Durchlauf für übrig gebliebene `.tmp`-Dateien — die
temporären Begleitdateien, die PyGameMakers atomarer Speichervorgang
erzeugt und normalerweise selbst wieder entfernt. Nur Dateien, die etwa
eine Minute oder älter sind, werden angefasst, damit ein laufender
Speichervorgang nie gefährdet wird. Meldet, wie viele Dateien entfernt
wurden, oder dass es nichts zu bereinigen gab. Anders als bei den obigen
Dialogen laufen diese Dateien nie durch das Ressourcensystem oder den
Papierkorb — eine `.tmp`-Datei ist nie die maßgebliche Kopie von
irgendetwas, daher wird sie direkt gelöscht.

---

## Nächste Schritte

- [[Raum_Editor_de|Raum-Editor]] / [[Objekt_Editor_de|Objekt-Editor]] - Woher die meisten Ressourcenreferenzen kommen
- [[FAQ_de|FAQ]] - Häufige Fragen, auch zur Datensicherheit
