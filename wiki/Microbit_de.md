# micro:bit (BBC-micro:bit-Simulator)

*[Startseite](Home_de) | [Vollständige Aktionsreferenz](Full-Action-Reference-Microbit-Actions_de) | [Erweiterungen](Extensions_de)*

---

PyGameMaker kann einen **simulierten BBC micro:bit** in dein Spielfenster
setzen: ein 5×5-LED-Display, die Tasten **A** und **B**, ein Touch-Logo, die
Pins 0/1/2, einen Beschleunigungssensor, Licht-, Temperatur-, Kompass- und
Geräuschsensoren, einen Lautsprecher und ein Funkmodul — alles auf dem
Bildschirm gezeichnet und mit denselben Ereignissen und Aktionen programmiert
wie der Rest der IDE. Es wird keine Hardware benötigt. Die Funktion stammt aus
der integrierten **micro:bit**-[Erweiterung](Extensions_de), die standardmäßig
aktiviert ist.

Das mitgelieferte Beispiel **`microbit_1`** („Würfel und Stimmungen“) ist ein
vollständiges Spiel: A und B zeigen ein fröhliches und ein trauriges Gesicht,
Schütteln würfelt, und das Berühren des Logos lässt die Zahl deiner bisherigen
Würfe durchlaufen.

---

## Erste Schritte

1. Erstelle ein Objekt, dessen **Name mit `microbit` beginnt** (zum Beispiel
   `microbit_1`), und platziere eine Instanz davon in einem Raum. Dieses
   Objekt *ist* der micro:bit: Die Engine zeichnet die Platine darüber und
   führt seinen Simulator aus.
2. Hake unter **Projekteinstellungen → Erweiterungen** **micro:bit** an. (Ein
   Projekt, das bereits eine micro:bit-Aktion verwendet, hat sie automatisch
   aktiv; ein Projekt ohne eine solche sieht die micro:bit-Blöcke und -Aktionen
   nie.)
3. Lege die Ereignisse auf **genau dieses Objekt**: Jede micro:bit-Aktion wirkt
   auf den micro:bit, der sie ausführt. Zum Beispiel *Button A Pressed* →
   *Show Image* `HAPPY`.
4. **Spiel testen.** Klicke auf die Tasten der Platine.

Ein Objekt wird auch zum micro:bit, wenn du `is_microbit` bei seiner
Raum-Instanz anhakst. Mehrere micro:bits in einem Raum sind in Ordnung — dann
lohnt sich das Funkmodul erst richtig.

---

## Die Platine und wie du sie bedienst

| Auf dem Bildschirm | Maus | Tastatur (optional) |
|---|---|---|
| Taste **A** / **B** | Klick (gehalten, solange die Maustaste gedrückt ist) | `A` / `B` |
| **A+B** zusammen | Rechtsklick auf eine der Tasten | `A` und `B` gedrückt halten |
| **Logo** berühren (golden, über dem Display) | Klick | — |
| Pins **0, 1, 2** (Kontakte am unteren Rand) | Klick | — |
| **Neigungsfeld** | Ziehen; der Rand entspricht einem g, beim Loslassen springt es in die Waagerechte zurück | Pfeiltasten |
| Taste **SHAKE** | Klick | `S` |
| Regler **Light / Temp / Compass / Sound** | Ziehen; der Wert bleibt | — |

Die Tastaturkürzel sind **standardmäßig aus**, damit sie nie die Tasten deines
eigenen Spiels wegnehmen. Schalte sie für eine Platine mit der
Objekteigenschaft `microbit_keyboard` ein (die gleichnamige Instanzvariable
funktioniert auch).

Weitere Objekteigenschaften: `microbit_scale` (Größenfaktor, Standard `1.0`,
etwa 220 px breit) und `microbit_show_sensors` (auf `false` setzen, um die
Sensorleiste auszublenden). Hat das Objekt einen **Sprite**, dient dieser als
Körper der Platine, und nur die LEDs und Bedienelemente werden darübergezeichnet.

Ein Klick auf die Platine löst nie zusätzlich deine eigenen Maus-Ereignisse aus.

---

## Die Aktionen (Kategorie **micro:bit**)

