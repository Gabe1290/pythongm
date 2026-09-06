# Netzwerk

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Netzwerktaste zuweisen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `bind_network_input` |
| **Symbol** | ⌨️ |
| **Kategorie** | Netzwerk |

Verknüpft eine lokale Taste mit einer „benannten Eingabe“, die an den Host gemeldet wird. Der Host prüft sie dann mit „Wenn der Spieler drückt“. Die Pfeiltasten und die Leertaste sind bereits verknüpft ("left", "right", "up", "down", "space")

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `name` | Text | — | Eine Bezeichnung Ihrer Wahl (z. B. "jump", "fire") |
| `key` | Text | — | Ein Tastenname: "space", "left", "a", "5", "lshift"... |

### Netzwerkobjekt erzeugen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `network_spawn` |
| **Symbol** | ✨ |
| **Kategorie** | Netzwerk |

Nur beim Host: erzeugt eine Instanz, die auf allen Clients automatisch als geglätteter „Geist“ erscheint. Auf einem Client ohne Wirkung. Der Host steuert die erzeugte Instanz – ihre Spiellogik mit global.is_host == 1 absichern

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `object` | Objekt | — | Die Art des zu erstellenden Objekts |
| `x` | Text | `0` |  |
| `y` | Text | `0` |  |
| `owner` | Text | `0` | Der Spieler, der diese Instanz steuert (0 = Host). Oft global.network_sender innerhalb von „Spieler beigetreten“.; optional |
| `relative` | Ja/Nein | Nein | Position relativ zu dem Objekt, das die Aktion ausführt; optional |

### Spiel hosten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `host_game` |
| **Symbol** | 🌐 |
| **Kategorie** | Netzwerk |

Wird zum Host einer LAN-Mehrspielerpartie: die anderen Spieler verbinden sich mit dieser Maschine. Nur einmal aufrufen (zum Beispiel im Erstellen-Ereignis des Raum-Controllers). Setzt global.player_id = 0 und global.network_role = "host"

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `game_name` | Text | `PyGameMaker` | Name, der in der Serverliste angezeigt wird (Netzwerksuche); optional |
| `max_players` | Zahl | `8` | Größte Anzahl Spieler, Host eingeschlossen (2 bis 16); optional |
| `port` | Zahl | `45782` | TCP-Port – muss beim Host und bei jedem Client gleich sein; optional |
| `player_name` | Text | — | Name dieses Spielers (leer = global.player_name, sonst "Player"); optional |
| `show_lobby` | Ja/Nein | Nein | Vor dem Spielbeginn einen Bildschirm „Warten auf Spieler …“ mit Startknopf anzeigen; optional |

### Wenn ich diese Instanz steuere

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `is_instance_owner` |
| **Symbol** | ❓ |
| **Kategorie** | Netzwerk |

Eine Bedingung: wahr, wenn DIESE Maschine die synchronisierte Instanz besitzt. Vor einen Block setzen, damit die Steuerungslogik nur auf der Maschine des richtigen Spielers läuft

*Parameter:* keine

### Wenn der Spieler drückt

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `remote_input` |
| **Symbol** | ❓ |
| **Kategorie** | Netzwerk |

Eine Bedingung beim Host: wahr, solange der genannte Spieler die genannte Eingabe hält. So kann der Host auf die Tasten eines Clients reagieren, ohne dessen Figur zu besitzen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `player` | Text | `0` | Spielernummer (0 = Host) |
| `name` | Text | — | Die zu prüfende benannte Eingabe (z. B. "jump") |

### Spiel beitreten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `join_game` |
| **Symbol** | 🔌 |
| **Kategorie** | Netzwerk |

Verbindet sich mit einer LAN-Mehrspielerpartie, die eine andere Maschine hostet. Der Host setzt global.player_id (1, 2, ...). Ist der Host nicht erreichbar, läuft das Spiel als Einzelspieler weiter

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `host` | Text | `127.0.0.1` | LAN-IP-Adresse des Hosts ("auto" öffnet den eingebauten Verbindungsbildschirm); optional |
| `port` | Zahl | `45782` | TCP-Port – muss mit dem des Hosts übereinstimmen; optional |
| `player_name` | Text | — | Name dieses Spielers (leer = global.player_name, sonst "Player"); optional |

### Spiel verlassen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `leave_game` |
| **Symbol** | 🚪 |
| **Kategorie** | Netzwerk |

Trennt die Verbindung (oder beendet das Hosten) und löscht die globalen Netzwerkvariablen

*Parameter:* keine

### Geteilte Variable lesen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `get_shared_var` |
| **Symbol** | 📥 |
| **Kategorie** | Netzwerk |

