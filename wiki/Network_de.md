# Netzwerk (LAN-Multiplayer)

*[Startseite](Home_de) | [Vollständige Aktionsreferenz](Full-Action-Reference-Network-Actions_de) | [Erweiterungen](Extensions_de)*

---

PyGameMaker kann ein Projekt in ein **LAN-Multiplayer-Spiel** verwandeln: Ein
Rechner hostet, die anderen treten über das lokale Netzwerk bei, und die
Spieler teilen Zustand — eine Punktetafel, eigene Nachrichten und sogar die
Avatare der anderen auf dem Bildschirm — ohne Server, ohne Konto und ohne
Internet. Das stellt die eingebaute **LAN-Multiplayer**-[Erweiterung](Extensions_de)
bereit, die standardmäßig aktiviert ist.

Die mitgelieferten Beispiele **`reseau_1`–`reseau_3`** sind vollständige,
spielbare Beispiele: ein gemeinsamer Raum, in dem sich zwei Spieler zusammen
bewegen, ein Klassenquiz mit Live-Punktetafel und eine kooperative
Schatzsuche für zwei.

Heute unterstützt: der **Desktop**-Export (pygame), als Host und als Client,
und der **HTML5**-Export als Client (eine Browserseite tritt einem
Desktop-Host bei; sie kann nicht selbst hosten). Ein **Kivy/Android**-Export
führt das Spiel als Einzelspieler aus — die Netzwerkaktionen tun dort
gefahrlos nichts.

---

## Zwei Stufen

**Stufe A — gemeinsame Tafel.** Keine Avatare, nur geteilter Zustand:
Variablen, die jeder Spieler lesen und schreiben kann, eigene Nachrichten und
wer verbunden ist. Das ist der einfachste Weg, ein Projekt multiplayerfähig zu
machen — ein Quiz, eine gemeinsame Punktetafel, ein „Wer zuerst antwortet“-Buzzer.

**Stufe B — vernetzte Instanzen.** Vom Host erzeugte Instanzen (Spieler,
Gegner, Sammelobjekte), die auf jedem Rechner automatisch erscheinen und sich
bewegen, sowie Avatare im Besitz eines Spielers, die jeder Spieler lokal
steuert, während alle anderen eine sanft interpolierte Kopie sehen.

---

## So funktioniert es

- Ein Spieler ruft **Spiel hosten** auf, meist im Create-Ereignis eines
  Raum-Steuerobjekts. Dieser Rechner wird zum **Host** — die Rechner aller
  anderen Spieler verbinden sich mit ihm. `global.player_id` wird `0`.
- Andere Spieler rufen **Spiel beitreten** mit der LAN-IP-Adresse des Hosts auf
  (oder mit `"auto"`, um einen eingebauten Verbindungsbildschirm zu zeigen, der
  Hosts im Netzwerk automatisch findet). `global.player_id` wird vom Host
  vergeben (`1`, `2`, ...).
- Ist der Host nicht erreichbar, **läuft das Spiel als Einzelspieler weiter** —
  der Beitritt blockiert oder zerstört nie ein Spiel.
- Spieleridentität und Verbindungsstatus sind immer als Globals lesbar:
  `global.is_host`, `global.player_id`, `global.player_count`,
  `global.network_role`, `global.network_connected`.
- **Schreibe deine Spiellogik mit einer gewöhnlichen „Wenn“-Aktion**, z. B.
  `global.is_host == 1`, um Aufgaben nur für den Host zu schützen (etwa das
  Erzeugen von Gegnern) — spezielle „Netzwerkbedingungs“-Aktionen sind nicht
  nötig.
- Eine mit **Geteilte Variable setzen** gesetzte geteilte Variable ist *überall* als
  `global.<Name>` lesbar — auch auf dem Rechner, der sie gesetzt hat.
- **Eigene Nachrichten** (**Netzwerknachricht senden**) melden ein Ereignis mit
  Namen und einer kleinen angehängten Information — ein Buzzerdruck, eine
  gewählte Antwort, ein „Bereit“-Signal.

---

## Die Aktionen (Kategorie **Netzwerk**)

| Aktion | Was sie tut |
|--------|-------------|
| **Spiel hosten** | Host werden. Zeigt optional eine Warteraum-Lobby mit einem Start-Knopf. |
| **Spiel beitreten** | Sich per Adresse mit einem Host verbinden (oder `"auto"` für den eingebauten Verbindungsbildschirm). |
| **Spiel verlassen** | Die Verbindung trennen (oder das Hosten beenden) und die Netzwerk-Globals löschen. |
| **Netzwerkspiel starten** | Nur Host: die Lobby beenden und allen das Losspielen mitteilen. |
| **Geteilte Variable setzen** | Eine Variable schreiben, die jeder Rechner als `global.<Name>` lesen kann. |
| **Geteilte Variable lesen** | Eine geteilte Variable in ein Global kopieren (zur Verwendung in einer Berechnung). |
| **Netzwerknachricht senden** | Eine eigene, benannte Nachricht mit Daten an alle senden. |
| **Netzwerkobjekt erzeugen** | Nur Host: eine Instanz erzeugen, die bei allen Clients erscheint. |
| **Diese Instanz synchronisieren** | Die handelnde Instanz als über die Rechner hinweg repliziert markieren. |
| **Besitzer der Instanz festlegen** | Einem bestimmten Spieler die lokale Steuerung einer synchronisierten Instanz geben. |
| **Wenn ich diese Instanz steuere** | Bedingung: Steuerlogik schützen, sodass sie nur auf dem besitzenden Rechner läuft. |
| **Netzwerktaste zuweisen** | Eine lokale Taste einer benannten Eingabe zuordnen, die der Host lesen kann. |
| **Wenn der Spieler drückt** | Bedingung (Host): Hält ein bestimmter Spieler eine benannte Eingabe gedrückt? |
| **Synchronisationsrate festlegen** | Die Snapshot-Rate des Hosts und die Interpolationsverzögerung der Clients einstellen. |