| Aktion | Was sie tut |
|--------|-------------|
| **Show Image** (`microbit_show_image`) | Ein eingebauter Bildname (`HEART`, `HAPPY`, `SAD`, `YES`, `NO`, `ARROW_N`, `SKULL`… insgesamt 64) oder fünf Zeilen mit je fünf Helligkeitsziffern wie `09090:99999:99999:09990:00900`. |
| **Scroll Text** (`microbit_scroll_text`) | Text über das Display laufen lassen (standardmäßig 150 ms pro Spalte). |
| **Show Number** (`microbit_show_number`) | Eine Ziffer bleibt stehen; längere Zahlen laufen durch. |
| **Set LED** (`microbit_set_pixel`) | Eine LED sofort einschalten: `x`, `y` von 0 bis 4, Helligkeit 0–9. |
| **Clear Display** (`microbit_clear_display`) | Alle LEDs ausschalten und alles Wartende verwerfen. |
| **Set Display Brightness** (`microbit_set_brightness`) | Gesamthelligkeit, 0–255. |
| **Play Tone** (`microbit_play_tone`) | Ein Piepton mit einer Frequenz für eine Anzahl Millisekunden. |
| **Play Melody** (`microbit_play_melody`) | Eine der 21 eingebauten Melodien (`DADADADUM`, `ENTERTAINER`, `POWER_UP`…) oder eigene Noten: `"C4:4 E G C5:8 R:4"` (Note, Oktave, `:Länge`; `R` ist eine Pause). |
| **Stop Sound** (`microbit_stop_sound`) | Den Lautsprecher stummschalten und wartende Töne verwerfen. |
| **Set Radio Group** (`microbit_radio_set_group`) | Die Funkgruppe wählen, 0–255. |
| **Send Radio Message** (`microbit_radio_send`) | Eine Zahl oder einen Text an die anderen micro:bits der Gruppe senden. |
| **Read Sensor** (`microbit_read_sensor`) | Einen Messwert (Beschleunigung x/y/z, Stärke, Kompass, Licht, Temperatur, Geräuschpegel, Pin 0–2 analog) in eine Variable schreiben — oder in eine globale Variable, wenn der Name mit `global.` beginnt. |
| **If Button Pressed** (`microbit_if_button`) | Bedingung: A, B, A+B oder das Logo wird gehalten. |
| **If Gesture** (`microbit_if_gesture`) | Bedingung: Die Platine befindet sich in einer Geste bzw. Lage (`shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`…`8g`). |
| **If Tilt** (`microbit_if_tilt`) | Bedingung: eine Beschleunigungsachse (Milli-g) mit einem Wert vergleichen. |
| **If LED Brightness** (`microbit_if_pixel`) | Bedingung: die Helligkeit einer LED mit einem Wert vergleichen. |

Die Bedingungen schützen die Aktion bzw. den Block, der ihnen folgt, im
GameMaker-Stil. Alle Parameter findest du in der
[Vollständigen Aktionsreferenz](Full-Action-Reference-Microbit-Actions_de).

> **Text gehört in doppelte Anführungszeichen.** `Scroll Text` und
> `Send Radio Message` lesen ihren Wert wie jeden anderen Ausdruck, also ist
> `Score - 3` eine Rechnung. Schreibe Text als `"Hallo"`. Das Display kennt nur
> druckbares ASCII; Umlaute und andere Akzentbuchstaben erscheinen als `?`,
> genau wie auf der echten Platine.

---

## Die Ereignisse

Sie werden auf dem eigenen Objekt des micro:bit ausgelöst:

| Ereignis | Wird ausgelöst, wenn |
|----------|----------------------|
| **Button A Pressed**, **Button B Pressed**, **Buttons A+B Pressed** | Die Taste(n) heruntergedrückt werden. |
| **Logo Touched** | Das Logo berührt wird. |
| **Pin 0 / 1 / 2 Touched** | Dieser Pin berührt wird. |
| **Shake**, **Logo Up**, **Logo Down**, **Tilt Left**, **Tilt Right**, **Screen Up**, **Screen Down**, **Free Fall**, **2g / 3g / 6g / 8g Impact** | Die Platine diese Geste erkennt (derselbe Algorithmus wie beim echten micro:bit). |
| **Loud Sound** / **Quiet Sound** | Der Mikrofonpegel die Schwelle für laut / leise überschreitet. |
| **Display Finished** | Die Anzeigewarteschlange alles abgespielt hat. |
| **Sound Finished** | Alle wartenden Töne und Melodien abgespielt sind. |
| **Radio Message Received** | Ein anderer micro:bit derselben Gruppe eine Nachricht gesendet hat. |

„Forever“ ist das gewöhnliche **Step**-Ereignis.

### Funk

Jede Platine startet in Gruppe 0. **Send Radio Message** liefert an jeden
*anderen* micro:bit derselben Gruppe (eine Platine hört sich nie selbst, und
eine andere Gruppe hört nichts). Der Empfänger bekommt das Ereignis und zwei
Variablen: `radio_number` (0, wenn der Text keine Zahl ist) und `radio_string`
(immer der Text). Der Text wird wie beim echten Funkmodul auf 32 Zeichen
gekürzt.

---

## Zeit: Anzeige- und Tonwarteschlange

Auf einem echten micro:bit *blockiert* durchlaufender Text das Programm. Ein
Spiel darf nicht blockieren, deshalb werden Anzeige-Aktionen **eingereiht** und
nacheinander abgespielt (höchstens 16; etwas anzufordern, das schon angezeigt wird,
bewirkt nichts). **Clear Display** leert die Warteschlange, und **Display
Finished** meldet, wann sie leer ist — so kannst du Animationen verketten. Töne
werden genauso eingereiht, mit **Stop Sound** und **Sound Finished**.