Kopiert eine geteilte Variable in eine globale Variable, um sie in einer Berechnung zu verwenden. Entspricht dem direkten Lesen von global.<name>

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `name` | Text | — | Name der zu lesenden geteilten Variable |
| `into` | Text | — | Name der globalen Variable, in die der Wert geschrieben wird |

### Netzwerknachricht senden

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `send_network_message` |
| **Symbol** | ✉️ |
| **Kategorie** | Netzwerk |

Sendet eine eigene Nachricht an alle. Löst auf den betroffenen Maschinen das Ereignis „Netzwerknachricht“ aus, mit global.network_event / global.network_data / global.network_sender

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `event` | Text | — | Eine Bezeichnung Ihrer Wahl, die der Handler prüft (z. B. "buzz", "answer") |
| `data` | Text | — | Eine Zahl, ein Text, true/false oder eine kurze Liste; optional |
| `target` | Auswahl | `all` | all = alle; host = nur der Host; Auswahl: `all`, `host` |

### Netzwerkmodus festlegen (v1)

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_network_mode` |
| **Symbol** | 🌐 |
| **Kategorie** | Netzwerk |

Eine ältere Low-Level-Aktion: startet den Raum im Host- oder Client-Modus (nur Zuschauer – die Eingabe eines Clients hat keine Wirkung). Besser „Spiel hosten“ / „Spiel beitreten“ verwenden. Für bestehende Projekte und die Schalter --net-host / --net-client erhalten

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `mode` | Auswahl | `host` | Host = andere verbinden sich mit Ihnen; Client = Sie verbinden sich mit einem Host; Auswahl: `host`, `client` |
| `host` | Text | `127.0.0.1` | LAN-IP-Adresse des Hosts (nur im Client-Modus); optional |
| `port` | Zahl | `45782` | TCP-Port – muss beim Host und beim Client gleich sein; optional |

### Geteilte Variable setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_shared_var` |
| **Symbol** | 📤 |
| **Kategorie** | Netzwerk |

Schreibt eine Variable, die alle Maschinen teilen. Beim Host wird sie sofort übernommen; auf einem Client ist es eine Anfrage an den Host. Überall lesbar als global.<name>

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `name` | Text | — | Ein einfacher Bezeichner (Buchstaben, Ziffern, _) – keine Leerzeichen, keine Operatoren |
| `value` | Text | `0` | Eine Zahl, ein Text oder true/false (zusammengesetzte Objekte werden abgelehnt) |

### Besitzer der Instanz festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_instance_owner` |
| **Symbol** | 🎮 |
| **Kategorie** | Netzwerk |

Legt fest, welcher Spieler diese synchronisierte Instanz steuert (0 = Host, 1, 2, ... = Clients). Auf der Maschine dieses Spielers läuft die Instanz lokal und reagiert flüssig, und ihr Zustand wird an den Host zurückgemeldet; überall sonst ist sie ein geglätteter Geist. Beim Host aufrufen, abgesichert mit global.is_host == 1

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `player` | Text | `0` | Spielernummer (0 = Host). Oft global.network_sender innerhalb von „Spieler beigetreten“. |

### Synchronisationsrate festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_sync_rate` |
| **Symbol** | ⏱️ |
| **Kategorie** | Netzwerk |

Stellt ein, wie oft der Host Momentaufnahmen sendet und wie weit dahinter die Clients sie zeichnen. Einmal beim Host aufrufen, und für die Verzögerung auch bei den Clients

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `hz` | Zahl | `20` | 10–30 funktioniert im lokalen Netz gut (Standard 20); optional |
| `interp_ms` | Zahl | `100` | Wie weit zurückversetzt Geister gezeichnet werden, in Millisekunden (Standard 100); optional |

### Netzwerkspiel starten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `start_networked_game` |
| **Symbol** | 🚦 |
| **Kategorie** | Netzwerk |

Nur beim Host: holt alle aus dem Warteraum und startet die Partie. Löst auf jeder Maschine das Ereignis „Netzwerkspiel gestartet“ aus

*Parameter:* keine

### Diese Instanz synchronisieren

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `sync_instance` |
| **Symbol** | 🔗 |
| **Kategorie** | Netzwerk |

Markiert die Instanz, die diese Aktion ausführt, als synchronisiert: ihre Position, ihre Drehung, ihr Bild und ihre Sichtbarkeit werden auf alle Maschinen kopiert. Im Erstellen-Ereignis aufrufen. Standardmäßig gehört sie dem Host; mit „Besitzer der Instanz festlegen“ kann ein Client sie steuern

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `vars` | Text | — | Namen zusätzlich zu kopierender Instanzvariablen, durch Kommas getrennt (z. B. "hp, colour"); optional |

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (8)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (25)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (16)
- [Partikel](Full-Action-Reference-Particles_de) (8)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