Alle Parameter findest du in der [Vollständigen Aktionsreferenz](Full-Action-Reference-Network-Actions_de).

---

## Die Ereignisse (Kategorie **Netzwerk**)

Sie werden auf jeder Instanz ausgelöst, deren Objekt sie behandelt, auf jedem
betroffenen Rechner:

| Ereignis | Wird ausgelöst, wenn |
|----------|----------------------|
| **Network Ready** | Ein Client die Verbindung zum Host abgeschlossen hat (der Host löst es für sich selbst nicht aus). |
| **Player Joined** | Ein neuer Spieler sich verbindet. `global.network_sender` / `global.network_player_name` benennen ihn. |
| **Player Left** | Ein Spieler die Verbindung trennt. |
| **Network Message** | Eine **Netzwerknachricht senden** ankommt — `global.network_event` / `global.network_data` / `global.network_sender`. |
| **Network Game Started** | Der Host **Netzwerkspiel starten** aufruft. |
| **Connection Lost** | Die Verbindung eines Clients zum Host abbricht. Das Spiel läuft weiter — nur die Geister dieses Spielers verschwinden. |

---

## Ein minimales Beispiel für einen gemeinsamen Raum (Stufe A)

In einem unsichtbaren Raum-Steuerobjekt:

- **Create:** `Spiel hosten`, wenn es der Rechner der Lehrkraft ist, sonst
  `Spiel beitreten` mit deren IP (oder `"auto"`).
- **Create:** `Geteilte Variable setzen` `round = 1` (nur Host, geschützt durch
  `global.is_host == 1`).
- Überall: `draw_text` mit `global.round` — alle Spieler sehen denselben Wert.

## Ein minimales Beispiel für gemeinsame Avatare (Stufe B)

Im Create-Ereignis des Spielerobjekts:

- `Diese Instanz synchronisieren` — diese Instanz wird jetzt repliziert.
- Auf dem **Host**: `Netzwerkobjekt erzeugen` erzeugt eine Spielerinstanz pro
  beitretendem Spieler (in einem **Player Joined**-Handler), danach
  `Besitzer der Instanz festlegen` mit der Nummer dieses Spielers.
- Bewegungscode, der durch `Wenn ich diese Instanz steuere` geschützt ist, läuft nur auf
  dem Rechner des besitzenden Spielers; überall sonst ist die Instanz ein sanft
  interpolierter Geist.

---

## Hinweise und Grenzen

- **TCP, nur LAN.** Kein NAT-Durchgriff, kein Spiel über das Internet — beide
  Rechner müssen im selben lokalen Netzwerk erreichbar sein (ein WLAN im
  Klassenzimmer oder ein Kabelnetz im Computerraum). WLAN mit Client-Isolation
  (an verwalteten Schulnetzen üblich) blockiert Erkennung und direkte
  Verbindung gleichermaßen; ein Kabelnetz ist die zuverlässigste Lösung.
- **Ports 45782 (TCP)** und **45783 (UDP, Erkennung)** — frage vor dem Einsatz
  in einem verwalteten Netzwerk die Schul-IT und rechne beim ersten Hosten mit
  einer Firewall-Abfrage.
- Ein Browser-Client (HTML5-Export) verbindet sich mit dem Port eins über dem
  des Hosts, z. B. `45783`, wenn der Host den Standard nutzt — das geschieht
  automatisch.
- Der Verlust des Hosts verläuft sanft: Das eigene Spiel eines Clients läuft
  weiter; nur die Geister der anderen Spieler verschwinden, und **Connection
  Lost** wird ausgelöst, damit du eine Meldung zeigen kannst.
- Ist die LAN-Multiplayer-Erweiterung **deaktiviert**, tun diese Aktionen und
  Ereignisse einfach nichts — siehe [Erweiterungen](Extensions_de).

---

## Siehe auch

- [File Exchange Multiplayer](FileExchange) (englisch) — der rundenbasierte
  Verwandte für ein Klassenzimmer, in dem eine Firewall die direkten
  Verbindungen dieser Erweiterung blockiert
- [Erweiterungen](Extensions_de) — wie LAN-Multiplayer ausgeliefert und wie es abgeschaltet wird
- [Vollständige Aktionsreferenz](Full-Action-Reference-Network-Actions_de) — jede Aktion und jeder Parameter
- [Ereignisreferenz](Event-Reference_de)