Der Ton ist eine Rechteckwelle, wie beim Summer der Platine. Hat der Computer
kein Audiogerät, wird er stillschweigend übersprungen (der Simulator verfolgt
ihn trotzdem).

---

## Exporte

Der **Desktop**-Export (Windows, Linux, macOS) packt die echte Engine, der
micro:bit funktioniert also genau wie in „Spiel testen“. Auch der
**HTML5**-Export enthält den Simulator: Platine und Sensorleiste werden im
Browser gezeichnet, du kannst Tasten, Logo und Pins anklicken oder antippen,
Neigungsfeld und Regler ziehen, und der Lautsprecher piept (Browser erlauben Ton
erst nach dem ersten Klick oder Tastendruck). Der **Android/Kivy**-Export hat
ihn ebenfalls: Platine und Sensorleiste werden gezeichnet (in vereinfachter
Optik mit eckigen Ecken), du kannst Tasten, Logo, Pins, Neigungsfeld,
Shake-Taste und Regler berühren, die Ereignisse werden ausgelöst, und der
Lautsprecher spielt seine Töne. Die Tastaturkürzel funktionieren nur für eine
Platine, deren Eigenschaft (oder Variable) `microbit_keyboard` gesetzt ist. Eine Platine wird an
ihrem Objektnamen erkannt (er muss mit `microbit` beginnen) oder an `is_microbit` bei ihrer Raum-Instanz.

---

## MicroPython-Export (auf einen echten micro:bit)

Das ist ein Export anderer Art. Statt eines Spiels für einen anderen Computer
macht er aus dem Programm deiner micro:bit-Objekte echten **MicroPython**-Code,
der auf einer physischen Platine läuft.

1. Öffne **Datei → micro:bit-Code (MicroPython) exportieren...** (ein Projekt
   muss geöffnet sein).
2. Gib an, welche Platine du hast: **V2 (2020 oder neuer)**, **V1 (Original,
   2016-2020)** oder **Beide (eine .hex-Datei für V1- und V2-Boards)**.
3. Wähle einen Ordner. Jedes micro:bit-Objekt bekommt sein eigenes Programm,
   `<Ordner>/<Objektname>/main.py`.
4. Wurde genau ein Objekt exportiert, bietet die IDE zwei Wege an, es auf die
   Platine zu bringen. **Auf den micro:bit kopieren?** kopiert `main.py` auf
   eine Platine, die per USB angeschlossen ist und bereits MicroPython
   ausführt (das Programm startet dann von selbst). **Eine flashbare .hex-Datei
   erstellen?** erzeugt eine `.hex`-Datei, die du auf das USB-Laufwerk
   **MICROBIT** der Platine ziehst — das funktioniert auch bei einer neuen
   Platine, die noch nie MicroPython ausgeführt hat.

Alle micro:bit-Aktionen und -Bedingungen werden übersetzt, ebenso *Set
Variable*, *Test Variable*, Blöcke und Kommentare. Jedes Ereignis wird zu einer
Abfrage innerhalb einer einzigen Schleife. Spielaktionen, die auf einer Platine
nichts bedeuten (Räume, Sprites, Punkte …), werden nicht exportiert. In
Ausdrücken funktionieren `irandom`, `random` und `choose`; andere
GameMaker-Funktionen werden nicht übersetzt.

Der Export-Dialog listet auf, was nicht exportiert werden konnte:

- **Display Finished** und **Sound Finished** (die Anzeige- und Tonaufrufe der
  Platine warten ohnehin, bis sie fertig sind).
- Auf einer V1-Platine, was eine V2 braucht: das Lesen des Geräuschpegels, das
  Touch-Logo (*If Button Pressed* mit dem Logo, **Logo Touched**) und die
  Ereignisse **Loud Sound** / **Quiet Sound**.
- Alles andere, wofür es in MicroPython keine Entsprechung gibt.

**Größe:** Das Programm muss auf einer V1-Platine in 8.187 Bytes und auf einer
V2 in 20.150 Bytes passen. **Beide** erzeugt eine einzige Universal-Hex-Datei;
sie ist daher durch die V1-Größe begrenzt und wird nach den Regeln der V1
exportiert.

> Die `.hex`-Dateien wurden gegen die echte micro:bit-Firmware geprüft, aber
> noch nicht auf einer physischen Platine.

---

## Wie geht es weiter?

- Öffne das Beispiel **`microbit_1`** im Willkommen-Tab und lies seine Anleitung.
- Probiere zwei Platinen in einem Raum aus, jede mit einem *Set Radio Group*,
  und sende eine Nachricht von einer Taste.
- Geplant: eine Live-Verbindung zu einem echten micro:bit über USB. Sie ist noch
  nicht verfügbar.

Siehe auch: [Erweiterungen](Extensions_de), [Vollständige Aktionsreferenz](Full-Action-Reference-Microbit-Actions_de), [Ereignisreferenz](Event-Reference_de).
